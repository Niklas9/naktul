#!/usr/bin/python


# Backup settings
BACKUP_SERVER_NAME = 'local-dev'
BACKUP_DIRS = ('/var/www/vhosts',)
BACKUP_DAYS_TO_STORE = 7  # number of days
BACKUP_SAVE_EVERY_MONTH = True  # stores the backup from the first every month
BACKUP_MYSQL_DBS = ('kmp', 'kcp')
BACKUP_MYSQL_HOST = 'localhost'
BACKUP_MYSQL_USER = 'root'
BACKUP_MYSQL_PASSWD = ''
BACKUP_MYSQL_DUMP_CMD = '/usr/bin/mysqldump'
BACKUP_NOTIFICATION_FROM = 'info@neun.se'
BACKUP_NOTIFICATION_CONTACTS = ('nandersson900@gmail.com',)
BACKUP_LOG_FILE = 'nback.log'

# Amazon AWS S3 settings
AWS_BUCKET = 'servers'
AWS_DIR = 'backups/%s' % BACKUP_SERVER_NAME
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

# don't change anything below this line !!!


import boto
import commands
import datetime
import logging
import math
import os
import smtplib
import tarfile

# TODO(niklas):
# * add clear comments to each class, method, python-style '''


class Logger(object):

    log_file = None  # must be overriden by subclass
    ref_class = None  # must be overriden by subclass
    cli = None
    LOG_FMT = ('%(asctime)s.%(msecs)d|%(process)d|%(thread)d|<%(name)s>'
               '|%(levelname)s|%(message)s')
    DATE_FMT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, log_level=None, cli=None):
        self.log_level = log_level
        self.cli = cli
        self.verify_logfile()
        if self.log_level is None:  self.log_level = logging.DEBUG
        if self.cli is None:  self.cli = True
        self.log = logging.getLogger(self.ref_class)
        self.log.setLevel(self.log_level)
        if len(self.log.handlers) == 0:  # make sure we don't dup handlers
            self.setup_logfile()
            if self.cli:  self.setup_cli()

    def setup_cli(self):
        cli = logging.StreamHandler()
        cli.setFormatter(self.ColoredFormatter(self.LOG_FMT, datefmt=self.DATE_FMT))
        self.log.addHandler(cli)

    def setup_logfile(self):
        f = logging.FileHandler(self.log_file)
        # want plain text in log files, so no colors here
        f.setFormatter(logging.Formatter(self.LOG_FMT, datefmt=self.DATE_FMT))
        self.log.addHandler(f)

    def verify_logfile(self):
        if os.path.isfile(self.log_file):  return
        f = open(self.log_file, 'w')
        f.write("")
        f.close()

    class ColoredFormatter(logging.Formatter):
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)        
        COLORS = {
            'INFO': GREEN,
            'DEBUG': BLUE,
            'WARNING': YELLOW,
            'CRITICAL': YELLOW,
            'ERROR': RED
        }
        # colored sequences in bash
        RESET_SEQ = '\033[0m'
        COLOR_SEQ = '\033[1;%dm'
        BOLD_SEQ = '\033[1m'

        def __init__(self, fmt, datefmt=None):
            process_str = '%(process)d'
            thread_str = '%(thread)d'
            fmt = fmt.replace(process_str, self._colorize(self.CYAN,
                                                          process_str))
            fmt = fmt.replace(thread_str, self._colorize(self.CYAN,
                                                         thread_str))
            logging.Formatter.__init__(self, fmt, datefmt=datefmt)

        def format(self, record):
            lvlname = record.levelname
            if lvlname in self.COLORS:
                lvlname_color = self._colorize(self.COLORS[lvlname], lvlname)
                record.levelname = lvlname_color
            return logging.Formatter.format(self, record)
        
        def _colorize(self, color, text):
            return self.COLOR_SEQ % (30 + color) + text + self.RESET_SEQ


class nback(Logger):

    # TODO(niklas):
    # * need to add better error handling, notification should run even
    #   though script crashes at some point (upload, db dump, .. etc)
    # * raise appropriate erros if e.g. AWS not connected when
    #   calling nback.upload() etc
    log_file = BACKUP_LOG_FILE
    ref_class = 'nback'
    filename = None
    filesize = None
    tmp_db_dir = None
    aws_conn = None
    aws_bucket = None
    # NOTE(niklas):
    # * if FILENAME_FMT is changed, need to change _get_backup_filename() also
    FILENAME_FMT = '%s-%s.tar.bz2'
    TMP_DB_DIR_FMT = 'nback-dbs-mysql-%s'
    TIMESTAMP_FMT = '%Y%m%d-%H%M'
    DB_OUTPUT_FILENAME = '%s/%s.sql'
    DB_DUMP_QUERY = '%s -u%s'
    DB_DUMP_QUERY_PASSWD = '%s -u%s -p%s'

    def __init__(self, *args, **kwargs):
        Logger.__init__(self, *args, **kwargs)
        self.filename = self.gen_filename()
        self.tmp_db_dir = self.gen_tmp_db_dir()
        self.log.debug('backup filename set to <%s>' % self.filename)
        self.log.debug('tmp database dir set to <%s>' % self.tmp_db_dir)
        self._tmp_db_names = []

    def gen_filename(self):
        return self.FILENAME_FMT % (BACKUP_SERVER_NAME, self._get_timestamp())

    def gen_tmp_db_dir(self):
        return self.TMP_DB_DIR_FMT % self._get_timestamp()

    def dump_mysql_databases(self):
        # TODO(niklas):
        # * if BACKUP_MYSQL_DBS is empty, backup all dbs
        os.makedirs(self.tmp_db_dir)
        if BACKUP_MYSQL_PASSWD == '':
            q = self.DB_DUMP_QUERY % (BACKUP_MYSQL_DUMP_CMD, BACKUP_MYSQL_USER)
        else:
            q = self.DB_DUMP_QUERY_PASSWD % (BACKUP_MYSQL_DUMP_CMD,
                                             BACKUP_MYSQL_USER,
                                             BACKUP_MYSQL_PASSWD)
        for db in BACKUP_MYSQL_DBS:
            tmp_db_filename = self.DB_OUTPUT_FILENAME % (self.tmp_db_dir, db)
            self._tmp_db_names.append(tmp_db_filename)
            self.log.debug('dumping db <%s> to <%s>..' % (db, tmp_db_filename))
            q_tmp = '%s %s > %s' % (q, db, tmp_db_filename)
            commands.getoutput(q_tmp)
        self.log.debug('dumped all dbs successfully')

    def tar_files(self):
        tar_file = tarfile.open(self.filename, 'w:bz2')
        for d in BACKUP_DIRS:
            self.log.debug('adding dir <%s>..' % d)
            tar_file.add(d)
        self.log.debug('adding db dir <%s>' % self.tmp_db_dir)
        tar_file.add(self.tmp_db_dir)
        tar_file.close()
        self.filesize = self.file_size_fmt(os.path.getsize(self.filename))
        self.log.debug('<%s> saved compressed, <%s>' % (self.filename,
                                                        self.filesize))

    def cleanup(self):
        os.remove(self.filename)
        for db_filename in self._tmp_db_names:
            os.remove(db_filename)
        os.rmdir(self.tmp_db_dir)
        self.log.debug('tmp files removed')

    def upload(self):
        k = boto.s3.key.Key(self.aws_bucket)
        k.key = '%s/%s' % (AWS_DIR, self.filename)
        self.log.debug('uploading...')
        k.set_contents_from_filename(self.filename)
        self.log.debug('upload successful')

    def sync(self):
        # TODO(nandersson):
        # * add some logic so we only get backups from this server here,
        #   e.g. match against server_name, suffix of 'tar.bz2' etc
        key_list = self.aws_bucket.list(prefix=AWS_DIR)
        for k in key_list:
            if self._get_backup_filename(k.key) == self.filename:  continue
            remove_file = True
            k_date = self._get_backup_date(k.key)
            k_day = k_date[6:8]  # fmt e.g.: 20130812
            if BACKUP_SAVE_EVERY_MONTH and k_day == '01':
                remove_file = False
            else:
                for i in range(BACKUP_DAYS_TO_STORE):
                    if k_date == self._get_timestamp('%Y%m%d', i):
                        remove_file = False
                        break
            if remove_file:
                k.delete()
                self.log.debug('removed outdated backup <%s>' % k.key)
        self.log.debug('everything in sync')

    def aws_connect(self):
        self.log.debug('connecting to AWS S3...')
        self.aws_conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        self.aws_bucket = self.aws_conn.get_bucket(AWS_BUCKET)
        self.log.debug('connected, bucket set to <%s>' % AWS_BUCKET)

    def aws_disconnect(self):
        self.aws_conn.close()
        self.log.debug('connection to AWS S3 closed')

    def send_notifications(self):
        timestamp = self._get_timestamp(fmt='%Y-%m-%d %H:%M')
        subject = 'Backup %s successful <%s>' % (BACKUP_SERVER_NAME, timestamp)
        body = ('%s\n\n%s\nTotal filesize: %s\nDatabases: %d'
                % (subject, self.filename, self.filesize,
                   len(BACKUP_MYSQL_DBS)))
        for email in BACKUP_NOTIFICATION_CONTACTS:
            self.log.debug('sending notification to <%s>..' % email)
            self.send_mail(email, subject, body)
        self.log.debug('all notifications sent')

    def run(self):
        self.log.info('running backup <%s>...' % BACKUP_SERVER_NAME)
        self.log.info('dumping databases...')
        self.dump_mysql_databases()
        self.log.info('taring files...')
        self.tar_files()
        self.log.info('uploading...')
        self.aws_connect()
        self.upload()
        self.log.info('syncing backups...')
        self.sync()
        self.aws_disconnect()
        self.log.info('cleaning up...')
        self.cleanup()
        self.log.info('sending notifications...')
        self.send_notifications()

    @staticmethod
    def _get_backup_filename(path):
        filename = path.split('/')
        return filename[len(filename)-1]

    @staticmethod
    def _get_backup_date(path):
        file_day = nback._get_backup_filename(path).split('-')
        if len(file_day) == 0:  return None
        return file_day[len(file_day)-2]

    @staticmethod
    def _get_timestamp(fmt=None, days_back=0):
        if fmt is None:  fmt = nback.TIMESTAMP_FMT
        date = datetime.datetime.now() - datetime.timedelta(days=days_back)
        return str(date.strftime(fmt))

    @staticmethod
    def file_size_fmt(bytes, precision=0):
        ''' Returns an humanized string for a given amount of bytes '''
        iden = ('B', 'KB', 'MB', 'GB', 'TB','PB', 'EB', 'ZB', 'YB')
        bytes = int(bytes)
        if bytes is 0:  return '0B'
        log = math.floor(math.log(bytes, 1024))
        return '%.*f%s' % (precision, bytes / math.pow(1024, log),
                           iden[int(log)])

    @staticmethod
    def send_mail(to, subject, body, host=None, sender=None):
        if host is None:  host = 'localhost'
        if sender is None:  sender = BACKUP_NOTIFICATION_FROM
        headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, to, subject)   
        smtp = smtplib.SMTP(host)
        smtp.sendmail(sender, to, (headers + body))
        smtp.quit()

if __name__ == '__main__':
    nback().run()
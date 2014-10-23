
import os

import lib.db.mongodb as mongodb_dump
import lib.db.mysql as mysql_dump
import lib.logger as logger
import lib.notification as notification
import lib.utils as utils
import lib.storage.aws_s3 as aws_s3
import settings


class Backup(logger.Logger):

    # TODO(niklas9):
    # * need to add better error handling, notification should run even
    #   though script crashes at some point (upload, db dump, .. etc)
    # * remove usage of os.system and use subprocess instead
    log_file = settings.BACKUP_LOG_FILE
    ref_class = 'nback'
    filename = None
    filesize = None
    dbs = None
    FILENAME_FMT = '%s-%s.tar.%s'
    NOTI_TIMESTAMP_FMT = '%Y-%m-%d %H:%M'
    TAR_BIN = '/bin/tar'
    GZIP_SUFFIX = 'gz'
    BZIP2_SUFFIX = 'bz2'

    def __init__(self, *args, **kwargs):
        logger.Logger.__init__(self, *args, **kwargs)
        self.filename = self.gen_filename()
        self.log.debug('backup filename set to <%s>' % self.filename)
        # init dbs
        self.dbs = []
        if settings.USE_MONGODB:
            self.dbs.append(mongodb_dump.MongoDBDump())
        if settings.USE_MYSQL:
            self.dbs.append(mysql_dump.MySQLDump())

    def dump_dbs(self):
        if len(self.dbs) == 0:
            self.log.warn('no databases setup to run, skipping..')
            return
        for db in self.dbs:
            db.dump()

    def tar_files(self):
        # TODO(nandersson):
        # * add support for xz compression
        # * refactor this method, magic variables, more helper methods etc
        self.log.info('taring and compressing files...')
        self.log.debug('compressing with <%s>' %
                       settings.BACKUP_COMPRESSION_ALGO)
        tar_arg_comp = 'z'
        if settings.BACKUP_COMPRESSION_ALGO == self.BZIP2_SUFFIX:
            tar_arg_comp = 'j'
        tar_args = '-c%sf' % tar_arg_comp
        cmd_raw = '%s %s %s'
        if settings.BACKUP_TAR_IGNORE_FAILED_READ:
            cmd_raw = '%s --ignore-failed-read %s %s'
        if len(settings.BACKUP_DIRS_EXCLUDE) > 0:
            for ed in settings.BACKUP_DIRS_EXCLUDE:
                cmd_raw += ' --exclude=\'%s\'' % ed
        cmd = cmd_raw % (self.TAR_BIN, tar_args, self.filename)
        dirs = []
        for d in settings.BACKUP_DIRS:
            self.log.debug('adding dir <%s>..' % d)
            dirs.append(d)
        for db in self.dbs:
            self.log.debug('adding db dir <%s>..' % db.get_tmp_dir())
            dirs.append(db.get_tmp_dir())
        # put cmd string together with dirs
        for d in dirs:  cmd += ' %s' % d
        if len(dirs) == 0:
            self.log.warn('no dirs to backup, proceeding..')
            return
        self.log.debug('executing cmd <%s>..' % cmd)
        os.system(cmd)
        self.log.debug('cmd complete')
        self.filesize = utils.file_size_fmt(os.path.getsize(self.filename))
        self.log.debug('<%s> saved compressed, <%s>' % (self.filename,
                                                        self.filesize))

    def upload_and_sync(self):
        # TODO(niklas9):
        # * add base class wrapper for storage, just straight to AWS S3 for now
        self.log.info('uploading...')
        s3 = aws_s3.AWSS3(settings.AWS_BUCKET, settings.AWS_ACCESS_KEY_ID,
                          settings.AWS_SECRET_ACCESS_KEY)
        s3.connect()
        s3.upload(self.filename)
        self.log.info('syncing...')
        s3.sync(self.filename)
        s3.disconnect()

    def gen_filename(self):
        return self.FILENAME_FMT % (settings.BACKUP_SERVER_NAME,
                                    utils.get_timestamp(),
                                    settings.BACKUP_COMPRESSION_ALGO)

    def cleanup(self):
        self.log.info('cleaning up...')
        for db in self.dbs:
            db.cleanup()
        os.remove(self.filename)
        self.log.debug('tmp files removed')

    def send_notifications(self):
        # TODO(niklas9):
        # * make all magic values here part of settings or smth
        timestamp = utils.get_timestamp(fmt=self.NOTI_TIMESTAMP_FMT)
        subject = 'Backup %s successful <%s>' % (settings.BACKUP_SERVER_NAME,
                                                 timestamp)
        body = ('%s\n\n%s\nTotal filesize: %s\nDatabases: %d'
                % (subject, self.filename, self.filesize,
                   len(settings.BACKUP_MYSQL_DBS)))
        for email in settings.EMAIL_CONTACTS:
            self.log.debug('sending notification to <%s>..' % email)
            notification.Email.send(email, subject, body)
        self.log.debug('all notifications sent')

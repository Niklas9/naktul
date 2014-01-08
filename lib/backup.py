
import os
import tarfile

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
    log_file = settings.BACKUP_LOG_FILE
    ref_class = 'nback'
    filename = None
    filesize = None
    dbs = None
    # NOTE(niklas9):
    # * if FILENAME_FMT is changed, need to change _get_backup_filename() also
    FILENAME_FMT = '%s-%s.tar.' + settings.BACKUP_COMPRESSION_ALGO
    NOTI_TIMESTAMP_FMT = '%Y-%m-%d %H:%M'

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
        # TODO(niklas):
        # * see how the basic Linux cmd 'tar' and 'bzip2' performs
        #   compares to this Python native lib.. it seems slow as it is
        #   now..
        self.log.info('taring files...')
        mode = 'w:%s' % settings.BACKUP_COMPRESSION_ALGO
        tar_file = tarfile.open(self.filename, mode=mode)
        for d in settings.BACKUP_DIRS:
            self.log.debug('adding dir <%s>..' % d)
            tar_file.add(d)
        for db in self.dbs:
            self.log.debug('adding db dir <%s>..' % db.get_tmp_dir())
            tar_file.add(db.get_tmp_dir())
        tar_file.close()
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
                                    utils.get_timestamp())

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

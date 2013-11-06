
import boto

import lib.logger as logger
import lib.utils as utils
import settings


class AWSS3(logger.Logger):

    FIRST_DAY_OF_MONTH = '01'

    log_file = settings.BACKUP_LOG_FILE
    ref_class = 'aws-s3'
    conn = None
    bucket = None
    bucket_name = None
    access_key = None
    secret_access_key = None

    def __init__(self, bucket_name, access_key, secret_access_key):
        logger.Logger.__init__(self)
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_access_key = secret_access_key

    def connect(self):
        self.log.debug('connecting to AWS S3...')
        self.conn = boto.connect_s3(self.access_key, self.secret_access_key)
        self.bucket = self.conn.get_bucket(self.bucket_name)
        self.log.debug('connected, bucket set to <%s>' % self.bucket_name)

    def disconnect(self):
        self.conn.close()
        self.log.debug('connection to AWS S3 closed')

    def upload(self, filename):
        filepath = '%s/%s' % (settings.AWS_DIR, filename)
        k = boto.s3.key.Key(self.bucket)
        k.key = filepath
        self.log.debug('uploading...')
        k.set_contents_from_filename(filename)
        self.log.debug('upload successful')

    def sync(self, filename):
        # TODO(nandersson):
        # * add some logic so we only get backups from this server here,
        #   e.g. match against server_name, suffix of 'tar.bz2' etc
        key_list = self.bucket.list(prefix=settings.AWS_DIR)
        for k in key_list:
            if self._get_backup_filename(k.key) == filename:  continue
            remove_file = True
            k_date = self._get_backup_date(k.key)
            k_day = k_date[6:8]  # fmt e.g.: 20130812
            remove_file = not (settings.BACKUP_SAVE_EVERY_MONTH and
                               k_day == self.FIRST_DAY_OF_MONTH)
            if remove_file:
                for i in range(settings.BACKUP_DAYS_TO_STORE):
                    if k_date == utils.get_timestamp('%Y%m%d', i):
                        remove_file = False
                        break
            if remove_file:
                k.delete()
                self.log.debug('removed outdated backup <%s>' % k.key)
        self.log.debug('everything in sync')

    @staticmethod
    def _get_backup_filename(path):
        path_tree = path.split('/')
        return path_tree[len(path_tree)-1]

    @staticmethod
    def _get_backup_date(path):
        file_day = AWSS3._get_backup_filename(path).split('-')
        if len(file_day) == 0:  return None
        return file_day[len(file_day)-2]
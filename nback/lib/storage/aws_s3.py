
import boto
import glob
import os

import nback.lib.logger as logger
import nback.lib.utils as utils
import nback.settings as settings


class AWSS3(logger.Logger):

    FIRST_DAY_OF_MONTH = '01'
    MB_IN_BYTES = 1049000
    MULTIPART_UPLOAD_CHUNK_SIZE = 250 * MB_IN_BYTES
    SPLIT_FILES_CMD = 'split -b %d %s %s'
    FILES_ALL_PREFIX = '%s*'

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

    def upload(self, src):
        dest = '%s/%s' % (settings.AWS_DIR, src)
        src_file_size = os.path.getsize(src)
        k = boto.s3.key.Key(self.bucket)
        k.key = dest
        self.log.debug('created S3 key %r' % k)
        self.log.debug('source filesize is <%d> bytes' % src_file_size)
        if src_file_size < self.MULTIPART_UPLOAD_CHUNK_SIZE:
            self._standard_transfer(k, src, dest)
        else:
            self._multipart_transfer(k, src, src_file_size, dest)

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

    def _standard_transfer(self, key, src, dest):
        self.log.debug('uploading...')
        key.set_contents_from_filename(src)
        self.log.debug('upload successful')

    def _multipart_transfer(self, key, src, src_file_size, dest):
        # TODO(nandersson):
        # * should be able to parallelize this, one for each core for example,
        #   to increase throughput (upload parts at the same time)
        # NOTE(nandersson):
        # * max filesize for a PUT request to AWS S3 API is 5GB, so need to
        #   split it up for files larger than that.. uploading in chunks of size
        #   set in self.MULTIPART_UPLOAD_CHUNK_SIZE
        self.log.debug('uploading using multipart...')
        chunks = (src_file_size / self.MULTIPART_UPLOAD_CHUNK_SIZE) + 1
        self.log.debug('splitting <%d> bytes in <%d> chunks of max <%d> bytes'
                       % (src_file_size, chunks,
                          self.MULTIPART_UPLOAD_CHUNK_SIZE))
        files = self._split_file(src, src_file_size,
                                 self.MULTIPART_UPLOAD_CHUNK_SIZE)
        mp = self.bucket.initiate_multipart_upload(key)
        for i, filename in enumerate(files):
            f = open(filename, 'r')
            self.log.debug('uploading chunk <%d>, part file <%s>..'
                           % (i+1, filename))
            mp.upload_part_from_file(f, i+1)
            f.close()
            os.remove(filename)
        mp.complete_upload()
        self.log.debug('upload successful')

    @staticmethod
    def _split_file(path, chunks, chunk_bytes):
        # TODO(nandersson):
        # * might want to move this to a more general file class
        os.system(AWSS3.SPLIT_FILES_CMD % (chunk_bytes, path, path))
        splitted_files = glob.glob(AWSS3.FILES_ALL_PREFIX % path)
        splitted_files.remove(path)
        return sorted(splitted_files)

    @staticmethod
    def _get_backup_filename(path):
        path_tree = path.split('/')
        return path_tree[len(path_tree)-1]

    @staticmethod
    def _get_backup_date(path):
        file_day = AWSS3._get_backup_filename(path).split('-')
        if len(file_day) == 0:  return None
        return file_day[len(file_day)-2]

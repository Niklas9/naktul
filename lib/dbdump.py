
# NOTE(niklas9):
# * base class for dbs

import os

import lib.logger as logger
import lib.utils as utils
import settings


class DBDump(logger.Logger):

    tmp_dir = None
    tmp_files = None
    log_file = settings.BACKUP_LOG_FILE
    ref_class = 'dbdump'

    def create_tmp_dir(self):
        # NOTE(niklas9)
        # * it's up to the client to make sure this method is called when ready
        os.makedirs(self.tmp_dir)

    def rm_tmp_dir(self):
        os.rmdir(self.tmp_dir)

    def dump(self):
        raise NotImplementedError

    def get_tmp_dir(self):
        return self.tmp_dir

    def gen_tmp_dir(self, path_fmt):
        return path_fmt % utils.get_timestamp()

    def cleanup(self, skip_tmp_files=False):
        if not skip_tmp_files and self.tmp_files is not None:
            for f in self.tmp_files:
                os.remove(f)
        self.rm_tmp_dir()
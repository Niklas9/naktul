
# TODO(niklas9):
# * add support for mongodb user authentication

import commands
import os

import nback.lib.dbdump as dbdump
import nback.settings as settings


class MongoDBDump(dbdump.DBDump):

    DUMP_QUERY = '--db %s -o %s'
    DUMP_CMD = '/usr/bin/mongodump'
    TMP_DIR_FMT = 'nback-dbs-mongodb-%s'

    db_path = None

    def __init__(self):
        dbdump.DBDump.__init__(self)
        self.tmp_dir = self.gen_tmp_dir(self.TMP_DIR_FMT)
        self.log.debug('tmp mongodb dir set to <%s>' % self.tmp_dir)
        self.create_tmp_dir()
        self.tmp_files = []
        self.db_path = self.tmp_dir +'/%s'

    def dump(self):
        self.log.debug('dumping mongodb dbs...')
        q = '%s %s' % (self.DUMP_CMD, self.DUMP_QUERY)
        for db in settings.BACKUP_MONGODB_DBS:
           self.log.debug('dumping db <%s>...' % db)
           query = q % (db, self.tmp_dir)
           commands.getoutput(query)
           self._add_to_tmp_files(self.db_path % db)
        self.log.debug('dumped all mongodb dbs successfully')

    def cleanup(self):    
        for f in self.tmp_files:
            os.remove(f)
        for db in settings.BACKUP_MONGODB_DBS:
            os.rmdir(self.db_path % db)
        super(MongoDBDump, self).cleanup(skip_tmp_files=True)

    def _add_to_tmp_files(self, db_dump_path):
        files = os.listdir(db_dump_path)
        for f in files:
            filepath = '%s/%s' % (db_dump_path, f)
            self.tmp_files.append(filepath)

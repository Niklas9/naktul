
import commands
import os

import nback.lib.dbdump as dbdump
import nback.settings as settings


class PostgreSQLDump(dbdump.DBDump):

    OUTPUT_FILENAME = '%s/%s.sql'
    DUMP_QUERY = '%s -h%s -U%s'
    DUMP_QUERY_OUTPUT = '%s %s > %s'
    TMP_DIR_FMT = 'nback-dbs-postgresql-%s'
    DUMP_CMD = '/usr/bin/pg_dump'

    def __init__(self):
        dbdump.DBDump.__init__(self)
        self.tmp_dir = self.gen_tmp_dir(self.TMP_DIR_FMT)
        self.log.debug('tmp postgresql dir set to <%s>' % self.tmp_dir)
        self.create_tmp_dir()
        self.tmp_files = []

    def dump(self):
        # TODO(niklas):
        # * if BACKUP_POSTGRESQL_DBS is empty, backup all dbs
        # * should listen to pg_dump exit status, if e.g. password is
        #   incorrect, it continues as nothing happens with a 0 byte
        #   database dump
        # * remove environment variable for password here? is this a security
        #   risk?
        os.environ['PGPASSWORD'] = settings.BACKUP_POSTGRESQL_PASSWD
        self.log.debug('dumping postgresql dbs...')
        q = self._get_dump_query()
        for db in settings.BACKUP_POSTGRESQL_DBS:
            tmp_db_filename = self.OUTPUT_FILENAME % (self.tmp_dir, db)
            self.tmp_files.append(tmp_db_filename)
            self.log.debug('dumping db <%s> to <%s>..' % (db, tmp_db_filename))
            q_tmp = self.DUMP_QUERY_OUTPUT % (q, db, tmp_db_filename)
            self.log.debug('dump command <%s>' % q_tmp)
            commands.getoutput(q_tmp)
        self.log.debug('dumped all postgresql dbs successfully')

    @staticmethod
    def _get_dump_query():
        user = settings.BACKUP_POSTGRESQL_USER
        return PostgreSQLDump.DUMP_QUERY % (PostgreSQLDump.DUMP_CMD,
                                         settings.BACKUP_POSTGRESQL_HOST, user)

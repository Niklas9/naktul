
import commands
import os

import lib.dbdump as dbdump
import settings


class MySQLDump(dbdump.DBDump):

    OUTPUT_FILENAME = '%s/%s.sql'
    DUMP_QUERY = '%s -u%s'
    DUMP_QUERY_PASSWD = '%s -u%s -p%s'
    DUMP_QUERY_OUTPUT = '%s %s > %s'
    TMP_DIR_FMT = 'nback-dbs-mysql-%s'
    DUMP_CMD = '/usr/bin/mysqldump'

    def __init__(self):
        dbdump.DBDump.__init__(self)
        self.tmp_dir = self.gen_tmp_dir(self.TMP_DIR_FMT)
        self.log.debug('tmp mysql dir set to <%s>' % self.tmp_dir)
        self.create_tmp_dir()
        self.tmp_files = []

    def dump(self):
        # TODO(niklas):
        # * if BACKUP_MYSQL_DBS is empty, backup all dbs
        # * should listen to mysqldumps exit status, if e.g. password is
        #   incorrect, it continues as nothing happens with a 0 byte
        #   database dump
        self.log.debug('dumping mysql dbs...')
        q = self._get_dump_query()
        for db in settings.BACKUP_MYSQL_DBS:
            tmp_db_filename = self.OUTPUT_FILENAME % (self.tmp_dir, db)
            self.tmp_files.append(tmp_db_filename)
            self.log.debug('dumping db <%s> to <%s>..' % (db, tmp_db_filename))
            q_tmp = self.DUMP_QUERY_OUTPUT % (q, db, tmp_db_filename)
            commands.getoutput(q_tmp)
        self.log.debug('dumped all mysql dbs successfully')

    @staticmethod
    def _get_dump_query():
        user = settings.BACKUP_MYSQL_USER
        passwd = settings.BACKUP_MYSQL_PASSWD
        if settings.BACKUP_MYSQL_PASSWD == '':
            return MySQLDump.DUMP_QUERY % (MySQLDump.DUMP_CMD, user)
        return MySQLDump.DUMP_QUERY_PASSWD % (MySQLDump.DUMP_CMD, user, passwd)
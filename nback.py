#!/usr/bin/python

import lib.backup as backup
import settings


class nback(backup.Backup):

    def run(self):
        self.dump_dbs()
        self.tar_files()
        self.upload_and_sync()
        self.cleanup()
        self.send_notifications()


if __name__ == '__main__':
    nback().run()
nback
=====

Backups files and databases (MySQL) to AWS S3

version 1.0 2013-08-19
author: nandersson900@gmail.com


Features
--------

    * backups any given files/directories
    * uses mysqldump to take complete SQL dump of all databases
    * saves backups for 7 days back and the first of every month indefinitely
    * uses the bzip2 compression algorithm for the smallest possible footprint
    # notifies any given email address every time backup is done
    * use bash shell for prettier log coloring


System requirements
-------------------
    * *nix-like environment
    * bzip2
    * Python >= 2.7.3 (only dep. python-boto)
    * MySQL >= 5.0


Getting started
---------------
    * edit top of nback.py with your settings/credentials
    * add a job to your crontab, and set it to run as often as you want backups
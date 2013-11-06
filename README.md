nback
=====

Backups files and databases (MySQL and MongoDB) to AWS S3

version 1.1 2013-11-06

author: nandersson900@gmail.com


Features
--------

  - backups any given files/directories
  - uses mysqldump to take complete SQL dump of all mysql dbs
  - uses mongodump to take complete BSON dump of all mongodb dbs
  - saves backups for 7 days back and the first of every month indefinitely
  - uses the bzip2 compression algorithm for the smallest possible footprint
  - notifies any given email address every time backup is done
  - use bash shell for prettier log coloring


System requirements
-------------------

It might work with other versions of the software given below,
however this is what I've tested with.

  - *nix-like environment
  - bzip2
  - Python >= 2.7.3 (only dep. python-boto)
  - MySQL >= 5.0 (optional)
  - MongoDB >= 2.0.4 (optional)


Getting started
---------------
  - edit settings.py with your settings/credentials
  - add a job to your crontab, and set it to run as often as you want backups
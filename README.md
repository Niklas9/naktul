naktul
======

![Naktul](https://vignette3.wikia.nocookie.net/starcraft/images/9/91/Naktul_SC2-HotS_Head1.jpg/revision/latest?cb=20150525032620 "Naktul")

Naktul is a tool that backups files and databases (MySQL, PostgreSQL, MongoDB)
to AWS S3.

It's named after the beautiful zerg broodmother character in Starcraft II:
Heart of the Swarm.

Features
--------

  - backups any given files/directories
  - uses mysqldump to take complete SQL dump of all mysql dbs
  - uses pg_dump to take complete SQL dump of all postgresql dbs
  - uses mongodump to take complete BSON dump of all mongodb dbs
  - saves backups for 7 days back and the first of every month indefinitely
  - choose between gzip and bzip2 compression algorithms for fastest or
    smallest possible footprint
  - notifies any given email address every time backup is done
  - use bash shell for prettier log coloring


System requirements
-------------------

It might work with other versions of the software given below,
however this is what I've tested with.

  - *nix-like environment
  - bzip2 or gzip
  - Python >= 2.7.3 (only dep. python-boto)
  - MySQL >= 5.0 (optional)
  - PostgreSQL >= 9.3 (optional)
  - MongoDB >= 2.0.4 (optional)


Getting started
---------------

  - install python-boto if you haven't already (on Debian/Ubuntu, $ sudo
    apt-get install python-boto)
  - edit settings.py with your settings/credentials
  - add a job to your crontab, and set it to run as often as you want backups

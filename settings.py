
# Backup settings
BACKUP_SERVER_NAME = 'server-name'
BACKUP_DIRS = ('/var/www',)
BACKUP_DAYS_TO_STORE = 7  # number of days
BACKUP_SAVE_EVERY_MONTH = True  # stores the backup from the first every month
USE_MYSQL = True
BACKUP_MYSQL_DBS = ('test',)
BACKUP_MYSQL_HOST = 'localhost'
BACKUP_MYSQL_USER = 'root'
BACKUP_MYSQL_PASSWD = ''
USE_MONGODB = True
BACKUP_MONGODB_DBS = ('test',)
BACKUP_NOTIFICATION_FROM = 'info@example.com'
BACKUP_NOTIFICATION_CONTACTS = ('your@email.com',)
BACKUP_LOG_FILE = 'nback.log'

# Amazon AWS S3 settings
AWS_BUCKET = 'servers'
AWS_DIR = 'backups/%s' % BACKUP_SERVER_NAME
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
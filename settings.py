# Backup settings
BACKUP_SERVER_NAME = 'server-name'
BACKUP_DIRS = ('/var/www',)
BACKUP_DAYS_TO_STORE = 7  # number of days
BACKUP_SAVE_EVERY_MONTH = True  # stores the backup from the first every month
BACKUP_LOG_FILE = 'nback.log'
BACKUP_COMPRESSION_ALGO = 'bz2'  # viable options: 'bz2', 'gz'

# MySQL database
USE_MYSQL = True
BACKUP_MYSQL_DBS = ('test',)
BACKUP_MYSQL_HOST = 'localhost'
BACKUP_MYSQL_USER = 'root'
BACKUP_MYSQL_PASSWD = ''

# MongoDB database
USE_MONGODB = True
BACKUP_MONGODB_DBS = ('test',)

# Notification settings
EMAIL_FROM = 'info@example.com'
EMAIL_CONTACTS = ('your@email.com',)
EMAIL_USE_TLS = True
EMAIL_TLS_PORT = 587
SMTP_HOST = 'localhost'
SMTP_USERNAME = ''
SMTP_PASSWD = ''

# Amazon AWS S3 settings
AWS_BUCKET = 'servers'
AWS_DIR = 'backups/%s' % BACKUP_SERVER_NAME
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

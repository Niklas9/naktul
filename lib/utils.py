
import datetime
import math

TIMESTAMP_FMT = '%Y%m%d-%H%M'
FILESIZE_IDENT = ('B', 'KB', 'MB', 'GB', 'TB','PB', 'EB', 'ZB', 'YB')
FILESIZE_ZERO = 'OB'
FILESIZE_FMT = '%.*f%s'
FILESIZE_1KB = 1024

def get_timestamp(fmt=None, days_back=0):
    if fmt is None:  fmt = TIMESTAMP_FMT
    date = datetime.datetime.now() - datetime.timedelta(days=days_back)
    return str(date.strftime(fmt))

def file_size_fmt(bytes, precision=0):
    ''' Returns a humanized string for a given amount of bytes '''
    bytes = int(bytes)
    if bytes is 0:  return FILESIZE_ZERO
    log = math.floor(math.log(bytes, FILESIZE_1KB))
    return FILESIZE_FMT % (precision, bytes / math.pow(FILESIZE_1KB, log),
                           FILESIZE_IDENT[int(log)])
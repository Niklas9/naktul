
import smtplib

import settings


class Email(object):

    MSG_FMT = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
    DEFAULT_SMTP_HOST = 'localhost'

    @staticmethod
    def send(to, subject, body, host=None, sender=None):
        if host is None:  host = Email.DEFAULT_SMTP_HOST
        if sender is None:  sender = settings.BACKUP_NOTIFICATION_FROM
        headers = Email.MSG_FMT % (sender, to, subject)
        try:
            smtp = smtplib.SMTP(host)
        except:
            pass
        else:
            smtp.sendmail(sender, to, (headers + body))
            smtp.quit()

import smtplib

import settings


class Email(object):

    MSG_FMT = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
    DEFAULT_SMTP_PORT = 25

    @staticmethod
    def send(to, subject, body, sender=None, host=None, port=None,
             username=None, passwd=None, use_tls=None):
        if sender is None:  sender = settings.EMAIL_FROM
        if host is None:  host = settings.SMTP_HOST
        if username is None:  username = settings.SMTP_USERNAME
        if passwd is None:  passwd = settings.SMTP_PASSWD
        if use_tls is None:  use_tls = settings.EMAIL_USE_TLS
        if port is None and use_tls:  port = settings.EMAIL_TLS_PORT
        if port is None:  port = self.DEFAULT_SMTP_PORT
        headers = Email.MSG_FMT % (sender, to, subject)
        smtp = smtplib.SMTP(host, port=port)
        if use_tls:
            smtp.starttls()
        if username is not None and passwd is not None:
            smtp.login(username, passwd)
        smtp.sendmail(sender, to, (headers + body))
        smtp.quit()

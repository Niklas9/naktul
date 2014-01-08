
import smtplib

import settings


class Email(object):

    MSG_FMT = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
    DEFAULT_SMTP_PORT = 25

    # TODO(niklas9):
    # * should log when failing on either try/except case below

    @staticmethod
    def send(to, subject, body, sender=None, host=None, port=None,
             username=None, passwd=None, use_tls=None):
        if sender is None:  sender = settings.EMAIL_FROM
        if host is None:  host = settings.MSTP_HOST
        if username is None:  username = settings.EMAIL_USERNAME
        if passwd is None:  passwd = settings.EMAIL_PASSWD
        if use_tls is None:  use_tls = settings.EMAIL_USE_TLS
        if port is None and use_tls:  port = settings.EMAIL_TLS_PORT
        if port is None:  port = DEFAULT_SMTP_PORT
        headers = Email.MSG_FMT % (sender, to, subject)
        try:
            smtp = smtplib.SMTP(host, port=port)
        except:
            return
        if use_tls:
            try:
                smtp.starttls()
            except:
                pass
        if username is not None and password is not None:
            try:
                smtp.login(username, password)
            except:
                pass
        smtp.sendmail(sender, to, (headers + body))
        smtp.quit()

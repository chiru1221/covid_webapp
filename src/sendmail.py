import smtplib
from email.mime.text import MIMEText

def send(from_address, to_address, message, title, cc=None):
    msg = MIMEText(message)
    msg['Subject'] = title
    msg['From'] = from_address
    if cc is not None:
        msg['Cc'] = cc
    msg['To'] = to_address

    try:
        smtp = smtplib.SMTP()
        smtp.connect()
        smtp.sendmail(from_address, to_address, msg.as_string())
        smtp.close()
    except:
        return 1
    return 0

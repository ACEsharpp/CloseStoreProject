import smtplib
from os.path import basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send(to_address, subject, text):
    from_add = 'i_kuanysh@inbox.ru'
    to_add = to_address
    subject = subject
    text = text

    msg = MIMEMultipart()
    msg['From'] = from_add
    msg['To'] = to_add
    msg['Subject'] = subject
    body = MIMEText(text, 'plain')
    msg.attach(body)
    server = smtplib.SMTP('smtp.mail.ru', port=587)
    server.connect("smtp.mail.ru",587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(from_add,'ps1GBgykmpCRL6gbzMwE')
    server.send_message(msg, from_addr=from_add, to_addrs=[to_add])
    server.quit()

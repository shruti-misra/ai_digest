import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import markdown

load_dotenv()

class EmailSender:
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body
        self.sender = os.environ["SENDER_EMAIL"]
        self.password = os.environ["PASSWORD"].replace('\xa0', '').replace(' ', '')
        self.receivers = [os.environ["RECEIVER_EMAIL"]]

    def send_email(self):
        html_body = markdown.markdown(self.body)
        msg = MIMEMultipart("alternative")

        msg['Subject'] = self.subject
        msg['From'] = formataddr(("Weekly AI Digest", self.sender))
        msg['To'] = ', '.join(self.receivers)

        part = MIMEText(html_body, 'html')
        msg.attach(part)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(self.sender, self.password)
            smtp_server.sendmail(self.sender, self.receivers, msg.as_string())
        print("Message sent!")

if __name__ == "__main__":

    subject = "Testing class"
    body = """
    # Hello from Python!
    This is a **bold** statement, and this is *italic*.

    - Bullet point 1
    - Bullet point 2

    [Visit Google](https://google.com)
    """
    email = EmailSender(subject, body)
    email.send_email()

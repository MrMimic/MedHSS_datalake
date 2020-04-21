import email
import imaplib
import os
import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Gmail(object):

    def __init__(self, email, password, server, port):

        self.email = email
        self.password = password
        self.server = server
        self.port = port

    def send_mail(self, corresponding, file_name, subject, text):
        """
        Uses server connected into the init to send mails

        :param corresponding: List of email to send mail to
        :type corresponding: list
        :param file_name: Path to the file to join
        :type file_name: str / None
        :param text: The text body
        :type text: str
        """

        server = smtplib.SMTP(self.server, self.port)
        server.starttls()
        server.login(self.email, self.password)

        # Write mail
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = corresponding
        msg['Subject'] = subject
        body = text
        msg.attach(MIMEText(body, 'plain'))
        # Add file
        if file_name is not None:
            attachment = open(file_name, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename = {}'.format(file_name))
            msg.attach(part)
        # Send
        text = msg.as_string()
        server.sendmail(self.email, corresponding, text)
        server.quit()

        print('Analysis sent back to {}'.format(corresponding))

    def read_last_mail(self):

        mail = imaplib.IMAP4_SSL(self.server)

        print('Connected to {}'.format(self.email))

        mail.login(self.email, self.password)
        mail.select('inbox')

        type, data = mail.search(None, 'ALL')
        mail_ids = data[0]

        id_list = mail_ids.split()
        latest_email_id = int(id_list[-1])

        typ, data = mail.fetch(str(latest_email_id), '(RFC822)')

        for response_part in data:
            if isinstance(response_part, tuple):

                msg = email.message_from_bytes(response_part[1])

                email_subject = msg['subject']
                email_from = re.findall('<.*?>', msg['from'])[0].replace('<', '').replace('>', '')

                email_time = re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2}', msg['date'])[0]

                print('Treating email received at {} from {}'.format(email_time, email_from))

        if 'EXE' not in email_subject:
            return email_from, email_subject, None

        for part in msg.walk():

            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue

            file_name = part.get_filename()

            if bool(file_name):
                file_path = os.path.join('input', file_name)
                if not os.path.isfile(file_path) :
                    with open(file_path, 'wb') as handler:
                        handler.write(part.get_payload(decode=True))

                print('Downloaded "{file}" from email titled "{subject}" with UID {uid}.'.format(file=file_name, subject=email_subject, uid=latest_email_id))

        return email_from, email_subject, file_path

    def read_pubmed_requests(self, file_path):
        with open(file_path, "r") as handler:
            pubmed_requests = handler.readlines()
        return pubmed_requests
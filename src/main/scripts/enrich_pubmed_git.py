from emails.gmail import Email
from monitoring.monitore_pubmed import Monitoring

mailer = Email(
    email="@gmail.com",
    password="",
    server='smtp.gmail.com',
    port=587)

email_from, email_subject, input_file_path = mailer.read_last_mail()

with open(input_file_path, "r") as handler:
    pubmed_requests = handler.readlines()

monitor = Monitoring()
for index, request in enumerate(pubmed_requests):

    file_path = monitor.launch_search(request=request, index=index+1)

    mailer.send_mail(
        corresponding=email_from,
        file_name=file_path,
        subject=f"#{index}",
        text="#")
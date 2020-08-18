#!/usr/bin/env python3
import os
import configparser

from monitoring.monitore_pubmed import Monitoring
from publication.publication import Publication
from emails.gmail import Gmail
from databases.sqlite import SQLite


# Read configuration
configuration = configparser.ConfigParser()
configuration.read(os.path.join("src", "main", "resources", "configuration.cfg"))
# Configure mailer
mailer = Gmail(email=configuration["account"]["mail"],
               password=configuration["account"]["pass"],
               server=configuration["account"]["server"],
               port=configuration["account"]["port"])

# Read last mail and associated requests
email_from, input_file_path = mailer.read_last_mail()
pubmed_requests = mailer.read_pubmed_requests(file_path=input_file_path)

# Launch a monitoring instance
monitor = Monitoring(configuration=configuration)

# For each request
for index, request in enumerate(pubmed_requests):
    # Write a local file
    file_path = monitor.launch_search(request=request, index=index + 1)
    # And send it back
    if os.path.isfile(file_path):
        mailer.send_mail(
            corresponding=email_from,
            file_name=file_path,
            subject=f"Auto analysis #{index + 1}",
            text="<3")

# Add daily scanned PMIDs
database = SQLite(configuration=configuration)
# Insert daily scanned PMIDs
database.insert_list_of_scanned_pmids(list(set(monitor.daily_scanned)))

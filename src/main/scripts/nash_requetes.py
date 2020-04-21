#!/usr/bin/env python3
import os
import configparser

from monitoring.monitore_pubmed import Monitoring
from publication.publication import Publication
from emails.gmail import Gmail

configuration = configparser.ConfigParser()
configuration.read(os.path.join("src", "main", "resources", "configuration.cfg"))

mailer = Gmail(email=configuration["account"]["mail"],
               password=configuration["account"]["pass"],
               server=configuration["account"]["server"],
               port=configuration["account"]["port"])

# email_from, email_subject, input_file_path = mailer.read_last_mail()
# pubmed_requests = mailer.read_pubmed_requests(file_path=input_file_path)

pubmed_requests = [
    '(((NASH[Title] OR non alcoholic fatty liver disease[Title] OR nonalcoholic fatty liver disease[Title] OR Non-alcoholic Fatty Liver Disease[Title] OR NAFLD[Title] OR nonalcoholic steatohepatitis[Title] OR Non alcoholic steatohepatitis[Title] OR "non alcoholic fatty liver disease"[MeSH Terms]) NOT "animals"[MH:NOEXP])) AND ("2019/11/05"[Date - Publication] : "3000"[Date - Publication])',
    '(((NASH[Title] OR non alcoholic fatty liver disease[Title] OR nonalcoholic fatty liver disease[Title] OR Non-alcoholic Fatty Liver Disease[Title] OR NAFLD[Title] OR nonalcoholic steatohepatitis[Title] OR Non alcoholic steatohepatitis[Title] OR "non alcoholic fatty liver disease"[MeSH Terms]) NOT (intestinal Microbiome[Title] OR gut microbiota[Title] OR "Gastrointestinal Microbiome"[MeSH Terms])) AND (lipotropic agents[Title/Abstract] OR fatty liver[Title/Abstract] OR liver cirrhosis[Title/Abstract] OR liver diseases[Title/Abstract] OR (fibrosis[Title/Abstract] AND liver)) AND ("diabetes mellitus"[MeSH Terms] OR "diabetes mellitus"[Title/Abstract] OR "diabetes"[Title/Abstract] OR "insulin resistance"[Title/Abstract] OR "insulin resistance"[MeSH Terms]) NOT "animals"[MH:NOEXP]) AND ("2019/11/05"[Date - Publication] : "3000"[Date - Publication])',
    '(((NASH[Title] OR non alcoholic fatty liver disease[Title] OR nonalcoholic fatty liver disease[Title] OR Non-alcoholic Fatty Liver Disease[Title] OR NAFLD[Title] OR nonalcoholic steatohepatitis[Title] OR Non alcoholic steatohepatitis[Title] OR "non alcoholic fatty liver disease"[MeSH Terms]) NOT (intestinal Microbiome[Title] OR gut microbiota[Title] OR "Gastrointestinal Microbiome"[MeSH Terms])) AND (Drug Induced Liver Disease [Title/Abstract] OR "Chemical and Drug Induced Liver Injury"[MeSH Terms] OR "liver diseases/chemically induced"[MeSH Terms] OR liver diseases chemically induced[Title/Abstract] OR "peroxisome proliferator-activated receptors"[MeSH Terms] OR PPAR[Title/Abstract] OR peroxisome proliferator activated receptors[Title/Abstract]) NOT "animals"[MH:NOEXP]) AND ("2019/11/05"[Date - Publication] : "3000"[Date - Publication])'
]

monitor = Monitoring(configuration=configuration)

exit(0)

for index, request in enumerate(pubmed_requests):

    file_path = monitor.launch_search(request=request, index=index+1)

    mailer.send_mail(
        corresponding=email_from,
        file_name=file_path,
        subject=f"Auto analysis #{index}",
        text="<3")

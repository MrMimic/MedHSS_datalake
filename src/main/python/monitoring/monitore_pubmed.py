import os
from enrichment.pubmication import Publication
from bs4 import BeautifulSoup as BS
import requests
import datetime as dt
import tqdm
import pandas as pd


class Monitoring(object):

    def __init__(self):
        self.already_scanned_file = os.path.join('resources', 'already_scanned.csv')
        try:
            self.already_scanned = pd.read_csv(self.already_scanned_file, header=None).iloc[:, 0].tolist()
        except pd.errors.EmptyDataError:
            self.already_scanned = []

    def launch_search(self, request, index):
        """
        Launch a request on PubMed
        """
        request = request.replace(' ', '+')
        file_name = '{}_{}_{}.csv'.format(
            index,
            dt.datetime.now().strftime('%Y-%m-%d'),
            request.replace(' ', '_')[:50]
        )
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&datetype=pdat&retmax=100000&term={}'.format(
            request
        )
        data = BS(requests.get(url).text, 'lxml')
        pmids = data.find_all('id')
        for pmid in tqdm.tqdm(pmids):
            pmid = pmid.text
            if int(pmid) not in self.already_scanned:
                publication = Publication(pmid=pmid)
                publication.get_data()
                publication.write_data(os.path.join('output', file_name))
                self.already_scanned.append(pmid)
        print()

        self.already_scanned = list(set(self.already_scanned))
        pd.DataFrame(self.already_scanned).to_csv(self.already_scanned_file, index=False, header=None)

if __name__ == '__main__':
    pubmed_requests = [
        '(((NASH[Title] OR non alcoholic fatty liver disease[Title] OR nonalcoholic fatty liver disease[Title] OR Non-alcoholic Fatty Liver Disease[Title] OR NAFLD[Title] OR nonalcoholic steatohepatitis[Title] OR Non alcoholic steatohepatitis[Title] OR "non alcoholic fatty liver disease"[MeSH Terms]) NOT "animals"[MH:NOEXP])) AND ("2019/11/05"[Date - Publication] : "3000"[Date - Publication])',
        '(((NASH[Title] OR non alcoholic fatty liver disease[Title] OR nonalcoholic fatty liver disease[Title] OR Non-alcoholic Fatty Liver Disease[Title] OR NAFLD[Title] OR nonalcoholic steatohepatitis[Title] OR Non alcoholic steatohepatitis[Title] OR "non alcoholic fatty liver disease"[MeSH Terms]) NOT (intestinal Microbiome[Title] OR gut microbiota[Title] OR "Gastrointestinal Microbiome"[MeSH Terms])) AND (lipotropic agents[Title/Abstract] OR fatty liver[Title/Abstract] OR liver cirrhosis[Title/Abstract] OR liver diseases[Title/Abstract] OR (fibrosis[Title/Abstract] AND liver)) AND ("diabetes mellitus"[MeSH Terms] OR "diabetes mellitus"[Title/Abstract] OR "diabetes"[Title/Abstract] OR "insulin resistance"[Title/Abstract] OR "insulin resistance"[MeSH Terms]) NOT "animals"[MH:NOEXP]) AND ("2019/11/05"[Date - Publication] : "3000"[Date - Publication])',
        '(((NASH[Title] OR non alcoholic fatty liver disease[Title] OR nonalcoholic fatty liver disease[Title] OR Non-alcoholic Fatty Liver Disease[Title] OR NAFLD[Title] OR nonalcoholic steatohepatitis[Title] OR Non alcoholic steatohepatitis[Title] OR "non alcoholic fatty liver disease"[MeSH Terms]) NOT (intestinal Microbiome[Title] OR gut microbiota[Title] OR "Gastrointestinal Microbiome"[MeSH Terms])) AND (Drug Induced Liver Disease [Title/Abstract] OR "Chemical and Drug Induced Liver Injury"[MeSH Terms] OR "liver diseases/chemically induced"[MeSH Terms] OR liver diseases chemically induced[Title/Abstract] OR "peroxisome proliferator-activated receptors"[MeSH Terms] OR PPAR[Title/Abstract] OR peroxisome proliferator activated receptors[Title/Abstract]) NOT "animals"[MH:NOEXP]) AND ("2019/11/05"[Date - Publication] : "3000"[Date - Publication])'
    ]
    # Okay, now DL
    monitor = Monitoring()
    for index, request in enumerate(pubmed_requests):
        data = monitor.launch_search(request=request, index=index+1)

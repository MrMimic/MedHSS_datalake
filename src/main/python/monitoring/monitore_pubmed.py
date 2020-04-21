import datetime as dt
import os


import requests
from bs4 import BeautifulSoup as BS

import tqdm
from publication.publication import Publication
from databases.sqlite import SQLite


class Monitoring(object):
    def __init__(self, configuration):
        # Store configuration
        self.configuration = configuration
        # Reach SQLite database to store scanned articles
        self.database = SQLite(configuration=configuration)
        # And to retrieve already scanned ones.
        self.already_scanned = self.database.get_already_scanned_pmids()
        # Store daily scanned
        self.daily_scanned = []

    def launch_search(self, request, index):
        """
        Launch a request on PubMed
        """
        request = request.replace(' ', '+')
        file_name = '{}_{}_{}.csv'.format(
            index,
            dt.datetime.now().strftime('%Y-%m-%d'),
            request.replace(' ', '_')[:50])
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&datetype=pdat&retmax=100000&term={}'.format(
            request)
        data = BS(requests.get(url).text, 'lxml')
        pmids = data.find_all('id')
        for pmid in tqdm.tqdm(pmids):
            pmid = pmid.text
            if int(pmid) not in self.already_scanned:
                publication = Publication(pmid=pmid)
                publication.get_data()
                publication.write_data(os.path.join('output', file_name))
                self.daily_scanned.append(pmid)

        self.database.insert_list_of_scanned_pmids(self.daily_scanned)
        return os.path.join('output', file_name)

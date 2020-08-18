#!/usr/bin/env python3
import os
from datetime import datetime
from typing import Dict, List

import requests
import tqdm
from bs4 import BeautifulSoup as BS

from databases.sqlite import SQLite
from publication.publication import Publication


class Monitoring():
    def __init__(self, configuration: Dict[str, str]) -> None:
        """
        Monitoring class. Allow to generate formatted output from PubMed requests.

        Args:
            configuration (Dict): The configuration of the class.
        """
        # Store configuration and output path
        self.configuration = configuration
        self.output_path = self.configuration["result"]["output_path"]
        # Reach SQLite database to store scanned articles
        self.database = SQLite(configuration=configuration)
        # And to retrieve already scanned ones.
        self.already_scanned = self.database.get_already_scanned_pmids()
        # Store daily scanned
        self.daily_scanned: List[str] = []

    def launch_search(self, request: str, index: int) -> str:
        """
        Launch a search on pubmed with a pre-formatted query.
        For each PMID result, write a formatted line on an output file.

        Args:
            request (str): The request to be sent.
            index (int): The index of the search among request list.

        Returns:
            str: Path of the output written file.
        """
        # Clean request
        request = request.replace(' ', '+')
        # Get today's date
        today = datetime.today().date()
        # And file name
        file_str = ''.join(filter(str.isalpha, request))[:50]
        # Combine them into a file name
        file_name = f"{index}_{today}_{file_str}.csv"
        # Call Pubmed API and index XML response
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&datetype=pdat&retmax=100000&term={}'.format(
            request)
        data = BS(requests.get(url).text, 'lxml')
        pmids = [pmid.text for pmid in data.find_all('id')]
        # For each PMID answering this request
        for pmid in tqdm.tqdm(pmids):
            if pmid not in self.already_scanned:
                # Create a publication object for each and store data locally
                publication = Publication(pmid=pmid,
                                          configuration=self.configuration)
                publication.get_data()
                publication.write_data(
                    file_path=os.path.join(self.output_path, file_name))
                # Then, add PMID to already scanned IDs
                self.daily_scanned.append(pmid)
        # And return written file's path
        return os.path.join(self.output_path, file_name)

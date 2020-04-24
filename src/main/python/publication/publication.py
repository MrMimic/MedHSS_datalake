#!/usr/bin/env python3
import os
import re

import requests
from bs4 import BeautifulSoup as BS
from typing import Dict


class Publication():
    def __init__(self, pmid: str, configuration: Dict[str, str]) -> None:
        """
        Publication storing object.

        Args:
            pmid (str): PMID of the publication.
            configuration (Dict[str, str]): Global configuration.
        """        
        # Store configuration
        self.configuration = configuration
        # Get publication types
        self.pth = self.configuration["has"]["publication_type"].split(";")
        self.pmid = pmid

    def get_data(self) -> None:
        """
        Retrieve all fields to get a complete publication object.
        """
        api = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={}'.format(
            self.pmid)
        data = requests.get(api).text
        data = BS(data, 'lxml')
        # Get DOI
        try:
            self.doi = data.find('articleid', attrs={'idtype': 'doi'}).text
        except AttributeError:
            self.doi = None
        # Get journal name
        try:
            self.journal = data.isoabbreviation.text
        except AttributeError:
            self.journal = None
        # Get year
        try:
            self.year = data.pubdate.year.text
        except AttributeError:
            try:
                self.year = data.datecompleted.year.text
            except AttributeError:
                try:
                    self.year = data.articledate.year.text
                except AttributeError:
                    self.year = None
        # Get month
        try:
            self.month = data.pubdate.month.text
        except AttributeError:
            try:
                self.month = data.datecompleted.month.text
            except AttributeError:
                try:
                    self.month = data.articledate.month.text
                except AttributeError:
                    self.month = None
        # Get day
        try:
            self.day = data.pubdate.day.text
        except AttributeError:
            try:
                self.day = data.datecompleted.day.text
            except AttributeError:
                try:
                    self.day = data.articledate.day.text
                except AttributeError:
                    self.day = None
        # Format pubdate
        self.pubdate = '{}/{}/{}'.format(self.year, self.month, self.day)
        # Get title
        self.title = data.articletitle.text
        # Parse authors
        try:
            authors = data.find_all('author', attrs={'validyn': 'Y'})
            self.authors = ', '.join([
                '{} {}'.format(author.lastname.text, author.initials.text)
                for author in authors
            ])
            self.first_author = '{} {}: {}'.format(
                authors[0].lastname.text, authors[0].initials.text,
                authors[0].affiliationinfo.affiliation.text)
            del authors
        except (AttributeError, IndexError):
            self.authors = None
            self.first_author = None
        # Get URL
        self.url = 'https://www.ncbi.nlm.nih.gov/pubmed/{}'.format(self.pmid)
        # Get pubtype
        pub_types = data.find_all('publicationtype')
        self.publication_type = ', '.join([
            pub_type.text for pub_type in pub_types
            if pub_type.text in self.pth
        ])
        del pub_types
        # Get associated MeSH terms
        meshs = data.find_all('meshheading')
        self.mesh_majors = list()
        self.mesh_all = list()
        for mesh in meshs:
            try:
                self.mesh_all.append(mesh.descriptorname.text)
                if mesh.descriptorname['majortopicyn'] == 'Y':
                    self.mesh_majors.append(mesh.descriptorname.text)
            except Exception:
                continue
        self.mesh_majors = '; '.join(self.mesh_majors)
        self.mesh_all = '; '.join(self.mesh_all)
        del meshs
        # Get abstract
        try:
            self.abstract = (re.sub('\n', '', data.abstract.text))
        except AttributeError:
            self.abstract = None

    def write_data(self, file_path: str) -> None:
        """
        Write the publication object as a line in output file.

        Args:
            filename (str): Path to output file.
        """
        with open(file_path, 'a') as h:
            h.write(
                'https://www.ncbi.nlm.nih.gov/pubmed/{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'
                .format(self.pmid, self.mesh_majors, self.title, self.abstract,
                        self.authors, self.first_author, self.publication_type,
                        self.year, self.pubdate, self.journal, ''))

import os
import re

import requests
from bs4 import BeautifulSoup as BS


class Publication(object):

    def __init__(self, pmid):

        # Get PTH
        with open(os.path.join('resources', 'PT_HAS.csv'), 'r') as H:
            self.pth = [line.strip('\n') for line in H.readlines()]

        self.pmid = pmid
        self.doi = None
        self.pmcid = None
        self.url = None

        self.title = None
        self.authors = None
        self.first_author = None
        self.journal = None
        self.abstract = None

        self.pubdate = None
        self.year = None
        self.month = None
        self.day = None

        self.publication_type = None
        self.mesh_majors = None
        self.mesh_all = None

    def get_data(self):
        api = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={}'.format(self.pmid)
        data = requests.get(api).text
        data = BS(data, 'lxml')

        try:
            self.doi = data.find('articleid', attrs={'idtype': 'doi'}).text
        except AttributeError:
            pass

        self.journal = data.isoabbreviation.text

        try:
            self.year = data.articledate.year.text
        except AttributeError:
            try:
                self.year = data.datecompleted.year.text
            except AttributeError:
                try:
                    self.year = data.pubdate.year.text
                except AttributeError:
                    pass
        try:
            self.month = data.articledate.month.text
        except AttributeError:
            try:
                self.month = data.datecompleted.month.text
            except AttributeError:
                try:
                    self.month = data.pubdate.month.text
                except AttributeError:
                    pass
        try:
            self.day = data.articledate.day.text
        except AttributeError:
            try:
                self.day = data.datecompleted.day.text
            except AttributeError:
                try:
                    self.day = data.pubdate.day.text
                except AttributeError:
                    pass

        self.pubdate = '{}/{}/{}'.format(self.year, self.month, self.day)

        self.title = data.articletitle.text

        try:
            authors = data.find_all('author', attrs={'validyn': 'Y'})
            self.authors = ', '.join(['{} {}'.format(author.lastname.text, author.initials.text) for author in authors])
            self.first_author = '{} {}: {}'.format(authors[0].lastname.text, authors[0].initials.text, authors[0].affiliationinfo.affiliation.text)
            del authors
        except (AttributeError, IndexError):
            pass

        self.url = 'https://www.ncbi.nlm.nih.gov/pubmed/{}'.format(self.pmid)

        pub_types = data.find_all('publicationtype')
        self.publication_type = ', '.join(['{}'.format(pub_type.text) for pub_type in pub_types if '{}'.format(pub_type.text) in self.pth])
        del pub_types

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

        try:
            self.abstract = (re.sub('\n', '', data.abstract.text))
        except AttributeError:
            pass

    def write_data(self, filename):

        with open(filename, 'a') as h:
            h.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                self.pmid,
                self.title,
                self.mesh_all,
                self.mesh_majors,
                self.year,
                self.abstract,
                self.authors,
                self.first_author,
                self.publication_type,
                self.month,
                self.journal,
                self.pubdate))

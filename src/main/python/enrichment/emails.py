
import re
import requests
from bs4 import BeautifulSoup as BS


def extract_emails(pmid):
    """"""
    api = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={}'.format(pmid)
    data = requests.get(api).text
    data = BS(data, 'lxml')

    # TITLE
    title = data.articletitle.text

    # AUTHORS
    authors = data.find_all('author', attrs={'validyn': 'Y'})
    for author in authors:
        emails =  list(set(re.findall('[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*.[a-zA-Z]+', str(author))))
        if len(emails) > 0:
            first_name = author.forename.text
            last_name = author.lastname.text
            affiliations = list()
            for aff in author.affiliationinfo:
                aff = re.sub('<.*?>', '', str(aff))
                if aff != '\n':
                    affiliations.append(aff)
            affiliations = '_'.join(affiliations)
            for email in emails:
                line_to_write = [pmid, '{} {}'.format(first_name, last_name), email, title, affiliations]
                with open('output/output.csv', 'a') as handler:
                    handler.write('{}\n'.format('\t'.join(line_to_write)))
                with open('scanned_pmids.dat', 'a') as handler:
                    handler.write('{}\n'.format(pmid))


def read_file(file_path):
    """"""

    with open('scanned_pmids.dat', 'r') as handler:
        already_scanned = [str(pmid.strip('\n')) for pmid in handler.readlines()]
    pmids = list()
    with open(file_path, 'r') as h:
        lines = [line for line in h.readlines()]
    for i, line in enumerate(lines):
        if i == 0:
            continue
        url = re.findall('/pubmed/.*?"', line)[0]
        url = re.sub('/pubmed/','', url)
        pmid = re.sub('"', '', url)
        if str(pmid) not in already_scanned:
            pmids.append(pmid)
    return pmids

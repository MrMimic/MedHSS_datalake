import os
from enrichment.pubmication import Publication
from bs4 import BeautifulSoup as BS
import requests
import datetime as dt
import tqdm


class Monitoring(object):

    def __init__(self):
        pass

    def launch_search(self, request):
        """
        Launch a request on PubMed
        """
        request = request.replace(' ', '+')
        print(request)
        file_name = '{}_{}.csv'.format(
            dt.datetime.now().strftime('%Y-%m-%d'),
            request.replace(' ', '_')[:50]
        )
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&datetype=pdat&retmax=100000&mindate=2019/10/01&maxdate=2019/10/07&term={}'.format(
            request
        )
        data = BS(requests.get(url).text, 'lxml')
        pmids = data.find_all('id')
        for pmid in tqdm.tqdm(pmids):
            pmid = pmid.text
            publication = Publication(pmid=pmid)
            publication.get_data()
            publication.write_data(os.path.join('output', file_name))
        print()


if __name__ == '__main__':
    pubmed_requests = [
        '"non alcoholic fatty liver disease"[MeSH Terms] AND "human"[MeSH Terms]',
        'cancer[MeSH Terms]',  # good one
        '("non alcoholic fatty liver disease"[MeSH Terms] NOT "Gastrointestinal Microbiome"[MeSH Terms]) AND ("Chemical and Drug Induced Liver Injury"[MeSH Terms] OR "liver diseases/chemically induced"[MeSH Terms] OR "peroxisome proliferator-activated receptors"[MeSH Terms]) AND human[MeSH Terms]',
        '("non alcoholic fatty liver disease"[MeSH Terms] NOT "Gastrointestinal Microbiome"[MeSH Terms]) AND ("lipotropic agents"[MeSH Terms] OR "fatty liver"[MeSH Terms] OR liver cirrhosis[MeSH Terms] OR liver diseases[MeSH Terms] OR (fibrosis[MeSH Terms] AND liver)) AND ("diabetes mellitus"[MeSH Terms] OR "insulin resistance"[MeSH Terms]) AND human[MeSH Terms]'
    ]
    # Okay, now DL
    monitor = Monitoring()
    for request in pubmed_requests:
        data = monitor.launch_search(request=request)

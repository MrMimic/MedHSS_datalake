import re
import os
import requests
from time import sleep
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs


class ReasearchGate(object):

    def __init__(self):

        self.output_dir = os.path.join('output')
        self.resources_dir = os.path.join('resources')

        self.base_page = 'https://www.researchgate.net'
        self.base_job_page = 'https://www.researchgate.net/job'

        self.job_url_regex = re.compile('\"jobUrl\"\:\"job\\\\(.*?)\&algorithm\=solrSearch\"')
        self.skill_regex = re.compile('\"coreTags\"\:\[(.*)\],"jobDiscoverMorePromo')

        self.ua = UserAgent()

        with open(os.path.join(self.resources_dir, 'scanned_urls.csv'), 'r') as handler:
            self.scanned_urls = handler.read().splitlines()

    def crawl_listed_jobs_page(self, url):
        """
        Parse a jobs pages for jobs URLs
        """
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19'
        headers = {'User-Agent': user_agent}
        while True:
            response = requests.get(url, headers=headers)
            jobs_urls = re.findall(self.job_url_regex, response.text)
            if len(jobs_urls) == 0:
                user_agent = self.ua.random
                print('Trying again (ua: {}).'.format(user_agent))
                sleep(5)
                continue
            else:
                break
        real_urls = ['{}{}'.format(self.base_job_page, job) for job in jobs_urls]
        return real_urls

    def extract_area_of_research_from_job_page(self, url):
        """
        Parse a job page to extract skills
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(url, headers=headers)

        indexed_page_data = bs(response.content, 'lxml')
        skills = indexed_page_data.find_all('div', attrs={'data-testid': 'skills'})
        indexed_skills = bs(str(skills), 'lxml')
        cleaned_skills = [skill.text for skill in indexed_skills.find_all('li')]

        if len(cleaned_skills) > 0:
            return cleaned_skills
        else:
            return None

    def write_skills(self, url, skills):
        """
        Write found skill in a file
        """
        with open(os.path.join(self.output_dir, 'research_gate_skills.csv'), 'a') as handler:
            for skill in skills:
                handler.write('{}\t{}\n'.format(skill, url))

    def write_url(self, url):
        """
        Write found skill in a file
        """
        with open(os.path.join(self.resources_dir, 'scanned_urls.csv'), 'a') as handler:
            handler.write('{}\n'.format(url.split('?')[0]))


import argparse
import configparser
import os
from tqdm import tqdm
from time import sleep

from download.researchgate import ReasearchGate
from emails.gmail import Email
from enrichment.pubmed import Executor
from enrichment.emails import read_file, extract_emails


parser = argparse.ArgumentParser()
parser.add_argument('--researchgate', help='Scan RG for skills', action='store_true')
parser.add_argument('--enrichment', help='PubMed classic enrichment', action='store_true')
parser.add_argument('--emails', help='Extract emails from PubMed', action='store_true')
args = parser.parse_args()

if args.emails:
    # Checks local files
    file_to_scan = [file_name for file_name in os.listdir('input') if file_name.endswith('.csv')]
    for file_name in file_to_scan:
        pmids = read_file(os.path.join('input', file_name))
        random.shuffle(pmids)
        for pmid in tqdm(pmids):
            extract_emails(pmid)

if args.enrichment:
    configuration = configparser.ConfigParser()
    configuration.read(os.path.join('configurations', 'config.cfg'))
    # Connect to mail
    mailer = Email(
        email=configuration.get('EMAIL', 'adress'),
        password=configuration.get('EMAIL', 'password'),
        server='smtp.gmail.com',
        port=587)
    # Check if file not already done
    with open(os.path.join('resources', 'files_done.txt'), 'r') as handler:
        treated = [line.strip('\n') for line in handler.readlines()]
    # Read last email
    email_from, email_subject, input_file_path = mailer.read_last_mail()
    # If file to treat has been downloaded
    if input_file_path is not None:
        if input_file_path not in treated:
            executer = Executor()
            # Enrich
            success, output_file_path = executer.launch_pubmed_enrichment()

            # Delete file
            if success is True:
                os.remove(input_file_path)
                print('Analysis completed, deleting {}'.format(input_file_path))

            # Now send back completed file
            mailer.send_mail(
                corresponding=email_from,
                file_name=output_file_path,
                subject='[COMPLETED] {}'.format(output_file_path),
                text='<3')
            with open(os.path.join('resources', 'files_done.txt'), 'a') as handler:
                handler.write('{}\n'.format(input_file_path))
        else:
            print('File {} already treated.'.format(input_file_path))
            os.remove(input_file_path)
    else:
        print('{} did not give any command ({})'.format(email_from, email_subject))

if args.researchgate:
    extractor = ReasearchGate()
    for job_page in range(1, 30):
        url = 'https://www.researchgate.net/jobs?regions=&page={}'.format(job_page)
        print(url)
        jobs_urls = extractor.crawl_listed_jobs_page(url=url)
        if len(jobs_urls) == 0:
            print('Please wait.')
            exit(0)
        for url in jobs_urls:
            if url.split('?')[0] not in extractor.scanned_urls:
                skills = extractor.extract_area_of_research_from_job_page(url=url)
                if skills is not None:
                    extractor.write_skills(url=url, skills=skills)
                    extractor.write_url(url=url)
                    print('Found {} skills in url: {}..'.format(len(skills), url[:100]))
                    sleep(5)
                else:
                    print('No skills found in {}..'.format(url[:100]    ))
            else:
                print('Skip: {}'.format(url[:100]))
        sleep(10)

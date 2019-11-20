import os
import re
import time

from tqdm import tqdm

from enrichment.pubmication import Publication


class Executor(object):

    def __init__(self):
        pass

    def launch_pubmed_enrichment(self):
        """
        Local pubmed enrichment
        """
        mesh_counter = dict()

        # try:
        for filename in os.listdir('input'):

            if filename.endswith('csv'):

                file_path = os.path.join('input', filename)

                print('\n{}\n'.format(filename))

                if 'output_{}'.format(filename) in os.listdir('output'):
                    with open('output/output_{}'.format(filename)) as handler:
                        scanned_pmids = [line.split('\t')[0] for line in handler.readlines()]
                        print('{} pmids already scanned'.format(len(scanned_pmids)))
                else:
                    scanned_pmids = list()

                with open(file_path, 'r') as h:
                    lines = [line.sptrip('\n') for line in h.readlines()]
                # del lines[0]

                for line in tqdm(lines):
                    # url = re.findall('/pubmed/.*?"', line)[0]
                    # url = re.sub('/pubmed/', '', url)
                    # pmid = re.sub('"', '', url)
                    #
                    # if str(pmid) in scanned_pmids:
                    #     continue
                    #
                    # del url
                    pmid=line

                    publication = Publication(pmid=pmid)
                    publication.get_data()
                    publication.write_data(os.path.join('output', 'output_{}'.format(filename)))

                    # Count all meshs
                    for mesh in publication.mesh_all.split('; '):
                        if mesh not in mesh_counter.keys():
                            mesh_counter[mesh] = 1
                        else:
                            mesh_counter[mesh] += 1

                    time.sleep(1.5)

        #
        # with open('mesh_{}'.format(filename), 'a') as h:
        #     for k, v in mesh_counter.items():
        #         h.write('{}\t{}\n'.format(k, v))

        return True, 'output/output_{}'.format(filename)

        # except Exception as E:
        #     print(E)
        #     return True, E
            # continue

    def compare_pdf_to_table(self):
        """"""
        with open('Detresse_respiratoire.csv', 'r') as H:
            titles = [line.strip('\n').split('\t')[1].lower() for line in H.readlines()]

        for pdf_name in os.listdir('OUTPUT'):
            path = os.path.join('OUTPUT', pdf_name)
            pdf = PDF(path=path)
            if pdf.title.lower() in titles:
                print('PRESENT: {}'.format(pdf.title))
            else:
                print('{}\tABSENT\t{}'.format(pdf_name, pdf.title))

if __name__ == '__main__':
    A = Executor()
    A.launch_pubmed_enrichment()

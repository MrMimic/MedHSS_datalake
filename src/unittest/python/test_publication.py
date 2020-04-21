
import pandas as pd
import os
import shutil
import unittest

from publication.publication import Publication


class MailerTest(unittest.TestCase):

    def setUp(self) -> None:
        # Get current folder
        current_folder = os.path.dirname(os.path.abspath(__file__))
        # And test target
        self.target = os.path.join(current_folder, "../", "../", "../", "target")
        # Specific output for this test
        self.output = os.path.join(self.target, "publication")
        # Create if needed
        if not os.path.isdir(self.output):
            os.mkdir(self.output)
        # Define configuration
        self.configuration = {
            "has": {
                "publication_type": "publication;review"
            }
        }

    def tearDown(self) -> None:
        shutil.rmtree(self.output)

    def test_get_data_write_data(self) -> None:
        pmid = "27647350"
        publication = Publication(pmid=pmid, configuration=self.configuration)
        # Get
        publication.get_data()
        self.assertEqual(publication.title, 'Recommendations for a standardized avian coronavirus (AvCoV) nomenclature: outcome from discussions within the framework of the European Union COST Action FA1207: "towards control of avian coronaviruses: strategies for vaccination, diagnosis and surveillance".')
        self.assertEqual(publication.year, "2016")
        self.assertEqual(publication.mesh_majors, "Terminology as Topic")
        # Write
        file_name = "output_name.csv"
        self.assertNotIn(file_name, os.listdir(self.output))
        publication.write_data(file_path=os.path.join(self.output, file_name))
        self.assertIn(file_name, os.listdir(self.output))
        # Read
        dataframe = pd.read_csv(os.path.join(self.output, file_name), delimiter="\t")
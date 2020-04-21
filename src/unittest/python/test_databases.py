
import os
import unittest
import shutil
from databases.sqlite import SQLite


class DatabasesTest(unittest.TestCase):

    def setUp(self) -> None:
        # Get current folder
        current_folder = os.path.dirname(os.path.abspath(__file__))
        # And test target
        self.target = os.path.join(current_folder, "../", "../", "../", "target")
        #Specific output for this test
        self.output = os.path.join(self.target, "database")
        # Create if needed
        if not os.path.isdir(self.output):
            os.mkdir(self.output)
        # Create configuration
        self.configuration = {
            "database": {
                "path": os.path.join(self.output, "dummy_base.sqlite")
            }
        }

    def tearDown(self) -> None:
        shutil.rmtree(self.output)

    def test_instance_and_create(self) -> None:
        self.assertNotIn("dummy_base.sqlite", os.listdir(self.output))
        database = SQLite(self.configuration)
        self.assertIsInstance(database, SQLite)
        self.assertIn("dummy_base.sqlite", os.listdir(self.output))

    def test_insert_and_read(self) -> None:
        database = SQLite(self.configuration)
        # Read to ensure empty DB
        scanned = database.get_already_scanned_pmids()
        self.assertEqual(scanned, [])
        # Insert scanned PMIDs
        list_of_scanned_pmids = ["pmid_1", "pmid_2", "pmid_3"]
        database.insert_list_of_scanned_pmids(list_of_scanned_pmids=list_of_scanned_pmids)
        # And read them
        scanned = database.get_already_scanned_pmids()
        self.assertEqual(scanned, list_of_scanned_pmids)
#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime


class SQLite():

    def __init__(self, configuration):
        self.configuration = configuration
        self.database_path = self.configuration["database"]["path"]
        if not os.path.isfile(self.database_path):
            self.create_database()

    def create_database(self):
        database = sqlite3.connect(self.database_path)
        # Storing articles
        already_scanned_table = {
            "paper_pmid": "TEXT PRIMARY KEY",
            "date": "DATETIME"
        }
        columns = [
            "{0} {1}".format(name, col_type)
            for name, col_type in already_scanned_table.items()
        ]
        command = "CREATE TABLE IF NOT EXISTS scanned ({});".format(
            ", ".join(columns))
        database.execute(command)
        database.close()
        print(f"Database created: {self.database_path}")

    def insert_list_of_scanned_pmids(self, list_of_scanned_pmids):
        list_of_scanned_pmids = list(set(list_of_scanned_pmids))
        command = "INSERT  OR IGNORE INTO scanned(paper_pmid, date) VALUES (?, ?)"
        # Adding today's date
        today = datetime.today().date()
        list_to_insert = [[pmid, today] for pmid in list_of_scanned_pmids]
        # Insert into SQLite
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()
        cursor.executemany(command, list_to_insert)
        cursor.close()
        connection.commit()
        connection.close()
        print(f"Inserted {len(list_of_scanned_pmids)} daily scanned PMIDs.")

    def get_already_scanned_pmids(self):
        command = "SELECT paper_pmid FROM scanned ;"
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()
        raw_pmids = cursor.execute(command)
        pmids = [pmid[0] for pmid in raw_pmids]
        cursor.close()
        connection.close()
        print(f"Found {len(pmids)} PMIDs already scanned.")
        return pmids

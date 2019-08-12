
import unittest
from download.researchgate import ReasearchGate


class DownloadTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_reasearch_gate_instance(self):
        instance = ReasearchGate()
        self.assertIsNotNone(instance)

import unittest,json
from unittest import TestCase
from src.Config import Config
from src.Web import Web

class TestConfig(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_select(self):
        web = Web(Config("private/my_account.json"))
        rows, _index = web.select_index("tests/new_coming.tsv", 3, 100, "quest")
        self.assertEqual(26, len(rows))
        self.assertEqual(None, _index)
        self.assertTrue("quest" in rows[0]['description'].lower())

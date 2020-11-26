import unittest
from unittest import TestCase
from src.Filter import Filter
from src.VRC import VrcWorld

class TestConfig(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_filter(self):
        w1 = VrcWorld()
        w1.id = 'black'
        w1.name = 'black1'
        w1.author_id = 'black2'
        w2 = VrcWorld()
        w2.id = 'white'
        w2.name = 'white1'
        w2.author_id = 'white2'
        w3 = VrcWorld()
        w3.id = 'a'
        w3.name = 'This is fuck'
        w3.author_id = 'ok'
        w4 = VrcWorld()
        w4.id = 'b'
        w4.name = 'That is fuck'
        w4.author_id = 'fail'

        instance = Filter()
        instance.add_black('id', 'black')
        instance.add_white('id', 'white')
        instance.add_black('name_or_description', 'fuck')
        instance.add_white('author_id', 'ok')

        self.assertEqual(False, instance.is_passed(w1))
        self.assertEqual(True, instance.is_passed(w2))
        self.assertEqual(True, instance.is_passed(w3))
        self.assertEqual(False, instance.is_passed(w4))


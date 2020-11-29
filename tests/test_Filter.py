import unittest
from unittest import TestCase
from src.Filter import Filter, FilterOption
from src.VRC import VrcWorld


class TestConfig(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def make_world(self, id, name, author_id, description):
        w = VrcWorld()
        w.id = id
        w.name = name
        w.author_id = author_id
        w.description = description
        return w

    def test_filter(self):
        w1 = self.make_world('black', 'black1', 'black2', 'black3')
        w2 = self.make_world('white', 'white1', 'white2', 'white3')
        w3 = self.make_world('a', 'This is fuck', 'ok', None)
        w4 = self.make_world('b', 'This is fuck', 'fail', None)
        w5 = self.make_world('c', 'Hoge', 'c', 'This is chill Kons avatars world')
        w6 = self.make_world('d', 'Hoge', 'Chill avatars world', None)

        instance = Filter()
        instance.add_black(FilterOption.ID, 'black')
        instance.add_white(FilterOption.ID, 'white')
        instance.add_black(FilterOption.TEXT, 'fuck')
        instance.add_white(FilterOption.AUTHOR, 'ok')
        instance.add_black(FilterOption.RE_TEXT, 'kon.+avatar')

        self.assertEqual(False, instance.is_passed(w1))
        self.assertEqual(True, instance.is_passed(w2))
        self.assertEqual(True, instance.is_passed(w3))
        self.assertEqual(False, instance.is_passed(w4))
        self.assertEqual(False, instance.is_passed(w5))
        self.assertEqual(True, instance.is_passed(w6))



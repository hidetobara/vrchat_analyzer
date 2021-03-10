import unittest
from unittest import TestCase
from src.DB import DbAll, DbMonths, DbComing
from src.VRC import VrcWorld

class TestDb(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def make_world(self, name, author_name, description):
        w = VrcWorld()
        w.id = 'abc' + name + author_name
        w.name = name
        w.author_id = 'def'
        w.author_name = author_name
        w.description = description
        w.thumbnail_image_url = 'http://hoge.com/hello.jpg'
        w.visits = 100
        w.favorites = 10
        return w

    def test_all(self):
        w1 = self.make_world('Hello', 'Bob', 'Good morning.')
        w2 = self.make_world('Bye', 'Tom', 'Bad morning.')

        db = DbAll(test=True, drop=True)
        db.insert([w1, w2])
        self.assertEqual(1, len(db.select_by_keywords(['Good'], 0)[0]))
        self.assertEqual(0, len(db.select_by_keywords(['Bad', 'Boy'], 0)[0]))

    def test_months(self):
        w1 = self.make_world('Hello', 'Bob', 'Good morning.')
        w2 = self.make_world('Bye', 'Tom', 'Bad morning.')

        db = DbMonths(test=True, drop=True)
        db.insert(2012, [w1, w2])
        self.assertEqual(2, len(db.select_by_month(2012, 0)[0]))
        self.assertEqual(0, len(db.select_by_month(2101, 0)[0]))
        self.assertEqual(0, len(db.select_by_month(2012, 1)[0]))

    def test_coming(self):
        ws = []
        for i in range(0, 25):
            ws.append(self.make_world('Hello-' + str(i), 'Bob', 'Good morning ' + str(i)))

        db = DbComing(test=True, drop=True)
        db.insert(ws)
        self.assertEqual(24, len(db.select(0)[0]))
        self.assertEqual(1, len(db.select(1)[0]))

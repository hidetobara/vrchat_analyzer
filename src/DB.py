import sqlite3

from src.VRC import VrcApi, VrcWorld

VRC_ALL_PATH = 'tmp/vrc_all.db'
VRC_MONTH_PATH = 'tmp/vrc_months.db'
VRC_COMING_PATH = 'tmp/vrc_coming.db'
PAGE_SIZE = 24

class DbAll:
    def __init__(self, test=False, drop=False):
        self.connection = sqlite3.connect(("tests/" if test else "") + VRC_ALL_PATH)
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        if drop:
            cursor.execute("DROP TABLE IF EXISTS all_worlds")
        cursor.execute("""
CREATE TABLE IF NOT EXISTS all_worlds (
    id TEXT, name TEXT,
    author_id TEXT, author_name TEXT,
    description TEXT, thumbnail_image_url TEXT,
    visits INT, favorites INT
)"""
        )
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS _id ON all_worlds(id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS _name ON all_worlds(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS _author_name ON all_worlds(author_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS _description ON all_worlds(description)")
        self.connection.commit()
    def __del__(self):
        self.connection.close()

    def insert(self, worlds):
        rows = []
        for w in worlds:
            rows.append([w.id, w.name, w.author_id, w.author_name, w.description, w.thumbnail_image_url, w.visits, w.favorites])
        cursor = self.connection.cursor()
        cursor.executemany("INSERT INTO all_worlds VALUES(?, ?, ?, ?, ?, ?, ?, ?)", rows)
        self.connection.commit()

    def select_by_keywords(self, keywords, page):
        cursor = self.connection.cursor()
        sql = "SELECT id,name,author_id,author_name,description,thumbnail_image_url,favorites FROM all_worlds"
        where = ""
        if len(keywords) > 0:
            where = " WHERE"
            for n, k in enumerate(keywords):
                where += '' if n == 0 else ' AND'
                where += ' (name LIKE "%{}%" OR author_name LIKE "%{}%" OR description LIKE "%{}%")'.format(k, k, k)
        limit = ' LIMIT {} OFFSET {}'.format(PAGE_SIZE, PAGE_SIZE * page)
        worlds = []
        for row in cursor.execute(sql + where + limit):
            w = VrcWorld.db_parse(row)
            if w:
                worlds.append(w)
        return worlds

class DbMonths:
    def __init__(self, test=False, drop=False):
        self.connection = sqlite3.connect(("tests/" if test else "") + VRC_MONTH_PATH)
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        if drop:
            cursor.execute("DROP TABLE IF EXISTS month_worlds")
        cursor.execute("""
CREATE TABLE IF NOT EXISTS month_worlds (
    month INT, rank INT,
    id TEXT, name TEXT,
    author_id TEXT, author_name TEXT,
    description TEXT, thumbnail_image_url TEXT,
    visits INT, favorites INT
)"""
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS _month ON month_worlds(month)")
        cursor.execute("CREATE INDEX IF NOT EXISTS _rank ON month_worlds(rank)")
        self.connection.commit()
    def __del__(self):
        self.connection.close()

    def insert(self, month, worlds):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM month_worlds WHERE month = {}".format(month))
        rows = []
        for n, w in enumerate(worlds):
            rows.append([month, n + 1, w.id, w.name, w.author_id, w.author_name, w.description, w.thumbnail_image_url, w.visits, w.favorites])
        cursor = self.connection.cursor()
        cursor.executemany("INSERT INTO month_worlds VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
        self.connection.commit()

    def select_by_month(self, month, page):
        cursor = self.connection.cursor()
        sql = "SELECT id,name,author_id,author_name,description,thumbnail_image_url,favorites FROM month_worlds"
        where = " WHERE month = {}".format(month)
        limit = ' ORDER BY rank LIMIT {} OFFSET {}'.format(PAGE_SIZE, PAGE_SIZE * page)
        worlds = []
        for row in cursor.execute(sql + where + limit):
            w = VrcWorld.db_parse(row)
            if w:
                worlds.append(w)
        return worlds

class DbComing:
    def __init__(self, test=False, drop=False):
        self.connection = sqlite3.connect(("tests/" if test else "") + VRC_COMING_PATH)
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        if drop:
            cursor.execute("DROP TABLE IF EXISTS coming_worlds")
        cursor.execute("""
CREATE TABLE IF NOT EXISTS coming_worlds (
    rank INT,
    id TEXT, name TEXT,
    author_id TEXT, author_name TEXT,
    description TEXT, thumbnail_image_url TEXT,
    visits INT, favorites INT
)"""
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS _rank ON coming_worlds(rank)")
        self.connection.commit()
    def __del__(self):
        self.connection.close()

    def insert(self, worlds):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM coming_worlds")
        rows = []
        for n, w in enumerate(worlds):
            rows.append([n + 1, w.id, w.name, w.author_id, w.author_name, w.description, w.thumbnail_image_url, w.visits, w.favorites])
        cursor = self.connection.cursor()
        cursor.executemany("INSERT INTO coming_worlds VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
        self.connection.commit()

    def select(self, page):
        cursor = self.connection.cursor()
        sql = "SELECT id,name,author_id,author_name,description,thumbnail_image_url,favorites FROM coming_worlds"
        limit = ' ORDER BY rank LIMIT {} OFFSET {}'.format(PAGE_SIZE, PAGE_SIZE * page)
        worlds = []
        for row in cursor.execute(sql + limit):
            w = VrcWorld.db_parse(row)
            if w:
                worlds.append(w)
        return worlds

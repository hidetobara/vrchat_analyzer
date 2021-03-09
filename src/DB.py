import sys,os,time,sqlite3
from pathlib import Path

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './private/vrchat-analyzer-ba2bcb1497e6.json'
from google.cloud import storage

from src.VRC import VrcApi, VrcWorld
from src.Config import Config

VRC_ALL_PATH = 'tmp/vrc_all.db'
VRC_MONTHS_PATH = 'tmp/vrc_months.db'
VRC_COMING_PATH = 'tmp/vrc_coming.db'
PAGE_SIZE = 24

class DbBase:
    @staticmethod
    def download_origin(path):
        if os.path.exists(path):
            p = Path(path)
            diff = time.time() - os.path.getmtime(p)
            if diff > 60 * 60 * 24:
                return
        filename = os.path.basename(path)
        client = storage.Client()
        bucket = storage.Bucket(client)
        bucket.name = Config.BUCKET_NAME
        blob = bucket.blob(filename)
        blob.download_to_filename(path)

    @staticmethod
    def upload_bucket(path):
        filename = os.path.basename(path)
        client = storage.Client()
        bucket = storage.Bucket(client)
        bucket.name = Config.BUCKET_NAME
        blob = bucket.blob(filename)
        blob.upload_from_filename(path)

class DbAll(DbBase):
    @staticmethod
    def fetch():
        DbBase.download_origin(VRC_ALL_PATH)
        return DbAll()

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

    def save(self):
        self.upload_bucket(VRC_ALL_PATH)

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
        if keywords is not None and len(keywords) > 0:
            where = " WHERE"
            for n, k in enumerate(keywords):
                where += '' if n == 0 else ' AND'
                where += ' (name LIKE "%{}%" OR author_name LIKE "%{}%" OR description LIKE "%{}%")'.format(k, k, k)
        limit = ' LIMIT {} OFFSET {}'.format(PAGE_SIZE + 1, PAGE_SIZE * page)
        worlds = []
        for row in cursor.execute(sql + where + limit):
            w = VrcWorld.db_parse(row)
            if w:
                worlds.append(w)
        return worlds[:PAGE_SIZE], len(worlds) > PAGE_SIZE

class DbMonths(DbBase):
    @staticmethod
    def fetch():
        DbBase.download_origin(VRC_MONTHS_PATH)
        return DbMonths()

    def __init__(self, test=False, drop=False):
        self.connection = sqlite3.connect(("tests/" if test else "") + VRC_MONTHS_PATH)
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

    def save(self):
        self.upload_bucket(VRC_MONTHS_PATH)

    def insert(self, month, worlds):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM month_worlds WHERE month = {}".format(month))
        rows = []
        for n, w in enumerate(worlds):
            rows.append([month, n + 1, w.id, w.name, w.author_id, w.author_name, w.description, w.thumbnail_image_url, w.visits, w.favorites])
        cursor = self.connection.cursor()
        cursor.executemany("INSERT INTO month_worlds VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
        self.connection.commit()

    def select_by_month(self, month, page, size=None):
        if size is None:
            size = PAGE_SIZE
        cursor = self.connection.cursor()
        sql = "SELECT id,name,author_id,author_name,description,thumbnail_image_url,favorites FROM month_worlds"
        where = " WHERE month = {}".format(month)
        limit = ' ORDER BY rank LIMIT {} OFFSET {}'.format(size + 1, PAGE_SIZE * page)
        worlds = []
        for row in cursor.execute(sql + where + limit):
            w = VrcWorld.db_parse(row)
            if w:
                worlds.append(w)
        return worlds[:size], len(worlds) > size

class DbComing(DbBase):
    @staticmethod
    def fetch():
        DbBase.download_origin(VRC_COMING_PATH)
        return DbComing()

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

    def save(self):
        self.upload_bucket(VRC_COMING_PATH)

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
        limit = ' ORDER BY rank LIMIT {} OFFSET {}'.format(PAGE_SIZE + 1, PAGE_SIZE * page)
        worlds = []
        for row in cursor.execute(sql + limit):
            w = VrcWorld.db_parse(row)
            if w:
                worlds.append(w)
        return worlds[:PAGE_SIZE], len(worlds) > PAGE_SIZE

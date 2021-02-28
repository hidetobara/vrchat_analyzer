import sqlite3


class DB:
    VRC_WORLDS_PATH = 'tmp/vrchat_worlds.db'

    def __init__(self):
        self.connection = sqlite3.connect(DB.VRC_WORLDS_PATH)
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS vrc_worlds")
        cursor.execute("""
CREATE TABLE IF NOT EXISTS vrc_worlds (
    id TEXT, name TEXT,
    author_id TEXT, author_name TEXT,
    description TEXT, thumbnail_image_url TEXT,
    visits INT, favorites INT
)"""
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS _id ON vrc_worlds(id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS _name ON vrc_worlds(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS _author_name ON vrc_worlds(author_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS _description ON vrc_worlds(description)")
        self.connection.commit()
    def __del__(self):
        self.connection.close()

    def insert_vrc(self, worlds):
        rows = []
        for w in worlds:
            rows.append([w.id, w.name, w.author_id, w.author_name, w.description, w.thumbnail_image_url, w.visits, w.favorites])
        cursor = self.connection.cursor()
        cursor.executemany("INSERT INTO vrc_worlds VALUES(?, ?, ?, ?, ?, ?, ?, ?)", rows)
        self.connection.commit()


    

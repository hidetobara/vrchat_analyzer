import os,json,datetime

def ts2str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")
def d2str(dt):
    return dt.strftime("%Y-%m-%d")
def str2ts(s):
    return datetime.datetime.fromisoformat(s) # %Y-%m-%d %H:%M:%S

class Config:
    INDEX_PATH = 'tmp/index.tsv'
    NEW_COMING_PATH = 'tmp/new_coming.tsv'
    CRAWLED_PATH = 'tmp/crawled.json'
    BQ_TABLE = 'vrchat-analyzer.crawled.worlds'
    BUCKET_NAME = 'vrchat-frontend'

    def __init__(self, path=None, table=None):
        self.table = {}
        if path is not None and os.path.exists(path):
            with open(path) as f:
                self.load_map(json.load(f))
        if table is not None:
            self.load_map(table)

    def load_env(self):
        for key, value in os.environ.itmes():
            self.table[key] = value

    def load_map(self, table):
        for key, value in table.items():
            self.table[key] = value
    
    def put(self, key, value):
        self.table[key] = value
    
    def get(self, key, default=None):
        if key not in self.table:
            return default
        return self.table[key]

import os,json,datetime,time,re


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

    @staticmethod
    def make_month_key(dt):
        return dt.strftime('%y%m')

    @staticmethod
    def make_last1_key():
        today = datetime.date.today()
        first = datetime.date(today.year, today.month, 1)
        last_month = first - datetime.timedelta(1)
        return Config.make_month_key(last_month)

    @staticmethod
    def get_old_month_keys(loop=4):
        months = []
        midmonth = datetime.date.today()
        for _ in range(loop+1):
            first = datetime.date(midmonth.year, midmonth.month, 1)
            months.append(first.strftime('%y%m'))
            midmonth = first - datetime.timedelta(3)
        return months[1:]
    

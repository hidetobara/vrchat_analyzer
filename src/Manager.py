import sys,os,json,datetime,re,html,urllib,time

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './private/vrchat-analyzer-ba2bcb1497e6.json'
from google.cloud import bigquery
from google.cloud import storage
from src.Config import Config
from src.VRC import VrcApi


def ts2str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")
def d2str(dt):
    return dt.strftime("%Y-%m-%d")
def str2ts(s):
    return datetime.datetime.fromisoformat(s) # %Y-%m-%d %H:%M:%S

class Manager:
    def __init__(self, config):
        self.config = config
        self.bq_client = bigquery.Client()
        self.api = VrcApi(config.get('USERNAME'), config.get("PASSWORD"))

    def insert_rows(self, rows, table_path):
        if len(rows) == 0:
            return
        cells = table_path.split('.')
        set_name = cells[-2]
        table_name = cells[-1]
        dataset_ref = self.bq_client.dataset(set_name)
        table_ref = dataset_ref.table(table_name)
        table = self.bq_client.get_table(table_ref)
        r = self.bq_client.insert_rows_json(table, rows)
        print("insert_logs=", r, "len=", len(rows))

    def selecting_ranked_worlds(self, table_path="vrchat-analyzer.crawled.worlds", limit=100):
        sql = """with temp1 as (
SELECT
    id,name,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at) as _rank,
    (SQRT(visits) + favorites) / (DATE_DIFF(CURRENT_DATE(), DATE(created_at), DAY)+1) as _value FROM `{}`
)
SELECT id,name,_value FROM temp1 WHERE _rank = 1 ORDER BY _value DESC LIMIT {}""".format(table_path, limit)
        print("sql=", sql)
        for row in self.bq_client.query(sql).result():
            yield row

    def crawl_worlds(self):
        last_updated = None
        if os.path.exists(Config.CRAWLED_PATH):
            with open(Config.CRAWLED_PATH, 'r') as f:
                crawled = json.load(f)
                last_updated = str2ts(crawled['last_updated'])
        worlds = []
        rows = self.api.get_updated_worlds(last_updated)
        if len(rows) > 0:
            last_updated = rows[0].updated_at
            worlds.extend(rows)
        time.sleep(1)
        worlds.extend(self.api.get_familiar_worlds())
        self.insert_rows(list(map(lambda x: x.to_bq(), worlds)), Config.BQ_TABLE)

        with open(Config.CRAWLED_PATH, 'w') as f:
            json.dump({'last_updated':ts2str(last_updated)}, f)

    def update_index(self):
        rows = []
        for w in self.selecting_ranked_worlds(limit=1000):
            detail = self.api.get_world_detail(w['id'])
            if detail is None:
                continue
            rows.append(detail.to_tsv())
            if len(rows) % 10 == 0:
                print("update=", len(rows))
            time.sleep(1)
        with open(Config.INDEX_PATH, "w", encoding='utf-8') as f:
            for row in rows:
                f.write("\t".join(row) + "\n")

        client = storage.Client()
        bucket = storage.Bucket(client)
        bucket.name = Config.BUCKET_NAME
        blob = bucket.blob("index.tsv")
        blob.upload_from_filename(Config.INDEX_PATH)

import sys,os,json,datetime,re,html,urllib

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './private/vrchat-analyzer-ba2bcb1497e6.json'
from google.cloud import bigquery

def ts2str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")
def d2str(dt):
    return dt.strftime("%Y-%m-%d")

class Manager:
    def __init__(self):
        self.bq_client = bigquery.Client()

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

    def selecting_ranked_worlds(self, table_path="vrchat-analyzer.crawled.worlds", limit=30):
        sql = """with temp1 as (
SELECT id,name,description,tags,ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at) as _rank,SQRT(visits) + favorites as _value FROM `{}`
)
SELECT id,name,description,tags,_value FROM temp1 WHERE _rank = 1 ORDER BY _value DESC LIMIT {}""".format(table_path, limit)
        print("sql=", sql)
        for row in self.bq_client.query(sql).result():
            yield row

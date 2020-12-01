import sys,os,json,datetime

from google.cloud import bigquery
from src.Config import Config, dt2str, d2str, str2dt

class BqClient:
    def __init__(self):
        self.bq_client = bigquery.Client()
        self.table_path = Config.BQ_TABLE

    def insert_rows(self, rows):
        if len(rows) == 0:
            return
        cells = self.table_path.split('.')
        set_name = cells[-2]
        table_name = cells[-1]
        dataset_ref = self.bq_client.dataset(set_name)
        table_ref = dataset_ref.table(table_name)
        table = self.bq_client.get_table(table_ref)
        r = self.bq_client.insert_rows_json(table, rows)
        print("insert_logs=", r, "len=", len(rows))

    def selecting_ranked_worlds(self, limit=100):
        sql = """with temp1 as (
SELECT
    id, name, author_id, author_name, created_at, updated_at, release_status,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) as _rank,
    (SQRT(visits) + SQRT(favorites)) / (DATE_DIFF(CURRENT_DATE(), DATE(created_at), DAY) + DATE_DIFF(CURRENT_DATE(), DATE(updated_at), DAY) +1) as _value
    FROM `{}`
)
SELECT id,name,author_id,author_name,created_at,updated_at,_value FROM temp1 WHERE _rank = 1 AND (release_status IS NULL OR release_status != 'hidden')
ORDER BY _value DESC LIMIT {}""".format(self.table_path, limit)
        print("sql=", sql)
        for row in self.bq_client.query(sql).result():
            yield row

    def selecting_new_coming_worlds(self, days):
        day_from = datetime.datetime.today() - datetime.timedelta(days=days)
        sql = """with temp1 as (
SELECT
    id, name, author_id, author_name, created_at, updated_at, release_status,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) as _rank,
    visits, favorites, FROM `{}`
    WHERE created_at >= '{}'
)
SELECT id,name,author_id,author_name,created_at,updated_at,visits,favorites FROM temp1 WHERE _rank = 1 AND (release_status IS NULL OR release_status != 'hidden')""".format(self.table_path, d2str(day_from))
        print("sql=", sql)
        for row in self.bq_client.query(sql).result():
            yield row

    def selecting_between(self, d_from, d_to, limit=60):
        sql = """with temp1 as (
SELECT
    id, name, created_at, updated_at, release_status,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) as _rank,
    SQRT(visits) + favorites as _value
    FROM `{}`
    WHERE created_at >= '{}' and created_at < '{}'
)
SELECT id,name,created_at,updated_at,_value FROM temp1 WHERE _rank = 1 AND (release_status IS NULL OR release_status != 'hidden')
ORDER BY _value DESC LIMIT {}""".format(self.table_path, d2str(d_from), d2str(d_to), limit)
        print("sql=", sql)
        for row in self.bq_client.query(sql).result():
            yield row

    def select_world(self, id):
        sql = "SELECT * FROM {} WHERE id = '{}' ORDER BY updated_at".format(self.table_path, id)
        print("sql=", sql)
        worlds = []
        for row in self.bq_client.query(sql).result():
            worlds.append(row)
        return worlds        

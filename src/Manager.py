import sys,os,json,re,html,urllib,time,math,datetime

from google.cloud import storage
from src.Config import Config, dt2str, d2str, str2ts
from src.VRC import VrcApi, VrcWorld
from src.BQ import BqClient
from src.Filter import SpreadSheet

class Manager:
    INDEX_LIMIT = 5000
    NEW_COMING_DAY = 28

    def __init__(self, config):
        self.config = config
        self.bq_client = BqClient()
        self.api = VrcApi(config.get('USERNAME'), config.get("PASSWORD"))

    def upload_bucket(self, path):
        filename = os.path.basename(path)

        client = storage.Client()
        bucket = storage.Bucket(client)
        bucket.name = Config.BUCKET_NAME
        blob = bucket.blob(filename)
        blob.upload_from_filename(path)

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
        time.sleep(0.3)
        worlds.extend(self.api.get_familiar_worlds())
        self.bq_client.insert_rows(list(map(lambda x: x.to_bq(), worlds)))

        with open(Config.CRAWLED_PATH, 'w') as f:
            json.dump({'last_updated':dt2str(last_updated)}, f)

    def insert_world(self, id, force):
        if not force:
            rows = self.bq_client.select_world(id)
            if len(rows) > 0:
                print("Already this worlds exists", rows[-1])
                return

        detail = self.api.get_world_detail(id)
        print("detail=", detail)
        if detail is None:
            print("Invalid world id=" + id)
            return
        self.bq_client.insert_rows([detail.to_bq()])
        print("Done")

    def update_index(self):
        rows = []
        deletes = []
        for w in self.bq_client.selecting_ranked_worlds(limit=Manager.INDEX_LIMIT):
            detail = self.api.get_world_detail(w['id'])
            if detail is None:
                detail = VrcWorld.bq_parse(w)
                if detail:
                    detail.set_deleted()
                    deletes.append(detail)
                continue
            rows.append(detail)
            if len(rows) % 50 == 0:
                print("update=", len(rows), "value=", w['_value'])
            time.sleep(0.5)

        with open(Config.INDEX_PATH, "w", encoding='utf-8') as f:
            for row in rows:
                f.write("\t".join(row.to_tsv()) + "\n")
        self.upload_bucket(Config.INDEX_PATH)

        if len(deletes) > 0:
            print("deltes[-1]=", deletes[-1])
            self.bq_client.insert_rows(list(map(lambda x: x.to_bq(), deletes)))

    def update_new_coming(self):
        news = []
        deletes = []
        for w in self.bq_client.selecting_new_coming_worlds(days=Manager.NEW_COMING_DAY):
            detail = self.api.get_world_detail(w['id'])
            if detail is None:
                detail = VrcWorld.bq_parse(w)
                if detail:
                    detail.set_deleted()
                    deletes.append(detail)
                continue
            news.append(detail)
            if len(news) % 50 == 0:
                print("update=", len(news))
            time.sleep(0.3)

        if len(news) > 0:
            news.sort(key=lambda x: x.fresh_value(), reverse=True)
            with open(Config.NEW_COMING_PATH, "w", encoding='utf-8') as f:
                for row in news:
                    f.write("\t".join(row.to_tsv()) + "\n")
            print("news[-1]=", row, "value=", row.fresh_value())
            self.upload_bucket(Config.NEW_COMING_PATH)
        if len(deletes) > 0:
            print("deltes[-1]=", deletes[-1])
            self.bq_client.insert_rows(list(map(lambda x: x.to_bq(), deletes)))
    
    def import_filter(self):
        ss = SpreadSheet()
        ss.test()


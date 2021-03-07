import sys,os,json,re,html,urllib,time,math,datetime,copy
from google.cloud import storage
import numpy

from src.Config import Config, dt2str, d2str, str2dt
from src.VRC import VrcApi, VrcWorld
from src.BQ import BqClient
from src.Filter import Filter
import src.DB as DB

class Manager:
    INDEX_LIMIT = 10000
    NEW_COMING_DAY = 21

    def __init__(self, config):
        self.config = config
        self.bq_client = BqClient()
        self.api = VrcApi(config.get('USERNAME'), config.get("PASSWORD"))
        self.filter = Filter()
        self.filter.import_from_spread_sheet(config.get('SHEET_KEY'))

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
                last_updated = str2dt(crawled['last_updated'])
        worlds = []
        rows = self.api.get_updated_worlds(last_updated)
        if len(rows) > 0:
            last_updated = rows[0].updated_at
            worlds.extend(rows)
        time.sleep(0.1)
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

    def update_index(self, limit=None):
        """
        update and re-index all worlds.
        """
        limit = Manager.INDEX_LIMIT if limit is None else limit
        rows = []
        deletes = []
        for w in self.bq_client.selecting_ranked_worlds(limit=limit):
            detail = self.api.get_world_detail(w['id'])
            if detail is None:
                detail = VrcWorld.bq_parse(w)
                if detail:
                    detail.set_deleted()
                    deletes.append(detail)
                continue
            if not self.filter.is_passed(detail):
                print("BAN=", detail)
                continue
            rows.append(detail)
            if len(rows) % 50 == 0:
                print("update=", len(rows), "value=", w['_value'])
            time.sleep(0.25)

        with open(Config.INDEX_PATH, "w", encoding='utf-8') as f:
            for row in rows:
                f.write("\t".join(row.to_tsv()) + "\n")
        self.upload_bucket(Config.INDEX_PATH)
        
        if len(deletes) > 0:
            print("deltes[-1]=", deletes[-1])
            self.bq_client.insert_rows(list(map(lambda x: x.to_bq(), deletes)))

        db = DB.DbAll(drop=True)
        db.insert_vrc(rows)
        self.upload_bucket(DB.VRC_ALL_PATH)

    def update_new_coming(self):
        """
        update and re-index new-coming worlds.
        """
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
            if not self.filter.is_passed(detail):
                print("BAN=", detail)
                continue
            news.append(detail)
            if len(news) % 50 == 0:
                print("update=", len(news))
            time.sleep(0.3)

        self.adjust_statistics(news)
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

        db = DB.DbComing(drop=True)
        db.insert(news)
        self.upload_bucket(DB.VRC_COMING_PATH)

    def update_last_month_index(self, today=None):
        """
        update and re-index month worlds.
        """
        if today is None:
            today = datetime.date.today()
        elif type(today) is str:
            today = str2dt(today)
        d_to = datetime.date(today.year, today.month, 1)
        d_tmp = d_to - datetime.timedelta(7) # last week
        d_from = datetime.date(d_tmp.year, d_tmp.month, 1)

        rows = []
        for w in self.bq_client.selecting_between(d_from, d_to):
            detail = self.api.get_world_detail(w['id'])
            if detail is None:
                continue
            if not self.filter.is_passed(detail):
                print("BAN=", detail)
                continue
            rows.append(detail)
            time.sleep(0.1)

        if len(rows) > 0:
            month_path = Config.make_month_path(d_from)
            with open(month_path, "w", encoding='utf-8') as f:
                for row in rows:
                    f.write("\t".join(row.to_tsv()) + "\n")
            print("rows[-1]=", row, "favorites=", row.favorites)
            self.upload_bucket(month_path)

        db = DB.DbMonths()
        db.insert(today.strftime("%y%m"), rows)
        self.upload_bucket(DB.VRC_MONTH_PATH)

    def adjust_statistics(self, worlds):
        fresh_values = list(map(lambda x: x.fresh_value(), worlds))
        all_ave = numpy.mean(fresh_values)
        all_std = numpy.std(fresh_values)
        avatar_values = list(map(lambda x: x.fresh_value(), filter(lambda x: "avatar" in x.description.lower(), worlds)))
        ava_ave = numpy.mean(avatar_values)
        ava_std = numpy.std(avatar_values)
        print("ave,std@all=", all_ave, all_std, "@ava=", ava_ave, ava_std)

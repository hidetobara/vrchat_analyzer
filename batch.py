import time,argparse,json
from google.cloud import storage
from src.Config import Config
from src.VRC import VrcApi
from src.Manager import Manager

c = Config("private/my_account.json")
api = VrcApi(c.get('USERNAME'), c.get("PASSWORD"))
manager = Manager()

cache_path = 'tmp/index.json'

def run_crawl_worlds():
    rows = api.get_created_worlds()
    time.sleep(1)
    rows.extend(api.get_published_worlds())
    time.sleep(1)
    rows.extend(api.get_familiar_worlds())

    manager.insert_rows(list(map(lambda x: x.to_bq(), rows)), "vrchat-analyzer.crawled.worlds")

def run_update_index():
    worlds = []
    for w in manager.selecting_ranked_worlds():
        detail = api.get_world_detail(w['id'])
        worlds.append(detail.to_web())
    data = {'worlds':worlds}
    with open(cache_path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    client = storage.Client()
    bucket = storage.Bucket(client)
    bucket.name = "vrchat-frontend"
    blob = bucket.blob("index.json")
    blob.upload_from_filename(cache_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--crawl_worlds", help="crawl updated, new-coming worlds", action="store_true")
    parser.add_argument("--update_index", help="update frontend-index", action="store_true")
    args = parser.parse_args()

    if args.crawl_worlds:
        run_crawl_worlds()
    if args.update_index:
        run_update_index()

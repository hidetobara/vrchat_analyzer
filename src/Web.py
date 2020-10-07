import os,json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './private/vrchat-analyzer-ba2bcb1497e6.json'
from google.cloud import storage
from src.Config import Config

class Web:
    def __init__(self, config):
        self.config = config

    def exist_index(self):
        return os.path.exists(Config.INDEX_PATH)

    def download_index(self):
        client = storage.Client()
        bucket = storage.Bucket(client)
        bucket.name = Config.BUCKET_NAME
        blob = bucket.blob("index.tsv")
        blob.download_to_filename(Config.INDEX_PATH)

    def selecting_index(self, offset=0, limit=10, query=None):
        array = []
        index = -1
        with open(Config.INDEX_PATH, "r", encoding='utf-8') as f:
            for line in f:
                index += 1
                if index < offset:
                    continue
                if query is None or query in line:
                    cells = line.split("\t")
                    ext = json.loads(cells[4])
                    array.append({
                        'col': len(array) % 3,
                        'id':cells[0], 'name':cells[1], 'author_name':cells[2], 'description':cells[3],
                        'launch_url':"https://www.vrchat.com/home/launch?worldId={}".format(cells[0]),
                        'thumbnail_image_url':ext['thumbnail_image_url'],
                        'is_last': False
                    })
                if len(array) >= limit:
                    break
        if len(array) > 0:
            array[-1]['is_last'] = True
        return array, index

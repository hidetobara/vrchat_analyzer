import os,json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './private/vrchat-analyzer-ba2bcb1497e6.json'
from google.cloud import storage
from src.Config import Config

class Web:
    def __init__(self, config):
        self.config = config

    def exist_cache(self, path):
        return os.path.exists(path)
    def download_cache(self, path):
        filename = os.path.basename(path)
        client = storage.Client()
        bucket = storage.Bucket(client)
        bucket.name = Config.BUCKET_NAME
        blob = bucket.blob(filename)
        blob.download_to_filename(path)

    def selecting_index(self, path, offset=0, limit=10, query=None):
        query = "" if query is None else query.lower()
        array = []
        index = -1
        with open(path, "r", encoding='utf-8') as f:
            is_end = True
            for line in f:
                index += 1
                if index < offset:
                    continue
                if query in line.lower():
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
                    is_end = False
                    break
        if len(array) > 0:
            array[-1]['is_last'] = True
        return array, None if is_end else index + 1

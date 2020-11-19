import os,json,datetime,shutil,glob,re
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './private/vrchat-analyzer-ba2bcb1497e6.json'
from google.cloud import storage
from src.Config import Config, epoch_to_datetime, dt2str

class Web:
    def __init__(self, config):
        self.config = config

    def extend_cache_date(self):
        today = datetime.date.today() - datetime.timedelta(hours=6)
        return "." + today.strftime("%y%m%d")
    def exist_cache(self, path):
        return os.path.exists(path + self.extend_cache_date())
    def download_cache(self, path):
        filename = os.path.basename(path)
        client = storage.Client()
        bucket = storage.Bucket(client)
        bucket.name = Config.BUCKET_NAME
        blob = bucket.blob(filename)
        blob.download_to_filename(path)
        shutil.copy(path, path + self.extend_cache_date())

    def get_locale(self):
        locale = 'en'
        languages = request.headers.get('Accept-Language').split(',')
        for language in languages:
            locale_long = language.split(';')[0]
            locale = locale_long.split('-')[0]
            break
        if locale not in ['ja', 'en']:
            locale = 'en'
        return locale.lower()

    def get_text(self, key):
        text = ''
        locale = self.get_locale()
        keys = key.split('.')
        path = '/app/lang/'+ locale +'/'+ '/'.join(keys[:-1]) +'.json'
        try:
            with open(path) as f:
                data = json.load(f)
                text = data[keys[-1]]
        except:
            pass
        return text

    def prepare(self):
        if not self.exist_cache(Config.INDEX_PATH):
            self.download_cache(Config.INDEX_PATH)
        if not self.exist_cache(Config.NEW_COMING_PATH):
            self.download_cache(Config.NEW_COMING_PATH)

    def get_index(self):
        self.prepare()
        worlds, offset_last = self.select_index(Config.NEW_COMING_PATH, 0, 12)
        context = { 'title':"Search VRC worlds", 'all_is_active':'active', 'worlds':worlds }
        return render_template('top.html', **context)

    def get_search(self):
        self.prepare()
        q = request.args.get('query')
        offset = request.args.get('offset', type=int)
        mode = request.args.get('mode')
        if q:
            q = re.sub('[ 　]+', ' ', q)
        if type(offset) is int:
            limit = 48
        else:
            offset = 0
            limit = 12
        
        if mode == "new_coming":
            worlds, offset_last = self.select_index(Config.NEW_COMING_PATH, offset, limit, q)
            context = { 'title':"Search VRC worlds", 'worlds':worlds, 'query':q, 'next':offset_last, 'coming_is_active':'active', 'mode':'new_coming' }
            return render_template('search.html', **context)
        else:
            worlds, offset_last = self.select_index(Config.INDEX_PATH, offset, limit, q)
            context = { 'title':"Search VRC worlds", 'worlds':worlds, 'query':q, 'next':offset_last, 'all_is_active':'active' }
            return render_template('search.html', **context)

    def select_index(self, path, offset=0, limit=10, query=None):
        query = "" if query is None else query.lower()
        keys = query.split(' ')
        array = []
        index = -1
        with open(path, "r", encoding='utf-8') as f:
            is_end = True
            for line in f:
                index += 1
                if index < offset:
                    continue
                hit = True
                for key in keys:
                    if key not in line.lower():
                        hit = False
                        break
                if hit:
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

    def get_tmp_info(self):
        data = []
        for p in glob.glob('/app/tmp/*'):
            path = Path(p)
            data.append({
                'path': p,
                'size': os.path.getsize(path),
                'created_at': dt2str(epoch_to_datetime(os.path.getctime(path)))
            })
        return jsonify(data)




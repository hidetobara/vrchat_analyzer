import os,json,datetime,shutil,glob,re
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './private/vrchat-analyzer-ba2bcb1497e6.json'
from google.cloud import storage
from src.Config import Config, epoch_to_datetime, dt2str

class Web:
    LIMIT = 24

    def __init__(self, config):
        self.config = config

    def exist_origin(self, path):
        return os.path.exists(path)
    def download_origin(self, path):
        filename = os.path.basename(path)
        client = storage.Client()
        bucket = storage.Bucket(client)
        bucket.name = Config.BUCKET_NAME
        blob = bucket.blob(filename)
        blob.download_to_filename(path)
    def extend_cache_date(self):
        today = datetime.date.today() - datetime.timedelta(hours=6)
        return "." + today.strftime("%y%m%d")
    def exist_cache(self, path):
        return os.path.exists(path + self.extend_cache_date())
    def download_cache(self, path):
        self.download_origin(path)
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

    def mode_to_str(self, mode):
        if mode is None:
            return None
        if 'new_coming' == mode:
            return self.get_text('search.recent')
        if 'last1' == mode:
            return self.get_text('search.last1')
        m = re.match(r'month(\d+)', mode)
        if m and len(m.group(1)) == 4:
            year_month = m.group(1)
            return '20' + year_month[0:2] + '/' + year_month[2:]
        return None

    def prepare(self):
        for p in [Config.INDEX_PATH, Config.NEW_COMING_PATH]:
            if not self.exist_cache(p):
                self.download_cache(p)
        for m in Config.get_old_months():
            p = Config.mode_to_path(m)
            if not self.exist_cache(p):
                self.download_cache(p)

    def get_index(self):
        self.prepare()
        worlds_coming, _ = self.select_index(Config.NEW_COMING_PATH, 0, Web.LIMIT)
        worlds_last1, _ = self.select_index(Config.make_last1_path(), 0, Web.LIMIT)
        olds = []
        for m in Config.get_old_months():
            worlds, _ = self.select_index(Config.mode_to_path(m), 0, 3)
            olds.append({'mode':m, 'title':self.mode_to_str(m), 'worlds':worlds})
        context = { 'coming_is_active':'active', 'worlds_coming':worlds_coming, 'worlds_last1':worlds_last1, 'olds':olds }
        return render_template('top1.html', **context)

    def get_search(self):
        self.prepare()
        q = request.args.get('q')
        p = request.args.get('p', type=int, default=0)
        mode = request.args.get('mode')
        if q:
            q = re.sub('[ 　]+', ' ', q)
        if p < 0:
            p = 0
        
        mode_path = Config.mode_to_path(mode)
        worlds, next_page = self.select_page(mode_path, p, q)
        context = {'worlds':worlds, 'q':'' if q is None else q, 'p':p, 'next':next_page, 'mode':mode, 'mode_name':self.mode_to_str(mode) }
        return render_template('search.html', **context)

    def select_page(self, path, page, query=None):
        array, index = self.select_index(path, page * Web.LIMIT, Web.LIMIT, query)
        return array, None if index is None else page + 1
    def select_index(self, path, offset=0, limit=10, query=None):
        query = "" if query is None else query.lower()
        keys = query.split(' ')
        array = []
        index = 0
        with open(path, "r", encoding='utf-8') as f:
            is_end = True
            for line in f:
                hit = True
                for key in keys:
                    if key not in line.lower():
                        hit = False
                        break
                if hit:
                    if offset <= index:
                        cells = line.split("\t")
                        ext = json.loads(cells[4])
                        array.append({
                            'index':index, 'col': len(array) % 3,
                            'id':cells[0], 'name':cells[1], 'author_name':cells[2], 'description':cells[3],
                            'launch_url':"https://www.vrchat.com/home/launch?worldId={}".format(cells[0]),
                            'thumbnail_image_url':ext['thumbnail_image_url'],
                            'is_last': False
                        })
                    index += 1
                if len(array) >= limit:
                    is_end = False
                    break
        if len(array) > 0:
            array[-1]['is_last'] = True
        return array, None if is_end else index 

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




import os,sys,traceback,json,datetime,time
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify

from src.Config import Config
from src.VRC import VrcApi
from src.Manager import ts2str, d2str, Manager

app = Flask(__name__)
manager = Manager()
c = Config("private/my_account.json")
#cache = 'tmp/index.{}.json'.format(d2str(datetime.date.today()))
cache = 'tmp/index.json'

@app.route('/')
def get_index():
    if os.path.exists(cache):
        with open(cache) as f:
            data = json.load(f)
    else:
        data = {'worlds':[], 'error':'No cache.'}

    context = { 'title':"Search VRC worlds", 'worlds': data['worlds'] }
    return render_template('index.html', **context)


#@app.route('/crawl_worlds', methods=['GET'])
def get_crawl_worlds():
    api = VrcApi(c.get('USERNAME'), c.get("PASSWORD"))
    rows = api.get_created_worlds()
    time.sleep(1)
    rows.extend(api.get_published_worlds())
    #time.sleep(1)
    #rows.extend(api.get_familiar_worlds())
    manager.insert_rows(list(map(lambda x: x.to_bq(), rows)), "vrchat-analyzer.crawled.worlds")
    return jsonify({'result':'ok', 'len':len(rows)})

#@app.route('/update_index', methods=['GET'])
def get_update_index():
    api = VrcApi(c.get('USERNAME'), c.get("PASSWORD"))
    worlds = []
    for w in manager.selecting_ranked_worlds():
        detail = api.get_world_detail(w['id'])
        worlds.append(detail.to_web())
    data = {'worlds':worlds}
    with open(cache, "w") as f:
        json.dump(data, f, ensure_ascii=False)
    return jsonify({'result':'ok', 'len':len(worlds)})

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8080)

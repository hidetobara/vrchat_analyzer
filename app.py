import os,sys,traceback,json
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify

from src.Config import Config
from src.Web import Web

app = Flask(__name__)
c = Config("private/my_account.json")
web = Web(c)

@app.route('/', methods=['GET'])
def get_index():
    worlds, offset_last = web.selecting_index(Config.NEW_COMING_PATH, 0, 12)
    context = { 'title':"Search VRC worlds", 'all_is_active':'active', 'worlds':worlds }
    return render_template('top.html', **context)

@app.route('/search', methods=['GET'])
def get_search():
    q = request.args.get('query')
    offset = request.args.get('offset', type=int)
    mode = request.args.get('mode')
    if type(offset) is int:
        limit = 48
    else:
        offset = 0
        limit = 12
    if mode == "new_coming":
        worlds, offset_last = web.selecting_index(Config.NEW_COMING_PATH, offset, limit, q)
        context = { 'title':"Search VRC worlds", 'worlds':worlds, 'query':q, 'next':offset_last, 'coming_is_active':'active', mode:'new_coming' }
        return render_template('search.html', **context)
    else:
        worlds, offset_last = web.selecting_index(Config.INDEX_PATH, offset, limit, q)
        context = { 'title':"Search VRC worlds", 'worlds':worlds, 'query':q, 'next':offset_last, 'all_is_active':'active' }
        return render_template('search.html', **context)

if __name__ == "__main__":
    if not web.exist_cache(Config.INDEX_PATH):
        web.download_cache(Config.INDEX_PATH)
    if not web.exist_cache(Config.NEW_COMING_PATH):
        web.download_cache(Config.NEW_COMING_PATH)
    app.run(debug=True,host='0.0.0.0',port=8080)

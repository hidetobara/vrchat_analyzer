import os,sys,traceback,json
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify

from src.Config import Config
from src.Web import Web

app = Flask(__name__)
c = Config("private/my_account.json")
web = Web(c)

@app.route('/', methods=['GET'])
def get_index():
    if not web.exist_index():
        web.download_index()

    worlds, _ = web.selecting_index(0, 12)
    context = { 'title':"Search VRC worlds", 'worlds':worlds }
    return render_template('index.html', **context)

@app.route('/search', methods=['GET'])
def get_search():
    q = request.args.get('query')
    offset_current = request.args.get('offset', type=int)
    if offset_current is None:
        offset_current = -1
    worlds, offset_next = web.selecting_index(offset_current + 1, 12, q)
    context = { 'title':"Search VRC worlds", 'worlds':worlds, 'query':q, 'current':offset_current, 'next':offset_next }
    return render_template('index.html', **context)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8080)

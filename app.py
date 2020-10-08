import os,sys,traceback,json
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify

from src.Config import Config
from src.Web import Web

app = Flask(__name__)
c = Config("private/my_account.json")
web = Web(c)

@app.route('/', methods=['GET'])
def get_index():
    context = { 'title':"Search VRC worlds" }
    return render_template('top.html', **context)

@app.route('/search', methods=['GET'])
def get_search():
    q = request.args.get('query')
    offset = request.args.get('offset', type=int)
    if type(offset) is int:
        limit = 48
    else:
        offset = 0
        limit = 12
    worlds, offset_last = web.selecting_index(offset, limit, q)
    context = { 'title':"Search VRC worlds", 'worlds':worlds, 'query':q, 'next':offset_last }
    return render_template('search.html', **context)

if __name__ == "__main__":
    if not web.exist_index():
        web.download_index()
    app.run(debug=True,host='0.0.0.0',port=8080)

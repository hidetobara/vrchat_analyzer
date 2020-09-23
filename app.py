import os,sys,traceback,json
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify

from google.cloud import storage
from src.Config import Config
from src.VRC import VrcApi
from src.Manager import ts2str, d2str, Manager

app = Flask(__name__)
c = Config("private/my_account.json")
manager = Manager(c)
cache_path = 'tmp/index.json'

@app.route('/', methods=['GET'])
def get_index():
    if not os.path.exists(cache_path):
        manager.download_index()
    with open(cache_path) as f:
        data = json.load(f)

    context = { 'title':"Search VRC worlds", 'worlds': data['worlds'] }
    return render_template('index.html', **context)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8080)

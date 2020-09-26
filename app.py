import os,sys,traceback,json
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify

from google.cloud import storage
from src.Config import Config
from src.VRC import VrcApi
from src.Manager import ts2str, d2str, Manager

app = Flask(__name__)
c = Config("private/my_account.json")
manager = Manager(c)

@app.route('/', methods=['GET'])
def get_index():
    if not manager.exist_index():
        manager.download_index()

    worlds = manager.selecting_index()
    context = { 'title':"Search VRC worlds", 'worlds':worlds }
    return render_template('index.html', **context)

@app.route('/search', methods=['GET'])
def get_search():
    q = request.args.get('query')
    worlds = manager.selecting_index(0, 10, q)
    context = { 'title':"Search VRC worlds", 'worlds':worlds, 'query':q }
    return render_template('index.html', **context)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8080)

import os,sys,traceback,json
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './private/vrchat-analyzer-ba2bcb1497e6.json'
from src.Config import Config
from src.Web import Web

app = Flask(__name__)
c = Config("private/my_account.json")
web = Web(c)

@app.context_processor
def utility_processor():
    return dict(_=web.get_text, get_locale=web.get_locale)

@app.route('/', methods=['GET'])
def get_index():
    return web.get_index()

@app.route('/search', methods=['GET'])
def get_search():
    return web.get_search()

@app.route('/tmp_info', methods=['GET'])
def get_tmp_info():
    return web.get_tmp_info()

if __name__ == "__main__":
    web.prepare()
    app.run(debug=True,host='0.0.0.0',port=8080)

from flask import Flask, request, send_from_directory
import os
from licenseInfo import *

app = Flask(__name__)

@app.route('/')
def serve_static_index():
    root_dir = os.path.dirname(os.getcwd())
    print(os.path.join(root_dir, 'static'))
    return send_from_directory(os.path.join(root_dir, 'backend'), "index.html")

@app.route('/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    print(os.path.join(root_dir, 'static'))
    return send_from_directory(os.path.join(root_dir, 'backend'), filename)

@app.route('/api/<owner>/<repo>', methods=['GET'])
def get_tasks(owner, repo):
    return retrieve_license_information(owner, repo)

if __name__ == "__main__":
    app.run(host='127.0.0.1',port='5555', 
        debug = True, ssl_context='adhoc')
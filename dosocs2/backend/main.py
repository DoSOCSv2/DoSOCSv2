from flask import Flask, request, send_from_directory
import os
from licenseInfo import *
from packageInfo import *

app = Flask(__name__)

@app.route('/')
def serve_static_index():
    root_dir = os.path.dirname(os.getcwd())
    print(os.path.join(root_dir, 'backend'))
    return send_from_directory(os.path.join(root_dir, 'backend'), "index.html")

@app.route('/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    print(os.path.join(root_dir, 'backend'))
    return send_from_directory(os.path.join(root_dir, 'backend'), filename)

@app.route('/api/<owner>/<repo>', methods=['GET'])
def get_package(owner, repo):
    return app.response_class(
        response=retrieve_license_information(owner, repo),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/<owner>/<repo>/package', methods=['GET'])
def get_tasks(owner, repo):
    return app.response_class(
        response=retrieve_package_information(owner, repo),
        status=200,
        mimetype='application/json'
    )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5555))
    app.run(host='0.0.0.0',port=port,
        debug = True)
def api_link(owner, repo):
    return url_for(serve_Static_index) + "/" + owner + "/" + repo

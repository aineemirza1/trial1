from __future__ import unicode_literals
from flask import Flask, render_template, request
from flask_json import FlaskJSON, json_response

app = Flask(__name__)
FlaskJSON(app)
STATUS_OK = "ok"
STATUS_ERROR = "error"


@app.route('/')
def gui():
    return json_response(status="success", data="Hello GUI")

@app.route('/in')
def ind():
    return render_template('new.html')
   


@app.route('/index', methods=['POST'])
def index():
    return json_response(status="success", data="Hello Word")


if __name__ == '__main__':
    app.debug = True
    app.run()

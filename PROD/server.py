import numpy as np
import pandas as pd
import pickle


from flask import Flask, request, jsonify
import datetime


with open("./data/model.pkl", 'rb') as pkl_model:
    model = pickle.load(pkl_model)

app = Flask(__name__)


@app.route('/')
def index():
    return "Test message. The server is running"


@app.route("/add", methods=["POST"])
def add():
    num = request.json.get("num")
    if num > 10:
        return 'too much', 400

    return jsonify({
        'result': num + 1
    })


@app.route("/predict", methods=["POST"])
def prediction():

    features = request.json
    features = np.array(features).reshape(1, 4)

    pred = model.predict(features)

    return jsonify({"prediction": pred[0]})


@app.route("/time")
def current_time():
    return {'time': datetime.datetime.now()}


@app.route('/hello')
def hello_funk():
    name = request.args.get("name")
    return f"hello {name}"


if __name__ == '__main__':
    app.run('localhost', 8000)


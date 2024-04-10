import subprocess

import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run_rs", methods=["POST"])
def run_rs():
    try:
        subprocess.run(["python", "rs_system.py"], check=True)
        return jsonify({"message": "rs_system.py executed successfully"})
    except subprocess.CalledProcessError as e:
        return jsonify(
            {"error": f"An error occurred while executing rs_system.py: {e}"}
        )


@app.route("/recommend", methods=["GET"])
def recommend():

    try:
        recommendation_df = pd.read_csv("./data/final_backup.csv")
    except FileNotFoundError:
        recommendation_df = pd.DataFrame()

    try:
        user_id = int(request.args.get("user_id"))
    except ValueError:
        return "Invalid ID. Please enter ineger."

    if recommendation_df.empty:
        return jsonify(
            {
                "error": "Recommendation data is not available. Please run the rs_system script first."
            }
        )
    else:
        user_recommendations = recommendation_df[recommendation_df["users"] == user_id][
            "recommendations"
        ].values
        if len(user_recommendations) > 0:
            return jsonify(
                {"user_id": user_id, "recommendations": user_recommendations[0]}
            )
        else:
            return jsonify(
                {"user_id": user_id, "recommendations": "No recommendations"}
            )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

from flask import Flask, jsonify, render_template, request
import pandas as pd
from rs_system import rs_system, default_recommendation

app = Flask(__name__)

try:
    recommendation_df = pd.read_csv("./data/final_backup.csv")
except FileNotFoundError:
    recommendation_df = pd.DataFrame()

def run_rs_system_script(events_raw):
    try:
        recommendation_df = rs_system(events_raw)
        default_rec_df = default_recommendation(events_raw, recommendation_df)
        final_df = pd.concat([recommendation_df, default_rec_df]).reset_index(drop=True)
        final_df.to_csv("./data/final_backup.csv", index=0)
        return True
    except KeyError as e:
        print(f"KeyError: {e}")
        return False
    except ValueError as e:
        print(f"ValueError: {e}")
        return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run_rs", methods=["POST"])
def run_rs():
    events_raw = pd.read_csv("./data/events.csv")
    success = run_rs_system_script(events_raw)
    if success:
        return jsonify({"message": "rs_system.py executed successfully"})
    else:
        return jsonify({"error": "An error occurred while executing rs_system.py"})


@app.route("/recommend", methods=["GET"])
def recommend():
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

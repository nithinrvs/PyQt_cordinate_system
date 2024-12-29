from flask import Flask, request, jsonify

app = Flask(__name__)

# List to store clicked points
points = []

@app.route("/save_point", methods=["POST"])
def save_point():
    data = request.json
    points.append((data["x"], data["y"]))
    return jsonify({"message": "Point saved", "points": points})

@app.route("/get_points", methods=["GET"])
def get_points():
    return jsonify(points)

if __name__ == "__main__":
    app.run(debug=True)

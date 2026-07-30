from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import Flask, abort, jsonify, render_template

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "intersections.json"


def load_intersections() -> list[dict[str, Any]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise RuntimeError("intersections.json must contain a list.")

    return data


def find_intersection(intersection_id: str) -> dict[str, Any] | None:
    for intersection in load_intersections():
        if intersection.get("id") == intersection_id:
            return intersection
    return None


@app.get("/")
def home():
    return render_template(
        "index.html",
        intersections=load_intersections(),
    )


@app.get("/crossing-demo")
def crossing_demo():
    return render_template("crossing_demo.html")


@app.get("/intersection/<intersection_id>")
def intersection_detail(intersection_id: str):
    intersection = find_intersection(intersection_id)

    if intersection is None:
        abort(404)

    return render_template(
        "intersection.html",
        intersection=intersection,
    )


# Future-ready prototype API routes.
@app.get("/api/intersections")
def api_intersections():
    return jsonify(load_intersections())


@app.get("/api/intersections/<intersection_id>")
def api_intersection(intersection_id: str):
    intersection = find_intersection(intersection_id)

    if intersection is None:
        return jsonify({"error": "Intersection not found"}), 404

    return jsonify(intersection)


if __name__ == "__main__":
    app.run(debug=True)

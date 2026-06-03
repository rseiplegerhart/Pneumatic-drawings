"""
Flask web app for generating pneumatic drawings.
Run: python web/app.py
Then open: http://localhost:5000
"""

import io
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, send_file, jsonify
from pneumatic.circuit import Circuit, Component
from pneumatic.renderer import render_pdf

app = Flask(__name__)


@app.route("/")
def index():
    today = date.today().strftime("%Y-%m-%d")
    return render_template("index.html", today=today)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    circuit = Circuit(
        title=data.get("title", "Pneumatic Circuit"),
        drawn_by=data.get("drawn_by", ""),
        date=data.get("date", ""),
    )

    for comp in data.get("components", []):
        circuit.add(Component(
            comp_type=comp["comp_type"],
            label=comp["label"],
            tag=comp["tag"].upper(),
            actuator=comp.get("actuator", "solenoid"),
            spring_return=comp.get("spring_return", True),
            position=(int(comp.get("col", 0)), int(comp.get("row", 0))),
        ))

    for conn in data.get("connections", []):
        circuit.connect(
            conn["from_tag"].upper(), conn["from_port"],
            conn["to_tag"].upper(),   conn["to_port"],
        )

    # Render to an in-memory buffer
    buf = io.BytesIO()
    # render_pdf accepts a file path; use a temp path then read back
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        render_pdf(circuit, tmp_path)
        with open(tmp_path, "rb") as f:
            buf.write(f.read())
    finally:
        os.unlink(tmp_path)

    buf.seek(0)
    filename = (circuit.title or "circuit").replace(" ", "_") + ".pdf"
    return send_file(buf, mimetype="application/pdf",
                     as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

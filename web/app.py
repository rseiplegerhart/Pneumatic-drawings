"""
Flask web app for generating pneumatic drawings.
Run: python web/app.py
Then open: http://localhost:5000

Set ANTHROPIC_API_KEY environment variable to enable AI circuit generation.
"""

import io
import sys
import os
import json
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, send_file, jsonify
from pneumatic.circuit import Circuit, Component
from pneumatic.renderer import render_pdf

app = Flask(__name__)

COMPONENTS_DIR = Path(__file__).parent.parent / "components"

CIRCUIT_SYSTEM_PROMPT = """You are an expert pneumatic circuit designer following ISO 1219-1 standards.
Given a description of a pneumatic circuit, output a JSON circuit definition — nothing else, no explanation.

Available component types:
  cylinder_da   – Double-acting cylinder
  cylinder_sa   – Single-acting cylinder (spring return)
  valve_52      – 5/2 directional control valve (fields: actuator, spring_return)
  valve_32      – 3/2 directional control valve NC (fields: actuator, spring_return)
  flow_control  – Flow control / one-way throttle
  check_valve   – Check valve (non-return)
  pressure_regulator – Adjustable pressure regulator
  gauge         – Pressure gauge
  supply        – Compressed air supply
  exhaust       – Exhaust to atmosphere

Actuator values (for valves): solenoid, manual, pilot, spring
spring_return: true or false

Grid layout: col/row integers, 0-based. Place supply at col 0 row 0, route left→right in airflow order.
Keep row 0 for the main supply line, row 1+ for branches/actuators.

Port naming conventions:
  supply:               "A" (outlet)
  pressure_regulator:   "P" (inlet), "A" (outlet)
  gauge:                "P" (inlet)
  valve_52:             "1" (supply in), "2(A)" (work A out), "4(B)" (work B out), "3" (exhaust A), "5" (exhaust B)
  valve_32:             "1(P)" (supply), "2(A)" (work out), "3(R)" (exhaust)
  flow_control:         "P" (inlet), "A" (outlet)
  check_valve:          "P" (inlet), "A" (outlet)
  cylinder_da:          "A" (extend port), "B" (retract port)
  cylinder_sa:          "A" (extend port)

Return ONLY a JSON object in this exact structure (no markdown, no extra text):
{
  "title": "descriptive title",
  "drawn_by": "",
  "date": "YYYY-MM-DD",
  "components": [
    {"comp_type": "supply", "tag": "AIR", "label": "Air Supply", "col": 0, "row": 0},
    {"comp_type": "valve_52", "tag": "V1", "label": "Main Valve", "actuator": "solenoid", "spring_return": true, "col": 2, "row": 0}
  ],
  "connections": [
    {"from_tag": "AIR", "from_port": "A", "to_tag": "PR1", "to_port": "P"}
  ]
}"""


def load_component_library() -> list[dict]:
    """Load component definition files from the components/ directory."""
    items = []
    if COMPONENTS_DIR.exists():
        for f in sorted(COMPONENTS_DIR.glob("*.json")):
            try:
                items.append(json.loads(f.read_text()))
            except Exception:
                pass
    return items


@app.route("/")
def index():
    today = date.today().strftime("%Y-%m-%d")
    ai_enabled = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return render_template("index.html", today=today, ai_enabled=ai_enabled)


@app.route("/interpret", methods=["POST"])
def interpret():
    """Use Claude to turn a natural language prompt into a circuit definition."""
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"error": "ANTHROPIC_API_KEY is not set on the server."}), 500

    data = request.get_json()
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Please enter a description."}), 400

    # Build the user message — include component library if any files exist
    library = load_component_library()
    if library:
        lib_text = json.dumps(library, indent=2)
        user_msg = (
            f"Component library (use these where they match the request):\n{lib_text}\n\n"
            f"Request: {prompt}"
        )
    else:
        user_msg = prompt

    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=CIRCUIT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )

        text = next((b.text for b in response.content if b.type == "text"), "")

        # Strip markdown code fences if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        circuit_data = json.loads(text)
        return jsonify(circuit_data)

    except json.JSONDecodeError as e:
        return jsonify({"error": f"Claude returned invalid JSON: {e}"}), 500
    except anthropic.APIError as e:
        return jsonify({"error": str(e)}), 500


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

    buf = io.BytesIO()
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

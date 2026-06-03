# Pneumatic Drawing Generator

Generates ISO 1219-1 pneumatic circuit drawings as A3 landscape PDFs using Python + reportlab.

## Primary Workflow

When the user describes a pneumatic circuit, do this:

1. Read all files in `components/*.json` — these are real equipment specs to use where tags match
2. Write a Python script in `output/` (e.g. `output/station2_clamp.py`) using the API below
3. Run it: `python output/station2_clamp.py`
4. The PDF lands in `output/` (e.g. `output/station2_clamp.pdf`)
5. Commit and push so the user can download from GitHub

PDFs are gitignored. Commit the `.py` script so the drawing can be regenerated.

---

## Python API

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pneumatic.circuit import Circuit, Component
from pneumatic.renderer import render_pdf

circuit = Circuit(title="Station 2 Clamp", drawn_by="", date="2026-06-03")

circuit.add(Component(comp_type="supply",             tag="AIR",  label="Air Supply",         position=(0, 0)))
circuit.add(Component(comp_type="pressure_regulator", tag="PR1",  label="Supply Regulator",   position=(1, 0)))
circuit.add(Component(comp_type="gauge",              tag="G1",   label="Line Gauge",         position=(2, 0)))
circuit.add(Component(comp_type="valve_52",           tag="V1",   label="Main Control Valve", position=(3, 0), actuator="solenoid", spring_return=True))
circuit.add(Component(comp_type="flow_control",       tag="FC1",  label="Extend Speed",       position=(4, 1)))
circuit.add(Component(comp_type="flow_control",       tag="FC2",  label="Retract Speed",      position=(4, 2)))
circuit.add(Component(comp_type="cylinder_da",        tag="CYL1", label="Clamp Cylinder",     position=(5, 1)))

circuit.connect("AIR",  "A",    "PR1",  "P")
circuit.connect("PR1",  "A",    "G1",   "P")
circuit.connect("G1",   "P",    "V1",   "1")
circuit.connect("V1",   "2(A)", "FC1",  "P")
circuit.connect("FC1",  "A",    "CYL1", "A")
circuit.connect("V1",   "4(B)", "FC2",  "P")
circuit.connect("FC2",  "A",    "CYL1", "B")

render_pdf(circuit, os.path.join(os.path.dirname(__file__), "station2_clamp.pdf"))
print("Done.")
```

---

## Component Types

| comp_type            | Description                        |
|----------------------|------------------------------------|
| `supply`             | Compressed air supply              |
| `exhaust`            | Exhaust to atmosphere              |
| `pressure_regulator` | Adjustable pressure regulator      |
| `gauge`              | Pressure gauge                     |
| `valve_52`           | 5/2 directional control valve      |
| `valve_32`           | 3/2 directional control valve (NC) |
| `flow_control`       | One-way flow control / throttle    |
| `check_valve`        | Check valve (non-return)           |
| `cylinder_da`        | Double-acting cylinder             |
| `cylinder_sa`        | Single-acting cylinder             |

Valve fields: `actuator` = `"solenoid"` | `"manual"` | `"pilot"` | `"spring"`, `spring_return` = `True` | `False`

---

## Port Names

| Component            | Ports                                                  |
|----------------------|--------------------------------------------------------|
| `supply`             | `"A"` (outlet)                                         |
| `pressure_regulator` | `"P"` (inlet), `"A"` (outlet)                          |
| `gauge`              | `"P"` (inlet)                                          |
| `valve_52`           | `"1"` (supply), `"2(A)"` (work A), `"4(B)"` (work B), `"3"` (exhaust A), `"5"` (exhaust B) |
| `valve_32`           | `"1(P)"` (supply), `"2(A)"` (work out), `"3(R)"` (exhaust) |
| `flow_control`       | `"P"` (inlet), `"A"` (outlet)                          |
| `check_valve`        | `"P"` (inlet), `"A"` (outlet)                          |
| `cylinder_da`        | `"A"` (extend port), `"B"` (retract port)              |
| `cylinder_sa`        | `"A"` (extend port)                                    |

---

## Grid Layout

`position=(col, row)` — integers, 0-based.

- Row 0: main supply line (supply → regulator → gauge → valve)
- Row 1+: branches (flow controls, cylinders)
- Place supply at col 0, route left → right in airflow order
- Keep col spacing consistent; valves are wide so leave a gap after them

---

## Component Library (`components/*.json`)

Each file defines a specific piece of equipment. Fields beyond the core ones
(manufacturer, model, bore_mm, etc.) are informational — copy `tag`, `comp_type`,
`label`, `actuator`, `spring_return` into the script. Example:

```json
{
  "tag": "CYL1",
  "comp_type": "cylinder_da",
  "label": "Clamp Cylinder",
  "manufacturer": "Festo",
  "model": "DNC-63-200-PPV",
  "bore_mm": 63,
  "stroke_mm": 200
}
```

When the user asks for a drawing, check these files first. If a component in the
request matches a file's tag or description, use the exact tag and label from the file.

---

## Adding New Equipment to the Library

Create `components/<name>.json` with at minimum:
```json
{ "tag": "XX1", "comp_type": "<type>", "label": "Description" }
```
Add actuator/spring_return for valves, bore/stroke for cylinders, set_pressure_bar for regulators.

---

## Output Directory

Scripts and PDFs go in `output/`. The directory is gitignored for PDFs but scripts are committed.
Create the directory if it doesn't exist: `mkdir -p output`

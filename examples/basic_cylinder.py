"""
Example: 5/2 solenoid valve driving a double-acting cylinder,
with upstream pressure regulator, gauge, and exhaust valves.
Run: python examples/basic_cylinder.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pneumatic.circuit import Circuit, Component
from pneumatic.renderer import render_pdf

circuit = Circuit(
    title="Basic Cylinder Circuit",
    drawn_by="Engineer",
    date="2026-05-27",
)

circuit.add(Component("supply",             "Air Supply",          "AIR",  position=(0, 0)))
circuit.add(Component("pressure_regulator", "Pressure Regulator",  "PR1",  position=(1, 0)))
circuit.add(Component("gauge",              "Supply Gauge",        "PG1",  position=(2, 0)))
circuit.add(Component("valve_52",           "5/2 Solenoid Valve",  "V1",   actuator="solenoid", spring_return=True, position=(3, 0)))
circuit.add(Component("flow_control",       "Speed Control A",     "FC1",  position=(4, 0)))
circuit.add(Component("flow_control",       "Speed Control B",     "FC2",  position=(5, 0)))
circuit.add(Component("cylinder_da",        "Clamp Cylinder",      "CYL1", position=(4, 1)))
circuit.add(Component("exhaust",            "Exhaust",             "EXH1", position=(2, 1)))

circuit.connect("AIR",  "A",  "PR1",  "P")
circuit.connect("PR1",  "A",  "PG1",  "P")
circuit.connect("PG1",  "A",  "V1",   "1")
circuit.connect("V1",   "2",  "FC1",  "P")
circuit.connect("V1",   "4",  "FC2",  "P")
circuit.connect("FC1",  "A",  "CYL1", "A")
circuit.connect("FC2",  "A",  "CYL1", "B")
circuit.connect("V1",   "3",  "EXH1", "P")

render_pdf(circuit, "basic_cylinder.pdf")

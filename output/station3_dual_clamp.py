import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pneumatic.circuit import Circuit, Component
from pneumatic.renderer import render_pdf

circuit = Circuit(
    title="Station 3 — Dual Clamp Cylinders",
    drawn_by="",
    date="2026-06-03",
)

# ── Supply rail (row 0) ──────────────────────────────────────────────────────
circuit.add(Component(comp_type="supply",             tag="AIR",  label="Air Supply",          position=(0, 0)))
circuit.add(Component(comp_type="pressure_regulator", tag="PR1",  label="Supply Regulator",    position=(1, 0)))  # Norgren B64G-4GK-AD3-RMG, 6 bar
circuit.add(Component(comp_type="gauge",              tag="G1",   label="Line Gauge",          position=(2, 0)))
circuit.add(Component(comp_type="valve_52",           tag="V1",   label="Clamp 1 Valve",       position=(3, 0), actuator="solenoid", spring_return=True))  # SMC VF3130-5G-02
circuit.add(Component(comp_type="valve_52",           tag="V2",   label="Clamp 2 Valve",       position=(6, 0), actuator="solenoid", spring_return=True))  # SMC VF3130-5G-02

# ── Cylinder 1 branches ──────────────────────────────────────────────────────
circuit.add(Component(comp_type="flow_control",  tag="FC1",  label="Cyl 1 Extend Speed",  position=(4, 1)))
circuit.add(Component(comp_type="flow_control",  tag="FC2",  label="Cyl 1 Retract Speed", position=(4, 2)))
circuit.add(Component(comp_type="cylinder_da",   tag="CYL1", label="Clamp Cylinder 1",    position=(5, 1)))  # Festo DNC-63-200-PPV, ø63 x 200mm

# ── Cylinder 2 branches ──────────────────────────────────────────────────────
circuit.add(Component(comp_type="flow_control",  tag="FC3",  label="Cyl 2 Extend Speed",  position=(7, 1)))
circuit.add(Component(comp_type="flow_control",  tag="FC4",  label="Cyl 2 Retract Speed", position=(7, 2)))
circuit.add(Component(comp_type="cylinder_da",   tag="CYL2", label="Clamp Cylinder 2",    position=(8, 1)))  # Festo DNC-63-200-PPV, ø63 x 200mm

# ── Supply connections ───────────────────────────────────────────────────────
circuit.connect("AIR",  "A",    "PR1",  "P")
circuit.connect("PR1",  "A",    "G1",   "P")
circuit.connect("G1",   "P",    "V1",   "1")
circuit.connect("V1",   "1",    "V2",   "1")   # supply rail continues to V2

# ── Cylinder 1 — extend path ─────────────────────────────────────────────────
circuit.connect("V1",   "2(A)", "FC1",  "P")
circuit.connect("FC1",  "A",    "CYL1", "A")

# ── Cylinder 1 — retract path ────────────────────────────────────────────────
circuit.connect("V1",   "4(B)", "FC2",  "P")
circuit.connect("FC2",  "A",    "CYL1", "B")

# ── Cylinder 2 — extend path ─────────────────────────────────────────────────
circuit.connect("V2",   "2(A)", "FC3",  "P")
circuit.connect("FC3",  "A",    "CYL2", "A")

# ── Cylinder 2 — retract path ────────────────────────────────────────────────
circuit.connect("V2",   "4(B)", "FC4",  "P")
circuit.connect("FC4",  "A",    "CYL2", "B")

output_path = os.path.join(os.path.dirname(__file__), "station3_dual_clamp.pdf")
render_pdf(circuit, output_path)

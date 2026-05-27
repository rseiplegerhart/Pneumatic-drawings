"""
Interactive CLI for building pneumatic circuit drawings.
Run: python -m pneumatic.cli
"""

import sys
from datetime import date
from .circuit import Circuit, Component
from .renderer import render_pdf

COMP_TYPES = {
    "1": ("cylinder_da",        "Double-acting cylinder"),
    "2": ("cylinder_sa",        "Single-acting cylinder (spring return)"),
    "3": ("valve_52",           "5/2 Directional control valve"),
    "4": ("valve_32",           "3/2 Directional control valve (NC)"),
    "5": ("flow_control",       "Flow control valve"),
    "6": ("check_valve",        "Check valve"),
    "7": ("pressure_regulator", "Pressure regulator"),
    "8": ("gauge",              "Pressure gauge"),
    "9": ("supply",             "Compressed air supply"),
    "10": ("exhaust",           "Exhaust to atmosphere"),
}

ACTUATORS = {
    "1": "solenoid",
    "2": "manual",
    "3": "pilot",
    "4": "spring",
}


def _prompt(msg: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{msg}{suffix}: ").strip()
    return val if val else default


def _prompt_int(msg: str, default: int, lo: int = 0, hi: int = 99) -> int:
    while True:
        raw = _prompt(msg, str(default))
        try:
            v = int(raw)
            if lo <= v <= hi:
                return v
        except ValueError:
            pass
        print(f"  Please enter a number between {lo} and {hi}.")


def _choose_component() -> tuple[str, str] | None:
    print("\n  Component types:")
    for k, (_, label) in COMP_TYPES.items():
        print(f"    {k:>2}. {label}")
    print("     q. Done adding components")
    choice = _prompt("  Choose").lower()
    if choice == "q":
        return None
    if choice not in COMP_TYPES:
        print("  Invalid choice.")
        return _choose_component()
    return COMP_TYPES[choice]


def _choose_actuator() -> str:
    print("  Actuator type:  1=Solenoid  2=Manual  3=Pilot  4=Spring")
    choice = _prompt("  Choose", "1")
    return ACTUATORS.get(choice, "solenoid")


def run() -> None:
    print("=" * 60)
    print("  Pneumatic Drawing Generator  |  ISO 1219-1")
    print("=" * 60)

    title   = _prompt("Drawing title", "Pneumatic Circuit")
    drawn_by = _prompt("Drawn by", "")
    today   = date.today().strftime("%Y-%m-%d")
    drawing_date = _prompt("Date", today)
    output  = _prompt("Output PDF filename", "circuit.pdf")
    if not output.endswith(".pdf"):
        output += ".pdf"

    circuit = Circuit(title=title, drawn_by=drawn_by, date=drawing_date)

    print("\n--- Add components (enter 'q' when done) ---")
    comp_count = 0
    used_cols: dict[int, int] = {}   # col → next available row

    while True:
        result = _choose_component()
        if result is None:
            break
        comp_type, default_label = result

        tag   = _prompt("  Tag (e.g. CYL1, V1)", f"C{comp_count + 1}")
        label = _prompt("  Description", default_label)
        col   = _prompt_int("  Grid column (0-based)", comp_count % 5, 0, 20)
        row   = used_cols.get(col, 0)
        used_cols[col] = row + 1

        actuator = "solenoid"
        spring_return = True
        if comp_type in ("valve_52", "valve_32"):
            actuator = _choose_actuator()
            sr = _prompt("  Spring return? (y/n)", "y").lower()
            spring_return = sr != "n"

        comp = Component(
            comp_type=comp_type,
            label=label,
            tag=tag,
            actuator=actuator,
            spring_return=spring_return,
            position=(col, row),
        )
        circuit.add(comp)
        comp_count += 1
        print(f"  Added {tag} at grid ({col},{row})")

    if not circuit.components:
        print("No components added. Exiting.")
        sys.exit(0)

    print("\n--- Add connections (enter 'q' when done) ---")
    tags = [c.tag for c in circuit.components]
    print(f"  Available tags: {', '.join(tags)}")
    while True:
        from_tag = _prompt("  From tag (or 'q' to finish)").upper()
        if from_tag == "Q":
            break
        if from_tag not in tags:
            print(f"  Unknown tag '{from_tag}'.")
            continue
        from_port = _prompt("  From port", "A")
        to_tag = _prompt("  To tag").upper()
        if to_tag not in tags:
            print(f"  Unknown tag '{to_tag}'.")
            continue
        to_port = _prompt("  To port", "P")
        circuit.connect(from_tag, from_port, to_tag, to_port)
        print(f"  Connected {from_tag}/{from_port} → {to_tag}/{to_port}")

    print("\nGenerating PDF...")
    try:
        render_pdf(circuit, output)
        print(f"\nDone!  Drawing saved to: {output}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()

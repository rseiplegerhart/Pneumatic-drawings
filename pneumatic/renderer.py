"""
Layout engine and PDF renderer.
Components are placed on a grid; connections are drawn as orthogonal lines.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm

from .circuit import Circuit, Component
from . import symbols as sym

# Grid spacing (points)
GRID_X = 160
GRID_Y = 140
MARGIN_X = 100
MARGIN_Y = 120

# Title block height
TB_HEIGHT = 60 * mm  # 60 mm — not used for layout, kept for reference

PAGE_W, PAGE_H = landscape(A3)

SYMBOL_DRAW = {
    "cylinder_da":       sym.draw_cylinder_da,
    "cylinder_sa":       sym.draw_cylinder_sa,
    "valve_52":          lambda c, cx, cy: sym.draw_valve_52(c, cx, cy),
    "valve_32":          lambda c, cx, cy: sym.draw_valve_32(c, cx, cy),
    "flow_control":      sym.draw_flow_control,
    "check_valve":       sym.draw_check_valve,
    "pressure_regulator": sym.draw_pressure_regulator,
    "gauge":             sym.draw_gauge,
    "supply":            sym.draw_supply,
    "exhaust":           sym.draw_exhaust,
}


def _component_centre(comp: Component) -> tuple[float, float]:
    col, row = comp.position
    cx = MARGIN_X + col * GRID_X
    cy = PAGE_H - MARGIN_Y - row * GRID_Y
    return cx, cy


def _draw_title_block(c: canvas.Canvas, circuit: Circuit) -> None:
    tb_x, tb_y = 10, 10
    tb_w, tb_h = PAGE_W - 20, 45

    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.rect(tb_x, tb_y, tb_w, tb_h)

    # Dividers
    c.line(tb_x + tb_w * 0.5, tb_y, tb_x + tb_w * 0.5, tb_y + tb_h)
    c.line(tb_x + tb_w * 0.75, tb_y, tb_x + tb_w * 0.75, tb_y + tb_h)

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(tb_x + tb_w * 0.25, tb_y + 16, circuit.title)

    c.setFont("Helvetica", 9)
    c.drawString(tb_x + tb_w * 0.51, tb_y + 28, f"Drawn by: {circuit.drawn_by}")
    c.drawString(tb_x + tb_w * 0.51, tb_y + 14, f"Date: {circuit.date}")

    c.drawString(tb_x + tb_w * 0.76, tb_y + 28, "Standard: ISO 1219-1")
    c.drawString(tb_x + tb_w * 0.76, tb_y + 14, "Scale: NTS")


def _draw_connections(c: canvas.Canvas, circuit: Circuit) -> None:
    centres = {comp.tag: _component_centre(comp) for comp in circuit.components}
    c.setLineWidth(1)
    c.setStrokeColorRGB(0, 0, 0)
    for conn in circuit.connections:
        if conn.from_tag not in centres or conn.to_tag not in centres:
            continue
        x1, y1 = centres[conn.from_tag]
        x2, y2 = centres[conn.to_tag]
        # Simple orthogonal routing: horizontal then vertical
        mid_x = (x1 + x2) / 2
        c.line(x1, y1, mid_x, y1)
        c.line(mid_x, y1, mid_x, y2)
        c.line(mid_x, y2, x2, y2)


def render_pdf(circuit: Circuit, output_path: str) -> None:
    c = canvas.Canvas(output_path, pagesize=landscape(A3))
    c.setTitle(circuit.title)

    # Border
    c.setLineWidth(2)
    c.rect(5, 5, PAGE_W - 10, PAGE_H - 10)

    _draw_title_block(c, circuit)
    _draw_connections(c, circuit)

    c.setLineWidth(1.2)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    for comp in circuit.components:
        cx, cy = _component_centre(comp)
        draw_fn = SYMBOL_DRAW.get(comp.comp_type)
        if draw_fn:
            draw_fn(c, cx, cy)
        else:
            # Unknown type: draw a labelled box
            c.rect(cx - 25, cy - 20, 50, 40)
            c.setFont("Helvetica", 8)
            c.drawCentredString(cx, cy, comp.comp_type)

        sym.draw_label(c, cx, cy, comp.tag, comp.label)

    c.save()
    print(f"PDF saved: {output_path}")

"""
ISO 1219-1 pneumatic symbol drawing functions.
All symbols are drawn centred on (cx, cy) with a nominal size of `s` points.
canvas: reportlab.pdfgen.canvas.Canvas
"""

import math


def _arrow(c, x1, y1, x2, y2, size=6):
    """Draw a filled arrowhead at (x2,y2) pointing from (x1,y1)."""
    angle = math.atan2(y2 - y1, x2 - x1)
    pts = [
        (x2, y2),
        (x2 - size * math.cos(angle - 0.4), y2 - size * math.sin(angle - 0.4)),
        (x2 - size * math.cos(angle + 0.4), y2 - size * math.sin(angle + 0.4)),
    ]
    p = c.beginPath()
    p.moveTo(*pts[0])
    p.lineTo(*pts[1])
    p.lineTo(*pts[2])
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def draw_supply(c, cx, cy, s=30):
    """Compressed air supply (filled triangle pointing up)."""
    h = s * 0.9
    pts = [(cx, cy + h / 2), (cx - s / 2, cy - h / 2), (cx + s / 2, cy - h / 2)]
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    c.drawPath(p, fill=1, stroke=1)


def draw_exhaust(c, cx, cy, s=30):
    """Exhaust to atmosphere (open triangle pointing down)."""
    h = s * 0.9
    pts = [(cx, cy - h / 2), (cx - s / 2, cy + h / 2), (cx + s / 2, cy + h / 2)]
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    c.drawPath(p, fill=0, stroke=1)


def draw_cylinder_da(c, cx, cy, s=60):
    """Double-acting cylinder (ISO 1219)."""
    w, h = s, s * 0.45
    # Body
    c.rect(cx - w / 2, cy - h / 2, w, h)
    # Piston line
    px = cx + w * 0.15
    c.line(px, cy - h / 2, px, cy + h / 2)
    # Piston rod
    c.line(px, cy, cx + w / 2 + s * 0.35, cy)
    # End cap (left closed)
    c.line(cx - w / 2, cy - h / 2, cx - w / 2, cy + h / 2)
    # Port markers
    c.circle(cx - w / 2 + 4, cy, 2, fill=1)
    c.circle(px - 4, cy, 2, fill=1)


def draw_cylinder_sa(c, cx, cy, s=60):
    """Single-acting cylinder with spring return."""
    w, h = s, s * 0.45
    c.rect(cx - w / 2, cy - h / 2, w, h)
    # Piston
    px = cx + w * 0.1
    c.line(px, cy - h / 2, px, cy + h / 2)
    # Piston rod
    c.line(px, cy, cx + w / 2 + s * 0.35, cy)
    # Spring inside (zigzag)
    segs = 6
    seg_w = (px - (cx - w / 2 + 4)) / segs
    spring_y = cy
    spring_amp = h * 0.2
    sx = cx - w / 2 + 4
    p = c.beginPath()
    p.moveTo(sx, spring_y)
    for i in range(segs):
        mid_x = sx + seg_w * (i + 0.5)
        end_x = sx + seg_w * (i + 1)
        p.lineTo(mid_x, spring_y + (spring_amp if i % 2 == 0 else -spring_amp))
        p.lineTo(end_x, spring_y)
    c.drawPath(p, fill=0, stroke=1)


def _valve_box(c, cx, cy, s, positions, arrows, label_rows=None):
    """
    Draw a directional control valve.
    positions: number of switching positions (boxes)
    arrows: list of lists of arrow specs per position box
            each spec: ('line'|'arrow', x1,y1,x2,y2) in unit coords (0..1 relative to box)
    """
    box_w = s
    box_h = s * 0.85
    total_w = box_w * positions
    left = cx - total_w / 2

    for i in range(positions):
        bx = left + i * box_w
        c.rect(bx, cy - box_h / 2, box_w, box_h)
        if label_rows and i < len(label_rows):
            c.setFont("Helvetica", 7)
            c.drawCentredString(bx + box_w / 2, cy - box_h / 2 - 9, label_rows[i])

    return left, box_w, box_h


def draw_valve_52(c, cx, cy, s=55, actuator="solenoid", spring_return=True):
    """5/2 directional control valve."""
    left, bw, bh = _valve_box(c, cx, cy, s, 2, [])

    # Position 0 (left/active): 5→2 and 4→3 (A,B ports)
    bx0 = left
    # A port: bottom left → top; B port: crosses
    _draw_52_pos0(c, bx0, cy, bw, bh)
    # Position 1 (right/rest)
    bx1 = left + bw
    _draw_52_pos1(c, bx1, cy, bw, bh)

    _draw_valve_ports_52(c, cx, cy, bw, bh, left)
    _draw_actuators(c, cx, cy, s, bw, bh, left, 2, actuator, spring_return)


def _draw_52_pos0(c, bx, cy, bw, bh):
    m = 8
    # Arrow from bottom-left to top-centre (supply → A)
    c.line(bx + m, cy - bh / 2 + m, bx + m, cy + bh / 2 - m)
    _arrow(c, bx + m, cy - bh / 2 + m, bx + m, cy + bh / 2 - m, 5)
    # Arrow from top-right to bottom-right exhaust
    c.line(bx + bw - m, cy + bh / 2 - m, bx + bw - m, cy - bh / 2 + m)
    _arrow(c, bx + bw - m, cy + bh / 2 - m, bx + bw - m, cy - bh / 2 + m, 5)
    # Cross line
    c.line(bx + m, cy, bx + bw - m, cy)


def _draw_52_pos1(c, bx, cy, bw, bh):
    m = 8
    c.line(bx + m, cy + bh / 2 - m, bx + m, cy - bh / 2 + m)
    _arrow(c, bx + m, cy + bh / 2 - m, bx + m, cy - bh / 2 + m, 5)
    c.line(bx + bw - m, cy - bh / 2 + m, bx + bw - m, cy + bh / 2 - m)
    _arrow(c, bx + bw - m, cy - bh / 2 + m, bx + bw - m, cy + bh / 2 - m, 5)
    c.line(bx + m, cy, bx + bw - m, cy)


def _draw_valve_ports_52(c, cx, cy, bw, bh, left):
    """Draw port labels below a 5/2 valve."""
    c.setFont("Helvetica", 7)
    half = bw
    # Port 1 (supply) — centre bottom of left box
    c.line(left + bw * 0.5, cy - bh / 2, left + bw * 0.5, cy - bh / 2 - 12)
    c.drawCentredString(left + bw * 0.5, cy - bh / 2 - 20, "1(P)")
    # Port 2 (A) — top of left box
    c.line(left + bw * 0.25, cy + bh / 2, left + bw * 0.25, cy + bh / 2 + 12)
    c.drawCentredString(left + bw * 0.25, cy + bh / 2 + 14, "2(A)")
    # Port 4 (B) — top of right box
    c.line(left + bw * 1.75, cy + bh / 2, left + bw * 1.75, cy + bh / 2 + 12)
    c.drawCentredString(left + bw * 1.75, cy + bh / 2 + 14, "4(B)")
    # Port 3 (exhaust A) — bottom right of left box
    c.line(left + bw * 0.75, cy - bh / 2, left + bw * 0.75, cy - bh / 2 - 12)
    c.drawCentredString(left + bw * 0.75, cy - bh / 2 - 20, "3(EA)")
    # Port 5 (exhaust B) — bottom of right box
    c.line(left + bw * 1.5, cy - bh / 2, left + bw * 1.5, cy - bh / 2 - 12)
    c.drawCentredString(left + bw * 1.5, cy - bh / 2 - 20, "5(EB)")


def draw_valve_32(c, cx, cy, s=55, actuator="solenoid", spring_return=True):
    """3/2 normally-closed directional control valve."""
    left, bw, bh = _valve_box(c, cx, cy, s, 2, [])
    m = 8
    # NC position (right box, rest): blocked on port 2, exhaust on 1
    bx1 = left + bw
    p = c.beginPath()
    p.moveTo(bx1 + m, cy - bh / 2 + m)
    p.lineTo(bx1 + m, cy + bh / 2 - m)
    c.drawPath(p, fill=0, stroke=1)
    # block symbol — two horizontal bars
    c.line(bx1 + m, cy + bh / 2 - m, bx1 + bw - m, cy + bh / 2 - m)
    c.line(bx1 + m, cy - bh / 2 + m, bx1 + bw - m, cy - bh / 2 + m)

    # Active position (left box): supply → work port
    bx0 = left
    c.line(bx0 + bw / 2, cy - bh / 2 + m, bx0 + bw / 2, cy + bh / 2 - m)
    _arrow(c, bx0 + bw / 2, cy - bh / 2 + m, bx0 + bw / 2, cy + bh / 2 - m, 5)

    # Ports
    c.setFont("Helvetica", 7)
    c.line(left + bw * 0.5, cy + bh / 2, left + bw * 0.5, cy + bh / 2 + 12)
    c.drawCentredString(left + bw * 0.5, cy + bh / 2 + 14, "2(A)")
    c.line(left + bw * 0.25, cy - bh / 2, left + bw * 0.25, cy - bh / 2 - 12)
    c.drawCentredString(left + bw * 0.25, cy - bh / 2 - 20, "1(P)")
    c.line(left + bw * 0.75, cy - bh / 2, left + bw * 0.75, cy - bh / 2 - 12)
    c.drawCentredString(left + bw * 0.75, cy - bh / 2 - 20, "3(R)")

    _draw_actuators(c, cx, cy, s, bw, bh, left, 2, actuator, spring_return)


def _draw_actuators(c, cx, cy, s, bw, bh, left, positions, actuator, spring_return):
    total_w = bw * positions
    right = left + total_w

    # Actuator on left side
    if actuator == "solenoid":
        _draw_solenoid(c, left - 4, cy, bh, side="left")
    elif actuator == "manual":
        _draw_manual(c, left - 4, cy, bh, side="left")
    elif actuator == "pilot":
        _draw_pilot(c, left - 4, cy, bh, side="left")
    else:  # spring default on left
        _draw_spring(c, left - 4, cy, bh, side="left")

    # Spring return on right side
    if spring_return:
        _draw_spring(c, right + 4, cy, bh, side="right")


def _draw_solenoid(c, x, cy, bh, side="left"):
    w = 18
    if side == "left":
        c.rect(x - w, cy - bh / 2, w, bh)
        # diagonal lines indicating solenoid
        c.line(x - w + 3, cy - bh / 2 + 3, x - 3, cy + bh / 2 - 3)
        c.line(x - w + 3, cy + bh / 2 - 3, x - 3, cy - bh / 2 + 3)
    else:
        c.rect(x, cy - bh / 2, w, bh)
        c.line(x + 3, cy - bh / 2 + 3, x + w - 3, cy + bh / 2 - 3)
        c.line(x + 3, cy + bh / 2 - 3, x + w - 3, cy - bh / 2 + 3)


def _draw_spring(c, x, cy, bh, side="right"):
    segs = 5
    seg_h = bh / segs
    amp = 5
    if side == "right":
        p = c.beginPath()
        p.moveTo(x, cy - bh / 2)
        for i in range(segs):
            mid_y = cy - bh / 2 + seg_h * (i + 0.5)
            end_y = cy - bh / 2 + seg_h * (i + 1)
            p.lineTo(x + (amp if i % 2 == 0 else -amp), mid_y)
            p.lineTo(x, end_y)
        c.drawPath(p, fill=0, stroke=1)
    else:
        p = c.beginPath()
        p.moveTo(x, cy - bh / 2)
        for i in range(segs):
            mid_y = cy - bh / 2 + seg_h * (i + 0.5)
            end_y = cy - bh / 2 + seg_h * (i + 1)
            p.lineTo(x - (amp if i % 2 == 0 else -amp), mid_y)
            p.lineTo(x, end_y)
        c.drawPath(p, fill=0, stroke=1)


def _draw_manual(c, x, cy, bh, side="left"):
    w = 14
    if side == "left":
        # Push button symbol: line + circle
        c.line(x - w, cy, x, cy)
        c.circle(x - w - 5, cy, 5, fill=0)
    else:
        c.line(x, cy, x + w, cy)
        c.circle(x + w + 5, cy, 5, fill=0)


def _draw_pilot(c, x, cy, bh, side="left"):
    w = 14
    if side == "left":
        c.line(x - w, cy, x, cy)
        _arrow(c, x - w, cy, x, cy, 5)
    else:
        c.line(x, cy, x + w, cy)
        _arrow(c, x, cy, x + w, cy, 5)


def draw_flow_control(c, cx, cy, s=40):
    """Flow control valve with check (one-way throttle), ISO 1219."""
    r = s * 0.3
    # Circle body
    c.circle(cx, cy, r, fill=0)
    # Arrow through circle (flow direction)
    c.line(cx - r, cy, cx + r, cy)
    _arrow(c, cx - r, cy, cx + r, cy, 5)
    # Throttle diagonal line
    c.line(cx - r * 0.6, cy + r * 0.6, cx + r * 0.6, cy - r * 0.6)
    # Port stubs
    c.line(cx - r - 12, cy, cx - r, cy)
    c.line(cx + r, cy, cx + r + 12, cy)


def draw_check_valve(c, cx, cy, s=40):
    """Check valve (non-return), ISO 1219."""
    r = s * 0.25
    # Circle
    c.circle(cx, cy, r, fill=0)
    # Filled triangle pointing right (flow direction)
    pts = [(cx + r * 0.5, cy), (cx - r * 0.4, cy + r * 0.55), (cx - r * 0.4, cy - r * 0.55)]
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    # Seat line
    c.line(cx + r * 0.5, cy - r * 0.6, cx + r * 0.5, cy + r * 0.6)
    c.line(cx - r - 12, cy, cx - r, cy)
    c.line(cx + r, cy, cx + r + 12, cy)


def draw_pressure_regulator(c, cx, cy, s=50):
    """Pressure regulator (adjustable), ISO 1219."""
    r = s * 0.35
    c.circle(cx, cy, r, fill=0)
    # Arrow through (flow direction)
    c.line(cx - r, cy, cx + r, cy)
    _arrow(c, cx - r, cy, cx + r, cy, 5)
    # Adjustment arrow (diagonal with arrowhead)
    c.line(cx - r * 0.5, cy + r * 0.5, cx + r * 0.5, cy - r * 0.5)
    _arrow(c, cx - r * 0.5, cy + r * 0.5, cx + r * 0.5, cy - r * 0.5, 5)
    # Port stubs
    c.line(cx - r - 12, cy, cx - r, cy)
    c.line(cx + r, cy, cx + r + 12, cy)
    # Spring line above (indicates spring-loaded)
    segs = 4
    sw = r * 0.6
    seg_w = sw / segs
    sy = cy + r + 6
    p = c.beginPath()
    p.moveTo(cx - sw / 2, sy)
    for i in range(segs):
        mid_x = cx - sw / 2 + seg_w * (i + 0.5)
        end_x = cx - sw / 2 + seg_w * (i + 1)
        amp = 4
        p.lineTo(mid_x, sy + (amp if i % 2 == 0 else -amp))
        p.lineTo(end_x, sy)
    c.drawPath(p, fill=0, stroke=1)


def draw_gauge(c, cx, cy, s=30):
    """Pressure gauge, ISO 1219."""
    r = s * 0.4
    c.circle(cx, cy, r, fill=0)
    # Needle
    c.line(cx, cy, cx + r * 0.6, cy + r * 0.6)
    # Port stub below
    c.line(cx, cy - r, cx, cy - r - 12)


def draw_label(c, cx, cy, tag, description, offset_y=-45, font_size=8):
    """Draw tag and description below a component."""
    c.setFont("Helvetica-Bold", font_size)
    c.drawCentredString(cx, cy + offset_y, tag)
    c.setFont("Helvetica", font_size - 1)
    c.drawCentredString(cx, cy + offset_y - 10, description)

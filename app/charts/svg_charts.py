"""Pure-Python SVG chart generator for financial breakdowns and loan amortization."""
import math
from decimal import Decimal
from typing import List, Dict, Any

CHART_PALETTE = [
    "#10b981",  # Emerald / Take-home net
    "#6366f1",  # Indigo / Municipal tax
    "#f59e0b",  # Amber / State tax
    "#06b6d4",  # Cyan / Pension (TyEL)
    "#ec4899",  # Pink / Unemployment
    "#8b5cf6",  # Purple / Health
    "#f43f5e",  # Rose / Church tax
    "#64748b",  # Slate
]

def render_breakdown_donut(
    slices: List[Dict[str, Any]],
    center_label: str = "Net Pay",
    center_sublabel: str = "€2,850/mo",
    size: int = 340,
) -> str:
    """
    Renders an SVG donut chart.
    slices: list of dicts with 'name', 'value' (number or Decimal), and optional 'color'.
    """
    total = sum(float(s["value"]) for s in slices if float(s["value"]) > 0)
    if total <= 0:
        return f"""
        <svg viewBox="0 0 {size} {size}" width="100%" height="{size}" class="finance-donut-chart">
            <circle cx="{size/2}" cy="{size/2}" r="110" fill="none" stroke="currentColor" stroke-width="32" opacity="0.1" />
            <text x="{size/2}" y="{size/2}" text-anchor="middle" dominant-baseline="middle" fill="currentColor" font-size="14">No data</text>
        </svg>
        """

    cx = size / 2
    cy = size / 2
    radius = 110
    inner_radius = 72
    stroke_width = radius - inner_radius
    circumference = 2 * math.pi * ((radius + inner_radius) / 2)

    svg_parts = [
        f'<svg viewBox="0 0 {size} {size}" width="100%" height="{size}" class="finance-donut-chart" role="img" aria-label="Financial distribution chart">',
        '<defs>',
        '  <filter id="donut-shadow" x="-10%" y="-10%" width="120%" height="120%">',
        '    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.15" />',
        '  </filter>',
        '</defs>',
        f'<g transform="rotate(-90 {cx} {cy})" filter="url(#donut-shadow)">',
    ]

    current_angle = 0.0
    for idx, s in enumerate(slices):
        val = float(s["value"])
        if val <= 0:
            continue
        color = s.get("color") or CHART_PALETTE[idx % len(CHART_PALETTE)]
        fraction = val / total
        slice_angle = fraction * 360.0

        # Calculate arc coordinates
        start_rad = math.radians(current_angle)
        end_rad = math.radians(current_angle + slice_angle)

        x1_outer = cx + radius * math.cos(start_rad)
        y1_outer = cy + radius * math.sin(start_rad)
        x2_outer = cx + radius * math.cos(end_rad)
        y2_outer = cy + radius * math.sin(end_rad)

        x1_inner = cx + inner_radius * math.cos(end_rad)
        y1_inner = cy + inner_radius * math.sin(end_rad)
        x2_inner = cx + inner_radius * math.cos(start_rad)
        y2_inner = cy + inner_radius * math.sin(start_rad)

        large_arc = 1 if slice_angle > 180 else 0

        path_d = (
            f"M {x1_outer:.2f} {y1_outer:.2f} "
            f"A {radius} {radius} 0 {large_arc} 1 {x2_outer:.2f} {y2_outer:.2f} "
            f"L {x1_inner:.2f} {y1_inner:.2f} "
            f"A {inner_radius} {inner_radius} 0 {large_arc} 0 {x2_inner:.2f} {y2_inner:.2f} Z"
        )

        svg_parts.append(
            f'<path d="{path_d}" fill="{color}" stroke="var(--bg-card, #ffffff)" stroke-width="2" class="donut-segment">'
            f'<title>{s["name"]}: {val:,.2f} ({fraction*100:.1f}%)</title>'
            f'</path>'
        )
        current_angle += slice_angle

    svg_parts.append('</g>')

    # Center Text
    svg_parts.append(f'<g class="donut-center" text-anchor="middle">')
    svg_parts.append(
        f'<text x="{cx}" y="{cy - 8}" class="donut-sublabel" font-size="12" fill="var(--text-muted, #64748b)" font-weight="600">{center_label.upper()}</text>'
    )
    svg_parts.append(
        f'<text x="{cx}" y="{cy + 18}" class="donut-mainlabel" font-size="20" fill="var(--text-primary, #0f172a)" font-weight="800">{center_sublabel}</text>'
    )
    svg_parts.append('</g>')
    svg_parts.append('</svg>')

    return "\n".join(svg_parts)

def render_amortization_chart(
    schedule: List[Dict[str, Any]],
    currency_symbol: str = "€",
    width: int = 560,
    height: int = 240,
) -> str:
    """
    Renders an SVG amortization curve showing balance reduction and cumulative interest.
    schedule is a sampled list of points with keys: 'year', 'balance', 'total_interest'.
    """
    if not schedule:
        return f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}"><text x="{width/2}" y="{height/2}" text-anchor="middle">No schedule</text></svg>'

    padding_x = 55
    padding_y = 35
    plot_w = width - (padding_x * 2)
    plot_h = height - (padding_y * 2)

    max_val = max(
        max(float(pt.get("balance", 0)) for pt in schedule),
        max(float(pt.get("total_interest", 0)) for pt in schedule),
        1.0,
    )
    num_pts = len(schedule)

    def get_x(i: int) -> float:
        if num_pts <= 1:
            return padding_x + plot_w / 2
        return padding_x + (i / (num_pts - 1)) * plot_w

    def get_y(val: float) -> float:
        return (padding_y + plot_h) - (val / max_val) * plot_h

    # Balance curve
    balance_pts = [f"{get_x(i):.1f},{get_y(float(pt['balance'])):.1f}" for i, pt in enumerate(schedule)]
    balance_polyline = " ".join(balance_pts)

    # Balance Area
    first_x = get_x(0)
    last_x = get_x(num_pts - 1)
    bottom_y = padding_y + plot_h
    balance_area_d = f"M {first_x:.1f},{bottom_y:.1f} L {balance_polyline} L {last_x:.1f},{bottom_y:.1f} Z"

    # Interest curve
    interest_pts = [f"{get_x(i):.1f},{get_y(float(pt.get('total_interest', 0))):.1f}" for i, pt in enumerate(schedule)]
    interest_polyline = " ".join(interest_pts)

    svg = f"""
    <svg viewBox="0 0 {width} {height}" width="100%" height="{height}" class="amortization-chart" role="img" aria-label="Amortization schedule graph">
        <defs>
            <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#10b981" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="#10b981" stop-opacity="0.0"/>
            </linearGradient>
            <linearGradient id="interestGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.0"/>
            </linearGradient>
        </defs>

        <!-- Grid Lines -->
        <line x1="{padding_x}" y1="{bottom_y}" x2="{width - padding_x}" y2="{bottom_y}" stroke="currentColor" opacity="0.15" stroke-width="1"/>
        <line x1="{padding_x}" y1="{padding_y + plot_h/2}" x2="{width - padding_x}" y2="{padding_y + plot_h/2}" stroke="currentColor" opacity="0.08" stroke-dasharray="4,4"/>
        <line x1="{padding_x}" y1="{padding_y}" x2="{width - padding_x}" y2="{padding_y}" stroke="currentColor" opacity="0.08" stroke-dasharray="4,4"/>

        <!-- Y Axis Labels -->
        <text x="{padding_x - 8}" y="{bottom_y}" text-anchor="end" font-size="10" fill="var(--text-muted, #64748b)">0</text>
        <text x="{padding_x - 8}" y="{padding_y + plot_h/2 + 3}" text-anchor="end" font-size="10" fill="var(--text-muted, #64748b)">{currency_symbol}{max_val/2:,.0f}</text>
        <text x="{padding_x - 8}" y="{padding_y + 4}" text-anchor="end" font-size="10" fill="var(--text-muted, #64748b)">{currency_symbol}{max_val:,.0f}</text>

        <!-- Shaded Area -->
        <path d="{balance_area_d}" fill="url(#balanceGrad)"/>

        <!-- Line Curves -->
        <polyline points="{balance_polyline}" fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>
        <polyline points="{interest_polyline}" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="4,4" stroke-linecap="round"/>

        <!-- Key X Axis Year Labels -->
        <text x="{first_x}" y="{bottom_y + 18}" text-anchor="middle" font-size="11" fill="var(--text-muted, #64748b)">Yr 0</text>
        <text x="{(first_x + last_x)/2}" y="{bottom_y + 18}" text-anchor="middle" font-size="11" fill="var(--text-muted, #64748b)">Yr {len(schedule)//2}</text>
        <text x="{last_x}" y="{bottom_y + 18}" text-anchor="middle" font-size="11" fill="var(--text-muted, #64748b)">Yr {len(schedule)}</text>
    </svg>
    """
    return svg

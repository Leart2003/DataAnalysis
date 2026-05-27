from __future__ import annotations

from math import cos, pi, sin
from pathlib import Path
from xml.sax.saxutils import escape


class SVGChartBuilder:
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_bar_chart(self, title: str, data: list[tuple[str, int]], filename: str) -> Path:
        width = 1000
        height = 600
        margin_left = 90
        margin_bottom = 120
        margin_top = 80
        chart_width = width - margin_left - 60
        chart_height = height - margin_top - margin_bottom
        max_value = max((value for _, value in data), default=1)
        bar_width = chart_width / max(len(data), 1)

        bars: list[str] = []
        labels: list[str] = []
        for index, (label, value) in enumerate(data):
            scaled_height = 0 if max_value == 0 else (value / max_value) * chart_height
            x = margin_left + index * bar_width + 8
            y = margin_top + chart_height - scaled_height
            bars.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width - 16:.2f}" '
                f'height="{scaled_height:.2f}" fill="#2f855a" rx="6" />'
            )
            labels.append(
                f'<text x="{x + (bar_width - 16) / 2:.2f}" y="{height - 55}" '
                f'text-anchor="end" transform="rotate(-35 {x + (bar_width - 16) / 2:.2f},{height - 55})" '
                f'font-size="13">{escape(label)}</text>'
            )
            labels.append(
                f'<text x="{x + (bar_width - 16) / 2:.2f}" y="{y - 8:.2f}" '
                f'text-anchor="middle" font-size="12">{value}</text>'
            )

        svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="#f7fafc"/>
  <text x="{width / 2}" y="40" text-anchor="middle" font-size="28" font-weight="bold">{escape(title)}</text>
  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="#2d3748" stroke-width="2"/>
  <line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{margin_left + chart_width}" y2="{margin_top + chart_height}" stroke="#2d3748" stroke-width="2"/>
  {''.join(bars)}
  {''.join(labels)}
</svg>
""".strip()
        return self._write_svg(filename, svg)

    def build_pie_chart(self, title: str, data: list[tuple[str, int]], filename: str) -> Path:
        width = 900
        height = 600
        center_x = 280
        center_y = 320
        radius = 180
        total = sum(value for _, value in data) or 1
        colors = ["#2b6cb0", "#dd6b20", "#38a169", "#805ad5", "#d53f8c", "#319795", "#718096"]

        current_angle = -pi / 2
        slices: list[str] = []
        legends: list[str] = []
        for index, (label, value) in enumerate(data):
            angle = (value / total) * 2 * pi
            x1 = center_x + radius * cos(current_angle)
            y1 = center_y + radius * sin(current_angle)
            x2 = center_x + radius * cos(current_angle + angle)
            y2 = center_y + radius * sin(current_angle + angle)
            large_arc = 1 if angle > pi else 0
            color = colors[index % len(colors)]
            path = (
                f"M {center_x} {center_y} "
                f"L {x1:.2f} {y1:.2f} "
                f"A {radius} {radius} 0 {large_arc} 1 {x2:.2f} {y2:.2f} Z"
            )
            slices.append(f'<path d="{path}" fill="{color}" stroke="#ffffff" stroke-width="2"/>')
            legends.append(
                f'<rect x="560" y="{120 + index * 34}" width="18" height="18" fill="{color}"/>'
                f'<text x="588" y="{134 + index * 34}" font-size="15">{escape(label)} ({value})</text>'
            )
            current_angle += angle

        svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="#fffaf0"/>
  <text x="{width / 2}" y="50" text-anchor="middle" font-size="28" font-weight="bold">{escape(title)}</text>
  {''.join(slices)}
  {''.join(legends)}
</svg>
""".strip()
        return self._write_svg(filename, svg)

    def build_line_chart(self, title: str, data: list[tuple[str, int]], filename: str) -> Path:
        width = 1000
        height = 600
        margin_left = 100
        margin_bottom = 100
        margin_top = 70
        chart_width = width - margin_left - 60
        chart_height = height - margin_top - margin_bottom
        max_value = max((value for _, value in data), default=1)
        step_x = chart_width / max(len(data) - 1, 1)

        points: list[str] = []
        labels: list[str] = []
        circles: list[str] = []
        for index, (label, value) in enumerate(data):
            x = margin_left + index * step_x
            y = margin_top + chart_height - ((value / max_value) * chart_height if max_value else 0)
            points.append(f"{x:.2f},{y:.2f}")
            circles.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="#c53030"/>')
            labels.append(
                f'<text x="{x:.2f}" y="{height - 40}" text-anchor="middle" font-size="13">{escape(label)}</text>'
                f'<text x="{x:.2f}" y="{y - 10:.2f}" text-anchor="middle" font-size="12">{value}</text>'
            )

        svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="#f0fff4"/>
  <text x="{width / 2}" y="40" text-anchor="middle" font-size="28" font-weight="bold">{escape(title)}</text>
  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="#2d3748" stroke-width="2"/>
  <line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{margin_left + chart_width}" y2="{margin_top + chart_height}" stroke="#2d3748" stroke-width="2"/>
  <polyline fill="none" stroke="#c53030" stroke-width="4" points="{' '.join(points)}"/>
  {''.join(circles)}
  {''.join(labels)}
</svg>
""".strip()
        return self._write_svg(filename, svg)

    def build_dashboard(self, chart_paths: list[Path], filename: str = "dashboard.html") -> Path:
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Cybersecurity Analysis Dashboard</title>
  <style>
    body {{
      margin: 0;
      font-family: Georgia, serif;
      background: linear-gradient(135deg, #edf2f7, #fffaf0);
      color: #1a202c;
    }}
    header {{
      padding: 32px 24px 16px;
      text-align: center;
    }}
    main {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
      padding: 24px;
    }}
    .card {{
      background: rgba(255, 255, 255, 0.86);
      border-radius: 18px;
      padding: 12px;
      box-shadow: 0 14px 32px rgba(26, 32, 44, 0.12);
    }}
    img {{
      width: 100%;
      display: block;
      border-radius: 12px;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Cybersecurity Attacks Analysis</h1>
    <p>Grafiket e gjeneruara nga projekti i analizes se te dhenave.</p>
  </header>
  <main>
    {''.join(f'<section class="card"><img src="{path.name}" alt="{path.stem}"></section>' for path in chart_paths)}
  </main>
</body>
</html>
""".strip()
        output_path = self.output_dir / filename
        output_path.write_text(html, encoding="utf-8")
        return output_path

    def _write_svg(self, filename: str, svg_content: str) -> Path:
        output_path = self.output_dir / filename
        output_path.write_text(svg_content, encoding="utf-8")
        return output_path


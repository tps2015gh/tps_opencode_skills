#!/usr/bin/env python3
"""HTML Report - Create A4 portrait HTML reports with positioned text and graphs"""

import os
import sys
import json
import time
import webbrowser


def create_svg_bar_graph(data, x='20mm', y='20mm', width='160mm', height='80mm', title='', colors=None):
    """Create SVG bar graph from data dict {label: value}"""
    if colors is None:
        colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948', '#b07aa1', '#ff9da7', '#9c755f', '#bab0ac']
    
    items = list(data.items())
    n = len(items)
    if n == 0:
        return ''
    
    max_val = max(v for _, v in items)
    if max_val == 0:
        max_val = 1
    
    # Parse width/height to pixels (approximate)
    w_px = int(float(width.replace('mm', '')) * 3.78)
    h_px = int(float(height.replace('mm', '')) * 3.78)
    
    bar_w = max(20, (w_px - 60) // n - 5)
    chart_h = h_px - 50
    chart_w = n * (bar_w + 5) + 40
    
    bars = ''
    labels = ''
    for i, (label, val) in enumerate(items):
        bar_h = int((val / max_val) * (chart_h - 30))
        bx = 30 + i * (bar_w + 5)
        by = chart_h - bar_h - 20
        color = colors[i % len(colors)]
        bars += f'<rect x="{bx}" y="{by}" width="{bar_w}" height="{bar_h}" fill="{color}" rx="2"/>'
        bars += f'<text x="{bx + bar_w//2}" y="{by - 3}" text-anchor="middle" font-size="9" fill="#333">{val}</text>'
        # Label
        lbl = label[:8] if len(label) > 8 else label
        labels += f'<text x="{bx + bar_w//2}" y="{chart_h - 5}" text-anchor="middle" font-size="8" fill="#666">{lbl}</text>'
    
    title_svg = f'<text x="{w_px//2}" y="14" text-anchor="middle" font-size="11" font-weight="bold" fill="#333">{title}</text>' if title else ''
    
    svg = f'''<svg style="position:absolute;left:{x};top:{y}" width="{w_px}" height="{h_px}" xmlns="http://www.w3.org/2000/svg">
    {title_svg}
    {bars}
    {labels}
    <line x1="28" y1="{chart_h - 20}" x2="{chart_w}" y2="{chart_h - 20}" stroke="#ccc" stroke-width="1"/>
    </svg>'''
    return svg


def create_svg_line_graph(data, x='20mm', y='20mm', width='160mm', height='80mm', title='', color='#4e79a7'):
    """Create SVG line graph from data dict {label: value}"""
    items = list(data.items())
    n = len(items)
    if n == 0:
        return ''
    
    max_val = max(v for _, v in items)
    min_val = min(v for _, v in items)
    if max_val == min_val:
        max_val = min_val + 1
    
    w_px = int(float(width.replace('mm', '')) * 3.78)
    h_px = int(float(height.replace('mm', '')) * 3.78)
    
    chart_h = h_px - 50
    chart_w = w_px - 60
    
    points = []
    dots = ''
    labels = ''
    for i, (label, val) in enumerate(items):
        px = 40 + i * (chart_w / max(1, n - 1))
        py = chart_h - int(((val - min_val) / (max_val - min_val)) * (chart_h - 30)) - 20
        points.append(f'{px},{py}')
        dots += f'<circle cx="{px}" cy="{py}" r="4" fill="{color}"/>'
        dots += f'<text x="{px}" y="{py - 8}" text-anchor="middle" font-size="8" fill="#333">{val}</text>'
        lbl = label[:6] if len(label) > 6 else label
        labels += f'<text x="{px}" y="{chart_h - 5}" text-anchor="middle" font-size="7" fill="#666">{lbl}</text>'
    
    polyline = f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>'
    title_svg = f'<text x="{w_px//2}" y="14" text-anchor="middle" font-size="11" font-weight="bold" fill="#333">{title}</text>' if title else ''
    
    svg = f'''<svg style="position:absolute;left:{x};top:{y}" width="{w_px}" height="{h_px}" xmlns="http://www.w3.org/2000/svg">
    {title_svg}
    <line x1="38" y1="{chart_h - 20}" x2="{w_px - 20}" y2="{chart_h - 20}" stroke="#ccc" stroke-width="1"/>
    <line x1="38" y1="20" x2="38" y2="{chart_h - 20}" stroke="#ccc" stroke-width="1"/>
    {polyline}
    {dots}
    {labels}
    </svg>'''
    return svg


def create_page(page, page_num, total_pages, font, font_size, border):
    """Create HTML for a single page"""
    # Handle both dict (with 'items' key) and list formats
    if isinstance(page, dict):
        items = page.get('items', [])
    else:
        items = page
    
    items_html = ''
    for item in items:
        if item.get('type') == 'bar_graph':
            colors = item.get('colors', None)
            items_html += create_svg_bar_graph(
                data=item.get('data', {}),
                x=item.get('x', '20mm'),
                y=item.get('y', '20mm'),
                width=item.get('width', '160mm'),
                height=item.get('height', '80mm'),
                title=item.get('title', ''),
                colors=colors
            ) + '\n'
        elif item.get('type') == 'line_graph':
            items_html += create_svg_line_graph(
                data=item.get('data', {}),
                x=item.get('x', '20mm'),
                y=item.get('y', '20mm'),
                width=item.get('width', '160mm'),
                height=item.get('height', '80mm'),
                title=item.get('title', ''),
                color=item.get('color', '#4e79a7')
            ) + '\n'
        else:
            text = item.get('text', '')
            x = item.get('x', '20mm')
            y = item.get('y', '20mm')
            fs = item.get('font_size', font_size)
            f = item.get('font', font)
            color = item.get('color', '#000000')
            bold = 'font-weight:bold;' if item.get('bold') else ''
            italic = 'font-style:italic;' if item.get('italic') else ''
            align = f'text-align:{item.get("align", "left")};' if item.get('align') else ''
            w = f'width:{item.get("w")};' if item.get('w') else ''
            items_html += f'<div style="position:absolute;left:{x};top:{y};font-family:{f};font-size:{fs};color:{color};{bold}{italic}{align}{w}">{text}</div>\n'
    
    # Page number
    items_html += f'<div style="position:absolute;left:95mm;top:290mm;font-family:{font};font-size:9px;color:#999;">หน้า {page_num}/{total_pages}</div>\n'
    
    # Border
    border_style = ''
    if border:
        bw = border.get('width', '2px')
        bc = border.get('color', '#000000')
        bs = border.get('style', 'solid')
        br = border.get('radius', '0')
        bp = border.get('padding', '10mm')
        border_style = f'border:{bw} {bs} {bc};border-radius:{br};padding:{bp};box-sizing:border-box;'
    
    return f'''<div class="page" style="{border_style}">
{items_html}
</div>'''


def create_report(config, output_file=None):
    """Create multi-page report from config"""
    # Default output folder
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)
    
    if output_file is None:
        output_file = os.path.join(reports_dir, f'report_{time.strftime("%Y%m%d_%H%M%S")}.html')
    elif not os.path.isabs(output_file):
        output_file = os.path.join(reports_dir, output_file)
    
    title = config.get('title', 'Report')
    font = config.get('font', 'Arial')
    font_size = config.get('font_size', '14px')
    border = config.get('border')
    pages = config.get('pages', [config.get('items', [])])
    
    total_pages = len(pages)
    pages_html = ''
    for i, page in enumerate(pages):
        pages_html += create_page(page, i + 1, total_pages, font, font_size, border) + '\n'
    
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
@page {{ size: A4 portrait; margin: 0; }}
body {{
    margin: 0;
    padding: 0;
    font-family: {font};
    font-size: {font_size};
    background: white;
}}
.page {{
    width: 210mm;
    height: 297mm;
    position: relative;
    background: white;
    page-break-after: always;
    overflow: hidden;
}}
.page:last-child {{
    page-break-after: auto;
}}
@media print {{
    body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .page {{ page-break-after: always; }}
    .page:last-child {{ page-break-after: auto; }}
}}
</style>
</head>
<body>
{pages_html}
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_file


def open_in_browser(file_path):
    abs_path = os.path.abspath(file_path)
    if sys.platform == 'win32':
        os.startfile(abs_path)
    else:
        webbrowser.open(f'file://{abs_path}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print('  python report.py create <json_file> [output.html]')
        print('  python report.py open <file.html>')
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'create':
        if len(sys.argv) < 3:
            print('Usage: python report.py create <json_file> [output.html]')
            sys.exit(1)
        json_file = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else None

        with open(json_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        result = create_report(config, output_file=output)
        print(f'Created: {result}')

    elif mode == 'open':
        if len(sys.argv) < 3:
            print('Usage: python report.py open <file.html>')
            sys.exit(1)
        open_in_browser(sys.argv[2])
        print(f'Opened: {sys.argv[2]}')

    else:
        print(f'Unknown mode: {mode}')
        print('Use "create" or "open"')

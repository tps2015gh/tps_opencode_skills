#!/usr/bin/env python3
"""Generate users entity report from MySQL"""

import sys
import io
import json
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import mysql.connector
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report import create_report

def generate_report(limit=50, output='users_report.html'):
    conn = mysql.connector.connect(host='localhost', user='root', password='', database='lands_auth2')
    cursor = conn.cursor()
    cursor.execute(f'SELECT iden, prefix_th, nameth, lnameth, nameen, lnameen, person_type_text, tel_mobile, email, pos_name, org_type, prov_name, create_dt FROM users_entity ORDER BY iden DESC LIMIT {limit}')
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    rows = []
    for idx, row in enumerate(data, 1):
        rows.append([str(idx)] + [str(cell) if cell is not None else '' for cell in row])

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    config = {
        "title": "Users Entity Report",
        "font": "Arial",
        "font_size": "14px",
        "orientation": "landscape",
        "border": {"width": "2px", "color": "#000000", "style": "solid", "radius": "0", "padding": "5mm"},
        "items": [
            {"text": "USERS ENTITY", "x": "10mm", "y": "8mm", "font_size": "24px", "bold": True},
            {"text": "Order by ID DESC", "x": "10mm", "y": "18mm", "color": "#888888"},
            {"text": f"Generated: {now}", "x": "200mm", "y": "8mm", "font_size": "10px", "color": "#888888"},
            {"type": "table", "x": "10mm", "y": "28mm", "width": "277mm", "header_color": "lightcyan", "border": "1px", "font_size": "10px", "rows_per_page": 19, "data": {
                "columns": ["#"] + columns,
                "rows": rows
            }}
        ]
    }

    result = create_report(config, output)
    print(f'Created: {result}')
    return result

if __name__ == '__main__':
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    output = sys.argv[2] if len(sys.argv) > 2 else 'users_report.html'
    generate_report(limit, output)

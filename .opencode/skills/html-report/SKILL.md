---
name: html-report
description: Create A4 portrait HTML reports with positioned text, custom fonts, and browser preview.
---

## HTML Report Skill

Create printable A4 portrait HTML reports with text at specific positions.

## Prerequisites

No extra dependencies - uses built-in Python modules.

## Usage

### Create report from JSON config
```bash
python .opencode/skills/html-report/report.py create config.json
```

### Open in browser
```bash
python .opencode/skills/html-report/report.py open report.html
# Or Windows:
start report.html
```

### Full workflow
```bash
# 1. Create config file
# 2. Generate report
python .opencode/skills/html-report/report.py create report.json my_report.html

# 3. Open in browser
start my_report.html

# 4. Print (Ctrl+P in browser)
```

## Config JSON Format

```json
{
  "title": "My Report",
  "font": "Arial",
  "font_size": "14px",
  "items": [
    {"text": "REPORT TITLE", "x": "20mm", "y": "20mm", "font_size": "28px", "bold": true},
    {"text": "Date: 2026-03-24", "x": "20mm", "y": "40mm", "color": "#888888"},
    {"text": "Status: OK", "x": "20mm", "y": "60mm", "color": "#00aa00"},
    {"text": "Body text goes here", "x": "20mm", "y": "80mm"},
    {"text": "Right aligned", "x": "150mm", "y": "80mm"},
    {"text": "Footer - Page 1", "x": "20mm", "y": "270mm", "font_size": "10px", "color": "#aaaaaa"}
  ]
}
```

## Item Options

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| text | Yes | - | Text content |
| x | Yes | - | Horizontal position |
| y | Yes | - | Vertical position |
| font_size | No | 14px | Font size |
| font | No | Arial | Font family |
| color | No | #000000 | Text color |
| bold | No | false | Bold text |

## Position Units

| Unit | Example | Description |
|------|---------|-------------|
| mm | 20mm | Millimeters (recommended) |
| cm | 2cm | Centimeters |
| px | 100px | Pixels |
| in | 1in | Inches |

## A4 Dimensions

- Width: 210mm
- Height: 297mm
- Safe margins: 15mm from edges

## Example: Invoice Layout

```json
{
  "title": "Invoice",
  "font": "Arial",
  "font_size": "12px",
  "items": [
    {"text": "INVOICE", "x": "20mm", "y": "20mm", "font_size": "32px", "bold": true},
    {"text": "Invoice #: 001", "x": "20mm", "y": "40mm"},
    {"text": "Date: 24/03/2026", "x": "20mm", "y": "50mm"},
    {"text": "To: Customer Name", "x": "20mm", "y": "70mm"},
    {"text": "Item 1", "x": "20mm", "y": "100mm"},
    {"text": "1,000.00", "x": "150mm", "y": "100mm"},
    {"text": "TOTAL: 1,000.00", "x": "120mm", "y": "200mm", "bold": true, "font_size": "16px"},
    {"text": "Thank you!", "x": "20mm", "y": "270mm", "color": "#888888"}
  ]
}
```

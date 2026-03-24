---
name: html-to-facebook
description: Convert HTML reports to Facebook forum posts with text and graph images.
---

## HTML to Facebook Post Skill

Convert HTML reports (from html-report skill) to Facebook-ready posts with text and graph images.

## Prerequisites

```bash
pip install pillow cairosvg
```

## Usage

### Convert HTML to Facebook post
```bash
python .opencode/skills/html-to-facebook/convert.py reports/report.html
```

### Convert with custom output folder
```bash
python .opencode/skills/html-to-facebook/convert.py reports/report.html output_folder/
```

### Convert and generate caption
```bash
python .opencode/skills/html-to-facebook/convert.py reports/report.html --caption
```

## Output

The script generates:
1. `post_text.txt` - Text content ready to copy-paste
2. `images/` - Folder with graph images (PNG)
3. `post_caption.txt` - Ready-to-use Facebook caption (if --caption flag)

## How It Works

1. Parse HTML report
2. Extract text content → format for Facebook
3. Convert SVG graphs → PNG images
4. Generate post text with image placeholders
5. Create caption with hashtags

## Example Output

```
📊 รายงาน AI Agent / Skill: ผลกระทบต่อนักพัฒนาไทย

━━━━━━━━━━━━━━━━━━━━

1️⃣ AI Agent คืออะไร?
• AI Agent คือ ระบบ AI ที่สามารถวางแผน ตัดสินใจ และทำงานได้เอง
• ต่างจาก Chatbot ธรรมดา ที่แค่ตอบคำถาม

2️⃣ Skill คืออะไร?
• Skill คือ ปลั๊กอิน/โมดูล ที่สอนให้ AI Agent ทำงานเฉพาะทางได้
• ปี 2026 มี skill มากกว่า 280,000+ ทั่วโลก

[ดูกราฟ: images/page1_graph1.png]

...
```

## Facebook Post Format

- Use emojis for visual appeal
- Short paragraphs (2-3 lines max)
- Bullet points for lists
- Image placeholders at relevant positions
- Hashtags at the end

## Files

| File | Description |
|------|-------------|
| convert.py | Main conversion script |
| SKILL.md | This file |

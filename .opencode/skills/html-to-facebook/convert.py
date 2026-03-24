#!/usr/bin/env python3
"""Convert HTML reports to Facebook forum posts with text and graph images"""

import os
import sys
import re
import json
from html.parser import HTMLParser


class HTMLReportParser(HTMLParser):
    """Parse HTML report to extract text and SVG elements"""
    
    def __init__(self):
        super().__init__()
        self.texts = []
        self.svgs = []
        self.current_svg = None
        self.in_svg = False
        self.in_style = False
        self.current_text = ""
        
    def handle_starttag(self, tag, attrs):
        if tag == 'svg':
            self.in_svg = True
            self.current_svg = {"attrs": dict(attrs), "content": ""}
            self.current_svg["content"] += f"<svg"
            for k, v in attrs:
                self.current_svg["content"] += f' {k}="{v}"'
            self.current_svg["content"] += ">"
        elif tag == 'style':
            self.in_style = True
            
    def handle_endtag(self, tag):
        if tag == 'svg' and self.in_svg:
            self.in_svg = False
            self.current_svg["content"] += "</svg>"
            self.svgs.append(self.current_svg)
            self.current_svg = None
        elif tag == 'style':
            self.in_style = False
            
    def handle_data(self, data):
        if self.in_style:
            return  # Skip CSS content
        if self.in_svg:
            self.current_svg["content"] += data
        else:
            text = data.strip()
            if text and text != " ":
                self.texts.append(text)


def extract_svg_to_files(html_content, output_dir):
    """Extract SVG graphs and save as files"""
    svg_pattern = r'<svg[^>]*>.*?</svg>'
    svgs = re.findall(svg_pattern, html_content, re.DOTALL)
    
    svg_files = []
    for i, svg in enumerate(svgs):
        filename = f"graph_{i+1}.svg"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg)
        svg_files.append(filepath)
    
    return svg_files


def svg_to_png(svg_file, png_file):
    """Convert SVG to PNG using cairosvg or fallback"""
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_file, write_to=png_file, scale=2)
        return True
    except ImportError:
        pass
    
    # Fallback: try using ImageMagick or just keep SVG
    try:
        os.system(f'convert "{svg_file}" "{png_file}"')
        return os.path.exists(png_file)
    except:
        pass
    
    return False


def format_for_facebook(texts, page_num):
    """Format text content for Facebook post"""
    formatted = []
    
    # Patterns to skip
    skip_patterns = [
        r'^@page', r'^body\s*\{', r'^\.page', r'^@media',
        r'^width:', r'^height:', r'^margin:', r'^padding:',
        r'^position:', r'^background:', r'^overflow:',
        r'^font-family:', r'^font-size:', r'^-webkit-',
        r'^print-color', r'^page-break'
    ]
    
    for text in texts:
        # Skip very short texts
        if len(text) < 3:
            continue
        if text.startswith("────"):
            continue
        if text.startswith("แหล่ง:"):
            continue
            
        # Skip CSS-like content
        if any(re.match(pattern, text) for pattern in skip_patterns):
            continue
        if text.endswith('{') or text.endswith('}'):
            continue
        if text in ['}', '{']:
            continue
            
        # Add emoji for headers
        if any(text.startswith(prefix) for prefix in ["1.", "2.", "3.", "4.", "5."]):
            num = text[0]
            emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'][int(num)-1]
            formatted.append(f"\n{emoji} {text[2:].strip()}")
        elif text.startswith("•"):
            formatted.append(f"  {text}")
        elif any(kw in text for kw in ["คือ", "เปลี่ยน", "สำคัญ", "ท้าทาย"]):
            formatted.append(f"\n📌 {text}")
        else:
            formatted.append(text)
    
    return "\n".join(formatted)


def create_facebook_post(html_file, output_dir=None, generate_caption=False):
    """Main function to convert HTML report to Facebook post"""
    
    if not os.path.exists(html_file):
        print(f"Error: File not found: {html_file}")
        return None
    
    # Set output directory
    if output_dir is None:
        base_name = os.path.splitext(os.path.basename(html_file))[0]
        output_dir = os.path.join(os.path.dirname(html_file), f"{base_name}_fb")
    
    os.makedirs(output_dir, exist_ok=True)
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Read HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', html_content)
    title = title_match.group(1) if title_match else "รายงาน"
    
    # Parse HTML
    parser = HTMLReportParser()
    parser.feed(html_content)
    
    # Extract and convert SVGs
    svg_files = extract_svg_to_files(html_content, images_dir)
    graph_images = []
    
    for i, svg_file in enumerate(svg_files):
        png_file = svg_file.replace('.svg', '.png')
        if svg_to_png(svg_file, png_file):
            graph_images.append(png_file)
            print(f"Converted: {os.path.basename(png_file)}")
        else:
            graph_images.append(svg_file)
            print(f"Saved SVG: {os.path.basename(svg_file)}")
    
    # Split texts by pages (look for page indicators)
    page_texts = []
    current_page = []
    
    for text in parser.texts:
        if "หน้า" in text and "/" in text and len(text) < 15:
            if current_page:
                page_texts.append(current_page)
                current_page = []
        else:
            current_page.append(text)
    
    if current_page:
        page_texts.append(current_page)
    
    # Generate Facebook post text
    post_lines = [f"📊 {title}\n{'━' * 30}\n"]
    
    graph_idx = 0
    for page_num, page_content in enumerate(page_texts, 1):
        post_lines.append(f"\n📄 หน้าที่ {page_num}\n{'─' * 20}")
        
        formatted = format_for_facebook(page_content, page_num)
        post_lines.append(formatted)
        
        # Add image reference
        if graph_idx < len(graph_images):
            img_name = os.path.basename(graph_images[graph_idx])
            post_lines.append(f"\n🖼️ [ดูกราฟ: images/{img_name}]")
            graph_idx += 1
    
    post_text = "\n".join(post_lines)
    
    # Save post text
    post_file = os.path.join(output_dir, "post_text.txt")
    with open(post_file, 'w', encoding='utf-8') as f:
        f.write(post_text)
    
    print(f"\nCreated: {post_file}")
    print(f"Images: {images_dir} ({len(graph_images)} files)")
    
    # Generate caption if requested
    if generate_caption:
        caption = f"""📊 {title}

สรุปข้อมูลจากรายงานฉบับเต็ม
ดูกราฟและข้อมูลในคอมเมนต์ 👇

#AI #รายงาน #ข่าวสาร #ไทย"""
        
        caption_file = os.path.join(output_dir, "post_caption.txt")
        with open(caption_file, 'w', encoding='utf-8') as f:
            f.write(caption)
        print(f"Caption: {caption_file}")
    
    # Create summary JSON
    summary = {
        "title": title,
        "source": html_file,
        "output_dir": output_dir,
        "pages": len(page_texts),
        "graphs": len(graph_images),
        "files": {
            "post_text": post_file,
            "images_dir": images_dir,
            "graph_images": [os.path.basename(g) for g in graph_images]
        }
    }
    
    summary_file = os.path.join(output_dir, "summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    return summary


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python convert.py <html_file> [output_dir] [--caption]")
        print("")
        print("Examples:")
        print("  python convert.py reports/report.html")
        print("  python convert.py reports/report.html output/ --caption")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    generate_caption = '--caption' in sys.argv
    
    result = create_facebook_post(html_file, output_dir, generate_caption)
    
    if result:
        print(f"\nDone! Files in: {result['output_dir']}")

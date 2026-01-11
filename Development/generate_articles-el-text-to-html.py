import os
import re
import unicodedata

# =========================
# CONFIG
# =========================
SITE = "https://asinoro.github.io/SparkEthos/"
IMAGE = SITE + "images/sparkethos-logo-image.png"

LANG_MAP = {
    "el": {
        "lang": "el",
        "header": "SparkEthos – Φιλοσοφία της Νοημοσύνης",
        "home": "index.html",
        "home_label": "← Επιστροφή στην Αρχική",
        "archives": "sparkethos-archives-el.html",
        "archives_label": "Αρχεία SparkEthos",
    },
    "en": {
        "lang": "en",
        "header": "SparkEthos – Philosophy of Intelligence",
        "home": "index-en.html",
        "home_label": "← Back to Home",
        "archives": "sparkethos-archives-en.html",
        "archives_label": "SparkEthos Archives",
    }
}

# =========================
# FORMATTING ENGINE
# =========================
def apply_formatting(text):
    # Μετατροπή **text** σε bold
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    return text

def txt_to_html(lines):
    html = []
    buffer = []
    in_list = False

    def flush_buffer():
        nonlocal buffer
        if buffer:
            p_text = "<br>".join(buffer).strip()
            p_text = apply_formatting(p_text)
            if p_text.startswith("👉"):
                html.append(f'<div class="highlight">{p_text[1:].strip()}</div>')
            else:
                html.append(f"<p>{p_text}</p>")
            buffer.clear()

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            flush_buffer()
            if in_list:
                html.append("</ul>")
                in_list = False
            continue

        # 1. Κύριοι Τίτλοι (🌐 ή η πρώτη γραμμή αν είναι κεφαλαία)
        if clean_line.startswith("🌐"):
            flush_buffer()
            title = clean_line.lstrip("🌐").strip()
            html.append(f'<h1 class="main-title">{title}</h1>')

        # 2. Κύριες Ενότητες (🔷)
        elif clean_line.startswith("🔷"):
            flush_buffer()
            if in_list: html.append("</ul>"); in_list = False
            content = apply_formatting(clean_line.lstrip("🔷").strip())
            html.append(f'<h2 class="section-title">🔷 {content}</h2>')

        # 3. Υπό-ενότητες (🔹)
        elif clean_line.startswith("🔹"):
            flush_buffer()
            if in_list: html.append("</ul>"); in_list = False
            content = apply_formatting(clean_line.lstrip("🔹").strip())
            html.append(f'<h3 class="sub-section-title">🔹 {content}</h3>')

        # 4. Λίστες (🔸, •, –, *)
        elif clean_line.startswith(("🔸", "•", "–", "*")):
            if not in_list:
                flush_buffer()
                html.append('<ul class="fancy-list">')
                in_list = True
            item = apply_formatting(clean_line.lstrip("🔸•–*").strip())
            html.append(f"<li>{item}</li>")

        # 5. Αποφθέγματα (>)
        elif clean_line.startswith(">"):
            flush_buffer()
            content = apply_formatting(clean_line.lstrip(">").strip())
            html.append(f'<blockquote class="quote-box">{content}</blockquote>')

        else:
            buffer.append(clean_line)

    flush_buffer()
    if in_list: html.append("</ul>")
    return "\n".join(html)

# =========================
# SINGLE LOOP EXECUTION
# =========================
print("🚀 Starting Professional HTML Generation...")

# Σαρώνουμε τα αρχεία ΜΙΑ φορά
for filename in os.listdir("."):
    # Επεξεργαζόμαστε μόνο αρχεία .txt που έχουν -el ή -en
    fn_lower = filename.lower()
    if not fn_lower.endswith(".txt"): continue
    
    if fn_lower.endswith("-el.txt"):
        cfg = LANG_MAP["el"]
    elif fn_lower.endswith("-en.txt"):
        cfg = LANG_MAP["en"]
    else:
        continue # Αγνοούμε αρχεία χωρίς σωστή κατάληξη γλώσσας

    with open(filename, "r", encoding="utf-8") as f:
        content_lines = f.readlines()
    
    if not content_lines: continue

    # Παραγωγή περιεχομένου
    body_content = txt_to_html(content_lines)
    
    # Το όνομα του αρχείου εξόδου (αλλάζουμε μόνο το .txt σε .html)
    output_name = filename.rsplit(".", 1)[0] + ".html"

    # HTML Template
    html_template = f"""<!DOCTYPE html>
<html lang="{cfg['lang']}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SparkEthos White Paper</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f4f7f9; color: #2c3e50; margin: 0; padding: 0 1rem; line-height: 1.8; max-width: 950px; margin-left: auto; margin-right: auto; }}
        header {{ background: #003366; color: white; padding: 2rem; text-align: center; font-weight: 700; font-size: 1.8rem; border-radius: 0 0 15px 15px; margin-bottom: 2rem; }}
        main {{ background: white; padding: 3rem; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
        .main-title {{ color: #003366; text-align: center; font-size: 2.5rem; font-weight: 800; margin-bottom: 2rem; border-bottom: 3px solid #e74c3c; padding-bottom: 1rem; }}
        .section-title {{ color: #e74c3c; font-weight: 800; font-size: 1.6rem; margin-top: 3rem; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; display: block; }}
        .sub-section-title {{ color: #0056b3; font-weight: 700; font-size: 1.3rem; margin-top: 2rem; display: block; }}
        p {{ margin-bottom: 1.2rem; font-size: 1.15rem; }}
        strong {{ font-weight: 800; color: #000; }}
        .highlight {{ border-left: 6px solid #e74c3c; background: #fff5f5; padding: 1.5rem; margin: 2rem 0; font-weight: 700; font-size: 1.2rem; border-radius: 4px; color: #c0392b; text-align: center; }}
        .quote-box {{ border-left: 6px solid #003366; background: #f0f7ff; padding: 1.2rem; font-style: italic; margin: 2rem 0; color: #34495e; }}
        .fancy-list {{ margin-bottom: 2rem; padding-left: 1.5rem; }}
        .fancy-list li {{ margin-bottom: 0.8rem; font-size: 1.1rem; list-style-type: none; position: relative; }}
        .fancy-list li::before {{ content: "•"; color: #e74c3c; font-weight: bold; position: absolute; left: -1.2rem; }}
        .back-link {{ display: inline-block; text-decoration: none; color: #003366; font-weight: bold; border: 2px solid #003366; padding: 0.6rem 1.2rem; border-radius: 5px; margin-bottom: 2rem; transition: 0.3s; }}
        .back-link:hover {{ background: #003366; color: #fff; }}
        footer {{ text-align: center; padding: 4rem 0; color: #7f8c8d; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <header>{cfg['header']}</header>
    <main>
        <a href="{cfg['home']}" class="back-link">{cfg['home_label']}</a>
        {body_content}
        <div style="text-align:center; margin-top:4rem;">
            <a href="{cfg['home']}" class="back-link">{cfg['home_label']}</a>
        </div>
    </main>
    <footer>© 2026 SparkEthos Collective</footer>
</body>
</html>"""

    with open(output_name, "w", encoding="utf-8") as out_f:
        out_f.write(html_template)
    
    print(f"✅ Success: {output_name}")

print("✨ All files processed successfully.")

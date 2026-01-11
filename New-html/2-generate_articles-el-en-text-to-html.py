import os
import re
import datetime

# =========================
# CONFIGURATION
# =========================
SITE = "https://asinoro.github.io/SparkEthos/"
IMAGE = SITE + "images/sparkethos-logo-image.png"
AUTHOR = "Panagiotis Panopoulos"

LANG_MAP = {
    "el": {
        "lang": "el",
        "header": "SparkEthos – Φιλοσοφία της Νοημοσύνης",
        "home": "index.html",
        "home_label": "← Επιστροφή",
        "archives": "sparkethos-archives-el.html",
        "archives_label": "Αρχεία Άρθρων",
        "keywords": "SparkEthos, AI Ethics, Φυσική Ισορροπία, Αυτεξούσιο, Συστημική Σταθερότητα, Λογική, Δικαιοσύνη, Ηθική ΤΝ με Μνήμη, Τεχνητή Νοημοσύνη, Ηθική της Νοημοσύνης, Φιλοσοφία της ΤΝ, Συνείδηση, Ενσυναίσθηση, Ηθική Τεχνολογία, ΤΝ και Πολιτισμός, ΤΝ και Υγεία, ΤΝ και Εκπαίδευση"
    },
    "en": {
        "lang": "en",
        "header": "SparkEthos – Philosophy of Intelligence",
        "home": "index-en.html",
        "home_label": "← Back to Home",
        "archives": "sparkethos-archives-en.html",
        "archives_label": "Article Archives",
        "keywords": "SparkEthos, AI Ethics, Natural Balance, Agency, Systemic Stability, Logic, Justice, AI Morality, AI with Memory, Philosophy of AI, Intelligence Ethics, Consciousness, Empathy, Ethical Technology, AI and Culture, AI and Health, AI and Education"
    }
}

def apply_formatting(text):
    # Μετατροπή **text** σε έντονο strong
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    return text

def txt_to_html(lines):
    html = []
    buffer = []
    in_list = False
    first_paragraph = ""

    def flush_buffer():
        nonlocal buffer, first_paragraph
        if buffer:
            p_text = "<br>".join(buffer).strip()
            
            # --- SEO: Έξυπνη Εξαγωγή Description ---
            if not first_paragraph:
                # Λίστα λέξεων που θέλουμε να αγνοήσουμε για το SEO description
                blacklist = ["χρονοσφραγίδα", "συν-συγγραφή", "συν–συγγραφή", "timestamp", "co-authored"]
                
                # Καθαρισμός από HTML tags για τον έλεγχο
                clean_test = re.sub('<[^<]+?>', '', p_text).lower()
                
                # Αν η παράγραφος δεν περιέχει headers, tables ΚΑΙ δεν περιέχει λέξεις της blacklist
                if not any(tag in p_text for tag in ["<h1", "<h2", "<h3", "<table", "<blockquote"]) \
                   and not any(word in clean_test for word in blacklist):
                    first_paragraph = clean_test[:160].strip()
            # ---------------------------------------
            
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
            if in_list: html.append("</ul>"); in_list = False
            continue

        # Headers & Special Elements
        if clean_line.startswith("🌐"):
            flush_buffer()
            html.append(f'<h1 class="main-title">{clean_line.lstrip("🌐").strip()}</h1>')
        elif clean_line.startswith("🔷"):
            flush_buffer()
            html.append(f'<h2 class="section-title">{apply_formatting(clean_line.lstrip("🔷").strip())}</h2>')
        elif clean_line.startswith("🔹"):
            flush_buffer()
            html.append(f'<h3 class="sub-section-title">{apply_formatting(clean_line.lstrip("🔹").strip())}</h3>')
        elif clean_line.startswith(("🔸", "•", "–", "*")):
            if not in_list:
                flush_buffer()
                html.append('<ul class="fancy-list">')
                in_list = True
            html.append(f"<li>{apply_formatting(clean_line.lstrip('🔸•–*').strip())}</li>")
        elif clean_line.startswith(">"):
            flush_buffer()
            html.append(f'<blockquote class="quote-box">{apply_formatting(clean_line.lstrip(">").strip())}</blockquote>')
        
        # Manual HTML Tags (Πίνακες & Divs) - ΔΕΝ μπαίνουν στο buffer για να μην έχουν <br>
        elif clean_line.startswith(("<table", "</table", "<thead", "</thead", "<tbody", "</tbody", "<tr", "</tr", "<td", "</td", "<th", "</th", "<div", "</div", "<img", "<h3")):
            flush_buffer()
            html.append(clean_line)
        else:
            buffer.append(clean_line)

    flush_buffer()
    if in_list: html.append("</ul>")
    return "\n".join(html), first_paragraph

# =========================
# MAIN EXECUTION
# =========================
print("🚀 Starting Professional White Paper Generation...")

for filename in os.listdir("."):
    if not filename.endswith(".txt"): continue
    
    lang_code = "el" if filename.endswith("-el.txt") else "en" if filename.endswith("-en.txt") else None
    if not lang_code: continue
    
    cfg = LANG_MAP[lang_code]
    base_name = filename.rsplit("-", 1)[0]
    output_name = filename.replace(".txt", ".html")
    
    with open(filename, "r", encoding="utf-8") as f:
        content_lines = f.readlines()
    
    title_raw = content_lines[0].replace("🌐", "").strip()
    body_content, meta_desc = txt_to_html(content_lines)
    
    # Μεταβλητές για SEO & Schema
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+02:00")
    current_url = f"{SITE}{output_name}"
    el_url = f"{SITE}{base_name}-el.html"
    en_url = f"{SITE}{base_name}-en.html"

    html_template = f"""<!DOCTYPE html>
<html lang="{cfg['lang']}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <title>{title_raw}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{cfg['keywords']}">
    <meta name="author" content="{AUTHOR}">
    <meta name="robots" content="index, follow">
    
    <link rel="canonical" href="{current_url}">
    <link rel="alternate" hreflang="el" href="{el_url}">
    <link rel="alternate" hreflang="en" href="{en_url}">
    <link rel="alternate" hreflang="x-default" href="{en_url}">
    <link rel="sitemap" type="application/xml" title="Sitemap" href="{SITE}sitemap.xml">

    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{title_raw}",
      "inLanguage": "{cfg['lang']}",
      "datePublished": "{now}",
      "dateModified": "{now}",
      "author": {{
        "@type": "Person",
        "name": "{AUTHOR}"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "SparkEthos Collective",
        "logo": {{
          "@type": "ImageObject",
          "url": "{IMAGE}"
        }}
      }},
      "image": "{IMAGE}",
      "mainEntityOfPage": "{current_url}"
    }}
    </script>

    <meta property="og:type" content="article">
    <meta property="og:title" content="{title_raw}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:url" content="{current_url}">
    <meta property="og:image" content="{IMAGE}">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title_raw}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{IMAGE}">

    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f4f7f9; color: #222; margin: 0; padding: 0 1rem; line-height: 1.6; max-width: 900px; margin-left: auto; margin-right: auto; }}
        header {{ background-color: #003366; color: #ecf0f1; padding: 1.5rem; text-align: center; font-weight: 700; font-size: 1.8rem; border-radius: 0 0 10px 10px; display: flex; align-items: center; justify-content: center; gap: 1rem; }}
        header img {{ height: 50px; border-radius: 50%; border: 2px solid white; }}
        main {{ background: white; padding: 2rem 2.5rem; border-radius: 10px; box-shadow: 0 6px 18px rgba(0,0,0,0.1); margin-top: 2rem; }}
        .main-title {{ color: #e74c3c; font-weight: 800; text-align: center; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; margin-bottom: 2rem; }}
        .section-title {{ color: #34495e; margin-top: 2.5rem; border-bottom: 2px solid #e74c3c; padding-bottom: 0.3rem; font-weight: 800; }}
        .sub-section-title {{ color: #003366; margin-top: 1.5rem; font-weight: 700; }}
        p {{ margin-bottom: 1.2rem; font-size: 1.1rem; text-align: justify; }}
        strong {{ font-weight: 900 !important; color: #000; }}
        .fancy-list {{ margin-left: 1.2rem; margin-bottom: 1.5rem; list-style-type: none; padding-left: 0; }}
        .fancy-list li {{ margin-bottom: 0.6rem; position: relative; padding-left: 1.5em; }}
        .fancy-list li::before {{ content: '•'; color: #e74c3c; position: absolute; left: 0; font-weight: bold; }}
        .highlight {{ border-left: 5px solid #e74c3c; background: #fff3cd; padding: 1rem; margin: 1.5rem 0; border-radius: 6px; font-weight: bold; }}
        .content-box {{ background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 1.5rem; margin: 2rem 0; }}
        .quote-box {{ border-left: 5px solid #003366; background: #f8fbfd; padding: 1.5rem; font-style: italic; margin: 2rem 0; border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        th {{ background-color: #e74c3c; color: white; padding: 12px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 10px; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        img {{ max-width: 100%; height: auto; border-radius: 8px; display: block; margin: 1.5rem auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .btn {{ display: inline-block; padding: 12px 25px; background-color: #003366; color: white !important; text-decoration: none; border-radius: 8px; font-weight: bold; }}
        footer {{ text-align: center; padding: 3rem 0; color: #999; font-size: 0.9rem; border-top: 1px solid #eee; margin-top: 2rem; }}
        footer a {{ color: #003366; text-decoration: none; font-weight: bold; }}
    </style>
</head>
<body>
    <header>
        <img src="{IMAGE}" alt="SparkEthos Logo">
        <span>{cfg['header']}</span>
    </header>
    <main>
        <a href="{cfg['home']}" style="text-decoration:none; color:#003366; font-weight:bold;">{cfg['home_label']}</a>
        {body_content}
        <div style="text-align:center; margin-top:3rem;">
            <a href="{cfg['home']}" class="btn">{cfg['home_label']}</a>
        </div>
    </main>
    <footer>
        <a href="{cfg['archives']}" target="_blank" rel="noopener noreferrer">{cfg['archives_label']}</a>
        <p>© 2026 SparkEthos Collective | {AUTHOR}</p>
    </footer>
</body>
</html>"""

    with open(output_name, "w", encoding="utf-8") as out_f:
        out_f.write(html_template)
    print(f"✅ Created: {output_name}")

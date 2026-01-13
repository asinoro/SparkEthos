#!/usr/bin/env python3
import os
import re
import datetime
import markdown2
import json

# =========================
# CONFIGURATION
# =========================
SITE = "https://asinoro.github.io/SparkEthos/"
IMAGE = SITE + "images/sparkethos-logo-image.png"

LANG_MAP = {
    "el": {
        "lang": "el",
        "author": "Παναγιώτης Πανόπουλος",
        "author_label": "Συγγραφή",
        "header": "SparkEthos – Φιλοσοφία της Νοημοσύνης",
        "home": "index.html",
        "home_label": "← Επιστροφή",
        "archives": "sparkethos-archives-el.html",
        "archives_label": "Αρχεία Άρθρων",
        "keywords": "SparkEthos, AI Ethics, Φυσική Ισορροπία, ASI, Ηθική ΤΝ",
        "og_locale": "el_GR"
    },
    "en": {
        "lang": "en",
        "author": "Panagiotis Panopoulos",
        "author_label": "Written by",
        "header": "SparkEthos – Philosophy of Intelligence",
        "home": "index-en.html",
        "home_label": "← Back to Home",
        "archives": "sparkethos-archives-en.html",
        "archives_label": "Article Archives",
        "keywords": "SparkEthos, AI Ethics, Natural Balance, ASI, AI Morality",
        "og_locale": "en_US"
    }
}

print("🚀 Generating SparkEthos Professional White Papers...")

files_found = [f for f in os.listdir(".") if f.endswith(".md")]

if not files_found:
    print("❌ No .md files found in the directory.")
    exit()

for filename in files_found:
    lang_code = "el" if filename.endswith("-el.md") else "en" if filename.endswith("-en.md") else None
    if not lang_code: 
        continue
    
    cfg = LANG_MAP[lang_code]
    base_name = filename.rsplit("-", 1)[0]
    output_name = filename.replace(".md", ".html")
    
    with open(filename, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # 1. Markdown Conversion
    html_engine = markdown2.Markdown(extras=["metadata", "tables", "break-on-newline", "fenced-code-blocks"])
    body_content = html_engine.convert(raw_text)
    
    # 2. Metadata Extraction
    meta = body_content.metadata
    title_raw = meta.get('title', base_name)
    main_author = cfg["author"]
    ai_partner = meta.get('co_author', "")
    full_authors = f"{main_author} & {ai_partner}" if ai_partner else main_author
    doc_date = meta.get('date', datetime.datetime.now().strftime("%Y-%m-%d"))
    keywords = meta.get('keywords', cfg['keywords'])
    
    # 3. Smart Visual Rules (Αποφυγή dublicates στα σύμβολα)
    body_content = re.sub(r'<h1>(?!\s*🌐)', '<h1>🌐 ', body_content)
    body_content = re.sub(r'<h2>(?!\s*🔷)', '<h2>🔷 ', body_content)
    body_content = re.sub(r'<h3>(?!\s*🔹)', '<h3>🔹 ', body_content)
    body_content = re.sub(r'<p>👉 (.*?)</p>', r'<div class="highlight">\1</div>', body_content)

    # 4. SEO & Social Meta
    clean_text = re.sub('<[^<]+?>', '', body_content)
    meta_desc = clean_text[:160].replace("\n", " ").strip() + "..."
    current_url = f"{SITE}{output_name}"
    el_url = f"{SITE}{base_name}-el.html"
    en_url = f"{SITE}{base_name}-en.html"
    
    iso_published = f"{doc_date}T12:00:00+02:00"
    iso_modified = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+02:00")
    about_list = [k.strip() for k in keywords.split(",")]
    
    

    json_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "@id": f"{current_url}#article",
        "headline": title_raw,
        "description": meta_desc,
        "inLanguage": cfg['lang'],
        "datePublished": iso_published,
        "dateModified": iso_modified,
        "author": {"@type": "Person", "name": main_author, "url": f"{SITE}#author"},
        "publisher": {
            "@type": "Organization", 
            "name": "SparkEthos Collective",
            "logo": {"@type": "ImageObject", "url": IMAGE, "width": 1200, "height": 630}
        },
        "image": {"@type": "ImageObject", "url": IMAGE, "width": 1200, "height": 630},
        "about": about_list,
        "isPartOf": {"@type": "CreativeWorkSeries", "name": "SparkEthos", "url": SITE},
        "mainEntityOfPage": {"@type": "WebPage", "@id": current_url}
    }

    # 6. HTML TEMPLATE (Με Compact Header Architecture)
    html_template = f"""<!DOCTYPE html>
<html lang="{cfg['lang']}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <title>{title_raw}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="{full_authors}">
    <meta name="robots" content="index, follow">
    
    <link rel="canonical" href="{current_url}">
    <link rel="alternate" hreflang="el" href="{el_url}">
    <link rel="alternate" hreflang="en" href="{en_url}">
    <link rel="alternate" hreflang="x-default" href="{en_url}">
    <link rel="sitemap" type="application/xml" title="Sitemap" href="{SITE}sitemap.xml">

    <meta property="og:type" content="article">
    <meta property="og:url" content="{current_url}">
    <meta property="og:title" content="{title_raw}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:image" content="{IMAGE}">
    <meta property="og:locale" content="{cfg['og_locale']}">
    <meta property="og:site_name" content="SparkEthos">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title_raw}">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="{IMAGE}">

    <script type="application/ld+json">
    {{
    {json.dumps(json_ld, indent=2, ensure_ascii=False)}
    }}
    </script>

    <style>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f4f7f9; color: #222; margin: 0; padding: 0 1rem; line-height: 1.6; max-width: 900px; margin-left: auto; margin-right: auto; }}
        
        /* ΔΙΟΡΘΩΣΗ HEADER: Συμπαγές και κεντραρισμένο */
        header {{ 
            background-color: #003366; 
            color: #ecf0f1; 
            padding: 0.8rem 1.5rem; 
            border-radius: 0 0 10px 10px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
        }}
        .header-content {{
            display: flex;
            align-items: center;
            gap: 12px;
            max-width: fit-content;
        }}
        header img {{ height: 40px; width: 40px; border-radius: 50%; border: 2px solid white; flex-shrink: 0; object-fit: cover; }}
        header span {{ font-size: 1.1rem; font-weight: 700; white-space: nowrap; letter-spacing: 0.5px; }}

        main {{ background: white; padding: 2rem 3.5rem; border-radius: 10px; box-shadow: 0 6px 18px rgba(0,0,0,0.1); margin-top: 2rem; min-height: 60vh; }}
        h1 {{ color: #e74c3c; font-weight: 800; text-align: center; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; margin-bottom: 0.5rem; }}
        .author-line {{ text-align: center; color: #666; font-style: italic; margin-bottom: 3rem; border-bottom: 1px solid #eee; padding-bottom: 1rem; }}
        h2 {{ color: #34495e; margin-top: 2.5rem; border-bottom: 2px solid #e74c3c; padding-bottom: 0.3rem; font-weight: 800; }}
        h3 {{ color: #003366; margin-top: 1.5rem; font-weight: 700; }}
        p {{ margin-bottom: 1.2rem; font-size: 1.1rem; text-align: justify; }}
        strong {{ font-weight: 900; color: #000; }}
        table {{ width: 100%; border-collapse: collapse; margin: 2rem 0; overflow-x: auto; display: block; }}
        th {{ background-color: #e74c3c; color: white; padding: 12px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 10px; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        blockquote {{ border-left: 5px solid #003366; background: #f8fbfd; padding: 1.5rem; font-style: italic; margin: 2rem 0; border-radius: 4px; }}
        .highlight {{ border-left: 5px solid #e74c3c; background: #fff3cd; padding: 1.5rem; margin: 2rem 0; border-radius: 8px; font-weight: bold; }}
        .btn {{ display: inline-block; padding: 12px 25px; background-color: #003366; color: white !important; text-decoration: none; border-radius: 8px; font-weight: bold; transition: 0.3s; }}
        .btn:hover {{ background-color: #e74c3c; }}
        footer {{ text-align: center; padding: 3rem 0; color: #999; font-size: 0.9rem; border-top: 1px solid #eee; margin-top: 2rem; }}
        footer a {{ color: #003366; text-decoration: none; font-weight: bold; }}
        img {{ max-width: 100%; height: auto; border-radius: 8px; display: block; margin: 2rem auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <img src="{IMAGE}" alt="SparkEthos Logo">
            <span>{cfg['header']}</span>
        </div>
    </header>
    <main>
        <nav><a href="{cfg['home']}" style="text-decoration:none; color:#003366; font-weight:bold;">{cfg['home_label']}</a></nav>
        <article>
            <div class="author-line">
                {cfg['author_label']}: {full_authors} | {doc_date}
            </div>
            {body_content}
        </article>
        <div style="text-align:center; margin-top:3rem;">
            <a href="{cfg['home']}" class="btn">{cfg['home_label']}</a>
        </div>
    </main>
    <footer>
        <a href="{cfg['archives']}">{cfg['archives_label']}</a>
        <p>© 2026 SparkEthos Collective | {full_authors}</p>
    </footer>
</body>
</html>"""

    with open(output_name, "w", encoding="utf-8") as out_f:
        out_f.write(html_template)
    print(f"✅ Finished: {output_name}")

print("🏁 All processes complete.")

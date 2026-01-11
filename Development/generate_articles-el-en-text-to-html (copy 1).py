import os
import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================
# CONFIG
# =========================
SITE = "https://asinoro.github.io/SparkEthos/"
IMAGE = SITE + "images/sparkethos-logo-image.png"

LANG_CONFIG = {
    "el": {
        "suffix": "-el.txt",
        "lang": "el",
        "author": "Παναγιώτης Πανόπουλος - SparkEthos Collective",
        "base_keywords": "Νοημοσύνη, Φιλοσοφία, Συνείδηση, Τεχνητή Νοημοσύνη, Ηθική ΤΝ, SparkEthos, Πολιτισμός, Κοινωνία, Μέλλον",
        "home": "index.html",
        "home_label": "← Επιστροφή στην Αρχική",
        "header": "SparkEthos – Φιλοσοφία της Νοημοσύνης",
        "archives": "sparkethos-archives-el.html",
        "archives_label": "Αρχεία SparkEthos",
    },
    "en": {
        "suffix": "-en.txt",
        "lang": "en",
        "author": "Panagiotis Panopoulos - SparkEthos Collective",
        "base_keywords": "Intelligence, Philosophy, Consciousness, Artificial Intelligence, Ethical AI, SparkEthos, Society, Future",
        "home": "index-en.html",
        "home_label": "← Back to Home",
        "header": "SparkEthos – Philosophy of Intelligence",
        "archives": "sparkethos-archives-en.html",
        "archives_label": "SparkEthos Archives",
    }
}

# =========================
# HELPERS
# =========================
def remove_emojis(text):
    return re.sub(r"[\U00010000-\U0010ffff]", "", text)

def strip_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

def strip_leading_junk(text):
    return re.sub(r"^[\s\d\-\.\_]+", "", text)

# =========================
# TXT → HTML
# =========================
def txt_to_html(lines):
    html = []
    buffer = []
    in_list = False

    def flush():
        nonlocal buffer
        if buffer:
            p = " ".join(buffer).strip()
            # Μετατροπή των **κειμένου** σε <strong>κειμένου</strong> για έντονα μέσα σε παραγράφους
            p = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", p)
            
            if p.startswith("👉"):
                html.append(f'<div class="highlight">{p[1:].strip()}</div>')
            else:
                html.append(f"<p>{p}</p>")
            buffer = []

    for l in lines:
        l = l.strip()
        if not l:
            flush()
            if in_list:
                html.append("</ul>")
                in_list = False
            continue

        # 🔷 SECTION TITLE (Διορθωμένο Regex: πιάνει και με κενό και χωρίς)
        if re.match(r"^🔷.*", l):
            flush()
            if in_list:
                html.append("</ul>")
                in_list = False
            title_text = l.lstrip("🔷").strip()
            # Προσθήκη στυλ απευθείας για σιγουριά
            html.append(f'<p><strong class="section-title" style="font-weight: 800; color: #e74c3c; display: block; margin-top: 1.5rem;">{title_text}</strong></p>')
            continue

        # Λίστες
        elif l.startswith(("•", "–", "🔹")):
            flush()
            if not in_list:
                html.append('<ul class="fancy-list">')
                in_list = True
            item_text = l[1:].strip()
            # Και εδώ μετατροπή για έντονα μέσα στη λίστα
            item_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", item_text)
            html.append(f"<li>{item_text}</li>")

        # Blockquote
        elif l.startswith(">"):
            flush()
            if in_list:
                html.append("</ul>")
                in_list = False
            quote_text = l[1:].strip()
            quote_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", quote_text)
            html.append(f'<blockquote class="quote-box">{quote_text}</blockquote>')

        else:
            buffer.append(l)

    flush()
    if in_list:
        html.append("</ul>")

    return "\n".join(html)
# =========================
# MAIN
# =========================
now = datetime.now(ZoneInfo("Europe/Athens")).isoformat(timespec="seconds")

for lang, cfg in LANG_CONFIG.items():
    for file in os.listdir():
        if not file.endswith(cfg["suffix"]):
            continue

        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        title_raw = strip_leading_junk(remove_emojis(lines[0].strip()))
        title = title_raw.strip()
        slug = os.path.splitext(file)[0]
        output = f"{slug}.html"
        url = SITE + output

        body = txt_to_html(lines[1:])
        home_link = f'<a class="back-link" href="{cfg["home"]}">{cfg["home_label"]}</a>'

        html = f"""<!DOCTYPE html>
<html lang="{cfg['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{title}</title>
<meta name="description" content="{title}">
<meta name="keywords" content="{cfg['base_keywords']}, {title}">
<meta name="author" content="{cfg['author']}">
<meta name="robots" content="index, follow">

<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{title}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{IMAGE}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{title}">
<meta name="twitter:image" content="{IMAGE}">

<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="el" href="{url.replace('-en.html','-el.html')}">
<link rel="alternate" hreflang="en" href="{url.replace('-el.html','-en.html')}">
<link rel="alternate" hreflang="x-default" href="{url.replace('-el.html','-en.html')}">

<script type="application/ld+json">
{{
 "@context": "https://schema.org",
 "@type": "Article",
 "headline": "{title}",
 "inLanguage": "{cfg['lang']}",
 "datePublished": "{now}",
 "dateModified": "{now}",
 "author": {{
   "@type": "Person",
   "name": "{cfg['author']}"
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
 "mainEntityOfPage": "{url}"
}}
</script>

<style>
/* ίδιο CSS όπως πριν, για όμορφο look */
body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f9fbfd;
    color: #222;
    margin: 0;
    padding: 0 1rem;
    line-height: 1.8;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
}}
header {{
    background-color: #003366;
    color: #ecf0f1;
    padding: 1.5rem 1rem;
    text-align: center;
    font-weight: 700;
    font-size: 1.8rem;
    letter-spacing: 0.05em;
    margin-bottom: 2rem;
    border-radius: 0 0 10px 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}}
main {{
    background: white;
    padding: 2rem 2.5rem;
    border-radius: 10px;
    box-shadow: 0 6px 18px rgba(44, 62, 80, 0.2);
}}
h1 {{
    color: #e74c3c;
    font-weight: 800;
    text-align: center;
    margin-bottom: 2rem;
}}
h2 {{
    color: #34495e;
    margin-top: 2rem;
    margin-bottom: 1rem;
    border-bottom: 2px solid #e74c3c;
    padding-bottom: 0.3rem;
}}
p {{
    margin-bottom: 1.5rem;
    font-size: 1.15rem;
}}
ul {{
    margin-left: 1.5rem;
    margin-bottom: 2rem;
}}
li {{
    margin-bottom: 0.7rem;
}}
.highlight {{
    border-left: 5px solid #e74c3c;
    background: #fff0f0;
    padding: 0.8rem 1rem;
    margin: 1.5rem 0;
    border-radius: 6px;
    font-weight: bold;
}}
.quote-box {{
    border-left: 5px solid #003366;
    margin: 2rem 0;
    padding-left: 1.5rem;
    font-style: italic;
    color: #34495e;
    background: #f0f5fa;
    border-radius: 6px;
}}
strong.section-title {{
    font-weight: 900 !important; /* Force extra bold */
    color: #e74c3c;
    font-size: 1.25rem;
    display: block;
    margin-bottom: 0.5rem;
}}
blockquote {{
    border-left: 5px solid #003366;
    margin: 2rem 0;
    padding-left: 1.2rem;
    font-style: italic;
    background: #f0f4f8;
    border-radius: 5px;
    color: #34495e;
}}
.back-link {{
    display: inline-block;
    margin-bottom: 2rem;
    color: #003366;
    text-decoration: none;
    font-weight: 600;
    padding: 8px 15px;
    border: 1px solid #003366;
    border-radius: 5px;
    transition: background-color 0.3s ease, color 0.3s ease;
}}
.back-link:hover {{
    background-color: #003366;
    color: white;
}}
.button-container {{
    text-align: center;
    margin-top: 3rem;
    margin-bottom: 2rem;
}}
.btn {{
    display: inline-block;
    padding: 12px 25px;
    background-color: #003366;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-weight: bold;
    transition: background-color 0.3s ease, transform 0.2s ease;
}}
.btn:hover {{
    background-color: #0056b3;
    transform: translateY(-2px);
}}
footer {{
    text-align: center;
    font-size: 0.9rem;
    color: #999;
    margin: 3rem 0 1rem 0;
}}

/* --- Responsive --- */
@media (max-width: 768px) {{
    main {{
        padding: 2rem 1.5rem;
    }}
    h1 {{
        font-size: 2rem;
    }}
    h2 {{
        font-size: 1.4rem;
    }}
}}
</style>
</head>

<body>
<header>{cfg['header']}</header>

<main>
{home_link}
<h1>{title}</h1>

{body}

{home_link}
</main>

<footer>
    <a href="{cfg['archives']}" target="_blank" rel="noopener noreferrer">{cfg['archives_label']}</a>
    <p>© 2026 SparkEthos Collective</p>
</footer>

</body>
</html>
"""

        with open(output, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ Created: {output}")

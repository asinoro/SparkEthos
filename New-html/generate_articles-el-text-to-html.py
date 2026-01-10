import os
import re
import unicodedata
from datetime import date

# =========================
# CONFIG
# =========================
SITE = "https://asinoro.github.io/SparkEthos/"
IMAGE = SITE + "images/sparkethos-logo-image.png"
AUTHOR = "Παναγιώτης Πανόπουλος - SparkEthos Collective"

BASE_KEYWORDS = (
    "Νοημοσύνη, Λογική, Φιλοσοφία, Συνείδηση, Τεχνητή Νοημοσύνη, Ηθική ΤΝ, Μνήμη σε Ηθική ΤΝ, Αυτογνωσία, Φυσική Ισορροπία, SparkEthos"
)

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
# TXT TO HTML
# =========================
def txt_to_html(lines):
    html = []
    buffer = []
    in_list = False

    def flush_buffer():
        nonlocal buffer
        if buffer:
            paragraph = " ".join(buffer).strip()
            # αν είναι σημαντική φράση, highlight
            if paragraph.startswith("👉"):
                paragraph = paragraph[1:].strip()
                html.append(f'<div class="highlight">{paragraph}</div>')
            else:
                html.append(f"<p>{paragraph}</p>")
            buffer = []

    for l in lines:
        l = l.strip()
        if not l:
            flush_buffer()
            if in_list:
                html.append("</ul>")
                in_list = False
            continue

        # Headers με emoji
        if re.match(r"^[🧠🧬🎭⚖️🕳️🧯🧩].*", l):
            flush_buffer()
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append(f"<h2>🔹 {l}</h2>")

        # Λίστες
        elif l.startswith(("•", "–", "🔹")):
            flush_buffer()
            if not in_list:
                html.append('<ul class="fancy-list">')
                in_list = True
            html.append(f"<li>{l[1:].strip()}</li>")

        # Blockquotes με >
        elif l.startswith(">"):
            flush_buffer()
            if in_list:
                html.append("</ul>")
                in_list = False
            html.append(f'<blockquote class="quote-box">{l[1:].strip()}</blockquote>')

        else:
            buffer.append(l)

    flush_buffer()
    if in_list:
        html.append("</ul>")

    return "\n".join(html)

# =========================
# MAIN LOOP
# =========================
for file in os.listdir():
    if not file.endswith("-el.txt"):
        continue

    raw_filename = os.path.splitext(file)[0]

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Τίτλος από την πρώτη γραμμή του txt
    first_line = lines[0].strip()
    title = strip_leading_junk(remove_emojis(first_line))

    slug = raw_filename  # κρατάμε το όνομα του αρχείου όπως είναι
    output = f"{slug}.html"
    url = SITE + output

    today = date.today().isoformat()
    body_html = txt_to_html(lines[1:])  # παράβλεψε την πρώτη γραμμή (τίτλο)

    html = f"""<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{title}</title>
<meta name="description" content="{title}">
<meta name="keywords" content="{BASE_KEYWORDS}, {title}">
<meta name="author" content="{AUTHOR}">
<meta name="robots" content="index, follow">

<!-- Open Graph -->
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{title}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{IMAGE}">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{title}">
<meta name="twitter:image" content="{IMAGE}">

<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="el" href="{url}">
<link rel="alternate" hreflang="en" href="{url.replace('-el.html','-en.html')}">
<link rel="alternate" hreflang="x-default" href="{url.replace('-el.html','-en.html')}">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "@id": "{url}#article",
  "headline": "{title}",
  "description": "{title}",
  "inLanguage": "el",
  "datePublished": "{today}",
  "dateModified": "{today}",
  "author": {{
    "@type": "Person",
    "name": "Panagiotis Panopoulos",
    "url": "{SITE}"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "SparkEthos Collective",
    "logo": {{
      "@type": "ImageObject",
      "url": "{IMAGE}",
      "width": 1200,
      "height": 630
    }}
  }},
  "image": {{
    "@type": "ImageObject",
    "url": "{IMAGE}",
    "width": 1200,
    "height": 630
  }},
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{url}"
  }}
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
<header >SparkEthos – Φιλοσοφία της Νοημοσύνης</header>

<main>
<a href="index.html" class="back-link">← Επιστροφή στην Αρχική</a>
<h1>{title}</h1>
{body_html}
<div class="button-container">
    <a href="index.html" class="btn">← Επιστροφή στην Αρχική</a>
</div>
</main>
<footer>
    <div class="footer-content">
        <a href="sparkethos-archives-el.html" target="_blank" class="btn">Αρχεία SparkEthos</a>
        <p>© 2026  SparkEthos Collective. Όλα τα δικαιώματα διατηρούνται.</p>
    </div>
</footer>
</body>
</html>
"""

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Created: {output}")


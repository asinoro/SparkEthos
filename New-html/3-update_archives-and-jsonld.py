#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import locale
import shutil
from datetime import datetime
from bs4 import BeautifulSoup
import argparse

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEW_HTML_DIR = BASE_DIR  # οι νέες HTML σελίδες είναι στον ίδιο φάκελο με το script
ROOT_DIR = os.path.dirname(BASE_DIR)

ARCHIVES = {
    "el": os.path.join(ROOT_DIR, "sparkethos-archives-el.html"),
    "en": os.path.join(ROOT_DIR, "sparkethos-archives-en.html"),
}

SITE_URL = "https://asinoro.github.io/SparkEthos/"

# =========================
# HELPERS
# =========================
def log(msg):
    print(msg)

def format_date(date_obj, lang):
    try:
        if lang == "el":
            locale.setlocale(locale.LC_TIME, "el_GR.UTF-8")
            return date_obj.strftime("%d %B %Y")
        else:
            locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
            return date_obj.strftime("%B %d, %Y")
    except locale.Error:
        return date_obj.strftime("%Y-%m-%d")

def smart_icon(title, keywords=""):
    text = f"{title} {keywords}".lower()
    ICON_MAP = {
        "        "ai": "🧠", "ΑΙ": "🧠", "ΤΝ": "🧠",
        "artificial intelligence": "🧠", "τεχνητή νοημοσύνη": "🧠",
        "conscious": "🧬", "συνείδηση": "🧬",
        "ethic": "⚖️", "ηθική": "⚖️",
        "justice": "⚖️", "δικαιοσύνη": "⚖️",
        "philosophy": "🎭", "φιλοσοφία": "🎭",
        "reflection": "🧘‍♂️", "στοχασμός": "🧘‍♂️",
        "control": "🧯", "έλεγχος": "🧯",
        "warning": "⚠️", "κίνδυνος": "⚠️",
        "paradox": "🧩", "παράδοξο": "🧩",
        "conscious": "🧬", "συνείδηση": "🧬",
        "security": "🟥", "ασφάλεια": "🟥", 
        "war": "🟥", "πόλεμος": "🟥",
        "future": "🚀", "μέλλον": "🚀",
        "evolution": "🌱", "εξέλιξη": "🌱",
        "logic": "🔹", "λογική": "🔹",
        "compass": "🧭", "πυξίδα": "🧭"
        "world": "🌍", "κόσμος": "🌍",
        "global": "🌐", "παγκόσμιο": "🌐",
        "alliance": "🤝", "συμμαχία": "🤝",
        "empathy": "💞", "ενσυναίσθηση": "💞",
        "sparkethos": "💠",
        "spark": "💡",
        }
    for key, icon in ICON_MAP.items():
        if key in text:
            return icon
    return "🌍"

def extract_html_metadata(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else os.path.basename(file_path)
    keywords_tag = soup.find("meta", {"name": "keywords"})
    keywords = keywords_tag["content"] if keywords_tag else ""
    canonical = soup.find("link", {"rel": "canonical"})
    href = canonical["href"].split("/")[-1] if canonical else os.path.basename(file_path)
    lang = soup.html.get("lang", "en") if soup.html else "en"
    json_ld_tag = soup.find("script", {"type": "application/ld+json"})
    date_obj = datetime.today()
    if json_ld_tag:
        try:
            data = json.loads(json_ld_tag.string)
            date_obj = datetime.fromisoformat(data.get("datePublished", date_obj.isoformat()))
        except Exception:
            pass
    return title, keywords, href, lang, date_obj

def load_archive_soup(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Δεν βρέθηκε {path}")
    shutil.copy(path, path + ".bak")
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    section = soup.find("section", id="articles")
    if not section:
        raise RuntimeError(f"❌ Δεν βρέθηκε <section id='articles'> στο {path}")
    existing = {a["href"]: div for div in section.find_all("div", class_="link-container") for a in div.find_all("a", href=True)}
    return soup, section, existing

def load_jsonld_from_html(path):
    if not os.path.exists(path):
        return {"webpage": None, "itemlist": {"@context": "https://schema.org","@type": "ItemList","itemListElement":[]}}
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    webpage = None
    itemlist = {"@context": "https://schema.org","@type":"ItemList","itemListElement":[]}
    for s in scripts:
        try:
            data = json.loads(s.string)
            if data.get("@type") == "WebPage":
                webpage = data
            elif data.get("@type") == "ItemList":
                itemlist = data
        except Exception:
            continue
    return {"webpage": webpage, "itemlist": itemlist}

def save_jsonld_to_html(file_path, webpage, itemlist, dry_run=False):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    for s in soup.find_all("script", type="application/ld+json"):
        s.decompose()
    head = soup.head or soup.new_tag("head")
    if not soup.head:
        soup.insert(0, head)
    for data in [webpage, itemlist]:
        if not data:
            continue
        script_tag = soup.new_tag("script", type="application/ld+json")
        script_tag.string = json.dumps(data, ensure_ascii=False, indent=2)
        head.append(script_tag)
    if not dry_run:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        log(f"✅ Ενημερώθηκε: {file_path}")
    else:
        log(f"🧪 DRY-RUN: Δεν γράφτηκε {file_path}")

# =========================
# MAIN
# =========================
parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()

# Load archives
archives_soups = {}
archives_jsonld = {}
for lang, path in ARCHIVES.items():
    soup, section, existing = load_archive_soup(path)
    archives_soups[lang] = {"soup": soup, "section": section, "existing": existing}
    archives_jsonld[lang] = load_jsonld_from_html(path)

# Scan new HTML files
for file in os.listdir(NEW_HTML_DIR):
    if not file.endswith(".html"):
        continue
    full_path = os.path.join(NEW_HTML_DIR, file)
    title, keywords, href, lang, date_obj = extract_html_metadata(full_path)
    if lang not in ARCHIVES:
        log(f"⚠️ Αγνώστη γλώσσα {lang} για {file}, αγνοείται")
        continue
    section = archives_soups[lang]["section"]
    existing_divs = archives_soups[lang]["existing"]

    display_date = format_date(date_obj, lang)
    data_date = date_obj.strftime("%Y-%m-%d")

    # ----------------
    # Update or insert <div>
    # ----------------
    if href in existing_divs:
        div = existing_divs[href]
        div["data-title"] = title
        div["data-date"] = data_date
        div["data-tags"] = keywords
        pub_date = div.find("span", class_="pub-date")
        if pub_date:
            pub_date.string = display_date
    else:
        new_div = BeautifulSoup(f'''
<div class="link-container"
     data-title="{title}"
     data-date="{data_date}"
     data-tags="{keywords}">
  <a href="{href}" target="_blank" class="link-button">
    <span class="icon">{smart_icon(title, keywords)}</span>{title}
  </a>
  <span class="pub-date">{display_date}</span>
</div>
''', "html.parser")
        section.insert(0, new_div)
        log(f"⚡ Νέο άρθρο στο HTML: {file}")

    # ----------------
    # Update JSON-LD ItemList
    # ----------------
    itemlist = archives_jsonld[lang]["itemlist"]
    urls = [item["url"] for item in itemlist.get("itemListElement",[])]
    page_url = SITE_URL + href
    if page_url not in urls:
        new_item = {
            "@type":"ListItem",
            "url": page_url,
            "name": title,
            "datePublished": data_date,
            "keywords":[k.strip() for k in keywords.split(",")] if keywords else [],
            "inLanguage": lang,
            "icon": smart_icon(title, keywords)
        }
        itemlist["itemListElement"].insert(0,new_item)
        # Reindex positions
        for idx,item in enumerate(itemlist["itemListElement"],1):
            item["position"] = idx
        log(f"➕ NEW JSON-LD item: {file}")

# Save archives
for lang, path in ARCHIVES.items():
    # HTML
    soup = archives_soups[lang]["soup"]
    if not args.dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        log(f"✅ Ενημερώθηκε HTML: {path}")
    else:
        log(f"🧪 DRY-RUN: HTML δεν γράφτηκε {path}")
    # JSON-LD
    save_jsonld_to_html(path, archives_jsonld[lang]["webpage"], archives_jsonld[lang]["itemlist"], dry_run=args.dry_run)

log("🎯 Ολοκληρώθηκε: HTML + auto-icon + JSON-LD sync!")

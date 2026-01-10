#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import argparse
from datetime import datetime
import locale
from bs4 import BeautifulSoup

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # New-html
ROOT_DIR = os.path.dirname(BASE_DIR)

NEW_HTML_DIR = BASE_DIR  # οι νέες HTML σελίδες εδώ

ARCHIVES = {
    "el": os.path.join(ROOT_DIR, "sparkethos-archives-el.html"),
    "en": os.path.join(ROOT_DIR, "sparkethos-archives-en.html"),
}

SITE_URL = "https://asinoro.github.io/SparkEthos/"

# =========================
# HELPERS
# =========================
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

def log(msg):
    print(msg)

def smart_icon(title, keywords=""):
    text = f"{title} {keywords}".lower()
    ICON_MAP = {
        "ai": "🧠", "artificial intelligence": "🧠", "τεχνητή νοημ": "🧠",
        "ethic": "⚖️", "ηθική": "⚖️",
        "philosophy": "🎭", "φιλοσοφ": "🎭",
        "control": "🧯", "έλεγχ": "🧯",
        "paradox": "🧩", "παράδοξ": "🧩",
        "conscious": "🧬", "συνείδη": "🧬",
        "security": "🟥", "στρατιω": "🟥", "war": "🟥", "κυβερνο": "🟥",
        "future": "🚀", "μέλλον": "🚀",
        "logic": "🔹", "λογικ": "🔹",
    }
    for key, icon in ICON_MAP.items():
        if key in text:
            return icon
    return "🌍"

def extract_metadata_from_html(file_path):
    """Βασική εξαγωγή τίτλου, ημερομηνίας και keywords από <meta> tags"""
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else os.path.basename(file_path)
    date_meta = soup.find("meta", {"name": "date"})
    date_str = date_meta["content"] if date_meta else datetime.today().strftime("%Y-%m-%d")
    keywords_meta = soup.find("meta", {"name": "keywords"})
    keywords = keywords_meta["content"] if keywords_meta else ""
    lang_meta = soup.find("html")
    lang = lang_meta.get("lang", "el") if lang_meta else "el"
    return title, date_str, keywords, lang

def load_jsonld_from_html(file_path):
    """Επιστρέφει dict με WebPage και ItemList JSON-LD"""
    if not os.path.exists(file_path):
        return {"webpage": None, "itemlist": {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": []}}
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    webpage = None
    itemlist = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": []}
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
    """Ενσωμάτωση JSON-LD στο υπάρχον HTML χωρίς να σβήνεται τίποτα"""
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    # Αφαιρούμε παλιά JSON-LD scripts
    for s in soup.find_all("script", type="application/ld+json"):
        s.decompose()
    
    # Δημιουργούμε νέα scripts
    new_scripts = []
    for data in [webpage, itemlist]:
        if data is None:
            continue
        script_tag = soup.new_tag("script", type="application/ld+json")
        script_tag.string = json.dumps(data, ensure_ascii=False, indent=2)
        new_scripts.append(script_tag)
    
    # Προσθέτουμε τα scripts στο <head>
    head = soup.head or soup.new_tag("head")
    if not soup.head:
        soup.insert(0, head)
    for s in new_scripts:
        head.append(s)
    
    content = str(soup)
    
    if dry_run:
        log(f"🧪 DRY-RUN: Δεν γράφτηκε {file_path}")
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"✅ Ενημερώθηκε: {file_path}")

# =========================
# MAIN
# =========================
parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()

# Load current archives
archives_data = {}
for lang, path in ARCHIVES.items():
    archives_data[lang] = load_jsonld_from_html(path)

# Scan new HTML files
for file in os.listdir(NEW_HTML_DIR):
    if not file.endswith(".html"):
        continue
    full_path = os.path.join(NEW_HTML_DIR, file)
    title, date_str, keywords, lang = extract_metadata_from_html(full_path)
    if lang not in ARCHIVES:
        log(f"⚠️ Unknown language {lang} in {file}, skipping")
        continue
    new_item = {
        "@type": "ListItem",
        "url": SITE_URL + file,
        "name": title,
        "datePublished": date_str,
        "keywords": [k.strip() for k in keywords.split(",")] if keywords else [],
        "inLanguage": lang,
        "icon": smart_icon(title, keywords)
    }
    # Prepend στην αρχή
    archives_data[lang]["itemlist"]["itemListElement"].insert(0, new_item)
    # Reindex positions
    for idx, item in enumerate(archives_data[lang]["itemlist"]["itemListElement"], 1):
        item["position"] = idx
    log(f"🔄 Updated HTML: {file}")
    log(f"➕ NEW JSON-LD item: {file}")

# Save updated archives
for lang, path in ARCHIVES.items():
    save_jsonld_to_html(path, archives_data[lang]["webpage"], archives_data[lang]["itemlist"], dry_run=args.dry_run)

log("🎯 Ολοκληρώθηκε (auto-icon + metadata + JSON-LD sync)")

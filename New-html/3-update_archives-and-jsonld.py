#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import locale
import shutil
import re
from datetime import datetime
from bs4 import BeautifulSoup
import argparse

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Το script τρέχει μέσα από το New-html, οπότε ο ROOT είναι ο γονέας
NEW_HTML_DIR = BASE_DIR 
ROOT_DIR = os.path.dirname(BASE_DIR)

ARCHIVES = {
    "el": os.path.join(ROOT_DIR, "sparkethos-archives-el.html"),
    "en": os.path.join(ROOT_DIR, "sparkethos-archives-en.html"),
}

# =========================
# HELPERS
# =========================
def log(msg):
    print(msg)

def extract_icon(title):
    """Εξάγει το emoji από τον τίτλο"""
    emoji_pattern = re.compile(r'[\U0001f300-\U0001f9ff\u2700-\u27bf]')
    match = emoji_pattern.search(title)
    return match.group() if match else "📄"

def clean_title(title):
    """Καθαρίζει τον τίτλο από emojis"""
    emoji_pattern = re.compile(r'[\U0001f300-\U0001f9ff\u2700-\u27bf]')
    return emoji_pattern.sub('', title).strip()

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

def extract_html_metadata(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    title = soup.title.get_text(strip=True) if soup.title else os.path.basename(file_path)
    keywords_tag = soup.find("meta", {"name": "keywords"})
    keywords = keywords_tag["content"] if keywords_tag else ""
    
    # Παίρνουμε το όνομα του αρχείου από το canonical ή το ίδιο το όνομα αρχείου
    canonical = soup.find("link", {"rel": "canonical"})
    href = canonical["href"].split("/")[-1] if canonical else os.path.basename(file_path)
    lang = soup.html.get("lang", "en") if soup.html else "en"
    
    date_obj = datetime.today()
    json_ld_tag = soup.find("script", {"type": "application/ld+json"})
    if json_ld_tag:
        try:
            data = json.loads(json_ld_tag.string)
            date_str = data.get("datePublished")
            if date_str:
                date_obj = datetime.fromisoformat(date_str.split('T')[0])
        except Exception:
            pass
    return title, keywords, href, lang, date_obj

def load_archive_soup(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Δεν βρέθηκε {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    section = soup.find("section", id="articles")
    if not section:
        raise RuntimeError(f"❌ Δεν βρέθηκε <section id='articles'> στο {path}")
    
    # Ευρετήριο: href -> το div container του
    existing = {}
    for div in section.find_all("div", class_="link-container"):
        a_tag = div.find("a", href=True)
        if a_tag:
            existing[a_tag["href"]] = div
            
    return soup, section, existing

# =========================
# MAIN PROCESS
# =========================
def run_update():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # 1. Φόρτωση Archives
    archives_data = {}
    for lang, path in ARCHIVES.items():
        soup, section, existing = load_archive_soup(path)
        archives_data[lang] = {"soup": soup, "section": section, "existing": existing, "path": path}

    # 2. ΚΑΘΑΡΙΣΜΟΣ ΟΡΦΑΝΩΝ (Διαγραφή αν το αρχείο δεν υπάρχει πια)
    log("🧹 Checking for orphan links...")
    for lang, data in archives_data.items():
        to_remove = []
        for href, div in data["existing"].items():
            # Μην διαγράφεις ποτέ τα index
            if "index" in href: continue
            
            path_in_root = os.path.join(ROOT_DIR, href)
            path_in_new = os.path.join(NEW_HTML_DIR, href)
            
            # Αν το αρχείο δεν υπάρχει πουθενά, διέγραψε το από το Archive
            if not os.path.exists(path_in_root) and not os.path.exists(path_in_new):
                div.decompose() # Αφαίρεση από το HTML tree
                to_remove.append(href)
        
        for r in to_remove:
            log(f"🗑️ Removed from {lang} archive: {r} (File not found)")
            del data["existing"][r]

    # 3. ΕΠΕΞΕΡΓΑΣΙΑ ΝΕΩΝ ΑΡΧΕΙΩΝ
    for file in os.listdir(NEW_HTML_DIR):
        if not file.endswith(".html") or "archives" in file or "template" in file:
            continue
        
        full_path = os.path.join(NEW_HTML_DIR, file)
        title, keywords, href, lang, date_obj = extract_html_metadata(full_path)
        
        if lang not in archives_data: continue
        
        data = archives_data[lang]
        if href in data["existing"]:
            log(f"⏭️ Skipping {file} (Already in archive)")
            continue

        # Δημιουργία νέου Container
        icon = extract_icon(title)
        display_title = clean_title(title)
        display_date = format_date(date_obj, lang)
        data_date = date_obj.strftime("%Y-%m-%d")

        new_div = BeautifulSoup(f'''
<div class="link-container" data-title="{display_title}" data-date="{data_date}" data-tags="{keywords}">
  <a href="{href}" target="_blank" class="link-button">
    <span class="icon">{icon}</span>{display_title}
  </a>
  <span class="pub-date">{display_date}</span>
</div>
''', "html.parser")

        data["section"].insert(0, new_div)
        log(f"✨ Added to {lang}: {display_title}")

    # 4. ΑΠΟΘΗΚΕΥΣΗ & ΜΕΤΑΦΟΡΑ
    if not args.dry_run:
        for lang, data in archives_data.items():
            with open(data["path"], "w", encoding="utf-8") as f:
                f.write(data["soup"].prettify())
            log(f"✅ Saved Archive ({lang})")

        # Μεταφορά στο Root
        for file in os.listdir(NEW_HTML_DIR):
            if file.endswith(".html") and "archives" not in file:
                src = os.path.join(NEW_HTML_DIR, file)
                dst = os.path.join(ROOT_DIR, file)
                shutil.move(src, dst)
        log("🚚 Files moved to Root folder.")

if __name__ == "__main__":
    run_update()
    log("🎯 Process Finished!")

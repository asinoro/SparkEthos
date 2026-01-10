import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
import locale
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEW_HTML_DIR = os.path.join(BASE_DIR, "New-html")

ARCHIVE_PAGES = {
    "el": "sparkethos-archives-el.html",
    "en": "sparkethos-archives-en.html",
}

def format_date(date_obj, lang):
    if lang == "el":
        locale.setlocale(locale.LC_TIME, "el_GR.UTF-8")
        return date_obj.strftime("%d %B %Y")
    else:
        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
        return date_obj.strftime("%B %d, %Y")

def default_icon(lang):
    return "🌍"  # default icon για νέα άρθρα

# -------------------------------
# 1. Φόρτωση archive pages
# -------------------------------
archive_soups = {}
existing_blocks = {"el": {}, "en": {}}

for lang, archive_file in ARCHIVE_PAGES.items():
    path = os.path.join(BASE_DIR, archive_file)
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Δεν βρέθηκε το {archive_file} στο root")

    # backup
    shutil.copy(path, path + ".bak")

    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    archive_soups[lang] = soup

    section = soup.find("section", id="articles")
    if not section:
        raise RuntimeError(f"❌ Δεν βρέθηκε <section id='articles'> στο {archive_file}")

    for div in section.find_all("div", class_="link-container"):
        a = div.find("a", href=True)
        if a:
            existing_blocks[lang][a["href"]] = div

# -------------------------------
# 2. Σκανάρισμα νέων άρθρων από New-html
# -------------------------------
if not os.path.exists(NEW_HTML_DIR):
    raise FileNotFoundError(f"❌ Ο φάκελος New-html δεν βρέθηκε")

for file in os.listdir(NEW_HTML_DIR):
    if not file.endswith(".html"):
        continue

    file_path = os.path.join(NEW_HTML_DIR, file)
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    lang = soup.html.get("lang", "en")
    if lang not in ARCHIVE_PAGES:
        continue

    title = soup.title.get_text(strip=True)

    keywords_tag = soup.find("meta", {"name": "keywords"})
    keywords = keywords_tag["content"] if keywords_tag else ""

    canonical = soup.find("link", {"rel": "canonical"})
    href = canonical["href"].split("/")[-1] if canonical else file

    json_ld = soup.find("script", {"type": "application/ld+json"})
    article_data = json.loads(json_ld.string)

    date_obj = datetime.fromisoformat(article_data["datePublished"])
    data_date = date_obj.strftime("%Y-%m-%d")
    display_date = format_date(date_obj, lang)

    section = archive_soups[lang].find("section", id="articles")

    # --------------------------------------------
    # Α) ΥΠΑΡΧΟΝ άρθρο → update metadata, χωρίς αλλαγή icon
    # --------------------------------------------
    if href in existing_blocks[lang]:
        block = existing_blocks[lang][href]
        block["data-title"] = title
        block["data-date"] = data_date
        block["data-tags"] = keywords

        pub_date = block.find("span", class_="pub-date")
        if pub_date:
            pub_date.string = display_date

        continue

    # --------------------------------------------
    # Β) ΝΕΟ άρθρο → προσθήκη με default icon μόνο αν δεν υπάρχει
    # --------------------------------------------
    new_block = BeautifulSoup(f'''
<div class="link-container"
     data-title="{title}"
     data-date="{data_date}"
     data-tags="{keywords}">
  <a href="{href}" target="_blank" class="link-button">
    <span class="icon">{default_icon(lang)}</span>{title}
  </a>
  <span class="pub-date">{display_date}</span>
</div>
''', "html.parser")

    # Εισαγωγή στο top του section
    section.insert(0, new_block)

    print(f"⚡ Νέο άρθρο προστέθηκε: {file}")

# -------------------------------
# 3. Αποθήκευση archive pages
# -------------------------------
for lang, archive_file in ARCHIVE_PAGES.items():
    save_path = os.path.join(BASE_DIR, archive_file)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(archive_soups[lang].prettify())

    print(f"✅ Ενημερώθηκε: {archive_file}")

print("🎯 Ολοκληρώθηκε: auto-icon + metadata sync (μόνο από New-html).")


import os
import json
import shutil
import locale
from datetime import datetime
from bs4 import BeautifulSoup

# =========================
# CONFIG
# =========================
DRY_RUN = False   # 🔁 True = δεν γράφει αρχεία | False = κανονική εγγραφή
DEFAULT_ICON = "🌍"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)   # SparkEthos root
NEW_HTML_DIR = SCRIPT_DIR                # τα νέα άρθρα είναι εδώ

ARCHIVE_PAGES = {
    "el": "sparkethos-archives-el.html",
    "en": "sparkethos-archives-en.html",
}

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
        # fallback αν δεν υπάρχουν locales
        return date_obj.strftime("%Y-%m-%d")

def log(msg):
    print(msg)

def smart_icon(title, keywords=""):
    text = f"{title} {keywords}".lower()

    ICON_MAP = {
        "ai": "🧠",
        "artificial intelligence": "🧠",
        "τεχνητή νοημοσύνη": "🧠",
        "ethic": "⚖️",
        "ηθική": "⚖️",
        "philosophy": "🎭",
        "φιλοσοφ": "🎭",
        "control": "🧯",
        "έλεγχος": "🧯",
        "paradox": "🧩",
        "παράδοξο": "🧩",
        "conscious": "🧬",
        "συνείδηση": "🧬",
        "security": "🟥",
        "Ασφάλεια": "🟥",
        "Πόλεμος": "🟥",
        "war": "🟥",
        "κυβερνοεπίθεση": "🟥",
        "cyberattack": "🟥",
        "future": "🚀",
        "μέλλον": "🚀",
        "logic": "🔹",
        "λογική": "🔹",
    }

    for key, icon in ICON_MAP.items():
        if key in text:
            return icon

    return "🌍"   # fallback

# =========================
# 1. ΦΟΡΤΩΣΗ ARCHIVES
# =========================
archive_soups = {}
existing_blocks = {"el": {}, "en": {}}

for lang, archive_file in ARCHIVE_PAGES.items():
    path = os.path.join(ROOT_DIR, archive_file)
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Λείπει το {archive_file}")

    if not DRY_RUN:
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

# =========================
# 2. ΣΚΑΝΑΡΙΣΜΑ ΝΕΩΝ HTML
# =========================
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
    if not json_ld:
        log(f"⚠️ Παράλειψη (δεν βρέθηκε JSON-LD): {file}")
        continue

    article_data = json.loads(json_ld.string)
    date_obj = datetime.fromisoformat(article_data["datePublished"])
    data_date = date_obj.strftime("%Y-%m-%d")
    display_date = format_date(date_obj, lang)

    section = archive_soups[lang].find("section", id="articles")

    # ---------------------------
    # Α) ΥΠΑΡΧΟΝ → update metadata
    # ---------------------------
    if href in existing_blocks[lang]:
        block = existing_blocks[lang][href]

        log(f"🔁 UPDATE metadata: {href}")

        if not DRY_RUN:
            block["data-title"] = title
            block["data-date"] = data_date
            block["data-tags"] = keywords

            pub_date = block.find("span", class_="pub-date")
            if pub_date:
                pub_date.string = display_date

        continue

    # ---------------------------
    # Β) ΝΕΟ → auto-icon
    # ---------------------------
    log(f"➕ NEW article: {href}")

    new_block = BeautifulSoup(f"""
<div class="link-container"
     data-title="{title}"
     data-date="{data_date}"
     data-tags="{keywords}">
  <a href="{href}" target="_blank" class="link-button">
    <span class="icon">{smart_icon(title, keywords)}</span>{title}
  </a>
  <span class="pub-date">{display_date}</span>
</div>
""", "html.parser")

    if not DRY_RUN:
        section.insert(0, new_block)

# =========================
# 3. ΑΠΟΘΗΚΕΥΣΗ
# =========================
for lang, archive_file in ARCHIVE_PAGES.items():
    path = os.path.join(ROOT_DIR, archive_file)

    if DRY_RUN:
        log(f"🧪 DRY-RUN: Δεν γράφτηκε το {archive_file}")
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(archive_soups[lang].prettify())
        log(f"✅ Ενημερώθηκε: {archive_file}")

log("🎯 Ολοκληρώθηκε (auto-icon + metadata sync)")

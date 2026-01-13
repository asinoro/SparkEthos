import os
import json
from datetime import date
from bs4 import BeautifulSoup

# Ρυθμίσεις
SITE = "https://asinoro.github.io/SparkEthos/"
SITEMAP_FILE = "sitemap.xml"

def extract_date_from_html(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        
        # Βρίσκουμε όλα τα ld+json (γιατί μπορεί να έχεις πάνω από ένα)
        json_ld_tags = soup.find_all("script", type="application/ld+json")
        
        for tag in json_ld_tags:
            try:
                # Καθαρισμός του κειμένου από τυχόν περίεργους χαρακτήρες ή κενά
                content = tag.string.strip()
                data = json.loads(content)
                
                # Έλεγχος αν το datePublished υπάρχει σε αυτό το tag
                if "datePublished" in data:
                    # Παίρνουμε μόνο το YYYY-MM-DD (αγνοούμε την ώρα αν υπάρχει)
                    return data["datePublished"].split('T')[0]
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ Σφάλμα ανάγνωσης στο {file_path}: {e}")
    
    # ΑΝ ΑΠΟΤΥΧΟΥΝ ΟΛΑ: 
    # Αν είναι η αρχική σελίδα, δώσε τη σταθερή ημερομηνία
    if "index" in file_path:
        return "2025-04-13"
        
    return date.today().isoformat()

def generate_sitemap():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Λίστα αρχείων (εξαιρούμε τα templates)
    files = [f for f in os.listdir(ROOT_DIR) if f.endswith(".html") and "template" not in f]
    
    articles_data = []
    for f in files:
        path = os.path.join(ROOT_DIR, f)
        # Παίρνουμε την ημερομηνία ΜΕΣΑ από το αρχείο
        pub_date = extract_date_from_html(path)
        articles_data.append((f, pub_date))

    # Ταξινόμηση: Τα νεότερα πάνω
    articles_data.sort(key=lambda x: x[1], reverse=True)

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for file_name, pub_date in articles_data:
        url = SITE + file_name
        priority = "1.00" if "index" in file_name else "0.80"
        if "archives" in file_name: priority = "0.70"

        xml += "  <url>\n"
        xml += f"    <loc>{url}</loc>\n"
        xml += f"    <lastmod>{pub_date}</lastmod>\n"
        xml += f"    <priority>{priority}</priority>\n"
        xml += "  </url>\n"

    xml += "</urlset>"

    sitemap_path = os.path.join(ROOT_DIR, SITEMAP_FILE)
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(xml)
    
    print(f"✅ Sitemap updated with internal dates! (Total: {len(articles_data)} URLs)")

if __name__ == "__main__":
    generate_sitemap()

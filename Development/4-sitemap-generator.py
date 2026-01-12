import os
from datetime import date

# Ρυθμίσεις
SITE = "https://asinoro.github.io/SparkEthos/"
SITEMAP_FILE = "sitemap.xml"

def generate_sitemap():
    # Σαρώνει τον τρέχοντα φάκελο για HTML αρχεία
    articles = [f for f in sorted(os.listdir('.')) if f.endswith(".html")]
    today = date.today().isoformat()

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for file in articles:
        url = SITE + file
        priority = "0.80"
        
        # Καθορισμός προτεραιότητας βάσει ονόματος αρχείου
        if "index" in file:
            priority = "1.00"
        elif "archives" in file:
            priority = "0.70"

        xml += "  <url>\n"
        xml += f"    <loc>{url}</loc>\n"
        xml += f"    <lastmod>{today}</lastmod>\n"
        xml += f"    <priority>{priority}</priority>\n"
        xml += "  </url>\n"

    xml += "</urlset>"

    try:
        with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
            f.write(xml)
        print(f"✅ Created/Updated Sitemap: {SITEMAP_FILE} ({len(articles)} URLs)")
    except Exception as e:
        print(f"❌ Error writing sitemap: {e}")

if __name__ == "__main__":
    generate_sitemap()

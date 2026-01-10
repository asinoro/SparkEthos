SITEMAP_FILE = "sitemap.xml"

def generate_sitemap():
    articles = [f for f in sorted(os.listdir()) if f.endswith(".html")]
    today = date.today().isoformat()

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for file in articles:
        url = SITE + file
        priority = "0.80"
        if "index" in file:
            priority = "1.00"
        elif "archives" in file:
            priority = "0.70"

        xml += f"  <url>\n"
        xml += f"    <loc>{url}</loc>\n"
        xml += f"    <lastmod>{today}</lastmod>\n"
        xml += f"    <priority>{priority}</priority>\n"
        xml += f"  </url>\n"

    xml += "</urlset>"

    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"✅ Created/Updated Sitemap: {SITEMAP_FILE}")

generate_sitemap()

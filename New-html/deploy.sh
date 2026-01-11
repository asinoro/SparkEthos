#!/bin/bash

# Αποθήκευση της διαδρομής του New-html φακέλου
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
ROOT_DIR=$(dirname "$SCRIPT_DIR")

echo "🚀 Starting SparkEthos Deployment Process..."

# 1. Δημιουργία των HTML από τα TXT (εντός New-html)
echo "🎨 1/3 Generating Articles..."
python3 "$SCRIPT_DIR/2-generate_articles-el-en-text-to-html.py"

# 2. Ενημέρωση Archives, JSON-LD και Μεταφορά Αρχείων στο Root
echo "📚 2/3 Updating Archives & Moving Files..."
python3 "$SCRIPT_DIR/3-update_archives-and-jsonld.py"

# 3. Ενημέρωση Sitemap (βρίσκεται στο SparkEthos Root)
echo "🗺️ 3/3 Updating Sitemap..."
python3 "$ROOT_DIR/4-sitemap-generator.py"

echo "------------------------------------------"
echo "✅ All tasks completed successfully!"
echo "📂 Files moved to: $ROOT_DIR"
echo "📝 Ready for: git add . && git commit -m 'New articles' && git push"

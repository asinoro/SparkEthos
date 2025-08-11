const fs = require('fs');

const templatePath = 'viewer-template.html';
const outputPath = 'viewer.html';
const jsonPath = 'sparkethos-en-el.json';

try {
    const templateHtml = fs.readFileSync(templatePath, 'utf-8');
    const jsonData = fs.readFileSync(jsonPath, 'utf-8');

    const embeddedJson = `
<script id="guide-data" type="application/json">
${jsonData}
</script>`;

    const finalHtml = templateHtml.replace('<!-- JSON_PLACEHOLDER -->', embeddedJson);

    fs.writeFileSync(outputPath, finalHtml);
    console.log('✅ viewer.html δημιουργήθηκε με ενσωματωμένο JSON!');
} catch (err) {
    console.error('❌ Σφάλμα κατά την παραγωγή του viewer.html:', err);
}

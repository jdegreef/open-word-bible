// Render docs/overview.html to docs/open-word-bible-overview.pdf.
// Greek placeholders {{GREEK:REF:a-b}} are filled from data/grc/, never typed.
// Usage: NODE_PATH=$(npm root -g) node scripts/build_overview.js
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
let html = fs.readFileSync(path.join(root, 'docs/overview.html'), 'utf8');
html = html.replace(/\{\{GREEK:([A-Z0-9]+)\.(\d+)\.(\d+):(\d+)-(\d+)\}\}/g, (_, book, ch, v, a, b) => {
  const data = JSON.parse(fs.readFileSync(path.join(root, `data/grc/${book}.${ch}.json`), 'utf8'));
  const words = data.verses[`${book}.${ch}.${v}`].filter(t => t.position >= +a && t.position <= +b);
  return words.map(t => t.text).join(' ');
});

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: 'load' });
  await page.pdf({
    path: path.join(root, 'docs/open-word-bible-overview.pdf'),
    format: 'Letter',
    preferCSSPageSize: true,
    printBackground: false,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font:8px Helvetica,Arial,sans-serif;text-align:center;color:#000">Open Word Bible · Project overview · <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
  });
  await browser.close();
})();

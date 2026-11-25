// Render report/executive_summary.html to PDF with the pre-installed Chromium (Playwright).
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.resolve('report/executive_summary.html'), { waitUntil: 'load' });
  await p.pdf({ path: 'report/executive_summary.pdf', format: 'A4', printBackground: true,
                margin: { top: '0mm', bottom: '0mm', left: '0mm', right: '0mm' }, preferCSSPageSize: true });
  await b.close();
})();

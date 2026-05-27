const fs = require('fs');
const html = fs.readFileSync('俄旅定制报价工具.html', 'utf-8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
const js = m[1];

// Write to temp file and use node --check
fs.writeFileSync('/tmp/adu_check.js', js);

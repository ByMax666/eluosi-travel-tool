const fs = require('fs');
const html = fs.readFileSync('俄旅定制报价工具.html', 'utf-8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
const js = m[1];

// Look for unclosed template literals
let inTemplate = false;
let templateStart = 0;
for (let i = 0; i < js.length; i++) {
  const ch = js[i];
  if (ch === '`') {
    if (!inTemplate) {
      inTemplate = true;
      templateStart = i;
    } else if (i === 0 || js[i-1] !== '\\') {
      inTemplate = false;
    }
  }
}
if (inTemplate) {
  console.log('UNCLOSED TEMPLATE at', templateStart);
  console.log(js.substring(templateStart, templateStart + 300));
}

// Count all types of brackets
const opens = { '{': 0, '(': 0, '[': 0 };
const closes = { '}': 0, ')': 0, ']': 0 };
for (const ch of js) {
  if (ch in opens) opens[ch]++;
  if (ch in closes) closes[ch]++;
}
for (const k of Object.keys(opens)) {
  const diff = opens[k] - closes[k === '{' ? '}' : k === '(' ? ')' : ']'];
  if (diff !== 0) console.log(`${k}: ${opens[k]} vs ${closes[k === '{' ? '}' : k === '(' ? ')' : ']']}, diff=${diff}`);
}

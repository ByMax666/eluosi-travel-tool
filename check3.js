const fs = require('fs');
const html = fs.readFileSync('俄旅定制报价工具.html', 'utf-8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
const js = m[1];
// Last 300 chars
console.log('LAST 300:');
console.log(js.substring(js.length - 300));
console.log('---');
// Check if the script tag is properly closed
const endIdx = html.lastIndexOf('</script>');
const startIdx = html.lastIndexOf('<script>', endIdx);
console.log(`Script end: ${endIdx}, content end: ${startIdx + '<script>'.length + js.length}`);
console.log(`HTML ends at: ${html.length}`);
console.log(`Expected end: ${startIdx + 7 + js.length + 9}`);

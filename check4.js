const fs = require('fs');
const html = fs.readFileSync('俄旅定制报价工具.html', 'utf-8');

// Find ALL script closing tags
let idx = -1;
let count = 0;
while ((idx = html.indexOf('</script>', idx + 1)) !== -1) {
  count++;
  console.log(`</script> #${count} at position ${idx}`);
  // Show context
  console.log(`  Context: ${html.substring(Math.max(0, idx-30), idx+30)}`);
}

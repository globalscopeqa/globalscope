// usage: node render-image.js <cover|thumb> <config.json> <out.png>
//   cover -> 1080x1080 (1:1)   thumb -> 1080x1920 (9:16 YouTube Short)
// Paths inside the config (bg, logo) may be relative to the config file.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { pathToFileURL } = require('url');
const [mode, cfgPath, out] = process.argv.slice(2);
if (!['cover', 'thumb'].includes(mode) || !cfgPath || !out) { console.error('usage: render-image.js <cover|thumb> <config.json> <out.png>'); process.exit(1); }
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const repoRoot = path.resolve(__dirname, '../../../..');
const abs = p => pathToFileURL(path.resolve(path.dirname(path.resolve(cfgPath)), p)).href;
cfg.bg = abs(cfg.bg);
cfg.logo = cfg.logo ? abs(cfg.logo) : pathToFileURL(path.join(repoRoot, 'globalscope-logo.png')).href;
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage();
  p.on('pageerror', e => console.error('page error:', e.message));
  await p.goto(pathToFileURL(path.join(__dirname, 'images.html')).href);
  const d = await p.evaluate(([m, c]) => window.draw(m, c), [mode, cfg]);
  fs.writeFileSync(out, Buffer.from(d.split(',')[1], 'base64'));
  await b.close();
  console.log(`wrote ${out} (${mode === 'cover' ? '1080x1080' : '1080x1920'})`);
})();

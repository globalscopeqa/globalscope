const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const dir = process.argv[2];
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] }); const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('file://' + path.join(dir, 'render.html'));
  await p.evaluate(tl => window.setup(tl), JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'))));
  const png = await p.evaluate(() => {
    const S = 720; cv.width = 1080; cv.height = 1080; const K = 1.5, o = ctx.setTransform.bind(ctx);
    ctx.setTransform = (a, b, c, d, e, f) => o(a * K, b * K, c * K, d * K, e * K, f * K);
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
    background(20);
    const rg = ctx.createRadialGradient(360, 560, 30, 360, 560, 420); rg.addColorStop(0, 'rgba(63,216,255,0.16)'); rg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = rg; ctx.fillRect(0, 0, S, S);
    // chip + logo
    box(36, 52, 236, 40, 'rgba(63,216,255,0.6)', 'rgba(8,20,34,0.9)', 20, 1.5);
    text('NETWORK 101 · EP 01', 154, 73, 15, C.cyan, MONO, 700, 'center', 2);
    box(S - 196, 36, 160, 100, '#fff', '#ffffff', 14, 1);
    const lw = 136, lh = lw * logo.height / logo.width; ctx.drawImage(logo, S - 184, 36 + (100 - lh) / 2, lw, lh);
    // headline
    text('HOW DOES THE', 36, 205, 56, C.white, SANS, 800, 'left', -1);
    text('INTERNET REACH', 36, 267, 56, C.white, SANS, 800, 'left', -1);
    glow(C.cyan, 28); text('YOUR DESK?', 36, 338, 66, C.cyan, SANS, 800, 'left', -1); noGlow();
    ctx.fillStyle = C.brand; ctx.fillRect(38, 386, 80, 5);
    text('From ISP to laptop, in 60 seconds', 36, 422, 22, 'rgba(255,255,255,0.75)', SANS, 500, 'left');
    // horizontal path
    const N = [['isp', 'ISP'], ['fw', 'FIREWALL'], ['core', 'CORE'], ['access', 'ACCESS'], ['wifi', 'WI-FI'], ['device', 'LAPTOP']];
    const y = 535, x0 = 78, x1 = 642, st = (x1 - x0) / 5;
    poly([[x0, y], [x1, y]], 'rgba(63,216,255,0.35)', 8); glow(C.cyan, 16); poly([[x0, y], [x1, y]], C.cyan, 3); noGlow();
    [0.17, 0.5, 0.83].forEach((u, k) => { for (let i = 0; i < 5; i++) dot(x0 + st * (i + u), y, 3.5, '#e8fbff', 14); });
    N.forEach((n, i) => {
      const x = x0 + st * i; glow(C.cyan, 22);
      ctx.beginPath(); ctx.arc(x, y, 34, 0, 7); ctx.fillStyle = 'rgba(10,40,64,1)'; ctx.fill(); ctx.strokeStyle = C.cyan; ctx.lineWidth = 2.5; ctx.stroke(); noGlow();
      icon(n[0], x, y, 34, '#d9f6ff');
      text(n[1], x, y + 58, 14, C.white, MONO, 700, 'center', 1.2);
    });
    text('globalscope.qa', 360, 672, 18, 'rgba(255,255,255,0.7)', MONO, 600, 'center', 3);
    const v = ctx.createRadialGradient(360, 360, 300, 360, 360, 560); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.5)'); ctx.fillStyle = v; ctx.fillRect(0, 0, S, S);
    return cv.toDataURL('image/png');
  });
  fs.writeFileSync(path.join(dir, 'globalscope-isp-to-laptop-cover-1x1.png'), Buffer.from(png.split(',')[1], 'base64'));
  await b.close();
})();

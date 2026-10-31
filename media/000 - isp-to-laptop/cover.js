const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const dir = process.argv[2];
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] }); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('file://' + path.join(dir, 'render.html'));
  await p.evaluate(tl => window.setup(tl), JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'))));
  const png = await p.evaluate(() => {
    cv.width = 1080; cv.height = 1920; const K = 1.5, o = ctx.setTransform.bind(ctx);
    ctx.setTransform = (a, b, c, d, e, f) => o(a * K, b * K, c * K, d * K, e * K, f * K);
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
    background(20);
    const rg = ctx.createRadialGradient(360, 820, 40, 360, 820, 520); rg.addColorStop(0, 'rgba(63,216,255,0.14)'); rg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
    // path overview, fully lit
    ctx.save(); ctx.translate(360, 0); ctx.translate(0, 500); ctx.scale(0.8, 0.8); ctx.translate(-360, 0);
    SCENES[6](7.3, 8); ctx.restore(); noGlow();
    // top fade for headline legibility
    const g = ctx.createLinearGradient(0, 0, 0, 640); g.addColorStop(0, 'rgba(4,7,13,0.95)'); g.addColorStop(0.8, 'rgba(4,7,13,0.75)'); g.addColorStop(1, 'rgba(4,7,13,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, 640);
    // chip + logo
    box(36, 52, 236, 40, 'rgba(63,216,255,0.6)', 'rgba(8,20,34,0.9)', 20, 1.5);
    text('NETWORK 101 · EP 01', 154, 73, 15, C.cyan, MONO, 700, 'center', 2);
    box(W - 196, 36, 160, 100, '#fff', '#ffffff', 14, 1);
    const lw = 136, lh = lw * logo.height / logo.width; ctx.drawImage(logo, W - 184, 36 + (100 - lh) / 2, lw, lh);
    // headline
    text('HOW DOES THE', 36, 230, 62, C.white, SANS, 800, 'left', -1);
    text('INTERNET REACH', 36, 302, 62, C.white, SANS, 800, 'left', -1);
    glow(C.cyan, 30); text('YOUR DESK?', 36, 380, 74, C.cyan, SANS, 800, 'left', -1); noGlow();
    ctx.fillStyle = C.brand; ctx.fillRect(38, 436, 90, 6);
    text('From ISP to laptop, in 60 seconds', 36, 482, 26, 'rgba(255,255,255,0.75)', SANS, 500, 'left');
    // footer
    const fg = ctx.createLinearGradient(0, 1185, 0, H); fg.addColorStop(0, 'rgba(4,7,13,0)'); fg.addColorStop(1, 'rgba(4,7,13,0.95)'); ctx.fillStyle = fg; ctx.fillRect(0, 1185, W, 95);
    text('globalscope.qa', 360, 1228, 20, 'rgba(255,255,255,0.7)', MONO, 600, 'center', 3);
    const v = ctx.createRadialGradient(360, 640, 420, 360, 640, 900); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.5)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
    return cv.toDataURL('image/png');
  });
  fs.writeFileSync(path.join(dir, 'globalscope-isp-to-laptop-cover.png'), Buffer.from(png.split(',')[1], 'base64'));
  await b.close();
})();

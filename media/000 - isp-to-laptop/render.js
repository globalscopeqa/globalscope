const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { spawn } = require('child_process');
const dir = process.argv[2], mode = process.argv[3];
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] }); const p = await b.newPage({ viewport: { width: 720, height: 1280 } });
  p.on('console', m => console.log('page:', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('file://' + path.join(dir, 'render.html'));
  const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'))); await p.evaluate(tl => window.setup(tl), tl);
  if (mode === 'preview') {
    for (const t of process.argv.slice(4).map(Number)) { const d = await p.evaluate(t => window.frame(t), t); fs.writeFileSync(path.join(dir, `prev_${t}.jpg`), Buffer.from(d.split(',')[1], 'base64')); }
  } else {
    const fps = 30, n = Math.ceil(tl.total * fps);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-i', path.join(dir, 'mix.wav'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', mode], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = 0; f < n; f++) {
      const d = await p.evaluate(t => window.frame(t), f / fps);
      if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 300 === 0) console.log('frame', f, '/', n);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await b.close();
})();

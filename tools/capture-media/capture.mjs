// SPDX-License-Identifier: GPL-3.0-or-later
//
// Re-runnable media capture for the Cyber Fidget documentation.
//
// Drives the studio (signed out) in a headless browser and writes PNG
// screenshots, short looping WebM clips and a poster PNG per clip into
// docs/assets/media/. Each capture is a named "scene" (a function below), so
// one scene can be re-run when the studio UI changes:
//
//   node capture.mjs <scene> [<scene> ...]   run the named scenes
//   node capture.mjs all                     run every scene
//   node capture.mjs --list                  list the scenes
//
// Options: --base <url>   studio site (default http://localhost:8000)
//          --out <dir>    output folder (default ../../docs/assets/media)
//          --headed       show the browser
//
// See README.md for prerequisites.

import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DOCS_ROOT = path.resolve(HERE, '..', '..', 'docs');

// ---------------------------------------------------------------------------
// Setup: arguments, Playwright, ffmpeg
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const opts = { base: 'http://localhost:8000', out: path.join(DOCS_ROOT, 'assets', 'media'), headed: false, list: false, scenes: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--base') opts.base = argv[++i];
    else if (a === '--out') opts.out = path.resolve(argv[++i]);
    else if (a === '--headed') opts.headed = true;
    else if (a === '--list') opts.list = true;
    else if (a.startsWith('--')) throw new Error('Unknown option ' + a);
    else opts.scenes.push(a);
  }
  opts.base = opts.base.replace(/\/+$/, '');
  return opts;
}

// Playwright is found as a normal package (npm install in this folder), or
// in the node_modules folder of the directory named by PLAYWRIGHT_DIR.
async function loadPlaywright() {
  try {
    return await import('playwright');
  } catch (e) {
    if (!process.env.PLAYWRIGHT_DIR) throw new Error('Playwright not found. Run "npm install" in this folder, or set PLAYWRIGHT_DIR to a folder whose node_modules contains it.');
  }
  const req = createRequire(path.resolve(process.env.PLAYWRIGHT_DIR) + path.sep);
  return req('playwright');
}

// Cropping and trimming use the small ffmpeg build that Playwright installs
// next to its browsers. FFMPEG can point at any other ffmpeg that has the
// libvpx encoder. Without ffmpeg, clips are kept as recorded (not cropped).
function findFfmpeg() {
  if (process.env.FFMPEG) return process.env.FFMPEG;
  const roots = [];
  if (process.env.PLAYWRIGHT_BROWSERS_PATH && process.env.PLAYWRIGHT_BROWSERS_PATH !== '0') roots.push(process.env.PLAYWRIGHT_BROWSERS_PATH);
  if (process.env.LOCALAPPDATA) roots.push(path.join(process.env.LOCALAPPDATA, 'ms-playwright'));
  roots.push(path.join(os.homedir(), '.cache', 'ms-playwright'));
  roots.push(path.join(os.homedir(), 'Library', 'Caches', 'ms-playwright'));
  for (const root of roots) {
    if (!fs.existsSync(root)) continue;
    for (const dir of fs.readdirSync(root).filter((d) => d.startsWith('ffmpeg-')).sort().reverse()) {
      for (const f of fs.readdirSync(path.join(root, dir))) {
        if (/^ffmpeg(-[a-z0-9]+)?(\.exe)?$/.test(f)) return path.join(root, dir, f);
      }
    }
  }
  return null;
}

const FFMPEG = findFfmpeg();

// ---------------------------------------------------------------------------
// Helpers shared by the scenes
// ---------------------------------------------------------------------------

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const VIEW = { width: 1280, height: 800 };

// Whole-column region on the left: tabs, workspace and code area.
const WORKSPACE = { x: 0, y: 112, width: 940, height: 668 };
// The emulator device only.
const DEVICE = { x: 920, y: 200, width: 300, height: 400 };
// The whole emulator column: device, status line and REBUILD box.
const EMU_COLUMN = { x: 862, y: 160, width: 418, height: 620 };

// A cursor dot and click ring, so clips that show a click path are readable
// (headless video does not draw the mouse).
const CURSOR_SCRIPT = `
(() => {
  const add = () => {
    if (document.getElementById('cf-capture-cursor')) return;
    const dot = document.createElement('div');
    dot.id = 'cf-capture-cursor';
    dot.style.cssText = 'position:fixed;left:0;top:0;width:18px;height:18px;margin:-9px 0 0 -9px;border-radius:50%;background:rgba(255,200,0,.85);border:2px solid #fff;box-shadow:0 0 6px #000;z-index:2147483647;pointer-events:none;transition:transform .08s;';
    document.documentElement.appendChild(dot);
    addEventListener('mousemove', (e) => { dot.style.left = e.clientX + 'px'; dot.style.top = e.clientY + 'px'; }, true);
    addEventListener('mousedown', () => { dot.style.transform = 'scale(.6)'; }, true);
    addEventListener('mouseup', () => { dot.style.transform = 'scale(1)'; }, true);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', add); else add();
})();
`;

function even(n) { return Math.round(n / 2) * 2; }

class Recorder {
  constructor(runner, name) {
    this.runner = runner;
    this.name = name;
  }

  async open({ cursor = true } = {}) {
    this.dir = fs.mkdtempSync(path.join(os.tmpdir(), 'cf-capture-'));
    this.context = await this.runner.browser.newContext({
      viewport: VIEW,
      deviceScaleFactor: 1,
      permissions: ['clipboard-read', 'clipboard-write'],
      recordVideo: { dir: this.dir, size: VIEW },
    });
    if (cursor) await this.context.addInitScript(CURSOR_SCRIPT);
    this.t0 = Date.now();
    this.page = await this.context.newPage();
    this.page.on('pageerror', (e) => console.log('  page error: ' + e.message));
    return this.page;
  }

  // Seconds since the page was created (the video's clock).
  now() { return (Date.now() - this.t0) / 1000; }

  // Close the recording and write <name>.webm (cropped to region, trimmed to
  // [from, to]) plus <name>.png, the poster frame at posterAt seconds in.
  async finish({ from, to, region, posterAt = 0.3, fps = 20, bitrate = '900k' }) {
    await this.context.close();
    const raw = await this.page.video().path();
    const outWebm = path.join(this.runner.out, this.name + '.webm');
    const outPng = path.join(this.runner.out, this.name + '.png');
    if (!FFMPEG) {
      fs.copyFileSync(raw, outWebm);
      console.log('  no ffmpeg found: kept the raw recording, not cropped or trimmed; no poster written');
    } else {
      const vf = [];
      if (region) vf.push(`crop=${even(region.width)}:${even(region.height)}:${even(region.x)}:${even(region.y)}`);
      const run = (args) => {
        const r = spawnSync(FFMPEG, ['-hide_banner', '-loglevel', 'error', '-y', ...args], { encoding: 'utf8' });
        if (r.status !== 0) throw new Error('ffmpeg failed: ' + r.stderr);
      };
      run(['-ss', String(Math.max(0, from)), '-t', String(to - from), '-i', raw, '-vf', vf.join(','), '-r', String(fps),
        '-c:v', 'libvpx', '-b:v', bitrate, '-crf', '10', '-an', '-auto-alt-ref', '0', outWebm]);
      run(['-ss', String(posterAt), '-i', outWebm, '-frames:v', '1', outPng]);
    }
    fs.rmSync(this.dir, { recursive: true, force: true });
    const kb = Math.round(fs.statSync(outWebm).size / 1024);
    console.log(`  wrote ${this.name}.webm (${kb} KB, ${(to - from).toFixed(1)} s) and ${this.name}.png`);
  }
}

class Runner {
  constructor(browser, base, out) {
    this.browser = browser;
    this.base = base;
    this.out = out;
  }

  recorder(name) { return new Recorder(this, name); }

  // A plain (not recorded) page, for screenshot-only scenes.
  async plainPage() {
    const context = await this.browser.newContext({ viewport: VIEW, deviceScaleFactor: 1, permissions: ['clipboard-read', 'clipboard-write'] });
    const page = await context.newPage();
    page.on('pageerror', (e) => console.log('  page error: ' + e.message));
    page.__context = context;
    return page;
  }

  // Screenshot to <out>/<name>.png, optionally cropped to clip.
  async shot(page, name, clip) {
    const file = path.join(this.out, name + '.png');
    // Hide the capture cursor so it does not appear in stills.
    await page.evaluate(() => { const c = document.getElementById('cf-capture-cursor'); if (c) c.style.visibility = 'hidden'; });
    await page.screenshot({ path: file, clip: clip || undefined });
    await page.evaluate(() => { const c = document.getElementById('cf-capture-cursor'); if (c) c.style.visibility = 'visible'; });
    console.log(`  wrote ${name}.png (${Math.round(fs.statSync(file).size / 1024)} KB)`);
  }
}

// Open the studio and make a blank-template app with the given App Name.
// Exact labels (verified in the studio source): "Create an app",
// "Code from Blank Template", App Name field, "Create".
async function newBlankApp(page, base, appName) {
  await page.goto(base + '/create/');
  await page.getByText('Create an app').first().waitFor();
  await sleep(1200);
  await page.getByText('Create an app').first().click();
  await page.getByRole('button', { name: /Code from Blank Template/ }).click();
  await page.locator('#builder-project-name').fill(appName);
  await page.getByRole('button', { name: 'Create', exact: true }).click();
  await page.locator('.ace_editor:visible').first().waitFor();
  await sleep(1500);
}

// Replace the contents of the visible code editor (the .cpp file).
async function setCode(page, code) {
  await page.evaluate((c) => {
    const el = [...document.querySelectorAll('.ace_editor')].find((e) => e.offsetParent);
    window.ace.edit(el).setValue(c, -1);
  }, code);
  await sleep(300);
}

// The final full listing of a docs page: the first cpp block after the
// "check-examples: final" marker.
function finalListing(docsRelPath) {
  const md = fs.readFileSync(path.join(DOCS_ROOT, docsRelPath), 'utf8').replace(/\r\n/g, '\n');
  const at = md.indexOf('<!-- check-examples: final -->');
  if (at < 0) throw new Error('No "check-examples: final" marker in ' + docsRelPath);
  const m = md.slice(at).match(/```cpp\n([\s\S]*?)\n```/);
  if (!m) throw new Error('No cpp block after the final marker in ' + docsRelPath);
  return m[1];
}

// A fenced cpp block of a docs page, by index among all cpp blocks that
// contain `needle`. Blocks written as insert-fragments are joined by
// assembleFragments().
function docsBlock(docsRelPath, needle) {
  const md = fs.readFileSync(path.join(DOCS_ROOT, docsRelPath), 'utf8').replace(/\r\n/g, '\n');
  for (const m of md.matchAll(/```cpp\n([\s\S]*?)\n```/g)) {
    if (m[1].includes(needle)) return m[1];
  }
  throw new Error('No cpp block containing ' + JSON.stringify(needle) + ' in ' + docsRelPath);
}

// Put a docs fragment (placement comments "Paste/Insert at the top of the
// file ...", "inside begin() ...", "inside update() ...") into the blank
// template for an app whose code name is `name`. Mirrors how a reader does it.
function assembleFragments(template, fragment) {
  const sections = { top: '', begin: '', update: '', end: '' };
  let cur = null;
  for (const line of fragment.split('\n')) {
    const m = line.match(/^\/\/ (?:Paste|Insert) (at the top of the file|inside begin\(\)|inside update\(\)|inside end\(\))/);
    if (m) {
      cur = { 'at the top of the file': 'top', 'inside begin()': 'begin', 'inside update()': 'update', 'inside end()': 'end' }[m[1]];
      continue;
    }
    if (cur) sections[cur] += line + '\n';
  }
  let code = template;
  const includeEnd = code.indexOf('\n\n', code.lastIndexOf('#include')) + 1;
  code = code.slice(0, includeEnd) + sections.top + code.slice(includeEnd);
  code = code.replace('    setColorsOff();\n}', '    setColorsOff();\n' + indent(sections.begin) + '}');
  code = code.replace('    display.display();\n}', indent(sections.update) + '    display.display();\n}');
  if (sections.end) code = code.replace('    unregisterButtonCallbacks();\n    setColorsOff();', indent(sections.end) + '    unregisterButtonCallbacks();\n    setColorsOff();');
  return code;
}

function indent(text) {
  return text.split('\n').map((l) => (l ? '    ' + l : l)).join('\n');
}

async function readEditorCode(page) {
  return page.evaluate(() => {
    const el = [...document.querySelectorAll('.ace_editor')].find((e) => e.offsetParent);
    return window.ace.edit(el).getValue();
  });
}

// Click REBUILD & RUN (the welcome button of the first build) and wait for
// the emulator to say it is running.
async function rebuildAndRun(page) {
  await page.getByRole('button', { name: 'REBUILD & RUN' }).click();
  await page.waitForFunction(() => /running your app/i.test(document.getElementById('builder-emulator-status')?.innerText || ''), null, { timeout: 120000 });
}

// Move the cursor smoothly (so the clip shows a path, not a jump).
async function glide(page, x, y, steps = 12) {
  await page.mouse.move(x, y, { steps });
}

async function clickCentre(page, locator, steps = 14) {
  const b = await locator.boundingBox();
  await glide(page, b.x + b.width / 2, b.y + b.height / 2, steps);
  await sleep(150);
  await page.mouse.down();
  await sleep(70);
  await page.mouse.up();
}

// Drive the emulator's slider with the mouse: press on the slider, then move
// the pointer up (value 100) or down (value 0) while the button is held.
async function sliderGrab(page, value) {
  const b = await page.locator('.cf-device-sliderzone').boundingBox();
  await page.mouse.move(b.x + b.width / 2, b.y + (1 - value / 100) * b.height);
  await page.mouse.down();
}

async function sliderTo(page, value, steps = 6) {
  const b = await page.locator('.cf-device-sliderzone').boundingBox();
  await page.mouse.move(b.x + b.width / 2, b.y + (1 - value / 100) * b.height, { steps });
}

// ---------------------------------------------------------------------------
// Scenes
// ---------------------------------------------------------------------------

const scenes = {};

// 1. Make a new sprite: Add art > Draw a new sprite > name it > draw > code.
scenes['new-sprite'] = async (r) => {
  const rec = r.recorder('new-sprite');
  const page = await rec.open();
  await newBlankApp(page, r.base, 'Hello');
  await sleep(600);
  const start = rec.now();

  await clickCentre(page, page.getByRole('button', { name: 'Add art' }));
  await sleep(900);
  await r.shot(page, 'new-sprite-add-art-menu', { x: 190, y: 112, width: 310, height: 290 });
  await clickCentre(page, page.getByText('Draw a new sprite'));
  await sleep(700);
  const name = page.locator('#art-new-sprite-name');
  await name.press('Control+A');
  await name.pressSequentially('Ball', { delay: 140 });
  await sleep(500);
  await r.shot(page, 'new-sprite-dialog', { x: 370, y: 250, width: 540, height: 300 });
  await clickCentre(page, page.getByRole('button', { name: 'Create', exact: true }));
  await page.locator('#pixel-grid').waitFor();
  await sleep(1000);

  // Draw a ball: an outline, then fill it.
  const grid = await page.locator('#pixel-grid').boundingBox();
  const cx = grid.x + grid.width / 2;
  const cy = grid.y + grid.height / 2;
  const radius = 30;
  await glide(page, cx + radius, cy, 8);
  await page.mouse.down();
  for (let a = 0; a <= 360; a += 8) {
    await page.mouse.move(cx + radius * Math.cos((a * Math.PI) / 180), cy + radius * Math.sin((a * Math.PI) / 180));
    await sleep(12);
  }
  await page.mouse.up();
  await sleep(300);
  await clickCentre(page, page.getByRole('button', { name: /^fill/i }).first());
  await glide(page, cx, cy, 6);
  await page.mouse.click(cx, cy);
  await sleep(900);
  await r.shot(page, 'new-sprite-drawn', WORKSPACE);

  // Back to the code.
  await clickCentre(page, page.locator('.activity-button[data-panel="ide"]'));
  await sleep(1200);
  const end = rec.now();
  await rec.finish({ from: start, to: end, region: WORKSPACE, posterAt: 0.2 });
};

// 2. Free starters: find a sprite, scroll to Copy as C++, copy, paste.
scenes['free-starters-copy'] = async (r) => {
  const rec = r.recorder('free-starters-copy');
  const page = await rec.open();
  await newBlankApp(page, r.base, 'Hello');
  await sleep(600);
  const start = rec.now();

  await clickCentre(page, page.getByRole('button', { name: /^All files/ }));
  await sleep(700);
  await clickCentre(page, page.getByRole('button', { name: 'Free starters', exact: true }));
  await page.locator('.sprite-grid > *').first().waitFor();
  await sleep(1200);
  await r.shot(page, 'free-starters-tab', WORKSPACE);

  // "Starter Sprites" is the collapsible heading inside this tab; search.
  const search = page.locator('#sprite-search');
  await clickCentre(page, search);
  await search.pressSequentially('heart', { delay: 140 });
  await sleep(900);
  await clickCentre(page, page.locator('.sprite-grid > *').first().getByRole('button', { name: /preview/i }));
  await sleep(800);

  // The Copy as C++ button is below the visible part of the panel: scroll.
  const popover = page.locator('.cf-all-files');
  const pb = await popover.boundingBox();
  await glide(page, pb.x + pb.width / 2, pb.y + pb.height / 2, 6);
  for (let i = 0; i < 6; i++) {
    await page.mouse.wheel(0, 90);
    await sleep(160);
  }
  await sleep(500);
  const copy = page.locator('#sprite-copy-cpp');
  await copy.scrollIntoViewIfNeeded();
  await sleep(500);
  await r.shot(page, 'free-starters-copy-as-cpp', WORKSPACE);
  await clickCentre(page, copy);
  await sleep(900);
  const close = page.getByRole('button', { name: 'Close', exact: true }).first();
  if (await close.isVisible()) await clickCentre(page, close);
  await sleep(500);

  // Paste it into the code, under the #include lines.
  await page.evaluate(() => {
    const el = [...document.querySelectorAll('.ace_editor')].find((e) => e.offsetParent);
    const ed = window.ace.edit(el);
    ed.gotoLine(5, 0);
    ed.focus();
  });
  await sleep(300);
  await page.keyboard.press('Control+V');
  await sleep(1500);
  await r.shot(page, 'free-starters-pasted', WORKSPACE);
  const end = rec.now();
  await rec.finish({ from: start, to: end, region: WORKSPACE, posterAt: 0.2 });
};

// 3. Where art comes in from a file (screenshots only).
scenes['add-art-from-file'] = async (r) => {
  const page = await r.plainPage();
  await newBlankApp(page, r.base, 'Hello');

  // The Add art menu, on the code tab.
  await page.getByRole('button', { name: 'Add art' }).click();
  await sleep(700);
  await r.shot(page, 'add-art-menu', { x: 190, y: 112, width: 310, height: 290 });
  await page.getByRole('button', { name: 'Add art' }).click();
  await sleep(400);

  // All files > In this project: Import from a file at the bottom.
  await page.getByRole('button', { name: /^All files/ }).click();
  await sleep(700);
  await r.shot(page, 'add-art-all-files', WORKSPACE);

  // Free starters > Starter Sprites > Upload your own.
  await page.getByRole('button', { name: 'Free starters', exact: true }).click();
  await page.locator('.sprite-grid > *').first().waitFor();
  await sleep(800);
  await page.getByText('Upload your own').click();
  await sleep(700);
  await r.shot(page, 'add-art-upload-your-own', WORKSPACE);
  await page.__context.close();

  // The 2D tab of a project with no art: IMPORT A FILE sits beside DRAW A SPRITE.
  const page3 = await r.plainPage();
  await newBlankApp(page3, r.base, 'Hello');
  await page3.locator('.activity-button[data-panel="pixel"]').click();
  await sleep(1200);
  await r.shot(page3, 'add-art-2d-no-art', WORKSPACE);
  await page3.__context.close();

  // With a sprite open: the Sprite file menu has Add from file.
  const page2 = await r.plainPage();
  await newBlankApp(page2, r.base, 'Hello');
  await page2.getByRole('button', { name: 'Add art' }).click();
  await page2.getByText('Draw a new sprite').click();
  await page2.locator('#art-new-sprite-name').fill('Ball');
  await page2.getByRole('button', { name: 'Create', exact: true }).click();
  await page2.locator('#pixel-grid').waitFor();
  await sleep(1200);
  await page2.locator('#art-sprite-file-button').click();
  await sleep(700);
  await r.shot(page2, 'add-art-sprite-file-menu', { x: 620, y: 500, width: 260, height: 300 });
  await page2.__context.close();
};

// 4. The finished Catcher game, played by the emulator's slider.
scenes['emulator-catcher'] = async (r) => {
  const rec = r.recorder('emulator-catcher');
  const page = await rec.open({ cursor: false });
  await newBlankApp(page, r.base, 'Catcher');
  await setCode(page, finalListing('getting-started/make-a-game.md'));
  await rebuildAndRun(page);
  await sleep(800);
  await page.evaluate(() => document.activeElement && document.activeElement.blur());

  // Start a fresh game so the loop starts at Score 0 Lives 3.
  await page.getByRole('button', { name: /restart/i }).click();
  await sleep(250);
  const start = rec.now();

  // Read the OLED canvas: where is the dot, where is the paddle? The canvas
  // is a scaled copy of the 128 x 64 screen.
  const probe = () => page.evaluate(() => {
    const c = document.querySelector('.cf-device-screen');
    const ctx = c.getContext('2d');
    const w = c.width;
    const h = c.height;
    const sx = w / 128;
    const sy = h / 64;
    const d = ctx.getImageData(0, 0, w, h).data;
    const lit = (x, y) => {
      const k = (y * w + x) * 4;
      return d[k] + d[k + 1] + d[k + 2] > 380;
    };
    let dotSum = 0;
    let dotN = 0;
    let dotX = 0;
    let padTop = -1;
    let padBottom = -1;
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        if (!lit(x, y)) continue;
        if (x >= 114 * sx) {
          if (padTop < 0) padTop = y;
          padBottom = y;
        } else if (y > 14 * sy && x > 4 * sx) {
          dotSum += y;
          dotX += x;
          dotN++;
        }
      }
    }
    return {
      dotY: dotN ? dotSum / dotN / sy : null,
      dotX: dotN ? dotX / dotN / sx : null,
      padTop: padTop >= 0 ? padTop / sy : null,
    };
  });

  let value = 50;
  await sliderGrab(page, value);
  let dotsSeen = 0;
  let lastX = 0;
  const deadline = Date.now() + 11000;
  let finishedDots = 0;
  while (Date.now() < deadline && finishedDots < 4) {
    const s = await probe();
    if (s.dotX !== null) {
      if (s.dotX < lastX - 20) {
        dotsSeen++;
        finishedDots++;
      }
      lastX = s.dotX;
    }
    if (s.dotY !== null && s.padTop !== null) {
      // The second dot is deliberately missed, to show lives and the red light.
      const wantMiss = dotsSeen === 1;
      let target = s.dotY - 7;
      if (wantMiss) target = s.dotY < 32 ? s.dotY + 26 : s.dotY - 30;
      target = Math.max(0, Math.min(50, target));
      const err = target - s.padTop;
      value = Math.max(0, Math.min(100, value - Math.max(-4, Math.min(4, err * 1.2))));
      await sliderTo(page, value, 1);
    }
    await sleep(30);
  }
  await sleep(600);
  await page.mouse.up();
  const end = Math.min(rec.now(), start + 10);
  await rec.finish({ from: start, to: end, region: DEVICE, posterAt: 1.0 });
};

// 5. A short sprite app: an actor moved with the slider and buttons.
scenes['emulator-sprites'] = async (r) => {
  const rec = r.recorder('emulator-sprites');
  const page = await rec.open({ cursor: false });
  await newBlankApp(page, r.base, 'Hello');
  const template = await readEditorCode(page);
  const block = docsBlock('concepts/sprites.md', 'heroActor.setPosQ8(x, y * 256);');
  const code = assembleFragments(template, block);
  await setCode(page, code);
  await rebuildAndRun(page);
  await sleep(800);
  await page.evaluate(() => document.activeElement && document.activeElement.blur());
  await sliderGrab(page, 50);
  await sleep(300);
  const start = rec.now();

  // Slide up and down, and hold the middle buttons to move sideways.
  for (let v = 50; v <= 100; v += 5) { await sliderTo(page, v, 1); await sleep(30); }
  await page.keyboard.down('d');
  await sleep(1200);
  await page.keyboard.up('d');
  for (let v = 100; v >= 10; v -= 4) { await sliderTo(page, v, 1); await sleep(30); }
  await page.keyboard.down('a');
  await sleep(1500);
  await page.keyboard.up('a');
  for (let v = 10; v <= 50; v += 4) { await sliderTo(page, v, 1); await sleep(30); }
  await sleep(300);
  await page.mouse.up();
  const end = Math.min(rec.now(), start + 8);
  await rec.finish({ from: start, to: end, region: DEVICE, posterAt: 0.2 });
};

// 6. The first build: REBUILD & RUN, then the emulator shows the text.
scenes['rebuild-and-run'] = async (r) => {
  const rec = r.recorder('rebuild-and-run');
  const page = await rec.open();
  await newBlankApp(page, r.base, 'Hello');
  await sleep(700);
  const start = rec.now();
  await clickCentre(page, page.getByRole('button', { name: 'REBUILD & RUN' }));
  await page.waitForFunction(() => /running your app/i.test(document.getElementById('builder-emulator-status')?.innerText || ''), null, { timeout: 120000 });
  await sleep(2500);
  const end = Math.min(rec.now(), start + 12);
  await r.shot(page, 'rebuild-and-run-done', EMU_COLUMN);
  await rec.finish({ from: start, to: end, region: EMU_COLUMN, posterAt: 0.1 });
};

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.list || opts.scenes.length === 0) {
    console.log('Scenes: ' + Object.keys(scenes).join(', ') + '\nUsage: node capture.mjs <scene>... | all  [--base URL] [--out DIR] [--headed]');
    return;
  }
  const names = opts.scenes.includes('all') ? Object.keys(scenes) : opts.scenes;
  for (const n of names) if (!scenes[n]) throw new Error('Unknown scene ' + n + '. Scenes: ' + Object.keys(scenes).join(', '));
  fs.mkdirSync(opts.out, { recursive: true });

  const { chromium } = await loadPlaywright();
  const browser = await chromium.launch({ headless: !opts.headed });
  const runner = new Runner(browser, opts.base, opts.out);
  let failed = 0;
  for (const n of names) {
    console.log('Scene ' + n);
    try {
      await scenes[n](runner);
    } catch (e) {
      failed++;
      console.log('  FAILED: ' + e.message.split('\n')[0]);
    }
  }
  await browser.close();
  console.log(failed ? failed + ' scene(s) failed' : 'Done');
  process.exitCode = failed ? 1 : 0;
}

main().catch((e) => { console.error(e.message); process.exit(1); });

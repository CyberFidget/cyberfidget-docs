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
// See README.md for prerequisites and "Driving the emulator" for how scenes
// are put together.

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
  const opts = { base: 'http://localhost:8000', site: 'https://cyberfidget.com', out: path.join(DOCS_ROOT, 'assets', 'media'), headed: false, list: false, scenes: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--base') opts.base = argv[++i];
    else if (a === '--site') opts.site = argv[++i];
    else if (a === '--out') opts.out = path.resolve(argv[++i]);
    else if (a === '--headed') opts.headed = true;
    else if (a === '--list') opts.list = true;
    else if (a.startsWith('--')) throw new Error('Unknown option ' + a);
    else opts.scenes.push(a);
  }
  opts.base = opts.base.replace(/\/+$/, '');
  opts.site = opts.site.replace(/\/+$/, '');
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
  const usable = (candidate) => {
    const probe = spawnSync(candidate, ['-version'], { encoding: 'utf8', timeout: 5000 });
    return !probe.error && probe.status === 0;
  };
  if (process.env.FFMPEG && usable(process.env.FFMPEG)) return process.env.FFMPEG;
  const roots = [];
  if (process.env.PLAYWRIGHT_BROWSERS_PATH && process.env.PLAYWRIGHT_BROWSERS_PATH !== '0') roots.push(process.env.PLAYWRIGHT_BROWSERS_PATH);
  if (process.env.LOCALAPPDATA) roots.push(path.join(process.env.LOCALAPPDATA, 'ms-playwright'));
  roots.push(path.join(os.homedir(), '.cache', 'ms-playwright'));
  roots.push(path.join(os.homedir(), 'Library', 'Caches', 'ms-playwright'));
  for (const root of roots) {
    let dirs;
    try { dirs = fs.readdirSync(root); } catch { continue; }
    for (const dir of dirs.filter((d) => d.startsWith('ffmpeg-')).sort().reverse()) {
      let files;
      try { files = fs.readdirSync(path.join(root, dir)); } catch { continue; }
      for (const f of files) {
        const candidate = path.join(root, dir, f);
        if (/^ffmpeg(-[a-z0-9]+)?(\.exe)?$/.test(f) && usable(candidate)) return candidate;
      }
    }
  }
  return null;
}

// ---------------------------------------------------------------------------
// Recording: pages, clips, stills
// ---------------------------------------------------------------------------

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const VIEW = { width: 1280, height: 800 };

// Ready-made crop regions, in page pixels (the page is 1280 x 800).
// Whole-column region on the left: tabs, workspace and code area.
const WORKSPACE = { x: 0, y: 112, width: 940, height: 668 };
// The tab rail, file strip and 2D or 3D workspace, without the emulator.
const STUDIO_PANEL = { x: 0, y: 112, width: 862, height: 640 };
// Everything below the site header: workspace and emulator side by side.
const WHOLE_STUDIO = { x: 0, y: 112, width: 1280, height: 668 };
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

// The docs site's page background (Material "slate" scheme,
// --md-default-bg-color, hsl(225, 15%, 14%)). Measured from the built docs
// site, not guessed: body background-color computed to rgb(30, 33, 41).
// If the docs theme colour changes, update this and re-capture every
// emulator clip (see README, "Driving the emulator").
const DOCS_BG = 'rgb(30, 33, 41)';

// Capture browser only: paint the area behind the emulator device in the
// docs page colour, so the device's LED glow fades into the docs page
// instead of into the studio's own dark purple (which showed as a dark frame
// around the device). Takes a browser context or a page; the style is added
// to every page that loads afterwards. Nothing on the server changes.
async function matchDocsBackground(target) {
  await target.addInitScript((bg) => {
    const add = () => {
      if (document.getElementById('cf-capture-docs-bg')) return;
      const style = document.createElement('style');
      style.id = 'cf-capture-docs-bg';
      style.textContent = '#studio-emulator-column, #studio-emulator-mount, #panel-builder-emulator, .studio-emulator-column, .builder-emu-main, .builder-emu-device-row, .builder-emu-device, #builder-emulator-container { background: ' + bg + ' !important; }';
      document.documentElement.appendChild(style);
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', add); else add();
  }, DOCS_BG);
}

// For clips that show the device alone: hide (but keep the space of) the
// "EMULATOR" label above it and the RESTART / sound row below it, so the crop
// with its glow margin shows only the device. Call after the app is running
// and before the clip starts.
async function hideEmulatorChrome(page) {
  return page.addStyleTag({ content: '.studio-emulator-stamp, .cf-device-controls, .builder-emulator-volume-wrap { visibility: hidden !important; }' });
}

// Crop rectangle (page pixels) around the emulator device: the chassis picture
// plus a margin for the LED glow (the glow layer is blurred, so it fades out
// within about 24 px of the body). Measure after the app is running, so
// the layout is settled, and use the same region for the whole clip.
async function deviceRegion(page, pad = 24) {
  const b = await page.evaluate(() => {
    const r = document.querySelector('.cf-device-chassis').getBoundingClientRect();
    return { x1: r.left, y1: r.top, x2: r.right, y2: r.bottom };
  });
  const x = Math.max(0, Math.floor(b.x1 - pad));
  const y = Math.max(0, Math.floor(b.y1 - pad));
  return { x: even(x), y: even(y), width: even(Math.min(VIEW.width, Math.ceil(b.x2 + pad)) - even(x)), height: even(Math.min(VIEW.height, Math.ceil(b.y2 + pad)) - even(y)) };
}

// Browser-context options shared by recorded and plain pages. `models: true`
// turns the studio's 3D tab on for this browser only (see enableModels).
async function newContext(browser, { video = null, cursor = false, models = false } = {}) {
  const context = await browser.newContext({
    viewport: VIEW,
    deviceScaleFactor: 1,
    permissions: ['clipboard-read', 'clipboard-write'],
    ...(video ? { recordVideo: { dir: video, size: VIEW } } : {}),
  });
  await matchDocsBackground(context);
  if (cursor) await context.addInitScript(CURSOR_SCRIPT);
  if (models) await enableModels(context);
  return context;
}

// The 3D tab only appears for visitors whose feature lookup says so. For a
// capture, answer that lookup inside this browser (signed out, 3D on), the
// same way the website's own browser tests do. Nothing on the server changes.
async function enableModels(context) {
  await context.route('**/api/user-features.php', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ user_id: null, features: { wireframe_studio: true } }),
  }));
}

class Recorder {
  constructor(runner, name) {
    this.runner = runner;
    this.name = name;
  }

  async open({ cursor = true, models = false } = {}) {
    this.dir = fs.mkdtempSync(path.join(os.tmpdir(), 'cf-capture-'));
    this.context = await newContext(this.runner.browser, { video: this.dir, cursor, models });
    this.t0 = Date.now();
    this.page = await this.context.newPage();
    this.page.on('pageerror', (e) => console.log('  page error: ' + e.message));
    return this.page;
  }

  // Seconds since the page was created (the video's clock).
  now() { return (Date.now() - this.t0) / 1000; }

  // Close the recording and write <name>.webm plus <name>.png. Pass one set
  // of options, or an array of them to cut several clips out of the same
  // recording (each extra one needs its own `name`):
  //   name       output base name (default: the recorder's name)
  //   from, to   the part of the recording to keep, in seconds (rec.now())
  //   region     crop rectangle in page pixels
  //   width      scale the cropped clip down to this width (keeps it small)
  //   posterAt   seconds into the finished clip for the poster frame
  // Playwright's small ffmpeg has no filter for joining pieces, so a long
  // wait (a build) is left out by cutting two clips around it.
  async finish(clips) {
    await this.context.close();
    const raw = await this.page.video().path();
    for (const clip of Array.isArray(clips) ? clips : [clips]) this.cut(raw, clip);
    fs.rmSync(this.dir, { recursive: true, force: true });
  }

  cut(raw, { name = this.name, from, to, region, width, posterAt = 0.3, fps = 20, bitrate = '900k' }) {
    const outWebm = path.join(this.runner.out, name + '.webm');
    const outPng = path.join(this.runner.out, name + '.png');
    const FFMPEG = findFfmpeg();
    if (!FFMPEG) {
      fs.copyFileSync(raw, outWebm);
      console.log('  no ffmpeg found: kept the raw recording, not cropped or trimmed; no poster written');
    } else {
      const vf = [];
      if (region) vf.push(`crop=${even(region.width)}:${even(region.height)}:${even(region.x)}:${even(region.y)}`);
      if (width) vf.push(`scale=${even(width)}:-2`);
      const run = (args) => {
        const r = spawnSync(FFMPEG, ['-hide_banner', '-loglevel', 'error', '-y', ...args], { encoding: 'utf8' });
        if (r.status !== 0) throw new Error('ffmpeg failed: ' + r.stderr);
      };
      run(['-ss', String(Math.max(0, from)), '-t', String(to - from), '-i', raw, ...(vf.length ? ['-vf', vf.join(',')] : []), '-r', String(fps),
        '-c:v', 'libvpx', '-b:v', bitrate, '-crf', '10', '-an', '-auto-alt-ref', '0', outWebm]);
      run(['-ss', String(posterAt), '-i', outWebm, '-frames:v', '1', outPng]);
    }
    const kb = Math.round(fs.statSync(outWebm).size / 1024);
    console.log(`  wrote ${name}.webm (${kb} KB, ${(to - from).toFixed(1)} s) and ${name}.png`);
  }
}

class Runner {
  constructor(browser, base, out, site) {
    this.browser = browser;
    this.base = base;
    this.out = out;
    this.site = site;
  }

  recorder(name) { return new Recorder(this, name); }

  // A plain (not recorded) page, for screenshot-only scenes.
  async plainPage({ models = false } = {}) {
    const context = await newContext(this.browser, { models });
    const page = await context.newPage();
    page.on('pageerror', (e) => console.log('  page error: ' + e.message));
    page.__context = context;
    return page;
  }

  // A page on the public website (the --site URL, signed out), drawn at twice
  // the size so small text stays sharp in the docs. Nothing is changed on the
  // server: signed out, the website keeps picks and settings in this browser.
  async sitePage() {
    const context = await this.browser.newContext({ viewport: VIEW, deviceScaleFactor: 2 });
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

// ---------------------------------------------------------------------------
// Moving the mouse so a viewer can follow
// ---------------------------------------------------------------------------

// Move the cursor smoothly (so the clip shows a path, not a jump).
async function glide(page, x, y, steps = 12) {
  await page.mouse.move(x, y, { steps });
}

async function clickAt(page, x, y, steps = 14) {
  await glide(page, x, y, steps);
  await sleep(150);
  await page.mouse.down();
  await sleep(70);
  await page.mouse.up();
}

async function clickCentre(page, locator, steps = 14) {
  const b = await locator.boundingBox();
  await clickAt(page, b.x + b.width / 2, b.y + b.height / 2, steps);
}

// Click a control: with `show` (the default) the cursor glides to it so the
// clip shows where it is; without, it is a plain click (setup steps).
async function tap(page, locator, show = true) {
  if (show) await clickCentre(page, locator);
  else await locator.click();
}

// Type into a field: letter by letter when shown, instantly otherwise.
async function typeInto(page, locator, text, show = true) {
  if (!show) return locator.fill(text);
  await locator.press('Control+A');
  await locator.pressSequentially(text, { delay: 140 });
}

// Press, move along the points, release: a drag the viewer can follow.
async function drag(page, points, { steps = 10, pause = 120 } = {}) {
  await glide(page, points[0].x, points[0].y, 10);
  await sleep(pause);
  await page.mouse.down();
  for (const p of points.slice(1)) await page.mouse.move(p.x, p.y, { steps });
  await sleep(pause);
  await page.mouse.up();
}

// ---------------------------------------------------------------------------
// Studio: projects, tabs, sprites and models
// ---------------------------------------------------------------------------

// Open the studio's landing page and let it settle.
async function openStudio(page, base) {
  await page.goto(base + '/create/');
  await page.getByText('Create an app').first().waitFor();
  await sleep(1200);
}

// A new project with no app code: the landing page's "Create an app" card.
async function newEmptyProject(page, base) {
  await openStudio(page, base);
  await page.getByText('Create an app').first().click();
  await page.locator('#builder-project-name').waitFor();
  await sleep(1200);
}

// Open the studio and make a blank-template app with the given App Name.
// Exact labels (verified in the studio source): "Create an app",
// "Code from Blank Template", App Name field, "Create".
async function newBlankApp(page, base, appName) {
  await openStudio(page, base);
  await page.getByText('Create an app').first().click();
  await page.getByRole('button', { name: /Code from Blank Template/ }).click();
  await page.locator('#builder-project-name').fill(appName);
  await page.getByRole('button', { name: 'Create', exact: true }).click();
  await page.locator('.ace_editor:visible').first().waitFor();
  await sleep(1500);
}

// The tab rail: 'builder' (Generate), 'ide' (Code), 'pixel' (2D),
// 'model' (3D), 'settings'.
function railButton(page, panel) {
  return page.locator(`.activity-button[data-panel="${panel}"]`);
}

async function openTab(page, panel, show = true) {
  await tap(page, railButton(page, panel), show);
  await sleep(show ? 900 : 600);
}

// "Added <name>" appears under the file strip after a file is added; any
// click elsewhere closes it. Close it during setup so it is not in the clip.
async function dismissToast(page) {
  if (await page.locator('.cf-file-toast').isVisible()) {
    await page.mouse.click(640, 88);
    await sleep(300);
  }
}

// Add art > Draw a new sprite > Sprite name > Create.
async function newSprite(page, name, show = true) {
  await tap(page, page.getByRole('button', { name: 'Add art' }), show);
  await sleep(show ? 700 : 300);
  await tap(page, page.getByText('Draw a new sprite'), show);
  await sleep(show ? 600 : 300);
  await typeInto(page, page.locator('#art-new-sprite-name'), name, show);
  await sleep(show ? 500 : 100);
  await tap(page, page.getByRole('button', { name: 'Create', exact: true }), show);
  await page.locator('#pixel-grid').waitFor();
  await sleep(1000);
}

// Add art > Build a 3D model > Model name > Create (needs models: true).
async function newModel(page, name, show = true) {
  await tap(page, page.getByRole('button', { name: 'Add art' }), show);
  await sleep(show ? 700 : 300);
  await tap(page, page.getByText('Build a 3D model'), show);
  await sleep(show ? 600 : 300);
  await typeInto(page, page.locator('#model-new-model-name'), name, show);
  await sleep(show ? 500 : 100);
  await tap(page, page.locator('[data-new-model-create]'), show);
  await page.waitForFunction((n) => window.__cfModelEditor?.debugState?.().model?.meta?.name === n, name);
  await sleep(1000);
}

// All files > Free starters > a starter model ('ship', 'cube', 'pyramid').
async function addStarterModel(page, starter, show = true) {
  await tap(page, page.getByRole('button', { name: /^All files/ }), show);
  await sleep(show ? 700 : 300);
  await tap(page, page.getByRole('button', { name: 'Free starters', exact: true }), show);
  await sleep(show ? 900 : 500);
  const button = page.locator(`.cf-all-files [data-model-starter="${starter}"]`);
  await button.scrollIntoViewIfNeeded();
  await sleep(show ? 600 : 200);
  await tap(page, button, show);
  await page.waitForFunction((n) => window.__cfModelEditor?.debugState?.().model?.meta?.name === n, starter);
  await sleep(1000);
}

// ---------------------------------------------------------------------------
// The 2D canvas
// ---------------------------------------------------------------------------

// A 2D tool button, by the start of its label ("Draw", "Line", "Oval"...).
function tool2d(page, name) {
  return page.locator(`#art-tool-buttons button[aria-label^="${name}"]`);
}

// Page position of the centre of sprite pixel (px, py) on the 128 x 64 canvas.
async function pixelAt(page, px, py) {
  const g = await page.locator('#pixel-grid').boundingBox();
  return { x: g.x + ((px + 0.5) * g.width) / 128, y: g.y + ((py + 0.5) * g.height) / 64 };
}

// Drag along sprite-pixel coordinates [[x, y], ...] on the canvas.
async function drawPixels(page, pixels, opts) {
  const points = [];
  for (const [x, y] of pixels) points.push(await pixelAt(page, x, y));
  await drag(page, points, opts);
}

// ---------------------------------------------------------------------------
// The 3D model stage
// ---------------------------------------------------------------------------

// The model editor's state (points, lines, view, selection, and where each
// point is on the stage). The studio exposes it for its own tests.
function modelState(page) {
  return page.evaluate(() => window.__cfModelEditor.debugState());
}

async function stageBox(page) {
  return page.locator('#model-editor-canvas').boundingBox();
}

// Page position of point `index` on the stage.
async function modelPoint(page, index) {
  const [s, b] = [await modelState(page), await stageBox(page)];
  return { x: b.x + s.projected[index].x, y: b.y + s.projected[index].y };
}

// Page position of the middle of line `index`.
async function modelLineMiddle(page, index) {
  const [s, b] = [await modelState(page), await stageBox(page)];
  const [i, j] = s.model.edges[index];
  return { x: b.x + (s.projected[i].x + s.projected[j].x) / 2, y: b.y + (s.projected[i].y + s.projected[j].y) / 2 };
}

// Index of the point whose model position is [x, y, z] (nearest one).
async function modelPointIndex(page, target) {
  const s = await modelState(page);
  let best = 0;
  let bestD = Infinity;
  s.model.vertices.forEach((v, i) => {
    const d = Math.hypot(v[0] - target[0], v[1] - target[1], v[2] - target[2]);
    if (d < bestD) { bestD = d; best = i; }
  });
  return best;
}

// Where to click so Add point places a point at model x, y. The editor puts
// a new point on the flat slice through the model's middle that faces you.
// With the view turned to face the front (yaw 0), x is across and y is up.
async function stageSpotFor(page, x, y) {
  const [s, b] = [await modelState(page), await stageBox(page)];
  return { x: b.x + b.width / 2 + x * s.view.zoom, y: b.y + b.height / 2 - (y * s.view.zoom) / Math.cos(s.view.pitch) };
}

// Turn the view by dragging empty space (top-left corner of the stage).
// The editor turns 0.008 radians per pixel dragged.
async function orbitTo(page, yaw, pitch, { steps = 24 } = {}) {
  const [s, b] = [await modelState(page), await stageBox(page)];
  const start = { x: b.x + 24, y: b.y + 24 };
  const end = { x: start.x + (yaw - s.view.yaw) / 0.008, y: start.y + (pitch - s.view.pitch) / 0.008 };
  await drag(page, [start, end], { steps });
}

// Zoom the stage view to `zoom` (pixels per model unit) with the scroll
// wheel; the editor zooms by e^(-deltaY / 1000).
async function zoomTo(page, zoom) {
  const [s, b] = [await modelState(page), await stageBox(page)];
  await page.mouse.move(b.x + b.width / 2, b.y + b.height - 30);
  await page.mouse.wheel(0, 1000 * Math.log(s.view.zoom / zoom));
  await sleep(200);
}

// ---------------------------------------------------------------------------
// The emulator
// ---------------------------------------------------------------------------

// Wait until the emulator says the app is running.
async function waitForApp(page) {
  await page.waitForFunction(() => /running your app/i.test(document.getElementById('builder-emulator-status')?.innerText || ''), null, { timeout: 120000 });
}

// Click REBUILD & RUN for the first build, or REBUILD for later builds; wait for
// the emulator to say it is running.
async function rebuildAndRun(page, show = false) {
  const welcome = page.getByRole('button', { name: 'REBUILD & RUN', exact: true });
  const button = await welcome.isVisible()
    ? welcome
    : page.locator('#builder-compile-wasm');
  await tap(page, button, show);
  await waitForApp(page);
}

// Read the emulator's screen: returns lit(x, y) for the 128 x 64 pixels.
// The screen canvas is a scaled copy of the device screen; this samples the
// middle of each device pixel.
async function readScreen(page) {
  const rows = await page.evaluate(() => {
    const c = document.querySelector('.cf-device-screen');
    const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
    const sx = c.width / 128;
    const sy = c.height / 64;
    const out = [];
    for (let y = 0; y < 64; y++) {
      let row = '';
      for (let x = 0; x < 128; x++) {
        const k = (Math.floor((y + 0.5) * sy) * c.width + Math.floor((x + 0.5) * sx)) * 4;
        row += d[k] + d[k + 1] + d[k + 2] > 380 ? '1' : '0';
      }
      out.push(row);
    }
    return out;
  });
  return (x, y) => rows[y][x] === '1';
}

// Drive the emulator's slider with the mouse: press on the slider, then move
// the pointer up (value 100) or down (value 0) while the button is held.
async function sliderGrab(page, value, steps = 1) {
  const b = await page.locator('.cf-device-sliderzone').boundingBox();
  await page.mouse.move(b.x + b.width / 2, b.y + (1 - value / 100) * b.height, { steps });
  await page.mouse.down();
}

async function sliderTo(page, value, steps = 6) {
  const b = await page.locator('.cf-device-sliderzone').boundingBox();
  await page.mouse.move(b.x + b.width / 2, b.y + (1 - value / 100) * b.height, { steps });
}

// Press an emulator button with the mouse and hold it for `ms`.
// Names: TopLeft, TopRight, MiddleLeft, MiddleRight, BottomLeft, BottomRight.
async function pressButton(page, name, ms = 150) {
  const b = await page.locator(`.cf-device-btn[data-button="${name}"]`).boundingBox();
  await glide(page, b.x + b.width / 2, b.y + b.height / 2, 8);
  await page.mouse.down();
  await sleep(ms);
  await page.mouse.up();
}

// ---------------------------------------------------------------------------
// Code from the docs
// ---------------------------------------------------------------------------

// Replace the contents of the visible code editor (the .cpp file).
async function setCode(page, code) {
  await page.evaluate((c) => {
    const el = [...document.querySelectorAll('.ace_editor')].find((e) => e.offsetParent);
    window.ace.edit(el).setValue(c, -1);
  }, code);
  await sleep(300);
}

async function readEditorCode(page) {
  return page.evaluate(() => {
    const el = [...document.querySelectorAll('.ace_editor')].find((e) => e.offsetParent);
    return window.ace.edit(el).getValue();
  });
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

// The first fenced cpp block of a docs page that contains `needle`. Blocks
// written as insert-fragments are joined by assembleFragments().
function docsBlock(docsRelPath, needle) {
  const md = fs.readFileSync(path.join(DOCS_ROOT, docsRelPath), 'utf8').replace(/\r\n/g, '\n');
  for (const m of md.matchAll(/```cpp\n([\s\S]*?)\n```/g)) {
    if (m[1].includes(needle)) return m[1];
  }
  throw new Error('No cpp block containing ' + JSON.stringify(needle) + ' in ' + docsRelPath);
}

// Put a docs fragment (placement comments "Insert at the top of the
// file ...", "inside begin() ...", "inside update() ...") into the blank
// template. Mirrors how a reader does it.
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
  await typeInto(page, page.locator('#art-new-sprite-name'), 'Ball');
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
  await openTab(page, 'ide');
  await sleep(300);
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
  await openTab(page3, 'pixel', false);
  await sleep(600);
  await r.shot(page3, 'add-art-2d-no-art', WORKSPACE);
  await page3.__context.close();

  // With a sprite open: the Sprite file menu has Add from file.
  const page2 = await r.plainPage();
  await newBlankApp(page2, r.base, 'Hello');
  await newSprite(page2, 'Ball', false);
  await sleep(200);
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
  await hideEmulatorChrome(page);
  await sleep(250);
  const start = rec.now();

  // Where is the falling dot, and where is the paddle (the lit column at the
  // right edge)? Positions are in device pixels.
  const probe = async () => {
    const lit = await readScreen(page);
    let dotSum = 0;
    let dotN = 0;
    let dotX = 0;
    let padTop = -1;
    for (let y = 0; y < 64; y++) {
      for (let x = 0; x < 128; x++) {
        if (!lit(x, y)) continue;
        if (x >= 114) {
          if (padTop < 0) padTop = y;
        } else if (y > 14 && x > 4) {
          dotSum += y;
          dotX += x;
          dotN++;
        }
      }
    }
    return {
      dotY: dotN ? dotSum / dotN : null,
      dotX: dotN ? dotX / dotN : null,
      padTop: padTop >= 0 ? padTop : null,
    };
  };

  let value = 50;
  await sliderGrab(page, value);
  let dotsSeen = 0;
  let lastX = 0;
  const deadline = Date.now() + 11000;
  while (Date.now() < deadline && dotsSeen < 4) {
    const s = await probe();
    if (s.dotX !== null) {
      if (s.dotX < lastX - 20) dotsSeen++;
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
  await rec.finish({ from: start, to: end, region: await deviceRegion(page), posterAt: 1.0 });
};

// 5. A short sprite app: an actor moved with the slider and buttons.
scenes['emulator-sprites'] = async (r) => {
  const rec = r.recorder('emulator-sprites');
  const page = await rec.open({ cursor: false });
  await newBlankApp(page, r.base, 'Hello');
  const template = await readEditorCode(page);
  const block = docsBlock('concepts/sprites.md', 'heroActor.setPosQ8(x, y * 256);');
  await setCode(page, assembleFragments(template, block));
  await rebuildAndRun(page);
  await sleep(800);
  await page.evaluate(() => document.activeElement && document.activeElement.blur());
  await hideEmulatorChrome(page);
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
  await rec.finish({ from: start, to: end, region: await deviceRegion(page), posterAt: 0.2 });
};

// 6. The first build: REBUILD & RUN, then the emulator shows the text.
scenes['rebuild-and-run'] = async (r) => {
  const rec = r.recorder('rebuild-and-run');
  const page = await rec.open();
  await newBlankApp(page, r.base, 'Hello');
  await sleep(700);
  const start = rec.now();
  await rebuildAndRun(page, true);
  await sleep(2500);
  const end = Math.min(rec.now(), start + 12);
  await r.shot(page, 'rebuild-and-run-done', EMU_COLUMN);
  await rec.finish({ from: start, to: end, region: EMU_COLUMN, posterAt: 0.1 });
};

// 7. 3D: open the 3D tab, Add art > Build a 3D model, name it, Create.
// Stills: the Add art menu with Build a 3D model, the New model dialog,
// the empty model, and Free starters with the Starter Models.
scenes['3d-new-model'] = async (r) => {
  const rec = r.recorder('3d-new-model');
  const page = await rec.open({ models: true });
  await newEmptyProject(page, r.base);
  await railButton(page, 'model').waitFor();
  await sleep(600);
  const start = rec.now();

  await openTab(page, 'model');
  await tap(page, page.getByRole('button', { name: 'Add art' }));
  await sleep(900);
  await r.shot(page, '3d-add-art-menu', { x: 190, y: 112, width: 310, height: 320 });
  await tap(page, page.getByText('Build a 3D model'));
  await sleep(700);
  await typeInto(page, page.locator('#model-new-model-name'), 'Arrow');
  await sleep(500);
  await r.shot(page, '3d-new-model-dialog', { x: 370, y: 250, width: 540, height: 300 });
  await tap(page, page.locator('[data-new-model-create]'));
  await page.waitForFunction(() => window.__cfModelEditor?.debugState?.().model?.meta?.name === 'Arrow');
  await sleep(1200);
  await dismissToast(page);
  await glide(page, 400, 450, 14);
  await sleep(1200);
  await r.shot(page, '3d-new-model-blank', STUDIO_PANEL);
  const end = rec.now();

  // Not in the clip: the starter models in Free starters.
  await page.getByRole('button', { name: /^All files/ }).click();
  await sleep(500);
  await page.getByRole('button', { name: 'Free starters', exact: true }).click();
  await sleep(800);
  await page.locator('.cf-all-files [data-model-starter="ship"]').scrollIntoViewIfNeeded();
  await sleep(500);
  await r.shot(page, '3d-starter-models', STUDIO_PANEL);
  await rec.finish({ from: start, to: end, region: WHOLE_STUDIO, posterAt: end - start - 0.3, width: 900 });
};

// 8. 3D: Add point (Mirror on adds the twin), then Connect points into an
// arrow shape, then turn the view to see it.
scenes['3d-add-points-lines'] = async (r) => {
  const rec = r.recorder('3d-add-points-lines');
  const page = await rec.open({ models: true });
  await newEmptyProject(page, r.base);
  await openTab(page, 'model', false);
  await newModel(page, 'Arrow', false);
  await dismissToast(page);
  // Face the front, tipped slightly, so the mirror twins look mirrored.
  await orbitTo(page, 0, 0.25, { steps: 4 });
  await glide(page, 400, 600, 4);
  await sleep(600);
  const start = rec.now();

  // The new model has two points (x = -4 and 4) joined by a line.
  await tap(page, page.locator('[data-model-tool="add"]'));
  await sleep(500);
  for (const [x, y] of [[0, 9], [9, -6], [3, -4]]) {
    const spot = await stageSpotFor(page, x, y);
    await clickAt(page, spot.x, spot.y);
    await sleep(600);
  }

  // Connect: click one point, then another.
  await tap(page, page.locator('[data-model-tool="connect"]'));
  await sleep(500);
  const pairs = [[[0, 9, 0], [4, 0, 0]], [[4, 0, 0], [9, -6, 0]], [[9, -6, 0], [3, -4, 0]], [[3, -4, 0], [-3, -4, 0]]];
  for (const [a, b] of pairs) {
    const ia = await modelPointIndex(page, a);
    const ib = await modelPointIndex(page, b);
    const pa = await modelPoint(page, ia);
    await clickAt(page, pa.x, pa.y);
    await sleep(350);
    const pb = await modelPoint(page, ib);
    await clickAt(page, pb.x, pb.y);
    await sleep(600);
  }
  await sleep(400);
  await r.shot(page, '3d-add-points-lines-done', STUDIO_PANEL);

  // Move, then turn the view a little to show it is a model in space.
  await tap(page, page.locator('[data-model-tool="move"]'));
  await sleep(400);
  const s = await modelState(page);
  await orbitTo(page, s.view.yaw + 0.6, s.view.pitch + 0.2);
  await sleep(500);
  await orbitTo(page, 0, 0.25);
  await sleep(1000);
  const end = rec.now();
  await rec.finish({ from: start, to: end, region: STUDIO_PANEL, posterAt: end - start - 0.3, width: 700 });
};

// 9. 3D: Move tool on the SHIP starter: turn the view, zoom, drag a point
// (its mirror twin follows), select a line, Mirror off, drag again, Undo.
scenes['3d-move-rotate-view'] = async (r) => {
  const rec = r.recorder('3d-move-rotate-view');
  const page = await rec.open({ models: true });
  await newEmptyProject(page, r.base);
  await openTab(page, 'model', false);
  await addStarterModel(page, 'ship', false);
  await dismissToast(page);
  // Seen from above and a little to one side, small enough to fit.
  await orbitTo(page, 0.5, 0.7, { steps: 4 });
  await zoomTo(page, 8);
  await glide(page, 400, 600, 4);
  await sleep(600);
  const start = rec.now();

  // Turn the view: drag empty space.
  const s0 = await modelState(page);
  await orbitTo(page, s0.view.yaw + 1.0, s0.view.pitch - 0.3);
  await sleep(400);
  await orbitTo(page, s0.view.yaw, s0.view.pitch);
  await sleep(400);

  // Zoom: scroll over the stage.
  const b = await stageBox(page);
  await glide(page, b.x + b.width / 2, b.y + b.height / 2 + 120, 10);
  for (let i = 0; i < 4; i++) { await page.mouse.wheel(0, -120); await sleep(150); }
  await sleep(300);
  for (let i = 0; i < 4; i++) { await page.mouse.wheel(0, 120); await sleep(150); }
  await sleep(400);

  // Drag a point that has a mirror twin: of the points well inside the
  // stage, the one farthest right of the middle.
  const s1 = await modelState(page);
  let pick = -1;
  s1.projected.forEach((q, i) => {
    const inside = q.x > 60 && q.x < s1.canvas.width - 60 && q.y > 60 && q.y < s1.canvas.height - 60;
    if (inside && s1.model.vertices[i][0] !== 0 && (pick < 0 || q.x > s1.projected[pick].x)) pick = i;
  });
  if (pick < 0) throw new Error('No point to drag inside the stage');
  let p = await modelPoint(page, pick);
  await drag(page, [p, { x: p.x + 20, y: p.y - 30 }], { steps: 14 });
  await sleep(700);

  // Select a line: the Selection panel describes it.
  const line = await modelLineMiddle(page, 0);
  await clickAt(page, line.x, line.y);
  await sleep(1000);

  // With mirror off, only the dragged point moves.
  await tap(page, page.locator('.model-mirror-tool'));
  await sleep(600);
  p = await modelPoint(page, pick);
  await drag(page, [p, { x: p.x + 20, y: p.y + 30 }], { steps: 14 });
  await sleep(700);
  await r.shot(page, '3d-move-rotate-view-mirror-off', STUDIO_PANEL);

  // Undo both drags, and put Mirror back on.
  await tap(page, page.locator('.model-undo'));
  await sleep(500);
  await tap(page, page.locator('.model-undo'));
  await sleep(500);
  await tap(page, page.locator('.model-mirror-tool'));
  await sleep(800);
  const end = rec.now();
  await rec.finish({ from: start, to: end, region: STUDIO_PANEL, posterAt: end - start - 0.3, width: 700 });
};

// 10. 3D: Try it in an app. In a project with no app code, the studio writes
// a small viewer app, opens Code and builds it; the emulator spins the model
// and the slider zooms. Two clips, so the build wait is left out:
// 3d-try-in-app (the click) and 3d-try-in-app-emulator (the running app).
// Stills: the Use in code line under the model's buttons; the running app.
scenes['3d-try-in-app'] = async (r) => {
  const rec = r.recorder('3d-try-in-app');
  const page = await rec.open({ models: true });
  await newEmptyProject(page, r.base);
  await openTab(page, 'model', false);
  await addStarterModel(page, 'ship', false);
  await dismissToast(page);
  await orbitTo(page, 0.5, 0.7, { steps: 4 });
  await zoomTo(page, 8);
  const ref = page.locator('#model-code-reference-line');
  await ref.waitFor();
  await ref.scrollIntoViewIfNeeded();
  await sleep(400);
  const rb = await page.locator('.model-right').boundingBox();
  await r.shot(page, '3d-use-in-code', { x: rb.x, y: 560, width: rb.width, height: 190 });
  await glide(page, 400, 600, 4);
  await sleep(600);
  const start = rec.now();

  await tap(page, page.locator('#model-try-app'));
  await sleep(3000);
  const clickEnd = rec.now();
  await waitForApp(page);
  await sleep(500);
  await page.evaluate(() => document.activeElement && document.activeElement.blur());
  const chromeHidden = await hideEmulatorChrome(page);
  const emuStart = rec.now();
  await sleep(1500);

  // The viewer app zooms with the slider.
  await sliderGrab(page, 50, 12);
  for (let v = 50; v <= 100; v += 3) { await sliderTo(page, v, 1); await sleep(40); }
  await sleep(600);
  for (let v = 100; v >= 0; v -= 3) { await sliderTo(page, v, 1); await sleep(40); }
  await sleep(600);
  for (let v = 0; v <= 50; v += 3) { await sliderTo(page, v, 1); await sleep(40); }
  await page.mouse.up();
  await sleep(800);
  const end = rec.now();
  // The whole-studio still keeps the label and the RESTART row.
  await chromeHidden.evaluate((e) => e.remove());
  await r.shot(page, '3d-try-in-app-running', WHOLE_STUDIO);
  // Two clips around the build: the click path, then the running app.
  await rec.finish([
    { from: start, to: clickEnd, region: WHOLE_STUDIO, posterAt: 0.2, width: 900 },
    { name: '3d-try-in-app-emulator', from: emuStart, to: end, region: await deviceRegion(page), posterAt: 1.0 },
  ]);
};

// 11. 2D drawing tools on a new sprite: Draw, Line, Rectangle, Oval, Fill,
// Erase. Still: the tool bar.
scenes['2d-drawing-tools'] = async (r) => {
  const rec = r.recorder('2d-drawing-tools');
  const page = await rec.open();
  await newEmptyProject(page, r.base);
  await openTab(page, 'pixel', false);
  await newSprite(page, 'Scene', false);
  await dismissToast(page);
  await r.shot(page, '2d-tool-bar', { x: 56, y: 160, width: 136, height: 590 });
  await glide(page, 400, 600, 4);
  await sleep(500);
  const start = rec.now();

  // Draw: a freehand hill.
  await tap(page, tool2d(page, 'Draw'));
  await sleep(300);
  const hill = [];
  for (let x = 4; x <= 60; x += 2) hill.push([x, Math.round(52 - 10 * Math.sin(((x - 4) / 56) * Math.PI))]);
  await drawPixels(page, hill, { steps: 2 });
  await sleep(400);

  // Line: a straight line (the options bar shows Width).
  await tap(page, tool2d(page, 'Line'));
  await sleep(500);
  await drawPixels(page, [[4, 58], [124, 58]], { steps: 20 });
  await sleep(400);

  // Rectangle: a house.
  await tap(page, tool2d(page, 'Rectangle'));
  await sleep(500);
  await drawPixels(page, [[76, 34], [104, 56]], { steps: 18 });
  await sleep(400);

  // Oval: a sun.
  await tap(page, tool2d(page, 'Oval'));
  await sleep(500);
  await drawPixels(page, [[100, 4], [118, 20]], { steps: 14 });
  await sleep(400);

  // Fill: the house and the sun.
  await tap(page, tool2d(page, 'Fill'));
  await sleep(400);
  for (const [x, y] of [[90, 45], [109, 12]]) {
    const at = await pixelAt(page, x, y);
    await clickAt(page, at.x, at.y);
    await sleep(500);
  }

  // Erase: a door.
  await tap(page, tool2d(page, 'Erase'));
  await sleep(400);
  await drawPixels(page, [[88, 56], [88, 46], [92, 46], [92, 56]], { steps: 8 });
  await sleep(900);
  await r.shot(page, '2d-drawing-tools-done', STUDIO_PANEL);
  const end = rec.now();
  await rec.finish({ from: start, to: end, region: STUDIO_PANEL, posterAt: end - start - 0.3, width: 700 });
};

// 12. 2D layers: New layer, draw on it, hide and show a layer, pick a layer,
// the layer's ... menu. Still: the menu.
scenes['2d-layers'] = async (r) => {
  const rec = r.recorder('2d-layers');
  const page = await rec.open();
  await newEmptyProject(page, r.base);
  await openTab(page, 'pixel', false);
  await newSprite(page, 'Scene', false);
  await dismissToast(page);
  // Layer 1: a filled box.
  await tool2d(page, 'Rectangle').click();
  await page.locator('#shape-mode').selectOption('filled');
  await drawPixels(page, [[30, 16], [70, 48]], { steps: 4, pause: 30 });
  await page.locator('#shape-mode').selectOption('outline');
  await tool2d(page, 'Draw').click();
  await glide(page, 400, 600, 4);
  await sleep(500);
  const start = rec.now();

  // New layer, then draw a line across the box on it.
  await tap(page, page.locator('#art-layer-add button'));
  await sleep(800);
  await tap(page, tool2d(page, 'Line'));
  await sleep(400);
  await drawPixels(page, [[10, 10], [110, 54]], { steps: 20 });
  await sleep(600);

  // Hide Layer 1, then show it again.
  const eye1 = page.locator('#art-layer-list button[aria-label$="Layer 1"].layer-visibility');
  await tap(page, eye1);
  await sleep(1000);
  await tap(page, eye1);
  await sleep(800);

  // Pick Layer 1 to draw on it.
  // (Layer names are editable fields; click the row's status line.)
  await tap(page, page.locator('#layer-list li[data-index="0"] small'));
  await sleep(800);

  // The ... menu of Layer 2.
  await tap(page, page.locator('#art-layer-list button[aria-label="Actions for Layer 2"]'));
  await sleep(900);
  // Crop to the open menu and the layer list together.
  const menu = await page.locator('[role="menu"]:visible').first().boundingBox();
  const list = await page.locator('#art-layer-list').boundingBox();
  const top = Math.min(menu.y, list.y) - 12;
  const bottom = Math.max(menu.y + menu.height, list.y + list.height) + 12;
  await r.shot(page, '2d-layers-menu', { x: 622, y: top, width: 240, height: bottom - top });
  await page.keyboard.press('Escape');
  await sleep(600);
  const end = rec.now();
  await rec.finish({ from: start, to: end, region: STUDIO_PANEL, posterAt: 0.2, width: 700 });
};

// 13. 2D frames: + Frame copies the frame, Move shifts the copy, the
// preview plays the frames and Speed changes how fast. Still: the preview.
scenes['2d-animation-frames'] = async (r) => {
  const rec = r.recorder('2d-animation-frames');
  const page = await rec.open();
  await newEmptyProject(page, r.base);
  await openTab(page, 'pixel', false);
  await newSprite(page, 'Ball', false);
  await dismissToast(page);
  await tool2d(page, 'Oval').click();
  await page.locator('#shape-mode').selectOption('filled');
  await drawPixels(page, [[8, 24], [24, 40]], { steps: 4, pause: 30 });
  await page.locator('#shape-mode').selectOption('outline');
  await tool2d(page, 'Draw').click();
  await glide(page, 400, 600, 4);
  await sleep(500);
  const start = rec.now();

  // + Frame copies the current frame; Move shifts the whole layer.
  const addFrame = page.getByRole('button', { name: 'Add a frame (copies the current one)' });
  for (let i = 0; i < 3; i++) {
    await tap(page, addFrame);
    await sleep(600);
    await tap(page, tool2d(page, 'Move'));
    await sleep(300);
    const from = await pixelAt(page, 16 + i * 26, 32);
    const to = await pixelAt(page, 16 + (i + 1) * 26, 32);
    await drag(page, [from, to], { steps: 12 });
    await sleep(500);
  }

  // The preview plays on its own. Drag Speed slower, then faster, then back.
  // The slider runs from -1000 to -16 (milliseconds per frame, negated).
  await sleep(1500);
  const speed = await page.locator('#preview-speed').boundingBox();
  const along = (ms) => ({ x: speed.x + 8 + ((1000 - ms) / 984) * (speed.width - 16), y: speed.y + speed.height / 2 });
  await drag(page, [along(100), along(260)], { steps: 14 });
  await sleep(2200);
  await drag(page, [along(260), along(60)], { steps: 14 });
  await sleep(1800);
  await drag(page, [along(60), along(100)], { steps: 8 });
  await sleep(1200);
  await r.shot(page, '2d-animation-frames-preview', { x: 622, y: 160, width: 240, height: 186 });
  const end = rec.now();
  await rec.finish({ from: start, to: end, region: STUDIO_PANEL, posterAt: 0.2, width: 700 });
};

// 14. The Generate tab, signed out, without generating anything (nothing is
// sent to a code generator). Stills: the start panel of a new project; the
// Generation settings it links to; and the How it works view of a demo app,
// whose explanation ships with the demo. Labels verified in
// inc/studio-body.php ("Make your first app", "Modify a Demo App",
// "Generator settings", "How it works") and builder.js.
scenes['generate-tab'] = async (r) => {
  const page = await r.plainPage();
  await newEmptyProject(page, r.base);
  await r.shot(page, 'generate-start', STUDIO_PANEL);

  await page.locator('#builder-generator-settings').click();
  await page.getByText('Choose how app generation runs for your account.').waitFor();
  await sleep(900);
  await r.shot(page, 'generate-settings', { x: 350, y: 410, width: 500, height: 210 });
  await page.__context.close();

  // A fresh browser, so the studio opens its landing page again.
  const demo = await r.plainPage();
  await newEmptyProject(demo, r.base);
  await demo.locator('#builder-try-demo').click();
  await sleep(600);
  await demo.locator('#builder-modify-demo-list').getByText('Spaceship', { exact: true }).click();
  await demo.locator('.builder-surface-tab[data-builder-view="explanation"]').waitFor();
  await sleep(3500);
  await demo.locator('.builder-surface-tab[data-builder-view="explanation"]').click();
  await demo.getByText('Explain Deeper').waitFor();
  await sleep(900);
  await r.shot(demo, 'generate-how-it-works', STUDIO_PANEL);
  await demo.__context.close();
};

// 15. The Archives on the public website, signed out. Stills of browsing, an
// item's page (it opens in a side panel), Try it here, a card after Send to my
// Fidget (signed out, that only queues it in this browser), the Report a
// problem form (opened, not sent) and command mode. The crops keep only
// Cyber Fidget's own items in view, so no maker's personal name appears.
// Labels verified on the live page (2026-10-21).
const ARCHIVES_ITEM = 'breakout';
const ARCHIVES_DRAWER = { x: 920, y: 0, width: 360, height: 800 };
scenes['archives'] = async (r) => {
  const open = async () => {
    const page = await r.sitePage();
    await page.goto(r.site + '/explore/', { waitUntil: 'networkidle' });
    await page.locator('.cf-card').first().waitFor();
    await sleep(1500);
    return page;
  };

  let page = await open();
  await r.shot(page, 'archives-browse', { x: 50, y: 248, width: 855, height: 520 });

  // An item's page, opened by clicking its card.
  await page.locator('.cf-card').filter({ hasText: 'Breakout' }).first().locator('.cf-card-name').click({ force: true });
  await page.getByText('Report a problem').waitFor();
  await sleep(1500);
  await r.shot(page, 'archives-item', ARCHIVES_DRAWER);

  // Try it here: the app runs in the panel.
  await page.locator('button, a').filter({ hasText: /^Try it here/i }).last().click();
  await sleep(6000);
  await r.shot(page, 'archives-try-it', ARCHIVES_DRAWER);

  // Report a problem: the form, not sent.
  await page.getByText('Report a problem').last().click();
  await sleep(1200);
  await r.shot(page, 'archives-report', ARCHIVES_DRAWER);
  await page.__context.close();

  // Send to my Fidget on a card: the card says it is waiting to send.
  page = await open();
  const card = page.locator('.cf-card').filter({ hasText: 'Breakout' }).first();
  await card.getByText('Send to my Fidget', { exact: false }).click();
  await sleep(1500);
  const box = await card.boundingBox();
  await r.shot(page, 'archives-queued', { x: box.x - 4, y: box.y - 4, width: box.width + 8, height: box.height + 8 });
  await page.__context.close();

  // Command mode, with its help.
  page = await open();
  await page.setViewportSize({ width: VIEW.width, height: 960 });
  await page.getByText('>_ terminal').first().click();
  await sleep(1200);
  await page.keyboard.type('help');
  await page.keyboard.press('Enter');
  await sleep(1200);
  await r.shot(page, 'archives-terminal', { x: 55, y: 185, width: 845, height: 715 });
  await page.__context.close();
};

// 16. The website's update page, as a returning owner whose Fidget isn't
// plugged in. Signed out, the page decides that from this browser's own
// storage, so the scene stores a Fidget record and a stand-in USB port in the
// capture browser (the same way the website's browser tests do); nothing is
// sent anywhere and nothing is installed. Stills: the page; the Install card
// with an earlier version picked; the Advanced section opened (nothing in it
// is pressed). Labels verified on the live page (2026-10-21).
scenes['update-page'] = async (r) => {
  const page = await r.sitePage();
  await page.addInitScript(() => {
    const port = { getPorts: async () => [], requestPort: async () => { throw new DOMException('none', 'NotFoundError'); },
      addEventListener: () => {}, removeEventListener: () => {} };
    Object.defineProperty(Navigator.prototype, 'serial', { configurable: true, get: () => port });
    sessionStorage.setItem('cf_recognized_visit', '1');
    localStorage.setItem('cf_loadout_v1', JSON.stringify({ schemaVersion: 1, deviceId: 'docs-fidget', deviceName: 'My Fidget',
      pairing: { method: 'usb-only', tokenRef: null }, device: { firmware: '1.4.0', storage: { appKB: 3072, usedKB: 0, reportedAt: '2026-10-21' } },
      installed: [], staged: [], lastSync: null }));
  });
  await page.setViewportSize({ width: VIEW.width, height: 1100 });
  await page.goto(r.site + '/update/', { waitUntil: 'networkidle' });
  await page.getByText('Install the update').waitFor();
  await sleep(2500);
  await r.shot(page, 'update-page', { x: 50, y: 100, width: 660, height: 880 });

  // Pick the stable release before the latest one.
  const select = page.locator('select').first();
  const second = await select.evaluate((el) => Array.from(el.options).filter((o) => !/test version/.test(o.textContent))[1]?.value);
  if (second) await select.selectOption(second);
  await sleep(800);
  const card = page.locator('h2', { hasText: 'Install the update' }).locator('xpath=..');
  const cb = await card.boundingBox();
  await r.shot(page, 'update-version', { x: cb.x - 2, y: cb.y - 2, width: cb.width + 4, height: cb.height + 4 });

  await page.locator('summary', { hasText: 'Advanced' }).click();
  await page.getByText('Erase everything and reinstall').first().waitFor();
  await sleep(800);
  const adv = page.locator('summary', { hasText: 'Advanced' }).locator('xpath=..');
  await adv.scrollIntoViewIfNeeded();
  await sleep(400);
  const ab = await adv.boundingBox();
  await r.shot(page, 'update-advanced', { x: ab.x - 2, y: ab.y - 2, width: ab.width + 4, height: ab.height + 4 });
  await page.__context.close();
};

// 17. Real code generator examples. THIS SCENE SPENDS GENERATIONS: it uses the
// signed-out free allowance (three generations) on the site given by --base,
// plus one explanation. Run it on purpose, not as part of `all` on a whim.
// It describes a small app in detail, asks for one change, opens History and
// How it works (Explain this code), then makes a pixel-art sprite app.
// Results differ from run to run: review every still before committing.
const GEN_PET = 'A pocket pet called Blip. Draw a small round creature in the middle of the screen with two eyes that blink every few seconds. '
  + 'It gets hungrier over time: show a hunger bar along the top of the screen. Press the top-right button to feed it: it does a little bounce, '
  + 'the hunger bar refills and it plays a short happy chirp. The LEDs show its mood: green when it is well fed, yellow when it is getting hungry, '
  + 'red when it is starving. Moving the slider changes how fast it gets hungry.';
const GEN_PET_CHANGE = 'Add a sleep mode: when the slider is all the way down, Blip closes its eyes, small Z letters float up from its head, '
  + 'the LEDs fade to a dim blue, and its hunger stops going down until the slider moves up again.';
const GEN_ROCKET = 'Draw a 32 by 24 pixel-art rocket ship as a sprite, with a flame under it that flickers between two animation frames. '
  + 'The rocket flies slowly from left to right across a starfield of twinkling dots and wraps around at the screen edge. '
  + 'Tilting the Fidget forward and back steers it up and down.';
// Send a description and wait for the reply: each applied reply adds a
// "KEPT" marker to the thread.
async function generate(page, text) {
  const kept = () => page.evaluate(() => (document.querySelector('#panel-builder-thread')?.innerText.match(/KEPT/g) || []).length);
  const before = await kept();
  await page.locator('#builder-refine-input').fill(text);
  await page.locator('#builder-refine-btn').click();
  const end = Date.now() + 300000;
  while ((await kept()) <= before) {
    if (Date.now() > end) throw new Error('no reply within 5 minutes');
    await sleep(2000);
  }
  await sleep(3000);
}
scenes['generate-examples'] = async (r) => {
  const page = await r.plainPage();
  await newEmptyProject(page, r.base);
  await page.locator('#builder-project-name').fill('Blip');
  await generate(page, GEN_PET);
  await r.shot(page, 'gen-pet-thread', STUDIO_PANEL);
  await rebuildAndRun(page).catch((e) => console.log('  build: ' + e.message.split('\n')[0]));
  await sleep(5000);
  await r.shot(page, 'gen-pet-emulator', EMU_COLUMN);

  await generate(page, GEN_PET_CHANGE);
  await r.shot(page, 'gen-pet-thread-2', STUDIO_PANEL);
  await rebuildAndRun(page).catch((e) => console.log('  build: ' + e.message.split('\n')[0]));
  await sleep(5000);
  await r.shot(page, 'gen-pet-emulator-2', EMU_COLUMN);

  await page.locator('.builder-surface-tab[data-builder-view="history"]').click();
  await sleep(1500);
  await r.shot(page, 'gen-pet-history', STUDIO_PANEL);

  await page.locator('.builder-surface-tab[data-builder-view="explanation"]').click();
  await sleep(800);
  const explain = page.getByRole('button', { name: /Explain this code/ });
  if (await explain.isVisible()) {
    await explain.click();
    await page.getByText('Explain Deeper').waitFor({ timeout: 240000 });
    await sleep(1500);
  }
  await r.shot(page, 'gen-pet-explain', STUDIO_PANEL);
  await page.__context.close();

  const art = await r.plainPage();
  await newEmptyProject(art, r.base);
  await art.locator('#builder-project-name').fill('Rocket');
  await generate(art, GEN_ROCKET);
  await r.shot(art, 'gen-rocket-thread', STUDIO_PANEL);
  await rebuildAndRun(art).catch((e) => console.log('  build: ' + e.message.split('\n')[0]));
  await sleep(5000);
  await r.shot(art, 'gen-rocket-emulator', EMU_COLUMN);
  await art.__context.close();
};

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.list || opts.scenes.length === 0) {
    console.log('Scenes: ' + Object.keys(scenes).join(', ') + '\nUsage: node capture.mjs <scene>... | all  [--base URL] [--site URL] [--out DIR] [--headed]');
    return;
  }
  // Scenes that spend generations only run when named, never as part of `all`.
  const costly = new Set(['generate-examples']);
  const names = opts.scenes.includes('all') ? Object.keys(scenes).filter((n) => !costly.has(n)) : opts.scenes;
  for (const n of names) if (!scenes[n]) throw new Error('Unknown scene ' + n + '. Scenes: ' + Object.keys(scenes).join(', '));
  fs.mkdirSync(opts.out, { recursive: true });

  const { chromium } = await loadPlaywright();
  const browser = await chromium.launch({ headless: !opts.headed });
  const runner = new Runner(browser, opts.base, opts.out, opts.site);
  let failed = 0;
  for (const n of names) {
    console.log('Scene ' + n);
    try {
      await scenes[n](runner);
    } catch (e) {
      failed++;
      console.log('  FAILED: ' + e.message.split('\n')[0]);
      // The scene line that failed, so the step is easy to find.
      const at = (e.stack || '').split('\n').find((l) => l.includes('capture.mjs'));
      if (at) console.log('  at ' + at.trim());
    }
  }
  await browser.close();
  console.log(failed ? failed + ' scene(s) failed' : 'Done');
  process.exitCode = failed ? 1 : 0;
}

main().catch((e) => { console.error(e.message); process.exit(1); });

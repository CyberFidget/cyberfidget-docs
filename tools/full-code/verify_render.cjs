// SPDX-License-Identifier: GPL-3.0-or-later
// Optional browser QA for the built documentation. See README.md for invocation.
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const http = require('node:http');
const path = require('node:path');
const { createRequire } = require('node:module');

async function main() {
  const [siteArg, outputArg, playwrightPackage] = process.argv.slice(2);
  if (!siteArg || !outputArg || !playwrightPackage) {
    throw new Error('Usage: node verify_render.cjs SITE OUTPUT PLAYWRIGHT_PACKAGE_JSON');
  }
  const site = path.resolve(siteArg);
  const output = path.resolve(outputArg);
  const { chromium } = createRequire(path.resolve(playwrightPackage))('playwright');
  await fs.mkdir(output, { recursive: true });
  const server = http.createServer(async (req, res) => {
    const uri = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    const file = path.resolve(site, '.' + uri, uri.endsWith('/') ? 'index.html' : '');
    if (!file.startsWith(site + path.sep)) {
      res.writeHead(403).end();
      return;
    }
    try {
      const mime = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png' };
      res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
      res.end(await fs.readFile(file));
    } catch {
      res.writeHead(404).end();
    }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  const results = [];
  try {
    browser = await chromium.launch({ executablePath: process.env.CF_CHROMIUM_EXECUTABLE_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
    for (const width of [1440, 390]) {
      const page = await browser.newPage({ viewport: { width, height: 1000 } });
      // Keep the visual check local and deterministic, including on offline machines.
      await page.route('**/*', route => new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort());
      for (const uri of ['concepts/buttons/', 'reference/functions/', 'getting-started/make-a-game/',
                         'concepts/app-lifecycle/', 'concepts/update-loop/', 'concepts/display/',
                         'concepts/audio/', 'concepts/leds/', 'concepts/slider/', 'concepts/accelerometer/',
                         'concepts/sprites/', 'getting-started/first-app/', 'software/apps/', 'software/ota-builder/']) {
        await page.goto(`http://127.0.0.1:${server.address().port}/${uri}`, { waitUntil: 'networkidle' });
        const slug = uri.split('/').filter(Boolean).pop();
        const measure = async state => {
          const size = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
          assert.ok(size.document <= width, `${uri} ${state} overflows at ${width}: ${JSON.stringify(size)}`);
          results.push({ uri, width, state, ...size });
        };
        await measure('initial');
        const advanced = page.locator('.admonition.advanced').first();
        if (await advanced.count()) {
          await advanced.scrollIntoViewIfNeeded();
          assert.equal(await advanced.evaluate(el => el.tagName), 'DIV');
          if (slug === 'buttons') {
            await page.waitForTimeout(350);
            await page.screenshot({ path: path.join(output, `${slug}-advanced-${width}.png`) });
          }
        }
        const details = page.locator('details.example').filter({ has: page.locator('summary', { hasText: 'Full code for this step' }) });
        if (uri.includes('buttons') || uri.includes('make-a-game')) {
          assert.ok(await details.count());
          const first = details.first();
          assert.equal(await first.getAttribute('open'), null);
          await first.locator('summary').click();
          await first.evaluate(el => el.scrollIntoView({ block: 'start' }));
          await page.evaluate(() => scrollBy(0, -80));
          assert.ok(await first.locator('.hll').count());
          assert.ok((await first.textContent()).includes('MyApp.cpp'));
          await measure('solution open');
          await page.waitForTimeout(350);
          await page.screenshot({ path: path.join(output, `${slug}-solution-${width}.png`) });
        }
        if (uri.includes('functions')) {
          await page.locator('#reading-the-signatures').evaluate(el => el.scrollIntoView({ block: 'start' }));
          await page.evaluate(() => scrollBy(0, -80));
          await page.waitForTimeout(350);
          await page.screenshot({ path: path.join(output, `reference-types-${width}.png`) });
          await page.locator('#symbol-hal--setrgbled').scrollIntoViewIfNeeded();
          const row = page.locator('tr').filter({ has: page.locator('#symbol-hal--setrgbled') });
          assert.ok((await row.textContent()).includes('void HAL::setRgbLed(int index, uint8_t r, uint8_t g, uint8_t b, uint8_t w)'));
          assert.ok((await row.locator('small').textContent()).includes('Example:'));
          await page.waitForTimeout(350);
          await page.screenshot({ path: path.join(output, `reference-signatures-${width}.png`) });
        }
      }
      await page.close();
    }
    await fs.writeFile(path.join(output, 'browser-results.json'), JSON.stringify(results, null, 2));
    console.log(JSON.stringify(results, null, 2));
  } finally {
    if (browser) await browser.close();
    server.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });

// SPDX-License-Identifier: GPL-3.0-or-later
// Live check on the Supported browsers page: asks this browser, right now,
// whether it offers the USB connection the website uses to reach a Cyber
// Fidget. It only tests that the browser offers it; Android phones offer it
// but connecting a Fidget there isn't confirmed, so they get a warning.
(() => {
  const ICONS = {
    pass: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>',
    fail: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 6.4 17.6 5 12 10.6 6.4 5 5 6.4 10.6 12 5 17.6 6.4 19 12 13.4 17.6 19 19 17.6 13.4 12z"/></svg>',
    warn: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
  };

  function result() {
    const hasUsb = 'serial' in navigator;
    const android = /Android/i.test(navigator.userAgent);
    if (hasUsb && android) {
      return { kind: 'warn', text: "This browser offers a USB connection, but connecting your Cyber Fidget over USB from an Android phone may not work. Set it up over WiFi instead (see below)." };
    }
    if (hasUsb) {
      return { kind: 'pass', text: 'This browser can connect to your Cyber Fidget over USB.' };
    }
    return { kind: 'fail', text: "This browser can't connect over USB. Use a computer with Chrome, Edge or Firefox for the USB features, or set up your Fidget over WiFi." };
  }

  function run(box) {
    box.className = 'cf-usb-check cf-usb-check--checking';
    box.querySelector('.cf-usb-check__icon').innerHTML = '';
    box.querySelector('.cf-usb-check__when').textContent = '';
    box.querySelector('.cf-usb-check__text').textContent = 'Checking this browser...';
    box.querySelector('button').disabled = true;
    setTimeout(() => {
      const r = result();
      const now = new Date();
      box.className = 'cf-usb-check cf-usb-check--' + r.kind;
      box.querySelector('.cf-usb-check__icon').innerHTML = ICONS[r.kind];
      box.querySelector('.cf-usb-check__when').textContent = 'Checked just now in this browser (' + now.toLocaleTimeString() + '):';
      box.querySelector('.cf-usb-check__text').textContent = r.text;
      box.querySelector('button').disabled = false;
    }, 700);
  }

  function init() {
    document.querySelectorAll('[data-cf-usb-check]').forEach((box) => {
      box.innerHTML = '<span class="cf-usb-check__icon"></span>'
        + '<span class="cf-usb-check__body"><span class="cf-usb-check__when"></span> <span class="cf-usb-check__text"></span></span>'
        + '<button type="button" class="md-button cf-usb-check__again">Check again</button>';
      box.querySelector('button').addEventListener('click', () => run(box));
      run(box);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

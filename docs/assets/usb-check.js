// SPDX-License-Identifier: GPL-3.0-or-later
(() => {
  function init() {
    document.querySelectorAll('[data-cf-usb-check]').forEach((box) => {
      box.textContent = 'serial' in navigator
        ? 'This browser can connect to your Cyber Fidget over USB.'
        : "This browser can't connect over USB. Use a computer with Chrome, Edge or Firefox for the USB features, or set up your Fidget over WiFi.";
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

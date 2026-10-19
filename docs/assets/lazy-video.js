// SPDX-License-Identifier: GPL-3.0-or-later
(() => {
  function init() {
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const videos = [...document.querySelectorAll('video')];
    const visible = new Set();

    function update(video) {
      if (motion.matches) {
        video.removeAttribute('autoplay');
        video.controls = true;
        video.pause();
      } else if (visible.has(video)) {
        video.controls = false;
        video.play().catch(() => { video.controls = true; });
      } else {
        video.pause();
      }
    }

    // Deferred clips have no controls in the markup: without JavaScript the
    // reader sees the poster still. This script adds controls where needed.
    // Only an intersecting clip receives a source; reduced motion keeps
    // its controls for manual playback instead of starting it automatically.
    const observer = 'IntersectionObserver' in window ? new IntersectionObserver(entries => {
      for (const entry of entries) {
        const video = entry.target;
        if (entry.isIntersecting) {
          visible.add(video);
          if (video.dataset.src && !video.hasAttribute('src')) {
            video.src = video.dataset.src;
            video.load();
          }
        } else {
          visible.delete(video);
        }
        update(video);
      }
    }) : null;

    for (const video of videos) {
      if (motion.matches) {
        update(video);
        // The opening clip has a native autoplay attribute. Reset it after
        // removing that attribute so its poster replaces any started frame.
        video.preload = 'none';
        if (!video.dataset.src) video.load();
      }
      if (!video.dataset.src && observer) {
        // Opening clips autoplay natively. Watch them too, so a blocked
        // autoplay (e.g. a phone in low-power mode) falls back to controls.
        observer.observe(video);
      } else if (video.dataset.src) {
        if (observer) {
          video.controls = motion.matches;
          observer.observe(video);
        } else {
          // Without an observer, keep playback manual and defer fetching
          // until the reader uses the controls (preload stays "none").
          video.src = video.dataset.src;
          video.controls = true;
        }
      }
    }
    motion.addEventListener('change', () => {
      for (const video of videos) {
        if (!observer && !video.dataset.src && !motion.matches) visible.add(video);
        update(video);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

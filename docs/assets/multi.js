// multi.js — simple multi-image per step with hover/click swap
// Authoring:
// <div class="cf-step-gallery">
//   <img class="cf-main" src="./img1.jpg" alt="">
//   <div class="cf-thumbs">
//     <img src="./img1.jpg" alt="">
//     <img src="./img2.jpg" alt="">
//     <img src="./img3.jpg" alt="">
//   </div>
// </div>
//
// Hover or click a thumb to swap the main image. Works with guide.js annotations
// if each main image has its own <!-- guide:annot src="..."> comment placed
// right after it in the Markdown.

// multi.js — swap main image on hover/click + notify guide.js to reload annotations
(function(){
  function ready(fn){ document.readyState!=='loading' ? fn() : document.addEventListener('DOMContentLoaded', fn); }

  // Derive ../.../file.annot.json from an image URL (same folder as the image)
  function annotFor(imgUrl){
    try {
      const u = new URL(imgUrl, document.baseURI);
      const dot = u.pathname.lastIndexOf('.');
      if (dot > -1) u.pathname = u.pathname.slice(0, dot) + '.annot.json';
      else u.pathname = u.pathname + '.annot.json';
      return u.pathname + u.search + u.hash;
    } catch { // relative URL string
      return imgUrl.replace(/\.[^.]+$/, '') + '.annot.json';
    }
  }

  function notifyAnnotChange(img){
    // Prefer explicit data-annot-src, else infer it from current main src
    const src = img.getAttribute('data-annot-src') || annotFor(img.src);
    img.setAttribute('data-annot-src', src);
    const ev = new CustomEvent('cf-annot-change', { detail: { img, src }});
    document.dispatchEvent(ev);
  }

  ready(()=>{
    document.querySelectorAll('.cf-step-gallery').forEach(gal => {
      const main = gal.querySelector('.cf-main');
      const thumbs = gal.querySelectorAll('.cf-thumbs img');
      if (!main || !thumbs.length) return;

      // initial active
      thumbs.forEach((t,i)=>{ if(i===0) t.classList.add('active'); });

      const link = gal.querySelector('a.cf-zoom') || (() => {
        const a = document.createElement('a');
        a.className = 'cf-zoom'; a.target = '_blank'; a.rel='noopener';
        main.parentNode.insertBefore(a, main);
        a.appendChild(main);
        return a;
      })();

      function activate(thumb){
        thumbs.forEach(t=>t.classList.toggle('active', t===thumb));
        main.src = thumb.src;
        link.href = thumb.src;  // <-- enable click-to-open full size
        const annot = annotFor(thumb.src);
        main.setAttribute('data-annot-src', annot);

        const ev = new CustomEvent('cf-annot-change', { detail: { img: main, src: annot } });
        document.dispatchEvent(ev);
      }

      // initialize annot src for first image
      if (!main.getAttribute('data-annot-src')) {
        main.setAttribute('data-annot-src', annotFor(main.src));
      }
      notifyAnnotChange(main);

      thumbs.forEach(t => {
        t.addEventListener('mouseenter', ()=>activate(t));
        t.addEventListener('click', ()=>activate(t));
      });
    });
  });
})();


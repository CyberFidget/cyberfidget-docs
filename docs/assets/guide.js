
// guide.js — render annotations (pins, boxes, circles, arrows) on images
(function(){
  function ready(fn){ document.readyState!=='loading' ? fn() : document.addEventListener('DOMContentLoaded', fn); }
  function fetchJSON(url){ return fetch(url, {cache:'no-store'}).then(r=>{ if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); }); }

  function normData(d){
    d = d || {};
    return {
      pins: Array.isArray(d.pins) ? d.pins : [],
      boxes: Array.isArray(d.boxes) ? d.boxes : [],
      circles: Array.isArray(d.circles) ? d.circles : [],
      arrows: Array.isArray(d.arrows) ? d.arrows : []
    };
  }

  function createOverlay(img, data){
    let wrap = img.closest('.cf-annot-wrap');
      if (!wrap){
        wrap = document.createElement('span');
        wrap.className = 'cf-annot-wrap';
        img.parentNode.insertBefore(wrap, img);
        wrap.appendChild(img);
      }

    // remove any existing overlay to prevent duplicates
    const old = wrap.querySelector('svg.cf-annot-overlay');
    if (old) old.remove();

    // store normalized data on wrapper for redraw()
    wrap.__annotData = normData(data);

    wrap.style.position = 'relative';
    wrap.style.display = 'inline-block';

    // build svg overlay
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('cf-annot-overlay');
    svg.style.position = 'absolute';
    svg.style.top = 0; svg.style.left = 0;
    svg.style.pointerEvents = 'none';          // <-- allow clicks to pass to the link
    svg.setAttribute('aria-hidden', 'true');
    wrap.style.position = 'relative';
    wrap.appendChild(svg);

    const defs = document.createElementNS('http://www.w3.org/2000/svg','defs');
    const marker = document.createElementNS('http://www.w3.org/2000/svg','marker');
    marker.setAttribute('id','cf-arrowhead'); marker.setAttribute('markerWidth','10');
    marker.setAttribute('markerHeight','7'); marker.setAttribute('refX','10'); marker.setAttribute('refY','3.5'); marker.setAttribute('orient','auto');
    const poly = document.createElementNS('http://www.w3.org/2000/svg','polygon');
    poly.setAttribute('points','0 0, 10 3.5, 0 7'); poly.setAttribute('fill','#e53935');
    marker.appendChild(poly); defs.appendChild(marker); svg.appendChild(defs);

    function redraw(img){
      const wrap = img.closest('.cf-annot-wrap'); if (!wrap) return;
      const svg = wrap.querySelector('svg.cf-annot-overlay'); if (!svg) return;
      const W = img.clientWidth || img.naturalWidth, H = img.clientHeight || img.naturalHeight;
      svg.setAttribute('width', W); svg.setAttribute('height', H);
      while (svg.firstChild) svg.removeChild(svg.firstChild);

      const d = normData(wrap.__annotData);
      if (!d.pins.length && !d.boxes.length && !d.circles.length && !d.arrows.length) return;

      const rect = img.getBoundingClientRect();
      svg.setAttribute('viewBox', `0 0 ${rect.width} ${rect.height}`);
      while (svg.lastChild && svg.lastChild.tagName !== 'defs' && svg.childNodes.length>1) svg.removeChild(svg.lastChild);

      // pins
      (data.pins||[]).forEach((p, i) => {
        const cx = p.x * rect.width, cy = p.y * rect.height;
        const g = document.createElementNS('http://www.w3.org/2000/svg','g');
        const circle = document.createElementNS('http://www.w3.org/2000/svg','circle');
        circle.setAttribute('cx', cx); circle.setAttribute('cy', cy); circle.setAttribute('r', 10);
        circle.setAttribute('fill', '#1976d2'); circle.setAttribute('opacity', '0.9');
        const text = document.createElementNS('http://www.w3.org/2000/svg','text');
        text.setAttribute('x', cx); text.setAttribute('y', cy+4); text.setAttribute('text-anchor','middle');
        text.setAttribute('font-size','12'); text.setAttribute('fill','#fff');
        text.textContent = (i+1).toString();
        const title = document.createElementNS('http://www.w3.org/2000/svg','title');
        title.textContent = p.label || `Pin ${i+1}`;
        g.appendChild(title); g.appendChild(circle); g.appendChild(text);
        svg.appendChild(g);
      });

      // boxes
      (data.boxes||[]).forEach((b) => {
        const x = b.x * rect.width, y = b.y * rect.height;
        const w = b.w * rect.width, h = b.h * rect.height;
        const r = document.createElementNS('http://www.w3.org/2000/svg','rect');
        r.setAttribute('x', x); r.setAttribute('y', y); r.setAttribute('width', w); r.setAttribute('height', h);
        r.setAttribute('fill', 'rgba(255,165,0,0.15)'); r.setAttribute('stroke','#ffa500'); r.setAttribute('stroke-width','2');
        const title = document.createElementNS('http://www.w3.org/2000/svg','title');
        title.textContent = b.label || 'Box';
        r.appendChild(title);
        svg.appendChild(r);
      });

      // circles
      (data.circles||[]).forEach((c) => {
        const cx = c.cx * rect.width, cy = c.cy * rect.height;
        const rr = c.r * rect.width;
        const cc = document.createElementNS('http://www.w3.org/2000/svg','circle');
        cc.setAttribute('cx', cx); cc.setAttribute('cy', cy); cc.setAttribute('r', rr);
        cc.setAttribute('fill', 'rgba(76,175,80,0.12)'); cc.setAttribute('stroke','#4caf50'); cc.setAttribute('stroke-width','2');
        const title = document.createElementNS('http://www.w3.org/2000/svg','title');
        title.textContent = c.label || 'Circle';
        cc.appendChild(title);
        svg.appendChild(cc);
      });

      // arrows
      (data.arrows||[]).forEach((a) => {
        if (!a.points || a.points.length < 2) return;
        const pts = a.points.map(p => `${p.x * rect.width},${p.y * rect.height}`).join(' ');
        const path = document.createElementNS('http://www.w3.org/2000/svg','polyline');
        path.setAttribute('points', pts); path.setAttribute('fill','none');
        path.setAttribute('stroke','#e53935'); path.setAttribute('stroke-width','3');
        path.setAttribute('marker-end','url(#cf-arrowhead)');
        const title = document.createElementNS('http://www.w3.org/2000/svg','title');
        title.textContent = a.label || 'Arrow';
        path.appendChild(title);
        svg.appendChild(path);
      });
    }

    const ro = new ResizeObserver(() => redraw(img));
    ro.observe(img);
    redraw(img);
  }

  function findCommentAnchors() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_COMMENT, null);
    const anchors = [];
    let node;
    while ((node = walker.nextNode())) {
      const m = (node.nodeValue||'').match(/\bguide:annot\s+src=["']([^"']+)["']/);
      if (m) {
        let prev = node.previousSibling;
        while (prev && prev.nodeType !== Node.ELEMENT_NODE) prev = prev.previousSibling;
        let img = null;
        if (prev) { if (prev.tagName && prev.tagName.toLowerCase() === 'img') img = prev; else img = prev.querySelector ? prev.querySelector('img') : null; }
        if (!img) { const imgs = Array.from(document.images); img = imgs[imgs.length-1] || null; }
        if (img) anchors.push({ img, src: m[1] });
      }
    }
    document.querySelectorAll('img[data-annot-src]').forEach(img => { anchors.push({ img, src: img.getAttribute('data-annot-src') }); });
    return anchors;
  }

  async function fetchJSON(url){
    const r = await fetch(url, {cache:'no-store'});
    if (r.status === 404) return null;        // treat as "no overlay"
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }

  function removeOverlay(img){
    const wrap = img.closest('.cf-annot-wrap');
    if (!wrap) return;
    const svg = wrap.querySelector('svg.cf-annot-overlay');
    if (svg) svg.remove();
    wrap.__annotData = { pins:[], boxes:[], circles:[], arrows:[] };
    // Very important: allow recreate on next load
    delete img.__cfProcessed;
  }

  let __cfReqSeq = 0;

  function ensureOverlay(img, jsonUrl){
    const mySeq = ++__cfReqSeq;
    img.__cfLastSeq = mySeq;

    fetchJSON(jsonUrl).then(data => {
      // If a newer request happened, ignore this response
      if (img.__cfLastSeq !== mySeq) return;

      if (data === null){
        // No annotations for this image: clear anything lingering
        removeOverlay(img);
        return;
      }

      const wrap = img.closest('.cf-annot-wrap');

      // If we have no wrapper yet, or we removed the SVG earlier, recreate it
      if (!wrap || !wrap.querySelector('svg.cf-annot-overlay') || !img.__cfProcessed){
        createOverlay(img, data);
        img.__cfProcessed = true;
        return;
      }

      // Update existing overlay data and redraw
      wrap.__annotData = {
        pins: Array.isArray(data.pins) ? data.pins : [],
        boxes: Array.isArray(data.boxes) ? data.boxes : [],
        circles: Array.isArray(data.circles) ? data.circles : [],
        arrows: Array.isArray(data.arrows) ? data.arrows : []
      };
      redraw(img);
    }).catch(()=>{/* ignore */});
  }


  ready(()=>{
    findCommentAnchors().forEach(({img, src}) => ensureOverlay(img, src));
  });

  // --- dynamic reload: when multi.js swaps the main image
  document.addEventListener('cf-annot-change', (e)=>{
    const img = e.detail?.img;
    const src = e.detail?.src || img?.getAttribute('data-annot-src');
    if (!img || !src) return;
    // Clear immediately so nothing lingers while we fetch the new file
    removeOverlay(img);
    ensureOverlay(img, src);
  });
})();

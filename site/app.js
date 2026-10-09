(function () {
  // Mobile menu
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.menu-toggle');
  if (toggle && header) {
    toggle.addEventListener('click', function () {
      var open = header.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  document.querySelectorAll('.sub-toggle').forEach(function (b) {
    b.addEventListener('click', function () {
      var li = b.parentElement;
      var open = li.classList.toggle('open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // Images that cannot load (e.g. when hotlinking is blocked) fold away quietly.
  function markMissing(img) {
    img.classList.add('img-missing');
    var m = img.closest('.media');
    if (m) m.classList.add('missing');
  }
  document.querySelectorAll('img').forEach(function (img) {
    if (img.complete && img.naturalWidth === 0 && img.getAttribute('src')) markMissing(img);
    img.addEventListener('error', function () { markMissing(img); });
  });
  var logo = document.querySelector('.brand img');
  if (logo) {
    var noLogo = function () { logo.closest('.brand').classList.add('no-logo'); };
    if (logo.complete && logo.naturalWidth === 0) noLogo();
    logo.addEventListener('error', noLogo);
  }

})();

// Boot hotspots: a dot and its zone in the list light up together; the dot shows the zone's text in a small card.
(function () {
  var box = document.querySelector('.hotspots');
  if (!box) return;
  var tip = box.querySelector('.hs-tip');
  var dots = box.querySelectorAll('.hs');
  var pinned = null;
  function zoneEl(z) { return document.getElementById('zone-' + z); }
  function show(dot) {
    dots.forEach(function (d) { d.classList.toggle('on', d === dot); d.setAttribute('aria-expanded', d === dot ? 'true' : 'false'); });
    document.querySelectorAll('.zone').forEach(function (z) { z.classList.toggle('on', dot && z.dataset.zone === dot.dataset.zone); });
    if (!dot) { tip.hidden = true; return; }
    var z = zoneEl(dot.dataset.zone);
    tip.innerHTML = z ? z.innerHTML : '';
    tip.hidden = false;
    var bw = box.clientWidth, bh = box.clientHeight;
    var x = dot.offsetLeft, y = dot.offsetTop, tw = tip.offsetWidth, th = tip.offsetHeight;
    var left = x + 26 + tw > bw ? x - 26 - tw : x + 26;
    var top = Math.min(Math.max(y - th / 2, 0), bh - th);
    tip.style.left = Math.max(0, left) + 'px'; tip.style.top = top + 'px';
  }
  dots.forEach(function (d) {
    d.addEventListener('mouseenter', function () { if (!pinned) show(d); });
    d.addEventListener('mouseleave', function () { if (!pinned) show(null); });
    d.addEventListener('focus', function () { show(d); });
    d.addEventListener('blur', function () { if (!pinned) show(null); });
    d.addEventListener('click', function (e) { e.stopPropagation(); pinned = pinned === d ? null : d; show(pinned || d); if (!pinned) show(null); });
  });
  document.addEventListener('click', function () { if (pinned) { pinned = null; show(null); } });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { pinned = null; show(null); } });
  document.querySelectorAll('.zone').forEach(function (z) {
    var dot = box.querySelector('.hs[data-zone="' + z.dataset.zone + '"]');
    z.addEventListener('mouseenter', function () { if (!pinned && dot) show(dot); });
    z.addEventListener('mouseleave', function () { if (!pinned) show(null); });
  });
})();

(function () {
  // The announcement line folds away once the page scrolls; on the home the bar also turns solid.
  var body = document.body;
  var onScroll = function () { body.classList.toggle('scrolled', window.scrollY > 40); };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
  // Gentle reveal of sections and cards as they enter the viewport.
  if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var els = document.querySelectorAll('.section .wrap > *, .choice, .card, .price, .quote, .isnot > div');
  if (!els.length) return;
  document.documentElement.classList.add('js-reveal');
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px' });
  els.forEach(function (el) { el.classList.add('reveal'); io.observe(el); });
})();

// Respect reduced motion: keep the hero clip on its poster frame.
if (matchMedia('(prefers-reduced-motion: reduce)').matches) document.querySelectorAll('.hero-video video').forEach(v => { v.removeAttribute('autoplay'); v.pause(); });

// Home shop strip: arrow buttons page through the photos (Canary-style card rail).
(function () {
  var track = document.querySelector('.strip-track');
  if (!track) return;
  function step(dir) {
    var card = track.querySelector('figure');
    var w = card ? card.getBoundingClientRect().width + 16 : track.clientWidth * .8;
    track.scrollBy({ left: dir * w, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }
  var prev = document.querySelector('.strip-btn.prev'), next = document.querySelector('.strip-btn.next');
  function sync() {
    if (prev) prev.disabled = track.scrollLeft < 4;
    if (next) next.disabled = track.scrollLeft + track.clientWidth > track.scrollWidth - 4;
  }
  if (prev) prev.addEventListener('click', function () { step(-1); });
  if (next) next.addEventListener('click', function () { step(1); });
  track.addEventListener('scroll', sync, { passive: true });
  window.addEventListener('resize', sync);
  sync();
})();

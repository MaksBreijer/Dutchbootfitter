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

  // Topographic contour lines: a deterministic noise field traced with marching squares.
  function hash(x, y, s) { var h = Math.sin(x * 127.1 + y * 311.7 + s * 74.7) * 43758.5453; return h - Math.floor(h); }
  function smooth(t) { return t * t * (3 - 2 * t); }
  function noise(x, y, s) {
    var xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
    var a = hash(xi, yi, s), b = hash(xi + 1, yi, s), c = hash(xi, yi + 1, s), d = hash(xi + 1, yi + 1, s);
    var u = smooth(xf), v = smooth(yf);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }
  function field(x, y, s) { return noise(x, y, s) * .6 + noise(x * 2.1, y * 2.1, s + 3) * .3 + noise(x * 4.3, y * 4.3, s + 7) * .1; }
  function draw(cv) {
    var r = cv.getBoundingClientRect();
    if (!r.width || !r.height) return;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.width = r.width * dpr; cv.height = r.height * dpr;
    var ctx = cv.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.strokeStyle = getComputedStyle(cv).color;
    ctx.lineWidth = 1;
    var seed = parseFloat(cv.dataset.seed || '1');
    var step = 14, cols = Math.ceil(r.width / step) + 1, rows = Math.ceil(r.height / step) + 1, sc = 1 / 170;
    var g = [];
    for (var j = 0; j <= rows; j++) { g[j] = []; for (var i = 0; i <= cols; i++) g[j][i] = field(i * step * sc, j * step * sc, seed); }
    ctx.beginPath();
    for (var lv = 0.18; lv < 0.95; lv += 0.045) {
      for (j = 0; j < rows; j++) for (i = 0; i < cols; i++) {
        var a = g[j][i], b = g[j][i + 1], c = g[j + 1][i + 1], d = g[j + 1][i];
        var x = i * step, y = j * step, pts = [];
        function e(p, q, x1, y1, x2, y2) { if ((p < lv) !== (q < lv)) { var t = (lv - p) / (q - p); pts.push([x1 + (x2 - x1) * t, y1 + (y2 - y1) * t]); } }
        e(a, b, x, y, x + step, y); e(b, c, x + step, y, x + step, y + step); e(d, c, x, y + step, x + step, y + step); e(a, d, x, y, x, y + step);
        for (var k = 0; k + 1 < pts.length; k += 2) { ctx.moveTo(pts[k][0], pts[k][1]); ctx.lineTo(pts[k + 1][0], pts[k + 1][1]); }
      }
    }
    ctx.stroke();
  }
  var canvases = document.querySelectorAll('canvas.contours');
  function all() { canvases.forEach(draw); }
  all();
  var t; window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(all, 150); });
  if (window.matchMedia) {
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    if (mq.addEventListener) mq.addEventListener('change', all);
  }
  new MutationObserver(all).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
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

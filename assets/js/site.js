/* aduttya.com: site.js. Plain JS, no dependencies. */

/* Where the paper's email form posts. Empty = skip the POST and just
   download. Set to a Formspree / Apps Script / Basin URL later. */
var FORM_ENDPOINT = '';

var PAPER_PDF = '/beyond-rankings-measuring-vendor-visibility-in-ai-driven-discovery.pdf';
var DL_KEY = 'aduttya_dl';
var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function store(get, val) {
  try {
    if (get) return localStorage.getItem(DL_KEY) === '1';
    localStorage.setItem(DL_KEY, val);
  } catch (e) { return false; }
}

/* ── Rails: prev/next by one card, disabled at the ends, hidden when it all fits ── */
(function () {
  document.querySelectorAll('[data-rail]').forEach(function (box) {
    var rail = box.querySelector('.rp-rail'), nav = box.querySelector('.rp-arrows');
    if (!rail || !nav) return;
    var b = nav.querySelectorAll('button');
    function sync() {
      var max = rail.scrollWidth - rail.clientWidth;
      nav.hidden = max < 8;
      b[0].disabled = rail.scrollLeft < 8;
      b[1].disabled = rail.scrollLeft > max - 8;
    }
    function step(d) {
      var c = rail.firstElementChild;
      var gap = parseFloat(getComputedStyle(rail).columnGap) || 24;
      rail.scrollBy({ left: d * ((c ? c.offsetWidth : 300) + gap), behavior: reduceMotion ? 'auto' : 'smooth' });
    }
    b[0].addEventListener('click', function () { step(-1); });
    b[1].addEventListener('click', function () { step(1); });
    rail.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', sync);
    sync();
  });
})();

/* ── Paper gate: email, then download. A courtesy, not security: the PDF URL is public. ── */
(function () {
  var gates = document.querySelectorAll('[data-gate]');
  if (!gates.length) return;

  function download() {
    var a = document.createElement('a');
    a.href = PAPER_PDF;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  if (store(true)) gates.forEach(function (g) { g.setAttribute('data-state', 'direct'); });

  gates.forEach(function (gate) {
    var form = gate.querySelector('form');
    if (!form) return;
    var err = gate.querySelector('.rp-err');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type=email]');
      var email = (input.value || '').trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
        if (err) err.textContent = 'Please enter a valid email address.';
        input.setAttribute('aria-invalid', 'true');
        input.focus();
        return;
      }
      if (err) err.textContent = '';
      input.removeAttribute('aria-invalid');

      if (FORM_ENDPOINT) {
        var fd = new FormData();
        fd.append('email', email);
        fd.append('opt_in', form.querySelector('input[name=opt_in]') && form.querySelector('input[name=opt_in]').checked ? 'yes' : 'no');
        fd.append('paper', 'beyond-rankings');
        fd.append('page', location.pathname);
        try {
          fetch(FORM_ENDPOINT, { method: 'POST', body: fd, mode: 'no-cors', keepalive: true }).catch(function () {});
        } catch (x) {}
      }

      store(false, '1');
      document.querySelectorAll('[data-gate]').forEach(function (g) { g.setAttribute('data-state', 'done'); });
      var done = gate.querySelector('.rp-gate-done');
      if (done) { done.setAttribute('tabindex', '-1'); done.focus({ preventScroll: true }); }
      download();
    });
  });
})();

/* ── Modal: opened by any [data-dl-open] link. The link itself points at the PDF,
      so it still works with JS off, and on repeat visits it just downloads. ── */
(function () {
  var m = document.getElementById('rp-modal');
  if (!m) return;
  var card = m.querySelector('.rp-modal-card');
  var last = null;

  function focusables() {
    return Array.prototype.filter.call(
      card.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),[tabindex]:not([tabindex="-1"])'),
      function (el) { return el.offsetParent !== null; }
    );
  }
  function open(trigger) {
    last = trigger;
    m.classList.add('rp-open');
    m.setAttribute('aria-hidden', 'false');
    document.body.classList.add('rp-lock');
    var i = m.querySelector('input[type=email]');
    setTimeout(function () { (i && i.offsetParent ? i : card.querySelector('.rp-modal-x')).focus(); }, 30);
  }
  function close() {
    if (!m.classList.contains('rp-open')) return;
    m.classList.remove('rp-open');
    m.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('rp-lock');
    if (last) last.focus();
  }

  document.querySelectorAll('[data-dl-open]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (store(true)) return;
      e.preventDefault();
      open(a);
    });
  });
  m.addEventListener('click', function (e) {
    if (e.target === m || e.target.closest('.rp-modal-x')) close();
  });
  document.addEventListener('keydown', function (e) {
    if (!m.classList.contains('rp-open')) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    if (e.key !== 'Tab') return;
    var f = focusables();
    if (!f.length) return;
    var first = f[0], lastEl = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); lastEl.focus(); }
    else if (!e.shiftKey && document.activeElement === lastEl) { e.preventDefault(); first.focus(); }
  });
})();

/* ── Copy buttons (citation block) ── */
(function () {
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    var src = document.getElementById(btn.getAttribute('data-copy'));
    if (!src || !navigator.clipboard) { btn.hidden = true; return; }
    var label = btn.textContent;
    btn.addEventListener('click', function () {
      navigator.clipboard.writeText(src.innerText.trim()).then(function () {
        btn.textContent = 'Copied';
        setTimeout(function () { btn.textContent = label; }, 1800);
      });
    });
  });
})();

/* ── Post: "On this page" built from the article's H2s ── */
(function () {
  var toc = document.querySelector('[data-toc]');
  var body = document.querySelector('[data-toc-src]');
  if (!toc || !body) return;
  var heads = body.querySelectorAll('h2');
  if (heads.length < 2) return;
  var list = toc.querySelector('ol');
  var links = [];
  heads.forEach(function (h, i) {
    if (!h.id) h.id = 'section-' + (i + 1);
    var li = document.createElement('li');
    var a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent;
    li.appendChild(a);
    list.appendChild(li);
    links.push(a);
  });
  toc.hidden = false;
  if (!('IntersectionObserver' in window)) return;
  var current = null;
  function mark(i) {
    if (current === i) return;
    if (current !== null) links[current].removeAttribute('aria-current');
    links[i].setAttribute('aria-current', 'true');
    current = i;
  }
  var io = new IntersectionObserver(function () {
    var y = window.innerHeight * 0.3, idx = 0;
    heads.forEach(function (h, i) { if (h.getBoundingClientRect().top < y) idx = i; });
    mark(idx);
  }, { rootMargin: '0px 0px -60% 0px', threshold: [0, 1] });
  heads.forEach(function (h) { io.observe(h); });
  window.addEventListener('scroll', function () {
    var y = window.innerHeight * 0.3, idx = 0;
    heads.forEach(function (h, i) { if (h.getBoundingClientRect().top < y) idx = i; });
    mark(idx);
  }, { passive: true });
  mark(0);
})();

/* ── Hero halftone: bone dots on ink with a faint orange streak.
      Paused off screen, drawn once under reduced motion. ── */
(function () {
  var c = document.querySelector('.rp-ht');
  if (!c || !c.getContext) return;
  var ctx = c.getContext('2d');
  var css = getComputedStyle(document.documentElement);
  function rgb(name) {
    var h = css.getPropertyValue(name).trim().replace('#', '');
    return [parseInt(h.substr(0, 2), 16), parseInt(h.substr(2, 2), 16), parseInt(h.substr(4, 2), 16)];
  }
  var BONE = rgb('--bone'), ORANGE = rgb('--orange');
  var W = 0, H = 0, dpr = 1, t = 0, raf = 0, visible = true, lastTs = 0;
  var GAP = 9;

  function hash(x, y) { var s = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return s - Math.floor(s); }
  function noise(x, y) {
    var ix = Math.floor(x), iy = Math.floor(y), fx = x - ix, fy = y - iy;
    var ux = fx * fx * (3 - 2 * fx), uy = fy * fy * (3 - 2 * fy);
    var a = hash(ix, iy), b = hash(ix + 1, iy), cc = hash(ix, iy + 1), d = hash(ix + 1, iy + 1);
    return a + (b - a) * ux + (cc - a) * uy + (a - b - cc + d) * ux * uy;
  }

  function size() {
    var r = c.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = r.width; H = r.height;
    c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    var cols = Math.ceil(W / GAP) + 1, rows = Math.ceil(H / GAP) + 1;
    // streak: a soft diagonal band that drifts slowly
    var ang = -0.62, ca = Math.cos(ang), sa = Math.sin(ang);
    var off = Math.sin(t * 0.35) * 0.08;
    for (var j = 0; j < rows; j++) {
      for (var i = 0; i < cols; i++) {
        var x = i * GAP + (j % 2 ? GAP / 2 : 0), y = j * GAP;
        var nx = x / W, ny = y / H;
        var v = noise(nx * 3.2 + t * 0.12, ny * 3.2 - t * 0.08) * 0.65 + noise(nx * 7.5 - t * 0.05, ny * 7.5) * 0.35;
        // diagonal light: stronger to the right and top
        var d = (nx - 0.55 - off) * ca - (ny - 0.45) * sa;
        var band = Math.exp(-(d * d) / 0.018);
        var s = Math.max(0, v - 0.42) * 1.9 + band * 0.45;
        if (s < 0.06) continue;
        var r = Math.min(GAP * 0.42, s * GAP * 0.38);
        var o = band * 0.75;
        var cr = BONE[0] + (ORANGE[0] - BONE[0]) * o;
        var cg = BONE[1] + (ORANGE[1] - BONE[1]) * o;
        var cb = BONE[2] + (ORANGE[2] - BONE[2]) * o;
        ctx.fillStyle = 'rgba(' + (cr | 0) + ',' + (cg | 0) + ',' + (cb | 0) + ',' + Math.min(0.5, 0.12 + s * 0.32).toFixed(3) + ')';
        ctx.beginPath();
        ctx.arc(x, y, r, 0, 6.2832);
        ctx.fill();
      }
    }
  }

  function loop(ts) {
    raf = 0;
    if (!visible) return;
    if (ts - lastTs > 40) { t += 0.04; lastTs = ts; draw(); }
    raf = requestAnimationFrame(loop);
  }

  size(); draw();
  window.addEventListener('resize', function () { size(); draw(); });
  if (reduceMotion) return;
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) {
      visible = e[0].isIntersecting;
      if (visible && !raf) raf = requestAnimationFrame(loop);
    }).observe(c);
  } else {
    raf = requestAnimationFrame(loop);
  }
  document.addEventListener('visibilitychange', function () {
    visible = !document.hidden;
    if (visible && !raf) raf = requestAnimationFrame(loop);
  });
})();

/* ── Ambient videos: hold on the poster frame for reduced motion ── */
(function () {
  if (!window.matchMedia || !window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('video[autoplay][muted]').forEach(function (v) {
    v.removeAttribute('autoplay'); v.pause(); v.preload = 'none';
  });
})();

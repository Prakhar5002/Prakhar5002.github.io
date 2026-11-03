(function () {
  'use strict';
  var root = document.documentElement;
  var reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  /* Theme */
  var toggle = document.getElementById('theme-toggle');
  var themeMeta = document.querySelector('meta[name="theme-color"]');
  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    if (toggle) {
      toggle.setAttribute('aria-pressed', String(theme === 'dark'));
      toggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    }
    if (themeMeta) themeMeta.setAttribute('content', theme === 'dark' ? '#0b1120' : '#f8fafc');
  }
  applyTheme(root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  /* Nav: mobile menu + scrolled border */
  var nav = document.querySelector('.nav');
  var menuBtn = document.getElementById('menu-btn');
  function setMenu(open) {
    nav.classList.toggle('is-open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }
  if (nav && menuBtn) {
    menuBtn.addEventListener('click', function () { setMenu(!nav.classList.contains('is-open')); });
    nav.querySelectorAll('.nav-links a').forEach(function (a) {
      a.addEventListener('click', function () { setMenu(false); });
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
  }
  function onScroll() { if (nav) nav.classList.toggle('is-scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* Phone clock: visitor's local time */
  var timeEl = document.getElementById('clock-time');
  var dateEl = document.getElementById('clock-date');
  function tick() {
    var now = new Date();
    if (timeEl) timeEl.textContent = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0');
    if (dateEl) dateEl.textContent = now.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' });
  }
  tick();
  setTimeout(function () { tick(); setInterval(tick, 60000); }, (60 - new Date().getSeconds()) * 1000);

  /* Reveal on scroll */
  var revealEls = document.querySelectorAll('[data-reveal]');
  var io = null;
  if (reduced || !('IntersectionObserver' in window)) {
    revealEls.forEach(function (el) { el.classList.add('is-visible'); });
  } else {
    // Hide-until-revealed only once the observer is about to exist, so an earlier error can't strand content at opacity 0
    root.classList.add('js');
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-visible'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* Phone icons: bounce, scroll to the product, ping its card */
  document.querySelectorAll('.app[href^="#"]').forEach(function (app) {
    app.addEventListener('click', function (e) {
      var id = app.getAttribute('href').slice(1);
      var target = document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      app.classList.remove('is-tapped');
      void app.offsetWidth;
      app.classList.add('is-tapped');
      target.classList.add('is-visible');
      target.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' });
      target.classList.add('is-pinged');
      clearTimeout(target._pingTimer);
      target._pingTimer = setTimeout(function () { target.classList.remove('is-pinged'); }, 1500);
      if (history.replaceState) history.replaceState(null, '', '#' + id);
    });
  });

  /* Hero stats count up once (final text equals the static HTML) */
  function countUp(el) {
    var end = parseFloat(el.getAttribute('data-count'));
    var dec = parseInt(el.getAttribute('data-decimals') || '0', 10);
    var suffix = el.getAttribute('data-suffix') || '';
    var start = null;
    function frame(t) {
      if (start === null) start = t;
      var p = Math.min((t - start) / 1200, 1);
      el.textContent = (end * (1 - Math.pow(1 - p, 3))).toFixed(dec) + suffix;
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  if (!reduced && 'IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { countUp(en.target); cio.unobserve(en.target); }
      });
    }, { threshold: 0.6 });
    document.querySelectorAll('[data-count]').forEach(function (el) { cio.observe(el); });
  }
})();

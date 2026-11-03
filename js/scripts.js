/* Portfolio interactions: theme toggle, mobile menu, scroll-spy, reveal-on-scroll, footer year.
 * The page is fully readable without this file; it only layers behaviour on top.
 * The first-paint theme is set by the inline script in <head>. */
(function () {
  'use strict';

  var root = document.documentElement;

  function saveTheme(value) {
    try {
      window.localStorage.setItem('theme', value);
    } catch (e) {
      /* storage blocked (private mode): the choice lasts for this page view only */
    }
  }

  /* ---------- Reveal on scroll ---------- */
  document.querySelectorAll('.grid-3').forEach(function (grid) {
    Array.prototype.forEach.call(grid.children, function (child, i) {
      child.style.setProperty('--d', (i % 3) * 60 + 'ms');
    });
  });
  var reveals = document.querySelectorAll('.reveal');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.classList.add('is-visible');
            io.unobserve(en.target);
          }
        });
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.08 }
    );
    reveals.forEach(function (r) {
      io.observe(r);
    });
  } else {
    reveals.forEach(function (r) {
      r.classList.add('is-visible');
    });
  }
  window.revealReady = true; // tells the <head> fallback that reveal is wired up

  /* ---------- Theme ---------- */
  var toggle = document.getElementById('theme-toggle');
  function paintToggle(theme) {
    if (!toggle) return;
    var dark = theme === 'dark';
    toggle.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    var icon = toggle.querySelector('i');
    if (icon) icon.className = 'fa-solid ' + (dark ? 'fa-sun' : 'fa-moon');
  }
  paintToggle(root.getAttribute('data-theme'));
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      saveTheme(next);
      paintToggle(next);
    });
  }

  /* ---------- Mobile menu ---------- */
  var menuBtn = document.getElementById('menu-toggle');
  var menu = document.getElementById('mobile-menu');
  function setMenu(open) {
    if (!menuBtn || !menu) return;
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    var icon = menuBtn.querySelector('i');
    if (icon) icon.className = 'fa-solid ' + (open ? 'fa-xmark' : 'fa-bars');
    menu.hidden = !open;
  }
  if (menuBtn && menu) {
    menuBtn.addEventListener('click', function () {
      setMenu(menuBtn.getAttribute('aria-expanded') !== 'true');
    });
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) setMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menuBtn.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        menuBtn.focus();
      }
    });
    var wide = window.matchMedia('(min-width: 768px)');
    var onWide = function (m) {
      if (m.matches) setMenu(false);
    };
    if (wide.addEventListener) wide.addEventListener('change', onWide);
    else if (wide.addListener) wide.addListener(onWide); // Safari < 14
  }

  /* ---------- Scroll-spy ---------- */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('[data-nav]'));
  function setActive(id) {
    navLinks.forEach(function (a) {
      var on = a.getAttribute('data-nav') === id;
      a.classList.toggle('is-active', on);
      if (on) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
  }
  // The last section is too short to cross the viewport middle, so it wins whenever the page end is reached.
  function atBottom() {
    return window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4;
  }
  setActive('profile');
  if ('IntersectionObserver' in window) {
    var spy = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) setActive(en.target.id);
        });
        if (atBottom()) setActive('contact');
      },
      { rootMargin: '-45% 0px -50% 0px' }
    );
    document.querySelectorAll('main section[id]').forEach(function (s) {
      spy.observe(s);
    });
  }
  window.addEventListener(
    'scroll',
    function () {
      if (atBottom()) setActive('contact');
    },
    { passive: true }
  );

  /* ---------- Footer year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (n) {
    n.textContent = String(new Date().getFullYear());
  });
})();

// Theme: respect saved choice, else system preference
(function initTheme(){
  const saved = localStorage.getItem('theme');
  // Light-primary brand: default to light when no saved choice.
  document.body.setAttribute('data-theme', saved || 'light');
})();

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const next = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.body.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    });
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
});

/* Hero: platform-view toggle + browser <-> phone sync-highlight */
document.addEventListener('DOMContentLoaded', () => {
  const stage = document.querySelector('.hero-stage');
  if (!stage) return;
  const frames = stage.querySelector('.stage-frames');
  stage.querySelectorAll('.seg-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      stage.querySelectorAll('.seg-btn').forEach(b => {
        const on = b === btn;
        b.classList.toggle('is-on', on);
        b.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      if (frames) frames.setAttribute('data-view', btn.dataset.view);
    });
  });
  const setSync = (key, on) =>
    stage.querySelectorAll('[data-sync="' + key + '"]').forEach(el => el.classList.toggle('synced', on));
  stage.querySelectorAll('[data-sync]').forEach(r => {
    r.addEventListener('mouseenter', () => setSync(r.dataset.sync, true));
    r.addEventListener('mouseleave', () => setSync(r.dataset.sync, false));
  });
});

/* Wire: draw the hero connector in on load */
window.addEventListener('load', () => {
  const w = document.getElementById('hero-wire');
  if (w) w.classList.add('draw');
});

/* Motion: reveal case-study rows + timeline items on scroll */
document.addEventListener('DOMContentLoaded', () => {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.16 });
  document.querySelectorAll('.reveal-row').forEach(el => io.observe(el));
});

/* Motion: count-up metrics when they scroll into view */
document.addEventListener('DOMContentLoaded', () => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const format = (el, val) => {
    const t = parseFloat(el.dataset.count);
    const n = (t % 1 !== 0) ? val.toFixed(1) : Math.round(val);
    return (el.dataset.prefix || '') + n + (el.dataset.suffix || '');
  };
  const run = (el) => {
    const target = parseFloat(el.dataset.count);
    if (reduce || isNaN(target)) { el.textContent = el.dataset.display; return; }
    const dur = 1200, start = performance.now();
    const step = (now) => {
      const p = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = format(el, target * eased);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = el.dataset.display;
    };
    requestAnimationFrame(step);
  };
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting){ run(e.target); io.unobserve(e.target); } });
  }, { threshold: 0.6 });
  document.querySelectorAll('.count').forEach(el => io.observe(el));
});

/* Motion: subtle device tilt toward the cursor */
document.addEventListener('DOMContentLoaded', () => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('[data-tilt]').forEach(wrap => {
    const dev = wrap.querySelector('.device, .split-viz');
    if (!dev) return;
    wrap.addEventListener('mousemove', (ev) => {
      const r = wrap.getBoundingClientRect();
      const px = (ev.clientX - r.left) / r.width - 0.5;
      const py = (ev.clientY - r.top) / r.height - 0.5;
      dev.style.setProperty('--rx', (px * 10).toFixed(2) + 'deg');
      dev.style.setProperty('--ry', (-py * 10).toFixed(2) + 'deg');
    });
    wrap.addEventListener('mouseleave', () => {
      dev.style.setProperty('--rx', '0deg');
      dev.style.setProperty('--ry', '0deg');
    });
  });
});

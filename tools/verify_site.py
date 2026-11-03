#!/usr/bin/env python3
"""Static checks for the portfolio page (spec 2026-11-03-portfolio-abhay-style-design.md).

Usage:  python3 -I tools/verify_site.py [group ...]     (no args = every group)
Exit 0 when every selected group passes, 1 otherwise.
"""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return f.read()


def exists(rel):
    return os.path.isfile(os.path.join(ROOT, rel))


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []  # (tag, attrs dict) in document order
        self.text = []  # visible text chunks
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag in ('script', 'style'):
            self._skip += 1

    def handle_startendtag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)


def page():
    html = read('index.html')
    p = Page()
    p.feed(html)
    text = re.sub(r'\s+', ' ', ' '.join(p.text))
    return html, p, text


def section(html, sid):
    m = re.search(r'<section[^>]*\bid="%s"[^>]*>(.*?)</section>' % re.escape(sid), html, re.S)
    return m.group(1) if m else ''


def count_class(block, cls):
    return len(re.findall(r'class="(?:[^"]*\s)?%s(?:\s[^"]*)?"' % re.escape(cls), block))


NAV = ['profile', 'experience', 'skills', 'what-i-do', 'projects', 'contact']
NAV_LABELS = ['Profile', 'Experience', 'Skills', 'What I Do', 'Projects', 'Contact']
COMPANIES = ['Smartworks', 'AUMVerse', 'Infinity Soft Systems', 'iFlair Web Technologies', 'Shantikunj']
SKILLS = ['Languages', 'Mobile', 'Frontend (Web)', 'Backend', 'Databases', 'Cloud &amp; DevOps',
          'State &amp; Data', 'Testing &amp; Quality', 'AI-assisted Dev']
DO = ['Mobile Apps', 'Web Apps', 'Backend &amp; APIs', 'Real-Time Systems', 'Payments &amp; Auth',
      'AI Features', 'Performance &amp; Stability', 'Upgrades &amp; Releases', 'Code Quality']
PROJECTS = ['AUMVerse', 'Workctrl', 'Meeting Room Tab', 'SW Tickets', 'Smart Setup', 'NoWorriesApp',
            'Clinicards', 'QU App']
STORE_URLS = [
    'https://aumverse.co',
    'https://apps.apple.com/us/app/workctrl/id6739703138',
    'https://play.google.com/store/apps/details?id=com.sts.swmobile',
    'https://apps.apple.com/us/app/sw-tickets/id6504776362',
    'https://play.google.com/store/apps/details?id=com.swticket',
    'https://apps.apple.com/in/app/noworriesapp/id6450531547',
    'https://play.google.com/store/apps/details?id=com.noworries',
    'https://play.google.com/store/apps/details?id=nl.synappz.clinicards.iherstel',
]
FORBIDDEN = ['~40%', '~30%', 'Figma', 'no cloud round-trip', '11 apps', '+91']
REQUIRED = ['5.5 years', '50,000+', '0.21%', '80–90%', '1,700']


def g_assets():
    f = []
    for rel in ['assets/fonts/nunito.woff2', 'assets/fonts/inter.woff2', 'assets/img/profile-640.webp',
                'assets/img/profile-640.jpg', 'assets/img/favicon.ico', 'assets/Prakhar_Pandey.pdf']:
        if not exists(rel):
            f.append('missing ' + rel)
    for rel, limit in [('assets/img/profile-640.webp', 80_000), ('assets/img/profile-640.jpg', 120_000)]:
        if exists(rel) and os.path.getsize(os.path.join(ROOT, rel)) > limit:
            f.append('%s larger than %d bytes' % (rel, limit))
    if exists('assets/fonts/nunito.woff2'):
        with open(os.path.join(ROOT, 'assets/fonts/nunito.woff2'), 'rb') as fh:
            if fh.read(4) != b'wOF2':
                f.append('nunito.woff2 is not a WOFF2 file')
    if exists('assets/Prakhar_Pandey.pdf'):
        with open(os.path.join(ROOT, 'assets/Prakhar_Pandey.pdf'), 'rb') as fh:
            if not fh.read(5).startswith(b'%PDF'):
                f.append('resume is not a PDF')
    return f


def g_head():
    html, p, _ = page()
    f = []
    if '<html lang="en" data-theme="light">' not in html:
        f.append('<html lang="en" data-theme="light"> missing')
    t = re.search(r'<title>(.*?)</title>', html, re.S)
    if not t or t.group(1).strip() != 'Prakhar Pandey · Senior Software Engineer (Mobile &amp; Full-Stack)':
        f.append('wrong <title>')
    metas = {(a.get('name') or a.get('property')): a.get('content') for tg, a in p.tags if tg == 'meta'}
    for k in ['viewport', 'description', 'color-scheme', 'og:title', 'og:description', 'og:image', 'og:url']:
        if not metas.get(k):
            f.append('meta %s missing' % k)
    if metas.get('color-scheme') != 'light dark':
        f.append('color-scheme must be "light dark"')
    links = [(a.get('rel'), a.get('href')) for tg, a in p.tags if tg == 'link']
    for need in [('canonical', 'https://prakhar5002.github.io/'),
                 ('stylesheet', 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'),
                 ('stylesheet', 'css/styles.css'), ('icon', 'assets/img/favicon.ico')]:
        if need not in links:
            f.append('link rel=%s href=%s missing' % need)
    if not any(tg == 'script' and a.get('src') == 'js/scripts.js' and 'defer' in a for tg, a in p.tags):
        f.append('js/scripts.js must load with defer')
    head = html.split('</head>')[0]
    inline = re.findall(r'<script>(.*?)</script>', head, re.S)
    if not inline or not all(s in inline[0] for s in ('localStorage', 'data-theme', "classList.add('js')")):
        f.append('inline theme bootstrap script missing from <head>')
    return f


def g_nav():
    html, p, _ = page()
    f = []
    navs = [a for tg, a in p.tags if tg == 'a' and 'data-nav' in a]
    ids = [a['data-nav'] for a in navs]
    if ids != NAV + NAV:
        f.append('data-nav links must be %s twice (desktop + mobile), got %s' % (NAV, ids))
    for a in navs:
        if a.get('href') != '#' + a.get('data-nav', ''):
            f.append('nav href mismatch for ' + a.get('data-nav', ''))
    labels = re.findall(r'<a href="#[\w-]+" data-nav="[\w-]+">([^<]+)</a>', html)
    if labels[:6] != NAV_LABELS:
        f.append('desktop nav labels must be %s, got %s' % (NAV_LABELS, labels[:6]))
    btn = {a.get('id'): a for tg, a in p.tags if tg == 'button'}
    if btn.get('theme-toggle', {}).get('aria-label') != 'Switch to dark theme':
        f.append('#theme-toggle with aria-label "Switch to dark theme" missing')
    m = btn.get('menu-toggle', {})
    if m.get('aria-expanded') != 'false' or m.get('aria-controls') != 'mobile-menu':
        f.append('#menu-toggle needs aria-expanded="false" aria-controls="mobile-menu"')
    if '<div id="mobile-menu" class="mobile-menu" hidden>' not in html:
        f.append('#mobile-menu must start hidden')
    if '<a class="skip-link" href="#profile">Skip to content</a>' not in html:
        f.append('skip link missing')
    if '<main id="main">' not in html:
        f.append('<main id="main"> missing')
    return f


def g_hero():
    html, _, _ = page()
    s = section(html, 'profile')
    if not s:
        return ['section#profile missing']
    f = []
    if '<h1>Hi, I\'m <span class="grad">Prakhar</span></h1>' not in s:
        f.append('hero h1 wrong')
    if 'Senior Software Engineer · Mobile &amp; Full-Stack' not in s:
        f.append('hero role line wrong')
    if '50,000+' not in s or '0.21%' not in s or '5.5 years' not in s:
        f.append('hero summary must mention 5.5 years, 50,000+ and 0.21%')
    if '<a class="btn btn-primary" href="#projects">' not in s:
        f.append('View My Work button missing')
    if '<a class="btn btn-outline" href="assets/Prakhar_Pandey.pdf" download>' not in s:
        f.append('Download Resume button missing')
    for url in ['https://github.com/Prakhar5002', 'https://www.linkedin.com/in/prakhar-pandey-97532915a']:
        if 'href="%s"' % url not in s:
            f.append('hero link missing: ' + url)
    if '<source srcset="assets/img/profile-640.webp" type="image/webp">' not in s:
        f.append('webp <source> missing')
    if '<img src="assets/img/profile-640.jpg" alt="Prakhar Pandey" width="280" height="280"' not in s:
        f.append('hero <img> must have src, alt, width and height')
    if 'class="photo-badge"' not in s:
        f.append('photo badge missing')
    return f


def g_experience():
    html, _, _ = page()
    s = section(html, 'experience')
    if not s:
        return ['section#experience missing']
    f = []
    if count_class(s, 'xp-card') != 5:
        f.append('need 5 .xp-card, got %d' % count_class(s, 'xp-card'))
    got = re.findall(r'<p class="xp-company">(.*?)</p>', s)
    if got != COMPANIES:
        f.append('companies must be %s, got %s' % (COMPANIES, got))
    if '<span class="tag tag-current">Current</span>' not in s:
        f.append('Current tag missing')
    if '<span class="tag">Personal product</span>' not in s:
        f.append('Personal product tag missing')
    for need in ['May 2024 – Present', 'Dec 2022 – Mar 2024', 'Feb 2022 – Nov 2022', 'May 2021 – Jan 2022',
                 '0.76 → 0.79', '80–90%', '1,700']:
        if need not in s:
            f.append('experience missing "%s"' % need)
    return f


def g_skills():
    html, _, _ = page()
    s = section(html, 'skills')
    if not s:
        return ['section#skills missing']
    f = []
    titles = re.findall(r'<h3>(.*?)</h3>', s)
    if titles != SKILLS:
        f.append('skill card titles must be %s, got %s' % (SKILLS, titles))
    if count_class(s, 'skill-card') != 9:
        f.append('need 9 .skill-card, got %d' % count_class(s, 'skill-card'))
    for need in ['CloudWatch', 'Claude Code', 'Kotlin', 'PostgreSQL']:
        if need not in s:
            f.append('skills missing ' + need)
    return f


def g_whatido():
    html, _, _ = page()
    s = section(html, 'what-i-do')
    if not s:
        return ['section#what-i-do missing']
    f = []
    titles = re.findall(r'<h3>(.*?)</h3>', s)
    if titles != DO:
        f.append('What I Do titles must be %s, got %s' % (DO, titles))
    chunks = s.split('class="card do-card')[1:]
    if len(chunks) != 9:
        f.append('need 9 .do-card, got %d' % len(chunks))
    for i, c in enumerate(chunks):
        n = len(re.findall(r'<li>', c))
        if n != 3:
            f.append('do-card %d has %d checks, need 3' % (i + 1, n))
    if re.search(r'\b(freelance|hire me|services)\b', s, re.I):
        f.append('What I Do must not read as freelance services')
    return f


def g_projects():
    html, _, _ = page()
    s = section(html, 'projects')
    if not s:
        return ['section#projects missing']
    f = []
    if count_class(s, 'project-card') != 8:
        f.append('need 8 .project-card, got %d' % count_class(s, 'project-card'))
    titles = re.findall(r'<h3>(.*?)</h3>', s)
    if titles != PROJECTS:
        f.append('project titles must be %s, got %s' % (PROJECTS, titles))
    covers = re.findall(r'<div class="cover" style="--c1:#[0-9a-f]{6};--c2:#[0-9a-f]{6}">', s)
    if len(covers) != 8:
        f.append('need 8 gradient covers, got %d' % len(covers))
    for url in STORE_URLS:
        if 'href="%s"' % url not in s:
            f.append('project link missing: ' + url)
    for tag in re.findall(r'<a class="link-btn"[^>]*>', s):
        if 'aria-label="' not in tag:
            f.append('link-btn without aria-label: ' + tag)
    return f


def g_contact():
    html, _, _ = page()
    s = section(html, 'contact')
    if not s:
        return ['section#contact missing']
    f = []
    if "<h2>Let's Work Together</h2>" not in s:
        f.append('contact heading missing')
    if 'href="mailto:pandey.prakhar5002@gmail.com"' not in s:
        f.append('mailto link missing')
    if 'Gurugram, India' not in s:
        f.append('location missing')
    if count_class(s, 'connect-item') != 3:
        f.append('need 3 .connect-item, got %d' % count_class(s, 'connect-item'))
    return f


def g_footer():
    html, _, _ = page()
    f = []
    if not re.search(r'<footer class="footer">\s*<p>© <span data-year>2026</span> Prakhar Pandey\. '
                     r'All rights reserved\.</p>\s*</footer>', html):
        f.append('footer markup missing')
    if '<!-- @sections -->' in html:
        f.append('insertion marker <!-- @sections --> still present')
    if not re.search(r'</main>\s*<footer', html):
        f.append('footer must follow </main>')
    return f


def g_links():
    html, p, _ = page()
    f = []
    ids = {a['id'] for _, a in p.tags if a.get('id')}
    for tg, a in p.tags:
        for attr in ('href', 'src', 'srcset'):
            v = a.get(attr)
            if not v:
                continue
            if v.startswith('#'):
                if v[1:] not in ids:
                    f.append('broken anchor ' + v)
            elif v.startswith(('http://', 'https://')):
                if tg == 'a' and (a.get('target') != '_blank' or a.get('rel') != 'noopener'):
                    f.append('external link needs target="_blank" rel="noopener": ' + v)
            elif v.startswith('mailto:'):
                continue
            elif not exists(v.split('?')[0]):
                f.append('missing local file ' + v)
    for m in re.finditer(r'<(a|button)\b([^>]*)>\s*<i\b[^>]*></i>\s*</\1>', html):
        if 'aria-label="' not in m.group(2):
            f.append('icon-only <%s> needs aria-label: %s' % (m.group(1), m.group(2).strip()))
    css = read('css/styles.css')
    for u in re.findall(r'url\("\.\./([^"]+)"\)', css):
        if not exists(u):
            f.append('css url() missing file ' + u)
    return f


def g_content():
    _, _, text = page()
    f = []
    low = text.lower()
    for w in FORBIDDEN:
        if w.lower() in low:
            f.append('forbidden text on page: ' + w)
    if re.search(r'\b\d{10}\b', text):
        f.append('phone-like number on page')
    for w in REQUIRED:
        if w not in text:
            f.append('required fact missing: ' + w)
    return f


def g_js():
    js = read('js/scripts.js')
    f = []
    for need in ["getElementById('theme-toggle')", "getElementById('menu-toggle')", 'IntersectionObserver',
                 '[data-year]', 'prefers-reduced-motion', 'localStorage', "setActive('contact')"]:
        if need not in js:
            f.append('js/scripts.js missing ' + need)
    # Final review I1: a JS failure must never leave the page hidden.
    if js.find('Reveal on scroll') > js.find('Theme ----'):
        f.append('reveal block must run first in scripts.js')
    if 'addListener' not in js:
        f.append('matchMedia needs an addListener fallback (Safari <14)')
    head = read('index.html').split('</head>')[0]
    if 'revealReady' not in head or 'revealReady' not in js:
        f.append('head needs a timeout that drops .js unless scripts.js sets window.revealReady')
    return f


def g_cleanup():
    f = []
    for rel in ['assets/fonts/bricolage-grotesque.woff2', 'assets/fonts/jetbrains-mono.woff2',
                'assets/img/android.jpg', 'assets/img/js.jpg', 'assets/img/karuna.png', 'assets/img/nodejs.png']:
        if exists(rel):
            f.append('should be removed: ' + rel)
    css = read('css/styles.css')
    for w in ['Bricolage', 'JetBrains']:
        if w in css:
            f.append('css still references ' + w)
    for need in [':focus-visible', '.skip-link:focus', 'prefers-reduced-motion']:
        if need not in css:
            f.append('css missing ' + need)
    # Final review I2: the blue focus ring is invisible on the navy contact block.
    if not re.search(r'\.contact :focus-visible\s*\{[^}]*outline-color:\s*#93c5fd', css):
        f.append('css needs .contact :focus-visible { outline-color: #93c5fd }')
    # Final review I3: once revealed, cards must hover at 200ms with no stagger delay.
    m = re.search(r'\.js \.card\.reveal\.is-visible\s*\{([^}]*)\}', css)
    if not m or 'opacity 0.5s' not in m.group(1) or 'transform 0.2s' not in m.group(1) \
            or not re.search(r'transition-delay:\s*var\(--d, 0ms\), 0s, 0s', m.group(1)):
        f.append('css needs .js .card.reveal.is-visible: staggered opacity fade, 200ms undelayed transform/shadow')
    return f


GROUPS = {
    'assets': g_assets, 'head': g_head, 'nav': g_nav, 'hero': g_hero, 'experience': g_experience,
    'skills': g_skills, 'whatido': g_whatido, 'projects': g_projects, 'contact': g_contact,
    'footer': g_footer, 'links': g_links, 'content': g_content, 'js': g_js, 'cleanup': g_cleanup,
}


def main(argv):
    names = argv or list(GROUPS)
    bad = 0
    for n in names:
        if n not in GROUPS:
            print('unknown group: ' + n)
            return 2
        try:
            fails = GROUPS[n]()
        except FileNotFoundError as e:
            fails = ['file not found: %s' % e.filename]
        if fails:
            bad += 1
            print('FAIL ' + n)
            for x in fails:
                print('  - ' + x)
        else:
            print('PASS ' + n)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

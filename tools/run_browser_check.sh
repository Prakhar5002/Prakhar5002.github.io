#!/usr/bin/env bash
# Runs tools/browser-check.html in headless Chrome and asserts the results. Exit 0 = pass.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Final review I1: copy of the page whose scripts.js 404s; content must become visible anyway.
sed 's#src="js/scripts.js"#src="js/missing.js"#' "$ROOT/index.html" > "$ROOT/.broken-js-check.html"
trap 'rm -f "$ROOT/.broken-js-check.html"' EXIT
DOM="$("$CHROME" --headless --disable-gpu --allow-file-access-from-files --virtual-time-budget=20000 --window-size=1500,1000 \
  --dump-dom "file://$ROOT/tools/browser-check.html" 2>/dev/null)"
python3 -I - "$DOM" <<'PY'
import datetime, html, json, re, sys
m = re.search(r'<pre id="out">(.*?)</pre>', sys.argv[1], re.S)
if not m or m.group(1).strip() == 'pending':
    print('FAIL harness did not finish'); sys.exit(1)
data = json.loads(html.unescape(m.group(1)))
fails = []
for key, r in data.items():
    if 'error' in r:
        fails.append('%s: %s' % (key, r['error'])); continue
    w = r['w']
    if key == 'brokenjs':
        if r.get('revealOpacity') != '1':
            fails.append('brokenjs: content hidden when scripts.js fails (opacity %s)' % r.get('revealOpacity'))
        continue
    if r['scrollWidth'] > w:
        fails.append('%s: horizontal overflow (%dpx > %dpx)' % (key, r['scrollWidth'], w))
    want_theme = 'dark' if key == 'dark1024' else 'light'
    if r['theme'] != want_theme:
        fails.append('%s: theme %s, expected %s' % (key, r['theme'], want_theme))
    want_bg = 'rgb(11, 17, 32)' if key == 'dark1024' else 'rgb(248, 250, 252)'
    if r['bodyBg'] != want_bg:
        fails.append('%s: body background %s, expected %s' % (key, r['bodyBg'], want_bg))
    if w < 768:
        if not r['menuBtnVisible'] or r['navLinksVisible']:
            fails.append('%s: mobile nav expected (menu button shown, links hidden)' % key)
        if not r.get('menuOpens') or not r.get('escCloses'):
            fails.append('%s: menu must open on click and close on Escape' % key)
    elif r['menuBtnVisible'] or not r['navLinksVisible']:
        fails.append('%s: desktop nav expected (links shown, menu button hidden)' % key)
r = data.get('1440', {})
checks = [('toggledTo', 'dark'), ('toggleLabel', 'Switch to light theme'), ('toggledBack', 'light'),
          ('activeAtTop', 'Profile'), ('activeAtBottom', 'Contact'), ('year', str(datetime.date.today().year))]
for k, v in checks:
    if r.get(k) != v:
        fails.append('1440: %s = %r, expected %r' % (k, r.get(k), v))
for f in fails:
    print('FAIL ' + f)
print('PASS browser checks (%d frames)' % len(data) if not fails else '%d failure(s)' % len(fails))
sys.exit(1 if fails else 0)
PY

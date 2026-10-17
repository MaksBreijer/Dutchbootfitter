#!/usr/bin/env python3
"""Compares the image alt texts of every page with the live bootfitter.nl page.

For each page it lists alt texts that are on the live page but missing here, and alt texts that are new here
(new images such as the page header banners). Writes alt-check.json next to verification.json.
Needs internet: it fetches each live page once (cached in build/.live-cache/)."""
import os, sys, json, re, html, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as G

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.live-cache')
os.makedirs(CACHE, exist_ok=True)


def live_html(url):
    f = os.path.join(CACHE, re.sub(r'[^a-z0-9]+', '_', url.lower()) + '.html')
    if not os.path.exists(f):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        open(f, 'w', encoding='utf-8').write(urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace'))
    return open(f, encoding='utf-8').read()


def alts(doc):
    out = []
    for tag in re.findall(r'<img\b[^>]*>', doc, re.I):
        m = re.search(r'\balt=("([^"]*)"|\'([^\']*)\')', tag)
        a = html.unescape((m.group(2) if m.group(2) is not None else m.group(3)) if m else '').strip()
        if a:
            out.append(a)
    return out


urls = [l.strip() for l in open(os.path.join(G.BASE, 'urls.txt')) if l.strip()]
report, missing_total = [], 0
for url in urls:
    slug = G.url_to_slug(url)
    path = os.path.join(G.OUT, G.slug_to_file(slug))
    if not os.path.exists(path):
        continue
    live, new = alts(live_html(url)), alts(open(path, encoding='utf-8').read())
    missing = sorted(set(live) - set(new))
    extra = sorted(set(new) - set(live))
    missing_total += len(missing)
    report.append({'page': G.slug_to_file(slug), 'missing_from_new': missing, 'new_here': extra})
json.dump(report, open(os.path.join(G.BASE, 'alt-check.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for r in report:
    if r['missing_from_new'] or r['new_here']:
        print(r['page'])
        for a in r['missing_from_new']:
            print('   - ontbreekt:', a)
        for a in r['new_here']:
            print('   + nieuw:    ', a)
print('pagina\'s:', len(report), ' live alt-teksten die ontbreken:', missing_total)

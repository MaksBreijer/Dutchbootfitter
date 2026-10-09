#!/usr/bin/env python3
"""Checks that every word of the copied original text appears, in order, on the matching new page."""
import os, re, sys, difflib, json
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as G
BASE = G.BASE

def md_words(t):
    t = t.split('===MAIN===', 1)[-1]
    t = re.sub(r'(?m)^(EMBED|VIDEO): \S+$', '', t)
    t = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', t)
    t = re.sub(r'<(https?://[^>]+)>', r'\1', t)
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)
    t = re.sub(r'(?m)^\s*(#+|>|[-*]|\d+\.)\s+', '', t)
    t = t.replace('\\|', '\x01').replace('\\*', '\x00').replace('**', '').replace('__', '')
    t = re.sub(r'(?<![\w\x00])\*|\*(?![\w\x00])', '', t)
    t = re.sub(r'(?m)^[\s|:-]*-{3,}[\s|:-]*$', '', t)
    t = re.sub(r'(?m)^\|(.*)\|\s*$', lambda m: m.group(1).replace('|', ' '), t)
    t = t.replace('\x00', '*').replace('\x01', '|')
    return t.split()

def html_words(path, drop=()):
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    for sel in ('[data-reuse]',) + tuple(drop):  # reused sentences are checked separately, against their own page
        for el in soup.select(sel):
            el.decompose()
    parts = [soup.select_one('main')] + soup.select('.cta-band') + soup.select('.post-cta')
    return ' '.join(visible_text(p) for p in parts if p).split()

BLOCK = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'ul', 'ol', 'div', 'section', 'article', 'figure', 'blockquote',
         'br', 'summary', 'details', 'td', 'th', 'tr', 'table', 'aside', 'nav', 'header', 'footer', 'main', 'time', 'address'}

def visible_text(el):
    from bs4 import NavigableString, Comment
    out = []
    def walk(n):
        for c in n.children:
            if isinstance(c, Comment):
                continue
            if isinstance(c, NavigableString):
                out.append(str(c)); continue
            if c.name in ('script', 'style', 'canvas', 'iframe'):
                continue
            blk = c.name in BLOCK or 'flow-step' in (c.get('class') or []) or 'flow-tag' in (c.get('class') or [])
            if blk: out.append(' ')
            walk(c)
            if blk: out.append(' ')
    walk(el)
    return ''.join(out)

ALLOWED_DROPS = {  # layout-only removals, each explained in the report
    'reacties-van-klanten-referenties': ['Vorige', 'Volgende'],
}
G.KNOWN = G.known_slugs()
report, bad, ws = [], 0, []
for slug in sorted(s for s in G.KNOWN if not s.startswith('_')):
    src = open(os.path.join(G.COPY, slug + '.md'), encoding='utf-8').read()
    if slug == 'tarieven-bootfitting':
        # the copier repeated each price name after its link; the live page shows it once
        src = re.sub(r'(?m)^- \[([^\]]+)\]\(([^)]+)\) \1 ', lambda m: f'- [{m.group(1)}]({m.group(2)}) ', src)
    if slug == 'home':
        # the services block sits straight after the intro; compare against that order
        head, _, body = src.partition('===MAIN===')
        src = head + '===MAIN===\n' + G.home_md(body)
    if slug == 'over-ons':
        # the page shows the same blocks in a different reading order; compare against that order
        head, _, body = src.partition('===MAIN===')
        src = head + '===MAIN===\n' + G.over_ons_md(body)
    exp = md_words(src)
    if not re.search(r'Pijn in voeten of scheenbenen\?', ' '.join(exp)):
        exp += G.CTA_HEADING.split() + G.CTA_BUTTON.split()
    drop = ['.blog-side'] if slug.startswith('bootfitting_blog__') else []
    act = html_words(os.path.join(G.OUT, G.slug_to_file(slug)), drop)
    sm = difflib.SequenceMatcher(None, exp, act, autojunk=False)
    diffs = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        e, a = exp[i1:i2], act[j1:j2]
        if op == 'delete' and all(w in ALLOWED_DROPS.get(slug, []) for w in e):
            continue
        if ''.join(e) == ''.join(a):
            ws.append({'page': G.slug_to_file(slug), 'original': ' '.join(e), 'new': ' '.join(a)})
            continue
        diffs.append({'op': op, 'context': ' '.join(exp[max(0, i1 - 6):i1]), 'original': ' '.join(e), 'new': ' '.join(a)})
    status = 'IDENTICAL' if not diffs else f'{len(diffs)} DIFFS'
    bad += bool(diffs)
    report.append({'page': G.slug_to_file(slug), 'words': len(exp), 'status': status, 'diffs': diffs})
# shared blog sidebar on every post
side_exp = md_words(open(os.path.join(G.COPY, '_blog_sidebar.md'), encoding='utf-8').read())
soup = BeautifulSoup(open(os.path.join(G.OUT, 'blog-mortons-neuroom-pijn-in-skischoen.html'), encoding='utf-8').read(), 'html.parser')
side_act = soup.select_one('.blog-side').get_text(' ').split()
report.append({'page': '(blog sidebar)', 'words': len(side_exp), 'status': 'IDENTICAL' if side_exp == side_act else 'DIFF', 'diffs': [] if side_exp == side_act else [{'new': ' '.join(side_act)}]})
# Blocks marked data-reuse may only repeat words that already stand, in the same order, on the page named by data-src
# ('chrome' = the shared header/footer text). Any text outside a data-src fragment counts as new copy and fails.
def chrome_words():
    from chrome import TOPBAR, NAV, CONTACT, RATING, FOOTER_NAV
    parts = [l for l, _ in TOPBAR] + [n[0] for n in NAV] + [l for l, _ in FOOTER_NAV[1]] + list(CONTACT.values()) + list(RATING.values())
    return ' \n '.join(parts).split()
def contains(hay, needle):
    n = len(needle)
    return n > 0 and any(hay[i:i + n] == needle for i in range(len(hay) - n + 1))
src_words = {'chrome': chrome_words()}
for f in sorted(os.listdir(G.OUT)):
    if not f.endswith('.html'):
        continue
    soup = BeautifulSoup(open(os.path.join(G.OUT, f), encoding='utf-8').read(), 'html.parser')
    blocks = soup.select('[data-reuse]')
    if not blocks:
        continue
    diffs = []
    for blk in blocks:
        for frag in blk.select('[data-src]'):
            src = frag['data-src']
            if src == 'new':  # approved new copy, listed in generate.APPROVED_COPY
                if frag.get_text() not in G.APPROVED_COPY:
                    diffs.append({'op': 'new-copy-not-approved', 'new': frag.get_text()})
                frag.decompose()
                continue
            if src not in src_words:
                src_words[src] = md_words(open(os.path.join(G.COPY, src + '.md'), encoding='utf-8').read())
            words = frag.get_text(' ').split()
            if not contains(src_words[src], words):
                diffs.append({'op': 'reuse-not-found', 'source': src, 'new': ' '.join(words)})
            frag.decompose()
        stray = visible_text(blk).split()
        if [w for w in stray if w != '·']:
            diffs.append({'op': 'new-copy', 'new': ' '.join(stray)})
    bad += bool(diffs)
    report.append({'page': f + ' (reused blocks)', 'words': 0, 'status': 'IDENTICAL' if not diffs else f'{len(diffs)} DIFFS', 'diffs': diffs})
json.dump(report, open(os.path.join(BASE, 'verification.json'), 'w'), ensure_ascii=False, indent=1)
for r in report:
    print(r['status'].ljust(10), r['words'], r['page'])
    for d in r['diffs'][:6]:
        print('    ', d)
print('pages with differences:', bad)
print('whitespace-only differences (same characters, different spacing):')
for w in ws: print('    ', w)
json.dump({'pages': report, 'whitespace_only': ws}, open(os.path.join(BASE, 'verification.json'), 'w'), ensure_ascii=False, indent=1)

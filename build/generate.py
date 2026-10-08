#!/usr/bin/env python3
"""Builds the redesigned DutchBootFitter site from the verbatim copy in ../copy/*.md.

Every visible word on a generated page comes from the copy files (or, for the shared
header and footer, from chrome.py, which was copied from the live site). Nothing is rewritten.
"""
import html, os, re, sys, json, shutil
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ROOT)
COPY = os.path.join(BASE, 'copy')
OUT = os.path.join(BASE, 'site')
ORIGIN = 'https://www.bootfitter.nl'

sys.path.insert(0, ROOT)
from chrome import TOPBAR, NAV, FOOTER_PAIN, FOOTER_NAV, CONTACT, BADGES, RATING, COPYRIGHT, SOCIALS, SKIP, MENU_OPEN, MENU_CLOSE, CTA_HEADING, CTA_BUTTON

CTA_RE = re.compile(r'^#{1,3} Pijn in voeten of scheenbenen\? Maak een afspraak om pijnloos® te skiën!\s*\n+\[Maak direct een afspraak\]\([^)]*\)\s*$', re.M)


def slug_to_file(slug):
    if slug == 'home':
        return 'index.html'
    if slug == 'category__bootfitting_blog':
        return 'blog.html'
    m = re.match(r'category__bootfitting_blog__page__(\d+)$', slug)
    if m:
        return f'blog-{m.group(1)}.html'
    if slug.startswith('bootfitting_blog__'):
        return 'blog-' + slug[len('bootfitting_blog__'):] + '.html'
    return slug.replace('__', '-') + '.html'


def url_to_slug(url):
    p = url.replace(ORIGIN, '').split('#')[0].split('?')[0].strip('/')
    return p.replace('/', '__') or 'home'


def known_slugs():
    return {f[:-3] for f in os.listdir(COPY) if f.endswith('.md')}


KNOWN = None


def local_href(url):
    """Map an original bootfitter.nl page URL to its file in the new site."""
    if not url.startswith(ORIGIN) and not url.startswith('http://www.bootfitter.nl') and not url.startswith('https://bootfitter.nl'):
        return url
    u = re.sub(r'^https?://(www\.)?bootfitter\.nl', ORIGIN, url)
    if '/wp-content/' in u or '/cdn-cgi/' in u or '?' in u:
        return u
    frag = ''
    if '#' in u:
        u, frag = u.split('#', 1)
        frag = '#' + frag
    s = url_to_slug(u)
    if s in KNOWN:
        return slug_to_file(s) + frag
    return url  # page we do not have: keep pointing at the original


def rewrite_links(h):
    def rep(m):
        return m.group(1) + html.escape(local_href(html.unescape(m.group(2))), quote=True) + m.group(3)
    return re.sub(r'(<a\b[^>]*?\bhref=")([^"]*)(")', rep, h)


def parse_copy(slug):
    raw = open(os.path.join(COPY, slug + '.md'), encoding='utf-8').read()
    head, _, body = raw.partition('===MAIN===')
    meta = {}
    for line in head.splitlines():
        m = re.match(r'^(?:#\s*)?(?:Line \d+:\s*)?(TITLE|META|DATE):\s*(.*)$', line.strip())
        if m:
            meta[m.group(1)] = m.group(2).strip()
    return meta, body.strip('\n')


def md_to_html(text):
    h = markdown.markdown(text, extensions=['tables', 'sane_lists'], output_format='html')
    h = re.sub(r'<table>', '<div class="table-wrap"><table>', h)
    h = re.sub(r'</table>', '</table></div>', h)
    h = re.sub(r'<p>VIDEO: (\S+)</p>', lambda m: f'<div class="embed video"><iframe src="{m.group(1)}" title="" loading="lazy" allowfullscreen></iframe></div>', h)
    h = re.sub(r'<p>EMBED: (\S+)</p>', lambda m: f'<div class="embed"><iframe src="{m.group(1)}" title="" loading="lazy"></iframe></div>', h)
    return rewrite_links(h)


def esc(s):
    return html.escape(s, quote=False)


def header_html(current_file):
    def link(label, url, cls=''):
        href = local_href(url)
        cur = ' aria-current="page"' if href == current_file else ''
        return f'<a href="{href}"{cur}{cls}>{esc(label)}</a>'
    top = ''.join(link(l, u) for l, u in TOPBAR)
    items = []
    for entry in NAV:
        label, url, children = entry
        if children:
            sub = ''.join(f'<li>{link(l, u)}</li>' for l, u in children)
            items.append(f'<li class="has-sub"><button class="sub-toggle" type="button" aria-expanded="false">{esc(label)}</button><ul class="submenu">{sub}</ul></li>')
        else:
            cls = ' class="nav-cta"' if label == 'Afspraak' else ''
            items.append(f'<li{cls}>{link(label, url)}</li>')
    return f'''<a class="skip" href="#main">{esc(SKIP)}</a>
<div class="topbar"><nav class="wrap" aria-label="Topbar">{top}</nav></div>
<header class="site-header">
  <div class="wrap"><div class="bar">
    <a class="brand" href="index.html"><img src="{ORIGIN}/wp-content/uploads/2021/06/cropped-logo_pijnloos_def_nieuw_oranje-1.png" alt="Logo DutchBootFitter" width="132" height="54"><span class="brand-mark" aria-hidden="true">Dutch<b>Boot</b>Fitter</span></a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary"><span class="bars" aria-hidden="true"></span><span class="lbl-open">{esc(MENU_OPEN)}</span><span class="lbl-close">{esc(MENU_CLOSE)}</span></button>
    <nav class="primary" id="primary" aria-label="Hoofdmenu"><ul class="nav">{''.join(items)}</ul></nav>
  </div></div>
</header>'''


SOCIAL_ICONS = {
    'Facebook-f': '<svg viewBox="0 0 320 512"><path d="M279 288l14-93h-89v-60c0-25 12-50 52-50h40V6S260 0 225 0c-73 0-121 44-121 125v70H23v93h81v224h100V288z"/></svg>',
    'Twitter': '<svg viewBox="0 0 512 512"><path d="M389 48h71L305 224l182 240H345L233 318 106 464H35l165-189L25 48h146l101 133zm-25 374h39L151 88h-42z"/></svg>',
    'Instagram': '<svg viewBox="0 0 448 512"><path d="M224 141c-64 0-115 51-115 115s51 115 115 115 115-51 115-115-51-115-115-115zm0 190c-41 0-75-34-75-75s34-75 75-75 75 34 75 75-34 75-75 75zm146-194c0 15-12 27-27 27s-27-12-27-27 12-27 27-27 27 12 27 27zm76 27c-2-36-10-68-36-94s-58-34-94-36c-37-2-148-2-185 0-36 2-68 10-94 36S3 133 1 169c-2 37-2 148 0 185 2 36 10 68 36 94s58 34 94 36c37 2 148 2 185 0 36-2 68-10 94-36s34-58 36-94c2-37 2-148 0-185zm-48 225c-8 20-23 35-43 43-30 12-101 9-134 9s-104 3-134-9c-20-8-35-23-43-43-12-30-9-101-9-134s-3-104 9-134c8-20 23-35 43-43 30-12 101-9 134-9s104-3 134 9c20 8 35 23 43 43 12 30 9 101 9 134s3 104-9 134z"/></svg>',
}


def footer_html():
    pain = ''.join(f'<li><a href="{local_href(u)}">{esc(l)}</a></li>' for l, u in FOOTER_PAIN[1])
    nav = ''.join(f'<li><a href="{local_href(u)}">{esc(l)}</a></li>' for l, u in FOOTER_NAV[1])
    badges = ''.join(f'<img src="{src}" alt="{html.escape(alt)}">' for alt, src in BADGES)
    socials = ''.join(f'<a href="{u}" aria-label="{html.escape(l)}">{SOCIAL_ICONS[l]}</a>' for l, u in SOCIALS)
    c = CONTACT
    return f'''<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-contact">
      <h4>{esc(c["heading"])}</h4>
      <address>{esc(c["street"])}<br>{esc(c["city"])}</address>
      <div class="contact-lines"><a href="{c["tel_href"]}">{esc(c["phone"])}</a><a href="mailto:{c["email"]}">{esc(c["email"])}</a></div>
    </div>
    <div><h4>{esc(FOOTER_PAIN[0])}</h4><ul>{pain}</ul></div>
    <div><h4>{esc(FOOTER_NAV[0])}</h4><ul>{nav}</ul></div>
    <div>
      <div class="badges">{badges}</div>
      <div class="rating">
        <div class="stars"><i aria-hidden="true"></i><span>{esc(RATING["name"])}</span></div>
        <span>{esc(RATING["text"])}</span>
        <a href="{RATING["write_href"]}">{esc(RATING["write"])}</a>
      </div>
    </div>
  </div>
  <div class="foot-bottom"><div class="wrap"><span>{esc(COPYRIGHT)}</span><div class="socials">{socials}</div></div></div>
</footer>'''


def cta_heading_html():
    q, _, rest = CTA_HEADING.partition('? ')
    return f'<span class="q">{esc(q)}?</span> {esc(rest).replace("pijnloos®", "<em>pijnloos®</em>")}'


def cta_html():
    return f'''<section class="cta-band"><canvas class="contours" data-seed="5" aria-hidden="true"></canvas><div class="wrap"><h2>{cta_heading_html()}</h2><a class="btn big" href="afspraak.html">{esc(CTA_BUTTON)}</a></div></section>'''


FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=Instrument+Sans:ital,wght@0,400..700;1,400&family=Instrument+Serif:ital@0;1&family=IBM+Plex+Mono:wght@400;500&display=swap">'


def post_cta_html(current_file):
    for slug, tail in POST_CTA.items():
        if slug_to_file(slug) == current_file:
            return f'<section class="post-cta"><div class="wrap prose">{md_to_html(tail)}</div></section>'
    return ''


def localize(doc):
    """Point image sources and image links at the copies stored next to the site, when we have them."""
    def rep(m):
        url = m.group(2)
        rel = re.sub(r'^https?://(www\.)?bootfitter\.nl/', '', html.unescape(url))
        rel = rel.replace('\u00ad', '')  # local copies are stored without soft hyphens in their names
        if (rel.startswith('wp-content/') or rel.startswith('wp-includes/')) and os.path.isfile(os.path.join(OUT, rel)):
            return m.group(1) + html.escape(rel, quote=True) + m.group(3)
        return m.group(0)
    return re.sub(r'((?:src|href)=")(https?://(?:www\.)?bootfitter\.nl/wp-[^"]+)(")', rep, doc)


def page(title, meta_desc, body, current_file, cta=True, full_doc=True):
    return localize(_page(title, meta_desc, body, current_file, cta, full_doc))


def _page(title, meta_desc, body, current_file, cta=True, full_doc=True):
    head = f'''<title>{esc(html.unescape(title))}</title>
<meta name="description" content="{html.escape(meta_desc)}">
{FONTS}
<link rel="icon" href="{ORIGIN}/wp-content/uploads/2021/06/cropped-logo_pijnloos_def_nieuw_oranje_KL-270x270.jpg">
<link rel="stylesheet" href="style.css">'''
    inner = f'''{header_html(current_file)}
<main id="main">
{body}
</main>
{cta_html() if cta else ''}
{post_cta_html(current_file)}
{footer_html()}
<script src="app.js"></script>'''
    if not full_doc:
        return head + '\n' + inner + '\n'
    return f'''<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head}
</head>
<body class="{'home' if current_file == 'index.html' else 'inner'}">
{inner}
</body>
</html>
'''


# ---------------------------------------------------------------- helpers
def inline(s):
    """Render one line of inline markdown without a wrapping <p>."""
    h = markdown.markdown(s.strip(), output_format='html')
    h = re.sub(r'^<p>(.*)</p>$', r'\1', h, flags=re.S)
    return rewrite_links(h)


POST_CTA = {}
CURRENT = [None]


def strip_cta(body):
    m = re.search(r'^#{1,3} Pijn in voeten of scheenbenen\?.*$', body, re.M)
    if m:
        tail = body[m.end():]
        tail = re.sub(r'^\s*\[Maak direct een afspraak\]\([^)]*\)', '', tail).strip()
        if tail:
            POST_CTA[CURRENT[0]] = tail
        return body[:m.start()].rstrip()
    return body


def split_sections(body):
    """Split markdown on headings of level <= 3, returning [(heading_line or None, text)]."""
    parts = re.split(r'(?m)^(#{1,3} .*)$', body)
    out = [(None, parts[0])]
    for i in range(1, len(parts), 2):
        out.append((parts[i], parts[i + 1]))
    return out


def is_link_list(text):
    lines = [l for l in text.strip().splitlines() if l.strip()]
    return bool(lines) and all(re.match(r'^\s*[-*] \[[^\]]+\]\([^)]+\)\s*$', l) for l in lines)


def img_tag(alt, src, cls='', loading='lazy'):
    return f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" loading="{loading}"{(" class=%s" % cls) if cls else ""}>'


IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')

POST_SIDEBAR = None


def blog_aside():
    global POST_SIDEBAR
    if POST_SIDEBAR is None:
        t = open(os.path.join(COPY, '_blog_sidebar.md'), encoding='utf-8').read()
        lines = t.strip().splitlines()
        title = lines[0].lstrip('# ').strip()
        sub = lines[2].lstrip('# ').strip()
        items = re.findall(r'^### \[([^\]]+)\]\(([^)]+)\)\s*\n+\s*(.+)$', t, re.M)
        lis = ''.join(f'<li><a href="{local_href(u)}">{esc(ti)}</a><span>{esc(d.strip())}</span></li>' for ti, u, d in items)
        POST_SIDEBAR = f'<aside class="side blog-side"><h2>{esc(title)}</h2><p>{esc(sub)}</p><ul class="post-list">{lis}</ul></aside>'
    return POST_SIDEBAR


def hero(h1_html, crumbs_html='', extra=''):
    return f'''<section class="page-hero"><canvas class="contours" data-seed="{random_seed()}" aria-hidden="true"></canvas><div class="wrap"><h1{' class="long"' if len(re.sub('<[^>]+>', '', h1_html)) > 70 else ''}>{h1_html}</h1>{crumbs_html}{extra}</div></section>'''


_seed = [1]


def random_seed():
    _seed[0] += 1
    return _seed[0] * 1.37


# ---------------------------------------------------------------- generic page
def render_generic(slug, meta, body, is_post=False):
    body = strip_cta(body)
    lead_imgs = []
    # images placed before the H1 (featured image on posts)
    m = re.search(r'(?m)^# .*$', body) or re.search(r'(?m)^## .*$', body)
    if m:
        pre = body[:m.start()]
        lead_imgs = IMG_RE.findall(pre)
        pre_rest = IMG_RE.sub('', pre).strip()
        h1 = m.group(0).lstrip('#').strip()
        body = (pre_rest + '\n\n' if pre_rest else '') + body[m.end():]
    else:
        h1 = None
    crumbs = ''
    cm = re.search(r'(?m)^\[Home\]\([^)]*\)\s*>.*$', body)
    if cm:
        segs = [s.strip() for s in cm.group(0).split('>')]
        crumbs = '<nav class="crumbs" aria-label="Kruimelpad">' + ' <span class="sep">&gt;</span> '.join(inline(s) for s in segs) + '</nav>'
        body = body[:cm.start()] + body[cm.end():]
    byline = ''
    bm = re.match(r'\s*- (\S[^\n]*)\n- \s*(\d{1,2} \w+ \d{4})\s*\n', body)
    if bm:
        byline = f'<p class="post-date"><span>{esc(bm.group(1).strip())}</span> <time>{esc(bm.group(2))}</time></p>'
        body = body[bm.end():]
    # trailing link-list sections become the aside
    secs = split_sections(body)
    aside_parts = []
    while len(secs) > 1 and secs[-1][0] and is_link_list(secs[-1][1]):
        hd, tx = secs.pop()
        items = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', tx)
        lis = ''.join(f'<li><a href="{local_href(u)}">{esc(t)}</a></li>' for t, u in items)
        aside_parts.insert(0, f'<div class="side-block"><h2>{inline(hd.lstrip("# "))}</h2><ul>{lis}</ul></div>')
    body = ''.join((h + '\n' if h else '') + t for h, t in secs)
    prose = md_to_html(body)
    feat = ''
    if lead_imgs:
        feat = ''.join(f'<figure class="media feature">{img_tag(a, s, loading="eager")}</figure>' for a, s in lead_imgs[:1])
        prose_extra = ''.join(f'<p>{img_tag(a, s)}</p>' for a, s in lead_imgs[1:])
        prose = prose_extra + prose
    if h1 is None:
        h1 = html.unescape(meta.get('TITLE', '')).split(' - ')[0]
        h1_html = None
    else:
        h1_html = inline(h1)
    aside = ''
    if is_post:
        aside = blog_aside()
    elif aside_parts:
        aside = '<aside class="side">' + ''.join(aside_parts) + '</aside>'
    hero_html = hero(h1_html, crumbs, byline) if h1_html else ''
    layout = 'with-side' if aside else 'solo'
    return f'''{hero_html}
<div class="wrap content {layout}">
  <article class="prose">{feat}{prose}</article>
  {aside}
</div>'''


# ---------------------------------------------------------------- home
def section_map(body):
    secs = split_sections(body)
    return secs


HOTSPOTS = {  # measured from the live homepage (Elementor hotspots), % of the boot photo
    'Kuit': (30.3, 8.2), 'Scheenbeen': (58.8, 23.3), 'Enkel': (22.3, 67.1),
    'Wreef': (59.7, 69.7), 'Kleine teen': (71.3, 89.3), 'Voetholte': (50.0, 94.8),
}


def zslug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


# The live homepage hero is a photo of snow-covered pine trees; the file comes from the live site's Elementor CSS.
HERO_BG = None
for _p in ['wp-content/uploads/hero-sneeuw.jpg']:
    if os.path.isfile(os.path.join(OUT, _p)):
        HERO_BG = _p


def render_home(meta, body):
    body = strip_cta(body)
    secs = split_sections(body)
    S = {h: t for h, t in secs if h}
    get = lambda key: next(t for h, t in secs if h and h.lstrip('# ').startswith(key))
    hd = lambda key: next(h for h, t in secs if h and h.lstrip('# ').startswith(key)).lstrip('# ')
    h1 = hd('Het geheim')
    lede = hd('Pijn in uw voeten')
    btns = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', get('Pijn in uw voeten'))
    actions = ''.join(f'<a class="btn{" ghost" if i else ""}" href="{local_href(u)}">{esc(t)}</a>' for i, (t, u) in enumerate(btns))
    actions = actions.replace('</a><a', '</a> <a')
    h1_html = esc(h1).replace('pijnloos skiën®', '<em>pijnloos skiën®</em>')
    lede_html = esc(lede).replace('? ', '? <br>', 1)
    bg = f'<img class="hero-bg" src="{HERO_BG}" alt="" role="presentation" loading="eager" fetchpriority="high">' if HERO_BG else ''
    out = [f'''<section class="hero photo">{bg}<div class="wrap">
<div class="hero-copy"><h1>{h1_html}</h1><div class="hero-foot"><p class="lede">{lede_html}</p><div class="actions">{actions}</div></div></div>
</div><a class="scroll-cue" href="#intro" aria-hidden="true" tabindex="-1"></a></section>''']
    # intro + definition
    intro = md_to_html(get('Pijnloos skiën®'))
    deft = get('Definitie bootfitting:')
    out.append(f'''<section class="section" id="intro"><div class="wrap split">
<div class="intro-copy"><h2>{esc(hd('Pijnloos skiën®'))}</h2>{intro}</div>
<div class="definition"><canvas class="contours" data-seed="9" aria-hidden="true"></canvas><h3>{esc(hd('Definitie bootfitting:'))}</h3>{md_to_html(deft)}</div>
</div></section>''')
    # complaints + zones
    comp = get('Herkent u')
    lst, _, rest = comp.partition('\n\n', ) if False else (None, None, None)
    items = re.findall(r'^- (.+)$', comp, re.M)
    after = [p for p in re.split(r'\n\s*\n', comp) if p.strip() and not p.strip().startswith('- ')]
    solve = after[0].strip()
    img = IMG_RE.search(comp)
    zones = re.findall(r'\*\*([^*]+)\*\*\s*\n+((?:(?!\*\*).+\n?)+)', comp)
    credit = [p.strip() for p in after if p.strip().startswith('©')][0]
    zl = ''.join(f'<div class="zone" id="zone-{zslug(n)}" data-zone="{zslug(n)}"><strong>{esc(n)}</strong><p>{"<br>".join(esc(x.strip()) for x in d.strip().splitlines() if x.strip())}</p></div>' for n, d in zones)
    # hotspots on the boot photo (side view: heel left, toe right), positions in % of the image
    spots = ''.join(f'<button type="button" class="hs" data-zone="{zslug(n)}" style="--x:{HOTSPOTS[n][0]}%;--y:{HOTSPOTS[n][1]}%" aria-label="{html.escape(n)}" aria-describedby="zone-{zslug(n)}"><span></span></button>' for n, d in zones if n in HOTSPOTS)
    li = ''.join(f'<li>{inline(i)}</li>' for i in items)
    out.append(f'''<section class="section alt"><div class="wrap">
<div class="section-head"><h2>{esc(hd('Wat kan een bootfitter'))}</h2><h3 class="sub">{esc(hd('Herkent u'))}</h3></div>
<div class="zones"><div class="zones-copy"><ul class="complaints">{li}</ul>
<p class="solve">{esc(solve)}</p></div>
<figure class="zones-fig"><div class="media hotspots">{img_tag(img.group(1), img.group(2))}{spots}<div class="hs-tip" aria-hidden="true" hidden></div></div>
<div class="zone-list sr-only">{zl}</div><figcaption class="zone-credit">{esc(credit)}</figcaption></figure></div>
</div></section>''')
    # choices
    cards = []
    choice_heads = [(h, t) for h, t in secs if h and h.startswith('### [')]
    # images belong to the text *before* each heading
    order = [h for h, t in secs if h]
    for h, t in choice_heads:
        idx = order.index(h)
        prev_text = secs[idx][1]  # secs has a leading (None, pre) entry, so secs[idx] is the previous section
        im = IMG_RE.search(prev_text)
        title, href = re.match(r'### \[([^\]]+)\]\(([^)]+)\)', h).groups()
        paras = t.strip().split('  \n')
        desc = paras[0].strip()
        more_t, more_u = re.match(r'\[([^\]]+)\]\(([^)]+)\)', paras[1].strip()).groups()
        cards.append(f'''<article class="choice"><a class="media" href="{local_href(href)}" tabindex="-1">{img_tag(im.group(1), im.group(2))}</a>
<div class="body"><h3><a href="{local_href(href)}">{esc(title)}</a></h3><p>{esc(desc)}</p><a class="more" href="{local_href(more_u)}">{esc(more_t)}</a></div></article>''')
    out.append(f'''<section class="section"><div class="wrap"><div class="section-head"><h2>{esc(hd('Wat wilt u doen?'))}</h2></div><div class="choices">{''.join(cards)}</div></div></section>''')
    # is / is not
    def ul(key):
        return ''.join(f'<li>{inline(i)}</li>' for i in re.findall(r'^- (.+)$', get(key), re.M))
    out.append(f'''<section class="section alt"><div class="wrap isnot">
<div class="is"><h3>{esc(hd('Wat is DutchBootFitter ?'))}</h3><ul>{ul('Wat is DutchBootFitter ?')}</ul></div>
<div class="not"><h3>{esc(hd('Wat is DutchBootFitter niet'))}</h3><ul>{ul('Wat is DutchBootFitter niet')}</ul></div>
</div></section>''')
    # FAQ
    faq = get('DutchBootFitter meest gestelde')
    qa = re.split(r'(?m)^> (.+)$', faq)
    dets = []
    for i in range(1, len(qa), 2):
        dets.append(f'<details{" open" if i == 1 else ""}><summary>{esc(qa[i].strip())}</summary><div class="answer">{md_to_html(qa[i + 1])}</div></details>')
    out.append(f'''<section class="section"><div class="wrap"><h2 class="faq-title">{esc(hd('DutchBootFitter meest gestelde'))}</h2><div class="faq">{''.join(dets)}</div></div></section>''')
    return '\n'.join(out)


# ---------------------------------------------------------------- pijn in voeten overview
def render_pain(meta, body):
    body = strip_cta(body)
    secs = split_sections(body)
    h1 = next(h for h, t in secs if h and h.startswith('# '))[2:]
    imgs_by_alt = {}
    cards = []
    pending = []  # images that appear before a heading belong to it
    for i, (h, t) in enumerate(secs):
        if not h or not h.startswith('## '):
            continue
        im = IMG_RE.findall(t)
        text = IMG_RE.sub('', t).strip()
        title_md = h[3:]
        tm = re.match(r'\[([^\]]+)\]\(([^)]+)\)', title_md)
        cards.append((tm, text, im))
    # each section's text may hold the next card's image (page order quirk): match images by heading text
    all_imgs = IMG_RE.findall(body)
    out = []
    for tm, text, im in cards:
        title, href = tm.groups()
        best, score = None, 0
        words = [w for w in title.lower().split() if len(w) > 4 and not w.startswith('skischoen')]
        for a, s in all_imgs:
            n = sum(w in a.lower() for w in words)
            if n > score:
                best, score = (a, s), n
        text = re.sub(r'\*\*Oplossing:\*\*', '\n\n**Oplossing:**', text)
        media = f'<a class="media" href="{local_href(href)}" tabindex="-1">{img_tag(*best)}</a>' if best else ''
        out.append(f'<article class="card pain">{media}<div class="body"><h2><a href="{local_href(href)}">{esc(title)}</a></h2>{md_to_html(text)}</div></article>')
        if best: all_imgs.remove(best)
    leftovers = ''.join(f'<p>{img_tag(a, s)}</p>' for a, s in all_imgs)
    return f'''{hero(esc(h1))}
<div class="wrap content"><div class="card-grid">{''.join(out)}</div>{leftovers}</div>'''


# ---------------------------------------------------------------- blog archive pages
def render_category(meta, body):
    body = strip_cta(body)
    i = body.find('## Volg hier')
    body = body[i:]
    intro = body.splitlines()[0][3:]
    rest = body[len(body.splitlines()[0]):]
    lines = rest.rstrip().splitlines()
    k = len(lines)
    while k > 0 and lines[k - 1].startswith('- '):
        k -= 1
    pager_md = '\n'.join(lines[k:])
    rest = '\n'.join(lines[:k])
    entries = re.split(r'(?m)^\[Bootfitter BLOG\]\([^)]*\)\s*$', rest)
    cards = []
    cat_label = 'Bootfitter BLOG'
    for e in entries:
        tm = re.search(r'(?m)^## \[([^\]]+)\]\(([^)]+)\)', e)
        if not tm:
            continue
        title, href = tm.groups()
        after = e[tm.end():]
        im = IMG_RE.search(after)
        after_noimg = re.sub(r'\[?!\[[^\]]*\]\([^)]*\)\]?(\([^)]*\))?', '', after)
        paras = [p.strip() for p in re.split(r'\n\s*\n', after_noimg) if p.strip()]
        excerpt = paras[0] if paras else ''
        sr = next((p for p in paras if p.startswith('Reacties uitgeschakeld')), '')
        date = next((p for p in paras if re.match(r'^\d{1,2} \w+ \d{4}$', p)), '')
        extra = [p for p in paras[1:] if p not in (sr, date)]
        cap = ''.join(f'<p class="caption">{inline(p)}</p>' for p in extra)
        media = f'<a class="media" href="{local_href(href)}" tabindex="-1">{img_tag(im.group(1), im.group(2))}</a>' if im else ''
        cards.append(f'''<article class="card">{media}<div class="body"><p class="meta"><a href="blog.html">{esc(cat_label)}</a></p><h2><a href="{local_href(href)}">{esc(title)}</a></h2><p>{inline(excerpt)}</p><span class="sr-only">{esc(sr)}</span><p class="date"><time>{esc(date)}</time></p>{cap}</div></article>''')
    pg = []
    for line in pager_md.strip().splitlines():
        line = line[2:].strip()
        lm = re.match(r'\[([^\]]+)\]\(([^)]+)\)', line)
        if lm:
            t, u = lm.groups()
            u = re.sub(r'/page/1/$', '/', u)
            pg.append(f'<a href="{local_href(u)}">{esc(t)}</a>')
        else:
            pg.append(f'<span aria-current="page">{esc(line)}</span>')
    return f'''{hero(esc(intro))}
<div class="wrap content"><div class="card-grid">{''.join(cards)}</div><nav class="pager" aria-label="Paginering">{' '.join(pg)}</nav></div>'''


# ---------------------------------------------------------------- testimonials
SIGNATURE_END = ('Groeten Eef van Schaik', 'Anneke Wiesenekker', 'Bert Advocaat', 'Lisette',
                 '@hberkenbosch via Twitter', 'Groet Esther', 'Groeten, Rixt Bonte, Den Haag',
                 'Jon Petter Olsen', 'Yves', 'Groeten Reinier Vogels')
SLIDER_CONTROLS = ('Vorige', 'Volgende')  # carousel buttons of the old slider; the grid needs none


def para_html(p):
    lines = [l.rstrip() for l in p.strip().splitlines()]
    return '<br>'.join(inline(l) for l in lines)


def render_reacties(meta, body):
    body = strip_cta(body)
    secs = split_sections(body)
    h1 = next(h for h, t in secs if h and h.startswith('# '))[2:]
    h2, txt = next((h, t) for h, t in secs if h and h.startswith('## '))
    paras = [p for p in re.split(r'\n\s*\n', txt) if p.strip() and p.strip() not in SLIDER_CONTROLS]
    quotes, cur = [], []
    for p in paras:
        cur.append(p)
        if p.strip().splitlines()[-1].strip() in SIGNATURE_END:
            quotes.append(cur); cur = []
    if cur:
        quotes.append(cur)
    qh = []
    for q in quotes:
        parts = []
        for p in q:
            im = IMG_RE.fullmatch(p.strip())
            parts.append(f'<figure class="media">{img_tag(im.group(1), im.group(2))}</figure>' if im else f'<p>{para_html(p)}</p>')
        qh.append(f'<blockquote class="quote">{"".join(parts)}</blockquote>')
    return f'''{hero(esc(h1), extra=f'<p class="lede">{esc(h2[3:])}</p>')}
<div class="wrap content"><div class="quotes">{''.join(qh)}</div></div>'''


# ---------------------------------------------------------------- werkwijze (flow diagram)
def render_werkwijze(meta, body):
    body = strip_cta(body)
    flow_h = '## De flow of werkwijze van DutchBootFitter'
    before, _, after = body.partition(flow_h)
    nxt = after.index('### Flow in plaats van een stappenplan')
    flow_txt, rest = after[:nxt], after[nxt:]
    img = IMG_RE.search(flow_txt)
    nodes = [p for p in re.split(r'\n\s*\n', IMG_RE.sub('', flow_txt)) if p.strip()]
    N = [para_html(p) for p in nodes]
    # Node order on the page: Afspraak, Gesprek, Assessment, Pathologie?, JA, NEE, Podologische behandeling,
    # Podologisch rapport, Maatskischoenen of eigen, Aanpassen eigen, Aanmeten maat, Skiën, Skiën, Afhalen
    assert len(N) == 14, len(N)
    flow = f'''<figure class="flow" aria-label="{html.escape(img.group(1))}">
  <div class="flow-step start">{N[0]}</div>
  <div class="flow-step">{N[1]}</div>
  <div class="flow-step">{N[2]}</div>
  <div class="flow-step decision">{N[3]}</div>
  <div class="flow-branches">
    <span class="flow-tag yes">{N[4]}</span><span class="flow-tag no">{N[5]}</span>
    <div class="flow-branch">
      <div class="flow-step">{N[6]}</div>
      <div class="flow-step">{N[7]}</div>
    </div>
    <div class="flow-branch">
      <div class="flow-step decision">{N[8]}</div>
      <div class="flow-split">
        <div class="flow-step a1">{N[9]}</div>
        <div class="flow-step b1">{N[10]}</div>
        <div class="flow-step end ski b2">{N[11]}</div>
        <div class="flow-step end ski a3">{N[12]}</div>
        <div class="flow-step end a2">{N[13]}</div>
      </div>
    </div>
  </div>
</figure>'''
    # keep everything else generic
    page_html = render_generic('werkwijze-dutchbootfitter', meta, before + '\nFLOWPLACEHOLDER\n\n' + rest)
    return page_html.replace('<p>FLOWPLACEHOLDER</p>', f'<h2>{esc(flow_h[3:])}</h2>{flow}')


# ---------------------------------------------------------------- tarieven (price list)
def render_tarieven(meta, body):
    body = strip_cta(body)
    secs = split_sections(body)
    h1 = next(h for h, t in secs if h and h.startswith('# '))[2:]
    h2, txt = secs[[h for h, t in secs].index(next(h for h, t in secs if h and h.startswith('## Overzicht')))]
    rows = []
    for item in re.findall(r'(?m)^- (.+)$', txt):
        m = re.match(r'\[([^\]]+)\]\(([^)]+)\)\s*(.*)$', item)
        name, href, rest = m.groups()
        assert rest.startswith(name), (name, rest[:40])  # the page shows the name once; the copy repeats it
        rest = rest[len(name):].strip()
        name = name.replace('\\*', '*')
        pm = re.match(r'^((?:tussen )?€ \d+(?: en € \d+)?)\s+(.*)$', rest)
        price, desc = pm.groups()
        rows.append(f'''<article class="price"><div class="price-head"><h3><a href="{local_href(href)}">{esc(name)}</a></h3><p class="amount">{esc(price)}</p></div><p>{esc(desc)}</p></article>''')
    remaining = ''.join((h + '\n' if h else '') + t for h, t in secs if h not in (None, '# ' + h1, h2))
    rem_page = render_generic('tarieven-bootfitting', meta, '# X\n' + remaining)
    rem_inner = rem_page.split('<div class="wrap content', 1)[1]
    return f'''{hero(esc(h1), extra=f'<p class="lede">{esc(h2[3:])}</p>')}
<div class="wrap content"><div class="price-list">{''.join(rows)}</div></div>
<div class="wrap content{rem_inner}'''


# ---------------------------------------------------------------- main
SPECIAL = {
    'home': render_home,
    'pijn-in-voeten': render_pain,
    'reacties-van-klanten-referenties': render_reacties,
    'werkwijze-dutchbootfitter': render_werkwijze,
    'tarieven-bootfitting': render_tarieven,
}


def build(artifact_index=False):
    global KNOWN
    KNOWN = known_slugs()
    os.makedirs(OUT, exist_ok=True)
    for f in ('style.css', 'app.js'):
        shutil.copy(os.path.join(ROOT, f), os.path.join(OUT, f))
    pages = sorted(s for s in KNOWN if not s.startswith('_'))
    for slug in pages:
        CURRENT[0] = slug
        meta, body = parse_copy(slug)
        if slug in SPECIAL:
            main = SPECIAL[slug](meta, body)
        elif slug.startswith('category__'):
            main = render_category(meta, body)
        else:
            main = render_generic(slug, meta, body, is_post=slug.startswith('bootfitting_blog__'))
        fn = slug_to_file(slug)
        title = meta.get('TITLE') or slug
        doc = page(title, meta.get('META', ''), main, fn)
        open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(doc)
        if slug == 'home':
            open(os.path.join(BASE, 'artifact-index.html'), 'w', encoding='utf-8').write(page(title, meta.get('META', ''), main, fn, full_doc=False))
    print('built', len(pages), 'pages')


if __name__ == '__main__':
    build()

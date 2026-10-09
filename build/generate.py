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
from chrome import O, TOPBAR, NAV, FOOTER_PAIN, FOOTER_NAV, CONTACT, BADGES, RATING, COPYRIGHT, SOCIALS, SKIP, MENU_OPEN, MENU_CLOSE, CTA_HEADING, CTA_BUTTON

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
    url = fix_url(url)
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


# Link fixes from seo/Kapotte-links-bootfitter.pdf (check of 5 October 2026). Only link targets change, never the text.
LINK_FIXES = {
    # 1. spam / gambling domains
    'josefsdas.restaurant': 'https://www.falstaff.com/en/restaurants/josefs-das-restaurant-radstadt',
    'villa-trapp.com': 'https://www.tripadvisor.com/Attraction_Review-g190441-d14136309-Reviews-Villa_Trapp-Salzburg_Austrian_Alps.html',
    'ski-mojo.info/wp-content/uploads/2023/06/Ski-Mojo-user-guide-eng.pdf': 'https://www.ski-mojo.com/wp-content/uploads/Documents/User-Guide-Ski-Mojo.pdf',
    # 2. internal links to pages that no longer exist
    'bootfitter.nl/bootfitting/afspraak-met-de-podoloog': ORIGIN + '/afspraak/',
    'bootfitter.nl/?page_id=5718': ORIGIN + '/afspraak/',
    'bootfitter.nl/afspraak_maken': ORIGIN + '/afspraak/',
    'bootfitter.nl/afspraak_met_de_podoloog': ORIGIN + '/afspraak/',
    'bootfitter.nl/op_maat_gemaakte_skischoenen': ORIGIN + '/bootfitting/op-maat-gemaakte-skischoenen/',
    'bootfitter.nl/informatie': ORIGIN + '/bootfitting/',
    # 3. links that only worked through a WordPress redirect
    'bootfitter.nl/contact': ORIGIN + '/afspraak/',
    'bootfitter.nl/bootfitting/skimojo-aanmeten': ORIGIN + '/bootfitting/ski-mojo-home/skimojo-aanmeten/',
    'bootfitter.nl/bootfitting/strolz-op-maat-gemaakte-skischoenen-aanmeten': ORIGIN + '/strolz-op-maat-gemaakte-skischoenen-aanmeten/',
    'bootfitter.nl/pijn-in-voeten/brede-voeten': ORIGIN + '/pijn-in-voeten/brede-voeten-in-een-smalle-skischoen/',
    'bootfitter.nl/bootfitting_blog/scheenbeenpijn-tij': ORIGIN + '/bootfitting_blog/scheenbeenpijn-tijdens-het-skien-oorzaak-en-oplossing/',
    'bootfitter.nl/category/bootfitting_blog/page/1': ORIGIN + '/category/bootfitting_blog/',
    # 4. dead external links
    'almkanal.at/surfen_almkanal_welle.html': 'https://www.almkanal.at/',
    'salzkammergut.at/sehenswertes/bahnen-bergbahnen/oesterreich-poi/detail/400929/schafbergbahn.html': 'https://www.5schaetze.at/de/schafbergbahn.html',
    'zipfit.com/en-eu': 'https://www.zipfit.com/',
    'fuerst.cc/en/history': 'https://www.original-mozartkugel.com/',
    'cafe-freiraum.at': 'https://www.altenmarkt-zauchensee.at/en/infrastructure/altenmarkt-zauchensee-cafe-freiraum.html',
}
# Keep the words, drop the link: Mayer's Restaurant closed for good; auszeit-radstadt.at and the deskline page the
# report suggested both no longer resolve; tula-bistro.at, its en. subdomain and its salzburg.info listing are all gone
# (checked October 2026).
LINK_REMOVE = {'schloss-prielau.at/mayers-restaurant', 'auszeit-radstadt.at', 'tula-bistro.at'}


def link_key(url):
    k = re.sub(r'^(https?:)?//', '', url.strip()).split('#')[0]
    k = re.sub(r'^www\.', '', k).rstrip('/')
    return k.lower() if '?' not in k else k.lower()


def fix_url(url):
    return LINK_FIXES.get(link_key(url), url)


def rewrite_links(h):
    def drop(m):
        return m.group(2) if link_key(html.unescape(m.group(1))) in LINK_REMOVE else m.group(0)
    h = re.sub(r'<a\b[^>]*?\bhref="([^"]*)"[^>]*>(.*?)</a>', drop, h, flags=re.S)

    def rep(m):
        return m.group(1) + html.escape(local_href(fix_url(html.unescape(m.group(2)))), quote=True) + m.group(3)
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
    h = re.sub(r'(<a [^>]*>)?<img [^>]*tinymce[^>]*loader\.gif[^>]*>(</a>)?', '', h)  # leftover of the WordPress editor
    h = re.sub(r'<table>', '<div class="table-wrap"><table>', h)
    h = re.sub(r'</table>', '</table></div>', h)
    h = re.sub(r'<p>VIDEO: (\S+)</p>', lambda m: f'<div class="embed video"><iframe src="{m.group(1)}" title="" loading="lazy" allowfullscreen></iframe></div>', h)
    h = re.sub(r'<p>EMBED: (\S+)</p>', lambda m: f'<div class="embed"><iframe src="{m.group(1)}" title="" loading="lazy"></iframe></div>', h)
    h = re.sub(r'src="https?://(?:www\.)?bootfitter\.nl/wp-content/uploads/elementor/thumbs/(DBF-\d+)-[^"]+"',
               lambda m: f'src="{THUMB_TO_SHOP[m.group(1)]}"' if m.group(1) in THUMB_TO_SHOP else m.group(0), h)
    # three or more photos in a row become a gallery grid
    h = re.sub(r'(?:<p><img [^>]*></p>\s*){3,}', lambda m: '<div class="gallery">' + re.sub(r'</?p>', '', m.group(0)) + '</div>', h)
    h = re.sub(r'<img (?![^>]*loading=)', '<img loading="lazy" ', h)
    return rewrite_links(h)


def esc(s):
    return html.escape(s, quote=False)


def header_html(current_file):
    def link(label, url, cls=''):
        href = local_href(url)
        cur = ' aria-current="page"' if href == current_file else ''
        return f'<a href="{href}"{cur}{cls}>{esc(label)}</a>'
    items = []
    for entry in NAV:
        label, url, children = entry
        if children:
            sub = ''.join(f'<li>{link(l, u)}</li>' for l, u in children)
            items.append(f'<li class="has-sub"><button class="sub-toggle" type="button" aria-expanded="false">{esc(label)}</button><ul class="submenu">{sub}</ul></li>')
        else:
            cls = ' class="nav-cta"' if label == 'Afspraak' else ''
            items.append(f'<li{cls}>{link(label, url)}</li>')
    # v8: one quiet bar (logo left, menu right, orange Afspraak); no announcement line.
    afspraak = local_href(O + '/afspraak/')
    cur = ' aria-current="page"' if afspraak == current_file else ''
    return f'''<a class="skip" href="#main">{esc(SKIP)}</a>
<header class="site-header">
  <div class="wrap"><div class="bar">
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary"><span class="bars" aria-hidden="true"></span><span class="lbl-open">{esc(MENU_OPEN)}</span><span class="lbl-close">{esc(MENU_CLOSE)}</span></button>
    <nav class="primary" id="primary" aria-label="Hoofdmenu"><ul class="nav">{''.join(items)}</ul></nav>
    <a class="brand" href="index.html"><img src="{ORIGIN}/wp-content/uploads/2021/06/cropped-logo_pijnloos_def_nieuw_oranje-1.png" alt="Logo DutchBootFitter" width="132" height="54"><span class="brand-mark" aria-hidden="true">Dutch<b>Boot</b>Fitter</span></a>
    <div class="bar-actions">
      <a class="act-cta" href="{afspraak}"{cur}>Afspraak</a>
    </div>
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
    utility = ''.join(f'<a href="{local_href(u)}">{esc(l)}</a>' for l, u in TOPBAR)
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
        <a class="ti-badge" href="{RATING["write_href"]}" target="_blank" rel="noopener"><img src="{O}/wp-content/uploads/2024/06/Trustindex-dutchbootfitter-150x150.jpg" alt="Google review schrijven" width="96" height="96" loading="lazy"></a>
        <a href="{RATING["write_href"]}">{esc(RATING["write"])}</a>
      </div>
    </div>
  </div>
  <div class="foot-bottom"><div class="wrap"><span>{esc(COPYRIGHT)}</span><nav class="foot-utility" aria-label="Topbar">{utility}</nav><div class="socials">{socials}</div></div></div>
</footer>'''


# Photos of the shop on the IJburglaan, from the live site's media library (alt texts as used there).
W = 'wp-content/uploads/winkel/'
SHOP = {
    'wachtruimte': (W + 'DBF-03.jpg', 'DutchBootFitter wachtruimte'),
    'wall': (W + 'DBF-01.jpg', 'DutchBootFitter wall'),
    'steunzolen': (W + 'DBF-02.jpg', 'DutchBootFitter steunzolen'),
    'klachten': (W + 'DBF-07.jpg', 'DutchBootFitter meest voorkomende klachten'),
    'assessment': (W + 'DBF-04.jpg', 'DutchBootFitter assessment'),
    'interieur': (W + 'DBF-12.jpg', 'DutchBootFitter interieur'),
    'keuken': (W + 'DBF-09.jpg', 'DutchBootFitter keuken'),
    'werkbank': (W + 'DBF-08.jpg', 'DutchBootFitter werkbank'),
    'bureau': (W + 'DBF-10.jpg', 'DutchBootFitter bureau'),
    'opmaat': (W + 'DBF-13.jpg', 'DutchBootFitter skischoenen op maat'),
    'skateboard': (W + 'DBF-11.jpg', 'DutchBootFitter'),
    'etalage': (W + 'etalage.jpg', 'DutchBootFitter etalage skiwinkel'),
    'team': (W + 'bart-marco-paul.jpg', 'Bart en Marco-Paul'),
    'slijpen': (W + 'slijpen.jpg', 'DutchBootFitter bootfitting'),
    'praktijk': (W + 'vloer-praktijk.jpg', 'DutchBootFitter bootfitting'),
    'oprekken': (W + 'oprekken.jpg', 'DutchBootFitter bootfitting'),
    'handwerk': (W + 'handwerk-steunzool.jpg', 'DutchBootFitter bootfitter met steunzool'),
    # full-size originals from the bootfitter.nl media library (alt texts as used there)
    'slijpmachine': (W + 'slijpmachine.jpg', 'Slijpmachine'),
    'handwerk-zw': (W + 'handwerk-zw.jpg', 'DutchBootFitter aan het werk'),
    'pers-zw': (W + 'pers-zw.jpg', 'Bootfitting'),
    # the fitting corner: chair and the blue Masterfit box (home, behind the definition card)
    'masterfit': (W + 'masterfit.jpg', 'DutchBootFitter bootfitting'),
}
# The live site shows small Elementor thumbnails of these photos; serve the sharp versions instead.
THUMB_TO_SHOP = {'DBF-%s' % k: W + 'DBF-%s.jpg' % k for k in ('01', '03', '04', '07', '08', '09', '10', '11', '12', '13')}
HERO_OVERRIDE = {'bootfitting': 'slijpmachine', 'bootfitting-mijn-skischoenen-aanpassen': 'oprekken', 'over-ons': 'wall', 'afspraak': 'wachtruimte', 'werkwijze-dutchbootfitter': 'assessment', 'tarieven-bootfitting': 'werkbank'}
HERO_ROTATION = ['wachtruimte', 'werkbank', 'keuken', 'assessment', 'bureau', 'wall', 'steunzolen', 'opmaat', 'slijpen', 'klachten', 'praktijk', 'slijpmachine', 'oprekken']


def shop_img(key, cls='', loading='lazy'):
    src, alt = SHOP[key]
    return img_tag(alt, src, cls, loading)


def cta_heading_html():
    q, _, rest = CTA_HEADING.partition('? ')
    return f'<span class="q">{esc(q)}?</span> {esc(rest).replace("pijnloos®", "<em>pijnloos®</em>")}'


def windmill_svg(uid='sail'):
    # Four latticed windmill sails, drawn like the latticed skis in the DutchBootFitter logo.
    rungs = ''.join(f'M6 {y}H50' for y in range(-206, -50, 16))
    sail = (f'<g id="{uid}"><path d="M-4 -230H4V-14H-4Z" fill="currentColor" stroke="none"/>'
            f'<path d="M6 -222H50V-46H6Z{rungs}M20.7 -222V-46M35.3 -222V-46"/></g>')
    sails = ''.join(f'<use href="#{uid}" transform="rotate({a})"/>' for a in (90, 180, 270))
    return (f'<svg class="windmill" viewBox="-240 -240 480 480" aria-hidden="true" focusable="false">'
            f'<g class="sails" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round">{sail}{sails}'
            f'<circle r="18" fill="currentColor" stroke="none"/></g></svg>')


def cta_html():
    return f'''<section class="cta-band"><div class="wrap"><div class="cta-copy"><h2>{cta_heading_html()}</h2><a class="btn big" href="afspraak.html">{esc(CTA_BUTTON)}</a></div>{windmill_svg('sail-cta')}<figure class="cta-photos"><div class="media a">{shop_img('interieur')}</div></figure></div></section>'''


FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300..800;1,300..800&display=swap">'


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
        if not (rel.startswith('wp-content/') or rel.startswith('wp-includes/')):
            return m.group(0)
        full = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', rel)  # the original upload behind a WordPress thumbnail
        for cand in (full, rel):
            if os.path.isfile(os.path.join(OUT, cand)):
                return m.group(1) + html.escape(cand, quote=True) + m.group(3)
        return m.group(0)
    return re.sub(r'((?:src|href)=")(https?://(?:www\.)?bootfitter\.nl/wp-[^"]+)(")', rep, doc)


def page(title, meta_desc, body, current_file, cta=True, full_doc=True):
    return localize(_page(title, meta_desc, body, current_file, cta, full_doc))


def _page(title, meta_desc, body, current_file, cta=True, full_doc=True):
    head = f'''<title>{esc(html.unescape(title))}</title>
<meta name="description" content="{html.escape(meta_desc)}">
{FONTS}
<link rel="icon" href="{ORIGIN}/wp-content/uploads/2021/06/cropped-logo_pijnloos_def_nieuw_oranje_KL-270x270.jpg">
<link rel="stylesheet" href="style.css?v=14">'''
    inner = f'''{header_html(current_file)}
<main id="main">
{body}
</main>
{cta_html() if cta else ''}
{post_cta_html(current_file)}
{footer_html()}
<script src="app.js?v=9"></script>'''
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
    key = HERO_OVERRIDE.get(CURRENT[0]) or HERO_ROTATION[sum(map(ord, CURRENT[0] or '')) % len(HERO_ROTATION)]
    return f'''<section class="page-hero"><div class="wrap"><div class="ph-copy"><h1{' class="long"' if len(re.sub('<[^>]+>', '', h1_html)) > 70 else ''}>{h1_html}</h1>{crumbs_html}{extra}</div><figure class="ph-photo media">{shop_img(key, loading='eager')}</figure></div></section>'''


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
    if slug == 'afspraak':
        prose = prose.replace('<h3>Maak hieronder uw keuze voor uw afspraak:</h3>\n<p></p>', '<h3>Maak hieronder uw keuze voor uw afspraak:</h3>\n' + planner_html(), 1)
    prose = review_cards(prose)
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
# Short clip of a Strolz boot being foamed to the foot in the shop; plays muted as the hero background.
HERO_VIDEO = W + 'strolz-aanmeten.mp4'
# Phones (portrait): the sharper vertical shot of the same fitting, ending with a client leaving with the bag.
HERO_VIDEO_PORTRAIT = W + 'strolz-aanmeten-staand.mp4'


# Hand-drawn marker strokes (an underline, a cross) that draw themselves in; decorative only.
MARK_SVG = {
    'under': ('<svg class="mark-svg" viewBox="0 0 300 30" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
              '<path pathLength="1" d="M4 13C70 9 160 8 296 11"/><path pathLength="1" d="M30 21C110 15 200 14 240 17"/>'
              '<path pathLength="1" d="M120 26C160 22 200 21 236 22"/></svg>'),
    'cross': ('<svg class="mark-svg" viewBox="0 0 100 60" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
              '<path pathLength="1" d="M4 6C30 18 62 34 90 58"/><path pathLength="1" d="M2 56C26 34 56 10 98 4"/></svg>'),
}


def mark(h, word, kind):
    i = h.rfind(word)
    return h[:i] + f'<span class="mark mark-{kind}">{word}{MARK_SVG[kind]}</span>' + h[i + len(word):]


# The three services on the home: the live site shows small product shots (one only 292 px); these are
# square crops of our own shop photos and the Strolz fitting clip, so the cards read as one set.
SERVICE_PHOTOS = {
    '/mijn-skischoenen-aanpassen/': W + 'dienst-aanpassen-foto.jpg',
    '/op-maat-gemaakte-skischoenen/': W + 'dienst-op-maat-foto.jpg',
    '/strolz-op-maat-gemaakte-skischoenen-aanmeten/': W + 'dienst-strolz-foto.jpg',
}


HEADING_ACCENTS = [
    ('<h2>Pijnloos skiën®</h2>', 'Pijnloos'),
    ('<h2>Wat wilt u doen?</h2>', 'doen?'),
    ('<h2>Wat kan een bootfitter voor u betekenen?</h2>', 'betekenen?'),
    ('Bootfitter FAQ</h2>', 'FAQ'),
]


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
    video = (f'<figure class="hero-video"><video autoplay muted loop playsinline preload="metadata" aria-label="Strolz skischoenen op maat worden aangemeten bij DutchBootFitter"><source src="{HERO_VIDEO_PORTRAIT}" media="(orientation: portrait) and (max-width: 900px)" type="video/mp4"><source src="{HERO_VIDEO}" type="video/mp4"></video></figure>'
             if os.path.isfile(os.path.join(OUT, HERO_VIDEO)) else '')
    out = [f'''<section class="hero photo{' has-video' if video else ''}">{'' if video else bg}<div class="wrap">
<div class="hero-copy"><h1>{h1_html}</h1><div class="hero-foot"><p class="lede">{lede_html}</p><div class="actions">{actions}</div></div><p class="hero-rating" data-reuse><i class="stars" aria-hidden="true"></i>{rq(RATING["text"], "chrome")}</p></div>
{video}</div><a class="scroll-cue" href="#intro" aria-hidden="true" tabindex="-1"></a></section>''']
    # intro + definition
    intro = md_to_html(get('Pijnloos skiën®'))
    # one paragraph with hard line breaks on the live site; shown as a lead line (what we stand for) on the left
    # under the heading, the rest on the right. Same words, same order.
    lines = [l.strip() for l in re.sub(r'^\s*<p>|</p>\s*$', '', intro.strip()).split('<br>')]
    intro_copy = (f'<div class="intro-copy"><div class="intro-lead"><h2>{esc(hd("Pijnloos skiën®"))}</h2><p class="lead">{lines[0]}</p></div>'
                  f'<div class="intro-body">{"".join(f"<p>{l}</p>" for l in lines[1:])}</div></div>')
    deft = get('Definitie bootfitting:')
    out.append(f'''<section class="section" id="intro"><div class="wrap split">
{intro_copy}
<div class="intro-visual"><figure class="media intro-photo">{shop_img('masterfit')}</figure>
<div class="definition"><h3>{esc(hd('Definitie bootfitting:'))}</h3>{md_to_html(deft)}</div></div>
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
    out.append(f'''<section class="section alt complaints-sec"><div class="wrap">
<div class="section-head"><h2>{esc(hd('Wat kan een bootfitter'))}</h2><h3 class="sub">{esc(hd('Herkent u'))}</h3></div>
<div class="zones"><div class="zones-copy"><ul class="complaints">{li}</ul>
<p class="solve">{esc(solve)}</p></div>
<figure class="zones-fig"><div class="media hotspots">{img_tag(img.group(1), img.group(2))}{spots}<div class="hs-tip" aria-hidden="true" hidden></div></div>
<div class="zone-list sr-only">{zl}</div><figcaption class="zone-credit">{esc(credit)}</figcaption></figure></div>
</div></section>''')
    strip = ''.join(f'<figure class="media s-{k}">{shop_img(k)}</figure>' for k in ('slijpmachine', 'keuken', 'werkbank', 'steunzolen', 'assessment', 'opmaat', 'oprekken', 'slijpen'))
    out.append(f'<div class="shop-strip" role="group" aria-label="DutchBootFitter IJburglaan"><div class="strip-track" tabindex="0">{strip}</div><div class="strip-nav wrap"><button type="button" class="strip-btn prev" aria-label="Vorige foto"></button><button type="button" class="strip-btn next" aria-label="Volgende foto"></button></div></div>')
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
        photo = next((v for k, v in SERVICE_PHOTOS.items() if href.endswith(k)), im.group(2))  # sharp shop photo, the live site's alt text
        cards.append(f'''<article class="choice"><a class="media" href="{local_href(href)}" tabindex="-1">{img_tag(im.group(1), photo)}</a>
<div class="body"><h3><a href="{local_href(href)}">{esc(title)}</a></h3><p>{esc(desc)}</p><a class="more" href="{local_href(more_u)}">{esc(more_t)}</a></div></article>''')
    # the services come straight after "what we stand for" (hero, intro, services); verify.py compares against home_md()
    out.insert(2, f'''<section class="section choices-sec"><div class="wrap"><div class="section-head"><h2>{esc(hd('Wat wilt u doen?'))}</h2></div><div class="choices">{''.join(cards)}</div></div></section>''')
    # is / is not
    def ul(key):
        return ''.join(f'<li>{inline(i)}</li>' for i in re.findall(r'^- (.+)$', get(key), re.M))
    out.append(f'''<section class="section alt isnot-sec">{windmill_svg('sail-mid')}<div class="wrap isnot">
<div class="is"><h3>{mark(esc(hd('Wat is DutchBootFitter ?')), 'DutchBootFitter', 'under')}</h3><ul>{ul('Wat is DutchBootFitter ?')}</ul></div>
<div class="not"><h3>{mark(esc(hd('Wat is DutchBootFitter niet')), 'niet', 'cross')}</h3><ul>{ul('Wat is DutchBootFitter niet')}</ul></div>
</div></section>''')
    # FAQ
    faq = get('DutchBootFitter meest gestelde')
    qa = re.split(r'(?m)^> (.+)$', faq)
    dets = []
    for i in range(1, len(qa), 2):
        dets.append(f'<details{" open" if i == 1 else ""}><summary>{esc(qa[i].strip())}</summary><div class="answer">{md_to_html(qa[i + 1])}</div></details>')
    out.append(f'''<section class="section faq-sec"><div class="wrap faq-wrap"><h2 class="faq-title">{esc(hd('DutchBootFitter meest gestelde'))}</h2><div class="faq">{''.join(dets)}</div></div></section>''')
    out += home_trust_blocks()
    # one orange key word per heading (markup only, the words stay the same)
    html_out = '\n'.join(out)
    for h, word in HEADING_ACCENTS:
        html_out = html_out.replace(h, h.replace(word, f'<span class="accent">{word}</span>', 1), 1)
    return html_out


# ---------------------------------------------------------------- home 06-08: team, shop, reviews
# These blocks only repeat sentences that already stand elsewhere on the site, word for word. Every text
# fragment carries data-src naming the page it comes from; verify.py checks each one against that page.
# They use no h2/h3, so the heading outline of the home page stays exactly as it was.
# New copy, approved by DutchBootFitter (October 2026); based on the Over Ons text "Zij brachten het 'bootfitten' naar Nederland
# ... En reeds in 2008 werden de eerste klanten geholpen". verify.py accepts data-src="new" only for strings listed here.
HERO_EYEBROW = ('De eerste Certified Master Bootfitters', 'Sinds 2008 brachten zij het bootfitten naar Nederland')
APPROVED_COPY = set(HERO_EYEBROW)


def nw(text, tag='span', cls='', attrs=''):
    """A piece of approved new copy (the appointment planner); verify.py accepts it because it is listed here."""
    APPROVED_COPY.add(text)
    c = f' class="{cls}"' if cls else ''
    return f'<{tag}{c}{attrs} data-src="new">{esc(text)}</{tag}>'


# Appointment planner (October 2026): pick a bootfitter, a service, a day and time, then your details.
# Not connected to a booking system yet: app.js shows a summary and opens an e-mail to the shop with it.
PLANNER_FITTERS = ('Bart', 'Selma', 'Maks')
PLANNER_SERVICES = ('Eigen skischoenen laten aanpassen', 'Op maat gemaakte skischoenen', 'Ski-Mojo aanmeten', 'Advies of iets anders')
PLANNER_TIMES = ('09:30', '11:00', '13:00', '14:30', '16:00')


def planner_html():
    def opts(name, values, avatar=False):
        out = []
        for i, v in enumerate(values):
            av = f'<span class="pl-avatar" aria-hidden="true" data-initial="{v[0]}"></span>' if avatar else ''
            sub = nw('Bootfitter', 'small') if avatar else ''
            out.append(f'<div class="pl-option"><input type="radio" name="{name}" id="pl-{name}-{i}" value="{html.escape(v)}" required>'
                       f'<label for="pl-{name}-{i}">{av}<span>{nw(v)}{"<br>" + sub if sub else ""}</span></label></div>')
        return '<div class="pl-options">' + ''.join(out) + '</div>'
    def step(n, text):
        return f'<legend>{nw(text)}</legend>'
    times = ''.join(nw(t, 'button', 'pl-time', f' type="button" aria-pressed="false" data-time="{t}"') for t in PLANNER_TIMES)
    def field(label, name, typ='text', cls='', extra=''):
        tag = (f'<textarea name="{name}" rows="3"{extra}></textarea>' if typ == 'textarea'
               else f'<input type="{typ}" name="{name}"{extra}>')
        return f'<label class="{cls}">{nw(label)}{tag}</label>'
    return f'''<form class="planner" data-reuse novalidate data-mail="{CONTACT["email"]}">
<fieldset>{step(1, 'Kies uw bootfitter')}{opts('fitter', PLANNER_FITTERS, avatar=True)}</fieldset>
<fieldset>{step(2, 'Waarvoor komt u?')}{opts('dienst', PLANNER_SERVICES)}</fieldset>
<fieldset>{step(3, 'Kies een dag en tijd')}<div class="pl-days" role="group" aria-label="Dag"></div><div class="pl-times" role="group" aria-label="Tijd">{times}</div></fieldset>
<fieldset>{step(4, 'Uw gegevens')}<div class="pl-fields">{field('Naam', 'naam', extra=' autocomplete="name" required')}{field('Telefoonnummer', 'telefoon', 'tel', extra=' autocomplete="tel" required')}{field('E-mailadres', 'email', 'email', 'full', ' autocomplete="email" required')}{field('Opmerking (optioneel)', 'opmerking', 'textarea', 'full')}</div></fieldset>
<div class="pl-submit"><button type="submit" class="btn big">{nw('Afspraak aanvragen')}</button>{nw('Vul alle stappen in.', 'p', 'pl-error', ' hidden')}</div>
<div class="pl-done" hidden>{nw('✓', 'div', 'check', ' aria-hidden="true"')}{nw('Uw aanvraag staat klaar', 'p', 'pl-done-title')}<ul class="pl-summary"></ul>{nw('Verstuur aanvraag per e-mail', 'a', 'btn big pl-mail', ' href="#"')}</div>
</form>'''


planner_html()  # registers the planner's copy in APPROVED_COPY, so verify.py knows it without building


# The Ski-Mojo pages list three customer quotes as stars, quote and name (an Elementor testimonial widget on
# bootfitter.nl); show them as review cards again. Same words, only the markup changes.
REVIEW_RE = re.compile(r'<p>((?:<em>★</em>){5}) (5/5)</p>\n<p>(&quot;|")(.+?)(&quot;|")</p>\n<p>([^<]{1,40})</p>\n?')


def review_cards(h):
    def card(m):
        return (f'<blockquote class="review-card"><p class="rc-stars">{m.group(1)} <span>{m.group(2)}</span></p>'
                f'<p class="rc-text">{m.group(3)}{m.group(4)}{m.group(5)}</p><p class="rc-name">{m.group(6)}</p></blockquote>')
    out = REVIEW_RE.sub(card, h)
    return re.sub(r'((?:<blockquote class="review-card">.*?</blockquote>)+)', r'<div class="review-cards">\1</div>\n', out)


def rq(text, src, tag='span', cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<{tag}{c} data-src="{src}">{esc(text)}</{tag}>'


def rlink(text, href, src, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<a{c} href="{href}" data-src="{src}">{esc(text)}</a>'


HOME_TEAM = [
    "Zij brachten het 'bootfitten' naar Nederland.",
    'En reeds in 2008 werden de eerste klanten geholpen met het aanpassen van hun eigen skischoenen.',
    'DutchBootFitter en Strolz Amsterdam wordt voortgezet door Bart, samen met Selma Cool, de nieuwe partner in het bedrijf.',
    'Hoe mooi is het dat Marco-Paul een positieve voetafdruk achterlaat in de ski- en podologiewereld.',
]
HOME_SHOP = ('wall', 'praktijk', 'handwerk', 'bureau')
HOME_REVIEWS = (1, 5, 7)  # quotes not addressed to Marco-Paul by name


def reacties_quotes():
    _, body = parse_copy('reacties-van-klanten-referenties')
    txt = next(t for h, t in split_sections(strip_cta(body)) if h and h.startswith('## '))
    paras = [p for p in re.split(r'\n\s*\n', txt) if p.strip() and p.strip() not in SLIDER_CONTROLS]
    quotes, cur = [], []
    for p in paras:
        cur.append(p)
        if p.strip().splitlines()[-1].strip() in SIGNATURE_END:
            quotes.append(cur); cur = []
    return quotes


def home_trust_blocks():
    o, r, c = 'over-ons', 'reacties-van-klanten-referenties', 'chrome'
    team = ''.join(rq(t, o, 'p') for t in HOME_TEAM)
    team_sec = f'''<section class="section team-sec" data-reuse><div class="wrap team-wrap">
<div class="team-copy">{rq('Over ons', o, 'p', 'blk-title')}<div class="team-text">{team}</div>{rlink('Over Ons', local_href('https://www.bootfitter.nl/over-ons/'), c, 'btn')}</div>
<figure class="team-photo media">{shop_img('team')}<figcaption>{rq('Bart (l.) & Marco-Paul (r.)', o)}</figcaption></figure>
<figure class="team-craft media">{shop_img('handwerk-zw')}</figure>
</div></section>'''
    tiles = ''.join(f'<figure class="media">{shop_img(k)}</figure>' for k in HOME_SHOP)
    maps = 'https://www.google.com/maps/search/?api=1&query=DutchBootFitter+IJburglaan+1089+Amsterdam'
    shop_sec = f'''<section class="section shop-sec" data-reuse><div class="wrap shop-wrap">
<div class="shop-head">{rq('DutchBootFitter. Een impressie', o, 'p', 'blk-title')}
<address class="shop-address"><a href="{maps}" rel="noopener">{rq(CONTACT['street'], c)}<br>{rq(CONTACT['city'], c)}</a></address>
<p class="shop-lines"><a href="{CONTACT['tel_href']}" data-src="{c}">{esc(CONTACT['phone'])}</a> {rlink(CONTACT['email'], 'mailto:' + CONTACT['email'], c)}</p></div>
<div class="shop-grid">{tiles}</div>
</div></section>'''
    cards = []
    for q in (reacties_quotes()[i] for i in HOME_REVIEWS):
        lines = [l.strip() for p in q for l in p.strip().splitlines() if l.strip()]
        body = ''.join(rq(l, r, 'span') + '<br>' for l in lines[:-1])
        cards.append(f'<blockquote class="review"><p>{body[:-4]}</p><footer>{rq(lines[-1], r, "cite")}</footer></blockquote>')
    rev_sec = f'''<section class="section reviews-sec" data-reuse><div class="wrap">
<div class="reviews-head">{rq('Wat klanten zeggen over DutchBootFitter', r, 'p', 'blk-title')}
<div class="reviews-score"><i class="stars" aria-hidden="true"></i>{rq(RATING['text'], c)}</div></div>
<div class="reviews">{''.join(cards)}</div>
{rlink('Wat klanten zeggen', local_href('https://www.bootfitter.nl/reacties-van-klanten-referenties/'), c, 'btn ghost-dark')}
</div></section>'''
    return [team_sec, shop_sec, rev_sec]


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


# ---------------------------------------------------------------- over ons
def home_md(body):
    """The home copy in reading order: the services ("Wat wilt u doen?") move up to straight after the intro
    (what we stand for). Every block keeps its words; only the block moves. verify.py checks against this."""
    a = body.index('## Wat wilt u doen?')
    b = body.index('### Wat is DutchBootFitter ?')
    services, rest = body[a:b], body[:a] + body[b:]
    i = rest.index('## Wat kan een bootfitter voor u betekenen?')
    return rest[:i] + services + rest[i:]


def over_ons_md(body):
    """The Over Ons copy in reading order: who we are, In Memoriam and who carries on, what the titles mean,
    the shop, then where to go next. Every block keeps its words; only the blocks move. verify.py checks against this."""
    S = {h.strip(): t.strip() for h, t in split_sections(strip_cta(body)) if h}
    h1 = next(h for h in S if h.startswith('# '))
    titles = next(h for h in S if h.startswith('### Bootfitter'))
    gallery, credit = S[h1].rsplit('\n\n', 1)  # the shop photos, then the photo credit line
    # the live page shows the Street View link as an embedded panorama
    street = re.sub(r'^\[(\S+)\]\(\1\)$', r'EMBED: \1', S['## DutchBootFitter. Een impressie'])
    order = [(h1, ''), ('## Over ons', S['## Over ons']), ('## In Memoriam', S['## In Memoriam']),
             ('## Wat is wat..?', S['## Wat is wat..?']), (titles, S[titles]),
             ('## DutchBootFitter. Een impressie', gallery + '\n\n' + street + '\n\n' + credit),
             ('### Wat wilt u doen?', S['### Wat wilt u doen?'])]
    assert set(S) == {h for h, _ in order}, set(S) ^ {h for h, _ in order}
    return '\n\n'.join(h + '\n\n' + t for h, t in order)


def render_over_ons(meta, body):
    secs = [(h.strip(), t) for h, t in split_sections(over_ons_md(body)) if h]
    (h1, _), (story_h, story), (memo_h, memo), (what_h, _), (titles_h, titles), (impr_h, impr), (next_h, nxt) = secs
    # Over ons: the text beside the photo of Bart and Marco-Paul
    team = IMG_RE.search(story)
    caption = re.search(r'(?m)^\*[^*].*\*$', story).group(0)
    text = IMG_RE.sub('', story, count=1).replace(caption, '')
    team_fig = f'<figure class="about-team media">{img_tag(team.group(1), team.group(2))}<figcaption>{inline(caption)}</figcaption></figure>'
    # In Memoriam: the bold one-liners become subheadings, the four closing names a signature
    memo_html = md_to_html(memo)
    memo_html = re.sub(r'<p><strong>([^<]+)</strong></p>', r'<h3>\1</h3>', memo_html)
    memo_html = re.sub(r'((?:<p>[^<]{1,40}</p>\s*){4})', r'<div class="memo-sign">\1</div>', memo_html, count=1)
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', nxt)
    next_lis = ''.join(f'<li><a href="{local_href(u)}">{esc(t)}</a></li>' for t, u in links)
    return f'''{hero(inline(h1.lstrip('# ')))}
<section class="about-story"><div class="wrap prose">
  <h2>{inline(story_h[3:])}</h2>
  {team_fig}
  <div class="story-text">{md_to_html(text)}</div>
</div></section>
<section class="about-memoriam"><div class="wrap"><div class="memo-card prose"><h2>{inline(memo_h[3:])}</h2>{memo_html}</div></div></section>
<section class="about-titles"><div class="wrap">
  <div class="titles-head prose"><h2>{inline(what_h[3:])}</h2><h3>{inline(titles_h[4:])}</h3></div>
  <div class="prose">{md_to_html(titles)}</div>
</div></section>
<section class="about-impression"><div class="wrap">
  <div class="prose"><h2>{inline(impr_h[3:])}</h2></div>
  <figure class="about-pano media">{shop_img('handwerk-zw')}</figure>
  {md_to_html(impr)}
</div></section>
<section class="about-next"><div class="wrap"><h3>{inline(next_h[4:])}</h3><ul>{next_lis}</ul></div></section>'''


# ---------------------------------------------------------------- main
SPECIAL = {
    'home': render_home,
    'pijn-in-voeten': render_pain,
    'reacties-van-klanten-referenties': render_reacties,
    'werkwijze-dutchbootfitter': render_werkwijze,
    'tarieven-bootfitting': render_tarieven,
    'over-ons': render_over_ons,
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

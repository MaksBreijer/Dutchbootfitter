# bootfitter.nl — nieuw ontwerp (overdracht aan Gianni)

Dit is het nieuwe ontwerp voor **bootfitter.nl** (DutchBootFitter), gebouwd als statische voorbeeldsite. Het is
**alleen frontend**: HTML-structuur, CSS en een beetje JavaScript. Er verandert niets aan de inhoud, de URL's of de
backend van WordPress.

> **De drie gouden regels**
> 1. **Bookly niet aanraken.** Het afspraaksysteem (plugin Bookly) blijft precies zoals het is, op alle 4 pagina's.
> 2. **Inhoud niet aanraken.** Teksten, paginatitels, meta-beschrijvingen, H1's, URL's, interne links en alt-teksten
>    blijven in WordPress staan zoals ze nu zijn. Alleen de opmaak verandert. Zo blijven de Google-posities behouden.
> 3. **Geen nieuwe plugins of backend-code.** Alles hieronder kan met het thema/Elementor en eigen CSS/JS.
>
> **Uitzondering:** drie kleine inhoudswijzigingen doe je wél in WordPress, op verzoek van DutchBootFitter (zie §6):
> de Instagram-knop op Ski-Mojo, de Strolz-prijs naar € 1195 en het weghalen van "Lorem ipsum" op Links.

Stand: 17 oktober 2026.

**Inhoud van deze zip:** `README.md` (dit bestand) · `site/` (de voorbeeldsite) · `uploaden/` (de nieuwe media, §5) ·
`build/`, `copy/`, `seo/` (de bron en de controles) · `verification.json` en `alt-check.json` (de uitslag van de controles).

---

## 1. Wat staat waar

| Map / bestand | Inhoud |
|---|---|
| `site/` | De kant-en-klare voorbeeldsite: 71 pagina's, `style.css`, `app.js`. Dit is wat je nabouwt. |
| `site/style.css` | **Alle** opmaak. Dit bestand is het belangrijkste wat je overzet. |
| `site/app.js` | Kleine scripts: mobiel menu, header bij scrollen, fade-in van secties, schoen-hotspots, fotostrip. |
| `site/wp-content/uploads/winkel/` | **Nieuwe** afbeeldingen en video's (bestaan nog niet op de live site; uploaden naar de mediabibliotheek). |
| `site/wp-content/uploads/20xx/...` | Afbeeldingen die al op bootfitter.nl staan (zelfde pad als live; niet opnieuw uploaden). |
| `copy/` | De letterlijke tekst van elke live pagina (Markdown). De bron van de voorbeeldsite. |
| `build/generate.py` | Bouwt `site/` uit `copy/`. Alle keuzes (welke foto waar, enz.) staan hier in tabellen. |
| `build/verify.py` | Controleert elke pagina woord voor woord tegen `copy/` → `verification.json`. |
| `build/check_alts.py` | Vergelijkt de alt-teksten van elke pagina met de live site → `alt-check.json`. |
| `seo/` | SEO-documenten (o.a. de lijst met kapotte links die al gerepareerd zijn). |

Bekijken: open `site/index.html`, of start een lokale server:

```sh
cd site && python3 -m http.server 8765    # dan http://localhost:8765
```

## 2. Stappenplan voor de bouw in WordPress

1. **Back-up** van de live site (bestanden + database) en werk eerst op een staging-kopie.
2. **Lettertype:** Open Sans via Google Fonts (`family=Open+Sans:ital,wght@0,300..800;1,300..800`), zoals nu al.
3. **CSS:** zet `site/style.css` in het (child-)thema of in Elementor → Site-instellingen → Eigen CSS. De kleuren
   staan als variabelen bovenaan (`--orange: #ff6c2f` is het oranje uit het logo).
4. **JS:** zet `site/app.js` in het thema (footer). Het blok "Appointment planner" onderaan wordt **niet** gebruikt
   (Bookly blijft); dat mag je weglaten.
5. **Media:** upload de bestanden uit `site/wp-content/uploads/winkel/` naar de mediabibliotheek (lijst in §5).
6. **Per paginatype de structuur nabouwen** (header, paginakop, kaarten — zie §4). De **tekst zelf laat je in WordPress
   staan**; je verandert alleen de secties/klassen eromheen.
7. **Bookly-pagina's:** alleen de opmaak rond het formulier aanpassen (zie §3).
8. **Controleren vóór livegang** met de checklist in §7.

## 3. Bookly — niet aanraken

Bookly staat op **4 pagina's**. In de voorbeeldsite is die plek gemarkeerd met `<div class="bookly-slot">` en een
HTML-commentaar `<!-- BOOKLY: ... -->`. Daar staat in WordPress het echte Bookly-formulier/shortcode.

| Pagina | URL |
|---|---|
| Afspraak | `/afspraak/` |
| Op maat gemaakte skischoenen | `/bootfitting/op-maat-gemaakte-skischoenen/` |
| Ski-Mojo aanmeten | `/bootfitting/ski-mojo-home/skimojo-aanmeten/` |
| Strolz aanmeten | `/strolz-op-maat-gemaakte-skischoenen-aanmeten/` |

- De Bookly-widget/shortcode, de instellingen, de diensten, de medewerkers en de koppelingen blijven **exact** zoals ze zijn.
- Alleen CSS eromheen mag. Test na elke wijziging een proefboeking op staging.
- Een eigen afspraakplanner bouwen is **niet** de bedoeling.

## 4. Het ontwerp in onderdelen

**Algemeen**
- Witte pagina, lichtgrijze vlakken `#f4f4f4`, oranje `#ff6c2f` als signaalkleur (één oranje sleutelwoord per kop op de home).
- Lettertype Open Sans, normale breedte, koppen vet.

**Header** (alle pagina's)
- Bovenaan een smalle balk met 4 oranje links (Tarieven, Wat klanten zeggen, Bootfitter BLOG, Links) — deze balk is belangrijk en blijft.
- Daaronder logo links, menu rechts, en de oranje knop **Afspraak** als laatste.
- Op de home ligt de balk doorzichtig op de video met wit logo en witte links, en wordt hij wit bij scrollen.

**Home**
- **Video-hero** (`strolz-aanmeten-breed.mp4`, op een staande telefoon `strolz-aanmeten-staand.mp4`): start meteen op het
  eerste beeld, zonder fade, en speelt doorlopend (`autoplay muted loop playsinline`). De poster (`*-poster.jpg`) is
  hetzelfde eerste beeld, zodat er niets verspringt tijdens het laden.
- "Pijnloos skiën®" met de definitie-kaart op een zwart-witfoto (leest en meetlint).
- **"Wat wilt u doen?"**: drie kaarten met productfoto's op wit (skischoenentas, Fischer RC4 met andere schoenen,
  Hannes Strolz) en een oranje **+**-tegel bij de link.
- **Volgorde op de home** (live staat "Wat wilt u doen?" lager; hier direct na de intro):
  hero → Pijnloos skiën® (intro + definitie) → Wat wilt u doen? → Wat kan een bootfitter voor u betekenen? (klachten met
  hotspots) → Wat is / Wat is niet → FAQ met blog → **Over ons**, **de winkel** (adres + foto's) en **klantreacties**.
  Die laatste drie blokken herhalen alleen zinnen die al op de site staan (Over Ons, footer, Wat klanten zeggen) en
  gebruiken geen extra koppen (h2/h3), zodat de kopstructuur van de home gelijk blijft.
- Het blok **"Het team"** staat uit (`SHOW_TEAM = False` in `generate.py`) tot er goede foto's zijn.

**Paginakop van binnenpagina's** (`page-hero banner`)
- De foto loopt over de volle breedte achter de titel, **zwart-wit via CSS** (`filter: grayscale(1)`), met een donker
  verloop; titel en kruimelpad links onderin, wit.
- Per sectie een vaste foto, zoals op de live site. Bouw ze in WordPress bij voorkeur als **sectie-achtergrond** in
  Elementor (zoals nu live): dan heeft de foto geen alt-tekst, precies als nu.

| Pagina's | Kopfoto (`uploads/winkel/`) |
|---|---|
| Pijn in voeten-subpagina's, Mijn skischoenen aanpassen, Op maat gemaakte skischoenen | `banner-leest.jpg` |
| Wat is bootfitting?, Werkwijze | `banner-oprekpers.jpg` |
| De Skischoen + subpagina's | `banner-skischoenen.jpg` (Fischer RC4 + Hannes Strolz) |
| Ski-Mojo + subpagina's | `banner-ski-mojo.jpg` |
| Rentmaxx Z-value | `banner-rentmaxx.jpg` |
| Alle andere pagina's en alle blogs | `banner-steunzool.jpg` |

  De volledige tabel staat in `BANNERS` / `BANNER_FOR` in `build/generate.py`.

**Overig**
- Tarieven: prijskaarten met het kleine fotootje van de live site naast de vier prijzen die er live een hebben.
- Werkwijze: de flow precies zoals live: het lege schema `wp-content/uploads/2021/09/flow.jpg` (alt "DutchBootFitter
  werkwijze") met elke tekst als HTML op zijn eigen vak (posities in procenten, `render_werkwijze()`). Op mobiel scrolt
  het schema opzij, zodat de tekst leesbaar blijft.
- Over Ons: dezelfde tekst in een logischere volgorde: wie we zijn (foto Bart & Marco-Paul) → In Memoriam → wat de
  titels betekenen → een impressie van de winkel → "Wat wilt u doen?".
- Afsluitende oranje afspraakbalk onderaan elke pagina, met de molenwieken.
- **Mobiel:** alles is getest op 375 px (iPhone): geen horizontaal scrollen, uitklapmenu, knoppen over de volle breedte,
  dienstkaarten swipen, het Werkwijze-schema scrolt opzij.
- Footer zoals live (contact, pijn in voeten, navigatie, keurmerken, Trustindex-beoordeling, social).

## 5. Nieuwe bestanden om te uploaden

Alles wat je moet uploaden, staat in de map **`uploaden/`** in deze zip (28 bestanden). Alle andere afbeeldingen staan al
op bootfitter.nl (zelfde pad), die hoef je niet opnieuw te uploaden.

- **Video hero:** `strolz-aanmeten-breed.mp4` (8,3 MB), `strolz-aanmeten-staand.mp4` (4,0 MB),
  `strolz-aanmeten-breed-poster.jpg`, `strolz-aanmeten-staand-poster.jpg`.
- **Kopfoto's:** `banner-leest.jpg`, `banner-oprekpers.jpg`, `banner-skischoenen.jpg`, `banner-ski-mojo.jpg`,
  `banner-rentmaxx.jpg`, `banner-steunzool.jpg`.
- **Dienstkaarten home:** `dienst-aanpassen-tas.jpg`, `dienst-op-maat-schoenen.jpg`, `dienst-strolz-schoen.webp`.
- **Winkelfoto's** (home, Over Ons, afspraakbalk): `DBF-01.jpg`, `DBF-03.jpg`, `DBF-04.jpg`, `DBF-07.jpg` t/m `DBF-13.jpg`,
  `bart-marco-paul.jpg`, `handwerk-steunzool.jpg`, `handwerk-zw.jpg`, `vloer-praktijk.jpg`.
- **Icoon:** `pijnloosskien.svg` (het skischoentje bij de links onderaan Over Ons).

In de voorbeeldsite staan ze onder `wp-content/uploads/winkel/` (en `wp-content/uploads/pijnloosskien.svg`). Pas na het
uploaden de paden in de CSS aan (zoek op `wp-content/uploads`).

## 6. SEO: wat gelijk blijft en wat bewust anders is

**Gecontroleerd gelijk aan de live site** (`build/verify.py`, `build/check_alts.py`, stand 17-10-2026):
- **Tekst:** alle 71 pagina's woord voor woord gelijk (alleen 3 spaties na een punt op Pijn in voeten, "voet.Oplossing" → "voet. Oplossing").
- **Paginatitels (`<title>`) en meta-beschrijvingen:** gelijk, ook de gekrulde apostrofs.
- **H1:** gelijk op elke pagina. Pagina's zonder H1 op de live site (blogoverzicht, Historie van de skischoen) hebben
  ook hier geen H1; hun titel is een H2 die er hetzelfde uitziet.
- **URL's en interne links:** gelijk (alleen de kapotte links uit `seo/Kapotte-links-bootfitter.pdf` zijn gerepareerd).
- **Alt-teksten:** gelijk aan de live site. Nieuwe, puur decoratieve foto's (kopfoto's, winkelfoto's) hebben een lege
  alt (`alt=""`), zodat Google precies dezelfde alt-teksten ziet als nu.

**Bewust anders** (allemaal klein en zonder SEO-risico). De eerste drie zijn inhoud: die pas je in WordPress aan.
- Ski-Mojo: een knop **"Uitlegvideo van Ski-Mojo"** naar de Instagram-reel
  `https://www.instagram.com/reel/DTcoYxbDGMI/` (opent in een nieuw tabblad), vlak voor "De voordelen van Ski-Mojo:".
- Prijs Strolz volledige maatschoen: **€ 1195** (live staat op Tarieven en in de FAQ nog € 1180).
- Links-pagina: de Elementor-opvultekst "Lorem ipsum" is weggelaten. Graag ook live verwijderen.
- Home: het ANWB-vignetblok staat live op alle apparaten verborgen; hier is het weggelaten.
- Meta-beschrijving van *Ski-Mojo afspraak* (live staat daar per ongeluk de tekst van de Links-pagina) en *Pijnlijke hiel*
  (live leeg) zijn in de voorbeeldsite ingevuld. Dit is optioneel: pas het alleen in Yoast aan als DutchBootFitter dat wil.
- De Bookly-laadplaatjes ("Laden...") zie je hier niet; Bookly zet ze zelf weer neer.

## 7. Checklist vóór livegang

- [ ] Proefboeking op alle 4 Bookly-pagina's werkt (bevestigingsmail komt aan).
- [ ] Geen URL of slug gewijzigd; geen nieuwe redirects nodig.
- [ ] Yoast: titels en meta-beschrijvingen onveranderd (steekproef met "Bron bekijken" of een SEO-crawler).
- [ ] Elke pagina heeft nog dezelfde H1 (of geen, waar dat nu ook zo is).
- [ ] Alt-teksten in de mediabibliotheek niet aangepast.
- [ ] `robots.txt`, sitemap (Yoast) en Google Search Console onveranderd; na livegang de sitemap opnieuw indienen.
- [ ] Mobiel getest (iPhone en Android): menu, video, kaarten, kopfoto's.
- [ ] Snelheid (PageSpeed Insights): video's met `preload="metadata"`, afbeeldingen `loading="lazy"` behalve de kopfoto.
- [ ] Podonet-vergoedingswidget (Tarieven), Google Maps, YouTube en Trustindex laden nog.

## 8. De voorbeeldsite opnieuw bouwen

```sh
pip install markdown beautifulsoup4
python3 build/generate.py     # bouwt site/ opnieuw uit copy/
python3 build/verify.py       # tekst woord voor woord → verification.json
python3 build/check_alts.py   # alt-teksten tegen de live site → alt-check.json (haalt de live pagina's één keer op)
```

Waar je dingen aanpast in `build/generate.py`:

| Wat | Waar |
|---|---|
| Kopfoto per pagina | `BANNERS`, `BANNER_FOR` |
| Foto's in de dienstkaarten | `SERVICE_PHOTOS`, `PRODUCT_PHOTOS` |
| Fotootjes bij de prijzen | `PRICE_PHOTOS` |
| Team-blok aan/uit | `SHOW_TEAM` |
| Extra links (Ski-Mojo Instagram) | `EXTRA_LINKS` |
| Gerepareerde links | `LINK_FIXES`, `LINK_REMOVE` |
| Goedgekeurde nieuwe tekst | `APPROVED_COPY` (alleen tekst die hierin staat, mag nieuw zijn; `verify.py` controleert dat) |

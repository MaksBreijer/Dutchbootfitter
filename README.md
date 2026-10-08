# bootfitter-site

De nieuwe statische website voor bootfitter.nl (DutchBootFitter).

- `site/` — de kant-en-klare site (71 pagina's, `style.css`, `app.js`). Open `site/index.html` in een browser; er is geen buildstap nodig om hem te bekijken.
- `copy/` — de letterlijke tekst van elke pagina van bootfitter.nl (Markdown), de bron waaruit de site gegenereerd wordt. Teksten blijven woord voor woord gelijk aan de huidige site.
- `build/` — de generator en de controle.
- `seo/` — SEO-documenten.

## Ontwerp (v2)

Het ontwerp combineert drie referenties, met behoud van alle tekst, SEO-titels/-beschrijvingen en afbeeldingen:

- **Fischer Sports** — paginabrede bergfoto in de hero, zwevende afgeronde navigatiebalk, grote smalle hoofdletterkoppen.
- **Canary Care** — warme, rustige vlakken, ronde pill-knoppen, fotokaarten met de tekst op de foto.
- **Solstice Design** — redactionele serif-cursief als accent, veel witruimte, kleine genummerde sectielabels.

Het oranje is exact het oranje uit het logo; hoogtelijnen blijven het enige ornament.

- **Lettertype:** Open Sans, net als op de huidige bootfitter.nl (via de breedte-as ook in smalle koppen).
- **Foto's van de winkel:** de interieurfoto's (DBF-01…13), de etalage en de werkplaats komen uit de mediabibliotheek van bootfitter.nl en staan in `site/wp-content/uploads/winkel/`. Ze staan op de home, in de kop van elke pagina, bij de afsluitende afspraak-oproep en als galerij op Over Ons.
- **Links:** de fixes uit `seo/Kapotte-links-bootfitter.pdf` zijn doorgevoerd in `LINK_FIXES` / `LINK_REMOVE` in `build/generate.py` (alleen linkadressen, de tekst blijft gelijk).

## Ontwerp (v4) — alles onder de header

De header (topbalk, menubalk, de video-hero op de home en de paginakop op binnenpagina's) blijft exact zoals hij is. Daaronder:

- **Home 01, intro:** kop links, tekst rechts (Solstice), daaronder een brede foto van de wachtruimte met de definitie erop.
- **Home 02, klachten:** gecentreerde intro (Canary), genummerde klachten met dunne lijnen, de schoen met hotspots op een warme cirkel.
- **Winkelfoto's:** een rij hoge afgeronde kaarten die je kunt scrollen, met pijlknoppen (Canary).
- **Home 03, keuzes:** fototegels waarbij de foto de hele kaart vult en de tekst op de foto staat (Fischer).
- **Home 04, wel/niet:** een donker contrastvlak met twee redactionele kolommen.
- **Home 05, FAQ:** kop links, zachte uitklapkaarten rechts.
- **Afspraak-oproep:** een grote afgeronde fototegel van de etalage, met de keuken als zwevende kaart (Fischer).
- **Binnenpagina's:** een grotere openingsalinea, oranje streepje boven tussenkoppen, kaartrasters als projectraster (Solstice), een getinte zijbalk, afgeronde prijs- en reactiekaarten.

Geen tekst, titel, meta-beschrijving, URL, afbeelding of link is veranderd; `build/verify.py` meldt 0 verschillen op alle 71 pagina's.

## Opnieuw bouwen

```sh
pip install markdown beautifulsoup4
python3 build/generate.py   # bouwt site/ opnieuw uit copy/
python3 build/verify.py     # controleert elke pagina woord voor woord tegen copy/, schrijft verification.json
```

Afbeeldingen, de afspraakwidget, Google Maps, de YouTube-video en de Podonet-widget laden nog van hun oorspronkelijke bronnen.

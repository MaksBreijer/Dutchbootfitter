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

## Opnieuw bouwen

```sh
pip install markdown beautifulsoup4
python3 build/generate.py   # bouwt site/ opnieuw uit copy/
python3 build/verify.py     # controleert elke pagina woord voor woord tegen copy/, schrijft verification.json
```

Afbeeldingen, de afspraakwidget, Google Maps, de YouTube-video en de Podonet-widget laden nog van hun oorspronkelijke bronnen.

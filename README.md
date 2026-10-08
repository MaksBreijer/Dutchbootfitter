# bootfitter-site

De nieuwe statische website voor bootfitter.nl (DutchBootFitter).

- `site/` — de kant-en-klare site (71 pagina's, `style.css`, `app.js`). Open `site/index.html` in een browser; er is geen buildstap nodig om hem te bekijken.
- `copy/` — de letterlijke tekst van elke pagina van bootfitter.nl (Markdown), de bron waaruit de site gegenereerd wordt. Teksten blijven woord voor woord gelijk aan de huidige site.
- `build/` — de generator en de controle.
- `seo/` — SEO-documenten.

## Opnieuw bouwen

```sh
pip install markdown beautifulsoup4
python3 build/generate.py   # bouwt site/ opnieuw uit copy/
python3 build/verify.py     # controleert elke pagina woord voor woord tegen copy/, schrijft verification.json
```

Afbeeldingen, de afspraakwidget, Google Maps, de YouTube-video en de Podonet-widget laden nog van hun oorspronkelijke bronnen.

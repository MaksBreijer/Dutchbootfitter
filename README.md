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

## Ontwerp (v5)

- **Header:** de balk zoals hij was, met het menu rechts uitgelijnd; de Afspraak-knop is een recht oranje vlak en de menuknop is ook recht (geen schuine vorm meer).
- **Geen textuur:** de hoogtelijnen achter de paginakoppen en op de definitiekaart zijn weg; een foto die niet laadt laat een effen vlak achter.
- **Foto's:** de winkelfoto's (DBF-…) zijn opnieuw geëxporteerd uit de originelen van 5184 px (nu 2400 px breed). Nieuw uit de mediabibliotheek: `slijpmachine.jpg`, `handwerk-zw.jpg`, `pers-zw.jpg`. De etalagefoto bestaat alleen op 562 px en wordt daarom alleen nog klein gebruikt. Waar de pagina's een WordPress-miniatuur (`-300x200` enz.) tonen, gebruikt `localize()` het originele bestand als dat lokaal staat (maximaal 1600 px).
- **Over Ons:** dezelfde tekst in een logische volgorde: wie we zijn (met de foto van Bart en Marco-Paul), In Memoriam en de voortzetting, wat de titels betekenen, een impressie van de winkel (fotoraster en Street View), en tot slot "Wat wilt u doen?". `verify.py` vergelijkt deze pagina woord voor woord met dezelfde volgorde (`over_ons_md()` in `generate.py`).

## Ontwerp (v6)

Referentie: Oregon Outdoor Alliance. De start van de site (topbalk, menu, video-hero, kop en knoppen) en de volgorde van alle bestaande secties blijven gelijk.

- **Strakker:** kleine afrondingen (6 px) in plaats van pillen en cirkels; sectienummers (01, 02 …) in Open Sans met een oranje streep eronder.
- **Hero:** één regel boven de kop, `DE EERSTE CERTIFIED MASTER BOOTFITTERS · SINDS 2008 BRACHTEN ZIJ HET BOOTFITTEN NAAR NEDERLAND`. Dit is de enige nieuwe tekst op de site, goedgekeurd door DutchBootFitter en gebaseerd op Over Ons ("Zij brachten het 'bootfitten' naar Nederland"). Hij staat in `HERO_EYEBROW` / `APPROVED_COPY` in `generate.py`; `verify.py` accepteert alleen nieuwe tekst die daar staat.
- **Home 06–08, na de FAQ:** de bootfitters (Over Ons), de winkel met adres en foto's, en drie klantreacties met de beoordeling. Deze blokken herhalen alleen zinnen die al op de site staan; ze gebruiken geen h2/h3, zodat de kopstructuur van de home gelijk blijft.
- **Footer:** de wiekjes van de molen staan nu subtiel rechtsonder in de footer (niet meer in de afspraak-oproep); de social-knoppen zijn vierkant in plaats van rond.
- **Controle:** blokken met `data-reuse` worden in `verify.py` apart gecontroleerd: elk stukje tekst (`data-src`) moet woord voor woord op de genoemde pagina staan (`chrome` = header/footer). Nieuwe tekst daarbuiten geeft een fout.

## Ontwerp (v7) — header: bootfitter.nl × Snuuzu

- **Van Snuuzu:** een dunne donkere aankondigingsregel ("Pijn in voeten of scheenbenen? Maak een afspraak om pijnloos® te skiën!", linkt naar Afspraak) die wegklapt bij scrollen; een rustige, doorzichtige balk op de video; kop linksonder met een witte knop en daaronder de sterren met "Beoordeling 4.5/5 gebaseerd op 484 reviews" (bestaande tekst, gecontroleerd als `data-reuse`).
- **Van de huidige site:** logo links, menu rechts (met HOME), de oranje Afspraak-knop en "pijnloos skiën®" vet in oranje.
- **Rustig gehouden:** geen telefoonicoon, geen streep onder het label, de tweede hero-knop is een onderstreepte link. Onder 1100 px: logo links, Afspraak en menuknop rechts.

## Ontwerp (v8) — rustiger header

- **Hero:** de H1, de tagline, twee knoppen (oranje hoofdknop, omlijnde tweede knop van gelijke grootte) en daaronder klein de sterren met de beoordeling. De regel boven de kop en het scroll-streepje zijn weg; zachtere overlay en meer witruimte.
- **Aankondigingsregel** boven de balk is weg (hij herhaalde de Afspraak-knop).
- **Mobiel (iPhone):** kop laag in beeld, knoppen onder elkaar over de volle breedte (52 px hoog, op één regel tot 375 px), ruimte voor de home-indicator via `safe-area-inset-bottom`.

## Ontwerp (v9) — diensten eerder, premium

- **Eerst waar we voor staan, dan de diensten:** na de hero komt "Pijnloos skiën®" (01) en direct daarna "Wat wilt u doen?" (02); de rest volgt in de volgorde van bootfitter.nl. `verify.py` vergelijkt de home met die volgorde (`home_md()` in `generate.py`).
- **Intro (waar we voor staan):** de alinea met harde regeleinden is opgesplitst op die regeleinden: links de kop met de eerste zin als grotere lead, rechts de uitleg en de uitnodiging om een afspraak te maken. Zelfde woorden, zelfde volgorde.
- **Premium dienstkaarten:** foto boven, tekst eronder op een rustig vlak, klein nummer (01–03) en één rustige link met pijl. De kleine productfoto's van de live site (één was maar 292 px) zijn vervangen door vierkante uitsneden van eigen foto's: `dienst-aanpassen.jpg` (oprekken), `dienst-op-maat.jpg` (DBF-13) en `dienst-strolz.jpg` (uit de Strolz-video); de alt-teksten zijn die van de live site (`SERVICE_PHOTOS`).
- **Mobiel:** de drie kaarten staan in een rij die je kunt swipen (de volgende kaart piept in beeld), in plaats van onder elkaar.
- **Compacter:** minder ruimte tussen secties en lagere kaarten en foto's, zodat er minder gescrold hoeft te worden.

## Ontwerp (v10) — oranje als signaal

- **Eén oranje sleutelwoord per kop** op de home ("**Pijnloos** skiën®", "Wat wilt u **doen?**", "… **betekenen?**", "… **FAQ**"), via `HEADING_ACCENTS` in `generate.py`: alleen opmaak (`<span class="accent">`), de woorden en de koppenstructuur blijven gelijk.
- **Oranje merkmoment:** de afspraak-oproep onderaan elke pagina is een vlak in het logo-oranje (`--brand: #e8561a`) met witte tekst, "pijnloos®" donker en een donkere knop; de foto erachter is weg.
- **Details:** geselecteerde tekst en links met een oranje onderstreping.
- **Molen:** de wieken draaien nu om de as (de draaipunt lag eerder in een hoek van de tekening, waardoor ze uit beeld zwaaiden), tegen de klok in zoals een Hollandse molen, en zichtbaar (14–18 s per rondje). De as staat net buiten de rechterrand van de footer en van het oranje afspraakvlak (witte molen), zodat de wieken af en toe het vlak in zwaaien en door de rand worden afgesneden. Bij "verminder beweging" staan ze stil.

## Opnieuw bouwen

```sh
pip install markdown beautifulsoup4
python3 build/generate.py   # bouwt site/ opnieuw uit copy/
python3 build/verify.py     # controleert elke pagina woord voor woord tegen copy/, schrijft verification.json
```

Afbeeldingen, de afspraakwidget, Google Maps, de YouTube-video en de Podonet-widget laden nog van hun oorspronkelijke bronnen.

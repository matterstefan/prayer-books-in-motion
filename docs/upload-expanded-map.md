# Erweiterte Karte auf GitHub hochladen

Dieses Paket aktualisiert die Karte auf den erweiterten Bestand und übernimmt
Stefan Matters Ortsprüfung vom 1. Oktober 2026.

## Upload

ZIP entpacken. Der Inhalt entspricht der Ordnerstruktur des GitHub-Projekts.
Den übergeordneten entpackten Ordner nicht als neuen Projektordner hochladen.
In GitHub jeweils den genannten Zielordner öffnen und über **Add file → Upload
files** die zugehörigen Dateien hineinziehen. Existierende Dateien werden unter
demselben Namen ersetzt. Neue Ordner lassen sich durch das Hochladen der
entsprechenden Unterordner aus dem Paket erzeugen.

| Ziel in GitHub | Inhalt aus dem Paket |
|---|---|
| Projekt-Hauptverzeichnis | `index.html` |
| `assets` | `app.js`, `styles.css` |
| `data/authority` | vier CSV-/JSON-Dateien |
| `data/derived` | `prayer-book-corpus.csv` |
| `data/expanded` | `mei-corpus.json`, `harvest-status.json`, `location-status.json` |
| `data/expanded/tables` | acht CSV-Dateien |
| `scripts` | vier Python-Skripte |
| `docs` | zwei Markdown-Dateien |
| `tests` | `map-data.cjs` |

Beim Upload in `data/expanded` können die drei Dateien und der enthaltene Ordner
`tables` gemeinsam ausgewählt werden. Falls die ursprünglichen fünf MEI-Dateien
bereits vorhanden sind, sind die identischen Kopien im Paket nur zur
Vollständigkeit dabei. Cache-Dateien müssen nicht hochgeladen werden.

Die Abrufskripte und der GitHub-Workflow sind nicht Teil dieses Updates. Für die
Kartenanzeige wird kein weiterer MEI-Abruf benötigt.

Mögliche Commit-Nachricht:

`Integrate full MEI corpus and reviewed place assignments into map`

## Nach dem Upload

Den Abschluss der GitHub-Pages-Aktualisierung abwarten und dann öffnen:

https://matterstefan.github.io/prayer-books-in-motion/

Wenn noch die alte Fassung erscheint, die Seite mit Cmd–Shift–R neu laden.
Erwartet werden initial 484 ausgewählte Drucke und das Jahr 2026.

Kurze Sichtprüfung:

1. Nach `Bologna` suchen: Druckort und Bibliotheken liegen am Stadtpunkt.
2. Nach MEI `02010269` suchen: Montserrat ist verortet, die alternative
   Katalogzuweisung wird in den Details erläutert.
3. Nach `00201166` suchen: Wien 1905 ist der letzte Nachweis, der heutige
   Aufenthaltsort bleibt unbekannt.
4. Karte verschieben, Details öffnen und wieder schliessen: Der Ausschnitt bleibt.
5. Zeitregler zurückziehen: Wege erscheinen erst ab dem Druckdatum; offene
   Punkte zeigen Annäherungen oder letzte Nachweise.

Die vollständigen Methoden und Testgrenzen stehen in
`docs/corpus-place-resolution.md`.

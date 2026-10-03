# Portfolio fotografico

Sito statico generato da cartelle. Nessuna dipendenza oltre a Python 3.

## Aggiungere un progetto
1. Crea `content/projects/NN-nome-progetto/` (il prefisso `NN-` decide l'ordine nel menu).
2. Metti dentro le immagini (l'ordine è alfabetico, quindi `01.jpg`, `02.jpg`, ...).
3. Facoltativo: `project.json` con `{"title": "Titolo diverso", "hidden": false}`.
4. Esegui `python3 build.py`: il sito aggiornato è in `docs/`.

## Altre pagine
- `content/home/`: immagini della home (se vuota usa la prima del primo progetto).
- `content/books/NN-nome/`: `cover.jpg` + `book.json`.
- `content/info.md`: testo della pagina Info.
- `content/site.json`: nome del sito e descrizione.

## Pubblicazione
GitHub Pages: Settings → Pages → Branch `main`, cartella `/docs`.

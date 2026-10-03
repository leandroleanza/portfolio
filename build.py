#!/usr/bin/env python3
"""Genera il sito statico a partire dalle cartelle in content/.

Struttura attesa:
  content/site.json                 -> nome, email, nav extra
  content/home/                     -> immagini della home (opzionale)
  content/projects/<NN-slug>/       -> una cartella per progetto
      project.json (opzionale)      -> {"title": "Titolo", "hidden": false}
      *.jpg|png|webp|svg            -> immagini in ordine alfabetico
  content/books/<NN-slug>/          -> un libro per cartella
      cover.(jpg|png|svg)           -> copertina
      book.json                     -> {"title","text","link","link_label"}
  content/info.md                   -> testo della pagina Info (paragrafi, **grassetto**)

Uso: python3 build.py   (scrive l'output in ./docs, pronto per GitHub Pages)
"""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


def load_json(path, default=None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default if default is not None else {}


def slugify(name):
    name = re.sub(r"^\d+[-_ ]*", "", name)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return s or "progetto"


def pretty(name):
    name = re.sub(r"^\d+[-_ ]*", "", name)
    return re.sub(r"[-_]+", " ", name).strip().title()


def images_in(folder):
    return sorted(
        [p for p in folder.iterdir() if p.suffix.lower() in IMG_EXT],
        key=lambda p: p.name.lower(),
    ) if folder.exists() else []


def esc(s):
    return html.escape(s, quote=True)


def md_inline(text):
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[(.+?)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    text = re.sub(r"&lt;([^&]+@[^&]+)&gt;", r'<a href="mailto:\1">\1</a>', text)
    return text


def copy_images(files, dest):
    dest.mkdir(parents=True, exist_ok=True)
    names = []
    for f in files:
        shutil.copy2(f, dest / f.name)
        names.append(f.name)
    return names


def layout(site, title, body, depth, current, projects, has_books, has_info, body_class=""):
    base = "../" * depth
    def link(t, href, slug):
        cls = ' class="active"' if slug == current else ""
        return f'<li><a href="{href}"{cls}>{esc(t)}</a></li>'

    nav_parts = []
    if projects:
        is_open = any(p["slug"] == current for p in projects)
        subs = "\n".join(link(p["title"], f"{base}{p['slug']}/", p["slug"]) for p in projects)
        nav_parts.append(
            f'<li class="has-sub{" open" if is_open else ""}">'
            f'<button class="sub-toggle" aria-expanded="{"true" if is_open else "false"}">Projects</button>'
            f'<div class="submenu"><ul>\n{subs}\n</ul></div></li>'
        )
    if has_books:
        nav_parts.append(link("Books", f"{base}books/", "books"))
    if has_info:
        nav_parts.append(link("Info", f"{base}info/", "info"))
    nav = "\n".join(nav_parts)
    page_title = site["title"] if not title else f"{title} — {site['title']}"
    return f"""<!doctype html>
<html lang="{esc(site.get('lang', 'it'))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page_title)}</title>
<meta name="description" content="{esc(site.get('description', ''))}">
<link rel="stylesheet" href="{base}assets/style.css">
</head>
<body class="{body_class}">
<header class="site-header">
  <h1 class="site-title"><a href="{base}">{esc(site['title'])}</a></h1>
  <button class="menu-toggle" aria-expanded="false" aria-controls="main-nav">Menu</button>
  <nav id="main-nav" class="main-nav"><ul>
{nav}
  </ul></nav>
</header>
{body}
<script src="{base}assets/site.js"></script>
</body>
</html>
"""


def slideshow(slug, names, depth, controls=True):
    base = "../" * depth
    n = len(names)
    slides = "\n".join(
        f'<figure class="slide{" is-active" if i == 0 else ""}" data-index="{i}">'
        f'<img src="{base}img/{slug}/{esc(name)}" alt="" {"loading=\"eager\"" if i < 2 else "loading=\"lazy\""}></figure>'
        for i, name in enumerate(names)
    )
    thumbs = "\n".join(
        f'<button class="thumb" data-index="{i}"><img src="{base}img/{slug}/{esc(name)}" alt="" loading="lazy"></button>'
        for i, name in enumerate(names)
    )
    numbers = " ".join(f'<button class="num" data-index="{i}">{i + 1}</button>' for i in range(n))
    if not controls:
        # Home: solo la foto, nessun controllo e nessuna interazione al passaggio del mouse
        return f"""<main class="gallery gallery-static" data-count="{n}">
  <div class="slideshow">
{slides}
  </div>
</main>"""
    return f"""<main class="gallery" data-count="{n}">
  <div class="slideshow">
{slides}
    <button class="hit prev-slide" aria-label="Precedente"></button>
    <button class="hit next-slide" aria-label="Successiva"></button>
  </div>
  <div class="thumbnails" hidden>
{thumbs}
  </div>
  <footer class="gallery-controls">
    <div class="pager"><button class="prev-slide">prev</button> / <button class="next-slide">next</button></div>
    <button class="thumbnail-toggle">show thumbnails</button>
  </footer>
</main>"""


def main():
    site = load_json(CONTENT / "site.json", {"title": "NOME COGNOME"})
    site.setdefault("title", "NOME COGNOME")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("")

    # progetti
    projects = []
    pdir = CONTENT / "projects"
    for d in sorted([p for p in pdir.iterdir() if p.is_dir()], key=lambda p: p.name.lower()) if pdir.exists() else []:
        meta = load_json(d / "project.json")
        if meta.get("hidden"):
            continue
        files = images_in(d)
        if not files:
            continue
        slug = slugify(d.name)
        projects.append({
            "slug": slug,
            "title": meta.get("title") or pretty(d.name),
            "names": copy_images(files, OUT / "img" / slug),
        })

    # libri
    books = []
    bdir = CONTENT / "books"
    for d in sorted([p for p in bdir.iterdir() if p.is_dir()], key=lambda p: p.name.lower()) if bdir.exists() else []:
        meta = load_json(d / "book.json")
        cover = next(iter(images_in(d)), None)
        slug = "book-" + slugify(d.name)
        cover_name = copy_images([cover], OUT / "img" / slug)[0] if cover else None
        books.append({"slug": slug, "cover": cover_name, "meta": {"title": meta.get("title") or pretty(d.name), **meta}})

    info_path = CONTENT / "info.md"
    has_info = info_path.exists()
    has_books = bool(books)

    def page(rel, html_text):
        target = OUT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html_text, encoding="utf-8")

    # home
    home_files = images_in(CONTENT / "home")
    if home_files:
        home_names = copy_images(home_files, OUT / "img" / "home")
        home_slug = "home"
    elif projects:
        home_names, home_slug = projects[0]["names"][:1], projects[0]["slug"]
    else:
        home_names, home_slug = [], "home"
    body = slideshow(home_slug, home_names, 0, controls=False) if home_names else '<main class="gallery"></main>'
    page("index.html", layout(site, "", body, 0, "", projects, has_books, has_info, "home"))

    # progetti
    for p in projects:
        page(f"{p['slug']}/index.html",
             layout(site, p["title"], slideshow(p["slug"], p["names"], 1), 1, p["slug"], projects, has_books, has_info))

    # books
    if has_books:
        items = []
        for b in books:
            m = b["meta"]
            cover = f'<img src="../img/{b["slug"]}/{esc(b["cover"])}" alt="{esc(m["title"])}">' if b["cover"] else ""
            link = ""
            if m.get("link"):
                link = f'<p class="book-link"><a href="{esc(m["link"])}" target="_blank" rel="noopener">{esc(m.get("link_label", "Link"))}</a></p>'
            paras = "".join(f"<p>{md_inline(t)}</p>" for t in m.get("text", "").split("\n\n") if t.strip())
            items.append(f'<article class="book">{cover}<h3>{esc(m["title"])}</h3>{paras}{link}</article>')
        page("books/index.html",
             layout(site, "Books", '<main class="books">' + "\n".join(items) + "</main>", 1, "books", projects, has_books, has_info))

    # info
    if has_info:
        raw = info_path.read_text(encoding="utf-8")
        blocks = [b for b in re.split(r"\n\s*\n", raw.strip()) if b.strip()]
        out = []
        for b in blocks:
            lines = [md_inline(l) for l in b.strip().splitlines()]
            out.append("<p>" + "<br>".join(lines) + "</p>")
        portrait = ""
        pf = images_in(CONTENT / "info")
        if pf:
            n = copy_images(pf[:1], OUT / "img" / "info")[0]
            portrait = f'<img class="info-portrait" src="../img/info/{esc(n)}" alt="">'
        page("info/index.html",
             layout(site, "Info", f'<main class="info">{portrait}{"".join(out)}</main>', 1, "info", projects, has_books, has_info))

    print(f"OK: {len(projects)} progetti, {len(books)} libri, info={'sì' if has_info else 'no'} -> {OUT}")


if __name__ == "__main__":
    main()

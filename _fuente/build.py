import json, re, sys, unicodedata, html, shutil, os
from bs4 import BeautifulSoup, NavigableString
sys.path.insert(0, os.path.dirname(__file__))
from meta import META

SRC, OUT = sys.argv[1], sys.argv[2]
BASE = "https://problemas-interesantes.github.io/"
import datetime
FECHA = datetime.date.today().isoformat()
SITE = "Problemas Interesantes"

raw = open(SRC, encoding="utf-8").read()
soup = BeautifulSoup(raw, "html.parser")

# ---------- CSS: el original + agregados ----------
css = soup.find("style").string
css = css.replace("  .problem h3 { margin: 0; font-size: 23px; font-weight: 600; }",
                  "  .problem h3, .problem h1.ptitle { margin: 0; font-size: 23px; font-weight: 600; line-height: 1.3; }")
css += """
  /* Agregados para el sitio multipágina */
  .topbar { border-bottom: 1px solid var(--line); }
  .topbar .wrap { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; padding-top: 14px; padding-bottom: 14px;
    font-family: Inter, system-ui, sans-serif; font-size: 15px; }
  .topbar .marca { font-weight: 600; letter-spacing: .08em; text-transform: uppercase; font-size: 13px; color: var(--accent); text-decoration: none; }
  .topbar nav { border: 0; padding: 0; gap: 18px; }
  .migas { font-family: Inter, system-ui, sans-serif; font-size: 14px; color: var(--muted); margin: 28px 0 14px; }
  .migas a { color: var(--muted); }
  .migas a:hover { color: var(--accent); }
  a.tag { text-decoration: none; }
  a.tag:hover { color: var(--accent); }
  .problem h1.ptitle { font-size: 30px; }
  .pasos { display: flex; justify-content: space-between; gap: 14px; margin: 8px 0 8px;
    font-family: Inter, system-ui, sans-serif; font-size: 15px; }
  .pasos a { color: var(--accent); text-decoration: none; max-width: 48%; }
  .pasos a:hover { text-decoration: underline; }
  .pasos .sig { margin-left: auto; text-align: right; }
  .relacionados { padding-top: 28px; }
  .relacionados ul, .lista-tema { list-style: none; padding: 0; margin: 0; }
  .relacionados li { padding: 4px 0; font-family: Inter, system-ui, sans-serif; font-size: 15px; }
  .relacionados a, .lista-tema h2 a { color: var(--ink); text-decoration: none; }
  .relacionados a:hover, .lista-tema h2 a:hover { color: var(--accent); }
  .lista-tema li { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 18px 22px; margin-bottom: 16px; overflow-x: auto; }
  .lista-tema h2 { font-family: "Source Serif 4", Georgia, serif; text-transform: none; letter-spacing: 0; font-size: 21px; color: var(--ink); margin: 0 0 6px; }
  .lista-tema p { margin: 0 0 8px; }
  .lista-tema .mas-link { font-family: Inter, system-ui, sans-serif; font-size: 14px; color: var(--accent); }
  .temas-todos { display: flex; gap: 8px; flex-wrap: wrap; }
  .temas-todos a { font-size: 14px; }
  .pagina-tema h1 { font-size: 38px; margin: 0 0 10px; }
  @media (max-width: 560px) {
    .problem h1.ptitle { font-size: 24px; }
    .pagina-tema h1 { font-size: 30px; }
    .pasos { flex-direction: column; }
    .pasos a { max-width: 100%; }
    .pasos .sig { margin-left: 0; text-align: left; }
  }
"""
os.makedirs(os.path.join(OUT, "problemas"), exist_ok=True)
os.makedirs(os.path.join(OUT, "temas"), exist_ok=True)
open(os.path.join(OUT, "estilo.css"), "w", encoding="utf-8").write(css.strip() + "\n")

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def esc(s): return html.escape(s, quote=True)

MATHJAX = """<script>
  window.MathJax = {
    tex: { inlineMath: [['\\\\(', '\\\\)']], displayMath: [['\\\\[', '\\\\]']] },
    options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea'] }
  };
</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script>"""

def head(title, desc, path, pre, extra_ld=None, og_type="article", math=True):
    url = BASE + path
    ld = "".join(f'\n<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (extra_ld or []))
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}estilo.css">
{MATHJAX if math else ''}{ld}
</head>
<body>
"""

def topbar(pre):
    return f"""<div class="topbar"><div class="wrap">
  <a class="marca" href="{pre}">{SITE}</a>
  <nav>
    <a href="{pre}#indice">Índice</a>
    <a href="{pre}temas/">Temas</a>
    <a href="{pre}#acerca">Acerca</a>
    <a href="{pre}#contacto">Contacto</a>
  </nav>
</div></div>
"""

def footer(pre):
    return f"""  <footer>
    {SITE} · Problemas de matemática con pista y solución ·
    <a href="mailto:problemasinteresantes@gmail.com" style="color:inherit">problemasinteresantes@gmail.com</a>
  </footer>
</div>
</body>
</html>
"""

# ---------- Extraer problemas ----------
probs = []
for art in soup.select("article.problem"):
    pid = art["id"]
    slug, seo_title, desc = META[pid]
    num = art.select_one(".num").get_text(strip=True).replace("N.º", "").strip()
    h3 = art.select_one("h3")
    title_html = h3.decode_contents()
    title_txt = h3.get_text()
    dif = art.select_one(".problem-head .dif").get_text(strip=True)
    tags = [t.get_text(strip=True) for t in art.select(".tags .tag")]
    # enunciado: hijos antes del primer <details>, sin cabecera ni etiquetas
    stmt = []
    for c in art.children:
        if getattr(c, "name", None) == "details":
            break
        if getattr(c, "name", None) and not set(c.get("class") or []) & {"problem-head", "tags"}:
            stmt.append(str(c))
    probs.append(dict(id=pid, slug=slug, seo=seo_title, desc=desc, num=num, title_html=title_html,
                      title_txt=title_txt, dif=dif, tags=tags, art=art, stmt="\n".join(stmt)))

DIFS = {"★": "accesible", "★★": "pide una idea", "★★★": "difícil"}
tema_count = {}
for p in probs:
    for t in p["tags"]:
        tema_count[t] = tema_count.get(t, 0) + 1
TEMAS_PAG = {t for t, n in tema_count.items() if n >= 2}   # páginas de tema solo con 2+ problemas

def tag_html(t, pre):
    if t in TEMAS_PAG:
        return f'<a class="tag" href="{pre}temas/{slugify(t)}.html">{esc(t)}</a>'
    return f'<span class="tag">{esc(t)}</span>'

# ---------- Páginas de problemas ----------
for i, p in enumerate(probs):
    pre = "../"
    art = BeautifulSoup(str(p["art"]), "html.parser").select_one("article")
    art["id"] = "problema"
    h = art.select_one("h3"); h.name = "h1"; h["class"] = "ptitle"
    tg = art.select_one(".tags")
    tg.clear()
    tg.append(BeautifulSoup("".join(tag_html(t, pre) for t in p["tags"]), "html.parser"))
    principal = next((t for t in p["tags"] if t in TEMAS_PAG), None)
    path = f"problemas/{p['slug']}.html"
    crumbs = [{"@type": "ListItem", "position": 1, "name": SITE, "item": BASE}]
    migas = f'<a href="{pre}">Inicio</a>'
    if principal:
        crumbs.append({"@type": "ListItem", "position": 2, "name": principal, "item": f"{BASE}temas/{slugify(principal)}.html"})
        migas += f' › <a href="{pre}temas/{slugify(principal)}.html">{esc(principal)}</a>'
    crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": p["seo"]})
    migas += f' › Problema N.º {p["num"]}'
    ld = [
        {"@context": "https://schema.org", "@type": "LearningResource",
         "name": p["seo"], "headline": p["seo"], "description": p["desc"], "url": BASE + path,
         "inLanguage": "es", "isAccessibleForFree": True, "learningResourceType": "Problema resuelto",
         "educationalLevel": DIFS.get(p["dif"], ""), "about": [{"@type": "Thing", "name": t} for t in p["tags"]],
         "keywords": ", ".join(p["tags"] + ["problema de matemática", "problema resuelto"]),
         "dateModified": FECHA,
         "isPartOf": {"@type": "WebSite", "name": SITE, "url": BASE}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs},
    ]
    prev = probs[i - 1] if i > 0 else None
    nxt = probs[i + 1] if i + 1 < len(probs) else None
    pasos = '<nav class="pasos" aria-label="Otros problemas">'
    if prev: pasos += f'<a href="{prev["slug"]}.html">← N.º {prev["num"]}: {prev["title_html"]}</a>'
    if nxt: pasos += f'<a class="sig" href="{nxt["slug"]}.html">N.º {nxt["num"]}: {nxt["title_html"]} →</a>'
    pasos += "</nav>"
    # relacionados: comparten algún tema
    rel = [q for q in probs if q is not p and set(q["tags"]) & set(p["tags"])]
    rel.sort(key=lambda q: (-len(set(q["tags"]) & set(p["tags"])), abs(int(q["num"]) - int(p["num"]))))
    rel = rel[:5]
    rel_html = ""
    if rel:
        rel_html = '<section class="relacionados"><h2>Problemas relacionados</h2><ul>' + "".join(
            f'<li><a href="{q["slug"]}.html">N.º {q["num"]} · {q["title_html"]}</a> <span class="dif">{q["dif"]}</span></li>' for q in rel
        ) + "</ul></section>"
    page = head(f"{p['seo']} | {SITE}", p["desc"], path, pre, ld)
    page += topbar(pre)
    page += f'<div class="wrap">\n  <p class="migas">{migas}</p>\n  {art}\n  {pasos}\n  {rel_html}\n'
    page += footer(pre)
    open(os.path.join(OUT, path), "w", encoding="utf-8").write(page)

# ---------- Páginas de temas ----------
temas_orden = sorted(TEMAS_PAG, key=lambda t: t.lower().replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u"))
for t in temas_orden:
    pre = "../"
    lista = [p for p in probs if t in p["tags"]]
    path = f"temas/{slugify(t)}.html"
    titulos = "; ".join(p["seo"] for p in lista[:3])
    desc = f"{len(lista)} problemas de {t.lower() if t[0] in 'ÁÉÍÓÚABCDEFGHIJKLMNOPQRSTUVWXYZ' and not any(c.isupper() for c in t[1:]) else t} con pista y solución: {titulos}…"
    desc = desc[:200].rsplit(" ", 1)[0] + "…" if len(desc) > 200 else desc
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{t}: problemas resueltos",
           "url": BASE + path, "inLanguage": "es",
           "mainEntity": {"@type": "ItemList", "itemListElement": [
               {"@type": "ListItem", "position": k + 1, "url": f"{BASE}problemas/{p['slug']}.html", "name": p["seo"]}
               for k, p in enumerate(lista)]}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": SITE, "item": BASE},
              {"@type": "ListItem", "position": 2, "name": "Temas", "item": BASE + "temas/"},
              {"@type": "ListItem", "position": 3, "name": t}]}]
    items = "".join(
        f'<li><h2><a href="../problemas/{p["slug"]}.html">N.º {p["num"]} · {p["title_html"]}</a> <span class="dif">{p["dif"]}</span></h2>'
        f'{p["stmt"]}<a class="mas-link" href="../problemas/{p["slug"]}.html">Pista y solución →</a></li>'
        for p in lista)
    otros = "".join(f'<a class="tag" href="{slugify(o)}.html">{esc(o)}</a>' for o in temas_orden if o != t)
    page = head(f"{t}: problemas resueltos | {SITE}", desc, path, pre, ld, og_type="website")
    page += topbar(pre)
    page += f"""<div class="wrap pagina-tema">
  <p class="migas"><a href="../">Inicio</a> › <a href="./">Temas</a> › {esc(t)}</p>
  <h1>{esc(t)}</h1>
  <p class="lead">{len(lista)} problemas resueltos. Cada uno tiene una pista y una solución escondidas, para intentarlo antes de mirar.</p>
  <section><ul class="lista-tema">{items}</ul></section>
  <section><h2>Otros temas</h2><div class="temas-todos">{otros}</div></section>
"""
    page += footer(pre)
    open(os.path.join(OUT, path), "w", encoding="utf-8").write(page)

# índice de temas
pre = "../"
items = "".join(f'<a class="tag" href="{slugify(t)}.html">{esc(t)} ({tema_count[t]})</a>' for t in temas_orden)
page = head(f"Temas: problemas de matemática por tema | {SITE}",
            "Problemas de matemática resueltos ordenados por tema: geometría, desigualdades, teoría de números, álgebra lineal, combinatoria, polinomios y más.",
            "temas/", pre, og_type="website", math=False)
page += topbar(pre)
page += f"""<div class="wrap pagina-tema">
  <p class="migas"><a href="../">Inicio</a> › Temas</p>
  <h1>Temas</h1>
  <p class="lead">Los problemas del sitio, agrupados por tema.</p>
  <section><div class="temas-todos">{items}</div></section>
"""
page += footer(pre)
open(os.path.join(OUT, "temas", "index.html"), "w", encoding="utf-8").write(page)

# ---------- Portada ----------
pre = ""
lis = "".join(
    f'<li data-tags="{esc("|".join(p["tags"]))}"><a href="problemas/{p["slug"]}.html"><span class="n">{p["num"]}</span>'
    f'<span class="t">{p["title_html"]} <span class="dif">{p["dif"]}</span></span></a></li>\n'
    for p in probs)
filtro_btns = '<button type="button" data-valor="" aria-pressed="true">Todos</button>' + "".join(
    f'<button type="button" data-valor="{esc(t)}" aria-pressed="false">{esc(t)} ({tema_count[t]})</button>' for t in temas_orden)
redir = {p["id"]: f"problemas/{p['slug']}.html" for p in probs}
ld_home = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE, "inLanguage": "es",
            "description": "Problemas de matemática resueltos, con pista y solución: ideas ingeniosas, no matemática sofisticada."},
           {"@context": "https://schema.org", "@type": "ItemList", "name": "Problemas", "itemListElement": [
               {"@type": "ListItem", "position": k + 1, "url": f"{BASE}problemas/{p['slug']}.html", "name": p["seo"]}
               for k, p in enumerate(probs)]}]
acerca = soup.select_one("#acerca").decode_contents()
contacto = soup.select_one("#contacto").decode_contents()
page = head(f"{SITE}: problemas de matemática resueltos con pista y solución",
            f"Más de {len(probs) // 5 * 5} problemas de matemática resueltos, con pista y solución: geometría, desigualdades, teoría de números, álgebra lineal, combinatoria. Ideas ingeniosas, no matemática sofisticada.",
            "", pre, ld_home, og_type="website", math=True)
page += f"""<script>
// Enlaces viejos del tipo #p6 llevan a la página nueva del problema.
(function () {{
  var r = {json.dumps(redir)};
  var h = location.hash.slice(1);
  if (r[h]) location.replace(r[h]);
}})();
</script>
<header>
  <div class="wrap">
    <p class="kicker">{SITE}</p>
    <h1>Ideas ingeniosas,<br>no matemática sofisticada</h1>
    <p class="lead">Una colección de problemas de matemática resueltos, elegidos porque la solución esconde una idea que vale la pena conocer.</p>
  </div>
</header>

<div class="wrap">
  <nav>
    <a href="#indice">Índice</a>
    <a href="temas/">Temas</a>
    <a href="#acerca">Acerca del sitio</a>
    <a href="#contacto">Contacto</a>
  </nav>

  <section id="indice">
    <h2>Problemas</h2>
    <div class="filtro" id="filtro" aria-label="Filtrar por tema">{filtro_btns}</div>
    <p class="leyenda">Dificultad: <span class="dif">★</span> accesible · <span class="dif">★★</span> pide una idea · <span class="dif">★★★</span> difícil</p>
    <ol class="indice" id="lista-indice">
{lis}    </ol>
  </section>

  <section id="acerca" class="about">{acerca}</section>

  <section id="contacto" class="contact">{contacto}</section>

  <footer>
    {SITE} · problemas-interesantes.github.io
  </footer>
</div>

<script>
// Filtro por tema del índice.
(function () {{
  var filtro = document.getElementById('filtro');
  var lista = document.getElementById('lista-indice');
  function aplicar(valor) {{
    Array.prototype.forEach.call(filtro.children, function (b) {{
      b.setAttribute('aria-pressed', b.dataset.valor === valor ? 'true' : 'false');
    }});
    Array.prototype.forEach.call(lista.children, function (li) {{
      li.style.display = (valor === '' || li.dataset.tags.split('|').indexOf(valor) !== -1) ? '' : 'none';
    }});
  }}
  Array.prototype.forEach.call(filtro.children, function (b) {{
    b.addEventListener('click', function () {{ aplicar(b.dataset.valor); }});
  }});
}})();
</script>
</body>
</html>
"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)

# ---------- 404 ----------
page = head(f"Página no encontrada | {SITE}", "La página que buscás no existe.", "404.html", "/", math=False, og_type="website")
page = page.replace('<link rel="canonical" href="https://problemas-interesantes.github.io/404.html">', '<meta name="robots" content="noindex">')
page += topbar("/")
page += """<div class="wrap pagina-tema">
  <h1 style="margin-top:40px">No encontramos esa página</h1>
  <p class="lead">Puede que el problema haya cambiado de dirección. <a href="/" style="color:var(--accent)">Volver al índice de problemas</a>.</p>
"""
page += footer("/")
open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(page)

# ---------- sitemap y robots ----------
urls = [("", "1.0"), ("temas/", "0.6")] + [(f"temas/{slugify(t)}.html", "0.6") for t in temas_orden] + \
       [(f"problemas/{p['slug']}.html", "0.8") for p in probs]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url><loc>{BASE}{u}</loc><lastmod>{FECHA}</lastmod><priority>{pr}</priority></url>\n" for u, pr in urls) + "</urlset>\n"
open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")
print(len(probs), "problemas,", len(temas_orden), "temas,", len(urls), "URLs")

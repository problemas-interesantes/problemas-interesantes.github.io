# Fuente del sitio (no se publica: GitHub Pages ignora carpetas que empiezan con "_")

- `problemas.html`: todos los problemas, uno por `<article class="problem" id="pN">`. Para agregar uno nuevo se añade un `<article>` al final de la sección `#problemas`.
- `meta.py`: para cada `pN`, la dirección (slug), el título y la descripción para buscadores.
- `build.py`: genera el sitio. Desde la raíz del repositorio:

      python3 _fuente/build.py _fuente/problemas.html .

  Regenera `index.html`, `problemas/`, `temas/`, `sitemap.xml`, `robots.txt`, `404.html` y `estilo.css`.
  No toca `google908c1e05637571c2.html` (verificación de Search Console).

# -*- coding: utf-8 -*-
"""Markdown longo -> PDF A4 com a identidade visual Gov Hub, via WeasyPrint.

Monta capa (print-cover), faixa de capítulo (print-header), rodapé repetido
(print-footer) e tabelas com legenda numerada (print-table) sem que ninguém
precise reescrever o CSS: a receita das referências desta skill já está aqui.

O markdown precisa de um capítulo por `## N. Título`. O que o script faz com
ele: remove Sumário/H1/linha de versão, aplica a convenção editorial sem
travessão, numera as tabelas com legenda inferida do título anterior, dá
largura fixa às colunas dos formatos conhecidos, evita título órfão no fim da
página, transforma imagem solta em `<figure>` e parágrafo iniciado por
**Limitações:** (ou Atenção/Ressalva/Cuidado ao ler) em bloco de destaque.

Uso:
    python3 build_doc.py --config documento.json [--html-only]
    python3 build_doc.py --markdown doc.md --cover-title "Relatório" \
        --project-short MIR --out-dir ./pdf

Os caminhos do JSON são relativos ao próprio JSON. Campos aceitos:
    markdown, out_dir, out_html, out_pdf, cover_title, cover_subtitle,
    doc_short, project_short, partners[], eyebrows{}, eyebrow_default,
    logo_dir, dash_convention

Conferência obrigatória: rasterize o PDF e olhe todas as páginas, atrás de
overflow silencioso e de espaço desperdiçado (ver references/print-pages.md).
"""
import re, sys, os, json, argparse
from pathlib import Path
import markdown
from bs4 import BeautifulSoup, NavigableString

SKILL = Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser(add_help=True)
ap.add_argument("--config")
ap.add_argument("--markdown"); ap.add_argument("--out-dir")
ap.add_argument("--cover-title"); ap.add_argument("--cover-subtitle")
ap.add_argument("--doc-short"); ap.add_argument("--project-short")
ap.add_argument("--logo-dir"); ap.add_argument("--html-only", action="store_true")
args = ap.parse_args()

cfg, base = {}, Path.cwd()
if args.config:
    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base = cfg_path.parent
for chave, valor in (("markdown", args.markdown), ("out_dir", args.out_dir),
                     ("cover_title", args.cover_title), ("cover_subtitle", args.cover_subtitle),
                     ("doc_short", args.doc_short), ("project_short", args.project_short),
                     ("logo_dir", args.logo_dir)):
    if valor: cfg[chave] = valor

def caminho(valor, padrao=None):
    if not valor: return padrao
    p = Path(valor)
    return p if p.is_absolute() else (base / p).resolve()

if not cfg.get("markdown"):
    sys.exit("faltou o markdown de entrada (--markdown ou markdown no --config)")
MD = caminho(cfg["markdown"])
if not MD.exists(): sys.exit(f"markdown não encontrado: {MD}")

OUT_DIR = caminho(cfg.get("out_dir"), MD.parent)
OUT_DIR.mkdir(parents=True, exist_ok=True)
HTML_OUT = OUT_DIR / cfg.get("out_html", MD.stem + ".html")
PDF_OUT = OUT_DIR / cfg.get("out_pdf", MD.stem + ".pdf")

COVER_TITLE = cfg.get("cover_title") or MD.stem.replace("_", " ")
COVER_SUBTITLE = cfg.get("cover_subtitle", "")
DOC_SHORT = cfg.get("doc_short") or COVER_TITLE
PROJECT_SHORT = cfg.get("project_short", "Gov Hub")
PARTNERS = cfg.get("partners") or ["lab-livre-black.svg", "unb-dark-outlined.svg"]
DASH_CONVENTION = cfg.get("dash_convention", True)

# logos: por padrão os da própria skill; o HTML referencia por caminho relativo
LOGO_DIR = caminho(cfg.get("logo_dir"), SKILL / "references" / "logo")
if not LOGO_DIR.exists(): sys.exit(f"logo_dir não encontrado: {LOGO_DIR}")
_rel = os.path.relpath(LOGO_DIR, OUT_DIR).replace(os.sep, "/")
# relativo só se não precisar subir a árvore; senão file:// absoluto (HTML não
# fica portátil: para distribuir, copie os logos ao lado da saída e aponte logo_dir)
LOGO_REL = _rel if not _rel.startswith("..") else LOGO_DIR.as_uri()

# ---------------------------------------------------------------------------
# 1. Markdown -> HTML bruto
# ---------------------------------------------------------------------------
src = MD.read_text(encoding="utf-8")

# remove o Sumário do markdown (o PDF usa os marcadores/bookmarks do próprio arquivo)
src = re.sub(r"^## Sumário\n.*?(?=^## )", "", src, flags=re.S | re.M)
# remove o H1 e o cabeçalho de versão (a capa cumpre esse papel)
src = re.sub(r"^# .*?\n", "", src, count=1, flags=re.M)
src = re.sub(r"^\*\*Versão:\*\*.*?\n", "", src, flags=re.M)

def fix_dashes(text):
    """Convenção editorial Gov Hub: sem travessão no texto corrido."""
    # pares " — x — " viram vírgulas; travessão isolado vira dois-pontos
    out = []
    for sent in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ú*`(])", text):
        n = sent.count(" — ")
        if n >= 2 and n % 2 == 0:
            sent = re.sub(r" — (.*?) — ", r", \1, ", sent)
        sent = sent.replace(" — ", ": ")
        sent = sent.replace("—", "-")
        out.append(sent)
    return " ".join(out)

# aplica só fora de blocos de código e de células de tabela com nomes de coluna
lines = []
in_code = False
for ln in src.split("\n"):
    if ln.startswith("```"):
        in_code = not in_code; lines.append(ln); continue
    if in_code:
        lines.append(ln); continue
    if ln.startswith("#"):
        lines.append(ln.replace(" — ", " · ")); continue
    ln = ln.replace("| — |", "| não se aplica |")
    lines.append(fix_dashes(ln) if DASH_CONVENTION else ln)
src = "\n".join(lines)

html_body = markdown.markdown(src, extensions=["tables", "fenced_code", "sane_lists"])
soup = BeautifulSoup(html_body, "lxml")
body = soup.body

# ---------------------------------------------------------------------------
# 2. Reestrutura: capítulos (h2), tabelas com legenda, títulos de tabela
# ---------------------------------------------------------------------------
NAVY = "#0A005A"; PURPLE = "#613EFF"; PEACH = "#FFE7E1"

chapters = []  # (num, eyebrow, title, [elements])
front = []       # abertura: blocos .gh-front-page antes do capítulo 01
descartado = []  # o que veio antes do capítulo 01 sem marcação (só avisa)
cur = None
for el in list(body.children):
    if isinstance(el, NavigableString):
        continue
    if el.name == "h2":
        m = re.match(r"^\s*(\d+)\.\s*(.*)$", el.get_text())
        num, title = m.group(1), m.group(2)
        cur = {"num": num, "title": title, "els": []}
        chapters.append(cur)
        continue
    if cur is None:
        # Antes do capítulo 01: só entra no PDF o que foi marcado de propósito
        # (HTML bruto com class="gh-front-page", ver print-frontmatter.md).
        # Título, descrição e badges soltos servem a quem lê o .md: a capa
        # cumpre esse papel no PDF. O que for descartado é reportado no fim.
        if "gh-front-page" in (el.get("class") or []):
            front.append(el)
        else:
            descartado.append(el.get_text(" ", strip=True)[:70])
        continue
    cur["els"].append(el)
if not chapters:
    sys.exit("nenhum capítulo encontrado: o markdown precisa de '## N. Título'")

EYEBROW = {str(k): v for k, v in (cfg.get("eyebrows") or {}).items()}
EYEBROW_DEFAULT = cfg.get("eyebrow_default", "Capítulo")

# parágrafos que viram bloco de destaque (callout), pelo rótulo em negrito inicial.
# Cada rótulo tem um ícone de produto (icons-catalog.md); o chip é navy, então a
# variante é a de contorno pêssego (-default). Ver editorial-report.md seção 5.
CALLOUT_ICONS = {
    "limitações:": "exclamation-triangle", "limitação:": "exclamation-triangle",
    "atenção:": "notification", "ressalva:": "information-circle",
    "cuidado ao ler:": "eye",
}
CALLOUT_ICONS.update(cfg.get("callout_icons") or {})
CALLOUT_LABELS = set(CALLOUT_ICONS)
ICONS_BASE = cfg.get(
    "icons_base",
    "https://cdn.jsdelivr.net/gh/GovHub-br/skills-assets@main/gov-hub/icons")
ICON_VARIANT = cfg.get("icon_variant", "default")

# CSS extra do documento: para peças que o markdown não expressa (cards, grids)
# e que entram como HTML bruto no .md. Receitas em references/editorial-report.md.
EXTRA_CSS = cfg.get("extra_css", "")
if EXTRA_CSS and not EXTRA_CSS.lstrip().startswith(("."  , "#", "@", "*", ":")):
    _f = caminho(EXTRA_CSS)                      # também aceita caminho de arquivo
    if not _f.exists(): sys.exit(f"extra_css não encontrado: {_f}")
    EXTRA_CSS = _f.read_text(encoding="utf-8")

def render_table(tbl, n):
    """Tabela do markdown -> print-table.md (legenda numerada + header navy + zebra)."""
    tbl["class"] = "gh-print-table"
    for attr in ("align", "style"):
        for td in tbl.find_all(["td", "th"]):
            if td.has_attr(attr):
                del td[attr]
    # coluna "#" estreita e "Coluna"/"Campo" com largura fixa
    ths = tbl.find("thead").find_all("th")
    head = [t.get_text().strip() for t in ths]
    colgroup = soup.new_tag("colgroup")
    widths = None
    if head[:3] == ["#", "Coluna", "Descrição"]:
        widths = ["8mm", "58mm", None]
    elif head[:4] == ["#", "Campo", "Tipo", "Descrição"]:
        widths = ["8mm", "52mm", "18mm", None]
    elif len(head) == 2:
        widths = ["44mm", None]
    if widths:
        for wdt in widths:
            col = soup.new_tag("col")
            if wdt: col["style"] = f"width:{wdt}"
            colgroup.append(col)
        tbl.insert(0, colgroup)
        if head[0] == "#":
            tbl["class"] = "gh-print-table gh-print-table--cols"
    return tbl

def caption_for(tbl, label, fallback=""):
    """label: último h3/h4 ou último parágrafo iniciado por <strong> antes da tabela."""
    head = [t.get_text().strip() for t in tbl.find("thead").find_all("th")]
    if label is None:
        return fallback or " × ".join(head)
    code = label.find("code")
    if head[:2] in (["#", "Coluna"], ["#", "Campo"]) and code is not None:
        return f"colunas de {code.get_text().strip()}"
    if label.name == "p":
        strong = label.find("strong")
        txt = strong.get_text().strip().rstrip(":") if strong else label.get_text().strip()
    else:
        txt = label.get_text().strip()
        m = re.match(r"^[\d.]+\s+(.*)$", txt)
        if m: txt = m.group(1)
        txt = re.sub(r"\s+·\s+\w+$", "", txt)
    return txt

table_counter = 0
for ch in chapters:
    new_els = []
    last_heading = None; last_label = None
    for el in ch["els"]:
        if el.name in ("h3", "h4"):
            last_heading = el; last_label = el
        elif el.name == "p" and el.contents and getattr(el.contents[0], "name", None) == "strong":
            last_label = el
        if el.name == "table":
            table_counter += 1
            head = [t.get_text().strip() for t in el.find("thead").find_all("th")]
            label = last_heading if head[:2] in (["#", "Coluna"], ["#", "Campo"]) else last_label
            cap = soup.new_tag("p", attrs={"class": "gh-table-caption"})
            cap.string = f"Tabela {table_counter}: {caption_for(el, label, ch['title'])}"
            new_els.append(cap)
            new_els.append(render_table(el, table_counter))
            continue
        # imagem sozinha num parágrafo -> <figure>, com o caminho relativo ao HTML de saída
        if el.name == "p":
            img = el.find("img")
            if img is not None and el.get_text().strip() == "":
                src = img.get("src", "")
                if not src.startswith(("http", "/", "../")):
                    img["src"] = "../" + src
                figura = soup.new_tag("figure", attrs={"class": "gh-figure"})
                figura.append(img.extract())
                new_els.append(figura)
                continue
            # parágrafo de limitação/ressalva -> bloco de destaque
            strong = el.contents[0] if el.contents else None
            if getattr(strong, "name", None) == "strong" and \
               strong.get_text().strip().lower() in CALLOUT_LABELS:
                rotulo = strong.get_text().strip().lower()
                box = soup.new_tag("div", attrs={"class": "gh-callout"})
                el.replace_with(box)
                badge = soup.new_tag("div", attrs={"class": "gh-callout__badge"})
                icone = soup.new_tag("img", alt="", src=(
                    f"{ICONS_BASE}/{CALLOUT_ICONS[rotulo]}-{ICON_VARIANT}.svg"))
                badge.append(icone)
                corpo = soup.new_tag("div", attrs={"class": "gh-callout__body"})
                corpo.append(el)
                box.append(badge); box.append(corpo)
                new_els.append(box)
                continue
        new_els.append(el)
    # título (h3/h4) + elemento seguinte num bloco indivisível: evita título órfão no fim da página
    # sem usar break-after:avoid (que impede a tabela seguinte de quebrar entre linhas no WeasyPrint)
    grouped = []; i = 0
    while i < len(new_els):
        e = new_els[i]
        if e.name in ("h3", "h4") and i + 1 < len(new_els) and new_els[i + 1].name in ("p", "ul", "pre"):
            keep = soup.new_tag("div", attrs={"class": "gh-keep"})
            keep.append(e); keep.append(new_els[i + 1])
            grouped.append(keep); i += 2
        else:
            grouped.append(e); i += 1
    ch["els"] = grouped

# ---------------------------------------------------------------------------
# 3. Monta o documento final
# ---------------------------------------------------------------------------
CSS = f"""
@page {{ size: A4; margin: 0; }}
@page content {{
  size: A4; margin: 20mm 20mm 32mm 20mm;
  @bottom-center {{ content: element(gh-footer); width: 100%; vertical-align: top; padding: 0; margin: 0; }}
}}
:root {{
  --primary-purple: {PURPLE}; --dark-navy: {NAVY}; --bg-peach: {PEACH};
  --text-strong: #202020; --text-body: #2D3748; --text-muted: #666666;
  --bg-white: #FFFFFF; --bg-subtle: #F8F9FA; --border-soft: #E9DFFF; --accent-pink: #F9006F;
  --editorial-00-navy: {NAVY};
  --font-family-base: 'Reddit Sans', 'Open Sans', sans-serif;
  --font-family-heading: 'Oswald', 'Reddit Sans', sans-serif;
  --section-color: var(--editorial-00-navy);
}}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: var(--font-family-base); color: var(--text-body); background: #fff; }}
code {{ font-family: 'DejaVu Sans Mono', monospace; font-size: 88%; color: var(--dark-navy); }}
pre {{ font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; line-height: 1.35; color: var(--text-body);
       background: var(--bg-subtle); border: 1px solid var(--border-soft); border-radius: 6px; padding: 10px 12px; white-space: pre; margin: 0 0 14px; }}
strong {{ color: var(--text-strong); }}

/* ---------- figuras ---------- */
.gh-figure {{ margin: 6px 0 16px; text-align: center; break-inside: avoid; page-break-inside: avoid; }}
.gh-figure img {{ max-width: 100%; height: auto; }}

/* ---------- bloco de destaque: limitações e ressalvas ---------- */
.gh-callout {{ border: 1.4px solid var(--section-color); border-radius: 8px; background: var(--bg-white);
  padding: 12px 14px; margin: 0 0 14px; display: flex; gap: 12px; align-items: flex-start;
  break-inside: avoid; page-break-inside: avoid; }}
.gh-callout__badge {{ width: 46px; height: 46px; flex-shrink: 0; border-radius: 6px;
  background: var(--dark-navy); display: flex; align-items: center; justify-content: center; }}
.gh-callout__badge img {{ width: 32px; height: 32px; }}
.gh-callout__body {{ flex: 1; }}
.gh-callout__body p {{ margin: 0; font-size: 10.5pt; text-align: left; }}
.gh-callout__body p > strong:first-child {{ display: block; color: var(--section-color);
  text-transform: uppercase; letter-spacing: .04em; font-size: 9pt; margin-bottom: 3px; }}

/* ---------- capa (print-cover.md) ---------- */
.gh-page {{ width: 210mm; height: 297mm; position: relative; overflow: hidden; page: cover; }}
.gh-cover {{ background: var(--bg-white); color: var(--dark-navy); }}
.gh-shape {{ position: absolute; display: block; }}
.gh-cover__logo {{ position: absolute; left: 20mm; top: 20mm; height: 12mm; width: auto; }}
.gh-cover__content {{ position: absolute; left: 20mm; right: 20mm; top: 32%; }}
.gh-cover__title {{ font-family: var(--font-family-heading); font-weight: 700; text-transform: uppercase;
  font-size: 46px; line-height: 1.04; letter-spacing: .005em; color: var(--dark-navy); margin: 0 0 18px; max-width: 14ch; }}
.gh-cover__subtitle {{ font-size: 14px; line-height: 1.55; max-width: 46ch; color: var(--text-body); margin: 0; }}
.gh-cover__footer {{ position: absolute; left: 20mm; bottom: 16mm; }}
.gh-cover__footer img {{ height: 34px; width: auto; vertical-align: middle; margin-right: 36px; }}
@page cover {{ size: A4; margin: 0; }}

/* ---------- abertura: o que vem antes do capítulo 01 (print-frontmatter.md) ---------- */
.gh-front {{ page: content; break-before: page; }}
.gh-front-page {{ break-after: page; }}

/* ---------- capítulos (print-header.md) ---------- */
.gh-chapter {{ page: content; break-before: page; }}
.gh-band {{ padding: 2mm 0 9mm; border-bottom: 2px solid var(--border-soft); color: var(--dark-navy); margin-bottom: 12mm; }}
.gh-band__row {{ display: flex; align-items: center; }}
.gh-band__num {{ font-size: 56px; font-weight: 800; line-height: 1; color: var(--dark-navy); opacity: .45; min-width: 34mm; margin-right: 8mm; }}
.gh-band__eyebrow {{ text-transform: uppercase; letter-spacing: 2px; font-size: 11px; font-weight: 700; color: var(--dark-navy); opacity: .7; margin-bottom: 7px; }}
.gh-band__title {{ color: var(--primary-purple); font-size: 22pt; font-weight: 800; line-height: 1.2; margin: 0; bookmark-level: 1; }}

/* ---------- corpo (escala print-header.md) ---------- */
.gh-body h3 {{ font-size: 16pt; color: var(--dark-navy); margin: 18px 0 10px; bookmark-level: 2; }}
.gh-body h4 {{ font-size: 12.5pt; color: var(--dark-navy); margin: 16px 0 8px; bookmark-level: 3; }}
.gh-body > :first-child, .gh-keep:first-child > h3, .gh-keep:first-child > h4 {{ margin-top: 0; }}
.gh-keep {{ break-inside: avoid; }}
.gh-body p  {{ font-size: 11.5pt; line-height: 1.5; color: var(--text-body); margin: 0 0 12px; text-align: justify; hyphens: none; }}
.gh-body li {{ font-size: 11.5pt; line-height: 1.5; color: var(--text-body); margin-bottom: 4px; text-align: justify; }}
.gh-body ul, .gh-body ol {{ margin: 0 0 12px; padding-left: 22px; }}
.gh-body blockquote {{ margin: 0 0 14px; padding: 10px 14px; border-left: 3px solid var(--primary-purple); background: var(--bg-subtle); }}
.gh-body blockquote p {{ margin: 0; font-size: 10.5pt; }}
.gh-body em {{ color: var(--text-body); }}

/* ---------- tabela (print-table.md) ---------- */
.gh-table-caption {{ font-size: 10.5pt; font-weight: 700; color: var(--section-color); margin: 0 0 6pt; break-after: avoid; }}
.gh-print-table {{ width: 100%; border-collapse: collapse; margin: 0 0 16px; }}
.gh-print-table thead {{ display: table-header-group; }}
.gh-print-table thead th {{ background: var(--section-color); color: #fff; font-weight: 600; font-size: 9.5pt; text-align: left; padding: 7pt 9pt; }}
.gh-print-table tbody td {{ padding: 6pt 9pt; font-size: 9.5pt; color: var(--text-body); border-bottom: 1px solid var(--border-soft); vertical-align: top; line-height: 1.35; }}
.gh-print-table tbody tr {{ break-inside: avoid; }}
.gh-print-table tbody tr:last-child td {{ border-bottom: none; }}
.gh-print-table tbody tr:nth-child(even) td {{ background: var(--bg-subtle); }}
.gh-print-table td code, .gh-print-table th code {{ font-size: 8.6pt; overflow-wrap: anywhere; }}
.gh-print-table--cols td:first-child {{ color: var(--text-muted); text-align: right; padding-right: 4pt; }}

/* ---------- rodapé (print-footer.md) ---------- */
.gh-footer-run {{ position: running(gh-footer); height: 32mm; }}
.gh-footer-bar {{ margin-top: 9mm; height: 2px; background: var(--border-soft); }}
.gh-footer {{ display: flex; align-items: center; justify-content: space-between; margin-top: 6.5mm; height: 9.5mm; }}
.gh-footer__text {{ font-size: 9pt; color: var(--text-muted); }}
.gh-footer__page {{ font-size: 9pt; font-weight: 800; color: var(--dark-navy); margin-right: 10px; }}
.gh-footer__page::before {{ content: counter(page); }}
.gh-footer__logo {{ height: 9.5mm; width: auto; }}
""" + EXTRA_CSS

def _parceiro(item):
    """Aceita "arquivo.svg" ou {"file": "...", "alt": "Nome"}; o alt é obrigatório
    para leitor de tela (ver SKILL.md, Acessibilidade)."""
    if isinstance(item, dict):
        arq, alt = item["file"], item.get("alt", "")
    else:
        arq, alt = item, Path(item).stem.replace("-", " ").title()
    return f'<img src="{LOGO_REL}/parceiros/{arq}" alt="{alt}">'

PARTNERS_IMGS = "".join(_parceiro(x) for x in PARTNERS)

COVER = f"""
<div class="gh-page gh-cover">
  <svg class="gh-shape" viewBox="0 0 100 100" style="right:-1px; bottom:-1px; width:104mm; height:104mm">
    <path fill="{PURPLE}" d="M100 100H0A100 100 0 0 1 100 0z"/>
  </svg>
  <svg class="gh-shape" viewBox="0 0 266 100" style="left:-26mm; top:64mm; width:74mm; height:27.8mm">
    <rect width="266" height="100" rx="50" fill="{PEACH}"/>
  </svg>
  <svg class="gh-shape" viewBox="0 0 100 100" style="right:-12mm; top:22mm; width:40mm; height:40mm">
    <path fill="{NAVY}" fill-rule="evenodd" d="M50 0a50 50 0 1 0 0 100a50 50 0 1 0 0-100zM50 25.6a24.4 24.4 0 1 1 0 48.8a24.4 24.4 0 1 1 0-48.8z"/>
  </svg>
  <img class="gh-cover__logo" src="{LOGO_REL}/logomarca-horizontal-navy.svg" alt="Gov Hub">
  <div class="gh-cover__content">
    <h1 class="gh-cover__title">{COVER_TITLE}</h1>
    <p class="gh-cover__subtitle">{COVER_SUBTITLE}</p>
  </div>
  <div class="gh-cover__footer">
    {PARTNERS_IMGS}
  </div>
</div>
"""

FOOTER = f"""
<div class="gh-footer-run">
  <div class="gh-footer-bar"></div>
  <div class="gh-footer">
    <span class="gh-footer__text"><span class="gh-footer__page"></span>{DOC_SHORT} &middot; {PROJECT_SHORT} &middot; Gov Hub &middot; Lab Livre - UnB</span>
    <img class="gh-footer__logo" alt="" src="{LOGO_REL}/icone-none-navy.svg">
  </div>
</div>
"""

parts = [f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>{DOC_SHORT} · {PROJECT_SHORT} · Gov Hub</title><style>{CSS}</style></head><body>""", COVER]

# abertura (folha de identificação, índice): HTML bruto escrito no próprio markdown,
# antes do primeiro "## N.". Ver references/print-frontmatter.md.
if front:
    parts.append(f"""
<section class="gh-front">
  {FOOTER}
  {"".join(str(e) for e in front)}
</section>""")

for ch in chapters:
    body_html = "".join(str(e) for e in ch["els"])
    parts.append(f"""
<section class="gh-chapter">
  {FOOTER}
  <div class="gh-band"><div class="gh-band__row">
    <div class="gh-band__num">{int(ch['num']):02d}</div>
    <div><div class="gh-band__eyebrow">{EYEBROW.get(ch['num'], EYEBROW_DEFAULT)}</div><h2 class="gh-band__title">{ch['title']}</h2></div>
  </div></div>
  <div class="gh-body">{body_html}</div>
</section>""")
parts.append("</body></html>")
HTML_OUT.write_text("\n".join(parts), encoding="utf-8")
print("html:", HTML_OUT, f"({table_counter} tabelas, {len(chapters)} capítulos"
      + (f", {len(front)} de abertura" if front else "") + ")")
for t in descartado:
    print(f"  ignorado (antes do capítulo 01, sem class=gh-front-page): {t}...")

if not args.html_only:
    from weasyprint import HTML
    HTML(filename=str(HTML_OUT), base_url=str(OUT_DIR)).write_pdf(str(PDF_OUT))
    print("pdf:", PDF_OUT)

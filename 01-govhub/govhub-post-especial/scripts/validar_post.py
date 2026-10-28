#!/usr/bin/env python3
"""Confere o HTML de uma página especial do gov-hub.io antes de colar no painel.

Uso:
    python3 validar_post.py post.html
    python3 validar_post.py post.html --fotos fotos.txt   # nomes das fotos como estão no painel, um por linha

Sai com código 1 e lista os problemas se algo quebraria no site.
"""
import argparse
import re
import sys
from pathlib import Path

PREFIXO = "ghx"
PASTA_FOTOS = "/blog/images/"
TAGS_PROIBIDAS = ("!doctype", "html", "head", "body", "script", "link", "meta", "title",
                  "header", "footer", "nav", "iframe")
EXT_IMAGEM = re.compile(r"\.(webp|png|jpe?g|gif|svg)$", re.I)


def seletores_css(css):
    """Devolve (seletor, linha) de cada regra, pulando @media/@container (entra neles) e @keyframes (pula)."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    saida, i, pilha = [], 0, []
    for m in re.finditer(r"([^{};]*)([{};])", css):
        texto, sinal = m.group(1).strip(), m.group(2)
        linha = css.count("\n", 0, m.start(2)) + 1
        if sinal == "{":
            dentro_keyframes = "keyframes" in pilha
            if texto.startswith("@"):
                pilha.append("keyframes" if "keyframes" in texto else "at")
            else:
                pilha.append("regra")
                if not dentro_keyframes:
                    saida.extend((s.strip(), linha) for s in texto.split(",") if s.strip())
        elif sinal == "}" and pilha:
            pilha.pop()
    return saida


def validar(texto, fotos=None):
    erros = []  # (exemplo, tipo); um problema sem exemplo usa a própria mensagem nos dois
    def erro(exemplo, tipo=None):
        erros.append((exemplo, tipo or exemplo))

    if re.search(r"\\[_*#\[\]]", texto):
        exemplos = sorted(set(re.findall(r"\S*\\[_*#\[\]]\S*", texto)))[:3]
        erro(f"barra invertida antes de _ * # [ ]: sinal de que o editor visual escapou o código "
             f"(ex.: {', '.join(exemplos)}). Gere de novo e cole no modo markdown.")
    if "@import" in texto:
        erro("@import no <style>: a fonte Reddit Sans já vem do site; tire o @import.")
    if re.search(r"!\[[^\]]*\]\(", texto):
        erro("imagem no formato do editor (![...](...)) no meio do HTML: aparece como texto. Use <img>.")
    for tag in TAGS_PROIBIDAS:
        if re.search(rf"<{re.escape(tag)}[\s>]", texto, re.I):
            erro(f"<{tag}> não pode entrar: o site já tem cabeçalho, rodapé e scripts; o post é só o miolo.")

    estilos = re.findall(r"<style>(.*?)</style>", texto, re.S)
    if len(estilos) != 1:
        erro(f"precisa de exatamente um bloco <style>, no começo (achei {len(estilos)}).")
    corpo = re.sub(r"<style>.*?</style>", "", texto, flags=re.S).strip()
    if not texto.lstrip().startswith("<style>"):
        erro("o arquivo deve começar pelo <style>.")
    if not corpo.startswith(f'<div class="{PREFIXO}">') or not corpo.endswith("</div>"):
        erro(f'depois do <style>, todo o conteúdo fica dentro de um único <div class="{PREFIXO}">...</div>.')

    for css in estilos:
        for sel, linha in seletores_css(css):
            if not re.match(rf"\.{PREFIXO}(?![\w-])", sel):
                erro(f'"{sel}" (linha {linha} do <style>)',
                     f'seletor CSS sem ".{PREFIXO}" na frente: sem isso o estilo vaza para o site inteiro')

    for attr in re.findall(r'class="([^"]*)"', corpo):
        for c in attr.split():
            if c != PREFIXO and not c.startswith(PREFIXO + "-"):
                erro(f'"{c}"', f'classe sem o prefixo "{PREFIXO}-": nomes como hero, band, lead, row, card '
                     "já são do site ou do Bootstrap e recebem o estilo deles")
    for i in re.findall(r'\sid="([^"]*)"', corpo):
        if not i.startswith(PREFIXO + "-"):
            erro(f'"{i}"', f'id sem o prefixo "{PREFIXO}-"')

    caminhos = re.findall(r'<img\b[^>]*\bsrc="([^"]*)"', corpo, re.I)
    caminhos += [h for h in re.findall(r'\bhref="([^"]*)"', corpo) if EXT_IMAGEM.search(h)]
    for c in caminhos:
        if c.startswith(("https://", "data:")):
            continue
        if not c.startswith(PASTA_FOTOS):
            erro(f'"{c}"', f"caminho de imagem que não começa por {PASTA_FOTOS} (com a barra no começo): quebra no site")
        elif fotos is not None and c[len(PASTA_FOTOS):] not in fotos:
            erro(f'"{c[len(PASTA_FOTOS):]}"', "foto que não está na lista do painel: confira o nome exato "
                 "(minúsculas, .webp, -1 quando o nome se repetiu) ou envie a foto antes")
    for tag in re.findall(r"<img\b[^>]*>", corpo, re.I):
        if not re.search(r'\balt="[^"]+"', tag):
            erro(tag[:70], "imagem sem texto alternativo (alt)")
    for tag in re.findall(r'<a\b[^>]*target="[^"]*"[^>]*>', corpo):
        if 'target="_blank"' in tag and 'rel="noopener"' not in tag:
            erro(tag[:70], 'link com target="_blank" sem rel="noopener"')
    return erros


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivo")
    ap.add_argument("--fotos", help="arquivo com os nomes das fotos no painel, um por linha")
    args = ap.parse_args()
    texto = Path(args.arquivo).read_text(encoding="utf-8")
    fotos = None
    if args.fotos:
        fotos = {l.strip().rsplit("/", 1)[-1] for l in Path(args.fotos).read_text(encoding="utf-8").splitlines() if l.strip()}
    erros = validar(texto, fotos)
    if erros:
        grupos = {}
        for exemplo, tipo in dict.fromkeys(erros):
            grupos.setdefault(tipo, []).append(exemplo)
        print(f"❌ {len(grupos)} tipo(s) de problema:")
        for tipo, exemplos in grupos.items():
            extras = [e for e in exemplos if e != tipo]
            print(f"  - {tipo}" + (f" ({len(extras)}x)" if len(extras) > 1 else ""))
            for e in extras[:3]:
                print(f"      {e}")
            if len(extras) > 3:
                print(f"      … e mais {len(extras) - 3}")
        sys.exit(1)
    print("✅ Pronto para colar no painel (modo markdown, com Página especial marcada).")


if __name__ == "__main__":
    main()

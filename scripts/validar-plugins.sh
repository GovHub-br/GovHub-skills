#!/usr/bin/env bash
# Valida o marketplace e os plugins deste repositório.
# Rode antes de abrir um PR: ./scripts/validar-plugins.sh
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

echo "==> Coerência entre manifestos e pastas de skill"
python3 - <<'PY'
import json, pathlib, re, sys

raiz = pathlib.Path.cwd()
erros = []

mercado = json.loads((raiz / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
declaradas = set()

for entrada in mercado["plugins"]:
    origem = (raiz / entrada["source"]).resolve()
    manifesto = origem / ".claude-plugin/plugin.json"
    if not manifesto.is_file():
        erros.append(f"{entrada['name']}: falta {manifesto.relative_to(raiz)}")
        continue

    plugin = json.loads(manifesto.read_text(encoding="utf-8"))
    if plugin["name"] != entrada["name"]:
        erros.append(f"{entrada['name']}: plugin.json declara name={plugin['name']!r}")

    for caminho in plugin.get("skills", []):
        pasta = (origem / caminho).resolve()
        arquivo = pasta / "SKILL.md"
        if not arquivo.is_file():
            erros.append(f"{entrada['name']}: {caminho} não tem SKILL.md")
            continue

        declaradas.add(pasta)
        achado = re.search(r'^name:\s*["\']?([^"\'\n]+?)["\']?\s*$',
                           arquivo.read_text(encoding="utf-8"), re.M)
        nome = achado.group(1).strip() if achado else None
        if nome != pasta.name:
            erros.append(f"{entrada['name']}: {caminho} tem name={nome!r}, "
                         f"esperado {pasta.name!r} (igual ao da pasta)")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", pasta.name):
            erros.append(f"{pasta.name}: nome de pasta precisa ser kebab-case minúsculo")

    print(f"  {entrada['name']:18} {len(plugin.get('skills', [])):3} skills  <- {entrada['source']}")

# Skills no disco que ninguém declarou passariam despercebidas — acusa.
for arquivo in raiz.glob("[0-9][0-9]-*/*/SKILL.md"):
    if arquivo.parent.resolve() not in declaradas:
        rel = arquivo.parent.relative_to(raiz)
        erros.append(f"{rel} existe no disco mas não está em nenhum plugin.json "
                     f"(rode ./scripts/atualizar-manifestos.py)")

if erros:
    print("\nERROS:")
    for e in erros:
        print(" -", e)
    sys.exit(1)
print("\n  ok — manifestos e pastas batem.")
PY

echo
echo "==> Validação oficial da CLI do Claude Code"
if ! command -v claude >/dev/null 2>&1; then
  echo "  claude não encontrado no PATH — pulando (instale o Claude Code para validar aqui)."
  exit 0
fi

claude plugin validate .
for categoria in [0-9][0-9]-*/; do
  claude plugin validate "$categoria"
done

#!/usr/bin/env python3
"""govhub-diagramas — extrai nós e arestas de um target/manifest.json do dbt.

Uso: python3 dbt_lineage.py <manifest.json> [--group schema|layer]

  --group schema  agrupa pelo schema físico (mapa de schemas)       [padrão]
  --group layer   agrupa pela camada inferida do path do modelo
                  (models/bronze/..., silver, gold, staging, marts...);
                  sources viram "fonte"; sem camada no path, usa o schema.

Saída (stdout, JSON):
  {"groups": [{"name": "...", "nodes": [{"id", "name", "kind", "materialization", "description"}]}],
   "edges": [[from_id, to_id], ...]}

Só stdlib. O JSON é insumo para diagramar — não gera layout.
"""
import json
import re
import sys

LAYER_RE = re.compile(
    r"(?:^|/)(bronze|silver|gold|staging|stg|intermediate|int|marts?|raw|prata|ouro|bruto)(?:/|_|$)",
    re.IGNORECASE,
)
KINDS = {"model", "seed", "snapshot"}


def _layer_of(item):
    if item["kind"] == "source":
        return "fonte"  # source é sempre o estágio "Fontes", mesmo que more no schema bronze
    path = item.get("original_file_path") or item.get("path") or ""
    m = LAYER_RE.search(path) or LAYER_RE.search(item.get("schema") or "")
    if m:
        return m.group(1).lower()
    return item.get("schema") or "outros"


def _items(manifest):
    items = {}
    for uid, s in manifest.get("sources", {}).items():
        items[uid] = {
            "id": uid, "name": f"{s['source_name']}.{s['name']}", "kind": "source",
            "materialization": "source", "description": s.get("description", ""),
            "schema": s.get("schema", ""), "path": s.get("path", ""),
            "original_file_path": s.get("original_file_path", ""),
        }
    for uid, n in manifest.get("nodes", {}).items():
        if n["resource_type"] not in KINDS:
            continue
        items[uid] = {
            "id": uid, "name": n["name"], "kind": n["resource_type"],
            "materialization": n.get("config", {}).get("materialized", "view"),
            "description": n.get("description", ""), "schema": n.get("schema", ""),
            "path": n.get("path", ""), "original_file_path": n.get("original_file_path", ""),
        }
    return items


def load(manifest_path, group="schema"):
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    items = _items(manifest)
    groups = {}
    for it in items.values():
        key = (it["schema"] or "sem-schema") if group == "schema" else _layer_of(it)
        groups.setdefault(key, []).append(
            {k: it[k] for k in ("id", "name", "kind", "materialization", "description")})
    edges = []
    for uid, n in manifest.get("nodes", {}).items():
        if uid not in items:
            continue
        for dep in n.get("depends_on", {}).get("nodes", []):
            if dep in items:
                edges.append([dep, uid])
    return {
        "groups": [{"name": k, "nodes": sorted(v, key=lambda x: x["name"])} for k, v in sorted(groups.items())],
        "edges": sorted(edges),
    }


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 1
    group = "schema"
    if "--group" in argv:
        i = argv.index("--group")
        group = argv[i + 1] if i + 1 < len(argv) else ""
    if group not in ("schema", "layer"):
        print("--group deve ser schema ou layer", file=sys.stderr)
        return 1
    try:
        out = load(argv[1], group)
    except FileNotFoundError:
        print(f"{argv[1]} não existe. Gere com: dbt parse (ou dbt compile) no projeto dbt.", file=sys.stderr)
        return 2
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

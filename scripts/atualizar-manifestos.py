#!/usr/bin/env python3
"""Gera .claude-plugin/marketplace.json e os plugin.json do repo GovHub-skills."""
import json, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION = "1.0.0"
AUTHOR = {"name": "GovHub BR / lablivre", "url": "https://github.com/GovHub-br"}
REPO = "https://github.com/GovHub-br/GovHub-skills"

CATS = [
    {
        "dir": "01-govhub",
        "name": "govhub-core",
        "titulo": "Específicas do GovHub",
        "description": "Skills específicas do GovHub BR: guia de implementação de pipelines (Airflow + dbt + Postgres), identidade visual oficial e relatório de prestação de contas a partir do git.",
        "keywords": ["govhub", "airflow", "dbt", "dados-abertos", "prestacao-de-contas", "identidade-visual"],
    },
    {
        "dir": "02-dados-e-bancos",
        "name": "govhub-dados",
        "titulo": "Dados & Bancos",
        "description": "Engenharia e ciência de dados, Postgres (schema, boas práticas, otimização), SQL, BigQuery, Jupyter e extração de PDF para banco.",
        "keywords": ["postgres", "sql", "bigquery", "data-engineering", "etl", "jupyter"],
    },
    {
        "dir": "03-backend-apis",
        "name": "govhub-backend",
        "titulo": "Backend & APIs",
        "description": "Python e FastAPI, design de APIs REST/GraphQL, documentação, integração com APIs de terceiros e segurança de APIs.",
        "keywords": ["python", "fastapi", "api", "rest", "graphql", "backend"],
    },
    {
        "dir": "04-infra-devops",
        "name": "govhub-infra",
        "titulo": "Infra & DevOps",
        "description": "Docker, IaC, GitHub Actions, shell scripting e observabilidade com Prometheus e Grafana.",
        "keywords": ["docker", "devops", "ci-cd", "github-actions", "prometheus", "grafana", "observability"],
    },
    {
        "dir": "05-qualidade-testes",
        "name": "govhub-qualidade",
        "titulo": "Qualidade, Testes & Arquitetura",
        "description": "TDD, testes em Python, depuração sistemática, clean code, arquitetura (ADR, DDD, padrões), performance, segurança e gestão de segredos.",
        "keywords": ["tdd", "testes", "clean-code", "arquitetura", "adr", "ddd", "seguranca", "performance"],
    },
    {
        "dir": "06-docs-relatorios",
        "name": "govhub-docs",
        "titulo": "Docs & Relatórios",
        "description": "Geração de documentos e relatórios: docx, xlsx, PDF, planilhas, README, changelog, diagramas Mermaid e conversão de web para Markdown.",
        "keywords": ["documentacao", "docx", "xlsx", "pdf", "changelog", "mermaid", "readme"],
    },
]


def skills_de(cat_dir: pathlib.Path):
    return sorted(
        p.name for p in cat_dir.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    )


def escrever(path: pathlib.Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  escrito {path.relative_to(ROOT)}")


todas = []
entradas_marketplace = []

for cat in CATS:
    cat_dir = ROOT / cat["dir"]
    skills = skills_de(cat_dir)
    todas += [f"./{cat['dir']}/{s}" for s in skills]

    escrever(
        cat_dir / ".claude-plugin" / "plugin.json",
        {
            "name": cat["name"],
            "version": VERSION,
            "description": f"{cat['description']} ({len(skills)} skills)",
            "author": AUTHOR,
            "homepage": REPO,
            "repository": REPO,
            "keywords": cat["keywords"],
            "skills": [f"./{s}" for s in skills],
        },
    )
    entradas_marketplace.append(
        {
            "name": cat["name"],
            "source": f"./{cat['dir']}",
            "description": f"{cat['titulo']} — {cat['description']} ({len(skills)} skills)",
            "category": "development",
        }
    )

# Plugin "tudo": na raiz do repo.
escrever(
    ROOT / ".claude-plugin" / "plugin.json",
    {
        "name": "govhub-skills",
        "version": VERSION,
        "description": f"Coleção completa de skills do GovHub BR / lablivre — as {len(todas)} skills de todas as categorias em um único plugin.",
        "author": AUTHOR,
        "homepage": REPO,
        "repository": REPO,
        "keywords": ["govhub", "dados-governamentais", "airflow", "dbt", "postgres", "python", "devops", "documentacao"],
        "skills": todas,
    },
)

escrever(
    ROOT / ".claude-plugin" / "marketplace.json",
    {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": "govhub",
        "version": VERSION,
        "description": "Marketplace de skills do Claude Code do GovHub BR / lablivre — dados governamentais, pipelines, relatórios oficiais, backend, infra, qualidade e documentação.",
        "owner": AUTHOR,
        "plugins": [
            {
                "name": "govhub-skills",
                "source": "./",
                "description": f"Coleção completa — todas as {len(todas)} skills de uma vez. Instale este OU os plugins por categoria abaixo, não os dois.",
                "category": "development",
            }
        ]
        + entradas_marketplace,
    },
)

print(f"\nTotal: {len(todas)} skills em {len(CATS)} categorias.")

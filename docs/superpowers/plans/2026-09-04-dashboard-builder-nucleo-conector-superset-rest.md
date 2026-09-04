# Núcleo `dashboard-builder` + Conector Superset via API REST — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separar a skill `dashboard-superset-builder` em um núcleo agnóstico de ferramenta (`dashboard-builder`) e um conector Superset, e migrar o conector de MCP para a API REST do Superset com um cliente Python empacotado e testado.

**Architecture:** Duas skills. `dashboard-builder` conduz o raciocínio de design (perfil do usuário, hierarquia, esboço, wireframe, gate humano) e, nos pontos em que precisa de dados ou ações reais, instrui o agente a invocar a skill conectora da ferramenta escolhida — mesmo mecanismo de handoff que superpowers usa entre suas próprias skills. `dashboard-superset-builder` fica só com o que é específico de Superset (perguntas de dataset/dashboard alvo, descoberta, execução), tudo via `scripts/superset_client.py`, um cliente REST com autenticação por cookie de sessão. Diferente do resto do repositório (conteúdo puro), o cliente é código executável e ganha testes automatizados com HTTP mockado.

**Tech Stack:** Markdown (SKILL.md + references), Python 3.10+ com `requests` (runtime do cliente) e `pytest` + `unittest.mock` (testes, sem servidor ao vivo), JSON (`.claude-plugin/*.json` gerados por `scripts/atualizar-manifestos.py`), Bash (`scripts/validar-plugins.sh`).

## Global Constraints

- **Nenhuma chamada de escrita** (`create-chart`, `create-dashboard`, `add-chart-to-dashboard`) pode ocorrer antes da aprovação humana explícita da Fase 3 do núcleo — barreira dura, sem exceção. Substitui a antiga regra sobre tools MCP com tag `mutate`.
- `SUPERSET_URL`, `SUPERSET_USERNAME`, `SUPERSET_PASSWORD` nunca entram em arquivo versionado — só variável de ambiente/`.env` local (já coberto pelo `.gitignore`).
- **Autenticação é por cookie de sessão, nunca JWT/bearer:** nesta instância o bearer é cego para parte dos dashboards (`GET /api/v1/dashboard/<slug>` devolve 404 com bearer e 200 com cookie).
- **Idempotência é obrigatória em toda escrita:** procurar por nome/slug antes de criar; ao achar, conferir o **conteúdo** (não só a existência) antes de decidir se atualiza.
- **`position_json` sempre com `meta` em todo nó**, cadeia mínima `ROOT → GRID → ROW → CHART`. O front do Superset 6 quebra a página inteira com `n.meta is undefined`.
- **Paginação é Rison** (`?q=(page:N,page_size:100)`); `page`/`page_size` soltos são ignorados em silêncio e devolvem 20 itens.
- **Nunca usar a listagem para saber se um dashboard existe** — `GET /api/v1/dashboard/` pode omitir dashboards que `GET /api/v1/dashboard/<slug>` devolve normalmente. Buscar pelo slug/id direto e devolver o id.
- `--dry-run` sempre **lê** de verdade; só pula a escrita.
- A Fase 1b (re-derivar de um dashboard fonte) continua **somente leitura e sem gate humano**.
- Criar dataset (inclusive virtual, via SQL) continua **fora de escopo** do conector.
- Fora de escopo deste plano: conectores Power BI e Metabase.

Spec completa: [`docs/superpowers/specs/2026-09-04-dashboard-builder-nucleo-conector-superset-rest.md`](../specs/2026-09-04-dashboard-builder-nucleo-conector-superset-rest.md).

---

## File Structure

```
01-govhub/dashboard-builder/                          # NOVO — núcleo
├── SKILL.md                                           # Tarefa 4
└── references/
    └── diretrizes-dashboard.md                        # Tarefa 4 (git mv do conector)

01-govhub/dashboard-superset-builder/                  # existente — vira conector
├── SKILL.md                                           # Tarefa 5 (reescrito)
├── scripts/
│   ├── superset_client.py                             # Tarefas 2 (auth+leitura) e 3 (escrita)
│   └── test_superset_client.py                        # Tarefas 2 e 3
└── references/
    ├── superset-api.md                                # Tarefa 1 (novo)
    └── superset-schema.md                             # Tarefa 5 (removido)

.claude-plugin/plugin.json                             # Tarefa 6 (script)
.claude-plugin/marketplace.json                        # Tarefa 6 (script)
01-govhub/.claude-plugin/plugin.json                   # Tarefa 6 (script)
README.md                                              # Tarefa 6 (à mão)
```

Fonte de conhecimento para a Tarefa 1: `api.md` na raiz do repositório (não
versionado — documento interno do usuário, baseado nos scripts de produção
`bootstrap_conjuntura.py` e `build_boletim.py`).

---

### Task 1: `references/superset-api.md` — conhecimento operacional da API

**Files:**
- Create: `01-govhub/dashboard-superset-builder/references/superset-api.md`

**Interfaces:**
- Consumes: `api.md` na raiz do repositório (leitura; não versionado, não copiar inteiro — curar).
- Produces: o documento que a Tarefa 2 e a Tarefa 3 implementam em código, e que a Tarefa 5 referencia pelo caminho `references/superset-api.md`. Os títulos de seção abaixo são citados pelo `SKILL.md` da Tarefa 5 e precisam bater exatamente: `## Autenticação`, `## Paginação`, `## Ordem de criação`, `## Idempotência`, `## position_json`, `## Armadilhas`.

- [ ] **Step 1: Ler o `api.md` da raiz**

Run: `cat /home/joaoegewarth/GovHub-skills/api.md`
Objetivo: é a fonte. Curar, não copiar inteiro — o que interessa à skill é
autenticação, paginação, ordem de criação, idempotência, `position_json` e as
armadilhas. Fora de escopo (não trazer): a seção sobre Airflow, os trechos sobre
os scripts específicos `bootstrap_conjuntura.py`/`build_boletim.py`, e a seção de
conferência pós-execução.

- [ ] **Step 2: Criar o arquivo**

Conteúdo de `01-govhub/dashboard-superset-builder/references/superset-api.md`:

````markdown
# API REST do Superset — o que a skill precisa saber

Conhecimento operacional destilado de scripts de produção que publicam
dashboards no Superset por API. As armadilhas da última seção custaram tempo
real e **não estão na documentação oficial**.

Quem implementa isto em código é `scripts/superset_client.py`; este documento é
o "porquê" por trás daquele script.

## Autenticação

Credenciais em variável de ambiente (nunca em arquivo versionado):

```
SUPERSET_URL=https://…
SUPERSET_USERNAME=…
SUPERSET_PASSWORD=…
```

**Use o cookie de sessão, não o JWT.** O Superset oferece os dois caminhos, mas
nesta classe de instância o bearer de `/api/v1/security/login` é **cego para
parte dos dashboards**: `GET /api/v1/dashboard/<slug>` devolve 404 com bearer e
200 com cookie, e a listagem com bearer omite os mesmos dashboards. Isso já fez
um script relatar "já existente, preservado" para um dashboard que ele podia e
precisava atualizar. O cookie enxerga estritamente mais.

O fluxo tem três passos:

1. `GET /login/` — o `csrf_token` é um campo oculto no HTML.
2. `POST /login/` com `username`, `password` e `csrf_token` — autenticação por
   **formulário**, que devolve o cookie de sessão.
3. `GET /api/v1/security/csrf_token/` — o token daí vai no header `X-CSRFToken`
   da sessão, junto com `Referer` apontando para a base. **O Superset recusa
   escrita sem `Referer`.**

## Paginação

A API **ignora `page` e `page_size` soltos** e devolve 20 itens em silêncio. O
parâmetro correto é `q`, em [Rison](https://github.com/Nanonid/rison):

```
GET /api/v1/dataset/?q=(page:0,page_size:100)
```

Com filtro:

```
q=(filters:!((col:table_name,opr:ct,value:gld_boletim)),page_size:100)
```

Para percorrer tudo: avance `page` até que a soma dos resultados alcance o
`count` da resposta, ou até vir uma página vazia.

## Ordem de criação

Cada recurso depende do anterior; criar fora de ordem devolve erro sem
explicação útil.

```
database  →  dataset  →  chart  →  dashboard
 conexão     tabela ou    visual    layout +
 ao banco    SQL virtual            filtros
```

A skill entra a partir de **chart** — criar database e dataset está fora do
escopo dela.

**Chart** — `POST /api/v1/chart/`:

```json
{
  "slice_name": "PIB da Construção Civil",
  "viz_type": "table",
  "datasource_id": 42,
  "datasource_type": "table",
  "params": "{\"datasource\":\"42__table\",\"viz_type\":\"table\",…}"
}
```

`params` é **string JSON**, não objeto. E o `datasource` de dentro dele repete o
id no formato `<id>__table` — os dois precisam concordar.

**Dashboard** — `POST /api/v1/dashboard/`:

```json
{
  "dashboard_title": "Boletim de Conjuntura",
  "slug": "boletim-conjuntura",
  "published": true,
  "json_metadata": "{…}",
  "position_json": "{…}"
}
```

`json_metadata` e `position_json` também são **strings JSON**.

## Idempotência

Rodar duas vezes não pode duplicar nada. O padrão é **procurar antes de criar** e
**conferir o conteúdo** quando já existe — achar pelo nome e seguir adiante não
basta (ver a primeira armadilha):

1. Listar os existentes e indexar por nome (`slice_name`) ou slug.
2. Se não existe → criar.
3. Se existe → comparar o conteúdo relevante (no mínimo `datasource_id` e
   `params`). Igual → não fazer nada. Diferente → `PUT`.

## `position_json`

O front do Superset 6 lê `node.meta.width` ao montar a página. Ligar um chart
direto no `ROOT_ID`, ou omitir `meta` em qualquer nó estrutural, quebra a página
inteira com `n.meta is undefined`.

A cadeia mínima é `ROOT → GRID → ROW → CHART`, e **todos os nós levam `meta`**,
mesmo vazio. O grid do Superset tem 12 colunas de largura; um layout de duas
colunas usa `width: 6` por chart.

## Armadilhas

**O chart não some quando o dataset some.** Ele continua na tela e apenas para de
carregar — ninguém é avisado. Uma renomeação de schema já deixou 27 charts órfãos
porque o script achava o chart pelo nome, reaproveitava o id e nunca conferia o
dataset.

**A listagem não revela todos os dashboards.** `GET /api/v1/dashboard/` pode
omitir dashboards que `GET /api/v1/dashboard/<slug>` devolve normalmente. Para
saber se existe, **busque pelo slug e devolva o id**, não um booleano — é o id
que permite atualizar em vez de só constatar.

**Dataset virtual guarda as colunas antigas.** Se o SQL passa a devolver outras
colunas, o dataset segue pedindo as de antes e o chart quebra com
`column "…" does not exist`.

**Execução completa sobrescreve ajustes feitos na interface.** Quem mexeu no
layout pelo Superset perde. Leia o layout publicado antes de reescrevê-lo.

**Apagar dataset exige que nenhum chart aponte para ele.** Confira na hora, não
com uma listagem de dez minutos atrás.

**Recorte de período é filtro, não dashboard.** Três dashboards que só diferem no
`default_filters` são três cópias para manter em dia; um dashboard com filtro
nativo na coluna resolve.

## Sobre schema de chart por `viz_type`

A API REST **não expõe** uma abstração tipada por `viz_type` (não há equivalente
ao `get_chart_type_schema` que o MCP oferecia). O campo `params` é o `form_data`
nativo do Superset, específico de cada `viz_type` e sem schema formal publicado.

A técnica de substituição é **exemplo-guiado**: leia um chart existente do
`viz_type` desejado (`get-chart <id>`) e use o `params` dele como referência de
forma. Não invente nomes de campo.
````

- [ ] **Step 3: Conferir que os seis títulos de seção citados pelo `SKILL.md` existem**

Run:
```bash
grep -c '^## Autenticação$\|^## Paginação$\|^## Ordem de criação$\|^## Idempotência$\|^## `position_json`$\|^## Armadilhas$' \
  /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/references/superset-api.md
```
Expected: `6`

- [ ] **Step 4: Conferir que nenhuma credencial ou endereço real vazou**

Run:
```bash
grep -inE '10\.0\.0\.|Bearer eyJ|SUPERSET_PASSWORD=.+[^…]$' \
  /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/references/superset-api.md
```
Expected: nenhuma saída (as credenciais aparecem só como nomes de variável, sem valores).

- [ ] **Step 5: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/references/superset-api.md
git commit -m "feat(dashboard-superset-builder): documentar a API REST do Superset

Curadoria do conhecimento operacional de scripts de produção: autenticação por
cookie de sessão (não JWT), paginação Rison, ordem de criação, idempotência,
position_json e as armadilhas que não estão na documentação oficial.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: `superset_client.py` — autenticação e leitura (TDD)

**Files:**
- Create: `01-govhub/dashboard-superset-builder/scripts/superset_client.py`
- Create: `01-govhub/dashboard-superset-builder/scripts/test_superset_client.py`

**Interfaces:**
- Consumes: as regras documentadas na Tarefa 1 (`references/superset-api.md`), seções `## Autenticação` e `## Paginação`.
- Produces, para a Tarefa 3 e a Tarefa 5 (nomes exatos):
  - `rison_q(page: int = 0, page_size: int = 100, filters=None) -> str`
  - `SupersetClient(base_url: str, username: str, password: str, session=None)` com atributos `.base` (str, sem barra final) e `.s` (a sessão HTTP)
  - `SupersetClient.login() -> None`
  - `SupersetClient.list_all(resource: str, filters=None) -> list[dict]`
  - `SupersetClient.get_dataset(id_) -> dict | None`
  - `SupersetClient.get_dashboard(ref) -> dict | None`
  - `SupersetClient.get_chart(id_) -> dict | None`
  - `cliente_do_ambiente() -> SupersetClient` (lê `SUPERSET_URL`/`SUPERSET_USERNAME`/`SUPERSET_PASSWORD`, já logado)
  - CLI: `list-datasets`, `get-dataset`, `get-dashboard`, `get-chart`

- [ ] **Step 1: Criar a pasta e escrever os testes que falham**

```bash
mkdir -p /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
```

Conteúdo de `01-govhub/dashboard-superset-builder/scripts/test_superset_client.py`:

```python
"""Testes do cliente REST do Superset. HTTP mockado — nenhum servidor ao vivo."""
import json
from unittest.mock import MagicMock

from superset_client import SupersetClient, rison_q


def resposta(status=200, corpo=None, texto=""):
    """Fabrica uma resposta HTTP falsa no formato que o `requests` devolve."""
    r = MagicMock()
    r.status_code = status
    r.text = texto
    r.json.return_value = corpo if corpo is not None else {}
    return r


def cliente(session):
    return SupersetClient("https://superset.exemplo/", "usuario", "senha", session=session)


# --- rison_q ---------------------------------------------------------------

def test_rison_q_paginacao_simples():
    assert rison_q(0) == "(page:0,page_size:100)"
    assert rison_q(2, 50) == "(page:2,page_size:50)"


def test_rison_q_com_filtro():
    q = rison_q(0, 100, filters=[("table_name", "ct", "gld_boletim")])
    assert q == "(filters:!((col:table_name,opr:ct,value:gld_boletim)),page:0,page_size:100)"


# --- login -----------------------------------------------------------------

def test_login_usa_formulario_e_fixa_csrf_e_referer():
    s = MagicMock()
    s.headers = {}
    s.get.side_effect = [
        resposta(texto='<input name="csrf_token" value="TOKEN-DA-PAGINA">'),
        resposta(corpo={"result": "TOKEN-DA-API"}),
    ]
    s.post.return_value = resposta()

    c = cliente(s)
    c.login()

    # autenticou por formulário, levando o csrf da página
    url_post, kwargs = s.post.call_args[0][0], s.post.call_args[1]
    assert url_post == "https://superset.exemplo/login/"
    assert kwargs["data"] == {
        "username": "usuario", "password": "senha", "csrf_token": "TOKEN-DA-PAGINA",
    }
    # fixou o csrf da API e o Referer na sessão
    assert s.headers["X-CSRFToken"] == "TOKEN-DA-API"
    assert s.headers["Referer"] == "https://superset.exemplo"


def test_base_url_perde_a_barra_final():
    assert cliente(MagicMock()).base == "https://superset.exemplo"


# --- listagem paginada -----------------------------------------------------

def test_list_all_percorre_todas_as_paginas():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"count": 3, "result": [{"id": 1}, {"id": 2}]}),
        resposta(corpo={"count": 3, "result": [{"id": 3}]}),
    ]
    assert cliente(s).list_all("dataset") == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert s.get.call_args_list[0][1]["params"] == {"q": "(page:0,page_size:100)"}
    assert s.get.call_args_list[1][1]["params"] == {"q": "(page:1,page_size:100)"}


def test_list_all_para_em_pagina_vazia():
    s = MagicMock()
    s.get.side_effect = [resposta(corpo={"count": 99, "result": []})]
    assert cliente(s).list_all("chart") == []


# --- leitura por id/slug ---------------------------------------------------

def test_get_dashboard_devolve_result():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 3, "dashboard_title": "Painel"}})
    assert cliente(s).get_dashboard("painel")["id"] == 3
    assert s.get.call_args[0][0] == "https://superset.exemplo/api/v1/dashboard/painel"


def test_get_dashboard_404_devolve_none_sem_levantar():
    s = MagicMock()
    s.get.return_value = resposta(status=404)
    assert cliente(s).get_dashboard("nao-existe") is None


def test_get_chart_devolve_result():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 1, "slice_name": "X"}})
    assert cliente(s).get_chart(1)["slice_name"] == "X"
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
```
Expected: erro de coleta — `ModuleNotFoundError: No module named 'superset_client'`.

- [ ] **Step 3: Escrever o `superset_client.py` (auth + leitura + CLI de leitura)**

Conteúdo de `01-govhub/dashboard-superset-builder/scripts/superset_client.py`:

```python
#!/usr/bin/env python3
"""Cliente REST do Superset para a skill dashboard-superset-builder.

Autenticação por cookie de sessão (nunca JWT) — o porquê está em
`references/superset-api.md`. Credenciais vêm do ambiente:
SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import requests

TIMEOUT = 30


def rison_q(page: int = 0, page_size: int = 100, filters=None) -> str:
    """Monta o parâmetro `q` em Rison.

    `filters` é uma lista de triplas (coluna, operador, valor). A API ignora
    `page`/`page_size` soltos e devolve 20 itens em silêncio — daí o Rison.
    """
    partes = []
    if filters:
        clausulas = ",".join(f"(col:{c},opr:{o},value:{v})" for c, o, v in filters)
        partes.append(f"filters:!({clausulas})")
    partes.append(f"page:{page}")
    partes.append(f"page_size:{page_size}")
    return "(" + ",".join(partes) + ")"


class SupersetClient:
    def __init__(self, base_url: str, username: str, password: str, session=None):
        self.base = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.s = session if session is not None else requests.Session()

    # --- autenticação ------------------------------------------------------

    def login(self) -> None:
        """Autentica por formulário e fixa X-CSRFToken e Referer na sessão."""
        pagina = self.s.get(f"{self.base}/login/", timeout=TIMEOUT)
        campo = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', pagina.text or "")
        self.s.post(
            f"{self.base}/login/",
            timeout=TIMEOUT,
            data={
                "username": self.username,
                "password": self.password,
                "csrf_token": campo.group(1) if campo else "",
            },
        )
        token = self.s.get(
            f"{self.base}/api/v1/security/csrf_token/", timeout=TIMEOUT
        ).json()["result"]
        self.s.headers["X-CSRFToken"] = token
        # O Superset recusa escrita sem Referer.
        self.s.headers["Referer"] = self.base

    # --- leitura -----------------------------------------------------------

    def list_all(self, resource: str, filters=None) -> list:
        """Percorre todas as páginas de /api/v1/<resource>/."""
        pagina, saida = 0, []
        while True:
            r = self.s.get(
                f"{self.base}/api/v1/{resource}/",
                params={"q": rison_q(pagina, 100, filters)},
                timeout=TIMEOUT,
            )
            corpo = r.json()
            resultados = corpo.get("result", [])
            saida += resultados
            if not resultados or len(saida) >= corpo.get("count", 0):
                return saida
            pagina += 1

    def _get_result(self, caminho: str):
        """GET que devolve `result`, ou None em 404 (não é erro: é 'não existe')."""
        r = self.s.get(f"{self.base}{caminho}", timeout=TIMEOUT)
        if r.status_code == 404:
            return None
        return r.json()["result"]

    def get_dataset(self, id_):
        return self._get_result(f"/api/v1/dataset/{id_}")

    def get_dashboard(self, ref):
        """Aceita slug ou id. Nunca usa a listagem: ela pode omitir dashboards."""
        return self._get_result(f"/api/v1/dashboard/{ref}")

    def get_chart(self, id_):
        return self._get_result(f"/api/v1/chart/{id_}")


def cliente_do_ambiente() -> SupersetClient:
    """Constrói o cliente a partir do ambiente e já autentica."""
    url = os.environ.get("SUPERSET_URL") or os.environ.get("SUPERSET_HOST_PORT")
    usuario = os.environ.get("SUPERSET_USERNAME")
    senha = os.environ.get("SUPERSET_PASSWORD")
    faltando = [
        nome
        for nome, valor in (
            ("SUPERSET_URL", url),
            ("SUPERSET_USERNAME", usuario),
            ("SUPERSET_PASSWORD", senha),
        )
        if not valor
    ]
    if faltando:
        sys.exit(f"Variáveis de ambiente ausentes: {', '.join(faltando)}")
    c = SupersetClient(url, usuario, senha)
    c.login()
    return c


def _imprimir(valor) -> None:
    print(json.dumps(valor, indent=2, ensure_ascii=False))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Cliente REST do Superset.")
    sub = p.add_subparsers(dest="comando", required=True)

    q = sub.add_parser("list-datasets", help="Lista datasets (paginação Rison).")
    q.add_argument("--filtro", help="Substring do table_name.")

    q = sub.add_parser("get-dataset", help="Colunas e métricas de um dataset.")
    q.add_argument("id")

    q = sub.add_parser("get-dashboard", help="Dashboard por slug ou id.")
    q.add_argument("ref")

    q = sub.add_parser("get-chart", help="params/form_data reais de um chart.")
    q.add_argument("id")

    args = p.parse_args(argv)
    c = cliente_do_ambiente()

    if args.comando == "list-datasets":
        filtros = [("table_name", "ct", args.filtro)] if args.filtro else None
        _imprimir(c.list_all("dataset", filtros))
    elif args.comando == "get-dataset":
        _imprimir(c.get_dataset(args.id))
    elif args.comando == "get-dashboard":
        _imprimir(c.get_dashboard(args.ref))
    elif args.comando == "get-chart":
        _imprimir(c.get_chart(args.id))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
```
Expected: 9 passed. Saída sem warnings.

- [ ] **Step 5: Conferir que o CLI recusa ambiente incompleto em vez de estourar**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
env -u SUPERSET_URL -u SUPERSET_HOST_PORT -u SUPERSET_USERNAME -u SUPERSET_PASSWORD \
  python3 superset_client.py get-dashboard 3; echo "exit=$?"
```
Expected: mensagem `Variáveis de ambiente ausentes: SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD` e `exit=1`.

- [ ] **Step 6: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/scripts/superset_client.py \
        01-govhub/dashboard-superset-builder/scripts/test_superset_client.py
git commit -m "feat(dashboard-superset-builder): cliente REST — autenticação e leitura

Login por formulário + cookie de sessão (nunca JWT), CSRF e Referer fixados na
sessão, paginação Rison, e leitura de dataset/dashboard/chart. get-dashboard
busca por slug ou id direto, nunca pela listagem, e trata 404 como 'não existe'.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: `superset_client.py` — escrita idempotente (TDD)

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/scripts/superset_client.py`
- Modify: `01-govhub/dashboard-superset-builder/scripts/test_superset_client.py`

**Interfaces:**
- Consumes, da Tarefa 2 (assinaturas exatas): `SupersetClient` com `.base` e `.s`, `SupersetClient.list_all(resource, filters=None)`, `SupersetClient.get_chart(id_)`, `SupersetClient.get_dashboard(ref)`, `cliente_do_ambiente()`, `_imprimir(valor)`, e o `main(argv=None)` com `argparse` já montado (acrescentar subcomandos ao mesmo parser).
- Produces, para a Tarefa 5 (nomes exatos):
  - `build_position_json(charts: list[dict]) -> dict` — cada item precisa de `id` e opcionalmente `slice_name`
  - `SupersetClient.create_chart(payload: dict, dry_run: bool = False) -> dict` — devolve `{"acao": …, "slice_name": …, "id": …}` com `acao` em `{"criado", "criaria", "atualizado", "atualizaria", "inalterado"}`
  - `SupersetClient.create_dashboard(payload: dict, chart_ids: list[int], dry_run: bool = False) -> dict`
  - `SupersetClient.add_chart_to_dashboard(dashboard_ref, chart_id: int, dry_run: bool = False) -> dict`
  - CLI: `create-chart --file X [--dry-run]`, `create-dashboard --file X [--dry-run]`, `add-chart-to-dashboard REF CHART_ID [--dry-run]`

- [ ] **Step 1: Acrescentar os testes que falham**

Acrescentar ao final de `01-govhub/dashboard-superset-builder/scripts/test_superset_client.py`:

```python
# --- build_position_json ---------------------------------------------------

def test_position_json_tem_meta_em_todo_no():
    from superset_client import build_position_json

    pos = build_position_json([{"id": 7, "slice_name": "A"}, {"id": 8, "slice_name": "B"}])
    nos = [v for k, v in pos.items() if k != "DASHBOARD_VERSION_KEY"]
    assert nos, "position_json não pode ser só a chave de versão"
    for no in nos:
        assert "meta" in no, f"nó sem meta quebra o front do Superset 6: {no['id']}"


def test_position_json_encadeia_root_grid_row_chart():
    from superset_client import build_position_json

    pos = build_position_json([{"id": 7, "slice_name": "A"}])
    assert pos["ROOT_ID"]["children"] == ["GRID_ID"]
    linha = pos["GRID_ID"]["children"][0]
    assert pos[linha]["type"] == "ROW"
    chart = pos[linha]["children"][0]
    assert pos[chart]["type"] == "CHART"
    assert pos[chart]["meta"]["chartId"] == 7
    assert pos[chart]["parents"] == ["ROOT_ID", "GRID_ID", linha]


def test_position_json_usa_duas_colunas_por_linha():
    from superset_client import build_position_json

    pos = build_position_json([{"id": i, "slice_name": str(i)} for i in range(1, 4)])
    linhas = pos["GRID_ID"]["children"]
    assert len(linhas) == 2, "3 charts em grid de 2 colunas => 2 linhas"
    assert len(pos[linhas[0]]["children"]) == 2
    assert len(pos[linhas[1]]["children"]) == 1
    primeiro = pos[linhas[0]]["children"][0]
    assert pos[primeiro]["meta"]["width"] == 6, "grid do Superset tem 12 colunas"


# --- create_chart idempotente ---------------------------------------------

PAYLOAD = {
    "slice_name": "Consumo Total",
    "viz_type": "table",
    "datasource_id": 42,
    "datasource_type": "table",
    "params": json.dumps({"datasource": "42__table", "viz_type": "table"}),
}


def test_create_chart_cria_quando_nao_existe():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"count": 0, "result": []})
    s.post.return_value = resposta(corpo={"id": 99})

    r = cliente(s).create_chart(PAYLOAD)

    assert r == {"acao": "criado", "slice_name": "Consumo Total", "id": 99}
    assert s.post.call_args[0][0] == "https://superset.exemplo/api/v1/chart/"


def test_create_chart_nao_faz_nada_quando_identico():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"count": 1, "result": [{"id": 5, "slice_name": "Consumo Total",
                                                "datasource_id": 42}]}),
        resposta(corpo={"result": {"id": 5, "params": PAYLOAD["params"]}}),
    ]

    r = cliente(s).create_chart(PAYLOAD)

    assert r == {"acao": "inalterado", "slice_name": "Consumo Total", "id": 5}
    s.post.assert_not_called()
    s.put.assert_not_called()


def test_create_chart_atualiza_quando_o_dataset_mudou():
    s = MagicMock()
    s.get.side_effect = [
        resposta(corpo={"count": 1, "result": [{"id": 5, "slice_name": "Consumo Total",
                                                "datasource_id": 7}]}),
        resposta(corpo={"result": {"id": 5, "params": PAYLOAD["params"]}}),
    ]
    s.put.return_value = resposta(corpo={"id": 5})

    r = cliente(s).create_chart(PAYLOAD)

    assert r == {"acao": "atualizado", "slice_name": "Consumo Total", "id": 5}
    assert s.put.call_args[0][0] == "https://superset.exemplo/api/v1/chart/5"


def test_create_chart_dry_run_le_mas_nao_escreve():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"count": 0, "result": []})

    r = cliente(s).create_chart(PAYLOAD, dry_run=True)

    assert r == {"acao": "criaria", "slice_name": "Consumo Total", "id": None}
    s.get.assert_called()  # dry-run lê de verdade
    s.post.assert_not_called()


# --- create_dashboard ------------------------------------------------------

def test_create_dashboard_nao_recria_quando_o_slug_ja_existe():
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 3, "slug": "painel"}})

    r = cliente(s).create_dashboard({"dashboard_title": "Painel", "slug": "painel"}, [7])

    assert r == {"acao": "inalterado", "slug": "painel", "id": 3}
    s.post.assert_not_called()


# --- add_chart_to_dashboard ------------------------------------------------

def test_add_chart_to_dashboard_preserva_o_layout_existente():
    from superset_client import build_position_json

    atual = build_position_json([{"id": 7, "slice_name": "A"}])
    s = MagicMock()
    s.get.return_value = resposta(corpo={"result": {"id": 3,
                                                    "position_json": json.dumps(atual)}})
    s.put.return_value = resposta(corpo={"id": 3})

    r = cliente(s).add_chart_to_dashboard("3", 8)

    assert r["acao"] == "adicionado"
    enviado = json.loads(s.put.call_args[1]["json"]["position_json"])
    chart_ids = [n["meta"]["chartId"] for n in enviado.values()
                 if isinstance(n, dict) and n.get("type") == "CHART"]
    assert sorted(chart_ids) == [7, 8], "o chart antigo tem que continuar lá"
```

- [ ] **Step 2: Rodar e confirmar que os novos testes falham**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
```
Expected: os 9 da Tarefa 2 passam; os 9 novos falham com `ImportError: cannot import name 'build_position_json'` e `AttributeError: … 'create_chart'`.

- [ ] **Step 3: Implementar `build_position_json` e as escritas**

Em `superset_client.py`, logo **depois** da função `rison_q`, acrescentar:

```python
LARGURA_COLUNA = 6  # o grid do Superset tem 12 colunas; 2 colunas => 6 cada
ALTURA_CHART = 50


def build_position_json(charts: list) -> dict:
    """Monta ROOT → GRID → ROW → CHART com `meta` em TODO nó.

    Omitir `meta` em qualquer nó quebra a página inteira do Superset 6 com
    `n.meta is undefined`. Duas colunas por linha.
    """
    pos = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"], "meta": {}},
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": [],
                    "parents": ["ROOT_ID"], "meta": {}},
    }
    for i in range(0, len(charts), 2):
        linha = f"ROW-{i // 2}"
        pos["GRID_ID"]["children"].append(linha)
        pos[linha] = {
            "type": "ROW", "id": linha, "children": [],
            "parents": ["ROOT_ID", "GRID_ID"],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }
        for chart in charts[i:i + 2]:
            no = f"CHART-{chart['id']}"
            pos[linha]["children"].append(no)
            pos[no] = {
                "type": "CHART", "id": no, "children": [],
                "parents": ["ROOT_ID", "GRID_ID", linha],
                "meta": {
                    "chartId": chart["id"],
                    "width": LARGURA_COLUNA,
                    "height": ALTURA_CHART,
                    "sliceName": chart.get("slice_name", ""),
                },
            }
    return pos
```

E, dentro da classe `SupersetClient`, logo **depois** de `get_chart`, acrescentar:

```python
    # --- escrita (nunca antes da aprovação humana da Fase 3) ---------------

    def create_chart(self, payload: dict, dry_run: bool = False) -> dict:
        """POST idempotente: procura por slice_name e compara o conteúdo.

        Achar pelo nome e seguir adiante não basta — um chart cujo dataset
        mudou continua na tela e só para de carregar, sem avisar ninguém.
        """
        nome = payload["slice_name"]
        atual = next(
            (c for c in self.list_all("chart") if c.get("slice_name") == nome), None
        )
        if atual is None:
            if dry_run:
                return {"acao": "criaria", "slice_name": nome, "id": None}
            novo = self.s.post(
                f"{self.base}/api/v1/chart/", json=payload, timeout=TIMEOUT
            ).json()
            return {"acao": "criado", "slice_name": nome, "id": novo["id"]}

        detalhe = self.get_chart(atual["id"]) or {}
        igual = (
            atual.get("datasource_id") == payload.get("datasource_id")
            and detalhe.get("params") == payload.get("params")
        )
        if igual:
            return {"acao": "inalterado", "slice_name": nome, "id": atual["id"]}
        if dry_run:
            return {"acao": "atualizaria", "slice_name": nome, "id": atual["id"]}
        self.s.put(
            f"{self.base}/api/v1/chart/{atual['id']}",
            json={
                "datasource_id": payload["datasource_id"],
                "datasource_type": payload["datasource_type"],
                "params": payload["params"],
            },
            timeout=TIMEOUT,
        )
        return {"acao": "atualizado", "slice_name": nome, "id": atual["id"]}

    def create_dashboard(self, payload: dict, chart_ids: list, dry_run: bool = False) -> dict:
        """POST de dashboard novo, com position_json montado a partir dos charts."""
        slug = payload.get("slug")
        if slug:
            existente = self.get_dashboard(slug)
            if existente:
                return {"acao": "inalterado", "slug": slug, "id": existente["id"]}
        charts = [{"id": i, "slice_name": (self.get_chart(i) or {}).get("slice_name", "")}
                  for i in chart_ids]
        corpo = dict(payload)
        corpo["position_json"] = json.dumps(build_position_json(charts))
        if dry_run:
            return {"acao": "criaria", "slug": slug, "id": None}
        novo = self.s.post(
            f"{self.base}/api/v1/dashboard/", json=corpo, timeout=TIMEOUT
        ).json()
        return {"acao": "criado", "slug": slug, "id": novo["id"]}

    def add_chart_to_dashboard(self, dashboard_ref, chart_id: int,
                               dry_run: bool = False) -> dict:
        """Lê o layout publicado, acrescenta o chart e reescreve.

        Ler antes é obrigatório: reescrever do zero apaga ajustes feitos na
        interface do Superset.
        """
        dash = self.get_dashboard(dashboard_ref)
        if dash is None:
            return {"acao": "dashboard_nao_encontrado", "id": None}
        atual = json.loads(dash.get("position_json") or "{}")
        existentes = [
            {"id": no["meta"]["chartId"], "slice_name": no["meta"].get("sliceName", "")}
            for no in atual.values()
            if isinstance(no, dict) and no.get("type") == "CHART"
        ]
        if any(c["id"] == chart_id for c in existentes):
            return {"acao": "inalterado", "id": dash["id"]}
        novo = self.get_chart(chart_id) or {}
        existentes.append({"id": chart_id, "slice_name": novo.get("slice_name", "")})
        if dry_run:
            return {"acao": "adicionaria", "id": dash["id"]}
        self.s.put(
            f"{self.base}/api/v1/dashboard/{dash['id']}",
            json={"position_json": json.dumps(build_position_json(existentes))},
            timeout=TIMEOUT,
        )
        return {"acao": "adicionado", "id": dash["id"]}
```

- [ ] **Step 4: Acrescentar os subcomandos de escrita ao CLI**

Em `main()`, logo **depois** do bloco que registra `get-chart`, acrescentar:

```python
    q = sub.add_parser("create-chart", help="Cria/atualiza um chart (idempotente).")
    q.add_argument("--file", required=True, help="JSON com o payload do chart.")
    q.add_argument("--dry-run", action="store_true")

    q = sub.add_parser("create-dashboard", help="Cria um dashboard novo.")
    q.add_argument("--file", required=True,
                   help='JSON com {"payload": {…}, "chart_ids": [1,2]}.')
    q.add_argument("--dry-run", action="store_true")

    q = sub.add_parser("add-chart-to-dashboard", help="Acrescenta um chart a um dashboard.")
    q.add_argument("ref")
    q.add_argument("chart_id", type=int)
    q.add_argument("--dry-run", action="store_true")
```

E, no despacho, logo **depois** do ramo `get-chart`, acrescentar:

```python
    elif args.comando == "create-chart":
        with open(args.file, encoding="utf-8") as fh:
            _imprimir(c.create_chart(json.load(fh), dry_run=args.dry_run))
    elif args.comando == "create-dashboard":
        with open(args.file, encoding="utf-8") as fh:
            entrada = json.load(fh)
        _imprimir(c.create_dashboard(entrada["payload"], entrada["chart_ids"],
                                     dry_run=args.dry_run))
    elif args.comando == "add-chart-to-dashboard":
        _imprimir(c.add_chart_to_dashboard(args.ref, args.chart_id,
                                           dry_run=args.dry_run))
```

- [ ] **Step 5: Rodar a suíte inteira**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 -m pytest test_superset_client.py -v
```
Expected: 18 passed, sem warnings.

- [ ] **Step 6: Conferir que o CLI expõe os sete subcomandos**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 superset_client.py --help
```
Expected: a lista de subcomandos traz `list-datasets`, `get-dataset`, `get-dashboard`, `get-chart`, `create-chart`, `create-dashboard`, `add-chart-to-dashboard`.

- [ ] **Step 7: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/scripts/superset_client.py \
        01-govhub/dashboard-superset-builder/scripts/test_superset_client.py
git commit -m "feat(dashboard-superset-builder): cliente REST — escrita idempotente

create-chart procura por slice_name e compara datasource_id e params antes de
decidir criar, atualizar ou não fazer nada. position_json sai com meta em todo
nó (ROOT -> GRID -> ROW -> CHART, 2 colunas). add-chart-to-dashboard lê o layout
publicado antes de reescrever, para não apagar ajustes feitos na interface.
--dry-run lê de verdade e só pula a escrita.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Skill nova `dashboard-builder` (núcleo)

**Files:**
- Create: `01-govhub/dashboard-builder/SKILL.md`
- Move: `01-govhub/dashboard-superset-builder/references/diretrizes-dashboard.md` → `01-govhub/dashboard-builder/references/diretrizes-dashboard.md`

**Interfaces:**
- Consumes: o conteúdo atual de `01-govhub/dashboard-superset-builder/SKILL.md` (as Fases 2 e 3, movidas quase literalmente).
- Produces: os nomes que a Tarefa 5 referencia — a skill `dashboard-builder`, a linha de cabeçalho `dashboard alvo:` do esboço, os rótulos de fase `Fase 2` e `Fase 3`, e o contrato de handoff ("invoque a skill conectora").

- [ ] **Step 1: Ler o `SKILL.md` atual inteiro**

Run: `cat /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/SKILL.md`
Objetivo: as Fases 2 e 3 vão quase literais para a skill nova; confirmar o texto exato antes de mover.

- [ ] **Step 2: Criar a pasta e mover as diretrizes**

```bash
cd /home/joaoegewarth/GovHub-skills
mkdir -p 01-govhub/dashboard-builder/references
git mv 01-govhub/dashboard-superset-builder/references/diretrizes-dashboard.md \
       01-govhub/dashboard-builder/references/diretrizes-dashboard.md
```

- [ ] **Step 3: Escrever o `01-govhub/dashboard-builder/SKILL.md`**

O arquivo tem quatro partes. A Fase 3 é **cópia literal** da seção
`## Fase 3 — Validação humana (gate obrigatório)` do `SKILL.md` atual do
conector. A Fase 2 é cópia da seção
`## Fase 2 — Montar o esboço (markdown + wireframe)`, com **três**
substituições — o envelope do esboço é agnóstico de ferramenta, mas os campos
dentro de `config:` não são, e o núcleo não pode fingir que são:

1. onde ela diz "consulte [`references/superset-schema.md`](references/superset-schema.md)"
   e manda chamar `get_chart_type_schema`, trocar por: "use os nomes de campo que
   a fase de descoberta do conector devolveu; se faltar algum, peça ao conector
   antes de montar o bloco — não invente nomes de campo.";
2. onde ela cita `add_chart_to_existing_dashboard` ao explicar o grid de 2
   colunas, trocar por "o conector posiciona em grid de 2 colunas";
3. o bloco de exemplo de componente inteiro (o fence ```` ```markdown ```` com
   `## Componente: Consumo Total do Período` e o parágrafo logo abaixo dele) é
   substituído por este, que mostra o envelope sem fixar vocabulário de nenhuma
   ferramenta:

   ````markdown
   ```markdown
   ## Componente: Consumo Total do Período
   - dataset: <o que a descoberta do conector devolveu>
   - prioridade: primária
   - config:
       <campos da ferramenta escolhida — o conector diz quais são e como se chamam>
   ```

   O envelope (`## Componente:`, `dataset:`, `prioridade:`, `config:`) é o mesmo
   para qualquer ferramenta. O conteúdo de `config:` **não é**: cada ferramenta
   tem seu próprio vocabulário, e quem fornece os nomes corretos é o conector, na
   fase de descoberta. Não invente nomes de campo e não reaproveite os de outra
   ferramenta.
   ````

O restante (frontmatter, Fase 0, handoff) é novo:

````markdown
---
name: dashboard-builder
description: >-
  Planeja um dashboard antes de construí-lo: levanta o perfil de quem vai usar,
  define a hierarquia da informação, produz um esboço estruturado em markdown com
  um wireframe do layout, e exige validação humana explícita antes de qualquer
  criação real. A criação em si fica com a skill conectora da ferramenta escolhida
  (Superset, Power BI ou Metabase). Use sempre que o usuário pedir para "montar um
  dashboard", "planejar um dashboard", "esboçar um dashboard", "criar um painel",
  "construir um dashboard" ou "recriar um dashboard com outra organização".
---

# Dashboard Builder

Esta skill conduz o **raciocínio de design** de um dashboard, do pedido inicial
até um esboço aprovado por um humano. Ela não fala com nenhuma ferramenta de BI:
sempre que precisa de dados reais ou de criar algo de verdade, invoca a **skill
conectora** da ferramenta escolhida.

**Nenhuma criação ou alteração acontece antes da Fase 3 (validação humana) ser
concluída com uma aprovação explícita.** Essa é uma barreira dura: se a resposta
do dev não for uma aprovação clara, não libere a execução — mesmo que pareça
óbvio que ele ia aprovar.

## Fase 0 — Contexto e escolha da ferramenta

Pergunte ao dev (só o que ainda não estiver claro na conversa):

1. **Perfil do usuário final do dashboard** — nível de experiência digital
   (iniciante / intermediário / avançado / especialista) e nível de conhecimento
   de negócio (leigo / técnico / especialista / gestor). Ver
   [`references/diretrizes-dashboard.md`](references/diretrizes-dashboard.md)
   seção "Perfil do usuário" para o que cada combinação implica em densidade e
   volume de informação.
2. **Dispositivo principal** (desktop / tablet / mobile) — dashboard corporativo
   tende a desktop, mas confirme.
3. **Qual pergunta o dashboard precisa responder em 5 segundos** — essa é a
   informação primária, a que recebe maior destaque no wireframe.
4. **Qual ferramenta de BI** — Superset, Power BI ou Metabase. Hoje só o Superset
   tem conector implementado (`dashboard-superset-builder`); para as outras duas,
   avise que o conector ainda não existe e não prossiga.

## Handoff — descoberta no conector

Com a ferramenta escolhida, **invoque a skill conectora correspondente**
(`dashboard-superset-builder` para Superset). Ela faz as perguntas específicas
da ferramenta (qual dataset, dashboard novo ou existente, se parte de um
dashboard fonte) e a descoberta somente leitura que devolve os **nomes reais** de
dataset, colunas e métricas.

Volte para a Fase 2 com esses nomes em mãos. Não monte o esboço com nomes
inventados: se a descoberta não achou algo, o esboço marca o item como pendente
e a Fase 3 não libera a execução.

## Fase 2 — Montar o esboço (markdown + wireframe)

<cópia literal da Fase 2 atual do conector, com as duas substituições descritas
no Step 3 deste plano>

## Fase 3 — Validação humana (gate obrigatório)

<cópia literal da Fase 3 atual do conector>

## Handoff — execução no conector

Só depois de uma aprovação explícita na Fase 3: **invoque de novo a skill
conectora** e peça a execução real do esboço aprovado. É o conector que sabe
traduzir cada bloco `## Componente:` em chamadas concretas da ferramenta.

Ao final, apresente ao dev o resumo que o conector devolveu: o que foi criado,
com links, e o que falhou, com a mensagem de erro.

## Referências

- [`references/diretrizes-dashboard.md`](references/diretrizes-dashboard.md) —
  resumo curado do guia de design (perfil de usuário, hierarquia de informação,
  densidade visual, contexto de uso, cores, tipografia) aplicado a dashboard.
````

- [ ] **Step 4: Conferir o frontmatter e as seções**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
python3 - <<'PY'
import pathlib, re
p = pathlib.Path("01-govhub/dashboard-builder/SKILL.md")
t = p.read_text(encoding="utf-8")
m = re.search(r'^name:\s*([^\n]+)$', t, re.M)
assert m and m.group(1).strip() == p.parent.name, "name não bate com a pasta"
for secao in ("## Fase 0", "## Fase 2", "## Fase 3", "## Handoff"):
    assert secao in t, f"faltou {secao}"
# Citar "Superset" como opção de ferramenta e nomear o conector é esperado. O que
# o núcleo NÃO pode ter é detalhe de implementação de nenhuma ferramenta.
for vazamento in ("superset_client", "api/v1", "viz_type", "chart_type",
                  "datasource_id", "superset-schema", "position_json",
                  "generate_chart", "add_chart_to_existing_dashboard"):
    assert vazamento not in t, f"detalhe de implementação vazou para o núcleo: {vazamento}"
print("OK")
PY
```
Expected: `OK`

- [ ] **Step 5: Conferir que as diretrizes foram movidas, não copiadas**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
ls 01-govhub/dashboard-builder/references/diretrizes-dashboard.md
ls 01-govhub/dashboard-superset-builder/references/diretrizes-dashboard.md 2>&1
```
Expected: o primeiro existe; o segundo dá `No such file or directory`.

- [ ] **Step 6: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-builder/ 01-govhub/dashboard-superset-builder/references/
git commit -m "feat(dashboard-builder): extrair o núcleo de planejamento

Skill nova, agnóstica de ferramenta: perfil do usuário, hierarquia da
informação, esboço + wireframe e o gate humano obrigatório. A Fase 0 escolhe a
ferramenta de BI e os dois handoffs (descoberta e execução) invocam a skill
conectora correspondente. As diretrizes de design vieram junto.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Reescrever `dashboard-superset-builder` como conector REST

**Files:**
- Modify: `01-govhub/dashboard-superset-builder/SKILL.md` (reescrito por inteiro)
- Delete: `01-govhub/dashboard-superset-builder/references/superset-schema.md`

**Interfaces:**
- Consumes: da Tarefa 1, os títulos de seção de `references/superset-api.md`; da Tarefa 2 e 3, os sete subcomandos do CLI (`list-datasets`, `get-dataset`, `get-dashboard`, `get-chart`, `create-chart`, `create-dashboard`, `add-chart-to-dashboard`) e o formato de retorno `{"acao": …}`; da Tarefa 4, a skill `dashboard-builder`, o cabeçalho `dashboard alvo:` e os rótulos `Fase 2`/`Fase 3`.
- Produces: nada para tarefas posteriores além do arquivo que a Tarefa 6 registra nos manifestos.

- [ ] **Step 1: Remover o cache de schema do MCP**

```bash
cd /home/joaoegewarth/GovHub-skills
git rm 01-govhub/dashboard-superset-builder/references/superset-schema.md
```
Motivo: era um cache do `get_chart_type_schema` do MCP, que não tem equivalente
na API REST. A técnica que o substitui está documentada em
`references/superset-api.md`, seção "Sobre schema de chart por `viz_type`".

- [ ] **Step 2: Reescrever o `SKILL.md` inteiro**

Conteúdo de `01-govhub/dashboard-superset-builder/SKILL.md`:

````markdown
---
name: dashboard-superset-builder
description: >-
  Conector Superset para a skill dashboard-builder: descobre datasets, colunas e
  métricas reais, lê dashboards existentes (inclusive para re-derivar um novo a
  partir de um dashboard fonte), e cria charts e dashboards de verdade via API
  REST do Superset. Use quando a ferramenta de BI escolhida for o Superset, ou
  quando o usuário pedir para "criar um chart no Superset", "publicar um dashboard
  no Superset", "ler um dashboard do Superset" ou "adicionar um chart a um
  dashboard do Superset".
---

# Conector Superset

Esta skill é o **braço de execução** da skill
[`dashboard-builder`](../dashboard-builder/SKILL.md) para o Superset. Ela não
decide o design do dashboard — isso é do núcleo. Ela responde por três coisas:
descobrir o que existe, e depois criar o que foi aprovado.

**Nenhum subcomando de escrita (`create-chart`, `create-dashboard`,
`add-chart-to-dashboard`) pode ser chamado antes de o núcleo confirmar que a
Fase 3 foi aprovada explicitamente.** Barreira dura, sem exceção.

Todas as chamadas passam por `scripts/superset_client.py`. **Não monte `curl` à
mão** e não invente endpoints: o script já encapsula autenticação, paginação e as
armadilhas documentadas em
[`references/superset-api.md`](references/superset-api.md).

## Pré-requisitos

O script precisa de `requests` e das credenciais no ambiente:

```bash
python3 -c "import requests" || pip install requests
# SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD no ambiente ou .env local
```

Se faltar variável, o script sai com a lista do que falta. **Nunca** coloque
credenciais em arquivo versionado — peça ao dev que exporte no ambiente.

## Fase 0-conector — perguntas específicas do Superset

1. **Dataset alvo**, se já existir (nome ou ID). Se o dev não souber, a Fase 1
   lista os candidatos.
2. **De onde vem o dashboard?**
   - `novo do zero` — a Fase 4 cria com `create-dashboard`.
   - `acrescentar a existente: <slug ou id>` — a Fase 4 usa
     `add-chart-to-dashboard`.
   - `novo a partir do fonte: <slug ou id>` — a Fase 1b lê o dashboard fonte
     antes, e a Fase 4 cria um dashboard **novo** (o fonte nunca é tocado).

Devolva as respostas ao núcleo: elas viram a linha `dashboard alvo:` no cabeçalho
do esboço da Fase 2.

## Fase 1 — Descoberta (somente leitura)

Se o dev indicou um dataset, pegue as colunas e métricas reais:

```bash
python3 scripts/superset_client.py get-dataset <id>
```

Se ele não souber qual usar, liste os candidatos e deixe-o escolher:

```bash
python3 scripts/superset_client.py list-datasets --filtro <parte-do-nome>
```

Use esses nomes reais no esboço, em vez de inventar. Se o dataset ainda não
existe no Superset, avise: criar dataset está **fora do escopo** desta skill, e
a Fase 4 só roda depois que ele existir. Não fique em loop — devolva a pendência
ao dev.

## Fase 1b — Ler o dashboard fonte (somente leitura)

Roda só quando a resposta da Fase 0-conector foi `novo a partir do fonte`.
Somente leitura: **não precisa de aprovação humana** e não escreve no fonte.

1. `python3 scripts/superset_client.py get-dashboard <slug ou id>` → título,
   charts e `position_json`. Se devolver `null`, o dashboard não existe: avise o
   dev e pare.
2. Para cada chart: `python3 scripts/superset_client.py get-chart <id>` →
   recupere `datasource_id`, `viz_type` original, e o `params`/`form_data` com
   métricas, dimensões e filtros.
3. Monte a lista de componentes pré-preenchida para a Fase 2 do núcleo — um
   bloco por chart, com **só os campos de dados** (dataset e o miolo de
   `params`). **Não** preencha `viz_type`, título nem posição: isso a Fase 2
   redecide do zero.
4. Capture o layout do fonte como bloco de referência textual
   `Estado atual do fonte:` — referência ("era assim"), nunca ponto de partida.

Casos de borda — **registre no esboço e siga**, nunca aborte a fase:

- `params` que não mapeia limpo → traga o que der e marque o bloco com
  `# viz_type a escolher` e `# config a confirmar`.
- `get-chart` devolve `null` (chart órfão, sem permissão) → pule o chart, siga
  nos outros, e **liste as falhas** ao fim da fase.
- Filtro em `adhoc_filters` com expressão SQL → não invente equivalente
  estruturado; marque com `# filtro do fonte a reconstruir`.

Um componente com qualquer um desses marcadores **não libera a Fase 4** — o
núcleo resolve antes, no gate.

## Fase 4 — Criação real

Só depois da aprovação explícita da Fase 3 do núcleo.

Para cada componente aprovado, na ordem do esboço:

1. Monte o payload do chart num arquivo JSON. `params` é **string JSON**, e o
   `datasource` de dentro dele repete o id no formato `<id>__table`:

   ```json
   {
     "slice_name": "Consumo Total do Período",
     "viz_type": "table",
     "datasource_id": 42,
     "datasource_type": "table",
     "params": "{\"datasource\":\"42__table\",\"viz_type\":\"table\",\"groupby\":[\"unidade\"],\"metrics\":[\"count\"],\"row_limit\":1000}"
   }
   ```

   Para saber a forma de `params` de um `viz_type`, leia um chart existente
   daquele tipo com `get-chart` e use o `params` dele como referência — a API
   REST não publica schema por `viz_type` (ver
   [`references/superset-api.md`](references/superset-api.md)).

2. Crie o chart (idempotente — rodar de novo não duplica):

   ```bash
   python3 scripts/superset_client.py create-chart --file componente.json
   ```

   A resposta traz `acao` (`criado`, `atualizado` ou `inalterado`) e o `id`.

3. Ligue os charts ao dashboard, conforme o `dashboard alvo:`:

   ```bash
   # novo (inclusive "novo a partir de"):
   python3 scripts/superset_client.py create-dashboard --file dashboard.json
   # onde dashboard.json = {"payload": {"dashboard_title": "...", "slug": "...",
   #                                     "published": true}, "chart_ids": [1, 2]}

   # acrescentar a um existente, um chart por vez:
   python3 scripts/superset_client.py add-chart-to-dashboard <slug ou id> <chart_id>
   ```

Use `--dry-run` primeiro se quiser mostrar ao dev o que mudaria — ele lê de
verdade e só pula a escrita.

Se um componente falhar, registre o erro e continue nos demais. Ao final,
devolva ao núcleo um resumo com o resultado de cada componente (ação, id e link)
e o link do dashboard.

## Fora de escopo

- **Alterar um dashboard existente** além de acrescentar charts — mexer no
  layout publicado, remover chart, mudar título ou filtros nativos. Reescrever o
  `position_json` inteiro apagaria ajustes feitos na interface.
- Criar dataset (físico ou virtual, via SQL) e criar conexão de banco.

## Referências

- [`references/superset-api.md`](references/superset-api.md) — autenticação,
  paginação, ordem de criação, idempotência, `position_json` e as armadilhas da
  API REST do Superset.
- `scripts/superset_client.py` — o cliente que implementa tudo isso.
````

- [ ] **Step 3: Conferir frontmatter, seções e ausência de resíduo de MCP**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
python3 - <<'PY'
import pathlib, re
p = pathlib.Path("01-govhub/dashboard-superset-builder/SKILL.md")
t = p.read_text(encoding="utf-8")
m = re.search(r'^name:\s*([^\n]+)$', t, re.M)
assert m and m.group(1).strip() == p.parent.name, "name não bate com a pasta"
for secao in ("## Fase 0-conector", "## Fase 1 ", "## Fase 1b", "## Fase 4", "## Fora de escopo"):
    assert secao in t, f"faltou {secao}"
for proibido in ("call_tool", "search_tools", "get_chart_type_schema",
                 "generate_chart", "add_chart_to_existing_dashboard",
                 "superset-schema.md", "MCP"):
    assert proibido not in t, f"resíduo de MCP: {proibido}"
print("OK")
PY
```
Expected: `OK`

- [ ] **Step 4: Conferir que os marcadores da Fase 1b são idênticos onde aparecem**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
grep -n 'viz_type a escolher\|config a confirmar\|filtro do fonte a reconstruir' \
  01-govhub/dashboard-superset-builder/SKILL.md
```
Expected: os três marcadores aparecem exatamente como `# viz_type a escolher`,
`# config a confirmar` e `# filtro do fonte a reconstruir` — sem variação de
grafia entre as ocorrências.

- [ ] **Step 5: Conferir que todo subcomando citado existe mesmo no CLI**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
for cmd in list-datasets get-dataset get-dashboard get-chart create-chart \
           create-dashboard add-chart-to-dashboard; do
  grep -q -- "$cmd" 01-govhub/dashboard-superset-builder/SKILL.md \
    && grep -q -- "\"$cmd\"" 01-govhub/dashboard-superset-builder/scripts/superset_client.py \
    && echo "ok $cmd" || echo "DIVERGENTE $cmd"
done
```
Expected: sete linhas `ok`, nenhuma `DIVERGENTE`.

- [ ] **Step 6: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add 01-govhub/dashboard-superset-builder/
git commit -m "feat(dashboard-superset-builder): virar conector REST do dashboard-builder

Reescrita: a skill perde as fases de design (foram para o núcleo) e fica com o
que é específico de Superset — perguntas de dataset/dashboard alvo, descoberta,
leitura de dashboard fonte e criação real, tudo via scripts/superset_client.py.
Remove o cache de schema do MCP, que não tem equivalente na API REST.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Registrar nos manifestos e no README

**Files:**
- Modify: `01-govhub/.claude-plugin/plugin.json` (via script)
- Modify: `.claude-plugin/plugin.json` (via script)
- Modify: `.claude-plugin/marketplace.json` (via script)
- Modify: `README.md` (à mão — contagens e tabela da seção "01 · Específicas do GovHub")

**Interfaces:**
- Consumes: `01-govhub/dashboard-builder/SKILL.md` (Tarefa 4) e `01-govhub/dashboard-superset-builder/SKILL.md` (Tarefa 5) precisam existir com frontmatter válido.

- [ ] **Step 1: Regenerar os manifestos**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
python3 scripts/atualizar-manifestos.py
```
Expected: `dashboard-builder` aparece entre as skills de `01-govhub`, e o total
sobe de 52 para 53.

- [ ] **Step 2: Validar a coerência**

Run: `cd /home/joaoegewarth/GovHub-skills && bash scripts/validar-plugins.sh`
Expected: exit 0; a tabela mostra `govhub-skills 53` e `govhub-core 5`.

- [ ] **Step 3: Atualizar as contagens no `README.md`**

Troque:
```diff
-| `govhub-skills` | **Tudo** — as 52 skills de todas as categorias | 52 |
-| `govhub-core` | [01 · Específicas do GovHub](#01--específicas-do-govhub) — pipelines, identidade visual, prestação de contas, dashboards Superset | 4 |
+| `govhub-skills` | **Tudo** — as 53 skills de todas as categorias | 53 |
+| `govhub-core` | [01 · Específicas do GovHub](#01--específicas-do-govhub) — pipelines, identidade visual, prestação de contas, dashboards | 5 |
```

- [ ] **Step 4: Atualizar a tabela da seção "01 · Específicas do GovHub"**

Substitua a linha de `dashboard-superset-builder` por estas duas:

```diff
-| [`dashboard-superset-builder`](01-govhub/dashboard-superset-builder/) | Planeja (esboço + wireframe), valida com o dev, e cria de fato dashboards e charts no Superset via MCP. |
+| [`dashboard-builder`](01-govhub/dashboard-builder/) | Planeja um dashboard antes de construí-lo: perfil de quem usa, hierarquia da informação, esboço + wireframe e validação humana obrigatória. Delega a criação à skill conectora da ferramenta escolhida. |
+| [`dashboard-superset-builder`](01-govhub/dashboard-superset-builder/) | Conector Superset do `dashboard-builder`: descobre datasets, lê dashboards existentes e cria charts/dashboards de verdade via API REST. |
```

- [ ] **Step 5: Conferir que o README e os manifestos concordam**

Run:
```bash
cd /home/joaoegewarth/GovHub-skills
grep -c '^| \[`dashboard-builder`\]' README.md
grep -c '^| \[`dashboard-superset-builder`\]' README.md
grep -c '53 skills' README.md
bash scripts/validar-plugins.sh >/dev/null && echo "validador ok"
```
Expected: `1`, `1`, `1` e `validador ok` — uma linha de tabela para cada skill e
a contagem atualizada.

- [ ] **Step 6: Commit**

```bash
cd /home/joaoegewarth/GovHub-skills
git add .claude-plugin/ 01-govhub/.claude-plugin/ README.md
git commit -m "feat: registrar dashboard-builder nos manifestos e no README

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: Verificação manual ponta a ponta

Não produz arquivo. **Não pode ser delegada a um subagente isolado:** precisa de
um Superset real alcançável, das credenciais no ambiente, e do usuário para
aprovar/reprovar no gate da Fase 3.

**Files:** nenhum.

- [ ] **Step 1: Preparar o ambiente**

```bash
export SUPERSET_URL=…  SUPERSET_USERNAME=…  SUPERSET_PASSWORD=…
cd /home/joaoegewarth/GovHub-skills/01-govhub/dashboard-superset-builder/scripts
python3 superset_client.py list-datasets --filtro gold | head -40
```
Expected: JSON com datasets reais. Se autenticar errado, pare aqui — nada
adiante funciona.

- [ ] **Step 2: Confirmar a leitura de um dashboard real**

```bash
python3 superset_client.py get-dashboard 3
```
Expected: título, charts e `position_json` do dashboard 3 — **sem** o erro de
`RoleInfo`/`PermissionView` que o MCP dava, provando que a migração resolveu o
bloqueio.

- [ ] **Step 3: Rodar o fluxo completo pelo núcleo**

Peça: "monta um dashboard no Superset a partir do dashboard 3, com outra
organização". Expected: a skill `dashboard-builder` conduz a Fase 0, invoca
`dashboard-superset-builder` para a Fase 0-conector e a Fase 1b, volta para
montar o esboço, e para no gate da Fase 3.

- [ ] **Step 4: Confirmar que o gate bloqueia**

Responda de forma vaga ("ok", "bacana"). Expected: nenhuma chamada de escrita; a
skill pede confirmação explícita.

- [ ] **Step 5: Aprovar e conferir a criação**

Aprove explicitamente. Expected: `create-chart` por componente e depois
`create-dashboard`, com os links no resumo final.

- [ ] **Step 6: Confirmar a idempotência**

Repita a Fase 4 com o mesmo esboço aprovado. Expected: as respostas trazem
`"acao": "inalterado"` — nenhum chart ou dashboard duplicado no Superset.

- [ ] **Step 7: Confirmar que o dashboard fonte ficou intocado**

Abra o dashboard 3 no Superset. Expected: título, charts e layout idênticos ao
Step 2.

- [ ] **Step 8: Registrar o resultado**

Se tudo passou, nenhum commit adicional é necessário. Se algo falhou, volte à
tarefa correspondente, corrija, e repita esta Tarefa 7.

---

## Self-Review (feito na escrita do plano)

**1. Cobertura da spec:**
- "Nova skill `dashboard-builder` (núcleo)" → Tarefa 4. ✅
- "`dashboard-superset-builder` fica só o conector" → Tarefa 5. ✅
- "`diretrizes-dashboard.md` migra" → Tarefa 4 Step 2 (`git mv`). ✅
- "`superset-schema.md` é removido" → Tarefa 5 Step 1. ✅
- "`references/superset-api.md` (novo)" → Tarefa 1. ✅
- "`scripts/superset_client.py` (novo)" → Tarefas 2 e 3. ✅
- "Manifestos e README atualizados" → Tarefa 6. ✅
- Autenticação por cookie de sessão, três passos → Tarefa 2 Step 3 (`login`) + teste em Step 1. ✅
- Os sete subcomandos da tabela da spec → Tarefas 2 (quatro de leitura) e 3 (três de escrita). ✅
- Idempotência obrigatória → Tarefa 3 (`create_chart`, `create_dashboard`, `add_chart_to_dashboard`) + três testes. ✅
- `position_json` com `meta` em todo nó → Tarefa 3, `build_position_json` + `test_position_json_tem_meta_em_todo_no`. ✅
- Paginação Rison → Tarefa 2, `rison_q` + dois testes. ✅
- Nunca usar a listagem para saber se um dashboard existe → Tarefa 2, `get_dashboard` usa o endpoint direto; `test_get_dashboard_404_devolve_none_sem_levantar`. ✅
- `--dry-run` lê e não escreve → Tarefa 3, `test_create_chart_dry_run_le_mas_nao_escreve`. ✅
- Schema de chart exemplo-guiado → Tarefa 1 (seção final de `superset-api.md`) e Tarefa 5 (Fase 4 Step 1 manda ler um chart existente). ✅
- Coreografia núcleo ↔ conector → Tarefa 4 (dois handoffs) e Tarefa 5 (Fase 0-conector devolve ao núcleo). ✅
- Verificação ponta a ponta (6 itens da spec) → Tarefa 7 Steps 2–7. ✅
- Fora de escopo (Power BI, Metabase, criar dataset) → Global Constraints + Tarefa 5 ("Fora de escopo"). ✅

**2. Placeholders:** nenhum "TBD/TODO". Os dois `<cópia literal …>` na Tarefa 4
Step 3 são instruções de extração com âncora exata e as substituições descritas
no mesmo step — o implementador lê o arquivo fonte no Step 1. Não são conteúdo
faltando.

**3. Consistência de nomes:** `rison_q`, `build_position_json`, `SupersetClient`,
`.base`, `.s`, `list_all`, `get_dataset`/`get_dashboard`/`get_chart`,
`create_chart`/`create_dashboard`/`add_chart_to_dashboard`,
`cliente_do_ambiente`, `_imprimir`, e as chaves de retorno `acao`/`slice_name`/
`slug`/`id` aparecem idênticas entre as Tarefas 2, 3 e 5 e os testes. Os sete
nomes de subcomando do CLI batem entre a Tarefa 2, a Tarefa 3, o `SKILL.md` da
Tarefa 5 e a checagem cruzada da Tarefa 5 Step 5. ✅

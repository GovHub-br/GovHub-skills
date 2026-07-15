---
name: pdf-postgres-extractor
description: Use this skill whenever the user wants to extract data from PDF files and save it to a PostgreSQL database. This includes extracting structured fields (like CNPJ, dates, values), tables (like invoice line items), and free text from PDFs — whether stored locally or in Google Drive — and inserting the extracted data into PostgreSQL tables. Trigger when the user mentions PDFs + database, invoice extraction, financial document parsing, NF extraction, or any workflow involving reading PDFs and persisting structured data to Postgres. If the user shows a PDF and mentions a database, use this skill.
---

# PDF → PostgreSQL Extractor

## O que esta skill faz

Extrai dados não estruturados de PDFs (especialmente notas fiscais e documentos financeiros) e os insere em tabelas PostgreSQL. O fluxo completo é:

1. Ler o PDF (local ou Google Drive)
2. Extrair texto, tabelas e campos estruturados
3. Mapear os dados ao schema do banco
4. Inserir no PostgreSQL

---

## Passo 1 — Obter o PDF

### Arquivo local
```python
import pdfplumber

with pdfplumber.open(caminho_do_arquivo) as pdf:
    paginas_texto = [p.extract_text() or "" for p in pdf.pages]
    paginas_tabelas = [p.extract_tables() for p in pdf.pages]
```

Se `pdfplumber` não estiver instalado:
```bash
pip install pdfplumber
```

### Google Drive (via MCP)
Use a ferramenta `mcp__claude_ai_Google_Drive__search_files` para localizar o arquivo pelo nome, depois `mcp__claude_ai_Google_Drive__download_file_content` para obter o conteúdo. Salve temporariamente em `/tmp/` antes de processar com pdfplumber.

---

## Passo 2 — Extrair o conteúdo

Combine texto e tabelas de todas as páginas:

```python
texto_completo = "\n".join(paginas_texto)

tabelas = []
for pagina in paginas_tabelas:
    for tabela in pagina:
        if tabela:
            tabelas.append(tabela)
```

Para PDFs escaneados (sem texto selecionável), use OCR:
```bash
pip install pytesseract pdf2image
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

```python
from pdf2image import convert_from_path
import pytesseract

imagens = convert_from_path(caminho_do_arquivo)
texto_completo = "\n".join(pytesseract.image_to_string(img, lang='por') for img in imagens)
```

---

## Passo 3 — Interpretar e estruturar os dados

Este é o passo inteligente: use seu entendimento do documento para identificar e extrair os campos relevantes.

### Para notas fiscais, identifique tipicamente:
- **Cabeçalho**: número da NF, data de emissão, chave de acesso, natureza da operação
- **Emitente**: CNPJ, razão social, endereço, IE
- **Destinatário**: CNPJ/CPF, razão social, endereço
- **Itens**: código, descrição, NCM, CFOP, quantidade, unidade, valor unitário, valor total
- **Totais**: valor dos produtos, frete, seguro, desconto, IPI, ICMS, valor total da NF
- **Impostos**: base de cálculo ICMS, alíquota, valor ICMS, base de cálculo IPI, valor IPI

Aplique lógica contextual — o mesmo campo pode aparecer em posições ou formatos diferentes dependendo do emissor. Quando o texto for ambíguo, prefira o valor que faz sentido matematicamente (ex: soma dos itens deve bater com o total).

### Saída esperada desta etapa

Um dicionário Python com os campos extraídos:
```python
dados = {
    "numero_nf": "000123",
    "data_emissao": "2024-03-15",
    "cnpj_emitente": "12.345.678/0001-90",
    "razao_social_emitente": "Empresa Exemplo Ltda",
    "cnpj_destinatario": "98.765.432/0001-11",
    "valor_total": 1500.00,
    "itens": [
        {"descricao": "Produto A", "quantidade": 2, "valor_unitario": 500.00, "valor_total": 1000.00},
        {"descricao": "Produto B", "quantidade": 1, "valor_unitario": 500.00, "valor_total": 500.00},
    ]
}
```

---

## Passo 4 — Conhecer o schema do banco

Antes de inserir, entenda onde os dados devem ir.

### Se o usuário informou a string de conexão:
```python
import psycopg2

conn = psycopg2.connect(dsn)  # ex: "postgresql://user:pass@host:5432/dbname"
cur = conn.cursor()

# Inspecione as tabelas relevantes
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'nome_da_tabela'
    ORDER BY ordinal_position;
""")
colunas = cur.fetchall()
```

Se `psycopg2` não estiver instalado:
```bash
pip install psycopg2-binary
```

### Se o usuário ainda não tem uma tabela

Proponha um schema baseado no que foi extraído do PDF e confirme com o usuário antes de criar. Por exemplo:

```sql
CREATE TABLE IF NOT EXISTS notas_fiscais (
    id SERIAL PRIMARY KEY,
    numero_nf VARCHAR(20),
    data_emissao DATE,
    cnpj_emitente VARCHAR(20),
    razao_social_emitente TEXT,
    cnpj_destinatario VARCHAR(20),
    valor_total NUMERIC(12,2),
    arquivo_origem TEXT,
    criado_em TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS itens_nf (
    id SERIAL PRIMARY KEY,
    nf_id INTEGER REFERENCES notas_fiscais(id),
    descricao TEXT,
    quantidade NUMERIC(10,3),
    valor_unitario NUMERIC(12,2),
    valor_total NUMERIC(12,2)
);
```

Sempre mostre o schema proposto e aguarde confirmação antes de criar ou alterar tabelas.

---

## Passo 5 — Inserir no PostgreSQL

```python
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(dsn)
cur = conn.cursor()

try:
    # Inserir cabeçalho da NF
    cur.execute("""
        INSERT INTO notas_fiscais (numero_nf, data_emissao, cnpj_emitente, razao_social_emitente, cnpj_destinatario, valor_total, arquivo_origem)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        dados["numero_nf"],
        dados["data_emissao"],
        dados["cnpj_emitente"],
        dados["razao_social_emitente"],
        dados["cnpj_destinatario"],
        dados["valor_total"],
        caminho_do_arquivo
    ))
    nf_id = cur.fetchone()[0]

    # Inserir itens
    if dados.get("itens"):
        execute_values(cur, """
            INSERT INTO itens_nf (nf_id, descricao, quantidade, valor_unitario, valor_total)
            VALUES %s
        """, [(nf_id, i["descricao"], i["quantidade"], i["valor_unitario"], i["valor_total"]) for i in dados["itens"]])

    conn.commit()
    print(f"NF {dados['numero_nf']} inserida com id={nf_id}")

except Exception as e:
    conn.rollback()
    raise e
finally:
    cur.close()
    conn.close()
```

---

## Tratamento de casos difíceis

**PDF com múltiplas NFs por arquivo**: processe página a página e insira cada uma separadamente.

**Campos ausentes ou ilegíveis**: use `None` em vez de deixar o campo em branco — evita erros de tipo. Informe o usuário quais campos não foram encontrados.

**Duplicatas**: antes de inserir, verifique se a NF já existe pelo número ou chave de acesso:
```python
cur.execute("SELECT id FROM notas_fiscais WHERE numero_nf = %s", (dados["numero_nf"],))
if cur.fetchone():
    print(f"NF {dados['numero_nf']} já existe, pulando.")
```

**Valores monetários inconsistentes**: se a soma dos itens divergir do total informado no documento, registre a divergência em um campo `observacoes` e insira assim mesmo — não descarte o registro.

---

## Fluxo resumido

```
PDF (local ou Drive)
    → pdfplumber extrai texto + tabelas
    → Claude interpreta e estrutura os campos
    → psycopg2 insere no PostgreSQL
```

Sempre confirme com o usuário o schema e a string de conexão antes de escrever no banco. Mostre um resumo do que foi extraído antes de inserir.

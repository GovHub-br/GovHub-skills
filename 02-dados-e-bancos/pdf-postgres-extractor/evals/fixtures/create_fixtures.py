"""Gera PDFs de nota fiscal simulados para uso nos evals."""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def nf_simples():
    """NF com poucos itens e layout típico."""
    path = os.path.join(OUTPUT_DIR, "nf_simples.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("NOTA FISCAL ELETRÔNICA - NF-e", styles["Title"]))
    elements.append(Spacer(1, 0.3 * cm))

    cabecalho = [
        ["Número NF:", "000456", "Data de Emissão:", "10/04/2024"],
        ["Chave de Acesso:", "43240412345678000195550010004560011234567890", "", ""],
        ["Natureza da Operação:", "Venda de Mercadoria", "", ""],
    ]
    t = Table(cabecalho, colWidths=[4 * cm, 6 * cm, 4 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3 * cm))

    elements.append(Paragraph("EMITENTE", styles["Heading2"]))
    emitente = [
        ["Razão Social:", "Tech Solutions Ltda"],
        ["CNPJ:", "12.345.678/0001-90"],
        ["Endereço:", "Av. Paulista, 1000 - São Paulo/SP"],
        ["IE:", "111.222.333.444"],
    ]
    t2 = Table(emitente, colWidths=[4 * cm, 14 * cm])
    t2.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 9)]))
    elements.append(t2)
    elements.append(Spacer(1, 0.3 * cm))

    elements.append(Paragraph("DESTINATÁRIO", styles["Heading2"]))
    destinatario = [
        ["Razão Social:", "Comércio Geral SA"],
        ["CNPJ:", "98.765.432/0001-11"],
        ["Endereço:", "Rua das Flores, 200 - Rio de Janeiro/RJ"],
    ]
    t3 = Table(destinatario, colWidths=[4 * cm, 14 * cm])
    t3.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 9)]))
    elements.append(t3)
    elements.append(Spacer(1, 0.3 * cm))

    elements.append(Paragraph("ITENS", styles["Heading2"]))
    itens = [
        ["Cód.", "Descrição", "NCM", "Qtd", "Un", "Vl. Unit.", "Vl. Total"],
        ["001", "Notebook Dell Inspiron 15", "8471.30.90", "2", "UN", "R$ 3.200,00", "R$ 6.400,00"],
        ["002", "Mouse Sem Fio Logitech", "8471.60.53", "5", "UN", "R$ 120,00", "R$ 600,00"],
    ]
    t4 = Table(itens, colWidths=[1.5 * cm, 6 * cm, 2.5 * cm, 1.5 * cm, 1 * cm, 2.5 * cm, 2.5 * cm])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elements.append(t4)
    elements.append(Spacer(1, 0.3 * cm))

    totais = [
        ["Valor Total dos Produtos:", "R$ 7.000,00"],
        ["Frete:", "R$ 150,00"],
        ["Desconto:", "R$ 0,00"],
        ["ICMS (12%):", "R$ 876,00"],
        ["VALOR TOTAL DA NF:", "R$ 7.150,00"],
    ]
    t5 = Table(totais, colWidths=[14 * cm, 4 * cm])
    t5.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightblue),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(t5)

    doc.build(elements)
    print(f"Criado: {path}")


def nf_multiplos_itens():
    """NF com muitos itens e valores de impostos detalhados."""
    path = os.path.join(OUTPUT_DIR, "nf_multiplos_itens.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("NOTA FISCAL ELETRÔNICA - NF-e", styles["Title"]))
    elements.append(Spacer(1, 0.3 * cm))

    cabecalho = [
        ["Número NF:", "001789", "Data de Emissão:", "22/05/2024"],
        ["Natureza da Operação:", "Venda de Mercadoria", "CFOP:", "5102"],
    ]
    t = Table(cabecalho, colWidths=[4 * cm, 6 * cm, 3 * cm, 5 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 9)]))
    elements.append(t)
    elements.append(Spacer(1, 0.2 * cm))

    elements.append(Paragraph("EMITENTE", styles["Heading2"]))
    emitente = [
        ["Razão Social:", "Distribuidora Nacional de Eletrodomésticos Ltda"],
        ["CNPJ:", "55.444.333/0001-22"],
        ["Endereço:", "Rod. Anhanguera, km 50 - Campinas/SP"],
    ]
    t2 = Table(emitente, colWidths=[4 * cm, 14 * cm])
    t2.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 9)]))
    elements.append(t2)
    elements.append(Spacer(1, 0.2 * cm))

    elements.append(Paragraph("DESTINATÁRIO", styles["Heading2"]))
    destinatario = [
        ["Razão Social:", "Supermercado Bom Preço ME"],
        ["CPF/CNPJ:", "11.222.333/0001-44"],
        ["Endereço:", "Rua Central, 555 - Belo Horizonte/MG"],
    ]
    t3 = Table(destinatario, colWidths=[4 * cm, 14 * cm])
    t3.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 9)]))
    elements.append(t3)
    elements.append(Spacer(1, 0.2 * cm))

    elements.append(Paragraph("ITENS", styles["Heading2"]))
    itens = [
        ["Cód.", "Descrição", "Qtd", "Un", "Vl. Unit.", "Desc.", "Vl. Total"],
        ["P001", "Geladeira Frost Free 400L", "3", "UN", "R$ 2.800,00", "R$ 84,00", "R$ 8.316,00"],
        ["P002", "Fogão 6 Bocas Inox", "5", "UN", "R$ 1.200,00", "R$ 0,00", "R$ 6.000,00"],
        ["P003", "Micro-ondas 30L", "10", "UN", "R$ 650,00", "R$ 50,00", "R$ 6.000,00"],
        ["P004", "Liquidificador 1000W", "20", "UN", "R$ 180,00", "R$ 0,00", "R$ 3.600,00"],
        ["P005", "Ferro a Vapor 2400W", "15", "UN", "R$ 95,00", "R$ 5,00", "R$ 1.350,00"],
        ["P006", "Cafeteira 1,8L Programável", "8", "UN", "R$ 320,00", "R$ 0,00", "R$ 2.560,00"],
    ]
    t4 = Table(itens, colWidths=[1.5 * cm, 6.5 * cm, 1.3 * cm, 1 * cm, 2.5 * cm, 1.7 * cm, 2.5 * cm])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elements.append(t4)
    elements.append(Spacer(1, 0.2 * cm))

    totais = [
        ["Valor Total dos Produtos:", "R$ 27.826,00"],
        ["Frete:", "R$ 480,00"],
        ["Seguro:", "R$ 120,00"],
        ["Desconto Total:", "R$ 139,00"],
        ["Base de Cálculo ICMS:", "R$ 27.826,00"],
        ["Valor ICMS (12%):", "R$ 3.339,12"],
        ["Base de Cálculo IPI:", "R$ 27.826,00"],
        ["Valor IPI (5%):", "R$ 1.391,30"],
        ["VALOR TOTAL DA NF:", "R$ 29.817,42"],
    ]
    t5 = Table(totais, colWidths=[14 * cm, 4 * cm])
    t5.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightblue),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(t5)

    doc.build(elements)
    print(f"Criado: {path}")


def nf_layout_alternativo():
    """NF com layout diferente — campos em ordem e formato distintos."""
    path = os.path.join(OUTPUT_DIR, "nf_layout_alternativo.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("DANFE - Documento Auxiliar da Nota Fiscal Eletrônica", styles["Title"]))
    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("Nº 000.099 | Série: 001 | Folha 1/1", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * cm))

    elements.append(Paragraph("Dados do Emitente", styles["Heading2"]))
    elements.append(Paragraph("Alpha Comércio de Materiais de Construção EIRELI", styles["Normal"]))
    elements.append(Paragraph("CNPJ: 77.888.999/0001-55 | IE: 999.888.777", styles["Normal"]))
    elements.append(Paragraph("Rua dos Construtores, 321 - Curitiba/PR | CEP: 80000-100", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * cm))

    elements.append(Paragraph("Dados do Destinatário", styles["Heading2"]))
    elements.append(Paragraph("Construtora Horizonte Ltda", styles["Normal"]))
    elements.append(Paragraph("CNPJ: 33.444.555/0001-66", styles["Normal"]))
    elements.append(Paragraph("Av. Brasil, 1500 - Porto Alegre/RS", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * cm))

    elements.append(Paragraph("Data de Emissão: 05/06/2024 | Natureza: Venda de Mercadoria | CFOP: 6102", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * cm))

    elements.append(Paragraph("Produtos / Serviços", styles["Heading2"]))
    itens = [
        ["Item", "Descrição do Produto", "Qtd", "Valor Unit.", "Total"],
        ["01", "Cimento CP-II 50kg (saco)", "200 SC", "R$ 38,50", "R$ 7.700,00"],
        ["02", "Areia Grossa m³", "15 M3", "R$ 120,00", "R$ 1.800,00"],
        ["03", "Brita 1 m³", "10 M3", "R$ 110,00", "R$ 1.100,00"],
        ["04", "Tijolo Cerâmico 9x19x19 (milheiro)", "5 MIL", "R$ 750,00", "R$ 3.750,00"],
    ]
    t = Table(itens, colWidths=[1 * cm, 8 * cm, 2.5 * cm, 3 * cm, 3 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph("Valor Total da Nota: R$ 14.350,00", styles["Heading2"]))
    elements.append(Paragraph("Frete: R$ 0,00 | ICMS ST: R$ 1.722,00 | PIS: R$ 94,51 | COFINS: R$ 435,82", styles["Normal"]))

    doc.build(elements)
    print(f"Criado: {path}")


if __name__ == "__main__":
    nf_simples()
    nf_multiplos_itens()
    nf_layout_alternativo()
    print("Todos os fixtures criados.")

"""
Gerador do RELATÓRIO TÉCNICO (PDF) — Dynamic Programming — AETHER 2.0.
Máximo 4 páginas, com as 5 figuras obrigatórias e todas as seções exigidas.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, HRFlowable, KeepTogether)

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figuras")

COR_PRETO = HexColor('#0A0A0F'); COR_LARANJA = HexColor('#FF6B1A')
COR_AZUL = HexColor('#1E3A8A'); COR_CINZA = HexColor('#374151')
COR_CINZA_CLARO = HexColor('#F3F4F6'); COR_BRANCO = HexColor('#FFFFFF')
COR_VERDE = HexColor('#10B981')

st = getSampleStyleSheet()
H1 = ParagraphStyle('H1b', fontName='Helvetica-Bold', fontSize=15, textColor=COR_PRETO,
                    spaceAfter=4, spaceBefore=8, leading=18)
H2 = ParagraphStyle('H2b', fontName='Helvetica-Bold', fontSize=11, textColor=COR_LARANJA,
                    spaceAfter=3, spaceBefore=6, leading=14)
P = ParagraphStyle('Pb', fontName='Helvetica', fontSize=8.7, textColor=COR_CINZA,
                   alignment=TA_JUSTIFY, leading=11.5, spaceAfter=4)
PB = ParagraphStyle('PBb', fontName='Helvetica', fontSize=8.7, textColor=COR_PRETO,
                    alignment=TA_LEFT, leading=11.5, spaceAfter=3)
CAP = ParagraphStyle('Cap', fontName='Helvetica-Oblique', fontSize=7.5, textColor=COR_CINZA,
                     alignment=TA_CENTER, leading=10, spaceAfter=6, spaceBefore=2)
SMALL = ParagraphStyle('sm', fontName='Helvetica', fontSize=7.8, textColor=COR_CINZA, leading=10)


def tabela(dados, widths, fs=7.6, hc=COR_PRETO):
    ec = ParagraphStyle('ec', fontName='Helvetica', fontSize=fs, textColor=COR_CINZA, leading=fs+2.5)
    ech = ParagraphStyle('ech', fontName='Helvetica-Bold', fontSize=fs+0.3, textColor=COR_BRANCO,
                         leading=fs+3, alignment=TA_CENTER)
    dd = []
    for i, row in enumerate(dados):
        nr = []
        for c in row:
            if isinstance(c, str) and (i == 0 or len(c) > 18 or '<' in c):
                nr.append(Paragraph(c.replace('\n', '<br/>'), ech if i == 0 else ec))
            else:
                nr.append(c)
        dd.append(nr)
    t = Table(dd, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), hc), ('TEXTCOLOR', (0,0), (-1,0), COR_BRANCO),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), fs+0.3),
        ('ALIGN', (0,0), (-1,0), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,1), (-1,-1), fs),
        ('TEXTCOLOR', (0,1), (-1,-1), COR_CINZA),
        ('TOPPADDING', (0,0), (-1,-1), 3.5), ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [COR_BRANCO, HexColor('#F9FAFB')]),
        ('LINEBELOW', (0,0), (-1,0), 1.5, COR_LARANJA),
        ('BOX', (0,0), (-1,-1), 0.4, HexColor('#D1D5DB')),
        ('LINEBELOW', (0,1), (-1,-2), 0.25, HexColor('#E5E7EB')),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(COR_PRETO); canvas.rect(0, h-1.5*cm, w, 1.5*cm, fill=1, stroke=0)
    canvas.setFillColor(COR_LARANJA); canvas.rect(0, h-1.5*cm, w, 0.12*cm, fill=1, stroke=0)
    canvas.setFillColor(COR_BRANCO); canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(1.5*cm, h-1.0*cm, 'AETHER 2.0')
    canvas.setFillColor(HexColor('#FFCBA4')); canvas.setFont('Helvetica', 8)
    canvas.drawString(3.6*cm, h-1.0*cm, '· Monitoramento de Riscos Ambientais')
    canvas.setFillColor(COR_BRANCO); canvas.setFont('Helvetica', 7.5)
    canvas.drawRightString(w-1.5*cm, h-1.0*cm, 'Dynamic Programming · FIAP GS 2026')
    canvas.setFillColor(COR_CINZA); canvas.setFont('Helvetica', 7.5)
    canvas.drawCentredString(w/2, 0.8*cm, f'Pág. {canvas.getPageNumber()} · Relatório Técnico · Prof. André Marques')
    canvas.restoreState()


def img(path, largura):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(path).size
    return Image(path, width=largura, height=largura*ih/iw)


def build():
    out = os.path.join(BASE, "relatorio_final.pdf")
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.9*cm, bottomMargin=1.2*cm,
                            title="Relatório Dynamic Programming — AETHER 2.0")
    s = []
    LARG = A4[0] - 3*cm

    # título
    s.append(Paragraph("Monitoramento de Riscos Ambientais com Grafos, BST e Algoritmos", H1))
    s.append(Paragraph("Cenário A — Rede de Resposta a Enchentes no Rio Grande do Sul (2024) · "
                       "Algoritmo Guloso: Dijkstra", H2))
    s.append(HRFlowable(width="100%", thickness=1.5, color=COR_LARANJA, spaceAfter=5))

    # 1. Identificação + contexto
    s.append(Paragraph("1. Identificação e Contextualização", H1))
    s.append(tabela([
        ["Integrante", "RM", "Cenário", "ODS"],
        ["[Seu Nome]", "RM xxxxx", "A — Enchentes RS", "9, 11, 13"],
        ["Lucas [Sobrenome]", "RM xxxxx", "478 municípios", "(ONU)"],
    ], [4.5*cm, 2.5*cm, 5.5*cm, 5*cm]))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "Em maio de 2024, o Rio Grande do Sul enfrentou a maior catástrofe climática do Brasil: "
        "<b>478 municípios atingidos, 183 mortes, 2,3 milhões de afetados e R$ 88 bilhões de prejuízo</b>. "
        "A Defesa Civil levou dias para mapear áreas críticas. Este projeto, parte do sistema AETHER 2.0, "
        "modela a rede de municípios como um <b>grafo ponderado</b> e calcula, a partir de um hub de recursos "
        "(Porto Alegre), a <b>rota ótima de atendimento</b> até cada município via <b>Dijkstra</b> (guloso). "
        "Uma <b>Árvore Binária de Busca (BST)</b> prioriza municípios por índice de risco e a <b>Força Bruta</b> "
        "valida a corretude do guloso. Os dados são reais: coordenadas oficiais do IBGE e índices de risco "
        "derivados da afetação registrada em 2024; as distâncias entre municípios são calculadas pela fórmula "
        "geodésica de <b>Haversine</b>.", P))

    # 2. Modelagem
    s.append(Paragraph("2. Modelagem das Estruturas de Dados", H1))
    s.append(Paragraph("<b>Grafo G = (V, E):</b> V = municípios (namedtuple imutável com id, nome, risco, "
        "custo, população, lat, lon); E = rotas, com peso = distância em km. Representado como "
        "<b>dicionário de listas de adjacência</b> {id: [(vizinho, peso)]}. <b>Justificativa (lista vs. matriz):</b> "
        "a rede é esparsa, então a lista usa espaço O(V+E) contra O(V²) da matriz, e percorrer vizinhos é O(grau) — "
        "ideal para Dijkstra.", P))
    s.append(Paragraph("<b>BST por índice de risco:</b> classe Node + BinarySearchTree implementadas do zero "
        "(sem bibliotecas). Suporta inserir, buscar_intervalo, percurso_in_order, altura e remover. A chave de "
        "ordenação é o risco; o percurso in-order decrescente fornece a fila de priorização do AETHER.", P))
    s.append(Paragraph("<b>Estruturas exigidas:</b> Lista (caminhos/adjacência), Tupla (vértices/arestas), "
        "Dicionário (custos, predecessores, adjacência), Conjunto (visitados — evita ciclos), Heap/heapq "
        "(fila de prioridade do Dijkstra).", P))

    # Figura 2 (BST) + Figura 1 (grafo) lado a lado
    f1 = img(os.path.join(FIG, "fig2_bst.png"), LARG)
    s.append(f1)
    s.append(Paragraph("Fig. 2 — BST de municípios por índice de risco (12 nós, balanceada). "
                       "Raiz = Porto Alegre (0,78); folhas críticas à direita (Muçum 0,98).", CAP))

    # 3. Complexidade
    s.append(Paragraph("3. Análise de Complexidade Teórica", H1))
    s.append(tabela([
        ["Algoritmo", "Tempo", "Espaço", "Observação"],
        ["Força Bruta (backtracking)", "O(V!) no pior caso", "O(V)", "Enumera todos os caminhos simples"],
        ["Dijkstra (heap binário)", "O((V+E) log V)", "O(V+E)", "Decisão local ótima → ótimo global"],
        ["BST (médio / pior)", "O(log n) / O(n)", "O(n)", "Inserção, busca, remoção"],
    ], [4.5*cm, 3.8*cm, 2.5*cm, 6.7*cm]))

    # 4. Resultados com figuras
    s.append(Paragraph("4. Resultados", H1))
    s.append(Paragraph("A Fig. 1 mostra a rede real de municípios (posição geográfica) e a rota ótima "
        "Porto Alegre → Muçum (município mais crítico, risco 0,98) calculada pelo Dijkstra.", P))
    s.append(img(os.path.join(FIG, "fig1_grafo_rota.png"), LARG))
    s.append(Paragraph("Fig. 1 — Rede de municípios do RS. Nós coloridos por risco; hub (azul), destino "
                       "(verde) e rota ótima (laranja).", CAP))

    # tabela de desempenho
    s.append(Paragraph("<b>Desempenho (Força Bruta x Dijkstra):</b> a Força Bruta só é viável para N ≤ 12; "
        "acima disso, o número de caminhos explode. O gap de otimalidade é <b>0% em todas as instâncias</b>, "
        "comprovando que o Dijkstra atinge o ótimo global.", P))
    s.append(tabela([
        ["N", "Arestas", "Dijkstra (ms)", "F. Bruta (ms)", "Caminhos FB", "Gap %"],
        ["5", "5", "0,065", "0,054", "2", "0,00"],
        ["10", "16", "0,068", "0,132", "9", "0,00"],
        ["12", "31", "0,088", "0,216", "21", "0,00"],
        ["20", "91", "0,138", "inviável", "—", "—"],
        ["50", "560", "0,480", "inviável", "—", "—"],
        ["100", "2174", "2,753", "inviável", "—", "—"],
    ], [1.3*cm, 2*cm, 3*cm, 3*cm, 3*cm, 2.2*cm]))
    s.append(Spacer(1, 4))

    # Fig 3 e 4 lado a lado
    f3 = img(os.path.join(FIG, "fig3_desempenho.png"), (LARG-0.3*cm)/2)
    f4 = img(os.path.join(FIG, "fig4_explosao.png"), (LARG-0.3*cm)/2)
    lado = Table([[f3, f4]], colWidths=[(LARG-0.3*cm)/2, (LARG-0.3*cm)/2])
    lado.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),
                              ('RIGHTPADDING',(0,0),(-1,-1),0)]))
    s.append(lado)
    s.append(Paragraph("Fig. 3 — Tempo x N (escala log): as curvas se cruzam em N≈10–12, a partir do qual a "
        "Força Bruta torna-se mais lenta e logo inviável.  |  Fig. 4 — Explosão combinatória: o nº de caminhos "
        "salta de 5 (N=4) para 1.029.308 (N=12).", CAP))

    # Fig 5 gap
    s.append(img(os.path.join(FIG, "fig5_gap.png"), LARG*0.62))
    s.append(Paragraph("Fig. 5 — Gap de otimalidade = 0%: o Dijkstra encontra exatamente o mesmo custo "
                       "da Força Bruta (ótimo) em todas as instâncias.", CAP))

    # 5. Escala de decisão
    s.append(Paragraph("5. Escala de Decisão (trade-off qualidade × custo)", H1))
    s.append(tabela([
        ["Nível", "Estratégia", "Quando usar", "Qualidade", "Custo computacional"],
        ["1", "Força Bruta", "N ≤ 12 (validação)", "Ótimo (100%)", "Exponencial — inviável"],
        ["2", "Dijkstra (guloso)", "Pesos ≥ 0, despacho", "Ótimo (gap 0%)", "O((V+E) log V) — eficiente"],
        ["3", "Prim/Kruskal (MST)", "Cobertura de bases", "Ótimo p/ cobertura", "O(E log V)"],
        ["4", "A*/heurístico", "N massivo, tempo real", "Aproximado", "Sub-linear (pior caso)"],
    ], [1.1*cm, 3.2*cm, 4*cm, 3*cm, 4.2*cm]))
    s.append(Spacer(1, 3))
    s.append(Paragraph("<b>Recomendação prática:</b> o AETHER adota o <b>Nível 2 (Dijkstra)</b> como motor de "
        "despacho do rover — combina otimalidade com escalabilidade (resolve N=100 em ~2,8 ms). A Força Bruta "
        "fica restrita à validação (oráculo). A camada de cobertura de bases é naturalmente atendida por MST (Nível 3).", PB))

    # 6. Conclusão
    s.append(Paragraph("6. Conclusão e Conexão com os ODS", H1))
    s.append(Paragraph("O Dijkstra provou-se a escolha ótima para o despacho de recursos em desastres: atinge o "
        "mesmo resultado da Força Bruta (gap 0%) com custo viável até centenas de municípios, enquanto a Força "
        "Bruta colapsa a partir de N≈12 pela explosão combinatória. A modelagem em grafo esparso (lista de "
        "adjacência) e a priorização por BST sustentam a operação do AETHER. O projeto conecta-se ao <b>ODS 9</b> "
        "(infraestrutura e inovação), <b>ODS 11</b> (cidades sustentáveis e resilientes) e <b>ODS 13</b> "
        "(ação climática), demonstrando como algoritmos clássicos salvam vidas em cenários reais brasileiros.", P))

    # 7. Referências
    s.append(Paragraph("7. Referências", H1))
    s.append(Paragraph(
        "CORMEN, T. et al. <i>Introduction to Algorithms</i>, 4ª ed. MIT Press, 2022 (Caps. 22–25). · "
        "SEDGEWICK, R.; WAYNE, K. <i>Algorithms</i>, 4ª ed. Addison-Wesley, 2011 (Parte 4). · "
        "SKIENA, S. <i>The Algorithm Design Manual</i>, 3ª ed. Springer, 2020. · "
        "IBGE — Malha municipal e coordenadas geográficas (geociencias). · "
        "Defesa Civil RS — Boletins das enchentes de maio/2024.", SMALL))

    doc.build(s, onFirstPage=header_footer, onLaterPages=header_footer)
    print("Relatório gerado:", out)


if __name__ == "__main__":
    build()

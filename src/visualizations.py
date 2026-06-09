"""
visualizations.py
=================
Geração das FIGURAS OBRIGATÓRIAS do relatório AETHER 2.0:

    Fig 1. Grafo de municípios do RS com a rota ótima (Dijkstra) destacada
    Fig 2. Representação visual da BST (10-15 nós) com índices de risco
    Fig 3. Gráfico comparativo de desempenho: tempo x N (Força Bruta x Dijkstra)
    Fig 4. Gráfico da explosão combinatória (nº de caminhos x N)
    Fig 5. Gráfico de gap de otimalidade (FB x Guloso) em função de N

Usa networkx + matplotlib apenas para VISUALIZAÇÃO (a lógica dos algoritmos
é implementada do zero nos outros módulos, conforme exige o enunciado).
"""

from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")  # backend sem display
import matplotlib.pyplot as plt
import networkx as nx

from .data_structures import (carregar_municipios, construir_grafo,
                              construir_bst, BinarySearchTree, Node)
from .greedy import dijkstra, reconstruir_caminho
from .performance_monitor import comparar_algoritmos, crescimento_caminhos

# Paleta AETHER
COR_LARANJA = "#FF6B1A"
COR_AZUL = "#1E3A8A"
COR_CINZA = "#9CA3AF"
COR_VERMELHO = "#DC2626"
COR_VERDE = "#10B981"


def _figdir(base: str) -> str:
    d = os.path.join(base, "report", "figuras")
    os.makedirs(d, exist_ok=True)
    return d


# ---------- FIGURA 1: grafo com rota ótima ----------
def fig_grafo_rota(base: str, hub_id: int, destino_id: int):
    munis = carregar_municipios(os.path.join(base, "data", "raw", "municipios_rs_2024.csv"))
    g = construir_grafo(munis)

    G = nx.Graph()
    pos = {}
    for mid, m in g.municipios.items():
        G.add_node(mid)
        pos[mid] = (m.longitude, m.latitude)  # posição geográfica real
    for u in g.vertices():
        for v, peso in g.vizinhos(u):
            if u < v:
                G.add_edge(u, v, weight=peso)

    _dist, pred, _ = dijkstra(g, hub_id)
    rota = reconstruir_caminho(pred, hub_id, destino_id)
    arestas_rota = list(zip(rota, rota[1:]))

    fig, ax = plt.subplots(figsize=(11, 9))
    # cor dos nós por risco
    riscos = [g.municipios[n].indice_risco for n in G.nodes()]
    nx.draw_networkx_edges(G, pos, edge_color=COR_CINZA, width=0.6, alpha=0.4, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=arestas_rota, edge_color=COR_LARANJA,
                           width=3.0, ax=ax)
    nodes = nx.draw_networkx_nodes(G, pos, node_color=riscos, cmap="OrRd",
                                   node_size=320, ax=ax, edgecolors="black", linewidths=0.5)
    # hub e destino destacados
    nx.draw_networkx_nodes(G, pos, nodelist=[hub_id], node_color=COR_AZUL,
                           node_size=520, ax=ax, edgecolors="white", linewidths=1.5)
    nx.draw_networkx_nodes(G, pos, nodelist=[destino_id], node_color=COR_VERDE,
                           node_size=520, ax=ax, edgecolors="white", linewidths=1.5)
    labels = {n: g.municipios[n].nome for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=6.2, ax=ax)

    cbar = fig.colorbar(nodes, ax=ax, shrink=0.7)
    cbar.set_label("Índice de Risco", fontsize=10)
    nome_hub = g.municipios[hub_id].nome
    nome_dest = g.municipios[destino_id].nome
    ax.set_title(f"Fig. 1 — Rede de municípios do RS (2024)\n"
                 f"Rota ótima Dijkstra: {nome_hub} (azul) → {nome_dest} (verde), "
                 f"destacada em laranja", fontsize=12, fontweight="bold")
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    caminho = os.path.join(_figdir(base), "fig1_grafo_rota.png")
    plt.savefig(caminho, dpi=140, bbox_inches="tight")
    plt.close()
    return caminho


# ---------- FIGURA 2: BST visual ----------
def fig_bst(base: str, n_nos: int = 12):
    munis = carregar_municipios(os.path.join(base, "data", "raw", "municipios_rs_2024.csv"))
    bst = construir_bst(munis[:n_nos])

    G = nx.DiGraph()
    pos = {}
    rotulos = {}

    def percorre(node: Node, x: float, y: float, dx: float):
        if node is None:
            return
        nid = node.municipio.id_ibge
        G.add_node(nid)
        pos[nid] = (x, y)
        rotulos[nid] = f"{node.municipio.nome[:10]}\n{node.municipio.indice_risco:.2f}"
        if node.esquerda:
            G.add_edge(nid, node.esquerda.municipio.id_ibge)
            percorre(node.esquerda, x - dx, y - 1, dx / 1.8)
        if node.direita:
            G.add_edge(nid, node.direita.municipio.id_ibge)
            percorre(node.direita, x + dx, y - 1, dx / 1.8)

    percorre(bst.raiz, 0, 0, 8)

    fig, ax = plt.subplots(figsize=(13, 7))
    nx.draw_networkx_edges(G, pos, edge_color=COR_AZUL, width=1.5, arrows=False, ax=ax)
    nx.draw_networkx_nodes(G, pos, node_color=COR_LARANJA, node_size=2100,
                           edgecolors="black", linewidths=1, ax=ax)
    nx.draw_networkx_labels(G, pos, rotulos, font_size=7, font_weight="bold", ax=ax)
    ax.set_title(f"Fig. 2 — Árvore Binária de Busca (BST) por índice de risco\n"
                 f"{len(bst)} municípios · altura={bst.altura()} · "
                 f"balanceada={'sim' if bst.esta_balanceada() else 'não'}",
                 fontsize=12, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    caminho = os.path.join(_figdir(base), "fig2_bst.png")
    plt.savefig(caminho, dpi=140, bbox_inches="tight")
    plt.close()
    return caminho


# ---------- FIGURA 3: tempo x N (FB x Dijkstra) ----------
def fig_desempenho(base: str, registros):
    ns = [r["n"] for r in registros]
    dij = [r["dijkstra_ms"] for r in registros]
    fb_ns = [r["n"] for r in registros if r["fb_ms"] is not None]
    fb = [r["fb_ms"] for r in registros if r["fb_ms"] is not None]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ns, dij, "o-", color=COR_AZUL, linewidth=2, markersize=7, label="Dijkstra (Guloso)")
    ax.plot(fb_ns, fb, "s-", color=COR_VERMELHO, linewidth=2, markersize=7, label="Força Bruta")
    ax.set_xlabel("N (número de municípios)", fontsize=11)
    ax.set_ylabel("Tempo de execução (ms)", fontsize=11)
    ax.set_title("Fig. 3 — Desempenho: tempo de execução x N\n"
                 "Força Bruta x Dijkstra (escala log)", fontsize=12, fontweight="bold")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3, which="both")
    ax.legend(fontsize=11)
    plt.tight_layout()
    caminho = os.path.join(_figdir(base), "fig3_desempenho.png")
    plt.savefig(caminho, dpi=140, bbox_inches="tight")
    plt.close()
    return caminho


# ---------- FIGURA 4: explosão combinatória ----------
def fig_explosao(base: str, pontos):
    ns = [p[0] for p in pontos]
    caminhos = [p[1] for p in pontos]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ns, caminhos, "o-", color=COR_LARANJA, linewidth=2.5, markersize=8)
    for x, y in pontos:
        ax.annotate(f"{y:,}", (x, y), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=8)
    ax.set_xlabel("N (número de municípios)", fontsize=11)
    ax.set_ylabel("Nº de caminhos simples enumerados", fontsize=11)
    ax.set_title("Fig. 4 — Explosão Combinatória da Força Bruta\n"
                 "Crescimento do nº de caminhos x N (escala log)",
                 fontsize=12, fontweight="bold")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3, which="both")
    plt.tight_layout()
    caminho = os.path.join(_figdir(base), "fig4_explosao.png")
    plt.savefig(caminho, dpi=140, bbox_inches="tight")
    plt.close()
    return caminho


# ---------- FIGURA 5: gap de otimalidade ----------
def fig_gap(base: str, registros):
    dados = [(r["n"], r["gap_otimalidade_pct"]) for r in registros
             if r["gap_otimalidade_pct"] is not None]
    ns = [d[0] for d in dados]
    gaps = [d[1] for d in dados]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(ns, gaps, color=COR_VERDE, width=1.2, edgecolor="black", linewidth=0.5)
    ax.axhline(y=0, color=COR_VERMELHO, linestyle="--", linewidth=1)
    ax.set_xlabel("N (número de municípios)", fontsize=11)
    ax.set_ylabel("Gap de otimalidade (%)", fontsize=11)
    ax.set_title("Fig. 5 — Gap de Otimalidade: Dijkstra x Força Bruta (ótimo)\n"
                 "Gap = 0% comprova que Dijkstra atinge o ótimo global",
                 fontsize=12, fontweight="bold")
    ax.set_ylim(-1, max(max(gaps), 1) + 1)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    caminho = os.path.join(_figdir(base), "fig5_gap.png")
    plt.savefig(caminho, dpi=140, bbox_inches="tight")
    plt.close()
    return caminho


def gerar_todas(base: str):
    """Gera todas as figuras obrigatórias e retorna os caminhos."""
    print("Gerando figuras obrigatórias...")
    munis = carregar_municipios(os.path.join(base, "data", "raw", "municipios_rs_2024.csv"))
    hub = 4314902  # Porto Alegre
    destino = 4313904  # Muçum (município mais crítico)

    f1 = fig_grafo_rota(base, hub, destino)
    print(f"  [OK] {f1}")
    f2 = fig_bst(base)
    print(f"  [OK] {f2}")

    registros = comparar_algoritmos()
    f3 = fig_desempenho(base, registros)
    print(f"  [OK] {f3}")

    pontos = crescimento_caminhos()
    f4 = fig_explosao(base, pontos)
    print(f"  [OK] {f4}")

    f5 = fig_gap(base, registros)
    print(f"  [OK] {f5}")
    return [f1, f2, f3, f4, f5]


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gerar_todas(base)

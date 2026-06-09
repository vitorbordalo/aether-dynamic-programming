"""
greedy.py
=========
Algoritmo GULOSO (Greedy) do sistema AETHER 2.0: DIJKSTRA — caminho mínimo
de fonte única.

Aplicação no AETHER: a partir de um HUB de recursos (ex.: Porto Alegre),
calcula a ROTA de menor custo (distância em km) até cada município afetado.
É exatamente a decisão de despacho do AETHER-ROVER: "qual o caminho mais
rápido da base até a cidade isolada?".

Por que Dijkstra é guloso:
    A cada passo, ele toma a decisão LOCALMENTE ótima — extrai do heap o
    vértice de menor custo acumulado ainda não finalizado — e nunca a revê.
    Para grafos com pesos não-negativos (distâncias são sempre >= 0), essa
    sequência de escolhas locais ótimas leva ao ótimo global (prova clássica
    de corretude de Dijkstra).

Estruturas usadas (conforme exigência do enunciado):
    - HEAP (heapq) como fila de prioridade -> extrair o mínimo em O(log V)
    - DICIONÁRIO para custos acumulados e predecessores
    - CONJUNTO (set) para vértices finalizados
"""

from __future__ import annotations
import heapq
from .data_structures import Grafo


def dijkstra(grafo: Grafo, origem: int) -> tuple[dict[int, float], dict[int, int], dict[str, int]]:
    """
    Executa Dijkstra a partir de 'origem'.

    Retorna:
        distancias   : dict {id_municipio -> custo mínimo acumulado desde a origem}
        predecessores: dict {id_municipio -> município anterior na rota ótima}
        metricas     : dict com contadores de operações elementares

    Complexidade: O((V + E) log V) usando heap binário.
    """
    # DICIONÁRIO de custos: começa com infinito para todos
    distancias: dict[int, float] = {v: float("inf") for v in grafo.vertices()}
    predecessores: dict[int, int] = {v: None for v in grafo.vertices()}
    finalizados: set[int] = set()           # CONJUNTO de vértices já fechados

    distancias[origem] = 0.0
    # HEAP (fila de prioridade): tuplas (custo_acumulado, id_municipio)
    heap: list[tuple[float, int]] = [(0.0, origem)]

    # Métricas de desempenho (operações elementares)
    metricas = {"arestas_relaxadas": 0, "insercoes_heap": 1, "extracoes_heap": 0}

    while heap:
        custo_atual, u = heapq.heappop(heap)   # decisão gulosa: menor custo local
        metricas["extracoes_heap"] += 1

        # Se já finalizamos este vértice, ignora entrada obsoleta do heap
        if u in finalizados:
            continue
        finalizados.add(u)

        # Relaxamento das arestas vizinhas
        for vizinho, peso in grafo.vizinhos(u):
            if vizinho in finalizados:
                continue
            novo_custo = custo_atual + peso
            metricas["arestas_relaxadas"] += 1
            if novo_custo < distancias[vizinho]:
                distancias[vizinho] = novo_custo
                predecessores[vizinho] = u
                heapq.heappush(heap, (novo_custo, vizinho))
                metricas["insercoes_heap"] += 1

    return distancias, predecessores, metricas


def reconstruir_caminho(predecessores: dict[int, int], origem: int, destino: int) -> list[int]:
    """
    Reconstrói o caminho ótimo da origem até o destino a partir do dicionário
    de predecessores. Retorna a lista de ids na ordem origem -> destino.
    """
    caminho: list[int] = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        if atual == origem:
            break
        atual = predecessores.get(atual)
    caminho.reverse()
    # valida que o caminho realmente começa na origem (senão é inalcançável)
    if not caminho or caminho[0] != origem:
        return []
    return caminho


def rotas_a_partir_do_hub(grafo: Grafo, hub: int) -> dict[int, dict]:
    """
    Calcula, para cada município, a rota ótima e o custo a partir do hub.
    Saída pronta para alimentar o relatório e o dashboard do AETHER.
    """
    distancias, predecessores, _ = dijkstra(grafo, hub)
    resultado: dict[int, dict] = {}
    for destino in grafo.vertices():
        if destino == hub:
            continue
        caminho = reconstruir_caminho(predecessores, hub, destino)
        resultado[destino] = {
            "custo_km": round(distancias[destino], 2),
            "caminho_ids": caminho,
            "caminho_nomes": [grafo.municipios[i].nome for i in caminho],
            "num_saltos": max(len(caminho) - 1, 0),
        }
    return resultado


# ------------------------------------------------------------------
# NOTA DE ARQUITETURA (visão sistêmica para o relatório):
# Embora a camada de DESPACHO use Dijkstra (caminho mínimo de fonte única),
# a camada de COBERTURA do AETHER (posicionar bases de recursos cobrindo todos
# os municípios com custo mínimo) é naturalmente modelada por uma Árvore
# Geradora Mínima (MST via Prim/Kruskal). O grafo e as estruturas aqui
# implementados suportam ambas as abordagens; nesta entrega aprofundamos
# Dijkstra por ser o que melhor representa a operação de resgate do rover.
# ------------------------------------------------------------------


if __name__ == "__main__":
    import os
    from .data_structures import carregar_municipios, construir_grafo

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, "data", "raw", "municipios_rs_2024.csv")
    munis = carregar_municipios(csv_path)
    g = construir_grafo(munis)

    HUB = 4314902  # Porto Alegre = hub de recursos
    distancias, predecessores, metricas = dijkstra(g, HUB)

    print(f"Dijkstra a partir de Porto Alegre (hub):")
    print(f"  Operações: {metricas}\n")
    print("  Rotas ótimas (5 municípios mais críticos):")
    rotas = rotas_a_partir_do_hub(g, HUB)
    criticos = sorted(munis, key=lambda m: m.indice_risco, reverse=True)[:5]
    for m in criticos:
        if m.id_ibge == HUB:
            continue
        r = rotas[m.id_ibge]
        print(f"    {m.nome:22s} risco={m.indice_risco:.2f}  "
              f"custo={r['custo_km']:6.1f} km  saltos={r['num_saltos']}")
        print(f"       rota: {' -> '.join(r['caminho_nomes'])}")

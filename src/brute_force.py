"""
brute_force.py
==============
Algoritmo de FORÇA BRUTA do sistema AETHER 2.0 — busca exaustiva de caminho
mínimo via enumeração completa com BACKTRACKING.

Papel no sistema:
    Serve como ORÁCULO DE VALIDAÇÃO. Para instâncias pequenas (N <= 12), enumera
    TODOS os caminhos simples possíveis entre origem e destino e identifica o de
    menor custo. O resultado deve coincidir com o do Dijkstra (que é ótimo), o
    que valida empiricamente a corretude do guloso.

    Também evidencia a EXPLOSÃO COMBINATÓRIA: o número de caminhos cresce de
    forma fatorial/exponencial com N, tornando a força bruta inviável para
    instâncias reais — justificando o uso do algoritmo guloso.

Estruturas usadas:
    - LISTA para o caminho atual (pilha de recursão)
    - CONJUNTO (set) para marcar vértices visitados e evitar ciclos
"""

from __future__ import annotations
from .data_structures import Grafo


def forca_bruta_caminho_minimo(grafo: Grafo, origem: int, destino: int) -> dict:
    """
    Enumera TODOS os caminhos simples de origem a destino usando recursão com
    backtracking, e retorna o de menor custo.

    Retorna dicionário com:
        melhor_caminho : list[int]   (ids na ordem origem->destino)
        melhor_custo   : float
        metricas       : contadores (chamadas recursivas, caminhos avaliados)
    """
    melhor = {"custo": float("inf"), "caminho": []}
    metricas = {"chamadas_recursivas": 0, "caminhos_avaliados": 0}

    visitados: set[int] = set()       # CONJUNTO p/ evitar ciclos
    caminho_atual: list[int] = []     # LISTA = caminho em construção

    def backtrack(u: int, custo_acumulado: float) -> None:
        metricas["chamadas_recursivas"] += 1
        visitados.add(u)
        caminho_atual.append(u)

        if u == destino:
            metricas["caminhos_avaliados"] += 1
            if custo_acumulado < melhor["custo"]:
                melhor["custo"] = custo_acumulado
                melhor["caminho"] = list(caminho_atual)
        else:
            # Poda: só continua se ainda houver chance de melhorar o melhor atual
            if custo_acumulado < melhor["custo"]:
                for vizinho, peso in grafo.vizinhos(u):
                    if vizinho not in visitados:
                        backtrack(vizinho, custo_acumulado + peso)

        # backtracking: desfaz a escolha
        caminho_atual.pop()
        visitados.remove(u)

    backtrack(origem, 0.0)

    return {
        "melhor_caminho": melhor["caminho"],
        "melhor_custo": round(melhor["custo"], 2) if melhor["custo"] != float("inf") else None,
        "metricas": metricas,
    }


def contar_caminhos(grafo: Grafo, origem: int, destino: int, limite: int = 2_000_000) -> int:
    """
    Conta o número total de caminhos simples entre origem e destino.
    Usado para evidenciar a explosão combinatória (curva nº de caminhos vs N).
    'limite' interrompe a contagem para evitar travamento em N grande.
    """
    total = 0
    visitados: set[int] = set()

    def conta(u: int) -> None:
        nonlocal total
        if total >= limite:
            return
        visitados.add(u)
        if u == destino:
            total += 1
        else:
            for vizinho, _peso in grafo.vizinhos(u):
                if vizinho not in visitados:
                    conta(vizinho)
        visitados.remove(u)

    conta(origem)
    return total


if __name__ == "__main__":
    import os
    from .data_structures import carregar_municipios, construir_grafo
    from .greedy import dijkstra, reconstruir_caminho

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, "data", "raw", "municipios_rs_2024.csv")
    munis = carregar_municipios(csv_path)

    # Subgrafo pequeno (primeiros 10 municípios) para a força bruta
    pequeno = munis[:10]
    g = construir_grafo(pequeno, raio_conexao_km=120.0)
    origem = pequeno[0].id_ibge
    destino = pequeno[-1].id_ibge

    # Força bruta
    fb = forca_bruta_caminho_minimo(g, origem, destino)
    # Dijkstra para comparação
    dist, pred, _ = dijkstra(g, origem)
    cam_dijkstra = reconstruir_caminho(pred, origem, destino)

    print(f"Origem:  {g.municipios[origem].nome}")
    print(f"Destino: {g.municipios[destino].nome}\n")
    print(f"FORÇA BRUTA  -> custo={fb['melhor_custo']} km")
    print(f"   caminho: {[g.municipios[i].nome for i in fb['melhor_caminho']]}")
    print(f"   métricas: {fb['metricas']}\n")
    print(f"DIJKSTRA     -> custo={round(dist[destino],2)} km")
    print(f"   caminho: {[g.municipios[i].nome for i in cam_dijkstra]}\n")
    coincidem = abs(fb['melhor_custo'] - dist[destino]) < 0.01
    print(f"Resultados coincidem? {coincidem}  (valida a corretude do guloso)")

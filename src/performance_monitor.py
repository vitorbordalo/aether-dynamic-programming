"""
performance_monitor.py
======================
Monitoramento de desempenho dos algoritmos do AETHER 2.0.

Para cada algoritmo e tamanho de instância (N = 5, 8, 10, 12, 20, 50, 100),
mede e registra:
    - Tempo de execução (ms) via time.perf_counter()
    - Memória alocada (MB) via tracemalloc
    - Número de operações elementares (contadores internos dos algoritmos)
    - Escalabilidade empírica (curva N vs tempo)

Demonstra empiricamente a partir de qual N a Força Bruta se torna inviável e
identifica o cruzamento das curvas Força Bruta x Guloso.
"""

from __future__ import annotations
import time
import tracemalloc
import math
import random
from .data_structures import Grafo, Municipio, construir_grafo, haversine_km
from .greedy import dijkstra, reconstruir_caminho
from .brute_force import forca_bruta_caminho_minimo, contar_caminhos


def _medir(funcao, *args, **kwargs):
    """Executa 'funcao' medindo tempo (ms) e pico de memória (MB)."""
    tracemalloc.start()
    inicio = time.perf_counter()
    resultado = funcao(*args, **kwargs)
    fim = time.perf_counter()
    _atual, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    tempo_ms = (fim - inicio) * 1000.0
    memoria_mb = pico / (1024 * 1024)
    return resultado, tempo_ms, memoria_mb


def gerar_instancia(n: int, semente: int = 42, densidade: float = 0.45) -> Grafo:
    """
    Gera uma instância de grafo com N municípios sintéticos porém realistas
    (coordenadas dentro da bounding box do RS), para testes de escalabilidade.
    Reprodutível via semente fixa.

    'densidade' controla a probabilidade de existir aresta entre dois municípios
    (além da conexão geográfica), tornando o grafo mais ou menos denso. Grafos
    densos evidenciam melhor a explosão combinatória da força bruta.
    """
    rnd = random.Random(semente + n)
    # bounding box aproximada do RS
    lat_min, lat_max = -33.7, -27.1
    lon_min, lon_max = -57.6, -49.7
    municipios = []
    for i in range(n):
        municipios.append(Municipio(
            id_ibge=900000 + i,
            nome=f"Municipio_{i:03d}",
            indice_risco=round(rnd.uniform(0.3, 0.99), 3),
            custo_atendimento=round(rnd.uniform(400, 1800), 1),
            populacao=rnd.randint(3000, 300000),
            latitude=round(rnd.uniform(lat_min, lat_max), 4),
            longitude=round(rnd.uniform(lon_min, lon_max), 4),
        ))
    # Constrói grafo conexo base
    g = Grafo()
    for m in municipios:
        g.adicionar_municipio(m)
    # Adiciona arestas por densidade (peso = distância real Haversine)
    arestas_existentes = set()
    for i in range(n):
        for j in range(i + 1, n):
            if rnd.random() < densidade:
                a, b = municipios[i], municipios[j]
                d = haversine_km(a.latitude, a.longitude, b.latitude, b.longitude)
                g.adicionar_aresta(a.id_ibge, b.id_ibge, round(d, 2))
                arestas_existentes.add((i, j))
    # Garante conectividade: conecta cada vértice isolado ou componente solto
    while not g.is_conexo():
        origem = next(iter(g.municipios))
        comp = set(g.bfs(origem))
        fora = [mid for mid in g.vertices() if mid not in comp]
        u = next(iter(comp)); v = fora[0]
        mu, mv = g.municipios[u], g.municipios[v]
        d = haversine_km(mu.latitude, mu.longitude, mv.latitude, mv.longitude)
        g.adicionar_aresta(u, v, round(d, 2))
    return g


def comparar_algoritmos(tamanhos=(5, 8, 10, 12, 20, 50, 100),
                        limite_forca_bruta: int = 12) -> list[dict]:
    """
    Compara Força Bruta x Dijkstra nos tamanhos dados.
    A força bruta só é executada até 'limite_forca_bruta' (acima disso é inviável).
    Retorna lista de registros (um por tamanho) com tempos, memória e operações.
    """
    registros = []
    for n in tamanhos:
        g = gerar_instancia(n)
        vertices = g.vertices()
        origem = vertices[0]
        destino = vertices[-1]

        reg = {"n": n, "arestas": g.num_arestas()}

        # ---- DIJKSTRA (guloso) ----
        (dist, pred, met_dij), t_dij, mem_dij = _medir(dijkstra, g, origem)
        reg["dijkstra_ms"] = round(t_dij, 4)
        reg["dijkstra_mb"] = round(mem_dij, 5)
        reg["dijkstra_ops"] = met_dij["arestas_relaxadas"] + met_dij["extracoes_heap"]

        # ---- FORÇA BRUTA (somente N pequeno) ----
        if n <= limite_forca_bruta:
            (fb, t_fb, mem_fb) = _medir(forca_bruta_caminho_minimo, g, origem, destino)
            reg["fb_ms"] = round(t_fb, 4)
            reg["fb_mb"] = round(mem_fb, 5)
            reg["fb_ops"] = fb["metricas"]["chamadas_recursivas"]
            reg["fb_caminhos"] = fb["metricas"]["caminhos_avaliados"]
            # gap de otimalidade: diferença % entre FB (ótimo) e Dijkstra
            custo_dij = dist[destino]
            custo_fb = fb["melhor_custo"]
            if custo_fb and custo_fb > 0:
                gap = abs(custo_dij - custo_fb) / custo_fb * 100.0
            else:
                gap = 0.0
            reg["gap_otimalidade_pct"] = round(gap, 4)
        else:
            reg["fb_ms"] = None
            reg["fb_mb"] = None
            reg["fb_ops"] = None
            reg["fb_caminhos"] = None
            reg["gap_otimalidade_pct"] = None

        registros.append(reg)
    return registros


def imprimir_tabela(registros: list[dict]) -> None:
    """Imprime a tabela comparativa formatada no console."""
    print(f"\n{'N':>4} | {'Arestas':>7} | {'Dijkstra(ms)':>12} | {'FB(ms)':>12} | "
          f"{'Dij ops':>8} | {'FB ops':>10} | {'Gap %':>6}")
    print("-" * 78)
    for r in registros:
        fb_ms = f"{r['fb_ms']:.4f}" if r['fb_ms'] is not None else "inviável"
        fb_ops = f"{r['fb_ops']:,}" if r['fb_ops'] is not None else "-"
        gap = f"{r['gap_otimalidade_pct']:.2f}" if r['gap_otimalidade_pct'] is not None else "-"
        print(f"{r['n']:>4} | {r['arestas']:>7} | {r['dijkstra_ms']:>12.4f} | {fb_ms:>12} | "
              f"{r['dijkstra_ops']:>8,} | {fb_ops:>10} | {gap:>6}")


def crescimento_caminhos(tamanhos=(4, 6, 8, 10, 12)) -> list[tuple[int, int]]:
    """
    Mede o número de caminhos simples conforme N cresce (explosão combinatória).
    Usa densidade alta e fixa para evidenciar o crescimento fatorial de forma
    clara e monotônica (grafo quase completo = pior caso da força bruta).
    """
    pontos = []
    for n in tamanhos:
        # densidade alta (0.85) -> grafo quase completo -> pior caso combinatório
        g = gerar_instancia(n, semente=7, densidade=0.85)
        v = g.vertices()
        total = contar_caminhos(g, v[0], v[-1])
        pontos.append((n, total))
    return pontos


if __name__ == "__main__":
    print("=" * 78)
    print("AETHER 2.0 — Monitoramento de Desempenho: Força Bruta x Dijkstra")
    print("=" * 78)
    regs = comparar_algoritmos()
    imprimir_tabela(regs)

    print("\nExplosão combinatória (nº de caminhos simples vs N):")
    for n, total in crescimento_caminhos():
        print(f"  N={n:>3}  ->  {total:>12,} caminhos")

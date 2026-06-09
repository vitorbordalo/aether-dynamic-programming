"""
AETHER 2.0 — Monitoramento de Riscos Ambientais com Grafos e Algoritmos
FIAP · Global Solution 2026 · Dynamic Programming — Prof. André Marques

Ponto de entrada único: executa toda a demonstração do projeto em sequência.
Compatível com Python 3.9+ em Windows, macOS e Linux.
"""

import sys
import os

# Garante Python 3.9+
if sys.version_info < (3, 9):
    sys.exit("Erro: Python 3.9 ou superior é necessário.")

# Adiciona a raiz do projeto ao path para imports funcionarem em qualquer SO
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

BASE = ROOT
CSV  = os.path.join(BASE, "data", "raw", "municipios_rs_2024.csv")
HUB  = 4314902   # Porto Alegre
SEP  = "=" * 70


def _secao(titulo: str) -> None:
    print(f"\n{SEP}")
    print(f"  {titulo}")
    print(SEP)


# ─────────────────────────────────────────────────────────────────────────────
# 1. ESTRUTURAS DE DADOS
# ─────────────────────────────────────────────────────────────────────────────
_secao("1 / 6  —  ESTRUTURAS DE DADOS  (BST · Grafo · Haversine)")

from src.data_structures import carregar_municipios, construir_grafo, construir_bst

munis = carregar_municipios(CSV)
print(f"Municípios carregados: {len(munis)}")

g = construir_grafo(munis)
print(f"Grafo: {g.num_vertices()} vértices · {g.num_arestas()} arestas · conexo={g.is_conexo()}")

bst = construir_bst(munis)
print(f"BST  : {len(bst)} nós · altura={bst.altura()} · balanceada={bst.esta_balanceada()}")

print("\nTop 5 municípios mais críticos (maior índice de risco):")
for m in bst.percurso_in_order_desc()[:5]:
    print(f"  {m.nome:<25s}  risco={m.indice_risco:.2f}  pop~{m.populacao:,}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. DIJKSTRA (algoritmo guloso)
# ─────────────────────────────────────────────────────────────────────────────
_secao("2 / 6  —  DIJKSTRA  (algoritmo guloso — caminho mínimo)")

from src.greedy import dijkstra, reconstruir_caminho, rotas_a_partir_do_hub

distancias, predecessores, metricas = dijkstra(g, HUB)
print(f"Hub: Porto Alegre")
print(f"Operacoes: {metricas}\n")

rotas = rotas_a_partir_do_hub(g, HUB)
criticos = sorted(munis, key=lambda m: m.indice_risco, reverse=True)
print("Rotas otimas para os 5 municipios mais criticos:")
contagem = 0
for m in criticos:
    if m.id_ibge == HUB:
        continue
    r = rotas[m.id_ibge]
    print(f"  {m.nome:<22s} risco={m.indice_risco:.2f}  "
          f"custo={r['custo_km']:6.1f} km  saltos={r['num_saltos']}")
    print(f"     rota: {' -> '.join(r['caminho_nomes'])}")
    contagem += 1
    if contagem == 5:
        break


# ─────────────────────────────────────────────────────────────────────────────
# 3. FORÇA BRUTA  (oráculo de validação)
# ─────────────────────────────────────────────────────────────────────────────
_secao("3 / 6  —  FORCA BRUTA  (oraculo de corretude · subgrafo pequeno)")

from src.brute_force import forca_bruta_caminho_minimo

pequeno    = munis[:10]
g_pequeno  = construir_grafo(pequeno, raio_conexao_km=120.0)
origem_id  = pequeno[0].id_ibge
destino_id = pequeno[-1].id_ibge

fb      = forca_bruta_caminho_minimo(g_pequeno, origem_id, destino_id)
dist_p, pred_p, _ = dijkstra(g_pequeno, origem_id)
cam_dij = reconstruir_caminho(pred_p, origem_id, destino_id)

print(f"Origem : {g_pequeno.municipios[origem_id].nome}")
print(f"Destino: {g_pequeno.municipios[destino_id].nome}\n")
print(f"Forca Bruta  -> custo = {fb['melhor_custo']} km")
print(f"  caminho: {[g_pequeno.municipios[i].nome for i in fb['melhor_caminho']]}")
print(f"  metricas: {fb['metricas']}\n")
print(f"Dijkstra     -> custo = {round(dist_p[destino_id], 2)} km")
print(f"  caminho: {[g_pequeno.municipios[i].nome for i in cam_dij]}\n")
coincidem = abs(fb["melhor_custo"] - dist_p[destino_id]) < 0.01
print(f"Resultados coincidem? {coincidem}  -> Dijkstra e otimo.")


# ─────────────────────────────────────────────────────────────────────────────
# 4. MONITOR DE DESEMPENHO
# ─────────────────────────────────────────────────────────────────────────────
_secao("4 / 6  —  DESEMPENHO  (Forca Bruta x Dijkstra · escalabilidade)")

from src.performance_monitor import comparar_algoritmos, crescimento_caminhos, imprimir_tabela

registros = comparar_algoritmos()
imprimir_tabela(registros)

print("\nExplosao combinatoria (no de caminhos simples x N):")
for n, total in crescimento_caminhos():
    print(f"  N={n:>3}  ->  {total:>12,} caminhos")


# ─────────────────────────────────────────────────────────────────────────────
# 5. FIGURAS
# ─────────────────────────────────────────────────────────────────────────────
_secao("5 / 6  —  VISUALIZACOES  (5 figuras obrigatorias)")

from src.visualizations import gerar_todas

gerar_todas(BASE)


# ─────────────────────────────────────────────────────────────────────────────
# 6. TESTES AUTOMATIZADOS
# ─────────────────────────────────────────────────────────────────────────────
_secao("6 / 6  —  TESTES  (pytest · 21 casos)")

resultado = pytest.main(["-v", "--tb=short", os.path.join(BASE, "tests")])

print(f"\n{SEP}")
if resultado == 0:
    print("  AETHER 2.0 — todos os modulos executados com sucesso.")
else:
    print("  AETHER 2.0 — concluido com falhas nos testes (ver acima).")
print(SEP)

sys.exit(resultado)

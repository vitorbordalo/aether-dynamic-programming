"""
test_algorithms.py
==================
Testes unitários (pytest) do sistema AETHER 2.0 — Dynamic Programming.

Cobrem:
    - Estruturas de dados (BST: inserção, busca por intervalo, in-order, altura, remoção)
    - Grafo (construção, conectividade, vizinhos)
    - Dijkstra (corretude, caminho, casos de borda)
    - Força Bruta (corretude e equivalência com Dijkstra = validação do guloso)

Executar:  pytest -v
"""

import os
import sys

# garante import dos módulos src/ independente do diretório de execução
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_structures import (
    Municipio, BinarySearchTree, Grafo, construir_bst, construir_grafo,
    carregar_municipios, haversine_km
)
from src.greedy import dijkstra, reconstruir_caminho, rotas_a_partir_do_hub
from src.brute_force import forca_bruta_caminho_minimo


# ---------- fixtures auxiliares ----------
def _municipios_exemplo():
    return [
        Municipio(1, "A", 0.50, 100.0, 1000, -30.0, -51.0),
        Municipio(2, "B", 0.80, 200.0, 2000, -29.5, -51.5),
        Municipio(3, "C", 0.30, 150.0, 1500, -30.5, -50.5),
        Municipio(4, "D", 0.95, 120.0, 1200, -29.0, -52.0),
        Municipio(5, "E", 0.65, 180.0, 1800, -31.0, -50.0),
    ]


# ======================= BST =======================
def test_bst_insercao_tamanho():
    bst = construir_bst(_municipios_exemplo())
    assert len(bst) == 5

def test_bst_in_order_crescente():
    bst = construir_bst(_municipios_exemplo())
    riscos = [m.indice_risco for m in bst.percurso_in_order()]
    assert riscos == sorted(riscos)

def test_bst_in_order_desc_mais_critico_primeiro():
    bst = construir_bst(_municipios_exemplo())
    desc = bst.percurso_in_order_desc()
    assert desc[0].indice_risco == 0.95  # D é o mais crítico

def test_bst_busca_intervalo():
    bst = construir_bst(_municipios_exemplo())
    res = bst.buscar_intervalo(0.60, 0.90)
    riscos = sorted(m.indice_risco for m in res)
    assert riscos == [0.65, 0.80]

def test_bst_altura_nao_negativa():
    bst = construir_bst(_municipios_exemplo())
    assert bst.altura() >= 0

def test_bst_remocao():
    bst = construir_bst(_municipios_exemplo())
    assert bst.remover(4) is True          # remove D (0.95)
    assert len(bst) == 4
    assert all(m.id_ibge != 4 for m in bst.percurso_in_order())

def test_bst_remocao_inexistente():
    bst = construir_bst(_municipios_exemplo())
    assert bst.remover(999) is False
    assert len(bst) == 5

def test_bst_vazia():
    bst = BinarySearchTree()
    assert len(bst) == 0
    assert bst.altura() == -1
    assert bst.percurso_in_order() == []


# ======================= GRAFO =======================
def test_grafo_construcao():
    g = construir_grafo(_municipios_exemplo(), raio_conexao_km=200.0)
    assert g.num_vertices() == 5
    assert g.num_arestas() > 0

def test_grafo_conexo():
    g = construir_grafo(_municipios_exemplo(), raio_conexao_km=200.0)
    assert g.is_conexo() is True

def test_grafo_aresta_simetrica():
    g = Grafo()
    for m in _municipios_exemplo():
        g.adicionar_municipio(m)
    g.adicionar_aresta(1, 2, 10.0)
    vizinhos_1 = dict(g.vizinhos(1))
    vizinhos_2 = dict(g.vizinhos(2))
    assert vizinhos_1[2] == 10.0
    assert vizinhos_2[1] == 10.0  # não-direcionado

def test_haversine_conhecido():
    # Porto Alegre -> Canoas ~ 14 km (aprox)
    d = haversine_km(-30.0346, -51.2177, -29.9177, -51.1844)
    assert 10 < d < 20


# ======================= DIJKSTRA =======================
def test_dijkstra_origem_zero():
    g = construir_grafo(_municipios_exemplo(), raio_conexao_km=300.0)
    dist, _pred, _met = dijkstra(g, 1)
    assert dist[1] == 0.0

def test_dijkstra_todos_alcancaveis():
    g = construir_grafo(_municipios_exemplo(), raio_conexao_km=300.0)
    dist, _pred, _met = dijkstra(g, 1)
    assert all(d < float("inf") for d in dist.values())

def test_dijkstra_caminho_valido():
    g = construir_grafo(_municipios_exemplo(), raio_conexao_km=300.0)
    _dist, pred, _met = dijkstra(g, 1)
    caminho = reconstruir_caminho(pred, 1, 4)
    assert caminho[0] == 1 and caminho[-1] == 4

def test_dijkstra_metricas_positivas():
    g = construir_grafo(_municipios_exemplo(), raio_conexao_km=300.0)
    _dist, _pred, met = dijkstra(g, 1)
    assert met["extracoes_heap"] > 0
    assert met["arestas_relaxadas"] >= 0


# ============ FORÇA BRUTA x DIJKSTRA (corretude do guloso) ============
def test_fb_igual_dijkstra():
    """O custo da força bruta (ótimo) deve coincidir com o de Dijkstra."""
    g = construir_grafo(_municipios_exemplo(), raio_conexao_km=300.0)
    origem, destino = 1, 4
    fb = forca_bruta_caminho_minimo(g, origem, destino)
    dist, _pred, _met = dijkstra(g, origem)
    assert abs(fb["melhor_custo"] - dist[destino]) < 0.01

def test_fb_caminho_comeca_e_termina_certo():
    g = construir_grafo(_municipios_exemplo(), raio_conexao_km=300.0)
    fb = forca_bruta_caminho_minimo(g, 1, 5)
    assert fb["melhor_caminho"][0] == 1
    assert fb["melhor_caminho"][-1] == 5

def test_fb_origem_igual_destino():
    g = construir_grafo(_municipios_exemplo(), raio_conexao_km=300.0)
    fb = forca_bruta_caminho_minimo(g, 1, 1)
    assert fb["melhor_custo"] == 0.0


# ======================= DADOS REAIS =======================
def test_carregar_dados_reais():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, "data", "raw", "municipios_rs_2024.csv")
    munis = carregar_municipios(csv_path)
    assert len(munis) >= 20
    # Porto Alegre presente
    assert any(m.nome == "Porto Alegre" for m in munis)

def test_dijkstra_dados_reais_hub():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, "data", "raw", "municipios_rs_2024.csv")
    munis = carregar_municipios(csv_path)
    g = construir_grafo(munis)
    rotas = rotas_a_partir_do_hub(g, 4314902)  # Porto Alegre
    # toda rota deve ter custo finito e positivo
    assert all(r["custo_km"] >= 0 for r in rotas.values())

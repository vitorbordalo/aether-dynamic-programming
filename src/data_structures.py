"""
Data_structures.py
===================
Estruturas de dados fundamentais do sistema AETHER 2.0 — Monitoramento de
Riscos Ambientais (Global Solution 2026 — Dynamic Programming).

Contém:
    - Município (namedtuple)          -> TUPLA imutável (id, nome, risco, custo, pop)
    - Node / BinarySearchTree         -> ÁRVORE BINÁRIA DE BUSCA implementada do ZERO
    - Grafo                           -> GRAFO ponderado (DICIONÁRIO de listas de adjacência)
    - utilitários de carga de dados   -> uso de LISTA, TUPLA, DICT, SET, HEAP

Nenhuma biblioteca externa de estrutura de dados é usada (sem bintrees,
sortedcontainers, etc). Apenas a biblioteca padrão do Python.

Autores: [Seu Nome] (RM xxxxx) e Lucas [Sobrenome] (RM xxxxx)
Disciplina: Dynamic Programming — Estruturas de Dados e Algoritmos — FIAP
"""

from __future__ import annotations
import csv
import math
from collections import namedtuple, deque
from typing import Optional, Iterator


# ============================================================
# 1. TUPLA IMUTÁVEL — representação de um município (vértice)
# ============================================================
# Usamos namedtuple porque o enunciado pede uma TUPLA imutável com os
# atributos principais do vértice. namedtuple é uma tupla nomeada: imutável,
# leve e com acesso por nome (legibilidade).
Municipio = namedtuple(
    "Municipio",
    ["id_ibge", "nome", "indice_risco", "custo_atendimento", "populacao",
     "latitude", "longitude"]
)


# ============================================================
# 2. ÁRVORE BINÁRIA DE BUSCA (BST) — implementada do zero
# ============================================================
class Node:
    """Nó da BST. Cada nó carrega um Município e usa o índice de risco como chave."""
    __slots__ = ("municipio", "esquerda", "direita")

    def __init__(self, municipio: Municipio):
        self.municipio = municipio
        self.esquerda: Optional["Node"] = None
        self.direita: Optional["Node"] = None

    @property
    def chave(self) -> float:
        """A chave de ordenação da BST é o índice de risco do município."""
        return self.municipio.indice_risco


class BinarySearchTree:
    """
    Árvore Binária de Busca ordenada pelo índice de risco dos municípios.

    Propriedade BST mantida: risco_esquerda < risco_pai <= risco_direita.
    (Empates de risco vão para a subárvore direita, garantindo determinismo.)

    Operações implementadas do zero:
        inserir(municipio)
        buscar_intervalo(r_min, r_max)   -> municípios com risco em [r_min, r_max]
        percurso_in_order()              -> municípios em ordem crescente de risco
        altura()                         -> altura da árvore (avaliação de balanceamento)
        remover(id_ibge)                 -> remove um nó pela identidade do município
    """

    def __init__(self):
        self.raiz: Optional[Node] = None
        self._tamanho = 0

    def __len__(self) -> int:
        return self._tamanho

    # ---------- INSERÇÃO ----------
    def inserir(self, municipio: Municipio) -> None:
        """Insere mantendo a propriedade BST. Complexidade média O(log n), pior O(n)."""
        novo = Node(municipio)
        if self.raiz is None:
            self.raiz = novo
            self._tamanho += 1
            return
        atual = self.raiz
        while True:
            if novo.chave < atual.chave:
                if atual.esquerda is None:
                    atual.esquerda = novo
                    break
                atual = atual.esquerda
            else:  # >= vai para a direita (trata empates de risco)
                if atual.direita is None:
                    atual.direita = novo
                    break
                atual = atual.direita
        self._tamanho += 1

    # ---------- BUSCA POR INTERVALO DE RISCO ----------
    def buscar_intervalo(self, r_min: float, r_max: float) -> list[Municipio]:
        """
        Retorna todos os municípios com índice de risco em [r_min, r_max],
        em ordem crescente de risco. Usa poda dos ramos fora do intervalo.
        """
        resultado: list[Municipio] = []
        self._buscar_intervalo(self.raiz, r_min, r_max, resultado)
        return resultado

    def _buscar_intervalo(self, node, r_min, r_max, acc) -> None:
        if node is None:
            return
        # Só desce à esquerda se ainda pode haver chaves >= r_min
        if node.chave > r_min:
            self._buscar_intervalo(node.esquerda, r_min, r_max, acc)
        # Visita o nó se está dentro do intervalo
        if r_min <= node.chave <= r_max:
            acc.append(node.municipio)
        # Só desce à direita se ainda pode haver chaves <= r_max
        if node.chave < r_max:
            self._buscar_intervalo(node.direita, r_min, r_max, acc)

    # ---------- PERCURSO IN-ORDER (ordem crescente de risco) ----------
    def percurso_in_order(self) -> list[Municipio]:
        """Retorna municípios em ordem crescente de risco. Útil para priorização."""
        resultado: list[Municipio] = []
        self._in_order(self.raiz, resultado)
        return resultado

    def _in_order(self, node, acc) -> None:
        if node is None:
            return
        self._in_order(node.esquerda, acc)
        acc.append(node.municipio)
        self._in_order(node.direita, acc)

    def percurso_in_order_desc(self) -> list[Municipio]:
        """Ordem DECRESCENTE de risco — os mais críticos primeiro (priorização AETHER)."""
        return list(reversed(self.percurso_in_order()))

    # ---------- ALTURA ----------
    def altura(self) -> int:
        """Altura da árvore (número de arestas no caminho mais longo da raiz à folha)."""
        return self._altura(self.raiz)

    def _altura(self, node) -> int:
        if node is None:
            return -1  # convenção: árvore vazia tem altura -1; folha tem altura 0
        return 1 + max(self._altura(node.esquerda), self._altura(node.direita))

    def esta_balanceada(self) -> bool:
        """
        Compara a altura real com a altura ideal (log2 n). Indica se a BST
        degenerou (vira lista ligada) ou está próxima do ideal.
        """
        if self._tamanho <= 1:
            return True
        altura_ideal = math.floor(math.log2(self._tamanho))
        return self.altura() <= 2 * altura_ideal

    # ---------- REMOÇÃO ----------
    def remover(self, id_ibge: int) -> bool:
        """
        Remove o município de dado id_ibge. Como a BST é ordenada por risco,
        primeiro localizamos o risco do município alvo via varredura, depois
        removemos o nó correspondente tratando os 3 casos clássicos
        (folha, 1 filho, 2 filhos). Retorna True se removeu.
        """
        alvo = None
        for m in self.percurso_in_order():
            if m.id_ibge == id_ibge:
                alvo = m
                break
        if alvo is None:
            return False
        self.raiz = self._remover(self.raiz, alvo)
        self._tamanho -= 1
        return True

    def _remover(self, node, alvo: Municipio):
        if node is None:
            return None
        if alvo.indice_risco < node.chave:
            node.esquerda = self._remover(node.esquerda, alvo)
        elif alvo.indice_risco > node.chave:
            node.direita = self._remover(node.direita, alvo)
        else:
            # mesmo risco — confirma identidade pelo id_ibge
            if node.municipio.id_ibge != alvo.id_ibge:
                # risco igual mas município diferente: procura nos dois lados
                node.direita = self._remover(node.direita, alvo)
                return node
            # Caso 1: folha
            if node.esquerda is None and node.direita is None:
                return None
            # Caso 2: um filho
            if node.esquerda is None:
                return node.direita
            if node.direita is None:
                return node.esquerda
            # Caso 3: dois filhos — substitui pelo sucessor in-order (menor da direita)
            sucessor = self._minimo(node.direita)
            node.municipio = sucessor.municipio
            node.direita = self._remover(node.direita, sucessor.municipio)
        return node

    def _minimo(self, node) -> Node:
        atual = node
        while atual.esquerda is not None:
            atual = atual.esquerda
        return atual


# ============================================================
# 3. GRAFO PONDERADO — dicionário de listas de adjacência
# ============================================================
class Grafo:
    """
    Grafo ponderado não-direcionado representado como DICIONÁRIO de listas
    de adjacência: {id_vertice: [(vizinho, peso), ...]}.

    Justificativa da representação (lista de adjacência vs matriz):
        - Espaço: O(V + E) na lista vs O(V^2) na matriz. Como a rede de
          municípios é ESPARSA (cada município conecta-se a poucos vizinhos),
          a lista de adjacência economiza muita memória.
        - Tempo: percorrer vizinhos de um vértice é O(grau) na lista, ideal
          para Dijkstra/BFS/DFS, que iteram exatamente sobre os vizinhos.
    """

    def __init__(self):
        self.adjacencia: dict[int, list[tuple[int, float]]] = {}   # DICIONÁRIO
        self.municipios: dict[int, Municipio] = {}                  # DICIONÁRIO

    def adicionar_municipio(self, municipio: Municipio) -> None:
        self.municipios[municipio.id_ibge] = municipio
        self.adjacencia.setdefault(municipio.id_ibge, [])

    def adicionar_aresta(self, u: int, v: int, peso: float) -> None:
        """Aresta não-direcionada (u<->v) com peso = distância/tempo."""
        self.adjacencia.setdefault(u, []).append((v, peso))   # LISTA de TUPLAS
        self.adjacencia.setdefault(v, []).append((u, peso))

    def vizinhos(self, u: int) -> list[tuple[int, float]]:
        return self.adjacencia.get(u, [])

    def num_vertices(self) -> int:
        return len(self.municipios)

    def num_arestas(self) -> int:
        # cada aresta foi contada duas vezes (grafo não-direcionado)
        return sum(len(v) for v in self.adjacencia.values()) // 2

    def vertices(self) -> list[int]:
        return list(self.municipios.keys())

    def bfs(self, origem: int) -> list[int]:
        """
        Busca em largura — demonstra uso de FILA (deque) e CONJUNTO (set).
        Retorna a ordem de visitação a partir de 'origem'.
        """
        visitados: set[int] = set()          # CONJUNTO p/ pertencimento O(1)
        fila: deque[int] = deque([origem])   # FILA
        ordem: list[int] = []
        visitados.add(origem)
        while fila:
            atual = fila.popleft()
            ordem.append(atual)
            for vizinho, _peso in self.vizinhos(atual):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)
        return ordem

    def is_conexo(self) -> bool:
        """Verifica se o grafo é conexo (todos alcançáveis a partir de um vértice)."""
        if not self.municipios:
            return True
        origem = next(iter(self.municipios))
        return len(self.bfs(origem)) == self.num_vertices()


# ============================================================
# 4. UTILITÁRIOS — carga de dados reais e construção do grafo
# ============================================================
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Distância geodésica (em km) entre dois pontos pela fórmula de Haversine.
    Padrão geográfico para distância sobre a superfície da Terra (raio 6371 km).
    """
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def carregar_municipios(caminho_csv: str) -> list[Municipio]:
    """Carrega os municípios reais do RS a partir do CSV (dados IBGE + afetação 2024)."""
    municipios: list[Municipio] = []   # LISTA
    with open(caminho_csv, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            municipios.append(Municipio(
                id_ibge=int(linha["id_ibge"]),
                nome=linha["nome"],
                indice_risco=float(linha["indice_risco"]),
                custo_atendimento=float(linha["custo_atendimento"]),
                populacao=int(linha["populacao"]),
                latitude=float(linha["latitude"]),
                longitude=float(linha["longitude"]),
            ))
    return municipios


def construir_grafo(municipios: list[Municipio], raio_conexao_km: float = 80.0) -> Grafo:
    """
    Constrói o grafo conectando municípios cuja distância Haversine seja menor
    que 'raio_conexao_km' (simula rotas/rodovias entre cidades próximas).
    O peso da aresta é a distância real em km entre os municípios.

    Garante conectividade total: após a conexão por raio, identifica componentes
    desconexos e os une pela menor aresta entre componentes (evita grafo
    desconexo, que quebraria o Dijkstra de fonte única).
    """
    g = Grafo()
    for m in municipios:
        g.adicionar_municipio(m)

    # Conecta pares dentro do raio
    for i in range(len(municipios)):
        for j in range(i + 1, len(municipios)):
            a, b = municipios[i], municipios[j]
            dist = haversine_km(a.latitude, a.longitude, b.latitude, b.longitude)
            if dist <= raio_conexao_km:
                g.adicionar_aresta(a.id_ibge, b.id_ibge, round(dist, 2))

    # Garante conectividade total: une componentes separados pela aresta mais curta
    while not g.is_conexo():
        # identifica o componente que contém o primeiro vértice
        origem = next(iter(g.municipios))
        componente = set(g.bfs(origem))
        fora = [mid for mid in g.vertices() if mid not in componente]
        # encontra a menor aresta entre o componente e o resto
        melhor = None
        menor = float("inf")
        for u in componente:
            mu = g.municipios[u]
            for v in fora:
                mv = g.municipios[v]
                d = haversine_km(mu.latitude, mu.longitude, mv.latitude, mv.longitude)
                if d < menor:
                    menor, melhor = d, (u, v)
        if melhor is None:
            break
        g.adicionar_aresta(melhor[0], melhor[1], round(menor, 2))

    return g


def construir_bst(municipios: list[Municipio]) -> BinarySearchTree:
    """Constrói a BST de municípios ordenada por índice de risco."""
    bst = BinarySearchTree()
    for m in municipios:
        bst.inserir(m)
    return bst


if __name__ == "__main__":
    # Demonstração rápida
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, "data", "raw", "municipios_rs_2024.csv")
    munis = carregar_municipios(csv_path)
    print(f"Municípios carregados: {len(munis)}")

    g = construir_grafo(munis)
    print(f"Grafo: {g.num_vertices()} vértices, {g.num_arestas()} arestas, conexo={g.is_conexo()}")

    bst = construir_bst(munis)
    print(f"BST: {len(bst)} nós, altura={bst.altura()}, balanceada={bst.esta_balanceada()}")
    print("\nTop 5 municípios mais críticos (maior risco):")
    for m in bst.percurso_in_order_desc()[:5]:
        print(f"  {m.nome:25s} risco={m.indice_risco:.2f} afetados~{m.populacao}")

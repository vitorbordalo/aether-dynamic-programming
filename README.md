# AETHER 2.0 — Monitoramento de Riscos Ambientais com Grafos e Algoritmos

**FIAP — Global Solution 2026 · 1º Semestre · Dynamic Programming (Estruturas de Dados e Algoritmos)**
**Professor:** André Marques

> *"A próxima corrida tecnológica já começou e participamos dela."*

---

## 👥 Identificação do Grupo

| Integrante | RM |
|---|---|
| [Vitor Bordalo Correa Guimaraes] | RM 561592 |
| Lucas Flekner Branquinho | RM 562262 |


---

## 🎯 Contextualização

Este projeto é parte do **AETHER 2.0 — Reverse Space Engineering**, solução da Global
Solution 2026 que aplica tecnologia da indústria espacial para responder a desastres
climáticos no Brasil.

Em **maio de 2024**, o Rio Grande do Sul sofreu a maior catástrofe climática da história
do país: **478 municípios atingidos, 183 mortes, 2,3 milhões de afetados e R$ 88 bilhões
em prejuízo**. A Defesa Civil levou dias para mapear áreas críticas.

Este módulo implementa o **núcleo algorítmico** do AETHER: dado um hub de recursos
(ex.: Porto Alegre), calcula a **rota ótima de atendimento** (menor distância) até cada
município afetado, usando **Dijkstra** (algoritmo guloso). Uma **Árvore Binária de Busca
(BST)** organiza os municípios por índice de risco para priorização, e a **Força Bruta**
serve como oráculo de validação da corretude do guloso.

**Cenário escolhido:** Cenário A — Rede de resposta a enchentes no Rio Grande do Sul.

**Conexão com os ODS da ONU:** ODS 9 (Infraestrutura e Inovação), ODS 11 (Cidades
Sustentáveis), ODS 13 (Ação Climática).

---

## 🗂️ Estrutura do Repositório

```
aether-dynamic-programming/
├── README.md                       # este arquivo
├── requirements.txt                # dependências Python
├── data/
│   ├── raw/
│   │   └── municipios_rs_2024.csv  # dados reais (IBGE + afetação 2024)
│   └── processed/                  # grafos/árvores serializados (gerados)
├── src/
│   ├── data_structures.py          # BST, Grafo, tupla, dict, heap, set (do zero)
│   ├── brute_force.py              # busca exaustiva com backtracking (baseline)
│   ├── greedy.py                   # Dijkstra (algoritmo guloso, com heapq)
│   ├── performance_monitor.py      # tempo, memória, operações, escalabilidade
│   └── visualizations.py           # figuras obrigatórias
├── notebooks/
│   └── analise_resultados.ipynb    # análise interativa e escala de decisão
├── tests/
│   └── test_algorithms.py          # testes unitários (pytest) — 21 testes
└── report/
    ├── relatorio_final.pdf         # relatório técnico
    └── figuras/                    # figuras geradas
```

---

## 🚀 Como Executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Rodar a demonstração das estruturas de dados
```bash
python -m src.data_structures
```

### 3. Rodar o algoritmo guloso (Dijkstra) com dados reais
```bash
python -m src.greedy
```

### 4. Validar com Força Bruta (oráculo de corretude)
```bash
python -m src.brute_force
```

### 5. Monitorar desempenho (Força Bruta x Dijkstra)
```bash
python -m src.performance_monitor
```

### 6. Gerar as figuras obrigatórias
```bash
python -m src.visualizations
```

### 7. Rodar os testes automatizados
```bash
pytest -v
```

---

## 🧱 Estruturas de Dados Utilizadas

| Estrutura | Onde é usada | Justificativa |
|---|---|---|
| **Lista** | adjacências, caminhos, resultados | acesso sequencial e ordem preservada |
| **Tupla** | `Municipio` (namedtuple), arestas `(v, peso)` | imutabilidade dos vértices/arestas |
| **Dicionário** | adjacência do grafo, custos, predecessores | acesso O(1) por id de município |
| **Conjunto (set)** | vértices visitados/finalizados | teste de pertencimento O(1), evita ciclos |
| **Heap (heapq)** | fila de prioridade do Dijkstra | extrair o mínimo em O(log V) |
| **Árvore Binária (BST)** | priorização por índice de risco | busca por faixa de risco em O(log n) médio |
| **Grafo (dict de listas)** | rede de municípios e rotas | espaço O(V+E), ideal para grafo esparso |

---

## 🔬 Algoritmos

### Força Bruta (baseline / oráculo)
Enumera **todos** os caminhos simples entre origem e destino via recursão com
*backtracking*. Usado para validar a corretude do guloso em instâncias pequenas
(N ≤ 12) e para evidenciar a **explosão combinatória**.

### Guloso — Dijkstra (solução eficiente)
A cada passo, extrai do heap o vértice de **menor custo acumulado** (decisão local
ótima) e relaxa suas arestas. Para pesos não-negativos (distâncias), garante o
**ótimo global**. Complexidade: **O((V + E) log V)**.

---

## 📊 Principais Resultados

- **Corretude validada:** o custo do Dijkstra coincide com o da Força Bruta em todas as
  instâncias testadas (**gap de otimalidade = 0%**).
- **Explosão combinatória:** o número de caminhos cresce de 5 (N=4) para **mais de 1
  milhão (N=12)**, tornando a Força Bruta inviável a partir de N ≈ 12.
- **Escalabilidade do Dijkstra:** resolve N=100 em poucos milissegundos.

---

## 📚 Referências

- CORMEN, T. et al. *Introduction to Algorithms*, 4th Ed. MIT Press, 2022. (Caps. 22–25)
- SEDGEWICK, R.; WAYNE, K. *Algorithms*, 4th Ed. Addison-Wesley, 2011. (Parte 4: Grafos)
- SKIENA, S. *The Algorithm Design Manual*, 3rd Ed. Springer, 2020.
- IBGE — Malha municipal e coordenadas: https://www.ibge.gov.br/geociencias
- Defesa Civil RS — Dados das enchentes de 2024.

---

*FIAP — Global Solution | 1º Semestre de 2026 | Dynamic Programming — Prof. André Marques*

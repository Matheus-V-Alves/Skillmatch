# SkillMatch360

**Motor de matching inteligente entre vagas e candidatos**

## Equipe - 2ESS FIAP

- Gustavo Atanazio - 559098
- Matheus Alves - 555177
- Larissa Pereira Biusse - 564068

## Sobre o Projeto

SkillMatch360 identifica automaticamente as melhores combinações entre candidatos e vagas, utilizando estruturas de dados avançadas e algoritmo guloso com desempate randômico.

### Estruturas Implementadas

- **Hash Table (dict)**: Armazenamento O(1) de candidatos, vagas e alocações
- **Grafo Bipartido**: Modelagem das relações candidato↔vaga com lista de adjacências
- **Heap (priority queue)**: Fila de prioridade para escolha gulosa das melhores arestas
- **BST (Binary Search Tree)**: Armazenamento ordenado dos matches por score

### Algoritmo de Score

```
Score = 0.6 × overlap_skills + 0.3 × experiência + 0.1 × localização
```

## Como Executar

### Execução Direta

```bash
python Gs2025.2.py
```

O programa já vem com dados de exemplo e executa automaticamente demonstrando:

- Carregamento de candidatos e vagas
- Construção do grafo e heap
- Matching guloso
- Top 10 matches
- Estatísticas completas

### Uso Programático

```python
from Gs2025_2 import run_matching

candidates = [
    {'id': 'C001', 'name': 'Ana Silva', 'skills': ['Python', 'Django'],
     'exp_years': 5, 'location': 'São Paulo'},
]

jobs = [
    {'id': 'J001', 'title': 'Dev Python', 'req_skills': ['Python', 'Django'],
     'min_exp': 3, 'location': 'São Paulo'},
]

# Com seed para reprodutibilidade
result = run_matching(candidates, jobs, seed=42, k_top=5)

# Acessando resultados
print(result['assignments'])    # dict: job_id -> candidate_id
print(result['ranking'])        # lista ordenada por score
print(result['top_k_per_job'])  # top candidatos por vaga
```

## Estruturas de Dados - Detalhamento

### 1. Hash Table

**Uso**: `candidates_db`, `jobs_db`, `job_assigned`, `candidate_assigned`  
**Justificativa**: Lookup e atualização em O(1) durante o matching

### 2. Grafo Bipartido

**Implementação**: `graph = {job_id: [(candidate_id, score), ...]}`  
**Justificativa**: Representa todas as possíveis combinações candidato-vaga

### 3. Heap (Max-Heap)

**Implementação**: heapq com scores negativos  
**Justificativa**: Extração eficiente O(log E) da melhor aresta disponível

### 4. BST

**Implementação**: Árvore binária com múltiplos valores por nó  
**Justificativa**: Permite travessia ordenada para consultas top-k

## Algoritmo Guloso - Fluxo

1. **Scoring**: Calcula compatibilidade para cada par (candidato, vaga)
2. **Build**: Cria grafo e insere todas arestas no heap
3. **Matching**:
   - Extrai aresta de maior score
   - Se vaga/candidato já alocados: descarta
   - Coleta empates (diferença < epsilon)
   - Escolhe aleatoriamente entre empates (seed controlável)
   - Marca alocação e insere na BST
4. **Output**: Gera assignments, ranking e top-k por vaga

## Resultados Esperados

### Performance

- **Tempo**: < 0.1s para 10 vagas × 20 candidatos
- **Complexidade**: O(J × C × log(J × C))
- **Taxa de match**: Depende da compatibilidade

### Exemplo de Match

```
[MATCH] Score: 0.950
  Vaga: J001 - Dev Python Pleno
  Candidato: C001 - Ana Silva
  Skills: Python, Django, PostgreSQL | Exp: 5 anos | Local: São Paulo
```

## Complexidade Computacional

| Operação            | Complexidade | Observação                |
| ------------------- | ------------ | ------------------------- |
| Construção do grafo | O(J × C)     | Calcula todos os scores   |
| Heap push           | O(E log E)   | E = arestas válidas       |
| Matching guloso     | O(E log E)   | Cada aresta processada 1x |
| BST inserção        | O(log M)     | M = matches realizados    |
| Total               | O(E log E)   | E ≈ J × C no pior caso    |

## Estrutura do Projeto

```
sprintDYNpy/
├── Gs2025.2.py    # Código principal completo
└── README.md      # Esta documentação
```

## Características Técnicas

- **Encoding UTF-8**: Suporte completo a acentuação
- **Seed Configurável**: Determinismo para testes e produção
- **Desempate Randômico**: Fairness entre candidatos equivalentes
- **Modular**: Classes separadas facilitam manutenção
- **Documentado**: Docstrings e comentários estratégicos

## Requisitos

- Python 3.7+
- Bibliotecas padrão: typing, dataclasses, collections, heapq, random

## Licença

Global Solution - 2ESS FIAP 2025

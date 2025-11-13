# SkillMatch360 - Documentação Técnica

## Resumo Executivo

SkillMatch360 é um protótipo de motor de matching entre vagas e candidatos que demonstra o uso de estruturas de dados avançadas (hash table, grafo, heap, BST) e algoritmo guloso com desempate randômico controlado.

## Arquitetura da Solução

### 1. Estruturas de Dados Implementadas

#### Hash Table (Dicionários Python)
- **Uso**: Armazenamento de candidatos, vagas e alocações
- **Complexidade**: O(1) para lookups e inserções
- **Implementação**:
  - `self.candidates: Dict[str, Candidate]`
  - `self.jobs: Dict[str, Job]`
  - `self.job_assigned: Dict[str, str]`
  - `self.candidate_assigned: Dict[str, str]`

#### Grafo Bipartido (Lista de Adjacência)
- **Uso**: Modelagem das relações vaga ↔ candidato
- **Estrutura**: `graph[job_id] = [(candidate_id, score), ...]`
- **Complexidade**: O(|V| + |E|) para construção
- **Vantagem**: Representa naturalmente o problema de matching bipartido

#### Heap (Fila de Prioridade)
- **Uso**: Extração eficiente da aresta de maior score
- **Implementação**: Max-heap usando `heapq` com scores negativos
- **Complexidade**: 
  - Push: O(log E)
  - Pop: O(log E)
  - E = número de arestas ≈ |Jobs| × |Candidates|

#### Árvore de Busca Binária (BST)
- **Uso**: Armazenamento ordenado dos matches finais
- **Funcionalidades**:
  - Inserção por score: O(log n) esperado
  - Travessia in-order reversa para ranking
  - Consulta top-k: O(k)
- **Estrutura**: Nós com score como chave, múltiplos matches por nó

### 2. Algoritmo de Scoring

```python
score = 0.6 * skill_score + 0.3 * exp_score + loc_bonus
```

**Componentes**:
- **skill_score**: overlap de skills / total de skills requeridas [0..1]
- **exp_score**: min(exp_candidate / min_exp_job, 2) / 2 [0..1]
- **loc_bonus**: 0.1 se localização coincide, senão 0

**Pesos configuráveis**: Permitem ajuste conforme prioridade do negócio.

### 3. Algoritmo Guloso de Matching

#### Fluxo:
1. **Inicialização**: Todas as arestas no heap por prioridade
2. **Loop principal**:
   - Pop da aresta de maior score
   - Verifica se vaga e candidato estão livres
   - **Coleta grupo de empate** (scores dentro de epsilon)
   - **Desempate randômico** entre pares válidos
   - Efetiva o match e atualiza estruturas
3. **Terminação**: Quando heap vazio ou todos alocados

#### Desempate Randômico:
```python
if len(valid_edges) > 1:
    chosen = random.choice(valid_edges)  # Seed controlável
```
- **Determinismo**: Mesmo seed → mesmo resultado
- **Fairness**: Empates não favorecem ordem de inserção

### 4. Complexidade Computacional

| Operação | Complexidade | Descrição |
|----------|-------------|-----------|
| Construção de arestas | O(J × C) | J = vagas, C = candidatos |
| Heap push todas arestas | O(E log E) | E ≈ J × C |
| Matching guloso | O(E log E) | Cada aresta processada ≤ 1 vez |
| BST inserção | O(log M) | M = matches finais |
| Top-k global | O(M) | Travessia in-order |
| Top-k por vaga | O(C log C) | Sorting local |

**Complexidade total**: O(J × C log(J × C))

## Critérios de Aceitação ✓

- [x] Processa dataset pequeno (≤10 vagas × ≤20 candidatos) em <1s
- [x] Cada vaga/candidato aparece no máximo 1 vez no resultado
- [x] BST retorna top-k corretamente ordenado
- [x] Seed fixo garante determinismo em empates
- [x] Logs indicam arestas criadas e processadas

## Resultados da Execução de Teste

### Dataset:
- **10 candidatos** com skills variadas
- **7 vagas** em diferentes localizações
- **65 arestas** criadas (score > 0.1)

### Resultados:
- **7 matches** realizados (100% das vagas preenchidas)
- **3 candidatos** não alocados
- **1 desempate** executado
- **Score mais alto**: 0.950 (Ana Silva → Desenvolvedor Python Pleno)

### Exemplo de Match:
```
Ana Silva (Python, Django, PostgreSQL, REST API, 5 anos, SP)
    ↓ Score: 0.950
Desenvolvedor Python Pleno (Python, Django, PostgreSQL, 3+ anos, SP)

Breakdown:
- Skill overlap: 3/3 = 100% → 0.6 * 1.0 = 0.600
- Experience: 5/3 = 1.67 → 0.3 * 0.835 = 0.250
- Location: SP = SP → 0.100
- Total: 0.950
```

## Como Usar

### Execução Básica:
```python
python Gs2025.2.py
```

### Customização:
```python
# Com seed para reprodutibilidade
result = run_matching(candidates, jobs, seed=42, k_top=5)

# Sem seed (aleatório)
result = run_matching(candidates, jobs, seed=None, k_top=3)

# Com score mínimo diferente
result = run_matching(candidates, jobs, seed=42, min_score=0.2)
```

### Retorno:
```python
{
    'assignments': {job_id: candidate_id, ...},
    'ranking': [(score, job_id, candidate_id), ...],
    'top_k_per_job': {job_id: [(cand_id, score), ...], ...},
    'stats': {...},
    'engine': SkillMatch360Instance
}
```

## Estrutura de Dados de Entrada

### Candidato:
```python
{
    'id': 'C001',
    'name': 'Nome Completo',
    'skills': ['Python', 'Django', 'PostgreSQL'],
    'exp_years': 5,
    'location': 'São Paulo'
}
```

### Vaga:
```python
{
    'id': 'J001',
    'title': 'Desenvolvedor Python Pleno',
    'req_skills': ['Python', 'Django', 'PostgreSQL'],
    'min_exp': 3,
    'location': 'São Paulo'
}
```

## Extensões Futuras

1. **Balanceamento da BST**: Implementar AVL ou Red-Black Tree
2. **Múltiplos matches**: Permitir 1 candidato → N vagas (se freelancer)
3. **Soft skills**: Adicionar dimensão de fit cultural
4. **Machine Learning**: Substituir fórmula manual por modelo treinado
5. **Persistência**: Exportar/importar de banco de dados
6. **API REST**: Expor como serviço web
7. **Feedback loop**: Atualizar pesos com base em sucesso real dos matches

## Validação do Determinismo

Execute duas vezes com mesmo seed:
```bash
python Gs2025.2.py  # Seed=42
python Gs2025.2.py  # Seed=42
# Resultados devem ser idênticos
```

Compare com seed diferente:
```python
result1 = run_matching(candidates, jobs, seed=42)
result2 = run_matching(candidates, jobs, seed=123)
# Resultados podem diferir nos empates
```

## Autores

**2ESS GRUPO:**
- Gustavo Atanazio - 559098
- Matheus Alves - 555177
- Larissa Pereira Biusse - 564068

---

**Data**: Novembro 2025  
**Versão**: 1.0 (Protótipo)

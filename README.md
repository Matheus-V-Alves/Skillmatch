# SkillMatch360

**Motor de matching inteligente entre vagas e candidatos**

## 👥 Equipe
- Gustavo Atanazio - 559098
- Matheus Alves - 555177
- Larissa Pereira Biusse - 564068

## 🎯 Sobre o Projeto

SkillMatch360 é um protótipo que identifica automaticamente as melhores combinações entre candidatos e vagas, utilizando estruturas de dados avançadas e algoritmo guloso com desempate randômico.

### Estruturas Implementadas
- **Hash Table**: Armazenamento O(1) de candidatos, vagas e alocações
- **Grafo Bipartido**: Modelagem das relações candidato↔vaga
- **Heap**: Fila de prioridade para escolha gulosa
- **BST**: Armazenamento ordenado dos matches

### Algoritmo de Score
```
Score = 0.6 × skills + 0.3 × experiência + 0.1 × localização
```

## 🚀 Como Usar

### Execução Básica
```bash
python Gs2025.2.py
```

### Execução com Parâmetros
```python
from Gs2025_2 import run_matching, get_sample_data

candidates, jobs = get_sample_data()

# Com seed para reprodutibilidade
result = run_matching(candidates, jobs, seed=42, k_top=5)

# Aleatório
result = run_matching(candidates, jobs, seed=None)
```

### Entrada de Dados

**Candidato:**
```python
{
    'id': 'C001',
    'name': 'Nome',
    'skills': ['Python', 'Django'],
    'exp_years': 5,
    'location': 'São Paulo'
}
```

**Vaga:**
```python
{
    'id': 'J001',
    'title': 'Dev Python',
    'req_skills': ['Python', 'Django'],
    'min_exp': 3,
    'location': 'São Paulo'
}
```

## 📊 Resultados

### Performance
- **Tempo**: < 0.1s para 10 vagas × 20 candidatos
- **Complexidade**: O(J × C × log(J × C))
- **Taxa de match**: 100% das vagas no teste

### Exemplo de Match
```
Ana Silva (Python, Django, PostgreSQL, 5 anos, SP)
    ↓ Score: 0.950
Dev Python Pleno (Python, Django, PostgreSQL, 3+ anos, SP)
```

## 🧪 Testes

```bash
python test_skillmatch.py
```

**Cobertura:**
- ✅ Determinismo (seed fixo)
- ✅ Unicidade de matches
- ✅ Fórmula de scoring
- ✅ BST ordenação
- ✅ Casos extremos
- ✅ Performance

## 📁 Estrutura

```
sprintDYNpy/
├── Gs2025.2.py              # Código principal
├── test_skillmatch.py       # Testes automatizados
├── exemplos_uso.py          # Exemplos práticos
└── README.md                # Esta documentação
```

## 🔧 Características Técnicas

### Decisões de Design
- **Algoritmo Guloso**: Simples e eficiente para matching
- **Desempate Randômico**: Fairness entre candidatos equivalentes
- **Seed Configurável**: Determinismo em testes
- **Modular**: Fácil extensão e manutenção

### Complexidade
| Operação | Complexidade |
|----------|--------------|
| Construção do grafo | O(J × C) |
| Heap operations | O(E log E) |
| Matching guloso | O(E log E) |
| BST inserção | O(log M) |

## 💡 Extensões Futuras
- Balanceamento da BST (AVL/Red-Black)
- Múltiplos matches por candidato
- Machine Learning para calibrar pesos
- API REST
- Integração com banco de dados

## 📄 Licença
Global Solution - 2ESS FIAP 2025

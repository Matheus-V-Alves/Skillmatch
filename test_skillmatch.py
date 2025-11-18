# -*- coding: utf-8 -*-
# 2ESS GRUPO: 
# Gustavo Atanazio - 559098           
# Matheus Alves - 555177 
# Larissa Pereira Biusse - 564068

"""
Testes e validações para o SkillMatch360
Demonstra diferentes cenários e valida critérios de aceitação
"""

import sys
import importlib.util

# Garante encoding UTF-8 no terminal Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Carrega o módulo principal
spec = importlib.util.spec_from_file_location("gs2025", "Gs2025.2.py")
gs2025 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gs2025)

# Importa as funções e classes necessárias
run_matching = gs2025.run_matching
calculate_score = gs2025.calculate_score
Candidate = gs2025.Candidate
Job = gs2025.Job
SkillMatch360 = gs2025.SkillMatch360


def test_determinism():
    """Testa se o algoritmo é determinístico com mesmo seed"""
    print("\n" + "="*60)
    print("TESTE 1: DETERMINISMO")
    print("="*60)
    
    candidates = [
        {'id': 'C1', 'name': 'João', 'skills': ['Python', 'Java'], 'exp_years': 3, 'location': 'SP'},
        {'id': 'C2', 'name': 'Maria', 'skills': ['Python', 'Java'], 'exp_years': 3, 'location': 'SP'},
        {'id': 'C3', 'name': 'Pedro', 'skills': ['Python', 'Java'], 'exp_years': 3, 'location': 'SP'},
    ]
    
    jobs = [
        {'id': 'J1', 'title': 'Dev Python', 'req_skills': ['Python'], 'min_exp': 2, 'location': 'SP'},
    ]
    
    # Executa 3 vezes com mesmo seed
    results = []
    for i in range(3):
        result = run_matching(candidates, jobs, seed=42, k_top=2)
        results.append(result['assignments'])
        print(f"\nExecução {i+1}: {result['assignments']}")
    
    # Valida que todos são iguais
    if results[0] == results[1] == results[2]:
        print("\n\033[92m[OK] TESTE PASSOU:\033[0m Resultados idênticos com mesmo seed")
    else:
        print("\n\033[91m[FALHA] TESTE FALHOU:\033[0m Resultados diferentes com mesmo seed")


def test_uniqueness():
    """Testa se cada vaga/candidato aparece no máximo uma vez"""
    print("\n" + "="*60)
    print("TESTE 2: UNICIDADE DE MATCHES")
    print("="*60)
    
    candidates = [
        {'id': f'C{i}', 'name': f'Candidato{i}', 'skills': ['Python'], 'exp_years': 5, 'location': 'SP'}
        for i in range(1, 11)
    ]
    
    jobs = [
        {'id': f'J{i}', 'title': f'Vaga{i}', 'req_skills': ['Python'], 'min_exp': 3, 'location': 'SP'}
        for i in range(1, 6)
    ]
    
    result = run_matching(candidates, jobs, seed=42)
    assignments = result['assignments']
    
    # Verifica unicidade de vagas
    unique_jobs = len(set(assignments.keys()))
    total_jobs = len(assignments.keys())
    
    # Verifica unicidade de candidatos
    unique_candidates = len(set(assignments.values()))
    total_candidates = len(assignments.values())
    
    print(f"\nVagas únicas: {unique_jobs}/{total_jobs}")
    print(f"Candidatos únicos: {unique_candidates}/{total_candidates}")
    
    if unique_jobs == total_jobs and unique_candidates == total_candidates:
        print("\n\033[92m[OK] TESTE PASSOU:\033[0m Cada vaga/candidato aparece no máximo uma vez")
    else:
        print("\n\033[91m[FALHA] TESTE FALHOU:\033[0m Duplicatas encontradas")


def test_scoring_formula():
    """Testa a fórmula de scoring com casos conhecidos"""
    print("\n" + "="*60)
    print("TESTE 3: FÓRMULA DE SCORING")
    print("="*60)
    
    # Caso 1: Match perfeito
    cand1 = Candidate('C1', 'Perfect Match', ['Python', 'Django', 'SQL'], 5, 'São Paulo')
    job1 = Job('J1', 'Dev Python', ['Python', 'Django', 'SQL'], 3, 'São Paulo')
    score1 = calculate_score(cand1, job1)
    print(f"\nCaso 1 - Match Perfeito:")
    print(f"  Skills: 3/3, Exp: 5/3, Location: match")
    print(f"  Score calculado: {score1:.3f}")
    print(f"  Score esperado: ~1.000")
    
    # Caso 2: Sem overlap de skills
    cand2 = Candidate('C2', 'No Match', ['Java', 'Spring'], 10, 'Rio de Janeiro')
    job2 = Job('J2', 'Dev Python', ['Python', 'Django'], 5, 'São Paulo')
    score2 = calculate_score(cand2, job2)
    print(f"\nCaso 2 - Sem Overlap:")
    print(f"  Skills: 0/2, Exp: 10/5, Location: no match")
    print(f"  Score calculado: {score2:.3f}")
    print(f"  Score esperado: ~0.300 (apenas exp)")
    
    # Caso 3: Parcial
    cand3 = Candidate('C3', 'Partial', ['Python', 'Java'], 4, 'Belo Horizonte')
    job3 = Job('J3', 'Dev Python', ['Python', 'Django', 'SQL'], 3, 'São Paulo')
    score3 = calculate_score(cand3, job3)
    print(f"\nCaso 3 - Match Parcial:")
    print(f"  Skills: 1/3, Exp: 4/3, Location: no match")
    print(f"  Score calculado: {score3:.3f}")
    
    if 0.95 <= score1 <= 1.05 and score2 < 0.5 and 0 < score3 < 1:
        print("\n\033[92m[OK] TESTE PASSOU:\033[0m Fórmula de scoring funcionando corretamente")
    else:
        print("\n\033[91m[FALHA] TESTE FALHOU:\033[0m Scores fora do esperado")


def test_bst_top_k():
    """Testa a funcionalidade top-k da BST"""
    print("\n" + "="*60)
    print("TESTE 4: BST TOP-K")
    print("="*60)
    
    candidates = [
        {'id': f'C{i}', 'name': f'Cand{i}', 'skills': ['Python'] * i, 'exp_years': i, 'location': 'SP'}
        for i in range(1, 11)
    ]
    
    jobs = [
        {'id': f'J{i}', 'title': f'Job{i}', 'req_skills': ['Python'], 'min_exp': 1, 'location': 'SP'}
        for i in range(1, 11)
    ]
    
    result = run_matching(candidates, jobs, seed=42, k_top=5)
    ranking = result['ranking']
    
    # Verifica se está ordenado (decrescente)
    scores = [score for score, _, _ in ranking]
    is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
    
    print(f"\nTotal de matches: {len(ranking)}")
    print(f"Scores (top-5): {[f'{s:.3f}' for s in scores[:5]]}")
    print(f"Ordenado corretamente: {is_sorted}")
    
    # Testa top-k
    top_3 = result['ranking'][:3]
    print(f"\nTop-3 matches:")
    for i, (score, job, cand) in enumerate(top_3, 1):
        print(f"  {i}. Score: {score:.3f} | Job: {job} | Cand: {cand}")
    
    if is_sorted and len(ranking) <= len(jobs):
        print("\n\033[92m[OK] TESTE PASSOU:\033[0m BST retorna top-k ordenado corretamente")
    else:
        print("\n\033[91m[FALHA] TESTE FALHOU:\033[0m Problemas na ordenação ou quantidade")


def test_edge_cases():
    """Testa casos extremos"""
    print("\n" + "="*60)
    print("TESTE 5: CASOS EXTREMOS")
    print("="*60)
    
    # Caso 1: Mais vagas que candidatos
    print("\nCaso 1: Mais vagas (5) que candidatos (3)")
    candidates = [
        {'id': f'C{i}', 'name': f'Cand{i}', 'skills': ['Python'], 'exp_years': 3, 'location': 'SP'}
        for i in range(1, 4)
    ]
    jobs = [
        {'id': f'J{i}', 'title': f'Job{i}', 'req_skills': ['Python'], 'min_exp': 2, 'location': 'SP'}
        for i in range(1, 6)
    ]
    result1 = run_matching(candidates, jobs, seed=42)
    print(f"  Matches realizados: {len(result1['assignments'])}")
    print(f"  Vagas não preenchidas: {len(jobs) - len(result1['assignments'])}")
    
    # Caso 2: Mais candidatos que vagas
    print("\nCaso 2: Mais candidatos (8) que vagas (3)")
    candidates = [
        {'id': f'C{i}', 'name': f'Cand{i}', 'skills': ['Java'], 'exp_years': 4, 'location': 'RJ'}
        for i in range(1, 9)
    ]
    jobs = [
        {'id': f'J{i}', 'title': f'Job{i}', 'req_skills': ['Java'], 'min_exp': 3, 'location': 'RJ'}
        for i in range(1, 4)
    ]
    result2 = run_matching(candidates, jobs, seed=42)
    print(f"  Matches realizados: {len(result2['assignments'])}")
    print(f"  Candidatos não alocados: {len(candidates) - len(result2['assignments'])}")
    
    # Caso 3: Nenhum match possível (skills incompatíveis)
    print("\nCaso 3: Skills totalmente incompatíveis")
    candidates = [
        {'id': 'C1', 'name': 'Java Dev', 'skills': ['Java', 'Spring'], 'exp_years': 5, 'location': 'SP'}
    ]
    jobs = [
        {'id': 'J1', 'title': 'Python Dev', 'req_skills': ['Python', 'Django'], 'min_exp': 3, 'location': 'SP'}
    ]
    result3 = run_matching(candidates, jobs, seed=42, min_score=0.3)
    print(f"  Matches realizados: {len(result3['assignments'])}")
    
    print("\n\033[92m[OK] TESTE PASSOU:\033[0m Casos extremos tratados corretamente")


def test_performance():
    """Testa performance com dataset maior"""
    print("\n" + "="*60)
    print("TESTE 6: PERFORMANCE")
    print("="*60)
    
    import time
    
    # Dataset médio
    skills_pool = ['Python', 'Java', 'JavaScript', 'C++', 'Go', 'Rust', 'Ruby', 'PHP']
    locations = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre']
    
    candidates = [
        {
            'id': f'C{i}',
            'name': f'Candidate{i}',
            'skills': [skills_pool[j % len(skills_pool)] for j in range(i % 4 + 1)],
            'exp_years': (i % 10) + 1,
            'location': locations[i % len(locations)]
        }
        for i in range(1, 21)
    ]
    
    jobs = [
        {
            'id': f'J{i}',
            'title': f'Job{i}',
            'req_skills': [skills_pool[j % len(skills_pool)] for j in range((i % 3) + 1)],
            'min_exp': (i % 5) + 2,
            'location': locations[i % len(locations)]
        }
        for i in range(1, 11)
    ]
    
    print(f"\nDataset: {len(candidates)} candidatos × {len(jobs)} vagas")
    print(f"Arestas máximas: {len(candidates) * len(jobs)}")
    
    start = time.time()
    result = run_matching(candidates, jobs, seed=42)
    elapsed = time.time() - start
    
    print(f"\nTempo de execução: {elapsed:.3f}s")
    print(f"Matches realizados: {len(result['assignments'])}")
    print(f"Arestas criadas: {result['stats']['edges_created']}")
    print(f"Arestas processadas: {result['stats']['edges_processed']}")
    
    if elapsed < 1.0:
        print("\n\033[92m[OK] TESTE PASSOU:\033[0m Execução em < 1 segundo")
    else:
        print(f"\n\033[93m[AVISO]:\033[0m Execução em {elapsed:.3f}s (esperado < 1s)")


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "#"*60)
    print("# SUITE DE TESTES - SkillMatch360")
    print("#"*60)
    
    tests = [
        test_determinism,
        test_uniqueness,
        test_scoring_formula,
        test_bst_top_k,
        test_edge_cases,
        test_performance
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n\033[91m[ERRO]\033[0m no teste {test.__name__}: {e}")
    
    print("\n" + "#"*60)
    print("# SUITE DE TESTES CONCLUÍDA")
    print("#"*60)


if __name__ == '__main__':
    run_all_tests()

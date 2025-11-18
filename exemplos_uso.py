# -*- coding: utf-8 -*-
# 2ESS GRUPO: 
# Gustavo Atanazio - 559098           
# Matheus Alves - 555177 
# Larissa Pereira Biusse - 564068

"""
Exemplos de Uso do SkillMatch360
Demonstra diferentes cenários e casos de uso
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

run_matching = gs2025.run_matching


# ============================================================
# EXEMPLO 1: Matching Básico com Dados Reais
# ============================================================

def exemplo_basico():
    """Exemplo simples de matching"""
    print("\n" + "="*70)
    print("EXEMPLO 1: MATCHING BÁSICO")
    print("="*70)
    
    candidatos = [
        {
            'id': 'C001',
            'name': 'Maria Silva',
            'skills': ['Python', 'Flask', 'PostgreSQL', 'Docker'],
            'exp_years': 4,
            'location': 'São Paulo'
        },
        {
            'id': 'C002',
            'name': 'João Santos',
            'skills': ['JavaScript', 'React', 'Node.js', 'MongoDB'],
            'exp_years': 3,
            'location': 'Rio de Janeiro'
        },
        {
            'id': 'C003',
            'name': 'Ana Costa',
            'skills': ['Java', 'Spring Boot', 'MySQL', 'Kafka'],
            'exp_years': 6,
            'location': 'Belo Horizonte'
        }
    ]
    
    vagas = [
        {
            'id': 'V001',
            'title': 'Desenvolvedor Python Backend',
            'req_skills': ['Python', 'Flask', 'PostgreSQL'],
            'min_exp': 3,
            'location': 'São Paulo'
        },
        {
            'id': 'V002',
            'title': 'Desenvolvedor Frontend React',
            'req_skills': ['JavaScript', 'React', 'Node.js'],
            'min_exp': 2,
            'location': 'Remoto'
        }
    ]
    
    resultado = run_matching(candidatos, vagas, seed=42, k_top=3)
    
    print("\n\033[92mRESULTADO DO MATCHING:\033[0m")
    for vaga_id, candidato_id in resultado['assignments'].items():
        vaga = next(v for v in vagas if v['id'] == vaga_id)
        cand = next(c for c in candidatos if c['id'] == candidato_id)
        print(f"   {vaga['title']} → {cand['name']}")
    
    return resultado


# ============================================================
# EXEMPLO 2: Comparando Diferentes Seeds (Determinismo)
# ============================================================

def exemplo_determinismo():
    """Demonstra comportamento com diferentes seeds"""
    print("\n" + "="*70)
    print("EXEMPLO 2: DETERMINISMO COM SEEDS")
    print("="*70)
    
    # Cenário com empate proposital
    candidatos = [
        {'id': 'C1', 'name': 'Alice', 'skills': ['Python', 'Django'], 'exp_years': 5, 'location': 'SP'},
        {'id': 'C2', 'name': 'Bob', 'skills': ['Python', 'Django'], 'exp_years': 5, 'location': 'SP'},
        {'id': 'C3', 'name': 'Carol', 'skills': ['Python', 'Django'], 'exp_years': 5, 'location': 'SP'},
    ]
    
    vagas = [
        {'id': 'V1', 'title': 'Dev Python', 'req_skills': ['Python', 'Django'], 'min_exp': 3, 'location': 'SP'},
    ]
    
    # Teste com mesmo seed (deve dar igual)
    print("\n\033[96mCom MESMO seed (42):\033[0m")
    for i in range(3):
        r = run_matching(candidatos, vagas, seed=42, k_top=2)
        print(f"   Execução {i+1}: {r['assignments']}")
    
    # Teste com seeds diferentes
    print("\n\033[93mCom seeds DIFERENTES:\033[0m")
    for seed in [10, 20, 30]:
        r = run_matching(candidatos, vagas, seed=seed, k_top=2)
        print(f"   Seed {seed}: {r['assignments']}")


# ============================================================
# EXEMPLO 3: Análise de Top-K por Vaga
# ============================================================

def exemplo_top_k():
    """Mostra os top candidatos para cada vaga"""
    print("\n" + "="*70)
    print("EXEMPLO 3: ANÁLISE TOP-K POR VAGA")
    print("="*70)
    
    candidatos = [
        {'id': 'C1', 'name': 'Expert Senior', 'skills': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Docker'], 'exp_years': 10, 'location': 'São Paulo'},
        {'id': 'C2', 'name': 'Pleno Completo', 'skills': ['Python', 'Django', 'PostgreSQL'], 'exp_years': 5, 'location': 'São Paulo'},
        {'id': 'C3', 'name': 'Junior Promissor', 'skills': ['Python', 'Django'], 'exp_years': 2, 'location': 'São Paulo'},
        {'id': 'C4', 'name': 'Generalista', 'skills': ['Python', 'Java', 'JavaScript'], 'exp_years': 4, 'location': 'Rio de Janeiro'},
        {'id': 'C5', 'name': 'Especialista DB', 'skills': ['PostgreSQL', 'MySQL', 'MongoDB'], 'exp_years': 7, 'location': 'São Paulo'},
    ]
    
    vagas = [
        {'id': 'V1', 'title': 'Desenvolvedor Python Senior', 'req_skills': ['Python', 'Django', 'PostgreSQL'], 'min_exp': 5, 'location': 'São Paulo'},
    ]
    
    resultado = run_matching(candidatos, vagas, seed=42, k_top=5)
    
    print("\n\033[92mTOP-5 CANDIDATOS PARA A VAGA:\033[0m")
    for vaga_id, top_candidatos in resultado['top_k_per_job'].items():
        vaga = vagas[0]
        print(f"\n   {vaga['title']}:")
        for i, (cand_id, score) in enumerate(top_candidatos, 1):
            cand = next(c for c in candidatos if c['id'] == cand_id)
            matched = "✓ SELECIONADO" if resultado['assignments'].get(vaga_id) == cand_id else ""
            print(f"   {i}. {cand['name']:20s} - Score: {score:.3f} {matched}")


# ============================================================
# EXEMPLO 4: Cenário com Vagas Não Preenchidas
# ============================================================

def exemplo_vagas_nao_preenchidas():
    """Cenário onde há mais vagas que candidatos"""
    print("\n" + "="*70)
    print("EXEMPLO 4: MAIS VAGAS QUE CANDIDATOS")
    print("="*70)
    
    candidatos = [
        {'id': 'C1', 'name': 'Dev Full Stack', 'skills': ['Python', 'JavaScript', 'React'], 'exp_years': 4, 'location': 'SP'},
        {'id': 'C2', 'name': 'Dev Backend', 'skills': ['Python', 'Django', 'PostgreSQL'], 'exp_years': 3, 'location': 'RJ'},
    ]
    
    vagas = [
        {'id': 'V1', 'title': 'Python Backend', 'req_skills': ['Python', 'Django'], 'min_exp': 2, 'location': 'SP'},
        {'id': 'V2', 'title': 'Python Senior', 'req_skills': ['Python', 'Django'], 'min_exp': 5, 'location': 'SP'},
        {'id': 'V3', 'title': 'React Developer', 'req_skills': ['JavaScript', 'React'], 'min_exp': 3, 'location': 'RJ'},
        {'id': 'V4', 'title': 'Full Stack', 'req_skills': ['Python', 'JavaScript'], 'min_exp': 3, 'location': 'SP'},
    ]
    
    resultado = run_matching(candidatos, vagas, seed=42, k_top=2)
    
    print(f"\n\033[95mESTATÍSTICAS:\033[0m")
    print(f"   Candidatos: {len(candidatos)}")
    print(f"   Vagas: {len(vagas)}")
    print(f"   Matches realizados: {len(resultado['assignments'])}")
    print(f"   Vagas não preenchidas: {len(vagas) - len(resultado['assignments'])}")
    
    print(f"\n✅ VAGAS PREENCHIDAS:")
    for vaga_id, cand_id in resultado['assignments'].items():
        vaga = next(v for v in vagas if v['id'] == vaga_id)
        cand = next(c for c in candidatos if c['id'] == cand_id)
        score = next(s for s, j, c in resultado['ranking'] if j == vaga_id and c == cand_id)
        print(f"   {vaga['title']:20s} → {cand['name']:20s} (Score: {score:.3f})")
    
    print(f"\n\033[91mVAGAS NÃO PREENCHIDAS:\033[0m")
    vagas_preenchidas = set(resultado['assignments'].keys())
    for vaga in vagas:
        if vaga['id'] not in vagas_preenchidas:
            print(f"   {vaga['title']}")


# ============================================================
# EXEMPLO 5: Análise de Score - O que Influencia?
# ============================================================

def exemplo_analise_score():
    """Analisa como cada fator influencia o score"""
    print("\n" + "="*70)
    print("EXEMPLO 5: ANÁLISE DE FATORES DO SCORE")
    print("="*70)
    
    vaga_referencia = {
        'id': 'V1',
        'title': 'Desenvolvedor Python',
        'req_skills': ['Python', 'Django', 'PostgreSQL'],
        'min_exp': 3,
        'location': 'São Paulo'
    }
    
    # Diferentes perfis para comparação
    candidatos_teste = [
        {
            'id': 'C1',
            'name': 'Match Perfeito',
            'skills': ['Python', 'Django', 'PostgreSQL'],
            'exp_years': 5,
            'location': 'São Paulo'
        },
        {
            'id': 'C2',
            'name': 'Sem Localização',
            'skills': ['Python', 'Django', 'PostgreSQL'],
            'exp_years': 5,
            'location': 'Rio de Janeiro'
        },
        {
            'id': 'C3',
            'name': 'Junior (Pouca Exp)',
            'skills': ['Python', 'Django', 'PostgreSQL'],
            'exp_years': 1,
            'location': 'São Paulo'
        },
        {
            'id': 'C4',
            'name': 'Skills Parciais',
            'skills': ['Python', 'Django'],
            'exp_years': 5,
            'location': 'São Paulo'
        },
        {
            'id': 'C5',
            'name': 'Apenas 1 Skill',
            'skills': ['Python'],
            'exp_years': 5,
            'location': 'São Paulo'
        }
    ]
    
    resultado = run_matching(candidatos_teste, [vaga_referencia], seed=42, k_top=5)
    
    print(f"\n\033[93mVAGA:\033[0m {vaga_referencia['title']}")
    print(f"   Skills requeridas: {', '.join(vaga_referencia['req_skills'])}")
    print(f"   Experiência mínima: {vaga_referencia['min_exp']} anos")
    print(f"   Localização: {vaga_referencia['location']}")
    
    print(f"\n\033[93mCOMPARAÇÃO DE CANDIDATOS:\033[0m")
    for _, top_cands in resultado['top_k_per_job'].items():
        for cand_id, score in top_cands:
            cand = next(c for c in candidatos_teste if c['id'] == cand_id)
            
            # Calcular componentes
            skill_overlap = len(set(cand['skills']) & set(vaga_referencia['req_skills']))
            skill_score = skill_overlap / len(vaga_referencia['req_skills'])
            exp_ratio = min(cand['exp_years'] / vaga_referencia['min_exp'], 2.0) / 2.0
            loc_match = "✓" if cand['location'] == vaga_referencia['location'] else "✗"
            
            print(f"\n   {cand['name']}:")
            print(f"      Score Total: {score:.3f}")
            print(f"      Skills: {skill_overlap}/{len(vaga_referencia['req_skills'])} ({skill_score*100:.0f}%) → {skill_score*0.6:.3f}")
            print(f"      Experiência: {cand['exp_years']}/{vaga_referencia['min_exp']} anos → {exp_ratio*0.3:.3f}")
            print(f"      Localização: {loc_match} → {0.1 if loc_match == '✓' else 0.0:.3f}")


# ============================================================
#  Export Resultados
# ============================================================

def exemplo_exportacao():
    """Mostra como exportar resultados para análise"""
    print("\n" + "="*70)
    print("EXEMPLO 6: EXPORTAÇÃO DE RESULTADOS")
    print("="*70)
    
    candidatos, vagas = gs2025.get_sample_data()
    resultado = run_matching(candidatos, vagas, seed=42, k_top=3)
    
    # Criar relatório em formato CSV
    print("\n RELATÓRIO DE MATCHES (formato CSV):")
    print("Vaga;Candidato;Score;Skills_Match;Exp_Candidate;Exp_Min;Location_Match")
    
    for vaga_id, cand_id in resultado['assignments'].items():
        vaga = next(v for v in vagas if v['id'] == vaga_id)
        cand = next(c for c in candidatos if c['id'] == cand_id)
        score = next(s for s, j, c in resultado['ranking'] if j == vaga_id and c == cand_id)
        
        skills_match = len(set(cand['skills']) & set(vaga['req_skills']))
        loc_match = 'Sim' if cand['location'] == vaga['location'] else 'Não'
        
        print(f"{vaga['title']};{cand['name']};{score:.3f};{skills_match}/{len(vaga['req_skills'])};{cand['exp_years']};{vaga['min_exp']};{loc_match}")
    
    print("\n Este formato pode ser salvo em CSV para análise em Excel/Power BI")


# ============================================================
# MENU PRINCIPAL
# ============================================================

def menu():
    """Menu interativo de exemplos"""
    exemplos = {
        '1': ('Matching Básico', exemplo_basico),
        '2': ('Determinismo com Seeds', exemplo_determinismo),
        '3': ('Análise Top-K', exemplo_top_k),
        '4': ('Vagas Não Preenchidas', exemplo_vagas_nao_preenchidas),
        '5': ('Análise de Score', exemplo_analise_score),
        '6': ('Exportação de Resultados', exemplo_exportacao),
        '7': ('Executar Todos', lambda: [f() for _, f in exemplos.values() if f != exemplos['7'][1]])
    }
    
    print("\n" + "#"*70)
    print("# EXEMPLOS DE USO - SkillMatch360")
    print("#"*70)
    print("\nEscolha um exemplo para executar:\n")
    
    for key, (desc, _) in exemplos.items():
        print(f"   {key}. {desc}")
    
    print("\n   0. Sair")
    
    escolha = input("\nOpção: ").strip()
    
    if escolha == '0':
        print("\nAté logo!")
        return
    
    if escolha in exemplos:
        exemplos[escolha][1]()
    else:
        print("\n\033[91mOpção inválida!\033[0m")
    
    input("\n\nPressione ENTER para continuar...")
    menu()


if __name__ == '__main__':
    # Executa todos os exemplos em sequência
    print("\n" + "#"*70)
    print("# DEMONSTRAÇÃO COMPLETA - SkillMatch360")
    print("# Executando todos os exemplos...")
    print("#"*70)
    
    exemplo_basico()
    input("\n[Pressione ENTER para próximo exemplo]")
    
    exemplo_top_k()
    input("\n[Pressione ENTER para próximo exemplo]")
    
    exemplo_vagas_nao_preenchidas()
    input("\n[Pressione ENTER para próximo exemplo]")
    
    exemplo_analise_score()
    input("\n[Pressione ENTER para próximo exemplo]")
    
    exemplo_exportacao()
    
    print("\n" + "#"*70)
    print("# DEMONSTRAÇÃO CONCLUÍDA!")
    print("#"*70)
    print("\n Dica: Execute 'python exemplos_uso.py' e escolha exemplos individuais")
    print("   ou modifique o código para seus próprios cenários!")

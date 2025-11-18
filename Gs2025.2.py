# -*- coding: utf-8 -*-
# 2ESS GRUPO: 
# Gustavo Atanazio - 559098           
# Matheus Alves - 555177 
# Larissa Pereira Biusse - 564068

"""
SkillMatch - Motor de matching entre vagas e candidatos
Hash Table + Grafo + Heap + BST + Algoritmo Guloso
"""

import sys
import heapq
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

# Garante encoding UTF-8 no terminal Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


# Estruturas de dados dos candidatos e vagas
@dataclass
class Candidate:
    id: str
    name: str
    skills: List[str]
    exp_years: int
    location: str


@dataclass
class Job:
    id: str
    title: str
    req_skills: List[str]
    min_exp: int
    location: str


# Nó da árvore binária de busca (BST)
class BSTNode:
    def __init__(self, score: float):
        self.score = score  # Score como chave de ordenação
        self.matches: List[Tuple[str, str]] = []  # Lista de matches com esse score
        self.left: Optional['BSTNode'] = None  # Subárvore esquerda (scores menores)
        self.right: Optional['BSTNode'] = None  # Subárvore direita (scores maiores)


# Árvore binária de busca para armazenar matches ordenados por score
class MatchBST:
    def __init__(self):
        self.root: Optional[BSTNode] = None
        self.total_matches = 0
    
    def insert(self, score: float, job_id: str, candidate_id: str):
        """Insere um match na BST"""
        self.root = self._insert_recursive(self.root, score, job_id, candidate_id)
        self.total_matches += 1
    
    def _insert_recursive(self, node: Optional[BSTNode], score: float, 
                         job_id: str, candidate_id: str) -> BSTNode:
        """Inserção recursiva na BST"""
        if node is None:
            new_node = BSTNode(score)
            new_node.matches.append((job_id, candidate_id))
            return new_node
        
        # Se o score é igual (com margem de erro), adiciona ao nó existente
        if abs(score - node.score) < 1e-9:
            node.matches.append((job_id, candidate_id))
        # Score menor vai para esquerda
        elif score < node.score:
            node.left = self._insert_recursive(node.left, score, job_id, candidate_id)
        # Score maior vai para direita
        else:
            node.right = self._insert_recursive(node.right, score, job_id, candidate_id)
        return node
    
    def _inorder_reverse(self, node: Optional[BSTNode], result: List):
        """Percorre a árvore em ordem decrescente (direita -> raiz -> esquerda)"""
        if node:
            self._inorder_reverse(node.right, result)
            for job_id, candidate_id in node.matches:
                result.append((node.score, job_id, candidate_id))
            self._inorder_reverse(node.left, result)
    
    def get_all_matches(self) -> List[Tuple[float, str, str]]:
        """Retorna todos os matches ordenados por score (maior para menor)"""
        result = []
        self._inorder_reverse(self.root, result)
        return result


# Função de scoring: calcula compatibilidade candidato-vaga
def calculate_score(candidate: Candidate, job: Job, 
                   skill_weight: float = 0.6,
                   exp_weight: float = 0.3,
                   loc_bonus: float = 0.1) -> float:
    """Calcula compatibilidade: 60% skills + 30% experiência + 10% localização"""
    # Calcula overlap de habilidades
    candidate_skills_set = set(s.lower() for s in candidate.skills)
    job_skills_set = set(s.lower() for s in job.req_skills)
    overlap = len(candidate_skills_set & job_skills_set)
    skill_score = overlap / max(1, len(job.req_skills))
    
    # Normaliza experiência (máximo 2x o requisito = score 1.0)
    exp_ratio = candidate.exp_years / max(1, job.min_exp)
    exp_score = min(exp_ratio, 2.0) / 2.0
    
    # Bônus se localização é igual
    location_bonus = loc_bonus if candidate.location.lower() == job.location.lower() else 0.0
    
    return skill_weight * skill_score + exp_weight * exp_score + location_bonus


# Motor principal do sistema de matching
class SkillMatch360:
    def __init__(self, seed: Optional[int] = None):
        # Hash Tables para armazenamento O(1)
        self.candidates: Dict[str, Candidate] = {}  # Hash: id -> candidato
        self.jobs: Dict[str, Job] = {}  # Hash: id -> vaga
        
        # Grafo bipartido: vaga -> [(candidato, score)]
        self.graph: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        
        # Heap (fila de prioridade) para algoritmo guloso
        self.heap: List[Tuple[float, str, str]] = []  # (-score, job_id, candidate_id)
        
        # BST para armazenar matches ordenados
        self.match_bst = MatchBST()
        
        # Hash Tables de controle de alocações
        self.job_assigned: Dict[str, str] = {}  # vaga -> candidato
        self.candidate_assigned: Dict[str, str] = {}  # candidato -> vaga
        
        # -----------------------Seed para reprodutibilidade--------------------------------------------
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # Estatísticas de execução
        self.stats = {
            'edges_created': 0,
            'edges_processed': 0,
            'matches_made': 0,
            'ties_broken': 0
        }
    
    def add_candidate(self, candidate: Candidate):
        """Adiciona candidato na hash table"""
        self.candidates[candidate.id] = candidate
    
    def add_job(self, job: Job):
        """Adiciona vaga na hash table"""
        self.jobs[job.id] = job
    
    def build_graph_and_heap(self, min_score: float = 0.0):
        """Constrói grafo bipartido e preenche heap com todas as arestas válidas"""
        print("\033[94m\n" + "─"*70)
        print("[CONSTRUÇÃO] Montando grafo bipartido e heap de prioridade...")
        
        # Para cada combinação vaga-candidato
        for job_id, job in self.jobs.items():
            for candidate_id, candidate in self.candidates.items():
                score = calculate_score(candidate, job)
                
                # Adiciona aresta se score mínimo atingido
                if score > min_score:
                    self.graph[job_id].append((candidate_id, score))  # Grafo
                    heapq.heappush(self.heap, (-score, job_id, candidate_id))  # Heap (negativo = max-heap)
                    self.stats['edges_created'] += 1
        
        print(f"  -> Arestas criadas: {self.stats['edges_created']}")
        print(f"  -> Vagas com conexões: {len(self.graph)}")
        print("─"*70 + "\033[0m")
    
    def greedy_matching(self, epsilon: float = 1e-6):
        """Algoritmo guloso: sempre escolhe a melhor aresta disponível"""
        print("\033[95m\n" + "─"*70)
        print("[MATCHING GULOSO] Processando alocações...")
        
        while self.heap:
            # Extrai aresta de maior score (guloso)
            neg_score, job_id, candidate_id = heapq.heappop(self.heap)
            score = -neg_score
            self.stats['edges_processed'] += 1
            
            # Pula se vaga ou candidato já alocados
            if job_id in self.job_assigned or candidate_id in self.candidate_assigned:
                continue
            
            # Coleta empates (scores muito próximos)
            tied_edges = [(score, job_id, candidate_id)]
            
            # Identifica todas as arestas empatadas
            while self.heap:
                next_neg_score, next_job, next_cand = self.heap[0]
                next_score = -next_neg_score
                
                if abs(next_score - score) <= epsilon:  # Empate detecta
                    heapq.heappop(self.heap)
                    tied_edges.append((next_score, next_job, next_cand))
                    self.stats['edges_processed'] += 1
                else:
                    break
            
            # Filtra apenas arestas ainda válidas
            valid_edges = [
                (s, j, c) for s, j, c in tied_edges
                if j not in self.job_assigned and c not in self.candidate_assigned
            ]
            
            if not valid_edges:
                continue
            
            # Desempate aleatório se necessário
            if len(valid_edges) > 1:
                self.stats['ties_broken'] += 1
                chosen_score, chosen_job, chosen_candidate = random.choice(valid_edges)
            else:
                chosen_score, chosen_job, chosen_candidate = valid_edges[0]
            
            # Registra o match escolhido
            self.job_assigned[chosen_job] = chosen_candidate  # vaga alocada
            self.candidate_assigned[chosen_candidate] = chosen_job  # candidato alocado
            self.match_bst.insert(chosen_score, chosen_job, chosen_candidate)  # ordenado
            self.stats['matches_made'] += 1
            
            # Reinsere empates não escolhidos de volta no heap
            for s, j, c in valid_edges:
                if (s, j, c) != (chosen_score, chosen_job, chosen_candidate):
                    if j not in self.job_assigned and c not in self.candidate_assigned:
                        heapq.heappush(self.heap, (-s, j, c))
        
        print(f"  -> Matches realizados: {self.stats['matches_made']}")
        print(f"  -> Arestas processadas: {self.stats['edges_processed']}")
        print(f"  -> Desempates executados: {self.stats['ties_broken']}")
        print("─"*70 + "\033[0m")
    
    def get_top_k_per_job(self, k: int = 3) -> Dict[str, List[Tuple[str, float]]]:
        """Retorna top-k melhores candidatos para cada vaga"""
        result = {}
        for job_id, edges in self.graph.items():
            sorted_edges = sorted(edges, key=lambda x: x[1], reverse=True)
            result[job_id] = [(cand_id, score) for cand_id, score in sorted_edges[:k]]
        return result
    
    def get_assignments(self) -> Dict[str, str]:
        """Retorna dicionário de alocações finais: vaga -> candidato"""
        return self.job_assigned.copy()
    
    def get_ranking(self) -> List[Tuple[float, str, str]]:
        """Retorna ranking completo de matches ordenado por score (usa BST)"""
        return self.match_bst.get_all_matches()
    
    def print_stats(self):
        print(f"\n\n\033[97m{'='*70}")
        print(f"  ESTATÍSTICAS FINAIS DO MATCHING")
        print(f"{'='*70}")
        print(f"  Candidatos carregados ........: {len(self.candidates)}")
        print(f"  Vagas carregadas ..............: {len(self.jobs)}")
        print(f"  Arestas criadas ...............: {self.stats['edges_created']}")
        print(f"  Arestas processadas ...........: {self.stats['edges_processed']}")
        print(f"  Matches realizados ............: {self.stats['matches_made']}")
        print(f"  Desempates executados .........: {self.stats['ties_broken']}")
        print(f"  Vagas NÃO preenchidas .........: {len(self.jobs) - len(self.job_assigned)}")
        print(f"  Candidatos NÃO alocados .......: {len(self.candidates) - len(self.candidate_assigned)}")
        print(f"{'='*70}\033[0m")


def run_matching(candidates: List[Dict], 
                jobs: List[Dict], 
                seed: Optional[int] = None,
                k_top: int = 3,
                min_score: float = 0.0) -> Dict:
    """Executa matching entre candidatos e vagas"""
    print(f"\n\n\033[96m{'='*70}")
    print(f"{'='*70}")
    print(f"  >>> SkillMatch360 - Motor de Matching <<<")
    print(f"  >>> Seed: {seed if seed is not None else 'Aleatório'} <<<")
    print(f"{'='*70}")
    print(f"{'='*70}\033[0m\n")
    
    engine = SkillMatch360(seed=seed)
    
    print("\033[93m\n" + "─"*70)
    print(f"[CARREGAMENTO] Candidatos: {len(candidates)}")
    for cand_data in candidates:
        engine.add_candidate(Candidate(**cand_data))
    
    print(f"[CARREGAMENTO] Vagas: {len(jobs)}")
    for job_data in jobs:
        engine.add_job(Job(**job_data))
    print("─"*70 + "\033[0m")
    
    engine.build_graph_and_heap(min_score=min_score)
    engine.greedy_matching()
    
    assignments = engine.get_assignments()
    ranking = engine.get_ranking()
    top_k_per_job = engine.get_top_k_per_job(k=k_top)
    
    engine.print_stats()
    
    print(f"\n\n\033[92m{'='*70}")
    print(f"  MATCHES REALIZADOS - Top {min(10, len(ranking))}")
    print(f"{'='*70}\033[0m")
    for i, (score, job_id, cand_id) in enumerate(ranking[:10], 1):
        job = engine.jobs[job_id]
        cand = engine.candidates[cand_id]
        print(f"  [{i}] Score: {score:.3f}")
        print(f"      Vaga ......: {job.title}")
        print(f"      Candidato .: {cand.name}")
        print()
    
    print(f"\n\033[93m{'='*70}")
    print(f"  TOP-{k_top} CANDIDATOS POR VAGA")
    print(f"{'='*70}\033[0m")
    for job_id, top_candidates in list(top_k_per_job.items())[:5]:
        job = engine.jobs[job_id]
        print(f"\n  >> Vaga: {job.title} ({job_id})")
        for i, (cand_id, score) in enumerate(top_candidates, 1):
            cand = engine.candidates[cand_id]
            matched = "*** ALOCADO ***" if job_id in assignments and assignments[job_id] == cand_id else ""
            print(f"     {i}. {cand.name:<25} Score: {score:.3f}  {matched}")
        print()
    
    return {
        'assignments': assignments,
        'ranking': ranking,
        'top_k_per_job': top_k_per_job,
        'stats': engine.stats,
        'engine': engine
    }

def get_sample_data():
    """Retorna dados de exemplo para testes (10 candidatos, 7 vagas)"""
    candidates = [
        {
            'id': 'C001',
            'name': 'Ana Silva',
            'skills': ['Python', 'Django', 'PostgreSQL', 'REST API'],
            'exp_years': 5,
            'location': 'São Paulo'
        },
        {
            'id': 'C002',
            'name': 'Bruno Costa',
            'skills': ['Java', 'Spring', 'MySQL', 'Microservices'],
            'exp_years': 3,
            'location': 'Rio de Janeiro'
        },
        {
            'id': 'C003',
            'name': 'Carla Mendes',
            'skills': ['JavaScript', 'React', 'Node.js', 'MongoDB'],
            'exp_years': 4,
            'location': 'São Paulo'
        },
        {
            'id': 'C004',
            'name': 'Daniel Oliveira',
            'skills': ['Python', 'Machine Learning', 'TensorFlow', 'Pandas'],
            'exp_years': 6,
            'location': 'Belo Horizonte'
        },
        {
            'id': 'C005',
            'name': 'Elena Rodrigues',
            'skills': ['React', 'TypeScript', 'CSS', 'HTML'],
            'exp_years': 2,
            'location': 'São Paulo'
        },
        {
            'id': 'C006',
            'name': 'Fernando Santos',
            'skills': ['Python', 'Django', 'Docker', 'AWS'],
            'exp_years': 7,
            'location': 'São Paulo'
        },
        {
            'id': 'C007',
            'name': 'Gabriela Lima',
            'skills': ['Java', 'Spring Boot', 'Kafka', 'Redis'],
            'exp_years': 4,
            'location': 'Curitiba'
        },
        {
            'id': 'C008',
            'name': 'Henrique Alves',
            'skills': ['JavaScript', 'Vue.js', 'Node.js', 'Express'],
            'exp_years': 3,
            'location': 'Porto Alegre'
        },
        {
            'id': 'C009',
            'name': 'Isabela Ferreira',
            'skills': ['Python', 'Data Science', 'Scikit-learn', 'SQL'],
            'exp_years': 5,
            'location': 'São Paulo'
        },
        {
            'id': 'C010',
            'name': 'João Pedro',
            'skills': ['C#', '.NET', 'Azure', 'SQL Server'],
            'exp_years': 6,
            'location': 'Brasília'
        }
    ]
    
    jobs = [
        {
            'id': 'J001',
            'title': 'Desenvolvedor Python Pleno',
            'req_skills': ['Python', 'Django', 'PostgreSQL'],
            'min_exp': 3,
            'location': 'São Paulo'
        },
        {
            'id': 'J002',
            'title': 'Desenvolvedor Java Sênior',
            'req_skills': ['Java', 'Spring', 'Microservices'],
            'min_exp': 5,
            'location': 'Rio de Janeiro'
        },
        {
            'id': 'J003',
            'title': 'Desenvolvedor Frontend React',
            'req_skills': ['React', 'JavaScript', 'TypeScript'],
            'min_exp': 2,
            'location': 'São Paulo'
        },
        {
            'id': 'J004',
            'title': 'Cientista de Dados',
            'req_skills': ['Python', 'Machine Learning', 'SQL'],
            'min_exp': 4,
            'location': 'São Paulo'
        },
        {
            'id': 'J005',
            'title': 'Desenvolvedor Full Stack',
            'req_skills': ['JavaScript', 'Node.js', 'React'],
            'min_exp': 3,
            'location': 'Porto Alegre'
        },
        {
            'id': 'J006',
            'title': 'Engenheiro de Software Backend',
            'req_skills': ['Python', 'Django', 'Docker'],
            'min_exp': 5,
            'location': 'São Paulo'
        },
        {
            'id': 'J007',
            'title': 'Desenvolvedor .NET',
            'req_skills': ['C#', '.NET', 'SQL Server'],
            'min_exp': 4,
            'location': 'Brasília'
        }
    ]
    
    return candidates, jobs


if __name__ == '__main__':
    candidates, jobs = get_sample_data()
    result = run_matching(candidates=candidates, jobs=jobs, seed=42, k_top=3, min_score=0.1)
    # SE QUISER TESTAR COM OUTRA SEED, ALTERE AQUI!!!!!
    print(f"\n\n\033[92m{'='*70}")
    print(f"{'='*70}")
    print(f"  *** EXECUÇÃO CONCLUÍDA COM SUCESSO! ***")
    print(f"{'='*70}")
    print(f"{'='*70}\033[0m")
    print(f"\n  Total de matches .....: {len(result['assignments'])}")
    print(f"  Melhor score .........: {result['ranking'][0][0]:.3f}" if result['ranking'] else "N/A")
    print(f"\n  NOTA: Para testar determinismo, execute com mesmo seed.")
    print(f"        Para aleatoriedade, use seed=None.\n")


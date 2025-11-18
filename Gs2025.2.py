# -*- coding: utf-8 -*-
# 2ESS GRUPO: 
# Gustavo Atanazio - 559098           
# Matheus Alves - 555177 
# Larissa Pereira Biusse - 564068

"""
SkillMatch360 - Motor de matching entre vagas e candidatos
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


class BSTNode:
    def __init__(self, score: float):
        self.score = score
        self.matches: List[Tuple[str, str]] = []
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None


class MatchBST:
    def __init__(self):
        self.root: Optional[BSTNode] = None
        self.total_matches = 0
    
    def insert(self, score: float, job_id: str, candidate_id: str):
        self.root = self._insert_recursive(self.root, score, job_id, candidate_id)
        self.total_matches += 1
    
    def _insert_recursive(self, node: Optional[BSTNode], score: float, 
                         job_id: str, candidate_id: str) -> BSTNode:
        if node is None:
            new_node = BSTNode(score)
            new_node.matches.append((job_id, candidate_id))
            return new_node
        
        if abs(score - node.score) < 1e-9:
            node.matches.append((job_id, candidate_id))
        elif score < node.score:
            node.left = self._insert_recursive(node.left, score, job_id, candidate_id)
        else:
            node.right = self._insert_recursive(node.right, score, job_id, candidate_id)
        return node
    
    def _inorder_reverse(self, node: Optional[BSTNode], result: List):
        if node:
            self._inorder_reverse(node.right, result)
            for job_id, candidate_id in node.matches:
                result.append((node.score, job_id, candidate_id))
            self._inorder_reverse(node.left, result)
    
    def get_all_matches(self) -> List[Tuple[float, str, str]]:
        result = []
        self._inorder_reverse(self.root, result)
        return result


def calculate_score(candidate: Candidate, job: Job, 
                   skill_weight: float = 0.6,
                   exp_weight: float = 0.3,
                   loc_bonus: float = 0.1) -> float:
    """Calcula compatibilidade: 60% skills + 30% experiência + 10% localização"""
    candidate_skills_set = set(s.lower() for s in candidate.skills)
    job_skills_set = set(s.lower() for s in job.req_skills)
    overlap = len(candidate_skills_set & job_skills_set)
    skill_score = overlap / max(1, len(job.req_skills))
    
    exp_ratio = candidate.exp_years / max(1, job.min_exp)
    exp_score = min(exp_ratio, 2.0) / 2.0
    
    location_bonus = loc_bonus if candidate.location.lower() == job.location.lower() else 0.0
    
    return skill_weight * skill_score + exp_weight * exp_score + location_bonus


class SkillMatch360:
    def __init__(self, seed: Optional[int] = None):
        self.candidates: Dict[str, Candidate] = {}
        self.jobs: Dict[str, Job] = {}
        self.graph: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self.heap: List[Tuple[float, str, str]] = []
        self.match_bst = MatchBST()
        self.job_assigned: Dict[str, str] = {}
        self.candidate_assigned: Dict[str, str] = {}
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.stats = {
            'edges_created': 0,
            'edges_processed': 0,
            'matches_made': 0,
            'ties_broken': 0
        }
    
    def add_candidate(self, candidate: Candidate):
        self.candidates[candidate.id] = candidate
    
    def add_job(self, job: Job):
        self.jobs[job.id] = job
    
    def build_graph_and_heap(self, min_score: float = 0.0):
        print("\n\033[96m[BUILD]\033[0m Construindo grafo e heap...")
        
        for job_id, job in self.jobs.items():
            for candidate_id, candidate in self.candidates.items():
                score = calculate_score(candidate, job)
                
                if score > min_score:
                    self.graph[job_id].append((candidate_id, score))
                    heapq.heappush(self.heap, (-score, job_id, candidate_id))
                    self.stats['edges_created'] += 1
        
        print(f"\033[96m[BUILD]\033[0m Criadas {self.stats['edges_created']} arestas válidas")
        print(f"\033[96m[BUILD]\033[0m Grafo: {len(self.graph)} vagas com conexões")
    
    def greedy_matching(self, epsilon: float = 1e-6):
        print("\n\033[93m[MATCH]\033[0m Iniciando matching guloso...")
        
        while self.heap:
            neg_score, job_id, candidate_id = heapq.heappop(self.heap)
            score = -neg_score
            self.stats['edges_processed'] += 1
            
            if job_id in self.job_assigned or candidate_id in self.candidate_assigned:
                continue
            
            tied_edges = [(score, job_id, candidate_id)]
            
            while self.heap:
                next_neg_score, next_job, next_cand = self.heap[0]
                next_score = -next_neg_score
                
                if abs(next_score - score) <= epsilon:
                    heapq.heappop(self.heap)
                    tied_edges.append((next_score, next_job, next_cand))
                    self.stats['edges_processed'] += 1
                else:
                    break
            
            valid_edges = [
                (s, j, c) for s, j, c in tied_edges
                if j not in self.job_assigned and c not in self.candidate_assigned
            ]
            
            if not valid_edges:
                continue
            
            if len(valid_edges) > 1:
                self.stats['ties_broken'] += 1
                chosen_score, chosen_job, chosen_candidate = random.choice(valid_edges)
            else:
                chosen_score, chosen_job, chosen_candidate = valid_edges[0]
            
            self.job_assigned[chosen_job] = chosen_candidate
            self.candidate_assigned[chosen_candidate] = chosen_job
            self.match_bst.insert(chosen_score, chosen_job, chosen_candidate)
            self.stats['matches_made'] += 1
            
            for s, j, c in valid_edges:
                if (s, j, c) != (chosen_score, chosen_job, chosen_candidate):
                    if j not in self.job_assigned and c not in self.candidate_assigned:
                        heapq.heappush(self.heap, (-s, j, c))
        
        print(f"\033[93m[MATCH]\033[0m Concluído: {self.stats['matches_made']} matches realizados")
        print(f"\033[93m[MATCH]\033[0m Arestas processadas: {self.stats['edges_processed']}")
        print(f"\033[93m[MATCH]\033[0m Desempates: {self.stats['ties_broken']}")
    
    def get_top_k_per_job(self, k: int = 3) -> Dict[str, List[Tuple[str, float]]]:
        result = {}
        for job_id, edges in self.graph.items():
            sorted_edges = sorted(edges, key=lambda x: x[1], reverse=True)
            result[job_id] = [(cand_id, score) for cand_id, score in sorted_edges[:k]]
        return result
    
    def get_assignments(self) -> Dict[str, str]:
        return self.job_assigned.copy()
    
    def get_ranking(self) -> List[Tuple[float, str, str]]:
        return self.match_bst.get_all_matches()
    
    def print_stats(self):
        print(f"\n{'='*60}")
        print("\033[95mESTATÍSTICAS DO MATCHING\033[0m")
        print(f"{'='*60}")
        print(f"Candidatos carregados: {len(self.candidates)}")
        print(f"Vagas carregadas: {len(self.jobs)}")
        print(f"Arestas criadas: {self.stats['edges_created']}")
        print(f"Arestas processadas: {self.stats['edges_processed']}")
        print(f"Matches realizados: {self.stats['matches_made']}")
        print(f"Desempates executados: {self.stats['ties_broken']}")
        print(f"Vagas não preenchidas: {len(self.jobs) - len(self.job_assigned)}")
        print(f"Candidatos não alocados: {len(self.candidates) - len(self.candidate_assigned)}")
        print(f"{'='*60}")


def run_matching(candidates: List[Dict], 
                jobs: List[Dict], 
                seed: Optional[int] = None,
                k_top: int = 3,
                min_score: float = 0.0) -> Dict:
    """Executa matching entre candidatos e vagas"""
    print(f"\n{'#'*60}")
    print("\033[92m# SkillMatch360 - Motor de Matching\033[0m")
    print(f"\033[92m# Seed: {seed if seed is not None else 'Aleatório'}\033[0m")
    print(f"{'#'*60}")
    
    engine = SkillMatch360(seed=seed)
    
    print(f"\n\033[94m[LOAD]\033[0m Carregando {len(candidates)} candidatos...")
    for cand_data in candidates:
        engine.add_candidate(Candidate(**cand_data))
    
    print(f"\033[94m[LOAD]\033[0m Carregando {len(jobs)} vagas...")
    for job_data in jobs:
        engine.add_job(Job(**job_data))
    
    engine.build_graph_and_heap(min_score=min_score)
    engine.greedy_matching()
    
    assignments = engine.get_assignments()
    ranking = engine.get_ranking()
    top_k_per_job = engine.get_top_k_per_job(k=k_top)
    
    engine.print_stats()
    
    print(f"\n{'='*60}")
    print(f"\033[92mMATCHES REALIZADOS (Top-{min(10, len(ranking))})\033[0m")
    print(f"{'='*60}")
    for i, (score, job_id, cand_id) in enumerate(ranking[:10], 1):
        job = engine.jobs[job_id]
        cand = engine.candidates[cand_id]
        print(f"{i}. Score: {score:.3f} | Vaga: {job.title} | Candidato: {cand.name}")
    
    print(f"\n{'='*60}")
    print(f"\033[92mTOP-{k_top} CANDIDATOS POR VAGA\033[0m")
    print(f"{'='*60}")
    for job_id, top_candidates in list(top_k_per_job.items())[:5]:
        job = engine.jobs[job_id]
        print(f"\nVaga: {job.title} ({job_id})")
        for i, (cand_id, score) in enumerate(top_candidates, 1):
            cand = engine.candidates[cand_id]
            matched = "[MATCHED]" if job_id in assignments and assignments[job_id] == cand_id else ""
            print(f"  {i}. {cand.name} - Score: {score:.3f} {matched}")
    
    return {
        'assignments': assignments,
        'ranking': ranking,
        'top_k_per_job': top_k_per_job,
        'stats': engine.stats,
        'engine': engine
    }

def get_sample_data():
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
    
    print(f"\n{'='*60}")
    print("\033[92mEXECUÇÃO CONCLUÍDA COM SUCESSO!\033[0m")
    print(f"{'='*60}")
    print(f"\nTotal de matches: {len(result['assignments'])}")
    print(f"Melhor score: {result['ranking'][0][0]:.3f}" if result['ranking'] else "N/A")
    print(f"\nPara testar determinismo, execute novamente com mesmo seed.")
    print(f"Para aleatoriedade, use seed=None.")


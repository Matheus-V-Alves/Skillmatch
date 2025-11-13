# 2ESS GRUPO: 
# Gustavo Atanazio - 559098           
# Matheus Alves - 555177 
# Larissa Pereira Biusse - 564068

"""
SkillMatch360 - Motor de Matching entre Vagas e Candidatos
Protótipo demonstrando estruturas de dados (hash table, grafo, heap, BST)
e algoritmo guloso com desempate randômico.
"""

import heapq
import random
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict


# ==================== ESTRUTURAS DE DADOS ====================

@dataclass
class Candidate:
    """Representa um candidato"""
    id: str
    name: str
    skills: List[str]
    exp_years: int
    location: str


@dataclass
class Job:
    """Representa uma vaga"""
    id: str
    title: str
    req_skills: List[str]
    min_exp: int
    location: str


class BSTNode:
    """Nó da Árvore de Busca Binária para armazenar matches por score"""
    def __init__(self, score: float):
        self.score = score
        self.matches: List[Tuple[str, str]] = []  # Lista de (job_id, candidate_id)
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None


class MatchBST:
    """Árvore de Busca Binária para armazenar matches ordenados por score"""
    def __init__(self):
        self.root: Optional[BSTNode] = None
        self.total_matches = 0
    
    def insert(self, score: float, job_id: str, candidate_id: str):
        """Insere um match na árvore"""
        self.root = self._insert_recursive(self.root, score, job_id, candidate_id)
        self.total_matches += 1
    
    def _insert_recursive(self, node: Optional[BSTNode], score: float, 
                         job_id: str, candidate_id: str) -> BSTNode:
        if node is None:
            new_node = BSTNode(score)
            new_node.matches.append((job_id, candidate_id))
            return new_node
        
        if abs(score - node.score) < 1e-9:  # Mesmo score
            node.matches.append((job_id, candidate_id))
        elif score < node.score:
            node.left = self._insert_recursive(node.left, score, job_id, candidate_id)
        else:
            node.right = self._insert_recursive(node.right, score, job_id, candidate_id)
        
        return node
    
    def get_top_k(self, k: int) -> List[Tuple[float, str, str]]:
        """Retorna os top-k matches em ordem decrescente de score"""
        result = []
        self._inorder_reverse(self.root, result)
        return result[:k]
    
    def _inorder_reverse(self, node: Optional[BSTNode], result: List):
        """Travessia in-order reversa (maior para menor)"""
        if node is None:
            return
        
        # Direita primeiro (maiores scores)
        self._inorder_reverse(node.right, result)
        
        # Adiciona todos os matches deste nó
        for job_id, candidate_id in node.matches:
            result.append((node.score, job_id, candidate_id))
        
        # Esquerda (menores scores)
        self._inorder_reverse(node.left, result)
    
    def get_all_matches(self) -> List[Tuple[float, str, str]]:
        """Retorna todos os matches ordenados por score (decrescente)"""
        result = []
        self._inorder_reverse(self.root, result)
        return result


# ==================== FUNÇÕES DE SCORING ====================

def calculate_score(candidate: Candidate, job: Job, 
                   skill_weight: float = 0.6,
                   exp_weight: float = 0.3,
                   loc_bonus: float = 0.1) -> float:
    """
    Calcula o score de compatibilidade entre candidato e vaga
    
    Fórmula:
    - skill_score: overlap de skills / total de skills requeridas [0..1]
    - exp_score: min(exp_candidate / min_exp_job, 2) / 2 [0..1]
    - loc_bonus: 0.1 se localização coincide, senão 0
    
    Score final = skill_weight * skill_score + exp_weight * exp_score + loc_bonus
    """
    # Score de habilidades
    candidate_skills_set = set(s.lower() for s in candidate.skills)
    job_skills_set = set(s.lower() for s in job.req_skills)
    overlap = len(candidate_skills_set & job_skills_set)
    skill_score = overlap / max(1, len(job.req_skills))
    
    # Score de experiência (cap em 2x o mínimo)
    exp_ratio = candidate.exp_years / max(1, job.min_exp)
    exp_score = min(exp_ratio, 2.0) / 2.0
    
    # Bônus de localização
    location_bonus = loc_bonus if candidate.location.lower() == job.location.lower() else 0.0
    
    # Score final
    total_score = (skill_weight * skill_score + 
                   exp_weight * exp_score + 
                   location_bonus)
    
    return total_score


# ==================== MOTOR DE MATCHING ====================

class SkillMatch360:
    """Motor principal de matching entre candidatos e vagas"""
    
    def __init__(self, seed: Optional[int] = None):
        # Hash tables para armazenamento
        self.candidates: Dict[str, Candidate] = {}
        self.jobs: Dict[str, Job] = {}
        
        # Grafo bipartido: job_id -> [(candidate_id, score), ...]
        self.graph: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        
        # Heap para processamento guloso (max-heap via scores negativos)
        self.heap: List[Tuple[float, str, str]] = []
        
        # BST para matches finais
        self.match_bst = MatchBST()
        
        # Alocações (hash tables)
        self.job_assigned: Dict[str, str] = {}  # job_id -> candidate_id
        self.candidate_assigned: Dict[str, str] = {}  # candidate_id -> job_id
        
        # Controle de aleatoriedade
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # Estatísticas
        self.stats = {
            'edges_created': 0,
            'edges_processed': 0,
            'matches_made': 0,
            'ties_broken': 0
        }
    
    def add_candidate(self, candidate: Candidate):
        """Adiciona um candidato à hash table"""
        self.candidates[candidate.id] = candidate
    
    def add_job(self, job: Job):
        """Adiciona uma vaga à hash table"""
        self.jobs[job.id] = job
    
    def build_graph_and_heap(self, min_score: float = 0.0):
        """
        Constrói o grafo bipartido e o heap com todas as arestas
        Apenas arestas com score > min_score são consideradas
        """
        print(f"\n[BUILD] Construindo grafo e heap...")
        
        for job_id, job in self.jobs.items():
            for candidate_id, candidate in self.candidates.items():
                score = calculate_score(candidate, job)
                
                if score > min_score:
                    # Adiciona ao grafo
                    self.graph[job_id].append((candidate_id, score))
                    
                    # Adiciona ao heap (negativo para max-heap)
                    heapq.heappush(self.heap, (-score, job_id, candidate_id))
                    
                    self.stats['edges_created'] += 1
        
        print(f"[BUILD] Criadas {self.stats['edges_created']} arestas válidas")
        print(f"[BUILD] Grafo: {len(self.graph)} vagas com conexões")
    
    def greedy_matching(self, epsilon: float = 1e-6):
        """
        Executa o algoritmo guloso de matching com desempate randômico
        
        epsilon: tolerância para considerar scores empatados
        """
        print(f"\n[MATCH] Iniciando matching guloso...")
        
        while self.heap:
            # Extrai a melhor aresta
            neg_score, job_id, candidate_id = heapq.heappop(self.heap)
            score = -neg_score
            self.stats['edges_processed'] += 1
            
            # Verifica se já alocados
            if job_id in self.job_assigned or candidate_id in self.candidate_assigned:
                continue
            
            # Coleta grupo de empate (arestas com score similar dentro de epsilon)
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
            
            # Filtra apenas pares válidos (ambos livres)
            valid_edges = [
                (s, j, c) for s, j, c in tied_edges
                if j not in self.job_assigned and c not in self.candidate_assigned
            ]
            
            if not valid_edges:
                continue
            
            # Desempate randômico se necessário
            if len(valid_edges) > 1:
                self.stats['ties_broken'] += 1
                chosen_score, chosen_job, chosen_candidate = random.choice(valid_edges)
            else:
                chosen_score, chosen_job, chosen_candidate = valid_edges[0]
            
            # Efetiva o match
            self.job_assigned[chosen_job] = chosen_candidate
            self.candidate_assigned[chosen_candidate] = chosen_job
            self.match_bst.insert(chosen_score, chosen_job, chosen_candidate)
            self.stats['matches_made'] += 1
            
            # Re-insere arestas não escolhidas que ainda podem ser úteis
            for s, j, c in valid_edges:
                if (s, j, c) != (chosen_score, chosen_job, chosen_candidate):
                    if j not in self.job_assigned and c not in self.candidate_assigned:
                        heapq.heappush(self.heap, (-s, j, c))
        
        print(f"[MATCH] Concluído: {self.stats['matches_made']} matches realizados")
        print(f"[MATCH] Arestas processadas: {self.stats['edges_processed']}")
        print(f"[MATCH] Desempates: {self.stats['ties_broken']}")
    
    def get_top_k_per_job(self, k: int = 3) -> Dict[str, List[Tuple[str, float]]]:
        """Retorna os top-k candidatos para cada vaga"""
        result = {}
        
        for job_id, edges in self.graph.items():
            # Ordena por score decrescente
            sorted_edges = sorted(edges, key=lambda x: x[1], reverse=True)
            # Pega top-k
            top_k = [(cand_id, score) for cand_id, score in sorted_edges[:k]]
            result[job_id] = top_k
        
        return result
    
    def get_assignments(self) -> Dict[str, str]:
        """Retorna o mapa de alocações job_id -> candidate_id"""
        return self.job_assigned.copy()
    
    def get_ranking(self) -> List[Tuple[float, str, str]]:
        """Retorna todos os matches ordenados por score (decrescente)"""
        return self.match_bst.get_all_matches()
    
    def print_stats(self):
        """Imprime estatísticas do matching"""
        print(f"\n{'='*60}")
        print(f"ESTATÍSTICAS DO MATCHING")
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


# ==================== FUNÇÃO PRINCIPAL ====================

def run_matching(candidates: List[Dict], 
                jobs: List[Dict], 
                seed: Optional[int] = None,
                k_top: int = 3,
                min_score: float = 0.0) -> Dict:
    """
    Função principal para executar o matching
    
    Args:
        candidates: Lista de dicts com dados dos candidatos
        jobs: Lista de dicts com dados das vagas
        seed: Seed para reprodutibilidade (None = aleatório)
        k_top: Número de top candidatos por vaga a retornar
        min_score: Score mínimo para criar uma aresta
    
    Returns:
        Dict com assignments, ranking, top_k_per_job, stats
    """
    print(f"\n{'#'*60}")
    print(f"# SkillMatch360 - Motor de Matching")
    print(f"# Seed: {seed if seed is not None else 'Aleatório'}")
    print(f"{'#'*60}")
    
    # Inicializa o motor
    engine = SkillMatch360(seed=seed)
    
    # Carrega candidatos
    print(f"\n[LOAD] Carregando {len(candidates)} candidatos...")
    for cand_data in candidates:
        candidate = Candidate(
            id=cand_data['id'],
            name=cand_data['name'],
            skills=cand_data['skills'],
            exp_years=cand_data['exp_years'],
            location=cand_data['location']
        )
        engine.add_candidate(candidate)
    
    # Carrega vagas
    print(f"[LOAD] Carregando {len(jobs)} vagas...")
    for job_data in jobs:
        job = Job(
            id=job_data['id'],
            title=job_data['title'],
            req_skills=job_data['req_skills'],
            min_exp=job_data['min_exp'],
            location=job_data['location']
        )
        engine.add_job(job)
    
    # Constrói grafo e heap
    engine.build_graph_and_heap(min_score=min_score)
    
    # Executa matching
    engine.greedy_matching()
    
    # Obtém resultados
    assignments = engine.get_assignments()
    ranking = engine.get_ranking()
    top_k_per_job = engine.get_top_k_per_job(k=k_top)
    
    # Estatísticas
    engine.print_stats()
    
    # Relatório de matches
    print(f"\n{'='*60}")
    print(f"MATCHES REALIZADOS (Top-{min(10, len(ranking))})")
    print(f"{'='*60}")
    for i, (score, job_id, cand_id) in enumerate(ranking[:10], 1):
        job = engine.jobs[job_id]
        cand = engine.candidates[cand_id]
        print(f"{i}. Score: {score:.3f} | Vaga: {job.title} | Candidato: {cand.name}")
    
    # Top-K por vaga
    print(f"\n{'='*60}")
    print(f"TOP-{k_top} CANDIDATOS POR VAGA")
    print(f"{'='*60}")
    for job_id, top_candidates in list(top_k_per_job.items())[:5]:
        job = engine.jobs[job_id]
        print(f"\nVaga: {job.title} ({job_id})")
        for i, (cand_id, score) in enumerate(top_candidates, 1):
            cand = engine.candidates[cand_id]
            matched = "✓ MATCHED" if job_id in assignments and assignments[job_id] == cand_id else ""
            print(f"  {i}. {cand.name} - Score: {score:.3f} {matched}")
    
    return {
        'assignments': assignments,
        'ranking': ranking,
        'top_k_per_job': top_k_per_job,
        'stats': engine.stats,
        'engine': engine
    }


# ==================== DADOS DE TESTE ====================

def get_sample_data():
    """Retorna dados de exemplo para teste"""
    
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


# ==================== EXECUÇÃO ====================

if __name__ == '__main__':
    # Obtém dados de exemplo
    candidates, jobs = get_sample_data()
    
    # Executa matching com seed para reprodutibilidade
    result = run_matching(
        candidates=candidates,
        jobs=jobs,
        seed=42,
        k_top=3,
        min_score=0.1
    )
    
    print(f"\n{'='*60}")
    print(f"EXECUÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"{'='*60}")
    print(f"\nTotal de matches: {len(result['assignments'])}")
    print(f"Melhor score: {result['ranking'][0][0]:.3f}" if result['ranking'] else "N/A")
    print(f"\nPara testar determinismo, execute novamente com mesmo seed.")
    print(f"Para aleatoriedade, use seed=None.")


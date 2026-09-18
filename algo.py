from collections import defaultdict
from puzzle import Puzzle
from multiprocessing import Pool


def hierholzer(component: list[Puzzle]) -> list[Puzzle]:
    adjacency: dict[str, list[Puzzle]] = defaultdict(list)
    for puzzle in component:
        adjacency[puzzle.head].append(puzzle)

    out_deg = defaultdict(int)
    in_deg = defaultdict(int)
    for puzzle in component:
        out_deg[puzzle.head] += 1
        in_deg[puzzle.tail] += 1

    # find start vertex for Euler path
    start_node = None
    for node in set(out_deg) | set(in_deg):
        if out_deg[node] - in_deg[node] == 1:
            start_node = node
            break
    
    #if not find (Euler cycle), choose any vertex with out edges
    if start_node is None:
        for node, edges in adjacency.items():
            if edges:
                start_node = node
                break
    
    # fallback in empty case
    if start_node is None:
        return []

    stack = [start_node]
    path_edges: list[Puzzle] = []
    edge_stack: list[Puzzle] = []

    current_adj = {node: list(edges) for node, edges in adjacency.items()}

    while stack:
        node = stack[-1]
        if current_adj.get(node):
            next_puzzle = current_adj[node].pop()
            stack.append(next_puzzle.tail)
            edge_stack.append(next_puzzle)
        else:
            stack.pop()
            if edge_stack:
                path_edges.append(edge_stack.pop())

    path_edges.reverse()
    return path_edges

def dfs_from_start(args: tuple) -> list[Puzzle]:
    graph, total, start_puzzle = args
    best_chain: list[Puzzle] = []

    def dfs(current_tail: str, used: set[int], chain: list[Puzzle]) -> None:
        nonlocal best_chain
        if len(chain) > len(best_chain):
            best_chain = chain[:]
        if len(chain) + (total - len(used)) <= len(best_chain):
            return
        for puzzle in graph.get(current_tail, []):
            puzzle_id = id(puzzle)
            if puzzle_id in used:
                continue
            used.add(puzzle_id)
            chain.append(puzzle)
            dfs(puzzle.tail, used, chain)
            chain.pop()
            used.remove(puzzle_id)

    dfs(start_puzzle.tail, {id(start_puzzle)}, [start_puzzle])
    return best_chain


def find_longest_chain(graph: dict[str, list[Puzzle]], all_puzzles: list[Puzzle]) -> list[Puzzle]:
    total = len(all_puzzles)
    tasks = [(graph, total, start_puzzle) for start_puzzle in all_puzzles]

    with Pool() as pool:
        results = pool.map(dfs_from_start, tasks)

    return max(results, key=len)
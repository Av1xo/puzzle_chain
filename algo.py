from puzzle import Puzzle

def find_longest_chain(graph: dict[str, list[Puzzle]], all_puzzles: list[Puzzle]) -> list[Puzzle]:
    best_chain: list[Puzzle] = list()
    total: int = len(all_puzzles)
    
    def dfs(current_tail: str, used: set[int], chain: list[Puzzle]) -> None:
        nonlocal best_chain
        
        if len(chain) > len(best_chain):
            best_chain = chain[:]
            print(best_chain)
        
        if len(chain) + (total - len(used)) <= len(best_chain):
            return
        
        for puzzle in graph.get(current_tail, list()):
            puzzle_id = id(puzzle)
            if puzzle_id in used:
                continue
            used.add(puzzle_id)
            chain.append(puzzle)
            dfs(puzzle.tail, used, chain)
            chain.pop()
            used.remove(puzzle_id)
    
    for start_puzzle in all_puzzles:
        used = {id(start_puzzle)}
        dfs(start_puzzle.tail, used, [start_puzzle])
        
    return best_chain
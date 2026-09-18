from collections import defaultdict
from pathlib import Path
from errors import *
from puzzle import Puzzle

def check_path(in_path: str) -> tuple[Path | None, bool]:
    path: Path = Path(in_path)
    
    if path.is_file() and path.suffix == ".txt":
        return path, True
    
    return None, False


def load_data(path: Path) -> list[str]:
    with open(path, "r") as data_file:
        data: list[str] = data_file.readlines()  

    if not data:
        raise EmptyDataError("[FAILED]: File empty")
    
    return data


def create_puzzles(data: list[str]) -> list[Puzzle]:
    puzzles: list[Puzzle] = list()
    
    for item in data:
        try:
            puzzle = Puzzle(item)
            puzzles.append(puzzle)
        except InvalidPuzzleError as e:
            print(e)
            continue
        
    return puzzles


def create_graph(puzzles: list[Puzzle]) -> dict[str, list[Puzzle]]:
    graph: dict[str, list[Puzzle]] = dict()
    
    for puzzle in puzzles:
        graph.setdefault(puzzle.head, []).append(puzzle)
        
    return graph

def find_components(all_puzzles: list[Puzzle]) -> list[list[Puzzle]]:
    parent: dict[str, str] = {}
    
    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    
    def union(x: str, y: str) -> None:
        parent.setdefault(x, x)
        parent.setdefault(y, y)
        root_x: str = find(x)
        root_y: str = find(y)
        
        if root_x != root_y:
            parent[root_x] = root_y
    
    for puzzle in all_puzzles:
        union(puzzle.head, puzzle.tail)
        
    groups: dict[str, list[Puzzle]] = {}
    for puzzle in all_puzzles:
        root = find(puzzle.head)
        groups.setdefault(root, []).append(puzzle)
    
    return list(groups.values())

def has_euler_path(component: list[Puzzle]) -> bool:
    out_deg: dict[str, int] = defaultdict(int)
    in_deg: dict[str, int] = defaultdict(int)
    
    for puzzle in component:
        out_deg[puzzle.head] += 1
        in_deg[puzzle.tail] += 1
    
    start_candidates = 0
    end_candidates = 0
    
    nodes = set(out_deg) | set(in_deg)
    for node in nodes:
        diff = out_deg[node] - in_deg[node]
        if diff == 1:
            start_candidates += 1
        elif diff == -1:
            end_candidates += 1
        elif diff != 0:
            return False
        
    return start_candidates <= 1 and end_candidates <= 1


def compare_result(puzzles: list[Puzzle]) -> str:
    result: str = puzzles[0].head + puzzles[0].body + puzzles[0].tail
    for puzzle in puzzles[1:]:
        result += puzzle.body + puzzle.tail
    return result
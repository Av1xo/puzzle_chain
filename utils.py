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
    
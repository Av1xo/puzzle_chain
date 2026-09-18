from sys import argv
from re import split
from puzzle import Puzzle
from utils import find_components, has_euler_path, load_data, check_path, create_puzzles, create_graph, compare_result
from algo import find_longest_chain, hierholzer
from errors import *

def get_data_from_path(args: list[str]) -> list[str]:
    data_path: str | None = args[1] if len(args) > 1 else None

    while(True):
        if data_path is None:
            data_path = input("Please, enter path to data file -> ")
        
        path, ok = check_path(data_path)
        
        if ok:
            try:
                return load_data(path)
            except EmptyDataError as e:
                print(e)
                data_path = None
                continue
        else:
            print(f"[FAILED]: Invalid path or not a .txt file: {data_path}")
            data_path = None


def prepare_data(data: list[str]) -> list[str]:
    return [
        item
        for data_line in data
        for item in split(r"[ ,;.]+", data_line.strip("\n ,;."))
        if item and len(item) >= 2 # (xx) + (xx)yyzz = xxyyzz
    ]
    
def find_longest_chain_in_component(component: list[Puzzle]) -> list[Puzzle]:
    graph = create_graph(component)
    return find_longest_chain(graph, component) 

def find_best_chain_overall(all_puzzles: list[Puzzle]) -> list[Puzzle]:
    components = find_components(all_puzzles)
    best_chain: list[Puzzle] = []

    for component in components:
        if has_euler_path(component):
            chain = hierholzer(component)
        else:
            chain = find_longest_chain_in_component(component)

        if len(chain) > len(best_chain):
            best_chain = chain

    return best_chain

def main(args: list[str]) -> None:
    data: list[str] = get_data_from_path(args)
    cleaned_data: list[str] = prepare_data(data)
    puzzles = create_puzzles(cleaned_data)
    best_chain: list[Puzzle] = find_best_chain_overall(puzzles)
    print(compare_result(best_chain))

if __name__ == "__main__":
    main(argv)
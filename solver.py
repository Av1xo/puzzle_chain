from re import split

from puzzle import Puzzle
from utils import (
    find_components,
    has_euler_path,
    create_puzzles,
    create_graph,
    compare_result,
)
from algo import find_longest_chain, hierholzer


def prepare_data(data: list[str]) -> list[str]:
    return [
        item
        for data_line in data
        for item in split(
            r"[ ,;.]+",
            data_line.strip("\n ,;.")
        )
        if item and len(item) >= 2
    ]


def find_longest_chain_in_component(
    component: list[Puzzle],
) -> list[Puzzle]:

    graph = create_graph(component)

    return find_longest_chain(graph, component)


def find_best_chain_overall(
    all_puzzles: list[Puzzle],
) -> list[Puzzle]:

    components = find_components(all_puzzles)

    best_chain: list[Puzzle] = []

    for component in components:
        if has_euler_path(component):
            chain = hierholzer(component)
            
            # If Girgoltzer failed to use all puzzle components,
            # run a guaranteed DFS
            if len(chain) != len(component):
                chain = find_longest_chain_in_component(component)
        else:
            chain = find_longest_chain_in_component(component)

        if len(chain) > len(best_chain):
            best_chain = chain

    return best_chain


def solve(data: list[str]) -> str:
    cleaned_data = prepare_data(data)
    puzzles = create_puzzles(cleaned_data)
    best_chain = find_best_chain_overall(puzzles)

    return compare_result(best_chain)
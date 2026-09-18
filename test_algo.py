import pytest

from puzzle import Puzzle
from utils import create_puzzles, create_graph, has_euler_path, find_components, compare_result
from algo import find_longest_chain, hierholzer
from solver import find_best_chain_overall, find_longest_chain_in_component


def validate_chain(chain: list[Puzzle]) -> bool:
    if not chain:
        return False

    seen_ids: set[int] = set()
    for puzzle in chain:
        pid = id(puzzle)
        if pid in seen_ids:
            return False
        seen_ids.add(pid)

    for i in range(len(chain) - 1):
        if chain[i].tail != chain[i + 1].head:
            return False

    return True

@pytest.fixture
def cycle_data() -> list[str]:
    return [
        "100020", "200030", "300040", "400050", "500010"
    ]

@pytest.fixture
def small_data() -> list[str]:
    return [
        "101120", "202230", "303340", "404450",   # ланцюжок A: 10-20-30-40-50 (4 пазли)
        "606670", "707780", "808890",             # ланцюжок B: 60-70-80-90 (3 пазли)
        "919596", "971298", "993401",             # сирітки
    ]


@pytest.fixture
def branched_data() -> list[str]:
    return [
        "100120", "200230", "300340", "400450", "500560",  # правильний шлях: 10-20-30-40-50-60 (5 пазлів)
        "100625", "250726",                                 # пастка №1 від вузла 10: 10-25-26 (2 пазли)
        "300835", "350936",                                 # пастка №2 від вузла 30: 10-20-30-35-36 (4 пазли)
        "771078",                                           # зайвий
    ]

@pytest.fixture
def disconnected_edges_data() -> list[str]:
    return ["100020", "200010", "300040", "400050"]


@pytest.fixture
def multigraph_data() -> list[str]:
    return ["100020", "100020", "200030", "300010"]


def test_fallback_to_dfs_on_disconnected_edges(disconnected_edges_data):
    puzzles = create_puzzles(disconnected_edges_data)
    chain = find_best_chain_overall(puzzles)
    assert len(chain) == 2
    assert validate_chain(chain)


def test_multigraph_duplicate_edges(multigraph_data):
    puzzles = create_puzzles(multigraph_data)
    chain = find_best_chain_overall(puzzles)
    assert validate_chain(chain)
    
    
def test_has_euler_path_true_for_cycle(cycle_data):
    puzzles = create_puzzles(cycle_data)
    components = find_components(puzzles)
    assert len(components) == 1
    assert has_euler_path(components[0]) is True


def test_hierholzer_finds_full_euler_cycle(cycle_data):
    puzzles = create_puzzles(cycle_data)
    components = find_components(puzzles)
    
    chain = hierholzer(components[0])

    assert len(chain) == 5
    assert validate_chain(chain)


def test_find_best_chain_overall_cycle_dataset(cycle_data):
    puzzles = create_puzzles(cycle_data)
    chain = find_best_chain_overall(puzzles)

    assert len(chain) == 5
    assert validate_chain(chain)


def test_puzzle_parses_head_body_tail():
    puzzle = Puzzle("123456")
    assert puzzle.head == "12"
    assert puzzle.body == "34"
    assert puzzle.tail == "56"


def test_puzzle_rejects_too_short_line():
    from errors import InvalidPuzzleError
    with pytest.raises(InvalidPuzzleError):
        Puzzle("1")


def test_create_puzzles_skips_invalid_lines(capsys):
    data = ["123456", "1", "654321"]
    puzzles = create_puzzles(data)
    assert len(puzzles) == 2


def test_find_components_separates_disjoint_chains(small_data):
    puzzles = create_puzzles(small_data)
    components = find_components(puzzles)

    sizes = sorted(len(c) for c in components)
    assert sizes == [1, 1, 1, 3, 4]


def test_has_euler_path_true_for_simple_chain(small_data):
    puzzles = create_puzzles(small_data)
    components = find_components(puzzles)
    chain_a = next(c for c in components if len(c) == 4)
    assert has_euler_path(chain_a) is True


def test_has_euler_path_false_for_branching(branched_data):
    puzzles = create_puzzles(branched_data)
    components = find_components(puzzles)
    main_component = max(components, key=len)
    assert has_euler_path(main_component) is False


def test_hierholzer_finds_full_euler_path(small_data):
    puzzles = create_puzzles(small_data)
    components = find_components(puzzles)
    chain_a = next(c for c in components if len(c) == 4)

    chain = hierholzer(chain_a)

    assert len(chain) == 4
    assert validate_chain(chain)


def test_find_longest_chain_picks_correct_branch(branched_data):
    puzzles = create_puzzles(branched_data)
    components = find_components(puzzles)
    main_component = max(components, key=len)
    graph = create_graph(main_component)

    chain = find_longest_chain(graph, main_component)

    assert len(chain) == 5
    assert validate_chain(chain)


def test_find_longest_chain_in_component_direct_call(branched_data):
    puzzles = create_puzzles(branched_data)
    components = find_components(puzzles)
    main_component = max(components, key=len)

    assert has_euler_path(main_component) is False
    chain = find_longest_chain_in_component(main_component)

    assert len(chain) == 5
    assert validate_chain(chain)


def test_find_best_chain_overall_small_dataset(small_data):
    puzzles = create_puzzles(small_data)
    chain = find_best_chain_overall(puzzles)

    assert len(chain) == 4
    assert validate_chain(chain)


def test_find_best_chain_overall_branched_dataset(branched_data):
    puzzles = create_puzzles(branched_data)
    chain = find_best_chain_overall(puzzles)

    assert len(chain) == 5
    assert validate_chain(chain)


def test_orphans_never_extend_chain(small_data):
    puzzles = create_puzzles(small_data)
    chain = find_best_chain_overall(puzzles)

    orphan_codes = {"91", "96", "97", "98", "99", "01"}
    chain_codes = {p.head for p in chain} | {p.tail for p in chain}
    assert not (orphan_codes & chain_codes)


def test_compare_result_builds_correct_string(small_data):
    puzzles = create_puzzles(small_data)
    chain = find_best_chain_overall(puzzles)
    result = compare_result(chain)

    assert result == "101120223033404450"
    assert len(result) == 6 + 4 * (len(chain) - 1)


def test_compare_result_matches_branched_expected(branched_data):
    puzzles = create_puzzles(branched_data)
    chain = find_best_chain_overall(puzzles)
    result = compare_result(chain)

    expected_pieces = ["100120", "200230", "300340", "400450", "500560"]
    expected = expected_pieces[0] + "".join(p[2:] for p in expected_pieces[1:])
    assert result == expected
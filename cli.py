from errors import EmptyDataError
from puzzle import Puzzle
from utils import check_path, load_data, create_puzzles, find_components, compare_result
from solver import prepare_data, find_best_chain_overall


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_CYAN = "\033[96m"


def color(text: str, value: str) -> str:
    return f"{value}{text}{Color.RESET}"

def make_box(title: str, items: list[tuple[str, str]]) -> str:
    item_lines_plain = [f"  {key}  {label}" for key, label in items]
    inner_width = max(len(title) + 4, *(len(line) for line in item_lines_plain)) + 2

    top = color("╭" + "─" * inner_width + "╮", Color.CYAN)
    bottom = color("╰" + "─" * inner_width + "╯", Color.CYAN)
    separator = color("├" + "─" * inner_width + "┤", Color.CYAN)
    border = color("│", Color.CYAN)

    title_line = border + color(title.center(inner_width), Color.BOLD) + border

    body_lines = []
    for key, label in items:
        plain = f"  {key}  {label}"
        padded = plain.ljust(inner_width)
        colored_content = padded.replace(key, color(key, Color.BRIGHT_CYAN), 1)
        body_lines.append(border + colored_content + border)

    return "\n".join([top, title_line, separator, *body_lines, bottom])


MENU_ITEMS = [
    ("1", "Load data from file"),
    ("2", "Find longest chain"),
    ("3", "Show result"),
    ("4", "Validate chain"),
    ("5", "Visualize chain"),
    ("6", "Exit"),
]

MENU = "\n" + make_box("Puzzle Chain Solver", MENU_ITEMS) + "\n"


def print_header() -> None:
    print()
    print(color(" Puzzle Chain Solver ".center(46, "─"), Color.BOLD))
    print()


def print_section(title: str) -> None:
    print()
    dashes = "─" * max(0, 40 - len(title))
    print(color(f"── {title} {dashes}", Color.CYAN))


def print_success(message: str) -> None:
    print(f"{color('✓', Color.BRIGHT_GREEN)} {message}")


def print_error(message: str) -> None:
    print(f"{color('✗', Color.BRIGHT_RED)} {message}")


def print_warning(message: str) -> None:
    print(f"{color('!', Color.BRIGHT_YELLOW)} {message}")


def print_info(label: str, value: object) -> None:
    print(f"  {color(f'{label:<14}', Color.DIM)} {value}")


def validate_chain(chain: list[Puzzle]) -> tuple[bool, str]:
    if not chain:
        return False, "The chain is empty."

    seen_ids: set[int] = set()
    for puzzle in chain:
        pid = id(puzzle)
        if pid in seen_ids:
            return False, f"Puzzle used twice: {puzzle.head}{puzzle.body}{puzzle.tail}"
        seen_ids.add(pid)

    for i in range(len(chain) - 1):
        if chain[i].tail != chain[i + 1].head:
            return False, (
                f"Broken link between puzzles {i} and {i + 1}: "
                f"{chain[i].tail} != {chain[i + 1].head}"
            )

    return True, "Chain is valid."


def load_data_flow(state: dict) -> None:
    print_section("Load data")

    data_path = input(f"  {color('Path to .txt file ->', Color.BOLD)} ").strip()
    path, ok = check_path(data_path)

    if not ok:
        print_error(f"Invalid path or file is not a .txt file: {data_path}")
        return

    try:
        raw_data = load_data(path)
    except EmptyDataError as error:
        print_error(str(error))
        return

    state["data"] = raw_data
    state["puzzles"] = None
    state["chain"] = None
    print_success(f"Loaded {len(raw_data)} lines from {data_path}")


def solve_flow(state: dict) -> None:
    if state["data"] is None:
        print_error("Load data first (option 1).")
        return

    print_section("Solving")

    cleaned = prepare_data(state["data"])
    puzzles = create_puzzles(cleaned)

    if not puzzles:
        print_error("No valid puzzles could be created from the input data.")
        return

    state["puzzles"] = puzzles
    state["chain"] = find_best_chain_overall(puzzles)

    components = find_components(puzzles)

    print_success("Search completed.")
    print_info("Puzzles", len(puzzles))
    print_info("Components", len(components))
    print_info("Best chain", len(state["chain"]))


def show_result_flow(state: dict) -> None:
    if state["chain"] is None:
        print_error("Find a chain first (option 2).")
        return

    print_section("Result")

    result = compare_result(state["chain"])
    print()
    print(f"  {color(result, Color.BRIGHT_GREEN)}")
    print()
    print_info("Chain length", f"{len(state['chain'])} puzzles")


def validate_flow(state: dict) -> None:
    if state["chain"] is None:
        print_error("Find a chain first (option 2).")
        return

    ok, message = validate_chain(state["chain"])
    (print_success if ok else print_error)(message)


def visualize_flow(state: dict) -> None:
    if state["chain"] is None:
        print_error("Find a chain first (option 2).")
        return

    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch
    except ImportError:
        print_error("Matplotlib is required: pip install matplotlib")
        return

    print_section("Chain visualization")

    chain = state["chain"]
    n = len(chain)

    per_row_raw = input("  Puzzles per row [10] -> ").strip()
    per_row = int(per_row_raw) if per_row_raw.isdigit() and int(per_row_raw) > 0 else 10

    box_w, box_h = 1.0, 0.6
    gap_x, gap_y = 0.35, 1.0
    rows = (n + per_row - 1) // per_row

    fig_w = min(per_row * (box_w + gap_x) + 1.5, 20)
    fig_h = rows * (box_h + gap_y) + 1

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    for i, puzzle in enumerate(chain):
        row, col = divmod(i, per_row)
        x = col * (box_w + gap_x)
        y = -row * (box_h + gap_y)
        full_number = puzzle.head + puzzle.body + puzzle.tail

        box = FancyBboxPatch(
            (x, y), box_w, box_h,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            linewidth=1, edgecolor="black", facecolor="#ffdede",
        )
        ax.add_patch(box)
        ax.text(
            x + box_w / 2, y + box_h / 2, full_number,
            ha="center", va="center", fontsize=9, fontweight="bold",
        )

        if col == 0:
            ax.text(
                x - 0.25, y + box_h / 2, str(i + 1),
                ha="right", va="center", fontsize=8, color="dimgray",
            )

        if i < n - 1 and (i + 1) // per_row == row:
            nx = (col + 1) * (box_w + gap_x)
            ny = y + box_h / 2
            ax.annotate(
                "", xy=(nx, ny), xytext=(x + box_w, ny),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.3),
            )
            mx = x + box_w + gap_x / 2
            ax.text(
                mx, ny + 0.14, puzzle.tail,
                ha="center", va="bottom", fontsize=7, color="dimgray",
            )

    ax.set_xlim(-0.7, per_row * (box_w + gap_x) + 0.3)
    ax.set_ylim(-rows * (box_h + gap_y) - 0.3, 0.9)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Biggest chain: {n} puzzles", fontsize=12, pad=12)
    plt.tight_layout()

    output_path = input("  Output image path [chain.png] -> ").strip() or "chain.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print_success(f"Chain saved to {output_path}")


ACTIONS = {
    "1": load_data_flow,
    "2": solve_flow,
    "3": show_result_flow,
    "4": validate_flow,
    "5": visualize_flow,
}


def run_cli() -> None:
    state: dict = {"data": None, "puzzles": None, "chain": None}

    print_header()

    while True:
        print(MENU)
        choice = input(color("  Select an option -> ", Color.BOLD)).strip()

        if choice == "6":
            print()
            print_success("Goodbye!")
            print()
            break

        action = ACTIONS.get(choice)
        if action is None:
            print_error("Unknown menu option.")
            continue

        try:
            action(state)
        except KeyboardInterrupt:
            print()
            print_warning("Operation interrupted.")
        except Exception as error:
            print_error(f"Unexpected error: {error}")


if __name__ == "__main__":
    run_cli()
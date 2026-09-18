from pathlib import Path
from errors import *


def check_path(in_path: str) -> tuple[Path | None, bool]:
    path: Path = Path(in_path)
    
    if path.is_file() and path.suffix == ".txt":
        return path, True
    
    return None, False


def load_data(path: Path) -> list[str]:
    with open(path, "r") as data_file:
        data: list[str] = data_file.readlines()  

    if not data:
        raise EmptyData("[FAILED]: File empty")
    
    return data
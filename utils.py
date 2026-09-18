from pathlib import Path


def check_path(in_path: str) -> tuple[Path | None, bool]:
    path: Path = Path(in_path)
    
    if path.is_file() and path.suffix == ".txt":
        return path, True
    
    return None, False


def load_data():
    pass
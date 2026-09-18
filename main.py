from sys import argv
from utils import load_data, check_path

def get_data_from_path(args: list[str]) -> list[str]:
    data_path: str | None = args[1] if len(args) > 1 else None

    while(True):
        if data_path is None:
            data_path = input("Please, enter path to data file -> ")
        
        path, ok = check_path(data_path)
        
        if ok:
            return load_data(path)

def main(args: list[str]) -> None:
    data: list[str] = get_data_from_path(args)


if __name__ == "__main__":
    main(argv)
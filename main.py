from sys import argv
from re import split
from utils import load_data, check_path
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
            except EmptyData as e:
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

def main(args: list[str]) -> None:
    data: list[str] = get_data_from_path(args)
    cleaned_data: list[str] = prepare_data(data)
    print(cleaned_data)


if __name__ == "__main__":
    main(argv)
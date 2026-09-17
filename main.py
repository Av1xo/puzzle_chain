from sys import argv
from utils import load_data, check_path


def main(args: list[str]) -> None:
    if len(args) > 1:
        data_path = args[1]
    else:
        data_path = input("Please, enter path to data file -> ")
        
    data = load_data()
    
if __name__ == "__main__":
    main(argv)
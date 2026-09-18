from errors import InvalidPuzzleError


class Puzzle:
    __head: str
    __body: str
    __tail: str
    
    def __init__(self, line: str) -> None:
        if len(line) < 2:
            raise InvalidPuzzleError("[FAILED] Invalid puzzle")
        
        self.__head = line[:2]
        self.__body = line[2:-2]
        self.__tail = line[-2:]
        
    @property
    def head(self):
        return self.__head
    
    @property
    def body(self):
        return self.__body
    
    @property
    def tail(self):
        return self.__tail
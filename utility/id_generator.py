from collections import defaultdict


class IdGenerator:
    def __init__(self) -> None:
        self._cur_id: int = 0

    def next_id(self) -> int:
        self._cur_id += 1
        return self._cur_id - 1

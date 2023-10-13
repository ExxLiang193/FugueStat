from collections import defaultdict


class IdGenerator:
    def __init__(self) -> None:
        self._cur_id: int = -1

    def next_id(self) -> int:
        self._cur_id += 1
        return self._cur_id

    def cur_id(self) -> int:
        return self._cur_id

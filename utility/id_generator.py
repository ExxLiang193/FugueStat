from typing import Generator


class IdGenerator:
    def __init__(self) -> None:
        self._cur_id: int = -1
        self.__generator = self._id_generator()

    def _id_generator(self) -> Generator[int, None, None]:
        while True:
            self._cur_id += 1
            yield self._cur_id

    def next_id(self) -> int:
        return next(self.__generator)

    def cur_id(self) -> int:
        return self._cur_id

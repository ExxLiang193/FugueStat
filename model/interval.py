from position import Position


class Interval:
    def __init__(self, left_position: Position, right_position: Position) -> None:
        self.value: int = right_position.abs_position - left_position.abs_position

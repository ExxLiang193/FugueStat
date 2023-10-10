from model.constants import AccidentalSymbol, ALTER_DEFAULT
from typing import Optional


class Accidental:
    ALTER_MAP = {
        -3: AccidentalSymbol.TripleFlat,
        -2: AccidentalSymbol.DoubleFlat,
        -1: AccidentalSymbol.SingleFlat,
        0: AccidentalSymbol.Natural,
        1: AccidentalSymbol.SingleSharp,
        2: AccidentalSymbol.DoubleSharp,
    }

    def __init__(self, alter: Optional[int]) -> None:
        self.alter: int = alter or ALTER_DEFAULT

    def __repr__(self) -> str:
        return self.ALTER_MAP.get(self.alter, self.ALTER_MAP[ALTER_DEFAULT])

from dataclasses import dataclass
from decimal import Decimal


MAX_VOICE_COUNT = 8
ALTER_DEFAULT = 0
OCTAVE_SUBDIVISIONS = 12


@dataclass(frozen=True)
class RawDuration:
    Note64th = Decimal("0.0625")
    Note32th = Decimal("0.125")
    Note16th = Decimal("0.25")
    Note8th = Decimal("0.5")
    NoteQuarter = Decimal("1")
    NoteHalf = Decimal("2")
    NoteWhole = Decimal("4")


@dataclass(frozen=True)
class AccidentalSymbol:
    TripleFlat = "bbb"
    DoubleFlat = "bb"
    SingleFlat = "b"
    Natural = ""
    SingleSharp = "#"
    DoubleSharp = "x"


@dataclass(frozen=True)
class BaseNoteName:
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"


@dataclass(frozen=True)
class Transformation:
    DEFAULT = "DEFAULT"
    REVERSAL = "REVERSAL"
    INVERSION = "INVERSION"
    REVERSAL_INVERSION = "REVERSAL_INVERSION"
    AUGMENTATION = "AUGMENTATION"
    DIMINUTION = "DIMINUTION"

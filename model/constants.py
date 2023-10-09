from dataclasses import dataclass
from decimal import Decimal


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

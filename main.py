import argparse
from time import time
from decimal import getcontext, FloatOperation


def enable_safe_float_handling():
    c = getcontext()
    c.traps[FloatOperation] = True


def parse_args():
    parser = argparse.ArgumentParser(description="Generates statistics for fugue")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    enable_safe_float_handling()
    args = parse_args()
    from model.note import Note
    from model.note_sequence import NoteSequence
    from decimal import Decimal
    from algorithm.model.skip_sequence import SkipSequence
    from pprint import PrettyPrinter

    t0 = time()
    seq_1 = NoteSequence(
        [
            Note.from_raw(40, Decimal("2")),
            Note.from_raw(38, Decimal("1")),
            Note.from_raw(37, Decimal("1")),
            Note.from_raw(35, Decimal("0.5")),
            Note.from_raw(33, Decimal("0.25")),
            Note.from_raw(32, Decimal("0.25")),
            # Note.from_raw(41, Decimal("1.5")),
            # Note.from_raw(None, Decimal("0.75")),
            # Note.from_raw(None, Decimal("1.75")),
            # Note.from_raw(29, Decimal("2.5")),
        ]
    ).optimize()
    seq_2 = NoteSequence(
        [
            Note.from_raw(None, Decimal("1")),
            Note.from_raw(2, Decimal("0.5")),
            Note.from_raw(3, Decimal("0.5")),
            Note.from_raw(4, Decimal("0.5")),
            Note.from_raw(5, Decimal("0.25")),
            Note.from_raw(6, Decimal("1.25")),
            Note.from_raw(7, Decimal("1")),
        ]
    ).optimize()
    pp = PrettyPrinter(indent=4)
    skip = SkipSequence([seq_1, seq_2])
    pp.pprint([(f"#{i}", voices) for i, voices in enumerate(skip.head)])
    print("Total time: {}".format(round(time() - t0, 5)))

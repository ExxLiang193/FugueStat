import argparse
import logging
import os
from decimal import FloatOperation, getcontext
from time import time
from typing import Dict, List

import numpy as np

from config import get_config
from model.note_sequence import NoteSequence
from workers.encoders.music_xml_encoder import MusicXMLEncoder
from workers.fugue_analyzer import FugueAnalyzer
from workers.parsers.musicxml.musicxml_parser import MusicXMLParser

np.set_printoptions(edgeitems=30, linewidth=100000)


def enable_safe_float_handling():
    c = getcontext()
    c.traps[FloatOperation] = True


def parse_args():
    parser = argparse.ArgumentParser(description="Generates statistics for fugue")
    parser.add_argument("filename", type=str)
    parser.add_argument("--logfile", type=str, default="log.txt")
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    enable_safe_float_handling()
    args = parse_args()
    config = get_config()

    log_level = {"level": logging.DEBUG} if args.debug else {"level": logging.ERROR}
    logging.basicConfig(
        filename=args.logfile, filemode="w", format="%(name)s - %(levelname)s - %(message)s", **log_level
    )
    logger = logging.getLogger(os.path.basename(__file__))

    t0 = time()

    music_xml_parser: MusicXMLParser = MusicXMLParser(args.filename)
    composition = music_xml_parser.to_composition()
    analyzer: FugueAnalyzer = FugueAnalyzer(composition, float(config["sensitivity"]), int(config["min-match"]))
    subject: NoteSequence = analyzer.extract_subject()
    matches: Dict[int, List[NoteSequence]] = analyzer.match_subject(subject)

    logger.debug(f"Total time: {round(time() - t0, 5)}")

    music_xml_encoder: MusicXMLEncoder = MusicXMLEncoder(args.filename)
    write = True
    if write:
        new_file_name = music_xml_encoder.from_analysis(matches, write=write)
        print(f"Output: {new_file_name}")

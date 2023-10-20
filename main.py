from __future__ import annotations

import argparse
import logging
import os
from decimal import FloatOperation, getcontext
from time import time
from typing import Dict, List, Tuple

import numpy as np

from config import get_config
from model.constants import Transformation
from model.note_sequence import NoteSequence
from workers.encoders.music_xml_encoder import MusicXMLEncoder
from workers.fugue_analyzer import FugueAnalyzer
from workers.parsers.musicxml.musicxml_parser import MusicXMLParser

np.set_printoptions(edgeitems=30, linewidth=100000)


def enable_safe_float_handling() -> None:
    c = getcontext()
    c.traps[FloatOperation] = True


def configure_logging(args):
    log_level = {"level": logging.DEBUG} if args.debug else {"level": logging.ERROR}
    logging.basicConfig(
        filename=args.logfile, filemode="w", format="%(name)s - %(levelname)s - %(message)s", **log_level
    )
    return logging.getLogger(os.path.basename(__file__))


def get_transformations(args) -> List[Transformation]:
    transformations: List[Transformation] = [Transformation.DEFAULT]
    if args.inversion:
        transformations.append(Transformation.INVERSION)
    return transformations


def parse_args():
    parser = argparse.ArgumentParser(description="Generates statistics and annotations for musical fugue.")
    parser.add_argument("filename", type=str, help="Path to music file to be ingested for analysis.")
    parser.add_argument("--logfile", type=str, default="log.txt", help="Path to log file for stdout and stderr.")
    parser.add_argument("--debug", action="store_true", help="Toggle debug mode for logging.")
    parser.add_argument("--inversion", action="store_true", help="Enable subject inversion detection.")
    return parser.parse_args()


if __name__ == "__main__":
    enable_safe_float_handling()
    args = parse_args()
    config = get_config()
    logger = configure_logging(args)
    transformations = get_transformations(args)

    t0 = time()

    music_xml_parser: MusicXMLParser = MusicXMLParser(args.filename)
    composition = music_xml_parser.to_composition()
    analyzer: FugueAnalyzer = FugueAnalyzer(composition, float(config["sensitivity"]), int(config["min-match"]))
    subject: NoteSequence = analyzer.extract_subject()
    matches: Dict[int, List[Tuple[NoteSequence, Transformation]]] = analyzer.match_subject(subject, transformations)

    logger.debug(f"Total time: {round(time() - t0, 5)}")

    music_xml_encoder: MusicXMLEncoder = MusicXMLEncoder(args.filename)
    write = True
    if write:
        new_file_name = music_xml_encoder.from_analysis(matches, write=write)
        print(f"Output: {new_file_name}")

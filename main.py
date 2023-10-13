import argparse
from time import time
from decimal import getcontext, FloatOperation
from model.note_sequence import NoteSequence
from pprint import PrettyPrinter
from workers.parsers.music_xml_parser import MusicXMLParser
from workers.encoders.music_xml_encoder import MusicXMLEncoder
from workers.fugue_analyzer import FugueAnalyzer
from config import get_config
from typing import List, Dict


def enable_safe_float_handling():
    c = getcontext()
    c.traps[FloatOperation] = True


def parse_args():
    parser = argparse.ArgumentParser(description="Generates statistics for fugue")
    parser.add_argument("file_name", type=str)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    enable_safe_float_handling()
    args = parse_args()
    config = get_config()

    pp = PrettyPrinter(indent=4)

    t0 = time()

    music_xml_parser: MusicXMLParser = MusicXMLParser(args.file_name)
    composition = music_xml_parser.to_composition()
    analyzer: FugueAnalyzer = FugueAnalyzer(composition, float(config["sensitivity"]), int(config["min-match"]))
    subject: NoteSequence = analyzer.extract_subject()
    matches: Dict[int, List[NoteSequence]] = analyzer.match_subject(subject)
    # for voice in matches.keys():
    #     print("#" * voice, voice)
    #     for match in matches[voice]:
    #         pp.pprint(match.notes)
    music_xml_encoder: MusicXMLEncoder = MusicXMLEncoder(args.file_name)
    write = True
    if write:
        new_file_name = music_xml_encoder.from_analysis(matches, write=write)
        print(f"Output: {new_file_name}")

    print("Total time: {}".format(round(time() - t0, 5)))

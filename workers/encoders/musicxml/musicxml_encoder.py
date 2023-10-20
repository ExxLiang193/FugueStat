from __future__ import annotations

import xml.etree.ElementTree as ET
from functools import reduce
from typing import TYPE_CHECKING, Dict, List, Tuple, Set

from utility.colour_generator import ColourGenerator

if TYPE_CHECKING:
    from model.constants import Transformation
    from model.note_sequence import NoteSequence
    from model.note import Note


class MusicXMLEncoder:
    NEW_FILE_SUFFIX = "_annotated"
    FILE_EXTENSION = ".musicxml"

    def __init__(self, file_name: str, version: str = "3.1") -> None:
        self.file_name: str = file_name
        self._version: str = version

    def _get_colour_map(self, transformations: Set[Transformation]) -> Dict[Transformation, str]:
        return {transformation: ColourGenerator.get_new_colour() for transformation in transformations}

    def from_analysis(self, matches: Dict[int, List[Tuple[NoteSequence, Transformation]]], write=True) -> str:
        xml_root: ET.Element = ET.parse(self.file_name).getroot()
        measures: List[ET.Element] = xml_root.findall("part/measure")
        flattened_matches: Dict[int, List[Tuple[Note, Transformation]]] = {
            voice: list(
                reduce(lambda acc, item: acc + [(note, item[1]) for note in item[0].notes], matches[voice], list())
            )
            for voice in matches
        }
        transformations: Set[Transformation] = {
            transformation for voice_idx in matches for _, transformation in matches[voice_idx]
        }
        matches_voice_pos: Dict[int, int] = {voice: 0 for voice in matches.keys()}
        file_note_id_pos: Dict[int, int] = {voice: 0 for voice in matches.keys()}
        colour_map: Dict[Transformation, str] = self._get_colour_map(transformations)
        for measure_element in measures:
            for note_element in measure_element.findall("note"):
                voice_idx: int = int(note_element.find("voice").text)
                cur_note_element_id = file_note_id_pos[voice_idx]
                note_idx = matches_voice_pos[voice_idx]
                if note_idx >= len(flattened_matches[voice_idx]):
                    file_note_id_pos[voice_idx] += 1
                    continue
                if flattened_matches[voice_idx][note_idx][0].is_tagged():
                    cur_matched_note_ids = flattened_matches[voice_idx][note_idx][0].ids
                else:
                    matches_voice_pos[voice_idx] += 1
                    continue
                if cur_note_element_id in cur_matched_note_ids:
                    note_element.attrib["color"] = colour_map[flattened_matches[voice_idx][note_idx][1]]
                if cur_note_element_id >= cur_matched_note_ids[-1]:
                    matches_voice_pos[voice_idx] += 1
                file_note_id_pos[voice_idx] += 1
        new_xml_tree = ET.ElementTree(xml_root)
        new_file_name = self.file_name.rstrip(self.FILE_EXTENSION) + self.NEW_FILE_SUFFIX + self.FILE_EXTENSION
        if write:
            new_xml_tree.write(new_file_name)
        return new_file_name

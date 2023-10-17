from __future__ import annotations
import xml.etree.ElementTree as ET
from collections import defaultdict
from model.composition import Composition
from model.note_sequence import NoteSequence
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List, Set
from utility.id_generator import IdGenerator
from workers.parsers.musicxml.musicxml_factory import MusicXMLFactory

if TYPE_CHECKING:
    from model.time_signature import TimeSignature


class MusicXMLParser:
    FILE_EXTENSION = ".musicxml"

    def __init__(self, file_name: str, version: str = "3.1") -> None:
        assert file_name.endswith(self.FILE_EXTENSION), f"Not a {self.FILE_EXTENSION} file!"
        self.file_name: str = file_name
        self._version: str = version
        self._note_id_generators: Dict[int, IdGenerator] = defaultdict(IdGenerator)

    def _get_voices(self, measure_elements: List[ET.Element]) -> Set:
        return set(
            int(note_element.find("voice").text)
            for measure_element in measure_elements
            for note_element in measure_element.findall("note")
        )

    def to_composition(self) -> Composition:
        xml_root: ET.Element = ET.parse(self.file_name).getroot()
        measures: List[ET.Element] = xml_root.findall("part/measure")

        voices: Set[int] = self._get_voices(measures)
        voice_note_sequences: Dict[int, NoteSequence] = defaultdict(NoteSequence)

        duration_scale: Decimal = Decimal(measures[0].find("attributes/divisions").text)

        musicxml_factory: MusicXMLFactory = MusicXMLFactory(duration_scale)
        cur_time_signature: TimeSignature = musicxml_factory.build_time_signature(measures[0].find("attributes/time"))

        for measure_element in measures:
            if (time_element := measure_element.find("attributes/time")) is not None:
                cur_time_signature: TimeSignature = musicxml_factory.build_time_signature(time_element)

            voice_in_measure: Dict[int, bool] = {voice: False for voice in voices}

            for note_element in measure_element.findall("note"):
                voice_idx: int = int(note_element.find("voice").text)
                voice_in_measure[voice_idx] = True
                note_id: int = self._note_id_generators[voice_idx].next_id()

                if note_element.find("rest") is not None:
                    voice_note_sequences[voice_idx].append_note(musicxml_factory.build_rest(note_element, note_id))
                elif (tie_element := note_element.find("tie")) is not None and tie_element.attrib["type"] == "stop":
                    voice_note_sequences[voice_idx].merge_last_note(musicxml_factory.build_note(note_element, note_id))
                else:
                    voice_note_sequences[voice_idx].append_note(musicxml_factory.build_note(note_element, note_id))

            for voice_idx in voices:
                if not voice_in_measure[voice_idx]:
                    voice_note_sequences[voice_idx].append_note(musicxml_factory.build_default_rest(cur_time_signature))

        return Composition(voice_note_sequences)

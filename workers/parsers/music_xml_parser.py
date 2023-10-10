from __future__ import annotations
import xml.etree.ElementTree as ET
from collections import defaultdict
from model.composition import Composition
from model.note_sequence import NoteSequence
from model.note import Note
from model.note_name import NoteName
from decimal import Decimal
from typing import TYPE_CHECKING, Iterable, Dict

if TYPE_CHECKING:
    from model.position import Position


class MusicXMLParser:
    def __init__(self, file_name: str, version: str = "3.1"):
        self.file_name: str = file_name
        self.version: str = version

    def _create_note(self, note_element: ET.Element, duration_scale: Decimal) -> Note:
        pitch_element: ET.Element = note_element.find("pitch")
        step: str = pitch_element.find("step").text
        alter: int = 0 if pitch_element.find("alter") is None else int(pitch_element.find("alter").text)
        octave: int = int(pitch_element.find("octave").text)
        position: Position = NoteName.from_raw(step, alter).as_position(octave)
        duration: Decimal = Decimal(note_element.find("duration").text) / duration_scale
        return Note.from_raw(position.abs_position, duration)

    def _create_rest(self, note_element: ET.Element, duration_scale: Decimal) -> Note:
        duration = Decimal(note_element.find("duration").text) / duration_scale
        return Note.from_raw(None, duration)

    def to_composition(self) -> Composition:
        voices: Dict[int, NoteSequence] = defaultdict(NoteSequence)
        xml_root: ET.Element = ET.parse(self.file_name).getroot()
        measures: Iterable[ET.Element] = xml_root.findall("part/measure")
        duration_scale: Decimal = Decimal(measures[0].find("attributes/divisions").text)
        for measure_element in measures:
            for note_element in measure_element.findall("note"):
                voice_idx: int = int(note_element.find("voice").text)
                if note_element.find("rest") is not None:
                    voices[voice_idx].append_note(self._create_rest(note_element, duration_scale))
                elif (tie_element := note_element.find("tie")) is not None and tie_element.attrib["type"] == "stop":
                    voices[voice_idx].merge_last_note(self._create_note(note_element, duration_scale))
                else:
                    voices[voice_idx].append_note(self._create_note(note_element, duration_scale))
        return Composition(voices)

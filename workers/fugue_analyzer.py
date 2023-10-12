from algorithm.model.skip_sequence import SkipSequence
from model.composition import Composition
from model.note_sequence import NoteSequence
from model.exceptions import InvalidFugueFormError
from typing import Tuple, List
from workers.stream_matcher import StreamMatcher
from algorithm.model.distance_metrics import DistanceMetrics


class FugueAnalyzer:
    def __init__(self, composition: Composition, sensitivity: float, min_match: int) -> None:
        self.composition: Composition = composition
        self.skip_sequence: SkipSequence = SkipSequence(composition.voices)
        self.sensitivity: float = sensitivity
        self.min_match: int = min_match

    def _get_leading_voice(self) -> Tuple[int, int]:
        first_notes = tuple(voice for voice, skip_node in self.skip_sequence[0].items() if not skip_node.note.is_rest())
        if len(first_notes) == 0:
            leading_voice, moment = sorted(
                [(voice, self.skip_sequence.next_note(0, voice)) for voice in self.skip_sequence[0].keys()],
                key=lambda pair: pair[1],
            )[0]
        elif len(first_notes) == 1:
            leading_voice, moment = first_notes[0], 0
        else:
            raise InvalidFugueFormError("Composition should feature only one leading fugal subject.")

        return leading_voice, moment

    def extract_subject(self) -> NoteSequence:
        leading_voice, moment = self._get_leading_voice()
        subject: NoteSequence = NoteSequence()
        while self.skip_sequence.is_solo(moment):
            subject.append_note(self.skip_sequence.get_note(moment, leading_voice))
            moment = self.skip_sequence.next_moment(moment, leading_voice)
        return subject

    def match_subject(self, subject: NoteSequence, voice: int) -> List[NoteSequence]:
        stream: NoteSequence = self.skip_sequence.voices[voice]
        metrics = [
            DistanceMetrics.replacement_with_penalty,
            DistanceMetrics.insertion_without_expansion,
            DistanceMetrics.insertion_with_expansion,
            DistanceMetrics.deletion_without_compression,
            DistanceMetrics.deletion_with_compression,
        ]
        stream_matcher = StreamMatcher(stream, 1, self.sensitivity, self.min_match, metrics)
        match, length = stream_matcher.match_next(subject, 1)
        return [match]
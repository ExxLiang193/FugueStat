from algorithm.model.skip_sequence import SkipSequence
from model.composition import Composition
from model.note_sequence import NoteSequence
from model.exceptions import InvalidFugueFormError
from typing import Tuple, List, Dict
from workers.stream_matcher import StreamMatcher
from algorithm.model.distance_metrics import DistanceMetrics


class FugueAnalyzer:
    def __init__(self, composition: Composition, sensitivity: float, min_match: int) -> None:
        assert sensitivity >= 0
        assert min_match >= 1
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

    def match_subject(self, subject: NoteSequence) -> Dict[int, List[NoteSequence]]:
        distance_metric: DistanceMetrics = DistanceMetrics(rest_penalty_factor=5, inversion_penalty_factor=2)
        metrics = [
            distance_metric.replacement_with_penalty,
            distance_metric.insertion_without_expansion,
            distance_metric.insertion_with_expansion,
            distance_metric.deletion_without_compression,
            distance_metric.deletion_with_compression,
        ]
        all_results = dict()
        for voice in self.skip_sequence.voices.keys():
            stream = self.skip_sequence.voices[voice]
            stream_matcher = StreamMatcher(stream, 1, self.sensitivity, self.min_match, metrics)
            result = stream_matcher.match_all(subject)
            for sequence in result:
                sequence.lstrip_rests()
            all_results[voice] = result
        return all_results

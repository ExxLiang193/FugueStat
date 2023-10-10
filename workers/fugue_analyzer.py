from algorithm.model.skip_sequence import SkipSequence
from model.composition import Composition
from model.note_sequence import NoteSequence


class FugueAnalyzer:
    def __init__(self, composition: Composition) -> None:
        self.composition: Composition = composition
        self.skip_sequence: SkipSequence = SkipSequence(composition.voices)

    def get_subject(self) -> NoteSequence:
        first_notes = tuple(voice for voice, skip_node in self.skip_sequence[0].items() if not skip_node.note.is_rest())
        if len(first_notes) == 0:
            leading_voice, moment = sorted(
                [(voice, self.skip_sequence.next_note(0, voice)) for voice in self.skip_sequence[0].keys()],
                key=lambda pair: pair[1],
            )[0]
        elif len(first_notes) == 1:
            leading_voice, moment = first_notes[0], 0
        else:
            raise Exception("Composition should feature only one leading fugal subject.")

        subject: NoteSequence = NoteSequence()
        while self.skip_sequence.is_solo(moment):
            subject.append_note(self.skip_sequence.get_note(moment, leading_voice))
            moment = self.skip_sequence.next_moment(moment, leading_voice)
        return subject

from Options import Option, ValueOption, TriggerOption, OnOffOption
import mido
from enum import Enum

class MidiControllerColumn:
    midi_ids: tuple[int, int, int, int, int, int]
    control_options: tuple[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]
    mapping: dict[int, Option]

    def __init__(self, 
                 midi_ids: tuple[int, int, int, int, int, int], 
                 control_options: tuple[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]|None
                 ):
        self.midi_ids = midi_ids
        self.control_options = control_options
        self.change_mapping(control_options=control_options)

    def change_mapping(self, control_options: tuple[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]):
        self.mapping = {}
        self.control_options = control_options
        if self.control_options is None:
            return
        for index in range(len(self.midi_ids)):
            midi_id = self.midi_ids[index]
            control_option = self.control_options[index]
            self.mapping[midi_id] = control_option

    def process_midi_event(self, midi_event: mido.Message) -> Option|None:
        if midi_event.type == "control_change":
            return self.mapping[midi_event.control]
        if midi_event.type == "note_on":
            return self.mapping[midi_event.note]
        return None


class MidiDevice(Enum):
    NOVATION_LAUNCHCONTROL_XL = {
        "name_prefix": "Launch Control XL:Launch Control XL Launch Contro",
        "name_suffix": ":0",
        "channels": (
            MidiControllerColumn(midi_ids=(13, 29, 49, 77, 41, 73), control_options=None),
            MidiControllerColumn(midi_ids=(14, 30, 50, 78, 42, 74), control_options=None),
            MidiControllerColumn(midi_ids=(15, 31, 51, 79, 43, 75), control_options=None),
            MidiControllerColumn(midi_ids=(16, 32, 52, 80, 44, 76), control_options=None),
            MidiControllerColumn(midi_ids=(17, 33, 53, 81, 57, 89), control_options=None),
            MidiControllerColumn(midi_ids=(18, 34, 54, 82, 58, 90), control_options=None),
            MidiControllerColumn(midi_ids=(19, 35, 55, 83, 59, 91), control_options=None),
            MidiControllerColumn(midi_ids=(20, 36, 56, 84, 60, 91), control_options=None),
        ),
        "extra_buttons": (104, 105, 106, 107, 108)
    }

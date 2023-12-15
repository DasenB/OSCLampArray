from Options import Option, ValueOption, TriggerOption, OnOffOption
import mido
import asyncio
from enum import Enum

class MidiControllerColumn:
    midi_ids: list[int]
    control_options: list[Option]|None
    mapping: dict[int, Option]
    name: str

    def __init__(self, name: str = "", midi_ids: list[int] = [], control_options: list[Option]|None = None):
        self.midi_ids = midi_ids
        self.control_options = control_options
        self.name = name
        self.change_mapping(name=self.name, control_options=control_options)

    def change_mapping(self, name: str, control_options: list[Option]|None):
        self.mapping = {}
        self.control_options = control_options
        self.name = name
        if self.control_options is None:
            return
        for index in range(min(len(self.midi_ids), len(control_options))):
            midi_id = self.midi_ids[index]
            control_option = self.control_options[index]
            self.mapping[midi_id] = control_option

    def find_option_for_event(self, midi_event: mido.Message) -> Option|None:
        if midi_event.type == "control_change":
            return self.mapping[midi_event.control]
        if midi_event.type == "note_on":
            return self.mapping[midi_event.note]
        return None


class MidiDevice(Enum):
    NOVATION_LAUNCHCONTROL_XL = {
        "name_prefix": "Launch Control XL:Launch Control XL Launch Contro",
        "name_suffix": ":0",
        "channels": [
            MidiControllerColumn(midi_ids=[13, 29, 49, 77, 41, 73], control_options=None),
            MidiControllerColumn(midi_ids=[14, 30, 50, 78, 42, 74], control_options=None),
            MidiControllerColumn(midi_ids=[15, 31, 51, 79, 43, 75], control_options=None),
            MidiControllerColumn(midi_ids=[16, 32, 52, 80, 44, 76], control_options=None),
            MidiControllerColumn(midi_ids=[17, 33, 53, 81, 57, 89], control_options=None),
            MidiControllerColumn(midi_ids=[18, 34, 54, 82, 58, 90], control_options=None),
            MidiControllerColumn(midi_ids=[19, 35, 55, 83, 59, 91], control_options=None),
            MidiControllerColumn(midi_ids=[20, 36, 56, 84, 60, 92], control_options=None),
        ],
        "extra_buttons": [104, 105, 106, 107, 108]
    }


class Midi:
    port: mido.ports.IOPort
    event_mapping: dict[int, Option]
    channels: list[MidiControllerColumn]
    name_prefix: str
    name_suffix: str
    port_is_open: bool
    controller: any

    def __init__(self, controller: any, device_description: MidiDevice, options: dict[str, list[Option]]) -> None:
        self.event_mapping = {}
        self.device_description = device_description.value
        self.port = None
        self.name_prefix = self.device_description["name_prefix"]
        self.name_suffix = self.device_description["name_suffix"]
        self.channels = self.device_description["channels"]
        self.port_is_open = False
        self.controller = controller

        for index in range(len(options.keys())):
            option_name = list(options.keys())[index]
            option_list = options[option_name]
            self.update_event_mapping(index, option_name, option_list)
        

    def find_device_name(self) -> str|None:
        for name in mido.get_ioport_names():
            if name.startswith(self.name_prefix) and name.endswith(self.name_suffix):
                return name
        return None
    
    def update_event_mapping(self, channel_id: int, option_name: str, options: list[Option]):
        if channel_id >= len(self.channels):
            return
        self.channels[channel_id].change_mapping(option_name, options)
        self.midi_mapping = {}
        for channel_column in self.channels:
            self.midi_mapping.update(channel_column.mapping)

    async def process_events(self):
        device_name = self.find_device_name()
        if self.port is None and self.port_is_open:
            self.port_is_open = False
        if device_name is None and self.port_is_open:
            self.port.close()
            self.port = None
            self.port_is_open = False
        if device_name is None and not self.port_is_open:
            return
        if device_name is not None and not self.port_is_open:
            self.port = mido.open_input(device_name)
            self.port_is_open = True
            await asyncio.sleep(2)
            for msg in self.port.iter_pending():
                pass
        for midi_event in self.port.iter_pending():
            key = None
            if midi_event.type == "control_change":
                key = midi_event.control
            elif midi_event.type == "note_on" or midi_event.type == "note_off":
                key = midi_event.note
                print(key)
            else:
                return
            if key not in self.midi_mapping:
                return
            option_handler = self.midi_mapping[key]
            option_handler.update(midi_event)
            self.controller.network.add_message(path=option_handler.id, value=option_handler.value * 2)
    
import mido
import asyncio
from Options import Option, ValueOption, TriggerOption, OnOffOption
from MidiDevice import MidiDevice

class Controller:
    options: list[tuple[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]]
    midi_device: dict[str, any]
    light_address: str
    light_port: int
    midi_mapping: dict[int, Option]

    def __init__(self, midi_device: MidiDevice, options: list[tuple[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]]) -> None:
        self.midi_device = midi_device.value
        self.options = options
        self.midi_mapping = {}
        for index in range(min(len(self.options), len(self.midi_device["channels"]))):
            midi_controller_column = self.midi_device["channels"][index]
            option_tuple = self.options[index]
            midi_controller_column.change_mapping(option_tuple)
            self.midi_mapping.update(midi_controller_column.mapping)

    def process_midi_event(self, midi_event: mido.Message):
        key = None
        if midi_event.type == "control_change":
            key = midi_event.control
        elif midi_event.type == "note_on" or midi_event.type == "note_off":
            key = midi_event.note
        else:
            return
        if key not in self.midi_mapping:
            return
        option_handler = self.midi_mapping[key]
        option_handler.update(midi_event)
        print(option_handler.id + " " + str(option_handler.value))

    def process_audio_buffer(self, audio_buffer):
        print("process audio")

    def process_gui_event(self, gui_event):
        print(gui_event)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.test_loop())
        loop.create_task(self.midi_loop())
        loop.run_forever()

    async def test_loop(self):
        index = 0
        while True:
            print(f'Test {index}')
            index += 1
            await asyncio.sleep(2)

    async def midi_loop(self):
        port_is_open = False
        port = None
        while True:
            await asyncio.sleep(0.001)
            midi_device_connected = self.midi_device["name"] in mido.get_ioport_names()
            if not midi_device_connected and port_is_open:
                port.close()
                port = None
                port_is_open = False
            if not midi_device_connected and not port_is_open:
                continue
            if midi_device_connected and not port_is_open:
                port = mido.open_input(self.midi_device["name"])
                port_is_open = True
                # await asyncio.sleep(2)
                # for msg in port.iter_pending():
                #     pass
            midi_event = port.poll()
            if midi_event is not None:
                self.process_midi_event(midi_event)

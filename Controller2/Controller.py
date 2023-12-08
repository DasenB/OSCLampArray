import mido
import asyncio
from Options import Option, ValueOption, TriggerOption, OnOffOption
from MidiDevice import MidiDevice
import sounddevice as sd
import numpy as np
import PySimpleGUI as sg
from collections import deque
import sys
from enum import Enum
import math
from Gui import Gui
from Audio import Audio


class Controller:
    options: list[tuple[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]]
    async_event_loop: any

    light_address: str
    light_port: int
    
    gui: Gui

    midi_port: mido.ports.IOPort
    midi_device: dict[str, any]
    midi_mapping: dict[int, Option]

    audio: Audio


    def __init__(self, midi_device: MidiDevice, options: list[tuple[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]]) -> None:
        self.midi_device = midi_device.value
        self.options = options
        self.midi_mapping = {}
        self.midi_port = None
        self.gui = Gui(controller=self)
        self.audio = Audio()

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

    def run(self):
        self.audio.start()
        self.async_event_loop = asyncio.get_event_loop()
        self.async_event_loop.create_task(self.midi_loop())
        self.async_event_loop.create_task(self.gui_loop())
        try:
            self.async_event_loop.run_forever()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        print("Stopping application...")
        try:
            if self.async_event_loop is not None:
                for task in asyncio.all_tasks(self.async_event_loop):
                    task.cancel()
                self.async_event_loop.stop()
                self.async_event_loop.close()
                self.async_event_loop = None
            if self.audio is not None:
                self.audio.stop()
            if self.gui is not None:
                self.gui.stop()
            if self.midi_port is not None:
                self.midi_port.close()
                self.midi_port = None
        except Exception as err:
            print("Failed to stop application.")
            print(err)
            sys.exit(1)
        print("Done.")
        sys.exit(0)


    async def gui_loop(self):
        while True:
            await asyncio.sleep(0.001)
            audio_data = self.audio.get_data()
            if audio_data is None:
                continue
            left,right = np.split(np.abs(np.fft.fft(audio_data)), 2)
            ys = np.add(left,right[::-1])
            ys = np.multiply(40, np.log10(ys))
            ys += 100
            self.gui.draw(frequencies=ys)

    async def midi_loop(self):
        port_is_open = False
        self.midi_port = None
        while True:
            await asyncio.sleep(0.001)
            midi_device_connected = self.midi_device["name"] in mido.get_ioport_names()
            if self.midi_port is None and port_is_open:
                port_is_open = False
            if not midi_device_connected and port_is_open:
                self.midi_port.close()
                self.midi_port = None
                port_is_open = False
            if not midi_device_connected and not port_is_open:
                continue
            if midi_device_connected and not port_is_open:
                self.midi_port = mido.open_input(self.midi_device["name"])
                port_is_open = True
                # await asyncio.sleep(2)
                # for msg in port.iter_pending():
                #     pass
            for midi_event in self.midi_port.iter_pending():
                self.process_midi_event(midi_event)

        


        
        

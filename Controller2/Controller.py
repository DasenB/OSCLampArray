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
from Box import Box
from Network import Network
from MidiDevice import Midi


class Controller:
    options: dict[str, list[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]]
    boxes: list[Box]

    async_event_loop: any
    network: Network
    gui: Gui
    midi: Midi
    audio: Audio


    def __init__(self, lamp_address: str, lamp_port:int, midi_device: MidiDevice, boxes: list[Box], options: dict[str, list[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]]) -> None:
        
        self.options = options
        self.boxes = boxes

        self.midi = Midi(controller=self, device_description=midi_device, options=options)
        self.network = Network(ip=lamp_address, port=lamp_port, batch_duration_s=1.0/20.0)
        self.gui = Gui(controller=self)
        self.audio = Audio()

    # def process_midi_event(self, midi_event: mido.Message):
    #     key = None
    #     if midi_event.type == "control_change":
    #         key = midi_event.control
    #     elif midi_event.type == "note_on" or midi_event.type == "note_off":
    #         key = midi_event.note
    #     else:
    #         return
    #     if key not in self.midi_mapping:
    #         return
    #     option_handler = self.midi_mapping[key]
    #     option_handler.update(midi_event)
    #     self.network.add_message(path=option_handler.id, value=option_handler.value * 2)
        # print(option_handler.id + " " + str(option_handler.value))

    def run(self):
        self.audio.start()
        self.async_event_loop = asyncio.get_event_loop()
        self.async_event_loop.create_task(self.network_loop())
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

    async def network_loop(self):
        while True:
            await asyncio.sleep(1/30)
            self.network.send_batch()


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
            self.gui.draw(frequencies=ys, osc_history=self.network.history)

    async def midi_loop(self):
        while True:
            await asyncio.sleep(0.001)
            self.midi.process_events()

        port_is_open = False
        self.midi_port = None
        device_name = self.midi_device["name_prefix"] + self.midi_device["name_suffix"]
        for name in mido.get_ioport_names():
            if name.startswith(self.midi_device["name_prefix"]) and name.endswith(self.midi_device["name_suffix"]):
                device_name = name
                break

        while True:
            await asyncio.sleep(0.001)
            midi_device_connected = device_name in mido.get_ioport_names()
            if self.midi_port is None and port_is_open:
                port_is_open = False
            if not midi_device_connected and port_is_open:
                self.midi_port.close()
                self.midi_port = None
                port_is_open = False
            if not midi_device_connected and not port_is_open:
                continue
            if midi_device_connected and not port_is_open:
                self.midi_port = mido.open_input(device_name)
                port_is_open = True
                # await asyncio.sleep(2)
                # for msg in port.iter_pending():
                #     pass
            for midi_event in self.midi_port.iter_pending():
                self.process_midi_event(midi_event)

        


        
        

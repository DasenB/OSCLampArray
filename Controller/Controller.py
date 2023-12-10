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


    def __init__(self, lamp_addresses: list[str], lamp_port:int, midi_device: MidiDevice, boxes: list[Box], options: dict[str, list[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]]) -> None:
        
        self.options = options
        self.boxes = boxes

        self.midi = Midi(controller=self, device_description=midi_device, options=options)
        self.network = Network(ips=lamp_addresses, port=lamp_port, batch_duration_s=1.0/20.0)
        self.gui = Gui(controller=self)
        self.audio = Audio()


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


        
        

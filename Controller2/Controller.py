import mido
import asyncio
from Options import Option, ValueOption, TriggerOption, OnOffOption
from MidiDevice import MidiDevice
import sounddevice as sd
import numpy as np
import PySimpleGUI as sg
from collections import deque
import sys

class Controller:
    options: list[tuple[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]]
    midi_device: dict[str, any]
    light_address: str
    light_port: int
    midi_mapping: dict[int, Option]
    idx: int
    sound_queue: deque
    audio_stream: sd.InputStream
    gui_window: sg.Window
    midi_port: mido.ports.IOPort
    async_event_loop: any


    def __init__(self, midi_device: MidiDevice, options: list[tuple[ValueOption, ValueOption, ValueOption, ValueOption, TriggerOption|OnOffOption, TriggerOption|OnOffOption]]) -> None:
        self.midi_device = midi_device.value
        self.options = options
        self.midi_mapping = {}
        self.idx = 0
        self.sound_queue = deque([], maxlen = 10000)
        self.midi_port = None
        self.gui_window = None
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

    def process_gui_event(self, gui_event):
        print(gui_event)

    def run(self):
        self.start_sound()
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
            if self.audio_stream is not None:
                self.audio_stream.stop()
                self.audio_stream.close()
                self.audio_stream = None
                sd.stop()
            if self.gui_window is not None:
                self.gui_window.close()
                self.gui_window = None
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
        layout = [[
            sg.Col([[ sg.Graph(canvas_size=(800, 200), graph_bottom_left=(0, 0), graph_top_right=(800, 200), background_color='grey', enable_events=True, key='graph')]], vertical_alignment='center', justification='center' )
        ]]
        self.gui_window = sg.Window('Window Title', layout, element_justification='c', finalize=True)

        while True:
            await asyncio.sleep(0.001)
            if(len(self.sound_queue) < self.sound_queue.maxlen):
                continue
            audio_data = np.array(self.sound_queue)
            logScale = True
            left,right=np.split(np.abs(np.fft.fft(audio_data)),2)
            ys=np.add(left,right[::-1])
            if logScale:
                ys=np.multiply(20,np.log10(ys))
                ys += 40
            graph = self.gui_window['graph'] 
            width = graph.CanvasSize[0]
            height = graph.CanvasSize[1]
            bar_width = width/len(ys)
            xpos_left = 0
            graph.erase()
            for value in ys:
                graph.draw_rectangle((xpos_left, 0), (xpos_left + bar_width, value), fill_color='black', line_color='white')
                xpos_left += bar_width

            event, value = self.gui_window.read(0)
            if event == "__TIMEOUT__":
                continue
            if event == "Exit" or event == None:
                self.stop()
                await asyncio.sleep(5)
            print(event, value)

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
            # midi_event = self.midi_port.poll()
            # if midi_event is not None:
                # self.process_midi_event(midi_event)
        
    def start_sound(self):
        def callback(indata: np.ndarray, outdata: np.ndarray, frames: int, time: any, status: any) -> None:
            if status:
                print("Sound Error")
                return
            outdata[:] = indata
            self.sound_queue.extend(indata[:, 0])
            # print(self.sound_queue)
            # device=(args.input_device, args.output_device)
        self.audio_stream = sd.Stream(blocksize=512, callback=callback, dtype='float32', channels=1, latency=0.005)
        # event = asyncio.Event()
        self.audio_stream.start()
        # await event.wait()


        
        

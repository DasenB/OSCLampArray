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

class Box:
    id: str
    value: int
    selected: bool
    disabled: bool
    position: (int, int)
    size: (int, int)
    on_message: str
    off_message: str
    value_message: str

    def __init__(self, id: str) -> None:
        self.id = id
        self.value = 0
        self.selected = False
        self.disabled = False
        self.position = (100, 200)
        self.size = (50, 50)


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
        width = 1300
        height = 400
        layout = [[
            sg.Col([[ sg.Graph(canvas_size=(width, height), graph_bottom_left=(0, 0), graph_top_right=(width, height), background_color='grey', enable_events=True, key='graph')]], vertical_alignment='center', justification='center' )
        ]]
        self.gui_window = sg.Window('Window Title', layout, element_justification='c', finalize=True, return_keyboard_events=True)
            
        graph = self.gui_window['graph'] 
        graph.bind("<ButtonPress-1>", "-select-box")
        graph.bind("<ButtonPress-3>", "-toggle-box-disabled")
        graph.bind("<B1-Motion>", "-move-box")
        # graph.bind("<B3-Motion>", print)
        graph.bind("<ButtonRelease-1>", "-move-end")
        # graph.bind("<ButtonRelease-3>", print)
        graph.bind("<MouseWheel>", print)
        # graph.configure(cursor="hand1")
        moving_boxes = []

        boxes = [Box(id="1"), Box(id="2"), Box(id="3"), Box(id="4")]
        for i in range(len(boxes)):
            boxes[i].position = (boxes[i].position[0] * i + 1, boxes[i].position[1])


        while True:
            await asyncio.sleep(0.001)
            if(len(self.sound_queue) < self.sound_queue.maxlen):
                continue
            audio_data = np.array(self.sound_queue)
            logScale = True
            left,right=np.split(np.abs(np.fft.fft(audio_data)),2)
            ys=np.add(left,right[::-1])
            if logScale:
                factor = 20 * 2
                ys=np.multiply(factor, np.log10(ys))
                ys += 100
            width = graph.CanvasSize[0]
            height = graph.CanvasSize[1]
            bar_width = width/len(ys)
            xpos_left = 0
            graph.erase()
            for box in boxes:
                top_right = (box.position[0] + box.size[0], box.position[1] + box.size[1])
                fill_color = "#000000"
                if box.disabled:
                    fill_color = "#505050"
                graph.draw_rectangle(box.position, top_right, fill_color=fill_color)
            for value in ys:
                graph.draw_rectangle((xpos_left, 0), (xpos_left + bar_width, value), fill_color='white', line_color='white')
                xpos_left += bar_width
            for box in boxes:
                top_right = (box.position[0] + box.size[0], box.position[1] + box.size[1])
                border_color = "pink"
                if not box.selected and not box.disabled:
                    border_color = "#94b8f2"
                if box.selected and not box.disabled:
                    border_color = "#1756e8"
                if box.selected and box.disabled:
                    border_color = "#ff0000"
                if not box.selected and box.disabled:
                    border_color = "#f29894"
                graph.draw_rectangle(box.position, top_right, line_color=border_color)
            for box in boxes:
                if box.disabled:
                    box.value = 0
                    continue
                box.value = 0
                box_min_x = float(box.position[0])
                box_min_y = float(box.position[1])
                box_max_x = float(box_min_x + box.size[0])
                box_max_y = float(box_min_y + box.size[1])
                for rect_index in range(len(ys)):
                    rect = float(ys[rect_index])
                    rect_min_x = float(rect_index * bar_width)
                    rect_max_x = float(rect_min_x + bar_width)
                    rect_min_y = float(0)
                    rect_max_y = float(rect)
                    if rect_max_x < box_min_x:
                        continue
                    if rect_min_x > box_max_x:
                        continue
                    if rect_max_y < box_min_y:
                        continue
                    if rect_min_y > box_max_y:
                        continue
                    overlap_min_x = max(rect_min_x, box_min_x)
                    overlap_min_y = max(rect_min_y, box_min_y)
                    overlap_max_x = min(rect_max_x, box_max_x)
                    overlap_max_y = min(rect_max_y, box_max_y)
                    overlap_width = overlap_max_x - overlap_min_x
                    overlap_height = overlap_max_y - overlap_min_y
                    overlap_area = overlap_height * overlap_width
                    box.value += overlap_area
                box_area = (box_max_x - box_min_x) * (box_max_y - box_min_y)
                if box_area == 0:
                    box.value = 0
                else:
                    box.value *= 127
                    box.value /= box_area

            event, value = self.gui_window.read(0)
            if event == "__TIMEOUT__":
                continue
            if event == "Exit" or event == None:
                self.stop()
                await asyncio.sleep(5)
            if event == "graph-move-end":
                moving_boxes = []
            if event == "graph-move-box":
                cursor = value["graph"]
                for moving_box in moving_boxes:
                    box = moving_box["box"]
                    new_x = cursor[0] - moving_box["x_offset"]
                    new_y = cursor[1] - moving_box["y_offset"]
                    new_x = max(0, new_x)
                    new_y = max(0, new_y)
                    if new_x + box.size[0] > width:
                        new_x = width - box.size[0]
                    if new_y + box.size[1] > height:
                        new_y = height - box.size[1]
                    box.position = (new_x, new_y)
            if event == "graph-select-box":
                cursor = value["graph"]
                for box in boxes:
                    top_right = (box.position[0] + box.size[0], box.position[1] + box.size[1])
                    box.selected = cursor[0] > box.position[0] and cursor[1] > box.position[1] and cursor[0] < top_right[0] and cursor[1] < top_right[1]
                    if box.selected:
                        moving_boxes.append({
                            "box": box,
                            "x_offset": cursor[0] - box.position[0],
                            "y_offset": cursor[1] - box.position[1]
                        })
            if event == "graph-toggle-box-disabled":
                cursor = value["graph"]
                for box in boxes:
                    top_right = (box.position[0] + box.size[0], box.position[1] + box.size[1])
                    hit = cursor[0] > box.position[0] and cursor[1] > box.position[1] and cursor[0] < top_right[0] and cursor[1] < top_right[1]
                    if hit:
                        box.disabled = not box.disabled

            if event == "Up:111":
                for box in boxes:
                    if not box.selected:
                        continue
                    box.size = (box.size[0], box.size[1] + 1) 
            if event == "Down:116":
                for box in boxes:
                    if not box.selected:
                        continue
                    box.size = (box.size[0], max(1, box.size[1] - 1)) 
            if event == "Right:114":
                for box in boxes:
                    if not box.selected:
                        continue
                    box.size = (box.size[0] + 1, box.size[1]) 
            if event == "Left:113":
                for box in boxes:
                    if not box.selected:
                        continue
                    box.size = (max(1, box.size[0] - 1), box.size[1]) 

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


    def start_sound(self):
        def callback(indata: np.ndarray, outdata: np.ndarray, frames: int, time: any, status: any) -> None:
            if status:
                print("Sound Error")
                return
            outdata[:] = indata
            self.sound_queue.extend(indata[:, 0])
           
        self.audio_stream = sd.Stream(blocksize=512, callback=callback, dtype='float32', channels=1, latency=0.005)
        self.audio_stream.start()


        
        

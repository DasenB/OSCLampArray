import PySimpleGUI as sg
from collections import deque
import numpy as np
from pynput import keyboard
from Box import Box

class Gui:
    controller: any
    window: sg.Window
    layout: any
    canvas_size: tuple[int, int]
    boxes: list[Box]
    dragged_boxes: list[Box]
    shift_state: bool
    alt_state: bool

    def __init__(self, controller: any) -> None:
        self.controller = controller
        self.canvas_size = (1300, 410)
        option_columns = list(self.controller.options.keys())
        osc_paths = []
        for option_column in option_columns:
            for option in self.controller.options[option_column]:
                osc_paths.append(option.id)
        box_settings_layout = [
            [sg.Text("Box: -", font=("Helvetica", 14, "bold"), key='box_settings_id')],
            [
                sg.Col([[sg.Text("Description")], [sg.Text("On Message")], [sg.Text("Off Message")], [sg.Text("Value Message")]]),
                sg.Col([
                    [sg.Input(size=(32, 1), key='box_settings_description')],
                    [sg.Combo(osc_paths, default_value="", size=(30, 1), key='box_settings_on_message')],
                    [sg.Combo(osc_paths, default_value="", size=(30, 1), key='box_settings_off_message')], 
                    [sg.Combo(osc_paths, default_value="", size=(30, 1),  key='box_settings_value_message')]
                    ], element_justification="right")
            ],
            [sg.Button(button_text="Cancel", key="cancel-box-settings"), sg.Button(button_text="Save", key="save-box-settings")]           
        ]
        midi_settings_layout = [
            [
                sg.Col([[sg.Text("Channel 1")], [sg.Text("Channel 2")], [sg.Text("Channel 3")], [sg.Text("Channel 4")]]),
                sg.Col([[sg.Combo(option_columns, default_value=option_columns[0], size=(30, 1))], [sg.Combo(option_columns, default_value=option_columns[1], size=(30, 1))], [sg.Combo(option_columns, default_value=option_columns[2], size=(30, 1))], [sg.Combo(option_columns, default_value=option_columns[3], size=(30, 1))]]),
                sg.VSeparator(),
                sg.Col([[sg.Text("Channel 5")], [sg.Text("Channel 6")], [sg.Text("Channel 7")], [sg.Text("Channel 8")]]),
                sg.Col([[sg.Combo(option_columns, default_value=option_columns[4], size=(30, 1))], [sg.Combo(option_columns, default_value=option_columns[5], size=(30, 1))], [sg.Combo(option_columns, default_value=option_columns[6], size=(30, 1))], [sg.Combo(option_columns, default_value=option_columns[7], size=(30, 1))]]),
            ],
            [sg.Button(button_text="Cancel", key="cancel-midi-settings"), sg.Button(button_text="Save", key="save-midi-settings")]           
        ]
        self.layout  = [
            [sg.Col([[ sg.Graph(canvas_size=self.canvas_size, graph_bottom_left=(0, 0), graph_top_right=self.canvas_size, background_color='grey', enable_events=True, key='graph')]], vertical_alignment='center', justification='center' )],
            [sg.Frame(title="Box Settings", layout=box_settings_layout, size=(400, 230)), 
             sg.Frame(title="MIDI Settings", layout=midi_settings_layout, size=(650, 230))]
        ]
        self.window = sg.Window('Window Title', self.layout, element_justification='c', finalize=True, return_keyboard_events=True)
        
        self.graph = self.window['graph'] 
        self.graph.bind("<ButtonPress-1>", "-select-box")
        self.graph.bind("<ButtonPress-3>", "-toggle-box-disabled")
        self.graph.bind("<ButtonRelease-1>", "-move-end")

        self.dragged_boxes = []
        self.boxes = self.controller.boxes
        self.display_box_setting_view()

        listener = keyboard.Listener(on_press=self.on_press,on_release=self.on_release)
        listener.start()
        self.shift_state = False
        self.alt_state = False
    
        

    def draw_audio(self, frequencies: list[int]) -> None:
        self.canvas_size = self.graph.CanvasSize
        width = self.canvas_size[0]
        height = self.canvas_size[1]
        bar_width = width/len(frequencies)
        xpos_left = 0
        self.graph.erase()
        for box in self.boxes:
            top_right = (box.position[0] + box.size[0], box.position[1] + box.size[1])
            fill_color = "#000000"
            if box.disabled:
                fill_color = "#505050"
            self.graph.draw_rectangle(box.position, top_right, fill_color=fill_color)
        for value in frequencies:
            self.graph.draw_rectangle((xpos_left, 0), (xpos_left + bar_width, value), fill_color='white', line_color='white')
            xpos_left += bar_width
        for box in self.boxes:
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
            self.graph.draw_rectangle(box.position, top_right, line_color=border_color)
        for box in self.boxes:
            if box.disabled:
                box.value = 0
                continue
            box.value = 0
            box_min_x = float(box.position[0])
            box_min_y = float(box.position[1])
            box_max_x = float(box_min_x + box.size[0])
            box_max_y = float(box_min_y + box.size[1])
            for rect_index in range(len(frequencies)):
                rect = float(frequencies[rect_index])
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
        for box in self.boxes:
            position = (box.position[0] + box.size[0] + 8, box.position[1] + box.size[1])
            self.graph.draw_text(str(box.description), position, color="#7d2c7c", font=("Arial", 14, "bold"), text_location=sg.TEXT_LOCATION_BOTTOM_LEFT, angle=30)

    def move_box_with_mouse(self, cursor: tuple[int, int]) -> None:
        width = self.canvas_size[0]
        height = self.canvas_size[1]
        for moving_box in self.dragged_boxes:
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

    def move_box_with_key(self, event) -> None:
        move_speed = 5
        for box in self.boxes:
            if not box.selected:
                continue
            change = (0, 0)
            if event == "Up:111":
                change = (0, move_speed)
            if event == "Down:116":
                change = (0, -move_speed)
            if event == "Right:114":
                change = (move_speed, 0)
            if event == "Left:113":
                change = (-move_speed, 0)
            box.position = (box.position[0] + change[0], box.position[1] + change[1])
    
    def select_box(self, cursor: tuple[int, int]) -> None:
        for box in self.boxes:
            box.selected = False
        for box in self.boxes:
            top_right = (box.position[0] + box.size[0], box.position[1] + box.size[1])
            hit = cursor[0] > box.position[0] and cursor[1] > box.position[1] and cursor[0] < top_right[0] and cursor[1] < top_right[1]
            if not hit:
                continue
            box.selected = hit
            self.dragged_boxes.append({
                "box": box,
                "x_offset": cursor[0] - box.position[0],
                "y_offset": cursor[1] - box.position[1]
            })
            break
        self.display_box_setting_view()
    
    def disable_box(self, cursor: tuple[int, int]) -> None:
        for box in self.boxes:
            top_right = (box.position[0] + box.size[0], box.position[1] + box.size[1])
            hit = cursor[0] > box.position[0] and cursor[1] > box.position[1] and cursor[0] < top_right[0] and cursor[1] < top_right[1]
            if hit:
                box.disabled = not box.disabled

    def resize_box(self, event: str) -> None:
        resize_speed = 4
        for box in self.boxes:
            if not box.selected:
                continue
            if event == "Up:111":
                box.size = (box.size[0], box.size[1] + resize_speed) 
            if event == "Down:116":
                box.size = (box.size[0], max(1, box.size[1] - resize_speed)) 
            if event == "Right:114":
                box.size = (box.size[0] + resize_speed, box.size[1]) 
            if event == "Left:113":
                box.size = (max(1, box.size[0] - resize_speed), box.size[1]) 
    
    def display_box_setting_view(self):
        selected_box = None
        for box in self.boxes:
            if box.selected:
                selected_box = box
                break
        if selected_box is None:
            self.window['box_settings_id'].update("Box: -")
            self.window['box_settings_description'].update("-")
            self.window['box_settings_on_message'].update("-")
            self.window['box_settings_off_message'].update("-")
            self.window['box_settings_value_message'].update("-")
            return
        self.window['box_settings_id'].update("Box: " + str(box.id))
        self.window['box_settings_description'].update(str(box.description))
        self.window['box_settings_on_message'].update(box.on_message)
        self.window['box_settings_off_message'].update(box.off_message)
        self.window['box_settings_value_message'].update(box.value_message)

    def save_box_setting_view(self):
        selected_box = None
        for box in self.boxes:
            if box.selected:
                selected_box = box
                break
        if selected_box is None:
            return
        box.description = self.window['box_settings_description'].get()
        box.on_message = self.window['box_settings_on_message'].get()
        box.off_message = self.window['box_settings_off_message'].get()
        box.value_message = self.window['box_settings_value_message'].get()

    def on_press(self, key):
        if key == keyboard.Key.shift:
            self.shift_state = True
        if key == keyboard.Key.alt:
            self.alt_state = True
    def on_release(self, key):
        if key == keyboard.Key.shift:
            self.shift_state = False
        if key == keyboard.Key.alt:
            self.alt_statel = False
        
    def select_box_by_id(self, id: str) -> None:
        for box in self.boxes:
            box.selected = box.id == id

    def draw(self, frequencies: list[int]) -> None:
        self.draw_audio(frequencies)
            
        event, value = self.window.read(0)
        if event == "__TIMEOUT__":
            return
        if event == "Exit" or event == None:
            self.controller.stop()
            return
        if event == "graph-move-end":
            self.dragged_boxes = []
            self.graph.unbind("<B1-Motion>")
        if event == "graph-move-box":
            cursor = value["graph"]
            self.move_box_with_mouse(cursor)
        if event == "graph-select-box":
            self.graph.bind("<B1-Motion>", "-move-box")
            cursor = value["graph"]
            self.select_box(cursor)
        if event == "graph-toggle-box-disabled":
            cursor = value["graph"]
            self.disable_box(cursor)
        if event in ["Up:111", "Down:116", "Right:114", "Left:113"] and self.shift_state:
            self.resize_box(event)
        if event in ["Up:111", "Down:116", "Right:114", "Left:113"] and not self.shift_state:
            self.move_box_with_key(event)
        if event in ["1:10", "2:11", "3:12", "4:13", "5:14", "6:15", "7:16", "8:17", "9:18", "0:19"] and self.alt_state:
            self.select_box_by_id(event.split(":")[0])
            self.display_box_setting_view()
        if event == "space:65":
            for box in self.boxes:
                if not box.selected:
                    continue
                box.disabled = not box.disabled
        if event == "save-box-settings":
            self.save_box_setting_view()
        if event == "cancel-box-settings":
            self.display_box_setting_view()

    def stop(self) -> None:
        self.window.close()
        self.window = None
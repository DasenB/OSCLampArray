import PySimpleGUI as sg
from collections import deque
import numpy as np

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

class Gui:

    controller: any
    window: sg.Window
    layout: any
    canvas_size: tuple[int, int]
    boxes: list[Box]
    dragged_boxes: list[Box]

    def __init__(self, controller: any) -> None:
        self.controller = controller
        self.canvas_size = (1300, 400)
        self.layout  = [[
            sg.Col([[ sg.Graph(canvas_size=self.canvas_size, graph_bottom_left=(0, 0), graph_top_right=self.canvas_size, background_color='grey', enable_events=True, key='graph')]], vertical_alignment='center', justification='center' )
        ]]
        self.window = sg.Window('Window Title', self.layout, element_justification='c', finalize=True, return_keyboard_events=True)
        
        self.graph = self.window['graph'] 
        self.graph.bind("<ButtonPress-1>", "-select-box")
        self.graph.bind("<ButtonPress-3>", "-toggle-box-disabled")
        self.graph.bind("<B1-Motion>", "-move-box")
        # self.graph.bind("<B3-Motion>", print)
        self.graph.bind("<ButtonRelease-1>", "-move-end")
        # self.graph.bind("<ButtonRelease-3>", print)
        self.graph.bind("<MouseWheel>", print)
        # self.graph.configure(cursor="hand1")

        self.dragged_boxes = []
        self.boxes = [Box(id="1"), Box(id="2"), Box(id="3"), Box(id="4")]
        for i in range(len(self.boxes)):
            self.boxes[i].position = (self.boxes[i].position[0] * i + 1, self.boxes[i].position[1])


    
        

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

    def move_box(self, cursor: tuple[int, int]) -> None:
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
    
    def select_box(self, cursor: tuple[int, int]) -> None:
        for box in self.boxes:
            top_right = (box.position[0] + box.size[0], box.position[1] + box.size[1])
            box.selected = cursor[0] > box.position[0] and cursor[1] > box.position[1] and cursor[0] < top_right[0] and cursor[1] < top_right[1]
            if not box.selected:
                continue
            self.dragged_boxes.append({
                "box": box,
                "x_offset": cursor[0] - box.position[0],
                "y_offset": cursor[1] - box.position[1]
            })
    
    def disable_box(self, cursor: tuple[int, int]) -> None:
        for box in self.boxes:
            top_right = (box.position[0] + box.size[0], box.position[1] + box.size[1])
            hit = cursor[0] > box.position[0] and cursor[1] > box.position[1] and cursor[0] < top_right[0] and cursor[1] < top_right[1]
            if hit:
                box.disabled = not box.disabled

    def resize_box(self, event: str) -> None:
        for box in self.boxes:
            if not box.selected:
                continue
            if event == "Up:111":
                box.size = (box.size[0], box.size[1] + 1) 
            if event == "Down:116":
                box.size = (box.size[0], max(1, box.size[1] - 1)) 
            if event == "Right:114":
                box.size = (box.size[0] + 1, box.size[1]) 
            if event == "Left:113":
                box.size = (max(1, box.size[0] - 1), box.size[1]) 

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
        if event == "graph-move-box":
            cursor = value["graph"]
            self.move_box(cursor)
        if event == "graph-select-box":
            cursor = value["graph"]
            self.select_box(cursor)
        if event == "graph-toggle-box-disabled":
            cursor = value["graph"]
            self.disable_box(cursor)

        if event in ["Up:111", "Down:116", "Right:114", "Left:113"]:
            self.resize_box(event)

    def stop(self) -> None:
        self.window.close()
        self.window = None
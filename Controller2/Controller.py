import PySimpleGUI as sg

class ControlValue:
    id: str
    osc_path: str
    midi_control_number: int
    description: str
    def __init__(self, id: str, midi_control_number: int, description: str) -> None:
        self.id = id
        self.midi_control_number = midi_control_number
        self.osc_path = self.id
        self.description = description
    def gui_element(self) -> sg.Col:
        return sg.Col(
            [
                [sg.Text(self.description)],     
                [sg.Spin(
                    [ i for i in range(0,127)],
                    initial_value=0, size=[3, 1],
                    enable_events=True,
                    key=self.id)
                ]
            ],
            vertical_alignment='center', justification='center')

class ControlAction:
    id: str
    osc_path: str
    midi_note_number: int
    description: str
    def __init__(self, id: str, midi_note_number: int, description: str) -> None:
        self.id = id
        self.midi_note_number = midi_note_number
        self.osc_path = self.id
        self.description = description
    def gui_element(self) -> sg.Col:
        return sg.Col(
            [
                [sg.Button(self.description, key=self.id)]
            ], 
            vertical_alignment='center', justification='center')

class Controller:
    elements: [sg.Col]
    midi_device: str
    light_address: str
    light_port: int
    def __init__(self, elements: [[ControlValue|ControlAction]]) -> None:
        return
    def process_midi_event(self, midi_event):
        print(midi_event)
    def process_audio_buffer(self, audio_buffer):
        print("process audio")
    def process_gui_event(self, gui_event):
        print(gui_event)

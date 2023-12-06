import PySimpleGUI as sg
import mido

class Option:
    id: str
    description: str
    value: int
    def __init__(self, id: str,  description: str) -> None:
        self.id = id
        self.description = description
        self.value = 0

class ValueOption(Option):
    def __init__(self, id: str,  description: str) -> None:
        super().__init__(id=id, description=description)
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
    def update(self, midi_event: mido.Message) -> int:
        if midi_event.type == "control_change":
            self.value = midi_event.value
        return self.value

class TriggerOption(Option):
    def __init__(self, id: str,  description: str) -> None:
        super().__init__(id=id, description=description)
    def gui_element(self) -> sg.Col:
        return sg.Col(
            [
                [sg.Button(self.description, key=self.id)]
            ], 
            vertical_alignment='center', justification='center')
    def update(self, midi_event: mido.Message) -> int:
        if midi_event.type == "note_on":
            self.value = 1
        if midi_event.type == "note_off":
            self.value = 0
        return self.value
    
class OnOffOption(Option):
    def __init__(self, id: str,  description: str) -> None:
        super().__init__(id=id, description=description)
    def gui_element(self) -> sg.Col:
        return sg.Col(
            [
                [sg.Checkbox(self.description, key=self.id)]
            ], 
            vertical_alignment='center', justification='center')
    def update(self, midi_event: mido.Message) -> int:
        if midi_event.type == "note_on":
            if self.value == 0:
                self.value = 1
            else:
                self.value = 0
        return self.value

from Controller import ControlValue, ControlAction
import mido

with mido.open_input(mido.get_output_names()[1]) as inport:
    for msg in inport:
        print(msg)

action_columns = []

wave_control = [
    ControlValue("wave1/red", midi_control_number=14, description="R"),
    ControlValue("wave1/green", midi_control_number=30, description="G"),
    ControlValue("wave1/blue", midi_control_number=50, description="B"),
    ControlValue("wave1/master", midi_control_number=76, description="Master"),
    ControlAction("wave1/trigger", midi_note_number=42, description="Trigger"),
    ControlAction("wave1/mute", midi_note_number=74, description="Mute"),
]
action_columns.append(wave_control)
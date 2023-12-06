from Controller import Controller
from Options import ValueOption, TriggerOption, OnOffOption
from MidiDevice import MidiDevice

option_columns = []

wave1_control = (
    ValueOption("wave1/red", description="Wave 1 R"),
    ValueOption("wave1/green", description="Wave 1 G"),
    ValueOption("wave1/blue", description="Wave 1 B"),
    ValueOption("wave1/master", description="Wave 1 Brightness"),
    TriggerOption("wave1/trigger", description="Wave 1 Trigger"),
    OnOffOption("wave1/mute", description="Wave 1 Mute"),
)
option_columns.append(wave1_control)

wave2_control = (
    ValueOption("wave2/red", description="Wave 2 R"),
    ValueOption("wave2/green", description="Wave 2 G"),
    ValueOption("wave2/blue", description="Wave 2 B"),
    ValueOption("wave2/master", description="Wave 2 Brightness"),
    TriggerOption("wave2/trigger", description="Wave 2 Trigger"),
    OnOffOption("wave2/mute", description="Wave 2 Mute"),
)

option_columns.append(wave2_control)


c = Controller(midi_device=MidiDevice.NOVATION_LAUNCHCONTROL_XL, options=option_columns)
c.run()
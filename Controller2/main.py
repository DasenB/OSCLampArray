from Controller import Controller
from Options import ValueOption, TriggerOption, OnOffOption
from MidiDevice import MidiDevice
from Box import Box

option_columns = {
    "Wave _1": (
        ValueOption("wave1/red", description="Wave_1 R"),
        ValueOption("wave1/green", description="Wave_1 G"),
        ValueOption("wave1/blue", description="Wave_1 B"),
        ValueOption("wave1/master", description="Wave_1 Brightness"),
        TriggerOption("wave1/trigger", description="Wave_1 Trigger"),
        OnOffOption("wave1/mute", description="Wave_1 Mute"),
    ),
    "Wave_2": (
        ValueOption("wave2/red", description="Wave_2 R"),
        ValueOption("wave2/green", description="Wave_2 G"),
        ValueOption("wave2/blue", description="Wave_2 B"),
        ValueOption("wave2/master", description="Wave_2 Brightness"),
        TriggerOption("wave2/trigger", description="Wave_2 Trigger"),
        OnOffOption("wave2/mute", description="Wave_2 Mute"),
    ),
    "Strobe": (
        ValueOption("strobe/red", description="Strobe R"),
        ValueOption("strobe/green", description="Strobe G"),
        ValueOption("strobe/blue", description="Strobe B"),
        ValueOption("strobe/master", description="Strobe Brightness"),
        TriggerOption("strobe/trigger", description="Strobe Trigger"),
        OnOffOption("strobe/mute", description="Strobe Mute"),
    ),
    "Glow": (
        ValueOption("glow/red", description="Glow R"),
        ValueOption("glow/green", description="Glow G"),
        ValueOption("glow/blue", description="Glow B"),
        ValueOption("glow/master", description="Glow Brightness"),
        TriggerOption("glow/trigger", description="Glow Trigger"),
        OnOffOption("glow/mute", description="Glow Mute"),
    ),
    "Perlin": (
        ValueOption("perlin/red", description="Perlin R"),
        ValueOption("perlin/green", description="Perlin G"),
        ValueOption("perlin/blue", description="Perlin B"),
        ValueOption("perlin/master", description="Perlin Brightness"),
        TriggerOption("perlin/trigger", description="Perlin Trigger"),
        OnOffOption("perlin/mute", description="Perlin Mute"),
    ),
    "Sparkle": (
        ValueOption("sparkle/red", description="Sparkle R"),
        ValueOption("sparkle/green", description="Sparkle G"),
        ValueOption("sparkle/blue", description="Sparkle B"),
        ValueOption("sparkle/master", description="Sparkle Brightness"),
        TriggerOption("sparkle/trigger", description="Sparkle Trigger"),
        OnOffOption("sparkle/mute", description="Sparkle Mute"),
    ),
    "Jumper_1": (
        ValueOption("jumper1/red", description="Jumper_1 R"),
        ValueOption("jumper1/green", description="Jumper_1 G"),
        ValueOption("jumper1/blue", description="Jumper_1 B"),
        ValueOption("jumper1/master", description="Jumper_1 Brightness"),
        TriggerOption("jumper1/trigger", description="Jumper_1 Trigger"),
        OnOffOption("jumper1/mute", description="Jumper_1 Mute"),
    ),
    "Jumper_2": (
        ValueOption("jumper2/red", description="Jumper_2 R"),
        ValueOption("jumper2/green", description="Jumper_2 G"),
        ValueOption("jumper2/blue", description="Jumper_2 B"),
        ValueOption("jumper2/master", description="Jumper_2 Brightness"),
        TriggerOption("jumper2/trigger", description="Jumper_2 Trigger"),
        OnOffOption("jumper2/mute", description="Jumper_2 Mute"),
    )
}

boxes = [
    Box(id="1", description="Strobe"), 
    Box(id="2", description="Blue"), 
    Box(id="3", description="Green"), 
    Box(id="4", description="Red"), 
    Box(id="5", description="Jumper 1"), 
    Box(id="6", description="Sparkle"),
    Box(id="7", description="Wave 1"),
    Box(id="8", description="Wave 2")
]
for i in range(len(boxes)):
    boxes[i].position = (boxes[i].position[0] * i + 20, boxes[i].position[1])

c = Controller(midi_device=MidiDevice.NOVATION_LAUNCHCONTROL_XL, boxes=boxes, options=option_columns)
c.run()
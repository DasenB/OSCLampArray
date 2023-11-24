import PySimpleGUI as sg
from tkinter import *
from tkinter import messagebox

sg.theme('Dark Blue 2')  # please make your windows colorful


strobe_on_duration =    sg.Col([[sg.Text('On (ms)')],   [sg.Spin([ i for i in range(0,99999)], initial_value=100, size=[5, 1], enable_events=True, key="strobe_on_duration")]], vertical_alignment='center', justification='center')
strobe_off_duration =   sg.Col([[sg.Text('Off (ms)')],  [sg.Spin([ i for i in range(0,99999)], initial_value=100, size=[5, 1], enable_events=True, key="strobe_off_duration")]], vertical_alignment='center', justification='center')
strobe_jitter =         sg.Col([[sg.Text('Jitter (ms)')],    [sg.Spin([ i for i in range(0,99999)], initial_value=100, size=[5, 1], enable_events=True, key="strobe_jitter")]], vertical_alignment='center', justification='center')
strobe_brightness =     sg.Col([[sg.Text('Brightness')],[sg.Slider(range=(0,255), orientation='v', size=(10,20), enable_events=True, key="strobe_brightness")]], vertical_alignment='center', justification='center')
strobe_trigger =     sg.Col([[sg.Button("Trigger", key="strobe_trigger")]], vertical_alignment='center', justification='center')
strobe_mute =     sg.Col([[sg.Button("Mute", key="strobe_mute")]], vertical_alignment='center', justification='center')
strobe_column=[[sg.Text('Strobe', font="Courier 12 bold")], [strobe_on_duration], [strobe_off_duration],  [strobe_jitter], [strobe_trigger], [strobe_mute], [strobe_brightness]]

rainbow_red =       sg.Col([[sg.Text('R')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="rainbow_red")]], vertical_alignment='center', justification='center')
rainbow_green =     sg.Col([[sg.Text('G')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="rainbow_green")]], vertical_alignment='center', justification='center')
rainbow_blue =      sg.Col([[sg.Text('B')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="rainbow_blue")]], vertical_alignment='center', justification='center')
rainbow_weight =    sg.Col([[sg.Text('Weight')],[sg.Slider(range=(0,255), orientation='v', size=(10,20), enable_events=True, key="rainbow_weight")]], vertical_alignment='center', justification='center')
rainbow_trigger =     sg.Col([[sg.Button("Trigger", key="rainbow_trigger")]], vertical_alignment='center', justification='center')
rainbow_mute =     sg.Col([[sg.Button("Mute", key="rainbow_mute")]], vertical_alignment='center', justification='center')
rainbow_column=[[sg.Text('Rainbow', font="Courier 12 bold")], [rainbow_red], [rainbow_green], [rainbow_blue], [rainbow_trigger], [rainbow_mute], [rainbow_weight]]

jumper1_red =       sg.Col([[sg.Text('R')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="jumper1_red")]], vertical_alignment='center', justification='center')
jumper1_green =     sg.Col([[sg.Text('G')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="jumper1_green")]], vertical_alignment='center', justification='center')
jumper1_blue =      sg.Col([[sg.Text('B')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="jumper1_blue")]], vertical_alignment='center', justification='center')
jumper1_weight =    sg.Col([[sg.Text('Weight')],[sg.Slider(range=(0,255), orientation='v', size=(10,20), enable_events=True, key="jumper1_weight")]], vertical_alignment='center', justification='center')
jumper1_trigger =     sg.Col([[sg.Button("Trigger", key="jumper1_trigger")]], vertical_alignment='center', justification='center')
jumper1_mute =     sg.Col([[sg.Button("Mute", key="jumper1_mute")]], vertical_alignment='center', justification='center')
jumper1_column=[[sg.Text('Jumper 1', font="Courier 12 bold")], [jumper1_red], [jumper1_green], [jumper1_blue], [jumper1_trigger], [jumper1_mute], [jumper1_weight]]

jumper2_red =       sg.Col([[sg.Text('R')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="jumper2_red")]], vertical_alignment='center', justification='center')
jumper2_green =     sg.Col([[sg.Text('G')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="jumper2_green")]], vertical_alignment='center', justification='center')
jumper2_blue =      sg.Col([[sg.Text('B')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="jumper2_blue")]], vertical_alignment='center', justification='center')
jumper2_weight =    sg.Col([[sg.Text('Weight')],[sg.Slider(range=(0,255), orientation='v', size=(10,20), enable_events=True, key="jumper2_weight")]], vertical_alignment='center', justification='center')
jumper2_trigger =     sg.Col([[sg.Button("Trigger", key="jumper2_trigger")]], vertical_alignment='center', justification='center')
jumper2_mute =     sg.Col([[sg.Button("Mute", key="jumper2_mute")]], vertical_alignment='center', justification='center')
jumper2_column=[[sg.Text('Jumper 2', font="Courier 12 bold")], [jumper2_red], [jumper2_green], [jumper2_blue], [jumper2_trigger], [jumper2_mute], [jumper2_weight]]

wave1_red =       sg.Col([[sg.Text('R')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="wave1_red")]], vertical_alignment='center', justification='center')
wave1_green =     sg.Col([[sg.Text('G')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="wave1_green")]], vertical_alignment='center', justification='center')
wave1_blue =      sg.Col([[sg.Text('B')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="wave1_blue")]], vertical_alignment='center', justification='center')
wave1_weight =    sg.Col([[sg.Text('Weight')],[sg.Slider(range=(0,255), orientation='v', size=(10,20), enable_events=True, key="wave1_weight")]], vertical_alignment='center', justification='center')
wave1_trigger =     sg.Col([[sg.Button("Trigger", key="wave1_trigger")]], vertical_alignment='center', justification='center')
wave1_mute =     sg.Col([[sg.Button("Mute", key="wave1_mute")]], vertical_alignment='center', justification='center')
wave1_column=[[sg.Text('Wave 1', font="Courier 12 bold")], [wave1_red], [wave1_green], [wave1_blue], [wave1_trigger], [wave1_mute], [wave1_weight]]

wave2_red =       sg.Col([[sg.Text('R')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="wave2_red")]], vertical_alignment='center', justification='center')
wave2_green =     sg.Col([[sg.Text('G')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="wave2_green")]], vertical_alignment='center', justification='center')
wave2_blue =      sg.Col([[sg.Text('B')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="wave2_blue")]], vertical_alignment='center', justification='center')
wave2_weight =    sg.Col([[sg.Text('Weight')],[sg.Slider(range=(0,255), orientation='v', size=(10,20), enable_events=True, key="wave2_weight")]], vertical_alignment='center', justification='center')
wave2_trigger =     sg.Col([[sg.Button("Trigger", key="wave2_trigger")]], vertical_alignment='center', justification='center')
wave2_mute =     sg.Col([[sg.Button("Mute", key="wave2_mute")]], vertical_alignment='center', justification='center')
wave2_column=[[sg.Text('Wave 2', font="Courier 12 bold")], [wave2_red], [wave2_green], [wave2_blue], [wave2_trigger], [wave2_mute], [wave2_weight]]

glow_red =       sg.Col([[sg.Text('R')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="glow_red")]], vertical_alignment='center', justification='center')
glow_green =     sg.Col([[sg.Text('G')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="glow_green")]], vertical_alignment='center', justification='center')
glow_blue =      sg.Col([[sg.Text('B')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="glow_blue")]], vertical_alignment='center', justification='center')
glow_weight =    sg.Col([[sg.Text('Weight')],[sg.Slider(range=(0,255), orientation='v', size=(10,20), enable_events=True, key="glow_weight")]], vertical_alignment='center', justification='center')
glow_trigger =     sg.Col([[sg.Button("Trigger", key="glow_trigger")]], vertical_alignment='center', justification='center')
glow_mute =     sg.Col([[sg.Button("Mute", key="glow_mute")]], vertical_alignment='center', justification='center')
glow_column=[[sg.Text('Glow', font="Courier 12 bold")], [glow_red], [glow_green], [glow_blue],  [glow_trigger], [glow_mute], [glow_weight]]

master_red =       sg.Col([[sg.Text('R')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="master_red")]], vertical_alignment='center', justification='center')
master_green =     sg.Col([[sg.Text('G')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="master_green")]], vertical_alignment='center', justification='center')
master_blue =      sg.Col([[sg.Text('B')],     [sg.Spin([ i for i in range(0,255)], initial_value=100, size=[3, 1], enable_events=True, key="master_blue")]], vertical_alignment='center', justification='center')
master_master =    sg.Col([[sg.Text('Weight')],[sg.Slider(range=(0,255), orientation='v', size=(10,20), enable_events=True, key="master_master")]], vertical_alignment='center', justification='center')
master_trigger =     sg.Col([[sg.Button("Trigger", key="master_trigger")]], vertical_alignment='center', justification='center')
master_mute =     sg.Col([[sg.Button("Mute", key="master_mute")]], vertical_alignment='center', justification='center')
master_column=[[sg.Text('Master', font="Courier 12 bold")], [master_red], [master_green], [master_blue], [master_trigger], [master_mute], [master_master]]


mixer_layout = [
    [   
        sg.Col([[ sg.Graph(canvas_size=(800, 200), graph_bottom_left=(0, 0), graph_top_right=(800, 200), background_color='grey', enable_events=True, key='graph')]], vertical_alignment='center', justification='center' )
    ],
    [
        sg.Col(strobe_column), sg.VerticalSeparator(), sg.Col(rainbow_column), sg.VerticalSeparator(),
        sg.Col(jumper1_column), sg.VerticalSeparator(), sg.Col(jumper2_column), sg.VerticalSeparator(), 
        sg.Col(wave1_column), sg.VerticalSeparator(), sg.Col(wave2_column), sg.VerticalSeparator(),
        sg.Col(glow_column), sg.VerticalSeparator(), sg.Col(master_column),
    ]
]

connection_layout = [
    [sg.Text('Enter IP Address', key="ip_label")],
    [sg.Input(key='$ip_address')],
    [sg.Button('Connect'), sg.Button('Exit')],
]

layout = [
    [sg.pin(sg.Col(connection_layout, key="$connection_layout", visible=True))],
    [sg.pin(sg.Col(mixer_layout, key="$mixer_layout", visible=False))]    
]
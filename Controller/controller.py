import PySimpleGUI as sg
import sounddevice as sd
from pythonosc import udp_client
from gui_layout import *
import random
import ipaddress
import numpy as np
import math
from scipy.fft import fft, fftfreq, rfft

# from midi import MidiConnector

# conn = MidiConnector('/dev/ttyACM0')

# while True:
#     msg = conn.read() 
#     print(msg)

import mido

with mido.open_input(mido.get_output_names()[1]) as inport:
    for msg in inport:
        print(msg)


class DiscoLigt:
    connection: udp_client

    def valid_ip(self, address):
        try: 
            print (ipaddress.ip_address(address))
            return True
        except:
            return False
    
    def connect(self, address) -> bool:
          if not self.valid_ip(address):
              return False
          self.connection = udp_client.SimpleUDPClient(address, 5005)
          self.connection.send_message("/sparkle_1/brightness/b", 0.0)
          return True
    

def record_audio():
    duration_s = 40 / 1000
    sample_rate = 44100
    gain = 20*10*10*10*35
    recording_size = int(duration_s * sample_rate)
    recording = sd.rec(recording_size, samplerate=sample_rate, channels=1, dtype='float64')
    sd.wait()
    recording = recording[:, 0]
    frequencies = np.log(np.abs(rfft(recording)))*gain
    
    for i in range(0, len(frequencies)):
        frequencies[i] = frequencies[i] / (len(frequencies) - i)**2

    return frequencies

def draw_spectrogram():
    graph = window['graph'] 
    width = graph.CanvasSize[0]
    height = graph.CanvasSize[1]

    frequency_data = record_audio()


    # frequency_data = frequency_data[0:np.min([len(frequency_data), 1000])]
    # frequency_data = height * (frequency_data / 15)
    # print(np.mean(frequency_data))
    bar_width = width/len(frequency_data)
    xpos_left = 0
    graph.erase()
    for value in frequency_data:
        graph.draw_rectangle((xpos_left, 0), (xpos_left + bar_width, value), fill_color='black', line_color='white')
        xpos_left += bar_width


window = sg.Window('Window Title', layout, element_justification='c', finalize=True)
dl = DiscoLigt()
# print(get_spectrogram())



while True:  # Event Loop
    draw_spectrogram()
    event, values = window.Read(timeout = 100)
    if event == "__TIMEOUT__":
        continue
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Connect':
        ip_input = values['$ip_address']
        if dl.connect(address=ip_input):
            window["$mixer_layout"].Update(visible = True)
            window["$connection_layout"].Update(visible = False)
        else:
            window["ip_label"].Update(text_color="#cc1515")
            window["ip_label"].Update(value="Enter a valid IP Address")

    

window.close()
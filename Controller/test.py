#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""
from gui_layout import *
import PySimpleGUI as sg
import asyncio
import numpy as np
import sounddevice as sd
from scipy.fft import fft, fftfreq, rfft


device = 4
block_duration = 100
gain = 20*10*10*10*35

window = sg.Window('Window Title', layout, element_justification='c', finalize=True)

def draw_audio(indata, frames, time, status):
    if any(indata):
        magnitude = np.abs(np.fft.rfft(indata[:, 0]))
        magnitude *= gain
        print(magnitude)
        graph = window['graph'] 
        width = graph.CanvasSize[0]
        height = graph.CanvasSize[1]

        recording = indata[:, 0]
        frequencies = np.log(np.abs(rfft(recording)))*gain
        
        for i in range(0, len(frequencies)):
            frequencies[i] = frequencies[i] / (len(frequencies) - i)**2
        
        bar_width = width/len(frequencies)
        xpos_left = 0
        graph.erase()
        for value in frequencies:
            graph.draw_rectangle((xpos_left, 0), (xpos_left + bar_width, value), fill_color='black', line_color='white')
            xpos_left += bar_width

async def record_audio(buffer, **kwargs):
    loop = asyncio.get_event_loop()
    event = asyncio.Event()
    idx = 0

    def callback(indata, frame_count, time_info, status):
        nonlocal idx
        if status:
            print(status)
        remainder = len(buffer) - idx
        if remainder == 0:
            loop.call_soon_threadsafe(event.set)
            raise sd.CallbackStop
        indata = indata[:remainder]
        buffer[idx:idx + len(indata)] = indata
        idx += len(indata)

    stream = sd.InputStream(callback=callback, dtype=buffer.dtype,
                            channels=buffer.shape[1], **kwargs)
    with stream:
        await event.wait()

try:
    samplerate = sd.query_devices(device, 'input')['default_samplerate']
    stream = sd.InputStream(device=device, channels=1, callback=draw_audio,
                        blocksize=int(samplerate * block_duration / 1000),
                        samplerate=samplerate)
    with stream:
        while True:
            event, values = window.Read(timeout = 10)
            
except KeyboardInterrupt:
    exit(0)
except Exception as e:
    exit(0)

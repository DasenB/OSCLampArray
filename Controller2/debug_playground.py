import sounddevice as sd
import numpy as np

frequency = 500
amplitude = 0.2

print(sd.query_devices())
print("========")
print(sd.query_hostapis())

for i in range(0, 200):
    start_idx = 0
    samplerate = sd.query_devices(i, 'output')['default_samplerate']

    def callback(outdata, frames, time, status):
        if status:
            return
        global start_idx
        t = (start_idx + np.arange(frames)) / samplerate
        t = t.reshape(-1, 1)
        outdata[:] = amplitude * np.sin(2 * np.pi * frequency * t)
        start_idx += frames

    with sd.OutputStream(device=i, blocksize=1024, callback=callback, dtype='float32', channels=1):
        print('#' * 80)
        print('Testing device=' + str(i))
        print("Press key for next")
        print('#' * 80)
        input()

    


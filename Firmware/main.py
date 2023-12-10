from machine import Pin
from time import sleep
from neopixel import NeoPixel
import sys
import select
import time
from collections import deque

class Firmware:

  led_count: int
  neopixel: NeoPixel

  def __init__(self, led_count: int = 249, data_pin: int = 15) -> None:
    self.led_count = led_count
    neopixel_led_pin = Pin(data_pin, Pin.OUT)
    self.neopixel = NeoPixel(neopixel_led_pin, self.led_count)
    self.update_led_count()
    print("LEDs: " + str(self.led_count))

  def update_led_count(self) -> int:
    self.led_count = int(sys.stdin.buffer.read(7))
    return self.led_count

  def read_led_buffer(self) -> bytes:
    data = sys.stdin.buffer.read(self.led_count * 3)
    return data
  
  def run(self):
    # counter = 0
    while True:
      # start_time = time.time_ns()
      data = self.read_led_buffer()
      for i in range(self.led_count):
        self.neopixel[i] = (data[i], data[i+1], data[i+2])
      self.neopixel.write()
      # end_time =  time.time_ns()
      # duration = float(end_time - start_time)/1000000000
      # print(str(counter) + ": " + str(duration))
      # counter += 1
      # # It takes around 0.042 seconds to process one frame


firmware = Firmware(led_count=249, data_pin=15)
firmware.run()
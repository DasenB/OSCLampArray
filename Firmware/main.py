from machine import Pin
from neopixel import NeoPixel
import sys
import gc
import micropython

class Firmware:

  led_count: int
  neopixel: NeoPixel
  status_led: Pin

  def __init__(self, led_count: int = 249, data_pin: int = 14) -> None:
    self.status_led = Pin("LED", Pin.OUT)
    neopixel_data_pin = Pin(data_pin, Pin.OUT)
    self.led_count = led_count
    self.neopixel = NeoPixel(neopixel_data_pin, self.led_count)
    self.setup()
    self.data = bytearray([0] * self.led_count * 3)

  def setup(self):
    import time
    self.status_led.toggle()
    for i in range(self.led_count):
      self.neopixel[i] = (255, 255, 255)
      self.neopixel.write()
      self.status_led.toggle()
    time.sleep(15)
    micropython.kbd_intr(-1)

  def read_led_count(self) -> int:
    return int(sys.stdin.buffer.read(7))
  
  # It takes around 0.042 seconds to process one frame
  def run(self):
    while True:
      self.data[:] = sys.stdin.buffer.read(self.led_count * 3)
      for i in range(self.led_count):
        self.neopixel[i] = (self.data[3*i], self.data[3*i+1], self.data[3*i+2])
      self.neopixel.write()
      self.status_led.toggle()
      gc.collect()


firmware = Firmware(data_pin=14, led_count=2*14*7)
firmware.run()
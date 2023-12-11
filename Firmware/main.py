from machine import Pin
from neopixel import NeoPixel
import sys
import gc


class Firmware:

  led_count: int
  neopixel: NeoPixel
  status_led: Pin

  def __init__(self, led_count: int = 249, data_pin: int = 15) -> None:
    self.status_led = Pin("LED", Pin.OUT)
    self.status_led.toggle()
    sys.stdout.write("Enter LED count: \n")
    self.led_count = self.read_led_count()
    neopixel_data_pin = Pin(data_pin, Pin.OUT)
    self.neopixel = NeoPixel(neopixel_data_pin, self.led_count)
    self.status_led.toggle()
    print("LEDs: " + str(self.led_count) + "\n")

  def read_led_count(self) -> int:
    return int(sys.stdin.buffer.read(7))
  
  # It takes around 0.042 seconds to process one frame
  def run(self):

    data = bytearray([0] * self.led_count * 3)
    while True:
      data[:] = sys.stdin.buffer.read(self.led_count * 3)
      for i in range(self.led_count):
        self.neopixel[i] = (data[i], data[i+1], data[i+2])
      self.neopixel.write()
      self.status_led.toggle()
      gc.collect()


firmware = Firmware(data_pin=15)
firmware.run()
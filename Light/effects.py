from pixel import Pixel
import time
import copy
import random
import numpy as np

class Effect:
  r_buffer: list[int]
  g_buffer: list[int]
  b_buffer: list[int]
  pixels: list[Pixel]  
  priority: int
  
  master_brightness: float
  r_brightness: float
  g_brightness: float
  b_brightness: float

  def __init__(self, name: str, pixels: list[Pixel]) -> None:
    self.r_buffer = [0] * len(pixels)
    self.g_buffer = [0] * len(pixels)
    self.b_buffer = [0] * len(pixels)
    self.pixels = copy.deepcopy(pixels)
    self.priority = 1
    self.master_brightness: float = 1.0
    self.r_brightness: float = 1.0
    self.g_brightness: float = 1.0
    self.b_brightness: float = 1.0
    self.name = name

  def mix_brightness(self):
    self.r_buffer = [int(i * self.master_brightness * self.r_brightness) for i in self.r_buffer]
    self.g_buffer = [int(i * self.master_brightness * self.g_brightness) for i in self.g_buffer]
    self.b_buffer = [int(i * self.master_brightness * self.b_brightness) for i in self.b_buffer]

  def get_buffer(self) -> tuple[list[int], list[int], list[int]]:
    return (self.r_buffer, self.g_buffer, self.b_buffer)
  
  def handle_event_brightness_r(self, address: str, value: float):
    if value < 0.0 or value > 1.0:
      return
    self.r_brightness = value

  def handle_event_brightness_g(self, address: str, value: float):
    if value < 0.0 or value > 1.0:
      return
    self.g_brightness = value

  def handle_event_brightness_b(self, address: str, value: float):
    if value < 0.0 or value > 1.0:
      return
    self.b_brightness = value

  def handle_event_brightness_master(self, address: str, value: float):
    if value < 0.0 or value > 1.0:
      return
    self.master_brightness = value

  def setup_brightness_handler(self, dispatcher):
    dispatcher.map(f"/{self.name}/brightness/r", self.handle_event_brightness_r)
    dispatcher.map(f"/{self.name}/brightness/g", self.handle_event_brightness_g)
    dispatcher.map(f"/{self.name}/brightness/b", self.handle_event_brightness_b)
    dispatcher.map(f"/{self.name}/brightness/master", self.handle_event_brightness_master)

  def setup_dispatcher(self, dispatcher):
    print(f"Warning: {str(self)} does not overwrite function 'setup_dispatcher'")



class SparkleEffect(Effect):
  last_update: float
  update_frequency: float

  def __init__(self, name: str, pixels: list[Pixel]) -> None:
    super().__init__(name, pixels)
    self.last_update = 0
    self.update_frequency = 1
  
  def update(self):
    now = time.time()
    if self.last_update + (1/self.update_frequency) > now:
      return
    self.last_update = now
    for i in range(0, len(self.pixels)):
      self.r_buffer[i] = random.randint(0, 255)
      self.g_buffer[i] = random.randint(0, 255)
      self.b_buffer[i] = random.randint(0, 255)
    super().mix_brightness()

  def setup_dispatcher(self, dispatcher):
    super().setup_brightness_handler(dispatcher)


class ColorEffect(Effect):
  def __init__(self, name: str, pixels: list[Pixel]) -> None:
    super().__init__(name, pixels)
  
  def update(self):
    self.r_buffer = [255] * len(self.pixels)
    self.g_buffer = [255] * len(self.pixels)
    self.b_buffer = [255] * len(self.pixels)
    super().mix_brightness()

  def setup_dispatcher(self, dispatcher):
    super().setup_brightness_handler(dispatcher)


# TODO: Check if skipped flashes are a problem on real hardware or a result of PythonSimpleGui and limited to simulator.
class StrobeEffect(Effect):
  last_update: float
  frequency: float
  on_duration: float
  active_flash: bool

  def __init__(self, name: str, pixels: list[Pixel]) -> None:
    super().__init__(name, pixels)
    self.last_update = 0
    self.frequency = 1
    self.on_duration = 0.04
    self.active_flash = False
  
  def update(self):
    now = time.time()
    next_change_time = 0
    if self.active_flash:
      next_change_time = self.last_update + self.on_duration
    else:
      next_change_time = self.last_update + (1/self.frequency)
    if next_change_time > now:
      return
    self.last_update = now

    self.active_flash = not self.active_flash
    self.r_buffer = [int(self.active_flash) * 255] * len(self.pixels)
    self.g_buffer = [int(self.active_flash) * 255] * len(self.pixels)
    self.b_buffer = [int(self.active_flash) * 255] * len(self.pixels)
    super().mix_brightness()

  def setup_dispatcher(self, dispatcher):
    super().setup_brightness_handler(dispatcher)



class WaveEffect(Effect):
  last_update :float
  speed: float
  size: float
  center_x: float
  center_y: float
  wave_radii: list[float]

  def __init__(self, name: str, pixels: list[Pixel]) -> None:
    super().__init__(name, pixels)
    self.last_update = 0
    self.speed = 0.9
    self.size = 35
    self.center_x = 75
    self.center_y = 60
    self.wave_radii = [0]
    self.max_radius = 0
    a = np.array([self.center_x, self.center_y])
    for p in self.pixels:
      b = np.array([p.x, p.y])
      distance = np.sqrt(np.sum((b-a)**2)) + self.size
      if distance > self.max_radius:
        self.max_radius = distance

  
  def update(self):
    now = time.time()
    last_update = self.last_update
    self.last_update = now

    a = np.array([self.center_x, self.center_y])
    index = 0
    for p in self.pixels:
      for r in self.wave_radii:
        b = np.array([p.x, p.y])
        distance = np.sqrt(np.sum((b-a)**2))
        if distance > (r - self.size) and distance < (r + self.size):
          brightness = (255 / (self.size)) * (distance - r)       
          self.r_buffer[index] = brightness
          self.g_buffer[index] = brightness
          self.b_buffer[index] = brightness
        else:
          self.r_buffer[index] = 0
          self.g_buffer[index] = 0
          self.b_buffer[index] = 0
        index += 1
    for i in range(0, len(self.wave_radii)):
      self.wave_radii[i] += self.speed
    keep_radii = []
    for r in self.wave_radii:
      if r <= self.max_radius + 10:
        keep_radii.append(r)
    self.wave_radii = keep_radii
    super().mix_brightness()

  def trigger(self):
    self.wave_radii.append(0)

  def setup_trigger_handler(self, dispatcher):
    dispatcher.map(f"/{self.name}/trigger", self.trigger)

  def setup_dispatcher(self, dispatcher):
    super().setup_brightness_handler(dispatcher)
    print(f"Warning: {str(self)} does not overwrite function 'setup_dispatcher'")


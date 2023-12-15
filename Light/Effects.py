from Pixel import Pixel
import time
import copy
import random
import numpy as np
from collections import deque 

class Effect:
  r_buffer: list[int]
  g_buffer: list[int]
  b_buffer: list[int]
  pixels: list[Pixel]  
  priority: int
  muted: float
  
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
    self.muted = 1.0

  def mix_brightness(self):
    self.r_buffer = [int(i * self.master_brightness * self.r_brightness * self.muted) for i in self.r_buffer]
    self.g_buffer = [int(i * self.master_brightness * self.g_brightness * self.muted) for i in self.g_buffer]
    self.b_buffer = [int(i * self.master_brightness * self.b_brightness * self.muted) for i in self.b_buffer]

  def get_buffer(self) -> tuple[list[int], list[int], list[int]]:
    return (self.r_buffer, self.g_buffer, self.b_buffer)
  
  def handle_event_brightness_r(self, address: str, value: int):
    float_value = float(value) / 255
    if float_value < 0.0 or float_value > 1.0:
      return
    self.r_brightness = float_value

  def handle_event_brightness_g(self, address: str, value: int):
    float_value = float(value) / 255
    if float_value < 0.0 or float_value > 1.0:
      return
    self.g_brightness = float_value

  def handle_event_brightness_b(self, address: str, value: int):
    float_value = float(value) / 255
    if float_value < 0.0 or float_value > 1.0:
      return
    self.b_brightness = float_value

  def handle_event_brightness_master(self, address: str, value: int):
    float_value = float(value) / 255
    if float_value < 0.0 or float_value > 1.0:
      return
    self.master_brightness = float_value

  def handle_event_mute(self, address: str, value: int):
    if value != 0:
      self.muted = 1.0
    else:
      self.muted = 0.0

  def setup_brightness_handler(self, dispatcher):
    dispatcher.map(f"{self.name}/red", self.handle_event_brightness_r)
    dispatcher.map(f"{self.name}/green", self.handle_event_brightness_g)
    dispatcher.map(f"{self.name}/blue", self.handle_event_brightness_b)
    dispatcher.map(f"{self.name}/master", self.handle_event_brightness_master)
    dispatcher.map(f"{self.name}/mute", self.handle_event_mute)

  def setup_dispatcher(self, dispatcher):
    print(f"Warning: {str(self)} does not overwrite function 'setup_dispatcher'")



class SparkleEffect(Effect):
  last_update: float
  update_frequency: float
  trigger_pulled: bool

  def __init__(self, name: str, pixels: list[Pixel]) -> None:
    super().__init__(name, pixels)
    self.last_update = 0
    self.update_frequency = 20.0
    self.trigger_pulled = False
  
  def update(self):
    now = time.time()

    if self.update_frequency == 0 and not self.trigger_pulled:
      return
    if self.update_frequency != 0.0 and self.last_update + (1/self.update_frequency) > now:
      return
    if self.trigger_pulled:
      self.trigger_pulled = False

    self.last_update = now
    for i in range(0, len(self.pixels)):
      self.r_buffer[i] = random.randint(0, 255)
      self.g_buffer[i] = random.randint(0, 255)
      self.b_buffer[i] = random.randint(0, 255)
    super().mix_brightness()

  def handle_event_frequency(self, address: str, value: int):
    self.update_frequency = float(value)

  def handle_event_trigger(self, address: str, value: int):
    if value > 0:
      self.trigger_pulled = True

  def setup_dispatcher(self, dispatcher):
    super().setup_brightness_handler(dispatcher)
    dispatcher.map(f"{self.name}/frequency", self.handle_event_frequency)
    dispatcher.map(f"{self.name}/trigger", self.handle_event_trigger)



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
    self.frequency = 10.0
    self.on_duration = 0.005
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

  def handle_event_frequency(self, address: str, value: int):
    if value != 0:
      self.frequency = float(value)

  def setup_dispatcher(self, dispatcher):
    super().setup_brightness_handler(dispatcher)
    dispatcher.map(f"{self.name}/frequency", self.handle_event_frequency)
    



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
    self.speed = 104
    self.size = 10
    self.center_x = 60
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
    if self.last_update == 0:
      self.last_update = now
    last_update = self.last_update
    self.last_update = now

    a = np.array([self.center_x, self.center_y])
    pixel_index = 0
    for i in range(len(self.pixels)):
        self.r_buffer[i] = 0
        self.g_buffer[i] = 0
        self.b_buffer[i] = 0
    for p in self.pixels:
      for r in self.wave_radii:
        b = np.array([p.x, p.y])
        distance = np.sqrt(np.sum((b-a)**2))
        if distance > (r - self.size) and distance < (r + self.size):
          brightness = (255 / (self.size)) * (distance - r)       
          self.r_buffer[pixel_index] += brightness + self.r_buffer[pixel_index]
          self.g_buffer[pixel_index] += brightness + self.g_buffer[pixel_index]
          self.b_buffer[pixel_index] += brightness + self.b_buffer[pixel_index]
      pixel_index += 1
    for i in range(len(self.pixels)):
        self.r_buffer[i] = min(255, self.r_buffer[i])
        self.g_buffer[i] = min(255, self.g_buffer[i])
        self.b_buffer[i] = min(255, self.b_buffer[i])
    for i in range(0, len(self.wave_radii)):
      self.wave_radii[i] += self.speed * (now - last_update)
    keep_radii = []
    for r in self.wave_radii:
      if r <= self.max_radius + 10:
        keep_radii.append(r)
    self.wave_radii = keep_radii
    super().mix_brightness()

  def trigger(self, address: str, value: int):
    if value > 0:
      self.wave_radii.append(0)

  def setup_trigger_handler(self, dispatcher):
    dispatcher.map(f"{self.name}/trigger", self.trigger)

  def setup_dispatcher(self, dispatcher):
    super().setup_brightness_handler(dispatcher)
    self.setup_trigger_handler(dispatcher)




class JumperEffect(Effect):
  last_update: float
  update_frequency: float
  trigger_pulled: bool
  position: int

  def __init__(self, name: str, pixels: list[Pixel]) -> None:
    super().__init__(name, pixels)
    self.last_update = 0
    self.update_frequency = 20.0
    self.trigger_pulled = False
    self.position = 0
  
  def update(self):
    now = time.time()

    if self.update_frequency == 0 and not self.trigger_pulled:
      return
    if self.update_frequency != 0.0 and self.last_update + (1/self.update_frequency) > now:
      return
    if self.trigger_pulled:
      self.trigger_pulled = False

    self.last_update = now
    self.position = random.randint(0, len(self.pixels))
    for i in range(0, len(self.pixels)):
      value = 0
      if i == self.position:
        value = 255
      self.r_buffer[i] = value
      self.g_buffer[i] = value
      self.b_buffer[i] = value
    super().mix_brightness()

  def handle_event_frequency(self, address: str, value: int):
    self.update_frequency = float(value)

  def handle_event_trigger(self, address: str, value: int):
    if value > 0:
      self.trigger_pulled = True

  def setup_dispatcher(self, dispatcher):
    super().setup_brightness_handler(dispatcher)
    dispatcher.map(f"{self.name}/frequency", self.handle_event_frequency)
    dispatcher.map(f"{self.name}/trigger", self.handle_event_trigger)



class BarEffect(Effect):
  queue: deque
  mapping: dict[float, list[tuple[int, Pixel]]]
  value: float
  last_update_time: float
  update_frequency: float

  def __init__(self, name: str, pixels: list[Pixel]) -> None:
    super().__init__(name, pixels)
    self.mapping = {}
    counter = 0
    for pixel in self.pixels:
      x = pixel.x
      if not x in self.mapping.keys():
        self.mapping[x] = []
      self.mapping[x].append((counter, pixel))
      counter += 1
    size = len(self.mapping.keys())
    self.queue = deque([0] * size, maxlen=size)  
    self.last_update_time = 0
    self.update_frequency = 3
    self.value = 0

  def update_queue(self):
    now = time.time()
    if self.update_frequency == 0:
      self.last_update_time = now
      return
    if self.update_frequency != 0.0 and self.last_update_time + (1/self.update_frequency) > now:
      return
    self.queue.append(self.value)
  
  def update(self):
    
    self.update_queue()

    positions = list(self.mapping.keys())
    positions.sort()
    for i in range(len(positions)):
      value = self.queue[i]
      for pixel_tuple in self.mapping[positions[i]]:
        pixel_index = pixel_tuple[0]
        pixel_object = pixel_tuple[1]
        if pixel_object.y < value:
          self.r_buffer[pixel_index] = 255
          self.g_buffer[pixel_index] = 255
          self.b_buffer[pixel_index] = 255
        else:
          self.r_buffer[pixel_index] = 0
          self.g_buffer[pixel_index] = 0
          self.b_buffer[pixel_index] = 0
    super().mix_brightness()


  def handle_event_value(self, address: str, value: int):
    self.value = float(value)/2.0

  def handle_event_frequency(self, address: str, value: int):
    self.update_frequency = float(value)

  def handle_event_trigger(self, address: str, value: int):
    if self.value > 0:
      self.value = 0
    else:
      self.value = 255

  def setup_dispatcher(self, dispatcher):
    super().setup_brightness_handler(dispatcher)
    dispatcher.map(f"{self.name}/value", self.handle_event_value)
    dispatcher.map(f"{self.name}/frequency", self.handle_event_frequency)
    dispatcher.map(f"{self.name}/trigger", self.handle_event_trigger)
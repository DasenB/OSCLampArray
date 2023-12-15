from Pixel import Pixel
from Effects import Effect
from LampSimulator import LampSimulator
from Lamp import Lamp
from pythonosc.dispatcher import Dispatcher
import asyncio
import numpy as np

class LightShow:
  
  pixels: list[Pixel]
  lamp: Lamp|LampSimulator
  effects: list[Effect]
  dispatcher: Dispatcher

  def __init__(self, lamp: Lamp|LampSimulator):
    self.lamp = lamp
    self.pixels = self.lamp._pixels
    self.effects = []
    self.dispatcher = Dispatcher()

  def blend_by_max(self, buffers: list[list[int]]) -> list[int]:
    result = [0] * len(self.pixels)
    for i in range(0, len(self.pixels)):
      for buffer in buffers:
        if buffer[i] > result[i]:
          result[i] = buffer[i]
    return result
    
  def add_effect(self, effect: Effect):
    effect.setup_dispatcher(self.dispatcher)
    self.effects.append(effect)

  async def test_frame_syncronization(self):
    while True:
      for pixel in self.pixels:
        pixel.r = 255
        pixel.g = 0
        pixel.b = 0
      self.lamp.update(pixels=self.pixels)
      await asyncio.sleep(2)
      for pixel in self.pixels:
        pixel.r = 0
        pixel.g = 255
        pixel.b = 0
      self.lamp.update(pixels=self.pixels)
      await asyncio.sleep(2)
      for pixel in self.pixels:
        pixel.r = 0
        pixel.g = 0
        pixel.b = 255
      self.lamp.update(pixels=self.pixels)
      await asyncio.sleep(2)

  async def test_pixel_order(self):
    counter = 0
    while True:
      for i in range(len(self.pixels)):
        value = 0
        if i == counter:
          print(str(i) + ": " + str(self.pixels[i].x) + "/" + str(self.pixels[i].y))
          value = 255
        self.pixels[i].r = value
        self.pixels[i].g = value
        self.pixels[i].b = value
      self.lamp.update(pixels=self.pixels)
      counter += 1
      await asyncio.sleep(0.1)

  async def run(self):
        
    while True:
      for effect in self.effects:
        effect.update()

      priority = -1
      selected_buffers: list[tuple[list[int], list[int], list[int]]] = []
      for effect in self.effects:
        if effect.priority > priority:
          selected_buffers = []
          priority = effect.priority
        if effect.priority == priority:
          selected_buffers.append(effect.get_buffer())
 
      selected_buffers = np.array(selected_buffers)
      r_buffer = self.blend_by_max(selected_buffers[:, 0])
      g_buffer = self.blend_by_max(selected_buffers[:, 1])
      b_buffer = self.blend_by_max(selected_buffers[:, 2])

      for i in range(0, len(self.pixels)):
        self.pixels[i].r = r_buffer[i]
        self.pixels[i].g = g_buffer[i]
        self.pixels[i].b = b_buffer[i]
      self.lamp.update(pixels=self.pixels)
      await asyncio.sleep(0)
  


from pixel import Pixel
from effects import Effect
from lampsimulator import LampSimulator
from pythonosc.dispatcher import Dispatcher
import asyncio
import numpy as np

class LightShow:
  
  pixels: list[Pixel]
  lamp: LampSimulator
  effects: list[Effect]
  dispatcher: Dispatcher

  def __init__(self, lamp: LampSimulator):
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

  async def run(self):
    while True:
      for effect in self.effects:
        effect.update()

      priority = -1
      selected_buffers: list[list[list[int], list[int], list[int]]] = []
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
  




class Pixel:
  r: int
  g: int
  b: int
  x: int
  y: int
  
  def __init__(self, x = 0, y = 0, diameter = 4) -> None:
    self.r = 255
    self.g = 255
    self.b = 255
    self.x = x
    self.y = y
    self.diameter = diameter
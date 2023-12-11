
class Pixel:
  r: int
  g: int
  b: int
  x: float
  y: float
  diameter: float
  def __init__(self, x: float = 0, y: float = 0, diameter: float = 4) -> None:
    self.r = 255
    self.g = 255
    self.b = 255
    self.x = x
    self.y = y
    self.diameter = diameter
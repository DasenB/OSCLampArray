from Pixel import Pixel
import serial

class Lamp:

    port_name: str
    serial_port: serial.Serial
    data: bytearray

    def __init__(self, serial_port: str):
        self.port_name = serial_port
        self.serial_port = serial.Serial(self.port_name)
        self.width = 21
        self.height = 14
        pixel_spacing = 8.5
        pixels = []
        for x in range(0, self.width):
            for y in range(0, self.height):
                pixel = Pixel(x=x*pixel_spacing, y=y*pixel_spacing, diameter=4)
                pixels.append(pixel)
        self._pixels = pixels
        self.data = bytearray([0] * len(pixels) * 3)

    def update(self, pixels: list[Pixel]) -> None:
        i = 0
        for pixel in pixels:
            pixel_bytes = bytes([pixel.r, pixel.g, pixel.b])
            # pixel_bytes = bytes([0, 0, 100])
            print(str(pixel.r) + "/" + str(pixel.g) + "/" + str(pixel.b) )
            self.data[3*i] = pixel_bytes[0]
            self.data[3*i+1] = pixel_bytes[1]
            self.data[3*i+2] = pixel_bytes[2]
            i += 1
        self.serial_port.write(self.data)
            

        

from pixel import Pixel
import PySimpleGUI as sg


class LampSimulator:

    def __init__(self) -> list[Pixel]:
        self.width = 21
        self.height = 14
        pixel_spacing = 8.5
        pixels = []
        for x in range(0, self.width):
            for y in range(0, self.height):
                pixel = Pixel(x=x*pixel_spacing, y=y*pixel_spacing, diameter=4)
                pixels.append(pixel)
        self._pixels = pixels

        layout = [[   
            sg.Graph(
                canvas_size=(400, 400),
                graph_bottom_left=(0, 0),
                graph_top_right=(400, 400),
                background_color='gray',
                enable_events=True, key='graph'
            )
        ]]
        self._window = sg.Window('Light Simulator', layout, element_justification='c', finalize=True)
        self._graph = self._window['graph'] 
        self._zoom = 2

    def update(self, pixels: Pixel) -> None:
        self._graph.erase()
        for pixel in pixels:
            center = (self._zoom * pixel.x + self._zoom * 10, self._zoom * pixel.y + self._zoom * 10)
            color = '#%02x%02x%02x' % (pixel.r, pixel.g, pixel.b)
            self._graph.draw_circle(center, pixel.diameter/2 * self._zoom, fill_color = color, line_width = 0)
        self._window.Read(timeout = 10)

        

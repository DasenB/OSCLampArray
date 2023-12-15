from LampSimulator import LampSimulator
from LightShow import LightShow
from Effects import SparkleEffect, ColorEffect, StrobeEffect, WaveEffect, JumperEffect, BarEffect
import asyncio
from pythonosc.osc_server import AsyncIOOSCUDPServer
from Lamp import Lamp


# for i in range(0, 14):
#   x =  i * 1200/14 + 1200/14 * 0.5
#   x *= 0.1
#   print("%.3f" % x)

# exit(0)


async def LightshowTask():
  # lamp = LampSimulator()
  lamp = Lamp(serial_port="/dev/serial/by-id/usb-MicroPython_Board_in_FS_mode_e6616407e327a226-if00")
  lightshow = LightShow(lamp=lamp)
  sparkle = SparkleEffect(name="/sparkle", pixels=lamp._pixels)
  color = ColorEffect(name="/color", pixels=lamp._pixels)
  strobe = StrobeEffect(name="/strobe", pixels=lamp._pixels)
  wave1 = WaveEffect(name="/wave1", pixels=lamp._pixels)
  wave2 = WaveEffect(name="/wave2", pixels=lamp._pixels)
  perlin = BarEffect(name="/bars", pixels=lamp._pixels)
  jumper1 = JumperEffect(name="/jumper1", pixels=lamp._pixels)
  jumper2 = JumperEffect(name="/jumper2", pixels=lamp._pixels)
  lightshow.add_effect(effect=sparkle)
  lightshow.add_effect(effect=color)
  lightshow.add_effect(effect=strobe)
  lightshow.add_effect(effect=wave1)
  lightshow.add_effect(effect=wave2)
  lightshow.add_effect(effect=perlin)
  lightshow.add_effect(effect=jumper1)
  lightshow.add_effect(effect=jumper2)

  server = AsyncIOOSCUDPServer(("0.0.0.0", 8000), lightshow.dispatcher, asyncio.get_event_loop())
  transport, protocol = await server.create_serve_endpoint()
  await lightshow.run()
  transport.close()

asyncio.run(LightshowTask())
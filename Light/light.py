from lampsimulator import LampSimulator
from lightshow import LightShow
from effects import SparkleEffect, ColorEffect, StrobeEffect, WaveEffect
import asyncio
from pythonosc.osc_server import AsyncIOOSCUDPServer


# for i in range(0, 14):
#   x =  i * 1200/14 + 1200/14 * 0.5
#   x *= 0.1
#   print("%.3f" % x)

# exit(0)


async def LightshowTask():
  lamp = LampSimulator()
  lightshow = LightShow(lamp=lamp)
  sparkle_1 = SparkleEffect(name="sparkle_1", pixels=lamp._pixels)
  color = ColorEffect(name="color", pixels=lamp._pixels)
  strobe = StrobeEffect(name="strobe", pixels=lamp._pixels)
  wave = WaveEffect(name="wave", pixels=lamp._pixels)
  # lightshow.add_effect(effect=sparkle_1)
  # lightshow.add_effect(effect=color)
  # lightshow.add_effect(effect=strobe)
  lightshow.add_effect(effect=wave)

  server = AsyncIOOSCUDPServer(("0.0.0.0", 5005), lightshow.dispatcher, asyncio.get_event_loop())
  transport, protocol = await server.create_serve_endpoint()
  await lightshow.run()
  transport.close()

asyncio.run(LightshowTask())
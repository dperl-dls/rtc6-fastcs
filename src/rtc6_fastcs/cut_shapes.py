from rtc6_fastcs.device import Rtc6Eth
from rtc6_fastcs.plan_stubs import *
from bluesky.run_engine import RunEngine

RE = RunEngine()
RTC = Rtc6Eth()

await RTC.connect()

# need to find the conversion of bits to distance. Then can do cylinder(length, width, passes)
def cylinder_200l_100w(passes):
    shape = [(-10000,10000,False),(0,5000,True),(20000,5000,True),(20000,-5000,True),(0,-5000,True),(-10000,-10000,True)] * passes
    RE(draw_polygon(RTC, shape)

from rtc6_fastcs.device import Rtc6Eth
from rtc6_fastcs.plan_stubs import *
from bluesky.run_engine import RunEngine

RE = RunEngine()
RTC = Rtc6Eth()

await RTC.connect()

# need to find the conversion of bits to distance. Then can do cylinder(length, width, passes)
def cut_cylinder_200l_100w(passes: int):
    shape = [(-100,100,False),(0,50,True),(200,50,True),(200,-50,True),(0,-50,True),(-100,-100,True)] * passes
    RE(draw_polygon(RTC, shape)

def cut_cylinder(width: int, length: int, passes: int):
    shape = [(-width,width,False),(0,(width/2),True),(length,(width/2),True),(length,(-width/2),True),(0,(-width/2),True),(-width,-width,True)] * passes
    RE(draw_polygon(RTC, shape))

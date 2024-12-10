import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from rtc6_fastcs.device import Rtc6Eth


def line(rtc6: Rtc6Eth, x: int, y: int):
    """add an instruction to draw a line to x, y"""
    yield from bps.abs_set(rtc6.list.add_line.x, x, wait=True)
    yield from bps.abs_set(rtc6.list.add_line.y, y, wait=True)
    yield from bps.trigger(rtc6.list.add_line.proc, wait=True)


def jump(rtc6: Rtc6Eth, x: int, y: int):
    """add an instruction to jump to x, y"""
    yield from bps.abs_set(rtc6.list.add_jump.x, x, wait=True)
    yield from bps.abs_set(rtc6.list.add_jump.y, y, wait=True)
    yield from bps.trigger(rtc6.list.add_jump.proc, wait=True)


def arc(rtc6: Rtc6Eth, x: int, y: int, angle_deg: float):
    """add an instruction to jump to x, y"""
    yield from bps.abs_set(rtc6.list.add_arc.x, x, wait=True)
    yield from bps.abs_set(rtc6.list.add_arc.y, y, wait=True)
    yield from bps.abs_set(rtc6.list.add_arc.angle_deg, angle_deg, wait=True)
    yield from bps.trigger(rtc6.list.add_arc.proc, wait=True)


def rectangle(rtc6: Rtc6Eth, x: int, y: int, origin: tuple[int, int] = (0, 0)):
    """add instructions to draw a rectangle with dimensions x, y and lower left corner at origin"""
    yield from jump(rtc6, *origin)
    yield from line(rtc6, x, origin[1])
    yield from line(rtc6, x, y)
    yield from line(rtc6, origin[0], y)
    yield from line(rtc6, *origin)


@bpp.run_decorator()
def draw_square(rtc6: Rtc6Eth, size: int):
    yield from bps.stage(rtc6)
    yield from rectangle(rtc6, size, size)
    yield from bps.trigger(rtc6)


JumpOrLineInput = tuple[int, int, bool] # x, y, laser_on
ArcInput = tuple[int, int, float]


@bpp.run_decorator()
def draw_polygon(rtc6: Rtc6Eth, points: list[JumpOrLineInput]):
    yield from bps.stage(rtc6)
    yield from jump(rtc6, *points[0][:-1])
    for point in points[1:]:
        if point[2]:
            yield from line(rtc6, *point[:-1])
        else:
            yield from jump(rtc6, *point[:-1])
    yield from bps.trigger(rtc6)


@bpp.run_decorator()
def draw_polygon_with_arcs(rtc6: Rtc6Eth, points: list[JumpOrLineInput | ArcInput]):
    yield from bps.stage(rtc6)
    if len(points[0]) != 2:
        raise ValueError("List of lines/arcs must start with a single point to jump to")
    yield from jump(rtc6, *points[0])
    for point in points[1:]:
        if isinstance(point[2], bool):
            if point[2]:
                yield from line(rtc6, *point[:-1])
            else:
                yield from jump(rtc6, *point[:-1])
        else:
            yield from arc(rtc6, *point)
    yield from bps.trigger(rtc6)

@bpp.run_decorator()
def go_to_home(rtc6: Rtc6Eth):
    yield from bps.stage(rtc6)
    yield from jump(rtc6, 0,0)

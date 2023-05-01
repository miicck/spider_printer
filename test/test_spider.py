from spider_printer import Spider
from spider_printer.spider.spider import MM_PER_REV
from spider_printer.spider.fake_gpio import FakeGPIO
import numpy as np


def test_spider_position():
    s = Spider(gp=FakeGPIO(), initial_position=(0, 0, 0))
    for n in range(100):
        x = np.random.random(3)
        x[2] = -1 - x[2]
        s.position = x
        assert max(abs(s.position - x)) < 0.1, f"{s.position} != {x}"


def test_spider_position_nonzero_start():
    x0 = np.array((0, 0, -4), dtype=float)
    s = Spider(gp=FakeGPIO(), initial_position=x0)
    assert max(abs(s.position - x0)) < 0.1

    for n in range(100):
        x = np.random.random(3)
        x[2] = -1 - x[2]
        s.position = x
        assert max(abs(s.position - x)) < 0.1, f"{s.position} != {x}"

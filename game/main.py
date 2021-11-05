import pygame as pg

from . import package_dir
from .gamecore import Core


def main():
    pg.init()

    pg.display.set_icon(pg.image.load(package_dir / 'images/icon.png'))
    window = pg.display.set_mode((925, 600))
    pg.display.set_caption('My pygame')
    clock = pg.time.Clock()

    gc = Core(window)

    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                return

        gc.update(events)

        gc.draw()

        clock.tick(gc.FPS)

import pygame as pg
from pygame import Vector2

from . import (
    package_dir,
    tools,
)
from .gameobject import GameObject


class Core:

    FPS = 60

    def __init__(self, window: pg.Surface) -> None:
        self.window = window
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = self.window.get_bounding_rect().size

        # Load graphics and sounds
        self.GFX = tools.load_graphics(package_dir / 'images')
        self.SFX = tools.load_sounds(package_dir / 'sounds')

        # Lists that store held down, pressed, and released keys.
        self.keys = [False]*360
        self.keys_pressed = [False]*360
        self.keys_released = [False]*360
        # First item will become tuple with mouse position, the rest are True/False if a button is pressed.
        self.mouse = [False]*17
        # Stores the positions where every mouse button was last pressed. First item not used.
        self.mouse_pressed_at = [None]*17
        # Stores if the mouse buttons were pressed/released in the latest loop. First item not used.
        self.mouse_pressed = [False]*17
        self.mouse_released = [False]*17

        self.player = GameObject(self.GFX['nat.png'], size=(60,50))
        self.playerspeed = 4


    def update(self, events: list[pg.event.Event]) -> None:
        """Function in charge of everything that happens during a game loop"""

        self.update_inputs(events)
        self.check_player_input()


    def check_player_input(self) -> None:

        if self.mouse_pressed[1]:
            ...

        if self.keys_pressed[pg.K_ESCAPE]:
            ...

        move = pg.Vector2()
        if self.keys[pg.K_w]:
            move.y -= self.playerspeed
        if self.keys[pg.K_s]:
            move.y += self.playerspeed
        if self.keys[pg.K_a]:
            move.x -= self.playerspeed
        if self.keys[pg.K_d]:
            move.x += self.playerspeed
        if move != pg.Vector2():
            move.scale_to_length(self.playerspeed)
            self.player.pos += move


    def update_inputs(self, events: list[pg.event.Event]) -> None:
        """Updates which keys & buttons are pressed"""

        # Saves the input states from the last loop
        keys_prev = self.keys.copy()
        mouse_prev = self.mouse.copy()

        for event in events:
            match event.type:
                case pg.MOUSEBUTTONDOWN:
                    self.mouse[event.button] = True
                case pg.MOUSEBUTTONUP:
                    self.mouse[event.button] = False
                case pg.MOUSEMOTION:
                    self.mouse[0] = event.pos
                case pg.KEYDOWN:
                    self.keys[event.key] = True
                case pg.KEYUP:
                    self.keys[event.key] = False

        # Checks where mouse buttons were clicked
        # and where they were released
        for i, (prev, now) in enumerate(zip(mouse_prev[1:], self.mouse[1:]), start=1):
            if pressed := not prev and now:
                self.mouse_pressed_at[i] = self.mouse[0]
            self.mouse_pressed[i] = pressed
            self.mouse_released[i] = prev and not now

        # Checks which keys were pressed or released
        for i, (prev, now) in enumerate(zip(keys_prev, self.keys)):
            self.keys_pressed[i] = not prev and now
            self.keys_released[i] = prev and not now

    def draw(self) -> None:
        self.window.fill((0, 0, 0))

        self.player.draw(self.window)

        pg.display.update()

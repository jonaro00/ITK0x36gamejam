from os import P_OVERLAY
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
        self.WINDOW_RECT = self.window.get_rect()
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = self.WINDOW_RECT.size

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
        self.playerspeed = int(Core.FPS / 15)
        self.pathing_to = self.player.rect.center
        self.pointer = Pointer(self.GFX['pointer.png'], pos=(-100, -100))

        self.Q_CD = int(Core.FPS * 1)
        self.q_cd = 0
        self.lazers: list[Lazer] = []

        self.W_CD = int(Core.FPS * 8)
        self.w_cd = 0
        self.flash = 0
        self._flash = pg.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))#), depth=pg.SRCALPHA)
        self._flash.fill((255,255,255))
        self.flash_dur = int(Core.FPS * 2)

    def update(self, events: list[pg.event.Event]) -> None:
        """Function in charge of everything that happens during a game loop"""

        self.update_inputs(events)
        self.check_player_input()

        self.pointer.update()
        for laz in self.lazers.copy():
            if not laz.rect.colliderect(self.WINDOW_RECT):
                laz.kill()
            laz.update()


    def check_player_input(self) -> None:

        if self.mouse[3]:
            self.pointer = Pointer(self.GFX['pointer.png'], pos=self.mouse[0], centered=True)
            self.pathing_to = self.mouse[0]

        if move := (Vector2(self.pathing_to) - Vector2(self.player.rect.center)):
            if move.length() > self.playerspeed:
                move.scale_to_length(self.playerspeed)
            self.player.pos += move

        self.q_cd -= 1
        if self.keys_pressed[pg.K_q] and self.q_cd <= 0:
            self.lazers.append(Lazer(self.mouse[0], self.GFX['lazer.png'], pos=Vector2(self.player.rect.center)+(5,5), centered=True, kill_func=self.lazers.remove))
            self.lazers.append(Lazer(self.mouse[0], self.GFX['lazer.png'], pos=Vector2(self.player.rect.center)+(-5,5), centered=True, kill_func=self.lazers.remove))
            self.q_cd = self.Q_CD

        self.w_cd -= 1
        if self.flash > 0:
            self.flash -= 1
        if self.keys_pressed[pg.K_w] and self.w_cd <= 0:
            self.flash = self.flash_dur
            self.w_cd = self.W_CD


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

        self.pointer.draw(self.window)
        self.player.draw(self.window)

        for laz in self.lazers:
            laz.draw(self.window)

        if self.flash >= 0:
            self._flash.set_alpha(int(self.flash / self.flash_dur * 190))
            self.window.blit(self._flash, (0,0))

        pg.display.update()


class Pointer(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = int(Core.FPS * 0.6)
    def update(self):
        self.time -= 1
        if self.time < 0:
            self.visible = False


class Lazer(GameObject):
    speed = 8
    def __init__(self, target, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.angle_towards(target)
        self.move = (Vector2(target) - Vector2(self.rect.center))
        self.move.scale_to_length(self.speed)
    def update(self):
        self.pos += self.move

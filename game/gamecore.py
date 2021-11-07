from random import choice, randint
from collections import defaultdict

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

        pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_CROSSHAIR)

        # Load graphics and sounds
        self.GFX = tools.load_graphics(package_dir / 'images')
        self.SFX = tools.load_sounds(package_dir / 'sounds')

        # Dicts that store held down, pressed, and released keys.
        self.keys = defaultdict(bool)
        self.keys_pressed = defaultdict(bool)
        self.keys_released = defaultdict(bool)
        # Is the mouse button pressed?
        self.mouse = defaultdict(bool)
        # Current mouse position
        self.mouse_pos = (0, 0)
        # Stores the positions where every mouse button was last pressed.
        self.mouse_pressed_at = {}
        # Stores if the mouse buttons were pressed/released in the latest loop.
        self.mouse_pressed = defaultdict(bool)
        self.mouse_released = defaultdict(bool)

        self.gameover = False

        self.bg = GameObject(self.GFX['bg.png'])

        self.player = GameObject(self.GFX['nat.png'], size=(60,50), pos=self.WINDOW_RECT.center, centered=True)
        self.playerspeed = int(Core.FPS / 15)
        self.pathing_to = self.player.rect.center
        self.pointer = Pointer(self.GFX['pointer.png'], pos=(-100, -100))

        self.hp = 10
        self.hp_cd = 0
        self.HP_CD = Core.FPS * 1
        self.points = 0

        self.enemies: list[Enemy] = []
        Enemy.textures = [
            self.GFX['hotdog.png'],
            self.GFX['simonbigbrain.png'],
            self.GFX['simonpog.png'],
        ]
        self.enemy_size = (32, 32)

        self.Q_CD = int(Core.FPS * 1)
        self.q_cd = 0
        self.lazers: list[Lazer] = []

        self.W_CD = int(Core.FPS * 8)
        self.w_cd = 0
        self.flash = 0
        self._flash = pg.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))#), depth=pg.SRCALPHA)
        self._flash.fill((255,255,255))
        self.flash_dur = int(Core.FPS * 2)

        self.E_CD = int(Core.FPS * 1)
        self.e_cd = 0
        self.bomb = None

    def update(self, events: list[pg.event.Event]) -> bool | None:
        """Function in charge of everything that happens during a game loop"""

        self.update_inputs(events)

        if self.gameover:
            # wait for game restart
            if self.keys_pressed[pg.K_RETURN]:
                return True
            return

        self.check_player_input()

        # move player
        if move := (Vector2(self.pathing_to) - Vector2(self.player.rect.center)):
            if move.length() > self.playerspeed:
                move.scale_to_length(self.playerspeed)
            self.player.pos += move

        # update other units
        self.pointer.update()
        # lazer collisions
        for laz in self.lazers.copy():
            if not laz.rect.colliderect(self.WINDOW_RECT):
                laz.kill()
            if self.bomb and self.bomb.rect.colliderect(laz.rect):
                # explode bomb
                for e in self.enemies.copy():
                    if (Vector2(self.bomb.rect.center) - Vector2(e.rect.center)).length() <= 150:
                        e.kill()
                        self.points += 1
                self.bomb = None
                laz.kill()
            for e in self.enemies.copy():
                if laz.rect.colliderect(e.rect):
                    e.kill()
                    laz.kill()
                    self.points += 1
                    break
            else: laz.update()
        # player collision with enemies
        self.hp_cd -= 1
        for e in self.enemies:
            e.update(self.flash)
            if e.rect.colliderect(self.player.rect) and self.hp_cd <= 0:
                self.hp -= 1
                if self.hp <= 0:
                    self.gameover = True
                    return
                self.hp_cd = self.HP_CD
                break

        # generate enemies
        if not randint(0, 60):
            axis = randint(0,1)
            if axis:
                y = randint(0, self.WINDOW_HEIGHT)
                x = choice([0-self.enemy_size[0], self.WINDOW_WIDTH])
            else:
                x = randint(0, self.WINDOW_WIDTH)
                y = choice([0-self.enemy_size[1], self.WINDOW_HEIGHT])
            self.enemies.append(Enemy(self.player, size=self.enemy_size, pos=(x, y), kill_func=self.enemies.remove))


    def check_player_input(self) -> None:

        if self.mouse[pg.BUTTON_RIGHT]:
            self.pointer = Pointer(self.GFX['pointer.png'], pos=self.mouse_pos, centered=True)
            self.pathing_to = self.mouse_pos

        self.q_cd -= 1
        if self.keys_pressed[pg.K_q] and self.q_cd <= 0:
            self.lazers.append(Lazer(self.mouse_pos, self.GFX['lazer.png'], pos=Vector2(self.player.rect.center)+(5,5), centered=True, kill_func=self.lazers.remove))
            self.lazers.append(Lazer(self.mouse_pos, self.GFX['lazer.png'], pos=Vector2(self.player.rect.center)+(-5,5), centered=True, kill_func=self.lazers.remove))
            self.q_cd = self.Q_CD

        self.w_cd -= 1
        if self.flash > 0:
            self.flash -= 1
        if self.keys_pressed[pg.K_w] and self.w_cd <= 0:
            self.flash = self.flash_dur
            self.w_cd = self.W_CD

        if self.bomb is None:
            self.e_cd -= 1
        if self.keys_pressed[pg.K_e] and self.e_cd <= 0:
            self.bomb = GameObject(self.GFX['bomb.png'], pos=self.player.rect.center, centered=True)
            self.e_cd = self.E_CD


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
                    self.mouse_pos = event.pos
                case pg.KEYDOWN:
                    self.keys[event.key] = True
                case pg.KEYUP:
                    self.keys[event.key] = False

        # Checks where mouse buttons were clicked
        # and where they were released
        for btn, now in self.mouse.items():
            prev = mouse_prev.get(btn, False)
            if pressed := not prev and now:
                self.mouse_pressed_at[btn] = self.mouse_pos
            self.mouse_pressed[btn] = pressed
            self.mouse_released[btn] = prev and not now

        # Checks which keys were pressed or released
        for key, now in self.keys.items():
            prev = keys_prev.get(key, False)
            self.keys_pressed[key] = not prev and now
            self.keys_released[key] = prev and not now

    def draw(self) -> None:
        self.window.fill((0, 0, 0))

        self.bg.draw(self.window)

        self.pointer.draw(self.window)
        if self.bomb: self.bomb.draw(self.window)
        for e in self.enemies:
            e.draw(self.window)
        self.player.draw(self.window)

        for laz in self.lazers:
            laz.draw(self.window)

        if self.flash >= 0:
            self._flash.set_alpha(int(self.flash / self.flash_dur * 190))
            self.window.blit(self._flash, (0,0))

        tools.Font.write(self.window, tools.Font.consolas_b24, f'Points: {self.points}', pos=(0, self.WINDOW_HEIGHT), anchor=6)
        tools.Font.write(self.window, tools.Font.consolas_b24, f'HP: {self.hp}', pos=(0, self.WINDOW_HEIGHT-24), anchor=6)
        if self.gameover:
            tools.Font.write(self.window, tools.Font.consolas_b24, 'Game over', pos=self.WINDOW_RECT.center, anchor=4, color=(255,0,0))
            tools.Font.write(self.window, tools.Font.consolas_b24, 'Press [Return] to play again', pos=Vector2(self.WINDOW_RECT.center)+(0,24), anchor=4, color=(255,0,0))

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

class Enemy(GameObject):
    textures = []
    speed = 2
    def __init__(self, target, *args, **kwargs):
        super().__init__(choice(self.textures), *args, **kwargs)
        self.target = target
    def update(self, slowed=False):
        speed = (self.speed if not slowed else self.speed / 2) or 1
        self.move = (Vector2(self.target.rect.center) - Vector2(self.rect.center))
        if self.move != Vector2():
            self.move.scale_to_length(speed)
        self.pos += self.move

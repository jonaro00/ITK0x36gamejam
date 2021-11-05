import pygame as pg

from . import (
    package_dir,
    tools,
)


class Core:

    FPS = 60

    def __init__(self, window):
        self.window = window

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


    def update(self, events):
        """Function in charge of everything that happens during a game loop"""

        self.update_inputs(events)
        self.check_player_input()


    def check_player_input(self):

        if self.mouse_pressed[1]:
            ...

        if self.keys_pressed[pg.K_ESCAPE]:
            ...


    def update_inputs(self, events):
        """Updates which keys & buttons are pressed"""

        # Saves the input states from the last loop
        keys_prev = self.keys.copy()
        mouse_prev = self.mouse.copy()

        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.mouse[event.button] = True
            elif event.type == pg.MOUSEBUTTONUP:
                self.mouse[event.button] = False
            elif event.type == pg.MOUSEMOTION:
                self.mouse[0] = event.pos

            elif event.type == pg.KEYDOWN:
                self.keys[event.key] = True
            elif event.type == pg.KEYUP:
                self.keys[event.key] = False

        # Checks where mouse buttons were clicked
        # and where they were released
        for i, c in enumerate(zip(mouse_prev[1:], self.mouse[1:])):
            if not c[0] and c[1]:
                self.mouse_pressed_at[i + 1] = self.mouse[0]
            self.mouse_pressed[i+1] = not c[0] and c[1]
            self.mouse_released[i+1] = c[0] and not c[1]

        # Checks which keys were pressed or released
        for i, p in enumerate(zip(keys_prev, self.keys)):
            self.keys_pressed[i] = not p[0] and p[1]
            self.keys_released[i] = p[0] and not p[1]

    def draw(self):
        self.window.fill((0, 0, 0))

        # draw

        pg.display.update()

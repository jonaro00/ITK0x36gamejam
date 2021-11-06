import pygame as pg
from pygame import Vector2


class GameObject:
    def __init__(self, texture: pg.Surface, size=None, pos=(0, 0), centered=False, visible=True):
        self.size = texture.get_size() if size is None else size
        self.texture = pg.transform.scale(texture, self.size)
        self._pos = Vector2(pos)
        if centered:
            self.pos -= Vector2(self.size) / 2
        self.visible = visible

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    @property
    def pos(self) -> Vector2:
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = Vector2(value)

    @property
    def rect(self) -> pg.Rect:
        return pg.Rect(self.pos, self.size)

    def draw(self, window):
        if self.visible:
            window.blit(self.texture, self.pos)

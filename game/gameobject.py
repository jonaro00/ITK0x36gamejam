import pygame as pg
from pygame import Vector2


class GameObject:
    def __init__(self, texture: pg.Surface, size=None, pos=(0, 0), centered=False, angle=0, visible=True, kill_func=lambda: None):
        self.size = texture.get_size() if size is None else size
        self.texture = pg.transform.scale(texture, self.size)
        if angle:
            self.texture = pg.transform.rotate(self.texture, angle)
            self.size = self.texture.get_size()
        self._pos = Vector2(pos)
        if centered:
            self.pos -= Vector2(self.size) / 2
        self.visible = visible
        self.kill = lambda: kill_func(self)

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

    def angle_towards(self, point: Vector2):
        self.texture = pg.transform.rotate(self.texture, (Vector2(point) - Vector2(self.rect.center)).angle_to((0, 1)))
        self.size = self.texture.get_size()
        self.pos = self.rect.center - Vector2(self.size) / 2

    def draw(self, window):
        if self.visible:
            window.blit(self.texture, self.pos)

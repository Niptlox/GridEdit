from time import time

import pygame as pg

pg.font.init()
DEFAULT_SHOW_TIME = 5


class InfoMessage:
    # полупрозрачное всплывающие  сообщение внизу экрана
    bg = (82, 82, 91, 220)
    width = 300
    height = 35
    textfont = pg.font.SysFont("", 33)

    def __init__(self, screen_size, align="bottom_right"):
        self.screen_size = screen_size
        self.rect = pg.Rect((self.screen_size[0] - 330, self.screen_size[1] - 45), (300, 32))
        self.align = align
        self.surface = pg.Surface(self.rect.size).convert_alpha()
        self.left_tact = 0
        self.count_tact = 0
        self.show_end_time = 0
        self.update_rect()

    def update_rect(self):
        if self.align == "bottom_right":
            self.rect = pg.Rect((self.screen_size[0] - self.width - 30, self.screen_size[1] - self.height - 20),
                                (self.width, self.height))
        if self.align == "bottom_center":
            self.rect = pg.Rect(((self.screen_size[0] - self.width) // 2, self.screen_size[1] - self.height - 20),
                                (self.width, self.height))
        self.surface = pg.Surface(self.rect.size).convert_alpha()

    def new(self, text, show_sec=DEFAULT_SHOW_TIME):
        text_msg = self.textfont.render(text, True, "#FDE047")
        self.width = max(300, text_msg.get_width() + 20)
        self.update_rect()
        self.show_end_time = time() + show_sec
        self.surface.set_alpha(255)
        self.surface.fill(self.bg)
        self.surface.blit(text_msg, (10, 5))

    def clear(self):
        self.show_end_time = 0

    def draw(self, surface):
        t = time()
        if self.show_end_time > t:
            lost = self.show_end_time - t
            if lost < 1:
                self.surface.set_alpha(int(lost * 250))
            surface.blit(self.surface, self.rect)

    def update(self):
        pass

    def pg_event(self, event):
        pass

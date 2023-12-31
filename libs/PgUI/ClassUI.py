import pygame as pg


class UI:
    def __init__(self, app) -> None:
        self.app = app
        self.screen = app.screen
        self.display = self.app.display
        self.rect = pg.Rect((0, 0), self.display.get_size())

    def _init_ui(self):
        pass

    def draw(self):
        self.screen.blit(self.display, (0, 0))
        pg.display.flip()

    def pg_event(self, event: pg.event.Event):
        pass

    @property
    def onscreenx(self):
        return self.rect.x + self.app.rect.x

    @property
    def onscreeny(self):
        return self.rect.y + self.app.rect.y


class SurfaceUI(pg.Surface):
    def __init__(self, rect, flags=0, surface=None):
        self.rect = pg.Rect(rect)
        super().__init__(self.rect.size, flags, surface)

    def draw(self, surface):
        surface.blit(self, self.rect)

    def pg_event(self, event: pg.event.Event):
        pass

    def set_size(self, size):
        self.rect.size = size
        super().__init__(self.rect.size)

    def convert_alpha(self):
        super().__init__(self.rect.size, 0, super().convert_alpha())
        return self


class ScrollSurface(SurfaceUI):
    """Поле с прокруткой. Только для объектов с методом 'draw(surface)'"""

    def __init__(self, rect, scroll, background="black"):
        super().__init__(rect)
        self.convert_alpha()
        self.scroll_surface = SurfaceUI((scroll, self.rect.size))
        self.objects = []
        self.background = background

    def mouse_scroll(self, dx, dy):
        self.scroll_surface.rect.x += dx
        self.scroll_surface.rect.y += dy

    def add_objects(self, objects):
        self.objects += objects
        for obj in objects:
            if obj.rect.right > self.rect.w:
                self.set_size((obj.rect.right + 5, self.rect.h))
            if obj.rect.bottom > self.rect.h:
                self.set_size((self.rect.w, obj.rect.bottom + 5))

    def draw(self, surface):
        self.scroll_surface.fill((0, 0, 0, 0))
        self.fill(self.background)
        for obj in self.objects:
            obj.draw(self.scroll_surface)
        self.blit(self.scroll_surface, self.scroll_surface.rect)
        surface.blit(self, self.rect)

    def pg_event(self, event: pg.event.Event):
        if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION):
            mouse_pos = tuple(event.pos)
            if self.rect.collidepoint(mouse_pos):
                event.pos = (mouse_pos[0] - self.scroll_surface.rect.x, mouse_pos[1] - self.scroll_surface.rect.y)
                for obj in self.objects:
                    obj.pg_event(event)
                event.pos = mouse_pos
                return True
    
    def set_size(self, size):
        self.scroll_surface.set_size(size)
        super(ScrollSurface, self).set_size(size)


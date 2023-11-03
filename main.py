import pygame as pg

from libs.ColorSchema import ColorSchema
from libs.PgUI import App
from libs.PgUI.InfoMessage import InfoMessage
# from libs.ToolsMenu import ToolsMenu

from moduls.logic.grid import Grid
from moduls.logic.tileset import TileSet
from moduls.logic.tools_menu import ToolsMenu

pg.init()
FULLSCREEN = False
WSIZE = (1200, 700)
WSIZE = 2560/1.5, 1440/1.5


class GridEditApp(App.App):
    def __init__(self):
        if FULLSCREEN:
            screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
            print(screen.get_size())
        else:
            screen = pg.display.set_mode(WSIZE)
        pg.display.set_caption(f"GridEdit")
        pg.display.set_icon(pg.image.load("icon.png"))
        super(GridEditApp, self).__init__(screen)
        self.tileset = TileSet()
        self.tileset.load("moduls/logic")
        self.color_schema = ColorSchema
        th = 250
        self.info_message = InfoMessage(self.rect.size)
        self.grid = Grid(self, (th, 0, self.rect.w - th, self.rect.h), self.color_schema, self.tileset,
                         show_message=self.info_message.new)
        self.tools_menu = ToolsMenu(self, (0, 0, th, self.rect.h), self.color_schema, self.tileset,
                                    on_tool_selected=self.grid.set_tool_tile)
        self.ui_elements = [self.grid, self.tools_menu, self.info_message]

    def pg_event(self, event):
        [el.pg_event(event) for el in self.ui_elements]

    def update(self):
        [el.draw(self.screen) for el in self.ui_elements]
        pg.display.flip()


if __name__ == '__main__':
    app = GridEditApp()
    app.main()

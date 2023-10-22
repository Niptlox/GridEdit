import logging
import pygame as pg

from libs.PgUI import App
from libs.PgUI.InfoMessage import InfoMessage

from moduls.logic.tileset import TileSet

pg.init()
FILENAME = ""
WSIZE = (720 * 2 + 400, 480 * 2 + 200)

logger = logging.getLogger("GridEdit")


# logger.setLevel()
def set_filename(new_filename):
    global FILENAME
    FILENAME = new_filename
    pg.display.set_caption(f"GridEdit '{FILENAME}'")
    return FILENAME






class ToolsMenu:
    def __init__(self, rect, color_schema=ColorSchema, tileset: TileSet = None, on_tool_selected=None, vertical=True):
        self.rect = pg.Rect(rect)
        self.display = pg.Surface(self.rect.size)
        self.color_schema = color_schema
        self.tileset = tileset
        self.on_tool_selected = on_tool_selected
        self.vertical = vertical

        self.active_cell = None
        self.tiles_start_pos = (10, 10)
        self.tile_side = 48
        self.tiles_space_x = 10
        self.tiles_space_y = 10
        self.scroll_active = True
        self.scroll = [0, 0]
        self.max_height = 0
        self.update_display()
        self.tools_rect = []

        self.set_active_tool(None)

    def get_current_surface(self):
        if self.vertical:
            return self._get_current_surface_vertical()
        return self._get_current_surface_horizontal()

    def _get_current_surface_horizontal(self):
        surface = pg.Surface(self.rect.size)
        surface.fill(self.color_schema.toolsmenu_bg_color)
        tiles = self.tileset.get_tiles()
        x, y = self.tiles_start_pos
        for i in range(len(tiles)):
            if i == self.active_cell:
                pg.draw.rect(surface, self.color_schema.toolsmenu_active_cell_color,
                             [x - 1, y - 1, self.tile_side + 2, self.tile_side + 2])
            surface.blit(pg.transform.scale(tiles[i][0], (self.tile_side, self.tile_side)), (x, y))
            x += self.tile_side + self.tiles_space_x
        return surface

    def _get_current_surface_vertical(self):
        self.tools_rect = []
        surface = pg.Surface(self.rect.size)
        surface.fill(self.color_schema.toolsmenu_bg_color)
        tiles = self.tileset.get_tiles()
        groups = self.tileset.groups
        y = self.tiles_start_pos[1]
        start_x = self.tiles_start_pos[0]
        print(self.scroll_active, self.scroll, -self.max_height)
        if self.scroll_active:
            start_x += self.scroll[0]
            y += self.scroll[1]
        i = 0
        for group in groups:
            x = start_x
            name, tile_keys = group["title"], group["tiles"]
            # for i in range(len(tiles)):
            text = self.color_schema.tools_menu_font_1.render(name, True, self.color_schema.tools_menu_font_1_color)
            surface.blit(text, (x, y + 5))
            y += 22 + self.tiles_space_y
            for tile_key in tile_keys:
                x = self.tiles_start_pos[0]
                for r in range(4):
                    key_r = (tile_key, r)
                    tile = self.tileset.get_tile(key_r)
                    if key_r == self.active_cell:
                        pg.draw.rect(surface, self.color_schema.toolsmenu_active_cell_color,
                                     [x - 1, y - 1, self.tile_side + 2, self.tile_side + 2])

                    surface.blit(pg.transform.scale(tile[0], (self.tile_side, self.tile_side)), (x, y))
                    self.tools_rect.append((pg.Rect(x, y, self.tile_side, self.tile_side), key_r))
                    x += self.tile_side + self.tiles_space_x
                y += self.tile_side + self.tiles_space_y
                i += 1
        if y + 10 > self.rect.h + self.scroll[1]:
            self.max_height = y
            self.scroll_active = True
        else:
            self.scroll_active = False
            self.scroll = [0, 0]
        return surface

    def set_active_tool(self, tool):
        self.active_cell = tool
        if self.on_tool_selected:
            self.on_tool_selected(tool)
        self.update_display()

    def mouse_pos2cell(self, mpos):
        mx, my = mpos[0] - self.rect.x, mpos[1] - self.rect.y
        for tool in self.tools_rect:
            if tool[0].collidepoint((mx, my)):
                return tool[1]
        return None

    def pg_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT:
                if self.rect.collidepoint(event.pos):
                    self.set_active_tool(self.mouse_pos2cell(event.pos))

            keyboard_mods = pg.key.get_mods()
            # print(1, self.active_cell)
            if self.active_cell:
                if event.button == pg.BUTTON_WHEELUP and keyboard_mods & pg.KMOD_LALT:
                    self.active_cell = self.active_cell[0], (self.active_cell[1] + 1) % 4
                elif event.button == pg.BUTTON_WHEELDOWN and keyboard_mods & pg.KMOD_LALT:
                    self.active_cell = self.active_cell[0], (self.active_cell[1] - 1) % 4
                elif event.button == pg.BUTTON_WHEELUP and keyboard_mods & pg.KMOD_LSHIFT:
                    num = (self.tileset.lst_tilekeys_of_groups.index(self.active_cell[0]) - 1) % len(
                        self.tileset.lst_tilekeys_of_groups)
                    self.active_cell = self.tileset.lst_tilekeys_of_groups[num], self.active_cell[1]
                elif event.button == pg.BUTTON_WHEELDOWN and keyboard_mods & pg.KMOD_LSHIFT:
                    num = (self.tileset.lst_tilekeys_of_groups.index(self.active_cell[0]) + 1) % len(
                        self.tileset.lst_tilekeys_of_groups)
                    self.active_cell = self.tileset.lst_tilekeys_of_groups[num], self.active_cell[1]
                self.set_active_tool(self.active_cell)
            if self.scroll_active and self.rect.collidepoint(event.pos):
                if event.button == pg.BUTTON_WHEELUP:
                    self.scroll[1] = min(self.scroll[1] + self.color_schema.toolsmenu_vscroll_step, 0)
                    self.update_display()
                elif event.button == pg.BUTTON_WHEELDOWN:
                    if self.color_schema.toolsmenu_vscroll_step > -self.max_height * 2 + self.rect.h:
                        self.scroll[1] -= self.color_schema.toolsmenu_vscroll_step

                    print(self.scroll, self.max_height, self.rect.h, -self.max_height + self.rect.h)
                    self.update_display()

    def update_display(self):
        self.display = self.get_current_surface()

    def draw(self, surface):
        surface.blit(self.display, self.rect)
        mpos = pg.mouse.get_pos()
        if self.rect.collidepoint(mpos):
            tool = self.mouse_pos2cell(mpos)
            if tool:
                label = self.tileset.get_properties(tool[0]).get("label", str(tool[0]).replace("_", " "))
                text = self.color_schema.tools_menu_font_labels.render(label, True, "white", (34, 32, 52, 100))
                surface.blit(text, (mpos[0], mpos[1] - text.get_height()-2))


class GridEditApp(App.App):
    def __init__(self):
        screen = pg.display.set_mode(WSIZE)
        pg.display.set_caption(f"GridEdit")
        pg.display.set_icon(pg.image.load("icon.png"))
        super(GridEditApp, self).__init__(screen)
        self.tileset = TileSet(autorotate_tile=True)
        self.tileset.load("moduls/logic")
        self.color_schema = ColorSchema
        th = 250
        self.info_message = InfoMessage(self.rect.size)
        self.grid = Grid((th, 0, self.rect.w - th, self.rect.h), self.color_schema, self.tileset,
                         show_message=self.info_message.new)
        self.tools_menu = ToolsMenu((0, 0, th, self.rect.h), self.color_schema, self.tileset,
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

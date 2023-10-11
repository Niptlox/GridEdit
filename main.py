import logging
import pygame as pg

from libs.ChunkGrid import ChunkGrid
from libs.PgUI import App
from libs.Tileset import TileSet, int_list

pg.init()

WSIZE = (720 * 2, 480 * 2)

logger = logging.getLogger("GridEdit")
logger.setLevel(logging.DEBUG)


class ColorSchema:
    grid_bg_color = "#9badb7"
    grid_line_color = "#847e87"
    tools_menu_font_1 = pg.font.SysFont("Roboto", 25)
    tools_menu_font_1_color = "#FFFFFF"
    toolsmenu_bg_color = "#4B5563"
    toolsmenu_border_color = "#000000"
    toolsmenu_active_cell_color = "#FFFFFF"
    toolsmenu_vscroll_step = 25


class Grid:
    def __init__(self, rect, color_schema=ColorSchema, tileset: TileSet = None):
        self.rect = pg.Rect(rect)
        self.tile_side = 16
        self.display = pg.Surface(self.rect.size)
        self.color_schema = color_schema
        self.scroll = [0, 0]
        self.zoom_scale = 4
        self.field = ChunkGrid()
        self.tileset: TileSet = tileset
        self.active_tile = None
        self.scroll_step = 1
        self.zoom_step = 0.25
        self.zoom_min = 0.5
        self.mouse_grab_field = None

        self.update_display()

    def get_current_surface(self):
        surface = pg.Surface(self.rect.size)
        surface.fill(self.color_schema.grid_bg_color)
        # size with zoom scale
        _tile_side = self.tile_side * self.zoom_scale
        line_offset_x, line_offset_y = (self.scroll[0] % 1) * _tile_side, (self.scroll[1] % 1) * _tile_side
        x = 0
        while x < self.rect.w:
            pg.draw.line(surface, self.color_schema.grid_line_color,
                         (x + line_offset_x, 0), (x + line_offset_x, self.rect.h))
            x += _tile_side
        y = 0
        while y < self.rect.h:
            pg.draw.line(surface, self.color_schema.grid_line_color,
                         (0, y + line_offset_y), (self.rect.w, y + line_offset_y))
            y += _tile_side
        r = self.zoom_scale * 2.1
        pos = self.scroll[0] * _tile_side + 1, self.scroll[1] * _tile_side + 1
        pg.draw.circle(surface, "red", pos, radius=r, width=1)
        # scroll_tile = self.scroll[0] // self.tile_side, self.scroll[1] // self.tile_side
        for ix in range(-1, int(self.rect.w // _tile_side) + 1):
            for iy in range(-1, int(self.rect.h // _tile_side) + 1):
                tile_pos = pg.Vector2(int_list((ix - self.scroll[0], iy - self.scroll[1])))
                tile = self.field[int_list(tile_pos)]
                # if ix == 0:
                #      print((ix, iy), tile_pos, int_list(tile_pos), "s", self.scroll, tile, line_offset_y)
                if tile is not None:
                    img = self.tileset.get_tile_image(tile, scale=self.zoom_scale)
                    # pos = ix * _tile_side + line_offset_x, iy * _tile_side + line_offset_y
                    pos = (pg.Vector2(self.scroll) + tile_pos) * _tile_side
                    surface.blit(img, pos)

        return surface

    def set_num_of_active_tile(self, num):
        if num is not None:
            self.active_tile = self.tileset.tiles[num][2]

    def set_tool_tile(self, tile):
        if tile is not None:
            self.active_tile = tile

    def mouse_pos2tile(self, mpos):
        _tile_side = self.tile_side * self.zoom_scale
        nx, ny = mpos[0] - self.rect.x - self.scroll[0] * _tile_side, mpos[1] - self.rect.y - self.scroll[
            1] * _tile_side
        return int(nx // _tile_side), int(ny // _tile_side)

    def add_zoom_at_pos(self, add_zoom: float, mpos: tuple):
        if self.zoom_scale > self.zoom_min or add_zoom > 0:
            bb = pg.Vector2(self.rect.size) / self.tile_side / self.zoom_scale - \
                 pg.Vector2(self.rect.size) / self.tile_side / (self.zoom_scale + add_zoom)
            self.zoom_scale += add_zoom
            self.scroll[0] -= bb.x / (self.rect.w / (mpos[0] - self.rect.x))
            self.scroll[1] -= bb.y / (self.rect.h / (mpos[1] - self.rect.y))

    def click_tile(self, pos):
        tile_key, direction = self.field[pos]
        on_click_str = self.tileset.properties[tile_key].get("on_click")
        if on_click_str:
            switch = lambda new_tile_key: self.field.__setitem__(pos, (new_tile_key, direction))
            eval(on_click_str, globals(), locals())
            print(self.field[pos])

    def pg_event(self, event):
        keyboard_mods = pg.key.get_mods()
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                tile_pos = self.mouse_pos2tile(event.pos)
                if event.button == pg.BUTTON_LEFT:
                    logger.debug(tile_pos, self.active_tile)
                    if keyboard_mods & pg.KMOD_LCTRL and self.field[tile_pos]:
                        self.click_tile(tile_pos)
                    elif keyboard_mods & pg.KMOD_LALT and self.field[tile_pos]:
                        self.field[tile_pos] = self.field[tile_pos][0], (self.field[tile_pos][1] + 1) % 4
                    else:
                        self.field[tile_pos] = self.active_tile
                elif event.button == pg.BUTTON_RIGHT:
                    logger.debug(tile_pos, None)
                    if keyboard_mods & pg.KMOD_LALT and self.field[tile_pos]:
                        self.field[tile_pos] = self.field[tile_pos][0], (self.field[tile_pos][1] - 1) % 4
                    else:
                        self.field[tile_pos] = None
                elif event.button == pg.BUTTON_WHEELUP and keyboard_mods & pg.KMOD_LCTRL:
                    self.add_zoom_at_pos(self.zoom_step, event.pos)
                elif event.button == pg.BUTTON_WHEELDOWN and keyboard_mods & pg.KMOD_LCTRL:
                    self.add_zoom_at_pos(-self.zoom_step, event.pos)
                self.update_display()
        elif event.type == pg.MOUSEMOTION:
            if event.buttons[1] and self.rect.collidepoint(event.pos):
                self.scroll[0] += event.rel[0] / (self.tile_side * self.zoom_scale)
                self.scroll[1] += event.rel[1] / (self.tile_side * self.zoom_scale)
                self.update_display()
        if event.type == pg.KEYDOWN:
            if keyboard_mods & pg.KMOD_LCTRL:
                if event.key == pg.K_UP:
                    self.zoom_scale += self.zoom_step
                elif event.key == pg.K_DOWN:
                    self.zoom_scale = max(self.zoom_step, self.zoom_scale - self.zoom_step)
            else:
                if event.key == pg.K_UP:
                    self.scroll[1] += self.scroll_step
                elif event.key == pg.K_DOWN:
                    self.scroll[1] -= self.scroll_step
                elif event.key == pg.K_LEFT:
                    self.scroll[0] += self.scroll_step
                elif event.key == pg.K_RIGHT:
                    self.scroll[0] -= self.scroll_step

            logger.debug(self.zoom_scale, event.mod, event.key, pg.KMOD_LCTRL)
            self.update_display()

    def update_display(self):
        self.display = self.get_current_surface()

    def draw(self, surface):

        surface.blit(self.display, self.rect)
        if self.rect.collidepoint(pg.mouse.get_pos()) and self.active_tile:
            surface.blit(self.tileset.get_tile_image(self.active_tile, scale=2), pg.mouse.get_pos())


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
                    self.scroll[1] = min(self.scroll[1]+self.color_schema.toolsmenu_vscroll_step, 0)
                    self.update_display()
                elif event.button == pg.BUTTON_WHEELDOWN:
                    self.scroll[1] = max(self.scroll[1]-self.color_schema.toolsmenu_vscroll_step, -self.max_height)
                    self.update_display()



    def update_display(self):
        self.display = self.get_current_surface()

    def draw(self, surface):
        surface.blit(self.display, self.rect)


class GridEditApp(App.App):
    def __init__(self):
        screen = pg.display.set_mode(WSIZE)
        pg.display.set_caption("GridEdit")
        super(GridEditApp, self).__init__(screen)
        self.tileset = TileSet(autorotate_tile=True)
        self.tileset.load("moduls/logic")
        self.color_schema = ColorSchema
        th = 250
        self.grid = Grid((th, 0, self.rect.w - th, self.rect.h), self.color_schema, self.tileset)
        self.tools_menu = ToolsMenu((0, 0, th, self.rect.h), self.color_schema, self.tileset,
                                    on_tool_selected=self.grid.set_tool_tile)
        self.ui_elements = [self.grid, self.tools_menu]

    def pg_event(self, event):
        [el.pg_event(event) for el in self.ui_elements]

    def update(self):
        [el.draw(self.screen) for el in self.ui_elements]
        pg.display.flip()


if __name__ == '__main__':
    app = GridEditApp()
    app.main()

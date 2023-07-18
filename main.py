import logging
import math

import pygame as pg
import json
from collections import Iterable, defaultdict
from libs.PgUI import App
import os

pg.init()

WSIZE = (720 * 2, 480 * 2)

logger = logging.getLogger("GridEdit")
logger.setLevel(logging.DEBUG)

SRC_TILESET = "tileset"
LOADER_GRID = "grid"

ExceptionImgLoader = lambda _path: Exception(f"Unknown load_type is used  for the image '{_path}'")
ExceptionSrcLoader = lambda _path, _src_type: Exception(f"In file '{_path}', the source_type is not {_src_type}")
ExceptionTilesetLoader = lambda _path: Exception(f"For 'TileSet' requires the 'tiles'  parameter st file '{_path}'")


def int_list(lst):
    return [math.floor(e) for e in lst]


def load_image(path):
    return pg.image.load(path)


def auto_rotate_image(image: pg.Surface, skip_duplicate=True):
    res_images = []
    buffers_raw = []
    for i in range(4):
        if i == 0:
            res_images.append((image, i))
            buffers_raw.append(image.get_buffer().raw)
            continue
        r_image = pg.transform.rotate(image, 90 * i)
        if skip_duplicate:
            raw = r_image.get_buffer().raw
            if raw in buffers_raw:
                continue
            buffers_raw.append(raw)
        res_images.append((r_image, i))
    return res_images


def load_images(dir_path, data):
    images = []
    if data.get("load_type", LOADER_GRID) == LOADER_GRID:
        img = load_image(os.path.join(dir_path, data.get("path")))
        tsize = data.get("tile_side")
        grid_width = data.get("grid_width")
        if tsize and not grid_width:
            grid_width = img.get_width() // tsize
        elif not tsize and grid_width:
            tsize = img.get_width() // grid_width
        else:
            raise Exception(f"For load_type 'Grid' requires the 'tile_side' or 'grid_width' parameter"
                            f" to load the '{data.get('path')}' image.")

        for y in range(0, img.get_height(), tsize):
            for ix in range(0, grid_width):
                x = ix * tsize
                images.append(img.subsurface((x, y, tsize, tsize)))
    else:
        raise ExceptionImgLoader(data.get("path"))
    return images


def load_source(filepath, src_type, run_exception=True):
    with open(os.path.join(filepath, src_type + ".res")) as f:
        res = json.load(f)
    if res.get("source_type") != src_type:
        if run_exception:
            raise ExceptionSrcLoader(filepath, src_type)
        return None
    return res


class TileSet:
    def __init__(self, autorotate_tile=True):
        self.tiles = []
        self.path = ""
        self.autorotate_tile = autorotate_tile

    def load(self, path):
        self.path = path
        json_data = load_source(self.path, SRC_TILESET)
        self._load_data(json_data)

    def _load_data(self, json_data):
        tiles_data = json_data.get("tiles")
        if tiles_data:
            self.groups = json_data.get("groups", [])
            self.lst_tilekeys_of_groups = sum([e["tiles"] for e in self.groups], [])
            self.processing = json_data.get("processing")
            tiles = _tiles = load_images(self.path, tiles_data)
            _properties = json_data.get("properties")
            keys = _keys = [e[0] if isinstance(e, list) else e for e in _properties]
            self.properties = {key: v for key, *v in _properties}

            if self.autorotate_tile:
                keys = []
                tiles = []
                rotates = []
                for img, key in zip(_tiles, _keys):
                    for r_img, r in auto_rotate_image(img, skip_duplicate=False):
                        keys.append(key)
                        tiles.append(r_img)
                        rotates.append(r)
            else:
                rotates = [0] * len(keys)
            keys_r = list(zip(keys, rotates))
            if json_data.get("preview"):
                preview = load_images(self.path, json_data.get("preview"))
                if self.autorotate_tile:
                    preview = sum([auto_rotate_image(img) for img in preview], [])
                else:
                    preview = [(img, 0) for img in preview]
            else:
                preview = tiles

            self.tiles = list(zip(tiles, preview, keys_r))
            self.tiles_dict = {key_r: i for i, key_r in enumerate(keys_r)}
        else:
            raise ExceptionTilesetLoader(self.path)

    def get_tile(self, key):
        if isinstance(key, str):
            key = (key, 0)
        return self.tiles[self.tiles_dict.get(key)]

    def get_tiles(self):
        return self.tiles

    def get_tile_image(self, key, scale=1):
        img = self.get_tile(key)[0]
        if scale == 1:
            return img
        return pg.transform.scale(img, pg.Vector2(img.get_size()) * scale)


class ChunkGrid:
    def __init__(self, chunk_size=32, store_tile_locations=False):
        self.chunks_field = {}
        self.chunk_size = chunk_size
        self.store_tile_locations = store_tile_locations
        self.tile_locations = defaultdict(list)

    def __getitem__(self, item):
        if isinstance(item, Iterable):
            item = list(item)
            if len(item) == 2:
                return self.chunk(self.xy2chunk_pos(item))[item[1] % self.chunk_size][item[0] % self.chunk_size]
        logger.error(f"Error Grid.get_item({item})")

    def __setitem__(self, key, value):
        if isinstance(key, Iterable):
            item = pos = tuple(key)
            if self.store_tile_locations:
                last_tile = self.chunk(self.xy2chunk_pos(item))[item[1] % self.chunk_size][item[0] % self.chunk_size]
                if last_tile is not None:
                    self.tile_locations[last_tile].remove(pos)
                if value is not None:
                    self.tile_locations[value].append(pos)
            if len(item) == 2:
                self.chunk(self.xy2chunk_pos(item))[item[1] % self.chunk_size][item[0] % self.chunk_size] = value
        logger.error(f"Error Grid.set_item({key}, {value})")

    def chunk(self, chunk_pos, default=True):
        chunk = self.chunks_field.get(chunk_pos)
        if chunk:
            return chunk
        if default:
            chunk = self.pass_chunk()
            self.chunks_field[chunk_pos] = chunk
            return chunk
        logger.error(f"Error Grid.chunk({chunk_pos}, default={default})")
        return None

    def pass_chunk(self):
        return [[None] * self.chunk_size for _ in range(self.chunk_size)]

    def xy2chunk_pos(self, xy):
        return xy[0] // self.chunk_size, xy[1] // self.chunk_size


class ColorSchema:
    grid_bg_color = "#9badb7"
    grid_line_color = "#847e87"
    tools_menu_font_1 = pg.font.SysFont("Roboto", 25)
    tools_menu_font_1_color = "#FFFFFF"
    toolsmenu_bg_color = "#4B5563"
    toolsmenu_border_color = "#000000"
    toolsmenu_active_cell_color = "#FFFFFF"


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
        pos = self.scroll[0] * _tile_side+1, self.scroll[1] * _tile_side+1
        pg.draw.circle(surface, "red", pos, radius=r, width=1)
        # scroll_tile = self.scroll[0] // self.tile_side, self.scroll[1] // self.tile_side
        for ix in range(-1, int(self.rect.w // _tile_side) + 1):
            for iy in range(-1, int(self.rect.h // _tile_side) + 1):
                tile_pos = pg.Vector2(int_list((ix - self.scroll[0] , iy - self.scroll[1])))
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
        if self.zoom_scale > self.zoom_step:
            bb = pg.Vector2(self.rect.size) / self.tile_side / self.zoom_scale - \
                 pg.Vector2(self.rect.size) / self.tile_side / (self.zoom_scale + add_zoom)
            self.zoom_scale += add_zoom
            self.scroll[0] -= bb.x / (self.rect.w / (mpos[0] - self.rect.x))
            self.scroll[1] -= bb.y / (self.rect.h / (mpos[1] - self.rect.y))

    def pg_event(self, event):
        keyboard_mods = pg.key.get_mods()
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                tile_pos = self.mouse_pos2tile(event.pos)
                if event.button == pg.BUTTON_LEFT:
                    logger.debug(tile_pos, self.active_tile)
                    self.field[tile_pos] = self.active_tile
                elif event.button == pg.BUTTON_RIGHT:
                    logger.debug(tile_pos, None)
                    self.field[tile_pos] = None
                elif event.button == pg.BUTTON_WHEELUP and keyboard_mods & pg.KMOD_LCTRL:
                    # self.zoom_scale = max(self.zoom_step, self.zoom_scale - self.zoom_step)
                    self.add_zoom_at_pos(-self.zoom_step, event.pos)
                elif event.button == pg.BUTTON_WHEELDOWN and keyboard_mods & pg.KMOD_LCTRL:
                    # self.zoom_scale += self.zoom_step
                    self.add_zoom_at_pos(self.zoom_step, event.pos)
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
        i = 0
        for group in groups:
            x = self.tiles_start_pos[0]
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
        # x, y = self.tiles_start_pos
        # for i in range(len(self.tileset.tiles)):
        #     if x <= mx <= (x + self.tile_side) and y <= my <= (y + self.tile_side):
        #         return i
        #     if self.vertical:
        #         y += self.tile_side + self.tiles_space_y
        #     else:
        #         x += self.tile_side + self.tiles_space_y
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

    def update_display(self):
        self.display = self.get_current_surface()

    def draw(self, surface):
        surface.blit(self.display, self.rect)


class GridEditApp(App.App):
    def __init__(self):
        screen = pg.display.set_mode(WSIZE)
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

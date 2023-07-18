"""import logging
import pygame as pg
import json
from collections import Iterable
from libs.PgUI import App
import os

WSIZE = (720, 480)

logger = logging.getLogger("GridEdit")

SRC_TILESET = "tileset"
LOADER_GRID = "grid"

ExceptionImgLoader = lambda _path: Exception(f"Unknown load_type is used  for the image '{_path}'")
ExceptionSrcLoader = lambda _path, _src_type: Exception(f"In file '{_path}', the source_type is not {_src_type}")
ExceptionTilesetLoader = lambda _path: Exception(f"For 'TileSet' requires the 'tiles'  parameter st file '{_path}'")


def load_image(path):
    return pg.image.load(path)


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
    def __init__(self):
        self.tiles = []
        self.path = ""

    def load(self, path):
        self.path = path
        json_data = load_source(self.path, SRC_TILESET)
        self._load_data(json_data)

    def _load_data(self, json_data):
        tiles_data = json_data.get("tiles")
        if tiles_data:
            tiles = load_images(self.path, tiles_data)
            if json_data.get("preview"):
                preview = load_images(self.path, json_data.get("preview"))
            else:
                preview = tiles
            properties = json_data.get("properties", [None] * len(tiles))
            self.tiles = list(zip(tiles, preview, properties))
            self.tiles_dict = {(value[0] if value else i): i for i, value in enumerate(properties)}
        else:
            raise ExceptionTilesetLoader(self.path)

    def get_tile(self, key):
        return self.tiles[self.tiles_dict.get(key)]

    def get_tiles(self):
        return self.tiles

    def get_tile_image(self, key, scale=1):
        img = self.get_tile(key)[0]
        if scale == 1:
            return img
        return pg.transform.scale(img, pg.Vector2(img.get_size()) * scale)

class ChunkGrid:
    def __init__(self, chunk_size=32):
        self.chunks_field = {}
        self.chunk_size = chunk_size

    def __getitem__(self, item):
        if isinstance(item, Iterable):
            item = list(item)
            if len(item) == 2:
                return self.chunk(self.xy2chunk_pos(item))[item[1] % self.chunk_size][item[0] % self.chunk_size]
        logger.error(f"Error Grid.get_item({item})")

    def __setitem__(self, key, value):
        if isinstance(key, Iterable):
            item = list(key)
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
    toolsmenu_bg_color = "#323c39"
    toolsmenu_border_color = "#000000"
    toolsmenu_active_cell_color = "#FFFFFF"


class Grid:
    def __init__(self, rect, color_schema=ColorSchema, tileset: TileSet = None):
        self.rect = pg.Rect(rect)
        self.tile_side = 16
        self.display = pg.Surface(self.rect.size)
        self.color_schema = color_schema
        self.scroll = [0, 0]
        self.zoom_scale = 1
        self.field = ChunkGrid()
        self.tileset: TileSet = tileset
        self.active_tile = None
        self.update_display()

    def get_current_surface(self):
        surface = pg.Surface(self.rect.size)
        surface.fill(self.color_schema.grid_bg_color)
        _tile_side = self.tile_side * self.zoom_scale
        line_offset_x, line_offset_y = self.scroll[0] % self.tile_side, self.scroll[1] % self.tile_side
        # size with zoom scale
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

        scroll_tile = self.scroll[0] // self.tile_side, self.scroll[1] // self.tile_side

        for ix in range(-1, int(self.rect.w // _tile_side)+1):
            for iy in range(-1, int(self.rect.h // _tile_side)+1):
                tile_pos = ix + scroll_tile[0], iy + scroll_tile[1]
                tile = self.field[tile_pos]
                if tile is not None:
                    img = self.tileset.get_tile_image(tile, scale=self.zoom_scale)
                    pos = tile_pos[0] * _tile_side + self.scroll[0]/self.zoom_scale, tile_pos[1] * _tile_side + self.scroll[1]/self.zoom_scale
                    surface.blit(img, pos)

        return surface

    def set_num_of_active_tile(self, num):
        if num is not None:
            self.active_tile = self.tileset.tiles[num][2][0]

    def mouse_pos2tile(self, mpos):
        nx, ny = mpos[0] - self.rect.x + self.scroll[0], mpos[1] - self.rect.y + self.scroll[1]
        _tile_side = self.tile_side * self.zoom_scale
        return int(nx // _tile_side), int(ny // _tile_side)

    def pg_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            print(event.button)

            if self.rect.collidepoint(event.pos):
                    tile_pos = self.mouse_pos2tile(event.pos)
                    if event.button == pg.BUTTON_LEFT:
                        logger.debug(tile_pos, self.active_tile)
                        self.field[tile_pos] = self.active_tile
                    if event.button == pg.BUTTON_RIGHT:
                        logger.debug(tile_pos, None)
                        self.field[tile_pos] = None
                    self.update_display()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                self.scroll[1] -= 1
            elif event.key == pg.K_DOWN:
                self.scroll[1] += 1
            elif event.key == pg.K_LEFT:
                self.scroll[0] -= 1
            elif event.key == pg.K_RIGHT:
                self.scroll[0] += 1
            if event.mod == pg.KMOD_LCTRL:
                if event.key == pg.K_UP:
                    self.zoom_scale += 0.2
                elif event.key == pg.K_DOWN:
                    self.zoom_scale = max(0.2, self.zoom_scale - 0.2)
            logger.debug(self.zoom_scale, event.mod, event.key, pg.KMOD_LCTRL)
            self.update_display()

    def update_display(self):
        self.display = self.get_current_surface()

    def draw(self, surface):
        surface.blit(self.display, self.rect)


class ToolsMenu:
    def __init__(self, rect, color_schema=ColorSchema, tileset: TileSet = None, on_cell_selected=None):
        self.rect = pg.Rect(rect)
        self.display = pg.Surface(self.rect.size)
        self.color_schema = color_schema
        self.tileset = tileset
        self.on_cell_selected = on_cell_selected
        self.active_cell = None
        self.set_active_cell(0)
        self.tiles_start_pos = (10, 10)
        self.tile_side = 16
        self.tiles_space_x = 6
        self.update_display()

    def get_current_surface(self):
        surface = pg.Surface(self.rect.size)
        surface.fill(self.color_schema.toolsmenu_bg_color)
        tiles = self.tileset.get_tiles()
        x, y = self.tiles_start_pos
        for i in range(len(tiles)):
            if i == self.active_cell:
                pg.draw.rect(surface, self.color_schema.toolsmenu_active_cell_color,
                             [x - 1, y - 1, self.tile_side + 2, self.tile_side + 2])
            surface.blit(tiles[i][0], (x, y))
            x += self.tile_side + self.tiles_space_x
        return surface

    def set_active_cell(self, num):
        self.active_cell = num
        if self.on_cell_selected:
            self.on_cell_selected(num)

    def mouse_pos2cell(self, mpos):
        mx, my = mpos[0] - self.rect.x, mpos[1] - self.rect.y
        x, y = self.tiles_start_pos
        for i in range(len(self.tileset.tiles)):
            if x <= mx <= (x + self.tile_side) and y <= my <= (y + self.tile_side):
                return i
            x += self.tile_side + self.tiles_space_x
        return None

    def pg_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT:
                if self.rect.collidepoint(event.pos):
                    self.set_active_cell(self.mouse_pos2cell(event.pos))
                    self.update_display()

    def update_display(self):
        self.display = self.get_current_surface()

    def draw(self, surface):
        surface.blit(self.display, self.rect)


class GridEditApp(App.App):
    def __init__(self):
        screen = pg.display.set_mode(WSIZE)
        super(GridEditApp, self).__init__(screen)
        self.tileset = TileSet()
        self.tileset.load("moduls/logic")
        self.color_schema = ColorSchema
        self.grid = Grid((0, 40, self.rect.w, self.rect.h - 40), self.color_schema, self.tileset)
        self.tools_menu = ToolsMenu((0, 0, self.rect.w, 40), self.color_schema, self.tileset,
                                    on_cell_selected=self.grid.set_num_of_active_tile)
        self.ui_elements = [self.grid, self.tools_menu]

    def pg_event(self, event):

        [el.pg_event(event) for el in self.ui_elements]

    def update(self):
        [el.draw(self.screen) for el in self.ui_elements]
        pg.display.flip()


if __name__ == '__main__':
    app = GridEditApp()
    app.main()
"""
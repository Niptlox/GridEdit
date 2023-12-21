import math
import os

import pygame as pg
import json

from libs.UClass.UClass import UClass

SRC_TILESET = "tileset"
LOADER_GRID = "grid"
TOP, RIGHT, BOTTOM, LEFT = 0, 1, 2, 3

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
        r_image = pg.transform.rotate(image, -90 * i)
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


class TileSet(UClass):
    def __init__(self, autorotate_tile=True):
        self.path = ""
        self.tiles = []
        self.autorotate_tile = autorotate_tile

    def load(self, path):
        self.path = path
        json_data = load_source(self.path, SRC_TILESET)
        self._load_data(json_data)

    def _load_data(self, json_data):
        tiles_data = json_data.get("tiles")
        self.file_extension = json_data.get("file_extension")
        if tiles_data:
            self.groups = json_data.get("groups", [])
            self.lst_tilekeys_of_groups = sum([e["tiles"] for e in self.groups], [])
            self.processing = json_data.get("processing")
            tiles = _tiles = load_images(self.path, tiles_data)
            _properties = json_data.get("properties")
            keys = _keys = [e[0] if isinstance(e, list) else e for e in _properties]
            self._properties = {key: v for key, v in _properties}

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

    def get_properties(self, tile_key):
        return self._properties.get(tile_key)

    def get_tile(self, key):
        if isinstance(key, str):
            key = (key, 0)
        return self.tiles[self.tiles_dict.get(key)]

    def add_tile(self, key, tile_imgs, properties=None):
        if self.autorotate_tile:
            for rot in range(4):
                self.tiles.append((tile_imgs[rot], tile_imgs[rot], (key, rot)))
                self.tiles_dict[(key, rot)] = len(self.tiles) - 1
        else:
            self.tiles.append((tile_imgs, tile_imgs, key))
            self.tiles_dict[key] = len(self.tiles) - 1

        self._properties[key] = {} if properties is None else properties
        self.lst_tilekeys_of_groups.append(key)

    def get_tiles(self):
        return self.tiles

    def get_tile_image(self, key, scale=1):
        img = self.get_tile(key)[0]
        if scale == 1:
            return img
        return pg.transform.scale(img, pg.Vector2(img.get_size()) * scale)

    def __setstate__(self, state):
        self.tiles = []
        self.autorotate_tile = state["autorotate_tile"]
        self.load(state["path"])

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("tiles")
        return state

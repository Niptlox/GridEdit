from libs import ColorSchema
from libs.GridSurface import Grid as _Grid
from .processing import main
from .chunk_grid import ChunkGrid
from .tileset import TileSet
import pygame as pg


class Grid(_Grid):
    pass

    def __init__(self, app, rect, color_schema=ColorSchema, tileset: TileSet = None, show_message=print):
        super(Grid, self).__init__(app, rect, color_schema, tileset, show_message)
        self.field = ChunkGrid()
        self.f = tileset.new_function("main", self.field)
        self.input_values = {}

    def update_output_input_tiles(self, function_d):
        input_tile_keys = self.tileset.processing["input"].values()
        output_tile_keys = self.tileset.processing["output"].values()
        print(self.field.tile_locations)
        input_poss = [e for tile_key in input_tile_keys for e in self.field.get_poss_of_tile(tile_key)]
        output_poss = [e for tile_key in output_tile_keys for e in self.field.get_poss_of_tile(tile_key)]
        function_d["input_tiles"] = sorted(input_poss)
        function_d["output_tiles"] = sorted(output_poss)

    def set_input_tiles(self, input_val, input_tiles):
        input_1 = self.tileset.processing["input"]["1"]
        input_0 = self.tileset.processing["input"]["0"]
        for pos, val in zip(input_tiles, input_val):
            self.field.set_tile_key(pos, input_1 if val else input_0)

    def get_output_tiles(self, output_tiles):
        output_1 = self.tileset.processing["output"]["1"]
        res = []
        for pos in output_tiles:
            print(pos, self.field[pos])
            res.append(self.field[pos][0] == output_1)
        return res


    def pg_event(self, event):
        super(Grid, self).pg_event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_f:
                self.update_output_input_tiles(self.f)

                inp = [1] * len(self.f["input_tiles"])
                r = self.run_function(self.f, inp)
                self.update_display()
                print("RES", r)
            if event.key == pg.K_u:
                self.update_output_input_tiles(self.f)
                print(self.f)

    def get_input(self, value_num):
        return self.input_values.get(value_num, 0)

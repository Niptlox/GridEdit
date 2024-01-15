from libs import ColorSchema
from libs.CommandHistory import wrap_cls
from libs.GridSurface import Grid as _Grid, CAPTION, get_caption, update_caption
from .processing import main
from .chunk_grid import ChunkGrid
from .tileset import TileSet
import pygame as pg


class Grid(_Grid):
    pass

    def __init__(self, app, rect, color_schema=ColorSchema, tileset: TileSet = None, show_message=print,
                 command_history=None):
        super(Grid, self).__init__(app, rect, color_schema, tileset, show_message, command_history=command_history)
        self.main_field = self.field = ChunkGrid()
        # self.f = tileset.new_function("main", self.field)
        self.edit_function = None

    def update_output_input_tiles(self, function_d):
        input_tile_keys = self.tileset.processing["input"].values()
        output_tile_keys = self.tileset.processing["output"].values()
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
            res.append(self.field[pos][0] == output_1)
        return res

    def pg_event(self, event):
        super(Grid, self).pg_event(event)
        if event.type == pg.KEYDOWN:
            # if event.key == pg.K_f:
            #     self.update_output_input_tiles(self.f)
            #     inp = [1] * len(self.f["input_tiles"])
            #     r = self.field.run_function(self.f, inp, self.tileset)
            #     self.update_display()
            #     print("RES", r)
            # elif event.key == pg.K_u:
            #     self.update_output_input_tiles(self.f)
            #     print(self.f)
            if event.key == pg.K_ESCAPE:
                self.close_function()

    def get_line_tiles(self):
        row, column = super().get_line_tiles()
        if self.app.tools_menu.magic_line_mode and row:
            joint_p, joint_t = (row & column).pop()
            row = {((p, ("path_+", 0)) if p == joint_p else
                    (p, ("bridge_+", p[1] % 2 * 2 + 1)) if self.field[p] in {("path_I", 0), ("path_I", 2),
                                                                             ("bridge_+", 0),
                                                                             ("bridge_+", 1), ("bridge_+", 2),
                                                                             ("bridge_+", 3)}
                    else (p, (t[0], 1))) for p, t in row}
            column = {
                ((p, ("bridge_+", p[0] % 2 * 2)) if self.field[p] in {("path_I", 1), ("path_I", 3),
                                                                      ("bridge_+", 0),
                                                                      ("bridge_+", 1), ("bridge_+", 2),
                                                                      ("bridge_+", 3)}
                 else (p, (t[0], 0))) for p, t in column if p != joint_p}

        return row, column

    def open_function(self, f):
        if self.edit_function:
            self.close_function()
        self.field = f["field"]
        self.edit_function = f
        caption = get_caption()
        caption[1:] = [f'({f["name"]})'] + caption[1:]
        update_caption()
        self.update_display()

    def close_function(self):
        self.field = self.main_field
        self.edit_function = None
        self.update_display()
        if len(get_caption()) > 1:
            get_caption().pop(1)
            update_caption()

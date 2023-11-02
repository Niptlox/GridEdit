from libs.Tileset import TileSet as _TileSet


class TileSet(_TileSet):

    def __init__(self):
        super().__init__(autorotate_tile=True)
        self.opened_function = None
        self.functions = {}
        self.function_last_id = 0

    def get_properties(self, tile_key):
        if tile_key in self.functions:
            return self.functions[tile_key]
        return super().get_properties(tile_key)

    def new_function(self, name, field):
        f = {"name": name, "field": field, "label": f"Func: {name}",
             "input": [], "output": [], "input_tiles": [], "output_tiles": []}
        fid = f"func_{name}_{self.function_last_id}"
        self.function_last_id += 1
        self.functions[fid] = f
        return f

    def run_function(self, fid):
        if fid not in self.functions:
            assert Exception(f"Function '{fid}' is not expected")




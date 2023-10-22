from libs.Tileset import TileSet as _TileSet


class TileSet(_TileSet):
    pass

    def __init__(self):
        super().__init__(autorotate_tile=True)
        self.opened_function = None
        self.functions = {}

    def get_properties(self, tile_key):
        if tile_key in self.functions:
            return self.functions[tile_key]
        return super().get_properties(tile_key)

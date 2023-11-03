from .processing import main
from libs.ChunkGrid import ChunkGrid as _ChunkGrid


class ChunkGrid(_ChunkGrid):
    def __init__(self, ):
        super(ChunkGrid, self).__init__(chunk_size=32, store_tile_locations=True, default_item=lambda: None,
                                        title="ChunkGrid")
        self.function_input = {}
        self.function_result = {}

    def set_tile_key(self, pos, tile_key):
        self[pos] = tile_key, self[pos][1]

    def get_poss_of_tile(self, tile_key):
        res = []
        for rot in 0, 1, 2, 3:
            tile = tile_key, rot
            for pos in self.tile_locations.get(tile, []):
                res.append(pos)
        return res

    def run_function(self, function_d, input_val, tileset):
        field = function_d["field"]
        for key, val in zip(function_d["input"], input_val):
            self.set_function_input(key, val)
        main(field, tileset)
        res = []
        for key in function_d["output"]:
            res.append(self.get_function_result(key))
        return res

    def get_function_input(self, num):
        return self.function_input.get(num)

    def set_function_input(self, num, value):
        self.function_input[num] = value

    def set_function_result(self, num, value):
        self.function_result[num] = value

    def get_function_result(self, num, default=False):
        return self.function_result.get(num, default)

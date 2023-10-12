from libs.ChunkGrid import ChunkGrid
from libs.Tileset import TileSet, TOP, RIGHT, BOTTOM, LEFT


class LogicProcessing:
    def __init__(self, field: ChunkGrid, tileset: TileSet):
        self.field = field
        self.tileset = tileset
        self.runed_pos = set()
        self.function_of_tiles = {eval(self.tileset.properties[tile_key[0]].get("processing"), globals(), locals())
                                  for tile_key in self.tileset.tiles_dict}
        self.run_field = ChunkGrid(self.field.chunk_size, default_item=lambda: [0, 0, 0, 0], store_tile_locations=True)
        self.runed = set()

    def run_tile(self, pos, recursion_run=False):
        self.runed.add(pos)
        tile_key, direction = self.field[pos]
        prop = self.tileset.properties[tile_key]

        switch = lambda new_tile_key: self.field.__setitem__(pos, (new_tile_key, direction))
        x, y = pos
        _around_tiles = [self.run_field[(x, y - 1)][BOTTOM], self.run_field[(x + 1, y)][LEFT],
                         self.run_field[(x, y + 1)][TOP], self.run_field[(x - 1, y)][RIGHT]]
        print("run tile", tile_key, direction, _around_tiles, self.runed)
        around_tiles = [bool(_around_tiles[(i + direction) % 4]) for i in range(4)]
        input_t = [around_tiles[i] for i in prop["input"]]
        if len(input_t) == 1:
            input_t = input_t[0]
        f = eval(prop["processing"], locals())

        output_t = f(input_t)
        if type(output_t) is not list:
            output_t = [output_t]

        for out, i in zip(output_t, prop["output"]):
            self.run_field[pos][(i + direction) % 4] = out

        if recursion_run:
            # pos of (TOP, RIGHT, BOTTOM, LEFT)
            around_poss = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
            start_tiles = self.tileset.processing.get("start_tiles")
            for i in prop["output"]:
                a_pos = around_poss[(i + direction) % 4]
                a_tile = self.field[a_pos]
                if a_pos not in self.runed and a_tile and a_tile[0] not in start_tiles:
                    self.run_tile(a_pos, recursion_run=True)

    def run(self, pos):
        pass


def main(tile_grid: ChunkGrid, tileset):
    start_tiles = tileset.processing.get("start_tiles")
    proc = LogicProcessing(tile_grid, tileset)
    for tile_key in start_tiles:
        for rot in 0, 1, 2, 3:
            tile = tile_key, rot
            for pos in tile_grid.tile_locations.get(tile, []):
                proc.run_tile(pos, recursion_run=True)
    print(proc.run_field.tile_locations)

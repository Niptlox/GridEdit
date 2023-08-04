from libs.ChunkGrid import ChunkGrid
from libs.Tileset import TileSet


class LogicProcessing:
    def __init__(self, field: ChunkGrid, tileset: TileSet):
        self.field= field
        self.tileset = tileset
        self.runed_pos = set()
        self.function_of_tiles = {eval(self.tileset.properties[tile_key].get("processing"), globals(), locals())
                                  for tile_key in self.tileset.tiles_dict}
        self.run_field = ChunkGrid(self.field.chunk_size)
        self.runed = set()

    def run_tile(self, pos):
        self.runed.add(pos)
        tile_key, direction = self.field[pos]
        prop = self.tileset.properties[tile_key]
        switch = lambda new_tile_key: self.field.__setitem__(pos, (new_tile_key, direction))
        x, y = pos
        _around_tiles = [self.run_field[(x, y -1)[2]], self.run_field[(x+1, y)[3]],
                         self.run_field[(x, y-1)[0]], self.run_field[(x-1, y)][1]]
        around_tiles = [bool(_around_tiles[(i+direction%4)]) for i in range(4)]
        input_t = [around_tiles[i] for i in prop["input"]]
        if len(input_t) == 1:
            input_t = input_t[0]
        f = eval(prop["processing"], locals())

        output_t = f(input_t)
        if type(output_t) is not list:
            output_t = [output_t]

        for out, i in zip(output_t, prop["output"]):
            self.run_field[pos][(i + direction) % 4] = out



    def run(self, pos):
        pass




def main(tile_grid: ChunkGrid, tileset):
    start_tiles = tileset.processing.get("start_tiles")
    for tile_key in start_tiles:
        for rot in 0, 1, 2, 3:
            tile = tile_key, rot
            for pos in tile_grid.tile_locations.get(tile, []):
                run_processing(pos)

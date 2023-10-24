from libs.ChunkGrid import ChunkGrid as _ChunkGrid


class ChunkGrid(_ChunkGrid):
    def __init__(self, ):
        super(ChunkGrid, self).__init__(chunk_size=32, store_tile_locations=False, default_item=lambda: None,
                                        title="ChunkGrid")

    def set_tile_key(self, pos, tile_key):
        self[pos] = tile_key, self[pos][1]

    def get_poss_of_tile(self, tile_key):
        res = []
        for rot in 0, 1, 2, 3:
            tile = tile_key, rot
            for pos in self.tile_locations.get(tile, []):
                res.append(pos)
        return res


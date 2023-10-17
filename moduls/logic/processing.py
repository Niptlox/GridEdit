from libs.ChunkGrid import ChunkGrid
from libs.Tileset import TileSet, TOP, RIGHT, BOTTOM, LEFT


class LogicProcessing:
    def __init__(self, field: ChunkGrid, tileset: TileSet):
        self.field = field
        self.tileset = tileset
        self.runed_pos = set()
        self.function_of_tiles = {eval(self.tileset.properties[tile_key[0]].get("processing", "lambda: None"), globals(), locals())
                                  for tile_key in self.tileset.tiles_dict}
        self.run_field = ChunkGrid(6, default_item=lambda: [0] * 4, store_tile_locations=True,
                                   title="run_field")
        self.runed = set()
        self.start_tiles = self.tileset.processing.get("start_tiles")

    def set_all_lamp_off(self):
        for pos in self.get_poss_of_tile("lamp_on"):
            self.field[pos] = ("lamp_off", self.field[pos][1])

    def find_path_connections(self, start_pos, path_poss=None, run_direction=None, set_signal=None):
        if path_poss is None:
            path_poss = set()
        res = {}
        new_pos = start_pos
        while new_pos is not None:
            pos = new_pos
            around_poss = self.get_output_around_pos(pos, run_direction, exclusion=path_poss)
            first = True
            new_set_signal = None
            for a_pos, a_dir, a_tile in around_poss:
                if set_signal is not None:
                    self.field[pos][a_dir] = set_signal
                a_prop = self.tileset.properties[a_tile[0]]
                if a_prop["path"]:
                    if first:
                        new_set_signal = self.field[pos][a_dir]
                        new_pos = a_pos
                    else:
                        _set_signal = self.field[pos][a_dir] if set_signal is None else set_signal
                        n_res = self.find_path_connections(a_pos, path_poss, run_direction=a_dir, set_signal=_set_signal)
                        res.update(n_res)
                else:
                    res[a_pos] = a_tile
            if set_signal is None:
                set_signal = new_set_signal

        return res

    def get_output_around_pos(self, pos, run_direction=None, exclusion=None):
        if exclusion is None:
            exclusion = set()
        x, y = pos
        tile_key, direction = self.field[pos]
        prop = self.tileset.properties[tile_key]
        around_poss = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
        paths = prop.get("paths")
        if run_direction is not None:
            # откуда пришел сигнал
            p_run_direction = str((run_direction - direction + 2) % 4)
        else:
            p_run_direction = None
        conn_tiles = self.find_path_connections(pos, {pos}, run_direction)
        for i in prop["output"]:
            i_d = (i + direction) % 4
            if i_d == p_run_direction:
                continue
            if paths:
                if i not in paths[p_run_direction]:
                    continue
            a_pos = around_poss[i_d]
            a_tile = self.field[a_pos]
            if a_pos not in exclusion and a_tile and a_tile[0] not in self.start_tiles:
                t_output = self.tileset.properties[a_tile[0]]["input"]
                # print("rec", a_tile, a_pos, i_d, ((i_d + 2 - a_tile[1]) % 4), t_output)
                if ((i_d + 2 - a_tile[1]) % 4) in t_output:
                    exclusion.add(around_poss[i_d])
                    yield (around_poss[i_d], i_d, a_tile)

    def run_tile(self, pos, recursion_run=False, run_direction=None, runed=None):
        if runed is None:
            runed = set()
        self.runed.add(pos)
        runed.add(pos)
        tile_key, direction = self.field[pos]
        print("{", tile_key)
        prop = self.tileset.properties[tile_key]
        if "paths" in prop:
            # откуда пришел сигнал
            p_run_direction = str((run_direction - direction + 2) % 4)
        switch = lambda new_tile_key: self.field.__setitem__(pos, (new_tile_key, direction))
        x, y = pos
        _around_tiles = [self.run_field[(x, y - 1)][BOTTOM], self.run_field[(x + 1, y)][LEFT],
                         self.run_field[(x, y + 1)][TOP], self.run_field[(x - 1, y)][RIGHT]]
        print((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
        print([self.run_field[(x, y - 1)], self.run_field[(x + 1, y)],
               self.run_field[(x, y + 1)], self.run_field[(x - 1, y)]])
        around_tiles = [bool(_around_tiles[(i + direction) % 4]) for i in range(4)]
        input_t = [around_tiles[i] for i in prop["input"]]
        if len(input_t) == 1:
            input_t = input_t[0]
        f = eval(prop["processing"], locals())

        output_t = f(input_t)
        if type(output_t) is not list:
            output_t = [output_t]

        around_poss = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
        out_pos = []

        for out, i in zip(output_t, prop["output"]):
            i_d = (i + direction) % 4
            if "paths" in prop:
                if i not in prop["paths"][p_run_direction]:
                    continue
            out_pos.append((around_poss[i_d], i_d))
            self.run_field[pos][i_d] = out
        print("run tile", pos, tile_key, direction, _around_tiles, around_tiles, input_t, output_t, prop["output"],
              self.runed)
        if recursion_run:
            # pos of (TOP, RIGHT, BOTTOM, LEFT)
            conn_tiles = self.find_path_connections(pos, {pos})
            for c_pos, c_tile in conn_tiles.items():
                self.run_tile(c_pos, recursion_run=True, runed=set(runed))
            # for a_pos, i_d in out_pos:
            #     a_tile = self.field[a_pos]
            #     if a_pos not in runed and a_tile and a_tile[0] not in self.start_tiles:
            #         a_prop = self.tileset.properties[a_tile[0]]
            #         t_output = a_prop["input"]
            #         print("rec", a_tile, a_pos, i_d, ((i_d + 2 - a_tile[1]) % 4), t_output)
            #         if ((i_d + 2 - a_tile[1]) % 4) in t_output:
            #             self.run_tile(a_pos, recursion_run=True, runed=set(runed), run_direction=i_d)
        print("}")

    def clear_run(self):
        self.runed.clear()

    def run(self, pos):
        pass

    def get_poss_of_tile(self, tile_key):
        res = []
        for rot in 0, 1, 2, 3:
            tile = tile_key, rot
            for pos in self.field.tile_locations.get(tile, []):
                res.append(pos)
        return res


class CompilLogic:
    def __init__(self, field, tileset):
        self.field = field
        self.tileset = tileset
        self.scheme = {}
        self.inputs = {}
        self.lamps = {}

    def find_path(self, pos):
        x, y = pos
        tile = self.field[pos]
        tile_key, direction = tile
        around_poss = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
        prop = self.tileset.properties[tile_key]

    def run_lamp(self, pos):
        x, y = pos
        tile = self.field[pos]
        key, direction = tile
        around_poss = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
        get_pos = around_poss[direction]
        self.lamps[pos] = self.find_path(get_pos)

    def run(self):
        poss = get_poss_of_tile(self.field, "lamp_on") + get_poss_of_tile(self.field, "lamp_off")
        for pos in poss:
            self._run(pos)


def get_poss_of_tile(field, tile_key):
    res = []
    for rot in 0, 1, 2, 3:
        tile = tile_key, rot
        for pos in field.tile_locations.get(tile, []):
            res.append(pos)
    return res


def main(tile_grid: ChunkGrid, tileset):
    start_tiles = tileset.processing.get("start_tiles")
    proc = LogicProcessing(tile_grid, tileset)
    proc.set_all_lamp_off()
    for tile_key in start_tiles:
        for pos in proc.get_poss_of_tile(tile_key):
            # print(pos)
            # try:
            proc.run_tile(pos, recursion_run=True)
        # except Exception as exc:
        #     input(f"Error({exc})!!!:")
        #     break
    print(proc.run_field.tile_locations)

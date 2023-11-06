from typing import Iterable

from libs.ChunkGrid import ChunkGrid
from libs.Tileset import TileSet, TOP, RIGHT, BOTTOM, LEFT

DEBUG = False


def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def any_v(arr):
    r = False
    for v in arr:
        r = r or v
    return r


def all_v(arr):
    r = True
    for v in arr:
        r = r and v
    return r


class LogicProcessing:
    def __init__(self, field: ChunkGrid, tileset: TileSet):
        self.field = field
        self.tileset = tileset
        self.runed_pos = set()
        self.function_of_tiles = {
            eval(self.tileset.get_properties(tile_key[0]).get("processing", "lambda: None"), globals(), locals())
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
                a_prop = self.tileset.get_properties(a_tile[0])
                if a_prop["path"]:
                    if first:
                        new_set_signal = self.field[pos][a_dir]
                        new_pos = a_pos
                    else:
                        _set_signal = self.field[pos][a_dir] if set_signal is None else set_signal
                        n_res = self.find_path_connections(a_pos, path_poss, run_direction=a_dir,
                                                           set_signal=_set_signal)
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
        prop = self.tileset.get_properties(tile_key)
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
                t_output = self.tileset.get_properties(a_tile[0])["input"]
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
        prop = self.tileset.get_properties(tile_key)
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
        around_tiles = [(_around_tiles[(i + direction) % 4]) for i in range(4)]
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
            #         a_prop = self.tileset.get_properties(a_tile[0])
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
        self.runed = {}
        self.path2group = {}
        self.path_groups_inout = {}
        self.path_groups_value = {}
        self.next_group_id = 0

    def find_path(self, pos):
        x, y = pos
        tile = self.field[pos]
        tile_key, direction = tile
        around_poss = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
        prop = self.tileset.get_properties(tile_key)

    def run_lamp(self, pos):
        x, y = pos
        tile = self.field[pos]
        key, direction = tile
        around_poss = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
        get_pos = around_poss[direction]
        self.lamps[pos] = self.find_path(get_pos)

    def create_path_group(self, start_pos, start_direction):
        group_id = self.next_group_id
        self.path_groups_inout[group_id] = [set(), set()]
        self.next_group_id += 1
        stack = [(start_pos, start_direction)]
        while stack:
            nextt = stack.pop(-1)
            while nextt:
                pos, run_direction = nextt
                if pos not in self.path2group:
                    self.path2group[pos] = [None] * 4
                nextt = None
                x, y = pos
                tile = self.field[pos]
                tile_key, tile_direction = tile
                prop = self.tileset.get_properties(tile_key)
                around_poss = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
                prop_output = prop["output"]
                if prop.get("paths"):
                    trun_direction2 = (run_direction - tile_direction + 2) % 4
                    prop_output = prop["paths"][str(trun_direction2)] + [trun_direction2]
                # напрвлениЯ в сис корд тайла
                for out_d in prop_output:
                    # напрвление в сис корд поля
                    out_dd = (out_d + tile_direction) % 4
                    self.path2group[pos][out_dd] = group_id
                    out_pos = around_poss[out_dd]
                    out_tile = self.field[out_pos]
                    if out_tile:
                        # напрвление в сис корд поля
                        _out_inp_d = (out_dd + 2) % 4
                        if out_pos in self.path2group and self.path2group[out_pos][_out_inp_d] is not None:
                            continue
                        # напрвление в сис корд тайла
                        out_inp_dd = (_out_inp_d - out_tile[1]) % 4
                        out_prop = self.tileset.get_properties(out_tile[0])
                        if out_prop.get("path"):
                            if out_inp_dd in out_prop["input"]:
                                if nextt is None:
                                    nextt = out_pos, out_dd
                                else:
                                    stack.append((out_pos, out_dd))
                        else:
                            if out_inp_dd in out_prop["output"]:
                                # таил отдающий значение в группу
                                self.path_groups_inout[group_id][0].add((out_pos, _out_inp_d))
                            elif out_inp_dd in out_prop["input"]:
                                # таил забирающий значение из группы
                                self.path_groups_inout[group_id][1].add((out_pos, _out_inp_d))

        return group_id

    def get_path_group(self, pos, direction):
        if pos not in self.path2group or self.path2group[pos][direction] is None:
            return self.create_path_group(pos, direction)
        return self.path2group[pos][direction]

    def get_path_value(self, pos, direction):
        group_id = self.get_path_group(pos, direction)
        dprint("pd", pos, direction, self.path2group)
        dprint("path", group_id, self.path_groups_inout[group_id])
        if group_id not in self.path_groups_value:
            all_v = [self.run_tile(pos)[direction] for pos, direction in self.path_groups_inout[group_id][0]]
            self.path_groups_value[group_id] = any_v(all_v)
        return self.path_groups_value[group_id]

    def run_tile(self, pos, last_pos=None):
        global all_v, any_v
        x, y = pos
        tile = self.field[pos]
        dprint("{run", tile, pos, )
        if tile is None:
            return [False] * 4
        elif pos in self.runed:
            return self.runed[pos]
        tile_key, direction = tile
        prop = self.tileset.get_properties(tile_key)
        around_poss = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
        # Get inputs value
        inputs_v = []
        if prop.get("path"):
            _output_v = [self.get_path_value(pos, (i + direction) % 4) for i in prop["output"]]
        else:
            for input_d in prop["input"]:
                i_dd = (input_d + direction) % 4
                i_dd2 = (i_dd + 2) % 4
                input_pos = around_poss[i_dd]
                input_tile = self.field[input_pos]
                if input_tile is None or input_pos == last_pos:
                    val = False
                else:
                    input_prop = self.tileset.get_properties(input_tile[0])
                    # print(i_dd, input_tile, "prop", (i_dd2 - input_tile[1]) % 4, input_prop["output"])
                    if (i_dd2 - input_tile[1]) % 4 in input_prop["output"]:
                        val = self.run_tile(input_pos, pos)[i_dd2]
                    else:
                        val = False
                # print("i_dd", i_dd, input_pos, input_tile, "val", val)
                inputs_v.append(val)
            if len(prop["input"]) == 1:
                inputs_v = inputs_v[0]
            # Run function
            spec_vars = {
                "self": self,
                "get_input": self.field.get_function_input,
                "set_result": self.field.set_function_result,
                "switch": lambda new_tile_key: self.field.__setitem__(pos, (new_tile_key, direction)),
                "any_v": any_v,
                "all_v": all_v
            }
            # run tile processing
            if prop.get("is_function", False):
                _output_v = prop["field"].run_function(prop, inputs_v, self.tileset)
            else:
                f = eval(prop["processing"], spec_vars)
                _output_v = f(inputs_v)

                print(pos, tile_key, inputs_v, _output_v)
        output_t = [False] * 4
        if prop["output"]:
            if len(prop["output"]) == 1:
                output_t[(prop["output"][0] + direction) % 4] = _output_v
            else:
                if isinstance(_output_v, Iterable):
                    for out_d, out_v in zip(prop["output"], _output_v):
                        output_t[(out_d + direction) % 4] = out_v
                else:
                    output_t = [None] * 4
        dprint("res", tile, pos, inputs_v, output_t, "}")
        self.runed[pos] = output_t
        return output_t

    def run(self):
        poss = sum([get_poss_of_tile(self.field, key) for key in self.tileset.processing.get("fin_tiles", [])],
                   start=[])
        for pos in poss:
            print(f"===================== run lamp (pos={pos}) =========================")
            self.run_tile(pos)


def get_poss_of_tile(field, tile_key):
    res = []
    for rot in 0, 1, 2, 3:
        tile = tile_key, rot
        for pos in field.tile_locations.get(tile, []):
            res.append(pos)
    return res


def _main(tile_grid: ChunkGrid, tileset):
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


def main(tile_grid: ChunkGrid, tileset, log=print):
    comp = CompilLogic(tile_grid, tileset)
    try:
        comp.run()
    except RecursionError as excRec:
        log(f"ErrorRecursion!!! {excRec}")
    except Exception as exc:
        log(f"Error!!! {exc}")
    print("FIN")

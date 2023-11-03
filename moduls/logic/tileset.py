from libs.Tileset import TileSet as _TileSet, pg, load_images

# Red Orange Amber Yellow Lime Green Emerald Teal Cyan LightBlue Blue Indigo Violet Purple Fuchsia Pink Rose WarmGray
FUNCTION_COLORS = ("#DC2626", "#EA580C", "#D97706", "#CA8A04", "#65A30D", "#16A34A", "#059669", "#0D9488",
                   "#0891B2", "#0284C7", "#2563EB", "#4F46E5", "#7C3AED", "#9333EA", "#C026D3", "#DB2777",
                   "#E11D48", "#57534E")
# Red  Yellow  Green  Teal  LightBlue Blue Indigo Violet  Pink  WarmGray
FUNCTION_COLORS = ("#DC2626", "#FEF08A", "#16A34A", "#0D9488",
                   "#0284C7", "#2563EB", "#4F46E5", "#7C3AED", "#DB2777",
                   "#57534E")
FUNCTION_COLORS_S = load_images("moduls/logic", {"path": "function_colors.png", "tile_side": 4})


class TileSet(_TileSet):
    def __init__(self):
        super().__init__(autorotate_tile=True)
        self.functions = {}
        self.function_last_id = 0

    def get_properties(self, tile_key):
        if tile_key in self.functions:
            return self.functions[tile_key]
        return super().get_properties(tile_key)

    def new_function(self, name, field):
        if self.function_last_id >= len(FUNCTION_COLORS_S):
            return list(self.functions.values())[-1]
        fid = f"func_{name}_{self.function_last_id}"
        _input = self.get_properties("function")["input"]
        _output = self.get_properties("function")["output"]
        f = {"name": name, "field": field, "label": f"Func: {name}",
             "input": _input, "output": _output, "input_tiles": [], "output_tiles": [],
             "color_num": self.function_last_id, "is_function": True, "fid": fid}
        self.add_function_data(f)
        return f

    def add_function_data(self, func):
        color_s = FUNCTION_COLORS_S[func["color_num"]]
        imgs = [self.get_tile_image(("function", i)).copy() for i in range(4)]
        [img.blit(color_s, (6, 6)) for img in imgs]
        # [pg.draw.rect(img, f["color"], (6, 6, 4, 4)) for img in imgs]
        fid = func["fid"]
        self.function_last_id += 1
        self.functions[fid] = func
        self.add_tile(fid, imgs, func)
        self.groups[-1]["tiles"].append(fid)

    def run_function(self, fid):
        if fid not in self.functions:
            assert Exception(f"Function '{fid}' is not expected")

    def __setstate__(self, state):
        super().__setstate__(state)
        self.functions = {}
        self.function_last_id = state["function_last_id"]
        for f in state["functions"].values():
            self.add_function_data(f)

    def set_data(self, data):
        super().set_data(data)

    def get_data(self):
        d = super().get_data()
        d["functions"] = self.functions
        d["function_last_id"] = self.functions
        return d

TileSet_ = TileSet
{
        "source_type": "tileset",
        "preview_": {
                "load_type": "grid",
                "path": "logicGridElemnets8x.png",
                "tile_side": 8
        },
        "tiles": {
                "load_type": "grid",
                "path": "logicGridElemnets16x.png",
                "tile_side": 16

        },
        "properties": [
                ["path_+", {"input": [0,1,2,3], "output": [0,1,2,3], "processing": "lambda x: x"}],
                ["path_I"],
                ["diod"],
                ["lamp_on"],
                ["lamp_off"],
                ["not"],
                ["xor"],
                ["and_2_u"],
                ["and_2_r"],
                ["and_3_u"],
                ["or_2_u"],
                ["or_2_r"],
                ["or_3_u"]
        ],
        "groups": [
                {"title": "Paths", "tiles": ["path_+", "path_I"]},
                {"title": "Outputs", "tiles": ["lamp_off"]},
                {"title": "Operands", "tiles": ["not", "xor", "and_2_u", "and_2_r", "and_3_u", "or_2_u", "or_2_r", "or_3_u"]}

        ],
        "processing": {"path": "processing.py", "type": "py", "run": "main"}
}
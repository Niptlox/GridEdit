{
  "source_type": "tileset",
  "file_extension": ".lg",
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

    [
      "path_+",
      {
        "label": "path +",
        "input": [ 0, 1, 2, 3 ],
        "output": [ 0, 1, 2, 3 ],
        "processing": "lambda x0123: [any_v(x0123)] * 4",
        "path": true
      }
    ],
    [
      "path_I",
      {
        "label": "path |",
        "input": [ 0, 2 ],
        "output": [ 0, 2 ],
        "processing": "lambda x02: [any_v(x02)]*2",
        "path": true
      }
    ],
    [
      "bridge_+",
      {
        "label": "bridge +",
        "input": [ 0, 1, 2, 3 ],
        "output": [ 0, 1, 2, 3 ],
        "processing": "lambda x0123: [x0123[0] or x0123[2], x0123[1] or x0123[3], x0123[0] or x0123[2], x0123[1] or x0123[3]]",
        "paths": {"0": [2], "2": [0], "1": [3], "3": [1]},
        "path": true
      }
    ],
    [
      "path_L",
      {
        "label": "path L",
        "input": [ 0, 1],
        "output": [ 0, 1],
        "processing": "lambda x0123: [any_v(x0123)] * 2",
        "path": true
      }
    ],
    [
      "diod",
      {
        "label": "diod",
        "input": [ 2 ],
        "output": [ 0 ],
        "processing": "lambda x2: x2"
      }
    ],
    [
      "lamp_on",
      {
        "label": "lamp on",
        "input": [ 0],
        "output": [ ],
        "processing": "lambda x0123: (switch('lamp_on') if x0123 else switch('lamp_off'))"
      }
    ],

    [
      "lamp_off",
      {
        "label": "lamp off",
        "input": [ 0],
        "output": [ ],
        "processing": "lambda x0123: (switch('lamp_on') if x0123 else switch('lamp_off'))"
      }
    ],
    [
      "not",
      {
        "label": "not",
        "input": [ 2 ],
        "output": [ 0 ],
        "processing": "lambda x2: not x2"
      }
    ],
    [
      "xor",
      {
        "label": "xor",
        "input": [ 1, 2 ],
        "output": [ 0 ],
        "processing": "lambda x12: 0 if all_v(x12) else any_v(x12)"
      }
    ],
    [
      "and_2_u",
      {
        "label": "and",
        "input": [ 1, 2 ],
        "output": [ 0 ],
        "processing": "lambda x12: all_v(x12)"
      }
    ],
    [
      "and_2_r",
      {
        "label": "and",
        "input": [ 0, 2 ],
        "output": [ 1 ],
        "processing": "lambda x02: all_v(x02)"
      }
    ],
    [
      "and_3_u",
      {
        "label": "and",
        "input": [ 1, 2, 3 ],
        "output": [ 0 ],
        "processing": "lambda x123: all_v(x123)"
      }
    ],
    [
      "or_2_u",
      {
        "label": "or",
        "input": [ 1, 2 ],
        "output": [ 0 ],
        "processing": "lambda x12: any_v(x12)"
      }
    ],
    [
      "or_2_r",
      {
        "label": "or",
        "input": [ 0, 2 ],
        "output": [ 1 ],
        "processing": "lambda x02: any_v(x02)"
      }
    ],
    [
      "or_3_u",
      {
        "label": "or",
        "input": [ 1, 2, 3 ],
        "output": [ 0 ],
        "processing": "lambda x123: any_v(x123)"
      }
    ],
    [
      "input_on",
      {
        "label": "input 1",
        "on_click": "switch('input_off')",
        "input": [],
        "output": [ 0 ],
        "processing": "lambda x: 1"
      }
    ],
    [
      "input_off",
      {
        "label": "input 0",
        "on_click": "switch('input_on')",
        "input": [],
        "output": [ 0 ],
        "processing": "lambda x: 0"
      }
    ],
    [
      "function_in_0",
      {
        "label": "function input top",
        "input": [],
        "output": [ 2 ],
        "processing": "lambda x: get_input(0)"

      }
    ],
    [
      "function_in_3",
      {
        "label": "function input left",
        "input": [],
        "output": [ 2 ],
        "processing": "lambda x: get_input(3)"
      }
    ],
    [
      "function_out_2",
      {
        "label": "function input bottom",
        "input": [2],
        "output": [],
        "processing": "lambda x: set_result(2, x)"

      }
    ],
    [
      "function_out_1",
      {
        "label": "function output right",
        "input": [2],
        "output": [],
        "processing": "lambda x: set_result(1, x)"
      }
    ],
    [
      "function",
      {
        "label": "function",
        "input": [0, 3],
        "output": [1, 2],
        "processing": "lambda x: run_function(prop, x)"
      }
    ],
    [
      "packer3to1",
      {
        "label": "packer 3 to 1",
        "input": [0, 3, 2],
        "output": [1],
        "processing": "lambda x023: x023"
      }
    ],
    [
      "unpacker1to3",
      {
        "label": "unpacker 1 to 3",
        "input": [3],
        "output": [0, 1, 2],
        "processing": "lambda x: x"
      }
    ]


  ],
  "groups": [
    {
      "title": "Paths",
      "tiles": [ "path_+", "path_I", "bridge_+", "path_L"]
    },
    {
      "title": "Inputs",
      "tiles": ["input_on", "input_off"]
    },

    {
      "title": "Outputs",
      "tiles": [ "lamp_off" ]
    },
    {
      "title": "Operands",
      "tiles": ["diod", "not", "xor", "and_2_u", "and_2_r", "and_3_u", "or_2_u", "or_2_r", "or_3_u" ]
    },
    {
      "title": "Function operators",
      "tiles": ["function_in_0", "function_in_3", "function_out_1", "function_out_2"]
    },
    {
      "title": "Data bus",
      "tiles": ["packer3to1", "unpacker1to3"]
    },
    {
      "title": "Functions",
      "tiles": []
    }

  ],
  "processing": {
    "path": "processing.py",
    "type": "py",
    "run": "main",
    "input": {"1":  "input_on", "0":  "input_off"},
    "output": {"1":  "lamp_on", "0":  "lamp_off"},
    "start_tiles": ["input_on", "input_off"],
    "fin_tiles": ["lamp_on", "lamp_off", "function_out_1", "function_out_2"]
  }
}
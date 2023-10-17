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

    [
      "path_+",
      {
        "input": [ 0, 1, 2, 3 ],
        "output": [ 0, 1, 2, 3 ],
        "path": true
      }
    ],
    [
      "path_I",
      {
        "input": [ 0, 2 ],
        "output": [ 0, 2 ],
        "path": true
      }
    ],
    [
      "bridge_+",
      {
        "input": [ 0, 1, 2, 3 ],
        "output": [ 0, 1, 2, 3 ],
        "path": true,
        "paths": {"0": [2], "2": [0], "1": [3], "3": [1]}
      }
    ],
    [
      "path_L",
      {
        "input": [ 0, 1],
        "output": [ 0, 1],
        "path": true
      }
    ],
    [
      "diod",
      {
        "input": [ 2 ],
        "output": [ 0 ],
        "processing": "lambda x2: x2"
      }
    ],
    [
      "lamp_on",
      {
        "input": [ 0],
        "output": [ 0],
        "processing": "lambda x0123: (switch('lamp_on') if x0123 else switch('lamp_off'))"
      }
    ],

    [
      "lamp_off",
      {
        "input": [ 0],
        "output": [ 0],
        "processing": "lambda x0123: (switch('lamp_on') if x0123 else switch('lamp_off'))"
      }
    ],
    [
      "not",
      {
        "input": [ 2 ],
        "output": [ 0 ],
        "processing": "lambda x2: not x2"
      }
    ],
    [
      "xor",
      {
        "input": [ 1, 2 ],
        "output": [ 0 ],
        "processing": "lambda x12: 0 if all(x12) else any(x12)"
      }
    ],
    [
      "and_2_u",
      {
        "input": [ 1, 2 ],
        "output": [ 0 ],
        "processing": "lambda x12: all(x12)"
      }
    ],
    [
      "and_2_r",
      {
        "input": [ 0, 2 ],
        "output": [ 1 ],
        "processing": "lambda x02: all(x02)"
      }
    ],
    [
      "and_3_u",
      {
        "input": [ 1, 2, 3 ],
        "output": [ 0 ],
        "processing": "lambda x123: all(x123)"
      }
    ],
    [
      "or_2_u",
      {
        "input": [ 1, 2 ],
        "output": [ 0 ],
        "processing": "lambda x12: any(x12)"
      }
    ],
    [
      "or_2_r",
      {
        "input": [ 0, 2 ],
        "output": [ 1 ],
        "processing": "lambda x02: any(x02)"
      }
    ],
    [
      "or_3_u",
      {
        "input": [ 1, 2, 3 ],
        "output": [ 0 ],
        "processing": "lambda x123: any(x123)"
      }
    ],
    [
      "input_on",
      {
        "on_click": "switch('input_off')",
        "input": [],
        "output": [ 0 ],
        "processing": "lambda x: 1"
      }
    ],
    [
      "input_off",
      {
        "on_click": "switch('input_on')",
        "input": [],
        "output": [ 0 ],
        "processing": "lambda x: 0"
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
      "tiles": [ "not", "xor", "and_2_u", "and_2_r", "and_3_u", "or_2_u", "or_2_r", "or_3_u" ]
    }

  ],
  "processing": {
    "path": "processing.py",
    "type": "py",
    "run": "main",
    "start_tiles": ["input_on", "input_off"]
  }
}
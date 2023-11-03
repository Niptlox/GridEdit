import pickle
import logging
from collections.abc import Iterable
from collections import defaultdict

from libs.UClass.UClass import UClass

logger = logging.getLogger("ChunkGrid")
logger.setLevel(logging.DEBUG)


def set_logger(_logger):
    global logger
    logger = _logger


class ChunkGrid(UClass):
    def __init__(self, chunk_size=32, store_tile_locations=False, default_item=lambda: None, title="ChunkGrid"):
        self.chunk_size = chunk_size
        self.chunks_field = {}
        self.store_tile_locations = store_tile_locations
        self.tile_locations = defaultdict(list)
        self.default_item = default_item
        self.title = title

    def __getitem__(self, item):
        if isinstance(item, Iterable):
            item = list(item)
            if len(item) == 2:
                return self.chunk(self.xy2chunk_pos(item))[item[1] % self.chunk_size][item[0] % self.chunk_size]
        logger.error(f"Error Grid.get_item({item})")

    def __setitem__(self, key, value):
        print(f"__set({self.title})__", key, value)
        if isinstance(key, Iterable):
            item = pos = tuple(key)
            if self.store_tile_locations:
                last_tile = self[pos]
                if last_tile is not None:
                    self.tile_locations[last_tile].remove(pos)
                if value is not None:
                    self.tile_locations[value].append(pos)
            if len(item) == 2:
                self.chunk(self.xy2chunk_pos(item))[item[1] % self.chunk_size][item[0] % self.chunk_size] = value
                return
        logger.error(f"Error Grid.set_item({key}, {value})")

    def chunk(self, chunk_pos, default=True):
        chunk = self.chunks_field.get(chunk_pos)
        if chunk:
            return chunk
        if default:
            chunk = self.pass_chunk()
            self.chunks_field[chunk_pos] = chunk
            return chunk
        logger.error(f"Error Grid.chunk({chunk_pos}, default={default})")
        return None

    def copy(self):
        obj = self.__class__(self.chunk_size, self.store_tile_locations)
        obj.chunks_field = dict(self.chunks_field)
        obj.tile_locations = type(self.tile_locations)(self.tile_locations)
        return obj

    def pass_chunk(self):
        return [[self.default_item() for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]

    def xy2chunk_pos(self, xy):
        return xy[0] // self.chunk_size, xy[1] // self.chunk_size

    def clear(self):
        self.chunks_field = {}
        self.tile_locations = defaultdict(list)

    def set_data(self, data):
        for key, val in data.items():
            self.__dict__[key] = val

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __getstate__(self):
        state = self.__dict__.copy()
        if "default_item" in state:
            del state['default_item']
        return state


def save(obj, f):
    pickle.dump(obj, file=f)


def load(f):
    return pickle.load(f)

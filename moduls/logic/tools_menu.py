from libs.ColorSchema import ColorSchema
from libs.ToolsMenu import ToolsMenu as _ToolsMenu
from .tileset import TileSet


class ToolsMenu(_ToolsMenu):
    def __init__(self, app, rect, color_schema=ColorSchema, tileset: TileSet = None, on_tool_selected=None):
        super(ToolsMenu, self).__init__(app, rect, color_schema, tileset, on_tool_selected)
        self.edit_function = None


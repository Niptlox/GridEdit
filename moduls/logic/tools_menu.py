from libs.ColorSchema import ColorSchema, open_ui_image
from libs.PgUI.Button import Button
from libs.ToolsMenu import ToolsMenu as _ToolsMenu
from .tileset import TileSet


class ToolsMenu(_ToolsMenu):
    def __init__(self, app, rect, color_schema=ColorSchema, tileset: TileSet = None, on_tool_selected=None):
        super(ToolsMenu, self).__init__(app, rect, color_schema, tileset, on_tool_selected)
        self.edit_function = None
        self.additional_tools["magic_line"] = Button(self.switch_magic_line, (0, 0, 25, 25),
                                                     open_ui_image("magic_line.png"))
        self.update_display()
        self.magic_line_mode = True

    def switch_magic_line(self, btn: Button):

        if self.magic_line_mode:
            btn.imgUpB.set_colorkey("white")
            btn.imgInB.set_colorkey("white")
        else:
            btn.imgUpB.set_colorkey(None)
            btn.imgInB.set_colorkey(None)
        self.magic_line_mode = not self.magic_line_mode
        self.update_display()

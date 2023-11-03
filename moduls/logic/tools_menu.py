from libs.ColorSchema import ColorSchema, open_ui_image
from libs.PgUI.Button import Button
from libs.ToolsMenu import ToolsMenu as _ToolsMenu, pg
from .chunk_grid import ChunkGrid
from .tileset import TileSet


class ToolsMenu(_ToolsMenu):
    def __init__(self, app, rect, color_schema=ColorSchema, tileset: TileSet = None, on_tool_selected=None):
        super(ToolsMenu, self).__init__(app, rect, color_schema, tileset, on_tool_selected)
        self.additional_tools["magic_line"] = Button(self.switch_magic_line, (0, 0, 25, 25),
                                                     open_ui_image("magic_line.png"))
        self.additional_tools["add_function"] = Button(self.add_function, (0, 0, 25, 25),
                                                     open_ui_image("add_function.png"))
        self.update_display()
        self.magic_line_mode = True
        self.function_index = 1

    def switch_magic_line(self, btn: Button):
        if self.magic_line_mode:
            btn.imgUpB.set_colorkey("white")
            btn.imgInB.set_colorkey("white")
        else:
            btn.imgUpB.set_colorkey(None)
            btn.imgInB.set_colorkey(None)
        self.magic_line_mode = not self.magic_line_mode
        self.update_display()

    def add_function(self, btn):
        f = self.tileset.new_function(f"f{self.tileset.function_last_id}", ChunkGrid())
        self.app.grid.open_function(f)

    def pg_event(self, event):
        kmod = pg.key.get_mods()
        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT and self.rect.collidepoint(event.pos) and kmod & pg.KMOD_LCTRL:
            tile = self.mouse_pos2cell(event.pos)
            prop = self.tileset.get_properties(tile[0])
            if prop.get("is_function"):
                self.app.grid.open_function(prop)
        else:
            super().pg_event(event)

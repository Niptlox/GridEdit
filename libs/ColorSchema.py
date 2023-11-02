import os.path
import sys

import pygame as pg

pg.font.init()


class ColorSchema:
    grid_bg_color = "#64748B"
    grid_line_color = "#334155"
    tools_menu_font_1 = pg.font.SysFont("Roboto", 25)
    tools_menu_font_labels = pg.font.SysFont("Roboto", 25)

    additional_tools_bg_color = "#6B7280"
    additional_tools_height = 30
    tools_menu_font_1_color = "#FFFFFF"
    toolsmenu_bg_color = "#4B5563"
    toolsmenu_border_color = "#000000"
    toolsmenu_active_cell_color = "#FFFFFF"
    toolsmenu_vscroll_step = 25
    highlighting_color = "#2e70ff"


def open_ui_image(name):
    return pg.image.load(os.path.join("src/ui", name))

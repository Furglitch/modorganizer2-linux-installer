#!/usr/bin/env python3

import re
import shutil
import subprocess
from pathlib import Path

from loguru import logger
from util.internal_file import internal_file

GTK_CSS = Path("~/.config/gtk-3.0/colors.css").expanduser()
OUTPUT_SUBDIR = "GTK"
OUTPUT_FILENAME = "gtk_colors.qss"


def _template_path() -> Path:
    repo_template = Path(__file__).resolve().parents[4] / "configs" / "template.qss"
    if repo_template.exists():
        return repo_template
    return internal_file("cfg", "template.qss")


def parse_css_color(value: str) -> str:
    """Convert CSS hex (#RRGGBB) to 'R,G,B' string."""
    if value.startswith("#") and len(value) == 7:
        r = int(value[1:3], 16)
        g = int(value[3:5], 16)
        b = int(value[5:7], 16)
        return f"{r},{g},{b}"
    return "255,255,255"


def lighten_rgb(rgb_str: str, factor: float = 0.2) -> str:
    r, g, b = map(int, rgb_str.split(","))
    r = min(int(r + (255 - r) * factor), 255)
    g = min(int(g + (255 - g) * factor), 255)
    b = min(int(b + (255 - b) * factor), 255)
    return f"{r},{g},{b}"


def _copy_font_file(font_name: str, output_dir: Path) -> None:
    try:
        matched_family = subprocess.check_output(
            ["fc-match", "-f", "%{family[0]}\n", font_name], text=True
        ).strip()
        if matched_family.casefold() != font_name.casefold():
            logger.debug(
                f"Font '{font_name}' resolved to '{matched_family}'; skipping font copy."
            )
            return
        font_file = subprocess.check_output(
            ["fc-match", "-f", "%{file}\n", font_name], text=True
        ).strip()
    except subprocess.CalledProcessError:
        logger.warning(f"Could not detect font file for '{font_name}'. Copy manually.")
        return

    font_path = Path(font_file)
    if font_path.is_file():
        dest_path = output_dir / font_path.name
        shutil.copy2(font_path, dest_path)
        logger.debug(f"Copied font file: {font_path.name}")
    else:
        logger.debug(f"Font file for '{font_name}' not found. Please copy it manually.")


def generate_gtk_theme(
    output_dir: Path, template_path: Path | None = None
) -> str | None:
    if not GTK_CSS.is_file():
        logger.debug(
            f"GTK3 colors.css not found at {GTK_CSS}; skipping GTK theme generation."
        )
        return None

    with open(GTK_CSS, "r", encoding="utf-8") as file:
        data = file.read()

    matches = re.findall(r"@define-color\s+([\w_]+)\s+(#[0-9a-fA-F]{6});", data)
    if not matches:
        logger.debug(f"No colors found in {GTK_CSS}; skipping GTK theme generation.")
        return None

    colors = {name: parse_css_color(value) for name, value in matches}

    mapped_colors = {
        "WINDOW_BG": colors.get("theme_bg_color_breeze"),
        "WINDOW_FG": colors.get("theme_fg_color_breeze"),
        "VIEW_BG": colors.get("theme_base_color_breeze"),
        "VIEW_FG": colors.get("theme_text_color_breeze"),
        "ALTERNATE_ROW_COLOR": lighten_rgb(colors.get("theme_base_color_breeze"), 0.05),
        "BORDER_COLOR": lighten_rgb(colors.get("borders_breeze"), 0.2),
        "SELECTION_BG": colors.get("theme_selected_bg_color_breeze"),
        "SELECTION_FG": colors.get("theme_selected_fg_color_breeze"),
        "BUTTON_BG": colors.get("theme_button_background_normal_breeze"),
        "BUTTON_FG": colors.get("theme_button_foreground_normal_breeze"),
        "BUTTON_HOVER": lighten_rgb(
            colors.get("theme_button_background_normal_breeze"), 0.1
        ),
        "BUTTON_FOCUS": lighten_rgb(
            colors.get("theme_button_decoration_focus_breeze"), 0.2
        ),
        "TOOLTIP_BG": colors.get("tooltip_background_breeze"),
        "TOOLTIP_FG": colors.get("tooltip_text_breeze"),
        "SCROLLBAR_BG": colors.get("theme_base_color_breeze"),
        "SCROLLBAR_HANDLE": lighten_rgb(colors.get("theme_base_color_breeze"), 0.15),
        "SCROLLBAR_HANDLE_HOVER": lighten_rgb(
            colors.get("theme_base_color_breeze"), 0.3
        ),
    }

    font_name = "Arial"
    font_match = re.search(r"font-family:\s*['\"]?([^;'\"\n]+)['\"]?;", data)
    if font_match:
        font_name = font_match.group(1)

    mapped_colors["FONT_FAMILY"] = font_name

    stylesheet_dir = output_dir / OUTPUT_SUBDIR
    stylesheet_dir.mkdir(parents=True, exist_ok=True)
    stylesheet_path = stylesheet_dir / OUTPUT_FILENAME

    stylesheet = (template_path or _template_path()).read_text(encoding="utf-8")
    for key, value in mapped_colors.items():
        if key == "FONT_FAMILY":
            stylesheet = stylesheet.replace(f"${{{key}}}", f'"{value}"')
        else:
            stylesheet = stylesheet.replace(f"${{{key}}}", f"rgb({value})")

    stylesheet_path.write_text(stylesheet, encoding="utf-8")
    _copy_font_file(font_name, stylesheet_dir)
    logger.info(f"Generated GTK QSS: {stylesheet_path}")
    return f"{OUTPUT_SUBDIR}/{OUTPUT_FILENAME}"


if __name__ == "__main__":
    generate_gtk_theme(Path("."))

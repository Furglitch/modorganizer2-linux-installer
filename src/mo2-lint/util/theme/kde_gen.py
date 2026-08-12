#!/usr/bin/env python3

import configparser
import shutil
import subprocess
from pathlib import Path

from loguru import logger
from util.internal_file import internal_file

KDE_GLOBALS = Path("~/.config/kdeglobals").expanduser()
OUTPUT_SUBDIR = "KDE"
OUTPUT_FILENAME = "kde_colors.qss"
COLOR_SECTIONS = (
    "Colors:Window",
    "Colors:View",
    "Colors:Selection",
    "Colors:Button",
    "Colors:Tooltip",
)


def _template_path() -> Path:
    repo_template = Path(__file__).resolve().parents[4] / "configs" / "template.qss"
    if repo_template.exists():
        return repo_template
    return internal_file("cfg", "template.qss")


def _get_rgb(
    config: configparser.ConfigParser,
    section: str,
    key: str,
    fallback: str = "255,255,255",
) -> str:
    try:
        return config.get(section, key)
    except configparser.Error:
        return fallback


def lighten_rgb(rgb_str: str, factor: float = 0.2) -> str:
    r, g, b = map(int, rgb_str.split(","))
    r = min(int(r + (255 - r) * factor), 255)
    g = min(int(g + (255 - g) * factor), 255)
    b = min(int(b + (255 - b) * factor), 255)
    return f"{r},{g},{b}"


def _copy_font_file(font_name: str, output_dir: Path) -> None:
    try:
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


def generate_kde_theme(
    output_dir: Path, template_path: Path | None = None
) -> str | None:
    if not KDE_GLOBALS.is_file():
        logger.debug(
            f"KDE globals not found at {KDE_GLOBALS}; skipping KDE theme generation."
        )
        return None

    config = configparser.ConfigParser()
    config.read(KDE_GLOBALS)

    if not any(config.has_section(section) for section in COLOR_SECTIONS):
        logger.debug(
            f"KDE globals at {KDE_GLOBALS} do not contain color sections; skipping KDE theme generation."
        )
        return None

    try:
        font_setting = config.get("General", "font")
        font_name = font_setting.split(",")[0]
    except (configparser.Error, ValueError):
        font_name = "Arial"

    colors = {
        "WINDOW_BG": _get_rgb(config, "Colors:Window", "BackgroundNormal"),
        "WINDOW_FG": _get_rgb(config, "Colors:Window", "ForegroundNormal"),
        "VIEW_BG": _get_rgb(config, "Colors:View", "BackgroundNormal"),
        "VIEW_FG": _get_rgb(config, "Colors:View", "ForegroundNormal"),
        "ALTERNATE_ROW_COLOR": _get_rgb(config, "Colors:View", "BackgroundAlternate"),
        "BORDER_COLOR": _get_rgb(config, "Colors:Window", "DecorationFocus"),
        "SELECTION_BG": _get_rgb(config, "Colors:Selection", "BackgroundNormal"),
        "SELECTION_FG": _get_rgb(config, "Colors:Selection", "ForegroundNormal"),
        "BUTTON_BG": _get_rgb(config, "Colors:Button", "BackgroundNormal"),
        "BUTTON_FG": _get_rgb(config, "Colors:Button", "ForegroundNormal"),
        "BUTTON_HOVER": _get_rgb(config, "Colors:Button", "DecorationHover"),
        "BUTTON_FOCUS": _get_rgb(config, "Colors:Button", "DecorationFocus"),
        "TOOLTIP_BG": _get_rgb(config, "Colors:Tooltip", "BackgroundNormal"),
        "TOOLTIP_FG": _get_rgb(config, "Colors:Tooltip", "ForegroundNormal"),
        "SCROLLBAR_BG": _get_rgb(config, "Colors:Window", "BackgroundNormal"),
        "SCROLLBAR_HANDLE": _get_rgb(config, "Colors:View", "BackgroundNormal"),
        "SCROLLBAR_HANDLE_HOVER": _get_rgb(
            config, "Colors:Selection", "BackgroundNormal"
        ),
        "FONT_FAMILY": font_name,
    }
    colors["SCROLLBAR_HANDLE"] = lighten_rgb(colors["SCROLLBAR_BG"], 0.15)
    colors["SCROLLBAR_HANDLE_HOVER"] = lighten_rgb(colors["SCROLLBAR_BG"], 0.3)

    stylesheet_dir = output_dir / OUTPUT_SUBDIR
    stylesheet_dir.mkdir(parents=True, exist_ok=True)
    stylesheet_path = stylesheet_dir / OUTPUT_FILENAME

    stylesheet = (template_path or _template_path()).read_text(encoding="utf-8")
    for key, value in colors.items():
        if key == "FONT_FAMILY":
            stylesheet = stylesheet.replace(f"${{{key}}}", f'"{value}"')
        else:
            stylesheet = stylesheet.replace(f"${{{key}}}", f"rgb({value})")

    stylesheet_path.write_text(stylesheet, encoding="utf-8")
    _copy_font_file(font_name, stylesheet_dir)
    logger.info(f"Generated KDE stylesheet: {stylesheet_path}")
    return f"{OUTPUT_SUBDIR}/{OUTPUT_FILENAME}"


if __name__ == "__main__":
    generate_kde_theme(Path("."))

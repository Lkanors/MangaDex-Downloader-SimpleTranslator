from __future__ import annotations

import os
import platform
import re
import warnings
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

from PIL import Image, ImageDraw, ImageFont

try:
    from fontTools.ttLib import TTFont as _TTFont

    _HAS_FONTTOOLS = True
except ImportError:
    _HAS_FONTTOOLS = False
    warnings.warn(
        "fontTools is not installed; falling back to filename-based script "
        "detection, which is less reliable for languages without a bundled "
        "font. Run `pip install fonttools` for accurate glyph coverage.",
        stacklevel=2,
    )

_BUNDLED_FONT_DIRS = (
    Path(__file__).with_name("Fonts"),
    Path(__file__).with_name("font_cache"),
)

_FONT_EXTENSIONS = (".ttf", ".otf", ".ttc", ".otc")


def _system_font_dirs() -> list[Path]:
    system = platform.system()
    dirs: list[Path] = []

    if system == "Windows":
        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        dirs.append(windir / "Fonts")
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            dirs.append(Path(local_appdata) / "Microsoft" / "Windows" / "Fonts")
    elif system == "Darwin":
        dirs.extend(
            [
                Path("/System/Library/Fonts"),
                Path("/System/Library/Fonts/Supplemental"),
                Path("/Library/Fonts"),
                Path.home() / "Library" / "Fonts",
            ]
        )
    else:  # Linux and other unix-likes
        dirs.extend(
            [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".fonts",
                Path.home() / ".local" / "share" / "fonts",
            ]
        )
        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            dirs.append(Path(xdg_data) / "fonts")

    return [d for d in dirs if d.exists()]


@lru_cache(maxsize=1)
def _all_font_files() -> tuple[Path, ...]:
    """All usable font files, bundled fonts first, deduplicated."""
    seen: dict[str, Path] = {}
    bundled = [d for d in _BUNDLED_FONT_DIRS if d.exists()]
    search_dirs = list(bundled) + _system_font_dirs()

    for directory in search_dirs:
        try:
            iterator = directory.glob("*") if directory in bundled else directory.rglob("*")
            for path in iterator:
                if path.is_file() and path.suffix.lower() in _FONT_EXTENSIONS:
                    seen.setdefault(str(path.resolve()).lower(), path)
        except (PermissionError, OSError):
            continue

    ordered_bundled = [p for p in seen.values() if any(str(p).startswith(str(d)) for d in bundled)]
    ordered_rest = sorted(p for p in seen.values() if p not in ordered_bundled)
    return tuple(ordered_bundled + ordered_rest)

@lru_cache(maxsize=512)
def _font_cmap(font_path: Path) -> Optional[frozenset]:
    if not _HAS_FONTTOOLS:
        return None
    try:
        tt = _TTFont(str(font_path), lazy=True, fontNumber=0)
        cmap = tt.getBestCmap()
        tt.close()
        return frozenset(cmap.keys()) if cmap else None
    except Exception:
        return None


# Fallback script -> font-filename-keyword hints, used only when fontTools
# is unavailable or a font's cmap couldn't be read. Extend as needed.
_SCRIPT_HINTS: tuple[tuple[re.Pattern, tuple[str, ...]], ...] = (
    (re.compile(r"[\u3040-\u30ff\u31f0-\u31ff]"), ("meiryo", "yugoth", "msgothic", "notosanscjkjp", "notosansjp", "sourcehansans", "ipam", "ipaex", "hiragino")),
    (re.compile(r"[\uac00-\ud7a3\u1100-\u11ff]"), ("malgun", "notosanscjkkr", "notosanskr", "applegothic", "gulim")),
    (re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]"), ("notosanscjk", "notosanssc", "notosanstc", "msyahei", "simsun", "pingfang", "heiti")),
    (re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]"), ("notosansarabic", "arial", "tahoma", "geeza")),
    (re.compile(r"[\u0590-\u05ff]"), ("notosanshebrew", "arial", "tahoma")),
    (re.compile(r"[\u0900-\u097f]"), ("notosansdevanagari", "mangal", "nirmala")),
    (re.compile(r"[\u0980-\u09ff]"), ("notosansbengali", "vrinda", "nirmala")),
    (re.compile(r"[\u0a00-\u0a7f]"), ("notosansgurmukhi", "raavi", "nirmala")),
    (re.compile(r"[\u0a80-\u0aff]"), ("notosansgujarati", "shruti", "nirmala")),
    (re.compile(r"[\u0b00-\u0b7f]"), ("notosansoriya", "nirmala")),
    (re.compile(r"[\u0b80-\u0bff]"), ("notosanstamil", "latha", "nirmala")),
    (re.compile(r"[\u0c00-\u0c7f]"), ("notosanstelugu", "gautami", "nirmala")),
    (re.compile(r"[\u0c80-\u0cff]"), ("notosanskannada", "tunga", "nirmala")),
    (re.compile(r"[\u0d00-\u0d7f]"), ("notosansmalayalam", "kartika", "nirmala")),
    (re.compile(r"[\u0d80-\u0dff]"), ("notosanssinhala", "iskoola", "nirmala")),
    (re.compile(r"[\u0e00-\u0e7f]"), ("notosansthai", "leelawadee", "tahoma")),
    (re.compile(r"[\u0e80-\u0eff]"), ("notosanslao", "dokchampa")),
    (re.compile(r"[\u1000-\u109f\uaa60-\uaa7f]"), ("notosansmyanmar", "myanmartext", "padauk")),
    (re.compile(r"[\u1780-\u17ff]"), ("notosanskhmer", "khmerui", "leelawadee")),
    (re.compile(r"[\u1200-\u139f\u2d80-\u2ddf]"), ("notosansethiopic", "nyala", "ebrima")),
    (re.compile(r"[\u0530-\u058f]"), ("notosansarmenian", "sylfaen")),
    (re.compile(r"[\u10a0-\u10ff]"), ("notosansgeorgian", "sylfaen")),
    (re.compile(r"[\u0400-\u04ff]"), ("notosans", "arial", "tahoma", "segoeui")),  # Cyrillic
    (re.compile(r"[\u0370-\u03ff]"), ("notosans", "arial", "tahoma", "segoeui")),  # Greek
    (re.compile(r"[\U0001f300-\U0001faff\u2600-\u27bf]"), ("segoeuiemoji", "notocoloremoji", "applecoloremoji", "notoemoji")),
)


def _heuristic_hints_for_char(char: str) -> tuple[str, ...]:
    for pattern, hints in _SCRIPT_HINTS:
        if pattern.match(char):
            return hints
    return ()


@lru_cache(maxsize=1024)
def _load_font_from_path(font_path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(font_path), size=size)


def _font_has_visible_glyph(font_path: Path, char: str) -> bool:
    try:
        font = _load_font_from_path(font_path, 40)
        bbox = font.getbbox(char)
        return bool(bbox) and bbox[2] > bbox[0] and bbox[3] > bbox[1]
    except Exception:
        return False


@lru_cache(maxsize=8192)
def _font_path_for_char(char: str) -> Optional[Path]:
    if char.isspace():
        return None

    codepoint = ord(char)
    fonts = _all_font_files()
    if not fonts:
        return None

    if _HAS_FONTTOOLS:
        for font_path in fonts:
            cmap = _font_cmap(font_path)
            if cmap and codepoint in cmap:
                return font_path

    hints = _heuristic_hints_for_char(char)
    if hints:
        for font_path in fonts:
            lowered = font_path.name.lower().replace(" ", "").replace("-", "").replace("_", "")
            if any(hint in lowered for hint in hints):
                return font_path

    for font_path in fonts:
        if _font_has_visible_glyph(font_path, char):
            return font_path

    return fonts[0]


def _font_for_run(font_path: Optional[Path], size: int) -> ImageFont.FreeTypeFont:
    if font_path is not None:
        try:
            return _load_font_from_path(font_path, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

Run = tuple[str, Optional[Path]]


def _split_runs(text: str) -> list[Run]:
    if not text:
        return []

    runs: list[Run] = []
    current_text = ""
    current_font: Optional[Path] = None

    for char in text:
        font_path = current_font if char.isspace() else _font_path_for_char(char)

        if current_text and font_path == current_font:
            current_text += char
        else:
            if current_text:
                runs.append((current_text, current_font))
            current_text = char
            current_font = font_path

    if current_text:
        runs.append((current_text, current_font))

    if runs and runs[0][1] is None:
        fallback = next((p for _, p in runs if p is not None), None)
        runs[0] = (runs[0][0], fallback)

    return runs


def _run_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> float:
    return draw.textlength(text, font=font)


def _line_width(draw: ImageDraw.ImageDraw, line: list[Run], size: int) -> float:
    return sum(_run_width(draw, text, _font_for_run(path, size)) for text, path in line)


def _break_runs_to_width(
    draw: ImageDraw.ImageDraw, runs: list[Run], size: int, max_width: float
) -> list[list[Run]]:
    """Character-level fallback wrap for text with no usable spaces."""
    lines: list[list[Run]] = [[]]
    current_width = 0.0

    for text, font_path in runs:
        font = _font_for_run(font_path, size)
        for char in text:
            char_width = _run_width(draw, char, font)
            if current_width and current_width + char_width > max_width:
                lines.append([])
                current_width = 0.0
            if lines[-1] and lines[-1][-1][1] == font_path:
                last_text, _ = lines[-1][-1]
                lines[-1][-1] = (last_text + char, font_path)
            else:
                lines[-1].append((char, font_path))
            current_width += char_width

    return [line for line in lines if line] or [[]]


def _wrap_mixed(draw: ImageDraw.ImageDraw, text: str, size: int, max_width: float) -> list[list[Run]]:
    lines: list[list[Run]] = []

    for raw_line in text.splitlines() or [text]:
        words = raw_line.split()

        if len(words) <= 1:
            runs = _split_runs(raw_line)
            if _line_width(draw, runs, size) <= max_width:
                lines.append(runs)
            else:
                lines.extend(_break_runs_to_width(draw, runs, size, max_width))
            continue

        current_line: list[Run] = []
        current_width = 0.0

        for word in words:
            word_runs = _split_runs(word)
            word_width = _line_width(draw, word_runs, size)
            last_font = current_line[-1][1] if current_line else None
            space_width = _run_width(draw, " ", _font_for_run(last_font, size)) if current_line else 0.0

            if word_width > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line, current_width = [], 0.0
                broken = _break_runs_to_width(draw, word_runs, size, max_width)
                lines.extend(broken[:-1])
                current_line = broken[-1] if broken else []
                current_width = _line_width(draw, current_line, size)
                continue

            if current_line and current_width + space_width + word_width > max_width:
                lines.append(current_line)
                current_line = list(word_runs)
                current_width = word_width
            else:
                if current_line:
                    current_line.append((" ", last_font))
                    current_width += space_width
                current_line.extend(word_runs)
                current_width += word_width

        lines.append(current_line)

    return lines


def _line_metrics(draw: ImageDraw.ImageDraw, line: list[Run], size: int) -> tuple[float, float, float]:
    """Returns (width, ascent, descent) for a line of mixed-font runs."""
    if not line:
        font = _font_for_run(None, size)
        ascent, descent = font.getmetrics()
        return 0.0, float(ascent), float(descent)

    width = 0.0
    ascent = 0.0
    descent = 0.0
    for text, font_path in line:
        font = _font_for_run(font_path, size)
        width += _run_width(draw, text, font)
        a, d = font.getmetrics()
        ascent = max(ascent, a)
        descent = max(descent, d)
    return width, ascent, descent


def _fit_mixed_text(
    draw: ImageDraw.ImageDraw, text: str, width: int, height: int
) -> tuple[list[list[Run]], int]:
    safe_text = text.strip() or " "
    min_size = 10
    max_size = max(12, min(height, max(width // 2, 18)))
    spacing = 4

    best_lines: list[list[Run]] = [_split_runs(safe_text)]
    best_size = min_size

    for size in range(max_size, min_size - 1, -1):
        lines = _wrap_mixed(draw, safe_text, size, max(10, width - 12))
        metrics = [_line_metrics(draw, line, size) for line in lines]
        text_width = max((m[0] for m in metrics), default=0.0)
        text_height = sum(m[1] + m[2] for m in metrics) + spacing * max(0, len(lines) - 1)

        best_lines, best_size = lines, size
        if text_width <= width - 8 and text_height <= height - 8:
            return lines, size

    return best_lines, best_size


# --------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------

def _polygon_bounds(coords: Iterable[Iterable[float]]) -> tuple[int, int, int, int]:
    xs = [int(round(point[0])) for point in coords]
    ys = [int(round(point[1])) for point in coords]
    return min(xs), min(ys), max(xs), max(ys)

def _estimate_background_color(image: Image.Image, coords: list[list[float]]) -> tuple[int, int, int]:
    x_min, y_min, x_max, y_max = _polygon_bounds(coords)
    if x_max <= x_min or y_max <= y_min:
        return (255, 255, 255)

    crop = image.crop((x_min, y_min, x_max, y_max)).convert("RGB")
    pixels = list(crop.getdata())
    if not pixels:
        return (255, 255, 255)

    quantized = Counter((r // 8 * 8, g // 8 * 8, b // 8 * 8) for r, g, b in pixels)
    dominant_bucket, _ = quantized.most_common(1)[0]

    matches = [
        p for p in pixels
        if (p[0] // 8 * 8, p[1] // 8 * 8, p[2] // 8 * 8) == dominant_bucket
    ]
    n = len(matches)
    r = sum(p[0] for p in matches) // n
    g = sum(p[1] for p in matches) // n
    b = sum(p[2] for p in matches) // n
    return (r, g, b)


def _paste_fill(image: Image.Image, coords: list[list[float]]) -> tuple[int, int, int]:
    x_min, y_min, x_max, y_max = _polygon_bounds(coords)
    if x_max <= x_min or y_max <= y_min:
        return (255, 255, 255)

    color = _estimate_background_color(image, coords)
    draw = ImageDraw.Draw(image)
    draw.polygon([(point[0], point[1]) for point in coords], fill=(*color, 255))
    return color


def _contrast_colors(bg: tuple[int, int, int]) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    r, g, b = bg
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if luminance > 140:
        return (0, 0, 0, 255), (255, 255, 255, 255)  # dark text on light bg
    return (255, 255, 255, 255), (0, 0, 0, 255)  # light text on dark bg


# --------------------------------------------------------------------------
# Drawing
# --------------------------------------------------------------------------

def _draw_mixed_line(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    line: list[Run],
    size: int,
    fill: tuple[int, int, int, int],
    stroke_fill: tuple[int, int, int, int],
    stroke_width: int,
) -> None:
    cursor_x = x
    for text, font_path in line:
        font = _font_for_run(font_path, size)
        draw.text(
            (cursor_x, y),
            text,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        cursor_x += _run_width(draw, text, font)


def _draw_translation(
    image: Image.Image, coords: list[list[float]], text: str, bg_color: tuple[int, int, int]
) -> None:
    draw = ImageDraw.Draw(image)
    x_min, y_min, x_max, y_max = _polygon_bounds(coords)
    width = max(1, x_max - x_min)
    height = max(1, y_max - y_min)
    spacing = 4

    lines, size = _fit_mixed_text(draw, text, width, height)
    metrics = [_line_metrics(draw, line, size) for line in lines]
    line_heights = [a + d for _, a, d in metrics]
    text_height = sum(line_heights) + spacing * max(0, len(lines) - 1)

    fill, stroke = _contrast_colors(bg_color)

    y = y_min + (height - text_height) / 2
    for line, (line_width, _, _), line_height in zip(lines, metrics, line_heights):
        x = x_min + (width - line_width) / 2
        _draw_mixed_line(draw, x, y, line, size, fill, stroke, stroke_width=2)
        y += line_height + spacing

def create(results: list, output_folder: str = "./output_translated"):
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    grouped = defaultdict(list)
    for image_path, coords, text in results:
        grouped[str(image_path)].append((coords, text))

    saved_files = []

    for file_path, blocks in grouped.items():
        image = Image.open(file_path).convert("RGBA")

        for coords, text in blocks:
            coords_list = [[float(point[0]), float(point[1])] for point in coords]
            bg_color = _paste_fill(image, coords_list)
            _draw_translation(image, coords_list, str(text), bg_color)

        output_file = output_path / Path(file_path).name
        image.save(output_file)
        saved_files.append(str(output_file))

    return saved_files
import textwrap
from PIL import ImageDraw, ImageFont


def truncate_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, max_lines: int = 3) -> list[str]:
    """Smart truncation: wrap text and cut at max_lines, adding ellipsis."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        w = _measure(test_line, font)
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while _measure(last + '…', font) > max_width and last:
            last = last[:-1]
        lines[-1] = last.strip() + '…'

    return lines


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text into lines without truncation."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test = ' '.join(current_line + [word])
        if _measure(test, font) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines if lines else ['']


def fit_text(
    text: str,
    draw: ImageDraw.ImageDraw,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    weight: str = 'Bold',
    font_getter=None
) -> tuple[list[str], ImageFont.FreeTypeFont]:
    """
    Dynamically shrinks font until all wrapped lines fit within max_height.
    Returns (lines, font).
    """
    size = start_size
    while size >= min_size:
        font = font_getter(weight, size)
        lines = wrap_text(text, font, max_width)
        total_h = sum(_line_height(l, font) for l in lines) + (len(lines) - 1) * 8
        if total_h <= max_height:
            return lines, font
        size -= 2
    # Last resort: truncate
    font = font_getter(weight, min_size)
    lines = truncate_text(text, font, max_width, max_lines=max_height // (_line_height('A', font) + 8))
    return lines, font


def _measure(text: str, font: ImageFont.FreeTypeFont) -> int:
    """Measure the pixel width of a string."""
    from PIL import Image
    img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _line_height(text: str, font: ImageFont.FreeTypeFont) -> int:
    """Measure the pixel height of a string."""
    from PIL import Image
    img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def text_width(text: str, font: ImageFont.FreeTypeFont) -> int:
    return _measure(text, font)


def text_height(text: str, font: ImageFont.FreeTypeFont) -> int:
    return _line_height(text, font)

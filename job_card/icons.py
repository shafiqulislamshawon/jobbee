"""
Pure Pillow icon drawing module.
Each function draws a minimal, consistent icon onto an ImageDraw canvas.
Icons are line-art style for a clean, professional look.
"""
from PIL import ImageDraw


def _draw_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, color: str, width: int = 2):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)


def draw_location_pin(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str):
    """Map pin icon."""
    w = size
    h = int(size * 1.3)
    r = w // 2
    # Circle head
    draw.ellipse([x, y, x + w, y + w], outline=color, width=2)
    # Pin body (two lines converging to a point)
    draw.line([x + r - 2, y + w - 2, x + r, y + h], fill=color, width=2)
    draw.line([x + r + 2, y + w - 2, x + r, y + h], fill=color, width=2)
    # Inner dot
    ir = max(2, w // 5)
    draw.ellipse([x + r - ir, y + r - ir, x + r + ir, y + r + ir], fill=color)


def draw_currency(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str):
    """Dollar sign circle icon."""
    r = size // 2
    cx, cy = x + r, y + r
    draw.ellipse([x, y, x + size, y + size], outline=color, width=2)
    # $ symbol lines
    mid_x = cx
    draw.line([mid_x, cy - r // 2, mid_x, cy + r // 2], fill=color, width=2)
    draw.arc([mid_x - r // 3, cy - r // 2 + 2, mid_x + r // 3, cy], start=0, end=180, fill=color, width=2)
    draw.arc([mid_x - r // 3, cy, mid_x + r // 3, cy + r // 2 - 2], start=180, end=360, fill=color, width=2)


def draw_briefcase(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str):
    """Briefcase icon."""
    h = int(size * 0.75)
    y_offset = size - h
    # Main body
    draw.rectangle([x, y + y_offset, x + size, y + size], outline=color, width=2)
    # Handle
    handle_w = size // 3
    handle_x = x + (size - handle_w) // 2
    draw.rectangle([handle_x, y, handle_x + handle_w, y + y_offset + 2], outline=color, width=2)
    # Middle line
    draw.line([x, y + y_offset + h // 2, x + size, y + y_offset + h // 2], fill=color, width=2)


def draw_clock(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str):
    """Clock icon."""
    r = size // 2
    cx, cy = x + r, y + r
    draw.ellipse([x, y, x + size, y + size], outline=color, width=2)
    # Clock hands
    draw.line([cx, cy, cx, cy - r // 2], fill=color, width=2)
    draw.line([cx, cy, cx + r // 3, cy], fill=color, width=2)


def draw_graduation_cap(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str):
    """Graduation cap icon (simplified)."""
    mid = size // 2
    # Hat brim (parallelogram approximation as polygon)
    draw.polygon([
        (x + mid, y),
        (x + size, y + size // 3),
        (x + mid, y + size // 2),
        (x, y + size // 3),
    ], outline=color, fill=None)
    # Hat top
    draw.rectangle([x + mid - size // 6, y + size // 3, x + mid + size // 6, y + size - 4], outline=color, width=2)
    # Tassel
    draw.line([x + size - 4, y + size // 3, x + size - 4, y + size - 4], fill=color, width=2)
    draw.ellipse([x + size - 7, y + size - 7, x + size - 1, y + size - 1], fill=color)


def draw_building(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str):
    """Building icon."""
    draw.rectangle([x, y + size // 4, x + size, y + size], outline=color, width=2)
    # Windows
    win_s = size // 5
    for col in [x + size // 5, x + size // 2]:
        for row in [y + size // 3, y + size * 2 // 3]:
            draw.rectangle([col, row, col + win_s, row + win_s], outline=color, width=1)
    # Roof triangle
    draw.polygon([(x, y + size // 4), (x + size // 2, y), (x + size, y + size // 4)], outline=color)


def draw_calendar(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str):
    """Calendar icon."""
    top = size // 5
    draw.rectangle([x, y + top, x + size, y + size], outline=color, width=2)
    draw.line([x, y + top * 2, x + size, y + top * 2], fill=color, width=2)
    # Calendar tabs
    for tab_x in [x + size // 4, x + size * 3 // 4]:
        draw.line([tab_x, y, tab_x, y + top + 2], fill=color, width=3)
    # Small grid squares
    sq = size // 5
    for col in range(3):
        for row in range(2):
            bx = x + size // 6 + col * (sq + 2)
            by = y + top * 2 + size // 7 + row * (sq + 2)
            draw.rectangle([bx, by, bx + sq - 2, by + sq - 2], outline=color, width=1)


def draw_users(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str):
    """People / vacancies icon."""
    r = size // 5
    # Two person silhouettes
    for offset in [0, size // 3]:
        cx = x + r + offset
        cy = y + r
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
        draw.arc([cx - r * 2, cy + r // 2, cx + r * 2, cy + size], start=0, end=180, fill=color, width=2)


ICON_MAP = {
    'location': draw_location_pin,
    'salary': draw_currency,
    'experience': draw_briefcase,
    'employment': draw_clock,
    'education': draw_graduation_cap,
    'workplace': draw_building,
    'deadline': draw_calendar,
    'vacancies': draw_users,
}


def draw_icon(draw: ImageDraw.ImageDraw, name: str, x: int, y: int, size: int, color: str):
    """Draw a named icon at the given position."""
    fn = ICON_MAP.get(name)
    if fn:
        fn(draw, x, y, size, color)

"""
Reusable UI components for the job card generator.
Each component function draws directly onto the Pillow canvas.
"""
from PIL import Image, ImageDraw
from .typography import get_font
from .utils.text import text_width, text_height, wrap_text, truncate_text
from .utils.image import load_logo, paste_image, rounded_rectangle_mask, hex_to_rgb
from .utils.qr import generate_qr
from .icons import draw_icon
from .themes import ThemeColors


# ---------------------------------------------------------------------------
# BADGE: "WE ARE HIRING"
# ---------------------------------------------------------------------------

def draw_hiring_badge(
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    y: int,
    theme: ThemeColors,
    label: str = "WE ARE HIRING",
    align: str = "center"
) -> int:
    """Draws the 'WE ARE HIRING' pill badge. Returns bottom y coordinate."""
    font = get_font('SemiBold', 22)
    padding_x, padding_y = 32, 12
    tw = text_width(label, font)
    th = text_height(label, font)
    badge_w = tw + padding_x * 2
    badge_h = th + padding_y * 2

    if align == "center":
        bx = (canvas_width - badge_w) // 2
    elif align == "left":
        bx = 80
    else:
        bx = canvas_width - badge_w - 80

    by = y
    radius = badge_h // 2

    # Badge background (mustard yellow)
    draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=radius, fill=theme.primary)

    # Badge text (black)
    tx = bx + padding_x
    ty = by + padding_y
    draw.text((tx, ty), label, font=font, fill=theme.text_primary)

    return by + badge_h


# ---------------------------------------------------------------------------
# JOB TITLE
# ---------------------------------------------------------------------------

def draw_job_title(
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    y: int,
    title: str,
    theme: ThemeColors,
    margin: int = 80,
    align: str = "center",
    max_font_size: int = 72,
    min_font_size: int = 36,
) -> int:
    """Draws the job title with dynamic font sizing. Returns bottom y coordinate."""
    max_w = canvas_width - margin * 2
    size = max_font_size

    while size >= min_font_size:
        font = get_font('ExtraBold', size)
        lines = wrap_text(title, font, max_w)
        if len(lines) <= 3:
            break
        size -= 4

    font = get_font('ExtraBold', size)
    lines = wrap_text(title, font, max_w)
    line_gap = 8

    current_y = y
    for line in lines:
        tw = text_width(line, font)
        th = text_height(line, font)
        if align == "center":
            tx = (canvas_width - tw) // 2
        elif align == "left":
            tx = margin
        else:
            tx = canvas_width - tw - margin
        draw.text((tx, current_y), line, font=font, fill=theme.text_primary)
        current_y += th + line_gap

    return current_y


# ---------------------------------------------------------------------------
# COMPANY NAME
# ---------------------------------------------------------------------------

def draw_company_name(
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    y: int,
    company: str,
    theme: ThemeColors,
    margin: int = 80,
    align: str = "center",
) -> int:
    """Draws company name below the job title. Returns bottom y."""
    font = get_font('SemiBold', 28)
    max_w = canvas_width - margin * 2
    tw = text_width(company, font)
    th = text_height(company, font)

    if tw > max_w:
        font = get_font('SemiBold', 22)
        tw = text_width(company, font)
        th = text_height(company, font)

    if align == "center":
        tx = (canvas_width - tw) // 2
    elif align == "left":
        tx = margin
    else:
        tx = canvas_width - tw - margin

    draw.text((tx, y), company, font=font, fill=theme.text_secondary)
    return y + th


# ---------------------------------------------------------------------------
# HORIZONTAL RULE
# ---------------------------------------------------------------------------

def draw_rule(
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    y: int,
    color: str,
    margin: int = 80,
    thickness: int = 2,
) -> int:
    """Draws a horizontal rule. Returns y after the line."""
    draw.line([(margin, y), (canvas_width - margin, y)], fill=color, width=thickness)
    return y + thickness


# ---------------------------------------------------------------------------
# METADATA GRID
# ---------------------------------------------------------------------------

def draw_metadata_grid(
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    y: int,
    items: list[tuple[str, str, str]],  # (icon_name, label, value)
    theme: ThemeColors,
    margin: int = 80,
    columns: int = 2,
    row_gap: int = 28,
    col_gap: int = 24,
) -> int:
    """
    Draws a 2-column metadata grid.
    Each item is (icon_name, label, value).
    Returns bottom y coordinate.
    """
    label_font = get_font('Medium', 16)
    value_font = get_font('SemiBold', 22)
    icon_size = 18

    col_w = (canvas_width - margin * 2 - col_gap) // columns
    current_x = margin
    current_y = y
    col = 0

    for icon_name, label, value in items:
        if not value:
            continue

        ix = current_x
        iy = current_y + 4

        # Draw icon
        draw_icon(draw, icon_name, ix, iy, icon_size, theme.primary)

        # Label
        label_x = ix + icon_size + 8
        draw.text((label_x, current_y), label.upper(), font=label_font, fill=theme.text_secondary)

        # Value
        val_y = current_y + text_height('A', label_font) + 4
        tw = text_width(value, value_font)
        if tw > col_w - icon_size - 16:
            value_font_small = get_font('SemiBold', 18)
            draw.text((label_x, val_y), value, font=value_font_small, fill=theme.text_primary)
            val_h = text_height(value, value_font_small)
        else:
            draw.text((label_x, val_y), value, font=value_font, fill=theme.text_primary)
            val_h = text_height(value, value_font)

        col += 1
        if col >= columns:
            col = 0
            current_x = margin
            current_y = val_y + val_h + row_gap
        else:
            current_x += col_w + col_gap

    if col > 0:
        # Finish incomplete row
        current_y = current_y + text_height('A', label_font) + text_height('A', value_font) + 4 + row_gap

    return current_y


# ---------------------------------------------------------------------------
# SKILLS CHIPS
# ---------------------------------------------------------------------------

def draw_skill_chips(
    draw: ImageDraw.ImageDraw,
    canvas: Image.Image,
    canvas_width: int,
    y: int,
    skills: list[str],
    theme: ThemeColors,
    margin: int = 80,
    max_rows: int = 2,
) -> int:
    """Draws skill pill chips in a flowing layout. Returns bottom y coordinate."""
    if not skills:
        return y

    font = get_font('Medium', 19)
    px, py = 20, 9
    gap_x, gap_y = 10, 10
    row_height = text_height('A', font) + py * 2

    current_x = margin
    current_y = y
    row = 0

    for skill in skills:
        if row >= max_rows:
            break
        tw = text_width(skill, font)
        chip_w = tw + px * 2

        if current_x + chip_w > canvas_width - margin and current_x > margin:
            current_x = margin
            current_y += row_height + gap_y
            row += 1
            if row >= max_rows:
                break

        # Draw chip
        draw.rounded_rectangle(
            [current_x, current_y, current_x + chip_w, current_y + row_height],
            radius=row_height // 2,
            fill=theme.background,
            outline=theme.text_primary,
            width=1,
        )
        draw.text(
            (current_x + px, current_y + py),
            skill,
            font=font,
            fill=theme.text_primary,
        )
        current_x += chip_w + gap_x

    return current_y + row_height


# ---------------------------------------------------------------------------
# DESCRIPTION
# ---------------------------------------------------------------------------

def draw_description(
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    y: int,
    description: str,
    theme: ThemeColors,
    margin: int = 80,
    max_lines: int = 3,
) -> int:
    """Draws a truncated description block. Returns bottom y."""
    if not description:
        return y

    font = get_font('Regular', 22)
    max_w = canvas_width - margin * 2
    lines = truncate_text(description, font, max_w, max_lines)
    line_h = text_height('A', font)
    line_gap = 6

    current_y = y
    for line in lines:
        draw.text((margin, current_y), line, font=font, fill=theme.text_secondary)
        current_y += line_h + line_gap

    return current_y


# ---------------------------------------------------------------------------
# DEADLINE BLOCK
# ---------------------------------------------------------------------------

def draw_deadline(
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    y: int,
    deadline: str,
    theme: ThemeColors,
    margin: int = 80,
) -> int:
    """Draws a bold deadline block. Returns bottom y."""
    label_font = get_font('Medium', 17)
    date_font = get_font('Bold', 32)

    label = "APPLICATION DEADLINE"
    label_w = text_width(label, label_font)
    label_h = text_height(label, label_font)
    draw.text(((canvas_width - label_w) // 2, y), label, font=label_font, fill=theme.text_secondary)

    date_y = y + label_h + 8
    date_w = text_width(deadline, date_font)
    date_h = text_height(deadline, date_font)
    draw.text(((canvas_width - date_w) // 2, date_y), deadline.upper(), font=date_font, fill=theme.primary)

    return date_y + date_h


# ---------------------------------------------------------------------------
# CTA BUTTON
# ---------------------------------------------------------------------------

def draw_cta_button(
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    y: int,
    theme: ThemeColors,
    label: str = "APPLY NOW  →",
    style: str = "black",  # "black" or "yellow"
    margin: int = 80,
) -> int:
    """Draws the CTA button. Returns bottom y."""
    font = get_font('Bold', 24)
    tw = text_width(label, font)
    th = text_height(label, font)
    px, py = 60, 18
    btn_w = tw + px * 2
    btn_h = th + py * 2
    btn_x = (canvas_width - btn_w) // 2
    btn_y = y

    if style == "black":
        bg = theme.text_primary
        fg = theme.primary
    else:
        bg = theme.primary
        fg = theme.text_primary

    draw.rounded_rectangle(
        [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
        radius=btn_h // 2,
        fill=bg,
    )
    draw.text((btn_x + px, btn_y + py), label, font=font, fill=fg)
    return btn_y + btn_h


# ---------------------------------------------------------------------------
# LOGO + HEADER BRANDING
# ---------------------------------------------------------------------------

def draw_header(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    y: int,
    company_name: str,
    portal_name: str,
    logo_path: str | None,
    theme: ThemeColors,
    margin: int = 80,
) -> int:
    """
    Draws the header: logo | company name | portal branding.
    Returns bottom y.
    """
    logo_size = (80, 80)
    logo = load_logo(logo_path, logo_size) if logo_path else None

    name_font = get_font('Bold', 26)
    portal_font = get_font('Regular', 18)

    logo_h = logo_size[1]
    current_y = y

    if logo:
        lx = margin
        ly = current_y + (logo_h - logo.size[1]) // 2
        paste_image(canvas, logo, (lx, ly))
        text_x = lx + logo.size[0] + 16
    else:
        # Draw a placeholder circle with first letter
        r = 36
        cx, cy = margin + r, current_y + r
        draw.ellipse([margin, current_y, margin + r * 2, current_y + r * 2], fill=theme.primary)
        init_font = get_font('ExtraBold', 30)
        letter = company_name[0].upper() if company_name else 'J'
        lw = text_width(letter, init_font)
        lh = text_height(letter, init_font)
        draw.text((cx - lw // 2, cy - lh // 2), letter, font=init_font, fill=theme.text_primary)
        text_x = margin + r * 2 + 16

    # Company name
    draw.text((text_x, current_y + 8), company_name, font=name_font, fill=theme.text_primary)

    # Portal branding on right side
    portal_w = text_width(portal_name, portal_font)
    draw.text((canvas_width - margin - portal_w, current_y + 8), portal_name, font=portal_font, fill=theme.text_secondary)

    return current_y + logo_h


# ---------------------------------------------------------------------------
# QR CODE
# ---------------------------------------------------------------------------

def draw_qr_block(
    canvas: Image.Image,
    canvas_width: int,
    canvas_height: int,
    url: str,
    theme: ThemeColors,
    qr_size: int = 120,
    margin: int = 80,
) -> None:
    """Draws a QR code in the bottom-right corner of the canvas."""
    if not url:
        return
    qr_img = generate_qr(url, size=qr_size, fg_color=theme.text_primary, bg_color=theme.background)
    if qr_img:
        qr_x = canvas_width - margin - qr_size
        qr_y = canvas_height - margin - qr_size
        paste_image(canvas, qr_img, (qr_x, qr_y))


# ---------------------------------------------------------------------------
# SECTION LABEL
# ---------------------------------------------------------------------------

def draw_section_label(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    label: str,
    theme: ThemeColors,
) -> int:
    """Draws a small uppercase section label. Returns bottom y."""
    font = get_font('SemiBold', 16)
    draw.text((x, y), label.upper(), font=font, fill=theme.text_secondary)
    return y + text_height(label, font) + 4

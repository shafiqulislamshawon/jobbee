from PIL import Image
import io


def load_logo(path: str, max_size: tuple[int, int] = (120, 120)) -> Image.Image | None:
    """Load a logo from a path, resize while preserving aspect ratio."""
    if not path:
        return None
    try:
        img = Image.open(path).convert('RGBA')
        img.thumbnail(max_size, Image.LANCZOS)
        return img
    except Exception:
        return None


def paste_image(canvas: Image.Image, img: Image.Image, position: tuple[int, int]):
    """Paste an RGBA image onto the canvas at position, handling transparency."""
    if img.mode == 'RGBA':
        canvas.paste(img, position, img)
    else:
        canvas.paste(img, position)


def rounded_rectangle_mask(size: tuple[int, int], radius: int) -> Image.Image:
    """Create a rounded rectangle mask for compositing."""
    mask = Image.new('L', size, 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255)
    return mask


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    """Convert hex color string to RGBA tuple."""
    r, g, b = hex_to_rgb(hex_color)
    return (r, g, b, alpha)

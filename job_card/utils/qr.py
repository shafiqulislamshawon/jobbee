from PIL import Image

try:
    import qrcode
    from qrcode.image.pil import PilImage
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


def generate_qr(url: str, size: int = 200, fg_color: str = "#111111", bg_color: str = "#FFFFFF") -> Image.Image | None:
    """
    Generate a high-contrast, scannable QR code as a PIL Image.
    Returns None if qrcode is not installed.
    """
    if not QR_AVAILABLE:
        return None

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert('RGBA')

    # Resize to the requested size while maintaining quality
    qr_img = qr_img.resize((size, size), Image.LANCZOS)
    return qr_img

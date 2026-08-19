from abc import ABC, abstractmethod
from PIL import Image, ImageDraw
from ..models import JobPost
from ..themes import ThemeColors, BRAND_THEME


class BaseTemplate(ABC):
    """Abstract base class for all card templates."""

    PORTAL_NAME = "JobBee.com"

    def __init__(
        self,
        job: JobPost,
        size: tuple[int, int] = (1080, 1350),
        theme: ThemeColors = None,
        show_qr: bool = True,
    ):
        self.job = job
        self.size = size
        self.width, self.height = size
        self.theme = theme or BRAND_THEME
        self.show_qr = show_qr

    def create_canvas(self) -> tuple[Image.Image, ImageDraw.ImageDraw]:
        img = Image.new('RGB', self.size, color=self.theme.background)
        draw = ImageDraw.Draw(img)
        return img, draw

    @abstractmethod
    def render(self) -> Image.Image:
        """Renders the complete card and returns a PIL Image."""
        ...

import os
from PIL import ImageDraw, ImageFont

# Get the directory where fonts are stored
FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')

def get_font(weight: str = 'Regular', size: int = 24) -> ImageFont.FreeTypeFont:
    """Loads a font of a specific weight and size."""
    # Assuming Inter-Regular.ttf, Inter-Bold.ttf etc.
    font_path = os.path.join(FONT_DIR, f'Inter-{weight}.ttf')
    
    # Fallback to Regular if specific weight is missing
    if not os.path.exists(font_path):
        font_path = os.path.join(FONT_DIR, 'Inter-Regular.ttf')
        
    # If even regular is missing, use default
    if not os.path.exists(font_path):
        return ImageFont.load_default()
        
    return ImageFont.truetype(font_path, size)

class TextWrapper:
    @staticmethod
    def get_text_width(text: str, font: ImageFont.FreeTypeFont) -> int:
        dummy_img = ImageDraw.Draw(None)
        bbox = dummy_img.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
        
    @staticmethod
    def get_text_height(text: str, font: ImageFont.FreeTypeFont) -> int:
        dummy_img = ImageDraw.Draw(None)
        bbox = dummy_img.textbbox((0, 0), text, font=font)
        return bbox[3] - bbox[1]

    @staticmethod
    def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        """Wraps text into multiple lines based on max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            width = TextWrapper.get_text_width(' '.join(current_line), font)
            if width > max_width:
                if len(current_line) == 1:
                    # Single word is longer than max width, have to force it
                    lines.append(current_line[0])
                    current_line = []
                else:
                    # Remove last word, finalize line, start new line with word
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines

    @staticmethod
    def truncate_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, max_lines: int) -> list[str]:
        """Wraps text and truncates with ellipsis if it exceeds max_lines."""
        lines = TextWrapper.wrap_text(text, font, max_width)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            # Add ellipsis to the last line
            last_line = lines[-1]
            while TextWrapper.get_text_width(last_line + "...", font) > max_width and len(last_line) > 0:
                last_line = last_line[:-1]
            lines[-1] = last_line.strip() + "..."
        return lines

from dataclasses import dataclass

@dataclass
class ThemeColors:
    primary: str
    primary_dark: str
    background: str
    text_primary: str
    text_secondary: str
    accent_light: str
    accent_dark: str
    border: str

# Default Brand Theme (Mustard Yellow, Black, White)
BRAND_THEME = ThemeColors(
    primary="#D4A017",
    primary_dark="#B8860B",
    background="#FFFFFF",
    text_primary="#111111",
    text_secondary="#6B6B6B",
    accent_light="#EAEAEA",
    accent_dark="#333333",
    border="#DDDDDD"
)

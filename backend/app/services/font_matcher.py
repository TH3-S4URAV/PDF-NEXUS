"""
PDF NEXUS - Font Matcher & Identification Engine
Maps embedded/subset PDF fonts to standardized font families, handles fallbacks,
calculates font metrics, and alerts on missing glyphs.
"""

import re
from typing import Tuple, Dict, Any, Optional

# Standard PDF Font Family mappings supported natively by PyMuPDF / PDF specification
STANDARD_FONT_MAP = {
    # Helvetica / Sans-serif family
    "helvetica": {"normal": "helv", "bold": "hebo", "italic": "heit", "bold_italic": "hebi"},
    "arial": {"normal": "helv", "bold": "hebo", "italic": "heit", "bold_italic": "hebi"},
    "calibri": {"normal": "helv", "bold": "hebo", "italic": "heit", "bold_italic": "hebi"},
    "segoe": {"normal": "helv", "bold": "hebo", "italic": "heit", "bold_italic": "hebi"},
    "sans": {"normal": "helv", "bold": "hebo", "italic": "heit", "bold_italic": "hebi"},
    "roboto": {"normal": "helv", "bold": "hebo", "italic": "heit", "bold_italic": "hebi"},
    "open sans": {"normal": "helv", "bold": "hebo", "italic": "heit", "bold_italic": "hebi"},
    
    # Times / Serif family
    "times": {"normal": "tiro", "bold": "tibo", "italic": "tiit", "bold_italic": "tibi"},
    "times new roman": {"normal": "tiro", "bold": "tibo", "italic": "tiit", "bold_italic": "tibi"},
    "georgia": {"normal": "tiro", "bold": "tibo", "italic": "tiit", "bold_italic": "tibi"},
    "cambria": {"normal": "tiro", "bold": "tibo", "italic": "tiit", "bold_italic": "tibi"},
    "serif": {"normal": "tiro", "bold": "tibo", "italic": "tiit", "bold_italic": "tibi"},
    
    # Courier / Monospace family
    "courier": {"normal": "cour", "bold": "cobo", "italic": "coit", "bold_italic": "cobi"},
    "courier new": {"normal": "cour", "bold": "cobo", "italic": "coit", "bold_italic": "cobi"},
    "consolas": {"normal": "cour", "bold": "cobo", "italic": "coit", "bold_italic": "cobi"},
    "monaco": {"normal": "cour", "bold": "cobo", "italic": "coit", "bold_italic": "cobi"},
    "mono": {"normal": "cour", "bold": "cobo", "italic": "coit", "bold_italic": "cobi"},
}

def clean_font_name(raw_name: str) -> str:
    """
    Cleans subset prefixes like 'ABCDEF+Calibri-Bold' or 'F1' into readable font names.
    """
    if not raw_name:
        return "Helvetica"
    # Remove 6-letter subset tags (e.g. 'BAAAAA+ArialMT' -> 'ArialMT')
    cleaned = re.sub(r"^[A-Z]{6}\+", "", raw_name)
    # Remove common PostScript suffixes
    cleaned = cleaned.replace("MT", "").replace("PS", "").replace(",Bold", "-Bold").replace(",Italic", "-Italic")
    return cleaned.strip()

def detect_font_style(font_name: str, flags: int = 0) -> Tuple[bool, bool]:
    """
    Determines if text is bold and/or italic based on font name tokens and font flags.
    PyMuPDF flags: bit 1 (italic, 2^1=2), bit 4 (bold, 2^4=16)
    """
    name_lower = font_name.lower()
    is_bold = bool(flags & 16) or ("bold" in name_lower) or ("black" in name_lower) or ("heavy" in name_lower)
    is_italic = bool(flags & 2) or ("italic" in name_lower) or ("oblique" in name_lower) or ("slanted" in name_lower)
    return is_bold, is_italic

def match_standard_font(font_name: str, is_bold: bool = False, is_italic: bool = False) -> Tuple[str, bool, Optional[str]]:
    """
    Returns (pymupdf_font_code, is_exact_match, warning_message).
    """
    cleaned = clean_font_name(font_name).lower()
    
    # Check mappings
    target_family = None
    for key in STANDARD_FONT_MAP:
        if key in cleaned:
            target_family = STANDARD_FONT_MAP[key]
            break
            
    exact_match = True
    warning = None
    if not target_family:
        # Default to Helvetica
        target_family = STANDARD_FONT_MAP["helvetica"]
        exact_match = False
        warning = f"Original font '{font_name}' is not a standard built-in font; substituted with Helvetica."
        
    if is_bold and is_italic:
        code = target_family["bold_italic"]
    elif is_bold:
        code = target_family["bold"]
    elif is_italic:
        code = target_family["italic"]
    else:
        code = target_family["normal"]
        
    return code, exact_match, warning

def color_to_hex(color_val: Any) -> str:
    """Converts PyMuPDF sRGB int, tuple, or list into hex #RRGGBB string."""
    if isinstance(color_val, int):
        r = (color_val >> 16) & 255
        g = (color_val >> 8) & 255
        b = color_val & 255
        return f"#{r:02x}{g:02x}{b:02x}"
    elif isinstance(color_val, (tuple, list)):
        if len(color_val) >= 3:
            # Check if normalized 0.0 - 1.0 or 0 - 255
            r = int(color_val[0] * 255 if color_val[0] <= 1.0 else color_val[0])
            g = int(color_val[1] * 255 if color_val[1] <= 1.0 else color_val[1])
            b = int(color_val[2] * 255 if color_val[2] <= 1.0 else color_val[2])
            return f"#{r:02x}{g:02x}{b:02x}"
    return "#000000"

def hex_to_rgb(hex_str: str) -> Tuple[float, float, float]:
    """Converts hex #RRGGBB string to normalized (r, g, b) floats for PyMuPDF (0.0 to 1.0)."""
    if not hex_str:
        return (0.0, 0.0, 0.0)
    clean_hex = hex_str.lstrip("#")
    if len(clean_hex) == 3:
        clean_hex = "".join([c * 2 for c in clean_hex])
    try:
        r = int(clean_hex[0:2], 16) / 255.0
        g = int(clean_hex[2:4], 16) / 255.0
        b = int(clean_hex[4:6], 16) / 255.0
        return (r, g, b)
    except Exception:
        return (0.0, 0.0, 0.0)

"""
Theme manager for WIZARD-FITTINGS isometric renderer (v2.0.0).

Three built-in themes:

* ``"light_technical"``   – White background, black lines, blue dimensions.
* ``"dark_professional"`` – Dark background, light grey lines.
* ``"blueprint"``         – Classic blueprint dark-blue background.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Theme:
    """
    Rendering theme definition.

    Attributes
    ----------
    name:
        Theme identifier.
    background:
        Canvas background colour.
    object_line_color:
        Primary object outline colour.
    object_line_width:
        Primary object outline stroke width (px).
    hidden_line_color:
        Hidden/back edge colour.
    hidden_line_width:
        Hidden edge stroke width (px).
    hidden_line_dash:
        SVG dash-array list for hidden lines.
    dim_line_color:
        Dimension line and text colour.
    face_top:
        Top face fill colour.
    face_left:
        Left face fill colour.
    face_right:
        Right face fill colour.
    text_color:
        General annotation text colour.
    font_family:
        Font family for all labels.
    """

    name: str
    background: str
    object_line_color: str
    object_line_width: float
    hidden_line_color: str
    hidden_line_width: float
    hidden_line_dash: list
    dim_line_color: str
    face_top: str
    face_left: str
    face_right: str
    text_color: str
    font_family: str


# ---------------------------------------------------------------------------
# Built-in theme definitions
# ---------------------------------------------------------------------------

THEMES: Dict[str, Theme] = {
    "light_technical": Theme(
        name="light_technical",
        background="#FFFFFF",
        object_line_color="#111111",
        object_line_width=1.8,
        hidden_line_color="#AAAAAA",
        hidden_line_width=0.6,
        hidden_line_dash=[4, 3],
        dim_line_color="#1A56DB",
        face_top="#F9F9F9",
        face_left="#ECECEC",
        face_right="#E0E0E0",
        text_color="#111111",
        font_family="Courier New",
    ),
    "dark_professional": Theme(
        name="dark_professional",
        background="#12161C",
        object_line_color="#D4D4D4",
        object_line_width=1.8,
        hidden_line_color="#555555",
        hidden_line_width=0.6,
        hidden_line_dash=[4, 3],
        dim_line_color="#5B9CF6",
        face_top="#2A2F3A",
        face_left="#1E2330",
        face_right="#181C26",
        text_color="#E0E0E0",
        font_family="Courier New",
    ),
    "blueprint": Theme(
        name="blueprint",
        background="#003366",
        object_line_color="#FFFFFF",
        object_line_width=1.5,
        hidden_line_color="#7AAFD4",
        hidden_line_width=0.5,
        hidden_line_dash=[6, 4],
        dim_line_color="#FFD700",
        face_top="#005599",
        face_left="#004488",
        face_right="#003377",
        text_color="#FFFFFF",
        font_family="Courier New",
    ),
}

DEFAULT_THEME = "light_technical"


class ThemeManager:
    """
    Manages theme selection and provides colour helpers for the renderer.

    Usage::

        tm = ThemeManager("dark_professional")
        print(tm.theme.background)
        print(tm.face_colors())

    Parameters
    ----------
    theme_name:
        One of ``"light_technical"``, ``"dark_professional"``,
        ``"blueprint"``.  Defaults to ``"light_technical"``.
    """

    def __init__(self, theme_name: str = DEFAULT_THEME) -> None:
        self.set_theme(theme_name)

    def set_theme(self, theme_name: str) -> None:
        """Switch to a different theme."""
        if theme_name not in THEMES:
            valid = sorted(THEMES)
            raise ValueError(
                f"Unknown theme {theme_name!r}.  Valid themes: {valid}"
            )
        self._theme = THEMES[theme_name]

    @property
    def theme(self) -> Theme:
        """The currently active :class:`Theme`."""
        return self._theme

    def face_colors(self) -> Dict[str, str]:
        """Return a dict of face colours for isometric drawing primitives."""
        t = self._theme
        return {
            "top":     t.face_top,
            "left":    t.face_left,
            "right":   t.face_right,
            "outline": t.object_line_color,
            "side":    t.face_left,
            "cap":     t.face_top,
        }

    def dim_color(self) -> str:
        """Return the dimension line colour."""
        return self._theme.dim_line_color

    @staticmethod
    def available_themes() -> list:
        """Return a list of available theme names."""
        return sorted(THEMES)
"""Theme token contrast and selector regression tests."""

from __future__ import annotations

import unittest
from pathlib import Path
import tomllib

from src.streamlit_ui import (
    APP_CSS,
    DARK_THEME_VARIABLES,
    LIGHT_THEME_VARIABLES,
    _theme_fallback_css,
)


def _luminance(hex_color: str) -> float:
    rgb = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    channels = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in rgb]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast(first: str, second: str) -> float:
    values = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (values[0] + 0.05) / (values[1] + 0.05)


class ThemeContrastTests(unittest.TestCase):
    def test_light_and_dark_text_tokens_meet_readable_contrast(self) -> None:
        for theme in (LIGHT_THEME_VARIABLES, DARK_THEME_VARIABLES):
            for text_key in ("--lexi-text", "--lexi-muted", "--lexi-accent"):
                for background_key in ("--lexi-page", "--lexi-surface", "--lexi-surface-raised"):
                    with self.subTest(text=text_key, background=background_key, theme=theme):
                        self.assertGreaterEqual(
                            _contrast(theme[text_key], theme[background_key]), 4.5
                        )

    def test_css_styles_affected_components_without_unsupported_theme_selectors(self) -> None:
        for expected in (
            '[data-testid="stSidebar"]', '[data-testid="stMetricValue"]',
            '[data-testid="stMetricLabel"]', '.category-card', '.hero-panel',
            '.result-panel', '.small-muted', '[data-testid="stCaptionContainer"]',
        ):
            with self.subTest(selector=expected):
                self.assertIn(expected, APP_CSS)
        self.assertNotIn('html[data-theme=', APP_CSS)

    def test_theme_css_uses_context_tokens_and_defaults_to_light(self) -> None:
        config = Path(__file__).resolve().parents[1] / ".streamlit" / "config.toml"
        ui_source = Path(__file__).resolve().parents[1] / "src" / "streamlit_ui.py"
        settings = tomllib.loads(config.read_text(encoding="utf-8"))
        self.assertEqual(settings["theme"]["base"], "light")
        self.assertIn("light", settings["theme"])
        self.assertIn("dark", settings["theme"])
        self.assertIn("sidebar", settings["theme"]["light"])
        self.assertIn("sidebar", settings["theme"]["dark"])
        self.assertIn("st.context.theme.type", ui_source.read_text(encoding="utf-8"))

    def test_streamlit_toolbar_and_theme_menu_are_not_hidden(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config_text = (root / ".streamlit" / "config.toml").read_text(encoding="utf-8")
        app_text = (root / "app.py").read_text(encoding="utf-8")
        ui_text = (root / "src" / "streamlit_ui.py").read_text(encoding="utf-8")
        self.assertNotIn("toolbarMode", config_text)
        self.assertNotIn("menuItems", app_text)
        self.assertNotIn("menuItems", ui_text)

    def test_theme_fallback_supports_dark_light_and_unknown_context(self) -> None:
        dark_css = _theme_fallback_css("dark")
        light_css = _theme_fallback_css("light")
        default_css = _theme_fallback_css(None)
        self.assertIn("--lexi-page: #0B1220", dark_css)
        self.assertIn("color-scheme: dark", dark_css)
        self.assertIn("--lexi-page: #F1F5F9", light_css)
        self.assertIn("color-scheme: light", light_css)
        self.assertEqual(default_css, light_css)


if __name__ == "__main__":
    unittest.main()

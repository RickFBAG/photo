from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import base64
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote


BASE_LANDSCAPE: Tuple[int, int] = (800, 480)  # Inky Impression 7.3 base orientation


class DisplayRenderer:
    def __init__(self, config) -> None:
        self.config = config
        self._inky = None
        self._jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(self._base_dir(), "templates")),
            autoescape=select_autoescape(["html", "xml"]),
        )
        try:
            from inky.auto import auto

            self._inky = auto()
            self._inky.set_border(self._inky.WHITE)
        except Exception:
            self._inky = None

    def _canvas_size(self) -> Tuple[int, int]:
        orientation = (self.config.get("display.orientation", "portrait") or "portrait").lower()
        if orientation == "portrait":
            return (BASE_LANDSCAPE[1], BASE_LANDSCAPE[0])
        return BASE_LANDSCAPE

    def create_canvas(self) -> Image.Image:
        bg = self.config.get("theme.background", "#000000")
        size = self._canvas_size()
        img = Image.new("RGB", size, color=bg)
        return img

    def get_draw(self, image: Image.Image) -> ImageDraw.ImageDraw:
        return ImageDraw.Draw(image)

    def show(self, image: Image.Image) -> None:
        if self._inky is None:
            image.save("preview.png")
            return
        orientation = (self.config.get("display.orientation", "portrait") or "portrait").lower()
        if orientation == "portrait":
            # Rotate to match Inky's hardware expectation (800x480 landscape)
            image = image.rotate(90, expand=True)
        # Ensure final size matches display base landscape
        if image.size != BASE_LANDSCAPE:
            image = image.resize(BASE_LANDSCAPE)
        self._inky.set_image(image)
        self._inky.show()

    def load_font(self, size: int) -> ImageFont.FreeTypeFont:
        font_name = self.config.get("theme.font", "DejaVuSans.ttf")
        try:
            return ImageFont.truetype(font_name, size=size)
        except Exception:
            return ImageFont.load_default()

    def _base_dir(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    def render_html(self, context: dict) -> Image.Image:
        tpl_name = self.config.get("display.template", "display.html")
        template = self._jinja_env.get_template(tpl_name)
        # Build CSS variable overrides from theme
        theme = self.config.get("theme", {}) or {}
        css_vars = ":root{--bg:%s;--fg:%s;--muted:%s;--accent:%s;--accent2:%s;}" % (
            theme.get("background", "#0b1220"),
            theme.get("primary", "#F2F5F9"),
            theme.get("muted", "#7D8CA3"),
            theme.get("accent", "#3EC1D3"),
            theme.get("accent2", "#FF6B6B"),
        )
        html = template.render(**context)

        width, height = self._canvas_size()
        css_path = os.path.join(self._base_dir(), "templates", "styles.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        full_html = f"<style>{css}</style><style>{css_vars}</style>" + html

        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--hide-scrollbars")
            options.add_argument(f"--window-size={width},{height}")
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            try:
                data_url = "data:text/html;charset=utf-8," + quote(full_html)
                driver.get(data_url)
                png_bytes = driver.get_screenshot_as_png()
            finally:
                driver.quit()

            img = Image.open(BytesIO(png_bytes)).convert("RGB")
            return img
        except Exception as exc:  # Fallback: return an error PNG so preview isn't blank
            img = Image.new("RGB", (width, height), color="#1b1f2a")
            draw = ImageDraw.Draw(img)
            msg = f"HTML render failed: {type(exc).__name__}\n{str(exc)[:300]}\nInstall Chrome or switch display.mode to 'pil'"
            draw.text((16, 16), msg, fill="#FF6B6B")
            return img



import io
import base64

from typing import Any

from PIL import Image


class SVGExporter:
    def __init__(self, width: int, height: int, bg_color: tuple[int, int, int, int]):
        self.width = width
        self.height = height
        self.bg_color = bg_color

    def format_color_and_opacity(
        self, color: tuple[int, int, int, int]
    ) -> tuple[str, float]:
        r, g, b, a = color
        return f"rgb({r}, {g}, {b})", min(a / 255, 1)

    def save_embedded_svg(self, raster_img: Image.Image, path: str) -> None:
        buffer = io.BytesIO()
        raster_img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        svg = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">',
            f'<image href="data:image/png;base64,{b64}" width="{self.width}" height="{self.height}" />',
            "</svg>",
        ]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(svg))

    def save_svg(self, shape_metas: list[dict[str, Any]], path: str) -> None:
        lines: list[str] = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">',
        ]

        bg_fill, bg_opacity = self.format_color_and_opacity(self.bg_color)
        lines.append(
            f'<rect width="100%" height="100%" fill="{bg_fill}" fill-opacity="{bg_opacity:.3f}" />'
        )

        for ps in shape_metas:
            command = ps["command"]["name"]
            fill, opacity = self.format_color_and_opacity(ps["color"])
            attrs = [
                f'{k.replace("_", "-")}="{v}"'
                for k, v in ps["command"].items()
                if k != "name"
            ]
            attrs.append(f'fill="{fill}"')
            attrs.append(f'fill-opacity="{opacity:.3f}"')
            lines.append(f"<{command} " + " ".join(attrs) + " />")

        lines.append("</svg>")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

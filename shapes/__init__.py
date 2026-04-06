import os

from typing import Protocol

from PIL import Image, ImageDraw

from utils import average_color

__all__ = ["shape_drawers", "apply_shape"]

_Ink = float | tuple[int, ...] | str


class _ShapeDrawer(Protocol):
    def __call__(
        self,
        draw: ImageDraw.ImageDraw,
        color: _Ink | None = None,
    ) -> None: ...


class _ShapeFactory(Protocol):
    def __call__(
        self,
        width: int,
        height: int,
    ) -> _ShapeDrawer: ...


shape_drawers: dict[str, _ShapeFactory] = {}

for filename in os.listdir(os.path.dirname(__file__)):
    if filename.endswith(".py") and not filename.startswith("__"):
        module_name = filename[:-3]
        module = __import__(f"shapes.{module_name}", fromlist=[module_name])
        for attr in dir(module):
            if attr.startswith("random_"):
                globals()[attr] = getattr(module, attr)
                shape_drawers[attr[7:]] = getattr(module, attr)


def apply_shape(
    shape_drawer: _ShapeDrawer,
    target: Image.Image,
    canvas: Image.Image,
    alpha: float = 1.0,
):
    mask = Image.new("L", target.size, 0)
    mask_draw = ImageDraw.ImageDraw(mask)
    shape_drawer(mask_draw, color=255)
    color = average_color(target, alpha, mask)

    overlay = Image.new("RGBA", target.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.ImageDraw(overlay)
    shape_drawer(overlay_draw, color=color)
    canvas.alpha_composite(overlay)

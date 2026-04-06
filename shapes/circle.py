import random

from PIL import ImageDraw

__all__ = ["random_circle"]


def random_circle(width: int, height: int):
    x = random.randrange(0, width)
    y = random.randrange(0, height)
    r = random.randrange(0, max(width, height) // 2)

    def draw_circle(
        draw: ImageDraw.ImageDraw,
        color: float | tuple[int, ...] | str | None = None,
    ) -> None:
        draw.circle((x, y), r, fill=color)

    return draw_circle, [{"name": "circle", "cx": x, "cy": y, "r": r}]

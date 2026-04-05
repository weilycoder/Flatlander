import random

from PIL import Image, ImageDraw

from utils import average_color

__all__ = ["random_circle"]


def random_circle(
    target: Image.Image,
    canvas: Image.Image,
    alpha: float = 1.0,
):
    width, height = target.size
    x = random.randrange(0, width)
    y = random.randrange(0, height)
    r = random.randrange(0, max(width, height) // 2)

    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.circle((x, y), r, fill=255)
    color = average_color(target, alpha, mask)

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.circle((x, y), r, fill=color)
    canvas.alpha_composite(overlay)

    return "circle", (r, x, y), color

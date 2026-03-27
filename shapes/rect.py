import random

from PIL import Image, ImageDraw

from utils import average_color


__all__ = ["random_rect"]


def random_rect(
    target: Image.Image,
    canvas: Image.Image,
    alpha: float = 1.0,
):
    width, height = target.size
    x1, x2 = sorted(random.sample(range(width), k=2))
    y1, y2 = sorted(random.sample(range(height), k=2))

    sub_img = target.crop((x1, y1, x2, y2))
    color = average_color(sub_img, alpha)

    # Draw on a transparent layer, then composite so alpha blends with existing pixels.
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle((x1, y1, x2, y2), fill=color)
    canvas.alpha_composite(overlay)

    return "rect", (x1, y1, x2, y2), color

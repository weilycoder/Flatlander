import math
import random

from PIL import Image, ImageDraw

from utils import average_color


__all__ = ["random_rect", "random_rotated_rect"]


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


def random_rotated_rect(
    target: Image.Image,
    canvas: Image.Image,
    alpha: float = 1.0,
):
    width, height = target.size
    left, right = sorted(random.sample(range(width), k=2))
    top, bottom = sorted(random.sample(range(height), k=2))

    w, h = right - left, bottom - top
    cx, cy = (left + right) / 2, (top + bottom) / 2
    theta_max = math.atan2(*sorted((w, h)))

    theta = random.uniform(-theta_max, theta_max)
    cost, sint = math.cos(theta), math.sin(theta)

    ww = ((w / 2) * cost - (h / 2) * sint) / math.cos(2 * theta)
    hh = ((h / 2) * cost - (w / 2) * sint) / math.cos(2 * theta)

    points = [
        (cx + dx * cost - dy * sint, cy + dx * sint + dy * cost)
        for dx, dy in ((ww, hh), (ww, -hh), (-ww, -hh), (-ww, hh))
    ]

    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(points, fill=255)
    color = average_color(target, alpha, mask)

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.polygon(points, fill=color)
    canvas.alpha_composite(overlay)

    return "rotated_rect", tuple(points), color

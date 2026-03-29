import sys
import random
import argparse

from typing import cast

import numpy as np

from rich import print as rprint
from PIL import Image, ImageColor, UnidentifiedImageError

from utils import average_color, mode_color
from shape_factory import shape_list, apply_shape


def error_exit(message: str):
    rprint(f"[red]Error[/red]: {message}", file=sys.stderr)
    sys.exit(1)


class Flatlander:
    def __init__(
        self,
        target: Image.Image,
        bg_color: tuple[int, int, int, int] | str,
        shape_alpha: float = 1.0,
    ):
        self.shape_alpha = shape_alpha
        self.width, self.height = target.size
        self.target = target
        self.shapes = []
        self.raster_img = Image.new("RGBA", (width, height), bg_color)
        self.current_diff = self.diff(self.raster_img)

    def add_shape(self, trials: int = 4) -> None:
        best_image = None
        best_shape = None
        best_diff = self.current_diff
        for _ in range(trials):
            shape_type = random.choice(shape_list)
            temp_image = self.raster_img.copy()
            shape = apply_shape(shape_type, self.target, temp_image, self.shape_alpha)
            diff = self.diff(temp_image)
            if diff < best_diff:
                best_diff = diff
                best_image = temp_image
                best_shape = shape
        if best_image is not None:
            self.raster_img = best_image
            self.current_diff = best_diff
            self.shapes.append(best_shape)

    def diff(self, image: Image.Image, without_alpha: bool = True) -> float:
        target_array = np.array(self.target)
        temp_array = np.array(image)
        if without_alpha:
            target_array = target_array[:, :, :3]
            temp_array = temp_array[:, :, :3]
        return np.sqrt(np.mean((target_array - temp_array) ** 2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fit complex images with simple geometric shapes."
    )
    parser.add_argument("input_image", help="Path to the input image.")
    parser.add_argument("output_image", help="Path to save the output image.")
    parser.add_argument(
        "-a",
        "--alpha",
        type=float,
        default=1.0,
        help="Alpha value for shapes (0.0 to 1.0).",
    )
    parser.add_argument(
        "-t",
        "--trials",
        type=int,
        default=4,
        help="Number of random shapes to try for each addition.",
    )
    parser.add_argument(
        "-n",
        "--num-shapes",
        type=int,
        default=256,
        help="Number of shapes to fit.",
    )
    parser.add_argument(
        "-b",
        "--background-color",
        type=str,
        default="average",
        help="Background color (e.g., '#RRGGBBAA') or 'average' or 'mode'.",
    )
    args = parser.parse_args()

    try:
        img = Image.open(args.input_image).convert("RGBA")
        width, height = img.size
    except FileNotFoundError:
        error_exit(f"The file '{args.input_image}' was not found.")
    except UnidentifiedImageError:
        error_exit(f"The file '{args.input_image}' is not a valid image file.")

    if args.background_color == "average":
        bg_color = average_color(img)
    elif args.background_color == "mode":
        bg_color = mode_color(img)
    else:
        try:
            bg_color = cast(
                tuple[int, int, int, int],
                ImageColor.getcolor(args.background_color, "RGBA"),
            )
        except ValueError:
            error_exit(f"'{args.background_color}' is not a valid color string.")

    flatlander = Flatlander(img, bg_color, args.alpha)
    while len(flatlander.shapes) < args.num_shapes:
        flatlander.add_shape(args.trials)
        rprint(
            f"Added shape {len(flatlander.shapes)}/{args.num_shapes}, "
            f"current diff: {flatlander.current_diff:.2f}"
        )
    flatlander.raster_img.save(args.output_image)

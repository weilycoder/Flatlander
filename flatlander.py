import sys
import random
import argparse

from typing import cast, Any
from svg_export import SVGExporter

from rich import print as rprint
from PIL import Image, ImageColor, UnidentifiedImageError

from utils import average_color, mode_color, RMSE
from shapes import shape_drawers, apply_shape


def error_exit(message: str):
    rprint(f"[red]Error[/red]: {message}", file=sys.stderr)
    sys.exit(1)


class Flatlander:
    def __init__(
        self,
        target: Image.Image,
        bg_color: tuple[int, int, int, int],
        shape_alpha: float = 1.0,
        shape_list: list[str] | None = None,
    ):
        self.shapes = 0
        self.shape_alpha = shape_alpha
        self.width, self.height = target.size
        self.target = target
        self.bg_color = bg_color
        self.raster_img = Image.new("RGBA", (self.width, self.height), bg_color)
        self.current_diff = self.diff(self.raster_img)
        self.shape_metas: list[dict[str, Any]] = []
        self.shape_list = (
            list(shape_drawers.keys()) if shape_list is None else shape_list
        )

    def add_shape(self, trials: int = 4) -> None:
        best_image = None
        best_diff = self.current_diff
        best_meta: list[dict[str, Any]] = []
        for _ in range(trials):
            shape_type = random.choice(self.shape_list)
            shape_drawer, cmds = shape_drawers[shape_type](self.width, self.height)
            temp_image = self.raster_img.copy()
            color = apply_shape(shape_drawer, self.target, temp_image, self.shape_alpha)
            diff = self.diff(temp_image)
            if diff < best_diff:
                best_diff = diff
                best_image = temp_image
                best_meta = [{"command": cmd, "color": color} for cmd in cmds]
        if best_image is not None:
            self.shapes += 1
            self.raster_img = best_image
            self.current_diff = best_diff
            self.shape_metas.extend(best_meta)

    def diff(self, image: Image.Image) -> float:
        return RMSE(self.target, image)

    def save_svg(self, path: str) -> None:
        svg_exporter = SVGExporter(self.width, self.height, self.bg_color)
        svg_exporter.save_svg(self.shape_metas, path)

    def save_png(self, path: str) -> None:
        self.raster_img.save(path)

    def save(self, path: str) -> None:
        if path.lower().endswith(".svg"):
            self.save_svg(path)
        else:
            self.save_png(path)


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
        default=16,
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
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )
    args = parser.parse_args()
    random.seed(args.seed)

    try:
        img = Image.open(args.input_image).convert("RGBA")
        width, height = img.size
    except FileNotFoundError:
        error_exit(f"The file '{args.input_image}' was not found.")
    except UnidentifiedImageError:
        error_exit(f"The file '{args.input_image}' is not a valid image file.")

    bg_color = cast(
        tuple[int, int, int, int], (0, 0, 0, 255)
    )  # default to opaque black
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
    while flatlander.shapes < args.num_shapes:
        flatlander.add_shape(args.trials)
        rprint(
            f"Added shape {flatlander.shapes}/{args.num_shapes}, "
            f"current diff: {flatlander.current_diff:.2f}"
        )
    flatlander.save(args.output_image)

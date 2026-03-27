from PIL import Image

import shapes


shape_list = tuple(shape[7:] for shape in dir(shapes) if shape.startswith("random_"))


def apply_shape(
    shape_name: str,
    target: Image.Image,
    canvas: Image.Image,
    alpha: float = 1.0,
):
    shape_func = getattr(shapes, f"random_{shape_name}")
    return shape_func(target, canvas, alpha)

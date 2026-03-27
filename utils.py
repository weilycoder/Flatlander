import numpy as np

from PIL import Image


def average_color(image: Image.Image, alpha: float = 1.0) -> tuple[int, int, int, int]:
    np_image = np.array(image)
    avg_color = np.round(np.mean(np_image, axis=(0, 1)))
    r, g, b, a = map(int, avg_color)
    return r, g, b, int(a * alpha)


def mode_color(image: Image.Image, alpha: float = 1.0) -> tuple[int, int, int, int]:
    np_image = np.array(image)
    pixels = np_image.reshape(-1, np_image.shape[2])
    unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
    mode_color = unique_colors[np.argmax(counts)]
    r, g, b, a = map(int, mode_color)
    return r, g, b, int(a * alpha)

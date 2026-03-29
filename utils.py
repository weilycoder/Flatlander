import numpy as np

from PIL import Image


def average_color(
    image: Image.Image,
    alpha: float = 1.0,
    mask: Image.Image | None = None,
) -> tuple[int, int, int, int]:
    np_image = np.array(image).astype(float)
    mask_array = np.array(mask).astype(float) / 255.0 if mask else None
    if mask_array is None or np.sum(mask_array) <= 0:
        avg_color = np.round(np.mean(np_image, axis=(0, 1)))
    else:
        weights = mask_array[..., None]
        weighted_sum = np.sum(np_image * weights, axis=(0, 1))
        avg_color = np.round(weighted_sum / np.sum(mask_array))
    r, g, b, a = map(int, avg_color)
    return r, g, b, int(a * alpha)


def mode_color(
    image: Image.Image,
    alpha: float = 1.0,
) -> tuple[int, int, int, int]:
    np_image = np.array(image).astype(float)
    pixels = np_image.reshape(-1, np_image.shape[2])
    unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
    mode_color = unique_colors[np.argmax(counts)]
    r, g, b, a = map(int, mode_color)
    return r, g, b, int(a * alpha)


def RMSE(
    target: Image.Image,
    current: Image.Image,
    *,
    mask: Image.Image | None = None,
    without_alpha: bool = True,
) -> float:
    target_array = np.array(target).astype(float)
    current_array = np.array(current).astype(float)
    if without_alpha:
        current_array = current_array[:, :, :3]
        target_array = target_array[:, :, :3]
    mask_array = np.array(mask).astype(float) / 255.0 if mask else None
    if mask_array is None or np.sum(mask_array) <= 0:
        return np.sqrt(np.mean((current_array - target_array) ** 2))
    weights = mask_array[..., None]
    weighted_diff = weights * (current_array - target_array) ** 2
    return np.sqrt(np.mean(weighted_diff))

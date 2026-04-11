import pkgutil
import importlib
import logging

from typing import cast, Any, Protocol, Sequence

from PIL import ImageDraw

__all__ = ["ShapeRegistry", "registry"]

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
    ) -> tuple[_ShapeDrawer, list[dict[str, Any]]]: ...


class ShapeRegistry:
    """Encapsulates discovery and access to shape factory functions.

    Uses pkgutil to discover modules under the shapes package and imports
    only modules that define callables starting with `random_`.
    """

    def __init__(self, package_name: str, package_path: Sequence[str]) -> None:
        self.__package_name = package_name
        # store as list to keep compatibility with pkgutil.iter_modules
        self.__package_path = list(package_path)
        self.__logger = logging.getLogger(f"{__name__}.registry")
        self.__shape_drawers: dict[str, _ShapeFactory] = {}

    def __discover(self) -> None:
        for _finder, name, ispkg in pkgutil.iter_modules(self.__package_path):
            if name.startswith("_"):
                continue
            try:
                mod = importlib.import_module(f"{self.__package_name}.{name}")
            except Exception as exc:  # pragma: no cover - best-effort import
                self.__logger.warning("Failed to import shape module %s: %s", name, exc)
                continue
            for attr in dir(mod):
                if attr.startswith("random_"):
                    func = getattr(mod, attr)
                    if callable(func):
                        # register under the short name (after 'random_')
                        self.__shape_drawers[attr[7:]] = cast(_ShapeFactory, func)

    @property
    def shape_drawers(self) -> dict[str, _ShapeFactory]:
        if not self.__shape_drawers:
            self.__discover()
        return self.__shape_drawers


# default registry for the package
registry = ShapeRegistry(__name__, __path__)

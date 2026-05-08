"""Core package exports for the Axelrod cultural dissemination project."""

__all__ = ["AxelrodModel", "save_demo_outputs"]


def __getattr__(name):
    if name in __all__:
        from .model import AxelrodModel, save_demo_outputs

        exports = {
            "AxelrodModel": AxelrodModel,
            "save_demo_outputs": save_demo_outputs,
        }
        return exports[name]
    raise AttributeError(f"module 'axelrod' has no attribute {name!r}")

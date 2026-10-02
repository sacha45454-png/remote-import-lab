"""
Пакет mypackage — учебный пример для ЛР по удалённому импорту.
"""

__version__ = "1.0.0"
__author__ = "Кожевников Александр"
__all__ = ["package_info", "hello"]


def package_info():
    """Краткая информация о пакете."""
    return f"mypackage v{__version__} by {__author__}"


from .mymodule import hello   # noqa: E402
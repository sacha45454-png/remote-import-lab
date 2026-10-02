import re
import sys
from urllib.request import urlopen
from urllib.error import URLError
from importlib.abc import PathEntryFinder
from importlib.util import spec_from_loader


class URLLoader:
    def create_module(self, target):
        return None

    def exec_module(self, module):
        origin = module.__spec__.origin
        with urlopen(origin) as page:
            source = page.read()
        code = compile(source, origin, mode="exec")
        exec(code, module.__dict__)


class URLFinder(PathEntryFinder):
    def __init__(self, url, available):
        self.url = url
        self.available = available

    def find_spec(self, name, target=None):
        if name not in self.available:
            return None
        kind = self.available[name]
        if kind == "module":
            origin = f"{self.url}/{name}.py"
            loader = URLLoader()
            return spec_from_loader(name, loader, origin=origin)
        elif kind == "package":
            origin = f"{self.url}/{name}/__init__.py"
            loader = URLLoader()
            spec = spec_from_loader(name, loader, origin=origin)
            spec.submodule_search_locations = [f"{self.url}/{name}"]
            return spec
        return None


def url_hook(some_str):
    if not some_str.startswith(("http", "https")):
        raise ImportError
    try:
        with urlopen(some_str, timeout=5) as page:
            data = page.read().decode("utf-8")
    except URLError as e:
        raise ImportError(f"Не удалось подключиться к {some_str}: {e}")

    filenames = re.findall(r'href="([^"]+)"', data)
    available = {}
    for fname in filenames:
        if fname.startswith("?") or fname.startswith("/"):
            continue
        if fname.endswith(".py"):
            available[fname[:-3]] = "module"
        elif fname.endswith("/"):
            available[fname[:-1]] = "package"
    return URLFinder(some_str, available)


sys.path_hooks.append(url_hook)
print("Path hooks успешно добавлены!")

# --- Блок для автоматического теста ---
sys.path.append("http://localhost:8000")

try:
    print("Пытаемся импортировать mypackage...")
    import mypackage

    print("\n--- Результат ---")
    print("Информация о пакете:", mypackage.package_info())

    from mypackage import mymodule

    mymodule.myfoo()

    from mypackage import utils

    print("Реверс строки 'abc':", utils.reverse("abc"))

except Exception as e:
    print(f"\n[ОШИБКА] Не удалось импортировать: {e}")
    print("Убедитесь, что HTTP-сервер запущен!")
    print("Убедитесь, что HTTP-сервер запущен!")
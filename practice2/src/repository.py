"""Источники npm-зависимостей без сторонних библиотек."""

import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class TestRepository:
    """Тестовые зависимости из локального JSON."""

    def __init__(self, path):
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(f"ошибка чтения тестового репозитория: {error}")
        if not isinstance(data, dict):
            raise ValueError("граф должен быть JSON-объектом")
        for name, deps in data.items():
            if not re.fullmatch(r"[A-Z]", name):
                raise ValueError("имена тестовых пакетов: A-Z")
            if not isinstance(deps, list) or any(
                not isinstance(item, str)
                or not re.fullmatch(r"[A-Z]", item)
                for item in deps
            ):
                raise ValueError("зависимости должны быть списками A-Z")
        self.data = data

    def dependencies(self, package):
        """Вернуть прямые зависимости тестового пакета."""
        if package not in self.data:
            raise ValueError(f"пакет {package} не найден в графе")
        return list(dict.fromkeys(self.data[package]))


class NpmRepository:
    """Прямые зависимости опубликованной latest-версии npm-пакета."""

    def __init__(self, url):
        self.url = url.rstrip("/")
        self.cache = {}

    def dependencies(self, package):
        """Прочитать dependencies через npm registry HTTPS API."""
        if package in self.cache:
            return self.cache[package]
        address = f"{self.url}/{quote(package, safe='')}/latest"
        request = Request(
            address, headers={"Accept": "application/json"}
        )
        try:
            with urlopen(request, timeout=15) as response:
                data = json.load(response)
        except (HTTPError, URLError, OSError, ValueError) as error:
            raise ValueError(f"ошибка npm API для {package}: {error}")
        deps = data.get("dependencies", {})
        if not isinstance(deps, dict):
            raise ValueError("неверный формат поля dependencies")
        if any(not isinstance(key, str) for key in deps):
            raise ValueError("некорректное имя зависимости")
        self.cache[package] = sorted(deps)
        return self.cache[package]


def create_source(repository, test_mode):
    """Выбрать тестовый JSON или официальный npm registry."""
    if test_mode:
        return TestRepository(repository)
    return NpmRepository(repository)

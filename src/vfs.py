"""Загрузка дерева виртуальной файловой системы из JSON."""

import base64
import binascii
import json
from pathlib import Path


class VFSError(ValueError):
    """Ошибка чтения либо проверки формата VFS."""


def validate_node(node):
    """Проверить узел VFS и декодировать содержимое файлов."""
    if not isinstance(node, dict):
        raise VFSError("узел должен быть объектом JSON")
    kind = node.get("type")
    if kind == "dir":
        children = node.get("children")
        if not isinstance(children, dict):
            raise VFSError("у каталога отсутствует children")
        return {
            "type": "dir",
            "children": {
                name: validate_node(child)
                for name, child in children.items()
                if valid_name(name)
            },
        }
    if kind == "file":
        encoded = node.get("content")
        if not isinstance(encoded, str):
            raise VFSError("поле content должно быть строкой base64")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as error:
            raise VFSError("неверные данные base64") from error
        return {"type": "file", "content": content}
    raise VFSError("неизвестный тип узла VFS")


def valid_name(name):
    """Проверить безопасное имя элемента дерева."""
    if not isinstance(name, str) or name in ("", ".", ".."):
        raise VFSError("неверное имя элемента VFS")
    if "/" in name or "\\" in name:
        raise VFSError("имя содержит разделитель пути")
    return True


def load_vfs(path):
    """Прочитать JSON и создать независимое дерево в памяти."""
    if path is None:
        return {"type": "dir", "children": {}}
    try:
        raw = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise VFSError(f"не удалось загрузить VFS: {error}") from error
    tree = validate_node(data)
    if tree["type"] != "dir":
        raise VFSError("корень VFS должен быть каталогом")
    return tree


def count_nodes(node):
    """Подсчитать количество элементов в дереве VFS."""
    if node["type"] == "file":
        return 1
    return 1 + sum(count_nodes(child) for child in node["children"].values())

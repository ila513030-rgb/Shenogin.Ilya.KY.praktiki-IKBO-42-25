"""Проверка параметров командной строки анализатора."""

import argparse
from pathlib import Path
from urllib.parse import urlparse


class ConfigError(ValueError):
    """Ошибка пользовательских параметров."""


def parser_for_stage(stage):
    """Создать парсер аргументов с настройками варианта 30."""
    parser = argparse.ArgumentParser(
        description="Анализ графа npm-зависимостей, вариант 30"
    )
    parser.add_argument("--package", required=True, help="Имя пакета")
    parser.add_argument(
        "--repository", required=True, help="URL npm или JSON-файл"
    )
    parser.add_argument(
        "--test-mode", action="store_true", help="Тестовый граф"
    )
    parser.add_argument(
        "--output", default="graph.png", help="Имя будущего изображения"
    )
    parser.add_argument(
        "--filter", default="", help="Исключаемая подстрока"
    )
    return parser


def validate_config(args):
    """Проверить все параметры и возвратить настройки."""
    if not args.package.strip():
        raise ConfigError("имя пакета не может быть пустым")
    if not args.output.lower().endswith(".png"):
        raise ConfigError("имя изображения должно оканчиваться на .png")
    if args.test_mode:
        if len(args.package) != 1 or not args.package.isupper():
            raise ConfigError("тестовый пакет должен быть буквой A-Z")
        if not ("A" <= args.package <= "Z"):
            raise ConfigError("тестовый пакет должен быть буквой A-Z")
        path = Path(args.repository)
        if not path.is_file():
            raise ConfigError("тестовый JSON-файл не найден")
    else:
        parsed = urlparse(args.repository)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ConfigError("нужен корректный HTTPS URL репозитория")
        if parsed.netloc.lower() != "registry.npmjs.org":
            raise ConfigError("поддерживается registry.npmjs.org")
        if not args.package.strip() or any(
            char.isspace() for char in args.package
        ):
            raise ConfigError("имя npm-пакета не должно содержать пробелы")
    return args

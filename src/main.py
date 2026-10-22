"""Консольный эмулятор: REPL и выполнение стартового скрипта."""

import argparse
import getpass
import os
import shlex
import socket
from pathlib import Path

from src.vfs import VFSError, count_nodes, load_vfs


def parse_command(line):
    """Разбирать кавычки и раскрывать переменные окружения."""
    return shlex.split(os.path.expandvars(line))


def execute_command(parts):
    """Выполнять команды-заглушки и сообщать об ошибках."""
    if not parts:
        return True
    name, *args = parts
    if name not in ("ls", "cd", "exit"):
        print(f"Ошибка: неизвестная команда {name}")
        return True
    if name == "exit":
        if args:
            print("Ошибка: exit не принимает аргументов")
            return True
        return False
    if name == "cd" and len(args) > 1:
        print("Ошибка: cd принимает не более одного пути")
        return True
    if name == "ls" and any(arg.startswith("-") for arg in args):
        print("Ошибка: ключи ls пока не поддерживаются")
        return True
    print(f"{name}: аргументы = {args}")
    return True


def run_line(line):
    """Обработать одну строку, вернув статус продолжения."""
    try:
        return execute_command(parse_command(line))
    except ValueError as error:
        print(f"Ошибка разбора: {error}")
        return True


def prompt_text():
    """Сформировать приглашение из данных реальной ОС."""
    return f"{getpass.getuser()}@{socket.gethostname()}:~$ "


def run_script(path):
    """Выполнить команды из скрипта с поддержкой комментариев."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        print(f"Ошибка чтения скрипта: {error}")
        return False
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        print(prompt_text() + line)
        if not run_line(line):
            return False
    return True


def main(argv=None):
    """Прочитать настройки, запустить скрипт и интерактивный цикл."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--vfs", help="путь к JSON-файлу VFS")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    args = parser.parse_args(argv)
    print(f"Конфигурация: vfs={args.vfs!r}, script={args.script!r}")
    try:
        vfs = load_vfs(args.vfs)
    except VFSError as error:
        print(f"Ошибка загрузки VFS: {error}")
        return
    print(f"VFS загружена в память, элементов: {count_nodes(vfs)}")
    if args.script and not run_script(args.script):
        return
    while True:
        try:
            if not run_line(input(prompt_text())):
                break
        except (EOFError, KeyboardInterrupt):
            print()
            break


if __name__ == "__main__":
    main()

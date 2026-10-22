"""Консольный эмулятор UNIX-подобной оболочки, этап 1."""

import getpass
import os
import shlex
import socket


def parse_command(line):
    """Разобрать строку с подстановкой переменных окружения."""
    return shlex.split(os.path.expandvars(line))


def execute_command(parts):
    """Выполнить команду-заглушку или завершить сеанс."""
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


def main():
    """Запустить интерактивный диалог."""
    prompt = f"{getpass.getuser()}@{socket.gethostname()}:~$ "
    while True:
        try:
            line = input(prompt)
            if not execute_command(parse_command(line)):
                break
        except (EOFError, KeyboardInterrupt):
            print()
            break
        except ValueError as error:
            print(f"Ошибка разбора: {error}")


if __name__ == "__main__":
    main()

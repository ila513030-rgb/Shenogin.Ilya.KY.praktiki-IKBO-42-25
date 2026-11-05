"""Графический эмулятор командной оболочки. Этапы 1–3."""

import argparse
import getpass
import os
import shlex
import socket
import tkinter as tk
from pathlib import Path

from src.vfs import VFSError, count_nodes, load_vfs


def parse_command(line):
    """Разобрать команду и раскрыть переменные окружения."""
    return shlex.split(os.path.expandvars(line))


def execute_command(parts):
    """Обработать команду и вернуть результат."""
    if not parts:
        return "", False
    command, *args = parts
    if command == "exit":
        if args:
            return "Ошибка: exit не принимает аргументов", False
        return "", True
    if command not in ("ls", "cd"):
        return f"Ошибка: неизвестная команда {command}", False
    if command == "cd" and len(args) > 1:
        return "Ошибка: cd принимает не более одного пути", False
    if command == "ls" and any(arg.startswith("-") for arg in args):
        return "Ошибка: ключи ls пока не поддерживаются", False
    return f"{command}: аргументы = {args}", False


class ShellWindow:
    """Окно графического эмулятора."""

    def __init__(self, root, args):
        """Создать интерфейс, загрузить VFS и выполнить стартовый скрипт."""
        self.root = root
        self.configure_window()
        self.create_output()
        self.create_input()
        self.write(
            f"Конфигурация: vfs={args.vfs!r}, "
            f"script={args.script!r}"
        )
        if not self.initialize_vfs(args.vfs):
            return
        if args.script:
            self.run_script(args.script)

    def configure_window(self):
        """Настроить заголовок, размеры и фон окна."""
        self.root.title(
            f"Эмулятор - [{getpass.getuser()}@"
            f"{socket.gethostname()}]"
        )
        self.root.geometry("850x550")
        self.root.configure(bg="#111827")

    def create_output(self):
        """Создать поле истории команд и результатов."""
        self.output = tk.Text(
            self.root,
            bg="#050A12",
            fg="#E5E7EB",
            insertbackground="white",
            font=("Consolas", 12),
            state="disabled",
            wrap="word"
        )
        self.output.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(12, 6)
        )

    def create_input(self):
        """Создать однострочное поле ввода."""
        self.entry = tk.Entry(
            self.root,
            bg="#1F2937",
            fg="white",
            insertbackground="white",
            font=("Consolas", 12)
        )
        self.entry.pack(
            fill="x",
            padx=12,
            pady=(6, 12),
            ipady=8
        )
        self.entry.bind("<Return>", self.handle_command)
        self.entry.focus_set()

    def initialize_vfs(self, path):
        """Загрузить VFS; заблокировать ввод в случае ошибки."""
        try:
            self.vfs = load_vfs(path)
        except VFSError as error:
            self.write(f"Ошибка загрузки VFS: {error}")
            self.entry.configure(state="disabled")
            return False
        self.write(
            "VFS загружена в память, элементов: "
            f"{count_nodes(self.vfs)}"
        )
        self.write("Введите команду.\n")
        return True

    def write(self, message):
        """Добавить строку в область вывода."""
        self.output.config(state="normal")
        self.output.insert("end", message + "\n")
        self.output.config(state="disabled")
        self.output.see("end")

    def process_line(self, line):
        """Разобрать и выполнить введённую команду."""
        self.write(f"> {line}")
        try:
            parts = parse_command(line)
            result, should_exit = execute_command(parts)
        except ValueError as error:
            self.write(f"Ошибка разбора: {error}")
            return False
        if result:
            self.write(result)
        return should_exit

    def handle_command(self, event=None):
        """Обработать нажатие Enter."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        if self.process_line(line):
            self.root.destroy()

    def run_script(self, path):
        """Выполнить команды из стартового файла."""
        try:
            lines = Path(path).read_text(
                encoding="utf-8"
            ).splitlines()
        except (OSError, UnicodeError) as error:
            self.write(f"Ошибка чтения скрипта: {error}")
            return
        for line in lines:
            if not line.strip():
                continue
            if line.lstrip().startswith("#"):
                continue
            if self.process_line(line):
                self.root.destroy()
                return


def main(argv=None):
    """Запустить графический эмулятор."""
    parser = argparse.ArgumentParser(
        description="Графический эмулятор оболочки"
    )
    parser.add_argument("--vfs")
    parser.add_argument("--script")
    args = parser.parse_args(argv)
    root = tk.Tk()
    ShellWindow(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()

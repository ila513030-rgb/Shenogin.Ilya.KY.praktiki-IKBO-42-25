# Эмулятор UNIX-подобной оболочки — вариант №30

**Дисциплина:** Конфигурационное управление  
**Выполнил:** Шеногин Илья, ИКБО-42-25  
**Готовы:** этапы 1, 2, 3. Этапы 4 и 5 не реализуются.

## Общее описание

Консольный эмулятор написан на Python 3 без внешних зависимостей.
Он поддерживает цикл ввода команд, раскрытие переменных окружения ОС,
выполнение стартовых скриптов и загрузку виртуальной файловой системы
(VFS) из JSON в оперативную память.

## Этап 1. REPL

- Приглашение к вводу формируется из реальных имени пользователя и имени узла:
  `username@hostname:~$`.
- Парсер использует `shlex.split` и `os.path.expandvars`;
  поддерживает аргументы в кавычках и переменные `$HOME`.
- `ls` и `cd` пока **заглушки**: отображают полученные аргументы.
- `exit` закрывает эмулятор.
- Неизвестные команды и неверные аргументы вызывают сообщение об ошибке.

## Этап 2. Конфигурация

Поддержаны параметры:

- `--vfs ПУТЬ` — JSON-файл виртуальной файловой системы;
- `--script ПУТЬ` — стартовый скрипт с командами.

При запуске параметры выводятся для отладки. Стартовый скрипт
исполняется последовательно, выводятся команды и ответы,
пустые строки и комментарии с `#` пропускаются.
Ошибки отдельных команд отображаются, выполнение продолжается.
Ошибка чтения файла скрипта также отображается.

## Этап 3. VFS

Структура VFS загружается **из JSON-файла в оперативную память**.
Данные на диске не распаковываются и не модифицируются.

Формат:

```json
{
  "type": "dir",
  "children": {
    "hello.txt": {
      "type": "file",
      "content": "SGVsbG8="
    }
  }
}
```

`dir` — каталог с объектом `children`, `file` — файл с содержимым
в base64. Строка `SGVsbG8=` означает текст `Hello`.
Поддержана вложенность. При загрузке проверяются имена элементов,
типы узлов, правильность base64 и формат JSON. При отсутствующем
или неверном JSON-файле выводится ошибка. Без `--vfs`
создаётся пустая VFS в памяти.

Подготовлены разные примеры:

- `tests/vfs/minimal.json` — пустая VFS;
- `tests/vfs/multiple.json` — несколько файлов и каталогов;
- `tests/vfs/nested.json` — не менее трёх уровней вложенности;
- `tests/vfs/invalid.json` — пример ошибочного JSON.

**Важно:** на первых трёх этапах `ls` и `cd` остаются заглушками.
Чтение каталогов и изменение текущего каталога относятся к этапу 4.

## Структура

```text
src/
  __init__.py
  main.py
  vfs.py
tests/
  test_shell.py
  test_vfs.py
  vfs/
  startup_all.txt
  startup_basic.txt
  startup_invalid.txt
  check_default.sh
  check_script.sh
  check_vfs.sh
  check_errors.sh
run.sh
run.bat
.gitignore
README.md
```

## Запуск

Из корня проекта:

```bash
python3 -m src.main
python3 -m src.main --script tests/startup_all.txt
python3 -m src.main --vfs tests/vfs/multiple.json
python3 -m src.main --vfs tests/vfs/nested.json --script tests/startup_all.txt
```

Linux: `sh run.sh --vfs tests/vfs/minimal.json`  
Windows: `run.bat --vfs tests/vfs/minimal.json`

## Проверка

```bash
python3 -m unittest discover -s tests -v
sh tests/check_default.sh
sh tests/check_script.sh
sh tests/check_vfs.sh
sh tests/check_errors.sh
```

Скрипты проверяют запуск без параметров, параметры `--vfs` и
`--script`, варианты VFS, команды-заглушки и ошибки.

## Пример диалога

```text
Конфигурация: vfs=None, script=None
VFS загружена в память, элементов: 1
user@host:~$ ls $HOME
ls: аргументы = ['/home/user']
user@host:~$ cd docs
cd: аргументы = ['docs']
user@host:~$ unknown
Ошибка: неизвестная команда unknown
user@host:~$ exit
```

Здесь `user`, `host` и `/home/user` — примеры: реальные значения
зависят от среды запуска.

## История этапов

Этапы сохранялись последовательными коммитами с префиксами:
`feat(stage1)`, `feat(stage2)`, `feat(stage3)` и `test(stage3)`.

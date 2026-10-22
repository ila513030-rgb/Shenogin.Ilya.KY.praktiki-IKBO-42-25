"""Тесты прототипа REPL."""

import os
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from src.main import execute_command, parse_command


class ShellTests(unittest.TestCase):
    def test_expand_environment(self):
        with patch.dict(os.environ, {"DEMO_PATH": "/tmp/example"}):
            self.assertEqual(parse_command("ls $DEMO_PATH"), [
                "ls", "/tmp/example"
            ])

    def test_placeholder_ls(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertTrue(execute_command(["ls", "docs"]))
        self.assertIn("['docs']", output.getvalue())

    def test_exit(self):
        self.assertFalse(execute_command(["exit"]))

    def test_unknown(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertTrue(execute_command(["missing"]))
        self.assertIn("неизвестная команда", output.getvalue())

    def test_wrong_cd_arguments(self):
        output = StringIO()
        with redirect_stdout(output):
            self.assertTrue(execute_command(["cd", "a", "b"]))
        self.assertIn("Ошибка", output.getvalue())


if __name__ == "__main__":
    unittest.main()

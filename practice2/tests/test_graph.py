"""Проверки этапов 1–3 средствами unittest."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from practice2.src.config import ConfigError, parser_for_stage
from practice2.src.config import validate_config
from practice2.src.graph import analyze
from practice2.src.repository import NpmRepository, TestRepository


DATA = Path(__file__).parent / "data"


class GraphTests(unittest.TestCase):
    """Тестирование графа и параметров."""

    def source(self, filename):
        """Создать тестовый источник из файла."""
        return TestRepository(DATA / filename)

    def test_transitive_dfs(self):
        graph = analyze(self.source("chain.json"), "A")
        self.assertEqual(set(graph), {"A", "B", "C", "D"})
        self.assertEqual(graph["A"], ["B", "C"])

    def test_cycle(self):
        graph = analyze(self.source("cycle.json"), "A")
        self.assertEqual(set(graph), {"A", "B", "C"})
        self.assertEqual(graph["C"], ["A"])

    def test_filter(self):
        graph = analyze(self.source("filter.json"), "A", "B")
        self.assertEqual(set(graph), {"A", "C", "D"})
        self.assertEqual(graph["A"], ["C"])

    def test_empty(self):
        self.assertEqual(analyze(self.source("empty.json"), "A"),
                         {"A": []})

    def test_missing_dependency(self):
        with self.assertRaisesRegex(ValueError, "не найден"):
            analyze(self.source("invalid.json"), "A")

    def test_filter_root(self):
        with self.assertRaises(ValueError):
            analyze(self.source("chain.json"), "A", "A")

    def test_cli_error(self):
        parser = parser_for_stage(3)
        options = parser.parse_args([
            "--package", "A", "--repository",
            str(DATA / "chain.json"), "--test-mode",
            "--output", "bad.txt"
        ])
        with self.assertRaises(ConfigError):
            validate_config(options)

    def test_json_structure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"A": ["b"]}', encoding="utf-8")
            with self.assertRaises(ValueError):
                TestRepository(path)

    def test_npm_mock(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self, *args):
                return b'{"dependencies":{"left-pad":"^1.0.0"}}'

        with patch("practice2.src.repository.urlopen",
                   return_value=FakeResponse()) as mocked:
            source = NpmRepository("https://registry.npmjs.org")
            self.assertEqual(source.dependencies("example"),
                             ["left-pad"])
            self.assertEqual(source.dependencies("example"),
                             ["left-pad"])
            self.assertEqual(mocked.call_count, 1)


if __name__ == "__main__":
    unittest.main()

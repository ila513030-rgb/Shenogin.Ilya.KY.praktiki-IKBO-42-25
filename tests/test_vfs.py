"""Тесты загрузки VFS из JSON."""

import tempfile
import unittest
from pathlib import Path

from src.vfs import VFSError, count_nodes, load_vfs


class VFSTests(unittest.TestCase):
    def test_default_is_empty(self):
        self.assertEqual(count_nodes(load_vfs(None)), 1)

    def test_minimal(self):
        self.assertEqual(count_nodes(load_vfs("tests/vfs/minimal.json")), 1)

    def test_multiple(self):
        tree = load_vfs("tests/vfs/multiple.json")
        self.assertEqual(tree["children"]["readme.txt"]["content"],
                         b"Hello")

    def test_nested(self):
        self.assertEqual(count_nodes(load_vfs("tests/vfs/nested.json")),
                         5)

    def test_invalid_json(self):
        with self.assertRaises(VFSError):
            load_vfs("tests/vfs/invalid.json")

    def test_missing_file(self):
        with self.assertRaises(VFSError):
            load_vfs("tests/vfs/missing.json")

    def test_invalid_base64(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "broken.json"
            file.write_text(
                '{"type":"dir","children":{"a":'
                '{"type":"file","content":"???"}}}',
                encoding="utf-8",
            )
            with self.assertRaises(VFSError):
                load_vfs(file)


if __name__ == "__main__":
    unittest.main()

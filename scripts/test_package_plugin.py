import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


class PackagePluginTest(unittest.TestCase):
    def test_archives_exclude_cache_files(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            contents = {
                "plugin.json": "{}",
                ".claude-plugin/plugin.json": "{}",
                "skills/example/SKILL.md": "skill content",
                "skills/example/scripts/run.py": "print('hello')",
                "skills/.DS_Store": "cache",
                "skills/example/.DS_Store": "cache",
                "skills/__pycache__/cached.pyc": "cache",
                "skills/example/scripts/__pycache__/nested/cached.pyc": "cache",
            }
            for name, content in contents.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)

            for mode, manifest in (
                ("codex", "plugin.json"),
                ("claude", ".claude-plugin/plugin.json"),
            ):
                with self.subTest(mode=mode):
                    output = root / f"{mode}.zip"
                    subprocess.run(
                        [sys.executable, str(Path(__file__).with_name("package_plugin.py")),
                         str(root), mode, str(output)],
                        check=True, capture_output=True,
                    )
                    expected = {manifest, "skills/example/SKILL.md", "skills/example/scripts/run.py"}
                    with ZipFile(output) as archive:
                        self.assertEqual(set(archive.namelist()), expected)
                        for name in expected:
                            self.assertEqual(archive.read(name).decode(), contents[name])

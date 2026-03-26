from __future__ import annotations

import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from template_utils import copy_rendered_tree  # noqa: E402


def owner_execute_enabled(path: Path) -> bool:
    return bool(path.stat().st_mode & stat.S_IXUSR)


class RalphInstallModeTests(unittest.TestCase):
    def test_copy_rendered_tree_preserves_executable_mode_for_rendered_text(self) -> None:
        with tempfile.TemporaryDirectory(prefix="copy-rendered-tree-") as temp_dir:
            temp_root = Path(temp_dir)
            source_root = temp_root / "source"
            destination_root = temp_root / "destination"
            source_root.mkdir(parents=True, exist_ok=True)

            source_script = source_root / "run-loop.sh"
            source_script.write_text("#!/bin/sh\necho '{{PROJECT_NAME}}'\n", encoding="utf-8")
            source_script.chmod(0o755)

            copy_rendered_tree(
                source_root,
                destination_root,
                {"PROJECT_NAME": "demo-app"},
                allow_missing=False,
            )

            destination_script = destination_root / "run-loop.sh"
            self.assertEqual(destination_script.read_text(encoding="utf-8"), "#!/bin/sh\necho 'demo-app'\n")
            self.assertTrue(owner_execute_enabled(destination_script))

    def test_install_ralph_preserves_shell_entrypoint_modes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="install-ralph-") as temp_dir:
            repo_root = Path(temp_dir) / "repo"
            result = subprocess.run(
                [sys.executable, "scripts/install_ralph.py", "--repo-root", str(repo_root)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)

            for relative_path in [
                "scripts/ralph/run-loop.sh",
                "scripts/ralph/run-once.sh",
                "scripts/ralph/status.sh",
                "scripts/ralph/manual-promote.sh",
                "scripts/ralph/commit-if-changed.sh",
            ]:
                generated_path = repo_root / relative_path
                self.assertTrue(generated_path.exists(), relative_path)
                self.assertTrue(owner_execute_enabled(generated_path), relative_path)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from install_scaffold import derive_scaffold_answers  # noqa: E402


class InstallScaffoldTests(unittest.TestCase):
    def test_derive_scaffold_answers_normalizes_project_names(self) -> None:
        answers = derive_scaffold_answers({"PROJECT_NAME": "Mina GitHub Trend"}, Path("/tmp/mina-github-trend"))

        self.assertEqual(answers["DIST_PACKAGE_NAME"], "mina-github-trend")
        self.assertEqual(answers["CLI_COMMAND_NAME"], "mina-github-trend")
        self.assertEqual(answers["PYTHON_PACKAGE_NAME"], "mina_github_trend")
        self.assertEqual(answers["ENV_PREFIX"], "MINA_GITHUB_TREND")

    def test_install_scaffold_writes_predefined_harness_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="install-scaffold-") as temp_dir:
            temp_root = Path(temp_dir)
            repo_root = temp_root / "repo"
            answers_path = temp_root / "answers.json"
            answers_path.write_text(
                json.dumps(
                    {
                        "PROJECT_NAME": "Mina GitHub Trend",
                        "ONE_LINE_PRODUCT": "CLI for inspecting GitHub trends.",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/install_scaffold.py",
                    "--repo-root",
                    str(repo_root),
                    "--answers",
                    str(answers_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)

            expected_paths = [
                "pyproject.toml",
                "Makefile",
                ".env.example",
                "src/mina_github_trend/cli/app.py",
                "src/mina_github_trend/worker/main.py",
                "tests/unit/test_task_service.py",
                "tests/integration/test_file_task_store.py",
                "tests/e2e/test_cli_smoke.py",
            ]
            for relative_path in expected_paths:
                self.assertTrue((repo_root / relative_path).exists(), relative_path)

            pyproject = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
            self.assertIn('name = "mina-github-trend"', pyproject)
            self.assertIn('"mina-github-trend" = "mina_github_trend.cli.app:main"', pyproject)
            self.assertIn('"pytest-cov>=5.0"', pyproject)
            self.assertIn('strict = true', pyproject)

            makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
            self.assertIn("uv run ruff check .", makefile)
            self.assertIn("uv run mypy src", makefile)
            self.assertIn("python -m mina_github_trend.worker.main --once --seed-demo-if-empty", makefile)

            e2e_test = (repo_root / "tests" / "e2e" / "test_cli_smoke.py").read_text(encoding="utf-8")
            self.assertIn("MINA_GITHUB_TREND_STATE_DIR", e2e_test)


if __name__ == "__main__":
    unittest.main()

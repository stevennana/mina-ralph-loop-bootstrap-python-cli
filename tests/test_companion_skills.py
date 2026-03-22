from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from companion_skills import SKILLS  # noqa: E402


class CompanionSkillTests(unittest.TestCase):
    def test_python_preset_recommends_clean_architecture_only(self) -> None:
        self.assertEqual(list(SKILLS), ["clean-architecture"])


if __name__ == "__main__":
    unittest.main()

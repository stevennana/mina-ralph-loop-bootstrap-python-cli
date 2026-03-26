#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


CODEX_SKILLS_DIR = Path.home() / ".codex" / "skills"


@dataclass(frozen=True)
class CompanionSkill:
    name: str
    repo_url: str
    repo_name: str
    source_path: str
    install_name: str
    area: str
    purpose: str
    recommended_stage: str
    pinned_commands: tuple[str, ...]

    @property
    def install_path(self) -> Path:
        return CODEX_SKILLS_DIR / self.install_name

    @property
    def installed(self) -> bool:
        return self.install_path.exists()


SKILLS: dict[str, CompanionSkill] = {
    "clean-architecture": CompanionSkill(
        name="clean-architecture",
        repo_url="https://github.com/MKToronto/python-clean-architecture-codex.git",
        repo_name="python-clean-architecture-codex",
        source_path=".agents/skills/clean-architecture",
        install_name="clean-architecture",
        area="architecture",
        purpose="architecture and boundary shaping",
        recommended_stage="startup",
        pinned_commands=(
            "git clone https://github.com/MKToronto/python-clean-architecture-codex.git",
            "cp -r python-clean-architecture-codex/.agents/skills/clean-architecture ~/.codex/skills/clean-architecture",
        ),
    ),
    "python-packaging-release": CompanionSkill(
        name="python-packaging-release",
        repo_url="https://github.com/stevennana/mina-ralph-loop-bootstrap-python-cli.git",
        repo_name="mina-ralph-loop-bootstrap-python-cli",
        source_path="companion-skills/python-packaging-release",
        install_name="python-packaging-release",
        area="packaging",
        purpose="console entry points, build metadata, and release workflow shaping",
        recommended_stage="later",
        pinned_commands=(
            "git clone https://github.com/stevennana/mina-ralph-loop-bootstrap-python-cli.git",
            "cp -r mina-ralph-loop-bootstrap-python-cli/companion-skills/python-packaging-release ~/.codex/skills/python-packaging-release",
        ),
    ),
    "cli-ux-typer-rich": CompanionSkill(
        name="cli-ux-typer-rich",
        repo_url="https://github.com/stevennana/mina-ralph-loop-bootstrap-python-cli.git",
        repo_name="mina-ralph-loop-bootstrap-python-cli",
        source_path="companion-skills/cli-ux-typer-rich",
        install_name="cli-ux-typer-rich",
        area="cli-ux",
        purpose="Typer command design, Rich output, and terminal ergonomics",
        recommended_stage="later",
        pinned_commands=(
            "git clone https://github.com/stevennana/mina-ralph-loop-bootstrap-python-cli.git",
            "cp -r mina-ralph-loop-bootstrap-python-cli/companion-skills/cli-ux-typer-rich ~/.codex/skills/cli-ux-typer-rich",
        ),
    ),
    "config-and-secrets": CompanionSkill(
        name="config-and-secrets",
        repo_url="https://github.com/stevennana/mina-ralph-loop-bootstrap-python-cli.git",
        repo_name="mina-ralph-loop-bootstrap-python-cli",
        source_path="companion-skills/config-and-secrets",
        install_name="config-and-secrets",
        area="configuration",
        purpose="settings policy, environment precedence, and secret handling",
        recommended_stage="later",
        pinned_commands=(
            "git clone https://github.com/stevennana/mina-ralph-loop-bootstrap-python-cli.git",
            "cp -r mina-ralph-loop-bootstrap-python-cli/companion-skills/config-and-secrets ~/.codex/skills/config-and-secrets",
        ),
    ),
    "cli-testing-observability": CompanionSkill(
        name="cli-testing-observability",
        repo_url="https://github.com/stevennana/mina-ralph-loop-bootstrap-python-cli.git",
        repo_name="mina-ralph-loop-bootstrap-python-cli",
        source_path="companion-skills/cli-testing-observability",
        install_name="cli-testing-observability",
        area="testing",
        purpose="pytest tiers, CliRunner coverage, and operator-visible diagnostics",
        recommended_stage="later",
        pinned_commands=(
            "git clone https://github.com/stevennana/mina-ralph-loop-bootstrap-python-cli.git",
            "cp -r mina-ralph-loop-bootstrap-python-cli/companion-skills/cli-testing-observability ~/.codex/skills/cli-testing-observability",
        ),
    ),
    "systemd-worker-ops": CompanionSkill(
        name="systemd-worker-ops",
        repo_url="https://github.com/stevennana/mina-ralph-loop-bootstrap-python-cli.git",
        repo_name="mina-ralph-loop-bootstrap-python-cli",
        source_path="companion-skills/systemd-worker-ops",
        install_name="systemd-worker-ops",
        area="operations",
        purpose="systemd service units, restart behavior, and worker runtime operations",
        recommended_stage="later",
        pinned_commands=(
            "git clone https://github.com/stevennana/mina-ralph-loop-bootstrap-python-cli.git",
            "cp -r mina-ralph-loop-bootstrap-python-cli/companion-skills/systemd-worker-ops ~/.codex/skills/systemd-worker-ops",
        ),
    ),
}

DEFAULT_STARTUP_SKILL_NAMES = ("clean-architecture",)


def _resolve_skills(requested: list[str] | None, *, include_all: bool = False) -> list[CompanionSkill]:
    if not requested:
        if include_all:
            return list(SKILLS.values())
        return [SKILLS[name] for name in DEFAULT_STARTUP_SKILL_NAMES]
    resolved: list[CompanionSkill] = []
    for name in requested:
        skill = SKILLS.get(name)
        if skill is None:
            raise SystemExit(f"Unknown companion skill: {name}")
        resolved.append(skill)
    return resolved


def _print_status(skills: list[CompanionSkill], json_output: bool) -> int:
    if json_output:
        payload = [
            {
                "name": skill.name,
                "installed": skill.installed,
                "install_path": str(skill.install_path),
                "area": skill.area,
                "purpose": skill.purpose,
                "recommended_stage": skill.recommended_stage,
            }
            for skill in skills
        ]
        print(json.dumps(payload, indent=2))
        return 0

    for skill in skills:
        state = "installed" if skill.installed else "missing"
        print(f"{skill.name}: {state} [{skill.recommended_stage}] ({skill.purpose})")
    return 0


def _print_commands(skill: CompanionSkill) -> int:
    print("\n".join(skill.pinned_commands))
    return 0


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _install_skill(skill: CompanionSkill) -> int:
    CODEX_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    if skill.install_path.exists():
        print(f"{skill.name} is already installed at {skill.install_path}", file=sys.stderr)
        return 0

    with tempfile.TemporaryDirectory(prefix="codex-companion-skill-") as tmp:
        tmp_path = Path(tmp)
        checkout_path = tmp_path / skill.repo_name
        _run(["git", "clone", "--depth", "1", skill.repo_url, str(checkout_path)])

        source_path = checkout_path / skill.source_path
        if not source_path.exists():
            raise SystemExit(f"Skill source path not found: {source_path}")

        shutil.copytree(source_path, skill.install_path)

    print(f"Installed {skill.name} to {skill.install_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect or install encoded companion skills.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show install status for companion skills.")
    status_parser.add_argument("skills", nargs="*", help="Optional subset of skill names.")
    status_parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    status_parser.add_argument("--all", action="store_true", help="Show all encoded companion skills, not just the startup set.")

    command_parser = subparsers.add_parser("command", help="Print install commands for one skill.")
    command_parser.add_argument("skill", help="Skill name.")

    install_parser = subparsers.add_parser("install", help="Install one encoded companion skill into ~/.codex/skills.")
    install_parser.add_argument("skill", help="Skill name.")

    args = parser.parse_args()

    if args.command == "status":
        return _print_status(_resolve_skills(args.skills, include_all=args.all), args.json)
    if args.command == "command":
        return _print_commands(_resolve_skills([args.skill])[0])
    if args.command == "install":
        return _install_skill(_resolve_skills([args.skill])[0])
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

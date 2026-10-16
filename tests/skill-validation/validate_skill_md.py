#!/usr/bin/env python3
"""
Validate SKILL.md files in a skills repo.

Checks each skills/<name>/SKILL.md for:
  - YAML frontmatter delimited by --- ... ---
  - required fields: name, description
  - frontmatter `name` matches the folder name (kebab-case)
  - description is non-empty and within a sane length
  - at least one heading (# ...) after the frontmatter
  - no obviously broken relative links to files that don't exist

Usage:
    python validate_skill_md.py [skills_dir]

Exits non-zero if any skill fails validation.
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml. Install with:")
    print("  pip install pyyaml --break-system-packages")
    sys.exit(1)

REQUIRED_FIELDS = ["name", "description"]
MAX_DESCRIPTION_LEN = 2000  # generous ceiling; skills descriptions can be long
MIN_DESCRIPTION_LEN = 20

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n?", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def find_skill_dirs(skills_root: Path):
    if not skills_root.exists():
        return []
    return sorted(p for p in skills_root.iterdir() if p.is_dir())


def validate_skill(skill_dir: Path):
    errors = []
    warnings = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"missing SKILL.md in {skill_dir}"], []

    text = skill_md.read_text(encoding="utf-8")

    match = FRONTMATTER_RE.match(text)
    if not match:
        errors.append("no valid --- frontmatter block found at top of file")
        return errors, warnings

    raw_frontmatter = match.group(1)
    try:
        frontmatter = yaml.safe_load(raw_frontmatter) or {}
    except yaml.YAMLError as e:
        errors.append(f"frontmatter is not valid YAML: {e}")
        return errors, warnings

    if not isinstance(frontmatter, dict):
        errors.append("frontmatter did not parse to a mapping of key: value pairs")
        return errors, warnings

    for field in REQUIRED_FIELDS:
        if field not in frontmatter or not str(frontmatter[field]).strip():
            errors.append(f"missing or empty required frontmatter field: '{field}'")

    name = str(frontmatter.get("name", "")).strip()
    if name and name != skill_dir.name:
        errors.append(
            f"frontmatter name '{name}' does not match folder name '{skill_dir.name}'"
        )
    if name and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        warnings.append(f"name '{name}' is not kebab-case")

    description = str(frontmatter.get("description", "")).strip()
    if description:
        if len(description) < MIN_DESCRIPTION_LEN:
            warnings.append(
                f"description is very short ({len(description)} chars) -- "
                "agents route on this text, make it specific"
            )
        if len(description) > MAX_DESCRIPTION_LEN:
            warnings.append(
                f"description is very long ({len(description)} chars) -- "
                f"consider trimming below {MAX_DESCRIPTION_LEN}"
            )

    body = text[match.end():]
    if not re.search(r"^#\s+\S", body, re.MULTILINE):
        warnings.append("no top-level '# Heading' found in the body after frontmatter")

    # Check relative links resolve to real files within the skill folder
    for link in LINK_RE.findall(body):
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        link_path = (skill_dir / link.split("#")[0]).resolve()
        if not link_path.exists():
            warnings.append(f"linked file does not exist: {link}")

    return errors, warnings


def main():
    repo_root = Path(__file__).resolve().parents[2]
    skills_root = Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "skills"

    skill_dirs = find_skill_dirs(skills_root)
    if not skill_dirs:
        print(f"No skill folders found under {skills_root}")
        sys.exit(1)

    total_errors = 0
    total_warnings = 0

    for skill_dir in skill_dirs:
        errors, warnings = validate_skill(skill_dir)
        status = "FAIL" if errors else ("WARN" if warnings else "OK")
        print(f"[{status}] {skill_dir.name}")
        for e in errors:
            print(f"   error:   {e}")
        for w in warnings:
            print(f"   warning: {w}")
        total_errors += len(errors)
        total_warnings += len(warnings)

    print()
    print(f"{len(skill_dirs)} skill(s) checked, {total_errors} error(s), {total_warnings} warning(s)")

    if total_errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

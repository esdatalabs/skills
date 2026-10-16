# Contributing

## Adding a skill

1. Create `skills/<kebab-case-name>/SKILL.md`.
2. Frontmatter must include:
   - `name`: must exactly match the folder name.
   - `description`: the single thing an agent uses to decide whether to load this skill. Be specific about *when* to trigger it, including example phrasings, and — if it overlaps with another skill in this repo — say explicitly when to prefer one over the other (see how `green-field-design` and `reverse-engineering` cross-reference each other).
3. Write the body as direct, imperative instructions to the agent, not documentation prose aimed at a human reader.
4. Keep the skill self-contained: any scripts, templates, or reference material it needs should live inside its own folder (`scripts/`, `reference/`, `templates/`), not scattered elsewhere in the repo.

## Python scripts inside a skill

If a skill ships a Python script that needs third-party libraries, add a `requirements.txt` next to it and document the install step in the `SKILL.md`:

```markdown
## Setup
pip install -r requirements.txt --break-system-packages
```

Prefer the standard library where practical to keep skills portable across environments.

## Validating

Run before every PR:

```bash
pip install -r tests/skill-validation/requirements.txt --break-system-packages
python tests/skill-validation/validate_skill_md.py
```

The validator checks:
- frontmatter exists and is valid YAML
- `name` and `description` are present
- `name` matches the folder name
- there's a top-level heading in the body
- relative links inside the skill resolve to real files

Errors fail CI; warnings are advisory but worth fixing.

## Style

- One skill = one clearly scoped job. If a `SKILL.md` is trying to cover two unrelated workflows, split it.
- Write descriptions for the agent that will route on them — front-load the trigger conditions, not the backstory.
- Prefer markdown output formats over prose paragraphs when a skill produces documents meant for another agent to consume.

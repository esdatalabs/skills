# Agent Skills

A collection of modular, self-contained "skills" that extend what an AI agent can do —
each skill packages instructions, and optionally scripts or reference material,
for a specific task domain.

## What is a skill?

A skill is a folder containing a `SKILL.md` file that tells an agent:

- **when** to use it (a description the agent matches against the task at hand)
- **how** to use it (step-by-step instructions or guidance)
- optionally, supporting scripts, templates, or reference docs

Skills are designed to be loaded on demand, not all at once — an agent scans
skill descriptions and only reads the full `SKILL.md` when it's relevant to the task.

## Structure

```
skills/<skill-name>/
├── SKILL.md          # required — YAML frontmatter + instructions
├── scripts/           # optional — helper scripts the agent can run
├── reference/          # optional — docs, schemas, examples
└── templates/          # optional — starter files
```

## Skills in this repo

| Skill | Description |
|---|---|
| [green-field-design](skills/green-field-design/SKILL.md) | Interviews the user to build a hierarchical design (App → Feature → Service → Scenario) for a **new** app, producing markdown docs another agent can build from. |
| [reverse-engineering](skills/reverse-engineering/SKILL.md) | The legacy-codebase counterpart — crawls an **existing** repo to draft a hypothesis of its design, then interviews the developer to confirm/correct it, producing the same doc hierarchy plus a `start-here.md` onboarding index. |

Both skills share the same App → Feature → Service → Scenario vocabulary and output format, so their docs are interchangeable and can live side by side for the same app.

## Using a skill

Point your agent's skill-loading mechanism at the `skills/` directory (or a specific
subfolder). See your agent framework's docs for how skill discovery/routing works —
in general, the agent reads each `SKILL.md`'s frontmatter `description` to decide
which skill to load in full for a given task.

## Adding a new skill

1. Create a folder under `skills/` in kebab-case: `skills/my-new-skill/`
2. Add a `SKILL.md` with frontmatter:

   ```yaml
   ---
   name: my-new-skill
   description: One or two sentences describing what this skill does and when to trigger it.
   ---
   ```

3. Write clear, imperative instructions below the frontmatter.
4. Add any scripts/templates the skill needs in subfolders (see [CONTRIBUTING.md](CONTRIBUTING.md) for guidance on including Python dependencies).
5. Validate before opening a PR:

   ```bash
   pip install -r tests/skill-validation/requirements.txt --break-system-packages
   python tests/skill-validation/validate_skill_md.py
   ```

CI runs this same check automatically on every push and pull request.

## License

[MIT](LICENSE) — see file for details.

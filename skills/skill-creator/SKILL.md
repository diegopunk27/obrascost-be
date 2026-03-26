---
name: skill-creator
description: How to add or extend Agent skills in this repo.
---

# Creating skills

1. Add a folder under `skills/<skill-name>/`.
2. Create `SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name
description: One line for discovery.
---
```

3. Keep content **short**: rules, examples, links to code paths.
4. Register the skill in [AGENTS.md](../../AGENTS.md) mapping table.
5. Run through [skill-sync](skill-sync/SKILL.md) mentally: tables consistent.

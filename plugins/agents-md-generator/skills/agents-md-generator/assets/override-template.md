# AGENTS.override.md Template

AGENTS.override.md extends or overrides the parent AGENTS.md in the same directory.
Codex loads AGENTS.override.md with higher priority than AGENTS.md.
Use for: team-specific overrides, personal preferences, environment-specific settings.

Typically gitignored at the project level, or used in team-specific subdirectories.

## Template

```markdown
# AGENTS.override.md -- Local Overrides

## Local Environment

- {{LOCAL_ENV_DETAILS}}

## Local Commands

{{#each LOCAL_COMMANDS}}
- {{COMMAND}}
{{/each}}

## Personal Preferences

{{#each PERSONAL_PREFERENCES}}
- {{PREFERENCE}}
{{/each}}

{{#if HAS_PATH_SCOPED_RULES}}
## Path-Scoped Rules

These rules apply only when working in this directory and override the parent AGENTS.md.

{{#each PATH_SCOPED_RULES}}
- {{RULE}}
{{/each}}
{{/if}}

## Maintenance Rules

When files in this directory are added, moved, renamed, or deleted, check whether this AGENTS.override.md needs updating. **Run the agents-md-generator skill to sync.**
```

## Usage Scenarios

### Personal Local Override
Place in project root as `AGENTS.override.md` (gitignored):
- Your personal conda env name vs team's docker setup
- Local port preferences (`--port 3001` instead of default `3000`)
- Personal tool aliases

### Team-Specific Override
Place in team subdirectory (e.g., `src/frontend/AGENTS.override.md`):
- Frontend team's lint rules that differ from backend
- Team-specific test commands or conventions
- Framework preferences within a monorepo

### Environment-Specific Override
Place in environment directory (e.g., `deploy/staging/AGENTS.override.md`):
- Staging-specific deploy commands
- Environment variables for staging
- Different safety rules for production vs staging

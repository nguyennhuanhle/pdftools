---
description: Create isolated git worktree for parallel development
argument-hint: [feature-description] OR [project] [feature] (monorepo)
---

Create an isolated git worktree for parallel feature development.

## Workflow

### Step 1: Get Repository Info

```bash
node .claude/scripts/worktree.cjs info --json
```

**Response fields:**
- `repoType`: "monorepo" or "standalone"
- `baseBranch`: detected base branch
- `projects`: array of {name, path} for monorepo
- `envFiles`: array of .env* files found
- `dirtyState`: boolean

### Step 2: Gather Info via AskUserQuestion

**Detect branch prefix from user's description:**
- Keywords "fix", "bug", "error", "issue" → prefix = `fix`
- Keywords "refactor", "restructure", "rewrite" → prefix = `refactor`
- Keywords "docs", "documentation", "readme" → prefix = `docs`
- Keywords "test", "spec", "coverage" → prefix = `test`
- Keywords "chore", "cleanup", "deps" → prefix = `chore`
- Keywords "perf", "performance", "optimize" → prefix = `perf`
- Everything else → prefix = `feat`

**For MONOREPO:** Use AskUserQuestion if project not specified:
```javascript
AskUserQuestion({
  questions: [{
    header: "Project",
    question: "Which project should the worktree be created for?",
    options: projects.map(p => ({ label: p.name, description: p.path })),
    multiSelect: false
  }]
})
```

**Env files:** Handled automatically - `.env*.example` templates are auto-copied with `.example` suffix removed.

### Step 3: Convert Description to Slug

- "add authentication system" → `add-auth`
- "fix login bug" → `login-bug`
- Remove filler words, kebab-case, max 50 chars

### Step 4: Execute Command

**Monorepo:**
```bash
node .claude/scripts/worktree.cjs create "<PROJECT>" "<SLUG>" --prefix <TYPE>
```

**Standalone:**
```bash
node .claude/scripts/worktree.cjs create "<SLUG>" --prefix <TYPE>
```

**Options:**
- `--prefix` - Branch type: feat|fix|refactor|docs|test|chore|perf
- `--env` - Comma-separated .env files to copy (legacy)
- `--json` - Output JSON for parsing
- `--dry-run` - Preview without executing

**Auto-behaviors:**
- **Env templates:** `.env*.example` files auto-copied with suffix removed

### Step 5: Install Dependencies (AI-Guided)

Based on your existing knowledge of the project, determine and run the appropriate install command in background:

```bash
# Examples - use your project context to determine
bun install          # bun.lock present
pnpm install         # pnpm-lock.yaml present
yarn install         # yarn.lock present
npm install          # package-lock.json or package.json
poetry install       # poetry.lock or pyproject.toml
pip install -r requirements.txt  # requirements.txt
cargo build          # Cargo.toml
go mod download      # go.mod
bundle install       # Gemfile
composer install     # composer.json
```

**Key:** You already have project context from reading files. Use that knowledge instead of re-detecting.

## Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `create` | `create [project] <feature>` | Create new worktree |
| `remove` | `remove <name-or-path>` | Remove worktree and branch |
| `info` | `info` | Get repo info |
| `list` | `list` | List existing worktrees |

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| `MISSING_ARGS` | Missing project/feature for monorepo | Ask for both |
| `MISSING_FEATURE` | No feature name (standalone) | Ask for feature |
| `PROJECT_NOT_FOUND` | Project not in .gitmodules | Show available projects |
| `MULTIPLE_PROJECTS_MATCH` | Ambiguous project name | Use AskUserQuestion |
| `MULTIPLE_WORKTREES_MATCH` | Ambiguous worktree for remove | Use AskUserQuestion |
| `BRANCH_CHECKED_OUT` | Branch in use elsewhere | Suggest different name |
| `WORKTREE_EXISTS` | Path already exists | Suggest use or remove |
| `WORKTREE_CREATE_FAILED` | Git command failed | Show git error |
| `WORKTREE_REMOVE_FAILED` | Cannot remove worktree | Check uncommitted changes |

## Example Session

```
User: /worktree fix the login validation bug

Claude: [Runs: node .claude/scripts/worktree.cjs info --json]
        [Detects: standalone repo, envFiles: [".env.example"]]
        [Detects prefix from "fix" keyword: fix]
        [Converts slug: "login-validation-bug"]
        [Runs: node .claude/scripts/worktree.cjs create "login-validation-bug" --prefix fix]

Output: ✅ Worktree created successfully!
        Path: ../worktrees/myrepo-login-validation-bug
        Branch: fix/login-validation-bug

        📄 Environment templates copied:
           ✓ .env.example → .env

Claude: [Knows this is a Node.js project with pnpm from earlier context]
        [Runs: pnpm install in background]
```

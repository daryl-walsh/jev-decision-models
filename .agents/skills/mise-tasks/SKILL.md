---
name: mise-tasks
description: Use when defining, configuring, or running project tasks with mise (mise-en-place) — TOML tasks, file tasks, task templates, dependencies (depends/wait_for/depends_post), arguments via the usage spec, sources/outputs caching, and monorepo task orchestration.
---

# Mise-Tasks Skill

Task running with [mise](https://mise.jdx.dev) (mise-en-place). mise runs project tasks
— builders, linters, tests, servers, deploy scripts — inside the mise environment, so the
tools and env vars declared in `mise.toml` are automatically on `PATH` when a task runs.

## When to Use This Skill

Use this skill when you need to:

- **Define tasks** in a `mise.toml` `[tasks]` section or as standalone executable **file tasks**
  (`mise-tasks/`, `.mise/tasks/`, …).
- **Wire up dependencies** — run `build` before `test`, clean up after deploy, or wait on a
  background service (`depends`, `depends_post`, `wait_for`).
- **Pass arguments/flags** to a task with validation, autocomplete, and `--help` (the `usage` spec).
- **Skip expensive re-runs** by declaring `sources`/`outputs` (incremental builds) or watch files
  with `mise watch`.
- **Share task definitions** via `[task_templates]` and `extends`, or across a repo with
  **monorepo mode** (`monorepo_root = true`) and `//path:task` targeting.
- **Run tasks**: `mise run <task>`, wildcards (`mise run 'test:*'`), parallel jobs (`--jobs`).

> **Source note:** This skill is synthesized from the **official mise documentation**
> (`mise.jdx.dev/tasks/*`, 9 pages). It is a single authoritative source — there are no
> cross-source conflicts. Where the docs mark a feature as deprecated or planned, this skill
> calls that out explicitly (see [Deprecations & Version Notes](#deprecations--version-notes)).

## Key Concepts

- **TOML task** — a task defined under `[tasks.*]` in `mise.toml`. Best for short commands and
  dependency graphs.
- **File task** — an executable script in a task directory (`mise-tasks/build`, etc.). Best for
  longer scripts; gets editor syntax highlighting and works for non-mise users. Configured with
  `#MISE key=value` header comments.
- **Task template** — a reusable definition under `[task_templates."ns:name"]` that tasks pull in
  via `extends`. Merge is *deep* for `tools`/`env`, *complete override* for `depends`.
- **`depends` / `depends_post` / `wait_for`** — the three dependency edges. `depends` = must run
  before (hard prereq); `depends_post` = runs after (cleanup, always); `wait_for` = soft/optional
  (waits only if the task is already scheduled).
- **`sources` / `outputs`** — incremental-build inputs/outputs. mise skips the task when the
  oldest output is newer than the newest source. `outputs = { auto = true }` tracks this for you.
- **`usage` spec** — the recommended way to declare args/flags. Values arrive as
  `$usage_<name>` env vars and `{{ usage.<name> }}` Tera template vars.
- **`vars`** — shared values for TOML tasks/config templating; like env vars but **not** exported
  to the task process. Reference with `{{vars.NAME}}`.
- **Monorepo mode** — `monorepo_root = true` gives a unified, path-prefixed task namespace across
  subprojects. Target tasks with `//projects/frontend:build` and wildcards (`//...:test*`).

## Quick Reference

All examples below are from the **official mise documentation**.

### Trivial TOML tasks (one-liners)

```toml
build = "cargo build"
test  = "cargo test"
lint  = "cargo clippy"
```

### A realistic `[tasks]` block

```toml
[tasks.build]
description = 'Build the CLI'
run = "cargo build"
alias = 'b'                      # `mise run b`

[tasks.test]
description = 'Run automated tests'
run = ['cargo test', './scripts/test-e2e.sh']   # commands run in series
dir = "{{cwd}}"                  # run in user's cwd, not the project root

[tasks.lint]
env = { RUST_BACKTRACE = '1' }
run = '''
#!/usr/bin/env bash
cargo clippy
'''

[tasks.ci]                       # aggregate task: only dependencies
depends = ['build', 'lint', 'test']

[tasks.release]
confirm = 'Are you sure you want to cut a new release?'
file = 'scripts/release.sh'      # execute an external script
```

### Dependencies: prereqs, cleanup, and soft waits

```toml
[tasks.test]
depends = ["lint", "build"]              # must finish first
run = "npm test"

[tasks.deploy]
depends = ["build", "test"]
depends_post = ["cleanup", "notify"]     # run after, success or failure
run = "kubectl apply -f deployment.yaml"

[tasks.integration-test]
wait_for = ["start-services"]            # only waits if it's already running
run = "npm run test:integration"
```

### Incremental builds — skip when nothing changed

```toml
[tasks.build]
run = "cargo build"
sources = ["Cargo.toml", "src/**/*.rs"]  # inputs (globs, ! to exclude)
outputs = ["target/debug/mycli"]         # or: outputs = { auto = true }
```

Task is skipped unless a source is newer than the oldest output.
Use `mise run --force build` to ignore the check, or `mise watch build` to rerun on change.

### Arguments via the `usage` spec (preferred)

```toml
[tasks.deploy]
description = "Deploy application"
usage = '''
arg "<environment>" help="Target environment" {
  choices "dev" "staging" "prod"
}
flag "-v --verbose" help="Enable verbose output"
flag "--region <region>" help="AWS region" default="us-east-1" env="AWS_REGION"
'''
run = '''
echo "Deploying to ${usage_environment?} in ${usage_region?}"
[[ "${usage_verbose?}" == "true" ]] && set -x
./deploy.sh "${usage_environment?}" "${usage_region?}"
'''
```

Run it: `mise run deploy staging --verbose --region us-west-2`.
mise generates real `--help`, autocomplete, and validation from this spec.

### File task with a `#MISE` header

```bash
#!/usr/bin/env bash
#MISE description="Build the CLI"
#MISE alias="b"
#MISE sources=["Cargo.toml", "src/**/*.rs"]
#MISE outputs=["target/debug/mycli"]
#MISE depends=["lint", "test"]
#MISE tools={rust="1.50.0"}
cargo build
```

Save as `mise-tasks/build`, then `chmod +x mise-tasks/build`. Run with `mise run build`.
(Formatters may rewrite `#MISE` → `# MISE`, which mise ignores; use `# [MISE]` to work around it.)

### Task templates (reusable definitions)

```toml
[task_templates."python:build"]
description = "Build a Python project"
run = "uv build"
tools = { python = "3.12", uv = "latest" }
env = { PYTHONPATH = "src" }

[tasks.build]
extends = "python:build"          # inherits run, tools, env

[tasks.test]
extends = "python:build"
run = "pytest --cov"             # override run, keep tools/env
```

Merge semantics: `tools` and `env` **deep-merge** (override one key, keep the rest);
`depends` is a **complete override**.

### Monorepo tasks

```toml
# /myproject/mise.toml
monorepo_root = true

[tools]
node = "20"                      # applies to all subdirectories

[monorepo]
config_roots = ["projects/*"]    # explicitly list project dirs (recommended)
```

```bash
mise //projects/frontend:build   # absolute target path from monorepo root
mise ':build'                    # task in the current config_root
mise '//...:test*'               # every test* task at any depth
```

### Running tasks

```bash
mise run build --release         # extra args go to the last command
mise run 'test:*'                # wildcard over grouped task names
mise run --jobs 8 test           # 8 parallel jobs (default is 4)
mise run -j 1 test               # force sequential (interleaved output)
mise run a arg1 ::: b arg2       # run multiple tasks with the ::: delimiter
mise tasks                       # list tasks;  mise tasks deps <t>  shows the graph
```

## Reference Files

This skill includes the full scraped documentation in `references/`:

- **`references/tasks.md`** *(official docs, ~56 KB, 9 pages)* — the complete Tasks documentation,
  covering: Tasks overview, TOML tasks, File tasks, Task templates, Task arguments (usage spec),
  Task configuration (every property), Running tasks, Task System Architecture (dependency DAG,
  parallel engine), and Monorepo tasks. Each section preserves the source URL and code examples.
- **`references/index.md`** — a short category index into `tasks.md`.

Open `references/tasks.md` and search for the section header (e.g. `## Task Configuration`,
`## Monorepo Tasks`) when you need the exhaustive property list or edge-case behavior.

## Working with This Skill

### Beginner — "I just want to run a command"
Start with **Trivial TOML tasks** above: add `mytask = "some command"` to `[tasks]`, then
`mise run mytask`. Or drop an executable script in `mise-tasks/mytask`. Read the *Tasks* and
*TOML-based Tasks* sections of `references/tasks.md`.

### Intermediate — "I need order, args, and speed"
- Chain tasks with `depends` / `depends_post` / `wait_for`.
- Add arguments with a `usage` spec (not the deprecated `arg()`/`option()`/`flag()` template
  functions — see below).
- Add `sources`/`outputs` so expensive tasks skip when inputs haven't changed.
- Reach for `references/tasks.md` → *Task Configuration* for the full property list.

### Advanced — "Monorepo / shared task libraries"
- Factor shared definitions into `[task_templates]` and `extends`.
- Turn on `monorepo_root = true`, list `[monorepo].config_roots` explicitly, and use `//path:task`
  targeting with `...`/`*` wildcards.
- Pull tasks from other repos with `git::` includes in `task_config.includes`.
- See *Monorepo Tasks* and *Task System Architecture* in `references/tasks.md`.

## Gotchas & Tips

- **Prefer `mise run <task>` in scripts/docs**, not bare `mise <task>` — a future mise subcommand
  could shadow your task name.
- **Shebangs matter.** Without a shebang, mise runs scripts under the platform default shell
  (`sh -c` on Unix, `cmd /c` on Windows). Add `#!/usr/bin/env bash` for bash features. TOML tasks
  with `sh`/`bash`/`zsh` run under `set -e` — disable per-script with `set +e`.
- **File tasks must be executable** (`chmod +x`) or mise won't discover them.
- **`confirm` only guards the task's own `run`.** `depends` tasks execute *before* the prompt.
  Put `confirm` on the dependency, or use `run = [{ task = "..." }]` to confirm first.
- **`vars` are not exported** to the task process (unlike `env`); reference them via `{{vars.NAME}}`.
- **`raw_args = true`** passes every argument through verbatim (including `--help`) — use it for
  tasks that thinly wrap a CLI with its own parser (`next build`, Django `manage.py`, argparse).
- **Redact secrets** with `redactions.env = ["SECRETS_*"]` so they don't leak into task output.

## Deprecations & Version Notes

These come straight from the official docs — mind them when writing new tasks:

- **Inline Tera arg functions (`arg()`, `option()`, `flag()`) in run scripts are deprecated.**
  Removal is planned for **mise 2026.11.0** (task-arguments page) / **2027.5.0** (toml-tasks page).
  Use the `usage` field instead. Don't mix the `usage` map with the old template functions.
- **Monorepo automatic filesystem discovery is deprecated** — define `[monorepo].config_roots`
  explicitly to avoid the deprecation warning.
- **Monorepo lockfiles are moving to a single root lockfile** (tri-state `lockfile` setting).
  Unset monorepos start warning in **2026.12.0** and default to root lockfiles in **2027.6.0**.
  Pin `lockfile = false` for mixed-version team compatibility during rollout.

## Notes

- This skill was generated from official mise documentation (`mise.jdx.dev`).
- Reference files preserve the source structure, URLs, and code examples.
- To refresh: re-run the scraper with the same configuration and the skill will be rebuilt.

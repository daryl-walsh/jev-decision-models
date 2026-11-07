# Mise-Tasks - Tasks

**Pages:** 9

---

## Tasks | mise-en-place

**URL:** https://mise.jdx.dev/tasks/

**Contents:**
- Tasks ​
- Tasks in mise.toml files ​
- File Tasks ​
- Environment variables passed to tasks ​

Define and run project tasks for building, testing, linting, deploying, and everyday development workflows.

You can define tasks in mise.toml files or as standalone shell scripts. These are useful for things like running linters, tests, builders, servers, and other tasks that are specific to a project. Of course, tasks launched with mise will include the mise environment—your tools and env vars defined in mise.toml.

Here's my favorite features about mise's task runner:

There are 2 ways to define tasks: inside of mise.toml files or as standalone shell scripts. You can also use task templates to create reusable task definitions.

Tasks are defined in the [tasks] section of the mise.toml file.

You can then run the task with mise run build (or mise build if it doesn't conflict with an existing command).

You can also define tasks as standalone shell scripts. All you have to do is to create an executable file in a specific directory like mise-tasks.

You can then run the task with mise run build like for TOML tasks. See the file tasks reference for more information.

The following environment variables are passed to the task:

**Examples:**

Example 1 (json):
```json
[tasks.build]
description = "Build the CLI"
run = "cargo build"
```

Example 2 (unknown):
```unknown
#!/usr/bin/env bash
#MISE description="Build the CLI"
cargo build
```

---

## Task Templates | mise-en-place

**URL:** https://mise.jdx.dev/tasks/templates.html

**Contents:**
- Task Templates ​
- Defining Templates ​
- Extending Templates ​
- Template Naming ​
- Merge Semantics ​
  - Example: Deep Merge for Tools ​
  - Example: Deep Merge for Env ​
  - Example: Complete Override for Depends ​
- Tera Templating ​
- Monorepo Usage ​

Task templates allow you to define reusable task definitions that can be extended by multiple tasks. This is particularly useful in monorepos or projects with similar task patterns across different components.

Templates are defined in the [task_templates.*] section of your mise.toml:

Tasks can extend templates using the extends field:

Templates use colon (:) separators for namespacing, similar to task naming conventions in monorepos:

When a task extends a template, fields are merged according to these rules:

Templates support Tera templating, rendered with the using project's context:

Available variables (same as regular tasks):

Task templates are especially useful in monorepos where multiple packages share similar build patterns:

The following features are planned for future releases:

**Examples:**

Example 1 (json):
```json
[task_templates."python:build"]
description = "Build a Python project"
run = "uv build"
tools = { python = "3.12", uv = "latest" }
env = { PYTHONPATH = "src" }

[task_templates."python:test"]
description = "Run Python tests"
run = "pytest"
tools = { python = "3.12" }
depends = ["build"]
```

Example 2 (json):
```json
[tasks.build]
extends = "python:build"

[tasks.test]
extends = "python:test"
run = "pytest --cov"  # Override run while keeping tools, depends
```

Example 3 (typescript):
```typescript
[task_templates."fullstack:build"]
tools = { python = "3.12", node = "18" }

[tasks.build]
extends = "fullstack:build"
tools = { node = "20" }  # Override node, keep python from template
# Result: tools = { python = "3.12", node = "20" }
```

Example 4 (typescript):
```typescript
[task_templates."python:build"]
env = { PYTHONPATH = "src", DEBUG = "0" }

[tasks.build]
extends = "python:build"
env = { DEBUG = "1" }  # Override DEBUG, keep PYTHONPATH from template
# Result: env = { PYTHONPATH = "src", DEBUG = "1" }
```

---

## File Tasks | mise-en-place

**URL:** https://mise.jdx.dev/tasks/file-tasks.html

**Contents:**
- File Tasks ​
- Task Configuration ​
- Shebang ​
- Editing tasks ​
- Task Grouping ​
- Arguments ​
  - Example file task with arguments ​
  - Example of a NodeJS file task with arguments ​
- CWD ​
- Running tasks directly ​

In addition to defining tasks through the configuration, they can also be defined as standalone script files in one of the following directories:

These are the default file-task directories. If task_config.includes is set for the current config scope, mise searches only the paths listed there instead.

Here is an example of a file task that builds a Rust CLI:

Ensure that the file is executable, otherwise mise will not be able to detect it.

Having the code in a bash file and not TOML helps make it work better in editors since they can do syntax highlighting and linting more easily.

They also still work great for non-mise users—though of course they'll need to find a different way to install their dev tools the tasks might use.

All configuration options can be found here task configuration You can provide additional configuration for file tasks by adding #MISE comments at the top of the file.

Assuming that file was located in mise-tasks/build, it can then be run with mise run build (or with its alias: mise run b).

Beware of formatters changing #MISE to # MISE. It's intentionally ignored by mise to avoid unintentional configuration. To workaround this, use the alternative: # [MISE].

The shebang line is optional, but if it is present, it will be used to determine the shell to run the script with. You can also use it to run the script with various programming languages.

This script can be edited by running mise tasks edit build (using $EDITOR). If it doesn't exist it will be created. This is convenient for quickly editing or creating new scripts.

File tasks in mise-tasks, .mise/tasks, mise/tasks, or .config/mise/tasks can be grouped into sub-directories which will automatically apply prefixes to their names when loaded.

Example: With a folder structure like below:

Running mise tasks will give the below output:

For comprehensive information about task arguments, see the dedicated Task Arguments page.

usage spec can be used within these files to provide argument parsing, autocompletion, documentation when running mise and can be exported to markdown. Essentially this turns tasks into fully-fledged CLIs.

The usage CLI is not required to execute mise tasks with the usage spec. However, for completions to work, the usage CLI must be installed and available in the PATH.

Here is an example of a file task that builds a Rust CLI using some of the features of usage:

For details on bash parameter expansion patterns like ${var?}, ${var:-default}, and ${var:+value}, see Bash Variable Expansion for Usage Variables.

If you have installed usage, completions will be enabled for your task. In this example,

(Note that cli and markdown help for tasks is not yet implemented in mise as of this writing but that is planned.)

If you don't get any autocomplete suggestions, use the -v (verbose) flag to see what's going on. For example, if you use mise run build -v and have an invalid usage spec, you will see an error message such as DEBUG failed to parse task file with usage

Here is how you can use usage to parse arguments in a Node.js script:

If you pass an invalid argument, you will get an error message:

Autocomplete will show the available choices for the output_file argument if usage is installed.

mise sets the current working directory to the directory of mise.toml before running tasks. This can be overridden by setting dir="{{cwd}}" in the task header:

Also, the original working directory is available in the MISE_ORIGINAL_CWD environment variable:

Tasks don't need to be configured as part of a config, you can just run them directly by passing the path to the script:

Note that the path must start with / or ./ to be considered a file path. (On Windows it can be C:\ or .\)

**Examples:**

Example 1 (unknown):
```unknown
#!/usr/bin/env bash
#MISE description="Build the CLI"
cargo build
```

Example 2 (sass):
```sass
chmod +x mise-tasks/build
```

Example 3 (unknown):
```unknown
#MISE description="Build the CLI"
#MISE alias="b"
#MISE sources=["Cargo.toml", "src/**/*.rs"]
#MISE outputs=["target/debug/mycli"]
#MISE env={RUST_BACKTRACE = "1"}
#MISE depends=["lint", "test"]
#MISE tools={rust="1.50.0"}
```

Example 4 (javascript):
```javascript
#!/usr/bin/env node
//MISE description="Hello, World in Node.js"

console.log("Hello, World!");
```

---

## Monorepo Tasks | mise-en-place

**URL:** https://mise.jdx.dev/tasks/monorepo.html

**Contents:**
- Monorepo Tasks ​
- Overview ​
  - Benefits ​
- Configuration ​
  - Enabling Monorepo Mode ​
  - Example Structure ​
- Task Path Syntax ​
  - Absolute Paths ​
  - Current config_root Tasks ​
  - Wildcard Patterns ​

mise supports monorepo-style task organization with target path syntax. This feature allows you to manage tasks across multiple projects in a single repository, where each project can have its own mise.toml configuration with tools, environment variables, and tasks that may be different from where the task is called from.

When monorepo_root is enabled in your root mise.toml, mise will automatically discover tasks in subdirectories and prefix them with their relative path from the monorepo root. This creates a unified task namespace across your entire repository.

The directory containing a mise.toml file is called the config_root. In monorepo mode, each project can have its own config_root with its own configuration, separate from the monorepo root. Note that if you use one of the alternate paths in a subdirectory like ./projects/frontend/.mise/config.toml, the config_root will be ./projects/frontend–not ./projects/frontend/.mise.

Add monorepo_root = true to your root mise.toml:

With this structure, tasks will be automatically namespaced:

Monorepo tasks use special path syntax with // and : prefixes. You can run these tasks directly with mise or with mise run. With non-monorepo tasks, the guidance is to avoid using the direct syntax for scripts because it could conflict with future core mise commands. However, mise will never define commands with a // or : prefix, so this guidance does not apply to monorepo tasks.

Use // prefix to specify the absolute path from the monorepo root:

Use : prefix to run tasks in the current config_root:

Optional Colon Syntax

The leading : is optional when running tasks from subdirectories or defining task dependencies. While both syntaxes work, we encourage using the : prefix to be explicit about monorepo task references.

Running from subdirectory:

The bare name syntax (without :) is supported primarily to ease migration from non-monorepo to monorepo configurations. When migrating, you won't need to update all your task dependencies immediately - they'll continue to work. However, using the : prefix makes it clear you're referencing a task in the current config_root.

mise supports two types of wildcards for flexible task execution:

Use ellipsis (...) to match any directory depth:

Additional glob patterns may be added in a future version so mise //projects/*:build and mise '//projects/**:build' will likely be supported. We're using ... because it matches how bazel and buck2 do it.

Use asterisk (*) to match task names:

You can combine both types of wildcards for powerful patterns:

Subdirectory tasks automatically use tools and environment variables from parent config files in the hierarchy. However, each subdirectory can also define its own tools and environment variables in its config_root. This allows you to:

vars follow the same hierarchy for task templating, so child config vars are available when running subdirectory tasks from the monorepo root.

Task templates like sources = ["{{env.SRC_DIR}}/*"] are rendered with env from the task's own config hierarchy, so a subproject's [env] section applies no matter where the task is invoked from.

Child task_config.includes templates can also reference inherited vars, which is useful for centralized task includes like git::https://example.com/tasks.git//go.toml?ref={{vars.central_ref}}.

Use mise install --monorepo to install the union of tools from every directory listed in [monorepo].config_roots. This is useful in CI when you want to warm a cache for all projects in the repository:

Passing a tool name filters the union while preserving multiple configured versions:

mise ls --monorepo lists the same union and can be used to inspect cache keys or debug which config roots are contributing tools. Both commands require monorepo_root = true and explicit [monorepo].config_roots.

Monorepos can use one lockfile at the monorepo root. Tools from packages/api/mise.toml write to <monorepo_root>/mise.lock, while environment and local variants write to root files such as mise.ci.lock and mise.local.lock.

This is rolling out as a tri-state setting. During the rollout window, unset keeps today's per-subproject lockfile behavior. Set lockfile = true to opt into root lockfiles now:

If mise finds old subproject lockfiles, it migrates them into the root lockfile the next time a lock-aware command runs. Root entries win on conflicts, unique subproject entries are preserved, and migrated subproject lockfiles are removed.

To keep lockfiles next to each subproject config after the default changes, pin the old behavior in the monorepo root:

Unset monorepos that use mise*.lock files will start warning in mise 2026.12.0 and will default to root lockfiles in mise 2027.6.0. Older mise versions do not understand unified monorepo lockfiles for subproject-owned tools. Teams that need mixed-version compatibility should use lockfile = false until everyone has upgraded.

You must explicitly list your config roots using the [monorepo] section:

This tells mise exactly which directories contain project configurations. Benefits:

Single-level globs (*) are supported, but recursive globs (**) are not. This ensures predictable performance while still allowing flexible patterns.

Automatic Discovery Deprecated

Automatic filesystem walking to discover monorepo subdirectories is deprecated. If you don't define [monorepo].config_roots, mise will still walk the filesystem but will emit a deprecation warning. Please migrate to explicit config roots.

The difference between mise tasks and mise tasks --all:

Given this structure:

When in projects/frontend/:

Place commonly-used tools and environment in the root mise.toml to avoid repetition:

Only override tools in subdirectories when they genuinely need different versions:

Prefix related tasks with common names to enable pattern matching:

Then run all test tasks: mise '//...:test*'

Organize projects in subdirectories to enable targeted execution:

Then run tasks by group:

The monorepo ecosystem offers many excellent tools, each with different strengths. Here's how mise's Monorepo Tasks compares:

Taskfile and Just are fantastic for single-project task automation. They're lightweight and easy to set up, but they weren't designed with monorepos in mind. While you can have multiple Taskfiles/Justfiles in a repo, they don't provide unified task discovery, cross-project wildcards, or automatic tool/environment layering across projects.

mise's advantage: Automatic task discovery across the entire monorepo with a unified namespace and powerful wildcard patterns.

Nx, Turborepo, and Lerna are powerful tools specifically designed for JavaScript/TypeScript monorepos.

mise's advantage: Language-agnostic support. While these tools excel in JS/TS ecosystems, mise works equally well with Rust, Go, Python, Ruby, or any mix of languages. You also get unified tool version management (not just tasks) and environment variables across your entire stack.

Bazel (Google) and Buck2 (Meta) are industrial-strength build systems designed for massive, multi-language monorepos at companies with thousands of engineers.

Both are extremely powerful but come with significant complexity:

mise's advantage: Simplicity through non-hermetic builds. mise doesn't try to control your entire build environment in isolation - instead, it manages tools and tasks in a flexible, practical way. This "non-hermetic" approach means you can use mise without restructuring your entire codebase or learning a new language. You get powerful monorepo task management with simple TOML configuration - enough power for most teams without the enterprise-level complexity that hermetic builds require.

Rush (Microsoft) offers strict dependency management and build orchestration for JavaScript monorepos, with a focus on safety and convention adherence.

Moon is a newer Rust-based build system that aims to be developer-friendly while supporting multiple languages.

mise's Monorepo Tasks aims to hit the sweet spot between simplicity and power:

When to consider alternatives:

The best tool is the one that fits your team's needs. mise's Monorepo Tasks is designed for teams who want powerful monorepo management without the complexity overhead, especially when working across multiple languages.

For monorepos with similar task patterns across projects, task templates allow you to define reusable task definitions at the monorepo root:

Projects can then extend these templates:

See Task Templates for complete documentation.

**Examples:**

Example 1 (json):
```json
# /myproject/mise.toml
monorepo_root = true

[tools]
# Tools defined here apply to all subdirectories
node = "20"
```

Example 2 (unknown):
```unknown
myproject/
├── mise.toml (with monorepo_root = true)
├── projects/
│   ├── frontend/
│   │   └── mise.toml (with tasks: build, test)
│   └── backend/
│       └── mise.toml (with tasks: build, test)
```

Example 3 (markdown):
```markdown
# Direct syntax (preferred for monorepo tasks)
mise //projects/frontend:build

# Also works with 'run'
mise run //projects/frontend:build

# Need quotes for wildcards
mise '//projects/frontend:*'
```

Example 4 (markdown):
```markdown
# Run build task in frontend project
mise //projects/frontend:build

# Run test task in backend project
mise //projects/backend:test
```

---

## Task System Architecture | mise-en-place

**URL:** https://mise.jdx.dev/tasks/architecture.html

**Contents:**
- Task System Architecture ​
- Task Dependency System ​
  - Dependency Graph Resolution ​
  - Dependency Types ​
    - depends - Prerequisites ​
    - depends_post - Cleanup Tasks ​
    - wait_for - Soft Dependencies ​
- Parallel Execution Engine ​
  - Job Control ​
  - Example Execution Flow ​

Understanding how mise's task system works helps you write more efficient tasks and troubleshoot dependency issues.

mise uses a sophisticated dependency graph system to manage task execution order and parallelism. This ensures tasks run in the correct order while maximizing performance through parallel execution.

When you run mise run build, mise creates a directed acyclic graph (DAG) of all tasks and their dependencies:

This graph ensures that:

mise supports three types of task dependencies:

Tasks that must complete successfully before this task runs:

Tasks that run after this task completes (whether successful or failed):

Tasks that should run first if they're in the current execution, but don't fail if they're not available:

mise executes tasks in parallel up to the configured job limit:

The default is 4 parallel jobs, but you can configure this globally:

Execution with --jobs 2:

mise discovers tasks from multiple sources in this order:

When you run mise run build, mise:

Tasks from parent directories are available in subdirectories and can be overridden:

In frontend/, you have access to: lint (from parent), test (overridden), build (from parent), bundle (local).

Use task arguments for conditional behavior:

The shebang ensures the script runs under bash on every platform. Without it, mise uses the platform default inline shell (sh -c on Unix, cmd /c on Windows), so the bash [ ... ] test would fail to parse on a Windows host. For richer argument handling, prefer the usage field instead of positional parameters.

Tasks can specify dependencies at runtime:

Reference tasks from other directories:

Tasks can skip execution if sources haven't changed:

mise will only run the task if:

Use mise run --force to ignore source/output checking:

Use mise watch for continuous development:

This automatically reruns tasks when their source files change.

Circular Dependencies:

Solution: Remove the circular reference or use wait_for instead of depends.

Missing Dependencies:

Solution: Define the missing task or remove the dependency.

Slow Parallel Execution:

The task architecture is designed to scale from simple single-task projects to complex multi-service applications with intricate build dependencies.

**Examples:**

Example 1 (json):
```json
[tasks.test]
depends = ["lint", "build"]
run = "npm test"
```

Example 2 (json):
```json
[tasks.deploy]
depends = ["build", "test"]
depends_post = ["cleanup", "notify"]
run = "kubectl apply -f deployment.yaml"
```

Example 3 (json):
```json
[tasks.integration-test]
wait_for = ["start-services"]  # Only waits if start-services is also being run
run = "npm run test:integration"
```

Example 4 (unknown):
```unknown
mise run --jobs 8 test        # Use 8 parallel jobs
mise run -j 1 test            # Force sequential execution
```

---

## Task Configuration | mise-en-place

**URL:** https://mise.jdx.dev/tasks/task-configuration.html

**Contents:**
- Task Configuration ​
- Task properties ​
  - run ​
  - run_windows ​
  - description ​
  - alias ​
  - depends ​
    - Passing environment variables to dependencies ​
    - Passing parent task arguments to dependencies ​
  - depends_post ​

This is an exhaustive list of all the configuration options available for tasks in mise.toml or as file tasks.

All examples are in toml-task format instead of file, however they apply in both except where otherwise noted.

The command(s) to run. This is the only required property for a task.

You can mix scripts with task references, and pass optional args and env to referenced tasks:

Simple forms still work and are equivalent:

Windows-specific variant of run supporting the same structured syntax:

A description of the task. This is used in (among other places) the help output, completions, mise run (without arguments), and mise tasks.

An alias for the task so you can run it with mise run <alias> instead of the full task name.

Tasks that must be run before this task. This is a list of task names or aliases. Arguments can be passed to the task, e.g.: depends = ["build --release"]. If multiple tasks have the same dependency, that dependency will only be run once. mise will run whatever it can in parallel (up to --jobs) through the use of depends and related properties.

You can pass environment variables to specific dependencies using two syntaxes:

Structured object format:

The structured format also supports combining env vars with arguments:

Note: These environment variables are passed only to the specified dependency, not to the current task or other dependencies.

You can forward a parent task's arguments to its dependencies using {{usage.*}} templates. Both the parent and child tasks must define a usage spec for the arguments they accept:

Running mise run deploy myapp passes "myapp" to both deploy and its build dependency.

This also works with the string syntax:

Arguments flow through dependency chains — if A depends on B which depends on C, each task can forward its resolved arguments to its own dependencies.

Like depends but these tasks run after this task and its dependencies complete. For example, you may want a postlint task that you can run individually without also running lint:

Supports the same argument and environment variable syntax as depends.

Similar to depends, it will wait for these tasks to complete before running however they won't be added to the list of tasks to run. This is essentially optional dependencies.

Supports the same argument and environment variable syntax as depends.

wait_for matches tasks differently depending on whether args or env vars are specified:

Environment variables specific to this task. These will not be passed to depends tasks.

Tools to install and activate before running the task. This is useful for tasks that require a specific tool to be installed or a tool with a different version. It will only be used for that task, not dependencies.

The directory to run the task from. The most common way this is used is when you want the task to execute in the user's current directory:

Hide the task from help, completion, and other output like mise tasks. Useful for deprecated or internal tasks you don't want others to easily see.

A message to show before running the task. This is useful for tasks that are destructive or take a long time to run. The user will be prompted to confirm before the task's own run command executes.

confirm only guards the task's own run command. Dependencies (depends) will execute before the confirmation prompt appears. If you need confirmation before dependencies run, add confirm to the dependency tasks themselves, or use run = [{ task = "..." }] instead of depends.

The confirm message supports Tera templates and can reference usage arguments:

Connects the task directly to the shell's stdin/stdout/stderr. This is useful for tasks that need to accept input or output in a way that mise's normal task handling doesn't support. This is not recommended to use because it really screws up the output whenever mise runs tasks in parallel. Ensure when using this that no other tasks are running at the same time.

In the future we could have a property like single = true or something that prevents multiple tasks from running at the same time. If that sounds useful, search/file a ticket.

When true, mise does not parse arguments to the task at all — every argument is passed through verbatim to the underlying command, including --help/-h. Use this for tasks that act as a thin proxy for a tool which already has its own argument parser (e.g. next build, Django manage.py, Python scripts using argparse):

Without raw_args, mise intercepts --help and prints its own task help. As an ad-hoc alternative for individual invocations, you can also use mise run task -- --help — the -- separator now bypasses mise's usage parser specifically for --help/-h. Arguments after that separator belong to the task, so mise run task -- -- --help forwards -- --help to the task.

Connects the task directly to the shell's stdin/stdout/stderr. Interactive tasks acquire an exclusive lock, ensuring sole access to standard I/O — while an interactive task is running, all other tasks (both interactive and non-interactive) are blocked. Non-interactive tasks can still run in parallel with each other. This is more targeted than the broad raw setting which forces single-threaded execution globally (by setting jobs = 1).

Files or directories that this task uses as input, if this and outputs is defined, mise will skip executing tasks where the modification time of the oldest output file is newer than the modification time of the newest source file. This is useful for tasks that are expensive to run and only need to be run when their inputs change.

The task itself will be automatically added as a source, so if you edit the definition that will also cause the task to be run.

This is also used in mise watch to know which files/directories to watch.

This can be specified with relative paths to the config file and/or with glob patterns, e.g.: src/**/*.rs. Ensure you don't go crazy with adding a ton of files in a glob though—mise has to scan each and every one to check the timestamp.

Running the above will only execute cargo build if mise.toml, Cargo.toml, or any ".rs" file in the src directory has changed since the last build.

The task_source_files function can be used to iterate over a task's sources within its template context.

Entries in sources prefixed with ! are excluded, matching the convention used by gitignore, watchexec, and rsync. Exclusions affect the freshness check, the task_source_files template function, and which files mise watch watches for changes.

Entries are evaluated in order, and the latest matching entry wins. A later non-negated entry can re-include a file an earlier ! excluded — for example, ["src/**/*.ts", "!src/**/*.test.ts", "src/keep.test.ts"] excludes all *.test.ts files except src/keep.test.ts.

To include a literal path that begins with !, escape the prefix as \! (e.g. "\\!important.txt" in TOML).

When a task depends on another task that also has sources defined, and the dependency runs because its sources changed, the dependent task will also re-run — even if the dependent's own sources haven't changed. This is useful for monorepo workflows where downstream tasks should be invalidated by upstream changes:

If a file in packages/core/src/ changes, both core:build and frontend:build will run. If nothing changes, both are skipped.

Note that dependencies without sources (which always run) do not trigger this invalidation — otherwise sources on the dependent task would be effectively useless.

The counterpart to sources, these are the files or directories that the task will create/modify after it executes.

auto = true is an alternative to specifying output files manually. In that case, mise will touch an internally tracked file based on the hash of the task definition (stored in ~/.local/state/mise/task-outputs/<hash> if you're curious). This is useful if you want mise run to execute when sources change but don't want to have to manually touch a file for sources to work.

The shell to use to run the task. This is useful if you want to run a task with a different shell than the default such as fish, zsh, or pwsh. Generally though, it's recommended to use a shebang instead because that will allow IDEs with mise support to show syntax highlighting and linting for the script.

Suppress mise's output for the task such as showing the command that is run, e.g.: [build] $ cargo build. When this is set, mise won't show any output other than what the script itself outputs. If you'd also like to hide even the output that the task emits, use silent.

Suppress all output from the task. If set to "stdout" or "stderr", only that stream will be suppressed.

For comprehensive information about task arguments and the usage field, see the dedicated Task Arguments page.

More advanced usage specs can be added to the task's usage field. This only applies to toml-tasks.

Both args and flags in usage specs can specify an environment variable as an alternative source for their value. This allows task arguments to be provided through environment variables when not specified on the command line.

The precedence order is:

For positional arguments:

File tasks (tasks defined as executable files in mise-tasks/ or .mise/tasks/) also support the env attribute:

Environment variables can satisfy required argument checks. If an argument is marked as required (using angle brackets <arg>), providing its value through the environment variable specified in the env attribute fulfills that requirement:

Vars are values that can be shared between TOML tasks and other Tera-rendered config like tool versions/options. They are similar to environment variables, but they are not exported to task processes. Reference them with {{vars.NAME}}.

Vars can also use value-producing directive forms from [env]:

The default form reads from a process environment variable with the same name when it is set and non-empty; values from [env] are not used for this lookup. The required form must be satisfied by the process environment or by a later config file like mise.local.toml. Values marked with redact = true are hidden from task output. Secrets are also supported as vars.

Tasks can also define task-local vars that override config vars for that task:

Like most configuration in mise, vars can be defined across several files. So for example, you could put some vars in your global mise config ~/.config/mise/config.toml, use them in a task at ~/src/work/myproject/mise.toml. You can also override those vars in "later" config files such as ~/src/work/myproject/mise.local.toml and they will be used inside tasks of any config file.

As of this writing vars are only supported in TOML tasks. I want to add support for file tasks, but I don't want to turn all file tasks into tera templates just for this feature.

Options available in the top-level mise.toml [task_config] section. These apply to all tasks which are included by that config file or use the same root directory, e.g.: ~/src/myproject/mise.toml's [task_config] applies to file tasks like ~/src/myproject/mise-tasks/mytask but not to tasks in ~/src/myproject/subproj/mise.toml.

Change the default directory tasks are run from.

Set the toml files and file-task directories mise should search when looking for tasks.

When task_config.includes is set, it replaces the default file-task directories for that config scope instead of adding to them. Include entries are rendered as Tera templates, so they can reference values such as config_root, env, and resolved vars.

The default file-task directories are:

If you want to keep the defaults and add another directory, include the defaults explicitly:

For local and monorepo task discovery, mise uses the nearest config file that defines task_config.includes. That means a child config's includes replaces both the defaults and any includes defined by parent configs for that directory. Global config files are loaded independently, so each global config file uses its own task_config.includes or the default directories if includes is unset.

Entries are evaluated in order, and when more than one include defines a task with the same name the last entry in the list wins. This applies uniformly to directory, toml-file, and git:: includes, so to override a task coming from a git:: include with a local one, list the local directory after the git:: entry:

If using included task toml files, note that they have a different format than the mise.toml file. They are just a list of tasks. The file should be the same format as the [tasks] section of mise.toml but without the [task] prefix:

If you want auto-completion/validation in included toml tasks files, you can use the following JSON schema: https://mise.en.dev/schema/mise-task.json

You can include directories or individual task toml files from git repositories using the git:: URL syntax:

URL format: git::<protocol>://<url>//<path>?ref=<ref>

When path points at a directory, mise loads both executable file tasks and any .toml task files inside that directory. When path points at a single .toml file, only that file is loaded.

Included .toml files use the task toml file format (the keys are task names — there is no [tasks.…] prefix). The repository will be cloned and cached in MISE_CACHE_DIR/remote-git-tasks-cache. Tasks from the include will be loaded as if they were local. You can disable caching with MISE_TASK_REMOTE_NO_CACHE=true or the --no-cache flag.

mise supports monorepo-style task organization with target path syntax. Enable it by setting monorepo_root = true in your root mise.toml.

For complete documentation on monorepo tasks including:

See the dedicated Monorepo Tasks documentation.

Redactions are a way to hide sensitive information from the output of tasks. This is useful for things like API keys, passwords, or other sensitive information that you don't want to accidentally leak in logs or other output.

A list of environment variables to redact from the output.

Running the above task will output echo [redacted] instead.

You can also specify these as a glob pattern, e.g.: redactions.env = ["SECRETS_*"].

The following settings control task behavior. These can be set globally in ~/.config/mise/config.toml or per-project in mise.toml:

Paths that mise will not look for tasks in.

Paths are separated by the OS path separator when using the environment variable (: on Unix, ; on Windows).

When enabled, arg(), option(), and flag() Tera functions in run scripts will not contribute to the task's usage spec—only the explicit usage field is used.

When using monorepo mode (monorepo_root = true), this controls how deep mise will search for task files in subdirectories.

Performance tip: Reduce this value if you have a very large monorepo and notice slow task discovery. For example, if your projects are all at projects/*, set to 2.

Or via environment variable:

If empty (default), uses default exclusions: node_modules, target, dist, build. If you specify any patterns, ONLY those patterns will be excluded (defaults are NOT included). For example, setting to [".temp", "vendor"] will exclude only those two directories.

When enabled, mise will skip directories that are ignored by .gitignore files when discovering tasks in a monorepo.

Change output style when executing tasks. This controls the output of mise run.

Mise will always fetch the latest tasks from the remote, by default the cache is used.

Automatically install missing tools when executing tasks.

Disable truncation of command lines in task execution output. When true, the full command line will be shown.

Tasks to skip when running mise run.

Run only specified tasks skipping all dependencies.

When source mtime equals output mtime, consider sources fresh (use <=). Default false uses strict < comparison.

Use content hashing (blake3) instead of metadata for source freshness. More accurate but slower.

Sets a global default timeout for all tasks. Individual tasks can also specify their own timeout.

When both a global timeout and a per-task timeout are set, the shorter of the two always wins—a per-task timeout cannot extend beyond the global timeout. The --timeout CLI flag overrides this global setting.

Show completion message with elapsed time for each task on mise run. Default shows when output type is prefix.

**Examples:**

Example 1 (json):
```json
[tasks.grouped]
run = [
  { task = "t1" },          # run t1 (with its dependencies)
  { task = "build", args = ["--release"], env = { RUSTFLAGS = "-C opt-level=3" } },
  { tasks = ["t2", "t3"] }, # run t2 and t3 in parallel (with their dependencies)
  "echo end",               # then run a script
]
```

Example 2 (json):
```json
tasks.a = "echo hello"
tasks.b = ["echo hello"]
tasks.c.run = "echo hello"
[tasks.d]
run = "echo hello"
[tasks.e]
run = ["echo hello"]
```

Example 3 (json):
```json
[tasks.build]
run = "cargo build"
run_windows = "cargo build --features windows"
```

Example 4 (json):
```json
[tasks.build]
description = "Build the CLI"
run = "cargo build"
```

---

## Running Tasks | mise-en-place

**URL:** https://mise.jdx.dev/tasks/running-tasks.html

**Contents:**
- Running Tasks ​
- Task Grouping ​
- Wildcards ​
  - Examples ​
- Running on file changes ​
- Watching files ​
- mise run shorthand ​
- Execution order ​

See available tasks with mise tasks. To show tasks hidden with property hide=true, use the option --hidden.

List dependencies of tasks with mise tasks deps [tasks]....

Run a task with mise tasks run <task>, mise run <task>, mise r <task>, or just mise <task>—however that last one you should never put into scripts or documentation because if mise ever adds a command with that name in a future mise version, the task will be shadowed and must be run with one of the other forms.

Most mise users will have an alias for mise run like alias mr='mise run'.

By default, tasks will execute with a maximum of 4 parallel jobs. Customize this with the --jobs option, jobs setting or MISE_JOBS environment variable. The output normally will be by line, prefixed with the task label. By printing line-by-line we avoid interleaving output from parallel executions. However, if --jobs == 1, the output will be set to interleave.

To just print stdout/stderr directly, use --interleave, the task.output setting, or MISE_TASK_OUTPUT=interleave.

Stdin is not read by default. To enable this, set raw = true on the task that needs it. This will prevent it running in parallel with any other task—a RWMutex will get a write lock in this case. This also prevents redactions applied to the output.

Extra arguments will be passed to the task, for example, if we want to run in release mode:

If there are multiple commands, the args are only passed to the last command.

You can define arguments/flags for tasks which will provide validation, parsing, autocomplete, and documentation.

Autocomplete will work automatically for tasks if the usage CLI is installed and mise completions are working.

Markdown documentation can be generated with mise generate task-docs.

Multiple tasks/arguments can be separated with this ::: delimiter:

mise will run the task named "default" if no task is specified—and you've created one named "default". You can also alias a different task to "default".

Tasks can be grouped semantically by using name prefixes separated with :s. For example all testing related tasks may begin with test:. Nested grouping can also be used to further refine groups and simplify pattern matching. For example running mise run test:**:local will matchtest:units:local, test:integration:local and test:e2e:happy:local (See Wildcards for more information).

Since TOML keys can't contain colons without quoting, use quoted keys in mise.toml:

Glob style wildcards are supported when running tasks or specifying tasks dependencies.

Available Wildcard Patterns:

mise run generate:{completions,docs:*}

And with dependencies:

It's often handy to only execute a task if the files it uses changes. For example, we might only want to run cargo build if an ".rs" file changes. This can be done with the following config:

Now if target/debug/mycli is newer than Cargo.toml or any ".rs" file, the task will be skipped. This uses last modified timestamps. It wouldn't be hard to add checksum support.

Run a task when the source changes with mise watch

Currently, this just shells out to watchexec (which you can install however you want including with mise: mise use -g watchexec@latest. This may change in the future.)

Tasks can be run with mise run <TASK> or mise <TASK>—if the name doesn't conflict with a mise command. Because mise may later add a command with a conflicting name, it's recommended to use mise run <TASK> in scripts and documentation.

You can use depends, wait_for and depends_post to control the order of execution.

This will ensure that the build task is run before the test task.

You can also define a mise task to run other tasks in parallel or in series:

**Examples:**

Example 1 (unknown):
```unknown
mise run build --release
```

Example 2 (julia):
```julia
mise run build arg1 arg2 ::: test arg3 arg4
```

Example 3 (json):
```json
[tasks."test:unit"]
run = 'cargo test --lib'
```

Example 4 (json):
```json
[tasks."lint:eslint"] # using a ":" means we need to add quotes
run = "eslint ."
[tasks."lint:prettier"]
run = "prettier --check ."
[tasks.lint]
depends = ["lint:*"]
wait_for = ["render"] # does not add as a dependency, but if it is already running, wait for it to finish
```

---

## Task Arguments | mise-en-place

**URL:** https://mise.jdx.dev/tasks/task-arguments.html

**Contents:**
- Task Arguments ​
- Recommended Methods ​
  - 1. Usage Field (Preferred) ​
    - Quick Example ​
  - 2. File Task Headers ​
    - Mounting Generated Specs ​
- Complete Usage Specification Reference ​
  - Positional Arguments (arg) ​
    - Basic Syntax ​
    - With Defaults ​

Task arguments allow you to pass parameters to tasks, making them more flexible and reusable. There are three ways to define task arguments in mise, but only two are recommended for current use.

The usage field is the recommended approach for defining task arguments. It provides a clean, declarative syntax that works with both TOML tasks and file tasks.

See Complete Usage Specification Reference for more details.

Arguments defined in the usage field are automatically available as environment variables prefixed with usage_:

In addition to environment variables, usage values are available inside Tera templates in task run scripts via a usage map:

The usage map uses snake_case argument/flag names as keys (just like the usage_ environment variables). Names with - are converted to _, so a flag like --dry-run becomes available as {{ usage.dry_run }} and $usage_dry_run. Variadic arguments/flags are exposed as arrays and can be used with Tera's for loops and filters like length. The usage map is separate from the deprecated Tera template functions (arg(), option(), flag()) described later on this page—you should not mix the two approaches in the same task.

{{usage.*}} templates can also be used in depends, depends_post, and wait_for to forward arguments to dependency tasks. See Passing parent task arguments to dependencies for details.

For file tasks, you can define arguments directly in the file using special #MISE or #USAGE comment syntax:

Use #MISE (uppercase, recommended) or #USAGE for defining arguments in file tasks. # [MISE] or # [USAGE] are also accepted as workarounds for formatters.

File tasks that wrap another CLI can mount a usage spec generated by that CLI:

The mount command runs when shell completion asks for the task spec, so it must work outside the task's final process. Calling the task itself, as shown above, lets mise apply task configuration before forwarding --usage-spec.

Positional arguments are defined with arg and must be provided in order.

Handling Variadic Args with Spaces in Bash

Variadic arguments are passed as a shell-escaped string. To properly handle arguments containing spaces as a bash array, wrap the variable in parentheses:

Priority order: CLI argument > Environment variable > Default value

Flags can be defined as booleans or as accepting values.

Custom completion can be defined for any argument or flag by name:

Output format (split on : for value and description):

For detailed help text, use multi-line format:

Hide arguments from help output (useful for deprecated or internal options):

When accessing usage-defined variables in bash scripts, use parameter expansion syntax to help shellcheck understand these variables and provide default values for boolean flags.

Use ${usage_var?} since usage guarantees they'll be set:

Use ${usage_var:-false} to provide a default value:

Use ${usage_var:?} to ensure non-empty values:

Use ${usage_var:+value} to pass flags only when set:

These expansions help shellcheck understand your script and prevent warnings about potentially unset variables while maintaining proper error handling.

Deprecated - Removal in 2026.11.0

The Tera template method for defining task arguments is deprecated and will be removed in mise 2026.11.0.

Why it's being removed:

Migration required: Please migrate to the usage field method before 2026.11.0.

Opt-out setting: If you want to disable the two-pass parsing behavior immediately (before removal), you can set:

Or via environment variable: MISE_TASK_DISABLE_SPEC_FROM_RUN_SCRIPTS=1

When enabled, mise will only use the usage field for spec generation, ignoring any arg(), option(), or flag() functions in run scripts. See Settings for more details.

Previously, you could define arguments inline in run scripts using Tera template functions:

Problems with this approach:

Empty strings during parsing: During spec collection (first pass), template functions return empty strings, so you can't use them in templates like:

Escaping complexity: Different shell types require different escaping:

No help generation: Doesn't generate proper --help output

Here's how to migrate from Tera templates to the usage field:

Handling Arguments with Spaces

If your variadic arguments may contain spaces, convert the variable to a bash array:

**Examples:**

Example 1 (bash):
```bash
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

Example 2 (markdown):
```markdown
# Execute with arguments
$ mise run deploy staging --verbose --region us-west-2

# Inside the task, these are available as:
# $usage_environment = "staging"
# $usage_verbose = "true"
# $usage_region = "us-west-2"
```

Example 3 (json):
```json
[tasks.deploy]
description = "Deploy application"
usage = '''
arg "<environment>" help="Target environment"
flag "-v --verbose" help="Enable verbose output"
flag "--region <region>" help="AWS region" default="us-east-1"
'''
run = '''
echo "Deploying to {{ usage.environment }} in {{ usage.region }}"
{% if usage.verbose %}
  echo "Verbose mode enabled"
{% endif %}
'''
```

Example 4 (yaml):
```yaml
$ mise run deploy --help
Deploy application

Usage: deploy <environment> [OPTIONS]

Arguments:
  <environment>  Target environment [possible values: dev, staging, prod]

Options:
  -v, --verbose          Enable verbose output
      --region <region>  AWS region [env: AWS_REGION] [default: us-east-1]
  -h, --help            Print help
```

---

## TOML-based Tasks | mise-en-place

**URL:** https://mise.jdx.dev/tasks/toml-tasks.html

**Contents:**
- TOML-based Tasks ​
- Trivial task examples ​
- Detailed task examples ​
- Adding tasks ​
- Common options ​
  - Run command ​
  - Specifying which directory to use ​
  - Adding a description and alias ​
  - Dependencies ​
  - Environment variables ​

Tasks can be defined in mise.toml files in different ways. Trivial tasks can be written into a [tasks] section, while more detailed tasks each get their own section.

You can use environment variables or vars to define common arguments:

You can edit the mise.toml file directly or using mise tasks add

will add the following to mise.toml:

For an exhaustive list, see task configuration.

Provide the script to run. Can be a single command or an array of commands:

Commands are run in series. If a command fails, the task will stop and the remaining commands will not run.

You can specify an alternate command to run on Windows by using the run_windows key:

The dir property determines the cwd in which the task is executed. You can use the directory from where the task was run with dir = "{{cwd}}":

Also, MISE_ORIGINAL_CWD is set to the original working directory and will be passed to the task.

You can add a description to a task and alias for a task.

You can specify dependencies for a task. Dependencies are run before the task itself. If a dependency fails, the task will not run.

There are other ways to specify dependencies, see wait_for and depends_post

You can specify environment variables for a task:

If you want to skip executing a task if certain files haven't changed (up-to-date), you should specify sources and outputs:

You can use sources alone if with mise watch to run the task when the sources change. You can use the task_source_files() function to get the resolved paths of a task's sources from within its template.

A message to show before running the task. The user will be prompted to confirm before the task is run.

Tasks are executed with set -e (set -o erropt) if the shell is sh, bash, or zsh. This means that the script will exit if any command fails. You can disable this by running set +e in the script.

You can specify a shell command to run the script with (default is sh -c or cmd /c):

By using a shebang (or shell), you can run tasks in different languages (e.g., Python, Node.js, Ruby, etc.):

A shebang is the character sequence #! at the beginning of a script file that tells the system which program should be used to interpret/execute the script. The env command comes from GNU Coreutils. mise does not use env but will behave similarly.

For example, #!/usr/bin/env python will run the script with the Python interpreter found in the PATH.

The -S flag allows passing multiple arguments to the interpreter. It treats the rest of the line as a single argument string to be split.

This is useful when you need to specify interpreter flags or options. Example: #!/usr/bin/env -S python -u will run Python with unbuffered output.

You can specify a file to run as a task:

Task files can be fetched remotely with multiple protocols:

Please note that the file will be downloaded and executed. Make sure you trust the source.

Url format must follow these patterns git::<protocol>://<url>//<path>?<ref>

Each task file is cached in the MISE_CACHE_DIR directory. If the file is updated, it will not be re-downloaded unless the cache is cleared.

You can reset the cache by running mise cache clear.

You can use the MISE_TASK_REMOTE_NO_CACHE environment variable to disable caching of remote tasks.

For comprehensive information about task arguments, see the dedicated Task Arguments page.

By default, arguments are passed to the last script in the run array. So if a task was defined as:

Then running mise run test foo bar will pass foo bar to ./scripts/test-e2e.sh but not to cargo test.

The recommended way to define arguments is using the usage field:

Arguments defined in the usage field are available as environment variables prefixed with usage_.

See the Task Arguments page for complete documentation.

Deprecated - Removal in 2027.5.0

Using Tera template functions (arg(), option(), flag()) in run scripts is deprecated and will be removed in mise 2027.5.0. Versions >= 2026.5.0 will show a deprecation warning.

Why it's being removed:

Please migrate to using the usage field instead. See the migration guide.

You can define arguments using Tera template functions (deprecated):

Then running mise run test foo bar will pass foo bar to cargo test. mise run test --e2e-args baz will pass baz to ./scripts/test-e2e.sh.

These are defined in scripts with {{arg()}}. They are used for positional arguments where the order matters.

These are defined in scripts with {{option()}}. They are used for named arguments where the order doesn't matter.

Flags are like options except they don't take values. They are defined in scripts with {{flag()}}.

The value will be true if the flag is passed, and false otherwise.

**Examples:**

Example 1 (unknown):
```unknown
build = "cargo build"
test = "cargo test"
lint = "cargo clippy"
```

Example 2 (sql):
```sql
[tasks.cleancache]
run = "rm -rf .cache"
hide = true # hide this task from the list

[tasks.clean]
depends = ['cleancache']
run = "cargo clean" # runs as a shell command

[tasks.build]
description = 'Build the CLI'
run = "cargo build"
alias = 'b' # `mise run b`

[tasks.test]
description = 'Run automated tests'
# multiple commands are run in series
run = [
    'cargo test',
    './scripts/test-e2e.sh',
]
dir = "{{cwd}}" # run in user's cwd, default is the project's base directory

[tasks.lint]
description = 'Lint with clippy'
env = { RUST_BACKTRACE = '1' } # env vars for the script
# you can specify a multiline script instead of individual commands
run = '''
#!/usr/bin/env bash
cargo clippy
'''

[tasks.ci] # only dependencies to be run
description = 'Run CI tasks'
depends = ['build', 'lint', 'test']

[tasks.release]
confirm = 'Are you sure you want to cut a new release?'
description = 'Cut a new release'
file = 'scripts/release.sh' # execute an external script
```

Example 3 (json):
```json
[env]
VERBOSE_ARGS = '--verbose'

# Vars can be shared between tasks like environment variables,
# but they are not passed as environment variables to the scripts
[vars]
e2e_args = '--headless'

[tasks.test]
run = './scripts/test-e2e.sh {{vars.e2e_args}} $VERBOSE_ARGS'
```

Example 4 (bash):
```bash
mise tasks add pre-commit --depends "test" --depends "render" -- echo pre-commit
```

---

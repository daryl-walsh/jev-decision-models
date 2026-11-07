---
name: betterleaks-config
description: Configuration and scanning guide for betterleaks — covers betterleaks.toml, config selection, hash inspection, Expr filters, and scan source patterns
doc_version: v2.0
---

# betterleaks — Configuration & Scanning Reference

## Overview

Betterleaks is a secrets-detection tool that finds credentials in source code, git history, S3, GitHub, and more. This skill covers two key areas drawn from official documentation:

1. **Configuration** (`betterleaks.toml`) — detection rules, filtering, validation, analysis, and revocation
2. **Scanning** — source selection, provider modes, concurrency, output, and allow-signatures

**Sources:**
- `documentation/overview/config.md` — Official config docs (high confidence)
- `documentation/overview/scanning.md` — Official scanning guide (high confidence)
- `config_patterns/config_patterns.md` — Config extraction report (medium confidence, 3 files, 256 settings)

---

## When to Use This Skill

Use this skill when you need to:

- **Write or audit a `betterleaks.toml`** — understand top-level shape, rule structure, and required vs optional fields
- **Select a configuration** — know the precedence order (`--config` > `BETTERLEAKS_CONFIG` > `BETTERLEAKS_CONFIG_TOML` > embedded default)
- **Inspect a resolved config** — use `config show`, `config show ids`, or `config hash` to verify what betterleaks will actually use
- **Suppress false positives** — write `prefilter` or `filter` Expr expressions, or add inline allow signatures
- **Enable credential validation or analysis** — understand `-v`/`--validate`, `-a`/`--analyze`, and the env-var equivalents
- **Tune scan concurrency** — set `-j`/`--jobs`, understand per-source I/O limits
- **Pick the right scan source** — filesystem, git, GitHub, GitLab, S3, Hugging Face, URL, stdin
- **Parse or emit structured output** — understand `--jsonl` finding envelopes and the scan result schema
- **Use the Go SDK** — call `cfg.Hash()`, `cfg.RuleHash()`, `cfg.RuleHashes()` for cache-key generation

---

## Key Concepts

### Configuration Selection Order

Betterleaks resolves configuration exactly once per scan invocation, in this priority order:

1. `--config` / `-c` (explicit path)
2. `BETTERLEAKS_CONFIG` environment variable (file path)
3. `BETTERLEAKS_CONFIG_TOML` environment variable (inline TOML string)
4. Embedded default configuration

**Important:** `.betterleaks.toml` files in scan targets are NOT loaded automatically. You must pass `--config .betterleaks.toml` explicitly.

### Provider Modes

| Flag | Short | Env var | Default | Effect |
| :--- | :--- | :--- | :--- | :--- |
| `--validate` | `-v` | `BETTERLEAKS_VALIDATE` | `false` | Enable credential validation |
| `--analyze` | `-a` | `BETTERLEAKS_ANALYZE` | `false` | Enable analysis (implies validation) |

Precedence per flag: explicit CLI flag > env var > default. Analysis implies validation after resolution — disabling validation alone does not disable analysis.

### Expr Expressions

Betterleaks uses [Expr](https://expr-lang.org/) for `prefilter`, `filter`, `validate`, `analyze`, and `revoke` fields. If a filter expression evaluates to `true`, the item is skipped.

---

## Quick Reference

### Config Inspection

```sh
# Print the fully resolved TOML config
betterleaks config show
betterleaks config show path/to/betterleaks.toml

# List all rule IDs (no provider requests made)
betterleaks config show ids
betterleaks config show ids --validation
betterleaks config show ids --analysis
betterleaks config show ids --revocation
betterleaks config show ids --analysis path/to/betterleaks.toml
```

### Config Hashing

```sh
# Hash the entire resolved config
betterleaks config hash --config custom.toml

# Hash one rule (matches finding's rule_hash field)
betterleaks config hash --config custom.toml --rule github-pat

# Use embedded defaults or env-var config
betterleaks config hash --rule github-pat

# Positional path also works
betterleaks config hash custom.toml --rule github-pat
```

The hash prints one bare SHA-256 and a newline. `--isolate-rule` or `--disable-rule` hashes the reduced config instead.

### Go SDK — Config Hashes

```go
configHash := cfg.Hash()

ruleHash, err := cfg.RuleHash("github-pat")
if err != nil {
    return err
}

// Get all rule hashes at once
ruleHashes := cfg.RuleHashes() // caller-owned map
```

### Scan Source Selection

```sh
# Filesystem (explicit or auto-detected)
betterleaks ./my-project
betterleaks auto ./my-project
betterleaks fs .

# Remote git
betterleaks https://github.com/betterleaks/betterleaks
betterleaks https://gitlab.com/group/project.git

# Cloud storage
betterleaks s3://bucket/prefix
betterleaks hf://buckets/owner/bucket
betterleaks https://huggingface.co/datasets/owner/dataset
```

### Provider Mode Control

```sh
# Enable validation via env var
BETTERLEAKS_VALIDATE=true betterleaks fs .

# Enable analysis via env var
BETTERLEAKS_ANALYZE=true betterleaks fs .

# Override env vars for this scan
betterleaks fs . --analyze=false --validate=false
```

### Scan Concurrency

```sh
# Use 8 detection workers
betterleaks filesystem . -j 8
betterleaks github https://github.com/my-company -j 8
```

Zero (default) uses `4 * GOMAXPROCS`. Detection and I/O concurrency are independent.

### Allow Signatures (suppress findings inline)

```sh
# Default allow signatures
betterleaks fs . --allow-signature betterleaks:allow --allow-signature '#nosec'
```

Add `betterleaks:allow` or `gitleaks:allow` to the line with the finding to suppress it. Matching is case-sensitive and literal.

### Automatic Source Detection (Go SDK)

```go
kind, err := sources.Auto(ctx, target)
if err != nil {
    return err // kind == sources.UnknownKind
}
switch kind {
case sources.FilesystemKind:
    // Construct sources.Files with Path: target.
case sources.GitKind:
    // Construct gogit.Source with URL: target.
case sources.URLKind:
    // Construct sources.URL with URL: target.
    // Set MaxArchiveDepth if archives should be scanned.
}
```

### JSON Output Schema

```json
{
  "schema_version": "1",
  "findings": [],
  "scan": {
    "state": "complete",
    "source": {"type": "filesystem", "targets": ["./src", "./tests"]},
    "started": "2026-09-23T17:00:00Z",
    "finished": "2026-09-23T17:00:01Z",
    "betterleaks_version": "v2.0.0-rc.1",
    "config_hash": "...",
    "bytes_scanned": 1234,
    "num_findings": 0,
    "confidence_counts": {"high": 0, "medium": 0, "low": 0, "none": 0, "other": 0},
    "severity_counts": {"high": 0, "medium": 0, "unknown": 0, "none": 0},
    "status_counts": {"valid": 0, "invalid": 0, "revoked": 0, "needs_validation": 0, "unknown": 0, "error": 0, "none": 0}
  }
}
```

Use `--jsonl` for one finding envelope per line followed by the final scan summary.

---

## Expr Filter Examples

### Accessing finding data

```expr
finding.secret
finding.captures["username"]
components["account-id"].secret
components["account-id"].captures["region"]
```

### Accessing attributes and components

```expr
attributes["path"]
components["account-id"]?.secret ?? ""
r.json?.login ?? ""
```

### Combining conditions

```expr
finding.captures["username"] == "example"
&& finding.captures["host"] == "example.invalid"
```

### Context window around a match

```expr
let providerMatchContext = finding["fragment_raw"][
    max(finding["match_start_idx"] - 150, finding["match_line_start_idx"]):
    min(finding["match_end_idx"] + 50, finding["match_line_end_idx"])
];
containsAny(providerMatchContext, ["provider"])
```

### Generic prefix extraction

```expr
let genericMatchPrefix = findMatch(
    finding["fragment_raw"][
        max(finding["match_start_idx"] - 50, finding["match_line_start_idx"]):
        finding["match_start_idx"]
    ],
    `[\w.-]{0,50}$`
);
let genericMatchContext =
    genericMatchPrefix +
    finding["fragment_raw"][finding["match_start_idx"]:finding["match_end_idx"]];
```

---

## Scanning — Source Concurrency Limits

Per-source I/O concurrency is bounded independently of detection workers (`-j`):

| Source work | Concurrency |
| :--- | :--- |
| Filesystem readers | `GOMAXPROCS` |
| Git history workers | Up to `min(GOMAXPROCS, 8)` |
| S3 and Hugging Face object reads | 4 |
| GitHub Actions runs | 4 |
| Provider repositories or buckets | One target at a time |
| URL and stdin | Serial |
| Container images and layers | Serial input; detection uses normal worker pool |

Reading and detection overlap. When detection falls behind, readers stop advancing; bounded queues prevent unbounded memory use.

---

## v1 to v2 Flag Migration

| Old flag (v1) | v2 replacement |
| :--- | :--- |
| `--validation-workers` | `--provider-workers` |
| `--validation-debug` | `--provider-debug` |
| `--validation-timeout` | `--provider-timeout` |
| `--validation-max-requests` | `--provider-max-requests` |
| `--validation-rps` | `--provider-rps` |
| `--validation-rps-rule` | `--provider-rps-rule` |
| `--validation-env-vars` | `--provider-env-vars` |

Also: `-v` / `--version` is now `-V` / `--version`; lowercase `-v` enables validation.

---

## Encoding Detection

```json
{
  "encodings": ["percent", "base64"],
  "decode_depth": 3
}
```

Betterleaks can decode nested encodings up to `decode_depth` levels.

---

## Working with This Skill

**Beginners:** Start with "Config Inspection" to see what betterleaks will use, then "Scan Source Selection" for your target type.

**Intermediate:** Use Expr filter examples to suppress false positives. Check "Provider Mode Control" for validation/analysis flags.

**Advanced:** Use the Go SDK hash methods (`cfg.Hash()`, `cfg.RuleHash()`) as cache keys. Study the JSON output schema for pipeline integration. Write context-window Expr expressions for precise filtering.

**Navigating references:**
- `references/documentation/overview/config.md` — Full config reference (high confidence)
- `references/documentation/overview/scanning.md` — Full scanning guide (high confidence)
- `references/config_patterns/` — Extracted config file patterns (medium confidence; 3 files, 256 settings, no named patterns detected)

---

## Available References

| Reference | Contents | Confidence |
| :--- | :--- | :--- |
| `references/documentation/overview/config.md` | betterleaks.toml top-level shape, Expr data variables, filter functions, hash semantics | High |
| `references/documentation/overview/scanning.md` | Source selection, provider modes, concurrency, output formats, allow signatures | High |
| `references/config_patterns/config_patterns.md` | Config extraction summary (3 files, 256 settings) | Medium |
| `references/dependencies/` | Dependency graph and analysis | — |

---

**Enhanced from official betterleaks documentation** | Sources: config.md, scanning.md (high confidence)

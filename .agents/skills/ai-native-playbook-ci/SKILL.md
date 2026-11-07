---
name: ai-native-playbook-ci
description: Practical guidance for AI-native CI/CD — continuous evals, AI in the PR review loop, hooks as approval gates, Claude in CI/CD pipelines, and autonomous monitoring with control bands (Stages 4–6 of the AI-Native SDLC Playbook).
doc_version: "1.0"
---

# AI-Native Playbook: CI, Deploy & Maintain

## Description

This skill covers the CI/CD and post-build stages of the AI-Native SDLC Playbook: how to run continuous evals as regression gates, integrate Claude into the PR review loop, enforce approval gates through hooks, run Claude non-interactively in CI/CD pipelines, and close the loop autonomously with control-band monitoring.

**Source:** Documentation (7 files, high confidence)
**Stages covered:** Test (4) → Deploy (5) → Maintain (6)
**Reference docs:** `references/documentation/`

---

## When to Use This Skill

Load this skill when you need to:

- **Write or run continuous evals in CI** — gate configuration changes (CLAUDE.md, skills, hooks) on a pass/fail eval suite
- **Set up AI in the PR review loop** — have Claude run multi-pass reviews (bugs, security, compliance) on every PR
- **Build hooks as approval gates** — block, ask, or allow agent actions based on environment or change-ticket status
- **Run Claude non-interactively in CI/CD** — use `claude -p` for judgment steps (triage, changelog, lint fix) inside pipelines
- **Expose deployment through MCP** — give the agent scoped deploy/rollback tools per environment
- **Set up autonomous monitoring** — detect control-band breaches and trigger Claude to diagnose and act without a human starting the loop
- **Understand governance trade-offs** at each automation tier

---

## Key Concepts

### The Plays (Stages 4–6)

| Play | Stage | What it does |
|------|-------|--------------|
| **09 — Continuous evals in CI** | Test (4) | Eval suite runs on every change to CLAUDE.md, skills, or hooks; gates merges on pass rate |
| **10 — AI in the PR review loop** | Test (4) | Claude runs bug / security / compliance passes on every PR; humans review behavior and risk |
| **11 — Hooks as approval gates** | Deploy (5) | Hooks enforce release gates per environment; managed settings make gates non-bypassable |
| **12 — CI/CD integration & deployment** | Deploy (5) | Claude runs non-interactively in pipelines; deployment exposed through scoped MCP tools |
| **13 — Closing the loop on metrics** | Maintain (6) | Detection script monitors control bands; breaches invoke Claude autonomously via gated routes |

### Eval Suite

Evals are the AI-native equivalent of stage-gate QA. They are a live suite: as models improve, discriminating cases must be refreshed. Each production incident should produce a new eval that stays in the suite as a regression test.

### Control Band

A control band is a range around a metric's normal level:
- Mean = average of last 30 days of hourly readings
- Sigma (σ) = standard deviation of those readings
- **1σ tier**: log only (chance noise triggers ~4×/day at 720 readings/month)
- **2σ tier**: investigate (noise triggers ~16×/month)
- **3σ tier**: act through gated routes (noise triggers ~1×/month)
- **Western Electric rules**: catch slow drift — flag if 4 of last 5 readings exceed 1σ, or 8 in a row exceed mean

### Autonomy Tiers (CI/CD)

| Environment | Autonomy level |
|-------------|---------------|
| Development | Agent deploys freely |
| Staging | Agent deploys; humans review |
| Production | Agent prepares; release manager authorizes; hook enforces gate |

---

## Quick Reference

### 1. Eval file structure (from official docs — play 09)

```json
{
  "from": "<commit-sha-before-PR>",
  "prompt": "Check that claims-api does not log request or response bodies.",
  "allowed_paths": ["claims-api/"],
  "checks": [
    { "type": "script", "command": "scripts/check-endpoints.sh" },
    { "type": "script", "command": "evals/log_bodies.py" }
  ]
}
```

*Save as `evals/<name>.json`. Run non-interactively in CI on a schedule and on any change to `CLAUDE.md`, skills, or hooks.*

### 2. CLAUDE.md review instructions (from official docs — play 10)

```markdown
# Review instructions
## Passes
Run three passes and tag each finding with its pass:
- Bugs: logic errors, broken edge cases, subtle regressions
- Security: injection risks, authentication gaps, PII in logs
- Compliance: the change matches spec.md, plan.md and our design principles
## What Important means here
Reserve Important for findings that would break behavior, leak data
or breach a policy. Style and naming are nits.
## Cap the nits
Report at most five nits per review; summarize the rest as a count.
## Do not report
Generated files under src/gen/ and anything CI already enforces.
```

### 3. Hook configuration for a release gate (from official docs — play 11)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__deploy-.*__release",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/release-gate.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

*Store team hooks in `.claude/settings.json` (in Git). Store non-bypassable hooks in managed settings owned by the platform or IT admin.*

### 4. Release gate shell hook (from official docs — play 11)

```bash
#!/bin/bash
# dev: allow. staging: ask. production: require approved change ticket.
input=$(cat)
tool=$(jq -r '.tool_name' <<<"$input")

env=$(echo "$tool" | sed 's/mcp__deploy-\(.*\)__release/\1/')

case "$env" in
  dev)      exit 0 ;;
  staging)  echo '{"action":"ask","message":"Deploy to staging — confirm?"}'; exit 0 ;;
  prod)
    ticket=$(jq -r '.tool_input.ticket // empty' <<<"$input")
    if [[ -z "$ticket" ]]; then
      echo '{"action":"block","message":"Production deploy requires an approved change ticket."}'; exit 1
    fi
    # verify ticket approval via your change-management API ...
    ;;
esac
```

### 5. Running Claude non-interactively in CI (from official docs — play 12)

```yaml
# GitHub Actions example — judgment step
- name: Triage failed build
  run: claude -p "$(cat .claude/prompts/triage-build.md)" --output-format json
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

*Start with read-only judgment steps (triage, changelog, summarize flaky tests). Add write steps behind existing gates only after read-only steps are stable.*

### 6. Control-band monitoring config (from official docs — play 13)

```yaml
# bands.yaml — monitor CI test failure rate
metric: ci_test_failure_rate
source:
  type: prometheus
  query: 'rate(ci_tests_failed_total[1h])'
bands:
  1sigma: log
  2sigma: investigate
  3sigma: act
western_electric: true
on_breach:
  command: claude -p evals/diagnose-breach.md
  allowed_paths: ['./', 'reports/']
  gates: [hooks/release-gate.sh]
```

---

## Working with This Skill

### For engineers new to AI-native CI

1. Start with **play 09** — write 20–50 evals from recent real tasks before touching CI automation.
2. Add **play 10** (PR review) next — it has no infrastructure prerequisites beyond an updated CLAUDE.md.
3. Introduce **play 11** (hooks) before adding any write automation to pipelines.
4. Only then layer in **play 12** (CI/CD) write steps, starting with dev and staging.

### For platform engineers

- Put team-level hooks in `.claude/settings.json` committed to the repo.
- Put non-negotiable (compliance, regulated) hooks in managed settings distributed via MDM or the admin console — individual engineers cannot override these.
- Scope MCP deploy servers per environment; do not expose a single server with production credentials to all pipeline jobs.
- Sandbox agent CI jobs in containers with a network policy and short-lived scoped tokens. No standing production credentials.
- Rehearse the rollback path in staging before enabling autonomous production action in play 13.

### For advanced / autonomy tier 3

- Play 13's autonomous loop requires `intent.md` (play 01), Claude-accelerated PR reviews (play 10), hooks as action boundaries (play 11), and a proven rollback path (play 12).
- The detection script should query your metrics store (Prometheus, CI API, etc.) on a schedule and invoke `claude -p` or the Agent SDK when a band is breached.
- Each breach tier maps to a different action: 1σ → log, 2σ → investigate and file a ticket, 3σ → diagnose + open PR through gated routes.

---

## Reference File Guide

| File | Content | Confidence |
|------|---------|------------|
| `references/documentation/09-continuous-evals-in-CI.md` | Full eval setup, example eval JSON, `log_bodies.py` script, governance considerations, live-suite management | High |
| `references/documentation/10-AI-in-the-PR-review-loop.md` | PR review pass structure, CLAUDE.md review block, traditional vs. AI-native comparison, governance | High |
| `references/documentation/11-Hooks-as-approval-gates.md` | Hook JSON config, release-gate.sh example, managed settings for regulated enterprises, governance | High |
| `references/documentation/12-CI_CD_integration_deployment.md` | CI/CD autonomy tiers, sandboxing, MCP deployment pattern, rollback rehearsal | High |
| `references/documentation/13-closing-the-loop-on-metrics.md` | Control band math, Western Electric rules, `bands.yaml`, detection script, Claude Tag (public beta) | High |
| `references/documentation/14-closing-thoughts-resources.md` | Resource list for platform teams, rollout order recommendations | High |
| `references/documentation/SKILL.md` | Full AI-Native SDLC Playbook SKILL.md covering all six stages | High |

*All reference files are in `references/documentation/`. The SKILL.md in that directory covers the complete playbook (all six stages); this skill focuses on stages 4–6.*

---

## Governance Considerations

| Play | Governance point |
|------|-----------------|
| Continuous evals | Gate config changes on pass rate; write an eval for every production incident |
| PR review | All PRs get identical review passes; humans judge behavior and risk, not style |
| Hooks | Gate conditions enforced for everyone; allow/block decisions logged with timestamps |
| CI/CD | Branch protection prevents agent from pushing to main; write steps arrive as PRs |
| Metrics loop | Gated routes only at 3σ; rollback must be rehearsed before autonomous invocation |

---

## Traditional vs. AI-Native Comparison

| Concern | Traditional | AI-native |
|---------|-------------|-----------|
| PR review capacity | Planned around human output; backlog grows under load | All PRs get identical multi-pass review; humans focus on intent and risk |
| Deployment judgment | Humans follow runbooks under pressure | Claude prepares; gates enforce approval; humans authorize |
| Incident response | Alert fires at 3 a.m.; may be missed; post-mortem actions may not reach codebase | Control band breach invokes Claude; diagnoses and acts through gated routes; people triage, not start |

---

**Source:** AI-Native SDLC Playbook — documentation (7 files, high confidence)
**Reference docs:** `references/documentation/`

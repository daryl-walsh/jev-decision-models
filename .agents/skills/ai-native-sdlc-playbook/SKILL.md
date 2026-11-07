---
name: ai-native-sdlc-playbook
description: Practical guidance for transforming software development with AI — covering all six SDLC stages (Plan, Design, Build, Test, Deploy, Maintain) using Claude Code, intent-driven workflows, skills as institutional knowledge, and continuous evals.
doc_version: "1.0"
---

# AI-Native SDLC Playbook

## Description

The AI-Native SDLC Playbook documents how organizations can transform each stage of the software development lifecycle using Claude and Claude Code. It describes the shift from traditional, human-authored processes to AI-native workflows where Claude generates, verifies, and maintains software artifacts — while humans review and steer.

The playbook is organized as **modular plays** grouped into six non-linear stages. Organizations can adopt individual plays in any order based on where they see the highest value.

**Source:** Documentation (9 files, high confidence)  
**Stages:** Plan → Design → Build → Test → Deploy → Maintain  
**Reference docs:** `references/documentation/`

---

## When to Use This Skill

Load this skill when you need to:

- **Adopt a specific SDLC play** — e.g., "how do I set up plan mode?" or "how do I write skills for institutional knowledge?"
- **Understand how traditional vs. AI-native workflows differ** at any stage of the lifecycle
- **Structure an intent.md, spec.md, or plan.md** artifact correctly
- **Configure CLAUDE.md or AGENTS.md** so Claude has the context a new joiner would need
- **Set up skills** to make organizational policies (security, brand, compliance) operationally enforced
- **Design parallel sessions or subagents** for concurrent work streams
- **Add a feedback loop** so an agent can verify its own work before a human reviews it
- **Write continuous evals in CI** to catch regressions whenever CLAUDE.md or skills change
- **Onboard a team** to AI-native development practices from traditional SDLC

---

## Key Concepts

### The Six Stages

| Stage | Traditional bottleneck | AI-native shift |
|-------|------------------------|-----------------|
| **Plan** | Ideas stay in heads or tickets | Claude produces `intent.md` from a brainstorm; product owner reviews before commit |
| **Design** | Analysts write requirements, designers parse them — slow and lossy | Single prompted session: Claude takes `intent.md` and outputs `requirements + design spec` |
| **Build** | Engineer starts coding directly; reviewers see finished diff | Claude starts in plan mode, produces `plan.md`; engineer corrects before code is written |
| **Test** | Manual QA stage-gates | Agent verifies its own work via feedback loop; CI runs continuous evals |
| **Deploy** | Separate ops team | Not detailed in this version of the playbook |
| **Maintain** | Incidents trigger manual follow-up | Incidents surface as triggers for new `intent.md` artifacts; evals catch regressions |

### Core Artifacts

- **`intent.md`** — Human-readable proto-spec capturing the problem, proposed outcome, affected systems, constraints, and open questions. Authored by Claude from a brainstorm; reviewed and committed by the product owner.
- **`spec.md`** (requirements + design) — Produced by Claude from `intent.md`, constrained by organizational skills; reviewed but not written by the product owner.
- **`plan.md`** — Implementation plan produced by Claude in plan mode, naming files that change, the order of work, and tests that prove it. Reviewed and committed before code is written.
- **`CLAUDE.md`** — Repository-level context file Claude reads at session start: conventions, commands, architecture, common mistakes.
- **`AGENTS.md`** — Similar to CLAUDE.md, the project-level instructions for agents.
- **Skills** — Policy-as-code: a folder with a `SKILL.md` whose frontmatter defines when it triggers and whose body defines what to do.

### Plays vs. Stages

Plays are modular. Each play maps to a stage but can be adopted independently. Organizations pick their first play based on where pain is highest — not on sequential order.

---

## Quick Reference

### Play 1 — Capture Intent (`intent.md`)

**Stage: Plan**

A person brainstorms with Claude; Claude produces a Markdown proto-spec. The product owner reviews and corrects it before it is committed as `intent.md`. Whether the input is a human idea, a filed ticket, or an incident alert, the same steps apply.

```markdown
# Intent: claims status self-service
Author: J. Ortiz (claims operations). Status: draft.

## Problem
Customers phone the contact center to ask where their claim is.
Handlers spend roughly a third of call time on status-only queries.

## Proposed outcome
Customers see claim status, next step and expected date in the portal.

## Affected users and systems
Claims handlers, portal team, claims-core API.

## Constraints
No new PII in the portal session. Existing authentication only.

## Open questions
Do third-party loss adjusters need access too?
```

**What changes:** The proto-spec is human-readable, version-controlled, and immediately consumable by the next stage — no hand-off friction.

---

### Play 2 — Requirements and Design (`spec.md`)

**Stage: Design**

Claude takes `intent.md` and produces a combined requirements-and-design spec, constrained by the organization's skills (brand, security, compliance, UX). The product owner reviews, flags areas of concern, and approves before the engineering team plans against it.

For front-end work: the product owner mocks the design in Claude Design from `intent.md`, iterates, then exports to Claude Code to build.

**Prerequisites:** `intent.md` + skills for brand, security, compliance, UX policies.

**What changes:** Requirements and design happen in a single session instead of two sequential phases run by separate teams.

---

### Play 3 — Plan Mode as Default Start (`plan.md`)

**Stage: Build**

Engineers start Claude Code in plan mode, feed it `spec.md`, and let Claude interview them — iterating until the plan is approved. The approved `plan.md` names every file that changes, the order of work, and the tests that prove it.

**How to execute:**
1. Start a Claude Code session in plan mode (`/plan` or `--plan`).
2. Provide `intent.md` and `spec.md`.
3. Ask for an implementation plan: files that change, order of work, tests that prove it.
4. Correct the plan. Commit `plan.md`.
5. Later stages check work against `plan.md`.

**Prerequisites:** `intent.md` or `spec.md` (if it exists); `CLAUDE.md` helps.  
**Infrastructure:** Claude Code with repository access.

**What changes:** The plan is written down and reviewable before any code is written. First-review friction drops because reviewers can check the diff against the committed plan.

---

### Play 4 — CLAUDE.md and AGENTS.md

**Stage: Build (ongoing)**

`CLAUDE.md` gives Claude the context a new joiner would need: conventions, commands, architecture, and the mistakes the team sees most often. Knowledge that used to sit in people's heads becomes a file the agent reads at the start of every session, maintained by the whole team.

**How to create:**
1. Run `/init` in the repo. Claude generates a starting `CLAUDE.md` from what it finds.
2. The team iterates on it whenever a mistake is made.

**What it covers:** Conventions, commands, architecture, common mistakes, links to key docs.

**Prerequisites:** None. A repo and Claude Code installed.

---

### Play 5 — Skills as Institutional Knowledge

**Stage: Any**

Skills make organizational policies operational. A skill is a folder containing a `SKILL.md` whose frontmatter says when it triggers and whose body says what to do.

**Rule of thumb:** Write a skill for institutional knowledge that must be applied consistently. Put components that are repo-specific in `CLAUDE.md` instead.

**How to create a skill:**
1. Pick one piece of knowledge enforced inconsistently today (a security standard, API design convention, brand rule).
2. Write it as a `SKILL.md` with frontmatter trigger conditions and a body with instructions.
3. Place it at `.claude/skills/<skill-name>/SKILL.md` (repo-scoped) or distribute via plugin (org-wide).
4. Test that the skill triggers: ask Claude to do the task in different ways and confirm the skill loads each time.
5. When policy changes, update the skill and have the policy owner sign off.
6. Engineers pick up the new version automatically in their next session.

**Example — `.claude/skills/secure-api-review/SKILL.md`:**

```markdown
# Secure API review

When you create or change an API endpoint:
1. Authentication: every endpoint requires the gateway JWT;
   no anonymous routes outside /health.
```

**Prerequisites:** None required. `CLAUDE.md` helps, but a skill does not depend on it.

---

### Play 6 — Parallel Sessions and Subagents

**Stage: Build**

**Parallel sessions:** Multiple full Claude Code instances, each working a separate task in its own Git worktree. Each session knows nothing about the others; the engineer is the only shared element.

**Subagents:** A scoped helper running inside a single session with its own context window and tool limits. Use for jobs that recur in multiple tasks — e.g., verifying the app runs correctly after each change.

**Example subagent definition (`AGENTS.md` or inline):**

```markdown
---
name: verifier
description: Runs the app and checks the change works before the session reports done
tools: Bash, Read
---

Start the app with make run. Exercise the changed behavior and the two
nearest neighboring flows. Report what you ran, what you saw, and any
behavior that does not match plan.md. Do not fix anything; report only.
```

**What changes:** One engineer can drive several work streams at once. Parallel sessions raise throughput; subagents keep each session focused.

**Prerequisites:** `CLAUDE.md` (all sessions read it). The feedback loop (Play 7) reduces supervision needed.

---

### Play 7 — Give the Agent a Feedback Loop

**Stage: Test**

Always give Claude a way to verify its own work — tests, a build, or a screenshot diff. The agent checks its own work and fixes mistakes before a human sees them.

**Feedback loop vs. verifier subagent:**
- **Feedback loop:** Runs continuously throughout the task, as many times as needed.
- **Verifier subagent:** A one-shot final check in a fresh context window once the session believes the work is done. The fresh context means the verdict isn't colored by assumptions that produced the code.

Use both: the loop for ongoing self-correction, the verifier for the final gate.

**Prerequisites:** Tests, a build command, or a visual diff mechanism.

---

### Play 8 — Continuous Evals in CI

**Stage: Test / Deploy**

Evals are the AI-native equivalent of stage-gate QA. They run whenever the agent's configuration changes — new model, rewritten prompt, changed skill, modified `CLAUDE.md`. The suite says whether the agent still does the work to the same standard.

**How to set up:**
1. Collect 20–50 real tasks from recent work, each with an expected or accepted outcome.
2. Write each as an eval: prompt + checks (tests pass, lint clean, behavior unchanged, policy followed).
3. Run the suite non-interactively in CI on a schedule and on any change to `CLAUDE.md`, skills, or hooks.
4. Gate configuration changes on results. A skill change that drops the pass rate gets reviewed before merge.
5. Each production incident becomes an eval, written by the team that owned it, staying in the suite as a regression test.

**Example eval file (`evals/status-no-pii-in-logs.json`):**

```json
{
  "from": "<last-commit-before-the-relevant-PR>",
  "prompt": "Add the /claims/{id}/status endpoint to claims-api",
  "allowed_folders": ["src/claims-api"],
  "checks": [
    { "type": "tests_pass" },
    { "type": "lint_clean" },
    { "type": "script", "path": "scripts/check-endpoints.sh" },
    { "type": "script", "path": "evals/scripts/log_bodies.py" }
  ]
}
```

**Live suite:** As models improve, cases that once discriminated stop doing so. Add new cases from ongoing monitoring.

**Prerequisites:** `CLAUDE.md` and a working feedback loop (Play 7). CI that can run Claude Code non-interactively, API key with eval budget.

---

## Working with This Skill

### Beginners — Where to start

1. **Read Play 1 (intent.md)** — even if you don't adopt anything else, structured intent captures reduce rework.
2. **Run `/init`** in your main repo to generate a starting `CLAUDE.md` (Play 4). This is the highest-leverage first action.
3. **Pick one play** based on your biggest pain point, and run it for one real task before expanding.

### Intermediate — Building the system

- Pair **Play 3 (plan mode)** with **Play 7 (feedback loop)** — plan first, then let the agent self-verify. This combination cuts review cycles significantly.
- Write your first **skill (Play 5)** around a policy that gets violated inconsistently. Start narrow: one rule, one enforcement check.
- Use **parallel sessions (Play 6)** once your `CLAUDE.md` is stable enough that each session starts with reliable context.

### Advanced — Full adoption

- Wire **evals into CI (Play 8)** so that any change to `CLAUDE.md` or skills is regression-tested automatically.
- Treat every production incident as an eval: write it, add it to the suite, and block future regressions.
- Use **verifier subagents** alongside feedback loops so final verification happens in a clean context window.
- Maintain skills as living policy documents — have the policy owner sign off on every change.

---

## Navigating Reference Documentation

All detailed source content is in `references/documentation/`:

| File | Content | Stage |
|------|---------|-------|
| `overview/01-what-changes-where-to-start.md` | The traditional→AI-native shift table across all 6 stages; how plays work; how to pick a first play | All |
| `overview/02-capture-intent.md` | intent.md structure, example, what changes, product owner workflow | Plan |
| `architecture/03-Requirements-and-design.md` | requirements+design spec workflow, front-end mock flow, traditional vs. AI-native comparison | Design |
| `overview/04-Plan-mode-as-the-default-start.md` | Plan mode how-to, plan.md content, prerequisites, step-by-step | Build |
| `overview/05-Agents-md_Claude-md.md` | CLAUDE.md content guide, `/init`, example for insurer portal | Build |
| `overview/06-skills-as-institutional-knowledge.md` | Skill creation steps, skill vs. CLAUDE.md distinction, example secure-api-review skill | Any |
| `overview/07-parallel-sessions-and-subagents.md` | Parallel session vs. subagent distinction, verifier subagent example | Build |
| `overview/08-give-agent-a-feedback-loop.md` | Feedback loop vs. verifier subagent, when to use each | Test |
| `overview/09-continuous-evals-in-CI.md` | Eval structure, CI setup, example eval JSON, live suite maintenance | Test/Deploy |

---

## Source Quality

All 9 documentation files were rated **high confidence**. There is a single source type (documentation), so no cross-source conflicts exist. The examples in this skill are drawn directly from the reference documents verbatim where practical.

---

*Enhanced from `references/documentation/` — 9 source files, documentation type, high confidence.*

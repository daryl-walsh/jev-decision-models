---
name: ai-native-playbook
description: AI-native SDLC playbook — plays, artifacts, and practices for transforming software development with Claude Code across Plan, Design, Build, Test, Deploy, and Maintain stages
doc_version: "1.0"
---

# AI-Native Playbook

## Description

This skill captures the AI-native software development lifecycle (SDLC) playbook: the plays, artifacts, and practices for transforming how organizations build software using Claude Code. It covers all six SDLC stages — Plan, Design, Build, Test, Deploy, and Maintain — with concrete guidance on when and how to apply each play.

**Source:** 8 documentation files across overview and architecture categories (all high confidence)
**Coverage:** Stages 1–6 of the AI-native SDLC
**References:** `references/documentation/` — full source documents

---

## When to Use This Skill

Use this skill when you need to:

- **Start an AI-native session**: Understand what artifact to create first (intent.md, spec.md, plan.md) and in what order
- **Write or review an intent.md**: Know the required sections and what the product owner must approve before moving forward
- **Generate a requirements and design spec**: Know how Claude takes intent.md and produces a spec, and what policies constrain it
- **Open a Claude Code build session**: Know to start in plan mode, give Claude the spec, and commit the resulting plan.md
- **Write or maintain a CLAUDE.md**: Understand what belongs in it vs. a skill vs. a prompt
- **Create or update a skill**: Know when institutional knowledge belongs in a skill (consistent enforcement, policy-owned) vs. CLAUDE.md
- **Run parallel sessions or subagents**: Know the difference and when to use each
- **Set up a feedback loop**: Give an agent a way to verify its own work before reporting done
- **Explain the AI-native SDLC to a team**: Use the Traditional vs. AI-native comparison tables as the basis

---

## Key Concepts

### The Six Stages

The playbook groups plays into six non-linear stages:

| Stage | Traditional | AI-native shift |
|---|---|---|
| **Plan** | Ticket filed, requirements written by analysts | intent.md captures the idea; product owner reviews before commit |
| **Design** | Separate requirements + design phases, different teams | Single prompted session; Claude produces spec from intent.md |
| **Build** | Engineer reads design, writes code, plan stays in their head | Plan mode first; Claude produces plan.md; engineer approves before code |
| **Test** | Tests written after code; agent has no feedback loop | Agent given tests/build/screenshot diff to verify its own work |
| **Deploy** | Manual coordination | Agent-assisted deploy with verification |
| **Maintain** | Incidents surface via alerts; handled ad hoc | Alert triggers intake; same intent → spec → plan → build flow |

### Core Artifacts

| Artifact | Stage | Owner | Purpose |
|---|---|---|---|
| `intent.md` | Plan | Product owner | Human-readable proto-spec; reviewed and committed before next stage |
| `spec.md` | Design | Product owner | Requirements + design in one doc; constrained by org skills |
| `plan.md` | Build | Engineer | Named files, order of work, tests that prove it; committed before code |
| `CLAUDE.md` | All | Engineering team | Context a new joiner would need; read by agent at every session start |
| Skill (`SKILL.md`) | All | Policy owner | Institutional knowledge applied consistently; version controlled |

### Skills vs. CLAUDE.md vs. Prompts

- **Skill**: Institutional knowledge that must be enforced consistently across the org. Policy-owned, centrally updated, triggers automatically. Example: security review rules for every API endpoint.
- **CLAUDE.md**: Repo-specific context — conventions, commands, architecture, common mistakes. Written for the repo, maintained by the team, iterated when a mistake recurs.
- **Prompt**: One-off instruction for a specific task. Not worth capturing as a skill or CLAUDE.md entry.

Rule of thumb from the docs: *write a skill for institutional knowledge that must be applied consistently; don't write a skill for components that belong in CLAUDE.md or a prompt.*

---

## Quick Reference

### intent.md — Required Sections

```markdown
# Intent: <title>
Author: <name> (<role>). Status: draft.

## Problem
<What is happening now that should not be, or not happening that should be>

## Proposed outcome
<What the system does after this change>

## Affected users and systems
<Who and what this touches>

## Constraints
<Non-negotiable limits — security, compliance, performance, compatibility>

## Open questions
<Unresolved decisions that the next stage must address>
```

*From: `references/documentation/overview/02-capture-intent.md`*

---

### Verifier Subagent — AGENTS.md Snippet

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

*From: `references/documentation/overview/07-parallel-sessions-and-subagents.md`*
Purpose: The verifier runs in a fresh context window once the session believes work is done — so its verdict is not colored by the assumptions that produced the code.

---

### Skill File — Secure API Review Example

```markdown
# Secure API review
When you create or change an API endpoint:
1. Authentication: every endpoint requires the gateway JWT;
   no anonymous routes outside /health.
```

*From: `references/documentation/overview/06-skills-as-institutional-knowledge.md`*
Path: `.claude/skills/secure-api-review/SKILL.md`

---

### Plan Mode Build Flow

```
1. Engineer starts session in plan mode
2. Engineer gives Claude: intent.md + spec.md
3. Claude produces plan.md naming:
   - Files that change
   - Order of the work
   - Tests that prove it
4. Engineer reviews and corrects the plan
5. Approved plan.md committed to repo
6. Code is written against the plan
```

*From: `references/documentation/overview/04-Plan-mode-as-the-default-start.md`*

---

### Skill Creation Checklist

```
1. Pick one piece of knowledge enforced inconsistently today
   (security standard, API convention, brand rule)
2. Write it as a skill: folder + SKILL.md with frontmatter
   (when it triggers, what to do)
3. Place at .claude/skills/<skill-name>/ (repo-level)
   or distribute org-wide via a plugin
4. Test: ask Claude to do the relevant task in different ways;
   confirm the skill loads each time
5. When policy changes, update the skill; policy owner signs off
6. Engineers pick up the new version automatically next session
```

*From: `references/documentation/overview/06-skills-as-institutional-knowledge.md`*

---

### Feedback Loop vs. Verifier Subagent

| | Feedback Loop | Verifier Subagent |
|---|---|---|
| **Runs** | Throughout the task, as many times as needed | Once, after session believes work is done |
| **Context** | Same session context | Fresh context window |
| **Purpose** | Self-correction during work | Independent final verdict |
| **Defined in** | Session setup / CLAUDE.md | AGENTS.md subagent definition |

*From: `references/documentation/overview/08-give-agent-a-feedback-loop.md`*

---

### Parallel Sessions vs. Subagents

| | Parallel Session | Subagent |
|---|---|---|
| **What it is** | Full Claude Code instance in its own Git worktree | Scoped helper inside one session |
| **Knows about other sessions** | No | Depends on what it's given |
| **Best for** | Independent streams of work running simultaneously | Recurring scoped jobs within a task |
| **Engineer's role** | Steering and reviewing all sessions | Setting up the subagent definition |

*From: `references/documentation/overview/07-parallel-sessions-and-subagents.md`*

---

## Working with This Skill

### Beginner

Start with the six stages. Read `01-what-changes-where-to-start.md` in `references/documentation/overview/` — it has the Traditional vs. AI-native comparison table for all stages and explains how the plays are modular (you don't have to transform all stages at once).

Pick your first play based on the biggest pain point in your current process:
- **Unclear specs causing rework** → Stage 1: Capture intent + Stage 2: Design
- **Engineers not knowing the codebase** → Stage 3: Build (CLAUDE.md + plan mode)
- **Policy drift and inconsistent enforcement** → Stage 3: Build (skills as institutional knowledge)
- **Agents making mistakes and not catching them** → Stage 4: Test (feedback loops + verifier subagent)

### Intermediate

Once you have intent.md and CLAUDE.md working, add skills for your highest-priority policies. Use the skill creation checklist above. Install skills at `.claude/skills/<name>/` so they ship with the code.

For each skill, confirm it triggers: ask Claude to do the relevant task in multiple ways and check that the skill loads.

### Advanced

Set up parallel sessions for independent streams of work. Define a verifier subagent in AGENTS.md to give each session an independent final check. Integrate the feedback loop (tests, build, screenshot diff) so agents self-correct before an engineer sees the output.

When policy changes, the workflow is: update the skill → policy owner signs off → engineers pick up the new version automatically next session.

---

## Stage-by-Stage Reference

### Stage 1 — Plan: Capture Intent

**Goal:** Produce a human-readable `intent.md` that the product owner approves before any design or code starts.

**Entry points:**
- A person has an idea → brainstorm with Claude → proto-spec → intent.md
- A ticket is filed → converted to intent.md format
- An incident is surfaced via alert → same intake flow (see Stage 6: Maintain)

**Key rule:** The product owner reviews and corrects the agent-written intent.md before it is committed. The proto-spec generated by Claude is version-controlled and immediately consumable by the next stage.

**Reference:** `references/documentation/overview/02-capture-intent.md`

---

### Stage 2 — Design: Requirements and Design

**Goal:** Claude takes intent.md and produces a requirements and design spec in a single prompted session, constrained by org skills (brand, security, compliance, UX).

**What changes:**
- Traditional: Requirements and design are separate phases run by separate teams. Lossy handoff between analysts and designers.
- AI-native: Both phases in a single session. Claude produces spec.md; product owner reviews (does not write it). Areas of concern are flagged.

**Front-end note:** Product owner mocks the design in Claude Design from intent.md, iterates on the mock, then exports to Claude Code to build.

**Prerequisites:** intent.md, plus skills for brand/security/compliance/UX policies.

**Reference:** `references/documentation/architecture/03-Requirements-and-design.md`

---

### Stage 3 — Build: Plan Mode + CLAUDE.md + Skills

**Three plays in this stage:**

#### Play: Plan Mode as Default Start

Engineers start Claude Code sessions in plan mode. Claude reads the codebase without changing anything, interviews the engineer, and produces plan.md. The engineer corrects the plan before code is written.

**Prerequisites:** intent.md and spec.md (if they exist); CLAUDE.md helps.
**Infrastructure:** Claude Code with repo access.

**Reference:** `references/documentation/overview/04-Plan-mode-as-the-default-start.md`

#### Play: CLAUDE.md

CLAUDE.md gives Claude the context a new joiner would need: conventions, commands, architecture, and the mistakes the team sees most often. Knowledge that used to sit in people's heads and on wikis becomes a file the agent reads at the start of every session, maintained by the whole team, iterated whenever a mistake recurs.

**How to start:** Run `/init` in the repo. Claude generates a starting CLAUDE.md from what it finds.

**Reference:** `references/documentation/overview/05-Agents-md_Claude-md.md`

#### Play: Skills as Institutional Knowledge

Skills make institutional knowledge operational: explicit, version-controlled, applied broadly, updated centrally when policy changes.

**Reference:** `references/documentation/overview/06-skills-as-institutional-knowledge.md`

---

### Stage 4 — Test: Feedback Loops + Verifier Subagent

**Goal:** Give the agent a way to verify its own work so it catches mistakes before an engineer sees them.

**Feedback loop:** Tests, a build, or a screenshot diff. Runs throughout the task as many times as the work requires. The agent self-corrects.

**Verifier subagent:** One way to package the final check. Runs in a fresh context window once the session believes the work is done. Because it starts fresh, its verdict is not colored by the assumptions that produced the code.

**Reference:** `references/documentation/overview/08-give-agent-a-feedback-loop.md`

---

### Stages 5–6 — Deploy and Maintain

Stage 6 (Maintain) closes the loop: incidents surfaced via alerts trigger the same intake flow as a new idea — intent.md → spec.md → plan.md → code. The same plays apply.

---

## Reference Files

| File | Content | Confidence |
|---|---|---|
| `references/documentation/overview/01-what-changes-where-to-start.md` | Full Traditional vs. AI-native comparison table for all stages; how the plays are organized; how to pick your first play | High |
| `references/documentation/overview/02-capture-intent.md` | Intent.md format, the three entry points (idea/ticket/alert), what changes in the capture stage | High |
| `references/documentation/architecture/03-Requirements-and-design.md` | Requirements and design stage; how Claude takes intent.md and produces spec.md; front-end design workflow | High |
| `references/documentation/overview/04-Plan-mode-as-the-default-start.md` | Plan mode workflow; plan.md contents; step-by-step how to execute it | High |
| `references/documentation/overview/05-Agents-md_Claude-md.md` | What goes in CLAUDE.md; how to initialize it with /init; example from an insurer's customer portal | High |
| `references/documentation/overview/06-skills-as-institutional-knowledge.md` | Skills vs. CLAUDE.md vs. prompts; skill creation checklist; secure API review example | High |
| `references/documentation/overview/07-parallel-sessions-and-subagents.md` | Parallel sessions vs. subagents; verifier subagent AGENTS.md example | High |
| `references/documentation/overview/08-give-agent-a-feedback-loop.md` | Feedback loop vs. verifier subagent distinction; what counts as a feedback mechanism | High |

---

**Source:** AI-Native Playbook documentation (8 files, all high confidence) | Enhanced by Skill Seeker

---
name: commitlint
description: Use when working with commitlint
---

# Commitlint Skill

Use when working with commitlint

## When to Use This Skill

Use this skill when you need to:
- understand commitlint features, APIs, and workflows
- find concrete code examples before implementing or debugging
- navigate the official documentation quickly through categorized references

## Quick Reference

### High-Signal Examples

**Example 1** (json):
```json
[
  "lower-case", // default
  "upper-case", // UPPERCASE
  "camel-case", // camelCase
  "kebab-case", // kebab-case
  "pascal-case", // PascalCase
  "sentence-case", // Sentence case
  "snake-case", // snake_case
  "start-case", // Start Case
];
```

**Example 2** (text):
```text
'.'
```

**Example 3** (elixir):
```elixir
npm install --save-dev commitlint-config-lerna @commitlint/config-conventional
```

### Key Usage Notes

**Pattern 1:** commitlint.config.jsparser-preset.jsjsexport default { parserPreset: "./parser-preset", };jsexport default { parserOpts: { headerPattern: /^(\w*)\(...

```
export default {
  parserPreset: "./parser-preset",
};
```

**Pattern 2:** Are you an LLM?

```
export default {
  rules: {
    "dollar-sign": function (parsed, when, value) {
      // rule implementation ...
    },
  },
};
```

**Pattern 3:** To use the rule in commitlint, you would use the unprefixed plugin name, followed by a slash, followed by the rule name.

```
{
  "peerDependencies": {
    "@commitlint/lint": ">=7.6.0"
  }
}
```

**Pattern 4:** Are you an LLM?

```
{
  // ...
  "commitlint": {
    "rules": {
      "references-empty": [2, "never"],
    },
    "parserPreset": {
      "parserOpts": {
        "issuePrefixes": ["PROJ-"],
      },
    },
  },
  // ...
}
```

## Reference Files

This skill includes comprehensive documentation in `references/`:

- **reference.md** - Reference documentation

Use `view` to read specific reference files when detailed information is needed.

## Working with This Skill

### Start Here
Start with the getting_started or tutorials reference files for foundational concepts.

### For Specific Features
Use the appropriate category reference file (api, guides, etc.) for detailed information.

### For Code Examples
Use the high-signal examples above first, then open the matching reference file for full context.

## Notes

- This skill was automatically generated from official documentation
- Reference files preserve the structure and examples from source docs
- Code examples include language detection for better syntax highlighting
- Quick reference entries are filtered to avoid low-signal placeholders and inline tokens

## Updating

To refresh this skill with updated documentation:
1. Re-run the scraper with the same configuration
2. The skill will be rebuilt with the latest information

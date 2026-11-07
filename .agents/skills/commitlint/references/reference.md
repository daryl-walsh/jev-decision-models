# Commitlint - Reference

**Pages:** 12

---

## Prompt

**URL:** https://commitlint.js.org/reference/prompt.md

**Contents:**
- `settings`
- `messages`
- `questions`

Prompt Config is used by `@commitlint/cz-commitlint`.

There are three fields: `settings`, `messages` and `questions`

Set optional options.

Set hint contents, you can configure it to support localization.

Specify the interactive steps, Steps can only be configured in

![cz-commitlint questions](/assets/cz-commitlint.png)

**Examples:**

Example 1 (js):
```js
export default {
  parserPreset: 'conventional-changelog-conventionalcommits',
  rules: {
    ...
  },
  prompt: {
    settings: {},
    messages: {
      skip: ':skip',
      max: 'upper %d chars',
      min: '%d chars at least',
      emptyWarning: 'can not be empty',
      upperLimitWarning: 'over limit',
      lowerLimitWarning: 'below limit'
    },
    questions: {
      type: {
        description: "Select the type of change that you're committing:",
        enum: {
          feat: {
            description: 'A new feature',
            title: 'Features',
            emoji: '✨',
          },
          fix: {
            description: 'A bug fix',
            title: 'Bug Fixes',
            emoji: '🐛',
          },
          docs: {
            description: 'Documentation only changes',
            title: 'Documentation',
            emoji: '📚',
          },
          style: {
            description: 'Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)',
            title: 'Styles',
            emoji: '💎',
          },
          refactor: {
            description: 'A code change that neither fixes a bug nor adds a feature',
            title: 'Code Refactoring',
            emoji: '📦',
          },
          perf: {
            description: 'A code change that improves performance',
            title: 'Performance Improvements',
            emoji: '🚀',
          },
          test: {
            description: 'Adding missing tests or correcting existing tests',
            title: 'Tests',
            emoji: '🚨',
          },
          build: {
            description: 'Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)',
            title: 'Builds',
            emoji: '🛠',
          },
          ci: {
            description: 'Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)',
            title: 'Continuous Integrations',
            emoji: '⚙️',
          },
          chore: {
            description: "Other changes that don't modify src or test files",
            title: 'Chores',
            emoji: '♻️',
          },
          revert: {
            description: 'Reverts a previous commit',
            title: 'Reverts',
            emoji: '🗑',
          },
        },
      },
      scope: {
        description:
          'What is the scope of this change (e.g. component or file name)',
      },
      subject: {
        description: 'Write a short, imperative tense description of the change',
      },
      body: {
        description: 'Provide a longer description of the change',
      },
      isBreaking: {
        description: 'Are there any breaking changes?',
      },
      breakingBody: {
        description:
          'A BREAKING CHANGE commit requires a body. Please enter a longer description of the commit itself',
      },
      breaking: {
        description: 'Describe the breaking changes',
      },
      isIssueAffected: {
        description: 'Does this change affect any open issues?',
      },
      issuesBody: {
        description:
          'If issues are closed, the commit requires a body. Please enter a longer description of the commit itself',
      },
      issues: {
        description: 'Add issue references (e.g. "fix #123", "re #123".)',
      },
    },
  }
};
```

---

## Rules

**URL:** https://commitlint.js.org/reference/rules.md

**Contents:**
- body-case
- body-empty
- body-full-stop
- body-leading-blank
- body-max-length
- body-max-line-length
- body-min-length
- breaking-change-exclamation-mark
- footer-empty
- footer-leading-blank

and a line in `footer` matches the regular expression `^BREAKING[ -]CHANGE:`

**Examples:**

Example 1 (text):
```text
  'lower-case'
```

Example 2 (js):
```js
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

Example 3 (text):
```text
  '.'
```

Example 4 (text):
```text
  Infinity
```

---

## Rules | commitlint

**URL:** https://commitlint.js.org/reference/rules.html

**Contents:**
- Rules ​
- body-case ​
- body-empty ​
- body-full-stop ​
- body-leading-blank ​
- body-max-length ​
- body-max-line-length ​
- body-min-length ​
- breaking-change-exclamation-mark ​
- footer-empty ​

condition: body is in case value

condition: body ends with value

condition: body has value or less characters

condition: body lines have value or less characters, or contain a URL

condition: body has value or more characters

This rule enforces that breaking changes are marked by both a ! in the header and BREAKING CHANGE in the footer. The behavior is that of an XNOR operation:

condition: footer has value or less characters

condition: footer lines have value or less characters

condition: footer has value or more characters

condition: header is in case value

condition: header ends with value

condition: header has value or less characters

condition: header has value or more characters

condition: scope is in case value

extended value (object based)

condition: all delimiters found in scope must match value

condition: scope is found in value

extended value (object based)

condition: scope has value or less characters

condition: scope has value or more characters

condition: message has value

condition: subject is in case value

condition: subject ends with value

condition: subject has value or less characters

condition: subject has value or more characters

condition: message has trailer value

description: type is in case value

condition: type is found in value

condition: type has value or less characters

condition: type has value or more characters

**Examples:**

Example 1 (unknown):
```unknown
'lower-case'
```

Example 2 (json):
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

Example 3 (unknown):
```unknown
'lower-case'
```

Example 4 (json):
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

---

## Configuration | commitlint

**URL:** https://commitlint.js.org/reference/configuration

**Contents:**
- Configuration ​
- Config via file ​
- Config via package.json ​
- Config option CLI ​
- Configuration object example ​
  - TypeScript configuration ​
- Shareable configuration ​
- Parser presets ​
  - Using an npm package ​
  - Using a local file ​

@commitlint/cli picks up configuration from the following files:

Configuration files are resolved using cosmiconfig.

You can add a commitlint field in package.json (or package.yaml) with an object that follows the below structure.

Add the path to the configuration file. Example: commitlint --config commitlint.config.js

CJS format is supported as well:

Configuration can also be a TypeScript file.

Relevant types and enums can be imported from @commitlint/types.

Below you can see main changes from a standard js file:

Every commitlint configuration can extend other commitlint configurations. Specify configurations to extend via the .extends key, using ids that can be resolved by the node resolve algorithm.

This means installed npm packages and local files can be used.

More information can be found in the Concepts – shareable config section.

The parser preset controls how commit messages are parsed into their component parts (type, scope, subject, body, footer, etc.). By default, commitlint does not ship with a parser preset — it falls back to conventional-changelog-angular defaults. When you extend @commitlint/config-conventional, the conventional-changelog-conventionalcommits preset is applied, which follows the Conventional Commits specification.

You can override the parser preset using the parserPreset property. It accepts:

You can also pass parserOpts directly without a separate file. This is useful for small adjustments like custom issue prefixes:

The parser is powered by conventional-commits-parser. Common options include:

For the complete list of options, see the conventional-commits-parser documentation.

When using a preset like conventional-changelog-conventionalcommits, you can pass a presetConfig object to customize the preset's behavior without replacing the entire parser configuration. This is commonly used to set commit types that appear in generated changelogs:

The available presetConfig options depend on the preset you are using. See the conventional-changelog-conventionalcommits documentation for details.

If you use semantic-release, both commitlint and semantic-release can share the same conventional-changelog-conventionalcommits preset. Keeping parserOpts and presetConfig consistent across both tools ensures that commits parsed during linting match what semantic-release uses for versioning and changelog generation:

Commitlint can output the issues encountered in different formats, if necessary. Use ids resolvable by the node resolve algorithm.

Refer to Rules for a complete list of available rules.

Config command-line submit interaction, works with @commitlint/cz-commitlint.

Refer to Prompt Config for details.

**Examples:**

Example 1 (javascript):
```javascript
const Configuration = {
  /*
   * Resolve and load @commitlint/config-conventional from node_modules.
   * Referenced packages must be installed
   */
  extends: ["@commitlint/config-conventional"],
  /*
   * Resolve and load conventional-changelog-atom from node_modules.
   * Referenced packages must be installed
   */
  parserPreset: "conventional-changelog-atom",
  /*
   * Resolve and load @commitlint/format from node_modules.
   * Referenced package must be installed
   */
  formatter: "@commitlint/format",
  /*
   * Any rules defined here will override rules from @commitlint/config-conventional
   */
  rules: {
    "type-enum": [2, "always", ["foo"]],
  },
  /*
   * Array of functions that return true if commitlint should ignore the given message.
   * Given array is merged with predefined functions, which consist of matchers like:
   *
   * - 'Merge pull request', 'Merge X into Y' or 'Merge branch X'
   * - 'Revert X'
   * - 'v1.2.3' (ie semver matcher)
   * - 'Automatic merge X' or 'Auto-merged X into Y'
   *
   * To see full list, check https://github.com/conventional-changelog/commitlint/blob/master/%40commitlint/is-ignored/src/defaults.ts.
   * To disable those ignores and run rules always, set `defaultIgnores: false` as shown below.
   */
  ignores: [(commit) => commit === ""],
  /*
   * Whether commitlint uses the default ignore rules, see the description above.
   */
  defaultIgnores: true,
  /*
   * Custom URL to show upon failure
   */
  helpUrl: "https://github.com/conventional-changelog/commitlint/#what-is-commitlint",
  /*
   * Custom prompt configs
   */
  prompt: {
    messages: {},
    questions: {
      type: {
        description: "please input type:",
      },
    },
  },
};

export default Configuration;
```

Example 2 (unknown):
```unknown
module.exports = Configuration;
```

Example 3 (lua):
```lua
import type { UserConfig } from "@commitlint/types"; 
import { RuleConfigSeverity } from "@commitlint/types"; 

const Configuration: UserConfig = {
  extends: ["@commitlint/config-conventional"],
  parserPreset: "conventional-changelog-atom",
  formatter: "@commitlint/format",
  rules: {
    "type-enum": [RuleConfigSeverity.Error, "always", ["foo"]], 
  },
  // ...
};

export default Configuration;
```

Example 4 (elixir):
```elixir
npm install --save-dev commitlint-config-lerna @commitlint/config-conventional
```

---

## Rules | commitlint

**URL:** https://commitlint.js.org/reference/rules

**Contents:**
- Rules ​
- body-case ​
- body-empty ​
- body-full-stop ​
- body-leading-blank ​
- body-max-length ​
- body-max-line-length ​
- body-min-length ​
- breaking-change-exclamation-mark ​
- footer-empty ​

condition: body is in case value

condition: body ends with value

condition: body has value or less characters

condition: body lines have value or less characters, or contain a URL

condition: body has value or more characters

This rule enforces that breaking changes are marked by both a ! in the header and BREAKING CHANGE in the footer. The behavior is that of an XNOR operation:

condition: footer has value or less characters

condition: footer lines have value or less characters

condition: footer has value or more characters

condition: header is in case value

condition: header ends with value

condition: header has value or less characters

condition: header has value or more characters

condition: scope is in case value

extended value (object based)

condition: all delimiters found in scope must match value

condition: scope is found in value

extended value (object based)

condition: scope has value or less characters

condition: scope has value or more characters

condition: message has value

condition: subject is in case value

condition: subject ends with value

condition: subject has value or less characters

condition: subject has value or more characters

condition: message has trailer value

description: type is in case value

condition: type is found in value

condition: type has value or less characters

condition: type has value or more characters

**Examples:**

Example 1 (unknown):
```unknown
'lower-case'
```

Example 2 (json):
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

Example 3 (unknown):
```unknown
'lower-case'
```

Example 4 (json):
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

---

## Configuration | commitlint

**URL:** https://commitlint.js.org/reference/configuration.html

**Contents:**
- Configuration ​
- Config via file ​
- Config via package.json ​
- Config option CLI ​
- Configuration object example ​
  - TypeScript configuration ​
- Shareable configuration ​
- Parser presets ​
  - Using an npm package ​
  - Using a local file ​

@commitlint/cli picks up configuration from the following files:

Configuration files are resolved using cosmiconfig.

You can add a commitlint field in package.json (or package.yaml) with an object that follows the below structure.

Add the path to the configuration file. Example: commitlint --config commitlint.config.js

CJS format is supported as well:

Configuration can also be a TypeScript file.

Relevant types and enums can be imported from @commitlint/types.

Below you can see main changes from a standard js file:

Every commitlint configuration can extend other commitlint configurations. Specify configurations to extend via the .extends key, using ids that can be resolved by the node resolve algorithm.

This means installed npm packages and local files can be used.

More information can be found in the Concepts – shareable config section.

The parser preset controls how commit messages are parsed into their component parts (type, scope, subject, body, footer, etc.). By default, commitlint does not ship with a parser preset — it falls back to conventional-changelog-angular defaults. When you extend @commitlint/config-conventional, the conventional-changelog-conventionalcommits preset is applied, which follows the Conventional Commits specification.

You can override the parser preset using the parserPreset property. It accepts:

You can also pass parserOpts directly without a separate file. This is useful for small adjustments like custom issue prefixes:

The parser is powered by conventional-commits-parser. Common options include:

For the complete list of options, see the conventional-commits-parser documentation.

When using a preset like conventional-changelog-conventionalcommits, you can pass a presetConfig object to customize the preset's behavior without replacing the entire parser configuration. This is commonly used to set commit types that appear in generated changelogs:

The available presetConfig options depend on the preset you are using. See the conventional-changelog-conventionalcommits documentation for details.

If you use semantic-release, both commitlint and semantic-release can share the same conventional-changelog-conventionalcommits preset. Keeping parserOpts and presetConfig consistent across both tools ensures that commits parsed during linting match what semantic-release uses for versioning and changelog generation:

Commitlint can output the issues encountered in different formats, if necessary. Use ids resolvable by the node resolve algorithm.

Refer to Rules for a complete list of available rules.

Config command-line submit interaction, works with @commitlint/cz-commitlint.

Refer to Prompt Config for details.

**Examples:**

Example 1 (javascript):
```javascript
const Configuration = {
  /*
   * Resolve and load @commitlint/config-conventional from node_modules.
   * Referenced packages must be installed
   */
  extends: ["@commitlint/config-conventional"],
  /*
   * Resolve and load conventional-changelog-atom from node_modules.
   * Referenced packages must be installed
   */
  parserPreset: "conventional-changelog-atom",
  /*
   * Resolve and load @commitlint/format from node_modules.
   * Referenced package must be installed
   */
  formatter: "@commitlint/format",
  /*
   * Any rules defined here will override rules from @commitlint/config-conventional
   */
  rules: {
    "type-enum": [2, "always", ["foo"]],
  },
  /*
   * Array of functions that return true if commitlint should ignore the given message.
   * Given array is merged with predefined functions, which consist of matchers like:
   *
   * - 'Merge pull request', 'Merge X into Y' or 'Merge branch X'
   * - 'Revert X'
   * - 'v1.2.3' (ie semver matcher)
   * - 'Automatic merge X' or 'Auto-merged X into Y'
   *
   * To see full list, check https://github.com/conventional-changelog/commitlint/blob/master/%40commitlint/is-ignored/src/defaults.ts.
   * To disable those ignores and run rules always, set `defaultIgnores: false` as shown below.
   */
  ignores: [(commit) => commit === ""],
  /*
   * Whether commitlint uses the default ignore rules, see the description above.
   */
  defaultIgnores: true,
  /*
   * Custom URL to show upon failure
   */
  helpUrl: "https://github.com/conventional-changelog/commitlint/#what-is-commitlint",
  /*
   * Custom prompt configs
   */
  prompt: {
    messages: {},
    questions: {
      type: {
        description: "please input type:",
      },
    },
  },
};

export default Configuration;
```

Example 2 (unknown):
```unknown
module.exports = Configuration;
```

Example 3 (lua):
```lua
import type { UserConfig } from "@commitlint/types"; 
import { RuleConfigSeverity } from "@commitlint/types"; 

const Configuration: UserConfig = {
  extends: ["@commitlint/config-conventional"],
  parserPreset: "conventional-changelog-atom",
  formatter: "@commitlint/format",
  rules: {
    "type-enum": [RuleConfigSeverity.Error, "always", ["foo"]], 
  },
  // ...
};

export default Configuration;
```

Example 4 (elixir):
```elixir
npm install --save-dev commitlint-config-lerna @commitlint/config-conventional
```

---

## CLI | commitlint

**URL:** https://commitlint.js.org/reference/cli.html

**Contents:**
- CLI ​
- Lint without a config file ​

By default commitlint requires a configuration with rules to run — without one it exits with an error (result code 9). Pass --default-config to fall back to the built-in default config (@commitlint/config-conventional) when no rules are found, so commitlint can run without any setup:

This is useful for one-off checks or server-side hooks (e.g. pre-receive) where creating a commitlint.config.js and installing a shareable config is not practical. A configuration file with rules always takes precedence over --default-config, and configs passed via --extends are kept and override the default config when the fallback applies.

**Examples:**

Example 1 (elixir):
```elixir
❯ npx commitlint --help

@commitlint/cli@21.2.0 - Lint your commit messages

[input] reads from stdin if --edit, --env, --from and --to are omitted

Options:
  -c, --color           toggle colored output          [boolean] [default: true]
  -g, --config          path to the config file; result code 9 if config is
                        missing                                         [string]
      --default-config  use built-in default config
                        (@commitlint/config-conventional) when no rules are
                        found                                          [boolean]
      --print-config    print resolved config
                                          [string] [choices: "", "text", "json"]
  -d, --cwd             directory to execute in
                                         [string] [default: (Working Directory)]
  -e, --edit            read last commit message from the specified file or
                        fallbacks to ./.git/COMMIT_EDITMSG              [string]
  -E, --env             check message in the file at path given by environment
                        variable value                                  [string]
  -x, --extends         array of shareable configurations to extend      [array]
  -H, --help-url        help url in error message                       [string]
  -f, --from            lower end of the commit range to lint; applies if
                        edit=false                                      [string]
      --from-last-tag   uses the last tag as the lower end of the commit range
                        to lint; applies if edit=false and from is not set
                                                                       [boolean]
      --git-log-args    additional git log arguments as space separated string,
                        example '--first-parent --cherry-pick'          [string]
  -l, --last            just analyze the last commit; applies if edit=false
                                                                       [boolean]
  -o, --format          output format of the results                    [string]
  -p, --parser-preset   configuration preset to use for
                        conventional-commits-parser                     [string]
  -q, --quiet           toggle console output         [boolean] [default: false]
  -t, --to              upper end of the commit range to lint; applies if
                        edit=false                                      [string]
  -V, --verbose         enable verbose output for reports without problems
                                                                       [boolean]
      --legacy-output   use the legacy input output format (single-line 'input:
                        ...')                                          [boolean]
  -s, --strict          enable strict mode; result code 2 for warnings, 3 for
                        errors                                         [boolean]
      --options         path to a JSON file or Common.js module containing CLI
                        options
  -v, --version         display version information                    [boolean]
  -h, --help            Show help                                      [boolean]
```

Example 2 (bash):
```bash
echo "feat: add new feature" | npx commitlint --default-config
```

---

## Rules configuration | commitlint

**URL:** https://commitlint.js.org/reference/rules-configuration.html

**Contents:**
- Rules configuration ​
- Plain array ​
- Function returning array ​
- Async function returning array ​

Rules are made up by a name and a configuration array. The configuration array contains:

Rule configurations are either of type array residing on a key with the rule's name as key on the rules object or of type function returning type array or Promise<array>. This means all of the following notations are supported.

**Examples:**

Example 1 (lua):
```lua
export default {
  // ...
  rules: {
    "header-max-length": [0, "always", 72], 
  },
  // ...
};
```

Example 2 (lua):
```lua
export default {
  // ...
  rules: {
    "header-max-length": () => [0, "always", 72], 
  },
  // ...
};
```

Example 3 (lua):
```lua
export default {
  // ...
  rules: {
    "header-max-length": async () => [0, "always", 72], 
  },
  // ...
};
```

---

## Working with Plugins | commitlint

**URL:** https://commitlint.js.org/reference/plugins.html

**Contents:**
- Working with Plugins ​
- Rules in Plugins ​
- Peer Dependency ​
- Share Plugins ​
- Local Plugins ​
  - Usage Example ​
- Further Reading ​

Our plugin implementation is based off of eslint's plugin implementation; Each plugin is an npm module with a name in the format of commitlint-plugin-<plugin-name>, such as commitlint-plugin-jquery. You can also use scoped packages in the format of @<scope>/commitlint-plugin-<plugin-name> such as @jquery/commitlint-plugin-jquery.

Plugins can expose additional rules for use in commitlint. To do so, the plugin must export a rules object containing a key-value mapping of rule ID to rule. The rule ID does not have to follow any naming convention (so it can just be dollar-sign, for instance).

To use the rule in commitlint, you would use the unprefixed plugin name, followed by a slash, followed by the rule name. So if this plugin were named commitlint-plugin-myplugin, then in your configuration you'd refer to the rule by the name myplugin/dollar-sign. Example: "rules": {"myplugin/dollar-sign": 2}.

To make clear that the plugin requires commitlint to work correctly you have to declare commitlint as a peerDependency in your package.json. The plugin support was introduced in commitlint version 7.6.0. Ensure the peerDependency points to @commitlint 7.6.0 or later.

In order to make your plugin available to the community you have to publish it on npm.

Recommended keywords:

Add these keywords into your package.json file to make it easy for others to find.

In case you want to develop your plugins locally without the need to publish to npm, you can send declare your plugins inside your project locally. Please be aware that you can declare only one local plugin.

**Examples:**

Example 1 (lua):
```lua
export default {
  rules: {
    "dollar-sign": function (parsed, when, value) {
      // rule implementation ...
    },
  },
};
```

Example 2 (json):
```json
{
  "peerDependencies": {
    "@commitlint/lint": ">=7.6.0"
  }
}
```

Example 3 (javascript):
```javascript
export default {
  rules: {
    "hello-world-rule": [2, "always"],
  },
  plugins: [
    {
      rules: {
        "hello-world-rule": ({ subject }) => {
          const HELLO_WORLD = "Hello World";
          return [
            subject.includes(HELLO_WORLD),
            `Your subject should contain ${HELLO_WORLD} message`,
          ];
        },
      },
    },
  ],
};
```

Example 4 (bash):
```bash
> echo "feat: random subject" | commitlint # fails
> echo "feat: Hello World" | commitlint # passes
```

---

## Prompt | commitlint

**URL:** https://commitlint.js.org/reference/prompt.html

**Contents:**
- Prompt ​
- settings ​
- messages ​
- questions ​

Prompt Config is used by @commitlint/cz-commitlint.

There are three fields: settings, messages and questions

Set optional options.

Set hint contents, you can configure it to support localization.

Specify the interactive steps, Steps can only be configured in

**Examples:**

Example 1 (lua):
```lua
export default {
  parserPreset: 'conventional-changelog-conventionalcommits',
  rules: {
    ...
  },
  prompt: {
    settings: {},
    messages: {
      skip: ':skip',
      max: 'upper %d chars',
      min: '%d chars at least',
      emptyWarning: 'can not be empty',
      upperLimitWarning: 'over limit',
      lowerLimitWarning: 'below limit'
    },
    questions: {
      type: {
        description: "Select the type of change that you're committing:",
        enum: {
          feat: {
            description: 'A new feature',
            title: 'Features',
            emoji: '✨',
          },
          fix: {
            description: 'A bug fix',
            title: 'Bug Fixes',
            emoji: '🐛',
          },
          docs: {
            description: 'Documentation only changes',
            title: 'Documentation',
            emoji: '📚',
          },
          style: {
            description: 'Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)',
            title: 'Styles',
            emoji: '💎',
          },
          refactor: {
            description: 'A code change that neither fixes a bug nor adds a feature',
            title: 'Code Refactoring',
            emoji: '📦',
          },
          perf: {
            description: 'A code change that improves performance',
            title: 'Performance Improvements',
            emoji: '🚀',
          },
          test: {
            description: 'Adding missing tests or correcting existing tests',
            title: 'Tests',
            emoji: '🚨',
          },
          build: {
            description: 'Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)',
            title: 'Builds',
            emoji: '🛠',
          },
          ci: {
            description: 'Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)',
            title: 'Continuous Integrations',
            emoji: '⚙️',
          },
          chore: {
            description: "Other changes that don't modify src or test files",
            title: 'Chores',
            emoji: '♻️',
          },
          revert: {
            description: 'Reverts a previous commit',
            title: 'Reverts',
            emoji: '🗑',
          },
        },
      },
      scope: {
        description:
          'What is the scope of this change (e.g. component or file name)',
      },
      subject: {
        description: 'Write a short, imperative tense description of the change',
      },
      body: {
        description: 'Provide a longer description of the change',
      },
      isBreaking: {
        description: 'Are there any breaking changes?',
      },
      breakingBody: {
        description:
          'A BREAKING CHANGE commit requires a body. Please enter a longer description of the commit itself',
      },
      breaking: {
        description: 'Describe the breaking changes',
      },
      isIssueAffected: {
        description: 'Does this change affect any open issues?',
      },
      issuesBody: {
        description:
          'If issues are closed, the commit requires a body. Please enter a longer description of the commit itself',
      },
      issues: {
        description: 'Add issue references (e.g. "fix #123", "re #123".)',
      },
    },
  }
};
```

---

## Examples | commitlint

**URL:** https://commitlint.js.org/reference/examples.html

**Contents:**
- Examples ​
- Validate for issue/ticket numbers ​
- Customizing Emojis and Alignment in VS Code ​
- Include Emojis in Commit Messages ​

These examples show common usages of how commitlint can be configured.

This example uses inline parserOpts to configure the parser to recognize custom issue prefixes (e.g. PROJ-123). The references-empty rule then enforces that every commit references a ticket.

See Parser presets for common parserOpts and configuration examples.

Some terminals have trouble correctly calculating the width of Unicode emojis, which can cause a missing space after the emoji, leading to misaligned text in the commit prompt.

To fix this issue in VS Code, you can specify an additional space after each emoji in your commitlint.config.ts file.

By default, emojis are only shown in the commit message prompt. To include them in the actual commit header, you need a custom parser and a setting to enable them.

This configuration is based on the conventional commit rules and uses a parser preset to validate commit headers that start with an emoji.

Although some emojis may appear without a trailing space in the terminal, the commit message itself is submitted with the correct formatting.

You can verify this with git log -4 --format=%B > commits.txt.

**Examples:**

Example 1 (json):
```json
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

Example 2 (elixir):
```elixir
import { type UserConfig } from "@commitlint/types";

export default {
  // Use the conventional commit rules as a base.
  extends: ["@commitlint/config-conventional"],
  prompt: {
    questions: {
      type: {
        enum: {
          // Add a space to a few common types for better alignment.
          build: {
            emoji: "🛠️ ", // The extra space fixes the alignment.
          },
          chore: {
            emoji: "♻️ ",
          },
          ci: {
            emoji: "⚙️ ",
          },
          revert: {
            emoji: "🗑️ ",
          },
        },
      },
    },
  },
} satisfies UserConfig;
```

Example 3 (javascript):
```javascript
import type { ParserPreset, UserConfig } from "@commitlint/types";
import config from "@commitlint/config-conventional";
import createPreset from "conventional-changelog-conventionalcommits";
import { merge } from "lodash-es";

// A helper function to create the custom emoji parser preset.
async function createEmojiParser(): Promise<ParserPreset> {
  // Generates the regex from the emojis defined in the conventional config.
  const emojiRegexPart = Object.values(config.prompt.questions.type.enum)
    .map((value) => value.emoji.trim())
    .join("|");

  const parserOpts = {
    // This regular expression validates commit headers with an emoji.
    breakingHeaderPattern: new RegExp(`^(?:${emojiRegexPart})\\s+(\\w*)(?:\\((.*)\\))?!:\\s+(.*)$`),
    headerPattern: new RegExp(`^(?:${emojiRegexPart})\\s+(\\w*)(?:\\((.*)\\))?!?:\\s+(.*)$`),
  };

  const emojiParser = merge({}, await createPreset(), {
    conventionalChangelog: { parserOpts },
    parserOpts,
    recommendedBumpOpts: { parserOpts },
  });

  return emojiParser;
}

const emojiParser = await createEmojiParser();

export default {
  extends: ["@commitlint/config-conventional"],
  parserPreset: emojiParser,
  prompt: {
    questions: {
      type: {
        enum: {
          // Customize emojis and add the extra space for better alignment.
          build: { emoji: "🛠️ " },
          chore: { emoji: "♻️ " },
          ci: { emoji: "⚙️ " },
          revert: { emoji: "🗑️ " },
        },
        // This setting includes the emoji in the final commit header.
        headerWithEmoji: true,
      },
    },
  },
} satisfies UserConfig;
```

Example 4 (unknown):
```unknown
⚙️ ci(scope): short

🛠 build(scope): short

🐛 fix(scope): short

✨ feat(scope): short
```

---

## Projects from the community | commitlint

**URL:** https://commitlint.js.org/reference/community-projects.html

**Contents:**
- Projects from the community ​
- Remark ​
- List of Projects ​

?> These projects are not affiliated with us in any way.

Before you use any of these projects make sure you know what you are doing. If you find anything weird about a project let us know.

If you want to add a project to this list open a pull request.

---

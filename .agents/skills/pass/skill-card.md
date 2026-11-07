## Description: <br>
Complete guide for using pass, the standard Unix password manager, including terminal password-store setup, GPG-encrypted entries, git synchronization, and common extensions. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[bastos](https://clawhub.ai/user/bastos) <br>

### License/Terms of Use: <br>


## Use Case: <br>
External users, developers, and operators use this skill when they need guidance for installing, initializing, organizing, synchronizing, and troubleshooting a pass password store. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill covers sensitive password and private-key workflows. <br>
Mitigation: Do not share decrypted passwords, exported vault files, or private-key files with an agent; keep secret handling local and user-directed. <br>
Risk: Some commands can overwrite or recursively delete password-store entries. <br>
Mitigation: Double-check entry paths before using recursive delete or force overwrite flags. <br>
Risk: The guide references third-party pass extensions. <br>
Mitigation: Review extension source and trustworthiness before cloning or installing extensions. <br>


## Reference(s): <br>
- [pass-update extension](https://github.com/roddhjav/pass-update) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown with inline shell commands and configuration examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Guidance may include commands that operate on encrypted password-store entries, GPG keys, git remotes, clipboard behavior, and pass extensions.] <br>

## Skill Version(s): <br>
1.0.0 (source: release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>

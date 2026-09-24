**Languages:** English | [简体中文](README.zh-CN.md)

# agents-md-maintenance

An agent skill for reviewing, editing, and compacting global or project `AGENTS.md` files. It groups rules by the decisions they govern, removes stale or recoverable text, and keeps the instructions an agent needs before it can follow the document index. Structural checks help catch broken links; a human or coordinator still reviews behavior.

## Install

Requires Node.js for the installer. This command installs the skill for supported coding agents on macOS, Linux, or Windows:

```sh
npx skills add x0c/agents-md-skill --skill agents-md-maintenance -g -y
```

The skill's audit helper requires Python 3. No service or paid API is needed.

## Use

Ask your coding agent to use `agents-md-maintenance`:

```text
Use the agents-md-maintenance skill to review and compact this repository's AGENTS.md.
Read the whole file, preserve effective rules and exceptions, and check its document links.
```

You can also request a specific rule edit or a read-only review. The skill distinguishes targeted work from a full cleanup; delegation is optional.

## What to test

- Did related rules end up together without turning the file into a collection of tiny sections?
- Did prohibitions, exceptions, and the scope of existing rules survive?
- Can the document index lead a fresh agent to the detail it needs?
- Did the rewrite reduce loaded context without making decisions worse?

The included `scripts/audit.py` checks links and structure. Its clean result does not prove that the edited rules retain their meaning. If you find a case where the skill behaves badly, [open an issue](https://github.com/x0c/agents-md-skill/issues) with a sanitized before/after example and the missed decision.

## License

MIT. See [LICENSE](LICENSE).

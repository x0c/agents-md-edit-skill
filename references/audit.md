# Read-Only Audit

Run `python3 <skill-directory>/scripts/audit.py PATH [--json]` from any working directory, replacing `<skill-directory>` with the installed directory containing this skill's `SKILL.md`. `PATH` must identify an existing Markdown file, usually an AGENTS.md file. The script locates the target from the supplied path, resolves relative local links from the target file's parent, follows symlinks for existence checks, and never modifies files.

The report includes file size and heading counts as descriptive measurements, possible repeated headings and index entries, local links found in index tables, missing targets, and the balance of managed-region markers. Counts are advisory; there are no universal size or density thresholds. JSON mode provides the same structural observations for automation.

The auditor recognizes headings that identify an index or navigation section, including localized headings. It checks local Markdown links in index tables and explicit path references in the first table column, including a bare relative filename. Prose outside index tables is ignored, so mentioning a filename in a description does not create a link check. External URLs and fragment-only links are skipped.

The script cannot judge whether a rule is useful, correct, supported, well placed, or semantically duplicated. Treat findings as leads for human review. A repeated item may be intentional; a clean report is not proof of document quality.

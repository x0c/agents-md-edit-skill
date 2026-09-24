# Decision Criteria

Judge an instruction by the future decision it changes. The unit of preservation is an effective behavior with its applicable boundary, not a sentence, paragraph, heading, or historical explanation.

## Rule value

- **Action:** What would an agent do differently with this instruction? If nothing changes, remove it from default instructions or retain it as background in the appropriate record.
- **Authority:** Does explicit user intent, a current source, or verified evidence support it? A past incident explains a rule but is not itself the rule.
- **Scope:** Which tasks, systems, and people does it cover? Keep exceptions and values that change the answer. Generalize an example only if it preserves the same boundary; do not widen a narrow prohibition by accident.
- **Owner:** Is this a default behavioral constraint, on-demand knowledge, a repeatable skill procedure, a generated contract, or transient task state? Put it with rules of the same domain and use pointers instead of restating its body.
- **Recoverability:** Could a fresh agent find a current authority and reconstruct this descriptive fact with a few cheap calls? Test the path, not an imagined ability to infer it. A fact can be derivable while the instruction to look for it is not.
- **Loading reliability:** Must this rule be present before an indexed document could reasonably be retrieved? Weigh scope, likelihood of retrieval, and the cost of omission. Rare but consequential prohibitions can justify default loading; narrow operating detail can live in linked documents when the index describes it well enough to be found.

Dates, authorship labels, anecdotes, lists of equivalent technologies, repeated emphasis, and explanations are candidates for compression, not automatic deletions. A named exception, numeric threshold, exact command, or path remains when replacing it would change behavior. Headings are navigation aids, not a required wrapper for each rule. When used, their rules should govern one subject; a short file can use a flat rules section, separate from navigation or other specialized sections.

Check recoverability before choosing the loading layer. Repository layout, ordinary commands, and copied signatures may be cheap to rediscover; hidden failure conditions, deliberate design choices, user constraints, and instructions to consult an authority often are not. Separate a rule's value from its residency: a valid, narrowly scoped rule can belong in a linked authority when its index summary reliably routes the relevant work. A lint or CI rule may still need an earlier agent directive when enforcement occurs after an avoidable risky action. When evidence is inconclusive, keep the behavior provisionally and identify what must be verified; uncertainty is not a permanent reason to keep verbose prose.

## Structural review

For a full-file task, map the current headings, then independently design a domain tree around decision ownership. A tree that merely repeats the current headings cannot reveal bad ownership. Map each rule to keep, merge, move, route to an authority, remove, or leave unresolved; do not use a blanket preservation list in place of those decisions. Review relationships across distant sections, including policies repeated in closure checklists, broad miscellaneous sections, and generated blocks that overlap non-managed text. Move a rule across headings when its owner changes; preserve a pointer only where it genuinely helps retrieval. State concrete problems and representative rewritten rules across the whole file, not just a proposed outline or a link count.

For a local task, scan headings and same-domain clauses, then inspect the affected authority. Expand scope only where an overlap or contradiction requires it. Do not invoke the local-work rule to narrow an explicitly requested whole-file cleanup.

## Behavioral review

Compare before and after on an ordinary task, a real exception, and an unrelated task. Ask whether the correct action is still selected, whether an exception has been lost, and whether an unrelated task now loads extra context or obeys an accidental new constraint. Inspect actual heading targets and authority links. The structural audit script detects broken navigation and marker imbalance; it does not detect misplaced, verbose, duplicated, stale, or conflicting instructions.

Treat these criteria as hypotheses. If an edited rule performs badly, determine whether the cause is the wording, the document route, missing knowledge, execution, or tooling. Correct the cause rather than adding another universal prohibition.

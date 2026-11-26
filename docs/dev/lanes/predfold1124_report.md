# predfold1124 — the owner's 2026-11-23 late rulings folded into the predicate documents

Lane predfold1124 (opus), branch lane/predfold1124, started at 172930848. Design only: nothing under src/, cli/,
lib/, memfn/, tests/ or scripts/ changed. The record (COND-FAMILY.md) was not edited.

## STATE AT HANDOFF

OWED: none

- Last rulings-file entry applied: **R-2** (option-hole-explicit RULED explicit). R-1 is applied too. The file holds
  no other entries.
- Lint `pred_doc_lint: checks passed 8801, failed 0`; `make -s test-plan-lint` green (2 passed, 0 failed).
- Model `predfold1124_model: 20 checks, 0 failed` (full run, with SUCCESSOR; 66 s wall).
- Sabotage `predfold1124_sabotage: 20 plants, 0 not caught` (102 s wall).

## RULINGS FOLDED

- **shorthand-is-callers.** Folded into core/labels/rule, with his statement and sentence. Condition 4 now counts
  only the caller's own labels, so `B(A)` read through `A.` is `B([A = A])` for every body. This rewrites
  argument-default (retitled "The caller's read of an argument's labels by its name"), closed-argument,
  call-prefix, the ownership table and nested-scope's example 1.
- **path-rules: yes.** A new piece, core/labels/rule/paths, holds his four rules verbatim, rules 5 and 6, the
  equivalence and nine lines. Line 5's reach is in core/labels/rule. stacked-chain is ANSWERED: the chain is legal
  by rule 1. Readings (b) and (c) of label-doors are marked WITHDRAWN. The export statement, flat-read-outside,
  export/arguments, binding-prefix, label-reference and two-sources were re-worded to match.
- **capture-in-set: error.** lib/structural/capture/in-set is ruled, with three lines. Candidate (b)'s lines moved
  to `rejected:`.
- **exact-count-unspecified: "agree error".** The unspecified overlay and holes/count were re-worded, with three
  new lines; lib/modifiers/padded-to has the line "The width unspecified". Candidate (a)'s line moved to
  `rejected:`.
- **The manager's two closures** (the options position half and the argument half). Both are marked as closures,
  "told to him, not his words". The withdrawn closure "stacked never chain" was not folded.
- **R-1 options-reach-constants: yes.** In lib/builtin/options the constant half is now ruled: options reach a
  string constant written after the statement in that file, and `x` never applies to a string. core/patterns/flags'
  defaults bullet also covers string constants. Candidate (a)'s line was renamed "A string constant" (answers
  unchanged); the line "A string from a library file" was added; candidate (b) moved to `rejected:`.
- **R-2 option-hole-explicit: explicit.** core/patterns/flags' EXPLICIT definition gains the option hole, and its
  open bullet is gone. core/holes/option and core/holes/flags get one clause each. Candidate (a)'s line was renamed
  "Through an option hole"; the line "Another letter through an option hole" was added; candidate (b) moved to
  `rejected:`.
- **R-1 and R-2 citations are in `history:` only.** Their record entries are on lane/pred-rev28 (d062f253c and
  db8382c63), after this lane's cut, so a `rulings:` item would fail lint L4 here. Each cites the full title, with
  the note "to add at the merge". QUOTES checks their words against the record at db8382c63.
- **New parked piece:** parked/ideas/effect-form.
- **Marked ANSWERED:** list-is-label, both-uses, pair-twice-alone.

## MANAGER READINGS TESTED

- **Shorthand readings (a)-(d): all SUPPORTED** (EXPAND/READINGS).
  - (a): placed twice, the last mention is read (alone first: the labelled spot).
  - (b): the shorthand label is protected.
  - (c): the "argument's binding" row is legal in every column.
  - (d): inside the definition that makes the label, the labelled use is read by its label only.
  - Not modelled: the never-pass part of (a). The engine models no warnings.
- **Path readings (d)-(g):**
  - (e) SUPPORTED: a caller's label is a start whatever the body stacks.
  - (f) SUPPORTED: `B.h` through a call by rule 4; `B.d` with two `d` in a sequence reads the last mention.
  - (d) UNTESTABLE: no program can spell `_` as a start.
  - (g) UNTESTABLE: the equivalence is a picture, not a spelling.
- **R-1 readings:**
  - (a) SUPPORTED: a library string in a weakly insensitive program's hole gives `xAB` FAILS, `Xab` HOLDS.
  - (c) SUPPORTED: `K("msg")` with K(k) := `/${k}=1/` gives `MSG=1` HOLDS.
  - (b) UNTESTABLE: the flag engine runs no capture request or selector.
- **R-2 readings:**
  - (a) SUPPORTED for a binding of a constant. NOT MODELLED for a macro's parameter: the flag engine resolves an
    option hole's name as a binding only.
  - (b) SUPPORTED: `s` through an option hole is not inherited at the hole (`a\nb` FAILS).

## ANSWERS CHANGED

ERRSWEEP: of the starting commit's 56 compile-error lines, 11 changed legality, all from refused to legal:
- `[n = [m = P]] & (n.m.d: <5)` (the chain, rule 1)
- `B(A) & (A.d: <5)`, 5 lines: call-prefix case 2 labelled; closed-argument labelled, listed, closed, and `_p`
- library `identity`, `peek`, `when`, `atomic`, `hits`

SWEEP (7 declared moves):
- Now refused by rule 2:
  - "Outer the caller's, inner private" `[n = [_x = P]] & (n.d: <5)`
  - "A blank label in the stack" `[l = [_ = P]] & (l.d: <5)`
  - The ownership table's stacked `n.h` and `B.n.h` cells follow.
- Answer changed: "Alone first" `B(A) & (A.d: <5)` now reads the labelled spot.
- Retired: "A label over a wider spot"; candidate (b)'s two capture lines; exact-count candidate (a)'s
  `EB(rx.digit, _)` line.

## WHAT MOVED

- core.md: core/labels/rule rewritten; core/labels/rule/paths is new; the ownership table rewritten;
  argument-default and closed-argument rewritten; sentence edits listed above; the R-2 clauses in flags,
  holes/option and holes/flags.
- library.md: the argument-labels lines and the options and capture in-set pieces; padded_to.
- parked.md: effect-form.
- Details: rulings, rejected, readings, evidence and history entries for each piece; the `shared:` line gains
  shorthand-is-callers, list-is-label and path-rules.

## DRAFT READINGS ADDED

These are the manager's readings, each marked "(the manager's reading)" in the base and recorded under
`readings:` with its run:
- shorthand (a)-(d)
- path (d)-(g)
- R-1 (a)-(c)
- R-2 (a)-(b)

No new reading of my own was added.

## OWNER QUESTIONS LEFT

None was raised by this fold. Still open from before:
- optional-entry-edges
- optional-label-general
- any-case-body, condition-group, default-imports, every-pass-spelling, export-choice, group-truth, not-test,
  number-in-loop, record-in-some, tuple-parts

His Discussion is parked.

## EVIDENCE AND COMMANDS

Directory docs/dev/lanes/predfold1124_evidence/: model.py, model.out, sabotage.out, succ_decl.tsv, CLAUDE.md (with
the known limits).

- Lint: `(cd worktrees/predfold1124 && python3 -I scripts/pred_doc_lint.py)` gives failed 0.
- Model: `timeout 5400 python3 -I -B docs/dev/lanes/predfold1124_evidence/predfold1124_model.py` gives 20 checks, 0
  failed, 66 s wall. `PREDFOLD1124_LIGHT=1` skips SUCCESSOR.
- Sabotage: `PREDFOLD1124_SABOTAGE=all` (same script) gives 20 plants, 0 not caught, 102 s wall. This is over 2
  minutes because p17 re-runs SUCCESSOR (67 s).
- SUCCESSOR: 15 models (predfix88 plus its 14), each against its pinned library; 64 s; no traceback.
  - 50 reds are declared by their FAIL line verbatim.
  - 40 keep predfix88's reasons.
  - 10 are new: predcall CLOSED; predfix82 SWEEP; predfix88 UNSPEC, SHORTHAND, STACKCHAIN, SPOTON, TABLE,
    NAMEGRID, SWEEP and DOC. Each is ruled-since or documents-moved by this fold, with its reason in the tsv.
- `make -s test-plan-lint` is green.

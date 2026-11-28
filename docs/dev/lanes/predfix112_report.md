# Lane predfix112: review r112 applied; array-gate and body-own-name folded (DESIGN)

Branch lane/predfix112, cut from lane/pred-rev28 at 2d7718d4e. Design only: nothing under src/, cli/, lib/, memfn/,
tests/ or scripts/ was edited. The rulings are the record entries of 2026-11-27 in
docs/design/plan_row_bodies/COND-FAMILY.md, "OWNER RULING — array-gate: "error. Agree with lean"" and "OWNER RULING —
body-own-name: "agree"; his read of the call case ("rx as an arg cant be directly on a path")"; the findings are
review r112 as ruled by the manager (filed: docs/dev/reviews/2026-11-27-r112-predfold1127.md).

## STATE AT HANDOFF

- OWED: none.
- The rulings file `docs/dev/lanes/predfix112_rulings.md` was re-read before each commit, before each run over two
  minutes and before this report. It stayed empty: no entry was applied (last entry: none).
- Branch tip: the commit carrying this report.
- pred_doc_lint: `pred_doc_lint: checks passed 10121, failed 0`. `make -s test-plan-lint`: green.
- Model: `predfix112_model: 11 checks, 0 failed` (full, SUCCESSOR112 included); sabotage: `PASS PLANTS112: 12 plants, caught 12` (one per check, two for READINGS112).
- Premise, before any edit: `pred_doc_lint: checks passed 10110, failed 0`; predfold1127 full at 2d7718d4e:
  `predfold1127_model: 13 checks, 0 failed` (SUCCESSOR1127: 19 models, 73 reds, all as declared).
- Owner questions left: 1 (gate-beside-direct). One correction for the manager's telling (below, under OWNER
  QUESTIONS LEFT): body-own-name makes THREE moved reads legal, not two.

## RULINGS FOLDED

- **array-gate** ("array-gate: error. Agree with lean"; as asked, for `[n = (P SEQ Q)] & some(@n.d, <5)`: "An
  error: a gate is never skipped, array or not"). core/labels/rule/one-path: the marked bullet and line "The array
  form through a gate" are RULED (a compile error, "array or not"); the details entry's reading (d) marked RULED, a
  rulings item and a rejected item (the exempt reading). lib/counting/some, count and every each say one line on it,
  with a rulings item in their details entries (review F7 (c)).
- **body-own-name** ("body-own-name: agree"; the statement as asked: "a path that skips nothing is always legal and
  reads the label directly under its last step; one-path limits only reads that skip a step."). It REPLACES the
  fold's reading (f) at its three sites (review F3):
  - core/labels/rule/one-path: the statement now ends "a path that skips nothing is always legal"; his words and
    his ground for the call case quoted ("Within the macro, the d from A is outside and would have to gate through
    rx but rx as an arg cant be directly on a path."); the "Nothing skipped" bullet: the direct target is read,
    targets reached by a skip beside it are not counted. Lines added: "The binding's own, nothing skipped" (`X & (X.d:
    <5)`, X := `[a = P] SEQ /;(?<d>\d)/`, X's own) and "A direct target beside a gate" (below, an owner question).
  - core/labels/paths/call-prefix: `[c = B(A)] & (c.d: <5)` and `B(A) & (B.d: <5)` with A := `/(?<d>\d)/`, B(rx) :=
    `/${rx}-(?<d>\d)/` legal again, the body's own `d`, their old answers RUN (below).
  - core/labels/paths/two-sources: the legal line "The body's own" is back (`B(/(?<d>\d)/) & (B.d: <5)`), its old
    answers.
  - details: one-path's reading (f) marked REPLACED, a rejected item for it; rulings items in call-prefix and
    two-sources; argument-label's recorded consequence "the body's own is `B.d`" marked RESTORED.
  - the other four moved reads stay compile errors: `date.v`, `W.h`, `pair.d`, `list_of.h` (RULE112).

## FINDINGS APPLIED

- F1 (the marking convention): every earlier item one-path reverses in part carries `[REVISED IN PART 2026-11-27 by
  one-path, line N (review r112 F1): <the half it loses>]`: flat-read-outside's ruling item (its sequence half) and
  rejected (b) (AMENDED: its ambiguity ground holds for `date.v`); rejected (c) marked `[REVIVED 2026-11-27 for
  skipped reads ...]`; the readings: flat-read-outside's `date.v` line, export's `date.v` reading, call-prefix (b)
  and (c) (REFUSED by one-path, LEGAL AGAIN by body-own-name); path-rules' "the manager's two readings as put";
  transform-export's rulings item and its TWOSPOT reading in lib/convention/argument-labels. Trap 25
  (parked/ideas/user-doc-traps, details) rewritten: "`date.v` is a compile error ...: write `date.m.v`".
- F2 (the manager's): the one-path piece's bullet "What moved": four printed reads are compile errors, `date.v`
  (write `date.m.v`), and `W.h`, `pair.d`, `list_of.h`, for which no path names one target, so the caller labels the
  argument (`W([x = ..], [y = ..])`, `pair([x = A])`, `list_of([x = ..])`); `c.d` and both `B.d` read the body's own.
  Each such line is printed at its piece and RUN by SWEEP112 / ERRSWEEP112.
- F3: folded by body-own-name (above).
- F4: one-path bullet "Optionals and loops (a reading, not run)"; the details reading UNTESTED; walker support: PLAN
  (below).
- F5: the bullet "Visible" says from outside a gate is a wall (rule 6), so its targets are not counted. The shape
  itself, `[n = (P SEQ /,(?<d>\d)/)] & (n.d: <5)`, is LEGAL under body-own-name's asked statement ("always legal"):
  printed as "A direct target beside a gate" (the group; the gate's `d` is `n.P.d`). The disposition's proposed rule
  "a gate counts its targets whatever the other target's kind" would make it the compile error: the two part, so it
  is not applied and is listed under OWNER QUESTIONS LEFT, both RUN.
- F6: core/labels/rule/kinds gains the rows "a list's alias `[(=) = a]` in a body" and "an argument's place
  (`${rx}` in a body)" (no name: never a start or a middle step; always passed, a node between; across an argument's
  place a target beside a direct one is not counted); the shorthand cell names one-path and body-own-name (`B.h`
  with B(rx) := `/${[p = rx]}(?<h>\d)/` reads the body's own `h`, RULE112). TABLE112 compares the two new rows with
  the walker's node kinds.
- F7: (a) the one-path rulings item quotes "gate-twice-scope: arrays would not require that rule" with its slug,
  class "an answer by slug"; (c) some/count/every (array-gate); (d) overtaken by array-gate; (e) "its five lines ;"
  spacing fixed (seven sites); EXAMPLES-5: "Two arguments, labelled" uses the caller's labels `x`, `y`.
- F8, COORD-1: PLAN lines (below). COORD-1: this lane's model reads git only by pinned commit (START112 =
  2d7718d4e); its header and CLAUDE.md name the older model that still reads a branch by name (predfold1123_model.py,
  `lane/pred-rev28:`).
- PLAN lines (for the manager to file):
  - F4: walker support for a labelled part under `?` or `*` and three run lines (`|` under a loop; an optional
    beside a sequence; list_of's looped and last spots). Trigger: the next fold touching one-path, or the first
    printed read into an optional or a loop.
  - F8: the kinds table carries "hides what it holds / shows it" and "may itself be skipped" as columns, the walker
    a lookup. Trigger: the next node kind; F6's two rows are its first step.
  - COORD-1: the next predicate model lane pins every git read by commit id; proposed to main as a pcrec-critic skill
    edit (the manager's). Small.

## MANAGER READINGS TESTED

The body-own-name entry's readings (READINGS112):
- (a) it replaces reading (f) at its three sites — DONE; SUPPORTED as run (no (f) text left in the three pieces;
  each names body-own-name).
- (b) his ground and the asked statement agree on every printed program — SUPPORTED for every call case, as run with
  the switch GROUND112 (his ground modelled as: an argument's labels are not counted when another target is):
  `c.d`, both `B.d`, and the one the entry names, `B(A) & (B.d: <5)` with B(rx) := `/${[p = rx]}-(?<d>\d)/`: both
  legal, the body's own `d`, the same answers: WHOLE `7-3` HOLDS, `3-7` FAILS, `1-2` HOLDS / SEARCHED `3-7 7-3`
  `7-3`@4 / FIND-ALL `7-3 3-7 1-2 7-7` [`7-3`@0, `1-2`@8]. They do NOT part there, so it is not an owner question.
  `X.d` over `[a = P] SEQ /;(?<d>\d)/` is no call: his ground says nothing of it (the GROUND112 model alone refuses
  it); the asked statement makes it legal, X's own: WHOLE `7;3` HOLDS, `3;7` FAILS, `1;2` HOLDS / SEARCHED `3;7
  7;3` `7;3`@4 / FIND-ALL `7;3 3;7 1;2 9;9` [`7;3`@0, `1;2`@8].
- (c) the argument's own label stays read by its source (`A.d`) — SUPPORTED as run (`B(A) & (A.d: <5)` equal to the
  hand regex `[0-4]-\d`).
The array-gate entry: "becomes ruled at the fix" — DONE (RULE112: refused, "behind a gate").

## ANSWERS CHANGED

Each line below was a compile error at 2d7718d4e and is legal now, with its answers RUN (SWEEP112, RULE112 against
hand regexes, MECH112 against MECH111's mechanically built regex):
- core/labels/paths/call-prefix "d as the call exports it, the argument setting one too" `[c = B(A)] & (c.d: <5)`, A
  := `/(?<d>\d)/`, B(rx) := `/${rx}-(?<d>\d)/`: WHOLE `7-3` HOLDS, `3-7` FAILS, `3-3` HOLDS / SEARCHED `3-7 7-3`
  `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (its answers before predfold1127).
- core/labels/paths/call-prefix "By the macro's name" `B(A) & (B.d: <5)`, the same A and B: the same answers (its
  predfold1127 keeper with A := `/(?<e>\d)/` re-spelled back; GONE112 declares the key).
- core/labels/paths/two-sources "The body's own" `B(/(?<d>\d)/) & (B.d: <5)`: WHOLE `7-3` HOLDS, `3-7` FAILS /
  SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (it replaces "Through the call, both").
No printed line that was legal at 2d7718d4e changed its answers (SWEEP112: moved 0).

## WHAT MOVED

- core.md: core/labels/rule/one-path (statement, `see:`, five bullets, two lines added, one line's reason);
  core/labels/rule/kinds (two rows, one cell); core/labels/paths/call-prefix (a bullet, three lines);
  core/labels/paths/two-sources (a bullet, one line).
- library.md: lib/convention/argument-labels (one line's labels renamed); lib/counting/some, count, every (a bullet
  each).
- core_details.md, library_details.md: rulings items (array-gate, body-own-name), rejected items, readings marked,
  the F1 markings, a history line with the old text verbatim for each base piece above; parked_details.md: trap 25.
- docs/dev/reviews/: the filed review r112, its directory (critics' files, dispositions, the coordinator's probe), the
  INDEX.md line. docs/dev/history/claude_md/docs__dev__lanes.md: this report's index line.

## DRAFT READINGS ADDED

- core/labels/rule/one-path "A direct target beside a gate" (`[n = (P SEQ /,(?<d>\d)/)] & (n.d: <5)`): legal, the
  direct group, read from body-own-name's "always" (a reading, run; an owner question below).
- core/labels/rule/one-path "Optionals and loops" (review F4): a marked reading, not run.
- core/labels/rule/kinds: the two new rows, every cell "a reading" except where a ruling is named.

## OWNER QUESTIONS LEFT

- **gate-beside-direct**: `[n = (P SEQ /,(?<d>\d)/)] & (n.d: <5)`, P := `/(?<d>\d)/`: the binding's own group `d`
  sits directly under `n`, P's `d` behind a gate beside it.
  - As printed, by body-own-name's statement as asked ("a path that skips nothing is always legal"): legal, the
    group: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2` [`7,3`@0, `1,2`@8];
    P's `d` is `n.P.d`: WHOLE `7,3` FAILS, `3,7` HOLDS / SEARCHED `7,3 3,7` `3,7`@4 / FIND-ALL `7,3 3,7 1,2`
    [`3,7`@4, `1,2`@8].
  - The other reading, gate-beside-label's manager reading (any gated target under the start makes the read the
    error) and review r112 F5's proposed rule ("a gate counts its targets whatever the other target's kind"): a
    compile error, "a `d` sits behind a gate ...: write the full path, `n.P.d`" (RUN: READINGS112, X112 off).
  - His gate-beside-label words ("did they know Q had a d and chose to skip it?") argue for the error; the statement
    he agreed to says "always". Lean: legal as printed, since nothing is skipped and the gate is not crossed.
- For the manager (a telling, not a question): the body-own-name entry told him "two of the seven moved reads become
  legal again (`c.d` and `B.d`) ...; the other five stay errors". The seven count call-prefix's `B.d` and
  two-sources' `B.d` separately; under the statement as asked BOTH are legal (RULE112), so three are legal again and
  four stay errors (`date.v`, `W.h`, `pair.d`, `list_of.h`).

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/predfix112_evidence/` (CLAUDE.md, predfix112_model.py, predfix112_model.out,
  predfix112_sabotage.out, predfix112_succ_decl.tsv).
- Model: `(cd worktrees/predfix112 && PREDFIX112_SUCCDIR=/var/tmp/pcrec-pcrec/scratch/predfix112/succ112b timeout
  6000 python3 -I -B docs/dev/lanes/predfix112_evidence/predfix112_model.py)`: `predfix112_model: 11 checks, 0 failed`. SUCCESSOR112: `20 models read, 78 reds, each against its declared key (78 declared): all as declared` (51 keys as predfold1127 declared, 22 moved by this lane's line-count shifts and 5 new, predfold1127's own, each with its reason in predfix112_succ_decl.tsv).
  The directory must be NEW and EMPTY: a first re-run into a used one read the old dumps as models and turned
  SUCCESSOR111 and SUCCESSOR1127 red; SUCCESSOR112 now refuses a non-empty directory.
- Sabotage: `PREDFIX112_SABOTAGE=all PREDFIX112_SUCCDIR=... PREDFIX112_LIGHT=1`: `PASS PLANTS112: 12 plants, caught 12` (one per check, two for READINGS112).
- `python3 -I scripts/pred_doc_lint.py`: `pred_doc_lint: checks passed 10121, failed 0`. `make -s test-plan-lint`: green. `scripts/lanecheck`: DONE rc=0.
- Commits: ad13c0374 (the documents), 65b587206 (the model's checks), 40fcc8468 (declarations, evidence CLAUDE.md,
  review r112 filed), and the tip carrying this report and the committed runs.

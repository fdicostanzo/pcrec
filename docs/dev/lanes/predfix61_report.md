# Lane predfix61 — review r61's FIX-NOW items applied; four owner questions opened; the review filed

Opus, design only (no build go). Branch lane/predfix61, cut from lane/pred-rev28 at 1fa811754. Input: review r61
(predfold1119) draft and critic texts, ruled by the manager's record entry "2026-11-19 MANAGER — review r61
(predfold1119) of the session's folds: dispositions ruled (no owner words)".

## STATE AT HANDOFF

OWED: none

STATE: complete. Commits: 8c0c2fab1 (F-A..F-G, three open pieces, the model), b119cdfbe (F-H..F-M, class-hole-order,
trap 25), 501c864f9 (evidence outputs; a class-value line reflowed), 650f07df0 (the review filed), and this report's
commit. Rulings file `docs/dev/lanes/predfix61_rulings.md`: empty at every commit and at this report (last entry
applied: empty). No rule added, no ruling reversed, no status raised to `ruled`; flags-in-filter untouched.

PREMISE TEST, before any edit: `python3 -I scripts/pred_doc_lint.py` printed "checks passed 5106, failed 0";
`GIT_DIR=/home/pcrec/projects/pcrec/.git timeout 110 python3 -I -B docs/dev/lanes/predasc_evidence/predasc_model.py`
printed "predasc_model: 24 checks, 0 failed". After the edits: lint "checks passed 5240, failed 0" (same command);
predasc 24 checks, 0 failed (it went red once on EXpos, which reads "[`a`, `b`, `c`]" from class-value's text that
F-K rewrote and wrapped; reflowed in 501c864f9, green again). `make -s test-plan-lint`: checks failed 0.

## FINDINGS APPLIED

By the draft's ids (commit letters: A = 8c0c2fab1, B = b119cdfbe; the filed review's table repeats this).
- F-A (A): core/labels/export statement 3: a part under a `_` part label, or `[_ = A]`, passes none of its labels
  (the manager's reading (b)); details reading SUPPORTED as rule-as-code (model FA).
- F-B (A, B): the statement keeps the ruled "both pass through"; the flat clause is "(a reading;
  core/labels/export/flat-read-outside)"; his words and the manager's correction quoted in the new piece's details;
  parked user-doc trap 25 restated (B), its old sentence verbatim in history.
- F-C (A): "the test can never pass" became "the test's outcome is fixed: `pcrec.test.never` where it then fails,
  `pcrec.test.always` where it then holds"; both polarities run.
- F-D (A): the partition "no path of the rx as composed sets the label before the hole (loop or not)"; the loop
  bullet's first-pass condition with its never-matching witness; rejected item 3 "by owner ruling (in a loop);
  outside a loop the manager's reading"; no new question.
- F-E (A): "every label visible in the surrounding rx" in core/holes/bare-condition/labels (statement and a bullet)
  and core/values/reads; which rx for a nested hole marked a reading; open piece bare-nested-scope.
- F-F (A): array-scope's readings (a), (b) marked in the base and listed in details `readings:`; `x.@a` routed
  through core/labels/paths; open piece array-vs-passes.
- F-G (A): "written last in the rx, outside every group, quantifier and branch", with the optional-group lines.
- F-H (B): core/holes/class's collapse qualified "for matching"; two-holes' "the order is not observable" replaced
  by "it matches as one class"; open piece class-hole-order.
- F-I (B): looped-compare's two live glosses and its readings item 2, and pass-start-read's rejected item, rewritten
  (old text verbatim in history); five live `evidence:` lines citing predloop marked "superseded by predasc"
  (core_details 2, library_details 3) and class-value's reading cites predasc EXwplus first.
- F-J (A, B): the "same" quote and its reason (A); the GUESS class marker on bare-condition/labels' first rulings
  item (A); export statement 3 a defined binding and a run line (A); class-order's `\b` bullet names SEARCHED and its
  subjects (B); looped-compare's joint equality "where both are set" (B).
- F-K (B): class-value quotes his "digits followed by letters" discussion (class DISCUSSION), `see:
  parked/ideas/class-base`, candidate (b) the ordered symbol set, `(?i)k` and `\p{..}` in the question.
- F-L (B): sort's statement is the general sort (no "only as"); placeholder row for `sort`, `longest_first(X)`, his
  `lengthSorted()`; the stable-sort reading dropped (history says why).
- F-M (B): GENERAL-11 (the lift bullet: only a SINGLE parameter lifts, a reading), GENERAL-4 (pointers to the
  lift's loop in core/holes/count, core/holes/pattern, lib/rx/repeat; two-holes points at lift-order), GENERAL-15
  (parked/ideas/cartesian: trigger half met).
- The review: filed as docs/dev/reviews/2026-11-19-r61-predfold1119.md (+ directory: COMMON, the five lens files,
  process.md, the coordinator's coord_v.py); its index line went into docs/dev/reviews/NOTES.md beside r60's,
  because docs/dev/reviews/CLAUDE.md keeps only the standing rules (its rule: "the full per-review entries, in
  order, are in the history file") and is at 12,125 bytes (`wc -c`) under a 12 KB cap. The brief said CLAUDE.md:
  the manager may move it.

## FINDINGS NOT APPLIED

- GENERAL-10's side question (does `pcrec.label.unset` also fire on an always-unset read): not in F-C's ruled form;
  left for the manager.
- STALE-5 (predasc plant s6 runs ~122 s) and a header note in predloop_model.py: both would edit another lane's
  committed evidence, which the brief forbids. Both lanes' files are unchanged.
- The review's proposed process changes (relay to main, not applied): critic skill §5 "run a git-show evidence
  script from the R/tree mirror with GIT_DIR=<repo>/.git"; skill §5 "name each drill's root concept in the OTHER
  briefs as excluded"; lens table simulate/mode-closure row "a fold that widens a scope is drilled against every
  privacy/closing rule of the same names"; and the draft's three guide lessons (widening vs privacy, name the
  two-valued pair, run every cited evidence script at a fold's tip).

## ANSWERS CHANGED

none: every printed answer at 1fa811754 still prints the same. The lines added are new (export statement 3, the
bare-condition/labels witnesses, the four open pieces), and no existing line was altered except class-order's `\b`
bullet, whose sentence now names the mode and subjects of the answer already printed on its second line.

## RESIDUALS AS PLAN ITEMS

(also in the filed review, with the same triggers)
- GENERAL-2: one piece for the label namespace, one for captures. TRIGGER: the next document pass.
- GENERAL-1: the unknown-label error for conditions in general in core/diagnostics/errors, told apart from
  `pcrec.test.never` on an unsettable label. TRIGGER: the next pass over core/diagnostics.
- GENERAL-5: equal strings merged vs repeats vs `unique`, one sentence in enumerate. TRIGGER: `.index` or a zip
  reading an array with a repeated string.
- GENERAL-12: modules and the `_` rule; the flat re-export of imported names. TRIGGER: the first module file whose
  labels clash with an importer's.
- F-L / GENERAL-9: sort/sorted and unique/distinct as one operation in two forms. TRIGGER: the first definition of
  either.
- GENERAL-11's unlock, a per-parameter property table. TRIGGER: the first user macro with an array parameter.

## OWNER QUESTIONS LEFT

Four open pieces, none answered, each with its candidates and run lines:
- flat-read-outside — core/labels/export/flat-read-outside: (a) flat reads outside follow the inside rules; (b) a
  flat read of a part's labels from outside is an error, the path required.
- bare-nested-scope — core/holes/bare-condition/nested-scope: (a) lexical, the literal the hole is written in;
  (b) composed, the rx where that literal ends up; one question for a bare condition, `$y` and `0`.
- array-vs-passes — core/labels/labels-vs-captures/array-vs-passes: (a) the array of settings; (b) the outermost
  loop's passes; the review's three witnesses.
- class-hole-order — core/holes/class/lift-order: (a) written order, the alternation; (b) one ascending class.

## EVIDENCE AND COMMANDS

- docs/dev/lanes/predfix61_evidence/predfix61_model.py: `timeout 110 python3 -I -B
  docs/dev/lanes/predfix61_evidence/predfix61_model.py` prints "predfix61_model: 15 checks, 0 failed"
  (predfix61_model.out). The label matcher is checked against python `re` on the coordinator's hand regexes and an
  ordered alternation (CONTROL: 6 programs, 0 differing); every one of its 21 formatted lines occurs verbatim in the
  documents (DOC); 13 owner sentences verbatim in the record (QUOTES).
- Counts quoted in the documents, each from that run: positive first-pass loop matches on 0 of 1,093 texts (FD);
  `A SEQ B` equals `[5-9]\d` 0 / 0 / 0 of 111 (FD); top-level written-last equality 0 / 0 / 0 of 121, inside an
  optional 1 / 58 / 90 (FG); unlifted class alternation vs one class 0 / 0 / 0 of 1,365 (FH); the joint form 100 of
  100 pairs where both are set (FJJ); `(?i)k` takes U+004B, U+006B, U+212A (FK).
- docs/dev/lanes/predfix61_evidence/predfix61_sabotage.out: the 13 plants, each run alone
  (`PREDFIX61_SABOTAGE=sN`), each CAUGHT by its target check, no traceback (`grep -c '^s[0-9]* target=.* CAUGHT'` on it = 13).
- Lint: `python3 -I scripts/pred_doc_lint.py` "checks passed 5240, failed 0" at the last document commit.
- predasc: `GIT_DIR=/home/pcrec/projects/pcrec/.git timeout 110 python3 -I -B
  docs/dev/lanes/predasc_evidence/predasc_model.py` "24 checks, 0 failed" after the edits.

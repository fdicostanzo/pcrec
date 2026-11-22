# process.md — round r83 crit-preddef1122 (design)
Coordinator: opus. Launched by pcrec-predicate. Started 2026-11-22T16:25:06-05:00.

## Freeze
- SUBJECT: lane/pred-rev28 tip 3e58abe9eadb89414dbe9fa8853151639b3b290d (rev-parsed; matches expected 3e58abe9e).
- Last reviewed: 30ca2520d (r82). Scope diff: subject/diff_30ca2520d_to_3e58abe9e.patch (789 lines; core.md 219, core_details 63, library 25, library_details 7).
- Build-landing commit (drift only): main 0c8ee75dd98717b7bd302cfb402bbfa8c9bb2caa. decisions.md/plan.md last commit at freeze: 50c8a6620ce9bba5631bee5a1700f87adf93db67 2026-11-22 14:09:48 -0500.
- R/tree = git clone --shared --no-checkout of the main repo, sparse (docs/design, docs/dev/lanes/*_evidence, doc_format, lint), detached at the tip (models need git show of older commits). R/tree_prev = same at 30ca2520d (coordinator only).

## Evidence re-runs (blind; verdict = LAST LINE)
At tip (.coord/reruns/):
- preddef: 22 checks, 0 failed (identical to committed preddef_model.out). rc 0.
- predfix82: 22 checks, 2 failed (SUCCESSOR, MARKS). rc 1.
- predcall: 14, 3 failed (SCAN, PREDREF, DOC). predref: 8, 3 failed (SCAN, MARKS, DOC).
- predbound: 21, 1 failed (DOC) BUT rc 0 (exit code disagrees with its own last line; exit code is not evidence).
- predfix77, predarr: AssertionError traceback (chars body reader).
- predscope: 20, 3 failed (NAMES, CLOSEDB, DOC).
- lint: checks passed 6639, failed 0.
At 30ca2520d (.coord/reruns_prev/): predfix82 0 failed; predcall 2 (SCAN, PREDREF); predref 2 (SCAN, MARKS); predbound/predscope/predfix77/predarr reds identical to tip.
- SUCCESSOR coverage: every red at tip is declared in preddef's SUCCESSOR. New reds this revision: predfix82 MARKS+SUCCESSOR, predcall DOC, predref DOC: all declared "here". Reds declared "by predfix82's declaration, unchanged": FAIL lines diffed prev vs tip: SCAN span count 252->270 with the same 32 bare reads and the same not-on-LEFT list; others identical. No undeclared red at the freeze.
- Observation: SUCCESSOR keys a declaration by check NAME; an "unchanged" declaration is not checked against the red's content (coordinator diffed by hand here).

## Agents
- 5 critics launched 2026-11-22T16:40:20-05:00 region (one message, background, unnamed, all opus): ruling af9e1f41350ee79ff (392 s), examples af649f987e56dfd8d (706 s), general af161740d18dfb102 (433 s), names a828cc923b3464d14 (606 s), fixind a1966e5c7227d61ff (582 s). All: file complete, CRITIC COMPLETE, lanecheck DONE; every final reply undeliverable (expected).
- Freeze drift check at return: see below.
- Verifier a8788258aa123ee3d (opus), V1-V15, 9 min, VERIFY COMPLETE + lanecheck DONE. 13 HOLDS, 2 PARTLY (V8 (i): unmarked holds, "error under (error)" not settled by text; V15: FIXIND-14's "not in see:" sub-claim REFUTED). No REFUTED resting on a crafted input, so no coordinator re-run needed.
- Coordinator inline checks: RULING-6 (no (g)/(h) in record 7510-7725: grep), RULING-1 (core_details.md:645-651 read).
- Freeze drift: subject branch 3e58abe9e -> 24821cc0e (at critic return) -> 691d42503 (hand-back); record/journal/wake only; program-options, weak-i, hole-flags. Hand-mapped in review.md: no finding affected. decisions.md/plan.md: no drift. main unchanged 0c8ee75dd.
- Blinding: no leak noticed; critics worked only from R/subject and R/tree (sparse clone excludes reports, reviews, pred working files). R/tree is a full-history clone: git show of denied files was possible but not needed.

## Per lens
| lens | raised | verified/answer | overlaps |
|---|---|---|---|
| RULING | 8 | quote/record claims; RULING-6 by grep | -1 with FIXIND-1/GENERAL-1; -2 with FIXIND-5; -3 with FIXIND-2/GENERAL-2/NAMES-5 |
| EXAMPLES | 7 | 2 answer-level (=NAMES-1), V1/V8/V9/V10 | -2/NAMES-1, -7/FIXIND-3, -4/FIXIND-16 |
| GENERAL | 12 | V3,V6,V13,V14,V15 | -1, -2 as above |
| NAMES | 10 | 7 answer-level, all HOLD | -1/EXAMPLES-2 |
| FIXIND | 16 | V8,V9,V10,V12,V13,V15 | as above |
Time to draft: about 85 min from setup start.

## Process observations
- The grid lens (NAMES) found every answer-level item: cells no printed line covers, where the engine decides what no sentence says (A1-A7). The lane's evidence checks only PRINTED lines (SWEEP/SCAN/UNMARKED), so "22 checks, 0 failed" said nothing about these cells. FIXIND independently named the same blind population for PROSE claims (month_numbered, when, occurrences).
- Three to four lenses found each of the two text roots (stale rejected list; the `[A = A]` equivalence): the root concept "what a part used alone is" was not assigned to one lens. Over-staffed on that root, harmless here (each brought a different witness).
- SUCCESSOR keys declarations by check name; an "unchanged" declaration is never compared to the red's content (coordinator did it by hand: R/tree_prev at the last reviewed commit, FAIL-line diff, 2 min).
- Models `git show` older commits by relative path, so a plain copy mirror cannot run them; a `git clone --shared --no-checkout` + sparse checkout into the round dir worked (no repo write) and ran every model unchanged.
- Subject branch kept moving (record entries) during the round; hand mapping was cheap because the fold areas did not overlap.

## Proposed changes
- P1 (top; skill §3 evidence re-run + the pred evidence convention): the newest model's GRID check: a committed table of the name-resolution grid (spelling x occurrences x read kind), each cell naming the sentence (file:line) that decides it and a run under the engine; an undecided cell is printed UNDECIDED, not skipped. Motivation: A1-A7 here, invisible to every printed-line check.
- P2 (pred evidence convention, SUCCESSOR): a declaration "superseded ... unchanged" carries the red's detail digest (its FAIL line text) and SUCCESSOR compares it, so a red that changes content under an unchanged name goes undeclared. Motivation: this round's hand diff (SCAN 252->270).
- P3 (skill §5 design mode R/tree): "when the evidence `git show`s older commits, R/tree is a `git clone --shared --no-checkout` + sparse checkout at the freeze in the round dir (no repo write); a plain copy cannot run it" (r83: 8 models ran unchanged).
- P4 (skill §5 drill assignment): name the ROOT CONCEPT a revision changes (here "a part used alone") and give its definition-completeness question to ONE lens; the others cite it (r83: 3-4 lenses per root).
- P5 (pred evidence): a model exits non-zero iff its last line reports a failure (predbound exits 0 on "1 failed").

## Framework notes
- The coordinator pattern fit a design re-check with interlocking semantic claims well: one opus verifier over 15 grouped items took 9 min and returned 2 PARTLY corrections a draft would otherwise have carried.
- For design subjects whose evidence is an executable model, the highest-yield lens is one that enumerates the INPUT space of a rule (the grid) rather than the documents' own examples; this probably generalizes to any design with a model (memfn plan rows, selectors): "enumerate the rule's cells, then ask the text and the model each".

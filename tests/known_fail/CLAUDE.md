# tests/known_fail — deferred-bug regressions (expected to fail)

`.rxt` files here assert the **correct** behaviour for bugs that are CONFIRMED
but deliberately deferred rather than fixed now; each one has an entry in
`docs/dev/known_issues.md` with a minimal repro and the milestone that owns it.
`tests/harness/run.sh` excludes this directory from its default discovery, so
`make test` stays green and honest — a known bug does not get to look fixed,
and it does not get to break the build either.

## Files

- **`k34_leftrec_giveup.rxt`** — [K34] (`docs/dev/known_issues.md`), landed
  2026-08-24 by the [DD-14.D27] corpus's landing lane. Eleven cells, three
  patterns (`(a|(?1)a)`, `(a|(?1)a)b`, `(a|(?1)a)c`): pcrec `frames`
  gives-up where libpcre2 10.46 reaches a clean, definite NOMATCH on a
  runaway left recursion whose callee has a non-recursive alternative (so
  [DD-14.EMPTY]'s root-width nomatch does not apply — the language is not
  empty). **The population is NOT empty as of this landing** — the
  directory's "legitimate good state" note below describes the period
  2026-08-24 (post-[DD-14.LB]) to this same day (pre-K34-park). Ratchet
  line at landing: `still failing: 1    now passing: 0` (this file is the
  1). The `.rxt` is GENERATED, not hand-written — see
  `tests/recursion/d27/sr_gen.py`'s `parked=`/`parked_ref` mechanism
  (its own docstring) and `tests/recursion/d27/CLAUDE.md`: it is rendered
  in the SAME generator run that leaves a pointer stanza at each cell's
  former position in `tests/recursion/d27/sr_depth.rxt`, from the identical
  oracle-verified case data, so the pointer and this file cannot drift
  apart — unlike `u9_atomic.rxt`/the closed `dd14_bc_open.rxt`, both
  hand-copied from a generated corpus's oracle answers. Closes when K34's
  loop-rule measurement (`docs/dev/known_issues.md` K34 "What is needed")
  lands and this directory's ratchet flags it; move the cells to
  `tests/recursion/leftrec.rxt` or `sr_depth.rxt` per the "Removing one"
  convention below.
- **`k49_utf8_lookbehind_retry.rxt`** — [K49] (`docs/dev/known_issues.md`),
  landed 2026-09-05 by lane `utfprom` while promoting the D27 blinded
  `tests/utf8/` corpus against the merged [M5.0] stage 2 tree. One cell,
  moved from `tests/utf8/axis09_nextpos_findall.rxt`'s "midstart-row3-
  boundary" block (pointer comment left at its former position): `(?<!.)`
  (`--features lookaround`, `-e utf8`) at explicit `startpos=2` over
  `"\xce\xb1\xce\xb2"` (two 2-byte UTF-8 characters — position 2 is a real
  CHARACTER boundary, alpha ends there and beta begins). The D27 corpus's
  own ARGUED design position (extract Sec 2.6.1.1's mid-character-startpos
  table) says the correct answer is NO MATCH — the assertion is false at
  position 2, and an unanchored retry must only try LATER CHARACTER
  boundaries (the next is position 4, where the assertion is false again).
  pcrec's live answer is a MATCH at `(3,3)`, an offset INSIDE beta's own
  2-byte encoding and not a character boundary at all — suspected to be
  the unanchored search's zero-width-assertion retry stepping by BYTE
  rather than by CHARACTER under `-e utf8`. See the known_issues.md entry
  for the full mechanism writeup and what's needed to close it.
- **(EMPTY of `.rxt` from 2026-08-24 [DD-14.LB] until the same day's K34
  park, above)** — the legitimate good
  state this directory's own header describes: no confirmed bug and no owed
  ruling is currently deferred with a repro on file. The ratchet reports
  "nothing to ratchet" and exits 0. The two most recent residents both left by
  the front door rather than by being deleted:
  - `dd14_bc_open.rxt` — [DD-14] wave B+C's two open cells, a call inside a
    lookbehind. Closed by [DD-14.LB], and **the two cells went to different
    places, which was the finding**: cell 1 (`^(?:(?<g>ab)){0}ab(?<=(?&g))$`)
    now COMPILES and is a live match cell in `tests/recursion/inlookaround.rxt`
    — the deferred width re-check (`pcrec_postresolve`, src/opt/postresolve.c)
    was exactly the fix its charter named. Cell 2
    (`^(?:(?<g>a|ab)){0}ab(?<=(?&g))$`) is still refused and is a live *ruled*
    `perr` in the same file, because it was never the tier-2 timing
    over-rejection it was parked as: its lookbehind body is ONE top-level
    branch of width 1..2 (the alternation is inside the CALLEE), which is
    `(?<=(a|bc))x` reached through a call, and `lookaround_design.md` §2.5
    charters the longest-first step-back loop it needs rather than shipping
    it. The diagnostic is what told the two apart — it changed from "this one
    is unbounded" to "this one can match 1..2 characters" at the same offset.
    **The lesson is this directory's own rule read from the other side:** a
    parked cell states a CAUSE, and a cause is a claim that can be wrong. Cell
    2's said "timing"; fixing the timing left the refusal standing and
    corrected the sentence, which is how the real cause got named.
  - `d27_nested_min_boundary.rxt` — K23 (2026-08-16): `(a{10,20}){10,50}` on
    the exact-minimum 100-byte subject returned `RX_ERR_STEPS` where the oracle
    answered span (0,100)/group (90,100) instantly. Found by the D27 blinded
    quantifier corpus; MOVED to `tests/base/` at [M4.6d] (30a83ed) when the
    runtime follow-min term fixed it, exactly as the "Removing one" convention
    below requires.
- **(previously empty)** — from 2026-08-15 until K23, no confirmed bug was deferred with a
  repro on file, which the ratchet treats as a legitimate good state (it
  reports "nothing to ratchet" and exits 0). The last resident was
  `k18_empty_exit_through_seen_eps.rxt`, which moved to `tests/base/` when K18
  was fixed; it is worth reading as the worked example of this directory's
  contract, because the ratchet is what forced the move and the
  `known_issues.md` close to land in the SAME commit. Three sibling files
  joined it there (arm-order, `{0,2}` split shapes, deep nesting) — a deferred
  bug's repro is written from the bug as FOUND, and the fix lane owes the axes
  that repro's own alphabet could not reach
- **run_known_fail.sh** — the "fixed by accident" ratchet (R2-PR8). Runs each
  `.rxt` here and INVERTS the verdict: still-failing is expected, and a file
  that has started PASSING is flagged and fails the script. Part of
  `make test`. An empty directory exits 0.

## Conventions

Adding a deferred bug: write the `.rxt` asserting the behaviour PCRE actually
has (oracle-verified, same as any other corpus file), put it here, and add the
`docs/dev/known_issues.md` entry naming the owning milestone. Never weaken an
expectation to make a bug look fixed.

Removing one: when the ratchet flags a file, MOVE it into the matching
`tests/<module>/` directory so the fix gains a live regression, close the
`known_issues.md` entry, and journal it — a fix nobody intended is worth
understanding, because its scope may be accidental too.

Maintenance: update this file when the directory's contents or contract change.

## `dd14_bc_open.rxt` — CLOSED 2026-08-24 by [DD-14.LB]

Kept as this directory's WORKED EXAMPLE, because all three of its cells left
for a different reason and the three reasons are the whole contract.

**CELL 3 (`^(a?(?1)b)$`) WAS WRONG TO BE HERE AT ALL** (removed 2026-08-24 on
manager review, before the other two). A left recursion whose language is
empty, parked as an unruled disagreement because pcrec answers NOMATCH where
the generated corpus expected `gu frames`. **The corpus was wrong, not
pcrec.** Design §12 P-12 RULES that `minw = infinity` is a legal compile the
MRL prune reads as "no position can match", so the constant-time nomatch IS
the ruled answer, and §5.9 scores it "agreed in kind" with libpcre2's
`rc -52`. The generalisable error was in the EXPECTATION's provenance: **a
give-up is pcrec's own artifact behaviour, never an oracle fact**, so
`gu frames` could not have been read off libpcre2 and was never checked
against the ruling that governs it. The cell is now live in
`tests/recursion/leftrec.rxt`, rendered by a generalisation of
`gen_corpus.py`'s `GU` block — `code=None` plus a required `ruling=` citation
— which writes `n "ab"` and records libpcre2's `rc -52` as a shape cross-check.

**CELL 1 was parked correctly and the charter it named was right.**
`^(?:(?<g>ab)){0}ab(?<=(?&g))$` — a callee of fixed width 2 inside a
lookbehind — was a tier-2 over-rejection caused by TIMING: `la_widths`
(src/parse/mod_lookaround.c) runs in the parse hook, where it must, because
that is the only place with a pattern OFFSET to refuse at, and the call graph
does not exist until every call is resolved and every rewriting pass has run.
[DD-14.LB] built the deferred width re-check the parked note asked for — the
hook RECORDS (`u.look.at`, and `widths == NULL` on a lookbehind now means
pending), `pcrec_postresolve` (src/opt/postresolve.c) re-asks module
`lookaround`'s own rule after `pcrec_callgraph_build` — and the cell is now a
live match cell in `tests/recursion/inlookaround.rxt`.

**CELL 2 WAS PARKED WITH THE WRONG CAUSE, and that is the lesson worth
keeping.** `^(?:(?<g>a|ab)){0}ab(?<=(?&g))$` was parked alongside cell 1 as
the same tier-2 timing over-rejection. Fixing the timing did not make it
compile. Its lookbehind body is ONE top-level branch — an `A_CALL` — of width
1..2, because the alternation is inside the CALLEE; that is `(?<=(a|bc))x`
reached through a call, and `lookaround_design.md` §2.5 CHARTERS the
longest-first step-back loop it needs rather than shipping it.
`tests/lookaround/refused.rxt` has pinned the call-free twin as a D26 tier-2
CAPABILITY limit all along. The cell is now a live ruled `perr` in
`tests/recursion/inlookaround.rxt` with that citation.

**THE EVIDENCE THAT SEPARATED THEM WAS THE DIAGNOSTIC.** Cell 2's refusal
moved from "this one is unbounded" — a claim about the call graph, and false —
to "this one can match 1..2 characters" — a claim about the shipped subset,
and true — at the same offset. Nothing else about the cell changed.

**THE RULE THIS DIRECTORY SHOULD BE READ BY, restated in three lines:**

- Park a cell when pcrec disagrees with a RULING.
- Do not park one when pcrec disagrees with an EXPECTATION nobody checked
  against a ruling — that is a corpus fix (cell 3).
- **A parked cell's stated CAUSE is a claim, and it can be wrong even when the
  disagreement is real** (cell 2). Discharging the named cause is not the same
  as closing the cell; re-measure before assuming the two coincide.

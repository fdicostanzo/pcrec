# tests/known_fail — deferred-bug regressions (expected to fail)

`.rxt` files here assert the **correct** behaviour for bugs that are CONFIRMED
but deliberately deferred rather than fixed now; each one has an entry in
`docs/dev/known_issues.md` with a minimal repro and the milestone that owns it.
`tests/harness/run.sh` excludes this directory from its default discovery, so
`make test` stays green and honest — a known bug does not get to look fixed,
and it does not get to break the build either.

## Files

- **`k64_precheck_forced_vm.rxt` — GONE, 2026-09-25, RETIRED AT MERGE (lane
  `chkgaps` landed it as standing check-gap coverage while K64 was still
  open; lane `k64fix` fixed K64 the same day, concurrently, with its own
  regression at `tests/base/k64_precheck_forced_vm.rxt` — same basename,
  same witness pattern `^([a-zA-Z0-9._%+-]+)+@` under `--engine=vm`,
  budget `steps=10000`).** Lived here 2026-09-25 only, never shipped in a
  `make test` run from this directory. The fix's own regression is a
  SUPERSET of this file's population (both the anchored/framed block this
  file carried AND a second frameless-arm block, plus the `gu` control
  proving the budget really reaches the VM), so retiring rather than
  promoting-in-place is the K34 close's own precedent applied the other
  direction: where K34's cells had no other home and were placed BY HAND
  into an already-counted file, this file's cells already had a home that
  landed independently, and keeping both would be two files asserting the
  identical claim. `docs/dev/known_issues.md` K64 is CLOSED (fix A,
  lane `k64fix`); this file's own two check-gap closures (the axes
  `GIVEUP1` bucket in `tests/axes/dump_diff.awk`/`run_axes.sh`, and
  `tests/codegen/run_prechecks.sh` §5.7's UNANCHORED positive control,
  sabotage S276) are UNRETIRED and stand on their own — they close a reach
  gap (no check before this compiled a forced-VM route outside K64's own
  narrow anchored witness) that is independent of which fix landed, and
  §5.7's own witness is deliberately NOT K64's population (see that
  section's header). See `docs/dev/lanes/chkgapsmerge_report.md` for the
  merge-time reconciliation.
- **`k34_leftrec_giveup.rxt` — GONE, 2026-09-23, by the front door
  ([OPTLOOP.1.impl] batch 2, lane `optimpl2`; the known-fail triage, lane
  `b2fix`).** Lived here 2026-08-24 .. 2026-09-23. [K34] (`docs/dev/
  known_issues.md`): pcrec `frames` gave up where libpcre2 10.46 reaches a
  clean, definite NOMATCH on a runaway left recursion whose callee has a
  non-recursive alternative. **NOT closed by K34's own charted "What is
  needed" (measuring PCRE2's `−52` loop rule) — D74 declined that route and
  it is still declined.** `[OPT-REQPOS]` tier 2b (the necessary
  CONTIGUOUS-LITERAL-RUN precheck) landed as an unrelated general
  optimization and, as a side effect, proves every match of `(a|(?1)a)`
  (and its `b`/`c`-tailed siblings) ends in a fixed literal REGARDLESS OF
  RECURSION DEPTH — branch 1 IS `"a"`, branch 2 always appends a trailing
  literal `"a"` after its call — so a subject lacking that literal (or the
  run `"ab"`/`"ac"` once the outer literal joins it) concludes NOMATCH in
  O(1) without ever entering the recursion. All 11 cells now pass; see
  `docs/dev/known_issues.md` K34's CLOSED note for the full mechanism and
  why this is a genuine resolution and not a `[MECH-REACH]` check-witness
  artifact. The 11 cells went back to their originally-parked position in
  `tests/recursion/d27/sr_depth.rxt`, placed BY HAND (this box's dlopen
  shim resolves libpcre2 10.42, not the pinned 10.46 reference, so a live
  `sr_gen.py` regeneration here would have re-derived the whole ten-file
  D27 corpus against the wrong oracle) — `sr_gen.py`'s spec was still
  edited so a future correctly-oracled regeneration reproduces the live
  cells rather than re-parking them.
- **`k49_utf8_lookbehind_retry.rxt` — GONE, 2026-09-05, by the front door.**
  It lived here for one day. Lane `utfprom` parked it at promotion (the
  `(?<!.)` mid-character retry, `(3,3)`); lane `k49fix` FIXED K49 the same
  day and the cell went back to its authored position in
  `tests/utf8/axis09_nextpos_findall.rxt`, green, with the pointer comment
  removed. The mechanism and the fix are in `docs/dev/known_issues.md` K49.
  **The one-day residency is itself the argument for this directory**: the
  cell was found by a blinded corpus, parked rather than argued away, and
  the park is what made it a schedulable piece of work instead of a note.
- **`k50_utf8_dfa_midchar_start.rxt`** — [K50] (`docs/dev/known_issues.md`),
  landed 2026-09-05 by lane `k49fix`, which found it while fixing K49 by
  asking whether the OTHER engine's "try the next start" mechanism had the
  same hazard. One cell: `\B` (`--features assertions`, `-e utf8`) at
  `startpos=0` over `"a\xce\xb1"` (`61 CE B1`; character boundaries 0, 1
  and 3). pcrec reports `(2,2)` — inside alpha's own encoding — because the
  DFA's start-anywhere self-loop (`src/ir/nfa.c:965`, a class of every byte)
  lets a match START at any byte offset under `-e utf8`.
  **UNLIKE ITS PREDECESSOR ABOVE, THIS CELL IS ORACLE-BACKED RATHER THAN
  ARGUED — and the filing instruction said to mark it ARGUED, so the
  correction is recorded here rather than silently applied.** The
  distinction is the useful part: K49's expectation was
  `pcrec-ARGUED` because no engine produces that cell at all, whereas
  libpcre2 10.37 answers `(3,3)` here under BOTH `PCRE2_UTF` and
  `PCRE2_UTF|PCRE2_MATCH_INVALID_UTF`, and `(2,2)` only under `options=0`.
  So pcrec's UTF-8 build is returning the BYTE answer, and D26 settles it
  without anyone needing to rule. It also reaches from an ORDINARY
  `startpos=0`, where K49 needed an explicit mid-loop `startpos`. Closes
  when the DFA's candidate match starts are confined to character
  boundaries — see K50's entry for the constraint any fix must respect
  (§2.6(c) requires a search to still find matches after an ill-formed
  byte, so the loop must keep traversing them; only the SPLIT into the
  pattern may be gated).
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

## `k53_uprops_oversize.rxt` — GONE, 2026-09-10, by the front door ([M5.0] stage 3, 2026-09-06 .. [K53-SELRETRY], 2026-09-10)

**Four days' residency, and the entry below is kept because the file did
exactly what this directory is for.** Lane `utf8k53` fixed K53 — the driver
drops the OPTIONAL anchored machine and re-emits when an emitted-size cap
refuses an artifact carrying one — and all sixteen blocks went back to their
authored positions: twelve to `tests/utf8/axis04_p_categories.rxt` and four to
`tests/utf8/axis12_scripts.rxt`, running **590/0** there.

**THE POSITIONS WERE RECOVERABLE WITHOUT A POINTER STANZA, and how is worth
knowing before the next lift.** The stage-3 lift left none (unlike
`axis12_scripts.rxt`, which carried one sentence). What made the twelve
placeable is that `axis04` is written in the CANONICAL Unicode
general-category order — one-letter `L M N P S Z C`, then `Lu..Co Cn` — so the
gaps were exactly where `L`, `C` and `Cn` belong, and the file's own header
count (148 blocks) said how many were missing. **A generated corpus's ORDER is
a pointer stanza nobody has to write**; a hand-ordered one would have needed
the stanza.

**AND THE RUN THAT PUT THEM BACK WAS THE FIRST TIME THEIR ORACLES WERE
EXERCISED.** Every expectation had been carried verbatim since the blinded
authoring, through a park in which the patterns did not compile — so nothing
had ever checked them against anything. All agreed. That is [M5.0] stage 4's
§3.4 lesson read from the good side: *a parked cell's carried oracle is an
unchecked claim until the construct compiles*, and the day it compiles is the
day the claim is settled.

The original entry, for the record:

## `k53_uprops_oversize.rxt` ([M5.0] stage 3, 2026-09-06)

Twelve blocks lifted out of `tests/utf8/axis04_p_categories.rxt` at that
corpus's promotion — the D27-blinded `\p` axis — for `\p{C}`, `\p{Cn}`,
`\p{L}` and their `\P` forms.

**They are here rather than downgraded to `perr`, and the distinction is the
whole point.** `perr` asserts that pcrec refuses, which pcrec does; but WHY it
refuses is a resource cap, not a fact about the language, and pinning it as a
refusal would record a limitation as if it were a promise. The blocks carry
the oracle's own answers (unchanged since the corpus was written) and the
ratchet fires the day the limitation lifts.

`docs/dev/known_issues.md` K53 has the diagnosis, which is an ENGINE one:
the OPTIONAL anchored DFA machine's bytes count toward `max_emit_bytes`, so it
refuses patterns that compile without it — `\p{L}` under `-e utf8` is
1,076,640 bytes at default axes and **772,412 with `-fno-anchored-dfa`**,
against a 1,000,000 cap. That contradicts that machine's own design promise
(`anchored_match_unwrapped.md` §2/§5.2: *"built OPTIONAL — an overflow is a
selection outcome, never a diagnostic"*), which `src/core/compile.c` keeps for
the subset-elems budget and not for this one.

**So the file's own "does it start passing" signal is pointed at an engine
change, not at module `unicode-props`.** A future reader seeing it go green
should look for the emit-bytes retry, not for a table edit.

**[M5.0] STAGE 5 ADDED FOUR MORE BLOCKS AND THE COUNT IS THE INTERESTING
PART.** Of 684 script patterns measured at default axes under `-e utf8`,
exactly TWO refuse — one SET under two names — and the four blocks are its four
spellings: `\p{Unknown}`, `\p{sc=Unknown}`, `\p{scx=Unknown}`, `\p{Zzzz}`.
They are written out rather than folded into one block because they are four
different LOOKUPS reaching one set, and a cure that fixed the bare spelling
alone would leave three red. `\P{Unknown}` compiles and is a live block in
`tests/utf8/axis12_scripts.rxt`; every other script compiles too, the largest
at a third of the cap. `\p{Unknown}` is the DERIVED complement of every listed
script, so it is the one script property with `\p{C}`'s shape rather than a
script's — which is why the prediction that scripts would be a large K53
population is refuted rather than confirmed by this addition.

Their expectations are the **10.46 reference's own answers**, from the same
probe that produced `axis12_scripts.rxt`.

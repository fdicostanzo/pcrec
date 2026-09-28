# admin88 — plan.md/decisions.md bookkeeping pass (2026-09-28)

Lane `admin88` (sonnet, ADMIN tier, DOCS ONLY). Branch `lane/admin88`,
worktree `worktrees/admin88`. Applies rulings Frank already made; nothing
here is new judgment except where explicitly noted as a scope decision.

No `make` run (nothing under `src/`/`cli/`/`lib/` touched; one line of
descriptive prose changed under `tests/mech/sabotages/`, not a check's
logic). `git diff --stat main..lane/admin88`:

```
 docs/dev/decisions.md                              |  60 ++++++
 docs/dev/known_issues.md                           |  23 +++
 docs/dev/plan.md                                   | 201 +++++++++------------
 docs/dev/plan_completed.md                         | 112 ++++++++++++
 tests/mech/sabotages/S203_rxt_head_detector_fires.sh |  11 +-
 5 files changed, 289 insertions(+), 118 deletions(-)
```

## (a) Phase-3 dispositions (`docs/dev/ph3_reassessment_2026-09-28.md`)

All eleven rows dispositioned as Frank AGREED:

- `[TT-4M]` (plan.md:310) — RE-PARK confirmation appended (trigger:
  Frank's own word, still unmet).
- `[DD-8]` (plan.md ~926, now archived-adjacent) — CLOSED
  (`STATE:started` → `STATE:completed`); residual filed as new row
  `[EMIT-DOT]` (plan.md:926, `STATE:not-started`).
- `[DD-11]` — RE-CHARTERED: opened `[DD-11.5]` (plan.md:1126,
  `STATE:not-started`) as its own child row per
  `docs/design/definitions_table.md`'s own "[DD-11.5]" section.
- `[CC-CLANG]` (plan.md:1147) — STEP 3 CLOSED (not merely re-chartered:
  the ask is already answered by the bench's standing cc axis, O-70/
  `[B33]`/`[B24]`, PARITY at `a32bc86e`, byte mode only — utf8 gap
  recorded as an open note, not a blocker).
- `[OPT-3]`, `[OPT-5]`, `[ENG-ABS]`, `[ENG-ISL]`, `[DD-13]` (plan.md:927),
  `[DD-13b.W1.3]` (plan.md:972) — RE-PARK confirmations appended, each
  restating its own unmet trigger from the reassessment doc.
- `[CLS-TREE]` (plan.md:1532) — RE-CHARTERED with the re-baseline:
  `\p{Xwd}` on the DFA is 197,685 B at the current pin, not the study's
  own 294,153 B at an earlier pin (`docs/dev/ucp_study.md` §G item 4).
  The `[UCP]` row's own stale "294 KB today" citation (it already had
  the correct 197,685 B figure elsewhere in the SAME row — an internal
  inconsistency) was corrected too, drive-by.

## (b) `[FINDINGS]` row (plan.md:360)

- B4: **HELD, option (c)** recorded verbatim (no reader has a trigger —
  C6 needs unbuilt S4, C3's cells are S1-dominated, C2 has only 16
  synthetic movers); `lane/findb4` (`e054d1ce`) stays parked, data half
  lands with S4.
- B5 (`lane/findb5`) and B6 (`lane/findb6`): re-pinned from "NOT merged"
  to their actual merge commits, `d604bee9` and `dcf25a49`.
- `[FIND-TIE]` (plan.md:362): `STATE:started` → `STATE:completed`; its
  stale "OWED to the manager at merge" census/sabotage text replaced
  with the actual result (merged `72e3ae41`; 134/5,751 byte movers, 0
  utf8; S329 DETECTED).

## (c) `[PATFACTS]` row (plan.md:495)

STEP 3.6 (lane pf36) re-pinned to its merge commit `f74bd589` and marked
as closing the whole STEP 3 migration — every relocation chartered
(3.0a/3.0/3.1/3.2/3.4/3.5/3.6) is now delivered+merged. §11.6 check 1
(PATFACTS non-perturbation) reaffirmed HELD by D126 — unchanged, no
action needed there.

## (d) optc2 residual rows + `[OPTLOOP.1.impl]` stale-tail sweep

Filed both proposed rows from `docs/dev/optloop/cycle2_close.md` §2
(neither had an existing row, confirmed by grep before filing):
- `[CAPS-VIEW-RERENDER]` (plan.md:353) — re-render `cycle1_caps_view.md`'s
  CAPS table under the frozen I-99/I-100 classification at the current
  pin.
- `[CAPTURES-DFA-MB]` (plan.md:354) — finish `captures_via_dfa_survey.md`
  candidate (c)'s M-B measurement at larger subject sizes.

Swept `[OPTLOOP.1.M6]` (plan.md:348): its own measurement (`cycle1_
profile.md`, run via the I-85 profile pass) actually completed and the
row's STATE tag was simply never flipped — now `STATE:completed` with
the finding recorded (steps-per-attempt problem, not per-step/dispatch).

## (e) findb2 follow-up row

Filed `[RUNSH-BUNDLE-DECL]` (plan.md:1539): the remaining half of
tri86's declaration-gate work — `run.sh` recognises a head-only analysis
bundle by declaration only under `--dump` today; `adversarial/`/
`witness/`/`golden/` still need a path-shaped `-not -path` exclusion for
every OTHER mode, because five of golden's files use an analyzer dialect
`pcrec --list-source` cannot parse at all yet. Filed, not scheduled.

## (f) Archive resident `STATE:completed` rows

Archived four unambiguous backlog rows verbatim to `plan_completed.md`
(new `## Archived 2026-09-28` section), following the `lane admin2`
2026-09-22 precedent for this exact job (full removal, no pointer line
— that precedent supersedes the earlier "row archived, one-line pointer
left" convention I found used further back in the file's history):
`[TT-4]`+`[TT-4.1]`, `[SPEC-1]`, `[UTF8-ATTRIB]`, `[OPT-VMFL]`. Each
row's header and both boundary lines were asserted programmatically
before the edit landed (see the commit message).

**Left resident, deliberately:**
- `[SPEC-1.9]` and `[DD-4]` — tagged `STATE:completed-in-place`, a
  distinct, intentional disposition (their own text: "retained... rather
  than archived" / "declared spec-tier in place"). Not touched.
- `[DD-8]` and `[FIND-TIE]` — closed by this very admin88 pass today,
  not pre-existing backlog debt. Left for a future sweep once they've
  aged, consistent with what the four archived rows looked like before
  today.

**Left resident, flagged as an open question for the manager/Frank:**
completed children nested under a still-open or merely-PARKED parent
row — `[OPTLOOP]`'s eight mechanism-completion children (`[OPTLOOP.1.
analysis]`, `[OPTLOOP.2.analysis]`, `[OPT-ANCHOR-VM]`, `[OPT-ENDWIN]`,
`[OPTLOOP.1.M6]`, `[OPT-PRECHECK-ADMIT]`, `[OPT-FREQPICK]`, `[OPT-
REQPOS]`, `[OPT-REQRUN-ENC]`), `[ENG-ISL.S0]` (child of PARKED
`[ENG-ISL]`), and `[DD-13a]`/`[DD-13b.W1]`/`[DD-13b]`/`[DD-13b.panel]`
(children of PARKED `[DD-13]`). I found no precedent anywhere in
`plan_completed.md`'s archiving history for moving a completed CHILD row
out while its umbrella row stays `STATE:started`/PARKED in `plan.md` —
every existing archived-children example (`[MOD-0.7a]`, `[M4.5a]`, etc.)
moved as part of the WHOLE parent milestone closing at once. Archiving
these piecemeal risks fragmenting a narrative still actively read
top-to-bottom (`[OPTLOOP]`'s own text walks through its mechanism
history in order); I did not judge that call myself and left it filed
here for a ruling rather than guess.

## (g) `docs/dev/decisions.md` D128

Added, closing D127's own "also owed" list (five session-82 rulings,
all already acted on elsewhere — each entry here is a pointer, not new
judgment) plus the 2026-09-28 rulings: B4 HELD option (c); FIND-TIE
(run reader's data tie follows its NONE order = rightmost, abi 43→44,
S329); all eleven phase-3 dispositions; the CC-CLANG STEP 3 closure.

## (h) S203's stale `SAB_DESC` prose

Grepped for S203/SAB_DESC: `tests/mech/sabotages/S203_rxt_head_detector_
fires.sh`. It was stale in the way tri86's own report already flagged
("Not fixed, flagged only") — `SAB_DESC` said "all 210 corpus files,"
a count from an even earlier pin's own re-statement of an original
"179." The live `CENSUS_FILES` at this pin (`tests/rxtsource/
run_rxtsource_tests.sh`) is 247. Fixed the string to 247 and added a
dated re-statement comment in the same style as the existing one,
noting this is descriptive text only (mech scores DETECTED/UNDETECTED,
never this string).

## (i) `known_issues.md` K71

Filed the `RX_ENGINE_WHY` kind/offset mismatch `docs/dev/ucp_study.md`
§G item 2 found (`x(?<=a)(?!b)` stamps `"(?!...) at pattern offset 1"`
where offset 1 is actually the `(?<=`) as K71 — OPEN, diagnostic-text
only, not an answer-correctness defect (no `tests/known_fail/` repro
filed).

## Two rows from lane/tri87's report

Filed `[CORPUS-PCAP]` (plan.md:1540) from `docs/dev/lanes/tri87_report.
md` on branch `lane/tri87` §6: `test-corpus`'s intermittent `TIMED OUT`
reds are `PROCS=nproc` oversubscription noise on this Mac (8P+2E cores,
`nproc`=10), not a regression — tri87 measured two entirely different
9-case populations across two red runs, both reproducing clean
standalone. One row, two candidates named inside it (the brief's own
text gave one tag, `[CORPUS-PCAP]`, for both items rather than two
separate tags, and tri87's own report frames them the same way — one
disposition section, two candidates): (1) cap `test-corpus`'s internal
worker concurrency to the box's own performance-core count on darwin
(`hw.perflevel0.physicalcpu`) rather than bare `nproc`; (2) a serialized
retry-on-timeout backstop. Filed, not scheduled.

## Ambiguities / things I could not resolve myself

1. **Item (f)'s nested-children question**, above — genuinely no
   precedent either way; flagged rather than guessed.
2. **`[CORPUS-PCAP]` as one row vs. two**: the brief's prose said "file
   two rows" but named only one tag (`[CORPUS-PCAP]`) for two numbered
   items. I filed one row carrying both candidates, matching how
   tri87's own report presents them (one §6, two candidates, one
   recommended as primary). If two separate tags were intended, they
   are easy to split out of this one row later.
3. I did **not** re-run any check, battery, or `make` target — this
   lane is DOCS ONLY and nothing under `src/`/`cli/`/`lib/`/`tests/`'s
   own check LOGIC changed (the one `tests/` edit is a sabotage row's
   descriptive string, not its assertion).

## Not touched

No `CLAUDE.md` needed updating — no file was added/removed/re-roled
by this pass (only prose inside existing files changed).

# Plan audit — census of `STATE:started` rows, 2026-09-19

Read-only census for Frank's planning question: once current plan items
finish, are there OPEN items that were INTERRUPTED and need completing?
Lane `planaudit`, worktree `worktrees/planaudit`. Nothing under `src/`,
`tests/`, or `docs/dev/plan.md` itself was touched; no `make` was run.

## Population note (a finding before the table)

`grep -n "STATE:started" docs/dev/plan.md` returns **43** lines, but most
of those are prose elsewhere in a row's own text — mid-paragraph phrases
like *"formerly STATE:started"* recording a row's history, not a row's
own current tag. Filtering to the format `docs/dev/plan.md` itself
documents (`^- \[TAG\] STATE:<state>`, i.e. the state token immediately
follows the tag) gives the TRUE population: **26 rows**. Of those, six
are this session's own work and were excluded per the brief
(`[REVW.4]`, `[REVW.2]`, `[DD-8]` — present; `[EMIT-VERB]` is actually
`STATE:not-started`, `[BSWEEP]`/`[ALLOC-PINS]` are actually
`STATE:completed`, so those three were never in the true population).
**23 rows were actually audited**, below.

## §1 Census, grouped by disposition (FINISH first, by size)

### FINISH — real remaining work

| tag | opened | last dated event | owed (≤15 words) | lane/branch/worktree | size |
|---|---|---|---|---|---|
| `[LIM-2]` | 2026-09-02, Frank's ruling (charter); lane `lim2` 2026-09-04 | 2026-09-17 (dfam12 M1+M2, explicitly says LIM-2's own remaining work is unaffected) | N2 (sound margin from closed-subgraph block count) — "OPEN FOR FRANK: charter M1 and/or N2," never chartered | lane/lim2 gone (merged 86e66dcd, mechanism itself reverted); `lane/m1part` for the later M1 study | S |
| `[OPT-EDGE]` | 2026-09-03, lane B `edge1` | 2026-09-04 (STEP 1.1 merged 81ef3044, abi 21) | re-measure the UNSTABLE m=2 scan-chain cell (bimodal, spec says re-measure); the entry-cost a+b·k fit | branch gone (merged); no open worktree | S |
| `[ENG-ISL]` | 2026-08-18 design thread; STEP 1 chartered 2026-09-03 | 2026-09-04 (STEP 1 merged cee7c741, abi 18) | STEP 2 shapes — the `ab[cd]\|abx` tail form, class-member expansion — named, never chartered | branch gone (merged) | M |
| `[DD-13b.W1.3]` | 2026-09-03, lane `w13` | 2026-09-04 (merged 8d68ddc2, abi 20) | W1.3.1 (run.sh composed-block path) ruled but blocked on `[PFX-1]` (STATE:not-started); `(?&site.group)`; W1.4 | branch gone (merged); blocker `[PFX-1]` unstarted | M |
| `[DD-13]` | 2026-08-17, Frank (umbrella tag for the whole pattern-source format) | 2026-08-26 on the row's own text (stamps half); superseded by DD-13b.W1.3's more recent 2026-09-04 | same chain as DD-13b.W1.3 above (its own child row) — W1.3.1/W1.4/site.group | see DD-13b.W1.3 | M |
| `[CLS-TREE]` | 2026-09-10, Frank (charter) | 2026-09-16 (+2 placement ruling, feeding the still-unwritten design note) | the design note + D6 panel + implementation — study and its ns/char timing gate are BOTH done, design note not yet written | lane `clstudy` gone (merged 039cfffb); no design-phase worktree open | L |

### COMPLETE-IN-PLACE — the work is done, the tag is stale

| tag | opened | last dated event | evidence it is done |
|---|---|---|---|
| `[K50-NULLGATE]` | 2026-09-06, chartered at K50 merge's red | 2026-09-06 | journal "[K50-NULLGATE] merged" same session (8 commits, no abi bump); "Owed: the Linux full battery" superseded by every full `make test` run since, including the 2026-09-19 `[REVW.3]` gate |
| `[ENCCHK-DD12A]` | 2026-09-05, chartered by manager at K52's filing | 2026-09-06 | merged same session as K50-NULLGATE (journal: "the sabotage-id collision with encchk's morning merge"); `test-encoding-checks` reads green repeatedly afterward (e.g. "encchk 11/0" multiple later sessions) |
| `[TT-12]` | 2026-09-02, Frank (charter) | 2026-09-04 (STEP 2 battery-proven, union chain green) | row's own text: STEP 0/1/2 all measured/merged/battery-proven; `scripts/battery.sh` (battery_v5) is the standing battery shape used ever since. Its one loose end (STEP 3, mech tiering) was explicitly forked into its own row, `[TT-13]` (STATE:not-started) |
| `[DD-13b.W1]` | 2026-08-30, on the DD-13b design's lift | 2026-09-01 (W1.2 merged + battery-proven) | row's own text: W1.1 and W1.2 both MERGED + BATTERY-PROVEN; all further work already lives under the separately-tracked `[DD-13b.W1.3]` row above |
| `[OPT-DIAL]` | 2026-09-03, Frank ("It can be switched...") | plan row's own text stops at "IMPLEMENTATION CHARTERED" (2026-09-16), but the implementation shipped and merged 2026-09-17 (K59 fixed, dial+K59 train solo battery green) — **the plan row was never updated after delivery** | `known_issues.md` K59 "FIXED 2026-09-17 (lane k59rung...)"; `docs/dev/lanes/dialimpl_report.md`, `dialsweep_report.md`, `dialtrain_byteid.md` all confirm merged + battery-proven |
| `[CC-DIFF]` | 2026-09-02, Frank (charter) | 2026-09-04 (STEP 2 merged 584b4db7, abi 22) | row's own text: STEP 1 + STEP 2 both merged; "Union chain... owed" was the same 2026-09-04 union chain TT-12's row records as green |
| `[ART-SIZE]` | 2026-08-28, Frank ("Go 1&2") | 2026-08-29 (STEP 2 battery-proven, merged 6e37a4c) | row's own words: **"STEP 2 is DONE; the row stays STARTED as the record's home until [ART-SIZE] is archived with STEP 1"** — explicitly a bookkeeping artifact, not open work |

### PARK — deliberately deferred by a ruling

| tag | opened | last dated event | the ruling that parks it |
|---|---|---|---|
| `[TT-4M]` | 2026-09-08, Frank (charter) | 2026-09-16 | Frank, 2026-09-16: "the HARNESS_BATCH default is NOT flipped... NOT SCHEDULED — do not charter without Frank's word" |
| `[SPEC-1]` | 2026-08-25, Frank (D80) | 2026-08-25 (row); its one open child `[SPEC-1.11]` dated 2026-08-29 | 10 of 11 sub-rows completed; the 11th, `[SPEC-1.11]`, is explicitly "BOONIES TIER — LATE GAME... Starts only on Frank's word" |
| `[DD-11]` | pre-2026-08-12 (assertions/newline work) | 2026-08-30 (battery-proven core) | row's own text on the newline-convention residual: "Decide with the assertions module or a real consumer, whichever asks first" — no consumer yet |
| `[CC-CLANG]` | 2026-08-30, Frank ("i installed clang...") | 2026-09-02 | STEPs 1+2 merged (abi 14, has_push gate, CLANGGEN=1); STEP 3 is explicitly "behind Frank's perf hold" |
| `[OPT-3]` | 2026-08-25 | 2026-08-26 (STEP 1+2 measured/built, abi 7) | STEP 1+2 delivered; every STEP-3 candidate (branch speculation, two-byte transition table) is individually marked "D77: not chartered" |
| `[OPT-5]` | 2026-08-30 | 2026-09-03 (STEP 2 battery-proven, abi 16, pin 288d505) | STEP 0-2 delivered/merged; STEP-3 candidates (period-k scan edge, construction-time synthesis, reverse-pass elision) each individually "D77 trigger: not chartered" |
| `[OPT-4.2]` | 2026-08-31 | 2026-09-03 | merged + battery-proven (`ESEL_DECLINED_NULLABLE_DEFAULT`, no abi bump); Frank, 2026-09-03: witness-gap "WAIT FOR A WITNESS — no row, no hunt"; bench cls-* re-measure item "NEEDS FRANK'S CHARTER" (not given) |
| `[OPT-VMFL]` | 2026-09-02, Frank (charter) | 2026-09-02 (stamp shipped, riding opt5i's abi 16) | the dispatcher itself: vmfl0's own measurement found "the D77 trigger for building the dispatcher for real is NOT met by this evidence" |
| `[ENG-ABS]` | 2026-08-18 design thread | 2026-08-29 (second mechanism merged + battery-proven, abi 10) | row's own text: the SECOND mechanism is fully merged; the FIRST mechanism (`^`-absorption) "stays gated on `[BENCH-1]`... and is NOT opened" — and `[BENCH-1]` itself is UNCLEAR (below) |

### UNCLEAR — a fact is missing

| tag | opened | last dated event | what's missing |
|---|---|---|---|
| `[BENCH-1]` | 2026-08-13, Frank (charter) | 2026-09-03 (syntax-census sub-task chartered as bench inbox item I-42) | this row is bench-owned: pcrec sent I-42 (a wide syntax census) to pcrec-bench 2026-09-03 ("first sample in ONE night... the third night from now at the earliest") and no later journal entry records a result coming back. Whether the bench ever ran it, and what it found, is not answerable from this repo — the fact is in pcrec-bench's own inbox/outbox channel, which this lane did not read (out of the read-only census's scope; the manager can check `pcrec-bench/docs/dev/outbox_to_pcrec.md` for an I-42 response) |

### Skipped (this session's own work, per the brief)

`[REVW.4]`, `[REVW.2]`, `[DD-8]` — all `STATE:started`, all current-session
lanes the manager already knows the state of. Not audited.

## §2 The FINISH rows, ordered by size (smallest first)

1. **`[LIM-2]` (S)** — a cheap, sound margin fix (N2: project a lower
   bound from the closed subgraph's own minimized block count, rather
   than the raw subset-construction count the original mechanism used
   and had to be reverted over). Needs only Frank's charter; has needed
   it since 2026-09-04.
2. **`[OPT-EDGE]` (S)** — two loose measurements: the `m=2` scan-chain
   floor cell reads bimodal/unstable and the row's own spec says
   re-measure it; the entry-cost `a+b·k` fit was never taken.
3. **`[ENG-ISL]` (M)** — STEP 2 of the alternation island: the
   `ab[cd]|abx` tail-form shape and class-member expansion, both named
   at STEP 1's landing, neither chartered since.
4. **`[DD-13b.W1.3]` / `[DD-13]` (M, same chain)** — W1.3.1 (the
   run.sh composed-block path) was RULED (Option 1: carry the target's
   prefix through `flush_block`) but gated on `[PFX-1]` landing first,
   and `[PFX-1]` is itself still `STATE:not-started`; `(?&site.group)`
   references and W1.4 (PCRE2 grouplist semantics) sit behind that.
   `[DD-13]` is the umbrella tag for this same chain — nothing separate
   is owed under it once W1.3.1/W1.4 land.
5. **`[CLS-TREE]` (L)** — the study and its ns/char timing gate are
   both fully delivered (2026-09-11); the design note, the D6 panel,
   and the actual kit implementation across the class-matching
   subsystem have not started. This is the largest genuinely-open item
   in the population — a full design-then-build phase, not a loose end.

## §3 Parent/child state disagreement

One case matches the pattern the brief asks about, on inspection it is
**not a defect**: `[DD-13b]` itself is `STATE:completed` while its two
child rows `[DD-13b.W1]` and `[DD-13b.W1.3]` are `STATE:started`. This
is not a stale parent — `[DD-13b]` is the DESIGN NOTE step (merged
2026-08-29, its own text says "the note has no open questions"), and
`[DD-13b.W1]`/`.W1.3` are the IMPLEMENTATION steps that came AFTER it,
nested under it in the file by naming convention rather than by a
completion relationship. No other row in the audited population showed
a parent/child state mismatch (`[SPEC-1]`'s 10-of-11-completed children
is the expected shape for a `STATE:started` parent, not a mismatch).

## Summary for the manager

- **26** rows are truly `STATE:started` today (not the 43 a bare grep
  suggests — the grep count double-counts historical "formerly
  STATE:started" prose inside other rows' own text).
- Of the 23 audited (3 skipped as this session's own): **7
  COMPLETE-IN-PLACE** (stale tags, ready to archive), **9 PARK**
  (each cites its own deliberate deferral — mostly D77 "not chartered"
  or an explicit Frank ruling), **6 FINISH** (real work, sized S/S/M/M/M/L
  above), **1 UNCLEAR** (`[BENCH-1]`, bench-side fact missing).
- The sharpest finding for "are there interrupted items": **no**, in
  the sense of abandoned mid-flight work — every FINISH row's remaining
  work is either explicitly ruled-and-waiting-on-a-precondition
  (`[LIM-2]`, `[DD-13b.W1.3]`/`[DD-13]`) or simply never chartered as a
  next step after its predecessor landed (`[ENG-ISL]`, `[OPT-EDGE]`,
  `[CLS-TREE]`). Nothing was dropped mid-build.
- The bigger finding is **staleness**: `[OPT-DIAL]`, `[CC-DIFF]`, and
  `[ART-SIZE]` are fully delivered, merged, and battery-proven, but
  their `plan.md` rows were never flipped to `STATE:completed` (in
  `[OPT-DIAL]`'s case, the row's own text stops mid-implementation and
  was never updated after the actual 2026-09-17 delivery at all).
  `[K50-NULLGATE]`, `[ENCCHK-DD12A]`, `[TT-12]`, and `[DD-13b.W1]` are
  the same shape. Archiving these seven rows to `plan_completed.md`
  is the highest-value, lowest-risk cleanup this audit found.

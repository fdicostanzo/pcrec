# [REVW.5.1] WAVE 5 RIDER — LANE REPORT

Lane `w5r` (sonnet), worktree `worktrees/w5r`, branch `lane/w5r` from
`main` at `fcf35d89` (wave 5 merged, zero non-`pcrec_` exports). Three
small items wave 5 flagged and did not build.

---

## Item 1 — `--flavour` gets its own applies-to relation

**Built as scoped.** `cli/main.c`'s `CLI_MODE_TABLE` drops the `FLAVOUR`
row (14 modes -> 13). A new `CLI_MODES_FLAVOUR_APPLIES` macro names the
three modes `--flavour` composes with (`--list-syntax`,
`--list-definitions`, `--explain`). Every other mode still refuses it,
with the diagnostic wording each site already had — D26, no wording
change: the five `if (flavour)` guards become
`if (flavour && !(modes & CLI_MODES_FLAVOUR_APPLIES))`, which is
behaviourally identical at each of them (verified by tracing dispatch
order at every site: by the time each guard runs, the three applies-to
modes are provably absent from `modes` already, since any of them being
active would have returned earlier in the function) but states the rule
once instead of leaving it implicit in block order and in a hand-spelled
five-name disjunction (the registry-query family's own site used to spell
`(list_verbs || list_families || list_axes || list_limits ||
list_schema) && flavour`; that is now the same one-line guard as
everywhere else).

`--source`'s own conflict check (`CLI_MODES_VS_SOURCE`) is the one site
whose behaviour needed an explicit rebuild rather than a restatement:
`--flavour` was the one table member that macro carried (the comment
above it in wave 4's code said so — "the one membership that includes
it"), so with `FLAVOUR` no longer a table row the macro drops it and the
call site gains an explicit `|| flavour` clause instead. The refusal at
that site is UNCHANGED — still `--source`'s own "does not compose with a
query surface" sentence, not the applies-to sentence — matching today's
behaviour exactly (verified live before and after: `--source
/nonexistent.rxt --flavour pcre2 -o /tmp/out.c` refuses with the same
message either way).

**The "remaining 13 modes take one union mask" half of the item's framing
was measured and NOT built.** w4_report.md's own §"THE UNION MEMBERSHIP,
PROPOSED NOT BUILT" already names the mechanism (`--probe-ask` and
`--emit-ir` deliberately do not refuse each other — block order doing the
work, wave 4's own comment at `CLI_MODES_VS_PATTERN_QUERY`); this lane
re-derived it independently while tracing whether the four narrowed masks
could collapse to one after `--flavour` left the table. `CLI_MODES_VS_LIST_SOURCE`
and `CLI_MODES_VS_SOURCE` are already exactly "every other mode" (12 of
13) and needed no change. `CLI_MODES_VS_COUNT_GROUPS` and
`CLI_MODES_VS_PATTERN_QUERY` are narrower (8 and 9 of 13) — widening
`CLI_MODES_VS_COUNT_GROUPS` to the full union is a no-op (every mode it
would newly catch is already caught earlier in dispatch order before
`--count-groups`'s own block runs), but widening `CLI_MODES_VS_PATTERN_QUERY`
is NOT: `--probe-ask` is checked before `--emit-ir`, and today
`--probe-ask claim --emit-ir -- '\d'` is ACCEPTED (verified live: prints
the probe answer, exits 0, `--emit-ir` silently ignored) precisely
because `CLI_MODES_VS_PATTERN_QUERY` does not test `EMIT_IR`. A literal
thirteen-mode union at that site would refuse the pair instead — an
acceptance flip the modesweep instrument would have caught. Left
unbuilt; the four masks stand exactly as wave 4 shaped them, minus
`FLAVOUR`.

**Validation — modesweep, before vs after:**

```
python3 docs/dev/lanes/w4_modesweep.py /tmp/pcrec_ref_w5r build/pcrec tests/named_groups/named_groups.rxt
invocations: 1407  identical(rc+stdout+stderr): 1407  DIFFERING: 0
accepted (rc=0) ref: 15   new: 15
refused  (rc!=0) ref: 1392   new: 1392
```

`/tmp/pcrec_ref_w5r` is a binary built from this branch's own point
(`fcf35d89`) before any lane edit. **1,407/1,407 identical, 0 differing
— exactly the "0 differing verdicts" gate.**

`tests/cli/run_cli_tests.sh`: **284 passed / 0 failed**, no re-pin.

`make strict CC=gcc-16`: clean.

No emitted byte can move (CLI dispatch only, `cli/main.c` alone touched)
— said so before running the sweep, and the sweep confirms it:
`python3 scripts/emit_sweep.py --ref fcf35d89` (against this item's own
built binary): five streams, all `movers=0 asymmetric=0`
(`c-default` 3518/3939 reach, `c-vm` 3519/3939, `emit-ir-vm` 3519/3939,
`composition` 33/98 producing/artifacts, `dumps` 7/7), self-check PASSED
at full reach, 295.6s.

`docs/spec/cli.md`'s `--flavour` description is unchanged: the applies-to
set itself did not move (still `--list-syntax`/`--list-definitions`/
`--explain`), so no D80 hunk is owed.

Commit: `b8c53c16`.

---

## Item 2 — check01_isolation.sh's positive control, dead on darwin

**Confirmed the exact reported symptom first**, unmodified: "the SPEC-M
named exception (mod_modifiers.o / pcrec_feature_enabled) fired 0
time(s), expected exactly 1" — reproduced live at this lane's own branch
point (`fcf35d89`, before any edit) as well as on `HEAD`, so it is
pre-existing rather than something this branch introduced.

**Cause, traced to the exact line.** darwin's `nm` prefixes every symbol
with `_` (GNU `nm` on Linux does not). `ENABLED_SYMS` and `UNDEF` are both
read through `nm | awk '{print $NF}'`, so on darwin they both carry the
prefix consistently with each other — the general `grep -qx "$s"` match
between them still works — but `EXC_SYMBOL="pcrec_feature_enabled"` is a
bare literal with no prefix, so the ONE comparison that checks a symbol
from `ENABLED_SYMS` against that literal (`[ "$s" = "$EXC_SYMBOL" ]`)
never matches on this box, and the ALLOWED arm can never fire.

**Fixed at the read site (the L8-F6 shape), not at the one broken
comparison**: `STRIP_NM_PREFIX='s/^_//'` is applied immediately after
each of the file's three `nm | awk '{print $NF}'` extractions
(`ENABLED_SYMS`, the recogniser-TU discovery loop, `UNDEF`), so every
later comparison in the file — including the SPEC-M exception's bare
literal compare — operates on the platform-independent spelling. A
no-op on Linux, where `nm` does not prefix symbols by default (reasoned
from GNU `nm`'s documented behaviour; this lane has no Linux box to
verify live on, and the brief did not ask for one — the strip is
conditional on the byte actually being there, not on the platform).

**Result**, live on this box:

```
PASS check01_isolation (36 symbol/TU pairs, 9 enabled-set symbols,
     4 recogniser TUs, 1 named exception)
```

Population UNCHANGED from the file's own documented figures (36 pairs, 9
symbols, 4 TUs) — the fix moves no discovery, only the comparison.

**Sabotage driven solo, by hand** (no `tests/mech/sabotages/` row exists
for this D27 `spec_mod0` check — it is validated by its own header's
hand-verified record, not by `make mech`). A genuinely unfoldable
reference to `pcrec_default_features` was planted in
`pcrec_verb_name_extent_scan` (`src/parse/scans.c`, a recogniser TU):

```c
if (pcrec_default_features && *pcrec_default_features == (char)0xAB) return patlen;
```

(A first attempt, `(void)pcrec_default_features;`, and a second,
assigning to a `static volatile` sink, were both silently optimized away
at `-O2` — GCC's escape analysis proved the comparisons could never be
true without ever loading the symbol, so the "sabotage" produced no
undefined reference at all and the check correctly read PASS on a build
that had not actually been sabotaged. The dereference above forces a
genuine runtime load of a value this translation unit cannot see at
compile time, confirmed present with `nm --undefined-only
build/obj/parse/scans.o` before trusting the check's verdict — the same
discipline the check's own file header already asks of the mech
sabotages it does have.)

With the plant in place and the tree rebuilt: the check FAILS, naming
the object and the symbol —

```
DISAGREE .../build/obj/parse/scans.o references the enabled-set symbol
         'pcrec_default_features' — a recogniser must not link it
POPULATION isolation.named_exceptions         1
FAIL check01_isolation: 1 reference(s)
```

— with the SPEC-M exception still firing exactly once (not a false
positive silencing the new defect). Reverted; `diff` against a saved
copy of the pre-sabotage file confirms an exact revert, and
`git diff --stat src/parse/scans.c` reads clean before this item's own
commit.

Commit: `3b722644`.

---

## Item 3 — S107's SAB_DOC_FIGURE, re-recorded

Re-recorded by the manager after the lane went silent past its own solo
drive (the run had finished; the lane never resumed — the seventy-first
session's chain-not-lane lesson, third instance). The solo drive at
3b722644 (`bash tests/mech/run_sabotage_matrix.sh S107`, one selector):
DETECTED — `corpus:9fail/79pass, brefdiff:4fail/11pass`, `1 rows
(unexpected: 0, undetected: 0, unreached: 0, anomalies: 0)`. The figure
now carries today's date and tree hash, keeps the 2026-08-22 origin and
its old numbers in parentheses, and names the +1 on both sides (§9b, the
utf8 fold-agreement arm [M5.0] stage 4, 2026-09-08 — evtriage2_report.md
§8). Clean-tree line: `brefdiff 12/0`. No check edited; a dated
measurement record, replaced by a dated measurement record.

---

## Validation summary

| what | result |
|---|---|
| item 1 build + strict | clean |
| item 1 modesweep before/after | 1,407/1,407 identical, 0 differing |
| item 1 cli suite | 284/0 |
| item 1 emit_sweep --ref fcf35d89 | 5 streams, 0 movers/0 asymmetric, self-check PASSED, 295.6s |
| item 2 check itself | PASS, 36/9/4/1 (population unchanged) |
| item 2 sabotage, solo, hand-verified | DETECTED (FAIL naming object+symbol), then reverted clean |
| item 3 S107 solo | DETECTED at 3b722644: corpus 9fail/79pass, brefdiff 4fail/11pass, 0 unexpected/undetected/anomalies |
| `make test-codegen` | run by the manager at close (log: scratchpad w5r_testcodegen.log); sole allowed FAIL the standing darwin nm probe |

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# lim1 report — [LIM-1] THE LIMITS TABLE (D90)

Lane `lim1`, worktree `worktrees/lim1`, branch `lane/lim1`, from `main` at
`fa01910`. Delivers D90's charter in full: `src/core/limits.def` (the single
numeric-limits table), `pcrec --list-limits` (the sixth registry-family TSV
surface), `tests/registry/limits_check.sh` (its independent-side check, wired
into `run_registry_tests.sh` and into the mech matrix as its own `limits`
arm), sabotage rows S208/S209, the folded-in `RX_ENGINE_SEL` value
(`"size-cap-retry"`), and the D80 spec hunks.

## 1. The table: population, survey delta vs the 16-floor

The brief's own enumeration named 16 numbers and explicitly said "treat 16 as
a floor, not the count" — SURVEY IT YOURSELF. A full grep sweep of `src/`,
`cli/`, `lib/` for policy-shaped `#define`/enum members (excluding the
file the table itself lives in) found **44**, in 4 "homes":

| home | count | where the definition physically lives |
|---|---|---|
| `LIMITS_H` | 28 | `src/core/limits.h`, generated in place from the table (physical single source — every `#define`/enum in that file now expands `#include "core/limits.def"`) |
| `EMIT_VM` | 6 | `src/gen/emit_vm.c` (runtime give-up budgets — deliberately NOT relocated into limits.h; that file's own inclusion rule is "changes what pcrec ACCEPTS/REJECTS/PROMISES at compile time", and a give-up budget does not) |
| `INTERNAL_H` | 3 | `src/core/internal.h` (`PCREC_PREFIX_K_MAX`, `PCREC_OFSK_MAX_SET`, `PCREC_MINW_MAX`) |
| `MOD_RECURSION`/`MOD_BACKREFS`/`MOD_LOOKAROUND` | 3 | one per module file (`RC_NUMBER_MAX`, `BR_NUMBER_MAX`, `LA_MSG_MAX`) — kept at the module per the brief's own "the modules" grouping |
| `RXT_SOURCE` | 4 | `src/parse/rxt_source.c` — the four caps `docs/spec/limits.md` §3.5 already documented in PROSE but which were bare buffer-size literals (`char name[128]`, an inline `64`) with no named symbol anywhere; this lane is what NAMES them (`RXT_CONFIG_NAME_MAX`, `RXT_TARGET_PREFIX_MAX`, `RXT_TARGET_DEF_MAX`, `RXT_FROM_NEST_MAX`) |

**Every home's definitions now derive from ONE `#include "core/limits.def"`
at their own site** — a per-HOME X-macro dispatch (`PCREC_LIMIT_<HOME>`,
documented in the `.def` file's own header), never a duplicated numeric
literal. Value cross-references resolve to the live compiled symbol
(`PCREC_MAX_EMIT_NAME_LEN`'s row is `PCREC_MAX_PREFIX_LEN + 96` and the dump
reads 156, not a re-typed 156).

**One duplicate found by the survey, fixed**: `src/gen/emit_vm.c`'s
`VM_MAX_BODY_CAPS` was an independently-spelled `64`, and its OWN neighbouring
constant (`PCREC_MAX_REVDET_BODY_GROUPS`, limits.h) already carried the
comment "Same number and same reason as the cursor rung's own
`VM_MAX_BODY_CAPS`" — two homes for one fact, coincidentally still equal.
Fixed to a bare alias: `#define VM_MAX_BODY_CAPS PCREC_MAX_REVDET_BODY_GROUPS`.
This is S209's own witness (below).

**Deliberately excluded, by the file's own stated rule** (a local algorithmic
bound with its correctness proof beside it, or a structural constant):
`TRIE_MAX_RDEPTH`/`MAX_GROUPS` (src/ir/nfa.c), `LEGEND_MAX_STATES`/
`LEGEND_MAX_EXAMPLE` (a debug-listing truncation width, emit_dfa.c),
`VM_MAX_STRIDE`/`VM_FAST_TIER_BYTES`/`VM_FAST_TIER_MIN` (emit_vm.c rung-
selection knobs with their own proofs), `VM_MRL_DYN_MAX` (emit_vm.c, an
unreachable-today soundness retreat — found by the survey's own bug-fix
pass, see §3), `SELECT_MAX_ROUNDS`/`COMPILE_MAX_ATTEMPTS` (bounded-loop
iteration caps), `PCREC_STEP_BUDGET_DEFAULT`/`PCREC_WORK_BUDGET_DEFAULT`
(lib/pcrec.h — API SENTINELS, both `0`, meaning "use the compiled-in
default"; the real defaults, `VM_DEFAULT_STEP_BUDGET`/`_WORK_BUDGET`, are
IN the table). All ten are named, cited, and in `tests/registry/
limits_check.sh`'s own allowlist, not silently skipped.

## 2. `pcrec --list-limits` (src/parse/limits_dump.c)

The sixth conforming `table_contract.md` producer. `#include`s
`src/core/limits.def` DIRECTLY (bypassing every home's own dispatch layer),
so every row's `name`/`value` come off the compiled binary, never a second
computation. MEASURED live:

    $ build/pcrec --list-limits | grep -vc '^#'
    44

Header + 7 columns (`name value unit kind override anchor desc`), `override`
mapped from the table's bare dispatch token (`NONE`/`FLAG`/`BUILD_D`) to its
display spelling (`none`/`flag`/`-D`). No `--flavour` (same reason
`--list-axes` has none: not a claim about PCRE2 syntax).

## 3. `tests/registry/limits_check.sh` — three checks, real findings on first run

1. **Row count by NAME MANIFEST** (44, not a bare number — learnings.md §3's
   "exact counts disarm themselves; the fix is a manifest").
2. **dump → `docs/spec/limits.md` §3/§8, forward.** Every ANCHORED row's
   value (comma-grouped the way the doc writes large numbers) must be found
   within its OWN cited section (extracted heading-to-heading, never the
   whole doc). Reverse (every doc number traces to a row) is deliberately
   NOT swept blind — that document's prose is full of measured WITNESS
   numbers unrelated to the table (byte counts of named artifacts,
   timings, corpus sizes), and a blind reverse scan is exactly the K35
   "population nobody counts" shape. The anchor→row assignment was built by
   a full read of `limits.md`; this check is what stops a FUTURE edit from
   silently breaking the forward half.
3. **dump vs CODE**: a bare policy-shaped `#define`/enum-member anywhere
   under `src/`/`cli`/`lib` OUTSIDE `limits.def`, against the named,
   cited allowlist (§1 above).

**Found and fixed two real doc drifts on its first live run**:
`docs/spec/limits.md` §3.3 named `PCREC_MAX_NFA_STATES`/`PCREC_MAX_VM_NODES`
by number but only said "and their siblings for DFA states, table entries
and subset construction" for the other four — now states all six by number.
`PCREC_DEFAULT_WARN_EMIT_BYTES` was spelled `250000` in §8, ungrouped,
against its comma-grouped siblings (`500,000`/`1,000,000`) in the same
section — now `250,000`.

**Found a real regex-tooling bug in the check itself, on the SECOND run**
(against S209's own plant, see §5): the line-anchored `^[[:space:]]*NAME =`
regex in part 3 never matches `enum { NAME = N };`'s actual shape (`enum {`
sits before the name), which is the SAME blind spot this lane's own manual
survey hit first. Fixed to a `{`/`;`/whitespace boundary match; re-verified
against a clean tree (still 21/0) and re-surfaced ONE more legitimate finding
on the wider sweep, `VM_MRL_DYN_MAX` (added to the allowlist, §1).

**MEASURED**: 21/21 passing, clean, on the merge-ready tree.

**Wiring**: part of `make test` via `run_registry_tests.sh` (own coverage
guard, 21 exact, mirrors `axes_registry_check.sh`'s shape); its own `limits`
arm in `tests/mech/run_sabotage_matrix.sh` — deliberately NOT folded into
`registry`, whose own comment states it skips any coverage-guard-shaped
wrapper for exactly the reason part 1 of this script is one.

## 4. `pcrec-bench` / axes_registry_check.sh: no manual update needed

`axes_registry_check.sh` already carried two GENERIC `RX_ENGINE_SEL`
value-set legs (dump-vs-`match_api.md`, dump-vs-`pcrec_engine_sel_name`'s own
`return` statements) landed by `[OPT-4.1]` the same day this lane started.
Both extract their value sets LIVE from their sources, so adding the seventh
row to `match_api.md`'s table and the seventh `case` to
`pcrec_engine_sel_name` was sufficient — MEASURED, both legs pass
automatically listing all seven values, and the file's own coverage guard
(83, unchanged) still holds:

    PASS: [RX_ENGINE_SEL] every dumped stamp_value (forced collapsed-prefilter
      declined-nullable overflowed-dfa overflowed-prefilter size-cap-retry
      selected) is in docs/spec/match_api.md §6.3's own value-set table
    checks passed: 83
    checks failed: 0

## 5. The folded item (I-19 (3)): `RX_ENGINE_SEL "size-cap-retry"`

**Before this lane**: the `[OPT-4]` SIZE rung's own SUCCESS (the emitted-size
cap refused the exact artifact, the retry's count-collapsed prefilter shipped
and survived) stamped `RX_ENGINE_SEL "selected"` — indistinguishable from a
compile that never touched any cap, because `dfa_disabled` (the flag that
routes to the DFA-overflow `ESEL_*` arms) is never set on this rung: the DFA
build itself SUCCEEDED, it was the WHOLE ARTIFACT an emitted-size cap
refused. `docs/spec/limits.md` §3.3's own `[OPT-4]` section had recorded this
gap in prose without a fix ("the SIZE rung's own decline is not this value...
the route stays `selected`") — true of the DECLINE only, silently also read
as true of the rung's SUCCESS.

**After**: a new value, `ESEL_SIZE_CAP_RETRY = 6` (`src/core/internal.h`),
placed OUTSIDE the existing `>= ESEL_OVERFLOWED_DFA` contiguous range on
purpose (its own cap is the emitted-SIZE one, not a DFA STATE cap, so folding
it into that range would make the range's own stated invariant lie about
what overflowed — the enum's own comment now states the corrected, bounded
form of that invariant). `ESEL_DECLINED_NULLABLE`'s own conjunct widened
from `CR_SEL1`-only to `collapse_reason != CR_NONE`, so a SIZE-rung nullable
decline now ALSO reads `"declined-nullable"` rather than falling through to
`"selected"` — the same gap, one branch over, closed in the same change.

Enum ordinals are pcrec's own C-internal detail (never emitted to any
artifact — only the STRING is stamped), so this is genuinely a value, not
scaffolding: **no abi bump** (D76).

**MEASURED, before/after, on the witness the brief names**:

    $ build/pcrec -p rx -o - -- '(a|b){1,30000}' | grep 'ENGINE_SEL\|VM_PREFILTER \|LANG_WHY'
    #define RX_ENGINE_SEL "size-cap-retry"      # was "selected"
    #define RX_VM_PREFILTER "hybrid"
    #define RX_VM_PREFILTER_LANG_WHY "size cap retry, exact 1335105 > 1000000"

    $ build/pcrec -p rx -o - -- '(a|b){0,30000}' | grep 'ENGINE_SEL\|VM_PREFILTER '
    #define RX_ENGINE_SEL "declined-nullable"   # was "selected"
    #define RX_VM_PREFILTER "none"

    $ build/pcrec -p rx -o - -- 'a(b|c)+d' | grep ENGINE_SEL
    #define RX_ENGINE_SEL "selected"             # unchanged (ordinary compile)

**Touched sites, matching how `[OPT-4.1]`'s own `"declined-nullable"`
landed**: `src/core/internal.h` (enum + both invariant comments),
`src/opt/select_engine.c` (the `fit.engine_sel` ternary ladder — two new
arms, CR_SEL1's existing arm UNCHANGED), `src/gen/emit_dfa.c`
(`pcrec_engine_sel_name`'s switch), `src/parse/axes_dump.c` (the
`engine-route` axis's 7th row, order renumbered 6→7 for `selected`),
`docs/spec/match_api.md` §6.3's value table + a new explanatory paragraph,
`docs/spec/tuning.md`'s `[OPT-4.1]` bullet (the false "stays selected"
sentence corrected).

**The witness cell**: `tests/resource/run_resource_tests.sh`'s
`size_rung_cell '(a|b){1,30000}' hybrid ...` — its verdict now reads
`RX_ENGINE_SEL` directly (`= size-cap-retry`) instead of parsing the
`_LANG_WHY` prefix; the nullable twin (`(a|b){0,30000}`) gained the matching
`declined-nullable` check. `tests/codegen/run_prefilter_collapse.sh` §7's
value-set case arm, §7's cross-check arm (`collapsed-prefilter` →
`collapsed-prefilter|size-cap-retry`), and §7b (six routes → seven, reusing
the SAME `(a|b){1,30000}` pattern as the resource cell's own witness rather
than inventing a second one — K35's "one witness, two readers" precedent)
all updated. `docs/spec/registry.md`'s `--list-axes` row count re-derived
live (61 → 63; one row is this fold-in, the other a pre-existing, unrelated
drift from the branch point — both stated, neither guessed).

## 6. Spec hunks (D80, landed in the same commits as their code)

- `docs/spec/limits.md` — §3.3 states all six state-count numbers by name;
  §8's advisory-warning default comma-grouped for consistency.
- `docs/spec/match_api.md` — §6.3's `_ENGINE_SEL` value table gains the
  seventh row + explanatory paragraph; the "LAST FOUR" framing corrected to
  "LAST FIVE".
- `docs/spec/tuning.md` — the `[OPT-4.1]` bullet's false "stays selected"
  claim corrected to the real, closed value.
- `docs/spec/registry.md` — `--list-axes` row count re-derived live
  (61 → 63) with the delta named; `--list-limits` mentioned nowhere else in
  that file (it is `table_contract.md`'s Scope table's job).
- `docs/spec/table_contract.md` — Scope table gains the `--list-limits` row
  (adopting the contract AT BIRTH, per the file's own charter).
- `docs/spec/cli.md` — "Six TSV dumps" → "Seven"; new `### --list-limits`
  subsection, positioned as the sixth surface (after `--list-definitions`,
  before `--list-source`, matching the numeric ordering `limits_dump.c`'s
  own header already states).

## 7. Directory CLAUDE.md updates

`tests/registry/CLAUDE.md` (limits_check.sh's own Files entry, findings
summary), `tests/resource/CLAUDE.md` (the `[LIM-1]` addendum on the
size-rung pair's verdict moving to `RX_ENGINE_SEL`), `tests/mech/
run_sabotage_matrix.sh`'s own header (the `limits` vocabulary word,
registered before S208/S209 per this directory's own R31 C11 convention).
`src/core/limits.def`'s own header comment carries the design (the home
dispatch mechanism, the row schema) in place of a separate design doc — this
table IS its own documentation, matching `axes_dump.c`'s own precedent.

## 8. Sabotage rows — claimed range S208-S209

Both use the new `limits` arm (never `registry`, whose own comment states it
deliberately skips any coverage-guard-shaped wrapper). `SAB_REACH` fields
omitted, following `S142`'s own precedent (a table/tree-consistency check has
no "reachability" question distinct from the check running at all — no
external oracle or construct needs to still exist).

| row | plant | detector | MEASURED (live matrix run) |
|---|---|---|---|
| S208 | `limits.def`'s `PCREC_MAX_VM_EMIT_CODE_BYTES` row edited 500000→400000, `limits.md` left stale | part 2 (dump-vs-doc, forward) | `limits:1fail/20pass` — DETECTED |
| S209 | `VM_MAX_BODY_CAPS` (emit_vm.c) put back as a bare `enum { ... = 64 };`, delinked from the table — the EXACT regression §1 found and fixed, value unchanged so no answer/byte moves | part 3 (dump-vs-code) | `limits:1fail/20pass`, `vmid:0fail/10pass`, `corpus:0fail/…pass` — DETECTED |

Both re-verified via `VALIDATE_ONLY=1` (fields OK) then a live
`bash tests/mech/run_sabotage_matrix.sh S208`/`S209`, each its own
invocation, at commit `74e4ab3` (post the part-3 regex fix — S209's FIRST
live run, against the pre-fix check, correctly came back
`**UNDETECTED — ZERO CHECKS FAILED**`, which is what found the check's own
regex bug rather than a code bug; re-run clean after the fix). The highest
existing id at branch time was S207 (matches the brief's own stated S194–
S207-taken range); no collision found in this worktree.

`S44_vm_repeat_cap_off.sh` — NOT this lane's own row, but its anchor went
stale from limits.h's restructuring (§1) and `tests/codegen/
run_codegen_tests.sh`'s `[SABANCHOR]` check caught it live. Re-anchored to
`limits.def`'s own row (value and intent unchanged), per `tests/mech/
sabotages/CLAUDE.md`'s own Conventions ("re-derive from whichever source is
the text your change LEAVES BEHIND"). `python3 scripts/
m6read_check_sab_anchors.py`: "all anchors resolve" (205 sabotages, 216
anchor sites) after the fix.

## 9. VERIFY — every command, MEASURED

| command | result |
|---|---|
| `make -j4` | clean, no warnings |
| `make strict` | "whole tree compiles clean with -Werror -Wshadow" |
| `PROCS=4 bash tests/registry/run_registry_tests.sh` | registry_check + definitions 54/0, limits_check 21/21, axes_registry_check 83/0, PC-3 clean, pc4 62,872 cells / 0 disagreements |
| `PROCS=4 make test-codegen` | see below (in flight at report time; result appended before send) |
| `make test-cli` | see below (in flight at report time; result appended before send) |
| `PROCS=4 make test-corpus` | **26,680/0**, pattern-compile failures 0, **178/178** file workers — exact match to the brief's own expected figures |
| `bash tests/resource/run_resource_tests.sh` | all PASS, including both `[OPT-4]`/`[OPT-4.1]` size-rung cells reading the new `RX_ENGINE_SEL` values |
| `bash tests/codegen/run_prefilter_collapse.sh` | **60 passed, 0 failed** — all 7 `RX_ENGINE_SEL` routes reachable, including `size-cap-retry` |
| `build/pcrec --list-limits \| head` | 44 rows, header conforms to `table_contract.md` |
| One-cell mid-lane fix: `git checkout docs/dev/artifact_size_log.tsv` after `test-corpus` | done |

## 10. Left out, with reasons

- **`--flavour`/reverse-doc sweep for `limits_check.sh`**: deliberately not
  a blind reverse scan of `limits.md`'s free prose — see §3's own reasoning
  (K35 population-nobody-counts shape). The FORWARD direction is the one
  D90's charter actually asks for ("the registry check pins docs/spec/
  limits.md §3 against the dump").
- **Physically relocating `EMIT_VM`/module-homed constants into
  `limits.h`**: considered and rejected — `VM_DEFAULT_WORK_BUDGET`'s own
  existing comment already argues against it (limits.h's inclusion rule is
  compile-time ACCEPT/REJECT/PROMISE; a runtime give-up budget is none of
  the three), and the brief's own listing groups these as "(emit_vm.c)"/
  "(the modules)" — i.e., cataloged at their existing home, not moved.
- **`make ubsan`/`make asan`/`make lint`**: not run this pass (opt-in,
  outside the brief's own VERIFY list; the merge battery covers them).

## 11. Claims, marked

MEASURED (command + number, this report): the 44-row population and its
home split (§1); `--list-limits`'s 44-row live count (§2); `limits_check.sh`
21/21 (§3); `axes_registry_check.sh` 83/0 including both `RX_ENGINE_SEL`
legs (§4); the before/after `RX_ENGINE_SEL` stamps on the three witness
patterns (§5); `run_registry_tests.sh`'s full green run (§9); S208/S209
DETECTED via the live matrix (§8); S44's re-anchor + the anchor-checker's
clean run (§8); `test-corpus` 26,680/0, 178/178 (§9); `run_resource_tests.sh`
and `run_prefilter_collapse.sh` both fully green (§9).

INFERRED: that the 44-number population is now complete (a further grep
pattern could in principle surface one more structural constant this
survey's regex shape missed — the check's own allowlist mechanism is built
to accommodate exactly that without requiring a re-audit of the whole
population).

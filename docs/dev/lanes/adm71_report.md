# adm71 — five small standing admin items

Lane adm71 (2026-09-19, sonnet), branch `lane/adm71` from main `923a5a58`.
Five unowned admin items, one commit per item, cheapest first. PARKED on
the branch per the brief — nothing merges here; a Linux battery pinned at
main is the manager's separate concern.

## Item 1 — `tests/mech/sabotages/CLAUDE.md` stale row count

`d5ea41a7`. The "Checking a definition without running it" section's
`VALIDATE_ONLY=1` example comment said `# all 180`; the directory holds
268 `S*.sh` rows today (`ls tests/mech/sabotages | grep -c '^S'`). Fixed.
Swept the rest of the file for other numeric claims (grepped every
integer-bearing line): the only other candidate, "until a full 180-row
matrix" a few lines above, is historical narrative describing a specific
past incident (the [M6.5.2] wave-E S70 UNDETECTED finding, at the
matrix's size AT THAT TIME) rather than a live count, so left as-is.
Doc-only, no validation beyond a read.

## Item 2 — S224 solo drive, re-record as MEASURED

`37e42b8c`. Drove `S224_vm_frameless_stamp_inverted.sh` solo
(`tests/mech/run_sabotage_matrix.sh S224`) at tree `d5ea41a79`:
**DETECTED, reach:ok(1/1), vmframeless:7fail/4pass** — identical to the
row's existing 2026-09-03 figure. The brief's premise ("an eleven-check
run_vm_frameless.sh") needed reconciling against the brief's own
observation that the suite has 6 checks today: traced the script's
control flow rather than re-running with a different lens. On a CLEAN
run the file has six top-level outcome points (the §1 six-witness
summary, the §1 negative control, §2's pure-DFA IFF half, the §3
corpus-sweep aggregate, and the two per-axis §3 population floors). The
stamp inversion is a bijection on {0,1}, so it wrongly flips all six
named witnesses INDIVIDUALLY — each prints its own `FAIL:` line from
inside `witness()`, bypassing what would have been ONE aggregate `ok()`
at line 148 — plus the §3 aggregate, for 7 `bad()` calls where a clean
run would print 2 `ok()`s in their place. The remaining 4 passes
(negative control, §2, two axis floors) are unaffected by construction.
Re-recorded the figure with today's date/tree hash and this
reconciliation; the row still detects and the split is genuinely
unchanged. No weakening.

## Item 3 — S88 solo drive, MEASURE the canonical figure

`8c97089c`. Drove `S88_atomic_ceiling_stamp_only.sh` solo at tree
`37e42b8c9`: **DETECTED, codegen:3fail/106pass, corpus:0fail/53pass,
atomicdiff:0fail/8pass** — matching `dd8_report.md`'s own independent
first drive of this row exactly (different pin, same split), so the
figure moves from PREDICTED to MEASURED at both pins. The prediction's
`atomicdiff` half does NOT hold: detection is carried entirely by
`codegen`'s rule 1(a) structural check, never by an answer divergence on
either engine axis. Verified independently of the mech harness: patched
`src/gen/emit_vm.c` by hand with only S88's edit (backed up, restored
after), rebuilt, and compiled the row's own named witness through
`--emit-main` — `(?>a|ab)c|abcd` on `"abcd"` gives the CORRECT `(0,4)`,
and `x*(?>a|ab)c|abcd` on `"xxxabcd"` gives the correct `(3,7)`, both
under the sabotage alone. The `SAB_DESC`'s "the uncut twin ends at 3" is
the theoretical hazard RULE H3 exists to forbid, not an answer this
witness or `atomicdiff`'s 8-cell corpus actually exposes. The row still
detects and still proves the stamp/code two-source design is
load-bearing (rule 1(a) fires, 1(b)/1(c)/1(d) stay green) — only the
CHANNEL moved from the predicted answer-level one to the structural one,
now stated in the figure.

## Item 4 — the `no-nullable-collapsed` prefilter decline: REACHABLE

`e021b982`. `docs/dev/lanes/dd8_report.md` §4.3 filed `src/gen/
emit_vm.c`'s `--emit-ir` prefilter value `no-nullable-collapsed`
(~line 8683, `docs/spec/ir_listing.md:113`) as UNREACHED BY ANY INPUT,
after its own corpus/flag-axis sweep and three hand-built witnesses all
missed it, with a structural argument that [OPT-4.2]'s rungless twin
(`prefilter_declined_nullable_default`) always declines first, on the
ORDINARY hybrid attempt, before any rung can be offered.

**(i) Code read: the argument is REFUTED.** It assumes the FIRST compile
attempt is already a VM+prefilter hybrid. That's only true when
`select_engine.c`'s fit picks `ENGM_VM` on attempt 1. A captures-free
pattern routes to a pure DFA-as-ENGINE attempt instead — `would_prefilter`
is false there (`fit.chosen != ENGM_VM`), so `prefilter_declined_
nullable_default`'s own conjunct fails and it cannot fire at all on that
attempt. The DFA build then genuinely runs (`src/core/compile.c`, after
`pcrec_select_engine`), and when it overflows
`PCREC_MAX_DFA_STATES_TABLE` (32000) under `--engine=auto` with no
`-fprefilter`, `compile_driver`'s `setjmp` handler offers the [SEL-1]
collapse rung (`collapse_reason = CR_SEL1`, `dfa_disabled = true`) — the
retry attempt where the RUNG-scoped decline (`prefilter_declined_
nullable`) actually lives. A nullable, collapsible-repeat pattern
reaching that rung hits it directly.

Confirmed live on this tree: `(?:ab){0,16000}` compiles to
`RX_ENGINE_SEL "declined-nullable"` / `--emit-ir` `prefilter
no-nullable-collapsed`. 16000 is the smallest round N found past the
32000-state boundary (linear sweep from 15000, which still compiles as an
ordinary in-cap DFA at 601KB).

**(ii) Sweep, as instructed.** `--emit-ir` on both the default axis and
`--engine=vm` forced, every `pattern`/`pattern-esc` line in the shipped
corpus (3,275 patterns, `tests/base` through every module directory):
**ZERO hits on either axis.** Matches dd8's own corpus-population
finding — the value is real and reachable, just not by anything the
corpus already carried. Also confirms a second structural fact: the
value is UNREACHABLE under forced `--engine=vm` specifically, since the
[SEL-1] retry ladder requires `defo.engine == PCREC_ENGINE_AUTO`
(`compile.c`'s `ovf_eligible` conjunct) — dd8's own pass-1 (forced VM)
could reach only three prefilter tokens "by construction" for exactly
this reason, though its report did not attribute the "no-nullable-
collapsed" absence to that specific mechanism.

**REACHABLE, so per the brief: witness added, arm kept, nothing
deleted.** `tests/base/opt41_rung_nullable_decline.rxt` — one pattern
block, six cases, oracle-verified against python3 `re`, cross-checked
against pcrec's own `--emit-main` driver before landing — plus its
`tests/base/CLAUDE.md` entry. Re-pinned `tests/rxtsource/
run_rxtsource_tests.sh`'s census in the same commit (`CENSUS_FILES`/
`CENSUS_BLOCKS`/`CENSUS_LINES`, `RUNSH_FILES`/`RUNSH_BLOCKS`/
`RUNSH_LINES`, `C3_PASS`: +1 file / +1 block / +6 lines, all six cases
PASS with no skip bucket moving) — verified clean (212/0/1-recorded, the
recorded line is the pre-existing darwin C3 non-native-pin skew this
box's own C3 pins already carry, per `run_rxtsource_tests.sh`'s own
2026-09-08 note on that behavior).

## Item 5 — the `-o` basename trap: SURVEY + helper, sites converted

`(this commit)`. Grepped `tests/` and `scripts/` for every site that
emits an artifact to two different `-o` targets and then `cmp`/`diff`s
between them — the shape `scripts/emit_sweep.py:396-398` avoids with
`-o -`, and the fifth recorded instance of the trap per the brief
(dd8_report.md §3.1 is the fourth).

**Method.** First pass: every `diff`/`cmp` site in the tree whose line
contains a literal `.c` substring (`grep -rnE '\b(diff|cmp)\b[^|]*\.c\b'
tests/ scripts/`). For each, read the emitting call(s) feeding the two
compared paths and classify by basename:

| site | basenames | exposed? | why |
|---|---|---|---|
| `run_anchored_match.sh` §1 negative control | `on.c` / `off.c` | **YES — CONVERTED** | raw `cmp -s`, no filtering |
| `run_search_pinned.sh` §1 negative control | `on.c` / `off.c` | **YES — CONVERTED** | raw `cmp -s`, no filtering |
| `run_trie_identity.sh` `gen_a`/`gen_b` | n/a | no | both use `-o -` |
| `run_vm_identity.sh` def/nc compare | `gen.c` (both sides) | no | same basename; the `norm.c` intermediate is an awk-derived copy of the `nc/gen.c` side, not a second emission |
| `run_tune_dial.sh` §2 | `artifact.c` (one shared `$OUT` path, `cp`'d out) | no | every `emit()` call writes the SAME `-o` path; the two sides being compared are `cp` copies of that one path taken at different times, never two independent `-o` names |
| `run_rungselect_tests.sh`, `run_startbnd_diff.sh`, `run_counterk_tests.sh`, `run_mrl_tests.sh`, `run_prefilter_tests.sh`, `run_altcls_tests.sh`, `run_possessify_tests.sh` | same basename in sibling dirs (`gen.c`/`d.c`/`g.c`/`art.c`) | no | basename identical across the compared sides by construction |
| `run_recursion_identity.sh` elision arm | `q.c` (both sides, `a/`, `b/`) | no | same basename in sibling dirs |
| `run_cli_tests.sh` case9/case10/case13/case14 | `-o -` throughout | no | already documents and avoids this exact trap in its own comments |
| `run_offset_skip.sh` | `p1.c`/`p2.c`, compared via `drop_own_header` | no | pre-existing header-stripping idiom |
| `run_island_tests.sh` | `*_on.c`/`*_off.c`, compared via `grep -v '^#include "'` | no | pre-existing header-stripping idiom |
| `run_encoding_checks.sh` | `b.c`/`u.c`, `a.c` (byte/utf8 dirs) | no | compared through `stamp_of`/`sigs_of` extractor functions, never raw file bytes |

Two genuinely exposed sites, both in the `run_codegen_tests.sh` family's
byte-identity-gate siblings, both §1 "negative control" checks whose
whole point is asserting the two builds GENUINELY DIFFER (so a build in
which the axis is a no-op cannot pass vacuously). Both used two different
`-o` basenames (`on.c`/`off.c`) and a raw `cmp -s`, so — regardless of
whether `-fno-anchored-dfa`/`-fno-start-pinned` do anything real — the
`#include "on.h"` vs `#include "off.h"` line alone guarantees `cmp -s`
reports a difference. **Currently both checks happen to read the RIGHT
answer** (each flag genuinely moves more than the include line, verified
by direct `diff`), so this was not a live false-negative — but the check
as written is STRUCTURALLY INCAPABLE of ever catching the exact defect
it exists to catch (a flag silently becoming a no-op), because the trap
alone always supplies "a difference" regardless of the flag's real
effect.

**Helper: `tests/lib/c_artifact_cmp.sh`, `cmp_c_artifacts FILE1 FILE2`**
(22 lines including comments, well under the 40-line bound) — strips any
`^#include "` line from both sides before `cmp -s`. Converted both
exposed sites (source the helper, swap `cmp -s` for `cmp_c_artifacts`,
identical control-flow otherwise — a pure mechanical swap in both
cases). Both scripts re-run in full afterward and pass at their
pre-existing counts (`run_anchored_match.sh` **20 passed / 0 failed**,
`run_search_pinned.sh` **17 passed / 0 failed**), confirming the swap
changed no verdict — only what a genuinely-vacuous axis would now
correctly read.

Not converted (out of scope, no defect found): the already-safe sites
above, which either already use `-o -`, already share a basename, or
already filter through an existing header-stripping idiom
(`run_offset_skip.sh`'s `drop_own_header`, `run_island_tests.sh`'s
`grep -v`). A follow-up consolidating those two pre-existing idioms onto
the new shared helper is a plausible future admin item, not undertaken
here (BOILERPLATE's altitude rubric: three independent idioms for one
fact is worth flagging, not necessarily worth touching in the same
change that adds the third).

## Validation

- `make -j4 CC=gcc-16` and `make strict CC=gcc-16`: clean after every
  item.
- Item 1: doc-only, no runtime validation.
- Item 2: `tests/mech/run_sabotage_matrix.sh S224` — DETECTED,
  reach:ok(1/1), vmframeless:7fail/4pass.
- Item 3: `tests/mech/run_sabotage_matrix.sh S88` — DETECTED,
  codegen:3fail/106pass, corpus:0fail/53pass, atomicdiff:0fail/8pass;
  plus a hand-reproduction of the row's own witness (restored before
  commit, `git status` clean).
- Item 4: `bash tests/harness/run.sh tests/base/
  opt41_rung_nullable_decline.rxt` (6/0), `python3 tests/harness/
  verify_rxt.py tests/base/opt41_rung_nullable_decline.rxt` (PASS=6
  FAIL=0), `bash tests/codegen/run_ir_listing.sh` (144/0, unchanged),
  `bash tests/rxtsource/run_rxtsource_tests.sh` (212/0/1-recorded,
  the one RECORD line the pre-existing darwin C3 skew).
- Item 5: `bash tests/codegen/run_anchored_match.sh` (20/0) and
  `bash tests/codegen/run_search_pinned.sh` (17/0), both re-run in full
  after the swap.

Targeted validation only, per the brief — the full `make test`/`make
mech` battery is the manager's at merge; a Linux battery is already
pinned at main and this lane's delivery parks on the branch.

## Rulings needed

None. All five items closed within the brief's own scope; item 4's
finding (REACHABLE, refuting dd8_report.md §4.3) and item 5's finding
(a structurally vacuous negative control, now fixed in both sites) are
both reported here rather than escalated, since the brief's own
disposition for each ("add witness and keep the arm"; "build and convert
if the helper is ≤40 lines and the swap is mechanical") was met without
needing a manager decision.

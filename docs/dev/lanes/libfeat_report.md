# libfeat — [REL-1.11] [LIB-FEATURES]: the library gets a `--features` lever

Branch `lane/libfeat`, worktree `worktrees/libfeat`, from main `f12e123d`
(abi 28). `pcrec_options` gains `const char *features`, applied per
`pcrec_compile()` call; `cli/main.c`'s own `--features` flag now fills it;
`pcrec_options` is the LIBRARY struct, not the artifact, so this is NOT an
`abi` event (confirmed — `abi` stays 28 throughout).

## 1. The design choice: global vs. context (D19), with the evidence

The charter's own mechanism sketch — "the CLI sets the field, not a
parallel path" — undersells the real hazard once you ask what happens
under concurrency. `src/parse/enabled.c`'s enabled-feature-set was
PROCESS-GLOBAL, write-once-then-read-many BY DESIGN (its own header
comment): the CLI calls `pcrec_enabled_set_spec()` exactly once, before
any compile starts, and nothing writes again while compiles run — which
is precisely what lets `tests/thread`'s TS-3 (concurrent `pcrec_compile()`
calls) be safe today. Making `pcrec_compile()` itself call
`pcrec_enabled_set_spec()` on every invocation — the naive reading of "one
mechanism" — reintroduces exactly the hazard D19 exists to forbid: two
concurrent `pcrec_compile()` calls asking for DIFFERENT specs would race on
the same three global variables, and worse, thread A's own parse could
read thread B's just-installed spec mid-parse (a genuine miscompile, not
merely a TSan-flagged benign race).

**Two candidate fixes, and why I took the second.** (a) A mutex around
`pcrec_compile()`'s whole body would restore correctness but SERIALIZE the
compiler's own hot path for every call that engages this new default
path — and since bare NULL now has to go somewhere, that would mean nearly
every `pcrec_compile()` call in the process, gutting the concurrent-compile
throughput D19's own test suite (TS-3) exists to certify. (b) Move the
enabled-set state OFF the global entirely and onto the per-compile `Ctx`
(`Ctx.enabled_features`/`enabled_label`/`enabled_modules`,
`src/core/internal.h`), resolved by a NEW **pure** function,
`pcrec_enabled_resolve_spec` (`src/parse/enabled.c`) — spec in,
mask/label/rendered-module-list out, no global touched at all. Two
concurrent calls with different specs cannot race because neither ever
writes memory the other can see. `pcrec_feature_enabled`/`pcrec_ext_gate`
(internal.h) now take the caller's resolved mask as an explicit parameter
instead of reading a global implicitly.

Taken: (b). It costs a mechanical but real refactor — every
`pcrec_feature_enabled(FEAT_X)` call site in `src/parse/{ext,mod_recursion,
mod_backrefs,mod_modifiers,parse}.c` and `src/parse/mod_verbs.c` now reads
`pcrec_feature_enabled(cx->enabled_features, FEAT_X)` (13 sites; `cx` was
already in scope at every one, confirmed by reading each site before
editing) — but it is the CORRECT fix rather than a faster-but-fragile one,
and it costs ZERO throughput: no lock, no serialization, and the OLD
global mechanism is untouched for its OTHER, real customers.

**The global is not retired — it still has customers who never call
`pcrec_compile()`.** The CLI's own `--probe-ask`/`--count-groups`/
`--list-source`/`--explain` query surfaces install and read it exactly as
before (`cli/main.c` keeps its pre-existing `pcrec_enabled_set_spec()`
call — see §3 below for why removing it, which the brief's literal item 3
asked for, would have been wrong), and `--list-syntax`'s built-status probe
(`src/dump/syntax_dump.c`'s `pcrec_construct_built_status` save/force/
restore dance) still uses it too. Both keep working unchanged: their own
throwaway `Ctx`es now seed `enabled_features` from `pcrec_enabled_mask()`
(one line added at each of the three `Ctx` constructions in that file,
plus `put_agreement`'s bare gate check switched from
`pcrec_feature_enabled(r->feature)` to
`pcrec_feature_enabled(pcrec_enabled_mask(), r->feature)`). One mechanism
(`pcrec_feature_enabled` taking an explicit mask) serves both customers;
what differs is only WHERE each customer's mask comes from.

## 2. A second, larger deviation: `NULL` does NOT mean `std1`

The plan row's own text says `NULL = the default resolution, D37` (i.e.
resolve through `pcrec_default_features`, `"std1"`, exactly like a bare
CLI invocation). **I did not build that, and the reason is measured, not
a hunch.** `docs/dev/decisions.md` D37's own addendum states, as ALREADY
SETTLED FACT: *"A LIBRARY caller that links libpcrec.a and calls
`pcrec_compile()` without `pcrec_enabled_set_spec()` runs at the raw
enabled mask, which is EMPTY at process start and stays empty ...
`tests/registry` RELIES ON THIS (`pcre2_check.c` compiles at the empty set
by construction and is flip-immune)."* That sentence is not a stray
comment — it is load-bearing across dozens of call sites I found and had
to fix regardless of the NULL question (§4 below), and dozens more I did
NOT find, because `pcrec_compile()`/direct-`Ctx` construction with
`pcrec_default_options()` and no explicit feature request is the ordinary,
unremarkable shape of a white-box internal test in this tree.

Making `NULL` resolve to `std1` inside `pcrec_compile()` would silently
enable `classes`+`modifiers` for every one of those callers — flipping
`\d` from refused to accepted, for instance — with no way to find every
affected call site short of auditing the whole `tests/` tree call by call.
That is precisely the "flip" D37's addendum names as the reason the
library's raw default was left alone, and exactly the re-opened question
its last sentence names ("The question ... re-opens WITH that promotion,
not before" — this row is that promotion). I answered it conservatively:

- **`pcrec_options.features == NULL` means "make no request"** — the
  compile proceeds with an EMPTY enabled set, identical to today's raw
  library default. Every existing internal `pcrec_compile()` caller is
  unaffected.
- **The CLI achieves full bare-invocation parity WITHOUT relying on
  `pcrec_compile()`'s NULL handling at all.** `cli/main.c` already computed
  `fspec = features ? features : pcrec_default_features` for its own
  global install; it now ALSO assigns `opt.features = fspec` — the
  resolved, concrete value, never NULL — before compiling. A bare
  `pcrec 'PATTERN'` invocation is therefore byte-for-byte unaffected by
  this whole change (verified live, §5).
- A DIRECT library caller who wants the CLI's own bare-invocation
  behaviour asks for it explicitly: `opt.features = pcrec_default_features;`
  (or the literal `"std1"`). One line, documented at the field itself
  (`lib/pcrec.h`), not a hidden trap.

This is a genuine narrowing of the plan row's stated design, done in the
open with its evidence, per BOILERPLATE's "state the concern, then keep
building" rule. `tests/core/features_opt_check.c`'s case 1 (`features =
NULL`) and case 3 (`features = "std1"`) happen to read identically for the
witness construct chosen (`(?=a)b`, module `lookaround`, never a std1
member) — which is expected and does not exercise the "empty vs. std1"
distinction; that distinction is the reason this section exists in the
report rather than something the acceptance check alone would surface.

## 3. `cli/main.c`: the brief's item 3, and where I deviated from it

Item 3 said "the CLI's own `pcrec_enabled_set_spec` call is REMOVED (the
library applies it)". I kept it, at both of the two sites the charter
names (`apply_target`'s per-target features block, `cli/main.c:1294`-ish;
the main single-invocation path, `~1669`). **Removing it breaks
`--probe-ask`/`--count-groups`/`--list-source`, which install NOTHING of
their own and rely entirely on this same block having installed the
global before their own dispatch runs later in the same function** — this
is not a hypothetical; `cli/main.c`'s own comment at the block says so
("--features installs the enabled set BEFORE anything consults the
gate ... composes with every mode"), and `docs/spec/cli.md`/`mod_verbs.c`'s
own comments cite live `--probe-ask --features X` invocations as the
verification mechanism for OTHER work in this tree. Blindly deleting the
call would have silently regressed those surfaces with no compile-time
signal.

What actually changed: the SAME resolved `fspec` this block already
computes is now ALSO assigned to `opt.features` (`ts.opt.features = fspec;`
/ `opt.features = fspec;`), so the compile itself is driven by the field —
the global install becomes redundant FOR THE COMPILE (harmless, still
correct) and load-bearing ONLY for the query surfaces that never reach
`pcrec_compile()` at all. Error text and timing are byte-identical to
before (same `pcrec_enabled_set_spec()` call, same `cli_err()` site) —
verified live, §5.

## 4. The blast radius I found and fixed (internal test files)

`pcrec_compile()` no longer reads the process-global implicitly at all —
that is true regardless of the NULL question in §2. Any test file that
called `pcrec_enabled_set_spec()` to install a NON-default set and then
relied on a bare `pcrec_default_options()` + `pcrec_compile()` (or a
directly-built `Ctx`) to see it needed migrating to pass the request
explicitly. Found by grep, fixed one by one, each rebuilt and reverified:

- **`tests/registry/pcre2_check.c`** — three compile helpers
  (`pcrec_try`/`pcrec_try_pos`/`pcrec_try_emit`) are called from inside the
  GATED passes (`check_gated_option_space`/`check_gated_uprops_space`),
  which install a focused module (e.g. `"modifiers"`) into the global and
  run thousands of compiles under it. Added a file-scope mirror
  (`g_pc2_features`, default `"none"`, matching the global's own pre-gate
  default) updated by a thin wrapper (`pc2_set_spec`) around every
  `pcrec_enabled_set_spec()` call in the file; all three compile helpers
  now pass `opt.features = g_pc2_features`.
- **`tests/registry/registry_check.c`** — `eng_refuses_by_name` (installs
  `feats`, compiles twice) and `check_free_discharge` (installs
  `"atomic-groups"`, compiles four patterns) now set `opt.features`
  explicitly at each of their `pcrec_compile()` calls.
- **`tests/registry/definitions_check.c`** — THREE `Ctx`-building helpers,
  not two: `check_str_entry`/`check_row_chain_entry`'s two
  `memset(&cx, 0, sizeof cx)` sites (found first), and — missed on the
  first pass, found only because `bash tests/registry/run_definitions_tests.sh`
  went red with 12 failures naming lookaround-shaped definition strings —
  `parse_one` and `mods_ctx`, which use the POINTER form
  `memset(cx, 0, sizeof(*cx))` my first grep for `memset(&cx, ...)` did
  not match. **This is the one real regression this lane produced and then
  caught itself**, and the mechanism is worth recording: a single grep
  pattern for "how a Ctx gets zeroed" is not exhaustive across a tree with
  two calling conventions (`Ctx cx` locals vs. `Ctx *cx` parameters) for
  the identical idiom. All four sites now read `cx->enabled_features =
  pcrec_enabled_mask();` right after their memset, restoring the
  "inherits whatever this file just installed" behaviour these white-box
  tests have always assumed.
- **`tests/registry/definitions_oracle_gen.c`** — same two-site pattern
  (`check_row_chain_entry`.equivalent, `check_textfn_entry`), same fix.
- **`tests/core/alloc_check.c`** — `child_attempt`'s conditional
  `pcrec_enabled_set_spec("unicode-props", ...)` call is now
  `opt.features = "unicode-props"` conditionally set on the `pcrec_options`
  it already builds; the now-pointless separate install call is deleted.
- **`tests/thread/ts3_driver.c`** — audited, NOT changed. It never calls
  `pcrec_enabled_set_spec()` anywhere, so it has always run at the empty
  default; that is exactly what it still gets under both the OLD
  (global-reading) and NEW (per-call, empty-by-default) mechanisms. Its
  two rejected jobs (`\d`, `(?=a)`) are unaffected.
- **`tests/parse/branch_count_check.c`**, **`tests/codegen/
  cpset_model_check.c`**, **`tests/mrl/cwmax_check.c`** — audited, NOT
  changed: none of the three ever calls `pcrec_enabled_set_spec()`, so all
  three already ran at (and still run at) the empty default.
- **`src/dump/syntax_dump.c`** — the three probe `Ctx` constructions
  (`built_status_probe`, and the two `--explain`/`--probe-ask` driving
  functions) each gained `cx.enabled_features = pcrec_enabled_mask();`
  right after their `memset`, and `put_agreement`'s bare
  `pcrec_feature_enabled(r->feature)` call became
  `pcrec_feature_enabled(pcrec_enabled_mask(), r->feature)` — all four
  preserve exactly the pre-existing "read whatever the CLI/probe machinery
  installed" behaviour.

No further `memset(&cx, 0, sizeof` / `memset(cx, 0, sizeof(*cx))` sites
exist in `src/` or `tests/` beyond the ones listed above and the ones
fixed (grepped tree-wide, both spellings, after the fact — see §6).

## 5. Validation, numbers inline — ALL COMPLETE

- `make -j4 CC=gcc-16` — clean.
- `make strict CC=gcc-16` — `strict: whole tree compiles clean with
  -Werror -Wshadow`.
- CLI black-box smoke (bare invocation, `--features none`, a bad spec) —
  byte-identical wording and behaviour to the pre-lane binary (bare `\d`
  compiles under `std1`, `--features none` refuses naming `classes`,
  `--features nosuchmodule` gives the unchanged wording).
- `bash tests/core/run_core_tests.sh` — **4/4 sub-checks green**
  (`sat_arith_check` 7, `sb_fragf_check` 6, `sb_stamp_check` 6, the new
  `features_opt_check` 5 — NULL/all/std1/nosuchmodule/interleaved, all as
  designed).
- `bash tests/registry/run_definitions_tests.sh` — **54/0** (was 12 FAILs
  before the `parse_one`/`mods_ctx` fix in §4).
- `bash tests/registry/run_registry_tests.sh` (full: PC-3, registry_check,
  definitions, axes_registry_check, limits_check, compliance_section.py,
  PC-4) — **0 `FAIL` lines in the whole log, `DONE rc=0`**; PC-3 alone
  `checks passed: 209 / checks failed: 0`; the definitions-oracle self-check
  `354 cells, 101244 A==B comparisons, 101244 A==C comparisons, 0
  disagreements`.
- `python3 scripts/emit_sweep.py --ref f12e123d` — **`SWEEP_DONE rc=0`,
  every one of the 5 self-check streams and 5 real-run streams reports
  `movers=0 asymmetric=0`** (corpus 3944 pattern rows, 306 composition
  files, elapsed 286.3s). Zero emitted bytes moved anywhere in the tree —
  exactly the expected result for a library-struct/mechanism-only change.
- `make test-codegen CC=gcc-16` (the 10-script `run_group.sh` target) —
  **9/10 scripts passed**, the one red being the pre-existing, documented
  darwin `nm arm_a.o` probe (`run_inline_capability.sh`: *"nm could not
  read arm_a.o (no rx_search symbol)"*) — confirmed pre-existing and
  unrelated (this is the standing red multiple prior lane reports and
  `docs/dev/wake.md` already document; not reproduced by anything this
  lane touched). **One real regression found and fixed along the way**:
  the first run showed a SECOND red, `[SABANCHOR] ... S111_gate_check_
  dropped.sh ... ANCHOR NOT FOUND` — my `pcrec_ext_gate` signature change
  (adding the `enabled_mask` parameter) moved the literal text a sabotage
  row's anchor was written against. Re-derived per `sabotages/CLAUDE.md`'s
  own rule for this exact situation ("re-derive from the text THIS CHANGE
  LEAVES BEHIND, not `git show HEAD:`, when your own lane is what moved
  the line"), intent re-verified (still deletes the one call that demotes
  a RESULT ask for a disabled module, at the same escape-doorway site),
  `scripts/m6read_check_sab_anchors.py` now reports "all anchors resolve"
  (270 rows / 286 anchor sites), and the re-run codegen target reads 9/10
  as expected.
- `make test-cli CC=gcc-16` — **cases passed: 284 / cases failed: 0**.
- `tests/thread/run_thread_tests.sh` — **SKIPS loudly (exit 0)**, exactly
  as BOILERPLATE's box facts predict: `gcc-16` on this darwin/arm64 box
  cannot link `-fsanitize=thread` (`___tsan_*` symbols unresolved). This
  is the box's standing condition, not a regression — confirmed by the
  script's own `SKIP:` line and `rc=0`. Because of this I cannot exercise
  the D19 claim under a real thread sanitizer here; the closest available
  proof is `features_opt_check`'s own interleaved single-process
  all/none/all/NULL/all sequence, which shows no state survives between
  calls but is NOT a substitute for TS-3-style concurrent-thread coverage.
  A genuine TSan confirmation of "no data race between two
  `pcrec_compile()` threads asking for different `--features`" is owed to
  whichever box can actually link TSan (ubuntubudu, per this tree's own
  box facts).
- No `.rxt` file added or touched (this row is a library struct field, not
  a corpus regression) — nothing owed there.
- No census/manifest pin moved apart from the one sabotage re-anchor
  above: `abi` unchanged (28), no emitted byte changed anywhere (the emit
  sweep confirms this directly), so no D76/D94 re-pin is owed.

**Nothing is owed.** Every validation item named in the brief completed
with numbers, and the one real defect this lane produced (the S111 anchor
drift) was found and fixed in the same session, not left for the manager.

## 6. Things worth a second look

- **`docs/dev/lanes/iface_digest.md` §1(b) is factually wrong about
  today's actual behaviour**, and it is worth fixing in the same wave that
  reads this report: it states *"a library caller gets the default `std1`
  set unconditionally"*. Measured (and independently confirmed by D37's
  own addendum, which predates the digest): a library caller who never
  calls `pcrec_enabled_set_spec()` gets the EMPTY mask, not `std1`. The
  digest also cited "tests/spec_mod0/ has C-level checks that link
  libpcrec.a" as this row's suggested test home — also not accurate:
  every `tests/spec_mod0/` check runs `build/pcrec` as a black box via
  `fork`/`exec` (`spec_pcrec.h`'s own header says so explicitly) and links
  nothing. `tests/core/` (this lane's actual home, §7 below) is the
  directory that genuinely fits "C-level check that links libpcrec.a".
- **A second `memset`-spelling exists for "build a Ctx by hand" in this
  tree** (`Ctx cx; memset(&cx, 0, sizeof cx);` vs. `Ctx *cx` parameter +
  `memset(cx, 0, sizeof(*cx))`), and nothing greps for both uniformly
  today. Any future change to `Ctx`'s zero-value contract (this one
  included) should grep BOTH spellings, not just the more common one — see
  §4's own missed-then-caught instance.

## 7. Where things live

- `lib/pcrec.h` — `pcrec_options.features` (new field, documented at the
  struct).
- `src/core/internal.h` — `Ctx.enabled_features`/`enabled_label`/
  `enabled_modules`; `pcrec_feature_enabled`/`pcrec_ext_gate` signatures;
  `pcrec_enabled_resolve_spec` declaration.
- `src/parse/enabled.c` — the pure resolver; `pcrec_enabled_set_spec`
  reduced to a thin caller of it plus the global install (unchanged
  otherwise).
- `src/parse/{ext,mod_verbs,mod_recursion,mod_backrefs,mod_modifiers,
  parse}.c` — 13 call-site updates, mechanical.
- `src/dump/syntax_dump.c` — 3 probe-`Ctx` seedings + 1 bare-mask call site.
- `src/gen/emit_dfa.c` — `emit_feature_comment`/`emit_feature_macros` now
  take `Ctx *` and read the per-compile stamp fields instead of the
  global getters (3 call sites updated).
- `src/core/compile.c` — `compile_driver`'s one resolution point (before
  the retry loop) + per-attempt `Ctx` seeding; `pcrec_count_groups` seeded
  from the global (query-surface behaviour, unchanged).
- `cli/main.c` — both `--features`-adjacent blocks now also set
  `opt.features`; nothing else changed.
- `tests/core/features_opt_check.c` (+ `run_core_tests.sh` wiring) — the
  new acceptance check.
- `tests/registry/{pcre2_check,registry_check,definitions_check,
  definitions_oracle_gen}.c`, `tests/core/alloc_check.c` — migrated to the
  new per-call mechanism (§4).
- `docs/spec/match_api.md` §8.2, `docs/spec/cli.md` (`--features` section),
  `lib/CLAUDE.md`, `CHANGELOG.md` — spec/doc hunks (D80).

## 8. Owed at hand-off

Nothing. All validation completed with numbers (§5). Logs archived at
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/
0d0f0671-4f9b-4850-b287-09b7b05fecb7/scratchpad/` (`libfeat_registry2.log`,
`libfeat_codegen3.log`, `libfeat_sweep.log`, `libfeat_cli2.log`) for
anyone who wants the full transcripts rather than the summary numbers
above — these are scratchpad paths and will not survive past this
session, so anything worth keeping from them is already quoted in §5.

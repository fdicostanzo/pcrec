# [FLAG-DEMOTE] build map: the internal deny word and the per-flag site list

Status: PROPOSED (lane flagprep, 2026-11-12, sonnet; design map only, NO build go).
Inputs: D195, `docs/dev/flag_audit_2026-11-12.md` (read-only audit), plan row
[FLAG-DEMOTE]. All file:line cites are against main a1d7743bf and WILL drift;
the build lane re-greps (the greps are given). Spec cites are by section.

## GOALS

1. The 20 confident public deny flags and the dropped alias leave the PUBLIC
   flags word, yet every internal writer (size-cap ladder, tune dial) and every
   test lever can still deny the mechanism. Who: callers (smaller contract,
   [IFACE-PUSH] headroom 6 -> about 27 free bits); measurable: `lib/pcrec.h`
   defines 22 fewer option macros, `grep -c "PCREC_BIT(" lib/pcrec.h` drops by 22.
2. Zero change to any DEFAULT artifact. Who: bench, identity gate; measurable:
   the default-corpus byte sweep (`make test-codegen`, the identity gate) moves 0
   bytes, abi number unchanged.
3. The answer-identity sweep (`make test-axes`) keeps reaching every demoted
   axis with no hand list. Who: the maintainers; measurable: `run_axes.sh` arm
   count unchanged (it hard-fails on an axis with no spelling).
4. A mostly mechanical build: one enabling commit with a proving pair, then
   batches that are rename + re-spell.

Priority: 2 > 1 > 3 > 4. Non-goals: the 3 medium and 6 unsure flags (stay
public, D195); renumbering surviving public bits (not needed, 27 free); a
pcrec_options field for the internal word.

## 0. What the audit got wrong or left out (read first)

- NO abi bump is expected. The audit calls the `rx_info.flags` KEPT-set change
  "a stamp/abi event". It is not for any default artifact: `emit_info_def`
  (`src/gen/emit_dfa.c`, search `const uint64_t kept`) masks every axis bit not in
  `kept`, so a default artifact's `.flags` never carries bits 12 or 50. Only an
  artifact built UNDER the denial (now harness-only) loses a bit from `.flags`.
  The spec hunk (tuning.md §2¶3, the KEPT sentence; match_api.md rx_info.flags)
  is owed; the abi number is not. The build lane PROVES it (goal 2) rather than
  assumes it; if the identity gate moves, stop and bump per D94.
- The fence. `tests/compound/run_lever_fence.sh` check (c) forbids the
  literal `--harness=` in docs/spec, docs/guide, README.md, examples, lib, tests,
  scripts and cli outside a named allowlist. Re-spelling about 118 test files
  and 3 scripts (the grep counts below) trips it on day one, and the spec cannot
  print the spelling. RULING NEEDED (section 5, R1).
- The compound parts do NOT inherit `PcrecEmitIn.harness`: `part_compile`
  (`src/core/compound.c:58-76`) builds its own emit input with `.harness = NULL`
  and copies only `parent->flags`. A harness-set denial would silently stop at the
  compound shell. The internal word needs an explicit carrier (section 1.3).
- pcrec-bench is a contract break, not a note (section 4).
- The sweep tool compares across revisions: `scripts/emit_sweep.py --extra`
  appends the arm to BOTH sides (its usage text), and the old side has no
  `--harness=no-X`. See R4.

## 1. The internal deny word

### 1.1 Shape (recommended: tagged keys, a second word in `Ctx`)

Every consumer of a denial today is one of two shapes: `pcrec_opt_has(cx->opt,
KEY)` (about 50 sites) or a table row with a `uint64_t deny` column evaluated by a
generic function against a flags word. The design keeps BOTH shapes and keeps the
keys as `uint64_t`:

- An INTERNAL KEY is `PCREC_XTAG | PCREC_BIT(n)` with `PCREC_XTAG = PCREC_BIT(63)`,
  n in 0..22, named `PCREC_X_NO_<NAME>`, defined in `src/core/internal.h` in a
  new block beside FLAG-ACCESS (NOT in `lib/pcrec.h`). Bit 63 of the public word
  is reserved for the tag forever (cost: one of the freed bits).
- The internal bits live in ONE new word `uint64_t xdeny`, in `Ctx`
  (`src/core/internal.h:4397`, next to `const pcrec_options *opt`), and in
  `FitSel` for the ladder predicates. NOT in `pcrec_options` (public ABI; the
  harness precedent in `internal.h` "outside `pcrec_options` and outside the
  caller contract") and not a 128-bit word (every `uint64_t deny` column, every
  `%llu` print and `pcrec_axis_on` would change type for nothing).
- ONE primitive and ONE reader-facing accessor, in the FLAG-ACCESS block
  (`internal.h:553-570`), so `tests/core/flag_access_check.py` still exempts only
  that block:

      #define PCREC_XTAG PCREC_BIT(63)
      static inline bool pcrec_key_has(uint64_t flags, uint64_t xdeny, uint64_t key)
      { return (key & PCREC_XTAG) ? (xdeny & key & ~PCREC_XTAG) != 0
                                  : (flags & key) != 0; }
      static inline bool pcrec_cx_has(const Ctx *cx, uint64_t key)
      { return pcrec_key_has(cx->opt->flags, cx->xdeny, key); }

  `pcrec_cx_has` is the ONE accessor for denial readers and works for public and
  internal keys alike, so a flag that is later demoted or promoted changes its
  macro name only, never its call shape. A composite key mixing a tagged and an
  untagged bit is forbidden (a `_Static_assert` in the table macros; the one
  existing composite that would mix is the FIT_TRACE mask, section 1.4).
- `flag_access_check.py` gains two rules: `pcrec_opt_has`/`pcrec_flags_has` on a
  `PCREC_X_` token is a finding (it would read the public word and answer "not
  denied", silently), and a raw `->xdeny` read outside the block is a finding.

Why tagged keys: `src/core/axes.def`, `axes_dump.c`'s `deny_cols`/`DENY_NAMES`,
the `--list-axes` columns, `run_axes.sh`'s macro->spelling pairing, and
`facts.def`/`DfaCand`/`ctxnode.c`/`clskit.c` tables all carry a key as a
`uint64_t` token and stringify it with `#macro`. They keep working with a tagged
key; only the three evaluators that apply a key to a word change (1.2).

Rejected: (a) "park in place": keep the 20 bits at their old positions in the
working word and only stop accepting them from callers. Zero reader edits, but the
freed positions are not free (the working word still owns them), which falsifies
D195's "about 27 free"; it is the cheap fallback if the manager prefers D77
(build under measurement) to the headroom. (b) a second table column per row:
doubles every table. (c) `unsigned __int128` keys: a type change everywhere.

### 1.2 Writers and readers: touch points (all `src/`)

Evaluators that apply a key to a flags word, each takes `cx` (or gets `xdeny`):

| site | today | change |
|---|---|---|
| `src/gen/emit_dfa.c:6014` | `pcrec_flags_has(flags, cand->deny)` (DFA candidate walk) | `pcrec_key_has(flags, cx->xdeny, cand->deny)` |
| `src/gen/emit_dfa.c:10977` | same on `r->c.deny` (start-table walk) | same |
| `src/gen/emit_dfa.c:13994` | `pcrec_flags_has(cx->opt->flags, r->deny)` (rev-end-form rows) | `pcrec_cx_has(cx, r->deny)` |
| `src/parse/ctxnode.c:135` | `pcrec_opt_has(cx->opt, r->deny)` | `pcrec_cx_has` |
| `src/gen/clskit.c:707,790,836` | `pcrec_clskit_deny_of(flags)` maps flags -> mask via `DENY_FLAG[]` | take `(flags, xdeny)`; its callers pass both |
| `src/gen/memfn_sites.c:42-62` | `deny_map[]` flag -> `MF_D_*`, `pcrec_memfn_denies(flags)` | key becomes `PCREC_X_NO_RUN_OVERLAP`; `pcrec_memfn_denies(flags, xdeny)`; the reverse `pcrec_memfn_deny_flags` (axes_dump.c:709) unchanged in shape |
| `src/facts/facts.c:161` | `pcrec_flags_masked(cx->opt->flags, pf_deny[f])` | key-aware masked variant (`facts.def:47,50`: rows for bits 28, 29) |
| `src/opt/possessify.c:2069-2073` | `fl = cx->opt->flags`, two `pcrec_flags_has` | `pcrec_cx_has(cx, ...)` |
| `src/core/compile.c:88-110` | `pcrec_axis_on(flags, deny, force)` | unchanged: no demoted key is read through it today (grep proves it at build time) |

Direct readers (`pcrec_opt_has(cx->opt, K)` -> `pcrec_cx_has(cx, X_K)`) are listed
per flag in section 3.

### 1.3 Who sets the word, per attempt

The driver builds the word once per ATTEMPT beside `cx.opt = &defo`
(`src/core/compile.c:2391`; also the facts view at `:3689` and the count-groups
`Ctx` at `:3863`, which sets 0) from three sources, OR-ed:

1. THE LEVER: `--harness=no-<axis>` sets `PcrecHarnessOptions.xdeny`
   (`internal.h:208` struct). The driver reads it through the emit input:
   `emit_in->harness ? emit_in->harness->xdeny : 0` OR new `emit_in->xdeny`
   (`PcrecEmitIn`, `internal.h:~270`). Reading `harness->xdeny` covers every CLI
   mode that already passes `.harness` (`cli/main.c:2453` callouts, `:3012`
   the listing pin, `:3587-3599` the compile) with no CLI edit. NO new global in
   libpcrec.a (fence check (a): still exactly `pcrec_harness_compile`).
2. THE DIAL: `TUNE_TABLE` (`src/core/tune.c:~75-96`) column `deny_flags`
   (`internal.h:7687`) holds only `PCREC_NO_PREMUL_TABLE` (row -2, `tune.c:81`).
   After the flag demotes every public cell is 0, so retype the column as the
   internal word (`xdeny`) and rename `pcrec_tune_deny_flags` (`tune.c:266`,
   `internal.h:7720`, `compile.c:2078`) to `pcrec_tune_xdeny`. OR-ed, never
   assigned (the spec sentence "a caller who typed -fno-premul-table at +1 keeps
   their denial", `tune.c` comment above `compile.c:2078`, becomes "a lever").
3. THE LADDER: `FitSets` (`compile.c:954`, the `flags_or` field) gains a LAST field
   `xflags_or`; the two rows that write internal keys carry it:
   `drop-premul` (`compile.c:1445`, `PCREC_NO_PREMUL_TABLE`) and `drop-islands`
   (`compile.c:1486`, `PCREC_NO_ALT_ISLAND`). `drop-landmark-walk` (`:1424`,
   bit 57) and `drop-prefilter` (`:1463`, bit 8) stay public KEEP flags and keep
   `flags_or`. The apply site `compile.c:2703` (`defo.flags |= w->flags_or`) gains
   `xdeny |= w->xflags_or`. `FitSel` (`compile.c:2582` build, `internal.h` struct)
   gains `.xdeny`; predicates `fit_premul_applies` (`compile.c:1203-1210`) and
   `fit_islands_applies` read it through `pcrec_key_has`. The FIT_TRACE mask
   (`compile.c:2021-2024`, `PCREC_NO_PREMUL_TABLE | PCREC_NO_PREFILTER`) splits into
   two masked terms (a composite of a tagged and an untagged bit is forbidden).
4. COMPOUND PARTS: `part_compile` (`src/core/compound.c:58-76`, and the three
   callers) takes the parent's EFFECTIVE `xdeny` and passes `.xdeny` in the part's
   emit input (parts keep `.harness = NULL`; `walk_arms` has its own bypass at
   `compound.c:174`, do not copy it). Without this the lever stops at the shell
   (the silent-no-op shape in `docs/dev/learnings.md` §3).

Sequencing hazard (audit section 6, confirmed): the word must exist and be
witnessed BEFORE any demotion lands, or the ladder and the dial stop denying.

### 1.4 Stamps, rx_info, listings

- Stamps (`<PREFIX>_VM_STRATS`, `RX_DFA_*`, ...) record EFFECT, not the flag word;
  none reads the deny word. Verified by grep: the only emitter of option bits is
  `emit_info_def` (`emit_dfa.c:3270-3306`).
- `rx_info.flags`: delete `PCREC_NO_ATOMIC_DISCHARGE` and `PCREC_NO_POSS_CTX_FOLLOW`
  from `kept` (`emit_dfa.c:3300-3302`). `axis_bits` ORs the tagged keys too (the
  X-macro includes the rows); filter `& ~PCREC_XTAG` there so the intent is
  explicit. Decision R3: drop (recommended, nothing public can set them) or add a
  harness-only stamp (rejected: a new emitted line is an abi event for a thing
  nobody reads).
- `--list-axes` (`src/dump/axes_dump.c`): `deny_cols` prints `deny_macro` from
  `#macro` (works) and `deny_bit` from the bit index (prints 63 for a tagged key:
  print `x<n>` instead, n = ctz of the key without the tag; ~5 lines). The
  `cli_flag` column carries the harness spelling for these rows (no schema change:
  `--engine=` already lives in that column).
- `--emit-facts` `deny:%s` (`src/dump/facts_dump.c:102`, `fd_deny_flag`) prints the
  key name: prints `PCREC_X_NO_VM_ANCHOR_BOUND` etc. (wording only; D26).

## 2. The CLI and the registry

- `cli_axis_apply` (`cli/main.c:1082-1096`) is one X-macro loop over
  `axes.def`. For a row whose `dm` is tagged, the shipped build must NOT accept
  `-fno-X` (it has no `df` once the row is re-spelled); under `-DPCREC_HARNESS`
  the same loop accepts `df` = `--harness=no-<axis>` and does
  `st->harness.xdeny |= dm & ~PCREC_XTAG`. The signature gains the harness pointer
  (or the caller passes `&xdeny`). One loop, no 21 `strcmp` arms ("add an axis by
  adding the row", `cli/CLAUDE.md`). An unknown `-fno-possessify` on the shipped
  binary falls through to the existing unknown-option diagnostic (D26: no new
  wording).
- Spelling rule: `--harness=no-<flag minus "-fno-">`: `no-possessify`,
  `no-revdet`, `no-counter`, `no-length-prune`, `no-atomic-discharge`,
  `no-premul-table`, `no-anchored-dfa`, `no-start-pinned`, `no-alt-island`,
  `no-cls-fold`, `no-vm-anchor-bound`, `no-end-window`, `no-ctx-node`,
  `no-view-edge`, `no-run-overlap`, `no-poss-ctx-follow`, `no-poss-bref-first`,
  `no-start-width`, `no-start-landing`, `no-rev-end-onewalk`. Consistent with the
  existing `--harness=no-compound` / `no-min-width`; no collision (exact `strcmp`).
- `src/core/axes.def`: each demoted row keeps its place and changes only the
  two tokens: `PCREC_AXIS(PCREC_X_NO_POSSESSIFY, "--harness=no-possessify", 0, "", DEFAULT_ON)`.
  The header comment at the top of the file (the "lib/pcrec.h is the only home of
  bit VALUES" paragraph) gains one sentence naming `internal.h` for internal keys.
  Keeping the rows is what keeps `run_axes.sh` complete for free (3 below).
- `tests/axes/run_axes.sh` (about `:314-370`): the pairing awk skips a
  `cli_flag` that starts with `--` (`f[1] !~ /^--/`, written for `--engine=`); the
  `--harness=` rows need their own branch: collect them into a second map and run
  those arms with `build/pcrec-harness`. Its `bit_macro` derivation greps
  `lib/pcrec.h` for `NAME = PCREC_BIT(N)`; the demoted macros vanish from the
  header, so the "every derived bit macro has a spelling" guard (`:352-358`) would
  stop covering them. Re-aim it to ALSO derive the internal keys from
  `internal.h` (grep `PCREC_X_`), keeping the hard-fail on zero (learnings §3).
  The `tuning.md` §2 "(bit N)" cross-check (`:362-375`: `doc_bits` vs `reg_bits`)
  must compare the same union.
- `tests/registry/axes_registry_check.sh`: `check_cli_flag_accepted` drives the
  parser live; run it for `--harness=` rows against `build/pcrec-harness` and
  assert the SHIPPED binary REJECTS each old `-fno-X` (new control: a demotion that
  left the public spelling alive passes everything else).
- `tests/ci/cloud_axes_shards.tsv`, `tests/ci/measured_axes.tsv`,
  `tests/ci/cloud_units_plan.py`, `tests/ci/fixtures/run_s8.green.txt`: keyed by
  flag spelling; re-key (mechanical; already on the fence allowlist).
- `Makefile:153`: `make` (the default target) already builds
  `build/pcrec-harness`, so `make test` needs no new dependency. Every re-spelled
  driver must resolve the harness binary the way `tests/axes/run_axes.sh` does.

## 3. Per flag (bit, macro, readers, tests, spec, bench)

"Direct" = `pcrec_opt_has(...)` single call sites to rewrite as `pcrec_cx_has(cx,
PCREC_X_...)`; "table" = reaches through an evaluator of section 1.2. Mech =
`tests/mech/sabotages/S*` that name it (re-aim, do not delete). Bench = pcrec-bench
code (not prose reports) naming it (section 4). All have an `axes.def` row and a
`src/dump/axes_dump.c` stamp-site mention (omitted below unless the line matters).
Spec = `docs/spec/tuning.md` section (heading carries "(bit N)", see R2) plus other
spec files.

| bit | flag | readers | tests / mech / pins | spec | bench |
|---|---|---|---|---|---|
| 4 | possessify | direct `emit_vm.c:9991`, `select_engine.c:569` | tests/possessify(4) mech(4) codegen(2) ci vm recursion prefilter axes atomic_groups; Makefile; S92 S98 S217 | §2.1; ir_listing §3 (`possessify` row: "EMPTY when -fno-possessify denied"), match_api (RX_VM_STRATS), limits §7¶4 | selfcheck only (prose) |
| 5 | revdet | direct `select_engine.c:591` | tests/rungselect(3) codegen(2) ci vm registry prefilter possessify mech lib counterk axes; Makefile; matrix row | §2.2 | none |
| 6 | counter | direct `emit_vm.c:2479,3214,6833` | tests/counterk(5) codegen(2) ci vm registry prefilter mech lib harness axes; Makefile; matrix row | §2.3 (replication cap refusal is a documented give-up the sweep classifies) | none |
| 7 | length-prune | direct `emit_vm.c:10652` | tests/mrl(4) mech(2) ci bench atomic_groups prefilter litscan lib base axes; `emit_sweep.py` DIFFER_PINS 4 cells (504-505, 557-558); Makefile; S59 | §2.4; match_api (`prune ceiling` "none"), ir_listing §3.1.2 | none |
| 12 | atomic-discharge | direct `atomic.c:550`; KEPT mask `emit_dfa.c:3300` | tests/ci(2) codegen atomic_groups (`run_atomic_diff.sh`) | §2.8 + §2¶3 (KEPT set); cli.md 1.18 (generic) | none |
| 15 | premul-table | LADDER `compile.c:1210,1445,2024`; DIAL `tune.c:81`; table `emit_dfa.c:6350` | tests/codegen(4) mech(3) ci uprops size resource axes; S249 S250 S251 S252 S634; the tune-dial and ladder drivers | §2.13, §5.4 table row; limits §8 ladder row | selfcheck.py:114,4439 prose only |
| 17 | anchored-dfa | direct `compile.c:391`; table `emit_dfa.c:10845` (route list) | 29 files: tests/mech(5) codegen(5) revend(3) landwalk(3) endmark(3) ci assertions(2) anchored(2) axes; S190 S439 S741 S890 S1073 S1824 | §2.15; match_api (anchored `_match`) | selfcheck.py:117 prose (adapter comment `:122,:1071`) |
| 22 | start-pinned | table `emit_dfa.c:10786` | tests/codegen(5) ci resource registry mech; DIFFER_PINS 4 cells (486-487, 539-540); `emit_sweep.py`; S221 | §2.19 | `DENY_FLAGS` "nopin" `adapter.py`; selfcheck 4106,4618,5919,7344 |
| 23 | alt-island | LADDER `compile.c:1486`; direct `emit_vm.c:4420` | tests/mech(3) island(3) codegen(3) registry ci; Makefile; S1880 S1881 S1894 | §2.20; limits §8 rung 6, §8.5¶1b | `configs.toml:630` (pinned testee flags), `DENY_FLAGS` "noisland", selfcheck 6849,7003,7010 |
| 24 | cls-fold | table `clskit.c:836` (`DENY_FLAG[]`) | tests/codegen(4) ci registry | tuning.md §2.22; match_api (`"fold"` stamp) | `configs.toml:695,701`, `DENY_FLAGS` "noclsfold", selfcheck 7123 |
| 28 | vm-anchor-bound | table `emit_dfa.c:10755,10761`; fact `facts.def:47` | tests/codegen(3) mech ci; DIFFER_PINS 4 cells (492-493, 545-546); S295 | §2.25; match_api (`"unanchored"`), registry | selfcheck.py:10824 (spelling pair) |
| 29 | end-window | table `emit_dfa.c:10472`; fact `facts.def:50` | tests/ci(3) mech(2) codegen(2); scripts/tests; DIFFER_PINS 4 cells (494-495, 547-548) + `ASSERT_ZERO` (`emit_sweep.py:612`); S295 S551 | §2.26; match_api (end window), registry | `adapter.py:915`, selfcheck.py:10825 |
| 35 | ctx-node | table `ctxnode.c:118,135` | tests/ucp(2) registry(2) mech(2) codegen(2) ci axes; S342 | §2.32; cli.md | `DENY_FLAGS` "noctxnode", selfcheck 11228,11230 (b118 control) |
| 42 | view-edge | direct `scanedge.c:577` | tests/ci(2) registry codegen assertions | §2.37 | `DENY_FLAGS` "noviewedge", selfcheck 11540 |
| 43 | run-overlap | table `memfn_sites.c:42` | tests/codegen(4) mech(3) memfn(2) registry ci; S267 S570 S571 | §2.38; match_api (`RX_RUN_WORDS`) | `DENY_FLAGS` "norunoverlap", selfcheck 11512,11515 |
| 50 | poss-ctx-follow | direct `possessify.c:2072`; KEPT mask `emit_dfa.c:3301` | tests/possessify(3) codegen(2) ci (`run_recursion_identity.sh:229,1929`) | §2.44; §2¶3 | `DENY_FLAGS` "nopossctxfollow", selfcheck 11899-11914 |
| 51 | poss-bref-first | direct `possessify.c:2073` | tests/possessify(3) codegen(2) ci registry reject(1: the reject table names it) | §2.45 | `DENY_FLAGS` "nopossbreffirst" |
| 53 | start-width | table `emit_dfa.c:10792` | tests/codegen(5) ci(3) mech(2) axes(2) (`start_landing_movers.tsv`); S220 S227 | §2.47 | `DENY_FLAGS` "nostartwidth", selfcheck 7729,11493 |
| 54 | start-landing | table `emit_dfa.c:10798` | tests/codegen(8) ci(3) mech(2) axes(2) uprops resource prefilter; S220 S252 | §2.48 | `DENY_FLAGS` "nostartlanding", selfcheck 7733,11493 |
| 56 | rev-end-onewalk | direct `emit_dfa.c:13940`; table `:13959-13963` | tests/endmark(3) codegen(2) mech ci; S772 | §2.50; limits §8 row 0a | `DENY_FLAGS` "norevendonewalk", selfcheck 7751 |
| DROP 45 | req-set-lead (alias) | `cli/main.c:1091` accept; `compile.c:2095-2117` strip+rewrite; `lib/pcrec.h:1105` macro; `axes.def` comment; `memfn/src/options.def:69` comment | tests/mech(3) codegen(3) axes(2) memfn(1); `emit_sweep.py:580` comment; S462 S596 S1110 | §2.40 + registry.md (`pres-set-lead` row) | `DENY_FLAGS` "noreqsetlead", selfcheck 11742 |

Totals (grep, `-fno-<flag>` over the 21): 118 files under tests/, 3 under
scripts/+Makefile. 7 are `.rxt` (flags lines); the rest are drivers.

Bit 55: no macro, no reader (verified: `grep -rn "PCREC_BIT(55)\|bit 55"` finds the
one `lib/pcrec.h:1204` comment, plus kit journal prose). Release = delete that
comment sentence and the audit table row; nothing else. `memfn/` is read-only for
this lane; `memfn/docs/responses.md:2871` already records the rung as dead.

Per-flag extras (from the audit, confirmed):
- 15, 23: the only two flags the ladder/dial write (section 1.3); they are the
  proving pair for the enabling commit.
- 12, 50: the KEPT mask (1.4). `--engine=dfa` plus the denial must still REFUSE
  (tuning §2.8¶2, §2.44¶2): keep those refusal tests, now through the lever.
- 29: spec §2.26 names a wrong-answer risk. The denial is today the only
  field-usable bisect for a suspected end-window miscompile. Demoting removes it
  from the shipped CLI (`build/pcrec-harness` is built by `make` but there is no
  install target). That is the rule's intended consequence (wrongness risk gets a
  test lever), noted so Frank's go is informed.
- 17 and 15: the audit's section 3 flags these as the strongest size knobs; D195
  chose demote. They remain reachable by `--tune=-2` (15) and the size cap ladder.
- 28/29 appear as `facts.def` deny columns: the fact is stored empty under the
  deny; the evaluator is `facts.c:161`, row 1.2.

## 4. pcrec-bench: a contract break (STOP RULE case)

The audit (section 3) found 2 pinned configs (cls-fold, alt-island). Reading
pcrec-bench code shows more, and they are code, not prose:

- `testees/pcrec/adapter.py:3421` `DENY_FLAGS` is a closed tuple of (flag, word,
  why). 12 of the 21 are in it (22, 23, 24, 35, 42, 43, 45, 50, 51, 53, 54, 56).
  The word joins the DERIVED `testee_id` (`effective_denies`, `:3844`): the
  spelling is part of a testee's IDENTITY. Re-spelling to `--harness=no-X` without
  a stable word mapping would change stored ids.
- `tools/selfcheck.py` (the bench's gate) runs these flags against a pin's
  `build/pcrec` at about 25 sites (listed in section 3's bench column): the
  deny-flag controls (`:7983`), the `-fno-alt-island` chain arms (`:6849`,
  `:7003`), `-fno-cls-fold` (`:7123`), b118 ctx-node (`:11228`), b135 start
  denies (`:11493`), `:7643-7751`, `:11512-11540`, `:11742`, `:11899-11914`.
- `testees/pcrec/configs.toml`: `:630` (`-fno-alt-island`), `:695,:701`
  (`-fno-cls-fold`), plus `$PCREC_LOCAL_FLAGS` hints at `:616,:678`.
- `testees/pcrec/list_axes.tsv` is `--list-axes` archived VERBATIM per pin, with
  the [B18] gate (`selfcheck.py:122`) comparing; the `cli_flag` and `deny_bit`
  cells of 20 rows change at the first pin after the demotion.
- `pin.sh` runs plain `make` (so `build/pcrec-harness` exists at new pins) but
  the adapter's argv builder targets `build/pcrec`.
- OLD PINS ARE UNAFFECTED: a pin built before the demotion keeps `-fno-X`. The
  adapter must pick the spelling and the binary by pin (an abi or commit
  threshold the bench owns). That is the bench's change, not ours.

Draft inbox item (the manager sends it; one-file `[inbox]` commit):

> I-nn (pcrec to bench): [FLAG-DEMOTE] (D195, Frank 2026-11-12). From pin P
> (the first main commit after the demotion lands; we will tell you the sha),
> 20 deny flags stop being public options and become test-only levers on a SECOND
> binary, `build/pcrec-harness` (already built by `make`, same libpcrec, same
> generated code). Old spelling -> new: `-fno-X` -> `--harness=no-X` for X in
> possessify, revdet, counter, length-prune, atomic-discharge, premul-table,
> anchored-dfa, start-pinned, alt-island, cls-fold, vm-anchor-bound, end-window,
> ctx-node, view-edge, run-overlap, poss-ctx-follow, poss-bref-first, start-width,
> start-landing, rev-end-onewalk. `-fno-req-set-lead` is removed (use
> `--memfn=no-pres-set-lead`). Pins before P are unchanged. Default artifacts are
> byte-identical across P (we check this), no abi change expected. What this
> breaks on your side: `adapter.py` DENY_FLAGS entries for 12 of these, their
> derived testee_id words (keep the WORDS stable, change the spelling per pin),
> `configs.toml:630,695,701`, about 25 selfcheck.py sites, and the
> `list_axes.tsv` archive at the first new pin. Please reply either way: when you
> can take the adapter change and whether you want the new binary path exposed
> as a field in pin.sh's output.

## 5. Rulings needed before the build go

| id | question | recommendation |
|---|---|---|
| R1 | The lever fence (`run_lever_fence.sh` check c) forbids `--harness=` in tests/, scripts/, cli/ outside an allowlist and in docs/spec. | Split by FAMILY: keep (a) and (b) as they are (one global; no lib/ declaration); in (c) allow `--harness=no-<axis>` for axes.def-derived spellings in tests/, scripts/, cli/ (not docs/spec, docs/guide, README, examples, lib). The spec says "a test-only lever" and points at `cli/CLAUDE.md`. Sabotage row: plant a `--harness=no-` mention in docs/spec, must fail. |
| R2 | tuning.md §2 headings carry "(bit N)" and `run_axes.sh` cross-checks them against the header. | Demoted headings read "(internal key X-n)"; the check compares the union of header bits and `internal.h` keys. |
| R3 | `rx_info.flags` for 12 and 50 | Drop from `kept`; spec hunk only; no new stamp. |
| R4 | `emit_sweep.py --extra` goes to BOTH sides; a ref older than the demotion lacks `--harness=no-X`. | Resolve the spelling per side from that side's own `--list-axes` (the `cli_flag` column) or run demoted arms only on the working side; 16 DIFFER_PINS cells (length-prune, start-pinned, vm-anchor-bound, end-window x byte/utf8 x c-default/c-vm) re-spelled. |
| R5 | Old callers setting a freed bit (4, 5, ...) are silently ignored (there is no unknown-bit refusal in `compile_driver`; grep finds none). | Leave it: pre-1.0, the macro is gone so source callers fail to compile. Reserve the freed positions in `lib/pcrec.h` with one comment block so none is reassigned in the same release. |

## 6. Order of work (commits for the build lane)

Each commit leaves `make strict` clean and the default-corpus byte sweep at 0
movers; validation per RUNS.md (background, queue). `make test` at the end of
each batch; `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` at C1.

- C0 spec and fence: ruling R1 applied to `run_lever_fence.sh` (+ its planted
  control), docs/dev decisions D195 addendum for R2-R5. No src.
- C1 THE INTERNAL WORD + THE PROVING PAIR (premul 15, alt-island 23), one commit:
  `PCREC_XTAG`, `pcrec_key_has`, `pcrec_cx_has`, `Ctx.xdeny`, `PcrecEmitIn.xdeny`,
  `PcrecHarnessOptions.xdeny`, the driver's per-attempt assembly, compound carry,
  `FitSets.xflags_or`/`FitSel.xdeny`, the dial column, the CLI loop, axes_dump
  `x<n>`, `flag_access_check.py` rules, run_axes/registry re-aim, and the two
  flags' macros moved out of `lib/pcrec.h`. Sabotage rows (each needs a witness
  that REACHES its site, [MECH-REACH]): ladder `xflags_or` write blanked; dial
  `xdeny` cell blanked; part drops the carried word; an evaluator reading the
  public word only; `pcrec_opt_has` on an X key (the checker). Re-aim
  S249-S252, S634, S1880/S1881/S1894 and the dial/ladder drivers
  (`run_tune_dial`, `run_premul_table`).
- C2 batch A, direct single-reader VM/opt: 5, 6, 7, 42 (+ S59, mrl/counterk
  drivers, DIFFER_PINS length-prune cells).
- C3 batch B, possessify/atomic: 4, 12, 50, 51 and the KEPT-set change (R3);
  `run_recursion_identity.sh`, atomic diff, reject table.
- C4 batch C, DFA candidate tables: 17, 22, 53, 54, 56, 28, 29 (+ facts rows);
  `start_landing_movers.tsv`, DIFFER_PINS start/vm-anchor/end-window cells
  (R4), `ASSERT_ZERO`, S190 S220-S227 S295 S441.. (see section 3).
- C5 batch D, tables outside DFA: 24 (clskit), 35 (ctxnode), 43 (memfn deny_map;
  also S267 S570 S571).
- C6 the drop and the release: 45 (alias, bit, `cli/main.c:1091`,
  `compile.c:2095-2117`, kit comment, §2.40, registry.md) and bit 55's comment;
  `lib/pcrec.h` freed-position block (R5); `lib/CLAUDE.md` lines 12-13;
  `cli/CLAUDE.md`; `docs/testing.md` (20 mentions).
- Last: spec sweep and a grep gate: `grep -rn "PCREC_NO_<20 names>" lib/ docs/spec
  README.md docs/guide` empty. Then the manager sends the bench item (section 4).

Spec hunks (D80), one per batch not one at the end: `tuning.md` §2.N for each
flag, §2¶3 (KEPT), §2¶4 table (bit column), §4 `pcrec_options` mirror, §5.4 row
(premul); `cli.md` §1.18; `match_api.md` and `ir_listing.md` prose that spells
`-fno-possessify`, `-fno-anchored-dfa`, `-fno-end-window`, `-fno-length-prune`,
`-fno-vm-anchor-bound`, `-fno-run-overlap`; `limits.md` §7¶4, §8 rungs 0a and 6 and
§8.5¶1b; `registry.md` (deny_bit `x<n>` rule, `cli_flag` may carry a lever).
Prose in spec must not print `--harness=` (R1).

## 7. The three standing questions

1. Measurement regime: RELEVANT only as the claim "no default artifact moves".
   That is a byte comparison, regime-free (identical gcc, identical corpus,
   before/after the same commit pair); no timing is read or produced. No speed
   number in this note is new; the audit's figures are quoted there.
2. Independent control: the control for "the lever denies what the flag denied" is
   the answer-identity sweep plus the stamp that each deny moves (`DIFFER_PINS`
   floors, form census), which read the ARTIFACT, not the flag word, so they do
   not share a source with the word they exercise. The control for the new word
   itself is the five sabotage rows in C1; their witnesses must reach the site
   (`REACH_ONLY=1`). The coverage population is counted by `run_axes.sh`'s
   hard-fail on an axis without a spelling (K35).
3. What moves when data is regenerated: `--list-axes` output (20 rows' `deny_bit`
   and `cli_flag` cells; `tests/registry` pins, `tests/ci/*axes*.tsv`), the
   bench's `list_axes.tsv` archive, `DIFFER_PINS` spellings, the tuning.md §2¶4
   table. No emitted byte, no stamp value, no abi number.

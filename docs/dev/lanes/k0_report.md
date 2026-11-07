# k0 — [XARCH-DEV] unit K0: the kit's CPU target table (kit request R-36)

Lane k0 (opus), branch `lane/memfn-k0` cut from the kit branch `lane/memfn-k1107` at de178e0dd (main with
R-36). Build GO: Frank 2026-11-07 (R-36, "this should be next (at least in parallel) to unblock kit").
Contract: `docs/design/memfn/target_seam_units.md` rev 1 (§2's K0 row, §3, §4, §5, §6) and
`docs/design/memfn/target_seam.md` rev 1. STATE: delivered; the four gate jobs are OWED (written and
dry-run, not queued; see Gate jobs).

## Summary

The target table now lives in the kit, as the units note's R3/R4 rule it, with its FACTS APART FROM
ITS C SPELLINGS (the manager's ruling, from Frank's 2026-11-07 manifesto entry: code may be emitted as
C or Rust): `memfn/src/targets.def` (the facts: tokens only), `memfn/src/targets_c.def` (the C
emitter's family guard conditions and the kit's host chain), `memfn/src/targets.c` (the entries, in a
facts section and a C section), and a new section of `memfn/include/memfn.h` (the view pcrec will call
at option parse, naming no target, family or feature). Tokens `generic`, `x86-64`, `x86-64-v3`,
`armv8-a`; families `x86_64` and `aarch64` (respelled by k0fix, 2026-11-07: k0fix_report.md) with their default lists and the host default. Per token:
its family, its NEEDS (what a part for it must enable) and sorted features (`sahf` in x86-64-v3's, R2);
then, separately, its C spellings: the region text (open, close: the needs as a clang push and a GCC
push, never `arch=`) and the family guard text. The run-time CPU predicate text is NOT in K0: it lands
with U4 in the C spellings (see The entries). How the split is held: Facts vs C spellings.

The table check is rev 0's shape, now over the kit's file (`memfn/tests/check_targets.sh`), run at
`make` (warns), `make strict` (fails) and in the new section `make test-memfn-targets` (fails), with one
additions: the kit's own host `#if` chain is held to the guard column under four preprocessor targets,
and every facts field must be a token list (no emitter text).
Its control (gcc's whole `-dM` set at the family floor plus each need, against `-march=<name>`) is
ADOPTED. The entries are checked against the design's rows as literals; the compile cells are rev 0's,
fed by the kit's texts: 9 of 9 ran, 40,602 answer checks each, 0 bad.

K0 moves NO emitted byte: no file under `src/`, `cli/` or `lib/` changed (`git diff de178e0dd HEAD --
src cli lib` is empty), nothing outside the kit calls the new entries (0 grep hits under `src/`, `cli/`,
`lib/`), and `make test-codegen` (the identity gate) ran green on the lane tip (Validation below). No
abi event. Six sabotage rows S2975-S2980 on a new mech arm `memfntargets`; each was planted by hand in
a scratch copy and went red.

## The table

THE FACTS, `memfn/src/targets.def`, an X-macro in options.def's idiom (the same rows rev 0's withdrawn
U1 checked, commit 171bdb343):

| family | default list |
|---|---|
| `x86_64` | `x86-64` (grows at U5 only, on a bench verdict) |
| `aarch64` | `armv8-a` |

| target | family | needs | features |
|---|---|---|---|
| `generic` | none (the portable target) | none | none |
| `x86-64` | x86_64 | `sse2` | `sse2` |
| `x86-64-v3` | x86_64 | `avx2,bmi,bmi2,cx16,f16c,fma,lzcnt,movbe,popcnt,sahf,sse4.1,sse4.2,ssse3,xsave` | the same |
| `armv8-a` | aarch64 | none (NEON is the baseline) | `neon` |

THE C SPELLINGS, `memfn/src/targets_c.def` (one row per family) and targets.c's C section:

| family | C guard condition (the guard's `#error` refuses a compile without it) |
|---|---|
| `x86_64` | `defined(__x86_64__) && !defined(__ILP32__)` |
| `aarch64` | `defined(__aarch64__)` |

The region pair is spelled from each target's needs column (`MF_NEEDS`, defined in targets.c's C
section to the pragma pair, in the facts section to the bare list). Both texts are string literals
assembled at compile time, so no entry builds text. The guard's message quotes its condition rather
than the family's name: the name is a fact and the condition a spelling, and string concatenation
cannot join two tables at compile time without repeating one in the other. The HOST default comes from
targets_c.def's `MF_TARGET_HOST` block, an `#if` chain at file scope on the kit's own compile (the kit
is compiled into libpcrec, so its host is pcrec's; it is C because the kit is, and is never emitted); no
function contains an `#if` (D155). A host with no family row gets the portable target's name as its
default list.

## Facts vs C spellings

- The structs: `mf_target` {name, family, needs, features} and `mf_family` {name, defaults} carry
  facts only. The C spellings are separate structs, `mf_target_c` {region_open, region_close} and
  `mf_family_c` {guard}, in tables parallel to the facts' and reached from a fact row by
  `mf_target_c_of(t)` / `mf_family_c_of(f)` (NULL for any pointer that is not a row). Every
  parse/listing/default/portable entry answers from the facts tables and never reads a C table. A Rust
  emitter would add its own spelling table and `_rust_of` pair beside the C one, from the same facts.
- `needs` is the one new fact the split surfaced: the region's attribute list had been a C-shaped column;
  as a fact it is "what a part for this target must enable above its family's portable compile", and
  the region is its C spelling. The rule tying it to features loosened from "equal" to "a subset"
  (armv8-a: needs none, features `neon`).
- THE CHECK (memfn/tests/check_targets.sh, part 1 of the section): every field of every facts row must
  be a token list, `[a-z0-9][a-z0-9._-]*` comma-separated or empty (as respelled by k0fix), which C (or Rust) text
  never is (a `(`, `#`, quote, a leading `_`, `=` or blank fails it); targets.def must hold no preprocessor directive; and
  targets_c.def must spell every family exactly once and no other. Failing directions, hand-checked
  through `TARGETS_DEF`/`TARGETS_C_DEF`: `__ARM_NEON` as armv8-a's feature, `arch=x86-64` as x86-64's
  need, aarch64's spelling row removed; each red.
- THE SABOTAGE ROW: S2980 plants that first direction (a facts row carries a C macro name; armv8-a is
  not the host family, so the compiler control skips it and only the token-list rule and the entries'
  literal see it): red, 2 FAIL.

Lane choices inside the table, answer-free: the family `baseline` column of rev 0 is DROPPED (no reader;
D77; the default list's members are checked to be of their family instead); the row ids are kit-private.

## The entries

`memfn/include/memfn.h`, section "the kit's CPU TARGET TABLE" (all `MF_NS`, exported as `pcrec_mf_*`):

| entry | answers |
|---|---|
| `const mf_target_c *mf_target_c_of(const mf_target *t)`, `const mf_family_c *mf_family_c_of(const mf_family *f)` | the C spellings of a row (region pair; family guard), or NULL for a pointer that is not a row |
| `const mf_target *mf_target_parse(const char *tok, size_t len, char *err, size_t n)` | the row the `len` bytes name, or NULL with the kit's refusal text (`unknown CPU target 'x86-64-v4' (known: generic x86-64 x86-64-v3 aarch64)`; `an empty CPU target (...)`) |
| `const mf_family *mf_family_parse(const char *tok, size_t len, char *err, size_t n)` | the same for a family token |
| `const mf_target *mf_targets(size_t *n)`, `const mf_family *mf_families(size_t *n)` | the listings, in table order (the population the checks count) |
| `const mf_target *mf_portable_target(void)` | the one familyless target (`generic`) |
| `const char *mf_host_defaults(void)` | the host family's default list (`x86-64` on this box, the default of the `x86_64` family) |

A row's fields: `mf_target` {name (canonical), family (pointer, NULL for the portable target), needs,
features}; `mf_family` {name, defaults (comma-separated canonical tokens)}. So "the default list for a
family" and "the portable token" are fields of the parsed row, and "the region and guard text for a
token" is `mf_target_c_of(t)->region_open` and `mf_family_c_of(t->family)->guard`.

Lane choices, answer-free unless noted:
- CANONICAL FORM: a token matches ASCII-case-blind with `_` read as `-` (`X86_64`, `x86_64_V3`,
  `AArch64` parse; the canonical form is the row's name). This is the one place a caller sees a choice:
  `x86_64` is what `uname -m` and the GNU triplets print. `arm64` (the Mac's `uname -m`) is NOT an alias;
  an alias column waits for a need. The table check asserts no two rows collide under this rule.
- LENGTH-BOUNDED tokens, so P1 can parse list members in place.
- The refusal text lists the known tokens and names no pcrec option (pcrec prints it after its own lead).
- The run-time CPU PREDICATE text is deferred to U4: its shape (an expression with
  `__builtin_cpu_init()` inside, or init and test apart; target_seam.md §6.2's leaning) is the U4
  controller's to fix, and nothing calls it before U4 (D77). Adding it then adds a field to `mf_target_c`
  (the spelling; the fact it spells is the target's features, already present).
- No `MF_SITE_ABI`/`MF_VOCAB`/`MF_CLASS_V` move: a new section, no existing struct, field or op changed
  (lane simdset's precedent, `memfn/include/CLAUDE.md`).

## Table check (vs gcc -march) and its control

`memfn/tests/check_targets.sh` reads targets.def and targets_c.def through `gcc -E` (the same X-macro
rows the kit compiles) and asserts:
1. THE COMPILER CONTROL, ADOPTED (units.md §5's lane choice): for each target of the host's family with
   needs, `gcc -march=x86-64 -mno-sse -m<each need>` defines exactly the macros `gcc -march=<name>`
   defines, the whole `-dM` output. Reasons: the control is outside the table (the compiler), and a
   whole-set compare is not a name-keyed filter (a chosen macro list could not have found `sahf`, R2);
   gcc whatever CC is, because clang's whole set differs by CPU-name macros alone (`__k8`, rev 0's
   measurement); the floor is the check's own column so `sse2` is a real comparison. At `make` a
   mismatch WARNS (R5-Q1), `make strict` and the section FAIL. A target of another family is SKIPPED and
   counted (today: armv8-a).
2. Structure: floors of 2 families and 4 targets (literals from the design); names distinct under the
   parser's matching rule; every target's family exists; exactly one familyless target, with no needs
   and no features; needs and features sorted, unrepeated, needs a subset of features; each default
   list non-empty, unrepeated, every member a target of that family. And the split's rule: every facts
   field a token list, no directive in targets.def, one C spelling row per family (Facts vs C
   split).
3. NEW, THE HOST CHAIN vs THE GUARDS: in each of four preprocessor cells (gcc as is, `-m32`, `-mx32`,
   clang `--target=aarch64-linux-gnu`) the chain names the family whose guard holds, or none where none
   does, and at most one guard holds. Its reason: the host chain is a second spelling of the guard
   predicates (the one `#if` K0 needs), and a drift between them would pick the wrong host default.

Today: `ok: 2 families, 4 targets, 2 compared against gcc -march, 1 skipped (another family or no
needs), host MF_FAM_X86_64, 4 host cells (0 skipped)`. Failing directions, hand-checked through
`TARGETS_DEF` on scratch copies: `sahf` dropped from both columns (`> #define __LAHF_SAHF__ 1`), the
guard without `!defined(__ILP32__)` (host cell gcc-mx32 red), an armv8-a row moved into x86_64 (its
family's default list then names a target of another family). Exit 0 ok, 1 mismatch, 2 could not run.

## Compile cells

`tests/memfn/run_targets.sh` part 3 (rev 0's harness; `tests/memfn/targets_check.c --fixture` now
writes the fixture from the KIT's guard and region texts): a family guard, a generic finder and two
`#if`-free intrinsic finders, each in its target's region.
- 9 of 9 cells ran (gcc 15.2: default, `-march=native`, `-march=x86-64-v4`, `-mno-sse2`,
  `-mgeneral-regs-only`, `-march=x86-64-v2`; clang 21.1.8: default, native, x86-64-v4), each `checks 40602
  bad 0 v3 1` against a naive finder written in the harness. RAN floor 6 gcc cells.
- objdump at default `-march`: `fx_w32` 3 ymm, `fx_w16` 7 xmm, `fx_generic` 0 ymm.
- The family guard refused `gcc -m32` and `clang --target=aarch64-linux-gnu` with its own message.

Part 2, the entries against literals: 42 PASS lines (floor 42, exact; one host row on every host),
including the canonical forms above, refusals (`x86-64-v4`, a prefix `x86`, a trailing blank, a token
plus a byte, empty tokens, `riscv`, `generic` and `x86-64-v3` as families), the length bound
(`x86-64-v3` with len 6 parses as `x86-64`), a short and a zero error buffer, each family's default list
and C guard, every row's C spelling present (and none for a copy of a row or NULL), the portable target,
and the host default list against `uname -m` (not the kit's `#if`).

## Spec and contract hunks

- docs/spec/: NONE in K0, by D80's own test: nothing K0 adds is caller-observable. No pcrec entry,
  flag, stamp, option, limit, diagnostic or emitted byte changed; the kit's entries are reached only
  through memfn.h, which is pcrec's internal seam, not the library contract, and no docs/spec/ file
  covers the kit's exports (`pcrec_mf_*` appear in none). units.md §4 assigns K0 no spec hunk: P1
  carries cli.md (the two options and refusal at parse), the `pcrec_options` field, rxt_format.md (the
  directive) and tuning.md §2.43¶1/¶3; U3 and U4 carry the rest. The one builder-observable change, a
  `make` warning when the table check fails (and `make strict` failing on it), is stated in the
  Makefile beside the rule; `make strict` still writes nothing.
- The kit's contract hunk is memfn.h's new section (the header is "the contract of record").
- The D146 replacement addendum (units.md §4's draft) is NOT filed here: R-36 says main files it with
  K0's landing.
- memfn/docs/responses.md and journal.md are the kit session's (single writer); this lane did not
  write them.

## Sabotage

S2975-S2980, the kit's next free ids (S2970-S2974 are S2e's recompute plants; no S2975+ anywhere in the
tree or the worktrees). A new mech arm `memfntargets` (tests/mech/run_sabotage_matrix.sh: vocabulary
entry and case; it runs `tests/memfn/run_targets.sh` linking the sabotaged tree's own libpcrec.a),
registered before its rows. `VALIDATE_ONLY=1`: 6 definitions valid; the anchor tripwire
(`scripts/m6read_check_sab_anchors.py`): all 1202 anchor sites resolve. Each row was planted by hand in
a scratch copy (memfn/ and the section's scripts copied, the planted targets.o swapped into a copy of
build/libpcrec.a) and the section run, ALL SIX AGAIN after the facts/spellings split (the figures
below are that second run; S2976's and S2978's anchors moved with the split, S2978's into
targets_c.def):

| row | plant | detector | hand result |
|---|---|---|---|
| S2975 | the 32-byte row drops `sahf` from both columns | the compiler control (part 1); the entries' literal | red, 2 FAIL |
| S2976 | x86-64's default list grows to `x86-64,x86-64-v3` (U5 early; structurally valid) | the entries' literal family row and host row (part 2) | red, 1 FAIL |
| S2977 | the region drops `#pragma GCC target` | the entries' region row; the compile cells (the v3 part no longer compiles at gcc's default) | red, 7 FAIL |
| S2978 | the x86-64 C guard (targets_c.def) admits ILP32 | the host cell gcc-mx32 (part 1); the entries' guard row | red, 2 FAIL |
| S2979 | `tok_names` accepts a prefix | the prefix refusal (part 2) | red, 1 FAIL |
| S2980 | a facts row carries C text: armv8-a's feature becomes `__ARM_NEON` | the token-list rule (part 1); the entries' literal | red, 2 FAIL |

C4: the rows' anchors carry the table's own text, so `tests/memfn/c4_allowlist.tsv` gains seven counted
rows (S2975 class 1: 2; S2976 classes 1/6: 1/2; S2978 classes 2/6: 2/2; S2980 classes 1/2: 2/1), with
S725/S726's reason; the
rows' prose is worded arch-free (S2975's file and id renamed for it). C4 does not apply to the kit
itself (memfn/ is exempt by design) nor to `tests/memfn/` (exempt), CONFIRMED: `make test-memfn-arch`
green with no row for targets.def, targets_c.def, targets.c, check_targets.sh, run_targets.sh or targets_check.c.

## Gate jobs

Written under `/var/tmp/pcrec-pcrec/scratch/memfn/k0/jobs/` (sourcing `common.sh`, modelled on s2e's
480-486), each dry-run clean, NOT queued (the brief). 450-453 were free in the queue log. All gate on
`/var/tmp/pcrec-pcrec/scratch/memfn/s2a/jobs/hold.sh` (the evening hold) and chain by `after`:
- `450-kit-k0-strict` — `make -j16; make strict` (expect none: the rc is make strict's).
- `451-kit-k0-sections` — test-memfn-targets, test-codegen, test-registry, test-memfn-finder,
  test-memfn-g2, test-memfn-link, test-memfn-arch, test-spec-history, test-claudemd-size, test-ci-shards
  (expect sections=10 lines).
- `452-kit-k0-test` — make test via `scripts/perfrun --label k0` (expect steps=1 lines).
- `453-kit-k0-mech` — S2975-S2980 for real (expect rows=6 lines; the trailer grep requires 0 unexpected,
  undetected, unreached, anomalies). `rows_for.sh` over K0's other changed files names S2968, S522 and
  S526, which read memfn.h, the Makefile or c4_allowlist.tsv at lines K0 did not change: left to the
  merge's tier.
No `expect last=` matcher is used (every population is `lines=`).

OWED: kit-k0-strict, kit-k0-sections, kit-k0-test, kit-k0-mech (their verdicts in each job's run dir;
the gate jobs run on the split tip; 452's make log at `/var/tmp/pcrec-pcrec/scratch/memfn/k0/test/test.make.log`, 453's at
`/var/tmp/pcrec-pcrec/scratch/memfn/k0/mech/mech.log`).

Validation run in the lane (niced, no timing window open; box held by queue job 213-altcatch-axes, not
a timing job), on the lane tip AFTER the facts/spellings split: `make` (the stamp: `targets-check: ok
...`), `make strict` green ("the kit's target table check passes"), `make test-memfn-targets` 14 passed
0 failed (entries 42/42), `make test-memfn-arch` 17/0, `make test-memfn-link` 11/0 (C15: the eight new
`pcrec_mf_*` symbols; C16: the three new PROVENANCE rows), `make test-claudemd-size`, `make
test-spec-history`, `make test-ci-shards` green, `make test-codegen` green (`light3_test-codegen.log`).
Before the split the same set was green too, after one fix: test-codegen's first run was red on ONE
reader the lane had missed ([TT-9] requires every `run_*.sh` in `tests/lib/san_scripts.txt` or
`san_excluded.txt`, so `tests/memfn/run_targets.sh` gained an OWN-TIER exclusion row beside its memfn
siblings). Logs: `/var/tmp/pcrec-pcrec/scratch/memfn/k0/light3_*.log` (and the earlier `light_*.log`).

## STATE AT HANDOFF

Delivered at the branch tip (`lane/memfn-k0`); no rulings file was named. OWED, not queued by the lane:
kit-k0-strict, kit-k0-sections, kit-k0-test, kit-k0-mech (job files
`/var/tmp/pcrec-pcrec/scratch/memfn/k0/jobs/450-kit-k0-strict`, `451-kit-k0-sections`, `452-kit-k0-test`,
`453-kit-k0-mech`, each dry-run clean). A fresh agent reads their verdicts; nothing else is open in the
lane.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| tokens generic, x86-64, x86-64-v3, aarch64 | yes, targets.def |
| families with default lists and the host default | yes; host from the kit's own compile; no-family host -> the portable token |
| per token: family, sorted features (`sahf` in v3, R2) | yes |
| region text (open/close), additive list + clang pragma pair, not `arch=` | yes, a C spelling of the needs (`mf_target_c`); checked in the entries and the compile cells |
| family guard text | yes, a C spelling (`mf_family_c_of(t->family)->guard`) |
| run-time CPU predicate text | DEFERRED to U4, said so (The entries) |
| entries: parse target, parse family (canonical or the kit's named refusal) | yes, `mf_target_parse`, `mf_family_parse` |
| entries: default list for a family / for the host; the portable token; region and guard for a token | yes: `mf_family.defaults`, `mf_host_defaults`, `mf_portable_target`; `mf_target_c_of`, `mf_family_c_of` |
| NOT the dispatch step; no pcrec caller | held: x86-64's list is `x86-64`; 0 callers under src/cli/lib |
| declared row table, first match, no if-chains | yes (the X-macro table; the parsers walk it first-match) |
| MF_NS symbols, internals static, only `pcrec_` exports (C15) | yes; test-memfn-link green |
| SPDX + provenance headers, PROVENANCE.md rows (C16) | yes, two rows |
| D155: no `#if` in a function that does work | yes (the host chain is file-scope in the .def) |
| D80 spec hunk | none needed; argued in Spec and contract hunks |
| K0 moves no emitted byte, proven | no src/cli/lib diff, 0 callers, test-codegen green; no abi event |
| table check against gcc `-march`; control adopted or refused with reason | ADOPTED, reasons in Table check |
| the check can FAIL: sabotage rows from S2975 | S2975-S2980, each hand-planted red; arm memfntargets |
| (ruling 2026-11-07) facts apart from C spellings, held by a check | yes: targets.def / targets_c.def + separate structs and `_c_of` entries; the token-list rule + S2980 |
| new section hooked where rev 0's was; C4 does not apply, confirmed | test-memfn-targets in TEST_SECTIONS + shards.tsv; C4 confirmed |
| no make test / mech run by the lane; light checks only | yes |
| jobs 450-453 (strict, sections, test, mech), dry-run, owed | yes, OWED |
| report, history index line, CLAUDE.md of every directory with new files | yes (memfn/, memfn/src/, memfn/include/, memfn/tests/, tests/memfn/ + NOTES.md) |
| journal nothing | nothing journaled |

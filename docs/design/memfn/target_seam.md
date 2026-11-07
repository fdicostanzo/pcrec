# The target seam: per-target code paths between pcrec and the kit

STATUS: PROPOSED rev 1 (lane xarchrev1, 2026-11-07, off main 6fc4b6912), over rev 0 (lane
xarchseam). Rev 1 applies the ruling of review `docs/dev/reviews/2026-11-07-r1-xarch.md`. Design
only: there is no build go, and nothing under `src/`, `cli/`, `lib/` or `memfn/` changes. Owner row:
`[XARCH-DEV]`. The kit asked for "the format of single-arch code paths" so it can shape its SIMD
forms now. §3 is that format, and it holds as rev 0 wrote it, with one correction: the attribute
spelling in §6.

## R1. What rev 1 changed (read first)

| finding | change | § |
|---|---|---|
| F1 | the target list is the single axis; a first-match table maps (flag, list) to the set; `generic` is separate from each family's baseline; the build-time sentence is restored | §0, §2 |
| F2 | D188 add. 2 folded in: family rows, the family is an input of every check, the family guard is pcrec's `#error` | §0, §2, §7, §8 |
| F3 | additive ISA list plus a clang pragma pair, probed at 12 compile cells | §6.1 |
| F4 | stems are `<prefix>__<tag>`; the bare stem belongs to the controller | §5 |
| F5 | one classification table for the artifact surface, plus a spec inventory | §5 |
| F6 | a CPU variant IS a compound part with a CPU predicate; the elision fact; addendum text PROPOSED | §6.2, §6.4 |
| F7 | per-call probe priced against an iterator field; continuation rule; D165 item 5 argued | §6.2 |
| F8 | the non-document remainder of the seam is listed | §3 |
| F9 | the gate field, the reader list, `target` as a form-entry column | §4 |
| F10 | picked: the kit's include stays in its text, inside the region | §3 |
| F11 | one primary column (the target name) with derived columns and a table check; the family-qualified admission rule; `ms` keyed by class | §2, §3 |
| F12 | `__builtin_cpu_init()`; the caveats are restored | §6.2 |
| F13 | the dispatch and target-code checks can fail; counted RAN floors | §8 |
| F14 | the controls in §7/§9 are corrected | §7, §9 |
| F15 | test time and benefit triggers | §9 |
| F16 | there is no dedicated stamp event: the stamp rides along | §7 |
| F17 | ruling bookkeeping: proposed addenda named | §0, §11 |
| F18 | cites re-taken at 6fc4b6912, with kit-branch drift noted | §4, §5 |

## 0. Ruled inputs

Quoted:
- **D188 add. 1** (owner, 2026-11-06): "A code path is a per-target VARIANT, planned and priced for
  its declared target. One artifact may hold several variants (generic plus SIMD) as
  target-attributed functions behind a once-per-process CPU dispatch. The artifact's target set is
  an explicit caller-given LIST, with a declared, stamped default when none is given, never
  assumed."
- **D188 add. 2**, owner text: "If they provided the rx and 'use simd' then compiled on a cpu
  family, it should build for that family. The kit doesn't have to spit out all possible cpu
  families. The demarcation is a 'cpu family' is the largest scope of an artifact." Denied (owner,
  same day): a single multi-family file. Agreed workaround: one artifact per family, and the user's
  build selects among them.
- **D188 add. 2, the manager's reading** (filed as "not ruled detail"): the variants are the
  family's declared, stamped default list; a cross-compile names the family as one word; the file
  carries one family guard that refuses compilation under another family.
- **[XARCH-DEV] RULED**: "A variant is a complete matcher planned and priced for one target. Build
  time: pcrec emits the build target's variant. Run time: one artifact holds 2-3 variants (generic +
  1-2 SIMD) as target-attributed functions, a once-per-process CPU dispatch entry, and each variant's
  own entry."
- **D155 add. 5**: "each ISA level is a separate target-attributed PART [...] The controller works
  out which level runs [...] A one-shot search pays the feature check per call [...] The iterator
  keeps the decision in its caller-held state (D165) [...] The decision is NEVER an artifact static."

Cited, not quoted:
- pcrec sends facts and never methods (D146, D157's Why, manifesto principle 7).
- Seams are designed in planning/emitting-split terms; do not split now; write SIMD forms
  emitter-shaped (Frank 2026-11-06, recorded in plan [IR-FORM] member (4)).
- Every seam is a document (manifesto principle 9).

Ruled by the manager on review r1 (verbatim in the review's RULING block):
- F1 is the single list axis.
- F2(c)/(d): the family is an input of every check; the guard is an `#error` with one owner.
- F6: a CPU variant is a compound part.
- F16: the stamp rides along.

## 1. Goals

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | the kit writes SIMD forms now, with no wait for the dispatch build | kit | a form's text compiles inside a target region at every §6.1 cell with zero CPU `#if` lines (the family guard is exempt by name, §2), counted by the §8 compile cells, not by grep alone |
| G2 | the default emits today's bytes | every caller | `emit_sweep.py --ref` over the corpus at default flags (`{generic}`): 0 moved, apart from the ride-along stamp event's declared moves (§7) |
| G2b | `-fmemfn-simd` keeps today's behaviour on x86-64 | opt-in callers | at the family default list's first value (`x86-64` alone), the object `.text` at the consumer's default `-march` equals today's (§7) |
| G3 | several variants coexist in one artifact | callers shipping to mixed CPUs of one family | `{x86-64, x86-64-v3}` links as one `.o` with no duplicate symbol, and the §8 dispatch cells pass |
| G4 | the seam survives a text round trip | the future planner/emitter split | every §3 field is a value; the non-document remainder is listed (§3) |

Priority: G2 > G2b > G1 > G4 > G3.

Non-goals:
- pricing (D188's half, unchanged);
- splitting the kit;
- a multi-family file (denied, D188 add. 2).

## 2. The target table and the list (pcrec-owned; one home)

pcrec owns ONE target table. Its primary column is the target NAME. Everything else is derived from
the name, or declared beside it and checked against it. A table check at `make` (not at test time)
asserts four things:
- every target's additive attribute list enables exactly the ISA macros that `gcc -march=<name>
  -dM -E` defines (the independent control is the compiler, not the table);
- the probe string is the name itself;
- every family row names exactly one baseline target;
- every target's family exists.

**Family rows** (the largest scope of an artifact, D188 add. 2):

| family | guard predicate (pcrec's file-scope `#error`, its ONE owner) | baseline target | declared default list (`-fmemfn-simd`) |
|---|---|---|---|
| `x86-64` | `defined(__x86_64__) && !defined(__ILP32__)` | `x86-64` | first value `x86-64`; becomes `x86-64,x86-64-v3` at the dispatch build step (§7, Q1) |
| `aarch64` | `defined(__aarch64__)` | `aarch64` | `aarch64` (no kit level yet; born with the first aarch64 row) |

**Target rows**:

| name (primary; also the stem tag and the probe string) | family | region attribute (derived: additive ISA list, §6.1) | features handed to the kit (derived) |
|---|---|---|---|
| `generic` | none (family-free: no guard, no region, no SIMD) | none | empty |
| `x86-64` | x86-64 | `sse2` | `sse2` |
| `x86-64-v3` | x86-64 | `avx2,bmi,bmi2,fma,lzcnt,movbe,popcnt,f16c,xsave,sse4.2,ssse3,sse4.1,cx16` | the same list |
| `aarch64` | aarch64 | none (NEON is baseline) | `neon` |

`x86-64-v2` and `x86-64-v4` are NOT rows. The kit has two x86 levels (w16, w32), so those targets
cannot plan differently (MEAS-5). A row is born with the first kit level that needs it, by D77.

**The list: one axis, first match** (the flag is an alias, never a second gate):

| # | `-f[no-]memfn-simd` | `--targets` list given | target set |
|---|---|---|---|
| 1 | `-fno-memfn-simd` (also given) | any | `{generic}` (the deny wins, as tuning.md §2.43 rules today) |
| 2 | any | yes | the given list. Every member must be of ONE family, or the compile is refused (D188 add. 2) |
| 3 | `-fmemfn-simd` | no | the declared default list of the family row, for the family named by `--family`, else the family of the host pcrec runs on |
| 4 | neither | no | `{generic}` (the default; today's bytes) |

**Build time** ([XARCH-DEV]): "pcrec emits the build target's variant" is a one-member list naming
that target: no controller, no probe, no libgcc. **Host resolution** is the ONLY place the host
enters (row 3). Every check and pin passes `--family` explicitly (§8).

The list's spelling is owed at the build, as one CLI option, one `pcrec_options` field and one
`.rxt` directive. It is placed with [EMIT-ENTRIES], which owns the entry set. The new stamp
`<PREFIX>_TARGETS` carries the family and the members, e.g. `"x86-64:x86-64,x86-64-v3"`.

`ms` per target is keyed by measure_store's `class` (e.g. `x86_64-avx2/zen4`). A target row
therefore gets one more derived column, its class prefix. When a target has no set, it takes the
[MEASURE-SET] (b) fallback rows (microarch -> ISA level -> family -> generic). That is one key, not
a second spelling of target identity (SEAM2-1).

## 3. What crosses the seam (per art)

The unit is ONE ART per (part, target); §6.2 explains why. The kit never learns that other targets
exist.

**pcrec -> kit (facts):**

| field | value | today |
|---|---|---|
| `target.features` | sorted feature tokens, derived from the target row; empty = generic | implied by `MF_P_PORTABLE_ONLY` + the consumer's macros |
| `target.family` | `x86-64` / `aarch64` / none | implied by `__x86_64__` |
| `prefix` | the part's stem (§5); it carries the target's name, so no separate `tag` field crosses | `prefix` |
| `ms` | the measurement set for this target (D188, per variant; §2) | `ms` |
| site facts, hooks, denies | unchanged, identical in every variant | unchanged |

**Admission** (kit-owned, in the kit's own `levels.def`):
- a level is admitted iff `level.family == target.family && level.needs ⊆ target.features`;
- the family test is needed because feature tokens are not family-unique (`aes`, `sha`);
- the `guard` column retires and `needs` replaces it;
- the family-predicate half of today's guard moves to pcrec's family row (one owner, F2(d)).

**kit -> pcrec (facts + text):**

| field | content |
|---|---|
| text | C valid inside a region compiled for the art's target: no CPU/ISA `#if`, no CPU checks; the level's compiler header (`immintrin.h`) is included IN the text, unguarded |
| MEMFN_FORMS / RUN_WORDS / MEMFN_LIBC | the art's stamp values, one per art (§5) |
| bracket marks | the target-dependent byte ranges (today's `simd_open`/`simd_close`), as an offset pair |
| `target_dependent` (the ELISION FACT) | true iff the art's text differs from what the `generic` art would render, i.e. some admitted level rendered (today: some rung chosen) |

F10 is settled by picking the include-in-text form. The kit's `#include <immintrin.h>` stays
inside its text, and so inside the region. This adds no new fact and no new `MF_INC_*` bit. Include
guards make the second region's include a no-op. Probed: gcc 15.2 and clang 21.1.8, each at the
three §6.1 flag cells, answers equal.

**The non-document remainder (G4, F8).** These callbacks cross today, and each becomes a
placeholder or a value when the seam is serialized ([IR-FORM] member (4) owns that):
- the sink's function members (`simd_open`/`simd_close` among ~11);
- `mf_hooks`'s `on_cand`, `member`, `table_name`, `fn_name`, `note`, `note_tag`.

The text-injecting ones (`table_name`, `fn_name`, `member`) become name placeholders. The rest
become returned values. Rev 0's "the one callback" was wrong.

## 4. Today's CPU conditionals, and what each becomes

The counts are from rev 0, re-held at 6fc4b6912 (memfn/ is unchanged from aeede1d16). Every
emitted CPU guard comes from `memfn/src/levels.def:41-46`.

| site | today | becomes |
|---|---|---|
| levels.def `guard` | the predicate (family + ISA macro) | `needs` (feature tokens), kit-private. The family half moves to pcrec's family row |
| ofsskip.c `fn_level_block` (568-575), vany.c `vany_level` (157, 178) | `#if <guard>`, `#include`, helper, `#endif` | `#include`, helper |
| ofsskip.c `fn_selector` (590-611), vany.c `vany_selector` (184-198) | the `#if`/`#elif` chain | ONE call to the top admitted rung, or to `__body` when none is admitted (`nr == 0`, today's SIMD-off text) |
| vany.c `mf_kernel_find_any` (210-215) | a caller-passed level mask | the mask is derived from `target.features` |
| SIMD admission: gate class `FLD_policy` / `MF_CLASS(PORTABLE)` (fields.def, gate.c, the `[FLD_policy]` column of 10 kit rows) | the policy bit gates SIMD rows | a gate field the walk reads, `needs ⊆ features` (the kit names it). `nr == 0` then holds because no SIMD row is admitted, not because rung[0] is empty (F9: `fn_rungs` always seats a chosen PREFIX row) |

**Retiring `MF_P_PORTABLE_ONLY` has these readers** (grep at 6fc4b6912; each moves in the same
change):
- memfn/include/memfn.h, lib/pcrec.h, src/core/internal.h, src/gen/memfn_stamps.c,
  src/gen/memfn_sites.h;
- memfn/src/{gate,fields.def,vrun,formhash}.c;
- memfn/tests/g2/*_gen.c;
- tests/memfn/{proven_check,arm_fixtures,proof_check}.c and run_proof.sh;
- sabotages S722, S1224.

**The kit must hear this (in flight):** lane/memfn-s2e's form-hash entry table (formhash.c,
5b6cf41aa) keys every row by the policy word. Under D188's per-variant pricing it needs a `target`
column, so that timed text and shipped text are compiled for the same target.

The rung chain survives inside a variant. A w32 helper whose range is too short falls to w16 (a
length test, ofsskip.c:686-687), and both rungs are valid at `x86-64-v3`.

**D188 fact (b)** ("the build compiled it") is PROPOSED to read: the art's `MEMFN_FORMS` value is
emitted INSIDE its region. A compiler that ignored the region would still compile the text (G1
cells catch that), but "in the list" is not proof by itself (RULE2-7). span_cards rev 1.5 §2.7/J6
carries the same restatement and moves with it.

## 5. Names, and the artifact surface

**Stems (F4).** A part for target `T` has the stem `<prefix>__<T'>`, where `T'` is the target name
with `-` turned into `_` (`rx__x86_64_v3`). Caller prefixes already refuse `__` (cli.md §1.6¶2,
row 1), so no new reservation is needed. The roles and target names must stay disjoint, and the
table check asserts it.

The bare stem `<prefix>` belongs to the controller, or to the lone part in a one-member list. A
one-member list therefore keeps today's names, and G2/G2b hold for it.

The §3 premise (every kit file-scope name is built from pcrec strings) re-holds, with these
exceptions:
- block-scope `rq_set`;
- the test-only `mf_tbl`, plus `mf_fn` on the kit branch;
- the external-linkage, harness-only `mf_reach_table`.

Kit-branch drift: runcmp.c's word load is :533-535 on main and :542-544 on 5b6cf41aa.

**Surface classification (F5).** Every emitted item falls in one class:

| class | items | rule |
|---|---|---|
| shared, once per file | `rx_iter`, the ABI header block, `PCREC_*` macros, `PCREC_FEATURE_*`, `--emit-main`'s `main` | written once, before any region |
| per artifact | `<PREFIX>_TARGETS`, the family guard, `.abi`/`.flags` | once |
| controller (the bare stem) | public entries, `rx_info`, `<PREFIX>_FRAME`/size macros = MAX over parts, `<PREFIX>_MEMFN_LIBC` = union | the caller allocates by the bare stem |
| per part | the part's entries and `__`-stem stamps (`MEMFN_FORMS`, `RUN_WORDS`, `MEASURES`, `SIMD_GUARDED_BYTES` reinterpreted as "bytes inside this part's region", from the bracket marks) | each part's own values |
| per-prefix types | `rx_buffers` | typedef'd ONCE at the bare stem; parts use the controller's type (no forwarding cast) |

`rx_info` reports the controller. Whether it also lists the parts is Q2, at [IFACE-PUSH] /
[RXINFO-REMODEL].

**Spec inventory, built in the same change (D80).** The build unit moves these sections:
- match_api §1¶2, §3.x (entries), §5.3 (no static; the libgcc probe), §6.3.2, §6.3.10¶3-4/¶8-9
  (stamps), §6.3.12, §10.7 (freestanding/libgcc: "allowed, guarded and stated", D155 Q-R9-8);
- cli.md §1.6¶2 (stems), §1.16¶5;
- tuning.md §2.43¶2-4 (the flag is an alias; "no ISA axis" becomes false; `test-memfn-simdfloor`
  loses its subject).

## 6. pcrec's half

### 6.1 Attributes: an additive region, two spellings (F3)

One region per target part:

```c
#if defined(__clang__)
#pragma clang attribute push (__attribute__((target("<attr>"))), apply_to = function)
#else
#pragma GCC push_options
#pragma GCC target("<attr>")
#endif
  ... the part's functions, kit text unchanged ...
#if defined(__clang__)
#pragma clang attribute pop
#else
#pragma GCC pop_options
#endif
```

`<attr>` is the target row's ADDITIVE list. It is never `arch=`: `arch=` replaces the TU's ISA set,
so file-scope always_inline callees (fortified `memcpy`, intrinsics) refuse to inline when the
consumer compiles above or beside the target. `#if defined(__clang__)` is a compiler-capability
test, the class §4 exempts, like today's `__has_attribute`. The kit writes no attribute.

**Probe (lane xarchrev1, scratch).**
- Subject: `(?i)cat -fmemfn-simd` as a v3 part (CPU `#if`s removed, the selector made one w32
  call), a `-fno-memfn-simd` generic part, and a dispatcher.
- Method: per cell, compile and link, then run 2,305,644 answer checks against an independent C
  oracle (a naive case-insensitive finder).

| compiler | `-march` | `arch=x86-64-v3` | additive pair |
|---|---|---|---|
| gcc 15.2 | default | compiles, 0 bad | compiles, 0 bad, 15 ymm |
| gcc 15.2 | native (Zen 4) | FAILS: `inlining failed ... 'memcpy': target specific option mismatch` | compiles, 0 bad |
| gcc 15.2 | x86-64-v4 | FAILS (same) | compiles, 0 bad |
| clang 21.1.8 | default | FAILS: 21 errors, `'_mm256_set1_epi8' requires target feature 'avx'` | compiles, 0 bad |
| clang 21.1.8 | native | compiles | compiles, 0 bad |
| clang 21.1.8 | x86-64-v4 | compiles | compiles, 0 bad; 10 `%k` mask-register uses |

The last cell is the stated consequence. Above its target, a part may carry the consumer's larger
ISA (clang put AVX-512 mask ops in the "v3" part), so "planned for its declared target" holds only
at or below the target. Such a build is safe only where the deployed CPUs have the consumer's
`-march`, the same rule as for any `-march` build. §8 adds the above-target cell.

The baseline `x86-64` region (`target("sse2")`) compiles under `-mno-sse2` and
`-mgeneral-regs-only`, and runs SSE2 there. Today's `__SSE2__` guard would fall to scalar instead.
That is correct for the declared target, but a kernel-style consumer that forbids vector registers
must use `{generic}` (the default). The spec says so.

### 6.2 Dispatch: a CPU variant is a compound part (F6, F7, F12)

Ruled (manager, F6): a CPU variant IS a compound part with a CPU predicate, selected by the existing
compound controller (D163; every exported entry is already a controller, compound_entries.md
rev 4). It is not a separate whole-artifact dispatcher. So:
- the controller's row table gains one predicate column, `cpu` (the target's probe). Variants ×
  subject parts compose as rows (`^\s+|\s+$` under `--features all` is parts × targets), never as
  nested dispatchers;
- **the elision fact**: an art whose `target_dependent` is false has NO variant. The controller row
  for that part names the generic art for every target, and the text is emitted once. About 99.5 %
  of patterns (22 of 4,624 distinct c-default artifacts differ at `-fmemfn-simd`, MEAS-9) therefore
  carry one copy and no probe;
- §8's dispatch cells are the controller's existing test shape, plus the `cpu` column.

**The probe per call (F7, priced).** The controller reads the CPU choice per call:

```c
if (!__builtin_cpu_supports("x86-64-v3")) { __builtin_cpu_init(); /* then re-test */ }
```

That is a load of libgcc's `__cpu_model`, a test and a branch: 0.44-0.59 ns per call on Linux x86
(linux_results.md). `__builtin_cpu_init()` runs only on the not-yet-true path. It is idempotent and
fixes the "answers 0 before libgcc's constructor" case (constructors, ifunc resolvers; F12;
isa_evaluation.md's caveats: unset before constructors run, and BELIEVED a per-`.so` copy).

The other option is to store the choice in `rx_iter`. That is a `PCREC_ITER_LAYOUT` 3 -> 4 event on
the SHARED block (it moves every artifact, against G2), or it takes the last free bit. **Leaning:
probe per call, no iterator field.** The choice is libgcc's process state, not an artifact static
(§5.3 holds).

**Continuation.** An `rx_iter` started by `rx_next` is continued only by `rx_next`. A part's own
`<stem>__<T'>_next` is a test entry, and mixing the two is undefined (match_api §3.8's
"another artifact's next" rule extends to parts). The probe's answer is constant per process after
init, so `rx_next` never switches parts mid-iteration.

**D165 item 5** ("no trampoline"). The controller IS the exported entry, and its parts stay `static`
(D88 add. 1), except the [XARCH-DEV]-ruled per-variant entries. Those are exported test entries,
and the controller never calls them through the export. A target-attributed part cannot inline into
a default caller, so each call pays one branch plus a direct call or tail-jump (objdump on rev 0's
shape: a tail-jump). That is a frame-free call, not a chain of exports. Acceptance is D165 item 5's
own named measurement (dense tiny matches, iterator vs the `_search` loop) at parity on a
two-variant artifact. A loss is a finding. On ELF, an ifunc would remove the branch, and that stays
pcrec's later choice.

**Platforms.** On Darwin, `__builtin_cpu_supports` answers 0 for every feature, so a Darwin x86-64
build of a multi-member list runs the baseline. On aarch64 there is no level yet. The table is
isa_evaluation.md's.

### 6.3 Requirements that move (RB-3, N-4, M-5)

requirements.md RB-3 ("select ISA only by predefined macros ... no CPU detection"), N-4 ("no
`__builtin_cpu_supports`"), M-5 and §1 item 5 are amended at the build:
- ISA is selected by the declared target;
- CPU detection lives only in pcrec's controller, never in kit text;
- the baseline vector tier still needs no `-m` flag (the `x86-64` region supplies `sse2`).

### 6.4 PROPOSED addendum text (for decisions.md at the go; not filed)

> **D155 addendum 6 / [MEMFN-RTDISPATCH] (PROPOSED):** add. 5's "each ISA level is a part" is
> realised as each TARGET is a part: a complete matcher planned for one target ([XARCH-DEV]),
> selected by the compound controller's `cpu` predicate. A part whose text does not depend on the
> target is not duplicated (the elision fact). The one-shot AND the iterator re-read libgcc's
> probe per call (no iterator field; the choice is never an artifact static). The FREQUENT /
> INFREQUENT site class and the per-site `freq` column (never built) are withdrawn. Item 6 /
> Q-R9-10 (the `#if` selector) and the C18 floor check lose their subject and retire with the
> `#if` arms. [MEMFN-RTDISPATCH]'s "per-site multiversioning" SHAPE is superseded; its 500 KB
> concern is met by elision.

> **D146 addendum (PROPOSED):** the target table (names, families, additive attributes, probe
> strings) is pcrec's: it names the artifact's code regions and the controller's predicate. The
> kit's ISA knowledge (levels, `needs`, forms) stays the kit's. pcrec hands the kit feature tokens
> as facts and reads no kit level.

## 7. Bytes: what stays, what moves

- **Default `{generic}`**: one art, bare stem, empty features, no region, no guard, no controller
  probe. The kit text is today's SIMD-off text. Check: `emit_sweep.py --ref <main before the build>`
  at default flags over all streams, expecting 0 moved. That is the true control, because rev 0's
  `--extra -fno-memfn-simd` arm is byte-equal to the default and is refused without a DIFFER_PINS
  floor (F14).
- **`-fmemfn-simd` at the first default list (`x86-64` alone)**: the source moves, because the
  `#if` arms go away and the family guard is added. The OBJECT does not move at the consumer's
  default `-march`. Probed on `(?i)cat`: today's artifact and the baseline-only form (`sse2` region)
  give byte-identical `.text`, 2618/224 both. The check is `emit_sweep.py` at `-fmemfn-simd
  --family x86-64` as the source-move arm, with its moves declared, plus a `.text` compare at
  default `-march` over the ~22 SIMD-reaching patterns (MEAS-3: the opposite arm is the meaningful
  one).
- **The dispatch step** changes the family row's default list to `x86-64,x86-64-v3`. That is a
  declared row change: stamped, an abi event of the SIMD-on axis, OFF by default.
- **`<PREFIX>_TARGETS` and the family guard** have no dedicated abi event (F16, ruled). They ride
  the first build step that moves bytes, using emit_sweep's declared-move mechanism.
- **Rev 0 §9.3 corrected (F2(e)).** A kit byte move under a target that is in a family's default list
  is an abi event for every SIMD-on artifact of that family, not only for artifacts that list it
  explicitly.
- **PLAN (PROBE-8).** D165's iterator buffer S is a max over the whole target table. A new form's
  state under a non-default target could therefore raise S for `{generic}` artifacts. Check at S's
  landing: derive S at `{generic}` and at the full table; if they differ, G2 gains an S carve-out.

## 8. Tests: each check can fail

Every check takes `--family` explicitly. The host is used only by one named cell that asserts
host resolution: row 3 of §2 picks the family `uname -m` names. Pins taken at `-fmemfn-simd` (tests/cli
MEMFN_FORMS `vrun@w32+w16`, tests/memfn row_floors/simd_accept, emit_sweep DIFFER_PINS) are taken
at `--family x86-64`, so a Mac `make test` reads the same pins (F2(c); CI is x86-64 only, and the
Mac is the population nobody counted).

| check | can fail because | independent control |
|---|---|---|
| per-part answers: every `.rxt` case through each part's own entry whose target the box's CPU has | a wrong part's answer | the corpus expectations / libpcre2 10.46, never another part |
| WHICH part ran: a test-only observable (the part's `MEMFN_FORMS` returned through a harness hook) plus a forced-probe lever that walks every row | a controller that always picks generic | the expected part from the harness's own cpuid read, not from the controller |
| target code: per-part instruction census (ymm > 0 in the v3 part's helpers, 0 in generic; counted) | a region that silently failed to apply | objdump of the built object |
| compile cells: default, `-march=native`, the above-target cell, clang (§6.1's matrix) | `arch=`-style failures, clang ignoring the pragma | the compiler |
| family guard: compile a `--family x86-64` artifact with `-m32` and with `--target=aarch64` clang | a silent or missing refusal | the `#error` must fire (rc != 0, message counted) |
| RAN floor: per box, the count of parts that RAN is a pin with a floor (dev box Zen 4: generic, x86-64, x86-64-v3; Zen 1 the same; Mac: generic, aarch64) | a box that skips everything and prints | the box's declared floor |

**Cost (F15).** Running every case per part multiplies `make test` (~11 min here, ~37-39 min CI,
~100 min Mac). Plan: generic plus the family's top part over the whole corpus, other parts over the
SIMD-reaching subset only (the elision fact names it). PLAN: measure the test time at the build.

**Spec-first tests (accepted).** A D27 author writes the contract tests at the build from this
rev's §2/§5/§6: which part runs, guard loudness, stems, max frames.

## 9. Cost, benefit and the first measurement (D77)

N parts cost N matchers for target-dependent arts only (the elision fact). The probe's real
`{generic, v3}` `(?i)cat` is text 6019 / data 672, against 2618 / 224 for today's single
`-fmemfn-simd` object: 2.3x text before elision of shared tables. That is ONE pattern and
UNMEASURED in general.

**First size measurement:**
- Setup: over the corpus at `-fmemfn-simd --family x86-64`, build each artifact as `{x86-64}` and
  as `{x86-64, x86-64-v3}` (real controllers and `rx_info`, not a stand-in).
- Report: the size ratio (text + data) as median / p95 / max, and the count of artifacts whose
  elision fact is false everywhere, read from `MEMFN_FORMS == "none"`, not from `.text` identity.
  VEX re-encoding makes `.text` identity read ~0 (F14).
- Scheduling: it is a heavy sweep, so it goes through the box queue. Trigger: [XARCH-DEV]'s go.
- Scope: this is size only. The row's named first job is separate: an M1-made set plus the count
  of disagreeing picks.

**Benefit (named before the go, D77).**
- The dispatch step needs a measured speed win of the v3 part over the baseline part on a
  SIMD-reaching pattern, as an official bench verdict (D144 add. 4).
- Without one, the family default stays `x86-64` alone, and multi-member lists remain
  caller-requested.

## 10. Standing questions

1. **Measurement regime.** Relevant to §6.1 and §9:
   - setup: gcc 15.2 and clang 21.1.8, Linux dev box (Zen 4), -O2;
   - §9 counts `.o` size;
   - §6.2's probe cost is latency per call (linux_results.md);
   - the official speed verdict is a bench run on the targeted box;
   - a different `-march` flips §6.1's `arch=` cells, which is why the additive form is chosen.
2. **Independent control.** Relevant. Every §8 check names a control outside the subject:
   - the compiler (`-dM -E`, objdump);
   - libgcc/cpuid in the harness;
   - the oracle;
   - emit_sweep's `--ref` build.
3. **What moves on regeneration.**
   - The target table: a row change moves the artifacts of that family's lists, and is an abi event
     of the SIMD-on axis.
   - A target's set: moves that part's picks and its stamps (D188, per variant).
   - levels.def `needs`: kit-private (C4), but a kit byte move is a pcrec abi event (§7).

## 11. Ruled vs open

RULED:
- D188 add. 1 (variants, no `#if`, a list with a stamped default);
- D188 add. 2 (one family per artifact; host default; no multi-family file; one artifact per family
  as the workaround);
- [XARCH-DEV] (complete matchers, build-time one variant, per-variant entries);
- D155 add. 5 (no static, the controller selects);
- the manager on r1: F1 single axis, F2(c)/(d), F6 compound part, F16 ride-along, D27 at the build;
- facts only (D146/D157).

PROPOSED here:
- the target table (§2: rows, derived columns, table check);
- the first-match list table;
- the admission rule `family && needs ⊆ features`;
- the gate field replacing `FLD_policy`'s SIMD reading;
- the include-in-text pick;
- `<prefix>__<T'>` stems and the surface table;
- the additive region pair;
- the per-call probe with `__builtin_cpu_init()`;
- the elision fact;
- D188 fact (b) read off an in-region stamp;
- the §8 checks;
- the §9 measurement and benefit trigger;
- the two addenda in §6.4 (D155 add. 6 / [MEMFN-RTDISPATCH], D146), plus the RB-3/N-4/M-5
  amendment (§6.3).

Bookkeeping at the build (F17):
- `RX__X86_64_V3_MEMFN_FORMS`-style names carry "memfn". D174 binds new names, so they are deferred
  to [STAMP-REVIEW], with a working spelling until then.
- D153 remodel overlap: the kit edits (§4) sit on [IR-FORM] member (4)'s site and on
  lane/memfn-s2e. They ride member (4), or sequence after it.

OPEN:
- **Q1** the x86-64 default list's end value. Leaning: `x86-64,x86-64-v3` at the dispatch step,
  only on §9's benefit trigger.
- **Q2** whether `rx_info` lists the parts. Leaning: yes, at [IFACE-PUSH].
- **Q3** whether length decisions keep subtracting the bracket-marked bytes. Leaning: yes, so a
  part's plan differs only by priced facts.
- **Q4** the list option's spelling (CLI / `pcrec_options` / `.rxt`), at [EMIT-ENTRIES].
- **Q5** whether an ifunc replaces the per-call branch on ELF. Leaning: only if D165 item 5's
  measurement shows a loss.

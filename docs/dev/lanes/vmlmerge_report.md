# vmlmerge — main (RQ-3, abi 71) merged into VMLAZY (abi 72), kit request R-12

Lane vmlmerge (2026-10-09, opus, light). Branch `lane/vmlmerge`, cut from
`lane/memfn-vmlazy` (41281588). Merge of main `631771b7` = `fd295ec0`;
FILEPIN self-pin = `9abebf34`; this report on top.

## 1. Conflicts and resolutions

| file | resolution |
|---|---|
| `src/gen/emit_dfa.c` | `PCREC_ARTIFACT_ABI 72` (this branch's) |
| `docs/spec/match_api.md` guard example | 72 |
| `docs/spec/match_api.md` §6 | 72 entry (now "bumped it from 71 ... `71` is RQ-3's, landed first") above RQ-3's 71 entry (turned to "was `71`", content intact) above 70 |
| `tests/codegen/run_codegen_tests.sh` | `ABI_EXPECT=72`; ledger message = main's (ending at RQ-3 70->71) + VMLAZY's transition re-spelled `71 -> 72` |
| `tests/codegen/run_recursion_identity.sh` | both SELF-PIN comment blocks (RQ-3's, then a VMLAZY one); FILEPIN re-pinned to the merge `fd295ec0` in its own commit `9abebf34` |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` | BEFORE 72, AFTER 71 (the parent's number, the row's convention), SAB_DESC and a re-aim note |
| `docs/dev/lanes/CLAUDE.md` | both sides' entries |

Also: `tests/codegen/CLAUDE.md`'s VMLAZY entry notes the landed 71 -> 72.
Auto-merged without conflict: `emit_vm.c`, `src/gen/CLAUDE.md`,
`tests/memfn/CLAUDE.md`. `make -j8` and `make strict` green on the merge.

## 2. Readers of the number, by grep

`git grep -nIE '\babi[ :=_"(]*7[012]\b|abi.{0,3}7[012]\b|ABI_EXPECT=|ABI_H 7[012]|!= 7[012]\b|ARTIFACT_ABI 7[012]'`
(lanes/journal/design/reviews/plan excluded), after the merge:
- CURRENT-abi readers, all 72 (6 sites): `emit_dfa.c:54`, `match_api.md` §1¶7 (three guard lines)
  (guard example), match_api §6 head entry, `run_codegen_tests.sh:3042`
  `ABI_EXPECT`, S693 BEFORE.
- History, left: `limits.md:797`, the `match_api.md` abi change log (now `docs/dev/history/abi_changelog.md`), `tuning.md:2035`,
  `src/gen/CLAUDE.md:1129`, `tests/codegen/CLAUDE.md:3806` (RQ-3 at 71);
  `cpset_structure.sh:907`, `run_resource_tests.sh:744`, `emit_sweep.py:1847`
  (dated re-pin notes); `memfn/docs/{requests,responses,wake}.md` (dated
  ledger lines); `decisions.md:6666`; `studies/revend_twin/` (committed
  study artifacts at abi 70, never built by make); the vmlazy-era
  `70 -> 72` notes in `tests/mech/CLAUDE.md`, `tests/memfn/{CLAUDE.md,
  c12_ceilings.tsv}`, S693 header.

## 3. Second reader class (byte counts)

`test-cpset-structure` (EMITTED_BYTES [3]), `test-resource` (K59 rung),
`test-memfn-arms` (C5 pins): all GREEN unchanged on the merge — nothing to
re-pin. RQ-3's +52 B and VMLAZY's lazy-prefix bytes do not meet in any
pinned witness.

`emit_sweep.py` VARIANT_PINS (not a make target; full population is the
slot's): measured on the 114 unique lazy movers of
`docs/design/memfn/probes/vmlazy/out/movers.tsv`, `--ref 631771b7
--tree-rev HEAD --variant lowsize|lowboth --bases byte`, PARTIAL population
(logs in the session scratchpad, not kept):
- asymmetric = 0 on every stream (no refusal flips).
- `(a{2,3}?){2,3}` at the LOWERED cap now drops its VM hybrid's prefilter
  (size-cap note on stderr; emit-ir-auto base `yes-collapsed` 2 -> 1,
  `no-size-cap` 6 -> 7; lowboth 3 -> 2 / 6 -> 7).
- `c{1,}?(?:$|[\n\t]+?01{1,2}|[^abc]){2,}` is refused on both sides; the
  refusal's byte figure 31706 -> 31938.
- `-fprefilter` arm: 7 listing movers, `refused` 86 -> 87, `yes-collapsed`
  2 -> 1.
So the lowsize/lowboth cells' `yes-collapsed` counts can fall by 1 and
`no-size-cap`/`refused` rise by 1: a full `--variant all` run at the slot
must re-measure, and re-pin only by its measurement (§5 OWED).

## 4. Check verdicts (taskset -c 12-15, gnutimeout)

Verdict by `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`:
- `make test-recursion-identity`: **RED** — `make: *** [Makefile:1058:
  test-recursion-identity] Error 1`; checks passed 9, failed 4:
  `[default] (A) 53`, `[vm] (A) 114`, `[noprefilter] (A) 53`,
  `[nocaptures] (A) 28` call-free patterns "emit a DIFFERENT PROGRAM REGION
  than ac4917d for a reason no ruling has recorded". Every listed pattern is
  a lazy cursor pattern (`(?:ab){3,}?`, `(?:a+?)+?b`, `((a{1,2}?){1,2}){1,2}`,
  ...), and 114 = the unique pattern count of vmlazy's movers.tsv (set
  equality not checked: the gate's diff lists live in its temp dir; rerun
  with `KEEP=1`). Cause: NORMALIZE re-spells the lazy rmin prefix INSIDE the
  VM program body, the span (A) compares against the pre-module pin. Example,
  `(?:ab){3,}? --engine=vm`, main vs merge:
  ```
  -    rx_span_cursor = scan_position;            (hoisted before the block)
  -        while (it_ < 3UL) {
  -            if (!(rx_span_cursor + 2 <= subject_length && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98))) goto rx_fail;
  -            rx_span_cursor += 2; it_++;
  +        rx_span_cursor = scan_position;
  +        while ((rx_span_cursor + 2 <= subject_length) && it_ < 3ULL && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {
  +            rx_span_cursor += 2;
  +            it_++;
  +    if ((ptrdiff_t)rx_span_cursor < slot_values[2] + 6) goto rx_fail;
  ```
  No ruled bucket admits it (NORMALIZE has no deny axis). The precedent for
  exactly this class is R4h's SEVENTH NAMED EXCEPTION, `adv_layout_canon`: a
  two-sided canonicalizer applied before every comparison, with a
  non-vacuity census. An EIGHTH exception canonicalizing the new lazy prefix
  (cursor init + capped scan + reach test) back to the old counted loop is
  the likely shape. It is a check-design change: NOT done here, a ruling
  for the managers. The vmlazy lane never ran this gate (§8 step 2 was the
  slot's), which is how it surfaced only now.
- GREEN (rc=0, no `*** [test-` line): test-codegen, test-registry,
  test-rxtsource, test-resource, test-cpset-structure, test-memfn-arms,
  test-memfn-stamps, test-memfn-rows, test-memfn-manifest,
  test-memfn-deleg, test-memfn-forms, test-memfn-reach.
- Mech S693 solo (`bash tests/mech/run_sabotage_matrix.sh S693`):
  `codegen:2fail/328pass DETECTED`; `== mech run COMPLETE: 1 rows
  (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, ...) at
  9abebf34 ==`.

## 5. Owed

1. The recursion-identity (A) ruling and its implementation (eighth
   exception or other), then the gate re-run: 16/0 expected only after it.
2. Full-population `emit_sweep --variant all` at the slot; lowsize/lowboth
   emit-ir-auto/stderr tallies may move by 1 (§3).
3. The rest of vmlazy_report §8 (G1 census at the merge, identity gate,
   N2, G2 full, perfrun, mech rows, anchors).

## § recursion-identity bucket (lane vmlrid)

Lane vmlrid (2026-10-09, opus, light), on `lane/vmlmerge` from `395168db`.
Owed item 1 of §5 above is DONE: comparison (A) of
`make test-recursion-identity` now admits NORMALIZE's lazy-prefix
re-spelling on all four axes, through kit manager ruling R1's named
exception, and admits nothing else. The gate is **GREEN, 18/0**.

### 1. Form: a one-sided mechanical rewrite, `lazy_prefix_rewrite()`

This is the EIGHTH named exception, in `tests/codegen/run_recursion_identity.sh`
beside `cls_range0_rewrite`. It has the fourth's shape
(`bref_rename_rewrite`). It rewrites the reference region's nine-line
pre-NORMALIZE prefix:

- `RX_SET(RX_SLOT_SPAN_LOWk, ...)`;
- the cursor init, hoisted outside the block;
- `{ unsigned long it_ = 0; while (it_ < NUL) { if (!(cur + S <= subject_lengthTEST)) goto fail; cur += S; it_++; } }`.

The output is 7106b370's spelling:

- the cursor init, inside the block;
- `while ((cur + S <= subject_length) && it_ < NULLTEST) { cur += S; it_++; }`;
- `if ((ptrdiff_t)cur < slot_values[LOW] + N*S) goto fail;`.

Every output string is taken from 7106b370's `emit_vm.c` hunk. TEST is
copied verbatim: the parent built `test` as the concatenation of
` && (m_i)` over the same `members[]` that the new loop prints one by one.
The result then goes through `adv_layout_canon`, because every subject
region goes through it too.

**Why not a two-sided canonicalizer like `adv_layout_canon`?** The new
spelling carries strictly more than the old one: the reach test names the
low-water slot's NUMBER and the offset `N*S`. A canonicalizer would have to
map new back to old, which means DROPPING the reach test. A dropped line is
never compared, so a wrong slot or a wrong offset would be admitted.
Rewriting the old side forward keeps every byte of the reach test compared.
S711 below is exactly that case.

**It is a regular transform.** R1 item 2's fallback was not needed:

- `N` and `S` are in the old loop's own text.
- The slot NUMBER is not in the region, because the `RX_SET` line names the
  macro, `RX_SLOT_SPAN_LOWk`. The same reference artifact carries it in its
  `#define RX_SLOT_SPAN_LOWk N` table. The gate reads that table off `r`
  (the full ac4917d artifact) and passes it in as `$1`. The value comes from
  the old artifact and is never read off the subject.

**Composition.**

- `rb_lazy` is `lazy(rb)`, and the fourth exception's baseline becomes
  `bref(rb_lazy)`. That one value is what the bref bucket, the D139 range
  rewrite and every deny-axis restore (island, fold, lit-run, atoms, poss
  arms, ctx-node, arm A) compare against.
- A lazy pattern that also needs another bucket is credited to both, and its
  message carries `+vmlazy-prefix`.
- The bref credit test became `rb_bref != rb_lazy`, so a lazy-only pattern
  does not inflate the bref count.
- Vocabulary: `vmlazy-prefix-moved=` on the (A) line, and
  `REGION MOVED (ruled, R-12 VMLAZY NORMALIZE lazy rmin prefix: counted verify loop -> capped span scan + reach test)`.
- The script's header carries the ruling sentence and the citation
  "kit manager ruling R1, R-12 VMLAZY, 2026-10-09".

### 2. Non-vacuity, and the census

**`lazy_pop` text census.** It is computed from pattern text, independent of
the artifact. It reads the masked, escape-collapsed text that POSSRC_RE uses
and counts `+?`, `{n}?`, `{n,}?` and `{n,m}?` with n >= 1, plus `(?…U`
option groups. Measured: **173** call-free patterns. K35 floor
`LAZY_CENSUS_FLOOR=150` (one `bad` below it).

**Per-axis assertions:**

- the bucket fires (`rlazy > 0`);
- it never exceeds the census;
- the rewrite never FIRES on a pattern outside the census
  (`rlazyoutside == 0`). This is checked whenever the rewrite fires, not only
  when the pattern is admitted.

**End of run:** no subject region on any axis still carries the old loop
head (`LAZYOLD_TOTAL == 0`, one `ok` line).

**Set equality by ID.** "Moved" is the baseline run's REGION DIFFERS set,
before the bucket existed. "Fires" is an independent grep of each census
pattern's ac4917d region for the old loop head. "Admitted" is every
`R-12 VMLAZY` or `+vmlazy-prefix` line in the final run's diff file.

| axis | census | moved (baseline red) | fires in ac4917d | admitted | alone | composed | admitted == moved == fires | rdiff |
|---|---|---|---|---|---|---|---|---|
| default | 173 | 53 | 53 | 53 | 33 | 20 | yes, by ID | 0 |
| vm | 173 | 114 | 114 | 114 | 94 | 20 | yes, by ID | 0 |
| noprefilter | 173 | 53 | 53 | 53 | 33 | 20 | yes, by ID | 0 |
| nocaptures | 173 | 28 | 28 | 28 | 8 | 20 | yes, by ID | 0 |

**What the 20 compose with, on every axis:**

- 16 with the ctx-node bucket (`ctx-node-moved` 455 -> 471 on default);
- 3 with the bref rename alone, plus 1 with a stamped deny-axis restore that
  also needed the rename. Together these account for `bref-rename-moved`
  397 -> 401.

**[vm] against vmlazy's `out/movers.tsv`, by ID.** The `c-vm` stream has
114 unique patterns. 108 of them are call-free and in this gate's corpus;
the other 6 are call-bearing and excluded by the classifier. All 108 are
admitted. The bucket admits **6 more**, and each is explained:

- `(a)(?:ab){2,4}?ab`, `(a)(?:ab){2,}?ab`, `(a)(?:ab){2,}?ac` and
  `(x)(\d{4,}?)\d` live in `tests/base/vm_lazy_rmin_prefix.rxt`. VMLAZY's
  REPLACE commit 08bda492 added that file. It is absent at NORMALIZE
  7106b370, where the census population was read. Each is admitted alone.
- `-+?(?=a)?b` and `[ab]+?(?![ab])` are possessified by [ART-POSS-ARMS]
  arm A in BOTH builds the census compared (`RX_VM_POSS_ARMS 0x1` at
  df66a032 and at the tip), so neither is a mover there. ac4917d predates
  the arms and emits a lazy cursor rung. The gate's ctx-node deny build,
  which denies `-fno-poss-ctx-follow -fno-poss-bref-first -fno-ctx-node`,
  restores that rung in the NEW spelling. So they are admitted composed:
  `[UCP] U2 context node ... +vmlazy-prefix`.

So the bucket's [vm] set is movers.tsv's call-free set plus 6 explained
patterns, not equal to it. The reasons are a later corpus file and the
census measuring the default build, not the deny build.

### 3. Why 53 / 114 / 53 / 28

Each count is the number of call-free patterns whose ac4917d program region
contains a VM lazy cursor rung with rmin >= 1 on that axis (the "fires"
column, measured independently). Route selection for these patterns is the
same at ac4917d and at the tip, so every such region moved and nothing else
did. Measured set relations: default = noprefilter, nocaptures ⊂ default ⊂ vm.

- **[vm] 114:** the engine is forced, so every lazy rmin >= 1 cursor rung
  is emitted.
- **[default] 53:** 61 of the 114 are capture-free lazy patterns that the
  default route sends to the DFA, so neither side has a program region.
  Examples: `(?:ab){3,}?`, `(?:a+?)+?b`, `(?:\w{1,2}?\b)+`.
- **[noprefilter] 53, the same set as default:** `-fno-prefilter` changes
  the hybrid's prefilter, not the engine.
- **[nocaptures] 28:** 25 of default's 53 are on the VM only because they
  have capture groups (`(a+?)`, `(ab){2,4}?`, `((a{1,2}?){1,2}){1,2}`, ...).
  With `--no-captures` they go to the DFA. The 28 that remain carry a
  construct that forces the VM without captures: a lookaround, a
  backreference or an atomic group (`(?>a+?)b`, `\w+?(?<=a)`,
  `(a|b)+?\1`, ...).

### 4. Planted control (by hand, varland's S273 method)

I built three compilers from `git archive` of the branch: the clean tip, a
CONTROL compiler and the S711 compiler.

- CONTROL: `vm_emit_span_scan(..., a->u.rep.rmin - 1)`, i.e. the cap off by
  one.
- S711: `vm_span_reach(v, low, lo_off - 1)`.

I then ran the gate's own `stamp_strip`, `prog_region`, `adv_layout_canon`
and `lazy_prefix_rewrite`, extracted verbatim from the script, against the
ac4917d reference over the 108 call-free [vm] movers (`--engine=vm`):

```
clean tip   admitted=90  not-admitted=18  rewrite-did-not-fire=0
            (the 18 are backref/lookaround patterns the gate admits composed)
CONTROL     admitted=0   not-admitted=108 rewrite-did-not-fire=0
S711        admitted=0   not-admitted=108 rewrite-did-not-fire=0

(?:ab){3,}? --engine=vm, CONTROL vs rewritten reference:
<   while (rx_span_cursor + 2 <= subject_length && it_ < 3UL && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) { rx_span_cursor += 2; it_++; }
>   while (rx_span_cursor + 2 <= subject_length && it_ < 2UL && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) { rx_span_cursor += 2; it_++; }
(?:ab){3,}? --engine=vm, S711 vs rewritten reference:
<   if ((ptrdiff_t)rx_span_cursor < slot_values[2] + 6) goto rx_fail;
>   if ((ptrdiff_t)rx_span_cursor < slot_values[2] + 5) goto rx_fail;
```

Neither plant is admitted. Each differs from the rewritten reference by
exactly the planted token, so both would land in `rdiff`.

### 5. Sabotage S711 (`tests/mech/sabotages/S711_vmlazy_reach_one_byte_short.sh`)

The plant is the reach test one byte short (`lo_off - 1`). Suites are
`recidentity harness`, with the harness scoped to
`tests/base/vm_lazy_rmin_prefix.rxt`.

- At stride > 1 the plant is ANSWER-INVISIBLE: the cursor only lands on
  `entry + k*W`, so the identity gate is the only check that can see it.
- At stride 1 it is a wrong answer.

Mech cannot score `recidentity` (varland finding 7: the scratch tree has no
git history), so the row declares that, and the bucket half was validated by
hand in §4.

Solo run at `ca278766`:

```
reach:ok(1/1), recidentity:SKIPPED-no-git-history, corpus:1fail/137pass
DETECTED ( SKIPPED -- no oracle)
== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0) at ca278766... ==
```

I confirmed the one harness failure by hand: `vm_lazy_rmin_prefix.rxt:173`,
`z(a){3,}?c?` with `engine vm` on "zaac", answers `match 0 4 2 3`, where
python re says nomatch.

### 6. Verdicts (taskset -c 12-15, gnutimeout; logs in the session scratchpad)

- `make test-recursion-identity` at `6d42f266`: **checks passed: 18, checks
  failed: 0**. `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` is empty.
  - (A) `differing=0` on all four axes, with `vmlazy-prefix-moved=53/114/53/28`.
  - (B) is identical on all four.
  - The brief expected 16. The script has 17 checks on a green run (the
    earlier red run's 9 + 4 failing axes, plus the 4 (A) passes those axes
    did not print). The 18th is this exception's own end-of-run `ok`.
- `make test-codegen`: run_group 15/15 scripts passed. The verdict grep is
  empty.
- Docs updated: `tests/codegen/CLAUDE.md`, in the VMLAZY entry, and
  `docs/dev/lanes/CLAUDE.md`, in this report's line.

# pfx0 — [PFX-1] STEP 0 census (2026-09-30, lane pfx0, sonnet; measurement only)

Brief: `parkmeas_report.md` A7. Nothing under `src/`, `tests/`, `docs/spec/`. Tree: `0c9a4ec3` (abi 49),
Mac M1, gcc-16, `build/pcrec` built in this worktree. All numbers are byte counts / grep counts of
the emitted text — no timing. Scratch scripts (`classify.py`, `sweep.py`, `readers.py`, `size.py`)
lived in the session scratchpad and are described in Method; they are not committed.

## Verdict (what the census decides)

1. **The internal-reader list is LONG: 86 files / 501 hits outside `src/`** read an INTERNAL prefixed
   name (37 live scripts/drivers 331 hits; 41 sabotage rows 121 hits; 8 `.md` 49 hits), plus 28
   files/144 hits that read a name the spec cites but the header does not export. So [PFX-1] STEP 1
   is an abi event with a wide reader sweep and **needs its own design**; it is not a small change.
2. **[DD-13b.W1.3.1] is NOT blocked on [PFX-1].** Its four `flush_block`-tail sites (`pcrec -p`,
   driver `-DRXT_PREFIX`/`-DRXT_UPREFIX`, the `RX_NCAPS` grep, `size_count.sh`'s stamp reads) already
   read ONLY exported or spec-documented names — `tests/harness/` contains ZERO internal-name reads.
   D96's premise ("so the four prefix sites are the exported set only") is already true; and
   PFX-1 STEP 1 would not remove the need to thread the target's prefix through them, because the
   exported names (entries, `<P>_NCAPS`, stamps) KEEP the prefix. Recommend the gate on W1.3.1 be
   read as discharged; Frank's sequencing word for [DD-13] is the remaining gate.
3. **Bytes-saved figure (the size dial's input): 0.5-1.0% of emitted source at `-p rx`, growing
   linearly with prefix length — 8-16% at a 23-char prefix, 17-30% at 60 chars.** Object code
   (`__TEXT`/`__DATA`) is byte-identical. So the saving is real only for long prefixes (the bench's
   ids are that long); at the harness's `rx` it is not worth an abi event by itself.
4. **A finding neither D96 nor the row anticipated: the prefix length is an INPUT to the VM's
   entry-shape decision.** `(foo|bar)[0-9]{2,5}(x)` compiled at `-p rx` / a 23-char prefix / a 60-char
   prefix stamps `RX_VM_PROGRAM_BYTES` 2517 / 3714 / 5823 and `RX_VM_ENTRY_SHAPE` `"inline"` /
   `"inline"` / `"plain"`, with `.text` 6247 / 6263 / 5019: the same pattern gets a different
   artifact by what it is named. (Same shape as [EMIT-VERB]'s `sb_len_uncut` finding one axis over:
   a size read that counts prefix bytes.) A fixed internal spelling makes the program-size decisions
   prefix-independent — a determinism argument for STEP 1 that does not depend on the byte saving.
   Filed as an observation, not chased into `emit_vm.c` (out of scope: no `src/`).

Recommendation: unblock W1.3.1 now (item 2). Keep [PFX-1] `not-started`; if chartered, STEP 1 gets a
design note first (reader sweep = the tables below; the prefix-dependent-rung finding as its
strongest motivation), not a build.

## (a) Classification — EXPORTED vs INTERNAL

Artifacts, each `--emit-main`, compiled at `-p zz` (a prefix no other token contains) and `-p rx`:
DFA `a(b|c)+d --engine=dfa --no-captures`; VM `(a+)(b*)\1c --features backrefs`; hybrid
`(foo|bar)[0-9]{2,5}(x)` (`RX_VM_PREFILTER "hybrid"`); composed `tests/definitions/composed.rxtin`
target `pair` (`--features all`, prefix derived from the block name). "Prefixed identifier" = every
token containing the prefix in the `.c` or `.h`. Classes: **EXPORTED** = appears in the `.h` or is
a link-visible definition (`nm -g` on `gcc -c`; the two sets coincided); **SPEC-CITED** = not
exported but `docs/spec/*.md` names it as `<prefix>_x`/`<PREFIX>_X` (the documented stamps, plus
eight-odd internal code names the spec mentions); **INTERNAL** = neither.

| artifact | prefixed tokens | EXPORTED | SPEC-CITED | INTERNAL (macro / sym / label / type) |
|---|---|---|---|---|
| dfa | 57 | 16 | 20 (all stamps) | 21 (0 / 18 / 0 / 3) |
| vm | 102 | 17 | 40 (34 stamp/macro, 5 sym, 1 label) | 45 (22 / 9 / 14 / 0) |
| hybrid | 127 | 16 | 52 (44 stamp/macro, 7 sym, 1 label) | 59 (19 / 22 / 16 / 2) |
| composed (`pair`) | 49 | 16 | 20 (all stamps) | 13 (0 / 6 / 7 / 0) |

EXPORTED, every artifact: the seven entries `<p>_match`, `_match_in`, `_match_caps`, `_match_caps_in`,
`_search`, `_search_in`, `_next_pos`; `<p>_buffers`, `<p>_info`; the header guard;
`<P>_NCAPS`, `<P>_BUFFER_ALIGN`, `<P>_RESUME_FRAMES`/`_FRAME_SIZE`, `<P>_TRAIL_FRAMES`/`_FRAME_SIZE`;
with module `vars` also `<P>_NVARS`, `<P>_VAR_*`, `<p>_span_match`, `<p>_span_match_caseless`,
`<p>_back_step`. The shared block (`rx_ctx`, `rx_info`, `rx_var`, `rx_group_entry`, `rx_callout_ref`,
`rx_matchfn`, `rx_renderfn`, `PCREC_*`) is FIXED-spelled already and is not a per-artifact token.

Wider population, to make the table more than four samples: 900 unique corpus `pattern` lines
(sampled seed 1 from `tests/*/*.rxt`, minus known_fail), each compiled at `-p zz --features all`
(`--engine=vm` on refusal): 825 compiled; **525 distinct prefixed tokens** across them:

| class | distinct tokens |
|---|---|
| EXPORTED (in `.h`) | 25 |
| SPEC-CITED stamp/macro | 47 |
| SPEC-CITED code | 16 (`zz_L0`, `_can_begin_match`, `_match_anchored`, `_match_run`, `_match_caps_run`, `_search_run`, `_run_state_bind`, `_prefilter`, `_ofsskip`, `_reqrun`, `_reqrun_whole`, `_forward_scan_edge`, `_forward_scan_views`, `_class_atoms`, `_var_names`, `_vars_resolve`) |
| INTERNAL | 437 = 194 `zz_L<n>` labels + 85 macros (`ZZ_SLOT_*`, `ZZ_CUT`, `ZZ_SET`, `ZZ_R_*`, ...) + 158 symbols/types/labels (`zz_forward_*`/`_reverse_*`/`_anchored_*` tables and steps, `zz_s<n>`, `zz_targets_<n>`, `zz_class_atom<n>`, `zz_run_state`, ...) |

So 83% of distinct prefixed names are internal — the row's premise (there is one artifact per TU,
so file-scope statics/labels/macros need no per-artifact spelling) holds on the population.

## (b) Readers of an INTERNAL prefixed name, by grep

Population: `tests/`, `scripts/`, `tools/`, `analyze/`, `Makefile`, excluding `.rxt`/`.rxtin`/`.tsv`
(corpus data). A hit is `<prefix-spelling>_<internal stem>` where the prefix spelling is `rx`/`RX`/`zz`/
`ZZ`/`<p>`/`<P>`/`<prefix>`/`<PREFIX>`/`%s`/`${var}`/`$(var)`. `%s_stem` catches the format-template
form sabotage anchors quote from the emitters. (Shell variables like `$total_fail` were matched by
a first cut and excluded — a bare `$name_` is not a prefix spelling.) The internal stem set is the
525-token union above minus EXPORTED/SPEC-CITED, with digit-suffixed families generalized.

| reader class | files | hits |
|---|---|---|
| live suite scripts / drivers | 37 | 331 |
| sabotage rows (`tests/mech/sabotages/*`) | 41 | 121 |
| `.md` (CLAUDE.md/docs) | 8 | 49 |
| `tests/harness/` (`run.sh`, `driver.c`, `dispatch_gen.sh`, `verify_rxt.py`) | **0** | **0** |
| **INTERNAL total** | **86** | **501** |
| SPEC-CITED *code* names read by live scripts / sabotage / md | 18 / 9 / 1 | 114 / 16 / 14 |

Live-script readers, file:first-hit-line (hits): `tests/codegen/run_codegen_tests.sh:150` (99),
`run_recursion_identity.sh:320` (42; the identity gates' `<p>_L0`/`<p>_accept` region markers — `_L0`
is spec-cited, `_accept` and `_call_frame` are internal), `run_premul_table.sh:11` (30), `tests/mrl/run_mrl_tests.sh:72`
(19), `tests/recursion/gen_corpus.py:962` (12), `run_ir_listing.sh:86` (11), `run_anchored_match.sh:67` (11),
`run_tiered_entry.sh:16` (9), `run_search_pinned.sh:146` (9), `tests/possessify/run_possessify_tests.sh:70` (8),
`tests/bench/run_bench.sh:159` (6), `run_vm_frameless.sh:33` (6), `run_offset_skip.sh:22` (6),
`tests/bench/tier_escalation_driver.c:17` (5), `tests/assertions/run_kreset_diff.sh:246` (5),
`run_form_census.sh:177` (5), `run_scan_edge_dispatch.sh:52` (5), `tests/thread/run_stackdepth_tests.sh:20` (5),
and 19 more files of 1-4 hits each (`run_encoding_checks.sh:48`, `run_dfa_stamps.sh:70`, `run_dfa_uniform_fold.sh:135`,
`run_cpset_structure.sh:512`, `tests/core/sb_stamp_check.c:148`, `tests/registry/axes_registry_check.sh:773`,
`tests/island/run_island_tests.sh:255`, `tests/anchored/run_anchored_dead_entry.sh:43`,
`tests/recursion/run_specimen_identity.sh:45`, `scripts/emit_sweep.py:236`, `Makefile:1104`, ...).
Sabotage rows: 41 files, 1-9 hits each (largest `S155_depth_capacity_untyped.sh` 9, `S157`/`S-U8` 5).

Two structural facts the counts hide: (1) nearly every reader hard-codes prefix `rx`, so the sweep is
a rename of names inside greps, not a parameterization — STEP 1's cost is the 86 files, not new
mechanism; (2) 27 of the 121 sabotage hits are `%s_`-template anchors into `src/gen/emit_*.c`, i.e.
they read the internal name as EMITTER text, so re-anchoring is per-row work of the D107/S-row kind
(`scripts/m6read_check_sab_anchors.py` is the checker).

**W1.3.1's four sites** (`tests/harness/run.sh` `flush_block` tail, `git show 0c9a4ec3`):
`:1890` `pcrec -p rx` (entry prefix); `:2110` `-DRXT_PREFIX="$px" -DRXT_UPREFIX="$upx"` — the driver
pastes only `_search`, `_search_in`, `_next_pos`, `_buffers`, `_match`, `_match_in`, `_match_caps`,
`_match_caps_in` and `_NCAPS`, `_TRAIL_FRAME_SIZE`, `_RESUME_FRAME_SIZE` (grep of `RXFN(`/`RXMAC(` in
`driver.c`: 11 distinct names, all EXPORTED); `:2069` `^#define RX_NCAPS` (EXPORTED, in the `.h`);
`tests/lib/size_count.sh:129` the D46 stamp reads (`RX_ENGINE`/`RX_VM_PREFILTER`/`RX_VM_RUNGS`:
SPEC-CITED stamps that keep the prefix). All four read exported/documented names only.

## (c) Emitted-bytes saving if internals took a fixed spelling

Method: compile each artifact at three prefix lengths; rewrite every INTERNAL token
`<prefix>_stem`/`<PREFIX>_STEM` → `p_stem`/`P_STEM` (a 2-char fixed spelling; EXPORTED, SPEC-CITED and
the fixed `rx_` shared-block names left alone); confirm the rewritten `.c` still compiles against the
unchanged `.h` and `.o` sections are unchanged; report file bytes (comments are off by default since
[EMIT-VERB], so the file is comment-free). Internal names never appear in the `.h` (checked: 0).

| artifact | prefix len | file bytes | after | saved | % | internal occurrences | `__TEXT`/`__DATA` before=after |
|---|---|---|---|---|---|---|---|
| dfa | 2 | 13,050 | 12,986 | 64 | 0.5 | 64 | 2459/200 |
| dfa | 23 | 15,024 | 13,836 | 1,188 | 7.9 | 54 | 2475/200 |
| dfa | 60 | 18,502 | 15,316 | 3,186 | 17.2 | 54 | 2515/200 |
| vm | 2 | 16,917 | 16,755 | 162 | 1.0 | 162 | 3687/200 |
| vm | 23 | 22,398 | 18,834 | 3,564 | 15.9 | 162 | 3703/200 |
| vm | 60 | 32,055 | 22,497 | 9,558 | 29.8 | 162 | 3743/200 |
| hybrid | 2 | 26,070 | 25,892 | 178 | 0.7 | 178 | 6247/200 |
| hybrid | 23 | 32,118 | 28,202 | 3,916 | 12.2 | 178 | 6263/200 |
| hybrid | 60 | 42,469 | 31,967 | 10,502 | 24.7 | 178 | 5019/200 (rung flip, item 4) |
| lookaround (VM) | 2 | 22,595 | 22,432 | 163 | 0.7 | 163 | 4107/200 |
| lookaround (VM) | 23 | 28,286 | 24,700 | 3,586 | 12.7 | 163 | 4123/200 |
| lookaround (VM) | 60 | 38,313 | 28,696 | 9,617 | 25.1 | 163 | 4163/200 |

(Mach-O `size` columns; the small `__TEXT` growth with prefix length is symbol-string bytes, not
code.) Saving = internal occurrences × (prefix − 2); the occurrence count is prefix-independent
(the dfa 2→23 dip 64→54 is the fixed `rx_` shared-block names, which collide with `-p rx` and are
excluded there). The rewrite is not itself a validated design — `p_`/`P_` may collide with a user's
own identifiers in a TU that includes the `.c`; a real STEP 1 picks a spelling with that in mind.

## (d) The two-header-in-one-TU check and the shared block

Already in the tree: `tests/codegen/run_codegen_tests.sh:437-520` (two differently-prefixed
artifacts in one TU, guard emitted once) and `:905+` (the ABI block byte-identical across four
prefixes with a whole-file control). Re-measured here on this tree: `vm_rx.h` + `hyb_zz.h` +
`dfa_rx.h` in one TU compiles clean under `-Wall -Wextra -Werror`; `rx_match` and `zz_match` both
assign to a `ptrdiff_t (*)(const rx_ctx *)`; the `PCREC_RX_ABI_H` block is 182 lines, md5
`44a34a2d2040406820c626e7fb79ee7d`, IDENTICAL across `rx`/`zz`/composed-`pair` and dfa/vm/hybrid.
**Confirmed gap (D96 addendum 3's "abi-VERSIONED guard"):** the guard is the literal
`PCREC_RX_ABI_H`, so a header whose block differs (simulated by editing one `PCREC_ERR_*` name in a
copy of `hyb_zz.h`) included after `vm_rx.h` compiles with no diagnostic — different-abi artifacts
silently share the first block. That work item is not covered by any existing check.
Shared-header-vs-self-containment weighing (row's last clause): not measured here; the block is 182
lines / ~7 KB per artifact, and D96 addendum 3 already retracted "distinct types", so the argument
for a separate file is now only the guard, which the versioned-guard fix covers without one.

## Method and caveats

- Population for (a) wide sweep is a 900-pattern seeded sample of corpus `pattern` lines, not the
  whole corpus; distinct-token counts are a floor (a rarer feature combination could add names).
  Digit families (`zz_L<n>`, `zz_s<n>`) are counted per distinct number.
- SPEC-CITED is a text match against `docs/spec/*.md`; it includes names the spec merely
  mentions as internal (`match_api.md` §"eight statics" for the entry chain), so it over-selects
  as "contract" — those 16 code names are the ones STEP 1 must rule on (keep prefixed with a spec
  hunk, or fix-spell and update the spec), and they carry 18 live files/114 hits of readers.
- Reader grep is textual. It cannot see a name built at run time in a script from parts, and it
  reads only the `rx`-and-template spellings; the `${var}_x` form is covered, `$var_x` is not
  (indistinguishable from a shell variable — the first cut's false-positive class).
- Mac scratch tier: sizes are compiler-deterministic byte counts (host-independent for the `.c`),
  the `__TEXT` numbers are Mach-O/gcc-16 and are indicative only for Linux.

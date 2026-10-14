# r4 (2026-10-12): LIGHT re-check of R-17 revision 2 (setfind.md)

**Under review:** `docs/design/memfn/setfind.md` (lane r17r5). It is R-17 as
the degenerate window search (D161 add. 3), with stateful mask/ring forms
plus adaptive (Q-R17-1), one routing event (Q-R17-2 / D155 add. 3), and
kit-owned body storage.
**Panel:** two read-only critics. K1 took soundness (opus); K2 took contract
fit and D157 (sonnet).
**Alongside:** lane r17dry compiled and dry-ran the follow-up harness
(`r17dry_report.md`).
- The full sequence check passed: 190 twins, 4.04G calls, 0 mismatches,
  and every mechanism population was non-zero.
- The planted stale-state check caught 152 of 152.
- ASan+UBSan were clean.
- The dry run lists 619 invocations, about 80 min.

**Consolidated by:** the kit manager.

## Verdict

**There is no blocker. The core holds.**

K1 verified the equality proof, the one-compare test in both directions,
the shift ranges, the LOWEST argument, the ring capacity, and storage
dominance at every real site, including the rev-end relocate path.

K2 confirmed the remaining structure:
- The degenerate mapping is sound for FIND.
- W3 at `move_back = 0` is byte-identical to today's result.
- D155 add. 3 is used correctly.
- The VM hat's one handle for entry and retry is right.

r3's BLOCKER C1-1 is CLOSED. Most r3 must-fixes are closed. The ones still
open are C1-2 (partial), C3-6 (wrong), C3-8 and C3-10 (deferred) and C3-2
(see K2-6).

**What still needs fixing is a revision 2.1, design text only.** The open
items are three must-fixes from each critic (K1-1, K1-2, K1-3; K2-1, K2-2,
K2-8) plus the SHOULDs below. No ruling is needed. Every fix is kit-internal
or a restatement of what pcrec provides.

**The follow-up timing does not wait for 2.1.** The harness measures forms,
not the contract, and it is ready. It runs when seambuild's chain is DONE.

## By-id

| id | sev | finding (short) | disposition (rev 2.1) |
|---|---|---|---|
| K1-1 | MUST-FIX | adapt's walk mode names the VM hat's function-local `start_set` from a prologue-flushed helper; does not compile; C3-6's row is false for adapt | pass T as a helper parameter (its text the `table_name` hook at each use); correct §R C3-6 |
| K1-2 | MUST-FIX | S833 is an equivalent mutant at end_back 1 | replace it with an over-read plant at end_back 0 (an overlapped block at hi−63: guard page + ASan), plus the `top ≤ hi` trace assertion |
| K1-3 | MUST-FIX | the dirty-stack control can fail safe silently (uniform fill gives base == top; -O2 keeps it in registers) | Q9 also at -O0 with a non-uniform fill satisfying `base ≤ lo < top`; a C-check that `mf_locals` text initializes every scalar the helper reads; S831's detector is named as that pair |
| K1-4 | SHOULD | G-S1/G-S2 unchecked | the kit refuses an `mf_use` whose s/n hook text or end_back differs from define; a C-check that s/n are not assigned after the storage point; a trace-build re-probe of every cache hit plus `top ≤ hi` |
| K1-5 | SHOULD | "handle used from two functions is refused" is unenforceable | compare the body-sink pointer at mf_locals with every mf_use |
| K1-6 | SHOULD | VM order: no handle before define; DFA: emit_scan_loop shared with reverse/anchored | order define → locals → table-if-read → use inside the entry emitter; key DFA mf_locals on the forward PF site (with K2-9) |
| K1-7 | SHOULD | dominance unchecked | movers compiled with `-Wjump-misses-init`, filtered to `<stem>__` diagnostics |
| K1-8 | SHOULD | -Werror hazards: ring `pos[]` maybe-uninitialized; placed-but-unread storage | ring witness compiled at -O2/-O3 in test-codegen; refuse placed-unread at mf_art_end |
| K1-9 | SHOULD | REACH greps text, not the cache path | dynamic cache-hit counts with a floor over R17-b movers for S829-S833, S841 |
| K1-10 | NIT | "exhaustive over all covers" is only over candidates; IDDFS must search S and its complement | restate, or add sub-terms; pseudocode searches both targets |
| K1-11 | NIT | the stem arrives as the K79 placeholder `\x01q…` | stem treated as opaque; a placeholder stem in G2's shadow set; a C-check that no pcrec identifier starts with `<stem>__` |
| K1-12 | NIT | mf_plan must see the same hooks as mf_define | superseded if K2-6 retires mf_plan; otherwise stated |
| K2-1 | MUST-FIX | no file-scope buffer at `cand_emit_table` (tables are function-local); `mf_flush_helpers` flushes word-loads only | define the DFA PF site from a new `u.pf.emit_block` on the PF rows (`ofs_site_define` precedent); table emission from the define result; state the flush-helpers kit change honestly as part of R17-a; re-derive C3-6 |
| K2-2 | MUST-FIX | "R-18 needs no re-routing" is overclaimed: the handoff/ASSIGN and OFS FUNC shapes may re-route | restate: "move once" holds for the PF sites; W3 is extended to the `ret_pred` reply only if justified, else that claim is withdrawn |
| K2-3 | SHOULD | "sites move once" is routing-once, not bytes-once; W6 depends on the unrun result | an honest statement in §0, with which outcome keeps it true |
| K2-4 | SHOULD | W1/W2 not freezable: origin ambiguity, no unbounded sentinel, wrap in `c − move_back`, reverse/non-FIND unspecified, zero-fill makes "stated 0" vacuous | fix the origin (from the span's beginning, per D161); reserve `MF_MOVE_UNBOUNDED`; a non-wrapping W3; refuse nonzero W1/W2 on non-FIND/reverse; make the field's statedness checkable (a stated bit or sentinel, per no-silent-defaults) |
| K2-5 | SHOULD | `locals_offered`/`needs_locals` presume method; needs_locals dead; §14 glosses; four density carriers | rephrase as a host capability; drop needs_locals; strip glosses; name one density carrier to fold into before R-18 (unlock) |
| K2-6 | SHOULD | mf_plan duplicates selection | DFA: `reads_table` and includes returned in `mf_result` from the emit_block define (K2-1), plus a back-patchable include slot; VM needs no prediction; mf_plan dropped |
| K2-7 | SHOULD | R17-a's zero-mover control omits mech | add the [SABANCHOR] exact-count gate + a derived re-aim list (S478 named) |
| K2-8 | MUST-FIX | R17-b's reader census is spec-only; test readers of the walk text go vacuous | name each reader (run_dfa_stamps.sh:254/260, run_mline_diff.sh:189, run_cpset_structure.sh:932, run_anchored_match.sh, run_offset_skip.sh, tests/startset `[vm-table]`) with before/after population and floor |
| K2-9 | SHOULD | one function per site does not hold (emit_scan_loop copies; rev-end relocate second function); placed-twice not refused | place mf_locals in the forward-loop caller; a stem (or a site) for relocate; refuse placed-twice at mf_art_end |
| K2-10 | SHOULD | C3-6 wrong, C3-8/C3-10 deferred, C3-2 via mf_plan | fix the §R rows truthfully (C3-8: decide the endianness spelling now; C3-10: K's derivation path stated) |
| K2-11 | SHOULD | stateful forms in the hybrid prefilter function pay init every call | the stateful row declines there unless §13 shows otherwise; the adaptive reliance stated |
| K2-12 | NIT | `pf_open` at :6228; `fn_ref` doc string | fix the citation; fields.def doc update at landing |
| r3 C1-2 | (partial) | BE declared UNREACHED | a byte-swapped LE test (a byte-reversing load + flipped `__BYTE_ORDER__` in the test TU) |
| setfind §12.5 | — | ids S825-S842 | renumber to main's allocation **S826-S843** |

All 24 ids are dispositioned: K1 12, K2 12. r3's residuals are folded in.

## Unlocks (filed, not built)

- **Use-invariance as a field class:** the K1-4 refusal for every
  multi-use handle. Trigger: the second stateful row.
- **A function token on mf_locals/mf_use:** kit state for any site, e.g.
  popcount COUNT. Trigger: COUNT is filed.
- **A trace-build re-probe of cache hits** as a standing oracle for cached
  kernels. Trigger: the first stateful row lands.
- **A reverse block cache (clz)** for MLINE/rev-inner. Trigger: the first
  rev-inner set landmark.
- **Pre-prologue facts via `mf_result`** instead of a dry-run API.
  Trigger: a second consumer.
- **`MF_MOVE_UNBOUNDED` + a fixed origin.** Trigger: R-18's first unbounded
  span (taken now in 2.1 per K2-4).
- **Lazy table demand recorded by `table_name`.** Trigger: a second
  conditional table read.
- **One density carrier.** Trigger: W6 is filed, or R-18's first density
  reader.
- **The reply as (window, span) lvalues.** Trigger: the first multi-span
  row.
- **A "uses per activation" host fact.** Trigger: a measured stateful-init
  loss in the hybrid prefilter function.

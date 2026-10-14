# r17r — R-17 revision 2: the small-set FIND as the degenerate window search

Lane r17r5, 2026-10-11/12, opus, a design lane for the memfn kit manager.
Branch `lane/r17r`, cut from `lane/memfn-r17` at `e704144c` (abi 75,
`MF_SITE_ABI` 10). The box was held by main's validation chain, so **NOTHING
WAS RUN**: no make, no gcc, no python of any instrument, no timing. Every
dry-run and run below is OWED. The one python3 invocation in this lane edited
three CLAUDE.md files as text; it executed no instrument.

- Design note: `docs/design/memfn/setfind.md`.
- Harness source (not run): `docs/design/memfn/probes/r17/{gen_twins_r2.py,
  time_r2.c, check_r2.c, run_time_r2.sh, summarize_r2.py}`.

## 1. What the note decides

1. **R-17 is D161's window search in its degenerate case (§2).** It has one
   span of one position, move-back 0 and overshoot 0. The kit's
   `mf_pred` of fixed-offset REQUIRED terms already IS one span, and its term
   offsets already express a negative move-back (MLINE at -1), which D161's
   text cannot.
   - **Carried now (stated by every FIND builder):** W1 `move_back` and W2
     `overshoot` (0/0); W3, FIND's result as "the window's beginning, never
     below lo"; W4 `locals_offered`; W5 `fn_ref` as a STMT site's name stem.
   - **Appended later without moving a byte:** W6-W10 (further spans, the
     reply's span, the consumer price, the frequency table, a joint rate).
2. **One primitive, `mf_set_terms(set, K)` (§3).**
   - Candidates are prime cubes and maximal modular arcs, with a complement
     form.
   - The objective is lexicographic (fewest terms; direct before complement;
     the derived op cost; the canonical key).
   - The search is bounded IDDFS over the lowest uncovered member, with
     BUDGET `UNMEASURED DEFAULT: 4096` and a census tripwire.
   - Uncoverable sets, |S| = 0 and |S| = 256 DECLINE.
   - Renderings are tagged EXACT or LOWEST.
   - The derivation is cross-checked against `pcrec_cube_of`.
3. **The forms are stateful-centred (§8).**
   - The mask form (W = 8 or 64, derived) and the ring form (`RING`
     unmeasured) carry an exact cache of `[base, top)`.
   - **The proof (§8.2):** they answer exactly the stateless F(lo) for ANY
     sequence of `lo`, given only that `s`, `n`, the subject bytes and
     `end_back` do not change. No monotonicity is needed: one unsigned
     compare tests both sides of the interval.
4. **Adaptive (§9.1).** [OPT-HYB-RESEED]'s two-mode shape over the
   skip distance, with a walk mode that is today's table walk. Every constant
   is `UNMEASURED DEFAULT`.
   - The static density gate (§9.2, with `D_ABSENT` declining) is a FALLBACK,
     rendered only if the follow-up shows the stateful/adaptive forms losing
     dense.
   - Without it, R-17 needs NO density fact, and N1 stops being its trigger.
5. **Rows (§4).** In expected order: `pf_terms_adapt`, `pf_terms_mask`,
   `pf_terms_ring`, `pf_memchr_set`, `pf_terms` (stateless), with today's
   walk as the floor. Each has its own deny and its contract (§4.2-§4.3). The
   measurement decides which exist.
6. **Arithmetic and spelling.**
   - The remainder guard: `lo < n && n - lo > end_back` (§5). An empty use
     writes nothing.
   - Endianness: one constant-folded ternary at the word load, plus a PDP
     `_Static_assert` (§6). The BE answer is UNREACHED on these boxes, and
     the note says so.
7. **Main's storage question is answered (§7).**
   - `mf_locals` is called once at a point dominating every use, before any
     `goto` can skip it: before `emit_init` on the DFA, before the entry seek
     on the VM.
   - The storage is automatic, lives one call and is initialized by the
     kit's text.
   - pcrec guarantees G-S1/G-S2 (`s`, the bytes, `n` and `end_back` are
     invariant) and promises nothing about the cursor.
   - One storage per site, so the VM hat's entry and retry share one cache.
   - Names are pcrec-given stems with a reserved `<stem>__*` namespace.
8. **One routing event (§11).**
   - **R17-a:** a zero-mover seam (`MF_SITE_ABI` 11; define-then-emit;
     `mf_plan` for includes and table-reads; `mf_locals`; N4).
   - **R17-b:** the one SIMD-off byte move (rows, denies, the abi bump,
     method-blind spec hunks, G1 at both layers).
   - **SIMD arms** then land as guarded helper definitions, at zero SIMD-off
     movers.
9. **The checks (§12):**
   - the G2 generated set space (T1-T4);
   - generated candidate sequences Q1-Q9 by a D27-blinded author;
   - the full kernel test with K35 floors;
   - guard pages, ASan and UBSan on rendered text;
   - 23 sabotage rows (S820-S842).

## 2. Proposed for main's ratification (chunk-2 note / R-18)

- **The window fields:** W1-W5 now; W6 only if §9.2 is in force; W7-W10 for
  R-18 (§2.2).
- **The storage capability** (§7, §14 STORAGE).
- **`mf_plan`** (or the deferred include anchor) and table-iff-read
  (§11.1, N3a/b).
- **Define-then-emit** at the PF table point, and a single VM-hat site with
  two uses (N2's remainder).
- **N4's door assertion.**
- **The spec hunks** (§11.3), with values unchanged.
- **18 more sabotage ids, S825-S842** (§12.5). main writes requests.md.

## 3. OWED (every item, its owner, its trigger)

| item | owner | trigger |
|---|---|---|
| DRY RUN of the harness: `DRYRUN=1 L=build/scratch/r17/dry2 CORE=12 bash docs/design/memfn/probes/r17/run_time_r2.sh`. It renders, compiles nothing and lists ~640 invocations, so it checks the generator and the grid. A compile of the generated header is owed with it (`gcc -O2 -fPIC -I$L -c check_r2.c`): none of this source text has been compiled | kit manager (any idle moment; it is light) | before the slot |
| THE CHECK and its PLANTED control (`check_r2`, `check_r2_plant`), run first by the script. Expected: `R17R2 CHECK: ... mismatches=0` with every population non-zero, and `R17R2 PLANT: cache twins caught = Y of Y` | kit manager | the slot |
| THE FOLLOW-UP TIMING: `L=build/scratch/r17/slot2 CORE=<idle> R=7 MIN_MS=50 [SUBJ_TSV=...] nohup bash docs/design/memfn/probes/r17/run_time_r2.sh > build/scratch/r17/slot2.log 2>&1 & disown`. Completion line: `R17R2 TIMING COMPLETE rc=0 rows=<K> void=0 perf=<P>`. ~1 h 45 min ± 30% (estimated) | kit manager, in a quiet slot via main | after main's current chain; one heavy thing on the box |
| the bench subjects TSV for lc/dig/bkn/bpr, regenerated read-only (lossreview instruments) | kit manager | before the slot |
| the reading: `python3 -I summarize_r2.py <L>`, then the verdict (rows, order, the gate, K, W, helper vs pieces) written into setfind.md §13 | kit manager / a fresh agent | the run's completion line |
| the disassembly check (no call in an inlined helper's hot loop) | the reader | with the run |
| a light re-check panel on revision 2 (the panel's step 3) | kit manager | before any build |
| main ratifies §2's fields and the storage capability in its chunk-2 note | main | chunk-2 |
| S825-S842 allocated | main (requests.md) | at ratification |
| the G2 sequence and set families (§12.1-§12.2), authored blinded in a D27 cell | a blinded lane | the build (R17-b) |
| R17-a and R17-b themselves | kit + main, one abi event | Q-R17-2 (A): after the follow-up AND chunk-2 |
| the BE answer arm | nobody here | UNREACHED: no BE target or qemu-user |
| the official SIMD verdict | pcrec-bench via main | the SIMD arms (§11.4) |


## 4. Not done, and why

- **No run of anything** (the brief: the box is held).
- **No edit to `responses.md`.** The kit session is its only writer, and the
  text is drafted in setfind.md §14.
- `docs/dev/lanes/CLAUDE.md` gained this report's row.

## 5. Charter vs committed

| charter item | where | status |
|---|---|---|
| answer every MUST-FIX/SHOULD (and NITs) by id in a §R table; say where the rulings change an answer | setfind.md §R (36/36; C1-6, C3-1, C3-5, C3-6 marked "changed by ruling") | DONE |
| quote every ruling verbatim | §1.1 | DONE |
| the window-contract mapping, the proposed fields and reply, carried-now vs appended | §2 | DONE |
| term derivation: candidates, objective, IDDFS + budget, purity, uncoverable decline, exact/non-exact, complement, cross-check vs pcrec_cube_of | §3 | DONE |
| row contracts per form (memchr_set, stateless SWAR, mask/ring, the walk floor) | §4 | DONE |
| n = 0 / NOP arithmetic without wrap | §5 | DONE |
| endianness with no #if in body code | §6 | DONE (BE answer UNREACHED, stated) |
| hook-safe local naming | §7.6 | DONE |
| the adaptive switch | §9.1 | DONE |
| the fallback density gate with an `absent` class | §9.2 | DONE |
| define-time round-trip REFUSE | §10 | DONE |
| the one routing event: what moves, abi package, stamps, spec hunks, G1 both layers | §11 | DONE |
| main's storage question: declaration site/scope, lifetime, init, cursor guarantees, several sites, -p naming | §7.1-§7.6 | DONE |
| stateful forms at SWAR and SIMD, with which fits which site; the PROOF | §8 (VM hat entry+retry and DFA PF re-entry, §7.5/§15) | DONE |
| re-derive C3-1/C3-6/C3-7 under D155 add. 3 | §R, §11 | DONE |
| checks: G2 set space + candidate sequences (blinded), kernel test with K35, guard/ASan/UBSan, rows.tsv/floors/witnesses/options.def/registry, sabotage with reach + more ids | §12 | DONE |
| the follow-up harness as source text, not run: stateful twins (mask, ring; SWAR, sse2/avx2), adaptive twin, exhaustive sequence check; the full grid; exact command, completion line, wall estimate | §13; `probes/r17/*_r2.*` | WRITTEN; runs OWED |
| pcrec-side needs as responses.md text (STORAGE marked; fields; N1; N2 remainder; N3; N4; spec) | §14 | DONE |
| standing design questions + UNLOCKS with triggers | §16, §17 | DONE |
| reconcile F-R9-7 / opt3 (C3-11) | §15 | DONE |
| corrections to r17s_report's stale facts | §1.3 | DONE |
| CLAUDE.md updates | `docs/design/memfn/CLAUDE.md`, `probes/CLAUDE.md`, `probes/r17/CLAUDE.md` | DONE |
| this report | here | DONE |

## Revision 2.1 (lane r17r21, 2026-10-12, opus; text only)

On `lane/r17r` from the kit tip `b7d086ff`. It applies the r4 light re-check
(`docs/dev/reviews/2026-10-12-r4-memfn-setfind.md`: 24 ids, r3's C1-2
residual, and the sabotage renumbering) to `docs/design/memfn/setfind.md`.
The box was held by main's validation chain, so **nothing was run**: no make,
no gcc, no python. Every disposition was checked against the code it cites
(`memfn/include/memfn.h`, `memfn/src/{pffind,ofsskip,runcmp}.c`,
`fields.def`, `src/gen/emit_dfa.c`, `src/gen/emit_vm.c`,
`src/gen/memfn_sites.c`, `src/core/internal.h`, the named test readers, and
D155 add. 3 / D157 / D161 add. 1-3 from the main tree) before it was written
in. The rulings (Q-R17-1, Q-R17-2, D161 add. 3) are unchanged. The note's
§R4 maps every id to where it is answered.

### What changed, per id

| id | change |
|---|---|
| K1-1 | A helper that reads pcrec's table takes it as a PARAMETER, named at each use by `table_name` (`<p>_ofsskip`'s precedent). pcrec's tables are function-local statics (`emit_u8_table`, `emit_dfa.c:3446`), so revision 2's adapt text did not compile. §4.3, §9.1, §R C3-6 |
| K1-2 | Revision 2's S833 (now S834) was an equivalent mutant at end_back 1. It is replaced by an end_back-0 overlapped block at `hi - 63` (reads `s[n]`), caught by the guard page, ASan and a `top <= hi` trace trap. §8.2, §12.5 |
| K1-3 | Q9 also at `-O0`, with a period-3 word fill at all three phases so the garbage claims a cached block, plus a C-check that `mf_locals` initializes every read scalar. S832's detector is that pair. §12.2 |
| K1-4 | `mf_use` refuses `s`/`n` text that differs from the define's (NARROWED: `end_back` is the site's, so a use cannot restate it); a C-check that `s`/`n` are not assigned after the storage point; a trace rendering that re-probes every cache hit. §4.2, §7.4, §12.4a |
| K1-5 | CORRECTED (below). §7.5 |
| K1-6 | The order define → locals → table-if-read → use is stated. The DFA point is keyed on the forward PF site, in `unanch_scan`. The VM half is CORRECTED (below). §7.1, §11.1 |
| K1-7 | `-Wjump-misses-init` over the movers, filtered to `<stem>__`, with its computed-`goto` limit stated (neither holding body has a computed `goto`; the DFA bodies' direct scan-loop gotos are analyzed). §7.2 |
| K1-8 | The ring witness at `-O2`/`-O3`; "placed, never read" refused at `mf_art_end`. §4.3, §7.1 |
| K1-9 | Cache-path rows S830-S834 and S842 get DYNAMIC reach (gcov counts of the cache-hit line, literal floor 1 per witness). §12.5 |
| K1-10 | The claim is restated, the pseudocode searches `S` and `¬S` at every k, AND the candidate rule gains sub-terms (every 128-long arc of a longer run), so objective 1 is exact over all covers by a stated dominance argument. Objectives 2-4 rank candidate covers only, stated. G2's oracle (b) re-derives the term space. §3.2, §3.3, §12.1 |
| K1-11 | The stem is opaque, written only through `puts`/`vprintf` (never an escaper, the placeholder's "one seam"); a placeholder stem in G2's shadow set; a C-check that pcrec writes no `<stem>__` identifier. §7.6 |
| K1-12 | Superseded: `mf_plan` is dropped |
| K2-1 | The DFA PF site is defined from a new `u.pf.emit_block` on the set rows (`ofs_site_define`'s precedent), and the table is emitted from the define's report. The flush half is CORRECTED (below). §11.1, §14 N2 |
| K2-2 | "Move once" holds for the PF sites only. W3 is not extended to the `ret_pred` reply (not justified). "R-18 needs no re-routing" is withdrawn for the handoff and the offset-skip FUNC. §0, §2.1, §2.2 |
| K2-3 | Routing-once, not bytes-once, with the §13 outcome that decides whether W6 lands with R-17. §0, §2.2 |
| K2-4 | D161's origin (the span's beginning), which makes W1 SIGNED (MLINE is -1); `MF_MOVE_UNBOUNDED` reserved; a non-wrapping W3 keyed on `back = move_back - d_min`; a `window_stated` bit (W0), refused unstated on FIND and stated on non-FIND or reverse sites. §2, §4.2, §11.1 |
| K2-5 | `decl_point` (a host capability) replaces `locals_offered`; `needs_locals` dropped; §14's glosses stripped; `freq` named as the one density carrier (an unlock; folding `rank_ppm` is main's to rule). §2.2, §9.2, §14, §17 |
| K2-6 | `mf_plan` dropped; `reads_table` is reported by the define (`mf_defined`). The include half is CORRECTED (below). §11.1, §14 N3 |
| K2-7 | The [SABANCHOR] exact-count gate and a derived re-aim list in R17-a; S478 named (anchor at `emit_dfa.c:7209`). §11.1, §12.6 |
| K2-8 | The seven named readers, each verified at its line and given a fate, both arms, and a floor pinned before R17-b. `run_offset_skip.sh` §2c is unchanged (the offset-skip sites do not move). §12.6 |
| K2-9 | The point is in the forward-loop caller; the stem is derived from the holding function (`<fn>_pf`), which gives the rev-end relocate its own; "placed twice" refused. §7.1, §7.6 |
| K2-10 | §R C3-6 re-derived; C3-8 decided (`__builtin_memcpy`; C4 needs no change, since `memfn/` and `tests/memfn/` are exempt from its scan); C3-10's K derivation path stated. §3.3, §6, §R |
| K2-11 | The hybrid's prefilter function is entered once per VM re-seed: storage rows are admitted there only if §13's `reset=1`/`reset=4` rows show no loss, else a host fact (`activation`) makes them decline, and that site keeps today's walk under K-1. §7.5, §17 |
| K2-12 | `pf_open` is `emit_dfa.c:6228`; `fn_ref`'s `fields.def` doc gains the STMT reading at landing. §1.3, §2.2 |
| r3 C1-2 | A byte-swapped LE answer test: a reversed-load macro over `__builtin_memcpy` plus a flipped `__BYTE_ORDER__`, through T5 and Q1-Q7. A real BE target stays UNREACHED. §6, §R |
| §12.5 ids | S825-S842 → S826-S843 (main's allocation, `ef3fa88b`), by one, everywhere. Five refusal rows are added with ids still to request |

### Dispositions corrected against the code (with evidence)

1. **K1-5 (one function per site).** The disposition, "compare the body-sink
   pointer at `mf_locals` with every `mf_use`", cannot work. pcrec builds a
   fresh stack `PcrecMfSink ps;` in every kit call
   (`src/gen/memfn_sites.c:357,371,379`), and every function of an artifact
   writes into the one buffer `job->csb`. So neither the sink pointer nor its
   `u` separates two functions. Done instead: a use in a function without the
   storage is an undeclared-identifier COMPILE error; storage declared in two
   functions needs two `mf_locals`, refused as "placed twice" (K2-9). The
   function token stays an unlock.
2. **K1-6, the VM half (where the VM hat is defined).** The order holds, but
   the define cannot be "inside the entry emitter". The helper must precede
   `<searchfn>_run` (C requires a declaration before use), and the prologue
   is written (`emit_vm.c:14000`) BEFORE `vm_emit_search_body` writes `_run`
   (`:14009`). Done instead: the VM hat is defined at file scope beside
   `pcrec_emit_req_run_blocks` (`emit_vm.c:13130`, whose own comment says "at
   file scope above the one search loop"), and the locals, table and entry
   use stay at the entry.
3. **K2-1, the flush half.** "State the flush-helpers kit change honestly as
   part of R17-a": the honest statement is that NO flush change is needed.
   Both routes now define at a file-scope point above the function, and the
   kit writes the helper there, as a FUNC definition already does.
   `mf_flush_helpers` writes only `<p>_w<W>` (`memfn/src/runcmp.c:466-490`)
   and stays so. Revision 2's flush claim was also wrong on ORDER (the
   prologue flush runs before `_run` exists), which the review did not name.
4. **K2-6, the include half.** The prologue precedes the define on BOTH
   routes (`emit_dfa.c:13459` before `pcrec_emit_dfa_engine`;
   `emit_vm.c:14000` before `:14009`), so "the VM needs no prediction" holds
   for `reads_table` only. Rather than build the back-patchable include slot
   (D77: no row needs it), the R-17 rows are made header-free
   (`__builtin_memchr`, `__builtin_memcpy`). The existing
   `pcrec_memfn_art_end` assertion (a kit text needing `<string.h>` the
   prologue did not include fails the compile) is the control. The slot is
   filed with a trigger.

Two smaller corrections found while verifying: revision 2's S839 (now S840)
named `-Wunused-const-variable`, but the table is a function-local static, so
the warning is `-Wunused-variable`. And revision 2's §7.1 put the DFA
declaration point inside `emit_scan_loop`, which `emit_reverse_block`
(`:11122`) and the anchored match-here (`:11760`) share, so it would have
placed the storage once per copy.

### The harness

Unchanged. The r4 verdict says it measures forms, not the contract. K1-2's
replaced plant and K1-3's `-O0` control are §12's checks on the kit's
RENDERED text, built with R17-b. The harness's twins reset their state per
sequence (`check_r2.c`'s `sreset`) and carry no end_back-0 over-read plant,
so neither disposition touches them. `run_time_r2.sh`'s command and its
completion line `R17R2 TIMING COMPLETE rc=N rows=K void=V perf=P` stay
valid. §13.3 now cites lane r17dry's results (0 mismatches over 4.04 G
calls, planted 152/152, ASan+UBSan clean, 619 invocations, ~80 min
estimated).

### OWED (each item, its owner, its trigger)

| item | owner | trigger |
|---|---|---|
| THE FOLLOW-UP TIMING (command and completion line in setfind.md §13.3, unchanged) | kit manager, in a quiet slot via main | seambuild's chain DONE (the r4 verdict: it does not wait for 2.1) |
| the reading (`summarize_r2.py`), the verdict into setfind.md §13, K's value by §3.3's path, the disassembly check | kit manager / a fresh agent | the run's completion line |
| the §13 `reset=1`/`reset=4` reading that decides K2-11 (storage rows on the hybrid's prefilter site, and whether the `activation` fact is taken) | the reader | with the verdict |
| main ratifies the window fields (W0-W5, D161's origin, signed W1), `decl_point` and the storage capability in its chunk-2 note | main | chunk-2 |
| ids for the five refusal rows of §12.5 | main (requests.md) | R17-a's edit set |
| the R17-a edit set and its derived sabotage re-aim list (S478 first), with the [SABANCHOR] exact-count gate | the R17-a build lane | R17-a |
| the reader populations of §12.6 (deny-arm floors pinned BEFORE R17-b; default-arm counts from the R17-b mover census) | the R17-b build lane | before / at R17-b |
| the G2 sequence and set families (§12.1-§12.2, incl. Q9 at `-O0`, the placeholder stem, the byte-swapped LE test), authored blinded in a D27 cell | a blinded lane | the build (R17-b) |
| R17-a and R17-b themselves | kit + main, one abi event | Q-R17-2 (A): after the follow-up AND chunk-2 |
| a real BE target's answer | nobody here | UNREACHED: no BE target or qemu-user |
| the official SIMD verdict | pcrec-bench via main | the SIMD arms (§11.4) |

### Charter vs committed

| charter item (the r17r21 brief) | where | status |
|---|---|---|
| apply every r4 disposition (K1-1..K1-12, K2-1..K2-12), each verified against the code it cites | setfind.md, §R4 | DONE; four corrected with evidence (above), K1-4 narrowed, K1-12 superseded |
| the r3 C1-2 residual | §6, §R C1-2 | DONE |
| renumber the sabotage rows to S826-S843 (S825 taken) | §8.2, §10, §12.5, every citing section | DONE |
| a header line "revision 2.1 (2026-10-12, r4 light re-check)" | setfind.md line 3 | DONE |
| a §R4 table mapping each r4 id to where it is answered | setfind.md §R4 | DONE (24 + C1-2 + ids) |
| fixed §R rows for r3 C3-6, C3-8, C3-10, C3-2, C1-2 | setfind.md §R | DONE |
| §14 draft: capabilities rephrased (K2-5), `mf_plan` dropped (K2-6 holds for the selection half), the N2 remainder corrected (K2-1) | setfind.md §14 | DONE |
| harness changes only if a disposition requires them, run OWED, command and completion line valid | §13.3 | NOT NEEDED (reasoned above); command and completion line unchanged |
| the rulings not reopened; K2-2/K2-3 claims restated honestly | §0 item 1, §2.1, §2.2 | DONE |
| CLAUDE.md files where roles change | `docs/design/memfn/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md` | DONE (no file changed role; the entries record the revision) |
| this "revision 2.1" section | here | DONE |
| run nothing | — | DONE: no make, gcc or python was run |

## Revision 2.2 (lane r17r22, 2026-10-12, opus; text only)

On `lane/r17r` from the kit tip `b50d4a80`. It folds every settled direction
of 2026-10-12 and the slot2 timing reading into
`docs/design/memfn/setfind.md`; read its §R5 first. **Nothing was run**: no
make, no gcc, no timing. The one number computed here (the `reset=call` row
across 20k/70k/300k/800k for the three chosen forms, setfind.md §9.2) is
python over the committed `probes/r17/out/slot2/times.tsv`; every other
number is cited from `probes/r17/reading_slot2.md`.

### What changed

1. **Forms (slot2, D155 add. 4.1).** One stateful row, `pf_terms_mask`, whose
   body is `next_candidate(&state, lo)`: `mask8_swar` at SWAR now,
   `mask64_sse2`/`mask64_avx2` as the later SIMD arms. NOT built, each with
   its measured reason and a filed trigger: the ring, the adaptive switch,
   the stateless term-OR, `pf_memchr_set`, and `mask64_swar` (admitted only
   where the state survives the whole call AND spans are ≥ 64; no site states
   either). The state struct binds `s` and `n` at the declaration, so the use
   passes only `lo` (§4.3).
2. **Primitives (D155 add. 4).** §3.4a: per-width vector type, `load_vector`,
   eq/cube/range, `first_lane`, plus two connectives (`vor`, `lane_mask`) the
   measured forms need. One guarded shared block per file, keyed to (abi,
   helper-set version), emitted only where a site uses a primitive (absent at
   R17-a, first in R17-b's abi event). Its bytes depend on the key only (every
   width of its set), or "first block wins" breaks in a mixed-layer file.
   Reserved stem PROPOSED as `pcrec_mfk_`.
3. **Endianness (C1-2 closed by construction).** The byte-order ternary lives
   only in the block's SWAR `load_vector`; `first_lane` is ctz at every
   width (§6, §12.7).
4. **K = 4**, read on the sparse regimes; the narrowing of §3.3's rule is
   stated (no K wins dense percall).
5. **§9.2 rewritten (D162 add. 1).** ADMIT when density is absent; decline only
   on positive density ≥ `T_DENSE` = 300k AND a state-losing call pattern
   (`B_EVEN` = 3 candidates per state lifetime); both labelled
   `MEASURED-UNOFFICIAL (slot2)`. Total without data (a class table). No input
   reaches the decline arm today, so R17-b reads no density fact and W6 is not
   part of R-17; the arm is a later form event. The state-lost residual is
   [FINDALL-NEXT]'s (break-even 2-3 candidates for `mask8_swar`).
6. **§11.** The shape table (R17-a zero-mover with no block; R17-b with the
   block, the abi event and the bench gate; then the SIMD arms). New §11.2a:
   the bench relay, with the 64K predictor caveat. §11.4: D147's open check at
   64K dense; AVX-512 as an unfiled later width.
7. **§12.** A rev 2.2 sabotage plan: S822/S834/S836 re-aimed; S839 kept
   reserved for the decline arm; **S838, S842, S843 REASSIGNED** (from adapt,
   ring and memchr_set) to the shared block's three rows; **seven more ids
   needed** (five refusal rows from rev 2.1, two width-dependent rows; ten if
   main prefers the three left unused). New §12.7: block identity, presence,
   the key's `#error`, the mixed-layer TU, byte order in one place, body
   invariance, the hook comparisons.
8. **§13.5:** the follow-up recorded as RUN, its decisions and every
   hypothesis's outcome. **§14:** N1 wording (R17-b does not read the object),
   THE GATE paragraph, N5 (the reserved stem), the id ask. **§15-§17**
   updated; §17 gains the rev 2.2 unlock table ([FINDALL-NEXT] cross-call
   state, the stateless-first twin, AVX-512, mask64 SWAR, the ring, adapt,
   memchr_set, the decline arm, word loads into the block, other sites over
   the primitives). **§R5:** each settled direction and each slot2 answer to
   its section.

### The bench draft

`docs/design/memfn/setfind_bench_request.md`: self-contained, for main to
relay (D78). Phase A gates R17-b (SIMD-off, both boxes); phase B is the SIMD
arms' later per-box acceptance. Cells (the 14 named R-17 cells by bench name,
the `lc`/`dig` dense controls, every mover from main's census incl. hybrid
prefilter movers), arms (A1 walk, A0 `mask8_swar`, A1′ A/A; B0/B1 later),
regimes (find-all, per-call) with density, run profile and candidates per
match per subject, a PROPOSED regression floor (ratio > 1 + max(0.05, A/A
spread) with trials agreeing, plus the absolute A/A delta for ns-scale cells),
the 64K caveat, and seven questions.

### OWED (each item, its owner, its trigger)

| item | owner | trigger |
|---|---|---|
| main ratifies §2 (W0-W5, signed W1), `decl_point` and the storage capability in its chunk-2 note | main | chunk-2 |
| the bench relay (phase A) on the R17-b branch, both boxes | main relays and schedules; pcrec-bench runs | R17-b built, before merge |
| confirm or replace the proposed regression floor (bench draft §4) | main + pcrec-bench | with the relay |
| allocate seven more sabotage ids, and accept or refuse the reassignment of S838/S842/S843 | main (requests.md) | R17-a's edit set |
| the R17-a edit set and derived re-aims ([SABANCHOR] count gate), incl. the `mf_locals` hook refusal | the R17-a build lane | R17-a |
| R17-b: `terms.c` (K = 4 labelled), `pf_terms_mask`, the shared block renderer (helper-set version 1), abi bump, spec hunks (registry floor 6 → 7; the block's guard sentence if `match_api.md` documents K80's) | kit + main | after chunk-2 and R17-a |
| the disassembly check over kit-RENDERED movers: no call in the inlined hot loop; the syn8 anomaly; `c->s`/`c->n` kept in registers | the R17-b build lane | with R17-b |
| the reader populations of §12.6 (deny-arm floors pinned before R17-b) and the walk-witness re-pick (`\w` is coverable at K = 4) | the R17-b build lane | before / at R17-b |
| the G2 families (§12.1-§12.2, incl. Q10 width invariance and per-width block edges), authored blinded | a blinded lane | R17-b |
| the SIMD arms and their phase-B bench verdicts | kit, then pcrec-bench via main | after R17-b merges |
| the decline arm of §9.2 | kit | the analysis object carries a byte-rate kind AND a call-pattern kind, or pcrec states `activation` |
| the stateless-first twin | kit | a bench cell where `mask8_swar` loses to the stateless SWAR form beyond the floor, or a kit round with slot time |
| a real BE target's answer | nobody here | UNREACHED |

### Charter vs committed

| charter item (the r17r22 brief) | where | status |
|---|---|---|
| D161 add. 3: R-17 is the degenerate one-span window search; §2 kept, PROPOSED for chunk-2 | §2, §0 item 1, §R5 #1 | DONE |
| D155 add. 3+4: per-width primitives; one guarded shared block keyed abi + helper-set version (K80); emitted only when used (R17-a zero-mover, first in R17-b's abi event); endianness in `load_vector` (C1-2 closed), ctz always; reserved kit stem | §3.4a, §6, §11, §12.7, §14 N5 | DONE (adds `vor`/`lane_mask`; block bytes key-only; stem PROPOSED) |
| D155 add. 4.1: `next_candidate(&state, lo)`; per-width implementation by measurement; the body never changes | §0 item 2, §4.3, §8.1-§8.2, §11.4, §12.7 | DONE |
| measured per width: SWAR mask8_swar, SSE2 mask64_sse2, AVX2 mask64_avx2 | §4.1, §4.3, §8.1 | DONE |
| ring and adaptive NOT built, reasons recorded, filed notes | §4.1, §8.3, §9.1, §17 | DONE |
| mask64_swar only where state survives the whole call AND spans ≥ 64 | §4.1, §4.3, §17 | DONE (designed, population zero, not built) |
| K = 4 for SIMD-off, with how it was read | §3.3 | DONE |
| mask64i == mask64: composable pieces cost nothing | §4.3 | DONE |
| stateless-first as an unbuilt twin with a trigger | §3.4, §17 | DONE |
| AVX-512 as an unfiled later width row | §11.4, §17 | DONE |
| D162: one analysis object; total without data | §2.2 W6, §9.2, §14 N1 | DONE |
| ADMIT when absent; decline only on positive density ≥ ~300k with a state-losing pattern; §9.2, its gate field and predicate rewritten; thresholds labelled per D149 with source | §9.2, §4.2, §7.5 | DONE (`T_DENSE`, `B_EVEN`) |
| state-lost residual to [FINDALL-NEXT] with break-even 2-3 for mask8_swar | §9.2, §15, §17 | DONE |
| bench relay draft: cells (named incl. lc/dig/bkn/bpr + dense controls), arms (walk vs forms, both layers), regimes (find-all, per-call, density and run profile), the numeric floor, questions, the 64K caveat | `setfind_bench_request.md`, §11.2a | DONE (floor PROPOSED) |
| §8 updated only where forms/next_candidate change it | §8.1, §8.2, §8.3, §8.4 | DONE |
| §11 routing shape: R17-a zero-mover, R17-b with the bench gate | §11 (shape table), §11.1, §11.2, §11.2a | DONE |
| §12 checks and sabotage: drop unbuilt rows, add block + next_candidate rows; ids S826-S843, say if more needed | §12.5 (rev 2.2 plan), §12.7 | DONE: 3 reassigned, 7 more needed |
| §13 records the follow-up as RUN | §13 title, §13.5 | DONE |
| §14 responses draft: gate wording, analysis-object wording | §14 | DONE |
| §17 unlocks: [FINDALL-NEXT], stateless-first, AVX-512 | §17 (rev 2.2 table) | DONE |
| a "revision 2.2" header line and a §R5 table | setfind.md header, §R5 | DONE |
| keep everything else; remove nothing still true | throughout (superseded text marked `[rev 2.2]` in place; only §9.2's body was replaced, its withdrawn rule summarized) | DONE |
| docs/design/memfn/CLAUDE.md if roles change | the setfind.md entry, the new bench-draft entry | DONE |
| this section | here | DONE |
| run nothing | — | DONE (python over a committed TSV only) |

## Revision 2.3 (lane r17r23, 2026-10-12, opus; text only)

Applies `docs/dev/reviews/2026-10-12-r5-memfn-setfind22.md` (critic K3, 11 ids,
no blocker) to `docs/design/memfn/setfind.md`, revises the bench draft, and
writes the I-148 corrigendum. Nothing was run (no make, gcc or timing). Each
disposition was checked against the code it cites. Branch `lane/r17r`, from
the kit tip `17e09a86`. The settled directions are not reopened. Read
setfind.md §R6 first.

### What changed, per id

| id | change | where |
|---|---|---|
| K3-1 | one sub-block per width (W8 / V16 / V32), each guarded and emitted only where a site uses that width; a SIMD-off artifact holds W8 only (no SIMD text), so the arms move no SIMD-off byte and a new width moves only its users; V16/V32 header-free; S836/S842/S843 re-aimed per width | §3.4b (new), §0 item 5, §3.4a, §11.4, §12.5, §12.7, §14 N5, §16.3 |
| K3-2 | the body guard reads `<stem>__c.n`; the use pastes only `lo`; the trace form of each use traps unless `c.n == n && c.s == s` (restores r4 K1-4); S824 re-aimed, S851 and one unnumbered row added | §4.2, §4.3, §5, §7.4, §8.2, §12.4a, §12.5, §12.7 |
| K3-3 | R17-b const-qualifies `subject`/`subject_length` in the definitions of the bodies holding a stateful site (`emit_dfa.c:1806`, `emit_vm.c:13137`), inside its abi event, on its movers only; the textual C-check becomes the fallback; S852 | §7.4, §11.2, §12.5, §12.7 |
| K3-4 | (P) = uses per activation below `B_EVEN` (median activation, PROPOSED); the per-retry fact is a proxy only; the `mfk-upa` trace counter named and filed; "state-losing by construction" dropped (bench draft, corrigendum) | §7.5, §9.2, §12.4a, §12.5 S839, §14, §17 |
| K3-5 | the bench gate: reproduce-on-rerun; F from the bench's standing spread, else at least 3 layout-perturbed A/A pairs; the absolute criterion on every cell; the 0.05 floor withdrawn | bench draft §3/§4/Q6, §11.2a, §14, the corrigendum |
| K3-6 | `T_DENSE` `MEASURED-BRACKET (70000, 300000]`; `B_EVEN` `UNMEASURED DEFAULT: 3` inside (1, 4); a point rate reads as `[r, r]`; (D) is corpus evidence | §9.2, §16.3 |
| K3-7 | N6 drafted with its cli.md / match_api.md hunk; same-commit inside R17-b if main agrees, else its own pcrec request landing no later than R17-b | §14 N6, §11.2, §11.3, §12.5 |
| K3-8 | the version dropped, and the guards carry no value: K80's guard is the key | §3.4b, §11.2, §12.5 S838, §12.7, §14 N5, §16.3 |
| K3-9 | `mf_locals` binds (the one comparison); `mf_use` checks neither | §4.2, §4.3, §8.2, §11.1, §12.7 |
| K3-10 | the renderer lands with R17-b; reconciliation with main's D155 add. 4 note recorded | §11.1, §11.2, §14 N5 |
| K3-11 | placeholder soundness stated (equal unrendered ⇒ equal rendered; only a false refusal possible) | §7.6 |

Also: §17 gains the r5 unlocks (the bound struct as the cross-call record, the
`mfk-upa` counter, `inputs_const`, per-width sub-blocks for other sites);
§16.2 notes the new independent controls; §R6 maps every id.

### Dispositions refined against the code (with evidence)

- **K3-7: the rule must also refuse the bare `pcrec_mfk`.** The disposition
  said "prefixes beginning `pcrec_mfk_` (case-folded)". Every generated name
  is `<PREFIX>_<suffix>` (cli.md §1.6¶1; `derived_name` in `emit_dfa.c`), so
  `-p pcrec_mfk` gives `pcrec_mfk_search` and upper-case `PCREC_MFK_*` macros
  inside the stem, and would pass the literal rule. N6 refuses `P` iff
  fold(`P`) is `pcrec_mfk` or begins `pcrec_mfk_`.
- **K3-8: the key is K80's guard, not an abi value in the kit's guards.** The
  disposition offered "specify the encoding, or drop the version", presuming
  the kit's guard could carry the abi. It cannot without a new contract field:
  `memfn.h` carries only `MF_SITE_ABI`, and `mf_art` has no
  `PCREC_ARTIFACT_ABI` (`emit_dfa.c:54`). It does not need to: K80's valued
  `PCREC_RX_ABI_H` guard and its `#error` are emitted in every artifact's
  prologue, before any engine or kit text (`emit_dfa.c:13027` in the
  self-contained `.c`; `:3417` in the header the `.c` includes), so a mixed-abi
  TU fails at K80 whatever the order of the sub-blocks. So the version is
  dropped AND the sub-block guards are plain `#ifndef`/`#define`. S838's rev 2.2
  plant (keyed on the abi only, version dropped) became the design, so S838 is
  re-aimed to "all widths share one guard", UNREACHED until the arms.

No disposition was overturned outright.

### Findings verified on the way (each a premise of a disposition)

- x86-64's baseline defines `__SSE2__`, so revision 2.2's SSE2 primitives were
  live text in every default x86-64 SIMD-off artifact (K3-1's premise).
- No emitted string in `src/gen/` writes `subject` or `subject_length`; the H3
  end-window sites write `window_end` only (`emit_vm.c:13311-13312`,
  `:13444-13448`); the VM match-here entry already declares
  `const unsigned char *const subject` (`emit_vm.c:12786`) (K3-3's premise).
- `valid_prefix` (`compile.c:141`) accepts any C identifier up to 60
  characters; it serves both the CLI and `pcrec_options.prefix`
  (`compile.c:2132`) (K3-7's premise).
- Observed, not filed by this lane: `-p pcrec` produces `PCREC_<STAMP>` macros
  in the same upper-case namespace as pcrec's fixed `PCREC_*` names
  (match_api.md's `PCREC_ERR_*`, `PCREC_RX_ABI_H`). No collision exists today;
  it is main's to judge whether it deserves a row.

### The corrigendum

`docs/design/memfn/setfind_bench_corrigendum_I148.md`: self-contained, for
main to relay to pcrec-bench as a follow-up to I-148 before the run. It quotes
I-148 §4 items 2-3 before and after (plus item 4, reproduction), the A1′ arm,
the WIN note and Q6; and §2 item 3's withdrawn "state-losing by construction"
before and after, with the §5 and Q3 asks that follow from it.

### OWED (each item, its owner, its trigger)

| item | owner | trigger |
|---|---|---|
| relay the corrigendum to pcrec-bench (follow-up to I-148) | main | now, before the phase A run |
| allocate TWO more sabotage ids for R17-b (the trace bound-vs-live trap row; the N6 refusal row, which moves to N6's own request if N6 does not ride R17-b) | main (requests.md) | R17-b's edit set |
| rule N6's placement: same-commit inside R17-b, or a separate pcrec request landing no later than R17-b | main | before R17-b |
| annotate the D155 addendum 4 manager note: the block's renderer and first appearance are R17-b's, not R17-a's (K3-10) | main (decisions.md) | at its next decisions edit |
| fold the per-width sub-blocks, the dropped version and N6 into the chunk-2 note with N5 | main | chunk-2 |
| two ids at the SIMD arms (body invariance by width; the W = 64 pack) | the kit asks, main allocates | the arms' request |
| R17-b additionally carries: the const parameters, the `<stem>__c.n` guard, the trace trap, the W8 sub-block renderer, and (if ruled) N6 with its spec hunk | kit + main (R17-b build lane) | R17-b |
| the `mfk-upa` trace counter | kit | the decline arm is coded, or the bench answers Q3 "cannot count it" |
| a finer reading of `T_DENSE` or `B_EVEN`, whichever the decline arm's first input sits near | kit | the decline arm |
| everything OWED by revision 2.2 above that is not superseded (chunk-2 ratification, the bench relay, R17-a's edit set, the disassembly check, reader populations, the G2 families, the SIMD arms, the stateless-first twin, a BE target) | as listed there | as listed there |

### Charter vs committed

| charter item (the r17r23 brief) | where | status |
|---|---|---|
| (A) a "revision 2.3" header line | setfind.md header | DONE |
| apply all 11 r5 dispositions, each verified against the cited code | §R6, the sections it names | DONE (9 applied, 2 refined: K3-7, K3-8) |
| K3-1: per-width sub-guards, each emitted on use; SIMD arms at zero SIMD-off movers; which width a SIMD-off artifact carries (W8 only) | §3.4b, §11.4 | DONE |
| K3-2: the guard reads `<stem>__c.n`; the trace trap restores K1-4 | §4.3, §5, §12.4a | DONE |
| K3-3: const subject inputs in stateful bodies, in R17-b's abi event | §7.4, §11.2 | DONE |
| K3-4: (P) = uses per activation; the trace counter named | §9.2, §12.4a | DONE (`mfk-upa`, filed) |
| K3-6: the D149 labels | §9.2, §16.3 | DONE |
| K3-7: N6, pcrec-side, with a cli.md hunk; same-commit in R17-b if main agrees, else a separate request | §14 N6 | DONE (rule refined to include the bare `pcrec_mfk`) |
| K3-8: specify the key or drop the version, pick and justify; S838 to match | §3.4b, §12.5 | DONE (version and value dropped; K80 is the key; S838 re-aimed) |
| K3-9..K3-11 made consistent | §4.2, §4.3, §8.2, §11.1, §7.6 | DONE |
| sabotage ids re-tabulated with S846-S852; say if more are needed | §12.5 (rev 2.3 table), §14 | DONE: 7 assigned; 2 more for R17-b, 2 at the arms |
| a §R6 table mapping each r5 id | setfind.md §R6 | DONE |
| §14's responses draft updated (N6, the per-width block) | §14 | DONE (N5 restated, N6, ids, gate corrections) |
| (B) the bench draft per K3-4 and K3-5 | `setfind_bench_request.md` (revision 2) | DONE |
| (C) the I-148 corrigendum, short and self-contained, before/after quotes | `setfind_bench_corrigendum_I148.md` | DONE |
| docs/design/memfn/CLAUDE.md for the new file | the setfind, bench-request and corrigendum entries | DONE |
| this section | here | DONE |
| run nothing | — | DONE |

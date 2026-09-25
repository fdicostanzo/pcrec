# The compare stack: a coordination map for the literal, class, fold and scan mechanisms

Owner row: `[OPT-LITSCAN]` (D122 + its ADDENDUM). Lane `cmpmap`,
2026-09-25, written from main at 897a97f0. Frank asked for it the same day: "a bunch of
stuff that all overlaps needs thoughtful coordination."

**What this is:** a MAP. It records where each mechanism sits today, which
definitions exist more than once, which primitive is the single source of
truth for each fact, what each member row consumes and must not re-derive,
and the order in which the rows should land, with the measurement that gates each
step (D77). **What this is not:** a design of any member. Every "form" named
below is today's shipped form or a row's own recorded direction. Nothing
here decides an emitted shape.

**Standing rule (D122 ADDENDUM), restated once because every row below
answers to it:** the kit is an OUTCOME, not a mandate. A site becomes a
caller only where the shared primitive fits it as well as its own form does,
on the measurement. A site that keeps its own form records why in §5, in
this file. The pricing is PAY-FOR-WHAT-YOU-USE: an all-exact run gets the plain exact
compare, and the K/T mask appears only where a position is caseless or
another non-singleton cube. The one thing that is ruled out is two
implementations of the SAME search that differ only by call site.

**Keeping it true:** a change that makes a site join the kit, leave it, or keep its own form
updates §2's row and §5's declaration in the same commit. This is the same
same-change discipline D80 applies to the spec.

---

## 0. Findings first

1. **The manager's layer frame holds, with three refinements (§1).**
   (a) The byte CUBE `(K, T)` is not an L1-only object. It is the operand at
   three layers: one-position membership (L1), the per-position lane of a run
   compare (L2), and a candidate-scan operand (L3). So `cube_of` is the
   shared primitive across the stack, and it belongs below all three.
   (b) Whether the operand is fixed at compile time or at run time is an
   axis that cuts across L2 and L3, not a layer of its own.
   (c) **The DFA route has no L2 site at all.** A literal run dissolves
   into transition-table states. On that route an L2 compare can only land
   through L3 (the prefilter or the pre-check) or through
   `[ENG-DIRECT]`/`[ENG-ISL]`.
2. **The literal compare "these bytes at these offsets" is spelled six ways
   today (§3 D6):** the VM per-byte chain, the island's single-child chain,
   the cursor rung's `&&` chain, REQ_RUN's constant `memcmp`, the offset-k
   verify chain and the run-time `$_span_match` loop. Only REQ_RUN's form
   gets gcc's fused wide compare (`vmlit_trigger_read.md`).
3. **Four emitted `memchr` scanners (§3 D5).** Two of them run the SAME
   search in one function on `router-prefix-order`: `DFA_PF_MEMCHR` and the
   REQ_RUN pre-check, both on `/`, which is the measured +80.8%. That pair
   is D122's named duplication, and it is exact-only. It needs no mask.
4. **The four losing WAF cells are not served by `[WORD-FOLD]`'s VM fused
   compare, and they are not all served by one mechanism.** Stamps read by
   this lane (§6.3): all four route through the DFA. None of them executes a
   literal-run compare today. Two have `RX_REQ_BYTE "none"` and one has
   `RX_DFA_PREFILTER "none"`. **This challenges the manager's sequence.**
   Their lever is at L3, and which L3 lever it is remains unattributed.
5. **ASCII case fold: one table, four spellings (§3 D1).** Three are guarded:
   `cls_casefold` by construction, `$_span_match_caseless` by
   `fold_agreement_check.c`/S116, and the UCD→ASCII restriction by
   `fold_agreement_utf8_check.c` part C. The fourth is not: `vm_cls_shape`'s
   FOLD recognizer at `src/gen/emit_vm.c:1633` re-spells "letter pair" as
   `(lo^hi)==0x20 && lo in 'A'..'Z'`. Drift there moves form selection, not
   answers.
6. **`cube_of` exists three times, all outside `src/` (§3 D2):**
   `studies/cls_tree_study/kit.py:293`, `studies/cls_tree_study/discover.c:90`
   (section-relative) and `docs/dev/optloop/wf/wf_run_probe.c:131` (absolute
   byte K/T plus an exact 256-point check). No agreement check ties any of
   them to anything in `src/`. `src/`'s only cube-shaped decisions are the
   two special cases, `nfree==0` (`pcrec_cls_single`) and `m=0x20`
   (`VM_CLS_SHAPE_FOLD`).
7. **The byte-frequency prior has four read sites in three files, and they
   disagree about encoding (§3 D7).** `reqbyte.c` (`bytekey`) and
   `emit_dfa.c:5499` (`req_byte_dominated_by`) gate it to `byte`.
   `prefix_k.c`'s offset-k cost model (`set_ppm`, :305) reads it under every
   encoding. Correctness is unaffected, because offset-k is "speed only".
   Whether the selection is right under `utf8` is an open question (§7 Q3).
8. **The two engines have different membership spelling menus (§3 D8).** The
   VM has five shapes, including cls-fold. The DFA side always emits tables
   (`can_begin_match`, `ofs_k`, `stay`, `scan`), except the scan-edge range
   test. The range idiom is spelled twice, differently
   (`emit_vm.c:1649` vs `emit_dfa.c:6260`). That unification is
   `[CLS-TREE]`'s kit, which is parked in `[BACKLOG-TRIAGE]`.

---

## 1. The layer frame, refined

| layer | question | the primitive that owns it today | refinement |
|---|---|---|---|
| **L0 fold definition** | which characters are the same under `(?i)` | `src/core/fold.c` (`pcrec_ascii_fold`, `pcrec_fold_ascii`, `pcrec_fold_ucd_simple`) + the generated `src/enc/utf8_fold_pairs.inc` | Unchanged. L0 PRODUCES byte cubes only in the byte domain (an ASCII fold pair is the `m=0x20` cube). A utf8 multi-byte fold is never a byte cube, which is the line D23 draws at construction time. |
| **L0.5 the cube** (new row) | is this byte set exactly one AND-mask cube `(x & K) == T` | nowhere in `src/`: three study/probe copies (§3 D2) | **Lifted out of L1**, because L1, L2 and L3 all consume it. A singleton is `nfree==0` (K=0xFF), a fold pair is K=0xDF, and a dead window tail is K=0x00. |
| **L1 one-position membership** | how "byte ∈ set" is SPELLED in emitted C | VM: `vm_cls_shape`/`vm_cls_test` (`emit_vm.c:1622/1643`). DFA: tables + `scan_test_range` | Unchanged. The SETS come from parse/lower_enc. L1 only spells them. |
| **L2 across-position compare** | do these k bytes at offsets o..o+k match this run | six spellings (§3 D6) | Operand axis: compile-time (literal) vs run-time (`$_span_match`, [VAR]). Direction axis: forward vs backward (`vm_rev_emit`, lookbehind). **No DFA-route site exists.** |
| **L3 candidate finding** | where could a match start / is a necessary run present | four `memchr` sites + the byte-class walks + the stay/scan-edge skips (§2.4) | An L3 search is an L0.5 operand (a byte or cube to find) plus an L2 verify at the hit. The REQ_RUN loop is already exactly that shape. |
| **L4 placement / elision / carried facts** | is this pass emitted at all, and what does the next pass inherit | `req_admit` (`emit_dfa.c:5514`); `[PATFACTS]` (D120) for the facts | Unchanged. The router/keyword elision widens G1 from "same byte" to "same run at the candidate start". |
| cross-cutting | frequency prior, the dial (λ), the subject-end guard under ASan/UBSan, SIMD last | prior: `prefix_k.c:89`; dial: `opt_dial_design.md`; guard: `[WORD-FOLD]` row + K27 | SIMD lands only inside an L2/L3 primitive, once. |

---

## 2. Site inventory (at 897a97f0)

Encoding note, once: after `pcrec_lower_enc` every `A_CLASS` is a BYTE
class, so every emitter-level L1/L2 site below is byte-domain under every
encoding (`byte`, `ascii`, `utf8`). utf8 matters only at L0 (which fold) and
in the utf8 `$_span_match_caseless` residual.

### 2.1 L0: case folding

| site | needs | current form |
|---|---|---|
| `src/core/fold.c:68` `pcrec_ascii_fold[256]` | the byte-encoding fold, compile time | a partner table with 52 ASCII letters. **THE SOURCE.** |
| `src/core/fold.c:148-149` `pcrec_fold_ascii` / `pcrec_fold_ucd_simple` | a fold relation per encoding | `PcrecFold` objects. The encoding names which one applies (`enc.h:203`) |
| `src/parse/parse.c:534` `cls_casefold` (callers :601, :1306 encoding fold; :658 ASCII fold for bitmap-named sets, deliberately) | construction-time class widening (D23) | derived FROM the table. A folded class is an ordinary class afterwards |
| `src/enc/enc_byte.c:184` `$_span_match_caseless` (emitted residual) | run-time fold for a backref / [VAR] value, byte | `'A'..'Z' → +32` on both sides, per byte |
| `src/enc/enc_utf8.c:148-220` `$_span_match_caseless` + `$_span_ci_fold_pairs` | run-time fold, utf8 | decode, then a binary search over `utf8_fold_pairs.inc`. Changes length. **Stays its own** (the `[OPT-LITSCAN]` row says so) |
| `src/gen/emit_vm.c:1633` `vm_cls_shape` FOLD arm | RECOGNIZES a fold-produced pair so L1 can spell it cheaply | `count==2 && (lo^hi)==0x20 && lo∈'A'..'Z'`. **A re-spelling of the letter range, unguarded** (§3 D1) |

### 2.2 L1: one-position membership spelling

| site | engine | current form |
|---|---|---|
| `emit_vm.c:1622` `vm_cls_shape` → `emit_vm.c:1643` `vm_cls_test` | VM | ALL→`1`; SINGLE→`==c`; RANGE→`(unsigned)(c-lo)<=span u`; FOLD→`(c\|0x20)==lower`; else a 32-byte bitmap load. Callers: `vm_emit` A_CLASS `:8395`, `vm_cursor_rep` `:4448`, `vm_rev_emit` `:5031/:5120`, `\b` `:8027-8031`, plus word-boundary/lookaround sites |
| `emit_vm.c:1668` `vm_cls_fold_count` → `RX_VM_CLS_FOLDS` | VM | stamp. Same derivation as the test (good) |
| `src/core/cpset.c:305` `pcrec_cls_single` | shared | the interval-list singleton test (`nfree==0`). Readers: `altcls.c:190`, `reqbyte.c:454`, `emit_vm.c:3659` (island) |
| `src/opt/scanedge.c:199` `pcrec_scan_range` → `emit_dfa.c:6260` `scan_test_range` / `:6272` bitmap | DFA scan-edge | `==c` / `<=hi` / `(unsigned char)(c-lo)<=span`, otherwise a per-state `scan<N>` table |
| `emit_dfa.c:5117` `pf_tables_bcls` (`can_begin_match`), `:5135` `pf_tables_ofs` (`ofs_k<k>`), `:5591` `dir_fwd_skip` (`stay<K>`) | DFA | always a 256-byte table subscript |
| `src/ir/dfa.c` `clsmap` | DFA | alphabet compression. Membership IS the transition table |

### 2.3 L2: across-position compare

| site | operand | engine | current form |
|---|---|---|---|
| `emit_vm.c:8384` `vm_emit` A_CLASS, chained through A_CAT | compile time | VM | **one label per byte**: bounds check + L1 test + goto. gcc never fuses the chain (`vmlit_trigger_read.md`). This is `[OPT-VMLIT]`'s site |
| `emit_vm.c:4157` `vm_isl_emit`, single-child arm (:4220) | compile time | VM (alternation island) | a per-node `scan_position+d < n && s[pos+d]==b` goto chain. The trie's non-branching chains are straight runs that are not path-compressed |
| `emit_vm.c:4386` `vm_cursor_rep` (:4442-4450) | compile time | VM (fixed-length rep body) | one `&&` chain over `subject[span_cursor+i]` |
| `emit_vm.c:5008` `vm_rev_emit` | compile time | VM, BACKWARD | per-byte L1 test with `cur--` |
| `emit_dfa.c:723` `emit_req_run_check` (verify half) | compile time | both (shared text) | **`!memcmp(s+c-i, "run", L)` with a constant L ≤ 8**. The one site gcc fuses |
| `emit_dfa.c:5158` `ofsk_emit_verify` | compile time | DFA / hybrid prefilter | a `&&` chain of `s[cand+k]==b` or `ofs_k<k>[s[cand+k]]` over the non-scanned offsets |
| `enc_byte.c:153/184` `$_span_match[_caseless]` ← `emit_vm.c:8116` `vm_bref` (:8209), `:8281` `vm_var` (:8297) | **run time** | VM | a byte loop that returns a prefix count. The caseless form uses the arithmetic fold |
| `enc_utf8.c:115/148` | run time | VM, utf8 | decode + fold. Stays its own |

### 2.4 L3: candidate finding

| site | what it scans | form |
|---|---|---|
| `emit_dfa.c:4974/5002` `pf_emit_memchr[_bounded]` (`DFA_PF_MEMCHR`) | the start state's ONE escape byte | rest-of-subject `memchr`, no verify |
| `emit_dfa.c:5023/5039` `pf_emit_bcls[_bounded]` | the escape SET | `while (!can_begin_match[s[pos]]) pos++`, one table load per byte. **This is what `(?i)union…` gets for `{u,U}`** |
| `emit_dfa.c:5196` `pf_block_ofs` → `<p>_ofsskip` (called `:5313/5333`) | a singleton byte at the offset k* the cost model chose | `memchr(s+pos+k*)`, then the §2.3 verify chain. Selection: `prefix_k.c:386` `pcrec_prefix_ksets` |
| `emit_dfa.c:7203` `emit_attempt` (:7554) | `(?m)^`'s predecessor byte | `memchr('\n')`, candidate = hit + 1 |
| `emit_dfa.c:810` `pcrec_emit_req_byte_check` (+ `:723` run form); callers `emit_dfa.c:6953`, `:7220`, `emit_vm.c:12542` | the necessary byte/run anywhere in the window | `memchr` on the pick. With a run: memchr + constant memcmp, restarting per hit |
| `emit_dfa.c:5591/5619` `dir_fwd_skip`/reverse | in-loop stay skip for state K | a table walk per state |
| `src/opt/scanedge.c:482` `pcrec_scanedge_dfa` → emit `:6260ff` | a counted run of one class | range or table test per byte (the [OPT-5] edge) |
| VM hybrid prefilter (`RX_VM_PREFILTER "hybrid"`, `emit_vm.c:10659`) | the DFA prefilter of the VM's language | **the DFA emitter's own text** (`emit_search_head`'s static customer). Single source already |

### 2.5 L4: placement, elision, analyses

| site | role |
|---|---|
| `emit_dfa.c:5514` `req_admit` (G2 `req_route_one_attempt` :5474; G1 `req_byte_dominated_by` :5495 over `dfa_cand_scan_byte` :5429) | the one admission derivation. Four readers. G1 is one-byte-only and blind to an offset-set scan (`dfa_cand_scan_byte` returns -1 for it). Lane `k64fix` is editing G2's VM arm now |
| `src/opt/reqbyte.c:583` `pcrec_req_byte` (`rb_walk` :380, `rb_pick` :517, `rn_scan_index` :539, `rn_window_start` :559) | necessary byte + run. **Literal members are `pcrec_cls_single` singletons only, so every caseless literal contributes nothing** (`reqpos_census.md` false-negative iii) |
| `src/opt/prefix_k.c:386` `pcrec_prefix_ksets` | the offset-k sets and cost model (NFA walk) |
| `emit_dfa.c:3268` `cand_derive` / `CandSet` | D63's candidate-set tool. Its `use_memchr` is the count==1 verdict |
| `src/ir/nfa.c:192` (M2.8 trie), `src/opt/altcls.c` | factoring. Finds straight runs, which `[OPT-VMLIT]` names as its string edges |
| `src/opt/prefix_k.c:89/125` the prior | `pcrec_byte_freq_ppm`. Readers in §3 D7 |

---

## 3. Duplications

| # | fact | the spellings | guarded by | verdict |
|---|---|---|---|---|
| D1 | ASCII case partner | `fold.c:68` (source); `cls_casefold` (derived); `enc_byte.c:194-195` arithmetic; `emit_vm.c:1633` recognizer | cls_casefold: by construction. residual: `tests/backrefs/fold_agreement_check.c` + **S116**. UCD↔ASCII: `fold_agreement_utf8_check.c` part C. **Recognizer: nothing** | The recognizer re-spells the letter range. A drift changes the form, not the answer; the identity gates would catch emitted-text motion on the corpus, but nothing ties it to the table. The kit's compile-time masks are the named THIRD consumer (the `[OPT-LITSCAN]` HARD REQUIREMENT). The recognizer should become a reader of the same source when `[CLS-TREE]`/the kit touches it |
| D2 | "is this set one AND-mask cube" | `kit.py:293`, `discover.c:90` (relative to section base, W≤256), `wf_run_probe.c:131` (absolute byte, plus an exact 256-point check); `src/` has only `nfree==0` (`pcrec_cls_single`) and `m=0x20` (`VM_CLS_SHAPE_FOLD`) | study-internal checks (the provenance-blindness proptest, 438/438); wf's hand cases + the 256-point check | Nothing in `src/` yet, so there is no drift today. **Whichever of the kit or `[CLS-TREE]` lands first brings the one `src/` definition**, with the 256-point exact check as its agreement control. The other becomes a caller. The two special cases become callers too (implement-then-replace) |
| D3 | "singleton" | `pcrec_cls_single` (intervals); `vm_cls_shape` `count==1` (bitmap scan); `cand_derive` `count==1` (over a DFA escape set, a different set) | none between the first two | Low stakes. It is the `nfree==0` cube and folds into D2's resolution |
| D4 | "contiguous range" test | `vm_cls_shape` RANGE → `(unsigned)(c-lo)<=span u` (`emit_vm.c:1649`); `pcrec_scan_range` → `(unsigned char)(c-lo)<=span` or `c<=hi` (`emit_dfa.c:6264-6266`) | none | The same L1 decision is derived twice over two domains (bitmap vs clsmap) and emitted in two texts. It is `[CLS-TREE]`'s to unify (the per-section kit) |
| D5 | "scan for a byte, verify around it" | `DFA_PF_MEMCHR`; `<p>_ofsskip`; the REQ_BYTE/REQ_RUN pre-check; `emit_attempt`'s `\n` | `req_admit` G1 elides only the one-byte same-byte case | **The router cell is this row, measured** (two passes on `/`, 315 → 39,098 calls, `cycle2_batch2_reading.md` §4.1). ofsskip with all-singleton contiguous offsets IS memchr+memcmp in another spelling. D122's first target |
| D6 | "these bytes at these offsets" | six spellings (§2.3) | none | Only REQ_RUN's is fused by gcc. The VM chain, island chain and cursor chain are the `[OPT-VMLIT]`/`[WORD-FOLD]` population |
| D7 | the frequency prior | one table (`prefix_k.c:89`); readers `prefix_k.c:305` (no encoding gate), `reqbyte.c:517/539/559` (`bytekey`), `emit_dfa.c:5499` (`byte` only) | `run_offset_skip.sh` §1 (sum = 1e6); the reqbyte `-e utf8` zero-movers control | **The encoding gate is spelled per reader and one reader lacks it.** This is `[PATFACTS]`'s cross-file-reach shape (D120) and the landing point for `[ENG-PGO]`'s `freq` block. §7 Q3 |
| D8 | the membership spelling menu | the VM's five shapes vs the DFA's tables | n/a | The engines disagree on how to spell a fold pair: the VM uses `(c\|0x20)==x`, the DFA prefilter a 256-byte table. That is `[CLS-TREE]`/`[FORM-CHAR2]` territory. Recorded only |

---

## 4. Shared primitives: one source each

| primitive | single source of truth | the agreement check that must guard it | produced by | consumed by |
|---|---|---|---|---|
| P1 fold relation | `src/core/fold.c` (+ `utf8_fold_pairs.inc`, generated from `third_party/ucd-16.0.0`) | `fold_agreement_check.c` (S116), `fold_agreement_utf8_check.c` (A/B/C). **The kit joins as the third consumer** | L0 | `cls_casefold`, the span residuals, kit masks, the cls-fold recognizer (to be) |
| P2 byte cube `(K,T)` | **to be created** in `src/core/` (next to `cpset.c`). Absolute byte domain, from an interval list | the exact 256-point membership check (wf's), run over every class the corpus produces; the fold pairs must come out K=0xDF (a P1 tie) | `[WORD-FOLD]`/kit or `[CLS-TREE]`, whichever lands first | L1 (cls-fold, the CLS-TREE sections), L2 lanes, L3 cube scan |
| P3 literal run fact (bytes, or cubes per position, plus offset from the candidate start) | today split: `Job.req_run` (necessary, anywhere); `PrefixKSets` (per offset, sets); the VM chain (implicit in the AST) | the REQ_RUN stamps + `run_prechecks.sh` §4/§5; identity gates | `reqbyte.c`, `prefix_k.c`, (future) an emitter-level maximal-run recognizer | L2/L3 sites. **A `[PATFACTS]` customer: one record, not three walks** |
| P4 the compare (L2) | today the only fused form is `emit_req_run_check`'s constant-length `memcmp`. The kit's compare generalizes it: exact → memcmp, cube positions → `(w&K)==T` | answer-identity (test-axes) per deny flag; UBSan/ASan both axes for the subject-end guard | `[OPT-LITSCAN]` | VM chain (`[OPT-VMLIT]`), island chain, cursor chain, ofsskip verify, REQ_RUN verify, span_match (run-time K/T, on need) |
| P5 the search (L3) | today `memchr` spelled at four sites. The kit's search is operand (byte, or cube via SWAR) + offset + FORM chosen from the prior | the `RX_DFA_PREFILTER`/`RX_REQ_*` stamps each derive from the SAME selection object as the text (the existing discipline) | `[OPT-LITSCAN]`, `[OPT-A]` (pair / skip / Teddy leads) | DFA prefilter, ofsskip, pre-check, emit_attempt |
| P6 frequency prior | `prefix_k.c:89` table + the `pcrec_byte_freq_ppm` accessor; the ENCODING KEY belongs WITH the value (`reqbyte_freq_pick.md` §3.3) | sum check; the utf8 zero-movers control. **Owed: one gate at the accessor, not per reader** | static today; `[ENG-PGO]` `freq` block later | offset-k model, rb_pick/run window, G1 dominance, the kit's FORM choice |
| P7 admission | `req_admit` | `run_prechecks.sh` §5, S269/S270 | `[OPT-PRECHECK-ADMIT]` | every pre-check emission + the three stamps. The router/keyword elision is a G1 widening INSIDE it, never a second predicate |
| P8 subject-end guard for wide loads | the `[WORD-FOLD]` row's rule: wide only where `pos+8<=n`, a per-byte epilogue inside the last <8 bytes, `memcpy` loads | `make ubsan`/`make asan` both axes; a K27-style both-directions witness | `[OPT-LITSCAN]` | every P4/P5 wide or SWAR form, and SIMD later |

---

## 5. Per-row declarations

| row | layer(s) | consumes | produces | must NOT re-derive |
|---|---|---|---|---|
| `[OPT-LITSCAN]` (owner) | L2, L3, L4 | P1, P2, P3, P6, P7, P8 | P4, P5; this map | a fold (P1), a cube test (P2), an admission rule outside `req_admit` (P7) |
| `[WORD-FOLD]` (member) | L2 (mask form), L3 (cube scan, the offset preference) | P1 via P2, P8 | the K/T mask shape inside P4 | K/T from anything but P2 (so, P1 for folds); its own subject-end rule (P8 is its rule, stated once) |
| `[OPT-VMLIT]` (member) | L2 (VM) | P3 (the maximal run, an emitter-level recognizer: its trigger read says it cannot ride REQ_RUN's fact), P4 | the VM caller | a separate literal-compare emission (it is P4's exact arm); the D51 step-budget sentence is its own spec hunk |
| `[CLS-TREE]` (+ `[FORM-CHAR2]`, `[OPT-CLSPACK]` folded in) | L1 | P1, P2 | per-section L1 spellings; retires D3/D4/D8 | a cube test (P2). The cls-fold recognizer becomes a P2 reader |
| `[OPT-A]` | L3 (pair scan, skip search, memchr2/3, Teddy leads), L2 (its coalescing lead = VMLIT) | P5's form slot, P6 | L3 forms as P5 arms | a second search primitive. A Teddy "no" with its reason is a result (the ADDENDUM's rule) |
| `[OPT-REQPOS]` 2b | L3 + L2 (the REQ_RUN loop) | P3, P6, P7 | **the first instance of P4+P5** (`emit_req_run_check`) | — (it is the seed; it becomes a caller when the kit is extracted) |
| `[OPT-FREQPICK]` | L4 selection | P6 | the pick | its own encoding gate (move it to P6: D7) |
| `[OPT-PRECHECK-ADMIT]` | L4 | P6, the DFA scan selection | P7 | — (K64 fix A in flight, lane k64fix) |
| `[OPT-K]` (shipped) | L3 | P6 (ungated, D7), the NFA walk | `PrefixKSets` (feeds P3) | the verify compare, once P4 exists (a caller) |
| `[PATFACTS]` (D120) | L4 facts | every analysis above | the one record (P3, the prior's readers, carried facts) | — (its STEP 1 inventory can start from §2 of this map) |
| `[OPT-DIAL]` | cross-cutting | λ | the FORM choice's size/speed term | per-site thresholds (the dial keys P5's form and `[CLS-TREE]`'s sections, not each site) |
| `[ENG-PGO]` `freq` block | cross-cutting | a findings file | P6's value, with its encoding key | a second prior table |
| `[VAR]` (lanes varland/varfollow) | L2 run time; L3 later (the required value as a run-time needle) | P1, `$_span_match` | the span_match caller population | a caseless compare of its own (the residual is shared with backrefs, the same entry) |
| `[ENG-DIRECT]`/`[ENG-ISL]` | the DFA-route L2 landing | P4 | — | — (cross-note only: a string edge in a direct-coded DFA is P4's caller, not a new compare) |

**Sites that keep their own form, with the reason (the ADDENDUM's
record):**
- utf8 `$_span_match_caseless`: decodes, and its folds change length. It is
  not a byte cube (the `[OPT-LITSCAN]` row, D23).
- DFA `clsmap`/transition tables: membership IS the state machine. There is
  no per-position test to share.
- `emit_attempt`'s `\n` memchr and `DFA_PF_MEMCHR`: one byte with no verify.
  They are already P5's degenerate arm and need no change unless a verify
  appears. **Status: provisional. A site that joins later updates this line.**

---

## 6. Proposed sequence, and the measurement that gates each step (D77)

### 6.1 The sequence

| step | layer | what | gate: the measurement that opens it | acceptance |
|---|---|---|---|---|
| **S1** | L3+L4, exact only | **Extract `emit_req_run_check`'s memchr+constant-memcmp as the kit's first primitive** (implement-then-replace: REQ_RUN re-emits byte-identically through it). **Make the DFA prefilter its second caller** for a literal run at a fixed offset from the candidate start. Widen G1 inside `req_admit`: a pre-check whose run the prefilter already verifies is `dominated` | already MEASURED: router +80.8% / keyword +59.7% (`cycle2_batch2_reading.md` §4.1); the ruling is D122 | those two cells back inside the null band vs 25b1984f; every non-mover byte-identical (the identity gate); answer-identity per deny flag |
| **S2** | L2, exact, VM | `[OPT-VMLIT]`: VM literal chains (and the island's single-child chains) emit P4's exact arm (constant-length memcmp) | **OWED** (the row's own words): the bench pass on ctx-lazy/ctx-greedy/level-context + the 5 wild-secrets VM cells at the current pin | its own cells improve (D119 rule 4); a D51 step-budget spec sentence |
| **S3** | read, no build | **Attribute the four WAF cells**: where does the 1 MB throughput time go (prefilter walk vs DFA stepping vs no filter at all) | none needed: a D77 read. Artifacts plus one Linux profile, through the executor channel | it names, per cell, which of (a)/(b)/(c) below would reach it, or none |
| **S4** | L3 (+L2 mask) | caseless, on S3's answer: (a) a CASELESS necessary run (`reqbyte.c`'s `RbSet` widened to cubes → P5 searches a case-invariant or cube member → P4 masked verify); (b) a cube scan for a 2-member one-cube start set (`{u,U}`: SWAR under P8, or the offset preference); (c) multi-literal prefilter (`[OPT-A]` Teddy-class) for keyword alternations | S3 | the attributed cells improve. **The K/T mask enters P4 here and only here** (pay-for-what-you-use) |
| **S5** | L1 | `[CLS-TREE]` kit: absorbs cls-fold (`[FORM-CHAR2]`), D3/D4/D8. P2 moves here if S4 has not already brought it | `[BACKLOG-TRIAGE]`'s ranking; not before `[REL-1]` (Frank, 2026-09-21) | its own study numbers + the ns/char arm (ubuntubudu) |
| **S6** | L2 run time | span_match K/T built at run time | **a measured cell where span_match time matters** (none yet; `[VAR]` is the likely customer) | — |
| **S7** | L2/L3 | SIMD, inside P4/P5 only | D119: last | — |
| rolling | L4 | `[PATFACTS]` STEP 1 (inventory; can start from §2 here); the carried facts (DFA entry at δ*(s0,run), VM resume past the literal, dead bounds checks) after S1, because S1 is the first site that verifies a run at the candidate start | S1 landed | — |

### 6.2 Where this agrees and disagrees with the manager's expectation

- **Agree:** L3/L4 first on router/keyword (S1). It is measured, it is
  exact-only, and it is the literal D122 duplication (D5). L1 later.
  span_match masks only on measured need.
- **Disagree, on the facts:** "L2 first for WORD-FOLD's 4 losing WAF cells"
  does not hold. The four are DFA-route (§6.3). The DFA route has no L2 site
  (§1 refinement c). None of the four executes a literal-run compare that a
  mask could replace. The census itself says so (`wordfold_census.md` §5:
  "the mechanism these four need is the scan-side AND-mask form, not
  `emit_vm.c`'s fused compare"; §8 item 3: "a third, so-far-unnamed
  emission site"). So the mask is not step 2. The exact VM compare (S2) and
  the WAF **attribution** (S3) come before any caseless build (S4).
  `[WORD-FOLD]`'s only VM-route caseless witness is
  `wild-secrets-slack-webhook-url`, which is already a near-tie (0.77x).

### 6.3 The WAF stamps (read by this lane, `build/pcrec` at main, `-p rx --features all`, patterns from pcrec-bench `bench/capability/patterns/`, read-only)

| cell | route | `RX_DFA_PREFILTER` | `RX_REQ_BYTE` / `RUN` / `WHY` | reachable by (inspection, not measured) |
|---|---|---|---|---|
| `942270-union-select` `(?i)union.*?select.*?from` | dfa | `byte-class` (a table walk over `{u,U}`) | none / none / none | (a) a caseless necessary run `union`; (b) a cube scan on `{u,U}` |
| `942160-sleep-benchmark` `(?i:sleep\s*?\(.*?\)\|benchmark…)` | dfa | `byte-class` | `41` `)` / none / emitted | (c)-shaped (two keywords); (a) finds no common run |
| `942140-dbnames` (a `(?i)\b` keyword alternation) | dfa | `byte-class-bounded` | none / none / none | (c) only |
| `942360-concat-sqli` (a `(?i)\b` keyword alternation) | dfa | **`none`** | none / none / none | (c), and first find out why the prefilter is `none` |
| (control) `router-prefix-order` `/user\|/users` | dfa | `memchr` (`/`) | `47` / `/user@0` / emitted | S1 |
| (control) `keyword-prefix-order` `in\|instanceof` | dfa | `offset-set` | `110` / `in@1` / emitted | S1 (G1 cannot see through an offset-set scan: `dfa_cand_scan_byte` returns -1) |

---

## 7. Open questions for Frank

1. **S2 before S3/S4?** The map puts the exact VM compare (`[OPT-VMLIT]`)
   ahead of any caseless work. The WAF cells need a scan-side mechanism
   that is unattributed, while the VM exact case has a named population and
   a gcc fact that already favours it. Is that the order you want, or
   should S3's attribution read run first because it is cheap?
2. **Where P2 (the cube) first lands.** Whichever of the kit (S4) or
   `[CLS-TREE]` (S5) comes first brings the one `src/` definition, and the
   other becomes a caller. Is that acceptable, given `[CLS-TREE]` is parked?
   The alternative is a standalone P2 landing with its agreement check
   ahead of both. That would be building ahead of need, which D77 argues
   against.
3. **The prior's encoding gate (D7).** The offset-k model reads the
   byte-keyed prior under `utf8`, while the other two readers refuse to.
   Should the gate move INTO the accessor (one derivation, `[PATFACTS]`'s
   shape), or is offset-k's ungated read intended? It is correctness-neutral.
   Only selection quality under utf8 is in question, and that is unmeasured.
4. **Multi-literal prefilter (S4 (c)).** Two of the four WAF cells look like
   keyword alternations that no single-run kit reaches. Is the Teddy-class
   lead (`[OPT-A]`) in `[OPT-LITSCAN]`'s scope as a P5 arm, or is it its own
   row that the kit merely hosts?

---

## 8. Pointers

D122 + ADDENDUM (`docs/dev/decisions.md:8288`); plan rows `[OPT-LITSCAN]`,
`[WORD-FOLD]`, `[CLS-TREE]`, `[FORM-CHAR2]`, `[OPT-VMLIT]`, `[OPT-A]`,
`[OPT-REQPOS]`, `[OPT-FREQPICK]`, `[OPT-PRECHECK-ADMIT]`, `[PATFACTS]`,
`[ENG-PGO]`; `docs/dev/optloop/wordfold_census.md` (+ `wf/`);
`docs/dev/optloop/vmlit_trigger_read.md`; `docs/dev/cls_tree_study.md`;
`docs/dev/optloop/cycle2_batch2_reading.md` §4.1; `docs/design/offset_k_skip.md`,
`reqpos_2b.md` §3, `reqbyte_freq_pick.md` §3, `opt_dial_design.md`;
`src/core/fold.c` header; `tests/backrefs/fold_agreement_check.c`,
`fold_agreement_utf8_check.c`; `tests/mech/sabotages/S116_fold_table_off_by_one.sh`.

# flagaudit: every public -f option against the 2026-10-29 / 2026-11-10 guideline

Read-only audit, 2026-11-12. Sources: lib/pcrec.h (flag enum), src/core/axes.def,
`build/pcrec --list-axes`, docs/spec/tuning.md (sec 2, 5.4 policy table), docs/design/opt_dial_inventory.md
(sec 3.1 rate table), decisions.md, plan.md / known_issues.md rows, pcrec-bench read-only.
Nothing was measured here; every "time" figure is quoted from the cited record.

## 1. The flags word

64-bit `pcrec_options.flags`. Bits 0-57 are assigned, 58-63 are free.

| bits | what |
|---|---|
| 0-3 | semantic, not -f: CASELESS, EMIT_MAIN, NO_CAPTURES, TRACE |
| 34, 41 | not -f: UCP (--ucp), SIZE_CAP_REFUSE (--size-cap=refuse) |
| 45 | `-fno-req-set-lead`: RETIRED alias (bit kept, rewritten to `--memfn=no-pres-set-lead` by compile.c) |
| 55 | RESERVED, no macro, no reader: pcrec.h says "the kit's `-fno-kit-size-drop`, R17-b"; nothing in cli/ src/ memfn/ reads it (decisions.md:9622 and :9697 disagree on whether it is free) |
| 4-33, 35-40, 42-44, 46-54, 56-57 | 50 live -f bits: 44 deny spellings, 6 force spellings (-fprefilter 9, -fprefilter-collapse 20, -fcomments 27, -futf-check 39, -fstartpos-guard=align 40, -fmemfn-simd 49) |

Used 58 of 64: 6 non-f, 1 alias, 1 reservation, 50 live -f. Free: 6 (58-63), 7 if the bit-55 reservation is released.
[IFACE-PUSH] hard trigger is <= 4 free, so 2 bits of headroom today.

No flag uses 2 bits. No live -f flag uses 0 bits, except the alias (45). Option-shaped controls that use NO bit: `--unroll`, `--engine`,
`--tune`, `--vm-entry-shape`, `--part-*`, `--memfn=`, `--size-cap`/limits. One flag denies two things: `-fno-req-byte` implies req-run,
`-fno-offset-skip` also removes the run-pinned rows (bit 32's rows), still one bit each.

Force pairs (6 pairs = 12 bits, 2 states + default each): 8/9 prefilter, 19/20 prefilter-collapse, 26/27 comments, 25/40 startpos guard/align,
48/49 memfn-simd; 39 utf-check is a lone force.

Structural prerequisite for freeing ANY bit by demotion: two internal writers OR deny bits into the same word, so a demoted bit
only leaves the public word if they get an internal channel:
- the size-cap fallback ladder (src/core/compile.c ~1415-1500, `w->flags_or`): sets NO_LANDMARK_WALK, NO_PREMUL_TABLE, NO_PREFILTER, NO_ALT_ISLAND;
- the tune dial (src/core/tune.c:81 `deny_flags`): NO_PREMUL_TABLE at -2.
Of the DEMOTE set only 15 (premul) and 23 (alt-island) are touched; 8 and 57 are KEEP anyway. So one small change (a second, internal-only deny word
beside `flags`, with the ladder and dial writing there) is the single enabler.
Also: the answer-identity sweep (tests/axes/run_axes.sh ~L314-370) DERIVES its flag list from `--list-axes` (deny/force macro + `cli_flag`) and passes
the spelling to build/pcrec; hard-fails if a bit has no CLI spelling. Demotion therefore needs the axes registry to carry a harness spelling column.

## 2. Summary table

Class: KEEP (can be slower / legit force or contract), DEMOTE (test-only lever), DROP, UNSURE (name the measurement).
"refs" = files under tests/, scripts/, src/, cli/, Makefile, docs/testing.md naming the flag (rough, includes shared drivers).

| bit | flag | mechanism | class | one-line evidence |
|---|---|---|---|---|
| 4 | -fno-possessify | possessification rewrite | DEMOTE | removes frames only; time "unmeasured" (tuning 5.4 GATE 3), never shown slower; tests/possessify/run_possdiff.sh |
| 5 | -fno-revdet | reverse-deterministic rung | DEMOTE | size "a wash", time unmeasured; no loss case on record; tests/rungselect/run_rungdiff.sh |
| 6 | -fno-counter | counter rung | DEMOTE | "NOT A RUNG: correctness floor"; nested no measured cost, single-level 1-3% noise (inventory 3.1); denial = ground-truth replication, refused above the copy cap |
| 7 | -fno-length-prune | MRL pruning | DEMOTE | "trades nothing" (5.4); pure work removal |
| 8 | -fno-prefilter | VM hybrid DFA prefilter | KEEP | can lose: dense candidates are why hyb-reseed exists; GATE 3 "measured only through an engine-changing proxy" so the exact loss rate is open; also the ladder's drop-prefilter bit |
| 9 | -fprefilter | force hybrid prefilter | DEMOTE (medium) | only reachable on `--engine=vm`, itself a diagnostic override; refuses on DFA artifacts; 82 refs but nearly all are sweep arms |
| 10 | -fno-altcls-merge | alternation sibling merge | UNSURE | time only measured combined with factor (-7.61%, i.e. denial FASTER); size wrong-signed (+2.40%); GATE 2 (moves refusal set) |
| 11 | -fno-altcls-factor | prefix/suffix factoring | KEEP | sign vs lit-run is an open bench question (litrun P4.b "most likely to flip the sign"); size wrong-signed; bench pins 4 configs on it |
| 12 | -fno-atomic-discharge | delete no-op atomic groups | DEMOTE | engine-selecting (DFA->VM); never faster; `--engine=vm` already gives a caller the VM; kept bit in rx_info.flags |
| 13 | -fno-splice-calls | inline subroutine call sites | KEEP | GATE 4: "time cost reverses sign with the workload" (inline copy vs shared region) |
| 14 | -fno-tiered-entry | two-tier stack entry | KEEP | 5.06x per-call win but escalation RE-RUNS the match from scratch on FRAMES overflow ([OPT-1]: 2/165, 7/165 escalations); a workload that always escalates pays double; a size trade (-7.48%) |
| 15 | -fno-premul-table | pre-multiplied DFA table | DEMOTE | denied is 1.79x slower, -22..-25% size: never slower; its only job is size, which `--tune=-2` already drives. Needs the internal channel (dial + ladder) |
| 16 | -fno-offset-skip | offset-k candidate filter | DEMOTE (medium) | denied "up to 2x slower"; size sub-material; adopted only where a cost model predicts >=2x; no loss population on record. Also silently removes the run-pinned rows |
| 17 | -fno-anchored-dfa | unwrapped match-here machine | DEMOTE | denied 1.16x / 1.99x / 2.11x slower on three populations (inventory 2.15a); size lever (-15%); ladder uses the SDR state, not this bit |
| 18 | -fno-size-term | [ART-SIZE] K ladder | KEEP | the ladder TRADES speed for size on big artifacts by design; at +1/+2 the dial has no cell, so this is the only way a caller declines it |
| 19 | -fno-prefilter-collapse | exact prefilter language | KEEP | GATE 4; the collapse weakens the prefilter and loses the prune ceiling (tuning 2.17 "what the collapse costs") |
| 20 | -fprefilter-collapse | force count collapse | KEEP | size vs speed choice at the caller's discretion (artifact stops scaling with the count) |
| 21 | -fno-scan-edge | counted-run scan edge | UNSURE | 2.7-3.0x faster on letters, 1.08x SLOWER on digits (denied faster); walk's edge cost 1.9% instrs (plan.md:341). Measure: edge vs table on digit-class runs over the bench's log/number subjects, Zen 4 + Zen 1 + Mac |
| 22 | -fno-start-pinned | elide reverse pass | DEMOTE | "PURE WIN" (5.4); denied = bigger and slower; bench uses it as a sibling for size columns |
| 23 | -fno-alt-island | trie for literal alternations | DEMOTE | "PURE WIN"; branch order cost x8.87 at width 256 without it. Ladder's drop-islands needs the internal channel |
| 24 | -fno-cls-fold | ASCII fold compare | DEMOTE | "NOT A RUNG: absorbed into lambda"; compiler-evidence faster and -38% .text (form_char_step0) |
| 25 | -fno-startpos-guard | caller-startpos boundary guard | KEEP | CONTRACT / GATE 1: answer-changing by design (UTF mid-character startpos) |
| 26 | -fno-comments | emitted commentary off | KEEP | rendering only, no speed effect; needed so CLI can override config block (D93). RELOCATE candidate, see section 6 |
| 27 | -fcomments | emitted commentary on | KEEP | as 26 |
| 28 | -fno-vm-anchor-bound | stop after first failed attempt when anchored | DEMOTE | [OPT-ANCHOR-VM] bar met 13/13; pure removal of attempts that cannot match |
| 29 | -fno-end-window | end-anchor start window | DEMOTE | spec 2.26 names the risk: a window one byte too narrow DROPS a match (wrong answer); bench: denial worse on uuid/ipv4. This is the guideline's own example shape |
| 30 | -fno-req-byte | necessary-byte pre-check | KEEP | can lose: bench BLOCK A (O-48) "-fno-req-byte recovers on all four" regression cells; K82/K88 per-call entry cost; D148 addenda 4-5 |
| 31 | -fno-req-run | necessary-run pre-check | KEEP | spec 2.28 para 6: "No decline rule ... This flag is the decline" |
| 32 | -fno-run-prefilter | run-pinned prefilter rows | UNSURE | denial reverts to memchr/offset-set + separate run pre-check. Measure: run-pinned vs -fno-run-prefilter on candidate-dense subjects (many hits on the scanned member, few full runs). Subset of -fno-offset-skip |
| 33 | -fno-lit-run | VM literal-run compare | KEEP | bench litrun notes: a narrow gcc cliff (out-of-line memcmp at some L) means a regression vs -fno-lit-run is expected in a length band; 6 bench configs |
| 35 | -fno-ctx-node | one-char lookaround as context node | DEMOTE | engine-moving (DFA vs VM), answer-identical, never faster denied |
| 36 | -fno-cls-kit | class-matcher kit (lambda) | UNSURE | size lever, moves refusal set (2.33 para 7); kit forms are slower than tables at -2/-1 by dial design, at 0 chosen by a size rule. Measure: ns/B kit vs bitmap on wide-class (UCP) VM patterns at --tune=0 |
| 37 | -fno-hyb-reseed | adaptive hybrid retry | KEEP | bench syntax NOTES: "5% slower than -fno-hyb-reseed is [OPT-HYB-RESEED-XCALL]'s trigger"; known_issues A1 clang loss |
| 38 | -fno-cls-pack | shared atom table | DEMOTE (medium) | size lever (256 B vs 32N); per-site cost one load + shift vs one load; no loss recorded |
| 39 | -futf-check | whole-subject UTF validation | KEEP | CONTRACT / GATE 1 (valid-UTF promise); 63 refs |
| 40 | -fstartpos-guard=align | align mid-char startpos | KEEP | CONTRACT; pair with 25, three states |
| 42 | -fno-view-edge | scan edges across \z views | DEMOTE | lifts two refusals only; denied = prior machine; [OPT-VEDGE] |
| 43 | -fno-run-overlap | overlapping word compares | DEMOTE | "NOT A RUNG: within a word of memcmp in size"; deny is the kit row flag (MF_D_RUN_OVERLAP) already |
| 44 | -fno-req-run-fold | caseless cube runs | KEEP (conditional) | K5: `(?i)cat` on lowercase text ~200x slower than the denial (walk_survey.md), 23-26x for `(?i)error`; a latent find-all quadratic, linear fix shape unbuilt. Reverts to DEMOTE the day K5 is fixed |
| 45 | -fno-req-set-lead | retired alias | DROP | tuning 2.40: "RETIRED ... alias of --memfn=no-pres-set-lead"; carries a bit only so compile can strip it |
| 46 | -fno-req-handoff | K82 handoff | KEEP | ~4.6 ns/call on back-to-back literal matches (plan.md:505), K88; "interim lever" |
| 47 | -fno-start-set | DFA/VM start-set hat | KEEP | L3: +14..+17 ns/call when the subject starts on a start byte (known_issues:410); "interim lever"; same loss family as 46 |
| 48 | -fno-memfn-simd | SIMD kit rows off | UNSURE | the deny only restates the default and beats a config-block ON (2.43). A ruling, not a measurement: can `-fmemfn-simd=none` (the value form already exists) carry it? |
| 49 | -fmemfn-simd | SIMD kit rows on | KEEP | default OFF; "each form must beat scalar or show a named benefit" (2026-10-08 ruling); a caller's hardware choice |
| 50 | -fno-poss-ctx-follow | possessify arm A0/A1 | DEMOTE | engine-selecting arm of possessify; never faster denied |
| 51 | -fno-poss-bref-first | possessify arm | DEMOTE | arm; answer-identical; VM-only either way |
| 52 | -fno-rev-end | reverse-from-end locator | UNSURE | dev box (Zen4/gcc 15.2): rev-end 1.7-2.6x FASTER than denied on all O-96 cells (known_issues:222), but K104's floor was seen elsewhere. Measure: O-96 (c)2 litrun cells on Zen 1 (ubuntubudu) and Mac vs -fno-rev-end |
| 53 | -fno-start-width | end-minus-width start | DEMOTE | "PURE WIN"; the only cost on record is COMPILE time (emit-c x2.53 on one pattern, plan.md:1976), not run time |
| 54 | -fno-start-landing | landing start | DEMOTE | same as 53 |
| 56 | -fno-rev-end-onewalk | one-walk forms of rev-end | DEMOTE | sub-form of 52; answer-identical; never slower recorded |
| 57 | -fno-landmark-walk | landmark walk locator | KEEP | spec 2.54 para 3: "the walk can be slower than the forward scan ... which is why the flag is public" |

## 3. Per-flag notes (only where the table line is not enough)

- **Engine-selecting denials (12, 13, 35, 50).** Class is ENGINE-SELECTING (tuning 1 para 3); 12 and 50 are in the "kept in rx_info.flags" set
  (2 para 3), so demoting them changes that set and the `.flags = N` text of an --emit-main build. 13 stays public only because inline-vs-linked can lose
  either way. 35 is masked.
- **The size levers (15, 17, 23, 36, 38, 14).** They are not "can be slower": they are "make the artifact smaller by being slower".
  The guideline (slower often enough to matter) classes the *optimization* (always on, never worse) as no public bit; the size knob a caller wants is
  `--tune=N`, `--unroll`, `--size-cap`, `--warn-emit-bytes` and the ladder. Frank can overrule this per flag: if a caller-selectable size knob is
  wanted for one of them, 17 and 15 are the strongest (largest sizes, -15% / -22..-25%). 14 is the exception kept above because its slow case is real.
- **Redundancy pairs that could share a bit.**
  (a) 22/53/54 `-fno-start-pinned/-width/-landing` are three candidate rows of ONE axis (`search-start`, first-match table) and are all PURE WIN: demote all three, or if a public deny is ever wanted, one bit for the axis.
  (b) 10/11 altcls merge/factor: one pass (altnf.c), tested together (run_altdiff.sh denies both), two bits only so a differential can hold one fixed; one public bit plus a harness lever for the other would do.
  (c) 46/47 req-handoff / start-set: same loss family ("a skip whose expected length is ~0 still pays its call"); planned unification under the start table (known_issues:410) would make them one handoff edge; share one bit then, not before.
  (d) 30/31/32/44 the necessary-run family and 16: one analysis chain (byte -> run -> run-pinned -> offset-skip); 31/32/44/16 are refinements of 30's family. Keep 30/31 public, demote the rest as in the table.
- **Contract bits (25, 40, 39).** Answer-changing by ruling; these are options, not tuning axes. Keep. (They could move out of the optimization word to a policy field at [IFACE-PUSH].)
- **8/9.** `-fno-prefilter` on a DFA-able pattern is a no-op, while `--engine=vm` changes the engine, so -fno-prefilter is not redundant with --engine=vm. `-fprefilter` has one use: a prefilter under `--engine=vm`.
- **44 conditional.** If the K5 linear fix lands, move 44 to DEMOTE in the same change.
- **Bench check.** `testees/pcrec/configs.toml` pins these flags: -fno-lit-run (6), -fno-altcls-factor (4), -fno-req-byte (3), -fno-hyb-reseed (3), -fno-cls-fold (3), -fno-start-set (2), -fno-scan-edge (2), -fno-rev-end (2), -fno-req-run (2), -fno-req-handoff (2), -fno-alt-island (2). Of those only cls-fold and alt-island are in the DEMOTE set; scan-edge and rev-end are UNSURE.

## 4. The move list, per DEMOTE/DROP flag

Common to every demote (do once):
1. lib/pcrec.h: remove the public macro (source break for library callers; pre-1.0 allowed, deliberate, memory pcrec-abi-changes-pre-release). Keep the bit as an internal constant in src/core/internal.h on a new internal deny word.
2. src/core/axes.def row gains a harness spelling (`--harness=no-X`); `cli_axis_apply` accepts it only under -DPCREC_HARNESS (build/pcrec-harness, Makefile:411-424). `--list-axes` `cli_flag` column must show where the spelling lives so tests/axes/run_axes.sh (which passes it to build/pcrec) and tests/registry/axes_registry_check.sh can run against the harness binary.
3. docs/spec/tuning.md: sec 2.N text moves to a "harness lever" note; sec 2 para 4 table row; sec 5.4 row; sec 4 `pcrec_options` mirror. docs/spec/cli.md help text; `build/pcrec --help` (the -f block lists them). D80: spec hunk in the same change. If an emitted stamp prints the flag, none do except the kept-in-rx_info.flags set below.
4. tests: every `tests/**` driver passing `-fno-X` switches to `build/pcrec-harness --harness=no-X`: possessify (run_possdiff.sh), rungselect, counterk, mrl, altcls, atomic_groups (run_atomic_diff.sh sec 3), recursion, codegen (run_tiered_entry, run_premul_table, ...), utf8 startbnd, assertions, plus the generated axes arms. S282/S571 style mech sabotages naming deny maps need re-aim (grep them).
5. Bench: `pcrec-bench/testees/pcrec/configs.toml` flags (cls-fold, alt-island) and the scratch-tier `PCREC_LOCAL_FLAGS` route would need the harness binary (pin.sh builds build/pcrec only; bench reporter code and docs text in report.py / interpret.py name -fno-start-pinned, -fno-alt-island, -fno-cls-fold, -fno-scan-edge as siblings, a doc-and-pairing change). Needs a bench inbox item (I-n) via outbox/inbox, one-file [inbox] commit.
6. Contract class: removing a public -f spelling is a caller-visible contract change. Allowed pre-1.0, ruled and spec'd, not silent.
7. abi: `.flags = N` in --emit-main output moves only for the kept-in-rx_info.flags set (12, 13, 50 today: demoting 12 and 50 changes both the KEPT list in tuning 2 para 3 and the emitted `.flags` text, so it IS a stamp/abi event; the rest are masked and move nothing). Run `make test-codegen`; grep the current abi number's readers per D94.

Per flag extras:
- 15 premul, 23 alt-island: ladder (compile.c ~1415-1500) and tune.c:81 write to the internal word instead of `defo.flags`; FIT_TRACE masks (compile.c:2024) retarget.
- 12 atomic-discharge, 50 poss-ctx-follow: rx_info.flags KEPT set shrinks (spec 2 para 3; match_api.md rx_info.flags).
- 45 DROP: cli/main.c:1091 (the alias accept), src/core/compile.c:2095-2117 (strip + rewrite), lib/pcrec.h:1105, axes.def comment :225, tuning.md sec 2.40 + table row, `--memfn=no-pres-set-lead` becomes the only spelling (15 test files name the old one; grep -fno-req-set-lead; bench has 2 refs in configs/scripts). Releases bit 45.
- 16 offset-skip: also carries the run-pinned deny; the harness lever must keep denying both rows (the deny is `NO_OFFSET_SKIP | NO_RUN_PREFILTER` composite today).
- 9 -fprefilter (force): its "do-or-die refusal" test (reject table) moves to the harness binary.
- 22/53/54: tests/axes/start_landing_movers.tsv and the run_scan_edge_census / run_premul_table / run_form_census / run_tune_dial codegen drivers (start_landing.md lists them); re-pin any manifest they read.

## 5. Bottom line

| | count | bits |
|---|---|---|
| live -f flags | 50 | |
| KEEP | 21 | 8 11 13 14 18 19 20 25 26 27 30 31 33 37 39 40 44 46 47 49 57 |
| DEMOTE confident | 20 | 4 5 6 7 12 15 17 22 23 24 28 29 35 42 43 50 51 53 54 56 |
| DEMOTE medium | 3 | 9 16 38 |
| UNSURE | 6 | 10 21 32 36 48 52 |
| DROP | 1 | 45 (alias, plus the 55 reservation if released) |

- Bits freed by DEMOTE + DROP: **24** (23 + 1) in the public word (only after the internal deny word exists).
- Free before: 6 (58-63). Free after: **30** (31 if the bit-55 reservation is released). With the 6 UNSURE resolved toward demote: up to 36-37.
- Of the 3 medium DEMOTEs, the least certain is 16 (offset-skip). Drop it from the set and the totals are 23 freed / 29 free.
- [IFACE-PUSH] trigger (<= 4 free) is nowhere near after this.

Measurements that settle the UNSURE rows (none run here): 10: merge and factor timed separately on the altcls corpus (the -7.61% is combined); 21: scan edge on digit-class runs; 32: run-pinned vs not on dense-candidate subjects; 36: kit vs bitmap ns/B on wide classes at tune 0; 48: ruling only; 52: O-96 cells on Zen 1 and Mac.

## 6. Notes for the manager

- Not bits freed, but a cheaper win outside this audit's classes: the 6 force/contract pairs (25/40, 26/27, 48/49, 8/9, 19/20, 39) hold 12 bits for 6 or 7 axes; at [IFACE-PUSH] comments (26/27, no codegen effect) and the startpos/utf policy could move to option fields. I did not count that.
- Sequencing hazard: the internal deny word must land BEFORE the first demotion, or the ladder/dial silently stop denying (a check sharing its source with what it controls: learnings sec 3). A sabotage row that blanks the new word's ladder write is the control.
- All 23 demotions are answer-identical with a differential already in place (tuning sec 2 'Differential' lines), so the moved checks should be byte-for-byte the same sweeps against the harness binary.

# growsurv: survey of the compiler's recursive and super-linear growth paths

Lane growsurv (sonnet), 2026-11-20. Read-only on code; facts and tables only. Tree: main 1acc4dbb1 (the K146/K147 fixes are NOT on
main; they sit on lane/k146fix, k146f2, k146land). Evidence: `docs/dev/lanes/growsurv_evidence/` (raw tables, generator, probe scripts, probe log).

## Summary

- 121 recursive functions in the compiler's call graph (gcc `-fcallgraph-info=su` SCCs over every `src/`, `cli/`, `lib/`, `shared/`, `memfn/src/` object at `-O2 -g`; 120 distinct sites outside internal.h plus the one inline `pcrec_ast_visit`). `memfn/src/` has no recursive function. List with frame sizes: `growsurv_evidence/recursive_functions.tsv`.
- Bounded by an explicit number, a finite graph or spine iteration today: about 12 functions (`vm_isl_words` 64 levels, `first_of`/`text_first` backreference-resolution leg 64, `anf_sublist`/`anf_list` created-list leg 64, `st_cond` 10, `vx_*` 8, `config_walk` 64, the `cand_*` trio on a finite cell graph, `add_list` on a finite table). Everything else (about 100 functions) is bounded ONLY by the parser's paren-depth cap (`PCREC_MAX_GROUP_DEPTH` 250) times its frame, i.e. by the measured compile-stack budget, and is covered only if one of the 15 hand-listed `DEPTH_FAMILIES` happens to load it.
- Unbounded or over-budget found by probe on main (counted by function): 5 recursion sites die on the 432 KB budget thread inside the claimed envelope: `vm_cost`/`vm_cost_rep`/`vm_cost_cat`/`vm_cost_cap`/`vm_cost_look` (K146, depth 250), `vm_emit_node` chain (K146 family, new shape with no quantifier, dies at nesting ~220), `first_of`/`text_first` (K147, and a NEW backreference-free shape), and `lm_maxw`/`lm_flatten` (CAT spine, `docs/spec/limits.md` §3.10¶1 "a run of assertions of any length costs no stack per element" is FALSE; the plan row [LM-SPINE-DEPTH] says "unreachable today", it is reachable on main).
- Super-linear growth with no refusal: 2 (lmwalk `lm_cat` rebuilds a fresh CAT spine per candidate: memory O(N^2), 3.4 GB at 5,000 elements; `vm_build_region_saves` O(targets^2 x slots), over 2.5 GB at a 320-link call chain).
- Candidate growth cells: 34 in §6 (14 crash or runaway on main, the rest refused gracefully today or covered).
- Crashes found (candidate K-rows, NOT fixed): KR-A `lm_maxw`/`lm_flatten` spine; KR-B `(abc|abd(…abe))*` first_of without a backreference; KR-C `(ab|ac(…ad))` vm_emit_node chain dies at 220 deep with no quantifier; KR-D lmwalk quadratic memory; KR-E call-chain runaway memory. K146 and K147 reproduce as filed.

## Method

1. Built every `.c` of `src/ cli/ lib/ shared/ memfn/src/` (120 files) with `gcc -O2 -g -std=gnu11 -fstack-usage -fcallgraph-info=su` in scratch (`scripts/` unchanged, no `make`, nice, -P2). Parsed the `.ci` VCG graphs, ran Tarjan SCC (`growsurv_evidence/scc.py`), joined frame sizes (the `.ci` "N bytes (static)" figure, the same number as `-fstack-usage`). A function's frame is its own frame; an inlined callee is part of it. BLIND SPOT: indirect calls (function-pointer tables such as the `walk_arms.def` arms, `AstVisit` callbacks, module hooks) are not edges, so the parser's group/atom recursion (`p_group` -> module hooks) does not appear as a cycle here even though it is the recursion the depth cap bounds; `p_rep`, `p_cat`, `p_alt_info` are the visible part of it.
2. For each recursive function, `spine.py` reports whether its body names `A_CAT`, uses `PCREC_SPINE_EACH` or an iterative `continue`/`for(;;)` arm, and carries `PCREC_OWN_FRAME`. That only prefilters; drivers below were then confirmed by probe or by reading the arm.
3. Probes: `growsurv_evidence/gen.py KIND N` generates a pattern (about 130 generator kinds), `probe.sh`/`probex.sh` compile it with a copy of the compiler under `ulimit -s 432` (the 432 KB budget of limits.md §3.10; `STK=` overrides) and `scripts/watchdog -s 20..60 -m 2g..6g`. `probex.sh` goes through a one-line `.rxt` file because `--pattern` is capped at 128 KB by the kernel's argument limit. `hist.sh`/`sample.sh` use gdb for the crash's frame histogram or a mid-run sample. Crash = rc 139; runaway memory = watchdog rc 122. Everything is one compile of at most a few seconds; the box lock was held by another queue job throughout and no suite or `make -j` was run.
4. The probes ran against the freshly built local copy of main's HEAD, not against `build/pcrec` (older). 316 probe lines are in `probe_log.txt`.

## Recursive functions by stage

Frame = bytes from the `.ci` graph. "Bound" = what stops depth growing without limit today. P250 = only the parser's `PCREC_MAX_GROUP_DEPTH` 250 (depth of the AST by nesting; a CAT/ALT spine is left-nested, `l` = prefix, so recursing on `->l` along a spine is spine LENGTH, not nesting). SPINE = iterates the spine (`PCREC_SPINE_EACH` or an `a = a->l; continue` arm). Table of all 121 with flags: `recursive_functions.tsv`; families are grouped here, the large frames (>= 160 B) are named individually.

### Parse (`src/parse`, `src/core/varexp.c`)

| function (file:line) | frame | what drives depth | bound |
|---|---|---|---|
| `p_rep` / `p_cat` / `p_alt_info` (parse.c:2007/2201/2232, mutual with the group parse through module hook pointers, invisible to the SCC) | 336/32/64 | group nesting in any position (quantified body, either alternation branch, lookaround, class-free) | `++cx->depth > PCREC_MAX_GROUP_DEPTH` at parse.c:1599 -> "parentheses are too deeply nested". Same depth for every group kind |
| `la_kind`, `la_has_kreset`, `br_strip_caps`, `lang_charset`, `eol_tail_plain`, `pcrec_ast_all_core`, `vars_*` (mod_lookaround.c, mod_backrefs.c, ctxnode.c, definitions.c, mod_vars.c) | 32-80 | AST nesting | P250; most iterate the `l` arm |
| `rc_remap_caps`, `rc_find_root_call`, `rc_view` (rxt_compose.c) | 48-64 | AST nesting of a composed `.rxt` definition | P250 (SPINE on rc_find_root_call) |
| `vx_parse_at` 256, `vx_render_into` 64 (varexp.c) | `${a:-${b:-...}}` word nesting | `PCREC_MAX_VAR_NEST_DEPTH` 8 (limits.md §3.6) |
| `st_cond` 192 / `st_seq` 304 (subst_template.c) | template `${n:-...}` nesting | `PCREC_MAX_TEMPLATE_NESTING` 10 (subst_template.c:400) |
| `parse_src` 1888, `config_walk` 640, `cfg_effective` 224, `closure_walk` 672, `reach_includes` 176, `reach_dfs` 144, `pcrec_rxt_frag_by_real`, `pcrec_rxt_source_free` (rxt_source.c) | `.rxt` `include`/`lib`/`config ... from` chains: depth = FILES in a chain | `config ... from` 64 (limits.md §3.5¶3); `closure_walk` has a seen-set (cycle-safe) but NO depth cap for a linear `lib` chain of K files; `reach_*` terminates on a seen mark. NOT probed (needs K files on disk) |

### Core and facts (`src/core`, `src/facts`)

| function | frame | driver | bound |
|---|---|---|---|
| `compile_driver` 11,200 / `pcrec_compile_driver` 8 / `part_compile` 576 / `walk_part` 128 / `pcrec_compound_walk` 976 (compile.c:2046, compound.c) | the compound route: a compile of the whole pattern compiles its parts inside it (two compiles nested) | P250 inside each; the 11 KB frame is paid once per compound level and the route is entered once per part; measured at `^(?i:...)|b$` depth 250 = 221,656 B (§3.10¶3) |
| `ss_walk` 400, `sa_walk` 64 (SPINE), `rw_node` 64 (SPINE), `em_set` 48, `em_tails` 32, `ew_walk_marked` 48 (SPINE), `land_char_from` 128, `pf_derive` 80 (startset.c, startanch.c, widths.c, endwin.c, kset.c, facts.c) | fact derivation walks over the AST | P250 (the CAT arms iterate) |
| `rb_walk` 320 (req.c:1319) | required-byte walk | P250; the req.c `rb_*` helpers carry `PCREC_OWN_FRAME` (15 marks) so the 320 is the dispatcher alone |

### Optimizer (`src/opt`)

| function | frame | driver | bound |
|---|---|---|---|
| `pcrec_minw` 32 (SPINE), `pcrec_cwmin` 32 (SPINE), `cwmax_walk` 64 (SPINE), `pcrec_nullable` 32 (mrl.c) | quantified body / lookaround / ALT-branch nesting; CAT and ALT spines iterate (comment mrl.c ~273: "one frame per branch overflowed an 8 MB stack at 200,000 branches", fixed [DD-10]) | P250 |
| `pcrec_has_*` x10, `pcrec_bref_mark`, `dis_walk` (atomic.c) | 32-64 | AST nesting; the CAT arms `continue` | P250 |
| `co_*` x5 (callout.c; `co_walk` 304) | nesting | P250 |
| `q_rewrite` 320, `qp_walk`, `qf_walk` (derive.c) | nesting | P250 |
| `lower_walk`, `u8_box` 128, `subtree_is_identity`, `cap_sig` (lower_enc.c) | encoding lowering, nesting | P250 |
| `altcls_walk` 112 (SPINE), `anf_head` 256 (SPINE), `anf_node_same`, `anf_sublist` 48 / `anf_list` 320 (altnf.c) | alternation factoring: a rule that CREATES a rest/head list can recurse into it | `PCREC_MAX_ALTCLS_FACTOR_DEPTH` 64 (altnf.c:515) for the created-list leg; the nesting leg is P250 |
| `rd_reverse` 80, `pcrec_revdet_first` 128, `rd_alt_disjoint` 128, `rd_walk` 80, `rd_shape` 32 (revdet.c) | reverse-deterministic rung | P250; body groups capped at `PCREC_MAX_REVDET_BODY_GROUPS` 64 |
| `first_of` 448 / `text_first` 368 (mutual), `item_first` 352, `ps_node` 288, `gk_build` 368, `pss_walk` 256 / `pss_rep` 240 (mutual), `cap_index` 48 (possessify.c) | `first_of`/`text_first`: the capture fact for a group nested in an alternation branch re-walks the nest from the innermost level, one frame pair per level and per re-walk; also the literal-alternation text of nested groups (see KR-B) | NOT bounded by 250 x frame: depth x re-walk. The only explicit numbers are `PCREC_MAX_POSS_REF_DEPTH` 64 (backreference resolution, possessify.c:382) and `PCREC_MAX_POSSESS_POSITIONS` 256. BROKEN on main at depth 250 (K147) |
| `cg_length_calls` 48 (callgraph.c) | recursion/call graph | P250 / call graph |
| `earliest_dfa_excluding` 32 (select_engine.c) | engine selection | P250 |

### IR (`src/ir`)

| function | frame | driver | bound |
|---|---|---|---|
| `compile_ast` 384 / `frag_star` 128 / `frag_row` 144 (nfa.c:663/237/630, mutual) | NFA construction: nesting, and the replication of bounded repeats | P250 depth; breadth bounded by `PCREC_MAX_NFA_STATES` 131,072 |
| `trie_build` 256 (nfa.c:457) | literal-alternative trie | by branch common-prefix depth; iterative on the spine (LOOP); not probed deeper than `alt_prefix` 20,000 |

### Emission (`src/gen`)

| function | frame | driver | bound |
|---|---|---|---|
| `vm_emit_node` 576 and the 7-way SCC with `vm_opt_chain` 80, `vm_poss_chain` 96, `vm_revdet_rep` 720, `vm_counter_phase` 240, `vm_star` 192, `vm_rep` 224 (emit_vm.c:9368 ...), arms called through the dispatcher | nesting in any position; the dispatcher plus each arm is a per-level stack cost | P250 x (576 + arm). On main the dispatcher is the union of the inlined arms (K146). 3 `PCREC_OWN_FRAME` marks are on the branch fix, not here (main has 3 marks total in emit_vm.c) |
| `vm_cost` 304 / `vm_cost_rep` 480 (mutual; arms `vm_cost_alt/cat/cap/atomic/look/rep` inlined) (emit_vm.c:3031/2436) | the cost walk over the whole nest, in every alternation/quantified position | P250 x ~785; K146: dies at depth 250 for ~14 shapes (§6 C3) |
| `vm_count_slots` 432, `vm_rev_emit` 288, `vm_det_seq` 64, `vm_cap_offsets` 64, `vm_rev_caps` 48, `vm_walk_caps` 64, `vm_walk_calls` 48 | per-level walks (slots, reverse emission, captures, calls) | P250 |
| `vm_isl_words` 224, `vm_isl_subtree_nodes` 64 (SPINE) | alternation-island enumeration | `VM_ISL_MAX_DEPTH` 64 (emit_vm.c:4160), `VM_ISL_MAX_WORDS` 8192, `VM_ISL_MAX_BYTES` 262,144 |
| `lm_flatten` 96, `lm_maxw` 32 (lmwalk.c:57/80) | the top-level CAT spine length (flatten: both `l` and `r`; maxw: `l` along the spine) | **NOTHING.** Dies at about 13,000 spine elements on a 432 KB stack (§6 C1). [LM-SPINE-DEPTH] says "unreachable today": it is reachable, the file is on main |
| `dfa_cand_scan` 656, `cand_row_scan` 336, `req_pres_ask` 2,048 (emit_dfa.c:8610/8575/8932; mutual), `cand_path_visit` 128 / `cand_path_follow` 48 | the candidate-route graph: the recursion is over a finite table of (slot, route) cells, visited once each (header says so, emit_dfa.c:12500) | constant, independent of the pattern (3 KB frames x at most `CAND_NSLOTS`) |
| `emit_tree` 176 (clskit.c:1086) | class-set tree emission | class tree depth; `[...]` classes do not nest parens; class-set operators not probed |
| `emit_subst_items` 128, `emit_region_items` 336 (emit_subst.c) | substitution templates | `PCREC_MAX_TEMPLATE_NESTING` 10 |
| `add_list` 352 (memfn_targets.c:57) | kit target-list closure | finite target table |

### memfn

`memfn/src/*.c`: no recursive function (no SCC). Kit calls are leaves of the walks above.

## Per-node loops and super-linear paths

Compile TIME is not promised (limits.md §3.3.5); a refusal is promised for the six state-count ceilings (§3.3.1: "never hang, exhaust memory or truncate"). The two findings below are MEMORY with no refusal.

| # | site | shape that drives it | growth | refused by | finding |
|---|---|---|---|---|---|
| L1 | `lm_cat` (lmwalk.c:70) called per candidate from `lm_walk_pre` (lmwalk.c:309) via `pcrec_lmwalk_admits` (compile.c:556) | N top-level elements that are byte classes: `(?:a\|b)` x N, `[ab]` x N, `(?:a\|b)(?:c\|d)` x N | each candidate builds a FRESH left-nested CAT spine of its prefix: N^2/2 AST nodes. Measured peak RSS (watchdog): N=1,000 11 MB, 2,500 766 MB, 5,000 3.46 GB; N=4,000 `[ab]` and `(?:a\|b)(?:c\|d)` > 4 GB | nothing until the emit-size cap fires at N >= ~8,000 (`(?:a\|b)`) (after the memory is spent); no memory ceiling | KR-D |
| L2 | `vm_build_region_saves` (emit_vm.c:8172, inner loop `for k < nstate` inside `for j < nt` inside `for i < nt`) | a chain of N mutually linked call targets: `(?<g0>a(?&g1)?)(?<g1>a(?&g2)?)...` | O(targets^2 x slots) time and the arena it fills: N=160 refused after 2.2 s, N=320 > 2 GB (watchdog kill), N=1,000 > 2.9 GB in 2 s; `--engine=vm` same; `--engine=dfa` refuses (requires VM) | `PCREC_MAX_SPLICE_NODES` 512 / `PCREC_MAX_SPLICE_TOTAL` 8,192 (splice count) do not fire; the emit-size refusal fires only below N~200 | KR-E |
| L3 | `pcrec_callgraph_reaches` called per (i,j) in the same loop | same | transitive reach per pair | none | part of L2 (not isolated) |
| L4 | NFA construction / DFA subset | nested bounded repeats, `(a\|b...){2,3}` nests, `(a\|b)+` nests | state-count explosion | `PCREC_MAX_NFA_STATES` ("pattern too large (NFA exceeds 131072 states ...)") and the DFA ceilings; replication product `PCREC_MAX_VM_REPLICATION_PRODUCT` | graceful, verified: `e_plus` 250, `d_alt2_cnt` 124, `nested_cnt` 60 all refuse by name |
| L5 | the emit-size ladder (limits.md §8.4) | any pattern whose VM body is huge | refuses by size ("A repeat's body is replicated ...") but only AFTER the work: `cat_cls` 5,000 elements 5.9 s, `cat_cnt` 1,000 1.4 s | the size caps | graceful; time is not promised |
| L6 | literals and alternations | `a` x 100,000 (5.2 s, falls back to the VM after the DFA work budget), 20,000-way literal alternation (0.4 s), prefix-sharing/common-tail alternations at 20,000 (0.4 s), `\Q...\E` 100,000 (5.3 s) | about linear | `--max-auto-dfa-elems` fallback | OK |
| L7 | `anf_*` factoring rounds, `gk_build`, `pss_*`, `ps_node` (possessify) | not isolated; no probe grew time or memory super-linearly in the families tried (`alt_prefix`, `alt_common`, `alt_rev`, `rep_big`, `star_alt`: all 0.1-0.4 s at 20,000) | | | no finding; a pairwise-pass survey would need a code read of possessify.c that this lane did not do |

## Matcher-side (generated code) growth

- DFA artifacts: iterative, fixed frame; subject length costs no stack. Probed `a.*z` on 100,000 B at a 128 KB stack: clean no-match.
- VM artifacts: backtracking uses an explicit resume stack and a trail of fixed capacity (`VM_DEFAULT_RESUME_FRAMES` 2,048, `VM_DEFAULT_TRAIL_FRAMES` 3,072; limits.md §3.2) and two budgets (steps 500M, work 1G). Probed with `--emit-main`, 8 MB stack:
  - `^(?:(a+)+)\1$` on `a`x40+`b` and `^(a|aa)+$` on `a`x60+`b`: clean give-up `steps` (rc 3).
  - `^(a(?1)?b)$` (`--engine=vm`) on `a`x50,000`b`x50,000: clean give-up `frames` (§3.2); on `a`x500`b`x500: match.
  - captures `^(?:(a)|(b))*$` and 10-deep nested capture star on 100,000 B: match, no growth.
  - `(.*?a){20}b` on 3,000 `a`, `(x+x+)+y` on `x`x60, varying lookbehind `(?<=a{1,200}b)c` on 100,000 B: clean no-match.
- The one stack hazard is K33 (limits.md §5¶5): the default entries run the full-capacity run struct (about 131 KB) as a stack local after a `PCREC_ERR_FRAMES` escalation. On a 128 KB thread the recursion specimen `^(a(?1)?b)$` SEGVs even on a 500-deep subject (reproduced: rc 139 at 128 KB, rc 0 and rc 3 at 8 MB). Known and documented; its fix is the `_in` entries. It belongs in the runner as a SUBJECT-LENGTH cell with a thread-size axis, not as a new finding.
- No emitted-code recursion exists (no recursive C function in a generated artifact was seen in the probes; recursion constructs use the explicit stack). Not exhaustively read.
- Not probed (suggested for the runner): subject length x pattern for each give-up code through the library entry on a deliberately small thread; `-fno-step-budget` (no counters emitted, so a hostile subject loops); `rx_info`-sized caller buffers.

## Candidate growth cells

Axis = depth (paren nesting), length (spine / literal / chain length), width (alternatives, class items), count (repeat counts, group counts), subject. "Today" = what main does at the stated N. `STK` = the 432 KB budget thread. Generators are `gen.py` kinds in `growsurv_evidence/` (`e_*` = one group per level, `d_*` = two per level, so use N=125 for two-per-level kinds).

| cell | axis | generator shape | stresses | expected graceful refusal / behavior | today (main, 1acc4dbb1) | covered by |
|---|---|---|---|---|---|---|
| C1 | length (CAT spine) | `x` + `\b` x 30,000 + `y`; `(?=a)` x 12,000 + `a`; `(?!b)`; `(?i)(?=a)`...; `(?<=x)`/`(?i)` lookbehind x 30,000 (z_lookb with -i) | `lm_maxw`, `lm_flatten` (lmwalk.c), via `pcrec_lmwalk_admits` | no per-element stack (§3.10¶1) | **SEGV at about 13,000 elements on STK** (8000/12000 pass); 8 MB: passes to 100,000 `\b`, refused by `PCREC_MAX_NFA_STATES` at 300,000. Also with `-e utf8`, `--no-captures`, `-i`, `--engine=dfa`. gdb: 13,000 `lm_maxw` frames, 33 B each | none (WIDTH w4/w5 are `\b` x 20,000 trailing and `\A` x 40,000 leading: they do not reach the landmark candidate) |
| C2 | depth, 2nd branch, quantified | `(a\|b` x250 `c` `)*` x250 and variants: `(a\|b...)*+`, `*?`, `?`, `(?>a\|b...)*`, `(?<n%d>a\|b...)*`, `(a\|[b-d]...[x-z])*`, `(.*\|b...)*`, `(a\|b\|c...)*`, `(a\|b...)*$`, `^`-anchored, `(?i)`, `\K` core, lookahead `(?=a\|b...)*` | `vm_cost*` (emit_vm.c:3031/2436) | refusal "parentheses are too deeply nested" at 251, compile at 250 | **SEGV at depth 250** for `e_star e_atomic e_poss e_lazy e_opt e_named e_cls e_ci e_K e_lookst e_dot e_third e_end e_start` (14 shapes); gdb: `vm_cost`/`vm_cost_rep`/`vm_cost_cat`/`vm_cost_cap` ~245 frames each. Only `(?:a\|b...)*` (non-capturing), `e_look`, `e_neg`, `e_lookbk`, `e_last`, `e_first`, `e_cnt` pass. Fixed on lane/k146fix | K146 / `altrep` DEPTH row proposed (r62 DEPTH-1); not on main |
| C3 | depth, backreference core | `(a\|b...\1)*` x250 (`e_ref`), `\k<n0>` core (`e_nref`) | `first_of`/`text_first` (possessify.c) | refuse or compile | **SEGV at depth 250**; first_of 750 + text_first 229 frames | K147 (known, r62 DEPTH-3/4) |
| C4 | depth, literal alternatives | `(abc\|abd` x250 `abe` `)*` x250 (`e_lit3`) | `first_of` (possessify.c), NO backreference | compile at 250 | **SEGV at depth 250**; first_of 936 frames. A NEW shape for K147: no backref needed | none (KR-B) |
| C5 | depth, no quantifier | `(ab\|ac` x N `ad` `)` x N (`e_lit4`), also `(ab\|ac(...))` | `vm_emit_node` chain (vm_cat / vm_emit_f / vm_cap / vm_alt, 756 `vm_emit_node` frames) | compile at 250 | **SEGV from nesting ~220** (180 passes, 220 dies) on STK; 250 on 8 MB passes. Lower than the cap and has no quantifier, so even the quantifier-position matrix misses it | none (KR-C) |
| C6 | depth, plain families | `(`,`(?:`,`(a\|`,`(?:..)*`,`(?:..)?`,`(?=`,`(?<=`,`(?>`,`(?i:`,`(?<n%d>`, `(?1)`/`(?250)` call-backs, compound `^(?i:...)\|b$` at 250/251 | the whole pipeline | 250 compiles, 251 refused | passes (note `(a\|b` + core + `)*` shapes differ from the DEPTH rows: see C2) | DEPTH_FAMILIES (§ below) |
| C7 | depth, two groups per level | `(a\|b(` x125 core `)*)*`, lookahead/atomic/possessive/lazy/count/call variants | all | 125 levels = 250 groups | pass at 124/125 on main for all 27 (the nest is 248-250 groups deep; those groups sit in non-quantified outer positions), refusals graceful: lookbehind of unbounded alt ("every alternative of a lookbehind must have a bounded length"), `{2,3}` nests "NFA exceeds 131072 states", `(?R)`/`(?1)` core "A repeat's body is replicated" | hand-run matrix only |
| C8 | depth, 251 | any family at 251 | parser | "parentheses are too deeply nested" | graceful (all `d_*` at n=250 two-per-level refuse by name) | DEPTH_FAMILIES (251 arm) |
| C9 | length (width), memory | `(?:a\|b)` x 2,500..5,000; `[ab]` x 3,000; `(?:a\|b)(?:c\|d)` x 4,000 | `lm_cat` quadratic (lmwalk.c:70) | refuse before memory (§3.3.1¶1) | peak RSS 766 MB at 2,500, 3.46 GB at 5,000, > 4 GB at 4,000/8,000 elements; size cap fires only from ~8,000 | none (KR-D) |
| C10 | count, call links | `(?<g_i>a(?&g_{i+1})?)` x N (`calls_chain`; `calls_chain2` with a leading `(?&g0)`) | `vm_build_region_saves` (emit_vm.c:8172), callgraph reach | refuse (splice budgets / size) | N=20..160 refused (size) in 0.1..2.2 s; **N=320 > 2 GB, N=1,000 > 2.9 GB in 2 s** | none (KR-E) |
| C11 | width, alternatives | 20,000-way alternation of literals (`alt_lit`), of capturing groups (`alt_cap`, 1,000 refused size-cap), of prefixed/common-suffix words, 2,000-wide lookbehind | `trie_build`, `anf_*`, `vm_isl_*`, `pcrec_minw` | compile or size refusal | 0.1-0.4 s, no crash at 128 KB source on STK; `alt_cap` 1,000 refused gracefully | WIDTH w1/w2/w7 |
| C12 | length, literal | `a` x 100,000 (+ `\Q..\E` 100,000, 10,000 x `\Qa\E`) | literal run handling | compile | 5.2-5.3 s, falls back to the VM (work budget), no crash | WIDTH w3/w6 |
| C13 | length, groups | `(a)` x 5,000, `(a)?` x 5,000, named groups x 1,000, `(a)\1`-style refs x 1,000, `(a)(?1)` x 1,000 | NFA/VM replication, group tables | refusal by size | refused by name ("A repeat's body is replicated ... raise --max-emit-code-bytes"), 0.1-5 s | none (was not hand-listed) |
| C14 | length, `{n,m}` chains | `(?:ab){2,5}` x 1,000, `a{1,2}` x 2,000 (parser: "multiple quantifiers" for a doubled quantifier) | NFA replication | refusal | graceful | none |
| C15 | count, repeat count | `(?:a\|b){65535}`, `a{1,2}`x2000, `(?:..){2,3}` nest to 60 | NFA | `PCREC_MAX_NFA_STATES` | `{65535}` falls back to the VM (work budget); nest 60 refused by name | none |
| C16 | length, classes | `[a-c]` x 12,000 items inside a class, `[[:alpha:]]` x 5,000, `[^a-c...]` x 20,000, utf8 class `[\p{L}\p{N}]` x 20,000 (refused size), 20,000 range class (refused size) | `emit_tree`, class build | compile / refuse | 0.1-0.6 s; graceful | none |
| C17 | length, inline options / comments | `(?i)(?-i)` x 20,000 (180 KB source), `(?#c)` x 12,000 (module `comments` not enabled by `all`: refused by name) | parser | compile | 0.1 s | none |
| C18 | length, anchors / zero-width | `^` x 30,000, `$` x 30,000, `\B`, `\G`, `(?:)` x 30,000 | CAT spine walkers other than lmwalk | compile | pass at 30,000 on STK (not reaching lmwalk's landmark) | WIDTH w4/w5 |
| C19 | depth, rxt include/lib chain | K files each `include`/`lib` the next | `closure_walk` (rxt_source.c:4612, 672 B/level), `reach_includes`, `parse_src` 1,888 B | a depth cap (`config from` has 64, §3.5¶3) | NOT probed. Candidate: 672 + 1,888 B x K on an 8 MB stack is about 3,000 files | none |
| C20 | depth, template and vars | `${a:-${a:-...}}` 9 deep; subst `${1:-${2:-...}}` 11 deep | `vx_parse_at`, `st_cond` | refuse at 9 / 11 | by their own named limits (§3.6, `PCREC_MAX_TEMPLATE_NESTING`); not probed | tests/vars etc. (not read) |
| C21 | depth, class-set / extended class | `(?[ ... ])` nests (if the module is enabled), `[[:alpha:]]` inside | `emit_tree`, class parse | refuse by depth | NOT probed (module not located) | none |
| C22 | subject length, steps | exponential-backtracking patterns on VM, subject 40-60 bytes | the step budget (500M) | `PCREC_ERR_STEPS` (-2) | clean give-up, rc 3 | harness / tests/vmbudget (not read) |
| C23 | subject length, frames | `^(a(?1)?b)$` on `a^N b^N`, N=50,000 | resume stack / trail 2,048/3,072 | `PCREC_ERR_FRAMES` (-3) | clean give-up at 8 MB; SEGV on a 128 KB thread (K33, documented) | run_stackdepth_tests.sh [TS-4] |
| C24 | subject length, captures | `^(?:(a)\|(b))*$` on 100,000 B; 10-deep nested capture star | capture slot writes | none needed | match | none |
| C25 | subject length, lookbehind | `(?<=a{1,200}b)c` on 100,000 `a` | work/step budgets | `PCREC_ERR_STEPS`/no-match | no-match (K^2 steps within budget) | limits.md §3.1¶5 |
| C26 | subject length, DFA | `a.*z`, 100,000 B on 128 KB | DFA loop | none | no-match | harness |
| C27 | depth, alternation first branch | `(?:(?:...c)\|a)` (`d_alt_first`), `(a\|b\|` `c` `)*` (`e_last`), `(` `c` `\|a\|b)*` (`e_first`) | cost/emit walks | compile | pass (first/last branch nests are not the crash positions) | DEPTH `altnest` |
| C28 | depth x width | `(a\|b` x N with 100 alternatives per level | all | compile / refuse | not probed (suggested: width W at each of the C2 levels) | none |
| C29 | depth, lookarounds | `(?=a\|b...)` x250, `(?!`, `(?<=` nests | cost, emit | compile | pass (non-quantified: `e_look e_neg e_lookbk`), crash when quantified (`e_lookst`, C2) | DEPTH `look`/`lookbehind` (non-quantified only) |
| C30 | depth, atomic | `(?>a\|b...)*` x250 | cost | compile | **SEGV** (C2); non-quantified passes | DEPTH `atomic` (non-quantified only) |
| C31 | depth, possessive / lazy / optional | `)*+`, `)*?`, `)?` | cost | compile | **SEGV** (C2) | none |
| C32 | depth, named groups | `(?<n%d>a\|b...)*` x250 | cost + names | compile | **SEGV** (C2); DEPTH `named` is `(?<n%d>a)` x250 with a single-literal body: passes | DEPTH `named` (wrong position) |
| C33 | depth, backreference in the nest | `(z)` + `(?:a\|b(?:...c)\1)*` x124, `\1` core | first_of, bref marks | compile | pass at 124; crash form is C3 | none |
| C34 | count x depth | `((a{1,3}){1,3}){1,3}...` | NFA replication | `PCREC_MAX_NFA_STATES` / replication product | refused by name ("NFA exceeds 131072 states") | none |

### Suggested runner shape (for the next lane)

For each construct kind K in {group, ncgroup, named, atomic, lookahead, neg lookahead, lookbehind, inline-option, call-back} x quantifier Q in {none, `*`, `+`, `?`, `*?`, `*+`, `{0,1}`} x position P in {sole branch, first branch, 2nd branch, last branch} x core C in {literal, class, backref, call, `\K`, `$`, literal-alternation `abc|abd`} generate the nest at 250 and 251 on the budget thread. C2-C5 above are exactly the cells of this product that die on main; the existing 15 rows are the Q=none, P=sole/first (plus 3 quantified at core `a`) diagonal. A second family at spine LENGTH N (zero-width kinds, class-bearing kinds, literal-class mixes) at 16,384 and 100,000 on the budget thread finds C1. A third, MEMORY family (peak RSS under `scripts/watchdog -m`) at N=1,000 / 2,000 / 4,000 finds L1/L2.

## Already covered

`tests/thread/run_compile_stack.sh` (make test-stackdepth, [DD-10]) on the `COMPILE_STACK` = 442,368-byte thread:

- DEPTH (each at 250 must compile, at 251 must be refused "too deeply nested"): 15 hand-listed `DEPTH_FAMILIES`: `grp (;a;)`, `ncgrp (?:`, `altnest (a|;b;)` (a alternation whose NESTED group is in the LAST branch with a single-literal first branch), `starnest (?:..)*`, `optnest (a(...)?)` (this is the K146 position but without an alternation and with a capturing-optional body of one literal), `optnest-vm` (engine 2), `look`, `lookbehind`, `atomic`, `inlineopt`, `named (?<n%d>a)`, `callouter`, `callinner`, `compound` (+ its reach check).
- UNBUILT: conditionals and branch reset nested 250 refused "not implemented".
- WIDTH (must compile, chain length 2,000-40,000): 10,000 `(%dx)` alternation; 20,000 `%dx` alternation; 20,000-byte literal; `x` + 20,000 trailing `\b`; 40,000 leading `\A` + `a`; quantified 20,000-byte literal on the VM; a 2,000-alternative lookbehind.
- CONTROL: the depth-250 `grp` on a 32 KB thread must die by signal.

What the table shows the 15 rows do not load: no row has a quantified group in a LATER alternation branch with the quantifier outside (C2), none has a capture-bearing alternation level with a backreference or a literal-alternation core (C3, C4), none nests an alternation of multi-character alternatives (C5), WIDTH has no zero-width run that reaches lmwalk's landmark (C1: the existing `\b` and `\A` rows put the run at the end or the front, never between two class items), and nothing measures memory. All RECORD lines are printed but never compared (r62 DEPTH-5). The `look`/`lookbehind`/`atomic`/`named` rows pass at 250 only because their body is a single non-quantified literal.

## STATE AT HANDOFF

Report and evidence committed on lane/growsurv. Rulings file empty (no entries applied). Nothing owed. Not done and flagged: C19/C20/C21 unprobed; L7 (possessify pairwise passes) not read; matcher-side emitted code not read exhaustively.

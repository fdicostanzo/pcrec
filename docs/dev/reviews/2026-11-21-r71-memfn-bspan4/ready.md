# CRITIC READY: memfn-bspan4 (r71, light design re-check of block_span.md rev 4)

## Per-unit verdicts

| unit | verdict | ids |
|---|---|---|
| U1 (table refactor, store-once, skip lift, `.rxt`) | READY WITH TEXT FIXES | READY-3 (floor call: say why, manager confirms the R-2 reading), READY-7 (d) (enumerator needs `gphases`); READY-5's U1 note (sample shift) optional |
| U2 (wrapper, deny, lifted `fn_selector`, MEMFN_CLASS) + U2b | READY WITH TEXT FIXES | READY-2 (Q4: floors at the measure, five places); U2b: READY-7 (a) (name the diff tool; §16's 42 not reproduced, verdicts hold). Still waits on `wrap-differs` |
| U3 | READY WITH TEXT FIXES (found while checking C18/U4 readers, not by the diff scan) | READY-4 (C18 red at U3 until U4's amendment), READY-5 (guarded check reads the new bound only via a sample) |
| U4 (checks) | READY WITH TEXT FIXES | READY-1 (NAMED red at x86-64; "two" vs three witnesses), READY-6 (pin count spelling) |
| C18 rule (regexes, `_b`, -O0 rule, controls, routing leg) | READY WITH TEXT FIXES | READY-1, READY-4. The rule itself holds as worded at every C9 cell (PROBED-AND-HELD) |
| U5 | NOT RE-CHECKED (r69 scope); diff scan: no rev 4 change breaks it | READY-7 (b) nit (S2931 re-check line) |
| U6 | NOT RE-CHECKED (r69 scope) beyond R-12's mask, which held on real artifacts | — |

Under `wrap-differs`: U1 identical under both arms. Arm 1: the table above. Arm 2: R-26's nine surfaces, plus READY-2's
pin is re-measured with `word`/`ident` out of V (pin-at-the-measure still works); READY-1/4/5/6 are arm-independent.

## Fix ledger

- R-2 (store-once): LANDED-RIGHT for E-find; the floor extension is a disclosed reading, needed (READY-3).
- R-4 (lift `fn_selector` only): LANDED-RIGHT (fn_selector :727-741 is V's selector line for line; S730/S690/S694 as listed).
- R-7 (-O0 ymm rule): LANDED-RIGHT (pshufb rule passes B 16 and B 32 at all 7 C9 cells).
- R-8 (path by selector head; control 1): LANDED-RIGHT (control red at all 7 cells, 3 witnesses).
- R-9 (no leg (i) control; leg (c) catches the bracket): LANDED-RIGHT (plant 2 LOUD by (c) at B 16 and B 32).
- R-10 (`_b` name form): LANDED-RIGHT (plant 3 LOUD both ways, B 16 and B 32).
- R-11 (routing leg): LANDED-RIGHT (amendment as worded: 4 correct texts 1 FUNC/no violation; 5 plants LOUD).
- R-12 (mask M1-M9): LANDED-RIGHT (drilled on 6 real artifacts incl. subst; every abi line masked, none unmasked).
- R-13 (anchor moves): LANDED-RIGHT (anchor map matches §10.2 for every function U1/U2 moves; S2931 nit READY-7 (b)).
- R-17 (U2b normalizer): LANDED-RIGHT (two-sided as declared; count-tool nit READY-7 (a)).
- R-20 (MEMFN_CLASS, `.rxt`, wiring): LANDED-WRONG (READY-2 floor; READY-5 an unlisted reader; READY-1 in the C18 wiring row).
- Q4 ruling (post-freeze): NOT-LANDED (READY-2 lists the five places; U2 can pin it).

## Findings

### READY-1 -- build -- C18's NAMED leg goes red at target x86-64 for every span witness rev 4 adds to `NAMED` -- CONFIRMED
§10.2 "NAMED span witnesses" (+ §10.1 wiring row "C18 / simdfloor"); U4. Fix check of R-7..R-11.
`simd_floor_check.py` (build tree) checks EVERY named witness on EVERY target with a level:
`for t in targets: ... for n, _, _ in NAMED: if (tn, 'named:'+n) in named_movers: ok(...) else: bad('named witness %s is NOT a
mover (its bin is unreached)')`, and `FLOORS` has both `x86-64` and `x86-64-v3`. Rev 4 itself says the selector calls `__body`
at x86-64 ("x86-64 does not move", §10.1; §11 row "-fmemfn-simd=x86-64 ... as -fno-memfn-simd"), so a V witness is no mover
there. Repro (no rebuild): `build/pcrec -p rxa --features all -fmemfn-simd=x86-64 --pattern '[0-9a-f]{17}'` vs the
`-fno-memfn-simd` artifact, run through the tree's own `simd_floor_check.text_legs` with the x86-64 target row
(`ready/mover.py`): `(False, {}, [])` = NOT a mover. Under V the x86-64 text is the OFF wrapper plus scaffolding, the same
relation, so `[0-9a-f]{17}`, `[0-9]{25}` and `[0-9a-f]{41}`@4095 each print `bad(... NOT a mover)` at x86-64: C18 red at U4
on correct text, as worded. Fix (text, trivial): NAMED gains a target column (the span witnesses named for x86-64-v3 only),
or the span witnesses get their own list with a per-target floor; say which. Also a text nit in the same place: §10.1's
wiring row says "its `NAMED` list gains the **two** span witnesses", §10.2 names **three** (`[0-9a-f]{41}`@4095 the third)
with "literal floor: 3 span SIMD FUNCs"; §10.1 should say three. Effort trivial; blast radius U4 (C18 run).

### READY-2 -- doc/build -- the post-freeze Q4 ruling (floor at the measure, not 0) moves five places in rev 4; U2 CAN pin it -- CONFIRMED (by reading)
Q4 ruling (COMMON: "pinned at the measured value at U2, not 0 (K35)"); r69 MANAGER RULING R-20 ("corpus floors 0") is
superseded on this point. Sentences that move:
(a) §9.3 bullet `MEMFN_CLASS`: "class DIFFER, corpus floors 0 at every (encoding, stream)" and the tail "Corpus floor 0 is
the REAL corpus's count (§0.1); ... and the ruled floor 0 stays a lower bound (§15 Q4)" -> floors pinned AT the U2
measure per (encoding, stream): about 28 byte / 20 utf8 on `c-default`, 0 on `c-vm` (no window site on the VM engine:
`[0-9a-f]{17} --engine=vm` emits no `rxa_mf1_c` walk, checked), both layers;
(b) §15 Q4, the whole item ("is 0 as ruled ... This note writes the ruling (0)") -> resolved: pinned at the measure;
(c) §14 U2 row "the deny row `span-vector` (both layers) with its `MEMFN_CLASS` row" -> "... with its floors measured and
pinned at U2" (U2 is the first unit holding V and the `.rxt`, as §9.3 already says for `span-loop`'s rows);
(d) §18.1 R-20 row (cites "§15 Q4" as answered) -> name the amendment; (e) §12's register lacks the row: add
"`span-vector` MEMFN_CLASS floors, MEASURED at U2".
Can U2 pin it: YES. `memfn_arm.py` floors count `nc = sum(1 for d in differ if d in corpus)`, corpus = `es.enumerate_corpus`
= every `.rxt` under the tree (`find_files(tree, (".rxt",))`), so the U1-committed `tests/memfn/span_seed.rxt` is in the
population at U2; the count is per (enc, stream) at the default width, and the U3 level block moves no pattern in or out
of `differ` (the wrapper already differs at U2 at both layers), so the U2 pin holds at U3. The three witnesses differ at
utf8 too: each is R7w k 31 under `-e utf8` (site.py, 3 compiles), so V there. Also note `--measure` is how
MEMFN_CLASS's house pins were measured; the build lane cites its measure log in the comment, as every row does.
Effort trivial; blast radius doc + U2.

### READY-3 -- design (the author's flagged reading) -- the floor enumerator is NEEDED and adds no red reader, but it is an extension of R-2's words the manager should confirm; one sentence of its reason is incomplete -- CONFIRMED (by reading + trace)
§3 "Where it runs"; r69 MANAGER RULING R-2 ("computed ONCE in `wf_find_prepare` ... read by both define and use").
Needed: YES. The floor's check row is `c_floor_test` -> `wf_test` -> `wf_test_to(rc, t, NULL, -1, 1)` -> `wf_loop_len(w, i,
skip)`, which reads `w->head` (window.c:3500). `w->head` retires at U1, so the floor must get each stretch's form from
somewhere: T-force (L) and T-lever render loops there at any width, and T-head ALSO renders loops at the floor whenever a
stretch reaches offset 64 (width > 64). Rev 4's reason says "T-head at width 32 renders none", true but incomplete: G2's
generated floor sites (`run_g2_win.sh` TRACED_FLOORS `E-generic:1021`, long rows past 64) do render T-head loops at the
floor, and they are the floor branch's reach. Without the floor call the build would need a second, use-side derivation
of the form at the floor: exactly the parallel mechanism the ruling forbids. So the extension is the ruling's intent;
it is still a second call site the ruling's text does not name (rev 4 says so honestly).
Records it adds: one wfS SEL + per-row records + one END per stretch at every traced floor define (phase=define, the
floor's `quiet` is wf_plan_site's). Readers checked, none goes red: `rows_check.py` `trace_chosen` collects (wfS,row) but
signatures are held only for rows.tsv rows; `reach_equal.py` counts REACH lines only and flags only a table present at BASE
and absent at HEAD (wfS is new at HEAD); G2's floors grep `table=wfE` / `table=fn` literally; `d27_frame.c` reads WPATH
only. The gate's reach registry (`REACH_ROWS = 64`, every chosen contract registers a slot on first sight, gate.c:939):
36 printed + 12 window (wfA 5, wfM 3, wfE 4) + 6 wfS = 54 <= 64, so no `REACH_DROPPED` (rows_check red) -- 10 slots left;
worth one line in §3 so the next table sees the budget. No table ASK at the floor (a phase-1 ask is quiet).
Fix (text): §3 "Where it runs" says the floor call is needed because `wf_test_to` reads the head at every frame (T-force,
T-lever, and T-head past offset 64, e.g. G2's long floor rows), and records it as a reading of R-2 for the manager to
confirm; the `trace_format.md` hunk names floor sites too. Effort trivial.

### READY-4 -- build (unit separability) -- U3 cannot be validated green without U4's C18 amendment: `make test`'s simdfloor section is red at U3 on correct V text -- CONFIRMED
§14 U3 / U4 order; §10.2 "The C18 amendment"; fix check of R-7..R-11 (the amendment was moved wholly into U4).
U3 lands the `w32` level block, so from U3 on every x86-64-v3 V site is a C18 MOVER (the `.rxt`'s 28 at width 32 are in C18's
corpus population: `es.enumerate_corpus` reads every `.rxt`). C18's regexes are only amended at U4. Repro (no rebuild): the
build tree's own `simd_floor_check.text_legs`, UNMODIFIED, on the hand-built literal V pair (`[0-9a-f]{17}`, B 16, and
`[0-9a-f]{41}`@4095, B 32; `ready/legs.py` without `--amend`): `issues=["(c) a deleted line that is no SIMD FUNC's floor
call: '    return rxa_mf1_vs0__body(rxa_mf1_s, rxa_mf1_c);'", 'a mover with no SIMD FUNC selector']` = RED; with rev 4's
amended SELECTOR/HELPER (`--amend`) the same texts give `issues=[]` at B 16 and B 32 (4 witnesses). `test-memfn-simdfloor`
is in `TEST_SECTIONS` (Makefile:467), i.e. in `make test`. So a build lane that validates U3 alone (the units are listed as
separable steps; U1 explicitly runs `make test`) reads a red it did not cause, or is tempted to "fix" C18 inside U3 without
U4's controls. Fix (text, trivial): move the C18 amendment's two regexes + name form + the -O0 rule (with control (1)) INTO
U3 (it is the unit that first emits what they read), leaving the NAMED witnesses, floors, the routing leg and the other
controls in U4; or state that U3 and U4 are validated together. The routing leg (`routing_shape.py`) does not go red at U3
(it sees 0 V FUNCs and so reports no violation), so only C18 (c) and its "mover with no selector" line bind.
Blast radius: U3's validation.

### READY-5 -- build/maintenance -- an unlisted reader of U3's new `simd_bounds.tsv` row: `simd_guarded_check.py` reads it only through an every-10th corpus SAMPLE -- CONFIRMED (reader), red is sample-dependent
§5 "The guarded bound", §9.3, §14 U3 ("the guarded bound and `simd_bounds.tsv`"). Not an r69 fix; a reader rev 4 does not list.
`tests/memfn/simd_guarded_check.py` (in `make test` as `test-memfn-guarded`) FAILS on "simd_bounds.tsv rows no artifact read
(a bound nothing reaches)" (:434-437). Its population is `NAMED` (8 vrun/VM/DFA witnesses, none a V site) plus
`enumerate_corpus` sampled `i % every == 0` with `EVERY=10` (run_simd_guarded.sh:31). `--list-source` yields ONE row per
pattern block (counterk.rxt: 39 blocks, 39 rows), so `span_seed.rxt` adds 41 rows and the V row `span-vector-w32` is read only
if the every-10th sample happens to land on one of its 28 V blocks at the `simd:x86-64-v3` arm. That is likely today (about
4 of the 41 rows sampled, the V rows the file's back two thirds) but it is exactly the trap the file's own `simd-form-named`
comment records ("fsfix 3: the SIMD-form population must not ride the every-Nth corpus sample (a 4-file corpus addition
shifted it from 6 to 5)"): any later corpus file ahead of `tests/memfn/` can shift it to 0 and turn the row UNREAD (red),
or a V bound violation goes unseen on the unsampled sites. Fix (text, trivial): U3 adds a V witness (e.g. `[0-9a-f]{17}`)
to `simd_guarded_check.py`'s `NAMED` and re-pins `FLOORS['simd-form-named']` 8 -> 9 (the witness renders a level only at the
x86-64-v3 arm), same unit as the row. Also note for U1: the `.rxt`'s 41 rows shift that every-10th sample, which moves the
sample-dependent `simd-form` floor (pinned AT the measure, it moved 18 -> 16 the last time a corpus file landed); §9.3's
"found by `make test` at U1" covers it, but naming it saves the lane a surprise. Effort trivial; blast radius U1/U3 make test.

### READY-6 -- build/doc -- the T-table pins' "present = 1 selector call and 1 `__w32(` call" reads 2 and 2 on a whole-text count -- CONFIRMED
§10.2 "The T-table pin cells" (R-14/R-16 fix area). On the literal V text (`ready/w/hx17/on.c`, §4.1 + §5 as written):
`grep -o 'rxa_mf1_vs0('` = 2 (the walk's call AND the selector's own definition head `int rxa_mf1_vs0(const ...`), and
`grep -o '__w32('` = 2 (the selector's call AND `__w32`'s definition head); OFF text: `rxa_mf1_vs0(` = 2. Rev 4 does scope
them ("in the walk", "in the selectors"), but defines "present" as 1/1 and gives no spelling of the scope, so a lane that
counts the spelling over the artifact reads every present cell as 2 (red on correct text against the stated 1/1). Fix (trivial): give the
counted spelling, e.g. calls `rxa_mf1_vs\d+\(rxa_mf1_s, rxa_mf1_c\)` (call sites only, 1 in the walk per V stretch; the
selector's call `__w32(rxa_mf1_s, rxa_mf1_c)` 1), or define present as 2/2 whole-text. Absent cells (0/0) are unaffected.

### READY-7 -- doc -- small text items a literal build lane would stop on -- CONFIRMED
(a) §2.2 / §16 item 12 / §2.1: `\w{20}`'s U2b count "42 lines added + removed after normalizing" (raw 46) is not reproduced:
on the same declared normalizer, gcc 15.2 -O2, today's `-fno-memfn-simd` text vs the literal wrapped OFF text, same
basename, I get raw 26 / normalized 22 by `difflib.ndiff` and raw 24 / normalized 20 by GNU `diff` (`ready/u2b.txt`,
`ready/u2b_diff.py`); r69 R-17 also said 22. Every verdict holds (DIFFERS), but U2b's output is "each count ... the DIFFERS
list", so the census should NAME its diff tool (the count depends on it), and §16's figure should be re-derived or say how it
was counted. (b) §10.2 re-aim map: `memfn/data/cards/kit-grid.tsv` is a file U5 edits and carries S2931
(`SAB_BEFORE='kit\tverify_cmp\t3\t...'`, line 131 of 141); append-only, so it does not move, but the map's own rule ("or is a
file a unit edits") lists it: add "re-check S2931 (unchanged by an append)" at U5. (c) §5 "writes the functions below at file
scope, inside the region": at `-fno-memfn-simd` there is no region; say "inside the region where the target has one".
(d) §3 "Where it runs": the enumerator at the end of `wf_find_prepare` needs the walk's `gphases` and `quiet`, which
`wf_find_prepare(al, d, w, fx, build)` does not take today (`build = !quiet` is there, `gphases` is not; `s` is `d->s`): one
parameter added, worth one clause so the lane does not move the call into `wf_plan_site`. Effort trivial each.

## PROBED-AND-HELD
- **Line cites at the build tree** (bdb53a9a9): window.c 1470/1477-1484/1491 (head), 2388 (`wf_tables_check`), 2456/2461/2464/
  2466-2470/2471 (`wf_find_prepare`), 2511/2516/2578/2583 (`wf_plan_site`), 3498/3517/3536/3576/3584, 3977/3988, 3006/3371/4065,
  1999 (`w->hl`); compose.c 169/172 (`walk_row`), 1102; ofsskip.c 615/626/636/674/707/727; vany.c 155/189; emit_dfa.c 3233,
  3743; options.def 122 (the last row: U2 appends); simd_floor_check.py 123/124 and its -O0 nm leg; routing_shape.py 38/39.
  All hold (wf_plan_site's header ends at 2510, the function opens at 2511: trivial). main's limits.md delta is §3.10 only
  (diff hunk @212), so the §8.3 cites hold at main too.
- **U1 buildability (read):** `skip`'s inputs all written in `wf_find_prepare` before the enumerator (find_groups ->
  build_runs (does not touch `grp`) -> srch->prepare -> strm->prepare); `plan_of` sets `grp = -1` (:1513) so the floor's
  `grp` reads are safe; `hors_skip`/`stop_skip` are pure plan functions (d_hors_head/find_head read only `w`); the E-find
  rows are positional initializers ending in `basis`, so an appended column is a last-member append; the fused B-fn row
  returns before find_groups (no list, and its text is ofsskip's, reading none). `wf_rc_init` names `_s`/`_c` exactly as
  V's parameters, so `__body` renders with the use's own names; `wf_find_expr` opens the walk with `s` = 1 (the subject is
  always declared for the call).
- **Trace readers of wfS (U1):** rows_check.py (A: REACH lines only; C: rows.tsv rows only), reach_equal.py (REACH counts;
  END-only tables only in `tables`, BASE-minus-HEAD flagged), run_g2_win.sh and run_finder.sh (literal `table=wfE`),
  run_part_census.py (`table=fn`), d27_frame.c (WPATH): none goes red. Reach slots 54 of 64 (36 printed + 12 window + 6 wfS).
- **C18 -O0 rule as worded:** 4 correct texts (`[0-9a-f]{17}` B16, `[0-9]{25}` B16, `[0-9a-f]{32}` B16, `[0-9a-f]{41}`@4095
  B32) x 7 C9 cells (none, x86-64, -v2, sandybridge, -v3, -v4, -mgeneral-regs-only): 28/28 PASS (0 family symbols, 6
  pshufb; ymm 0 at B16, 188-196 at B32); -O2 -Wall -Wextra -Werror compiles 28/28. Control (1) (no always_inline on
  `__w32`) on 3 witnesses x 7 cells: 21/21 RED (`rxa_mf1_vs0__w32` defined, pshufb 0). Amended SELECTOR finds the one
  selector, amended HELPER finds `__w32` and `__w32_b` on all 7 texts. Controls (2) bracket count and (3) a non-admitted
  level (block helper renamed, or helper+call renamed): 6/6 LOUD at B16 and B32. The tree's 4 applicable C18 plants
  rejected on V texts (4 x 4); its "scalar floor line deleted" plant does not apply to V's head but runs on the first
  (ofsskip) mover as today. Leg (b) preprocessed: exactly one deleted line per V selector (2/2).
- **Routing leg as worded** (`ready/rsv.py`, a wrapper over the tree's routing_shape): OFF/ON `[0-9a-f]{17}`, ON
  `[0-9a-f]{41}`, OFF `[0-9]{25}`: 1 FUNC, no violation each; plants selector-does-work, drops-a-parameter, helper-below,
  level-not-defined-above, unrouted: 5/5 LOUD.
- **U2b normalizer as declared** (gcc 15.2 -O2, same basename): `[0-9a-f]{32}`@32 0/0, `\d{32}`@32 0/0 IDENTICAL;
  `\b[0-9a-f]{32}\b` @32 and @4095 raw 3 -> 0 (the positive control); `\w{20}` 26 -> 22 DIFFERS (negative control);
  `\w{501}`@4095 2 -> 2 DIFFERS. Every padding line seen matched the one regex; no `nop`/`xchg %ax` line escaped it.
- **Identity-gate mask on real artifacts** (DFA default, DFA x86-64-v3, VM `--emit-main` x86-64-v3, subst `x$1y`): every
  line carrying 109 matched exactly one of M1-M9 with its number group = 109 (27 lines), 0 unmasked, 0 mask matches on a
  non-abi line; version string `0.2.0-beta` static; `RXA_FINDINGS` is a findings-data hash (not code, not abi). A memfn deny
  stamps nothing: `--memfn=no-span-loop` on `[0-9a-f]{17}` byte-identical `.c` and `.h` to the default.
- **Anchor map** (kit/anchors_fn.txt + my rerun over compose.c, emit_sweep.py, kit-grid.tsv, simd_guarded_check.py,
  formhash.c, run_axes.sh, levels.def, vany.c: 50 more pairs): the U1 list (S3276-S3285, S2982) and U2 list (S730, S690,
  S694; S724/S2995/S3001/S3002/S687/S691/S692/S695/S728 unmoved) match; no anchor in plan_of, wf_test_to, d_hors_head,
  find_head, wf_find_prepare, wf_find_expr, c_find_test, c_floor_test, wf_plan_site, wf_tables_check, wf_find_define,
  the ren_search_row struct; none in simd_floor_check.py, routing_shape.py, memfn_arm.py, options.def, kit.h.
- **Pin-cell facts re-derived** (site.py): `ab[0-9]{26} --memfn=no-fd-d1` D1w k 26; `[xy][0-9]{26}` PAIR k 26 (B-pair, not
  fused); `[0-9a-f]{20}[g-z]{20}`@4095 D-hors k 20 then 19; `[0-9a-f]{16}` D-hors k 15. The 3 MEMFN_CLASS witnesses are V
  under `-e utf8` (R7w k 31 each).
- **Not checked:** U5/U6 beyond the diff scan and R-12; G2-V generator; F2; C6. Budget used: about 60 pcrec compiles,
  about 140 gcc compiles/preprocesses (cap 150 each).

CRITIC COMPLETE

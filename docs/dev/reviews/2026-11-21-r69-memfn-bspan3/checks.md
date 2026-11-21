# CRITIC CHECKS: memfn-bspan3 (r69, design re-check of block_span.md rev 3)

## Fix ledger

- F-3 (checks part): LANDED-WRONG (CHECK-1: the declared mask misses `    .abi = N,`; CHECK-9: SPAN-SEED's wiring per check unstated and memfn_arm.py MEMFN_CLASS unnamed; CHECK-8: the V count's k has no trace source). SPAN-SEED itself and its merge-base reference landed right.
- F-7: LANDED-WRONG (CHECK-5): the WALK witness is right (hand plant: SEGV at the end guard page, 6855 / 13546 differ; HORS SAME 0 / 18598), but "caught by: the guard page" names no check, and G2-V whole (the check that compiles `[0-9]{25}`) states no guard-page subjects.
- F-8 (plant (c) part): LANDED-RIGHT. Hand plant at k 15 (`[0-9a-f]{16}`, LO 0, B 16): SEGV at the start guard page, 4836 / 8730 differ; the pins' `{16}` cell reaches it (D-hors k 15 traced at 32 and 4095); the K >= 16 assert turns it into a refused compile; §12's label is MEASURED and DERIVED.
- F-9: LANDED-WRONG (CHECK-4: U2's one-writer lift moves 8 more anchors, REACH not run at U2, §17 says 5 for a list of 6; CHECK-5: plant (e)'s named detector does not hold its witness).
- F-12: LANDED-RIGHT. The unfiltered `git grep -n -w 109` at the build tree (219 hits) reviewed: the readers are exactly §9.2's list (emit_dfa.c:55; match_api.md §1 (three K80 lines), §6 table row, §6¶17 [coordinator: line cites replaced by sections for the spec-cite hook]; run_codegen_tests.sh:3243; S693:126; run_recursion_identity.sh's ABASEPIN comment; abi_changelog.md outside the grep's paths, listed by hand); every other hit is PCRE2 error 109, a timing or a count.
- F-18 (as a detector): LANDED-WRONG (CHECK-6): all 12 cells reach as stated (traced), but no D1w cell guards F-4's own fix, and the frame pin guards a column `w->brow` already implies.

## Findings

### CHECK-1 — CONFIRMED — build — the identity gate's DECLARED mask misses the `rx_info.abi` line; the gate is red on every artifact at U2 (r68 F-3, fix-induced)
§10.2 "Identity gate" declares the mask before data as "exactly the abi-number lines, a literal list of their four
spellings (`(abi N)` header, `#if ... != N`, the `#error` text's `(abi N)`, `#define PCREC_RX_ABI_H N`)". A real artifact
carries a FIFTH: the `.c`'s rx_info initializer `    .abi = 109,` (src/gen/emit_dfa.c:3233; emit_subst.c:1187 for subst
artifacts). Repro: `build/pcrec -p rxa --features all -o checks/hex32_off.c --pattern '[0-9a-f]{32}'` at the build tree;
`grep -n 109` over .c + .h -> .c:1 `(abi 109)`, .c:311 `    .abi = 109,`, .h:1 `(abi 109)`, .h:8 `#if ... != 109`, .h:9
`#error ... (abi 109)`, .h:12 `#define PCREC_RX_ABI_H 109`. Expected: every abi-carrying line in the mask. Observed: the
`.abi = N,` line is unmasked, so after U2's bump EVERY corpus and SPAN-SEED artifact differs from the merge base on that
line, and "nothing else is masked" forbids widening after data. The note's own sources name the line: match_api.md §6's
table row 1 is `abi` (`109`) and run_codegen_tests.sh:3210 reads `^    \.abi = `. Also the subst artifact's guard
spelling is `#if !defined(PCREC_RX_ABI_H) || (PCREC_RX_ABI_H + 0) != N` (emit_subst.c:522), which the "`#if ... != N`"
wording covers only if read as a pattern, not "a literal list". Fix: list five spellings (add `    .abi = N,`), state the
mask as anchored regexes over .c AND .h, and state the gate compiles both arms with the SAME `-o` basename (the .c's
`#include "<name>.h"` line otherwise differs: probe hex32_off vs hex32_nsl). Severity build (a guaranteed false red at
U2, or a lane that widens the mask after data). Effort trivial. Blast: U2, U6 (the gate). Side fact held: a memfn deny
stamps nothing in the artifact (`--memfn=no-span-loop` vs default on `[0-9a-f]{32}`: the .h identical, the .c differs
only in the include line), so the abi lines are the only expected merge-base difference.

### CHECK-2 — CONFIRMED — build — the C18 amendment's -O0 leg (ii) "a `ymm` register in the caller" is false-red on BOTH named span witnesses and every real site (B = 16 is xmm); its `always_inline`-drop control is then visible only to the `nm` test the amendment retires (r68 F-1 controls, fix-induced; my F-18-as-detector / C18 drill)
§10.2 "The C18 amendment": "(ii) `objdump -d` of the -O0 object shows a `ymm` register in the function that calls the
selector"; named witnesses `[0-9a-f]{17}` (k 16, B 16) and `[0-9]{25}` (k 24, B 16). §4.1/§4.4: at B = 16 the block is
`nib_blk`'s `sse` text (`__m128i`, `_mm_*`), an xmm stream. Repro (hand-built V per §4.1 + §5, text literal, spliced
into the build tree's `-fmemfn-simd=x86-64-v3 --harness=span-head=0` artifact in place of its one loop; tools
checks/tools/mkv.py; answers checked first: 0 / 13546 and 0 / 9202 differ vs python `re`, guard pages both ends):
`gcc -O0 -c` then ymm count inside `<rxa_search>`: `[0-9]{25}` 0 (xmm 492, pshufb 6), `[0-9a-f]{17}` 0 (xmm 492);
`[0-9a-f]{41}` at width 4095 (k 40, B 32) 138. So (ii) is red on the two literal-floor witnesses and on all 3 real sites
(k 31, B 16). Control (drop `always_inline` from `__w32`): -O0 `nm` then lists `t rxa_mf1_vs0__w32` and the ymm moves
into `__w32` (138 -> 0 in rxa_search) at B 32, but at B 16 ymm is 0 in both shapes, so the ONLY reading that separates
the two shapes on the named witnesses is the `nm` symbol, which the amendment says "does not apply". At -O2 the plant is
SAME or near (gcc inlines the static anyway: 0 / 2 lines differ, hex41 / dig25), so only the -O0 leg can see it. Fix:
(ii) reads "no `<fn>__w<VW>` symbol in the -O0 object AND a `pshufb` (xmm or ymm) in the selector's caller" (both
measured above: symbol absent, pshufb 6), and the control is "drop `always_inline`: the symbol appears"; keep a B 32
witness (`[0-9a-f]{41}` at 4095) if a ymm reading is wanted. Severity build (C18 red at U4 on the note's own witnesses,
or a lane that tunes the rule after data). Effort trivial. Blast U4. C9's seven march cells (-O2 -Werror, -O0) all
compile clean on the hand-built V at B 16 and B 32, and clang -Wall -Wextra -Werror is clean (F-6's `unused` holds).

### CHECK-3 — CONFIRMED (by reading + compile) — doc — the C18 control "move `__w32` outside the bracket makes (i) fail" names the wrong leg; (i) has no control that can fail it
§10.2: "a plant that moves `__w32` outside the bracket makes (i) fail". The bracket is the sink's `simd_open`/
`simd_close` byte accounting (it writes no text; the artifact's REGION, pcrec's `#pragma GCC target` push/pop, wraps
every function body of the file, which C18's placement lint itself requires: simd_floor_check.py docstring "every
function body and initializer of the file lies between them"). A kit plant cannot place `__w32` outside the REGION; out
of the BRACKET it is still compiled under avx2 and (i) "the -O0 compile succeeds" PASSES (the hand-built V compiles at
-O0 at all seven C9 cells). What catches it is (c)'s inserted-bytes == `SIMD_GUARDED_BYTES` (S730's class). §16 item 6c's
probe models a caller OUTSIDE the region (`outreg`), a shape no artifact has. Fix: the control names (c)'s byte count;
leg (i) either drops its control claim or gets one that can fire (e.g. an always_inline AVX2 helper called from a
function the kit emits outside the region: not a real shape, so better say (i) is a compile-must-succeed leg with no
plant). As a mech row it is still DETECTED (by (c)), so severity doc; but C18's PLANTS harness checks "rejected by the
leg it names", so a control written as stated would be red there. Effort trivial.

### CHECK-4 — CONFIRMED (anchor map + code) — maintenance/build — the re-aim list covers U1 only; U2's "one writer" lift rewrites the anchors of 8 more mech rows, and REACH is not scheduled at U2 (r68 F-9, F-11 fix-induced)
Drill 1. kit/anchors_fn.txt + the functions rev 3 moves. §10.2 "Re-aims at U1" lists S3277, S3278, S3279, S3280, S3281,
S3282 (and §17 says "5 re-aims"; the list names SIX rows). §5 "One writer" (F-11) has U2 lift ofsskip's `fn_selector` /
`fn_level_block` into one shared helper "taking the function's head (return type, attributes, parameters) as an input".
That cannot leave these anchors' text alone, because each names an ofsskip-only type or the ofsskip head:
- `fn_level_block` (ofsskip.c:711-712: `o->simd_open(o->u, (int)r->decl->level);`, `art->includes |=
  kit_level(r->decl->level)->includes;`): S2995 (g2simd), S3001 (g2simd), S3002 (g2simd), S724 (simdfloor). A V caller
  has no `fn_row *r`, so the level and the render become inputs;
- `fn_selector` (:733-736, `rung[0]->decl->level` + `fn_call_line(art, h, p, names[0], o)`): S730 (simdfloor);
- `fn_call_line` (:629, `"    return %s(subject, n, pos"`): S690, S694 (memfnstamps, memfnarms). V's call forwards
  `(rxa_mf1_s, rxa_mf1_c)`, so the argument list becomes an input (the head is, per §5);
- `fn_define` (:802, `if (fn_head(art, h, p, x.body_fn, o) || body->render(...))`): S695, whose AFTER also calls
  `fn_selector` with today's signature.
Each becomes an anchor-not-found at the matrix (loud, not silent), but rev 3 runs `REACH_ONLY` "at U1 and before
delivery" only, so U2 lands its byte event with 8 dead rows until U6. Also SUSPECTED: S3285 (`enum { WF_SPAN_HEAD = 64 };`,
window.c:1470) — U1 "`w->head` retires into the H rows", so T-head's H(64) may carry the constant and the enum go. Fix:
§10.2 gains "Re-aims at U2": the 8 rows above (plus S3285 at U1 if the enum moves), each re-anchored on the shared writer
with its REACH re-proved on its OFSSKIP witness at U2 (the writer is shared, so one plant now also hits V: say whether a
V witness is added or the ofsskip witness suffices); `REACH_ONLY` at U2 as at U1; §17's count "5 re-aims" -> 6 (U1) +
8 (U2). Severity maintenance (loud at U6 at worst). Effort small. Held: no anchor sits in `plan_of`, `d_hors_head`,
`find_head` (skip's writers, window.c:3977/3988), `wf_test_to` or `wf_find_define`; the wf_loop rows S3276/S3283/S3284
keep their anchors and still REACH at SIMD-off, because G2's window family states the PORTABLE target
(g2_win_gen.c:182) and parses loops in the define text too (`parse_loops(ft, ...)`, :1288), so a loop moved into
`__body` stays visible to its pins.

### CHECK-5 — SUSPECTED (detector population uncounted; by reading) — design — plants (e) and (b) name witnesses that are not in their named detector's population (r68 F-9 plant (e), F-7 plant (b))
(e): §10.2 "caught by G2's head-pass loop pins on an eligible stretch (SPAN-SEED's k 16 HORS cell) under
`span-head=N`". G2's head passes (run_g2_win.sh:568, the lever on every art) run G2's GENERATED window sites through the
kit API at the PORTABLE target (g2_win_gen.c:182); they never compile a pcrec pattern, so SPAN-SEED's cell is not in
their population, and no §10.2 check compiles SPAN-SEED under `--harness=span-head=N` or `--memfn=span-loop` (the T-table
pins run default compiles only). Whether G2's own space holds a V-eligible site (frame E-find, brow D-hors with k >= 16,
or R7w with 24 <= k <= 64) is counted nowhere (K35). Probe: its long rows (set `abc`, k 500 and 1024) are not eligible:
the pcrec analogue `[abc]{501}` at width 4095 traces `fd chosen=R7w`, k 500, past T-vscan's 64 (so is `{1025}`).
Second dependency: under the plant at SIMD-off V is the wrapper, so the pins see a difference only if
`__body` is literally H(64) (§5's words) and not "the head the non-V rows would pick" (H(N) under the lever), which
would make the plant SAME in every loop pin (the loops in `__body` are parsed from the define text). Classification:
SILENT-MOVE unless both hold; LOUD if they do. Fix (cheap, text-only, no new lever): add lever/force cells to the
T-table pins: `[0-9a-f]{17}` with `--harness=span-head=8` (pcrec-harness) and with `--memfn=span-loop`, widths 32,
expect 0 `__w32` and 0 `vs0` calls (exactly the T-lever / T-force rows ahead of V), at x86-64-v3 AND -fno-memfn-simd;
14 cells. (b): "caught by: the guard page" names no check. G2-V unit's guard pages are on G2's generated windows (the
same population question: does it hold a WALK stretch ending at the window's last position?), and G2-V whole (the check
that compiles `[0-9]{25}`) states python `re` and staircases but NO guard-page subjects. Confirmed by hand that the
witness works when a guard page is there: plant (b) on `[0-9]{25}` (R7w, k 24, B 16), end-flush subjects: SEGV, 6855 /
13546 answers differ; on HORS `[0-9a-f]{32}`: SAME, 0 / 18598 (F-7's premise re-proved). Fix: G2-V whole's control
column gains "subjects flush against a PROT_NONE page at both ends", and plant (b)'s row names G2-V whole. Severity
design (a plant row whose REACH is green while its detector cannot see it). Effort small. Blast U4.

### CHECK-6 — CONFIRMED (trace) — design — the T-table pins have no D1w cell, so F-4's own fix (key T-vscan on brow R7w, not pick WALK) has no detector; the frame pin guards a column that cannot move (r68 F-18, F-4)
All 12 pin cells traced on the round's MFTRACE harness at the stated widths (x86-64-v3): every fd row, frame and k is as
§10.2 states ([0-9a-f]{16}/{17}: D-hors k 15/16 at 32 and 4095; {1001}/{1002}: D-hors k 1000/1001; [0-9]{24}/{25}: R7w
k 23/24 at 32 and 4095; {65}/{66}: R7w k 64/65; `ab[0-9]{26}`: D1 k 26; `[xy][0-9]{26}`: PAIR k 26;
`[0-9a-f]{20}[g-z]{20}`: E-stmt at 32, D-hors two stretches k 20 and 19 at 4095). But the brow cells are D1 (pick LIBC)
and PAIR: a regression of T-vscan's key back to rev 2's "pick WALK" leaves both absent (neither pick is WALK), so neither
can see it. The one site that separates R7w from "pick WALK" is a D1w walk: `ab[0-9]{26} --memfn=no-fd-d1` traces
`fd chosen=D1w`, k 26 (probe above; also §16 item 5's `x[0-9]{26}`). V is answer-identical there, so only a text pin sees
the plant, and no check compiles SPAN-SEED with `--memfn=no-fd-d1` (the identity gate and G1 population run defaults
and the deny only). Classification of a plant "T-vscan keyed on pick FF_WALK": SILENT-MOVE (an unmeasured D1w cell
gains V under an unrelated finder deny, exactly F-4's harm). Fix: one more pin cell, `ab[0-9]{26}` with
`--memfn=no-fd-d1` at width 32 (D1w, k 26: absent), its fd row checked by the trace like the others; 13 cells. Second,
lower: `w->brow` is set only in `wf_find_prepare` (window.c:2461; E-generic and the legacy rows leave it NULL from
`plan_of`'s memset), and E-stmt never segments through `wf_test_to` (no loop at head 0: probe), so the frame column is
implied by the brow column and the E-stmt pin cannot fail under a frame-drop plant. Either drop the frame column from
the row (a simplification: brow R7w / D-hors already means E-find) or label the pin a documentation cell. Severity
design (CHECK-6 main), maintenance (the frame column). Effort trivial. Blast U4.

### CHECK-7 — CONFIRMED — build — U2b's declared normalizer, read literally, leaves a real site DIFFERS on padding (`nopl 0x0(%rax,%rax,1)`), so "identical on the population, or the build stops" stops the build; and the "32 non-movers" are not a normalizer control (identical C text, cannot fail) (r68 F-14 fix, drill 4)
§2.1: "padding lines (`nop`, `xchg %ax,%ax`, `data16 ... nopw`, `cs nopw`) removed. A diff that survives is DIFFERS";
CONSTRAINT: identical on the population "or the build stops". Repro (two-level wrapper per §5 hand-spliced around the
H64 lone-test chain of the build tree's `-fno-memfn-simd` artifact, checks/tools/wrapoff.py + census.sh; gcc 15.2 -O2,
kit/objfn.sh): `[0-9a-f]{32}` raw 0; `\d{32}` raw 0; `\b[0-9a-f]{32}\b` raw 3 lines (`cs nopw 0x0(%rax,%rax,1)`, and
`nopl   0x0(%rax,%rax,1)` <-> `xchg   %ax,%ax`), and after the declared list taken as whole-line spellings ONE line
survives: `nopl   0x0(%rax,%rax,1)`. "`nop`" does not say whether it means the bare mnemonic or every `nop*` form
(`nopl`, `nopw`, `data16 cs nopw`, ...); the declared-before-data rule forbids settling it after the diff. Floor
witness `\w{20}`: raw 24, normalized 22 (so it CAN be seen: holds). The "32 non-movers whose diff is 0 by construction
(the normalizer's own control)": at a non-eligible stretch (4 scan classes x k 16..23) T-head decides in both arms, so
the two C files are byte-identical and the objdumps are equal before any normalizing: the pair never exercises the
normalizer and cannot fail (a control sharing the source of what it controls, learnings §3). The REAL two-sided
normalizer control is in the population already: `\b[0-9a-f]{32}\b` (raw DIFFERS, must normalize to IDENTICAL), with
`\w{20}` the other side (must stay DIFFERS). Fix: declare the padding set as one regex, e.g.
`^((data16|cs) +)*(nop[wlq]?( .*)?|xchg +%ax,%ax)$`, name `\b[0-9a-f]{32}\b` as the normalizer's positive control
(raw > 0, normalized 0) and `\w{20}` as its negative; drop the 32 non-movers' "control" label (keep them as the
"every non-eligible cell renders identical C" count if wanted: a byte compare, no objdump). Severity build (a false
build stop on the real population, or a lane that edits the normalizer after data). Effort trivial. Blast U2b.

### CHECK-8 — CONFIRMED (trace format) — doc — SPAN-SEED's V count reads "the trace record's FDROUTE row and k", but no trace record carries k
§10.1: "prints its count of V sites (by the trace record's FDROUTE row and k, never a text regex)". Today's MFTRACE on
`[0-9]{25}` emits ASK/END/FDROUTE/REACH/ROW/SEL/WCAND/WPATH records; FDROUTE is `art=1 site=1 row=R7w arm=E-find
ren=B-walk frame=E-find`: no k (probe above). k exists only as the kit's own segmentation: the new wfS table's trace
(the kit's decision, i.e. the count would be the kit's answer, not the predicate re-applied) or the loop text under
`--harness=span-head=0` (the round's site.py method, a text read). Fix: §10.1 names the k source; the independent one
is the head-0 lever compile's loop text (`lo`, `end`) joined to FDROUTE's row, with the predicate (D-hors 16..1000, R7w
24..64) applied in the check; or a new trace field `k=` on the wfS record, stated as kit-sourced. The floors guard
population loss only, so either is acceptable once named. Severity doc. Effort trivial.

### CHECK-9 — CONFIRMED (by reading the check) — build — a population-read check rev 3 never names: `make test-axes`'s memfn arm (tests/axes/memfn_arm.py MEMFN_CLASS) is red at U2 until `span-vector` is classified at both layers; and SPAN-SEED's wiring into each check is unstated (r68 F-3)
memfn_arm.py's docstring: "the rows `pcrec --list-axes` prints in its `memfn` section are READ, and must equal
MEMFN_CLASS's keys exactly: a row the kit adds with no classification ... is RED"; each (row, layer) is DIFFER (a
floor of distinct CORPUS patterns + a named witness that must differ; witness-only patterns allowed: span-loop=force's
`[0-9a-f]{32}`), ASSERT_ZERO or REFUSES. run_axes.sh's simd layer is the family's top target (x86-64-v3,
`memfn_top_target`), so V renders there. §7 adds the row `span-vector` (options.def), §9.3 names emit_sweep.py's
DIFFER_PINS (a hand-run sweep tier: emit_sweep is invoked by no Makefile target; its floors apply over corpus +
`--patterns-file`) but not MEMFN_CLASS, and §14 U6 runs `make test-axes`. With 0 corpus V sites the honest class is
DIFFER, corpus floors 0 at every (encoding, stream), witnesses = SPAN-SEED's bench texts (`[0-9a-f]{32}`, `\d{32}`),
both layers (the deny is LIVE at default too: the wrapper); ASSERT_ZERO would be false (the deny is not inert) and
would go red the day a corpus pattern lands in range. Wider: §10.1 says every population-read check "reads SPAN-SEED as
well", but each check takes extra patterns differently (emit_sweep `--patterns-file`, with floors applied only WITH the
corpus; memfn_arm.py witness-only rows; simd_floor_check.py's literal NAMED list; run_axes.sh's answer identity reads
.rxt cases WITH subjects, which a pattern list has none of), and none of these is said. Fix: §9.3 adds the MEMFN_CLASS
row (DIFFER, corpus floors 0, SPAN-SEED witnesses, both layers) and §10.1 a per-check wiring line (which file, which
flag). For G-1's answer half, the cheapest honest wiring is a committed .rxt of SPAN-SEED's patterns with
oracle-verified subjects (CLAUDE.md: test expectations oracle-verified), which would also put V sites INTO the corpus:
then §0.1/§11's "corpus 0" and the floors move, so decide it in the note, not in the lane. Severity build (test-axes
red at U2; G-1's deny-arm-over-SPAN-SEED has no mechanism). Effort small. Blast U2, U4, U6.

### CHECK-10 — CONFIRMED (by reading) — design — the C18 amendment re-spells simd_floor_check.py only; C18's leg (d) / C11's routing rule (tests/memfn/routing_shape.py) never sees a V selector (name filter + head regex), so "the selector does no work" (D155 add. 1) has no detector for V (r68 F-1, F-11)
routing_shape.py: "The FUNC population is named by pcrec's FUNC suffixes, a NAME filter": `FUNC_SUFFIXES =
('_reqrun_whole', '_reqrun', '_ofsskip')`, `HEAD = ^static inline size_t (\w+)\(const unsigned char \*subject,
size_t n, size_t pos`. V's selector is `static inline __attribute__((always_inline)) int <p>_mf<h>_vs<j>(const unsigned
char *rxa_mf1_s, size_t rxa_mf1_c)` (§5): neither the suffix nor the head matches, so C18 (d) ("routing_shape.py ...
over the ON text", simd_floor_check.py docstring) and C11 count V's selectors as non-FUNCs. A plant of S690's class
for V (a statement before the selector's call, answer-neutral) would be caught only if simd_floor_check's amended
SELECTOR regex (which requires the body to be exactly one `return ...__w<VW>(...)` line) refuses it at ON: at OFF,
where the selector calls `__body`, nothing reads it (C18 reads OFF only as the diff base). Also SAME class: S694
(dropped arguments) at OFF is a compile error (loud). §5 says "the one writer is also the one place F-1's spelling
question is decided (the head is an input, C18 reads the same family)" but the family has at least three READERS
(simd_floor_check.py SELECTOR/HELPER, routing_shape.py HEAD/FUNC_SUFFIXES, run_g2_simd.py HELPER :275, which is G2's
ofsskip family and need not change). Fix: the C18 amendment adds routing_shape.py: the suffix `_vs<j>` (or the name
rule `_mf\d+_vs\d+`) and the head family, with its own planted control (its `--selftest` shapes at :171-180 gain a
V selector that does work), and states run_g2_simd.py is out of scope. Severity design (an unguarded ruled rule on a
new member). Effort small. Blast U4.

## PROBED-AND-HELD

- Plants by hand on emitted C (drill 2; build tree artifacts, V spliced per §4.1/§5 literally, set_epi8 highest lane first; answers vs python `re`, guard pages at both ends, every start position): base V answers identical on `[0-9]{25}` (R7w k 24 B 16) 0 / 13546, `[0-9a-f]{17}` (D-hors k 16 B 16) 0 / 9202, `[0-9a-f]{32}` (k 31 B 16) 0 / 18598, `[0-9a-f]{41}` at 4095 (k 40 B 32) 0 / 22130. Plant (b): LOUD on WALK, SAME on HORS. Plant (c): LOUD. C18 controls: drop always_inline = SAME at -O2, visible at -O0 only by `nm` (CHECK-2); move out of the bracket = LOUD by (c), not (i) (CHECK-3); non-admitted level = LOUD by the exclusivity lint once HELPER is re-spelled (by reading). Plant (e): SILENT-MOVE unless G2's space holds an eligible site and `__body` is literal H64 (CHECK-5). Plant (d): LOUD at the identity gate over SPAN-SEED (28 V sites at width 32 at SIMD-off), but only once CHECK-1's mask is fixed (a gate red on every artifact cannot single out (d)).
- C9-x86 on the hand-built V: -O2 -Wall -Wextra -Werror and -O0 clean at all 7 march cells (none, x86-64, -v2, sandybridge, -v3, -v4, -mgeneral-regs-only), B 16 and B 32; clang -Wall -Wextra -Werror clean (F-6's `unused` works).
- Identity gate expected differences (drill 3): a memfn deny stamps nothing (`--memfn=no-span-loop` vs default, `[0-9a-f]{32}`: .h identical, .c differs only in the `#include "<name>.h"` line); `MEMFN_FORMS` stays "none" on the deny arm; no comment or stamp carries the option set. So with CHECK-1's fifth spelling the mask is complete for the corpus artifact shape probed (DFA, default emit; subst artifacts carry their own two spellings, CHECK-1).
- U2b (drill 4): hand two-level wrapper at -fno-memfn-simd, gcc 15.2 -O2: `[0-9a-f]{32}` 0, `\d{32}` 0, `\b[0-9a-f]{32}\b` padding only (3 raw lines, CHECK-7 for the normalizer), `\w{20}` 22 normalized (the floor witness can be seen). Matches r68's figures.
- Re-aims (drill 1): no mech anchor in `plan_of`, `d_hors_head`, `find_head`, `wf_test_to`, `wf_find_define`; the wf_loop rows (S3276, S3283, S3284) keep REACH at SIMD-off because G2's window family runs the portable target and parses loops in the define text too. G2's existing default-pass checks (loop pin at literal 64, default == head-64 pass) are unaffected by the wrapper at SIMD-off for the same reason.
- U1's own rows (T-deny/T-force/T-lever) are exercised by existing checks the identity gate does not replace: G2's head passes and long rows (deny/force/head states), memfn_arm.py's span-loop ASSERT_ZERO and span-loop=force DIFFER 14 + witness `[0-9a-f]{32}`.
- T-table pin cells: 16 traced compiles, every fd row / frame / k as §10.2 states (CHECK-6 lists them).
- Under `wrap-differs` outcome 2 (for the fork): the proxy row would sit between T-lever and T-vwin, so it needs its own pin cells and a plant-(e)-style ordering cell, and U2b's normalizer (CHECK-7) becomes a committed check's rule; nothing in this lens differs under outcome 1.
- Per unit: U4 (checks) NOT READY: one decision owed (SPAN-SEED's wiring into each check, CHECK-9), the rest text fixes (CHECK-2, -3, -5, -6, -8, -10). U2b READY WITH TEXT FIXES (CHECK-7). U6 (abi package) READY WITH TEXT FIXES (CHECK-1; the reader list is complete). U2 needs CHECK-4's re-aims and CHECK-9's MEMFN_CLASS row before its REACH/axes run.
- Budget: about 40 pcrec compiles, about 90 gcc/clang compiles; k reached 15..40 by hand (B 16 and 32), pins to k 1001 by trace.

CRITIC COMPLETE


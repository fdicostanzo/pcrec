# crit-vlb2 verify

## Verdicts

### TRAIL (SOUND-1, FIX-1, READY-1)
- Code (review tree emit_vm.c:2858-2864): `static Cost vm_cost_look(...) { Cost c = vm_cost(v, a->l, false); c.frames += 1 + a->u.look.nbranch; c.trail += 2; return c; }`. `vm_plan_capacities` (:8040-8041): `bt_frames = cost.frames + 1; trail_frames = cost.trail + 1;` (bounded pattern only; unbounded gets VM_DEFAULT_TRAIL_FRAMES, `frame_capacity` option overrides).
- Emitted today (my compiles, verify/t_abcx.c, t_a3bx.c): `(?<=ab|c)x` -> `#define RX_FAST_TRAIL 3` (t_abcx.c:65) and `#define RX_TRAIL_FRAMES 3` (t_abcx.h:271); `(?<=a{3}|b)x` -> RX_FAST_TRAIL 4 / RX_TRAIL_FRAMES 4. Emitted `RX_TRAIL`: `if (run->trail_depth >= run->trail_cap) return RX_R_FRAMES;` (t_abcx.c:112). RX_SET = RX_TRAIL + store. Storage is a fixed array `rx_trail_entry trail[RX_TRAIL_FRAMES]` bound by `rx_run_state_bind(..., storage.trail, RX_TRAIL_FRAMES)`; no malloc/realloc/grow in the file (grep empty). Capacity is fixed per artifact; only a caller supplying bigger buffers via rx_search_in (or the frame_capacity option) changes it. No automatic tier rescues a bounded pattern: the stamped size IS cost.trail+1.
- Design (subject 322, 358-362): "`D_i` is a matcher slot written by `VK_SET`, so it is TRAILED" ; "`D_i` is set before each push and decremented after each pop." L_adv_i: `D_i = D_i - 1   // VK_SET`. The pop (rx_fail) rewinds the trail to the frame's mark, which was recorded in RX_PUSH (`trail_mark = run->trail_depth`) AFTER the D_i write; the decrement therefore writes a new entry above all later marks. No `vm_cost` in design (earlier critics' grep; not re-run).
- Hand trace, cap = 3 (cost.trail 2 + 1; body a{1,2} charges no trail), cost unchanged. `(?<=a{1,2})x` on `bax` (libpcre2 [2-3]): lookbehind at cursor 2: MARK (depth 0->1), POS (->2), D=min(2,2)=2 (RX_TRAIL at depth 2 < 3 ok, ->3); push (mark 3); back 2 to 0; body a{1,2} reads `b` fails; pop rewinds to depth 3; L_adv: D != lo(1), `D = D-1` -> RX_TRAIL at depth 3 >= cap 3 -> RX_R_FRAMES. Overflow BEFORE the answer [2-3]. (The attempt at cursor 1 does not overflow: D=1 -> exhaustion without a decrement.) `abx` (libpcre2 nomatch, probe): same path at cursor 2 (a matches, end 1 != 2, pop, decrement) -> FRAMES instead of nomatch. `(?<=x|[ab]{1,3})y` on `caay` (libpcre2 [3-4]): branch 0 fixed `x` fails and pops L_b1 (rewinds to depth 2); branch 1 range [1,3]: D=3 (depth 2->3), push, back 3 -> `c` fails, pop, D=2 needs depth 3 >= 3 -> FRAMES. Smallest overflowing cell: any positive-atomic lookbehind with ONE range branch whose first candidate fails and a second exists (`(?<=a{1,2})x` on `bax`); cap 3 means the first decrement overflows.
- Also true: an atomic cut does not rewind the trail (vm_look header property 3, quoted by FIX-1), so entries outlive the assertion; the subject_ceiling stamp is likewise under-charged.
- Caveat: no build exists, so the "overflow" is a hand trace of the design as written against today's cost/capacity code, not a run. Fix direction (cost term sum(hi-lo+1) or non-trailing D) is the manager's.
VERDICT: HOLDS.

### SOUND-2
- (a) Subject 398-405 lists exactly four rewrites ("1. `D_i` becomes the constant `k` ... 2. `L_adv_i` ... threaded ... 3. A frame whose continuation is only `rx_fail` ... elided. 4. The slot is dropped."), and line ~415 says "Every rewrite preserves answers." The same table's column "end-check fail, negative arm" differs between rows: `one-length` = `RX_R_INTERNAL` (§5.3), `range` = "decline (`rx_fail`)". None of rewrites 1-4 changes that cell, so substituting lo=hi=k into `range` yields a decline, not `one-length`'s hard return. HOLDS (and the divergence is observable only when the end-check fails, i.e. the S136-sabotage case).
- (b) emit_vm.c:7404-7408: `for (int i = 0; i < m; i++) { bl[i] = vm_label(v); bodl[i] = vm_label(v); endl[i] = vm_label(v); }`; `vm_label` (:926) is `return v->nlabel++;`. Adding `L_try_i`/`L_adv_i` to this loop for every branch would shift every later label number in an all-fixed artifact. The design text (subject 398-436) says nothing about label allocation (only "Slot allocation ... only for branches with lo_i < hi_i"). The "renderer emits every label" half of the critic's table row was not separately checked. HOLDS (as a text gap; renumbering is conditional on how a builder allocates).
- (c) Subject 1015-1018: "The negative-lookbehind hard error stays tied to "one length". ..." followed by "Benefit: one emission path, no table." Under B the end-check action is still selected by lo==hi, so a one-column selection remains; the "no table" claim is overstated as written. HOLDS.
VERDICT: HOLDS.

### READY-2
- libpcre2 10.46 default (oracle_probe c): `(?<=(?:)*a)x` -> `REJECT 125 at 0: length of lookbehind assertion is not limited`; `(?<=(?:\b)*a)x` -> same. At max_varlookbehind=0 (ready/mv0, run by me): both `reject@0 err 125`.
- pcrec review tree `build/pcrec --features all -p rx --emit-main` on each: rc=0 (compiles).
- mrl.c:660-666 quoted: "`(?:\b)*` and `(?:)*` answer 0 rather than "unbounded" ... and a lookbehind branch made of them is legitimately fixed-width."
VERDICT: HOLDS.

### READY-7
- population.tsv (vlbinv_evidence), column B_loop: `yes` = 30 rows / 22 distinct; `yes(deferred path)` = 2 rows / 2 distinct (`^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$`, `^(?:(?<g>a|ab)){0}ab(?<=(?&g))$`); `needs-bref-width` = 4 rows / 2 distinct; `no` = 1. So B_loop yes + deferred = 32 rows (24 distinct) (+4 bref = 36). Subject 703 (stage 1 scope): "the 36 real corpus rows flipped"; subject 871: "Stage 1 covers 32 rows (24 distinct) ... Stage 2 brings 36." Self-contradictory as the critic says.
VERDICT: HOLDS.

### READY-3
- Quote, tests/codegen/run_recursion_identity.sh:2163-2166: `if [ "$mism" -ne 0 ]; then bad "[$label] $mism call-FREE patterns are accepted by one build and refused by the other. Module recursion must not change what pcrec ACCEPTS on a pattern with no call construct in it:"` -> `bad` = hard failure.
- Count: of the 24 distinct B_loop rows, the 2 `deferred path` rows contain subroutine calls (`(?&g)`), so call-free flips = 22 distinct (30 rows), not 24 as the critic states (24 is the call-bearing-inclusive stage-1 count). The mechanism (refused-by-pre-build, accepted-by-post-build call-free corpus patterns trip the mism check until re-pinned) holds; I did not run the gate (no suites).
VERDICT: PARTLY (mechanism holds; the call-free distinct count is 22, not 24).

### READY-4 + FIX-3
Quoted in the review tree (emit_vm.c unless noted):
- base chain: `vm_slot_splice` (:1206-1213) = `2*(ngroups+1) + nguard_total + nlow_total + nmark_total + 3*nrev_total + nctr_total + npend_total + nlookmark_total + nlookpos_total + i` ("the eighth and topmost slot family"); `vm_slot_lookpos` (:1220-1226) sums the totals below it. A new family's placement (above splice => no base moves; below => splice base gains a term) is not stated in the design (grep of §5.1b text above: only "new slot family ... only for branches with lo_i < hi_i").
- naming: `vm_slot_name` (:1045-1090) ends `return NULL;` after the splice arm (":1085" splice `SLOT_SPLICE_SAVE%d`); no arm for a new family.
- totals/RX_NSLOTS: :10600-10634, `nstate = 2*(v->ngroups+1) + nguard_total + ... + nlookpos_total + nsplice_total;` plus per-family `*_total` assignments and `v->nlookmark = v->nlookpos = 0;` resets. A missed term is the header-documented "out-of-bounds write in EMITTED code, K27's class" (:1227-1234 quoted).
- VmSnap (:7566) `typedef struct { int guard, low, mark, rev, ctr, lookmark, lookpos; } VmSnap;` and `vm_w_range` calls (:7799-7817) enumerate guard/low/mark/rev/ctr/lookmark/lookpos.
- vm_listing_slots (:9488-9495): `if (n == 0) { vm_listing_slot_row(o, family, NULL, NULL, none_msg); return; }` -> an unconditionally listed new family emits a row in EVERY listing (counter/pending/splice are not listed at all, as FIX-3 notes). Whether that moves the 18 ir_listing baselines I did not run; the code path is as stated.
- docs/spec/ir_listing.md:107 [3.2¶2]: "`family` is a fixed vocabulary, append-only: `group`, `guard`, `low`, `mark`, `revdet`, `lookmark`, `lookpos`." and [3.2¶3] "Every family contributes at least one row."
VERDICT: HOLDS (listing-baseline movement is code-derived, not run).

### FIX-8
- emit_vm.c:1126-1135 `vm_slot_ctr`: "The counter rung's slot for loop `i` — `SLOT_COUNTER<i>`, one TRAILED iteration counter per counter loop, sitting above the three-slot reverse-deterministic block. Like every base here it is the sum of the family TOTALS the counting pass found, never of a running counter". Allocation: count pass `v->nctr++` (:3139); rung `const int ctr = vm_slot_ctr(v, v->nctr++);` (:6377). It is written with `vm_set(v, ctr, "0", "counter rung: iteration counter (trailed)")` (:6118, :6326) and `vm_set(v, ctr, vm_rolef(v, "slot_values[%d] + 1", ctr), ...)` (:6344), i.e. VK_SET-trailed exactly like D_i. Semantics equivalent (trailed, written with a set, read afterward); the counter family is also in VmSnap/vm_w_range. Note vm_slot_ctr's slot base sits BELOW pend/lookmark/lookpos/splice, so allocating D_i from it shifts those bases in a varying artifact (the critic says this; consistent with the base chain quoted above). Design preference is the manager's.
VERDICT: HOLDS (semantics only).

### FIX-2
- tests/mech/sabotages/S133_backstep_inlined.sh:40-41 `SAB_COUNT=1`, `SAB_BEFORE='    pcrec_vm_b_seek(v->sb, VSK_BACKSTEP, NULL, k);` + the "ENCODING SEAM's back-step" note + the `scan_position == %s_BACK_STEP_NONE` branch; S134_backstep_sentinel_unchecked.sh:35-37 `SAB_COUNT=1`, SAB_BEFORE the single sentinel `pcrec_vm_b_branch(... "scan_position == %s_BACK_STEP_NONE" ...)`. Both anchor the one literal-`k` site (emit_vm.c:7198-7203, quoted in the same lines). A `range` row would add a second `pcrec_vm_b_seek` with a different operand, which neither anchor text matches (SAB_COUNT=1 matches the one-length site only). Detector (per SAB_DOC_FIGURE): "codegen RED on the per-site count for the residlb1/residlb2/residlb3/residlbneg/residlbna/residlbtwo/residlbbref fixtures".
- Fixtures (tests/codegen/run_codegen_tests.sh:1534-1540): `(?<=ab)c back_step:1`, `(?<=a|bc)x :2`, `(?<=a|bc|def)x :3`, `(?<!ab|cd)x :2`, `(?<*a|bc)x :2`, `(?<=ab)(?<=xb)c :2`, `(a)(?<=aa)\1 :1` -- all fixed-width; no `range` fixture. Subject §7 "Existing rows that move" lists S136/S135 (critic; I did not re-grep the list for S133/S134 beyond the subject line-380 claim "per-site count is unchanged").
VERDICT: HOLDS.

### READY-5
S-U4 (tests/mech/sabotages/S-U4_width_rule_byte_units.sh): `SAB_FILE="src/opt/mrl.c"`, `SAB_SUITES="harness lookaround"`, `SAB_HARNESS_TARGET="tests/lookaround"`; SAB_AFTER makes the A_CLASS arm `return pcrec_sat_add(acc, 4, MRL_MINW_MAX);` (was 1); SAB_DESC: "every lookbehind whose branch contains any class reads cwmin != cwmax and refuses, (?<=a)x included"; SAB_DOC_FIGURE: "lookbehind.rxt and lookbehind_widths.rxt red wholesale". Detector = refusal of fixed-width cells.
- After stage 1 (§5.2: refusal of a varying branch is deleted; hi/lo only decide the row and the caps) `(?<=a)x` under the sabotage is a `range` [1,4] branch: candidates 4..2 fail the end-check (decline), 1 answers as before. Hand-trace on `aaax`: D=3 (clamped to cursor) ends at 1 != 3, D=2 ends at 2 != 3, D=1 matches -> same answer. So the refusal detector is gone for ordinary cells: HOLDS.
- BUT the critic's "only the identity gate or gate 3 would see it" is overstated: the sabotage multiplies every class width by 4, so the cap/ceiling boundary cells go red in tests/lookaround. `(?<=a{1,255})x` would be hi=1020 > 255 -> err-200-shaped refusal; `(?<=a{65535})x` hi=262140 > 65535 -> refusal. The cell `(?<=a{1,255})x` exists today in tests/lookaround/d27/refusals.rxt:68 (a pcrec refusal pin that flips to a match cell at stage 1) and W8/W9/W9b are in the design as cells. So S-U4 likely still goes red there (suite `harness lookaround`), for a different reason than its stated figure; its SAB_DOC_FIGURE is still wrong. Not run (no sabotage matrix).
- S136 (tests/mech/sabotages/S136_width_rule_accepts_variable.sh): SAB_FILE src/parse/mod_lookaround.c; SAB_BEFORE is `if (lo != hi || hi >= PCREC_W_UNBOUNDED || hi > INT_MAX) { *bad_lo = lo; *bad_hi = hi; return false; }` inside la_widths' per-branch loop, so the natural edit touches EVERY branch. Hand traces with only the LAST branch `d` stored as k=2: positive `(?<=bc|d)x` on `abcx`: x at 3, branch 0 `bc` (k=2, correct) back to 1, matches `bc`, end 3 == POS -> success [3-4], GREEN. Negative `(?<!bc|d)x` on `bcax`: x at 3, `bc` from 1 reads `ca` fails; `d` (k=2) from 1 reads `c` fails; no end-check reached, assertion holds, match [3-4], GREEN (no INTERNAL). With ALL branches (or branch 0) at K+1 both go red (branch 0 k=3: positive nomatch; negative `bc` from 0 ends at 2 != 3 -> INTERNAL). So: "never only the last" holds; the natural edit (every branch) is fine.
VERDICT: PARTLY (S-U4 detector loss holds, but S-U4 likely still goes red on cap/ceiling boundary cells; S136 last-branch-only trace HOLDS).

### FIX-4 + READY-8
- src/core/limits.def:20 `name     the C symbol, spelled exactly as it appears at its use sites`; unit list (:24-26): `"bytes" | "states" | ... | "positions" | "chars" | "frames" | "steps" | "work-units" | "count" | "percent" | "ppm" | "bits" | ""` -- no "characters"; real example `PCREC_UPROP_NAME_MAX, 48, "chars", "identifier cap"` (:182). Kind (:46-56) is a closed list of five: "compile budget", "runtime capacity", "size cap", "selection knee", "identifier cap". src/dump/limits_dump.c:93-101 prints the same five in the dump's own `# kind:` header. Design §10 (subject ~920-922): "unit: characters (bytes in byte mode); kind: a LANGUAGE limit with no override, unlike a §3.3 compile budget", names `lookbehind_branch_max`/`lookbehind_var_max` (lowercase). All three off-schema.
- tests/registry/limits_check.sh:97 `EXPECT_NAMES="$(cat <<'EOF' | sort`; :179 `if [ "$n" -eq 78 ] && [ "$NAMES" = "$EXPECT_NAMES" ]`; :180 "reports all 78 named rows". :192-198 `group()` comma-groups values > 3 digits ("Values below 1000 are never comma-grouped ... and are searched bare"), so a §3.11 must spell 65,535 (255 bare).
VERDICT: HOLDS.

### FIX-5
- vm_stmt.h:224 `struct { VmSeek sk; const char *slotx; int k; } seek;`. vm_stmt.c VSK_RESTORE arm (:457-460): `pcrec_sb_printf(sb->b, "    scan_position = (size_t)slot_values[%s];\n", s->u.seek.slotx);` -- `slotx` is the INDEX text inside `slot_values[...]`. VSK_BACKSTEP arm (:464-468): renders `%d` of `s->u.seek.k` and ignores slotx. Producer emit_vm.c:5894: `pcrec_vm_b_seek(v->sb, VSK_RESTORE, vm_rolef(v, "%d", sl), 0);` -- a bare slot number. Design §5.6 (subject ~686-690): "`VK_SEEK` already carries a `slotx` operand (used by `VSK_RESTORE`). The `range` row's back-step sets it to `D_i`'s slot expression ... `vm_r_seek`'s `VSK_BACKSTEP` arm renders `slotx` when it is present and the literal otherwise." Rendering `slotx` verbatim (as the sentence reads) would emit the slot NUMBER/macro as the count, not `slot_values[<slotx>]`; the wording is ambiguous at best. (Consequence is predicted, not built.)
VERDICT: HOLDS.

### FIX-6
- `build/pcrec --features all -fcomments -p rx --emit-main -o verify/lbc.c --pattern '(?<=ab|c)x'` (rc 0). lbc.c:450 `// lookbehind branch 1 of 2, fixed width 2: step back and run the branch FORWARD`; :468 `// lookbehind branch 2 of 2, fixed width 1: step back and run the branch FORWARD (the LAST branch: no retry frame)`; :464/:478 `// lookbehind END-CHECK: the branch must finish exactly where the assertion started -- ...`.
- Design: subject :396 `"fixed width %d" is an `--emit-ir` LISTING label, not emitted C.`; :431-433 "The `range` row gets its own role text ... Neither is emitted C." -- false under `-fcomments` (true only without it). The sibling texts (last-branch suffix, negative END-CHECK role wording) are visible in the output above; the "(the LAST branch: no retry frame)" suffix would be wrong on a range last branch (design: "pushed on every branch including the last"). I did not re-quote the other notes in emit_vm.c.
VERDICT: HOLDS.

### FIX-7
- vm_stmt.c:345-353 (`vm_r_return`): emits `if (%s_call_frame >= run->resume_cap) return %s_R_INTERNAL;`. emit_vm.c:8510-8521 comment: "THE SENTINEL TEST IS D72's CODE ... PCREC_ERR_INTERNAL is exactly the "the artifact detected an inconsistency between its own analyses" code D72 minted". So a second producer exists.
- docs/spec/match_api.md:1299-1306 [4¶6]: "Its one producer is module `lookaround`'s negative-polarity lookbehind end-check (`(?<!X)`) ...". Design §10 (subject ~923-925): "Its producer is the end-check of a `one-length` branch on the negative arm only." -- carries the "one producer" drift forward. (emit_vm.c:12100 comment not re-read.)
VERDICT: HOLDS.

### READY-6
- docs/design/la_d27_extract.md:155-158 "A lookbehind body's every TOP-LEVEL BRANCH must have a fixed width ... A body with any variable-width branch is REFUSED with pcrec's own reason."; :171 "`(?<=a{2,3})x`, `(?<=a?)x` -- REFUSED (bounded variable)."; :225 the refusal sentence "variable-length lookbehind is not implemented: every alternative of a lookbehind must have a fixed length ..."; :323 G2 "**pcrec REFUSES these too** (§2.5) ... the author must not write a match expectation for it".
- docs/design/sr_d27_extract.md:356-371: "per the **[DD-14.LB] amendment** (2026-08-24), which is a RULING, not merely a design intent" ... "A single call that is itself the lookbehind's one top-level branch, whose CALLEE has an alternation of DIFFERENT fixed widths (row 2 above, `(a|ab)`), is REFUSED by pcrec -- even though PCRE2 accepts it". plan_completed.md (7ddfbfa95, line 3740, [DD-14.LB]): "parked cell 2 ... lands as a RULED perr (tier 2), not a known_fail".
- libpcre2 10.46: `^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$` -> `ACCEPT maxlookbehind=2 caps=1`; on `ab` -> `[0-2]`.
- D27 corpora (tests/lookaround/d27/..., tests/recursion/d27/...) and whether §10 lists the extracts were not re-checked beyond the critic's grep; the extracts and the ruling text above are as described.
VERDICT: HOLDS.

### READY-9
- docs/spec/pattern_language.md:152 `| 7 grammar | a PCRE2-like sentence | the pattern is not well-formed; PCRE2 refuses it too |`; :151 shape 6 `| 6 resource | a sentence naming the budget and its raise flag | a compile-time budget was exceeded (limits.md §3.3) |`; shape 5 (:150) names "variable-length lookbehind, §7.4" as its example. The design (§10, subject ~915) puts the cap/ceiling/unbounded refusals in shape 7. A length limit is not "not well-formed" in the table's wording. HOLDS.

### READY-10
1. Subject :707 "Oracle differential, libpcre2 10.46 (PC-3's harness)." tests/registry/pcre2_check.c header: "the registry against libpcre2 (step PC-3)" -- a registry compile/row check, not a match differential. tests/lookaround/run_lookaround_diff.sh exists. HOLDS.
2. Subject :1041 "`match_api.md` §6¶19 says no bump is owed when no previously compiling ..." ; match_api.md [6¶19] reads "**What is fixed within one `abi`:** the emitted output is byte-exact, whole-file ... for a given pattern, prefix and option set"; [6¶18] reads "**What changes at a bump:** any change to the emitted scaffolding for identical inputs ...". HOLDS (cite points at the weaker paragraph; whether ¶19 later states the no-bump rule I read only its first lines).
3. src/opt/mrl.c:509-510 (pcrec_cwmax header): "`pcrec_cwmin` may under-estimate for free. This function may OVER-estimate for free". pcrec_cwmin's own header (:680-686) says "this function's safe direction is DOWN" -- no literal "for free" there, but the premise is the same. PARTLY (literal phrase appears in the cwmax header, about both).
4. Subject :760 "Latent until [branch-reset] lands"; `grep -n -i 'branch-reset\|branch_reset'` on `git show 7ddfbfa95:docs/dev/plan.md` hits only line 948 (the extended module list "... conditionals, branch-reset;"), no `- [branch-reset]` row. HOLDS.
VERDICT (READY-9): HOLDS. VERDICT (READY-10): HOLDS (item 3 PARTLY).

### READY-11
- `git show 7ddfbfa95:docs/dev/plan.md` row `- [IFACE-PUSH] STATE:not-started` at line 1280 with its 10 continuation lines (1281-1290, saved verify/iface_full.txt): `grep -i -c lookbehind` = 0; no `varlookbehind`/`max_var`. Its refs line (1284) names docs/design/plan_row_bodies/IFACE-PUSH.md, which at the freeze also has 0 hits for "lookbehind". The design's deferral (subject §5.2 ~530 and §13.3) names [IFACE-PUSH] as the home of the max_varlookbehind setting, but the row does not carry it.
VERDICT: HOLDS.

Addendum to READY-10 item 2: [6¶19] in full says outputs are byte-exact within one abi and "a difference has found a pcrec bug"; it never states "no bump is owed when no previously compiling pattern moves" (that is only implied by ¶18's "for identical inputs"). So item 2 is PARTLY: the cite is the wrong/weaker paragraph, not an outright misquote of a different rule.

### SOUND-4
- libpcre2 10.46 (oracle_probe c): `(?<=a(*ACCEPT)b{1,2})x` -> `ACCEPT maxlookbehind=1 caps=0`; `(?<=a(*ACCEPT)b)x` -> `ACCEPT maxlookbehind=1 caps=0`.
- pcrec review tree on `(?<=a(*ACCEPT)b{1,2})x`: `pcrec: (*...) requires module 'verbs' (pattern offset 5)`. Latent only; unreachable until the verbs module.
VERDICT: HOLDS.

### SIMLIT-1 (spot check, 3 numbers against raw files in simlit/)
1. simlit/out_b_0.txt: `patterns=8592 (with>=1 varying branch: 8466) subjects=1093 cases=37409568 sim-matches=16140897` and `DIFFS(excl D142)=0`. Cross-check: subjects 3^0..3^6 = 1093; cases = 8592 x sum over subjects of min(4, len+1) = 8592 x 4354 = 37,409,568 (computed by hand: 1+6+27+108 + 4x(81+243+729)=4354). Matches.
2. simlit/out_u_0.txt: `subjects=1365 cases=39274032 sim-matches=14250964 sim-INTERNAL=0 sentinel-pops=17129347`, `DIFFS(excl D142)=0  D142-class=3714`; byte file shows sentinel-pops=0 (matches "dead under byte").
3. Sabotage S3 (simlit/out_b_3.txt): `sim-INTERNAL=8586600`, `DIFFS(excl D142)=8586600` -- equals the "8,586,600 byte cases" in SIMLIT-3.
Not re-run: the simulator itself (no re-execution), only the recorded outputs and their arithmetic.
VERDICT: HOLDS.

VERIFY COMPLETE

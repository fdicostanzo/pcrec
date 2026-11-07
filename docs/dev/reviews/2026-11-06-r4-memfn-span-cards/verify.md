# verify

## Verdicts

### PREMISE-1 + SLOT-5
Verdict: PARTLY (fact HOLDS; consequence "vrun keys ARE row-1 keys" not forced).
Ran: `build/pcrec -p rx -o v1.c --pattern '(?i)x/1234'` -> `RX_MEMFN_FORMS "none"`; with `-fmemfn-simd` -> `RX_MEMFN_FORMS "vrun@w32+w16"`; `RX_MEASURES ""` both. Read: span_cards §2.5 (rev0:130-133) "Row 1's SIMD-on arm needs no SIMD card ... `none` means the text is identical"; D186 add. 2 C9 (decisions.md@80341284e:10046) "NOT smp20 (on '/' the SIMD build calls memchr, the same as scalar)" — speaks of '/' only; span_pick.md:184 (§The pick 6) "a `-fmemfn-simd` build may pick its own position by its OWN T-PICK row ...; else SIMD forms are rungs (D147)".
Note: the design's premise is false on its own witness (the census hedge at :133 would fire at once), so J6's vrun half is not "droppable alone" as long as row 1 claims a SIMD-on arm; but §The pick 6 lets row 1 price the SCALAR layer only with SIMD forms as rungs — the fix is either vrun keys to row 1 or "row 1 prices the scalar layer; SIMD forms ride as rungs", stated. Not a forced key move.

### PREMISE-2 (a)(b)(c)
Verdict: HOLDS (a, b, c); the answer-gate aside PARTLY (wording only).
Read: (a) every `mf_art_begin` in memfn/tests/g2/g2_win_gen.c (:646,:657,:740,:795,:852,:931,:952,:1040,:1042) passes `MF_P_PORTABLE_ONLY` (grep of non-PORTABLE begins: 0), site policy :639 `s.policy = MF_P_PORTABLE_ONLY`; g2_simd_gen.c:5-10 is a separate family "with the policy word lacking MF_P_PORTABLE_ONLY". (b) vany.c:16 "NOT ROUTED. No mf_site row, no fn_rows[]/fd_rows[] entry". (c) vrun.c:19-25 "ONE RUN term of length 2..VRUN_MAX_RUN ... REACH: ... not shorter than VW + T"; consistent with my probe (vrun rides the `x/1234` run of an ofsskip site, not a stop set). Design rev0:158/:166 claim "ONE window-site builder" and "one stop set S at offset 0".
Note: the SIMD cards cannot come out of g2_win_gen.c as written; vrun needs a RUN-term subject. The "find-all count" gate (rev0:158) vs g2_win_run.c's reference check (g2_win_gen.c:18-19) is a wording mismatch, not a defect.

### PREMISE-3
Verdict: HOLDS.
Read: memfn/src/formhash.c:240-241 `int walk = !strcmp(id, "walk"), libc = !strcmp(id, "libc"); if (!walk && !libc) return -1;` and :291 `mf_art_begin(&ar, "mf", MF_P_PORTABLE_ONLY, 0, NULL, NULL)` + `mf_emit` (no SIMD text renderable); memfn/data/cards/kit-kernels.tsv:21-23 "the kernel renders outside any site, so mf_form_hash cannot hash it yet: the deps are OWED"; finder.c:36-38 PAIR "holds only for the asker that renders it (the asker fact SF_ASKER_PAIR)"; runcmp.c rows[] (`words`, `overlap`, ...) are run-verify compare rows.
Note: "add the ids to canon()" is a new hashing entry shape (policy word + site kind per id), not table entries.

### PREMISE-4 + SLOT-3 + CONTRACT-4
Verdict: HOLDS for (b) R-35, (c) Goal 1, S1229's anchor; PARTLY for (a) the §3.6 abi rule.
Read: (a) measure_sets.md:905-908 "D162 ruling 1 is KEPT: data regeneration that moves an emitted byte is an abi event. The stamp names the set, so a default change moves the stamp of every consulting artifact. Every default-set change is therefore an abi event" — the literal "every" contradicts (B)'s "NO pcrec abi", but the "therefore" rests on consulting artifacts, of which stage 2 has none (every stamp `""`); so (B) needs a §3.6 hunk (or the ritual), it is not a hard ruling breach. (b) requests.md:815-818 "Stage 2 adds no reader, moves no emitted byte, and leaves DEFAULTS unchanged" / "It flips DEFAULTS to zen4-grid3 ... Its flip needs its own landing verdict from main": (B) "No ruling is amended" (rev0:479) is false. (c) `build/pcrec --list-measurements` prints grid1's row with `default_for` = `idk` (col 8), so under (B) two rows change, contradicting Goal 1 (rev0:29) "changes by exactly the new set's row". S1229_meas_default_table_class.sh:13 `SAB_BEFORE='    { "idk", "zen4-grid1", 1u },'` = measures_table.inc:130, lost under (B). CONTRACT-4's "no count pin": run_measures_tests.sh:75 is a floor `-ge 1`, and :77-94 is the DEFAULTS/default_for/DEFAULTS.log check — confirmed.
Note: (B) is not answer-free on the ruling axis; (A) or a ruling from main.

### PREMISE-5
Verdict: HOLDS.
Read: finder.c:282-289 PAIR row "No deny: within E-find it moves bytes under E-find's own (`window-search`), and fn-pair has none", its facts `SF_SPAN0 | SF_TWO_MEMBER | SF_ASKER_PAIR`; the asker fact is set only from `st->renders_pair` (finder.c:656), hard-wired `.renders_pair = 1` at window.c:1840 (the only setter); options.def rows are vrun-*, precheck-assign-byte, fd-d1 (one-member D1 only), fd-pres-*, window-search ("denied, a fixed-width pattern takes the forward scan and any other window search a plain byte loop", :90-95), window-skip — none routes a two-member {X,x} stop to the R7w walk.
Note: `find_hit.walk.*.alt` and walk-vs-pair on {X,x} need a new test-only force; "force rows" (rev0:158) names nothing existing.

### PREMISE-7
Verdict: HOLDS.
Read: memfn/data/cards/kit-kernels.tsv:7-14 "ver 1 (lane simdset, 2026-10-29): `mf_kernel_find_any` ... vany2-w16 vany2-w32 vany3-w16 vany3-w32 ... vany2-body vany3-body", quantities beta.. with `vs` WALK/LIBC, all UNMEASURED; the design names it once (rev0:92 "declared in `kit-kernels@1`, UNMEASURED") but never says which card (kit-kernels@1 or kit-grid@3) governs vany rows from stage 2 on.
Note: trivial text fix; append-only rule of the card file makes the choice matter.

### PREMISE-8 + CONTRACT-2
Verdict: HOLDS (as the readers stand); the fix is cheap.
Read: cli/main.c:82 "It checks nothing the kit checks"; :131-133 `want[6] = { "key", "value", "unit", "value_e6", "status", "source" }`; header keys read: id/rev/values_digest/class/tier/composite (:139-145), `values_digest` copied verbatim, no `format` key, no recompute. tests/memfn/arm_fixtures.c:1527-1567 `fd_load_set`: rows section only, `ms->id = path`, no header, no digest, and no `status` check (a `null` row with a value is handed — CONTRACT-2's extra point confirmed).
Note: §4.2's "follow the same rule" cannot mean a digest check without new code; the least form is "test levers hand noise UNMEASURED always" (SLOT-6's), stated.

### PREMISE-10
Verdict: HOLDS.
Ran: `grep -n '3381\|3,381\|3536\|3,536' smp20.out smp20.py span_pick.md` -> smp20.out only `:38 "@5 {4} at 3536 points"` (a with-data arm), smp20.py no hit, span_pick.md:306-307 "(3,536 points) P's argmin is '/' at 3,381" and :325. smp20.out has 42 lines.
Note: cite span_pick.md:306-307 (or commit the P-blind count); §7's control has no committed line to reproduce.

### MEAS-1
Verdict: HOLDS.
Ran: the critic's meas/aa/A/a.c (read: a plain find/count loop) copied to verify/aa/{A,B}, `(cd $x && gcc -O2 -c -o a.o a.c && gcc -O2 -o bin a.o)` -> `cmp A/bin B/bin`: identical; also `build/pcrec -p rx -o p.c --pattern '(?i)x/1234'` twice + `gcc -O2 -c` in two dirs -> `cmp A/p.o B/p.o`: identical. Read: kit_proof/measure/measure.sh:71-72 `cmp -s .../DEF/a.c .../AA/a.c || { say "build: ... DEF and AA sources differ ..."; return 1; }`; design rev0:168-169 "a SEPARATE compile and link of the same text ... so code placement differences are in the floor".
Note: the A/A arm is a same-binary rerun (only run-time ASLR/page placement differs); the "placement in the floor" claim is false unless the arm is perturbed.

### MEAS-2
Verdict: HOLDS.
Read: rev0:206 "pass iff `noise_e6 / value_e6 <= gate_e6`" with `gate_e6` 30000 (rev0:100); measure_sets.md §7.3 "A group passes iff its noise <= its card's `gate_e6`" with noise "as fractions of the value" — no sign/zero rule either. Ran `python3 -I meas/est.py` (read: implements both readings literally and correctly): literal gate True on all 6 cases incl. `verify~0` (301 %) and `verify<0`; scaled gate refuses outlier/verify~0/verify<0.
Note: write `noise_e6 * 10^6 <= gate_e6 * |value_e6|` plus a near-zero rule.

### MEAS-3
Verdict: HOLDS.
Read: measure_sets.md:1276-1290 §7.4 "A delta row (an arm's effect against its base: ... a charge, ...) is NULL when ... |Δ| <= max(A/A floor ..., FRG x base) ... [or] The launch-paired deltas disagree in sign"; rev0:194 verify_cmp "m(arm) - m(null) per launch, then the median" and enter "the pass arm minus the fail arm" (rev0:83) are such deltas; the design's only NULL text is rev0:324 (derived-noise propagation). est.py `verify<0` gives value -30000 (a negative cost) admitted by the literal gate.
Note: delta rows take §7.4 (NULL, never refusing the group).

### MEAS-4
Verdict: HOLDS (mechanism and arithmetic); size on the box SUSPECTED, as the critic says.
Read: measure_store/zen4-grid1/1/set.tsv:67 `kit.eps.streamed.slope ratio 1730 ... F3 A/A p90 (member-free single calls)`; rev0:197-198 aa = the GROUP's A/A arm "scaled to the row's unit by the same ratio as the value" (absolute); rev0 §3.7 J2 = ONE group "walk, walk#b, memchr, pair x 3 lengths"; rev0:207 "the unit group at half" (1.5 %). Ran `python3 -I meas/slope.py` (read: the arithmetic aa_rel/ratio): 0.173 %/0.06 = 2.88 % (critic 2.83 % at 0.17 %) > 1.5 %; vrun-w32 (r 0.03) 5.67 % > 3 %; even 0.10 % gives memchr 1.67 % > 1.5 %. measure_sets §7.3 says aa "as fractions of the value", which the design departs from.
Note: p90 is a pessimistic stand-in for the per-group median, but at 0.10 % the unit group still refuses on memchr.

### MEAS-5 (a)-(e)
Verdict: PARTLY — (a) first half HOLDS, (a) second half REFUTED, (b)(c)(d)(e) HOLD.
Read: rev0:187-192 "m(p,l) = the median over 7 rounds of ns per unit of work (per byte, per hit, ...)" and "find_byte: the least-squares slope of m over the three lengths" — slope of ns/B over length is ns/B^2 (slope.py: -1.7e-9), HOLDS. But "find_hit and enter: the slope of TIME over hit (candidate) count" (rev0:191) names time, not m, so the critic's "m in ns PER HIT ... no slope recovers h" models a sentence the design does not write: REFUTED for that half. (b) the miss-only point shared with J2 (rev0:82) is another job: HOLDS. (c) "the group's A/A arm" unnamed for J1/J5/J6 (J4's is `null#b`): HOLDS. (d) sp's unit/normalization unstated: HOLDS. (e) est.py: noiseA (isqrt of rounded sd^2 + aa^2) vs noiseC (one root) differ on 4,793/20,000 inputs — re-ran, same count; integer LS recipe and even-median unstated: HOLDS.
Note: Goal 3's exact recompute needs a literal integer recipe.

### MEAS-6
Verdict: HOLDS.
Read: rev0:82 find_hit points g in {4096,256,32} + the miss-only point; rev0:248 J3 "each density" a group (12 groups) — so one row spans 4 groups. Ran slope.py: LS weights at x = {0,1/4096,1/256,1/32} hits/B: -13.0,-12.7,-7.3,+33.0; g=32 share of Sxx 0.739. span_pick.md:278 "{x,X} 1,097 ppm, '/' 4,154" (g ~ 912 / ~241) vs g=32 = 31,250 ppm. A/A propagation 38.4 x d (independent) vs design's 1 x d: arithmetic correct.
Note: the noise-scaling half is a model argument (independent vs constant offset), sound as stated.

### MEAS-7
Verdict: HOLDS (model faithful; rates reproduce).
Read meas/drift.py: per group, fresh launch effects (sd sb) + within noise (sw), A and A#b paired in-launch, floor = median |A#b - A|, refuse iff |median(group walk) - unit walk median| > floor — this is rev0:182-183 "a group whose in-group walk differs from the unit row's walk beyond its A/A floor is REFUSED" as written. Re-ran `python3 -I meas/drift.py`: no-drift false REFUSE 0.245/0.295/0.387/0.572 at sb 0/0.5/1/2 (identical to the critic); drift=1 caught 0.52-0.63. stats.py's variant (sb 1, sw 1) gives 0.252. "Undefined" part: J4 arms are forms + `null`, J5 whole artifacts, J1 widths (rev0 §3.6/§3.7) — no walk arm: confirmed from the job table.
Note: the comparison mixes between-launch variance (difference of medians) with a within-launch floor; with ~40 groups FULL is improbable.

### MEAS-8
Verdict: HOLDS (faithful).
Read meas/sweep.py: 5 widths truly equal, 8 cells, (a) iff 128 within the floor of the best on every cell, (b) iff some w beats 128 beyond the floor on >= 1 cell and loses on none — rev0:228-233 literally. Re-ran: sd 0 a 0.063 / b 0.551 / c 0.386; sd 1 a 0.042 / b 0.504 / c 0.454 (identical).
Note: under a no-effect truth, outcome (b) (a D186 unit change, PAIR cards delayed) is picked about half the time.

### MEAS-9
Verdict: HOLDS (as a derivation gap; the exact alternative figure depends on the error model).
Read: rev0:397-399 "a departure happens with probability Phi(-z) ...: 15.9 % at z = 1, 2.3 % at z = 2"; rev0:199-200 noise is a 5-launch sample s.d., not /sqrt(L). Re-ran `python3 -I meas/stats.py`: z=2 -> 0.0062 (stored median vs truth, iid launches) and 0.0577 (new-run draw vs s from 5); P(s < 0.5 sigma | L=5) = 0.090.
Note: Phi(-z) assumes a known sigma; with 4 dof the figure is not 2.3 % under either reading; state the model and use a t_{L-1} quantile.

### MEAS-10
Verdict: HOLDS (under the scaled reading of the gate, MEAS-2).
Ran est.py case `outlier` (4 launches within 0.03 %, one +8 %): value 1,000,100 (median unmoved), noise 35,764 = 3.58 % > 3 % -> scaled gate False (literal gate True, MEAS-2).
Note: robust centre + non-robust spread; a MAD-based spread fixes it.

### MEAS-14
Verdict: HOLDS for J3 and the window figures; PARTLY for "+2/3".
Read: rev0:248 "J3 hit | ... = 12 groups, 4-5 arms | 54"; the §2.5 keys (rev0:120) give `one` arms memchr, walk, pair (+ walk#b) = 4 and `alt` pair, walk (+ walk#b) = 3 -> 6x4 + 6x3 = 42 (stats.py). Window: "~35-45" (§0), "~35-minute" (rev0:60), "~32, ~45 with quiet-gate waits" (rev0:252). rev0:60 "the cost is +2/3 of a ~35-minute window": 5/3 launches is +2/3 of the 3-launch cost (12.5 of 18.8 min, stats.py), which the sentence can be read to say; loose wording, not an error.

### SLOT-1
Verdict: HOLDS.
Read: docs/spec/measures.md:43 [2¶2] "The sections are `header`, `cards`, `rows`, `cells` and `members`"; :80 `cells | cell group arm length launch round ns_e6`; src/core/ks_measures.c:44 `meas_sections[] = { "header", "cards", "rows", "cells", "members" }`; measure_sets.md:557-558 "**The `raw/` directory is gone.** Its job (the reader's input) moved into the set's `cells` section, where the checker can reach it (§1.5)". The design adds `raw.tsv` (and `cells.tsv`) without naming the `cells` section.
Note: the design must use `cells` or argue (e.g. embed size) why not.

### SLOT-2
Verdict: HOLDS.
Ran: `git show 80341284e:docs/dev/decisions.md | grep -i 'contributes its\|method cards to that\|cards to that script'` and the same on plan.md -> no hit (plan.md's one "contribut" hit is unrelated). Design rev0:151 quotes D176 Q3 as "the kit contributes its method cards to that script". D176 Q3 (decisions.md@80341284e:9920) and [MEASURE-SET] FORMAL LIBRARY (plan.md row [MEASURE-SET]) say "a canned, self-contained pcrec script (part of pcrec, not bench)". measure_sets.md:1203-1205 rejects "(b) A mode of the kit's harness only ... inverts the ownership" and "(c) One python script. Install time must not need python."
Note: misquote confirmed; §3.1 must engage §7.1 (a stage-2 slot may be fine, but say why).

### SLOT-7
Verdict: HOLDS (wording); the narrowing is arguable, not wrong on its face.
Read: plan.md@80341284e [MEASURE-SET] "RULED Q1 ...: plan_cost.def rows migrate into the sets" (and D176 Q3 "`plan_cost.def` rows migrate into the sets"); design rev0:407 "when plan_cost.def's cost rows migrate into sets (D176 Q1), its policy rows stay". The ruling says "rows" with no cost/policy split (and it is in Q3's text in decisions.md, Q1's in plan.md).
Note: the design adds a distinction the ruling does not make; it needs main's ruling or a POLICY home argued.

### SLOT-4
Verdict: HOLDS.
Read: tests/memfn/finder_check.py:395-399 `if table == "kit-grid" and c["dims"].split(";")[0] == "form": f = parts[2]; fid = "walk" if f == "WALK" else f; ...` — any other first dim falls through to `ok()` with no resolution and no `unreached` line. Design cards rev0:106 `find_byte` dims `method`, `find_hit` `method;landing;split`, `enter` `kind;entry` (rev0:109) — skipped; only `verify_cmp` (`form;cls;pass`, :108) reaches the guard. Keys spell `find_byte.memchr` (rev0:121) while deps list `walk, libc` (rev0:106) and canon() knows `walk`/`libc` (formhash.c:240). `enter`'s dep "kit:form.<the site's method>" names no dim of its key.
Note: S2c's witness "check C resolves every new dep" would read green with nothing resolved.

### SLOT-6
Verdict: HOLDS.
Read: cli/main.c:73-76 "THE HARNESS'S SET READER, the test build's `--harness=measures=FILE` lever until [MEASURE-SET] M0's loader ([KNOW-SRC]'s ksrc.c) gives a shipped compile one"; M0 is on main: plan.md@80341284e [MEASURE-SET] status "M0 on main (measures row, measure_store/ zen4-grid1@1, --measures + config, stamp, --list-measurements)" and cli/main.c:1549 handles `--measures NAME|NAME@REV|FILE`. arm_fixtures.c:1527-1567 is a further private parser (see PREMISE-8).
Note: the sunset condition is met; teaching the lever format-2 extends a mechanism its own comment retires.

### SLOT-11
Verdict: HOLDS.
Read: memfn/docs/requests.md:836 (R-35) "**Sabotage ids:** the kit takes its own from the top of the free range and records them in its first commit (three lanes are allocating)"; design rev0:20 "ids the manager's" and rev0:490 "(ids: the manager's)".
Note: trivial text fix.

### CONTRACT-1
Verdict: HOLDS.
Read: tests/memfn/finder_check.py:343-346 `for fn in sorted(os.listdir(sdir)): if not fn.endswith(".tsv"): continue` over memfn/data/sets; :312-324 `digest()` feeds `b"pcrec-meas-1\0"` and key/unit/status/value only; :372-374 `bad("%s: values_digest %s, recomputed %s" ...)`. Design rev0 §3.8 step 1 writes `memfn/data/sets/kit-interim-grid3.tsv` (FORMAT 2) and §5 lists finder_check.py:320 as UNCHANGED.
Note: a format-2 interim there turns check C red (or is silently excluded); list finder_check's digest as a reader.

### CONTRACT-3
Verdict: HOLDS.
Read: scripts/ksgen.c:347-358 writes each `KsMeasRow` positionally `{ {cols}, value_e6, unit_code, status_code }`; tests/knowledge/meas_store_check.c:79-80 `decode_to(... "pre", pre) || decode_to(... "fresh", fresh)` compares the embedded pre-parse with a fresh parse. `grep -n ksgen span_cards_rev0.md`: no hit. An appended `noise_e6` field is zero in the pre-parse unless ksgen writes it.
Note: list ksgen.c and the regenerated measures_table.inc in §4.5/§8.2.

### CONTRACT-5
Verdict: HOLDS (re-run).
Ran (scratch verify/): grid1's set.tsv with `id` -> `bigset` and `kit.eps.streamed.slope` value_e6 -> `2000000000000000` (> MF_MEASURE_MAX 1e15, memfn.h:1220), digest refixed by `python3 -I tests/knowledge/ks_ref.py digest big.tsv` (f6abb3af0853008e), then `build/pcrec -p rx -o c5.c --measures=big.tsv --pattern P` for `a[bc]+d`, `foo|bar`, `(?i)x/1234`: all rc=1 "pcrec: internal error: the memfn kit refused the window family's phase-1 ask on the DFA prefilter (src/gen/emit_dfa.c, window_reply_ask)". Control (same set, id `okset`, value unchanged, digest refixed): rc=0. measures.md [2.2¶3] states no value bound.
Note: a loader-accepted set kills every compile with an "internal error"; the design copies the shape for noise (bound checked only kit-side); add the loader refusal (value and noise).

### CONTRACT-6 + COST-1 + SLOT-10 + MEAS-13
Verdict: HOLDS (no evaluator exists; S2a's rule would be a new engine; the loader checks no derived value). MEAS-13's math points stand as text gaps.
Ran: `grep -rn -i 'cross-lin\|ratio-complement\|interp-log2'` over src, tests/knowledge, memfn, measure_store, scripts (*.c *.h *.py *.sh): hits only the NAME registry ks_measures.c:36-39, mfixtures.py fixture text (:13, :113), and memfn/data/sets/generate.py:104-130 — a PRODUCER computing its own synthetic values inline (`v = 1.0 - BETA[f][i] / BETA["WALK"][i]`), not a by-name evaluator. docs/spec/measures.md [3.2¶2] "A value a selection reads is the row's `value_e6` as stored; no reader recomputes a derivation." No `recompute` in ks_measures.c or ks_ref.py.
Note: S2a's "derived-noise rule in spec, C and ks_ref.py" is a new recompute engine with population zero in zen4-grid3; "derived noise is the producer's rule, unchecked at load" (or `-` until a producer) meets R-35 and D77.

### CONTRACT-9
Verdict: HOLDS.
Read: measure_sets.md:490-494 "**What the digest excludes.** It leaves out every provenance column (`abs_ns_e6`, `noise_e6`, `n`, `source`, ...)" — false for format 2, and the design lists only measure_sets.md §4.1 (rev0:338) and :476,:1923 (rev0:384), not :490-494. tests/knowledge/mfixtures.py:177 `("format", hdr("format", "2"), "format 2")` is the refused-format fixture S2a makes legal; the design names mfixtures goldens generically (rev0:461). The "four constructors" vs three is PREMISE-9/SLOT-12 (not re-checked here; both critics' greps agree on three).
Note: trivial list additions.

### COST-2
Verdict: HOLDS.
Read: rev0:493 S2b content "`census0.py`, its run (J0) and output; `cells.tsv`'s row-1 population"; rev0:494 S2c creates "`memfn/measure/` (§3.1)" where §3.1 homes `cells.tsv`; `ls worktrees/crit-memfn-span-cards/memfn/measure` -> No such file or directory.
Note: name cells.tsv's S2b home (or move its writing to S2c).

### COST-4
Verdict: PARTLY.
Read: docs/design/alt_normal_form.md:583-585 "it crosses the seam with its consumer, as a field the kit's `fields.def` declares ... and that crossing is the kit's `MF_SITE_ABI` event, not 2p's" (also :1909) — a FUTURE consumer's crossing, not a scheduled stage-3 bump; design hard-codes "MF_SITE_ABI 23 -> 24" (rev0:15, :291, :460). measure_sets.md §3.6's own house form is "the next number at landing (never a literal in a brief)".
Note: the race is real in kind (a literal number with two candidate landers), but alt_normal_form does not schedule stage 3 to take 24; fix = "next free MF_SITE_ABI at landing" plus a named base commit per unit.

### COST-5 (8) and (10)
Verdict: HOLDS for both (the critic's reason for (8) is slightly off; the conclusion stands).
Read (8): rev0:440-442 "Control: on smp20 it reproduces `smp20.out`'s band-0 argmin at the stand-in point; plant: a census reading the incumbent from the wrong trace field moves smp20's line (red)". smp20.out's `least @...` column is the argmin over ALL stops (P line :2 / :13), computed without the incumbent; at band 0 the pick is the argmin whenever it is strictly cheaper, so the incumbent's identity never enters the controlled quantity — the plant stays green unless the control also diffs the incumbent column (smp20.out :7-14 "incumbent @...").
Read (10): rev0:494 "(10) an arm's text from another method than its key (dep hash mismatch: check C red)"; finder_check.py:395-399 check C maps a key's first token to a form id over SET rows and cards; it never reads the rendered cell text G2 `--cards` produced; and for `find_byte`/`find_hit` (dim `method`) it does not run at all (SLOT-4).
Note: (10) needs a cell-text-hash vs dep-hash check in G2 `--cards`; (8) needs the control to diff the incumbent.

VERIFY COMPLETE

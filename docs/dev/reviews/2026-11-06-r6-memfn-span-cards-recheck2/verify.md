# verify — memfn-span-cards-r11

## Verdicts

### READY-1
HOLDS. ks_measures.c:466-481 (6f1b40f75): non-`-` inputs on a non-computed row -> mfail "a %s row names inputs"; computed-row inputs must pass is_row_key/is_cell_id (:396-415, cell id column, not the `arm` column). Design ef2f130fc §4.4 (:935-941) puts the §2.2¶3 hunk (measured `delta` row `inputs` names ONE base arm) at S2c as spec text only; the §9 S2a/S2c/S2e rows (:1222-1226) and §10.2 table (:1159-1168) name no loader/ks_ref.py/mfixtures change for it (S2a: "bound and status refusals" only). No unit assigns the loader change.

### READY-3
HOLDS. run_measures_tests.sh STORE loop (:46-64 R4 cmp of NAME listing vs file, R5 NAME decoded vs ks_ref decode of FILE) and embedded-text compare (:104 cmp emb/$name.text vs set.tsv) all go red once the embed omits `cells` (design §3.8 :806-820 "text and pre-parse alike"), given the file has cells (grid1 has an empty cells section only, :105). The design names run_measures_tests.sh only as a reader of the listing's columns (§10.2 :1168), not these compares; "No embed reader needs the cells" (:819-821) omits them. Detector claims for S1241/S1232 not separately re-run (not verified).

### READY-4
HOLDS. Makefile:358-362: text step is `sh scripts/embed_text.sh` (header: "embeds each FILE's bytes, unmodified"); ksgen only the pre-parse. `grep embed_text` over the design: 0 hits; design names only scripts/ksgen.c (:807, :1167). Sabotage (v) detector (:1226) names no check file.

### READY-6
HOLDS. Design §3.4 (:570) "The recompute reads ONLY the set file" vs §3.5 (:668-672) "The one recorded input ... list of groups that never ran ... in PROVENANCE.md" (prose, no format). Goal 2's floor (§1 :146) needs the census (form, cls) population ("for each census (form, cls), at least one verify_cmp row") and J1's verdict ("pair unless J1 (b)"; verdict lives in span_cards/slot/j1/verdict, :740, not in the set). Neither is in the set; a never-ran group's keys are not recoverable from a group name. (Pair presence could be inferred from rows, but the census key list cannot.)

### READY-8
HOLDS. Design §2.4 (:294) "Every zen4-grid3 row's `deps` column is `-`"; measure_sets.md at 6f1b40f75 §2.4 (:632-634) "A row's `deps` column holds `owner:dep-id=hash`, written by the producer", staleness on them (:662-668), §7.2 (:1226-1232 region) "refuses a row ... whose `deps` lacks a card dep". Design still claims staleness via form hash (:744, :1341). Mitigating fact the critic omitted: grid1's committed rows already carry `-` deps (set.tsv rows 35-40), so `-` follows precedent, but that precedent already contradicts the measure_sets text; the finding's contradiction stands.

### READY-2
HOLDS. At 6f1b40f75: kit-grid.tsv 10 cards, 9 with `kit:form.` dep; kit-kernels.tsv 5 more (beta, f, saving, xover, gstar, all with `kit:form.<form>` dep, form first); kit-synthetic 0. finder_check.py:333-343 walks every card table. Population 9+5 = 14 at the tree, 17 after kit-grid@3 (+3, design :290-293). The design's "12 with a kit:form. dep after kit-grid@3" (§9 S2c :1224) counts kit-grid only (9+3).

### READY-5
PARTLY. Holds: (1) run_sabotage_matrix.sh:177ff has a CLOSED SAB_SUITES vocabulary (codegen, trie, ... resource); the design (:1216-1224) names no runner for (j),(j2),(k),(l), whose detectors are `--dry-run` assertions of the slot harness (never built by make, §3.1); (2) design :517 "a draw failing either is re-drawn (seeded, deterministic)" states no bound, so a plant forcing every draw to fail loops; (3) cli/main.c:1567-1573 takes the set only as `--list-measurements=X` (bare flag = index), while design :446 and :789 spell `--list-measurements FILE` / `draft.tsv`. Weaker: (l) -- the gate text (:499-500) says "find-all count ... against the generator's planted count" (count-only, so a pos+1 shift passes), but sabotage (l) (:1224) says "expected-count gate against the generator's planted positions"; the text is ambiguous, the count-only reading is the stated mechanism. (o)-crash claim (finder_check digest int(value_e6)) not re-run.

### MEAS-1
HOLDS (mechanism), magnitude softer than claimed. Design §3.2 (:511-518): pads "drawn by a seeded generator from (job, l, arm)", re-draws "seeded, deterministic"; no run/window term, and §3.5 re-runs the SAME frozen commit "whole", so a re-run links identical placements; place_drill.py A (:63-65) computes held as r2*r2 (independent runs), and its own rev-1 comment (:67-68) says a re-run has "identical text, identical layout". My own run (verify/v_seed.py, place_drill's unit_refused and model copied from the design's file, 20,000 trials, v_seed.out): s 0.5% tau 0.5%: refused 5.86%, held seeded 0.73% vs independent 0.50%; tau 0.7%: 7.39% vs 4.15%; tau 1.0%: 36.17% vs 27.98%. The critic's 1.02% vs 0.38% (meas/seeded_place.out) is not reproduced at tau 0.5 (about 1.5x, not 2.7x); at tau 0.7-1.0 the ratio is 1.3-1.8x. Direction and cause hold, "~3x" overstates.

### MEAS-2
HOLDS (text ambiguity real). §3.5 (:675-680): PARTIAL "Goal 2's floor holds over every key not named"; REFUSED "or Goal 2's floor fails"; §1 Goal 2 (:146) "passes its gates but misses the floor is REFUSED". By hand from §3.7's job table: J3 holds every random find_hit row for libc/walk/walk-set; if J3 is drift-refused, reading A (floor over all keys) -> REFUSED, reading B (named keys exempt) -> PARTIAL with no priced random find_hit row for those forms. Under A every job's refusal removes a floor key (J2 byte: find_byte keys; J3; J4 verify per census; J5 NONE; J2p pair unless (b)), so PARTIAL is reachable only via J1 (b) and the "some group is refused" clause is dead; under B the r5 GOAL2 scenario (all non-unit groups refused but one) is PARTIAL with 3 priced keys. Re-read outcome_drill.out S3/S6/S8: consistent with this hand derivation. The text does not pick a reading.

### MEAS-3
HOLDS. §3.5 (:674) "A group passes iff every cost row in it passes"; §3.7 J2 row: byte group = libc, walk-set and twins; so a walk-set row over its gate refuses the group and removes find_byte.libc from the set (REFUSED under reading A since every find_byte key is a floor key, PARTIAL with libc unpriced under B). Normalisers (ctl per job, W unit only, trim per row) read no sibling, as the critic says.

### MEAS-4
HOLDS. Threshold = 3 x isqrt(sp2_2+sp2_j) = 3 x sqrt(2) s_L = 4.24 s_L on the per-launch scale; the statistic |med_j - med_2| of 7 launches has s.d. about 0.66 s_L (sqrt2 x 1.2533/sqrt7 = 0.67), so the threshold is about 6.4 s.e. Re-run (verify/drift_se.py, 3000 trials, drift_se.out): sd 0.65-0.67 s_L; s_L 1%: d 3% refused 18.8% by the rule vs 90.2% at 3 s.e. (0.3% false at d 0), d 2% 3.0% vs 52.1%. The design's "smaller drifts are unresolvable by a 7-launch median comparison" (:672ff drift paragraph) is false for 2-3% drifts at s_L 1%. (Script imports the critic's mine.py; the hand derivation above is independent.)

### MEAS-5
HOLDS (mechanism); magnitude depends on the critic's assumed spike model. Design §3.5 (:632) NULL rule: "UNLESS every D_l > 0 and med(D_l) > aa_D" with no trim, while the spread trims one launch. Re-run (verify/null_outlier.py, 6000 trials, null_outlier.out): g 1024 h 20, s 0.5%: clean priced 97.8%; spike q 2% k 3%: 86.1% (text) vs 98.3% (with trim); q 5% k 8%: 69.5% vs 91.4% (critic's figures 87.0/97.5 and 68.8/90.9: same within MC noise). The spike distribution (q, k) is the critic's assumption, not measured; the finding is a real fragility, its size is illustrative.

### MEAS-6
HOLDS. Re-run (verify/j1_sweep.py, 1500 trials, j1_sweep.out): false (b) 0.0% at every margin 1-3 x k 3-6, tau 0 and 1, so the "chosen for (b)'s false rate" claim (§3.6 :735-737) cannot be what selected m 2 / k 5. Power, effect 4 s.d., tau 1: m2/k5 9.8% (design 9.7%), m1/k5 90.9%, m1.5/k5 55.8%. Design's "an effect smaller than a width's own placement spread is not one an artifact would see" is not what the numbers say at tau 1 (effect 4 vs per-launch r s.d. about 1.4).

### MEAS-7
HOLDS. §3.5 (:668-672): the one recorded input the recompute takes as given is the never-ran list in PROVENANCE.md; §3.6 (:741-743) J1's verdict is re-derived only by slot/j1_rule.py (slot harness) from j1_cells.tsv outside the set; S2e's recompute (§9 :1226) lists rows, groups, floor, partial and no J1 re-derivation. A false (b) from a slot bug yields an accepted PARTIAL with no independent check.

VERIFY COMPLETE

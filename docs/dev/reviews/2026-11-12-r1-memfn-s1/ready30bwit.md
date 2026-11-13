# CRITIC ready30bwit: s1

## Findings

### READY-B-1 (AF): the population exists at BT, but 3.0b names no count or floor for it
CONFIRMED, severity maintenance (K35), effort tiny, blast radius sabotage row AF only. Unit 3.0b; TEXT fix.
Repro: copy of `memfn/tests/g2/g2_win_gen.c` (BT) with a counter in the `window-search` block, one gcc line against
`worktrees/crit-s1/build/libpcrec.a`, run at run_g2_win.sh's defaults (seed 20261022, 1500 sites):
`PROBE bwalk 126 stop_offered 24 stop_marker_read 24 stop_alone_read 24 any_stop_read 27 nonbw_stop_read 3`.
So AF's "G2 B-walk sites whose stop alone is offered" is 24 sites at BT and its detector (the `g2w_t<id>_<ref>[`
marker of the stop's ref, read in B-walk's `while (... && !(member))` text, `window.c` :3120-3127) reaches every one:
a plant reporting OWN there would red. But §5 3.0b's table_name population lists only the stop-below-a-TABLE site
and the stated-hook-no-offer site as MUST-INCLUDE members; nothing counts the B-walk-stop-offered sites, so a G2
generator change (`rand_set`'s 2-4-member branch, `rand_span`'s 50% offer) could take AF's population to 0 and AF
would read UNDETECTED/green with no alarm (learnings §3, K35). Fix (one sentence in 3.0b's witnesses): the G2
table_name class prints and floors "B-walk sites whose stop marker is read" (24 at seed 20261022/1500; the kit's
measured-count-no-margin floor ruling, `run_g2_pres.sh` :75-100) beside the two named members. Also: 3 non-B-walk
E-find sites read the stop's marker too, so AF's red is not B-walk-only; harmless, but the row text may say so.

### READY-B-2 (E, E2, and the "agreement green on G2" witness): neither named detector runs a window-family define through an MF_TRACE kit at BT
CONFIRMED for the G2 half, SUSPECTED for the run_finder half. Severity answer (a sabotage row that cannot red),
effort small, blast radius rows E and E2 (E2 names no carrier of its own, it inherits E's) and §5 3.0b's witness
"the two agreement checks green ... on G2". Unit 3.0b; TEXT fix (one sentence naming the traced pass), small build.
Evidence (BT): (1) `memfn/tests/run_g2.sh` :1027-1034 runs the window family with `LIB="$plainlib"` ("It links the
PLAIN library"), and `run_g2_win.sh` :210-216 `kit_objs` compiles memfn/src with no `-DMF_TRACE`. The only G2 process
on the traced kit (`libpcrec_mftrace.a`, built by `mk_mftrace_lib.sh`; `run_g2.sh` :289) is the `--rows` half's
`g2_gen.c`, which states no window facts any more (`g2_gen.c` :66, "The window facts W0-W2 ... this once stated").
So "G2's MF_TRACE kit, `mk_mftrace_lib.sh`" defines zero window-family sites and the agreement never runs in G2.
(2) `run_finder.sh` builds the traced driver `fxt` (:29-36) but hands it only to `finder_check.py` (:74; modes
fd sites, routing, pres routing, query, seam); the purity harness, the one fixture population of window-family
DEFINE sites (11 FUNC/RETURN sites, `arm_fixtures.c` :2151-2224), runs on the PLAIN `fx` (:159, :169, and
`run_purity_reach.sh` builds plain). Whether any `fxt` mode defines an E-find/E-generic/E-func/E-stmt window site is
unshown (its window-stating fixtures are the pre-check `ps_run` sites, a different family); to confirm, list the
`form_id`s `fxt` renders under finder_check. Expected vs observed: E's plant (`reply_of` always E-generic) must be
red; as wired it is red only through `reach_equal.py`'s corpus job (a boxqueue run, not a mech arm). Fix: 3.0b's
harness growth adds `"$WORK/fxt" --purity` (traced purity; the 11 E-func sites then carry E and E2) and/or a traced
pass of the window family (`run_g2_win.sh` against `libpcrec_mftrace.a`, or `kit_objs` with `-DMF_TRACE`), and
E's row text names that pass instead of "G2's MF_TRACE kit".

### READY-B-3 (the `[s1d]` successor probe): not specified enough to build; and `probe.c` is already broken at BT by U2, not only by 3.0b
CONFIRMED (arity), SUSPECTED (runtime effect). Severity maintenance (census numbers), effort small, blast radius the
span_pick census (census0.py sweep/forecast inputs). Unit 3.0b; TEXT fix (name jobs, contents, call), no design move.
(1) WHICH JOBS: the only in-tree jobs that build the probe are `docs/dev/lanes/r33_sim/240-kit-r33-sweep.sh` and
`241-kit-r33-rp.sh` (both `bash "$SIM/build.sh"`, both with `TREE=/home/pcrec/projects/pcrec/worktrees/r33`, a lane
worktree); `docs/design/memfn/span_pick/CLAUDE.md` :41-47 names "job 240" and "job 488" (S2f) as the sweep's
re-makers, and J0's job (440, journal) did too; 440/488 are boxqueue job files, not in the tree. The `[s1d]` block
says only "points the census jobs at it": it names no job, no file the pointing edits, and no `collect.py` home
(collect.py takes `--probe BIN` and stays in r33_sim, so only the binary path moves; say so).
(2) WHAT THE PROBE DOES: unstated. probe.c :91-108 `wr_json` asks `pcrec_mf_wdecide(art, s, &r)` and prints the
decision group. The successor must choose the new call: NONE (decision group only, same JSONL, byte-equal sweep;
recommended for continuity, job 488 compares byte for byte) or DEFINE with the wrapped define's hooks (adds the
frame part, which census0 could read). Name the choice and the JSONL keys.
(3) DRIFT ALREADY AT BT: probe.c :37-39 wraps `pcrec_mf_art_begin(ar, prefix, uint32_t policy, denies, ms, an)`
(SIX args, a678d0a4e's `memfn.h` :1323), but U2 made it FIVE (`memfn.h` :1425 at BT: `a, prefix, denies, ms, an`).
`gcc -Wall -Wextra -c probe.c` at BT compiles clean (rc 0; the `__wrap_`/`__real_` prototypes are the probe's own,
so nothing checks them), and on SysV x86-64 the real call happens to forward `ms`/`an` correctly while the probe's
own `an` (R33RATE's rate source) is read from r9, an unset register: the sweep's per-art rate table is garbage or a
crash. So "left to break at 3.0b" was moot: it broke silently at U2. The successor's spec should say "built on BT's
`mf_art_begin` and the new `mf_wdecide`", with its `build.sh` compiling the prototypes against `memfn.h` (e.g. a
`__typeof__(pcrec_mf_art_begin)` check) so the next seam move fails its build instead of its data.

### READY-B-4: unrevised text that the `[s1d]` block supersedes still reads the old way, in five places
CONFIRMED (grep of SUBJ's plan_frame.md). Severity doc, effort trivial, blast radius a build lane reading the
wrong sentence. Unit 3.0b; TEXT fixes only.
- §5 row (AB), SUBJ :1149: "`stop_test` has no plant of its own among the 18 (§7 Q14)". AF (:1150) is that plant;
  should read "its plant is (AF)".
- §7 Q14, SUBJ :1265: "It makes 3.0b 19 rows (S2994-S3012)". Those ids are taken (§5 header :879-881); mark `[s1d]`
  "expected S3078-S3096".
- §7 Q15 (3), SUBJ :1266 recommendation "(3) leave it to break", and §3's package, SUBJ :760-767 ("LEFT TO BREAK
  ... a re-run of those jobs edits it to call NONE"), plus §R2.2 R23 :52. Only the re-base block (:1043-1045) says the
  ruling rejected it; Q15's row should carry "RULED: (3) rejected, successor probe" so a reader of §7 does not get
  the overruled answer.
- §3 package, SUBJ :760-761: "pcrec's ASK-1..ASK-5" and the pre-K38 caller lines (`arm_fixtures.c` :2271 ...,
  `g2_win_gen.c` :742 ...). At BT they are ASK-1, ASK-3..ASK-6 and :2313/:2320/:2347/:2365, :817/:877/:941, plus
  `run_decide_check.c` :207 (all verified at BT). The re-base block has the right list; §3 should point to it.
- Re-base block :1027-1028: "K38-2 itself took S3040-S3042 and S3060-S3064". At BT, K38-2's range also holds
  S3043-S3048 (k382fix, `tests/mech/sabotages/S3043_*` .. ), S3059 and S3069 (`git grep -hoE 'S30[4-6][0-9]' 35bee4da9
  -- memfn/tests tests src`). Harmless for 3.0b's S3078+ (all inside the reserved S3040-S3069), but the sentence
  is wrong; say "from its reserved S3040-S3069".

### READY-B-5 (ASK-6): its refusal is silent, and 3.0b names no witness for ASK-6's reach
CONFIRMED (code and one compile), severity answer-adjacent (a stamp moves silently), effort tiny, blast radius
every cover-routed pattern's `<PREFIX>_REQ_RUN` `@`. Unit 3.0b; TEXT fix (or a one-line loud check).
`req_run_at` (`emit_dfa.c` :16077) reads `if (!mf_wdecide(...) && w.has_stop)`: a refused ask falls through to
`at = -1` with no error, unlike ASK-1's `window_reply_ask` (:7614-7617, an internal error). 3.0b gives the kit a NEW
refusal on exactly this call: row (S) makes "call 0 (UNSTATED) answers -1". So a 3.0b build that edits ASK-6 to the
new signature but leaves the call UNSTATED (or passes a non-NULL `def` the kit refuses) silently drops the `@`.
The cover row is routed by default (`emit_dfa.c` :10375-10390), so the population is large: `build/pcrec -p rx
--features all --pattern 'foo[0-9]{4}bar'` at BT emits `#define RX_REQ_RUN "626172@0"` and `RX_DFA_SCAN "cover"`;
`abcdef`, `xaaaay`, `a{6}b` route `cover` too. Byte identity (emit_sweep, "as 3.0a") would see the `@0` vanish, so
the check exists, but no 3.0b sentence or sabotage row names it, and F/ASK-3/ASK-4 cover ASK-1 only. Fix: one
sentence ("ASK-6's reach: emit_sweep's byte identity over cover-routed `@` stamps; a refused ASK-6 ask is a byte
move") or make the refusal loud as ASK-1's is (pcrec-side, D80-neutral: no caller-visible change on a green build).

## PROBED-AND-HELD

- Sabotage ids: `git grep -E 'S30(7[8-9]|8[0-9]|9[0-9])|S3[1-9][0-9][0-9]'` over all 234 local branches (denylist
  excluded): S3078-S3096 appear ONLY in SUBJ's plan_frame.md and in lane/memfn-k1108's journal quoting it; free.
  Highest live id S3077 (lane/rpfix, unmerged); S3070-S3073 appear on no branch (s1fix's reservation is ledger-only).
- K38-2a lever: `kit_run_opts_of(d->art, KIT_RUN_WHOLE)` at `window.c` :938 and :1563 (BT) as cited; lever table
  `compose.c` :1424-1427; `arm_fixtures.c` states no `mf_lever` (grep 0), so purity's arts are lever-free as the
  block says. `reach_equal.py --arms` passes arm strings to `--bin`: a `--harness=run-tie-left` arm needs
  `--ref-bin`/`--bin` to be the MF_TRACE `pcrec-harness` (cli/CLAUDE.md :30 (7)); if pointed at plain pcrec every
  compile in that arm fails on both sides, but `reach_equal.py` :240-241 reds "no row chosen at HEAD" per arm, so
  the mistake cannot pass green. The open question is buildable; held.
- AF population: 24 B-walk sites with the stop's marker read (probe above); `B-walk` member-tests the stop through
  `wf_member` (`window.c` :3120-3127). AB's population (other positions' markers read) 53 sites; no-marker 1265.
- G2 class populations at seed 20261022/1500 (my probe's run of the copied generator, failures 0): e-find 1350,
  pair 355 (Y), fn 54 (Z), REPORT rendered 1013 (AA), walk 126, hors 131.
- F: `run_cand_oracle.sh` :84-95 builds `-DPCREC_CAND_TRACE` (as cited :90); `run_fallback_table.sh` :143 trace builds;
  witness rows `offset-set`, `offset-set-bounded` present in cand_oracle_witnesses.tsv; `window_reply_ask` :7608-7620,
  its error text :7615-7617; `ofs_site_define` :7626; `cand_asked_hold` :7047. Held.
- AD: `wf_floor_uses` :3409-3417 reads s/n/lo, result/miss (STMT ASSIGN), on_miss (STMT ON_MISS) at USE; `cl_miss`
  `gate.c` :673-678 holds the `MF_MISS_N` by-address case. Held. U: `compose.c` :250-261 comment as cited. I:
  `fd_opt` `finder.c` :521; `fd-d1` opt `finder.c` :268; `window-search` deny `options.def` :90. Held.
- U2: `g2_art_begin` `g2_win_gen.c` :109-118 states the portable target; `g2_simd_gen.c` has 0 window facts
  (grep `nalt|mf_walt|mf_wspan` 0); `MF_P_PORTABLE_ONLY` retired (fields.def :136). MF_SITE_ABI 27 (`memfn.h` :39).
- Separability: every `mf_wdecide(` caller at BT: `emit_dfa.c` :7614, :16077; `arm_fixtures.c` :2313, :2320, :2347,
  :2365; `g2_win_gen.c` :817, :877, :941; `run_decide_check.c` :207; `r33_sim/probe.c` :94 (via `pcrec_mf_`). No
  other in-tree caller (memfn/src only defines it, :1279). 3.0b's caller list is exact; ASK-1 + ASK-6 + the kit
  callers in one commit is still one separable unit (3.0a landed; K38-3 touches none of the files).
- Compiles: 3 gcc (G2 probe x2, probe.c -c), 4 pcrec. Greps ~40. No make, no suites.

## Verdict

3.0b: READY WITH LISTED TEXT FIXES. Must-fix before the go: READY-B-2 (E/E2's named detectors run no window-family
define under MF_TRACE; name the traced purity pass or a traced window-family pass) and READY-B-3 (name the census
jobs, the successor's call and its `mf_art_begin` arity). Should-fix: READY-B-1 (AF population floor), READY-B-5
(ASK-6 witness), READY-B-4 (five stale sentences).

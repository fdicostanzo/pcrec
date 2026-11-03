# CHECK — span_pick rev 5 -> rev 5.1 (light diff check, crit-memfn-spanpick51, 2026-11-03)

Subject: `828b04c55:docs/design/memfn/span_pick.md` (lane/memfn-spanpick51; not on main). Review
answered: `ff8de05a2:docs/dev/reviews/2026-11-03-r2-memfn-spanpick5.md` RULINGS. Code: main 2636dee99
(src/cli/lib/memfn/tests/scripts identical to the design's cite tree 4f9368e7c: `git diff --stat` empty).
Main has since landed R10 (27cfc44f7 roadmap §0a; 2636dee99 kit ratchet rows R20-R27 with recipes).

Severity: MAJOR = a stage-1 witness that cannot do its job as written; MINOR = a missed reader or a
text gap a lane would hit; NIT = wording.

## Findings

### FIX-NOW landing (per review id)

R1 (1g), R2 (NONE row + named exception), R3/R3a (1f readers, MF_CLASS_V, function-list census,
widened backstop, second plant), R4 (U6 kept), R5 (breaker table b/c/d), R6 (reach equality, golden
test, patterns-file inputs), R7 (purity harness), R8 (translate grouping kept), R9 (today's T-FIND
order), R11 (cites), R12 (row 0), R13 (landing order), R14-R20 (pick text): ALL LAND in the text.
Cites spot-checked at main and hold: finder.c :271/:277/:282/:287/:293/:306/:322 (R1, R2, then D1, D1c,
D1w, PAIR, R7w: R9's order is today's); findings.h :303 `pcrec_find_byte_rate`; findings.c :579
(bytes 0 unless MEASURED), :538 (`underivable-arrives`), :661; presence.c :58-62 `uniform_mass`;
window.c :1592-1597 `d_hors_holds`; emit_dfa.c :11256 (`k.landmark`); compose.c :882 stale comment.
Exceptions to "lands correctly" are the items below (all text-level).

### C1 [MAJOR, CONFIRMED] 1d's purity harness: its plant cannot go red as the harness is worded

The harness is "N window sites, plan calls in order, reversed and repeated, `mf_wreply` compared field
by field"; its plant is "a row that reads `art->nsites` (red under reordering)". `art->nsites` has ONE
writer, `mf_define` (compose.c :1072 `uint32_t h = ++art->nsites;`; grep `nsites` over memfn/src), and
the plan face takes `const mf_art *` (`mf_wdecide`, window.c :1059-1074). A harness that only issues
plan calls sees the same `nsites` on every call in every order, so a row keyed on it answers the same
everywhere: the plant stays GREEN (an unreached plant, K35 shape). Order only reaches the plan face
through DEFINES between plan calls (the real phase-1/phase-2 interleave).
Fix: the harness interleaves `mf_define` of earlier sites between plan calls (each site's reply
compared fresh-art vs after k defines, in order / reversed / repeated), and the plant row must change
an answer with `nsites` (e.g. holds iff `nsites > 0`), with a control run showing the plant moves a
reply on the unharnessed fixture.

### C2 [MINOR, CONFIRMED] 1d's sticky-`err` case has no stated expected outcome

`mf_wdecide` returns -1 whenever `art->err[0]` is set (window.c :1062), i.e. breaker (a) is live
today, and 1d fixes (a) "only if every error path keeps its outcome and diagnostic, else its own unit
change". If the case asserts "same inputs, same plan" it is red at 1d's base unless (a) is fixed in
1d. Fix: state the case's expectation both ways: (a) unfixed -> after a refused define every plan call
refuses (-1), recorded as breaker (a), not a purity failure; (a) fixed -> replies equal.

### C3 [MINOR, CONFIRMED] the census base list is red against its own backstop at 1a's base

Ran the backstop grep (`kit_walk(`, `< best`, `< bm`, `< lo`, `< sm`, `< wl`, `> c)`, `tie_takes`,
`TIE_`, `< inc`) over memfn/src/*.{c,h,def} and mapped each hit to its enclosing function. Hits in NO
listed function:
- `fd_decide` (finder.c :695; hits :702 `kit_walk(&fd_table` and :733 `lo0 < lo`): the fd table's
  actual walk, called under `fd_route`/`fd_find`, not named;
- `decide` (window.c :986; hits :1000 `kit_walk(&wf_atable` and :1010 `kit_walk(&wf_mtable`): the KEY
  and M walks; the list names KEY's and M's row functions but not their walker;
- `kit_walk`'s own definition (compose.c :192) and prototype (kit.h :951);
- file-scope `wf_ties` rows and the `TIE_` enum (window.c :77-101): in no function at all.
Descriptive members also need their function names for a "declared FUNCTION list": compose's
`arms[]` walk = `select_arm` (compose.c :263, hit :290); `fn_rows` BODY/PREFIX = `fn_select` (ofsskip.c
:457, hit :463) and `ofs_fn_serves` (:478, hit :488); Table E's walk = `wf_prepare` (window.c :1796,
hit :1821). Every other hit is in a listed function (a_model_choose, a_mass_choose, m_margin_holds,
run_member, translate :1335, wf_find_decide :1738, rc_row_of, kit_pres_picks :165/:182/:192). Both
plants DO go red (run_member's loop hits `< bm`/`tie_takes`; presence :182 hits `< sm`).
Fix: add `fd_decide`, `decide`, `select_arm`, `fn_select`, `ofs_fn_serves`, `wf_prepare` by name;
declare the exclusions (kit_walk's definition/prototype; file-scope table rows, or map `wf_ties` to
TIE as a data member).

### C4 [MINOR, CONFIRMED] 1g's reader list misses three code readers

The design's own grep (`MF_PROV_|MF_FID_|mf_prov|\.prov\.|->prov\b|prov_stanza`) plus `provchk`:
- memfn/tests/g2/g2_win_gen.c :832 `kind.prov.digest = 1;` (listed :830-831 only; :627, the twin, is
  in its range): a build break once `prov` goes (the digest moves to `mf_akind.digest`);
- tests/memfn/run_finder.sh :67 (`--provchk "$WORK/provchk"`) and finder_check.py :748
  (`--provchk` required) / :758 (`check_prov(..., a.provchk)`): if prov_check.c is reduced to a static
  assertion, the argument and its plumbing go or stay deliberately;
- doc readers under the CLAUDE.md rule: memfn/CLAUDE.md :38 and tests/memfn/CLAUDE.md :82 name
  `prov_check.c`; memfn.h :105-108's MF_SITE_ABI 15 history names `mf_prov`.
Everything else the grep finds is listed (memfn.h :1213-1238; memfn_sites.c :186-191, :247-248,
:273-276, :577-613; memfn_sites.h :170-176; arm_fixtures.c :1267, :1580-1584; finder_check.py :65,
:658-740; prov_check.c; run_finder.sh :37-41; S1092). Not readers, correctly: memfn_sites.c
`analysis_invariant` (:197-216) reads pcrec's OFFER, not the seam; the other `prov`/`fidelity` hits
(rxt layer, findings, S240/S992/S993/S1030/S309) are pcrec's own provenance vocabulary. No docs/spec
names `mf_akind`/`mf_prov`/`PRIOR_*` (grep empty). Kit side: memfn/src reads only `tag`, `present`,
`payload` (presence.c :50-54), so 1g is kit-text-free as claimed.
Fix: add the three lines/files to 1g's row.

### C5 [MINOR, CONFIRMED] the 588 sample is not a `--patterns-file` as named

R6's input "job 588's sample (`docs/dev/lanes/s3_evidence/sample_588.tsv`, the list
`gen_sample_588.py` reads)": that file is `id<TAB>stratum<TAB>pattern` with `#` headers;
`read_patterns_file` (emit_sweep.py :1553-1566) takes WHOLE lines as patterns, so passing it directly
sweeps 24 bogus literal patterns (`smp01\tLIBC/one/norun\t\\|` compiles) and passes trivially.
Its writer is `pick_588.py` (the TSV header says so); gen_sample_588.py only reads it.
Fix: the unit text says "column 3 of sample_588.tsv, `#` lines dropped, into a scratch patterns file
(24 patterns, counted)"; name pick_588.py as the generator.

### C6 [MINOR, CONFIRMED] reach equality for 1a and 1f needs the same row-set statement 1e has

`MFTRACE REACH` lines are keyed `table=… row=…` by name (gate.c :884-900), so names survive the
pres_row shift, but 1a deletes R3a/R3b/R4 and 1f deletes R8/R1/R2: `reach_print` emits one line per
table row (it walks `fd_row_contract(i)`), so their lines vanish whatever their counts (rows.tsv
:119-124 mark all six `pending-site`; whether R8/R1/R2's `asked` is non-zero, as heads of the FIND
walk, finder.c :249-281, is SUSPECTED, not run). "Chosen and asked per row equal at base and HEAD",
read as a diff of the REACH lines, is red on 1a and 1f as worded. Fix: "equal on every surviving row; the deleted rows'
lines are the declared difference" for 1a and 1f (1e already has its declared map).

### C7 [MINOR, SUSPECTED] the "deletes" column vs main's new ratchet recipes (R20-R27, 2636dee99)

Main's R10 rows landed after the cite tree, with literal recipes. Two units claim more than their row
can drop: 1b's "2 tie spellings" against R23 (base 1: `wf_ties` + `tie_over`, minus 1); 1c's "2" (U6
now out) against R24, whose recipe counts translate's `p->rank_pos[j] = (uint16_t)i;` line
(window.c :1341): 1c keeps translate's rank loop (it "reads T_MASS_STRETCH", `rank_pos[0]` asserted),
so the recipe still counts it and R24 drops 2 -> 1 unless the loop's spelling goes. A unit whose
"lowers its row" witness shows less than the design claims will read as a shortfall.
Fix: restate each unit's deletion as its R20-R27 row delta (1a: R26 -3, R27 -1; 1b: R22, R23 -1;
1c: R24 -1, or -2 only if translate's rank is derived from run_member; 1d: R21 -1; 1e: R20 per its
recipe), or have main adjust R24's recipe.

### C8 [NIT] 1g leftovers in the text

- Rate-source row 0 still describes the handed object as "(PRESENT, PRIOR_NONE, no payload)"; after
  1g the seam carries no source: "(PRESENT, no payload)", PRIOR_NONE being pcrec's offer state.
- 1g's re-aimed finder_check L(4) (render loop varying the digest) has no plant now that S1092
  retires: name one (a kit row reading `digest`, red) or record it as unplanted.
- "For main ... BEFORE 1a, roadmap §5's kit ratchet rows ... and §0a" is DONE on main (27cfc44f7,
  2636dee99); and "name the bench pattern list" is still owed by main before 1a's witness can run.

### Landing order (1a, 1f, 1g, 1b, 1c, 1d, 1e): HOLDS

No unit reads a later one: 1c needs 1b's primitive (before it); 1e needs 1d's step list (before it);
1d's `mass_domain` copy deletion uses 1b's primitive (before it); 1f deletes rows/denies/pay rule
with no dependency on 1b-1e and precedes 1e's merged walk as intended; 1g touches no decider and no
kit `.c` (independent). 1f and 1g are separate MF_SITE_ABI bumps; every code reader takes the number
symbolically (`s->abi = MF_SITE_ABI`, memfn_sites.c :413; arm_fixtures.c :228; proof_check.c :156;
proven_check.c :63), so two consecutive bumps are separable. 1a and 1f are both MF_CLASS_V events
(pres_row), again separable. R10, the stated pre-step, is done on main.

## Verdict

READY FOR GO: yes with fixes C1, C2, C3, C4, C5, C6 (text only; C7 and C8 at the lane's or main's
discretion). C1 is the one that matters: as worded, 1d's purity plant cannot go red, so the witness
would pass a real order dependence. The others are a missed reader or a list a lane would trip over
at 1a/1d/1f/1g. No unit depends on a later one; every FIX-NOW of review r2 lands.

## PROBED-AND-HELD

- Code tree: `git diff --stat 4f9368e7c 2636dee99 -- src cli lib memfn tests scripts` is empty, so
  every rev 5.1 cite at 4f9368e7c is checkable at main HEAD.
- 1g's kit-side claim: memfn/src names no `prov`/`MF_PROV_`/`MF_FID_`/`fidelity`/`mf_akind`; the
  only kit read of the object is presence.c :50-54 (`tag`, `present`, `payload`). Byte identity holds
  (MF_SITE_ABI reaches no emitted text, memfn_sites.c :413 is the only code reader, symbolic).
- 1g's `KSRCTRACE object` move "reads pcrec's offer instead, columns unchanged": the offer carries
  `bytes` (findings.c :579) and the fidelity TOKEN; `prov_fidelity_token` only maps the enum back to
  the same token, `-` for none, so printing the offer's token (NULL -> `-`) is byte-identical. The
  out-of-vocabulary refusal is unreachable past the schema's `closed fidelity` row. e1_object_check's
  hand table still pins every column.
- 1g's "no docs/spec names them": grep of docs/spec for `mf_akind|mf_prov|MF_PROV|MF_FID|PRIOR_NONE|
  PRIOR_AUTHORED|analysis object` is empty.
- Sabotages touching 1g's files: only S1092 targets a removed line (retired, listed);
  S1109/S520/S993 target compose.c/emit_dfa.c/findings.c lines 1g does not touch. The
  `docs/design/*/sabotage_anchors*.tsv` S1092/S1025 rows are historical snapshots, not live readers.
- 1f's grep (`fd-r8|fd-ndisp|mf_finder_pay|fd_pay|pay_fill|n_interval|pay-grid`): every code hit is in
  the listed files; tests/oracle/local_adapter.py (`_canon_intervals`) is a false hit, scripts/NOTES.md
  is prose.
- Census plants: both go red under the backstop (run_member's copy hits `< bm` and `tie_takes`;
  presence.c :182's copy hits `< sm`).
- MFTRACE REACH keys rows by name, so 1a's and 1f's MF_CLASS_V (pres_row index) shifts do not by
  themselves break reach equality on surviving rows.
- R9: finder.c's FIND order today is R8, R3a, R3b, R4, R1, R2, D1, D1c, D1w, PAIR, R7w (:249-322);
  after 1a/1f, "D1, D1c, D1w, PAIR, R7w" is exactly the residue.
- R2: `uniform_mass` (presence.c :58-62) is floor(k x 1e6 / 256) as the NONE row states; d_hors_holds
  (window.c :1592-1597) reads `kit_set_mass` against HORS_MIN, so the named exception is accurate.
- R10 is done on main (27cfc44f7, 2636dee99): R20-R27 with recipes, total 44.

## STATE AT HANDOFF

OWED none. Read-only check; no repo edits, no make, no timing. Files: CHECK.md, CHECK.deliver, sp51.md (a copy of the subject) in this scratch dir.

# plants findings

## Findings

Review tree at SUBJECT 65551ae98. `python3 -I scripts/m6read_check_sab_anchors.py`: 1299 rows, 1353 anchor sites, "all anchors resolve". Every SAB_BEFORE checked below occurs exactly once in its file.
"Reach on SUBJECT" = the row's SAB_REACH run here. "Reach on plant" = whether the same probe would ALSO print on the planted build (reasoned, or read off the probe's code).

| row | plant (BEFORE->AFTER) | named detector | would it red? | class | reach on SUBJECT | reach on plant | DOC_FIGURE |
|---|---|---|---|---|---|---|---|
| S3129 | rr_alt_union `if (1 \|\| ...)`: row 1 never applies | facts [facts-ahead] default rule (1) cells | yes. `xy(?:ab\|ac)zw` noaltcls lists 61627a77/fffeffff, want 787961627a77/...; about 13 other `-` mover cells red too | LOUD (listing; no answer moves, as the row says) | prints | would NOT print (the run is 61627a77) | OWED |
| S3130 | width clause `r->head.n != n \|\| l->maxw != n \|\| r->maxw != n` -> `0` | harness spanarms.rxt S-c (both engines) + facts S-c cell | yes. `ab\|abc` (noaltcls), and `ab(?:\|c)` after altcls (empty branch = unit, n=0, common head 0 == n), both claim xyabzw. Proxy: DFA C with the pre-check run edited to "xyabzw" answers nomatch on "xyabczw" (want 0 7). The facts cell lists 787961627a77, want 78796162 | LOUD | prints | would NOT print | OWED |
| S3131 | `{ rr_alt_union, PCREC_WALK_ARM(ALT) }` -> arm 0 | facts `alt` twin cells | yes. The `alt noaltcls xy(?:ab\|ac)zw` twin lists 787961627a77/..., want 61627a77/fffeffff; every rule (1) twin reds | LOUD | prints | would NOT print (restore=alt no longer restores) | OWED |
| S3132 | `u = rn_common_head(...)` -> `u = l->head` | harness rungselect.rxt `((a)\|b){3}c` | yes. The run becomes 61616163. Proxy: narrowing the emitted offset-set k0 table to {a} flips babc, bbbbc, bababc to nomatch (the real plant's literal "aaac" check also drops abbc, aabbc...) | LOUD | prints | would NOT print | OWED |
| S693 | PCREC_ARTIFACT_ABI 107 -> 106 | codegen [DD-14.FB] ABI_EXPECT=107 (run_codegen_tests.sh:3243) | yes | LOUD | no SAB_REACH (pre-existing row; a constant has no reach) | n/a | hand-measured 2026-10-09 (old) |
| S3012 | a_mass_choose in-run `continue` deleted | g2win DECIDE (memfn/tests/run_g2_win.sh) | plausibly yes: in-run stops go back to T_MASS_STRETCH, rs is ignored, so run-tie-left no longer moves them (comment: 86 fails). Not rebuilt | LOUD (reasoned) | prints `REACH-G2W-INRUN n=200` | WOULD ALSO PRINT: it prints the requested count n7=200 (PLANTS-1) | names the FORMER detector g2pres (PLANTS-3) |
| S288 | presence.c P2 `else if (!proof->stop) dom = 0;` dropped | prechecks run_prechecks.sh:1643 `[ab]\x80[0-9]*\x81` REQ_WHY emitted | yes. No run (rsc=0), lead 0x80 != proof byte 0x81, proof->stop=0 (offset-set scan); the plant compares rate[0x81] <= rate[0x80], and both sit at the 2 ppm floor (findings.c:742), so it reads dominated | LOUD | prints | would NOT print (the reach reads REQ_WHY "emitted") | no figure (pre-existing) |
| S3042 | req_run_at returns pcrec_find_run_scan_index(rate, pos, len) (re-spelled for the new signature; the same call shape as emit_dfa.c:11345, so it compiles) | codegen reqcube_check.py C4 lever rows | yes. Under run-tie-left the block scans offset 0 (memchr(subject + pos, 122...)) while the plant stamps @3, so "@ != run block's scan offset" reds. req_run_at's only reader is the stamp (emit_dfa.c:16569) | LOUD | prints `REACH-C4-DIFFERS` | would NOT print (the lever stamp is @3) | old k382 figure |
| S686 | memchr_holds -> `a >= 0`, then swap pair/memchr | harness reqcube.rxt dispatch blocks + memfnarms C5 | yes. every_pos_holds needs a<0, so it misses cubes; the three body contracts are identical (FN_BODY_SERVES), so the gate does not stop memchr. Proxy: `(?i)select` body as a memchr on 'C' (67) gives select, xselectx -> nomatch. reqcube has subjects in both cases at the scan position | LOUD | prints (the pair body text is there by default too) | would NOT print (no pair body) | old r4e0 figure |
| S711 | lazy reach `lo_off` -> `lo_off - 1` | harness vm_lazy_rmin_prefix.rxt new blocks (rxt:265-282) | yes. Proxy (`+2`->`+1`, `+3`->`+2`): 4 subjects flip nomatch->match | LOUD | prints (`+ 6` for `(?:ab){3,}?`) | would NOT print (the plant gives `+ 5`) | STALE: quotes the masked rxt:173 witness (PLANTS-2) |

S3129 equivalence claim (plant == SUBJECT `--harness=restore=alt`): HOLDS. PCREC_WALK_ARM(ALT) is read in exactly one place, the rr_alt_rows loop (req.c:645). `1 ||` makes row 1 return false before it writes `*o`, so the loop ends on row 2 exactly as when the arm skips row 1. Compound parts inherit walk_arms (compound.c:175), which matches a plant that applies everywhere. Empirical check, BASE plain vs SUBJECT pcrec-harness restore=alt with altcls denied, 8 patterns (`xy(?:ab|ac)zw`, `((a)|b){3}c`, `cat|dog`, `q(?:cat|dog)q`, AKIA..., `(?:ab|Ab)(?:cd|Cd)(?:ef|Ef)`, `foo(?:bar|baz)+qux`, `x(a|b)(c|d)y`): gen.c differs only in the abi noise. The facts listings differ only in the why column (`harness:alt` where BASE has rate:/decline:). That token is the one observable way the lever differs from the plant.


### PLANTS-1 S3012's SAB_REACH is a tautology: it prints the REQUESTED in-run site count, not a reached one
CONFIRMED (code read + run). Severity: maintenance (check adequacy). Effort: small. Blast radius: S3012 only (any future row reusing `run_g2_win.sh --reach`).
- memfn/tests/run_g2_win.sh:367-368 greps `in-run N` from the generator log and prints REACH-G2W-INRUN if N>=100.
- memfn/tests/g2/g2_win_gen.c:993 `int n7 = k3n ? atoi(k3n) : 200;` and :1475-1476 prints `in-run %d` with `n7` -- the number of in-run sites ASKED FOR, a constant 200, not the number rendered, not the number whose stop went through a_mass_choose's in-run `continue`.
- Observed on SUBJECT: `REACH-G2W-INRUN n=200`. On the planted build the generator links the planted libpcrec.a but n7 is still 200, so the token prints identically: the reach cannot tell clean from planted and does not even prove the in-run sites rendered (only that the generator built and exited 0).
- The real reach evidence exists but is not the row's probe: INRUN_FLOORS="lever:143 set:54 set_won:13 meet:60" (run_g2_win.sh:125, :439), measured by the driver in the full run.
- Proposal: make --reach print a measured count (e.g. the driver's `inrun set`/`meet` value, or a generator count of rendered in-run sites whose stop lies inside R) and gate it on a floor; or point SAB_REACH at the floor values.

### PLANTS-2 S711's SAB_DOC_FIGURE quotes a harness failure that can no longer happen
CONFIRMED (emitted-C proxy). Severity: doc. Effort: trivial (re-measure or reword). Blast radius: S711 only.
- tests/mech/sabotages/S711_vmlazy_reach_one_byte_short.sh SAB_DOC_FIGURE: "the one harness failure ... vm_lazy_rmin_prefix.rxt:173, z(a){3,}?c? on \"zaac\" (engine vm) answers match 0 4".
- Today `z(a){3,}?c?` stamps `RX_REQ_RUN "7a616161@0"` (BASE and SUBJECT alike), so the pre-check drops "zaac" before the VM runs. Proxy: emitted VM C for that pattern with the reach test `slot_values[4] + 3` edited to `+ 2` (exactly the plant's `lo_off - 1`) answers `nomatch` on "zaac". That old witness is masked.
- Mechund's re-aim moved the detection onto the two new blocks (`(?:a{2,}?|x)[ab]`, `z(?:a{3,}?|x)c?`, rxt:265-282). The same proxy turns those red: "ab", "abx" -> match 0 2; "zaac" -> match 0 4; "zaa" -> match 0 3, where the clean answers are nomatch (4 cells flip). The row's file was not touched in the round: DESC, figure and comment still describe the 2026-10-09 witness and say nothing about the new ones.
- Proposal: add an S711 RE-AIMED line naming the new witnesses, and replace the figure with the new detection cells, or mark it OWED.

### PLANTS-3 Figures OWED or naming a retired detector (S3129-S3132, S3012), plus stale S288 prose
CONFIRMED (read). Severity: doc. Effort: trivial each. Blast radius: 6 row files.
- S3129, S3130, S3131, S3132 SAB_DOC_FIGURE all say "MEASURED by the lane's mechrows cloud run (docs/dev/lanes/r1on_report.md OWED)". None of the four new rule (1) rows has a measured matrix figure at SUBJECT. S3130 and S3132 cite only a scratch-build plant.
- S3012 SAB_DOC_FIGURE still gives the FORMER detector's measurement ("memfn/tests/run_g2_pres.sh --plant S3012 RED"), while SAB_SUITES is now `g2win`. The new figure ("86 fails on the plant, 2026-11-14") is only in a comment. The figure field should carry it.
- S288: the 2026-10-23 comment says "the probe's compile takes the cover row's deny --memfn=no-window-search", but the re-aimed SAB_REACH has no such deny. The new witness `[ab]\x80[0-9]*\x81` is not fixed-width, so it needs none: it compiles to offset-set "0,1*" with REQ_WHY "emitted". SAB_DESC still names the guard `!cs->memchr_form`, which is `!proof->stop` at the anchor.

## PROBED-AND-HELD
- Anchors: m6read_check_sab_anchors.py over 1299 rows, all resolve. SAB_BEFORE is unique for S3129, S3132, S686 BEFORE2 (grep -c = 1).
- SAB_REACH runs on SUBJECT, all print their expect token: S3129, S3130, S3131, S3132, S686, S711, S288, S3042, S3012 (9/9; S693 has no reach).
- Planted-vs-clean discrimination by the reach: 8 of 9 tell the two apart. S3012 does not (PLANTS-1).
- Emitted-C proxies: S3130 (DFA ofsskip literal, 3 subjects), S3132 (k0 table, 6 subjects), S711 (2 new blocks, 10 subjects; old rxt:173 witness, 2 subjects, masked), S686 (pair -> single memchr body, 4 subjects). Each proxy edits exactly the emitted line or table the plant moves.
- S3129 restore=alt equivalence: 8 BASE/SUBJECT pairs, gen.c identical modulo abi.
- Compile count: about 16 pair compiles (32) + about 25 single compiles + 14 gcc links, well inside budget.

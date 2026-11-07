# checks findings — altcode
STATE: done
## Findings

### CHK-1: trie-identity sweep now runs behind the alternation owner; its population is uncounted and the recorded sabotage figures are stale
- status: SUSPECTED for the shrunken sensitivity (confirm with the PLANT-REQUEST below); the population fact is CONFIRMED
- severity: maintenance (a soundness net for rules 1/2 of the trie may have gone partly vacuous)
- effort: S (measure; add a count or a reach floor); blast radius: tests/codegen/run_trie_identity.sh, tests/codegen/CLAUDE.md sabotage table
- where: tests/codegen/run_trie_identity.sh:176-199 (controls), sweep() FLAGS (no deny) ; tests/codegen/CLAUDE.md:95
- argument: only `check_control` passes `-fno-altcls-factor -fno-altcls-merge` (both sides). The 500-pattern identity sweep (FLAGS=() and FLAGS=(-i)) compiles with the owner ACTIVE on both the shipped and the -DPCREC_NO_TRIE builds, so the trie sees the owner's output. Measured on SUBJECT, case-sensitive sweep, patterns regenerated from the script's own awk (seed 20260809): 416 of 500 patterns stamp RX_ALTCLS_MERGES+FACTORED > 0 at default flags. Those are exactly the 3-letter-alphabet shared-prefix/duplicate families the sweep was designed around (families 0,1,2,8). Whatever is left for nfa.c's trie after rules M/P/S is what the identity compares; nobody counts it. The controls prove the trie fires with the owner DENIED, which is a different population from what the sweep runs, so "the owner's effect on tries" (trie engaged on an owner-rewritten tree) is measured nowhere, and the sweep's sensitivity is not asserted. The CLAUDE.md table (disjoint_run_len `return n;` = 64 of 500; rule-1 hoist = 94 of 500) was measured pre-owner; mech S12 only needs ONE red pattern to be DETECTED, so erosion of that count is invisible to the matrix (design §5 lesson 1: the witness fact is not asserted above its floor).
- fix shape: run the sweep a second time with the owner denied on both sides (cheap: same corpus), or print/floor "patterns on which the shipped trie builds a non-trivial trie after the owner" and re-measure the two table rows.

### CHK-2: a DECLARED dump row that never exists is silently accepted (declared-list check goes green on an INVENTED line)
- status: CONFIRMED (called `dumps_declared_delta` as a pure function on synthetic dumps, no sweep run: REF `A1 B2 C3`, HEAD `A1 B9 C3`, declared {B, BOGUS} -> returned [] (no problem); declared map afterwards {B: True, BOGUS: False})
- severity: maintenance (check can attest a delta nobody made)
- effort: S; blast radius: scripts/emit_sweep.py stream 5, and `--dumps-declared-rows` including the new `KEY@F` spelling
- where: scripts/emit_sweep.py dumps_declared_delta (the zip loop sets `declared[key] = True` and nothing reads it afterwards) and sweep_dumps (`res.declared_moves += sum(1 for k in declared if k[0]==flag)` counts invented keys as moves)
- argument: the docstring says "every declared row exists on both sides and differs"; the code only checks rows it happens to meet in the zip, and only flags unmet ones in the SURFACE-IDENTICAL branch. When the surface differs for another reason (the real declared row), a typo or invented key (`--list-axes:altcls-merge@9`, `--list-limits:BOGUS`) passes and inflates the declared-moves figure. DELETED line: red (undeclared row moved). INVENTED line: green. The `@F` form this diff adds widens the exposure. (The `gone`/`new` families are judged both ways correctly: nref/nhead counts.)
- fix shape: after the loop, `problems += [k for k, hit in declared.items() if k[0]==flag and not hit]`.

### CHK-3: island section 11 lost its "ladder straddles the cap" non-vacuity cell; the rung loop's identity arm is conditional and uncounted
- status: SUSPECTED as a latent vacuity (it holds today: measured below)
- severity: maintenance
- effort: S; where: tests/island/run_island_tests.sh capwit loop (~l.505-525), the deleted block "NON-VACUITY: the ladder must actually STRADDLE the cap"
- argument: before, a cell asserted the top rung's chain is in (425000,500000) code bytes. It was deleted and replaced by a cell for the 1,000-word random set. The ladder loop's only assertion on a rung that compiles both ways is now `if stamp==0 then must equal -fno-alt-island`; a rung that keeps its island asserts nothing, and no cell counts how many rungs reached the guard/retry. Measured on SUBJECT (owner denied, --engine=vm): N=260 island 1 (448,561 code B vs chain 355,674); N=300 island 0 + drop note (407,473 vs 407,474); N=340 island 0 + note (459,274 vs 459,275). So 2 of 3 rungs reach the retry and the top chain is still inside the old window; the check is not vacuous today but nothing would say so if the estimator moved and all three rungs kept islands (the ok line would still print "hold ... N=260/300/340"). The shortcut-guard's own behaviour is also no longer separately witnessed: the retry makes every refused rung compile, so a guard that declined everything still passes (the DENSE cell catches only over-eager drops, and only owner-denied).

### CHK-4: "3 of 3 req_pieces declines witnessed" counts the witness table's own labels
- status: CONFIRMED by reading (tests/codegen/run_facts_checks.sh [facts-pieces])
- severity: maintenance (low)
- effort: S
- argument: `npwhy` is the number of distinct `decline:*` strings in the heredoc table, compared with a literal 3. The row-by-row `got == want` comparison does exercise the three real declines (WALL/OVER/ONE exist in facts.h:403-405 and facts_dump.c:117-119), so each is reached today. But a fourth PF_WHY_PIECES_* added to the code leaves the check green: the 3 is not read from the enum/table. Control and controlled share a source (learnings §3 shape). Same table's "independent model" values are pasted from a file under docs/dev/lanes (denied to me), so the independence cannot be checked from the tree; I only checked the byte rows (`a(?:bc|d)e` -> 3:[97][100][101]|4:[97][98][99][101]; `a|é|日|😀` 1..4) by hand: they are right.

### CHK-5: stale prose / figures on re-anchored rows
- status: CONFIRMED by reading
- severity: doc
- argument: S66's header still describes `altcls_walk_alt`, "src/opt/altcls.c's own file header" and its SAB_DOC_FIGURE cites that header's "STAGE 1 soundness paragraph: 'the bitmap is the union'"; grep of src/opt/altcls.c at SUBJECT finds neither (stage 1 was deleted; the plant now lives in altnf.c). S366's SAB_DOC_FIGURE ("wclass:3fail/7pass ... [5a] [5c] [W3]") was measured at the S3 tip and the arm it plants over is now a different body (set reading, not `vm_isl_words(v, a->l...)`). S693's SAB_DESC still says "stays 71". The anchors themselves are fine (see Notes).

### CHK-6: S1894 has no REACH/POP, and the row's shipped-cap witness is outside the matrix
- status: CONFIRMED by reading
- severity: maintenance (low)
- argument: S1894's only detector is run_fallback_table.sh seq-isldrop/note-isl, a 24-word fixture sized for the `trlowsize` low-cap build (measured 29,750 vs 31,815 B in the comment). The fixture's reach (island attempt refused, chain fits) is asserted only by the expected sequence string `drop-islands@size` itself, which is good (a wrong reach changes the string), but there is no SAB_REACH/POP line to catch drift of the estimator; section 11 (shipped caps, 1,000 words) is red under the plant but has no arm, as the row admits. Acceptable but worth a SAB_REACH on the trlowsize build.

### CHK-7: `--facts-encodings byte` makes the facts stream blind to utf8
- status: CONFIRMED by reading (emit_sweep.py FACTS_ENCODINGS)
- severity: maintenance (low)
- argument: by design ("holds a utf8-only change to the byte half"), but the stream then reports movers=0 with zero utf8 rows compared and prints no note that half the population was not read. A declared-new fact with `--facts-encodings byte` is judged on `encs & {byte,utf8}` = {byte} only. Fine if the reviewer remembers; the summary line should name the encodings read.

## PROBED-AND-HELD
- Anchors: `python3 -I scripts/m6read_check_sab_anchors.py` against the review tree: 1117 rows / 1158 anchor sites, ONE stale: S238_size_drop_unstamped.sh (ANCHOR COUNT 6, SAB_COUNT 5) on src/core/compile.c. CONFIRMED regression of this diff: the same script on BASE reports "all anchors resolve" (1102 rows); the drop-islands row in fit_rungs[] added a sixth occurrence of S238 anchor `.cells = { { ESEL_SIZE_CAP_RETRY, ESEL_SIZE_CAP_RETRY }, PFLW_PASS, NULL },`; S238's SAB_COUNT needs 6 or a tighter anchor, else the row plants 5 of 6 sites or refuses to apply. (Reported for the coordinator; not re-derived beyond the script's count.)
- All 14 SAB_REACH commands (S1880-S1893) run against the unplanted SUBJECT binary: each printed exactly its SAB_REACH_EXPECT.
- altnf_rules.rxt: 78 cells (m/n/g incl. \K start and capture slots) re-read through libpcre2-8.so.0 (ctypes): 0 disagree. altnf_lowering.rxt: 33 cells: 0 disagree. counterk.rxt's new `(?:ab|cd|aqr|cst){8}z` block: 10 cells: 0 disagree.
- Answer parity of the lowering merge: for \p{Lu}, \p{Nd}, \p{L}, ., (?i)[\x{100}-\x{17f}k], \p{Greek} under --engine=vm -fno-cls-kit (the box path), plus \p{Lu}/\p{Nd}/\p{L}/./[^a] under vm and auto: every one of the 1,112,062 valid scalar values classified identically to libpcre2 (members accepted in 20k-cp anchored chunks, non-members rejected in chunks): 0 bad chunks, 17 compiles.
- Lookbehind with the seal removed from lower_enc.c: 12 patterns (class/alternation lookbehinds, negative, {2}, \p{Greek}, (?i)) x 258 subjects x 3 engine modes = 9,288 cells vs libpcre2: 0 diff. (The seal is no longer needed by those shapes.)
- run_axes retirement of `-fno-cls-kit`: entry and floor deleted together (no orphan); the `-fno-altcls-merge` entry still reached: the size_term tower (`--engine=vm`) compiles at default and refuses with "pattern too large (VM exceeds 131072 emitted nodes)" under -fno-altcls-merge, on SUBJECT and on BASE alike.
- run_cpset_structure ALLOW_FN: four anf_cls_* allowances; the check has a built-in STALE test for a missing function or a read-less function (its fixture 2b'), so a deleted or renamed function goes red; a NEW u.cls reader elsewhere in altnf.c is policed (function scope).
- dumps `gone`/`new` and facts declared-new: deleted declaration -> count/undeclared-row red; invented declaration -> "rows for none, want one per ..." / "listed 0 times" red. A declared-new fact cannot hide an undeclared one (any other added row breaks the line count).
- run_wclass_census [N1]-[N5]: reads the stamp or box count off a fresh compile; failure to extract gives "?"/empty and goes red, not green. N4 is two-sided (merged 0 / denied 1).

## Notes
Plant classification (from reading; none rebuilt):
- S1880 LOUD (answer vs libpcre2, block 1). S1881 LOUD (block 2; only the lowering caller has unequal widths). S1882 LOUD (x1éy). S1888 LOUD ((?:ab|a|ad) on "ad" 0,2 vs 0,1; I hand-checked a[bd]|a gives 0,2). S1889 LOUD ((?:a|ab)[cb] on abc -> 0,2 vs 0,3). S1890 LOUD (\K start 1,2 lost; capture twin). S1891 LOUD (ad -> 0,2 vs 0,1). S1887 LOUD (ms 3 "abcx", startpos.rxt, generated from libpcre2). S1894 LOUD (refusal where the chain compiles).
- S1883, S1884, S1885, S1892, S1893 SILENT-MOVE by design (count/stamp witnesses; answers cannot move): witnesses are the unplanted value 0/1 vs plant's other value, with reach confirmed above. S1886 SILENT-MOVE (fact witness, values compared to a model; the model file is denied to me).
- Floor concern (design §5 lesson 1): for each count witness the fact is a stamp that differs in the two builds (0 vs 1 or 1 vs 0), not a threshold, so no floor hides it. S1887's unplanted run is intentionally under the floor (run=none) and the plant lifts it over; correct direction.
- Who chose the input: the answer witnesses S1888-S1891 are the design's own S-d/S-k/S-w/S-h patterns with cells read from libpcre2 (verified above); the count witnesses (S1892, S1893, N1-N5, rerun/suffix cells, 'b|ab|c' = 1) take their expected values from the implementation's measured stamps plus the design's hand derivation, so they pin the lane's reading of §3.3, not an independent one. Acceptable for stamps, but a reviewer should know these are not oracle-backed.
- PLANT-REQUEST (for CHK-1): on SUBJECT, apply `return n;` as the first statement of `disjoint_run_len` (src/nfa path named in tests/codegen/CLAUDE.md row 1; mech S12) and, separately, the rule-1 accept-hoist (CLAUDE.md row 2); build the plain compiler and the -DPCREC_NO_TRIE reference as run_trie_identity.sh does and report the `differing` count of the 500 case-sensitive patterns. Expected if the owner has eroded the net: well under 64 / 94; SAME as before would clear CHK-1. Also report how many of the 500 patterns have a non-trivial trie after the owner.

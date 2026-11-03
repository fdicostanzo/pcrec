## Findings

(SUBJECT = efd724b4b. Lines are in the file at SUBJECT.)

HOUSE-1  CONFIRMED  doc/maintenance  effort: trivial  blast: comment only
memfn/include/memfn.h:1240-1242 (the new mf_akind comment) says "the kit's trace names only the digest it was handed". `grep -rn digest memfn/src` returns nothing: no kit trace or row names the digest. The sentence describes a thing that does not exist (header comment no longer matches the code under it; also reads as a promise a kit row will be held to). Drop the clause or say "no kit row reads it".

HOUSE-2  CONFIRMED  maintenance (dead code / names)  effort: small  blast: tests/memfn/{prov_check.c,run_finder.sh}
tests/memfn/prov_check.c:18 `int main(void) { return 0; }` exists only so the file links into `$WORK/provchk` (run_finder.sh:40-41), a binary never run. This is the "main that does nothing" shape. The assertion needs only `gcc -c -Werror ... -o /dev/null` (or a `-fsyntax-only`). The file name prov_check.c, the variable `provchk` (run_finder.sh:41, and the "-Werror as provchk" comment at :44) and the family label "PROVENANCE" now name a check of mf_akind.digest's offset, which is not provenance (D174: names describe behaviour). Rename to e.g. akind_layout_check.c, or at least drop the empty main and link step.

HOUSE-3  CONFIRMED  maintenance (garbage accepted)  effort: trivial  blast: test driver only
tests/memfn/arm_fixtures.c:1600 `strtoull(digest, NULL, 0)` accepts any string: `--fd-an zzz` and `--fd-an 12x` both silently become 0 / 12 and the L check then compares an unintended digest (a typo reads as the reference object). Also base 0 turns "010" into 8. The option loop at :1656-1661 likewise silently skips an unknown flag and a trailing odd arg (pre-existing, but this unit rewrote the loop and the value parse). Parse once in main with an endptr check and usage-fail (rc 2), pass a uint64 down; this also removes the string-through-fd_site_mode hop.

HOUSE-4  CONFIRMED  maintenance (names/labels)  effort: trivial  blast: tests/memfn/finder_check.py
(a) :622 `KIT_READERS_RE` now scans memfn.h's comment-stripped code for retired names; it matches no "kit reader". Name describes the old purpose (D174), e.g. RETIRED_PROV_RE.
(b) :636-640 docstring labels "(4a)/(4b)" survive from the deleted parts (1)-(3); with those gone the numbering has no referent. Use (a)/(b) or none.
(c) :648-649 `named = [f for f in PROV_FIELDS if f in members] + [x for x in members if x == "prov"]` is a second membership pass for one extra word; put "prov" in PROV_FIELDS and use one comprehension.
(d) the section L docstring head (:62-68) and the new test body are mostly narrating what retired ("R-24's stanza parts (1)-(3) retired ... (S1092 with them)"); the guide wants that in NOTES/history, the header should say what L checks now.

HOUSE-5  SUSPECTED  maintenance (history narration in the header)  effort: trivial
memfn/include/memfn.h:184-192 (MF_SITE_ABI 22 entry) and :1231-1235, :1237-1241 carry design-row citations ("span_pick.md unit 1g, D186 add. 2") in three places in 40 lines. The ABI-list entry is the established house register for the number; the other two (object banner and the mf_akind comment) restate it. Keep one. SUSPECTED because the banner's "as amended by" pointer is arguably useful.

HOUSE-6  CONFIRMED  doc/maintenance (stale register)  effort: trivial
tests/findings/e1_object_check.py:14-21 the new "THE PREMISE" paragraph is fine, but the sibling prose at :93-94 and the C-E1-1 blurb (:25-26) still speak of the table as "written where the object is built"; only the added paragraph says the source moved. Low risk; mention for consistency. (Not verified further.)

HOUSE-7  CONFIRMED  maintenance  effort: trivial
src/gen/memfn_sites.c:177-186 and :225-227: two comments both cite "span_pick.md unit 1g" for the same fact (provenance stays pcrec's); the akind_state_map comment explains deleted code (what "stay pcrec's"), the analysis_trace comment explains why the arg changed. A comment should say what the code is, not what it stopped being; the reason lives in the ABI-22 entry. Drop the unit-1g parentheticals.

## PROBED-AND-HELD
- Dead names: grep of the SUBJECT tree (excluding docs/build/lanes) for mf_prov, MF_PROV, MF_FID, prov_stanza, prov_fidelity_token, akind_source_map, S1092: only memfn.h's ABI-history entries, retirement notes, the finder_check strings and the frontend's `prov_fidelity` field (still live, findings.c:580 feeds the offer). 0 stray live uses.
- memfn_sites.c: akind_state_map, akind_source_name, akind_state_name, akind_unmeasured_name are all still used (analysis_build / analysis_trace); no dead table or enum name array left; `strcmp` still used (string.h include still needed). memfn_sites.h: the deleted prototype left no orphan include.
- arm_fixtures.c: an_rates/an_kinds/an_obj still used; `fd_an_make` signature and the usage string match the new option. g2_win_gen.c: two edits are minimal and equivalent (2 sites).
- run_finder.sh: `--provchk` arg removed consistently from the caller and finder_check.py argparse.
- No duplication introduced: the two kit-render loops in finder_check L reuse run(); no copy of an existing helper.

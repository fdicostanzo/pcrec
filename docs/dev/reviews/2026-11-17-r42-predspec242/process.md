# process — round predspec242 (coordinator, opus)
- 17:22 freeze: subject dc2922ec5 (merged ddd83fb1c), main HEAD 110006837 (same text); record COND-FAMILY @110006837 (2546 lines; subject branch saw 2472). Round dir created fresh.
- 17:22-17:24 sanity run of predspec242b engine from R/R/tree copy: 2m07s, IDENTICAL to committed .out.
- 17:25 launched 3 opus critics (simulate, modeclosure, ruling), unnamed, background. All three returned IN the launch turn (7.4 / 14.0 / 17.8 min), files complete with CRITIC COMPLETE, lanecheck .done present. No resends, no nudges. Final replies lost ("ended without SubagentHandback") — files carried everything.
- Findings raised: simulate 5, modeclosure 6, ruling 15 (13 confirmed, 1 suspected = MODECLOSURE-2 confirmed same thing).
- Overlaps: SIMULATE-2 = MODECLOSURE-1 (empty trailing pass; found independently, same engine line pathimpact l.154). RULING-13 (suspected) = MODECLOSURE-2 (confirmed). RULING-4 vs PART P/MODECLOSURE black-box held.
- 17:44 verifier (opus) launched over 10 grouped items; returned in the launch turn at 17:53 (9.0 min), file complete, VERIFY COMPLETE, lanecheck done. Final reply lost again; file carried everything.
- Verdicts: V1 HOLDS, V2 PARTLY (SIMULATE-1's consequence REFUTED by §2.4 "unless the literal has them"), V3-V9 HOLD, V10 HOLDS (660 vs 738 is a metric difference).
- Inline coordinator checks: RULING-1 (heading grep), RULING-8 / unsettable rows (quoted lines), the fix-induced number diff against r40 verify.md (D1), grep for live rev 24.1 carry wording outside §R (none).
- 17:55 draft written. Total round time 33 min (freeze 17:22 -> draft 17:55). No blinding leaks noticed; no critic touched the repo beyond reading copies.
- Per lens: simulate 5 raised (1 PARTLY-refuted, 4 hold; overlaps A1); modeclosure 6 raised (6 hold, 1 doc); ruling 15 raised (all kept; 4 verified by V9, rest text claims checked by reading).

## Process observations
- The coordinator's COMMON paraphrased a document rule ("`00` is not a numeral unless the test is spelled padded", taken from the launcher's brief) instead of quoting §2.4 ("no leading zeros ... unless the literal has them"). The simulate critic followed the brief, not the text, and filed an answer claim the verifier refuted from §2.4. The skill already says "a lens is briefed from the SUBJECT's text"; the COMMON violated it for a rule the launcher stated.
- Two lenses converged on the empty trailing pass by two different controls: the CAPTURE-STATE drill does not name nullable bodies, yet both critics reached them. Worth naming.
- Every agent's final reply was lost ("ended without SubagentHandback"); the pre-created files + CRITIC COMPLETE + lanecheck .done made it irrelevant. The design-mode file discipline is load-bearing.
- A 3-critic opus round + opus verifier finished in 33 min on an 870 KB subject because the brief pointed at §R line ranges and the evening entry range (2364-2546) and the evidence copy was pre-run.
- Fix-induced as an inline coordinator step was cheap (r40 verify.md numbers vs grep of §R) and found one explained mismatch.

## Proposed changes
1. Skill §5 COMMON template: "Where COMMON states a rule of the subject (a domain, a numeral form, a scope), QUOTE the subject's sentence with its line; never restate the launcher's paraphrase (r?? predspec242 B1: a brief's 'unless spelled padded' produced a refuted answer claim; §2.4 says 'unless the literal has them')."
2. Lens table, mode closure CAPTURE-STATE drill: add "a NULLABLE loop body (PCRE runs and keeps a final empty iteration) and the PASS FORMS at two depths, literal vs hole spelling of one pattern (predspec242 A1/A2)".
3. Lens table, simulate (or mode closure): "a callout model of a TEMPORAL rule is drilled with a group set by a lookaround inside a pass (predspec242 A5: a positional construction passed 16 of 16)".

## Framework notes
- The coordinator pattern worked at the small end: 3 critics + verifier, all returning within the launch turn, with the coordinator doing the fix-induced step inline instead of staffing a fourth lens. For a confirming re-check this is the right size: the launcher's "SHORT" profile held (33 min).
- The coordinator's own brief is a new blinding hazard: it carries the launcher's paraphrases into every critic. The launcher's drill text should reach critics as the drill, while any document rule it restates is re-quoted from the subject by the coordinator.

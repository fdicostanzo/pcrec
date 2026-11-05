# CONTRACT critic -- memfn-sp1c (subject 3ecb647c7, base 7b671bc2c, rulings at 42fca94ec)

Lens: CONTRACT (contract + rulings + goals). Written incrementally.

## Findings

### CONTRACT-1 — the pspans refusal narrows Q-G2-13, and the ruling's own record is not amended
- CONFIRMED (reading + probe). Severity: design/doc. Effort: S. Blast radius: docs/design/memfn/integration.md (Q-G2-13 ruling row :2726, §R4.7.2 :2783ff, §14.6 totality), memfn/src/compose.c:585-587.
- Q-G2-13 was RULED (after first being REFUSED) as IN the vocabulary: a run byte outside its mask "never holds", and "refusing it would only turn a correct answer into an error" (§R4.7.2, §14.6 totality). Unit 1c now refuses exactly that shape on `mf_site.pspans`. memfn.h states the carve-out (mf_term.run note :616-622; pspans :799-804), but integration.md's Q-G2-13 row, which is the record readers consult, still says IN with no presence exception. The refusal message also cites "Q-G2-13" as if it supported the refusal, when it was the ruling that rejected refusing.
- The carve-out is defensible: a presence span is a fact pcrec states, pcrec's one run constructor already refuses the shape (src/facts/req.c:276-285 `rn_put`), and D187 wants the set and the cube to agree. But that reason belongs in the ruling row, with D187 and MF_SITE_ABI 23. G2 is not affected: no g2 generator states `pspans` (grep).
- Repro: /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1c/contract/p/edge.c, built against each tree's libpcrec.a. Cases "caseless NON-normal (a/0xDF)" and "mask 0, run byte 'a'": BASE check=OK with ports rc=0 (picks computed); SUBJECT check="a RUN presence span states a run byte outside its mask (...)" with ports rc=-1. Expected per the brief: refused, which holds. The finding is the unamended ruling record.
- Fix: append to the Q-G2-13 row: "on a presence span (pspans), REFUSED since MF_SITE_ABI 23 (D187, span_pick 1c): a stated fact, never a rendered term". Optionally reword the message to "(a rendered term may state one, Q-G2-13; a presence fact may not, D187)".

### CONTRACT-2 — the 1c row's promised `rank_pos[0]` assertion is absent; its replacement comment overclaims
- CONFIRMED that the assertion is missing (reading). SUSPECTED that the comment is false on a kit-admitted site. Severity: maintenance (goals). Effort: S. Blast radius: memfn/src/window.c:1356-1369; span_pick.md 1c row.
- span_pick.md rev 5.2's 1c row promises "translate's run rank reads T_MASS_STRETCH, `rank_pos[0]` asserted against `run_member`". The subject has no check. In its place is a comment (window.c:1361): "rank_pos[0] IS the run member by construction".
- Why the claim is not by construction: translate ranks the plan's sets `w->set[hint_at..]` with `exact` 0. `run_member` (window.c:808-829) picks over R's OWN span sets `r->set`, with `exact` 1 on a verify-NO R. The plan's sets come from `merge` (window.c:249), which INTERSECTS every covering span. So a site whose second span narrows an R position ranks one set and chooses the member on another. Example: R = {a,A},{b} verify YES, plus a one-position span {a} at offset 0. Separately, a plain C-run grouped term (no C-pin) has no member at all.
- No mover: BASE ranked the same plan-derived cube, and 200,000 random ranking cases matched BASE (CONTRACT probe rank_diff.c; see PROBED-AND-HELD). pcrec states R as ONE span (src/gen/emit_dfa.c:1060-1064, :1127-1131), so pcrec cannot reach the divergence today.
- To confirm: a direct kit driver with the two-span example above, reading the translated ranking through the define path (a window plan's rendered run scan).
- Fix: add the promised check where C-pin fired (`rank_pos[0] == member - term offset`, loud), or restate both the comment and the 1c row ("rank_pos[0] is the least-mass position of the plan's term; the member where the term is R's pinned stretch and no other span narrows it").

### CONTRACT-3 — `kit_run_member`'s `after` walk is only correct if T_MASS_STRETCH is a strict order; kit.h does not say so
- CONFIRMED by reading. Severity: maintenance (the TIE table is meant to be re-ruled by stage-3 rows). Effort: S. Blast radius: memfn/src/kit.h:194-209, window.c:767-786, :1363-1367; tests/mech/sabotages/S1095.
- kit.h promises that "asking again from each answer walks the whole order". The `after` filter (window.c:776-778) defines "ranked after" through `kit_tie_takes(T_MASS_STRETCH, after->pos, j)`. `kit_tie_takes` answers 0 for TIE_EXCHANGE/PARKED/RESEED (window.c:115). Under such a row value every equal-mass position is filtered out, a later call finds no candidate and returns pos -1, and translate stores `(uint16_t)-1` = 65535 in `rank_pos[k]` while `rank_n` stays n (window.c:1366-1368). vrun.c:238 then indexes `term.offset + rank_pos[i]`.
- The same split shows in the re-anchored S1095. Its plant swaps the operands in the PICK spelling only (window.c:780), not the `after` filter. On translate's ranking the mutant therefore drops tied positions and writes -1 entries, rather than producing the named "tie to the leftmost". The row still DETECTS, but by a different mechanism than its name says.
- Fix: state the precondition in kit.h ("T_MASS_STRETCH's row must be HIGHER, LOWER or LEFTMOST"), or derive "after" from the same comparison the pick uses, e.g. one `kit_member_before(a, b)` used by both. Assert `r.pos >= 0` in translate.

### CONTRACT-4 — "cube mass" wording left beside the D187 rewrite
- CONFIRMED (grep). Severity: doc. Effort: XS. Blast radius: memfn/include/memfn.h:1600 (public: mf_pres_picks.run_scan, "the rarest position, its cube's mass"), memfn.h:1440 (mf_wreply run_stated, "PICK's cube mass"), memfn/src/window.c:545 (A-mass, "PICK's cube mass").
- The subject rewrote the same phrase at window.c:804 ("PICK's position mass") and in presence.c's P3 header ("its set's mass"), but not at these three sites. Under the new refusal both readings give the same number. The public header should still say "its set's mass" to match D187 and kit.h.

### CONTRACT-5 — span_pick.md's stage-1 ratchet end count is stale after 1c's -2
- CONFIRMED (recipe run). Severity: doc. Effort: XS. Blast radius: docs/design/memfn/span_pick.md §Staging ("stage 1 ends at 4 or 5 (R20 2, R24 1, R25 1, R22 0-1)").
- Running roadmap §5's R24 recipe gives BASE 2 and SUBJECT 0: `^static void run_member(` 1, translate's `rank_pos[j] = (uint16_t)i;` 0, `out->run_scan = (int16_t)scan;` 0, minus 1. R25 is 1 at both (unchanged), and the mass-function count is 1 at both.
- The 1c row allows -2 ("only if translate's rank is derived from run_member"), and the rank IS derived, so the delta is permitted. But the design's stated end of stage 1 still assumes R24 ends at 1, so stage 1 now ends at 3 or 4. The subject carries no design hunk; the ratchet-log line is the manager's to append (roadmap §5).

## PROBED-AND-HELD

- **The refusal fires exactly on the stated classes (edge.c, BASE vs SUBJECT, 8 classes).** It refuses a non-normal caseless run (a/0xDF) and mask 0 with run byte 'a'. It accepts an omitted mask, all-0xFF masks, a normal caseless run (A/0xDF) and mask 0 with run byte 0, all answer-identical to BASE. A one-byte run is refused as before by "at least two positions". A NULL `run` is refused earlier by `pred_kinds` ("RUN term without bytes"), so the new message never misdescribes it. One-member SET spans are unaffected: the check still holds them to exactly one member, which is what `kit_pres_picks` now relies on when it reads `term[0].set` directly.
- **Window sites are not refused.** `kit_presence_check` sees only `pspans`. `term_prove` (compose.c:345) uses `kit_run_set`, the same formula as BASE's inline loop, so a non-normal rendered term is still "never holds", as Q-G2-13 rules. A window-routed site (`wplan`) cannot carry `pspans`, because `wf_check` requires a forward FIND and `pspans` requires ALL_PRESENT.
- **On pcrec's side the refusal is unreachable, and loud if it were reached.** pcrec's one run constructor `rn_put` (src/facts/req.c:276) refuses a non-canonical pair as an internal error, and `whole_mask` is only ever copied from that walk (src/facts/facts.c:222-228). If the kit refused anyway, `req_pres_ask` raises `pcrec_ctx_fail` "internal error: the memfn kit refuses the pre-check's presence spans" (emit_dfa.c:8749-8751): a failed compile, never a crash or a miscompile. The trace shadow (emit_dfa.c:11215, :11323) records `port-refused` and continues. Every `kit_pres_picks` caller sits behind `kit_presence_check`: `mf_pres_ports`, and `fd_pres`/`pres_layout_check` only after `site_check` (compose.c:971, :1025).
- **mf_pres_ports differential, 40,000 random NORMAL-form presence sites (pres_diff.c), both libs: byte-identical output.** The sites cover 0-3 members and a 2-31 position run with masks from {FF, DF, F0, FE, 00} or none, across four rate regimes (NONE, tie-heavy, spread, flat), ASSIGN with `head_max` 0-4, a random start set and a random proof. 36,733 returned rc=0. In the matching non-normal run (40,000 sites) every SUBJECT difference is an rc=-1 refusal.
- **Ranking and member equivalence, 200,000 random cases (rank_diff.c).** BASE's translate insertion sort over the term's cube (verbatim arithmetic) matched SUBJECT's `kit_run_member` walk over the sets, in both `rank_pos` and `rank_ppm`. BASE's `run_member` loop (exact and all) matched `kit_run_member`. Runs were 2-32 positions with one-bit and two-bit cubes, under NONE, 0/1000 tie-heavy and spread rates: 0 mismatches.
- **Compiler byte identity, BASE vs SUBJECT, 19 patterns** (caseless runs, `zzzzzzz~J`, `(?i)x/1234`, hulls, runs longer than 8, VM_ATTEMPT routes). Arms: default, `--engine=vm`, `-fmemfn-simd`, `-e utf8` (the NONE row), `--analysis log` and `--analysis weblog`. 114 identical outputs, 0 differing, rc identical. `--analysis uniform` is no built-in bundle, so those 20 compiles failed identically on both sides. Pattern 15 (`\b`) fails identically ("requires module 'assertions'").
- **MF_TRACE pair, 12 patterns x {default, --engine=vm}.** The whole stderr is identical once BASE's KITMASS line is removed, PRES slot records included (19 of 24 runs have `slot=PRES`). BASE's KITMASS lines sum to nonnormal=0 and mask0=0 over 65,892 cubes, which corroborates D187's zero count.
- **Every reader of MF_SITE_ABI 22/23 was found by grep.** The code reads the symbol only: presence.c:124, window.c:1097/:1290, compose.c, formhash.c, every g2 generator. No numeric pin exists in tests, scripts, stamps or docs/spec. The 22 mentions in tests/memfn (prov_check.c, finder_check.py, arm_fixtures.c, run_finder.sh), S1856, e1_object_check.py and window_contract.md are 1g provenance, not readers. memfn.h's history entry 23 and memfn/include/CLAUDE.md both carry 23. The new message's "MF_SITE_ABI 23" follows the house since-N convention used elsewhere in compose.c. memfn/docs/wake.md :28 "21 -> 22" is the kit session's in-flight note, not a reader.
- **Goals.**
  - `kit_pos` and its cube fields are deleted. `kit_mass` is set-only (`uint8_t *set`, n x 32 bytes).
  - KITMASS is retired in presence.c, trace_format.md and reach_equal.py, and no other reader exists (grep).
  - U2 is met: the P3 scan asks `kit_run_member` (`sc`), `run_member` asks it, and translate's rank is derived from it with T_MASS_STRETCH. U5's run window already reads T_WINDOW since 1b.
  - R24 2 -> 0 (permitted -2) and R25 1 -> 1, per the recipes.
  - The census map moves 51 -> 50 (two parts out, `kit_run_member` in), matching ratchet rule (c), which requires a new member to be listed.
  - mass_check's floor rises 25 -> 40 with the NORMAL cases, including a control.
  - window_site.md's TIE row names `kit_run_member`. memfn/src/CLAUDE.md and tests/memfn/CLAUDE.md are updated.
  - S1095, S1097 and S458 are re-anchored with hand-measured DETECTED figures.
- **Rulings.**
  - D186: a unit change, NO-MOVER. Every probe above is identical.
  - D187: the first step's "zero -> set-only, byte-identical" holds, and the refusal stays inside its "two shapes cannot disagree".
  - D157: the memfn.h text states facts only. The ports' method appears only in a compose.c comment, which is kit-internal.
  - D174: no caller-facing name. `kit_run_member`, `kit_run_set` and `kit_pos_at` are kit-internal (kit.h).
  - D80: nothing a pcrec caller can observe moved (no byte, no pcrec abi, no flag), and docs/spec names no presence span (grep), so no spec hunk is owed.
- **Budget: about 300 pcrec compiles**, plus 4 direct kit drivers (pres_diff, rank_diff, edge; light).
- **Disclosure.** One `grep -rn "rank_pos\[0\]"` over memfn/ printed a single line of memfn/docs/journal.md (a denied file): its 1c entry restating U2/R24. It was read incidentally, it informed no finding, and every finding above was derived from the code and the recipe runs.

CRITIC COMPLETE

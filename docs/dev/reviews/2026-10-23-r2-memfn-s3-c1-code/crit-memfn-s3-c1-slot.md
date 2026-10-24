# crit-memfn-s3-c1 — SLOT TRACING / roll-call / rulings / contract (opus)

Subject ae83da9d4 (BASE c3ea619c3), review tree worktrees/crit-memfn-s3-c1. Read-only; no make.

## Disclosures
- Spawn-time injection: session-root CLAUDE.md and the manager's memory index (context only).
- Read worktrees/memfn/docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md (allowed); auto-injection while reading it pulled in worktrees/memfn's CLAUDE.md, docs/CLAUDE.md, docs/dev/CLAUDE.md, docs/dev/reviews/CLAUDE.md (orientation only).
- guide/addenda/kit.md (an allowed input) cites D176 by name with three one-line rules; I did not open decisions.md D176.
- diff --stat lists docs/dev/lanes/s3_* and s3_evidence/ files; names seen, contents NOT opened.

(findings below, written incrementally)

Probes: ~40 single compiles with the review tree's build/pcrec into the scratch dir (no runs, no timing).

## Q1. SLOT TRACING

| slot | table the design names | code | verdict |
|---|---|---|---|
| A (stop) | §2.1 A rows + MARGIN, kit_tables | window.c `wf_atable`, `wf_mtable` (kit_walk) | matches |
| B (find) | §2.2 = finder FIND slot (`fd_rows`), pick rendered | finder.c `fd_find` (fd_decide over FD_FIND, L_OFF, need REQUIRED, stop facts via `set_facts`, `SF_STRETCH_CUBE`); renderers `wf_brows` (B-fn, B-pair, B-memchr, B-walk) | one table, asked the design's question; renderer list is a plain row list (see F4) |
| C (verify) | §2.3 row list | `c_plan` rows; E-find's C-run via `find_groups` -> runcmp; C-table `offer_at` | matches |
| D (resume) | §2.5 kit_table | `wf_dtable` (D-hors deny `wf-hors`, D-one) | matches, one extra conjunct (F8) |
| E (frame) | §2.6 E-func, E-stmt, E-find, E-generic | `wf_etable` | matches rev 3.3 |

**Does E-find render every Table B row's pick?** Every pick a cover site can REACH, yes: LIBC (D1) and LIBC_BACK (D1c) -> B-memchr, WALK (D1w, R7w) -> B-walk, PAIR -> B-fn or B-pair. Probes: `hello` (D1, memchr 'l' @3), `hello --memfn=no-fd-d1` (D1w, walk), `(?<=Q)ab --features all` (D1c: `if (c < 1) c = 1;` then memchr 'Q' @-1), `(?i)foobar` (PAIR, B-fn: `rx_mf1_ofsskip__body`), `\b(?i:foobar)\b` (PAIR, B-pair), `(?i)a[0-9]b` (R7w, walk).

**Table B rows a cover site can never reach:**
- R8, R3a, R3b, R2: their contracts serve LY_SIMD only, and `fd_find` always asks at `CL_L_OFF` (ruling (a)).
- R4, R1: their kinds are KD_ALL, which excludes REPORT. They also read iterator history or call-length facts that no compile states.
- D1w: reached on a cover site only under `--memfn=no-fd-d1`, because REPORT has no seek role.
- D1c: reached only for a one-member stop below the candidate (a lookbehind item).
- The unbuilt picks (V1, W64, A3, NONE) belong only to those unreachable rows. If one ever became reachable, E-find would decline it silently (F5).

## Findings

### F1. CONFIRMED, speed, MED. PAIR's run-stretch condition narrows Table B: an isolated two-member cube stop gets a byte walk where the default build used memchr
- **Repro:** `ab(?=[Qq])` with `--features all`.
  - Default: `RX_DFA_SCAN "cover"`, and the find step is `while (c + 2 < n && !((s[c+2] == 81 || s[c+2] == 113))) c++`.
  - `--memfn=no-wf-find`: `"offset-set-bounded"` with `memchr(subject + pos + 1, 98, ...)`.
  - This is the C1 class of loss (a byte walk where a memchr existed), reached through a different door.
- **Cause:**
  - A-mass picks the rarest position, `{Q,q}` at offset 2, and that choice is blind to the find method (r1 C8, not claimed fixed).
  - The PAIR row requires `SF_STRETCH_CUBE` (finder.c PAIR row; window.c `stop_stretch_cube`/`in_stretch_at`).
  - A context item is a one-position span, so it is never in a stretch. The stop falls to R7w and B-walk.
- **Why it is a narrowing:** the stretch is a limit of fn-pair's RUN-term spelling (`ofs_fn_scan` reads `plan_hint` in a RUN term). It is not a property of the two-stream find, and B-pair needs no stretch.
  - Guide architecture.md: "Narrowing the table counts as a copy".
  - window_site.md §2.2's PAIR row ("today's scope") carries the narrowing into the design.
- **Contract:** registry.md §6 `wf-find` promises "two `memchr` streams for two bytes one bit apart ... a byte walk otherwise". The repro contradicts it.
- **Unmeasured:** magnitude (no runs allowed), and how many corpus patterns have this shape (a census of more than 50 compiles is heavy).
- **Fix (effort S):** drop `SF_STRETCH_CUBE` from PAIR's facts. B-fn keeps its own translatability test, and B-pair renders any cube stop.
- **Blast radius:** cover artifacts with an isolated cube stop. Needs a G2 caseless-context stream and a bar-sample cell.

### F2. CONFIRMED, speed at the SIMD layer, MED. SIMD reaches only B-fn, so B-pair plans lose the default build's vrun kernels; a re-pinned SIMD count stayed lowered (C2's rule)
- **Repro:** with `-fmemfn-simd`:

  | pattern | default | `--memfn=no-wf-find` |
  |---|---|---|
  | `\b(?i:foobar)\b` | `MEMFN_FORMS "none"` (B-pair, no `__w16`) | `"vrun@w32+w16"` |
  | `(?i)foo[0-9]bar` | `MEMFN_FORMS "none"` (B-pair, no `__w16`) | `"vrun@w32+w16"` |

- **Lowered pins:** scripts/emit_sweep.py `DIFFER_PINS` `("byte","-fmemfn-simd","c-default")` went 20 -> 9 and `("utf8",...)` 15 -> 10, marked "S3 re-pin".
  - The note dates from job 600, before the C1 build, and these pins were not raised afterwards. Only simd_floor_check.py (39 -> 33 -> 46) and simd_guarded `simd-form` were restored.
  - critics.md: "A re-pinned floor or count is a TRADE to judge".
- **Design:** §6 makes a SIMD-on loss a finding for the SIMD thread, not an S3 blocker. So this needs an explicit trade line, not a silent pin.
- **Fix:** see F3 (SIMD rungs over the shared two-stream renderer); otherwise re-measure the pin and record the trade.

### F3. CONFIRMED, maintenance, MED. B-pair is a third copy of the two-stream find
- window.c `wf_b_pair` and ofsskip.c `pair_body` are the same leapfrog: a fresh flag, ha/hb offsets, a re-search when a hit goes stale, the nearer hit. B-memchr likewise restates fn-memchr's and pf_memchr's search.
- F2 follows directly: the SIMD rungs (vrun PREFIX) sit over fn-pair's copy only.
- **General form:** one stream renderer, `find(set, d*, bound) -> text`. Its users would be the ofsskip BODY rows, the pf_* arms and E-find's loop, with vrun's PREFIX rows sitting over it.
- **Unlocks:** SIMD for every PAIR and memchr stop in any frame; deleting B-fn's translatability test; a later path to retiring the legacy E-stmt translation (`legacy_ok`/`translate`) in favour of E-find.
- **Trigger:** F2 judged unacceptable, or the next edit to any of the three copies.

### F4. CONFIRMED, maintenance/observability, LOW-MED. The Table B renderer choice is a decision that is neither traced nor listed
- B-fn versus B-pair decides whether SIMD exists (F2). Yet `MFTRACE WPATH`/`FDROUTE` print `fd=PAIR arm=E-find` either way (`wf_plan_brow` returns the finder row).
- Nothing reads `wf_brows[].row`, `wf_brows[].basis` or `wf_drows[].basis` (grep shows no reader).
- Guide: "observable (listable, with every verdict and the winner printable)".
- **Fix (effort S):** add the renderer to WPATH (e.g. `fd=PAIR/B-pair`).

### F5. SUSPECTED, maintenance, LOW. Two consumers of the FIND slot treat an unrenderable pick differently
- `fd_route` calls a pick with no arm "a kit build error, refused loudly".
- In E-find the same pick sets `fx->holds = 0` silently. A native window site then falls to the floor's byte loop, and a REPORT site is refused.
- Unreachable today (F1 section above).
- **Fix:** a self-check in `mf_finder_rows`: every FD_FIND pick reachable at L_OFF has a `wf_brows` renderer.

### F6. CONFIRMED, speed (a missed win, not a regression), LOW-MED. Table A picks a stop Table B may have no row for, and the whole cover is lost
- **Repro:** `(?<=[Qq])ab --features all`: not cover (`"offset-set-bounded"`).
- **Cause:** A-mass picks `{Q,q}` at offset -1, no B row exists (ruling (d)), and E-find declines.
- A one-member `b` at offset 1 (D1, memchr) would have kept cover.
- **General form:** A's domain is the positions some B row finds, or the priced (stop × method) choice r1 C8 folded.
- **Trigger:** the census count design §2.2 cites. I could not verify that count (it lives under s3_evidence, denied).

### F7. CONFIRMED, doc/contract, LOW. Spec over-promises and names the architecture (C15 PARTLY)
- **Over-promise:** registry.md §6 `wf-find` (F1, F2).
  - It says "two memchr streams for two bytes one bit apart"; F1's repro gets a byte walk.
  - It says "under `-fmemfn-simd`, for a window of such positions, its guarded SIMD kernels too"; `\b(?i:foobar)\b` gets none.
- **Architecture names in caller-facing text** (style.md Naming, D174):
  - registry.md §6 rows: "E-find", "D-hors", "`HORS_MIN`", "the kit refuses a REPORT site".
  - tuning.md §2.43¶3d: "The window family's scalar rows", "(D-hors)".
  - The new option spellings `wf-find`/`wf-hors` are family letters plus a method name. D174 is not retroactive, but these spellings are new.
- **Already fixed:** the `--list-axes` descs are worded by behaviour.

### F8. CONFIRMED, doc, LOW. D-hors's admission rule in the design and spec omits a conjunct the code has
- window.c `d_hors_holds` also requires the window's last offset to be >= 0 (`dx->whi < 0` declines).
- window_site.md §2.5 ("exactly as S3 built it") and registry.md §6 `wf-hors` state only mass >= HORS_MIN and at least 2 positions.
- I could not check S3's original build (7e1caad08 is outside BASE..SUBJECT). Either the doc is stale or the admission changed.

### F9. CONFIRMED, doc, MED. The design states no ranked, checkable goals
- window_site.md rev 3.3 has no Goals section: no three to five goals, no priority order, no non-goals (architecture.md, Frank 2026-10-23).
- The checkable content is §6's bar:
  - answers first;
  - scalar cells against DEF within floors and five caps;
  - SIMD-on "reported".
- The order "answers > scalar layer > SIMD layer (reported only)" is implicit. F1/F2 are exactly where an explicit SIMD-layer goal or non-goal would decide.
- rev 3.3 is marked "DRAFT ... NOT YET ACCEPTED", yet the code and the spec hunks implement it.

### F10. SUSPECTED, maintenance, LOW. D1c is keyed on a label as well as the fact
- D1c's kinds are `CM(DFA_ATTEMPT) | CM(REPORT)` on top of its fact, `SF_CONTEXT_STOP` (the stop lies below the candidate).
- Design §0 says rules are keyed on facts, never labels; §2.2 lists the two kinds itself, so the code agrees with the design text.
- Effect: a native window site of another kind with a one-byte stop below the candidate would have no row. No such site exists today.

### F11. CONFIRMED (design-held), maintenance, LOW. R7w's serve column now carries two renderers' needs
- `CM(REF)` on `table_ref` is pf_walk's need on native routes. E-find's B-walk relies on a window site reading UNSTATED (gate rule 3, pass), which is ruling (c).
- R7w's K96 comment ("serves exactly what its arm does") is no longer true for E-find.
- **General form:** split the decision row from the renderer's applicability (the renderer rows would get contracts, which ties in with F4).

### F12. CONFIRMED, test, LOW. PAIR's pcrec-side reach floor is a placeholder
- row_floors.tsv has `fd PAIR PLACEHOLDER PLACEHOLDER`. Only G2's `EFIND_FLOORS pair:125 fn:48` counts the population (K35).

## Q2. Roll-call of round 1's C1-C17

| id | claimed | status | cite |
|---|---|---|---|
| C1 | yes | FIXED as stated: the private LIBC/WALK enum is gone, every reachable pick is rendered, PAIR is built. A residual narrowing is new finding F1 | finder.c `fd_find`, PAIR row; window.c `wf_brows`; probes in Q1 |
| C2 | yes | PARTLY: simd_floor_check is 46/46 and simd_guarded `simd-form` is back to 6. emit_sweep `DIFFER_PINS` `-fmemfn-simd` c-default stays at 20->9 (byte) and 15->10 (utf8), and B-pair plans lose vrun (F2) | scripts/emit_sweep.py; d190e3a70 does not touch it |
| C3 | yes | FIXED: Table B is asked with (set, d*, stretch, kind/body/policy/options), need REQUIRED; KD_ALL is back on R8..R2 and the PRES rows; D1c fires (`(?<=Q)ab`). Layer fixed at OFF and table_ref UNSTATED are now RULED, see (a) and (c) | finder.c ct_* and `fd_find`; gate.c `cl_table_ref` |
| C4 | (doc) | DONE as a draft: rev 3.3 records E-find, but is not accepted (F9) | window_site.md header, §2.6 |
| C5 | no | NOT (PLAN): `e_legacy_holds`/`e_generic_holds` still key on `site_kind == REPORT`, and so does `select_arm`'s early return | window.c, compose.c `select_arm` |
| C6 | no | NOT (PLAN): D-hors is still reachable only inside E-find | window.c `wf_find_decide` |
| C7 | yes | FIXED: `wf_dtable` is a kit_table with contracts, the `wf-hors` deny, a traced walk and a path suffix. `basis` is still read by nothing (F4) | window.c Table D |
| C8 | no (FOLD) | NOT: the stop is still priced by mass only; F1 and F6 are its consequences | window.c `a_mass_choose` |
| C9 | yes | FIXED for the frame (`wf_frame`, `wf_open`/`wf_cand`/`wf_close`, `wf_test_to` shared). New duplication: B-pair against fn-pair (F3) | window.c |
| C10 | (gate) | the design side is DONE: rev 3.3 §6 puts the sample in the bar; G2 gained 300 caseless and 400 dense sites. Widening G2 to ~13-wide windows and high bytes is not verified | run_g2_win.sh |
| C11 | yes | NOT VERIFIED: the change is in s3_evidence/census.py, which is on the denylist | commit d190e3a70 subject |
| C12 | no | NOTED (ideas.md) | — |
| C13 | yes | FIXED: plants S1425 (shift value), S1426 (C-run mask), S1427 (walk set), S1428 (B-pair stream), S1429 (fn-pair stream); a PAIR decision drop is caught by `EFIND_FLOORS pair:`/`fn:` | memfn/tests/run_g2_win.sh |
| C14 | yes | FIXED: `e_find_holds` reads `fx->holds`, computed once in `wf_find_decide`, with no const cast | window.c |
| C15 | yes | PARTLY: the `--list-axes` descs are worded by behaviour; the spec rows and the option names are not (F7) | options.def, registry.md §6 |
| C16 | no | NOT (FILE): `--harness=kit-proof` is still parsed and documented as "inert" | cli/main.c |
| C17 | where touched | MOSTLY: `WF_FIND_ID` (but "wf-find" is still spelled separately in options.def), `WF_WHY_MAX`, `libc` now off on Horspool text, `fd_find_form` gone. `find_groups` still runs on the query path (build=0, count only) | window.c |

## Q3. Rulings

- **(a) FIND asked at the OFF variant, SIMD through PREFIX rows. AGREES** with the design (§2.2, bullet 3) and with `fd_route` (finder §1.5 rule 1). Native sites get SIMD the same way, so this is not a narrowing against them. The SIMD hole is in the renderer list, not in this ruling: only B-fn carries PREFIX rows (F2, F3). D147 ("each layer the best it can be") is served for B-fn plans only.
- **(b) KD_ALL's REPORT widening reverted on R8, R3a, R3b, R4, R1, R2 and P0-P9; kept (KD_STOP) on D1, D1w, PAIR, R7w; D1c lists REPORT explicitly. AGREES** with §2.2 bullet 4. The D1c kind label sits uneasily with §0 (F10).
- **(c) A window site's table_ref reads UNSTATED. AGREES** with §2.2. Under gate rule 3 it passes R7w, which does not USE the field. That is sound because B-walk serves both C-table and C-own. Cost: R7w's contract now means two different things (F11).
- **(d) A stop of 2+ members below the candidate has no B row, so cover declines. AGREES** with §2.2 (verified: `(?<=[Qq])[a-z]{3}`, `(?<=[Qq])ab` are not cover). But A does not know about it, so a cover that another stop could serve is lost (F6). The census count could not be verified.
- **(e) E-find as its own Table E row. AGREES** with rev 3.3 §2.6. Against the guide's "general form": E-find is the general find-then-verify, and E-stmt/E-func plus `translate()` are the legacy special case, kept for zero movers. The unlock is in F3 (implement-then-replace). Its renderers restating the pair/memchr streams is a parallel mechanism (F3).
- **(f) D-hors admission unchanged. AGREES** in substance: mass >= HORS_MIN (145822 = floor(sqrt(74760 × 284434))) and a window of at least 2 positions. The extra conjunct `whi >= 0` is undocumented (F8). Probes: it fires on `[0-9a-f]{8}` and `[a-z]{3}`, but not on four spaces, `ee`, ` the ` or `\d{4}`.

## Q4. Contract and goals

- **The spec hunks match the code** on the following:
  - abi 84;
  - `"cover"` as a `_DFA_SCAN` value and its `attempt-start`;
  - §6.3.4¶8/¶9 (the anchored machine's table and folds);
  - the memfn floor 12 -> 14 (the two new rows exist, `--list-axes` shows them);
  - tuning.md §2.43¶3d's deny effects.
- **Over-promises:** the registry `wf-find` row's find-form and SIMD sentences (F7, from F1/F2).
- **Names by behaviour:** the `--list-axes` text passes; the spec rows do not (F7).
- **Goals:** none are stated in ranked form (F9). The code serves the implicit order: answers (G2, plants) > scalar against DEF (PAIR restored) > SIMD reported. That last tier is where F2 sits.

## PROBED-AND-HELD
- **Renderers:** every pick reachable at L_OFF on a REPORT site has one; 6 probes, Q1.
- **fn-pair and fn-memchr share one `serves` (FN_BODY_SERVES).** So when `b_fn_holds` holds, the BODY walk cannot fall to fn-memchr on a cube scan position, which would be an answer hazard. Checked by reading.
- **Below-candidate stops:**
  - The D1c raise (`if (c < 1) c = 1`) is sound: A-mass takes stops from core positions only, so a stop below the candidate is always core.
  - B-memchr renders LIBC_BACK as a forward memchr at c + d, which is the right find for a forward window search.
- **D-hors shift table:** conservative at untested offsets (`hors_table` breaks out), and probe positions beyond the window do not affect soundness.
- **Native routes cannot reach PAIR:** `find_facts` never sets `SF_STRETCH_CUBE`, and `fd_route` maps FF_PAIR to no arm.
- **Window fields in the finder rows:** `fd_find`'s `gate_in` has `wf = NULL`, so the finder rows read no window fact and no window field declines them.
- **Denies:** `--memfn=no-wf-hors` on `[0-9a-f]{8}` falls back to B-walk, and `--memfn=no-wf-find` on cover patterns gives `"unanchored"` with today's prefilters (7 patterns).
- **SIMD on the B-fn path:** `(?i)foobar -fmemfn-simd` keeps `vrun@w32+w16` on the default path (C2's named witness holds).
- **Population:** about 40 compiles in total.

# pdrev2 — part_d.md rev 2 (the kit's design for R-38 Part D, review r1 memfn-partd as ruled)

Lane pdrev2 (opus), 2026-11-12. Branch `lane/memfn-pdesign` (worktree `worktrees/pdesign`), on top of
main `522faf600`. Deliverable: `docs/design/memfn/part_d.md` rev 2 (commit `92976462f`) plus its
pointer line in `docs/design/memfn/CLAUDE.md`. DESIGN ONLY: no code under `memfn/src` or `src/`.
Code cites are by function name, re-read at `522faf600` (the same as `35bee4da9` under `memfn/` and
`src/gen/`).

## STATE AT HANDOFF

- STATE: done. Rev 2 and the CLAUDE.md line are committed; this report is committed.
- OWED: none. No suite and no queue job. Measured in this lane (single compiles only):
  (1) a PROBE build: a scratch copy of the tree under `/var/tmp/pcrec-pcrec/scratch/memfn/pdrev2/probe`
  with `run_shaped` patched to "verify NO and two or more positions: R; verify YES: never", built with
  `nice make -j8`, against this worktree's own `build/pcrec`, on 17 patterns;
  (2) today's half of the F4 witness (default against `-fno-req-run`);
  (3) python3 `re` answers for the five witnesses.
- No rulings file named in the brief. The review's Rulings section was applied as its last entry
  reads ("F11 RULED ... option (b) ... Main also agreed F26 and F9").

## Summary

Rev 2 applies every FIX-NOW and DOC finding, plus the three decisions:
- **F26: the direct translation is IN, in D2.** The derived run part's terms are written straight
  from the reply. The terms are one RUN term over the findable stretch that holds the scan
  (`run_len` 1 allowed), and SET terms for every other extent position. The family's second decision
  is gone. Four pieces are not built, and that is the benefit:
  - the internal R flag;
  - `a_mass_choose`'s widened exclusion;
  - the tiling check (and today's "find is not at the scan" check);
  - the restricted pinned join, together with the latent-UB route.
- **F9: still needed under F26, so it is SCOPED to the derived part.** The direct translation emits
  tableless wide SET terms, so ofsskip must still admit them. The scope is one argument to
  `ofs_fn_applies`. It is named a special case to retire (§6 C7, with its trigger). `FORM_FLOORS`
  do not move under the scope.
- **F11: R BY ROLE.** Any verify-NO span of two or more positions is R. pcrec decides how far R
  reaches. It is one `MF_SITE_ABI` event. `xy/users\d+` keeps `run-pinned`.

**A finding against the ruling's wording (MEASURED).** Read literally, "the kit never infers R from
shape" would make verify-YES spans never pinned. That reading MOVES today's cover bytes. The probe
moved 7 of 17 cover artifacts, among them `abc`, `foobar` and `(?i)select`. On `abc`, the word
compare became a byte compare and `RX_RUN_WORDS` went 1 -> 0. So rev 2 applies R by role to
verify-NO spans, as the plan note writes it ("R (the run's pinned verify-NO span)"). A verify-YES span
keeps today's whole-compare rule, now named as the kit's own spelling choice. §7 Q1 asks the kit
manager and main to confirm this reading.

The decline's answer-level and G1 holes (F1-F4, F7) each get a design change and a witness that
fails without it (part_d §2.4's table):
- F1: the twin's landmark becomes the head byte, and pcrec reads `pres[run].verify`.
- F2: the head rule reads "tested run".
- F3: the decline row comes after P2.
- F4: on a REQUIRED route there is no decline. P0 verifies the whole run with no scan, through
  ofsskip's `fn-walk` body (K66). Today's half of the witness is MEASURED: default `nomatch` against
  `steps` under `-fno-req-run`.
- F7: a one-position stretch renders as one RUN term of `run_len` 1.

## Per-finding changes

| finding | disposition | where in part_d rev 2 | change |
|---|---|---|---|
| F1 | FIX-NOW | §2.4 item 5; §4 item 1; §9 item 2; witness table | the twin's byte branch where `!rs \|\| !ext->ver_len`; on a decline the landmark is the head member; pcrec's "run shipped" readers listed (incl. `PF_REQ_LANDMARK_MAXOFF`, `req_handoff_k`, `req_handoff_entry_applies`, `req_handoff_applies`, `req_landmark_hit_ppm`, the head-vs-`req_byte` check); witness `(a\|bc)[a-z]{8}.q` / `bcabcdefgh-q` -> (0,12) |
| F2 | FIX-NOW | §2.4 item 4; witness table | the run span is decided first; P3's member rule and the head rule read `trun`; `pres_layout_check`'s `need` reads `trun` and gains a "no HEAD" refusal so G2 sees it; witness `[a-z]{8}.q` / `zz abcdefgh-q` -> (3,13) |
| F3 | FIX-NOW | §2.4 item 2; witness table | the decline row sits after P0 and P2 (`fd_rows[]`: P0, P2, decline, P3, P4, P9); witness `x.(?:cat\|dog)` / `x-dog` -> (0,5), dominated |
| F4 | FIX-NOW (design) | §2.4 item 3; §2.1 item 4 and ofsskip `fn-walk`; witness table | no decline on REQUIRED; P0's `no_scan` column gives the scan-less whole run; the choice is reasoned against "pcrec prefers a findable run" (D157 / F11); witness `(x?)([a-z]+)+eeeeeeee~#~#~#~#.[0-7]{32}\1`, today default `nomatch`, `-fno-req-run` `steps` (MEASURED) |
| F5 | FIX-NOW | §2.4 item 4; §9 item 5 | `set_leads` -1 and `dominated` led by the set's pick where the run has no scan; `rr.scan` guarded; pcrec readers named |
| F6 | FIX-NOW | §5.1 D2 | the deny clips every mode's stretch to the findable stretch (identity today); `emit_sweep` covers the deny arm |
| F7 | FIX-NOW | §2.1 item 2; witness table; §5.1 D2 check | a RUN term of `run_len` 1 for a lone findable scan; a deny-arm refusal floor of 0; witnesses `\d{3}-\d{4}`, `\d[aA]\d` |
| F8 | FIX-NOW | §2.1 item 2; §3.1 `translate` row | the derived part no longer goes through `translate`'s `j - i >= 2` grouping; `translate` is unchanged for family sites |
| F9 | FIX-NOW (decided) | §2.1 "two admissions, SCOPED"; §6 C7; §5.1 D0 | still needed under F26, so scoped to the derived part through one argument; retirement trigger; `FORM_FLOORS` consequence named; Q3's population counted at D0 |
| F10 | FIX-NOW (dissolved by F26) | §2.1 "What F26 deletes" | no carrier is needed because the derived part never enters the family; `merge` stays the one writer of `m->run`; the F-8 exception question is superseded by F11 |
| F11 | FIX-NOW (joint ruling) | §2.2; §4; §9 item 1; §7 Q1 | R by role; one `MF_SITE_ABI` event; memfn.h text for `run_stated`/`mf_wspan.verify`; the verify-YES reading MEASURED and raised as Q1 |
| F12 | FIX-NOW | §2.4 item 1; §4 | "findable" stays the kit's private rule; rev 1's (b) and item 3 are dropped |
| F13 | DOC | §4 `MF_CLASS_V` reasons; §2.2 "The reply" | the index-shift reason with its readers (`decider_census.tsv`, `arm_fixtures --finder-rows`, S1122); (a) restated as WHERE the state occurs; the `run_stated` cite corrected (only `req_run_at` reads it) |
| F14 | FIX-NOW | §5.1 D1 check; "Order" | D1's check is at reply level; the refusal-0 floor moves to D2; "D1 alone" is qualified |
| F15 | FIX-NOW | §2.4 item 2; §5.1 D1 content | the row obligations listed; the fact comes through a kit-internal out-parameter of `kit_pres_picks` (no second `kit_run_decide`) |
| F16 | FIX-NOW | §5.1 D0 | `g2_pres.h` and `g2_pres_run.c` readers added |
| F17 | FIX-NOW | §5.2 "The breaker and the background" | a per-position breaker; "no background" sites counted |
| F18 | FIX-NOW | §5.1 D0; §5.2 | wide strata on their own rng (today's 354 byte-identical); refusals counted with the K-1 message only; the base count becomes D2's must-be-0 population |
| F19 | FIX-NOW | §5.1 D3 | population widened to the derived parts' verified positions; a floor from a non-kit source; D3 resized to M |
| F20 | FIX-NOW | §5.1 D3 | `settest` classes bounded: `cn` = 3-7 compares, above that `cn+` UNMEASURED |
| F21 | FIX-NOW | §0 G1; §5.1 D1 check and plant p3; §5.2 | G2 computes "no findable position" itself; per-site equality |
| F22 | DOC | §5.1 D0/D2; §5.2 window family | the contradiction is gone under R by role; `g_run_shaped` and `two_runs`' fix rule move at D2 |
| F23 | FIX-NOW | §2.1 precheck readers; §3 grep | `run_comment` and the row contract's `FLD_table_ref`/`FLD_table_name` comments; the grep is widened |
| F24 | FIX-NOW | §5.1 D1 plant p1; §5.2 floors | p6 is deleted with its piece; the floor ("a wide position lighter than every findable one") now makes p1 fail |
| F25 | FIX-NOW | §4 "Caller-observable consequences"; §9 item 7 | `match_api.md` §6.3.7¶7 rows 1 and 3, §6.3.7¶8, `tuning.md` §2.29 and §2.30, the `--list-axes` floor |
| F26 | FIX-NOW (decided) | §2.1 | the direct translation, and what it deletes |

## R by role

- **Rule (as ruled, applied to verify-NO spans).** An alternative's verify-NO span of two or more
  positions is R, whatever its sets. It is unique per alternative (`wf_check`). `run_member` keeps
  EXACT_AROUND on it: its member is the least-mass exact position and its pinned stretch is the exact
  run around that member. A wide R position never enters the pinned compare.
- **No byte moves today.** pcrec makes 8 `pcrec_memfn_wspan` calls. The only multi-position verify-NO
  span among them is R (in `pf_window_of`), and today it is shape-only. G2's window family does move,
  by design: its verify-NO multi spans with wide sets become R, and D0 counts them.
- **Stage-3 benefit.** `xy/users\d+` keeps `run-pinned` and its `@`. Under rev 1 it lost both.
- **Verify-YES spans (§7 Q1).** They keep today's whole-compare rule as the kit's spelling choice.
  The literal-ruling reading MOVES cover bytes: the probe moved 7 of 17, and 2 more patterns refused
  only because the derived statement lost R, which F26 removes. Leaning: confirm.
- **The reply.** `run_stated` and `pinned` keep their fields and their one pcrec reader
  (`req_run_at`). The memfn.h text changes. One `MF_SITE_ABI` meaning event, in S2's landing.

## The direct translation

- **`run_part_terms`** (the name is the builder's) replaces `derive_run_part` + `wf_prepare` for the
  derived part. It writes:
  - the scan stretch `[a, b)` as one RUN term (`run_len` >= 1);
  - every other extent position as its own SET term (`table_ref` 0);
  - `plan_hint` = the RUN term, `plan_pos` = scan - a;
  - the RQ-2 ranking, from the one ranking function it now shares with `translate`.
  A scan-less part (P0's REQUIRED whole run) has a term for every position and no scan.
- **Identity today.** Every extent is all findable, so the output is one RUN term at `ver_lo`,
  exactly what today's check enforces. Today's G2 presence pass refuses none (354 rendered, 0
  failures).
- **Deleted.** The internal R flag, `a_mass_choose`'s widening, the tiling check, today's scan
  check, and the restricted pinned join (and with it the latent-UB route). `run_bytes` keeps a loud
  refusal as the one `(T, K)` builder.
- **ofsskip / precheck.** Two scoped admissions, both only for the derived part:
  - tableless SET terms, tested by `kit_set_test`;
  - the scan-less `fn-walk` BODY row, which has no deny (K66, D158).
  precheck's `run_part`, `run_comment` and its row-contract comments are generalised.
- **Sabotage fates.**
  - S3006: re-targeted to the shared ranking function.
  - S3012: its detector (the derived part's refusal) goes away with the family route. It is RE-AIMED
    to a verify-YES pinned-span witness, or retired, as REACH decides.
  - Every row in window.c, ofsskip.c and precheck.c gets a REACH re-run.

## Build units

| unit | size | readiness after rev 2 | findings that moved it |
|---|---|---|---|
| D0 G2 first | M | READY | F16, F17, F18, F21, F22, F9 (Q3 count) |
| D1 the decision | M | READY pending the narrow re-check | F1, F2, F3, F4, F5, F12, F13, F14, F15, F24, F25 |
| D2 the rendering (direct translation, scoped ofsskip, R by role, deny) | L | READY pending the narrow re-check | F6, F7, F8, F9, F10, F11, F23, F26 |
| D3 the census floor | M (was S) | READY | F19, F20 |

- **Order.** D0 -> D1 -> D2 -> D3. D1 may land alone only with its reply-level check green and the
  K-1 refusal count at or below the base. Any stage-3 population needs D1 and D2 together.
- **The D27 author (ruled YES, at build).** A cell from `scripts/mk_d27_cell.sh`, denied `src/`,
  `tests/`, `memfn/src/` and `memfn/tests/`, writes witnesses from the contract text only (part_d §4,
  memfn.h's new text, `match_api.md` §6.3.7). They cover handoff (F1), member head (F2), dominated
  (F3), REQUIRED (F4), the deny-arm one-position stretch (F7), and a wide R keeping `run-pinned`.
- **For main.** The facts pcrec's stage 3 must state or read are part_d §9, seven items: R by role;
  the decline and the "run shipped" readers; nothing to render; the scan-less REQUIRED run;
  `mf_pres_picks` on a run with no scan; the version events; the spec hunks.

## Open questions

1. **Does the F11 ruling reach verify-YES spans?** For the kit manager and main. Leaning: no, as the
   plan note's parenthesis reads. The other reading moves today's cover bytes (MEASURED).
2. **The deny's name** (D174). Leaning `run-verify-wide`. The kit manager's call.
3. **F4's choice** (P0 scan-less, rather than pcrec preferring a findable run). The kit manager to
   confirm. Leaning as chosen.
- Rev 1's Q3 and Q5 are ANSWERED (F9, F26). Rev 1's Q4 moved to part_d §9.

## Charter-vs-committed checklist

| brief item | where |
|---|---|
| BOILERPLATE.md and memfn/CLAUDE.md first; first command `rev-parse --show-toplevel` | done; it printed `/home/pcrec/projects/pcrec/worktrees/pdesign` |
| read the review's Rulings section first, including the joint F11 ruling | done; also the [RUN-POS-SET] plan note of 522faf600 |
| 1. every FIX-NOW (F1-F12, F14-F21, F23-F26) and DOC (F13, F22), each marked `[r1pd Fn]` | part_d rev 2; every F1..F26 carries at least one mark (grep); per-finding table above |
| 2. F26 IN in D2, the deleted pieces listed as the benefit | part_d §2.1 "What F26 deletes" |
| 2. F9 scoped or unneeded, say which | part_d §2.1: NEEDED, scoped; §6 C7 retirement |
| 2. F11 R by role; pcrec decides reach; the kit never infers from shape; an `MF_SITE_ABI` event in S2's landing; §4's numbers as stated choices | part_d §2.2, §4, §9 item 1; the verify-YES reading is raised as §7 Q1 with a measurement |
| 3. F1-F4 and F7: a concrete design change and a witness that fails without it | part_d §2.4 witness table |
| 4. D0-D3 with per-unit readiness, the D27 author, the pcrec-side facts for main | part_d §5.1 "Readiness after rev 2", "The D27 author", §9 |
| cites verified at 35bee4da9 or later by grep; spec/plan by section or [TAG]; "rev 2" line at top | code by function name, re-read at 522faf600; spec by §; the rev 2 line is the file's second paragraph |
| report with the deliver file's sections, a per-finding table and an `OWED:` line | this file |
| no code, no suites, no queue jobs, no monread; scope (worktree + scratch only) | held: one `nice make -j8` in the worktree, one in scratch (the probe copy), 17 x 2 single compiles plus the F4 witness |

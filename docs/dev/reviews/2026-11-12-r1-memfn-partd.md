# Review 2026-11-12 r? — memfn Part D design (critic round partd, design mode, the round before a BUILD GO)

**DRAFT by the coordinator (crit-partd). Dispositions are PROPOSED; the manager (and, for the kit's
own calls, the kit manager) rules them.** Critic texts and the verifier's file: `review/` beside this
file (rd0d3.md, rd1.md, rd2.md, sound.md, seam.md, verify.md, COMMON.md).

## Subject and freeze

- Subject: `docs/design/memfn/part_d.md` rev 1 at 5999409e3 (branch lane/memfn-pdesign, tip
  36b080512), the kit's design answer to `memfn/docs/requests.md` "R-38 Part D, SCHEDULED (2026-11-12)".
- Build tree: main 35bee4da9 (= the design's base and the merge-base); review tree built there once
  (`nice make -j2`, rc 0).
- Client design in force: `docs/design/run_pos_set_stage3_readiness.md` at 14570db62 (identical on
  main and the subject branch; an ancestor of both).
- Rulings frozen at decisions.md e102f5c48, plan.md a4bec96bc. Re-diffed at critic return and at
  hand-back: plan.md +1 line ([COND-FAMILY]); decisions.md gained D196 + its addendum
  (168fac791..a460b14f8: intersection semantics, [COND-FAMILY]). Both unrelated to Part D: **no
  freeze drift that touches the subject.**
- FREEZE NOTES: (1) the F-8 ruling (window R identified by shape alone) has its only reachable record
  in `memfn/src/window.c:270-273`'s comment (the kit's ledgers were denied); (2) D195 (public option
  bits follow caller effect) is dated the freeze day; critics read it as not touching `--memfn=` deny
  rows (an options.def axis, not a flags-word bit) — HELD by rd2 and seam.

## Lenses as run

| lens (file) | model | the one question | why chosen |
|---|---|---|---|
| readiness D0+D3 (rd0d3) | opus | per unit: cites hold, complete, separable; can each check fail | last round before a build go; one readiness critic per unit (D0 and D3 are both test/measurement units) |
| readiness D1 (rd1) | opus | same, for THE DECISION | as above |
| readiness D2 (rd2) | opus | same, for THE RENDERING, plus its deny row | as above |
| soundness (sound) | opus | apply the rules as written to real/crafted witnesses: does any answer move; does G3 (zero movers) hold | a correctness promise by argument (G2's per-position claim, G3's "nothing moves") |
| seam/contract/ruling (seam) | opus | does the answer hold together with its client and the rulings; goals; sibling-of-family + general form/unlocks | a kit<->pcrec seam with a contract change (MF_CLASS_V meaning) and relied-on rulings |
| verifier (verify) | opus | re-derive every finding that would change the design | answer-level claims rested on hand-execution of unbuilt states |

Premise was folded into the readiness critics ("do the cites hold") and seam (K-2's claims); goals and
the two standing questions into seam. All five critics and the verifier returned files complete in the
launch turn (7-16 min each); no resend, no nudge, no replacement.

## Which lens caught what

- Answer-level and G1 holes in the DECLINE (a new reply state) came from three lenses at once:
  sound (SND-1, SND-4), rd1 (RD1-1, RD1-5, RD1-7), seam (SEAM-3, SEAM-4). Every one is on PCREC's
  side of the seam (or a kit rule pcrec reads), which the kit-side G2 family cannot see.
- The deny arm's two defects were found independently by rd2 and sound (RD2-2=SND-3, RD2-3=SND-6).
- The unit-check problems (a check that cannot pass at its unit, a census with no floor, a filler byte
  that does not exist) came from the readiness critics only (rd0d3, rd1).
- The K-2 / R-label question (the documents disagree) came from seam only.

## Overall verdict (proposed): NOT READY — a rev 2 with the FIX-NOW items, then a narrow re-check

Per unit (the critics' verdicts, coordinator-adjusted for consolidation):
- **D0** ready with listed text fixes (F16-F18, F22).
- **D1** ready with listed text fixes (F1-F5, F14, F15, F21, F25) — but F1-F4 are design decisions,
  not wording, and F1 is answer-level.
- **D2** ready with listed text fixes (F6-F10, F23, F24) — F7 and F9 need a decision first.
- **D3** NOT ready (F19, F20): its census cannot see the new sites and its plant cannot fail.
- **Cross-document**: F11 (K-2: which side stops R) has no answer in either document; the client's
  stage-3 build brief cannot be written without it.

Why not "ready with text fixes": one answer-level hole (F1), three G1 compile-failure holes in the
decline (F2, F3, F7), and two open decisions (F9, F11) that change what D2 builds. A narrow re-check
(fix-induced + one readiness critic on D1/D2, and seam on F11) after rev 2 is proposed.

## Findings (consolidated; ids F-n; source ids in brackets; verifier verdict)

### Answer level

- **F1 — a declined run on a handoff route subtracts the RUN's K from the BYTE landmark: matches lost**
  [SND-1, SEAM-3, RD1-7; verify HOLDS (INFERRED; today's half MEASURED)]. pcrec's
  `PF_REQ_LANDMARK_MAXOFF` (src/facts/facts.c:359), `req_handoff_k` (emit_dfa.c:8971),
  `req_handoff_entry_applies` (:8920) and `req_landmark_hit_ppm` (:9002-9014) key on "a run shipped"
  (`whole_len >= 2`), while `req_site_define` makes the head BYTE the landmark when the link is
  untested (:1548) and writes `head_max` = the run's K (:1568); the `gate != b` invariant is also
  skipped (:1510-1514). The kit's twin keeps `h` = 1e6 on a declined run (presence.c:333-345). Witness
  shape `(a|bc)[a-z]{8}.q` (today: VM route, handoff K 11; stage 3: run `[a-z]{8}` declined, K 2,
  subject `bcabcdefgh-q` NOMATCH vs python match at 0). §4 item 1 names only the "nothing tested"
  consequence. **PROPOSED: FIX-NOW** — part_d §4 item 1 states the full fact ("on a decline the
  landmark is the head member, never the run; every pcrec reader of 'a run shipped' reads
  `pres[run].verify`"), the twin takes the byte branch on "no tested run", and the client's §2.1
  reader table gains these rows; a decline witness with a tested member head on a handoff route in
  both G2 and pcrec's tests.

- **F4 — the decline row ahead of P0 silently voids K66's REQUIRED whole-run proof** [SND-2; verify
  PARTLY: the design gap HOLDS; the critic's give-up witness REFUTED by a control (the VM refutes it
  linearly another way); K66's own witness confirms the proof is answer-relevant (`-fno-req-run` ->
  `steps`)]. A stage-3 run with no findable position can out-rank an exact run by bits
  (alt_normal_form §4.4), and the design treats the decline as speed-only. **PROPOSED: FIX-NOW
  (design)** — state the decline's effect on a REQUIRED span and choose: a non-scanning verified whole
  run on REQUIRED (the generic floor's settest is linear), or "no decline on REQUIRED; pcrec prefers a
  run with a findable position there"; a G2/pcrec witness on the K66 shape. Severity design, answer
  plausible but unwitnessed.

### G1 (compile failure on stage-3 sites)

- **F2 — the chain-HEAD rule keys on "stated run"; a declined site has no head and pcrec's
  `req_site_define` fails "verify nothing"** [RD1-1, SND-4; verify HOLDS]. finder.c:847-850 (`led[i] &&
  run >= 0`, `head < 0 && run < 0 && ...`); compose.c:699/704 the same slip; emit_dfa.c:1538-1546.
  G2's `pres_layout_check` accepts the headless layout, so only pcrec sees it. **PROPOSED: FIX-NOW** —
  §2.4 item 2 lists every `run >= 0`/`run < 0` guard (finder.c 817, 848, 849, 855; compose.c 699, 704)
  and says which read "tested"; decline witnesses carry a member.

- **F3 — the decline row FIRST (ahead of P2) breaks P2's "every span or none" `proven_by`, which
  pcrec's admission reads** [RD1-5, SEAM-4; verify HOLDS (INFERRED)]. memfn.h:1186-1187;
  emit_dfa.c:8641-8649; presence.c:310-327. **PROPOSED: FIX-NOW** — place the row after P2 (or give it
  P2's verdict) and write "first in slot PRES ..." precisely; a dominated decline witness.

- **F7 — under D2's deny, a run whose findable stretch is ONE position refuses the compile**
  [RD2-3, SND-6; verify HOLDS (INFERRED)]. `\d{3}-\d{4}`, `\d[aA]\d`: `rs` needs `stretch`,
  `in_stretch` needs `multi` (window.c:300-301, 353-357); `c_pin` needs `run_len >= 2` (:1040);
  `ofs_fn_applies` needs `checked > 0` / refuses a 2-member SET scan (ofsskip.c:128-138). `test-axes`
  would red on the memo's own witness. **PROPOSED: FIX-NOW** — the design states the one-position
  case (decline on the deny arm, or a scan-only part admitted for a derived part) and §5.2 gains the
  layout with a deny-arm refusal floor of 0.

### Design / readiness (would change what is built)

- **F5 — P4's `set_leads` and P2's `dominated` on a declined run are unstated; `mf_pres_picks`'
  public text and three pcrec readers are not listed** [RD1-2; verify HOLDS]. memfn.h:1737-1744;
  emit_dfa.c:8661-8667, 11290-11353. **PROPOSED: FIX-NOW** (text; feeds F2/F3).

- **F6 — D2's deny as written moves today's P3 window artifacts on runs longer than 8** [RD2-2, SND-3;
  verify HOLDS, today MEASURED: `[a-z]+abcdefghijkl` compares positions 4..11]. "The stretch IS the
  member's findable stretch" replaces `stretch_window`. **PROPOSED: FIX-NOW** — "the mode's own
  stretch, clipped to the maximal findable stretch around the scan" (identity today), and an
  `emit_sweep` deny-arm row in D2's check (G3 says every arm).

- **F8 — "`run_len` 1 kept as a RUN term" is unreachable: `translate` groups only `j - i >= 2`**
  [RD2-1; verify HOLDS]. window.c:1522; a lone cube becomes a 2-member SET scan that ofsskip refuses.
  **PROPOSED: FIX-NOW** — list `translate` in D2 and §3.1; a "lone cube scan between wide positions"
  witness/floor.

- **F9 — ofsskip's tableless-set admission is a second byte mover with no deny and no scope, against
  G3; G2 already states such terms** [RD2-5, SEAM-7, RD0-5; verify HOLDS (movers unmeasured)].
  g2_gen.c:769/3053/3110 (`table_ref_on = rn(4) != 0`), run_g2.sh:152 FORM_FLOORS; pcrec's only
  tableless writer is `cover_window` (REPORT, never translated, window.c:1627), so pcrec's today
  population is plausibly zero but G2's is not. **PROPOSED: FIX-NOW (decide now)** — leaning: scope
  the admission to the derived part (G3 holds by construction; named as a special case to retire), or
  give it its own deny with a behavioural name; D0 counts Q3's population at the base; D2 names the
  FORM_FLOORS consequence.

- **F10 — "R by the kit's flag" has no carrier, is a second R recognition beside `run_shaped`, and is
  an unasked exception to F-8** [RD2-7, SEAM-5 (first half), SEAM-9 (verify PARTLY: facts hold, the
  "seam" reading is a ruling), SEAM-10]. `mf_wspan`/`mf_walt` have no field (memfn.h:642-659);
  `merge` is the one writer (window.c:309); `wf_prepare` gets no parent (:2587-2595). **PROPOSED:
  FIX-NOW** — name the carrier and the writer it overrides; carry "F-8 has an exception for the
  derived statement" as a §7 question for the kit manager.

- **F11 — K-2: the two documents disagree on who stops R at a wide position** [SEAM-1, SEAM-2; verify
  HOLDS (today MEASURED: `xy/users\d+` is run-pinned, R grows over walked offsets)]. The client
  (readiness §2.1 `pf_window_of` row) grows R over walk-proven WIDE positions; part_d §2.2 keeps R by
  shape, so such a site loses C-pin and the run-pinned row. part_d's D157 objection to pcrec-side
  shape-stopping is contestable: memfn.h:1572-1573 already states R's shape as a contract fact. A third
  option (SEAM-2): R = any multi-position verify-NO span (the only such span pcrec states is R itself;
  `run_member` already restricts a verify-NO R to EXACT_AROUND), no byte move today, an `MF_SITE_ABI`
  meaning event. **PROPOSED: FIX-NOW (a ruling, jointly kit manager + main)** — pick one of: pcrec
  stops R at the first non-shape position (reads memfn.h's text); the verify-NO widening (MF_SITE_ABI
  event); or accept the movers (C6's trigger fires on day one). Both documents then state it, and §4's
  "NO MF_SITE_ABI event" becomes a stated choice.

- **F12 — §4 (b) and item 3 write today's FIND capability into `has_scan`'s meaning** [SEAM-8; verify
  HOLDS as text; D157 reading a ruling]. C1/C2 would then cost a second `MF_CLASS_V` event for a fact
  pcrec does not need (it can read the scanned position's set). **PROPOSED: FIX-NOW** (drop (b) and
  item 3; "findable" stays the kit's private rule).

- **F14 — D1's G2 check "refusals 0 on runs with a findable position" cannot pass before D2; plant
  (p1) is not a D1 witness** [RD0-1, RD1-4; verify HOLDS, MEASURED: one `[0-9]` position per site
  -> 322 K-1 refusals, 187 with a findable scan]. **PROPOSED: FIX-NOW** — D1's check is the
  reply-level "wide never the scan" count; the refusal-0 floor moves to D2; or D1+D2 land as one
  checked unit (the "D1 alone first" sentence is then qualified).

- **F15 — a new `fd_rows[]` row's manifest obligations are unlisted** [RD0-8, RD1-6, RD1-3; verify
  HOLDS, decider_census MEASURED 86/0 -> 85/2]. rows.tsv, row_floors.tsv, `ROWS_FLOOR=31`,
  finder_history.md, ROWCON `FD_CT`, G2's `G2P_NROUTE`/`route_of`, the reach class while stage 3 is
  absent (`pending-site:`), decider_census MEMBER_COUNT/RUN_CALLERS and the fact's source (via kit.h's
  internal `kit_pres_picks`, not a second `kit_run_decide` call). **PROPOSED: FIX-NOW** (text).

- **F16 — D0's file list misses the driver and table readers of `run`/`mask`** [RD0-2; verify HOLDS].
  g2_pres.h:59, g2_pres_run.c:129-139 (`members(..., m[2])`). **PROPOSED: FIX-NOW** (text).

- **F17 — C2's classifier needs a byte in no set; §5.2's own draws make it not exist** [RD0-3; verify
  HOLDS]. `filler()` returns 0. **PROPOSED: FIX-NOW** — a per-position breaker and a background byte
  outside the verified sets, or a bounded draw with the uncoverable sites counted.

- **F18 — D0 "at the base" as written FAILS on every refusal and re-drawing drops every fixed-seed
  floor** [RD0-4; MEASURED 354 -> 51 rendered]. **PROPOSED: FIX-NOW** — wide strata as an ADDED
  stream on its own rng (today's 354 sites byte-identical), refusals counted only with the K-1 message
  (anything else still a FAIL), the base count becomes D2's must-be-0 population.

- **F19 — D3's census cannot see the derived part and has no floor: its plant cannot fail** [RD0-6;
  verify HOLDS (the sweep record shape not opened)]. vcls.py:15-17/100-103, census0.py:249-254.
  **PROPOSED: FIX-NOW** — widen the population to pre-check derived parts' VERIFIED positions (golden
  files and readers named), a K35 floor from a non-kit source, then the plant; D3 resized (not S).

- **F20 — `settest` class `cn` is open-ended, so a 128-compare set is "measured" by a 7-compare row**
  [RD0-7; verify HOLDS]. **PROPOSED: FIX-NOW** (text: a bound on `cn`, above it UNMEASURED or
  `lower-bound`).

- **F21 — the "declines" floor is a lower bound; an over-declining kit passes** [RD0-9, SUSPECTED].
  **PROPOSED: FIX-NOW** — G2 computes "no findable position" from its own sets; per-site equality; the
  plant "decline when the scan is a cube".

- **F23 — two precheck.c readers of the one-RUN-term shape are missing** [RD2-4, SND-5; verify
  HOLDS]. `run_comment` (precheck.c:150-190, reads `term[0]`: emitted comment text) and the row
  contract's `FLD_table_ref`/`FLD_table_name` comments (:401-402, :427-428). §3's grep had no
  `term\[0\]|run_len`. **PROPOSED: FIX-NOW** (text; widen the grep).

- **F24 — plant (p6) can stay green: no floor guarantees a wide R position lighter than the scan**
  [RD2-6]. **PROPOSED: FIX-NOW** (one floor on rated arts).

- **F25 — the decline is caller-observable, and neither document names its spec hunk (D80)**
  [SEAM-11]. `_REQ_RUN` without `@` (match_api.md row 3's case list), `_REQ_WHY`'s value, tuning
  §2.30 (run-pinned not available where R is wide, per F11's answer). **PROPOSED: FIX-NOW** (facts in
  part_d §4; rows in the client's §2.3).

- **F26 — §7 Q5's direct translation is the general form D2 should weigh now** [SEAM-5, second
  half]. D2 adds three pieces (the internal R flag, `a_mass_choose`'s widened exclusion, the tiling
  check) whose only job is to keep the family's second decision equal to the reply; the direct form
  deletes all three and the latent-UB route (memory pcrec-general-mechanisms-not-special-cases, D153).
  **PROPOSED: FIX-NOW as a DECISION** — rev 2 records the kit manager's choice with its reason (the
  coordinator does not rule it; the leaning in part_d was "not now").

### Doc

- **F13 — `MF_CLASS_V`'s reasons**: omits the precedent-backed one (the new row shifts
  `pres_row`/`pres_led`, as at 6, 7, 8), (a) is already memfn.h:1210-1212's text, and §2.2's
  `us.wr.run_stated` cite is off (only `req_run_at` reads it) [SEAM-6; verify HOLDS]. **PROPOSED: DOC.**
- **F22 — "g2_win_gen.c adds runs with a wide position inside R"** contradicts §2.2 (such a span is
  never R) and the shape already exists (`rand_span`, `two_runs`) [RD0-10]. **PROPOSED: DOC.**

## PROBED-AND-HELD (summary; counts in each critic file)

- Cites: every critic re-read its unit's cites at 35bee4da9 — rd1 10/10, rd2 12/12, seam 6/6 K-1
  facts, verify 10/10; the version numbers (MF_SITE_ABI 27, MF_CLASS_V 9); the seven named existing
  sabotages exist and target what the design says (rd2 7/7; S3012's re-aim correct).
- §2.1's "today a wide position refuses loudly, never a miscompile" MEASURED (sound: 7 driver probes
  through memfn.h; rd0d3: 322/322 refusals all the K-1 message). The latent `run_bytes` UB is real and
  unreachable today (sound, seam).
- G3 for D1 and the non-deny D2 rules: every today run position is one member or a cube (filled by
  `pcrec_memfn_wpos_cube`, `PCREC_MAX_REQ_RUN_POS_SET` 2), so the findable column, the widened
  in-run exclusion and the pinned-join restriction are identities today (rd1, sound, INFERRED; 8 today
  stamps MEASURED).
- §3.3's per-position promise as §2.1 renders it holds (sound), and D187 add. 1's covering-cube rule
  is respected (seam). The occurrence oracle needs no change for joint supersets (rd0d3).
- The pcrec<->kit seam survives a text round trip for the decline (seam); `pres_row`'s index shift is
  harmless to pcrec (resolved by id, memfn_sites.c:782-800).
- Rulings: D144 item 4 / the 2026-10-29 rule — no deny for the decline row (a correctness fix), a deny
  for D2 (can be slower) — agree; D195 does not touch `--memfn=` rows; D77 triggers present on §6;
  D174's `run-verify-wide` describes behaviour (seam, rd2).

## By-id completeness

rd0d3: RD0-1 F14, RD0-2 F16, RD0-3 F17, RD0-4 F18, RD0-5 F9, RD0-6 F19, RD0-7 F20, RD0-8 F15,
RD0-9 F21, RD0-10 F22. rd1: RD1-1 F2, RD1-2 F5, RD1-3 F15, RD1-4 F14, RD1-5 F3, RD1-6 F15, RD1-7 F1.
rd2: RD2-1 F8, RD2-2 F6, RD2-3 F7, RD2-4 F23, RD2-5 F9, RD2-6 F24, RD2-7 F10. sound: SND-1 F1,
SND-2 F4, SND-3 F6, SND-4 F2, SND-5 F23, SND-6 F7. seam: SEAM-1 F11, SEAM-2 F11, SEAM-3 F1,
SEAM-4 F3, SEAM-5 F10+F26, SEAM-6 F13, SEAM-7 F9, SEAM-8 F12, SEAM-9 F10, SEAM-10 F10, SEAM-11 F25.
41 critic findings -> 26 consolidated; none dropped.

## D27 recommendation

The decline is a new caller- and reader-visible contract state, and every answer/G1 hole in it was on
pcrec's side of the seam where the kit's G2 cannot look. RECOMMEND a D27 spec-first author (denied
src/ and tests/) writing decline witnesses from the rev-2 contract text (§4) for the joint stage-3
landing: handoff routes, REQUIRED routes, dominated sites, a member head. The launcher decides.

## Lessons for the guide (proposed)

1. **A new reply STATE is a seam event even with no new field.** All answer/G1 holes (F1-F3) were
   pcrec readers that equate two facts the new state separates ("a run is stated" == "a run part
   ships"). Proposed text for the lens table, seam round trip: "When the subject introduces a new
   STATE of existing fields (a decline, an untested-but-stated link), enumerate every reader on the
   OTHER side that infers one field from another (`whole_len >= 2` as 'the run shipped'), and
   hand-execute each on the new state."
2. **Apply a deny's text literally to today's corpus and to the design's own witnesses.** Two critics
   independently found the deny arm both moving today's bytes and refusing the design's own witness.
   Proposed readiness clause: "for each proposed deny row, apply its sentence as written to (a) one
   today artifact per mode it touches and (b) the design's witness list; the arm must reproduce (a)
   and compile (b)."
3. **Ask whether each unit's CHECK passes at that unit alone.** D1's check could only pass after D2
   (F14); the per-unit readiness brief asked "separable" of the code, not of the check. Proposed: the
   readiness question's "is it separable" reads "can its code land AND its checks pass at that unit
   alone".

## Rulings (kit manager, 2026-11-12)

Overall: NOT READY, as proposed. Rev 2 follows, then a narrow re-check (fix-induced, readiness on D1/D2, seam on F11).
- FIX-NOW: F1-F12, F14-F21 and F23-F26, as proposed.
- DOC: F13 and F22.
- A D27 spec-first author for the decline's contract: YES, at build.

Decisions:
- **F26: take §7 Q5's direct translation NOW, in D2.**
  - What it deletes: the internal R flag (F10), `a_mass_choose`'s widened exclusion, and the tiling check, all pieces whose only job is to keep a second decision equal to the reply, plus the latent-UB route.
  - Why: the house rule is to build the general mechanism, not special cases, and the deleted special cases are the benefit.
  - Consequences: F10 dissolves into it, and rev 2 shows which F10 text survives.
- **F9: scope ofsskip's tableless admission to the derived part only.** G3 holds by construction. It is named as a special case to retire, with its trigger. D0 counts Q3's population at the base, and D2 names the FORM_FLOORS consequence. If F26's direct form removes the need, rev 2 says so.
- **F11: a JOINT ruling with main, PENDING.**
  - Kit leaning: the third option, R = any multi-position verify-NO span. It moves no byte today, and is an `MF_SITE_ABI` meaning event.
  - Why that option:
    - pcrec stopping R at the first non-shape position makes pcrec read the kit's scan capability (D157: facts, not methods), and the boundary moves whenever the kit learns a new scan.
    - Accepting the movers fires C6's trigger on day one, with no measurement behind it.
  - Then both documents state it, and §4's "no MF_SITE_ABI event" becomes a stated choice.
- **F11 RULED (2026-11-12, kit manager + main jointly): option (b).** R is identified by its ROLE: any multi-position verify-NO span that pcrec states is R. pcrec decides how far R reaches (`pf_window_of` grows it over walk-proven positions, readiness memo §2.1). The kit never infers R from shape, and pcrec never reads the kit's scan capability (D157). This is an `MF_SITE_ABI` meaning event inside S2's single landing. main's stage 3 brief says "R by role, not shape". Main also agreed F26 and F9.

# part_d — the kit's answer to R-38 Part D: run positions of 1 to 128 members (design, rev 2)

**rev 2 (2026-11-12, lane pdrev2, opus):** applies the RULED review
`docs/dev/reviews/2026-11-12-r1-memfn-partd.md` (FIX-NOW F1-F12, F14-F21, F23-F26; DOC F13, F22;
the three decisions F26 direct translation IN, F9 scoped, F11 R BY ROLE, joint with main). Each
change is marked `[r1pd Fn]`. Rev 1 (lane pdesign, 5999409e3) is in git history; its §7 Q1 and Q5
are answered here, its §6 C6 is retired by F11.

**Status: DESIGN ONLY, no build go for the kit units here.** Base main `35bee4da9` (cites re-read at
`522faf600`, which carries the F11 ruling's plan note under [RUN-POS-SET]); K38-2 landed
(`MF_SITE_ABI` 27, `MF_CLASS_V` 9). The request: `memfn/docs/requests.md` "R-38 Part D, SCHEDULED"
(set S2, GO Frank 2026-11-11), which lands with pcrec's [RUN-POS-SET] stage 3 in one pcrec abi event.
pcrec's side: `docs/design/run_pos_set_stage3_readiness.md` (its §2.1 is pcrec's reader table, its
§2.2 names the kit sites K-1, K-2, K-3, its §3 is the witness list). Design of record for the run's
seam: `docs/design/memfn/span_runs_sheet.md` rev 1.3 (§2.1-§2.5, §4, §5). Facts, not methods (D157):
every "how" below is the kit's own choice, written here so that pcrec can read what it gets back.

Code is cited by function name, read at `522faf600` (identical to `35bee4da9` under `memfn/` and
`src/gen/`). Measured in this rev: one PROBE build (a scratch copy with `run_shaped` patched, §2.2)
and today's half of the F4 witness (§2.4). No suite was run (Frank's evening hold).

## 0. Goals (ranked; a higher goal wins a conflict)

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | **Every run pcrec states gets a correct reply, and every site renders or declines cleanly.** No refusal and no miscompile on any run of 1..128-member positions, in any encoding; a REQUIRED run keeps its linear no-match proof (K66) `[r1pd F4]` | every user; pcrec's stage-3 lane | G2's presence family over generated runs of 1..128-member sets (§5.2): zero refusals, zero oracle or classifier reds; each decline equal, per site, to G2's own "no findable position" computation `[r1pd F21]` |
| G2 | **A verified extent never claims more than the sets prove** | pcrec's readers of `ver_lo`/`ver_len` (the landmark mass, later the earned skip) | C2's classifier: for every verified position, every byte outside the stated set is rejected by the rendered text (all 256 bytes tried) |
| G3 | **Zero movers on today's population** | every user | `emit_sweep` at the build, EVERY arm including the new deny `[r1pd F6]`: no artifact moves whose run has only one-member or cube positions. The scoped ofsskip admission holds G3 by construction `[r1pd F9]` |
| G4 | **No new scan method without its measurement** (D77; memory `pcrec-new-method-needs-measurement-card`) | the owner, the kit | the build adds no find, scan or skip form; every per-candidate test is an existing carded form (`settest`, `rc-*`, the `walk` loop, §5.3) |

**Non-goals.** Scanning a wide position (§6 C1). Proving exactness (Part C's ranges). Pricing. A
seam field that only today's shape test needs. pcrec-side code (stage 3's lane); the pcrec-side
FACTS stage 3 must state or read are §9's.

## 1. The request's facts, as the kit reads them

1. The run presence span (`pspans`, LAST, `nalt` 1, `nterm` 0) and R inside the window site's
   PARKED/RESEED statements carry positions of ANY 1..128-member byte set (`mf_wspan.set[j]`). The
   run span already admits any non-empty set (`pres_span0_clear`). The statement's LAYOUT does not
   change; the MEANING of a verify-NO span of two or more positions does (§2.2, `[r1pd F11]`).
2. A position may be a joint superset (`cat|dog` states `{c,d}{a,o}{t,g}`). The kit's contract is
   per position: a candidate HOLDS each verified position's set, never "the candidate matches"
   (span_runs_sheet §2.3). A joint superset changes no promise (§3.3).
3. Every encoding: digits (10 members), hex (22), `[a-z]` (26), `\w` (63), UTF-8 continuation sets.
   New runs appear where none was stated before (`[a-z]{8}`, `cat|dog`).
4. pcrec reads `mf_class.run` at every reader and needs a reply, a scan-less verified run, or a
   STATED decline for every stated run (§2.4). A refusal fails the compile.

## 2. The three K38-2 sites

### 2.1 K-1: the derived run part becomes a DIRECT TRANSLATION of the reply `[r1pd F26]`

**Today.** `derive_run_part` copies the reply's extent `[ver_lo, ver_lo + ver_len)` into a one-span
window statement (verify YES, core all); `wf_parts_prepare` hands it to `wf_prepare`, so the window
family DECIDES the extent a second time (R by `run_shaped`, `run_member`'s verify-YES branch,
`a_mass_choose`'s in-run filter, C-pin, `c_run`, `translate`), and a loud check refuses unless the
result is one RUN term at `ver_lo` whose `plan_pos` is the reply's scan ("the derived run part's
find is not at the run reply's scan position"). A wide position never joins `c_run`'s group, so a
wide extent refuses (MEASURED by the review: 322 of 322 refusals carry that message).

**Rev 2: the part's terms are written from the reply, with no second decision.** A new kit function
(name the builder's; here `run_part_terms`) replaces `derive_run_part` + the family call for the
derived part. From the run span's sets and the reply `(has_scan, scan, ver_lo, ver_len)`:

1. **The scan stretch** `[a, b)`: the maximal stretch of positions inside the extent, holding `scan`,
   each with a `(T, K)` spelling (one member, or a two-member cube). `has_scan` 1 guarantees that
   `scan` has one (§2.4 item 1).
2. **The terms, ascending by offset**: each extent position below `a` is its own `MF_T_SET` term
   (its full set, `table_ref` 0); `[a, b)` is ONE `MF_T_RUN` term of `run_len` b - a, **1
   included** (a lone one-member or cube scan between wide positions, `[r1pd F7, F8]`); each extent
   position from `b` up is its own `MF_T_SET` term. Every term `need` REQUIRED, `ppm` full, as
   `translate` writes them. At most `ver_len` <= `MF_WSPAN_POS` = `MF_MAX_TERM` terms, so a part
   always fits.
3. **The scan**: `plan_hint` = the RUN term's index, `plan_pos` = scan - a. The ranking (RQ-2,
   `rank_n`/`rank_pos`/`rank_ppm`) is the run decision asked over the RUN term's positions, by the
   SAME function `translate` uses (moved out of `translate` into one shared function, so S3006's
   target is one place); its first answer is the scan (the same rule over a subset that holds the
   global winner), held by one loud check.
4. **Scan-less** (`has_scan` 0, `ver_len` > 0: only P0's REQUIRED whole run, §2.4 item 3): every
   extent position is a term (the stretch rule does not apply), `plan_hint` = `MF_NO_PRED`,
   `rank_n` 0.
5. The RUN term's `(T, K)` comes from `run_bytes`, generalised to read positions through a set
   accessor (its two callers: `translate` and this function); it refuses (`kit_fail`) a position
   with no `(T, K)` spelling, so `(T, K)` stays a complete spelling of every RUN term (§2.3).

**Identity today (G3).** Every today extent is all findable, so `[a, b)` = the extent: one RUN term
at `ver_lo` of length `ver_len`, `plan_hint` 0, `plan_pos` scan - `ver_lo`, `need` REQUIRED, the
ranking over the extent's sets with the art's tie (the lever included). That is exactly what the
family's path produces today: its check refuses anything else and today's G2 presence pass refuses
nothing (354 rendered, 0 failures, re-run by the review's verifier). `emit_sweep` holds it at D2.

**What F26 deletes (the benefit).** Rev 1's D2 needed four pieces only to keep the family's second
decision equal to the reply; none is built:
- the kit-internal R flag on the derived statement (rev 1 §2.1; review F10: it had no carrier in
  `mf_wspan`/`mf_walt`, no path through `wf_part_site` to `wf_prepare`, and broke F-8 for one
  client). `merge` stays the one writer of `m->run` `[r1pd F10]`;
- `a_mass_choose`'s widened in-run exclusion (every R position but `rs`);
- `wf_parts_prepare`'s generalised TILING check (and today's "find is not at the scan" check, which
  goes with the family call);
- `c_run`'s pinned join restricted to the member's findable stretch, and with it the LATENT-UB ROUTE:
  `run_bytes` over a non-shape position (uninitialised `a` under mask 0xFF) was reachable only if a
  pinned R held a wide position. After F26 and F11 the pinned stretch is either exact-only (verify-NO
  R: `run_member` asks EXACT_AROUND) or all-spelled by definition (the verify-YES pinned span,
  §2.2), and the derived part never reaches `c_run`.

What survives of rev 1 §2.1: the extent may contain wide positions; the scan is findable; wide
positions are SET terms tested by the kit's own membership test (`kit_set_test`, card `settest`).

**ofsskip and precheck: the derived part's two admissions, SCOPED** `[r1pd F9, F23]`. The derived
part reaches ofsskip through precheck's `run_part`. Two shapes that today's `ofs_fn_applies` refuses
are admitted ONLY there:
- a multi-member `MF_T_SET` term with `table_ref` 0 (the run span forces `table_ref` 0, so pcrec
  offers no table for it): `verify_chain` renders it with `kit_set_test`, `table_params` skips it;
- a scan-less predicate (`plan_hint` `MF_NO_PRED`): the function's BODY is a byte loop over every
  candidate in `[pos, n - maxk)` running the verify chain, a new BODY row of ofsskip's table (name
  the kit's; here `fn-walk`) above `fn-memchr`, holding only where no scan is stated. Its form is the
  existing walk loop (§5.3). It has no deny: it is the only renderable body for a K66 proof (D158).

The scope is ONE argument to `ofs_fn_applies` ("the derived run part"), passed by precheck's
`run_part` where the site states a run presence span (under `wf_parts_check` such a site's FUNC part
is always the derived one), and by the BODY walk it reaches; every other caller (the OFS row, G2's
OFS and STMT families) keeps today's refusals. The renderers' rules are general; only the admission
is scoped. **G3 holds by construction**: no today predicate reaches the new admissions.
**F9's question answered: the admission is still NEEDED under F26** (the direct translation emits
tableless wide SET terms that ofsskip must test), so it is scoped, not dropped. It is a named
SPECIAL CASE TO RETIRE (§6 C7, with its trigger). `run_g2.sh`'s `FORM_FLOORS`
(`generic:5800 ofsskip:1120`) do NOT move under the scope; the general admission would move both
(G2's OFS/STMT families draw tableless multi-member SET terms on about a quarter of their sites), so
the retirement re-pins them.

precheck's readers of the one-RUN-term shape `[r1pd F23]`:
- `run_part`: a FUNC part whose terms are all at offsets >= 0, with at most one RUN term, which is
  `plan_hint`'s (or no scan and no RUN term needed), admitted by `ofs_fn_applies` with the scope.
  The `nterm == 1` and `plan_hint == 0` clauses go.
- `run_comment` reads `term[0]` as the run; it reads the RUN term (`term[plan_hint]`) instead, and
  states the SET-tested positions ("and a set test at each of positions ...") and, scan-less, "every
  position from `pos` is tested" in place of the memchr clause. Emitted comment text, so its moves
  are stage-3 movers only (today's parts are one RUN term).
- the row contract's `FLD_table_ref` and `FLD_table_name` comments ("a run part has no SET term",
  "no part has a SET term to name") become false; they read "the derived part's SET terms carry
  `table_ref` 0 and are the kit's own test (no table to name)".

### 2.2 K-2: the window site's R, BY ROLE `[r1pd F11]`

**Today.** `run_shaped` identifies R by shape alone (the F-8 ruling: "two or more positions, each one
member or a cube"), in `merge` and in `wf_check` (at most one per alternative). pcrec states R in
`pf_window_of`, verify NO, grown over walk-proven positions.

**The ruling (joint, kit manager + main, 2026-11-12; plan [RUN-POS-SET] note).** R is identified by
its ROLE: **any span of two or more positions that pcrec states verify NO is R.** pcrec decides how
far R reaches (`pf_window_of` grows it over walk-proven positions, readiness memo §2.1, now by a
subset-of-set test with `pcrec_memfn_wpos_bits`); the kit never infers R from shape, and pcrec never
reads the kit's scan capability (D157). An `MF_SITE_ABI` meaning event inside S2's single landing.

**Why it moves no byte today** (review SEAM-2, enumeration re-verified): pcrec's window statements
are 8 `pcrec_memfn_wspan` calls; the only multi-position verify-NO span among them is R itself
(`pf_window_of`), which is shape-only today. The one other verify-NO kind is a ONE-position walked
span. `run_member` already treats a verify-NO R by EXACT_AROUND (member and pinned stretch exact
positions only), so a wide R position never enters the pinned compare. Stage 3's witness
`xy/users\d+` (today `run-pinned`, offsets `0*,1,..,7`): R becomes `xy/users{0-9}`, still R, member
and pinned stretch `xy/users` as today, so it KEEPS `run-pinned` and `_REQ_RUN`'s `@` (under rev 1
it lost both: review F11's measured mover).

**Verify-YES spans: the ruling's subject is the verify-NO R; a verify-YES span keeps today's
whole-compare rule, now named as the kit's compare grouping, not R** (an open confirmation, §7 Q1).
MEASURED (probe, scratch copy of this tree, `run_shaped` patched to "verify NO and two or more
positions: R; verify YES: never"; 17 patterns, single compiles): 9 artifacts moved, 7 of them cover
sites (`/user|/users`, `abc`, `foobar`, `\bfoobar\b`, `hello world`, `[aA][bB][cC]def`,
`(?i)select`: the cover span `{0..k-1: S_d}` lost C-pin, so `abc`'s one masked word compare became a
byte compare around the stop and `RX_RUN_WORDS` went 1 -> 0), and 2 pre-check parts refused (the
derived statement, verify YES, lost R: F26 removes that route). `xy/users\d+` and the other 6 did
not move. So reading the ruling as "a verify-YES span is never pinned" would move today's cover
bytes. Rev 2 reads it as the plan note writes it ("R (the run's pinned verify-NO span)") and keeps,
for verify-YES spans only, today's rule as the kit's private grouping:
- **R**: the alternative's verify-NO span of two or more positions (any sets). Unique per
  alternative (`wf_check`: "an alternative states two verify-NO spans of two or more positions: R is
  identified by its role, so it is unique").
- **The verify-YES pinned span** (where no R is stated): a verify-YES span of two or more positions
  each with a `(T, K)` spelling. Every one of its positions is verified anyway (verify YES); whether
  they are ONE compare with the stop inside is a spelling choice, which may read the kit's own
  spelling (D157 binds pcrec, and the kit's method stays the kit's). Today's code path, unchanged:
  `run_member`'s WHOLE branch, `a_mass_choose`'s in-run filter, C-pin. `wf_check` keeps "at most
  one such span per alternative". Where an alternative states R AND such a span, R is the member
  span and the verify-YES span is verified by C-yes, unpinned (today such an alternative exists only
  in G2's window family, never in pcrec's statements, §5.2).
- `merge` writes `m->run` from the two rules above (R first); `run_shaped` is replaced by the two
  role/spelling predicates; F-8's "R is identified by this shape alone" is RETIRED for R.

**What R by role changes inside the kit (stage-3 population only).** Positions R newly covers carry
`multi` in the candidate list; where their meet is one member or a cube, `in_stretch` (the TIE
table's first row) reads them. pcrec grows R only over WALK-PROVEN positions, whose k-set lies inside
R's set, so the meet at those offsets is the walked span's own set, unchanged: the candidate masses
do not move, only the tie row and R's membership do.

**The reply.** `mf_wreply.run_stated` keeps its field and its pcrec reader (`req_run_at`, row 2,
with `pinned`; it is the only reader of `run_stated`, the run-pinned prefilter row reads `pinned`
through `next_keys`, `[r1pd F13]`). Its memfn.h text changes: "1 iff the chosen alternative has a
member span: R (its verify-NO span of two or more positions; member the least-mass EXACT position,
stretch the exact run around it) or, where none is stated, a verify-YES span the kit compares whole;
0 where R has no one-member position". `mf_wspan.verify`'s text gains "a verify-NO span of two or
more positions IS the run R (at most one per alternative)".

### 2.3 K-3: the run compare (`runcmp.c`, `rc_of`; `kit_run_set`)

**What it must become: NOTHING.** A RUN term only ever holds positions with a `(T, K)` spelling: its
two writers are `translate` (groups shape positions by `c_run`'s rule) and the direct translation
(§2.1, the scan stretch), and their one builder `run_bytes` refuses anything else. Wide positions
reach the text only as SET terms. runcmp's rows (`run_len` 1 included: `memcmp` exact, `bytes`
masked), `tuning.md` §2.38's `words` row, `gate.c`'s `cl_run`, the form hash and `kit_run_set` keep
their meaning.

### 2.4 The decision's changes (presence.c, finder.c, compose.c)

1. **The scan is findable.** `run_modes[]` gains a candidate column: `exact` (EXACT_AROUND, as
   today) or `findable` (WHOLE and WINDOW: one member or a cube). "Findable" is the KIT'S PRIVATE
   RULE (what today's finds read); it is not written into `has_scan`'s meaning `[r1pd F12]`.
   Today every run position is findable, so nothing moves (G3).

2. **The decline row, AFTER P0 and P2** `[r1pd F3, F4]`. A run with NO findable position (`[a-z]{8}`,
   `cat|dog`, `\d{4}`) on an OPTIONAL, non-dominated route is DECLINED by a new PRES row placed
   after P2 and before P3 (`fd_rows[]`: P0, P2, the decline, P3, P4, P9). It reads a new span fact
   (here `SF_RUN_NOSCAN`, set on the run span only), taken from the run answer `kit_pres_picks`
   already asks, handed back through a kit-internal out-parameter (kit.h); no second
   `kit_run_decide` call and no change to `mf_pres_picks`' public layout `[r1pd F15]`. Its link:
   verify 0, `proven_by` 0; `cls.run` all zero and unread; `cls.pres_row[run]` names it. It tests
   nothing, so `fd_run_modes[]` gains no entry; it has no deny (denying it would refuse the compile;
   memory `pcrec-flag-follows-caller-effect`). Placement: P2 first keeps P2's "every span of the
   site, or none" `proven_by` (memfn.h `mf_link`), which pcrec's `dominated` admission reads (review
   F3: the rev 1 placement left a dominated site's run span unproven, so pcrec admitted a pre-check
   with nothing to verify). P0 first is item 3.

3. **REQUIRED: no decline; P0 verifies the whole run SCAN-LESS** `[r1pd F4]`. A REQUIRED span's run
   keeps K66's linear no-match proof: P0's reply on a run with no findable position is
   `{has_scan 0, scan 0, ver_lo 0, ver_len n}` (the whole run verified at every candidate, no find),
   written as the P0 row's `no_scan` column in `fd_run_modes[]` (P0: the whole run, scan-less; P3,
   P9: unreachable, the decline row precedes them, a loud refusal if reached). The part renders by
   §2.1 item 4 and ofsskip's `fn-walk` body. Chosen over the alternative "pcrec prefers a run with a
   findable position on REQUIRED" because that would make pcrec read the kit's scan capability, the
   very thing the F11 ruling forbids (D157). Speed: a walk per candidate position on a site that
   today scans a byte; the population is stage-3-only (a wide run must out-rank an exact one by
   bits, alt_normal_form §4.4) and is counted by D3's census; C1 is its upgrade.

4. **The readers that took "a stated run" for "a tested run"** `[r1pd F2, F5]`. The run span is
   decided FIRST in `fd_pres`'s span loop (each span's row is independent; only P3's member rule
   reads the run's link), so its final link is known before the members'. With
   `trun = run >= 0 && cls->pres[run].verify`:
   - P3's member rule: `k.verify = !trun && i == set_pick` (a declined run leaves the set's pick
     verified, as on a run-less site);
   - the chain-HEAD rule: `if (led[i] && trun) head = i;` and
     `if (head < 0 && !trun && set_pick verified) head = set_pick;` (both `run >= 0`/`run < 0` guards);
   - `pres_layout_check` (compose.c): the head part's `need` reads `trun`, not `run >= 0`; and it
     gains the check G2 lacked: "no tested run and a verified member, yet no HEAD" refuses, so a
     headless declined layout reds in G2 instead of only in pcrec;
   - the coverage rule (`covered[]`) already reads `cls->pres[run].verify`: unchanged;
   - `kit_pres_picks`: where the run has no scan, P4's `set_leads` is -1 (no run scan to compare, as
     with no run) and P2's `dominated` takes the set's pick as the lead (as with no run) while still
     requiring `proof->run` for a stated run (dominance never claims a run the proof does not
     verify). `rr.scan` is read only where `has_scan` is 1. memfn.h's `set_leads`/`dominated` text
     says both; pcrec's readers are `req_set_leads_applies` and the pick shadow's `rdom`/`rlead`
     records (§9).

5. **The twin's landmark is the head member where the run is not tested** `[r1pd F1]`. The FIFTH's
   mass in `kit_pres_picks` takes its byte branch where `!rs || !ext->ver_len` (a declined run has
   `ext` = none). A scan-less P0 run keeps the run branch (its part ships). This is the kit half of
   F1; pcrec's half is §9 item 2.

**Witnesses for the answer-level and G1 findings** (each FAILS without its change; python3 `re`
oracle for the answers; the stage-3 halves INFERRED, stage 3 being unbuilt):

| finding | pattern, subject | right answer | without the change | with it |
|---|---|---|---|---|
| F1 | `(a\|bc)[a-z]{8}.q`, `bcabcdefgh-q` (handoff route; today `_REQ_HANDOFF "11"`, VM) | match (0,12) | declined `[a-z]{8}`, landmark `q`, K = the run's 2: the attempt restarts at 9, NOMATCH | landmark `q`, K = `q`'s own 11 (pcrec reads `pres[run].verify`; the twin's byte branch): match |
| F2 | `[a-z]{8}.q`, `zz abcdefgh-q` | match (3,13) | `set_leads` -1, no led, `run >= 0` keeps head -1: `q` is REST, pcrec's "verify nothing" internal error (G2 green) | head `q`; G2's new `pres_layout_check` clause reds the old rule |
| F3 | `x.(?:cat\|dog)`, `x-dog`, on a start search proving the run (`pres_proof.run` 1, stage 3's statement) | match (0,5) | the decline ahead of P2: members `proven_by` 1, run 0: pcrec admits a pre-check verifying nothing (internal error) | P2 decides every span: `dominated`, no pre-check |
| F4 | `(x?)([a-z]+)+eeeeeeee~#~#~#~#.[0-7]{32}\1` (`--features all`), `e` + 36 `a` + `~#~#~#~#x` + 32 `8` | no match | stage 3 ranks `[0-7]{32}` (160 bits) above the exact 128-bit run; declined: `steps` (exit 3). Today's half MEASURED: default `nomatch` in 0.00 s; `-fno-req-run` `steps` in 2.24 s | P0 walks the whole wide run scan-less: `nomatch` |
| F7 | `\d{3}-\d{4}` on the deny arm (`--memfn=no-run-verify-wide`), `tel 555-1234`; `\d[aA]\d`, `x1A2`, both arms | (4,12); (1,4) | the stretch is one position: the family path makes it a SET term ofsskip refuses (one member: `checked` 0; a cube: a 2-member SET scan): `test-axes` reds | one RUN term of `run_len` 1 at `-` (`fn-memchr`) / at `[aA]` (`fn-pair`) |

## 3. Every other kit reader of a run position (grep, `memfn/src`)

Found by `grep -n -E 'in_stretch|run_shaped|shape\(|run_bytes|find_groups|kit_run_decide|kit_run_set|kit_run_member|kit_mass|rc_of|fd_run_modes|rank_pos|MF_T_RUN|cube|term\[0\]|run_len|run >= 0|run < 0'`
over `memfn/src/*.c` (rev 2 widened it by the last four alternatives, `[r1pd F23]`), each hit read in
its function.

### 3.1 The table

"Assumes <= 2" means the code is correct only while every run position is one member or a cube.

| reader (function) | reads | assumes <= 2? | fate |
|---|---|---|---|
| `kit_run_decide` / `kit_run_member` (presence.c, window.c) | positions as sets, mass by `kit_mass` | YES, implicitly (with `exact` 0 every position is a scan candidate) | §2.4 item 1: the `findable` column |
| `stretch_window`, `stretch_exact` (presence.c) | summed set mass; one-member test | no | unchanged; under the deny clipped to the findable stretch (§5.1 D2) |
| `fd_run_modes[]`, `fd_run_mode` (finder.c) | the route's stretch mode | no | gains the `no_scan` column (P0: scan-less whole run, §2.4 item 3) |
| `fd_pres`: P3's member rule, the head rule (finder.c) | "a stated run is a tested run" (`run >= 0`, `run < 0`) | YES | §2.4 item 4: read `trun`; the run span decided first |
| `kit_pres_picks`: P4's `scan_mass`, P2's lead, the FIFTH's branch | `rr.scan` with no `has_scan` guard; `rs` as "a run part ships" | YES | §2.4 items 4, 5 |
| `pres_layout_check` (compose.c) | the head's `need` by `run >= 0` | YES | §2.4 item 4, plus the headless-layout refusal |
| `fd_pres`'s coverage rule (`covered[]`) | the extent's one-member positions, where the run is tested | no | unchanged |
| `run_shaped`, `in_stretch`, `shape` (window.c) | shape by definition | YES | §2.2: R by role; `run_shaped` becomes the verify-YES pinned span's spelling test; `in_stretch` unchanged |
| `merge`, `wf_check` (window.c) | R by shape; "two R-shaped spans" | YES | §2.2 |
| `c_run` (window.c) | the pinned join has no shape test | YES (relied on R being shape-only) | unchanged: the pinned stretch is exact (verify-NO R) or spelled (verify-YES pinned span); the derived part no longer reaches it (§2.1) |
| `run_bytes` (window.c) | shape; uninitialised `a` when `shape()` is 0 | YES (latent UB) | reads a set accessor, refuses a position with no spelling (§2.1 item 5) |
| `translate`'s grouping (`grouped = j - i >= 2`) and RQ-2 ranking | groups of two or more; the scanned RUN term's positions | no | unchanged for family sites; the ranking moves into one shared function (§2.1 item 3); the derived part no longer passes `translate` `[r1pd F8]` |
| `a_mass_choose`'s in-run stop | the `stretch` positions of a verify-YES R | no (after F26: verify-YES pinned spans only, all spelled) | unchanged (rev 1's widening deleted, §2.1) |
| `run_member` (window.c) | verify NO: EXACT_AROUND; verify YES: WHOLE | YES on verify YES, through item 1 | the `findable` column (§2.4); its verify-YES branch now serves the verify-YES pinned span only |
| `derive_run_part`, `wf_parts_prepare` | one RUN term; the family's second decision | YES | §2.1: the direct translation; the check deleted |
| `precheck.c` `run_part`, `run_comment`, the row contract's `FLD_table_ref`/`FLD_table_name` | `nterm == 1`, `term[0]` RUN, `plan_hint == 0`; "no SET term" | YES | §2.1 |
| `ofsskip.c` `ofs_fn_applies`, `verify_chain`, `table_params`, the BODY rows | a multi-member SET term needs pcrec's table; a scan always | YES | §2.1: the scoped admission; `fn-walk` |
| `vrun.c` `vrun_applies` (SIMD) | `nterm == 1`, one RUN term, `run_len >= 2` | YES | UNCHANGED: it declines a multi-term part, which gets the scalar body. Bytes move only on stage-3 wide runs at `-fmemfn-simd` (§6 C4) |
| `runcmp.c` `rc_of`, `run_cmp_sat`; `kit_run_set`; `gate.c` `cl_run`; `term_prove` (compose.c) | `(T, K)` | YES | unchanged (§2.3) |
| `pres_span0_clear` (compose.c) | the run span's sets: non-empty | no | unchanged |
| `finder.c` `find_facts` (FIND sites' RUN term) | `run_len == 1` | no | not a run-presence reader |

### 3.2 Which readers assume <= 2 members, in short

Implicitly, through "every position is findable" or "a stated run is tested": `kit_run_decide`
(and through it `run_member`'s verify-YES case and `kit_pres_picks`), P3's member rule, the head
rule, `pres_layout_check`, the twin's branch, `run_bytes`. Explicitly, by their stated shape:
`derive_run_part`/`wf_parts_prepare`, `run_part`, `run_comment`, `ofs_fn_applies`, `vrun_applies`,
runcmp's `(T, K)`, and R's recognition.

### 3.3 Correctness of a superset position

- **The promise is per position and stays that way.** `ver_len` says that every yielded candidate
  holds each position of the extent IN ITS STATED SET; never combinations. A joint superset is
  harmless (`cog` holds every set of `{c,d}{a,o}{t,g}`). The kit never infers exactness from its
  sets (span_runs_sheet §2.3); Part C's ranges are pcrec's statement of exactness.
- **A verified position is tested against its FULL set, exactly.** A RUN term holds only spelled
  positions, so its cube IS the set. A wide position is a SET term tested by `kit_set_test`, whose
  maximal byte ranges are exact. A covering test (a cube hull, a vector range test) is legal only
  for a position the reply does NOT count verified (D187 add. 1); the extent is contiguous, so a
  hull-tested position would end it. The build has no such form (§6 C5).
- **No reader turns a superset into a claim.** `fd_pres`'s coverage rule credits only one-member
  positions. `term_prove` proves a SET term's whole set. The twin's product mass errs toward
  refusing the landmark.
- **The control** is C2's classifier over all 256 bytes per verified position (§5.2); the plant is a
  cube hull rendered for a wide position.

## 4. `MF_SITE_ABI`, `MF_CLASS_V`, the pcrec abi, and what pcrec reads

Each number is a STATED CHOICE, the next number at landing, never a literal; readers by grep.

- **`MF_SITE_ABI`: ONE event** `[r1pd F11]`, chosen: R by role. A verify-NO span of two or more
  positions now means R whatever its sets (§2.2); no layout move. The scoped ofsskip admissions
  (§2.1) are kit-side rendering admissions on a predicate the kit itself writes, not a statement
  meaning: no event of their own.
- **`MF_CLASS_V`: ONE event**, chosen, with three reasons `[r1pd F13]`:
  1. the decline row joins the PRES slot between P2 and P3, so `pres_row`/`pres_led`'s indices
     move for P3, P4 and P9, the precedent of `MF_CLASS_V` 6, 7 and 8 (no layout move). pcrec's
     reader resolves rows by id (`memfn_sites.c`, through `mf_finder_rows`), so it survives; the
     recorded indices are re-pinned in `tests/memfn/decider_census.tsv`, `arm_fixtures
     --finder-rows` and S1122;
  2. WHERE an untested run link occurs: memfn.h's `mf_run_reply` text already says "read ONLY where
     the run span's link is tested; else all zero and UNREAD"; what is new is that a stated run's
     link may be untested outside P2 (the decline, `proven_by` 0);
  3. a NEW read state: a TESTED run with `has_scan` 0 and `ver_len` > 0 (P0's scan-less whole run).
     `has_scan`'s text keeps its words ("0: no single find position") and the invariant line gains
     "`has_scan` 0 with `ver_len` > 0: every candidate position is tested (no find)".
  Rev 1's reason (b) ("`has_scan` means one member or a cube") is DROPPED `[r1pd F12]`.
- **pcrec abi: rides stage 3's one event.** Kit bytes move only on runs that hold a wide position,
  i.e. only on runs stage 3 states for the first time. The deny row (§5.1 D2) adds a member to
  `pcrec --list-axes`'s memfn section, so its floor literal in `docs/spec/` moves in the same change.
- **New reply field: NONE.** What pcrec must read, from existing fields, as facts (pcrec's side is
  §9):
  1. **The decline** `[r1pd F1]`: `cls.pres[run].verify` 0, `proven_by` 0, `pres_row[run]` the
     decline row. The run part does not ship, so on a decline **the landmark is the head member
     (P3's set pick, as on a run-less site), never the run**: every reader of "a run shipped" reads
     `pres[run].verify`, never `whole_len`. Where no member is verified either, the site has nothing
     to render (pcrec's admission).
  2. **The scan-less REQUIRED run**: `pres[run].verify` 1, `has_scan` 0, extent the whole run. The
     run part ships (its landmark is the run); there is no scan position (`@`).
  3. **The extent may span wide positions**: still "each position held IN ITS STATED SET", never
     exactness.
  4. **The window site**: R is pcrec's verify-NO span of two or more positions; `run_stated` 0 only
     where R has no one-member position (existing meaning of the EXACT_AROUND member).
  Rev 1's item 3 ("`@scan` is always a one-member or cube position") is DROPPED `[r1pd F12]`: `scan`
  is an index into the run pcrec stated, whose set pcrec can read.
- **Caller-observable consequences, which pcrec's spec hunk carries (D80)** `[r1pd F25]`:
  `match_api.md` §6.3.7¶7 row 1 holds only where the run part has a scan, and row 3's case list
  gains "a run the kit declines on the pre-check" and "a REQUIRED run verified with no scan
  position"; §6.3.7¶8 and `tuning.md` §2.29 gain the `_REQ_WHY` value pcrec names for a declined
  run with nothing to render; `tuning.md` §2.30: the run-pinned rows apply wherever R has a
  one-member position, however wide its other positions (a wide position no longer costs them,
  §2.2); the `--list-axes` floor (above). The rows land in the readiness memo §2.3's list.

## 5. Build units

Kit units, on a kit branch cut from main after K38-2, landing in ONE merge with pcrec's stage 3.
Sizes as span_runs_sheet §5: S under a day of lane work, M a lane, L a lane plus a fix round.
Sabotage ids are taken at build time from the top of the free range. Every heavy run is a boxqueue
job; existing sabotages are checked with `REACH_ONLY=1`.

### 5.1 The units, with what each finding moved

| unit | size | content | check (passes AT THIS UNIT) | the plant that makes it fail | existing sabotages |
|---|---|---|---|---|---|
| D0 | M | **G2 FIRST.** `g2_pres_gen.c`, `g2_pres.h` (`run`/`mask` arrays) and `g2_pres_run.c` (`in_set`, `members(..., m[2])`, `filler`) take positions as SETS `[r1pd F16]`; the wide strata are an ADDED stream on their own rng, so today's 354 sites stay byte-identical `[r1pd F18]`; C2's classifier probes every non-member byte of every verified position, with a per-position breaker (§5.2) `[r1pd F17]`; G2 computes "no findable position" from its own sets `[r1pd F21]`. The G2 window family's R model (`g_run_shaped`, `two_runs`' fix rule) is NOT changed here (D2 changes it with R by role) `[r1pd F22]`. COUNTS at the base: K-1 refusals, with the K-1 message only; G2 window alternatives with a verify-NO multi-position span holding a wide position (they become R at D2); the OFS/STMT tableless multi-member SET terms (Q3's population, `[r1pd F9]`) | the family runs; any refusal OTHER than the K-1 message FAILS; the base counts recorded as literals (K35: the script's, sharing no source with the kit); the K-1 count becomes D2's must-be-0 population | n/a (measures the base) | none |
| D1 | M | **THE DECISION.** `findable` column in `run_modes[]`; the decline row after P2 with `SF_RUN_NOSCAN` and its contract; P0's scan-less `no_scan` column; the run span decided first; P3's member rule, the head rule and `pres_layout_check` read `trun` (+ its headless-layout clause); `kit_pres_picks`' `has_scan` guards, `set_leads`/`dominated` on a run with no scan, the twin's byte branch. `MF_CLASS_V` moves; memfn.h text for `mf_link` (run span), `mf_run_reply`, `mf_pres_picks`. A new row's obligations `[r1pd F15]`: `tests/memfn/rows.tsv` and `row_floors.tsv` lines, `ROWS_FLOOR` +1 in `run_rows.sh`, `memfn/docs/finder_history.md` entry, an `FD_CT` contract, G2's `G2P_NROUTE`/`route_of` gain the route, its reach class `pending-site:` while stage 3 is absent, `decider_census.tsv` row + `MEMBER_COUNT`, `RUN_CALLERS` unchanged (no second `kit_run_decide`) | `emit_sweep`: zero movers on today's corpus, every arm, both layers (G3). G2 presence family, REPLY level `[r1pd F14]`: the scan is never a wide position (count = wide-position count); each decline equals G2's own "no findable position" on an OPTIONAL non-dominated route, per site (F21); REQUIRED no-findable runs come back scan-less tested; a dominated decline witness keeps `proven_by` on every span (F3); a declined run with a member has a HEAD (F2); the twin's landmark on a declined handoff site is the byte's (F1). Refusals are NOT gated here: the K-1 count may only fall | (p1) the `findable` column ignored: the scan lands on a wide position on the floored sites where a wide position is lighter than every findable one (F24's floor, moved here: p6 is deleted with its piece) `[r1pd F24]`. (p2) the decline row deleted: G2's decline equality reds. (p3) "decline when the scan is a cube" (F21's plant): per-site equality reds. (p4) the head rule back to `run >= 0`: `pres_layout_check`'s new clause reds | S3005 (twin mass: re-aimed if the byte branch moves its witness), S3008, S1122 (re-pin `pres_row`), S1104: REACH re-run |
| D2 | L | **THE RENDERING.** The direct translation (§2.1: `run_part_terms`, the shared ranking function, `run_bytes` over a set accessor); `derive_run_part`'s family call and `wf_parts_prepare`'s check deleted; precheck's `run_part`/`run_comment`/row-contract comments; ofsskip's SCOPED admissions (tableless SET terms through `kit_set_test`; the scan-less `fn-walk` BODY row, its row-table obligations as D1's: +1 `ROWS_FLOOR`); **R by role** (§2.2: `merge`, `wf_check`, the verify-YES pinned span's spelling test, memfn.h `mf_wspan.verify`/`run_stated` text, `MF_SITE_ABI` moves); G2's window R model `g_run_shaped` and `two_runs`' fix rule to R by role (a second verify-NO multi-position span becomes verify YES, not three-member) `[r1pd F22]`. Its DENY row in `options.def` (D174 name, e.g. `run-verify-wide`): denied, EVERY mode's stretch is clipped to the maximal findable stretch holding the scan, a decision option read by every reader of the decision on the art (reply extent, the twin, the part) `[r1pd F6]`; identity today (every position findable). A scan-less P0 run is not clipped (nothing to clip around; the K66 proof is undeniable, D158) | `emit_sweep` zero movers on today's corpus, every arm INCLUDING `--memfn=no-run-verify-wide` (G3, F6). G2 presence family on every target/level, both layers: refusals 0 (D0's K-1 population, `[r1pd F14]`), C2 (256-byte non-member probes), the occurrence oracle (`tests/memfn/occurrence_oracle.py`), the deny pass with its one-position-stretch layouts and a deny-arm refusal floor of 0 (F7). G2 window family: R-by-role alternatives (member exact, pinned stretch exact). `make test-memfn-g2`, `test-memfn-finder`, `test-axes` | (p5) a wide verified position rendered by its cube hull: C2 reds. (p6') one range dropped from `kit_set_test` in `verify_chain`: the occurrence oracle reds. (p7) the direct translation's stretch rule widened past a wide position: `run_bytes`' refusal reds G2's refusal floor. (p8) `run_shaped` restored for verify-NO spans: the G2 window family's wide-R alternatives lose their member (and the stage-3 `xy/users\d+` witness loses `run-pinned`). (p9) the scope dropped from `ofs_fn_applies`: `emit_sweep`/`FORM_FLOORS` move | S3006 (rank: re-targeted to the shared ranking function), S3012 (in-run filter: its detector, the derived part's refusal, is deleted with the family route; RE-AIM to a G2 window witness of a verify-YES pinned span under `run-tie-left`, or retire with that role if none detects it, decided by REACH), S3047 (second derived part, `wf_parts_check`: kept), S3007, S3011, S285, S279 (runcmp/ofsskip: kept, RUN terms spelled-only), S1104: REACH re-run on every window.c, ofsskip.c and precheck.c row; a row whose only reacher was the derived part's family route is re-aimed or its reach class re-stated (`rows_check.py`) |
| D3 | M (was S) | **THE MEASUREMENT'S FLOOR.** No new method (G4), so no new card. The `verify_cmp` card's census (span_cards §2.3, `kit-grid@3`, form `settest`) is WIDENED to the pre-check derived parts' VERIFIED positions (`vcls.py`'s population filter and `census0.py`'s `row1_class` today see only stated window sites), golden files and readers named at the build `[r1pd F19]`; `settest`'s classes get a bound: `c1`, `c2`, `cn` = 3 to 7 compares (the measured `\w` instance), above 7 `cn+` UNMEASURED (or `lower-bound`), never priced by the 7-compare row `[r1pd F20]`; the `walk` loop's parts (`fn-walk`) are counted | the census lists every (form, cls) the stage-3 artifacts use, none silently priced; a K35 floor on the derived parts' verified positions FROM A NON-KIT SOURCE (pcrec's artifact count of stage-3 run parts, from its artifact diff) | a census that drops the derived parts' settest terms: the floor reds | none |

**Order.** D0, then D1, then D2, then D3. **D1 lands alone only with its own reply-level check green
and the K-1 refusal count at most D0's base** (D1 changes the scan's candidates and adds the decline,
neither of which renders a wide extent); every stage-3 population needs D2, so D1 and D2 land together
whenever stage 3 lands `[r1pd F14]`. One kit branch, one landing with stage 3.

**Readiness after rev 2** (the review's per-unit verdicts, and what moved them):
- **D0: READY.** F16 (file list), F17 (breaker), F18 (added stream, refusal accounting), F21 (G2's own
  decline computation), F22 (the window R model moves at D2, not here), F9 (Q3 counted).
- **D1: READY pending the narrow re-check.** F1, F2, F3, F4, F5 (the decision's design changes and
  their witnesses), F12/F13 (the seam text), F14 (a check that passes at D1), F15 (row obligations),
  F24 (the floor that makes p1 fail), F25 (spec facts for pcrec).
- **D2: READY pending the narrow re-check.** F26 (the direct translation replaces four pieces), F6
  (deny reproduces today, every arm swept), F7/F8 (one-position stretches render), F9 (scoped
  admission), F10 (dissolved), F11 (R by role), F23 (precheck's readers).
- **D3: READY, resized to M.** F19 (population + non-kit floor), F20 (the `cn` bound).

**The D27 author (ruled YES, at build).** A spec-first author in a D27 cell (`scripts/mk_d27_cell.sh`),
denied `src/`, `tests/`, `memfn/src/` and `memfn/tests/`, writes decline and R-by-role witnesses from
the CONTRACT TEXT only (this §4, memfn.h's new `mf_link`/`mf_run_reply`/`mf_pres_picks`/`run_stated`/
`mf_wspan.verify` text, `match_api.md` §6.3.7's rows): handoff routes (F1), a member head (F2),
dominated sites (F3), REQUIRED routes (F4), the deny arm's one-position stretch (F7), a wide R that
keeps `run-pinned`. Answers oracle-verified (python3 `re`; libpcre2 where it applies). The witnesses
land with the joint stage-3 merge.

### 5.2 The G2 coverage the wide sets need

- **Generator** (D0; both layers, every level the U2 target list admits, default and `run-tie-left`
  levers, the deny arm). Per run position, a set from a stratified member-count distribution: 1; 2 as
  a cube; 2 not a cube; 3-8; 9-32; 33-128; exactly 128. Shapes: one range; a union of ranges
  (`{80-89, B1-BF}`); scattered members; `\d`, hex, `[a-z]`, `\w`, `\s`; caseless pairs; UTF-8 lead
  and continuation sets. Layouts: a wide position next to the scan, at either end of the extent,
  between two findable stretches (`ab\dcd`); a lone findable position between wide ones (`\d[aA]\d`,
  F7/F8); runs with NO findable position on OPTIONAL, REQUIRED and dominated routes (F3, F4); a
  declined run with a member on a handoff (ASSIGN) site (F1); joint supersets as the per-position
  union of 2-4 literal branches (`cat|dog`); the readiness memo §3's witnesses verbatim. Lengths
  2..`MF_WSPAN_POS`. The wide strata draw from their OWN rng stream after today's sites (F18).
- **The breaker and the background** `[r1pd F17]`. EXTENT's broken occurrence uses, per position, a
  byte outside THAT position's set (one always exists: `info(S) >= 1` means at most 128 members).
  The background (COVER, EXTENT, SCAN) is a byte in no position's set where one exists; a site whose
  sets' union covers all 256 bytes is counted "no background" (a K35 floor of its own, never silent)
  and skips the probes that need one.
- **Oracles**: the occurrence oracle (unchanged, D27-written from span_runs_sheet §3.3) reads the
  STATED sets as the language; C2's classifier reads the RENDERED text: per verified position the
  admitted bytes equal the stated set.
- **Floors** (K35, literals in the script, counts of THIS family's records, never the kit's
  `moved`): sites with >= 1 wide verified position; declines (equal per site to G2's own
  computation, F21); scan-less REQUIRED runs; wide positions never the scan; sites on rated arts
  where a wide position is lighter than every findable one (F24, p1's reach); one-position
  stretches on the deny arm (F7); deny-pass sites; "no background" sites; per target.
- **The window family** (D2): `g_run_shaped` becomes R by role (verify NO, two or more positions) plus
  the verify-YES pinned span's spelling rule; `two_runs`' fix turns every verify-NO multi-position
  span after an alternative's first into verify YES (rev 1's three-member fix would now make a second
  R). D0's base count of wide verify-NO spans is that family's moved population, by design.

### 5.3 The measurement cards (memory `pcrec-new-method-needs-measurement-card`)

D2 adds no find, scan or skip form. The per-candidate tests on new sites are `kit_set_test`
(`verify_cmp`, form `settest`, card in `kit-grid@3`, its classes bounded by D3) and the runcmp
rows; the scan-less body `fn-walk` is the existing `walk` loop (card `walk`) with the verify chain as
its per-candidate test. D3 counts every class the stage-3 artifacts use. Each §6 candidate that is
built adds its card in the same change.

## 6. Faster methods and retirements: candidates with triggers (not build; D77)

| # | candidate | trigger (the measurement that would start it) |
|---|---|---|
| C1 | scan a WIDE position with a set find (the set-FIND walk or a table/class find), so a declined run gets a pre-check and a scan-less P0 run a find | the stage-3 census counts declined and scan-less runs on corpus + bench, AND a bench G1 on those patterns shows an engine-only (or walk) artifact losing to a set-find prototype by more than noise |
| C2 | scan a NON-CUBE two-member position (`fn-pair` on any two bytes; the window family's B-pair does) | the census's declines whose best position is a non-cube pair (`cat\|dog`) are a counted population AND G1 shows a loss |
| C3 | several RUN terms per part (word compares of the findable stretches on both sides of a wide position) | `verify_cmp` shows per-byte compares of a side stretch cost more than `rc-words` by more than noise, on a counted population of stage-3 parts |
| C4 | `vrun` (SIMD) on a multi-term part | a SIMD-layer G1 on stage-3 wide runs loses against `vrun` on the same run with D2's deny |
| C5 | a covering prefilter (cube hull, vector range test) ahead of the exact `settest`, counted unverified | a SIMD measurement of the hull test against `settest` on the census's classes |
| C6 | RETIRED by F11 `[r1pd F11]`: rev 1's "stated R label" is what R by role gives, with no field | — |
| C7 | RETIRE the scoped ofsskip admission (§2.1) for the general rule (a tableless set is the kit's own test everywhere; scan-less bodies wherever stated), with its OWN deny (behavioural name) and G3 checked with it denied `[r1pd F9]` | D0's base count of today's refused tableless OFS/STMT predicates (pcrec's population, expected 0: its one tableless writer, `cover_window`, is REPORT and never translated; and G2's) is non-zero on pcrec's side, OR a second kit writer of tableless SET terms appears; the retirement re-pins `run_g2.sh`'s `FORM_FLOORS` |

## 7. Open questions (each with a leaning)

1. **Does the F11 ruling reach verify-YES spans?** (kit manager + main.) Rev 2 reads the plan note's
   "R (the run's pinned verify-NO span)" literally: verify-NO multi-position spans are R by role; a
   verify-YES span keeps today's whole-compare rule as the kit's spelling choice (§2.2). The other
   reading MOVES today's cover bytes (MEASURED, probe: 7 of 17 patterns, `abc`'s word compare among
   them). Leaning: confirm rev 2's reading; the other reading needs its own measured trigger (a cover
   G1 loss), not a ruling.
2. **The deny's name** (D174): leaning `run-verify-wide` ("verify wide run positions"). Kit manager's
   call.
3. **ANSWERED (F9):** the tableless admission is scoped to the derived part; its retirement is C7.
4. **The decline's admission on pcrec's side**: moved to §9 as stated pcrec-side facts.
5. **ANSWERED (F26):** the direct translation is IN, in D2 (§2.1).
6. **F4's choice (scan-less P0 over "pcrec prefers a findable run on REQUIRED")** is the kit
   manager's to confirm; leaning as chosen (§2.4 item 3): the alternative crosses D157 the way F11
   forbids.

## 8. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: RELEVANT.** D2 adds per-candidate membership tests, and P0's scan-less parts
   walk every candidate. Whether verifying a wide position pays (fewer engine entries) or costs (a
   compare per candidate on a hit-dense scan) depends on the regime; hit-dense Greek/Cyrillic text
   with a scan on `{CE,CF}` is the sharp case. Linux, `taskset`-pinned, both layers. The deny is
   D2's alpha OFF arm; the decline and the scan-less body are correctness and have none. The official
   verdict is pcrec's G1 (its timing vs its own deny, population from a pcrec-side artifact diff).
2. **Independent control: RELEVANT.** C2 reads the RENDERED text; the occurrence oracle is
   D27-written from the contract; G2 computes the decline from its own sets (F21); `emit_sweep`'s
   zero-mover gate is pcrec's artifact diff (never the kit's `moved`); D3's floor comes from pcrec's
   artifact count (F19). Each plant in §5.1 names the check that reds, and each existing row is
   REACH-rerun.
3. **What moves when data is regenerated: RELEVANT.** The byte-rate payload decides the scan
   (findable positions only), P3's window and the twin, so a rate regeneration can move a pick on a
   wide run: a pcrec abi event by its bytes, as today. A UCD bump moves pcrec's sets (pcrec's). The
   `verify_cmp` card's regeneration moves no byte (no pricing reads it yet).

## 9. For main: the pcrec-side facts stage 3 must state or read

Facts only (D157); the how is stage 3's. Each is a reader of the reply or a statement pcrec makes.

1. **R by role** `[r1pd F11]`. pcrec states R as a verify-NO span of two or more positions over the
   walk-proven positions (`pf_window_of`'s subset-of-set test, `pcrec_memfn_wpos_bits`), and NEVER
   stops R at a non-shape position; it reads `pinned`/`run_stated` as today. The stage-3 brief says
   "R by role, not shape". Witness: `xy/users\d+` keeps `run-pinned`, offsets `0*,1,..,7`, and
   `_REQ_RUN`'s `@`.
2. **The decline** `[r1pd F1, F2, F3]`. `pres[run].verify` 0, `proven_by` 0, `pres_row[run]` = the
   decline row; `cls.run` unread. Every pcrec reader of "a run shipped" reads `pres[run].verify`,
   never `whole_len`: `PF_REQ_LANDMARK_MAXOFF` (facts.c; computed before the kit replies, so stage 3
   moves or re-reads it), `req_handoff_k`, `req_handoff_entry_applies`, `req_handoff_applies`,
   `req_landmark_hit_ppm`, and `req_site_define`'s head-vs-`req_byte` check (today skipped whenever
   `run >= 0`). These rows join the readiness memo §2.1 table. Witness F1 (§2.4).
3. **Nothing to render.** A declined run with no verified member: pcrec's admission declines the
   pre-check (today `req_site_define`'s "verify nothing" internal error) and names its `_REQ_WHY`
   value (§6.3.7¶8, `tuning.md` §2.29).
4. **The scan-less REQUIRED run** `[r1pd F4]`. `pres[run].verify` 1, `has_scan` 0, extent the whole
   run: the run part ships (landmark and K are the run's), `_REQ_RUN` carries no `@`
   (§6.3.7¶7 row 1 needs a scan). Witness F4.
5. **`mf_pres_picks` on a run with no scan** `[r1pd F5]`: `set_leads` -1, `dominated` led by the set's
   pick and still requiring `proof->run`; readers `req_set_leads_applies` and the pick shadow's
   `rdom`/`rlead` records.
6. **Version events** at landing: `MF_SITE_ABI` (R by role) and `MF_CLASS_V` (the row index shift,
   the decline's place, the scan-less state), the next numbers, readers by grep; pcrec's abi event is
   stage 3's own.
7. **Spec hunks** `[r1pd F25]`: §4's list (`match_api.md` §6.3.7¶7 rows 1 and 3, §6.3.7¶8,
   `tuning.md` §2.29, §2.30, the `--list-axes` floor), in the readiness memo §2.3's list.

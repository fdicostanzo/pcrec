# part_d — the kit's answer to R-38 Part D: run positions of 1 to 128 members (design, rev 1)

**Status: DESIGN ONLY, no build go for the kit units here.** Lane pdesign (opus), 2026-11-12. Base
main `35bee4da9`, K38-2 landed (`MF_SITE_ABI` 27, `MF_CLASS_V` 9). The request: `memfn/docs/requests.md`
"R-38 Part D, SCHEDULED" (set S2, GO Frank 2026-11-11), which lands with pcrec's [RUN-POS-SET] stage 3
in one pcrec abi event. pcrec's side: `docs/design/run_pos_set_stage3_readiness.md` (its §2.2 names
the three kit sites K-1, K-2, K-3; its §3 is the witness list). Design of record for the run's seam:
`docs/design/memfn/span_runs_sheet.md` rev 1.3 (§2.1-§2.5, §4, §5). Facts, not methods (D157): every
"how" below is the kit's own choice, written here so that pcrec can read what it gets back.

Everything about the code is READ at `35bee4da9`. Nothing was built or run (Frank's evening hold).
Code is cited by function name. The witness patterns' set sizes are from the readiness memo §3.

## 0. Goals (ranked; a higher goal wins a conflict)

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | **Every run pcrec states gets a correct reply, and every site renders or declines cleanly.** No refusal and no miscompile on any run of 1..128-member positions, in any encoding | every user; pcrec's stage-3 lane | G2's presence family over generated runs of 1..128-member sets (§5.2): zero refusals, zero oracle or classifier reds, the declines counted and each one stated in the reply |
| G2 | **A verified extent never claims more than the sets prove** | pcrec's readers of `ver_lo`/`ver_len` (the landmark mass, later the earned skip) | C2's classifier: for every verified position, every byte outside the stated set is rejected by the rendered text (all 256 bytes tried, not only one-bit neighbours) |
| G3 | **Zero movers on today's population** | every user (the unit's bytes move only where stage 3 states something new) | `emit_sweep` at the build, every arm: no artifact moves whose run has only one-member or cube positions |
| G4 | **No new scan method without its measurement** (D77; memory `pcrec-new-method-needs-measurement-card`) | the owner, the kit | the build adds no find, scan or skip form. The one new verify site reuses an existing carded method (`settest`, `verify_cmp`). The faster forms are §6 candidates, each with its trigger |

**Non-goals.** Scanning a wide position (§6 C1). Proving exactness (Part C's ranges, not scheduled).
Any pcrec-side reader (stage 3's lane). Pricing. A seam field that only today's shape test needs.

## 1. The request's facts, as the kit reads them

1. The run presence span (`pspans`, LAST, `nalt` 1, `nterm` 0) and R inside the window site's
   PARKED/RESEED statements carry positions of ANY 1..128-member byte set (`mf_wspan.set[j]`).
   The seam already admits any non-empty set on the run span (`pres_span0_clear`'s check refuses
   only the empty set). The STATEMENT form does not change.
2. A position may be a joint superset (`cat|dog` states `{c,d}{a,o}{t,g}`). The kit's contract is
   already per position. It promises that a candidate HOLDS each verified position's set, never
   that the candidate is a match (span_runs_sheet §2.3). So a joint superset is invisible to the
   kit and changes no promise (§3.3).
3. Every encoding, so wide byte-encoding sets come too: digits (10 members), hex (22), `[a-z]` (26),
   `\w` (63). New runs also appear where none was stated before (`[a-z]{8}`, `cat|dog`).
4. pcrec reads `mf_class.run` at every reader, and needs a reply or a STATED decline for every
   stated run. A refusal fails the compile.

## 2. The three K38-2 sites (answers to the request's "for you to confirm")

All three readings in the request are CONFIRMED at `35bee4da9`. For each site below: what the
code does today, what a wide position does to it, and what it must become.

### 2.1 K-1: the derived run part (`derive_run_part`, `wf_parts_prepare`)

**Today.** `derive_run_part` copies the reply's extent `[ver_lo, ver_lo + ver_len)` into a
one-span window statement (verify YES, core all), and the window family decides it as a part.
Its plan reaches the legacy part shape through `translate`. In `translate`, `c_run`'s groups become
`MF_T_RUN` terms through `run_bytes`, and every other plan position becomes an `MF_T_SET` term.
`wf_parts_prepare` then requires ONE RUN term at `ver_lo` with the find at the reply's scan, and
otherwise refuses with "the derived run part's find is not at the run reply's scan position".
`precheck.c`'s `run_part` requires the same shape: `nterm == 1`, `term[0]` a RUN term,
`plan_hint == 0`, and `ofs_fn_applies` true.

**What a wide position does.** It never joins a group, because `c_run` and `run_group_ok` require
`shape()` (one member, or a two-member cube). The plan therefore has several terms, and the check
in `wf_parts_prepare` REFUSES the compile. The failure is loud and is never a miscompile, as the
memo inferred. A second effect appears only if the derived extent is made R (as §2.1 requires
below): `c_run`'s PINNED branch (`in_pinned(o) && in_pinned(o-1)`) joins neighbours WITHOUT
checking their shape. `run_bytes` would then build a RUN term over a wide position. On a
non-shape position `shape()` returns 0 without writing `*a`, so `run[i]` is an uninitialized byte
under mask 0xFF. Today this cannot be reached, because a pinned R is always shape-only. It becomes
reachable the moment R can hold a wide position. It is a LATENT MISCOMPILE and must become a
loud guard (unit D2).

**What it must become.** The part VERIFIES every extent position against its full set and SCANS
only a position the existing finds can read:
- The run decision's scan is FINDABLE: one member, or a two-member cube (§2.4 item 1). The
  extent may contain wide positions.
- The derived extent is R for the window family BY THE KIT'S OWN KNOWLEDGE (it built the statement
  from pcrec's run), not by `run_shaped`. This is a kit-internal flag on the derived statement,
  not a seam field.
- Inside a pinned R, only the MEMBER's maximal stretch of findable positions is ONE compare (one
  RUN term, `run_len` 1 included, so that a lone cube scan keeps `fn-pair`). Every other extent
  position is its own term. A one-member position is a byte compare. A wider position is the kit's
  own membership test `kit_set_test` (the generic row's and the window floor's C-own spelling).
  Today a pinned R is all findable, so the member's stretch is the whole R and the bytes are
  identical (G3).
- `run_bytes` refuses (`kit_fail`) any position that is not one member or a cube. That turns the
  latent defect into a loud one.
- `ofs_fn_applies` and `verify_chain` (ofsskip.c): a multi-member SET term with `table_ref` 0 is
  tested by `kit_set_test`, and a term with a table keeps pcrec's table probe; `table_params`
  skips such terms. `runs <= 1` stays true, because only the member's stretch is a RUN term.
- `run_part` (precheck.c): a FUNC part whose predicate `ofs_fn_applies` admits, every term at an
  offset >= 0, with the scan term (`plan_hint`) either a RUN term or a one-member SET. The
  `nterm == 1` and `plan_hint == 0` clauses are dropped.
- `wf_parts_prepare`'s check stays loud, but checks the general property: the part's terms TILE
  `[ver_lo, ver_lo + ver_len)` exactly (ascending, contiguous, each position in one term), and
  the scanned position (`term[plan_hint].offset + plan_pos`, or the SET term's offset) equals
  `rr.scan`.
- `a_mass_choose`'s in-run filter excludes EVERY position of a verify-YES R except the run
  decision's `rs`, not only the `stretch` ones. Otherwise a wide R position with a smaller mass
  becomes the stop and the check above refuses. Today every R position is a stretch position, so
  nothing moves.

### 2.2 K-2: the window site's R (`run_shaped`)

**Today.** R is "two or more positions, each one member or a cube". `run_shaped` identifies R by
shape alone (the F-8 ruling), in `merge` (C-meet) and in `wf_check` (at most one per alternative).

**What a wide position does.** A stated R with a wide position is NOT R. Its positions stay in the
plan as necessary conditions (verify NO, sound). The window family's member, C-pin and the
run-pinned compare do not apply to it. The reply states this as `mf_wreply.run_stated` 0. pcrec
already reads that field (`req_run_at`; the run-pinned prefilter row's `us.wr.run_stated`), so the
outcome is a STATED decline, not a silent one. The memo's "silently" holds only for the plan's
contents.

**What it must become: NOTHING in the minimal form.** The shape test is KEPT. Two widenings were
considered and REJECTED, for these reasons:
- **Recognizing R shape-free** ("two or more positions, none full") MOVES TODAY'S BYTES.
  `pcrec_cover_site` (src/gen/known.c, `cover_window`) states a verify-YES span `{0..k-1: S_d}`
  of ARBITRARY sets. That span is R today exactly where every `S_d` is one member or a cube, and
  then C-pin keeps the stop in the plan (`c_stop`). A shape-free test would make every multi-position
  cover span R, so C-pin would fire on cover artifacts that do not use it today.
- **A stated R label** (a field on `mf_walt` naming R's span) is the general form, and it is an
  `MF_SITE_ABI` event. It also moves bytes: cover spans that are R today by shape lose R unless
  pcrec labels them, and labelling them only where they are shape-only would put the kit's shape
  test on pcrec's side (D157). It is §6 C6, with a trigger.

So R on the window site stays "one member or a cube per position". pcrec decides what it states
there. A wide position in R costs that site its run member (`run_stated` 0) and nothing else.

### 2.3 K-3: the run compare (`runcmp.c`, `rc_of`; `kit_run_set`)

**Today.** Every RUN term is `(T, K)`. `rc_of` reads the run, the mask and the length, and
`kit_run_set` rebuilds a set from `(T, K)` (for `term_prove`, and `kit_run_at`).

**What it must become: NOTHING.** Under §2.1 a RUN term only ever holds one-member or cube
positions, and its one builder (`run_bytes`) now refuses anything else. So `(T, K)` is still a
complete spelling of every RUN term. Wide positions reach the text only as SET terms. runcmp's
rows, `tuning.md` §2.38's `words` row, `gate.c`'s `cl_run`, the form hash and `kit_run_set` keep
their meaning. The invariant that used to hold by construction now has a guard.

### 2.4 The decision's two changes (presence.c, finder.c)

1. **The scan is findable.** `kit_run_decide`'s mode table (`run_modes[]`) gains a candidate
   column: `exact` (EXACT_AROUND, as today) or `findable` (WHOLE and WINDOW: one member or a cube).
   Today `kit_run_member` called with `exact` 0 considers EVERY position. With a 25-member UTF-8
   continuation set, which has almost no mass on ASCII-heavy rates, it would choose a position no
   find can read. Today every run position is findable, so nothing moves (G3).
2. **The stated decline.** A run with NO findable position (`[a-z]{8}`, `cat|dog`: c/d, a/o and t/g
   each differ in more than one bit; `\d{4}`) has `has_scan` 0 from the decision. Today P0 or P9
   would still test the link, and `derive_run_part` would then refuse the compile. Instead, a new
   PRES row FIRST in `fd_rows[]` (ahead of P0) reads a new span fact, "the run states no findable
   position" (computed from the same `kit_run_decide` answer that `kit_pres_picks` already asks).
   Its link is untested and not proven. `cls.run` stays all zero. `cls.pres_row[run]` names the
   row. The row tests nothing, so `fd_run_modes[]` gains no entry. It has no deny: denying it would
   refuse the compile (memory `pcrec-flag-follows-caller-effect`: a correctness fix gets none).

## 3. Every other kit reader of a run position (grep, `memfn/src` at `35bee4da9`)

Found by `grep -n -E 'in_stretch|run_shaped|shape\(|run_bytes|find_groups|kit_run_decide|kit_run_set|kit_run_member|kit_mass|rc_of|fd_run_modes|rank_pos|MF_T_RUN|cube'`
over `memfn/src/*.c`, then each hit read in its function.

### 3.1 The table

"Assumes <= 2" means the code is correct only while every run position is one member or a cube.

| reader (function) | reads | assumes <= 2? | fate |
|---|---|---|---|
| `kit_run_decide` / `kit_run_member` (presence.c, window.c) | positions as sets, mass by `kit_mass` | YES, implicitly: with `exact` 0, every position is a scan candidate, so it assumes every position is findable | §2.4 item 1: the `findable` column |
| `stretch_window`, `stretch_exact` (presence.c) | summed set mass; one-member test | no | unchanged (a wide position's large mass keeps it out of P3's least window; when it is inside, it is verified by §2.1's SET term) |
| `fd_run_modes[]`, `fd_run_mode` (finder.c) | the route's stretch mode | no | unchanged; §2.4 item 2's row precedes them |
| `fd_pres`, P3's member rule `k.verify = run < 0 && i == set_pick` | "a stated run is a tested run" | YES (every stated run was testable) | it reads "no TESTED run": a declined run leaves P3's set pick verified, as on a run-less site. The decline fact is computed before the span loop (the run is the LAST span) |
| `kit_pres_picks`: P4's `scan_mass = kit_mass(rs->set[rr.scan])` and P2's `one_member(rs->set[rr.scan])` | `rr.scan` with no `has_scan` guard | YES (`has_scan` was always 1) | both read `rr.scan` only where `has_scan` is set. Otherwise the run has no lead (P2's lead is the set's pick; P4 compares against no scan) |
| the twin admission's mass (`kit_pres_picks`, the FIFTH), over `ext`'s extent | the product of capped per-position masses | no | unchanged; correct, but over a joint superset the product OVERESTIMATES the hit rate (it assumes the positions are independent), which only makes the admission more conservative (§3.3) |
| `fd_pres`'s coverage rule (`covered[]`) | the extent's one-member positions | no | unchanged |
| `run_shaped`, `in_stretch`, `shape` (window.c) | shape by definition | YES (that is their meaning) | kept (§2.2); the derived extent is R by the kit's own flag (§2.1) |
| `c_run` (window.c) | the pinned join has NO shape test; the unpinned join has one | YES (the pinned branch relies on R being shape-only) | §2.1: inside a pinned R, join only within the member's findable stretch |
| `run_group_ok`, `find_groups`, `build_runs` (E-find's C-run) | shape | no (the check is explicit) | unchanged |
| `run_bytes` (window.c) | shape; an uninitialized `a` when `shape()` is 0 | YES (latent UB) | §2.1: refuses loudly |
| `translate`'s RQ-2 ranking (`rank_pos[]`) | `kit_run_decide` over the scanned RUN term's positions | no (a RUN term is findable only) | unchanged; the ranking is built only when `plan_hint` is a RUN term, so `rank_ok` holds |
| `a_mass_choose`'s in-run stop | the `stretch` positions of R only | YES (all of R was stretch) | §2.1: excludes every R position but `rs` |
| `run_member` (window.c) | verify NO: EXACT_AROUND; verify YES: WHOLE | YES on verify YES, through item 1 | the `findable` column (§2.4) |
| `derive_run_part`, `wf_parts_prepare` | one RUN term | YES | §2.1 |
| `precheck.c` `run_part` | `nterm == 1`, RUN, `plan_hint == 0` | YES | §2.1 |
| `ofsskip.c` `ofs_fn_applies`, `verify_chain`, `table_params` | a multi-member SET term needs pcrec's table | YES (no tableless wide term was ever stated) | §2.1: `kit_set_test` when `table_ref` is 0 |
| `vrun.c` `vrun_applies` (SIMD) | `nterm == 1`, one RUN term | YES | UNCHANGED: it DECLINES a multi-term part, which then gets the scalar `fn-memchr`/`fn-pair` body. This moves bytes only on new wide runs at `-fmemfn-simd` (§4; candidate C4) |
| `runcmp.c` `rc_of`, `run_cmp_sat`; `kit_run_set`; `gate.c` `cl_run`; `term_prove` (compose.c) | `(T, K)` | YES | unchanged: `run_bytes` keeps them findable-only (§2.3) |
| `pres_span0_clear` (compose.c) | the run span's sets: non-empty | no | unchanged |
| `finder.c` `find_facts` (FIND sites' RUN term) | `run_len == 1` | no | not a run-presence reader |

### 3.2 Which readers assume <= 2 members, in short

Implicitly, through "every position is findable": `kit_run_decide` (and through it `run_member`'s
verify-YES case and P4/P2 in `kit_pres_picks`), P3's member rule, `a_mass_choose`, `c_run`'s pinned
join and `run_bytes`. Explicitly, by their stated shape: `derive_run_part`/`wf_parts_prepare`,
`run_part`, `ofs_fn_applies`, `vrun_applies`, runcmp's `(T, K)`, and R's recognition.

### 3.3 Correctness of a superset position (question 3)

- **The promise is per position and stays that way.** `ver_len` says that every yielded candidate
  holds each position of `[ver_lo, ver_lo + ver_len)` IN ITS STATED SET. It says nothing about
  combinations. A joint superset (`{c,d}{a,o}{t,g}`) is therefore harmless: the candidate `cog`
  holds every set, and the reply never claimed otherwise. The kit never infers exactness from its
  sets (span_runs_sheet §2.3). Part C's ranges, when scheduled, are pcrec's statement of
  exactness, never the kit's inference.
- **A verified position is tested against its FULL set, exactly.** A RUN term is findable-only,
  so its cube IS the set. A wide position is tested by `kit_set_test`, whose maximal byte ranges
  are exact. A covering test (a cube hull, a vector range test that is wider than the set) is a
  legal private test only for a position the reply does NOT count as verified (D187 add. 1). The
  extent is contiguous, so a hull-tested position inside the extent ends it there. The build has
  no such form; §6 C5 is the candidate.
- **No reader turns a superset into a claim.** `fd_pres`'s coverage rule credits only one-member
  positions. `term_prove` (`mf_class.proven[]`) proves a SET term's whole set, never a byte inside
  it. The twin's product mass errs toward refusing the landmark.
- **The control** is C2's classifier, extended to all 256 bytes per verified position (§5.2). The
  plant is a cube hull rendered for a wide position.

## 4. `MF_SITE_ABI`, `MF_CLASS_V`, the pcrec abi, and what pcrec reads (questions 4, 5)

- **`MF_SITE_ABI`: NO event** in the minimal form. pcrec's statements keep their layout and their
  meaning: the run span already takes any non-empty set, and R on a window site keeps its
  shape-based meaning (§2.2). The OFS admission of a tableless wide SET term (§2.1) is a kit-side
  RENDERING admission, not a change to what a statement means. Whether it moves bytes on today's
  OFS sites is measured at the build (§7 Q3). If it does, the movers are a declared population,
  not an abi number. The only candidate that would need an event is C6 (the R label).
- **`MF_CLASS_V`: ONE event** (the next number at landing, never a literal; readers by grep).
  `mf_class`'s layout is unchanged; the MEANING of the run's link widens in two ways. (a) On any
  route a stated run may come back untested AND unproven: the decline (§2.4 item 2). Until now
  P0/P3/P9 always tested a stated run, and pcrec's `req_site_define` treats "nothing tested" as an
  internal error. (b) `has_scan` now means "the scan is a one-member or cube position". The
  memfn.h text of `mf_link` (the run span) and of `mf_run_reply` says both.
- **pcrec abi: rides stage 3's one event.** Kit bytes move only on runs that hold a wide position,
  so only on runs stage 3 states for the first time. The new deny row (§5.1 D2) adds a member to
  `pcrec --list-axes`'s memfn section, so the floor literal in `docs/spec/` moves in the same
  change (memfn/CLAUDE.md, option namespace).
- **New reply field: NONE.** What pcrec must read, all from existing fields, each as a fact:
  1. **The decline**: `cls.pres[run].verify` 0 with `proven_by` 0 means that the kit tests
     nothing of this run. `cls.run` is all zero and unread, and `cls.pres_row[run]` names the
     deciding row. Where no member span is tested either, the site has nothing to render; that
     admission is pcrec's (today it is an internal error).
  2. **The extent may span wide positions.** `[ver_lo, ver_lo + ver_len)` still means "each
     position held IN ITS STATED SET", and it is still never exactness.
  3. **The scan** (`@scan`) is always a one-member or cube position.
  4. **The window site**: `mf_wreply.run_stated` 0 where the stated R holds a wide position
     (existing meaning, by shape).

## 5. Build units

Kit units, on a kit branch cut from main after K38-2 (it is), landing in ONE merge with pcrec's
stage 3. Sizes as span_runs_sheet §5: S is under a day of lane work, M a lane, L a lane plus a fix
round. Sabotage ids are taken at build time from the top of the free range. Every heavy run is a
boxqueue job. Existing sabotages are checked with `REACH_ONLY=1`.

### 5.1 The units

| unit | size | content | check | the plant that makes it fail | existing sabotages |
|---|---|---|---|---|---|
| D0 | M | **G2 FIRST** (as K38-2a was): `g2/g2_pres_gen.c`'s positions become SETS (today it draws `run`/`mask`, cube-domain), drawn by §5.2's generator. The family's C2 classifier probes every non-member byte of every verified position. `g2/g2_win_gen.c` adds runs with a wide position inside R. `run_g2.sh`'s main family adds OFS predicates with tableless wide SET terms. Run at the BASE, this pass COUNTS today's refusals (the K-1 population, expected > 0) as a recorded baseline, not a gate | the family runs; refusal and decline counts recorded per class (K35: floors in the script, sharing no source with the kit) | n/a (measures the base) | none |
| D1 | M | **THE DECISION**: the `findable` candidate column in `run_modes[]`; the decline row first in `fd_rows[]` with its fact and contract; P3's member rule reads "no tested run"; `kit_pres_picks`' `has_scan` guards. `MF_CLASS_V` moves; memfn.h text for `mf_link` (run span) and `mf_run_reply`; `decider_census.tsv` gains the row | `emit_sweep`: zero movers on today's corpus, every arm, both layers (G3). G2 presence family: every decline witness (`[a-z]{8}`, `cat|dog`, digits-only) comes back declined, never refused; refusals 0 on runs with a findable position | (p1) the `findable` column ignored (WHOLE takes `exact` 0, any position): a run whose least-mass position is wide refuses at define, so G2's refusal floor (0) reds. (p2) the decline row deleted: G2's decline witnesses refuse | S3005 (twin mass), S3006 (rank), S3008, S3012: REACH re-run, no re-aim expected (their sites keep findable-only runs) |
| D2 | L | **THE RENDERING**: the derived extent is R by the kit's flag; `c_run`'s pinned join stays inside the member's findable stretch (`run_len` 1 kept as a RUN term); `run_bytes` refuses a non-findable position; `a_mass_choose` excludes all of R but `rs`; ofsskip's `kit_set_test` for tableless SET terms (`ofs_fn_applies`, `verify_chain`, `table_params`); `run_part` and `wf_parts_prepare`'s check generalised (§2.1). Its DENY row in `options.def` (name the kit's, behavioural: e.g. `run-verify-wide`, D174): denied, the WHOLE and WINDOW stretch is the member's findable stretch (a `run_modes[]` stretch like `stretch_exact`), so wide positions are unverified filters and the part is today's one RUN term. That is the alpha OFF arm, and its extent is still the reply's | `emit_sweep` zero movers on today's corpus (G3), with ofsskip's admission counted separately (§7 Q3). G2 presence family on every target/level, both layers: C2 (EXTENT incl. 256-byte non-member probes), the occurrence oracle (`tests/memfn/occurrence_oracle.py`), the deny pass. `make test-memfn-g2`, `test-memfn-finder`, `test-axes` | (p3) a wide verified position rendered by its cube hull: C2's non-member probe reds. (p4) one range dropped from `kit_set_test` on the derived part: the occurrence oracle reds (an occurrence is lost). (p5) the pinned join's shape test deleted: `run_bytes`' guard refuses, so G2's refusal floor reds. (p6) the in-run filter back to `stretch` only: the derived part's stop leaves the scan, and the check in `wf_parts_prepare` refuses (G2 red) | S3007, S3011 (runcmp: kept, their runs findable-only), S3047 (second derived part: kept), S3012 (in-run filter: RE-AIMED to the widened exclusion), S285/S279 (RUN term length/offset: kept), S1104: REACH re-run on each |
| D3 | S | **THE MEASUREMENT'S FLOOR**: no new method (G4), so no new card. The `verify_cmp` card's census (span_cards §2.3, `kit-grid@3`, form `settest`) is re-run over the stage-3 corpus, so the settest classes the new sites use are counted. A class outside the measured set reads UNMEASURED (append-only version if a row is added) | the census lists every (form, cls) the stage-3 artifacts use; none silently priced | a census that drops the derived part's settest terms: its population floor reds | none |

**Order.** D0, then D1, then D2 (D2's checks need D1's findable scan); D3 rides D2 or follows it.
One kit branch, one landing with stage 3. D1 and D2 may land together; D1 alone is zero-mover and
safe to land first if stage 3 is not ready.

### 5.2 The G2 coverage the wide sets need

- **Generator** (D0; both layers, every level the U2 target list admits, default and
  `run-tie-left` levers, the deny arm). Per run position, a set drawn from a stratified
  member-count distribution: 1; 2 as a cube; 2 not a cube; 3-8; 9-32; 33-128; exactly 128. Each in
  shapes: one contiguous range; a union of ranges (`{80-89, B1-BF}`); scattered random members;
  the byte classes `\d`, hex, `[a-z]`, `\w`, `\s`; caseless pairs; UTF-8 lead and continuation
  sets. Run layouts: a wide position next to the scan, at either end of the extent, between two
  findable stretches (`ab\dcd`); runs with NO findable position (decline witnesses); joint
  supersets built as the per-position union of 2-4 literal branches (`cat|dog`); the request's
  witnesses (readiness §3) verbatim. Lengths 2..`MF_WSPAN_POS`.
- **Oracles**: the occurrence oracle (unchanged, written D27-blinded from span_runs_sheet §3.3) reads
  the STATED sets as the language. The kit's promise is per position, so a joint superset needs no
  oracle change. C2's classifier, read off the RENDERED text: per verified position the admitted
  bytes equal the stated set (every non-member rejected, every member admitted).
- **Floors** (K35, literals in the script): sites with >= 1 wide verified position; declines; wide
  positions never chosen as the scan (counted, must equal the wide-position count); deny-pass
  sites; per target. Each is a count of THIS family's records, never the kit's own `moved`.

### 5.3 The measurement card (memory `pcrec-new-method-needs-measurement-card`)

D2 adds no find, scan or skip form. The one verify method it uses on a new site is `kit_set_test`
(`verify_cmp`, form `settest`), which already has its card in `kit-grid@3`. D3 counts its new
classes. Each §6 candidate that is built adds its card in the same change.

## 6. Faster methods: candidates with triggers (not build; D77)

| # | candidate | trigger (the measurement that would start it) |
|---|---|---|
| C1 | scan a WIDE position with a set find (the kit's set-FIND walk or a table/class find), so a run with no findable position gets a pre-check | the stage-3 census counts runs declined for "no findable position" on corpus + bench, AND a bench G1 on those patterns shows that an engine-only artifact loses to a hand-built set-find prototype by more than noise |
| C2 | scan a NON-CUBE two-member position (`fn-pair` on any two bytes; the window family's B-pair already does this) | the census's declines whose best position is a non-cube pair (`cat\|dog`) are a counted population AND G1 shows a loss |
| C3 | several RUN terms per part (word compares of the findable stretches on both sides of a wide position) | `verify_cmp` shows per-byte compares of a side stretch cost more than `rc-words` by more than noise, on a counted population of stage-3 parts |
| C4 | `vrun` (SIMD) on a multi-term part: KA/KB plus the SET terms verified after | a SIMD-layer G1 on stage-3 wide runs shows a loss against `vrun` on the same run with the wide positions denied (D2's deny arm) |
| C5 | a covering prefilter (a cube hull or vector range test) ahead of the exact `settest`, counted as unverified | a SIMD measurement of the hull test against `settest` on the census's classes |
| C6 | a stated R label on window sites (`MF_SITE_ABI` event), so a wide R keeps its member and C-pin | the stage-3 census counts artifacts whose run-pinned prefilter is lost (`run_stated` 1 -> 0), AND G1 on them shows a loss |

## 7. Open questions (each with a leaning)

1. **K-2: keep R shape-identified?** Leaning: yes (§2.2). Both widenings move today's cover
   bytes. pcrec keeps the choice of what it states in R, and the reply's `run_stated` 0 is the
   stated decline. C6 waits for its trigger.
2. **The deny's name** (behavioural, D174): leaning `run-verify-wide` ("verify wide run
   positions"). The kit manager's call.
3. **Does ofsskip's tableless-set admission move today's OFS sites?** UNMEASURED. pcrec's OFS
   predicates come from the window family's legacy translation, where `offer_at` may leave
   `table_ref` 0. Today such a predicate is refused by `ofs_fn_applies` and goes to the generic
   row. Leaning: the general rule (a tableless set is tested by the kit's own membership test,
   everywhere), with D2's first `emit_sweep` deciding. If today's sites move, they become a
   declared population with G1 alpha at both layers, or the admission is scoped to the derived
   part and the scope is named as a special case to retire.
4. **The decline's admission on pcrec's side** (pcrec's, stated so it is not lost): a pre-check
   whose run is declined and whose members are untested renders nothing. Today `req_site_define`
   treats that as an internal error. Stage 3 names the `RX_REQ_WHY` value.
5. **Is the derived part re-deciding a second decision?** The window family decides the derived
   extent again and a loud check holds it equal to the reply (span_runs_sheet Goal 2's one
   decision). A direct translation of the reply into terms would delete the check and the
   in-run filter's role on the part. Leaning: NOT now (K38-1/3.0a routed the part through the
   family on purpose); it is noted as a simplification for the next restructure of
   `wf_parts_prepare`.

## 8. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: RELEVANT.** D2 adds per-candidate membership tests. Whether verifying a
   wide position pays (fewer engine entries) or costs (a compare per candidate on a hit-dense
   scan) depends on the regime. Hit-dense Greek/Cyrillic text with a scan on `{CE,CF}` is the
   sharp case: the run decision avoids it only where the art's byte rates say so. Linux,
   `taskset`-pinned, both layers. The deny is the alpha OFF arm. The official verdict is
   pcrec's G1 (its timing vs its own deny, population from a pcrec-side artifact diff).
2. **Independent control: RELEVANT.** C2 reads the RENDERED text, not the decision. The
   occurrence oracle is D27-written from the contract. `emit_sweep`'s zero-mover gate is
   pcrec's artifact diff (K35, never the kit's `moved`). Each plant in §5.1 names the check that
   reds, and each existing row is REACH-rerun.
3. **What moves when data is regenerated: RELEVANT.** The byte-rate payload decides the scan
   (`findable` positions only) and P3's window, so a rate regeneration can move a pick on a wide
   run. That is a pcrec abi event by its emitted bytes, as today. A UCD bump moves pcrec's sets
   (pcrec's). The `verify_cmp` card's regeneration moves no byte (no pricing reads it yet).

# part_d — the kit's answer to R-38 Part D: run positions of 1 to 128 members (design, rev 4)

**rev 4 (2026-11-12, lane pdrev4, opus):** applies the RULED narrow re-check review
`docs/dev/reviews/2026-11-12-r3-memfn-partd3.md` (FIX-NOW RDY-1..6 and FIX-2..9; the JOINT ruling
FIX-1: P8's retirement extends to `dominated`/`rdom` on non-cube runs, main's plan row
[SHADOW-TABLE]; DOC FIX-S2, FIX-S3). Each change is marked `[r3pd ID]`; every check a fix adds or
changes names its control (the plant or input that reds without it). §9 is re-stated whole as the
final list for main's stage-3 brief. Cites re-read at main `5d41c1f2d` (later than `a8ae73be0`):
`git diff --stat a8ae73be0 5d41c1f2d` over `memfn/`, `src/gen/`, `tests/memfn/`, `memfn/tests/`,
`tests/mech/`, `docs/spec/`, `scripts/emit_sweep.py` and `docs/design/memfn/` is empty; plan.md gained
[SHADOW-TABLE]. Code is cited by function, the spec and plan by section or [TAG].

**rev 3 (2026-11-12, lane pdrev3, opus):** applies the RULED re-check review
`docs/dev/reviews/2026-11-12-r2-memfn-partd2.md` (FIX-NOW P1-P19, P22, P23; DOC P20, P21; NOTED P24;
the decisions P3 a no-scan run is run-less in P2, P9 the scan-less body's own UNMEASURED card and
behavioural name, P15 D3's record `run_part_terms` with a G2 pre-landing floor, P8 `leads`/`rlead`
retired on non-cube runs (joint with main), P14 R by role scoped to a window site's alternative).
Each change is marked `[r2pd Pn]`. Cites re-read at main `a8ae73be0` (later than `a9fc6dbd8`):
nothing under `memfn/`, `src/gen/`, `tests/memfn/`, `memfn/tests/`, `tests/mech/`, `docs/spec/`,
`scripts/emit_sweep.py` or the census instruments moved since the base `35bee4da9` (`git diff
--stat` empty); `span_runs_sheet.md` moved only in §5's K38-3 row. D3 is now READY (§5.1).

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
| G4 | **No new method without its measurement card** (D77; memory `pcrec-new-method-needs-measurement-card`) | the owner, the kit | the build adds no find, scan or skip form; every per-candidate test is an existing carded form (`settest`, `rc-*`), and the ONE new form, the scan-less body `fn-every-pos`, carries its own card in the same change, visibly UNMEASURED (§5.3) `[r2pd P9]` |

**Non-goals.** Scanning a wide position (§6 C1). Proving exactness (Part C's ranges). Pricing. A
seam field that only today's shape test needs. pcrec-side code (stage 3's lane); the pcrec-side
FACTS stage 3 must state or read are §9's.

## 1. The request's facts, as the kit reads them

1. The run presence span (`pspans`, LAST, `nalt` 1, `nterm` 0) and R inside the window site's
   PARKED/RESEED statements carry positions of ANY 1..128-member byte set (`mf_wspan.set[j]`). The
   run span already admits any non-empty set (`pres_span0_clear`). The statement's LAYOUT does not
   change; the MEANING of a verify-NO span of two or more positions in a window site's alternative
   does (§2.2, `[r1pd F11]`; the presence site's run span is not R, `[r2pd P14]`).
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
   `rank_n` 0. `MF_NO_PRED` is 0xFF and `MF_MAX_TERM` 32, so NO reader may index
   `term[plan_hint]` on such a part: every reader of the scan is listed, with its guard, in the
   ofsskip paragraph below `[r2pd P2]`.
5. The RUN term's `(T, K)` comes from `run_bytes`, generalised to read positions through a set
   accessor (its two callers: `translate` and this function); it refuses (`kit_fail`) a position
   with no `(T, K)` spelling, so `(T, K)` stays a complete spelling of every RUN term (§2.3).
6. **ONE spelling accessor** `[r2pd P23]`. "This position has a `(T, K)` spelling" (one member, or
   a two-member cube) is today written, or would be, four times: §2.4 item 1's `findable` column,
   item 1's scan stretch, §2.2's verify-YES pinned span test, and `run_bytes`' refusal (item 5).
   The build writes ONE kit accessor (name the builder's; here `kit_pos_spelled`) and all four read
   it; `in_stretch` (the TIE table's first row) keeps its own meaning (a meet of one member or a
   cube inside R's stretch) and is not folded. One plant covers the four: the accessor answering
   "spelled" for a three-member set. **Its detectors** `[r3pd FIX-2]`: NOT `run_bytes`' refusal
   (p7's), which reads the same accessor and so cannot fire under the plant; the planted position
   becomes part of a RUN term whose `(T, K)` admits bytes outside its set (or misses a member), so
   **C2's classifier** reds at D2 (the rendered test's admitted bytes differ from the stated set),
   with the occurrence oracle as the second detector; at D1 the reply puts the scan on a three-member
   position, which D1's "the scan is never a wide position" floor reds only where such a position is
   the lightest: so F24's floor is STRATIFIED, with its own literal for sites where a position of
   THREE or more members is lighter than every findable one (> 0 at the base, D0), the plant's D1
   reach. pcrec's side has the same family for "the pre-check tests the run" (§9 item 2).
   **The rest of the spelling family** `[r3pd FIX-S2]` (DOC): `in_stretch` (above) and presence.c's
   `one_member` (P2's lead byte) also classify a position's members. Their general form is ONE
   accessor returning the position's class {one, cube, wide}; `kit_pos_spelled` is "not wide". The
   build may write the class accessor and read all six through it; unlock: C2's classifier becomes
   one row per class.

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
  candidate in `[pos, n - maxk)` running the verify chain, a new BODY row of ofsskip's `fn_rows[]`,
  named for what it does `[r2pd P9]` (D174): **`fn-every-pos`** ("verify every candidate position";
  never `walk`: card `walk` is `MF_FH_FIND` over `pf_walk` with a TABLE, and formhash.c's own entry
  comment says the tableless loop "is not the walk"). It has no deny: it is the only renderable body
  for a K66 proof (D158). Its card is its own, UNMEASURED (§5.3).

**The BODY slot's order, by FACT** `[r2pd P2, P9]`. `fn_rows[]`' BODY slot is today `fn-pair`
(`pair_holds`: `x->b >= 0`) then `fn-memchr` (`memchr_holds`: always, "the slot's floor").
`fn-every-pos` is the FIRST BODY row, and the three `holds` predicates become DISJOINT facts of
the walk's input, so the order is a fact and not a position: `fn-every-pos` holds iff no scan is
stated (`x->a < 0`); `fn-pair` iff a scan is stated and it is a cube (`x->a >= 0 && x->b >= 0`);
`fn-memchr` iff a scan is stated and it is one byte (`x->a >= 0 && x->b < 0`). A BODY with no row
holding is the walk's existing error. So a scan-less part can never reach `fn-pair` (rev 2's
placement "above `fn-memchr`" left it below `fn-pair`, which a zeroed `x.b` would have taken: a
pair body on byte 0, a wrong NOMATCH on a matching subject, review P2), and the order of the three
rows cannot move a pick. Witness (§2.4's table, row P2).

**Every reader of the scan on a derived part, with its guard** `[r2pd P2]`:
- `ofs_fn_scan` (ofsskip.c) reads `term[plan_hint]` unguarded. It gains the guard: where
  `plan_hint == MF_NO_PRED` it writes `k`, `a`, `b` = -1 (no scan), which is the fact
  `fn-every-pos` holds on and the two scan rows refuse.
- its callers, each reading -1 as "no scan": `fn_define` (the BODY walk's input `x`, above);
  `legend_at` and `legend` (the block's comment: "every position from `pos` is tested" in place of
  the scanned byte); precheck's `run_comment` (precheck's readers, below); `ofs_fn_serves` (computes `x`
  for the window family's B-pair; its caller `b_fn_holds` in window.c already returns 0 on
  `MF_NO_PRED` before calling it, and the B-pair never sees a derived part).
- `ofs_fn_applies` refuses `plan_hint >= nterm` before it reads `term[plan_hint]`; under the scope
  argument it admits `MF_NO_PRED` instead, skips the scan-term clauses, and counts every term as
  checked.
- **The libc note and include are the chosen BODY row's own.** `fn_define` today sets
  `MF_INC_STRING_H` and notes `memchr` for every body ("both bodies write `memchr(`"); a
  `fn-every-pos` body writes no `memchr`, so the note moves into each BODY row's text writer (the
  run compare's `memcmp` note stays the RUN term's). Otherwise the artifact's `_MEMFN_LIBC` stamp
  names a call the text never makes, and pcrec's libc census equality reds (review P2, SUSPECTED,
  made moot by the move).

**The scope, and who passes it** `[r2pd P21]`. The scope is ONE argument to `ofs_fn_applies`
("the derived run part"). Its THREE callers today: precheck's `run_part` passes it where the site
states a run presence span (under `wf_parts_check` such a site's FUNC part is always the derived
one); ofsskip's own OFS row (`ofsskip_applies`) and the window family's B-pair (`ofs_fn_serves`,
from `b_fn_holds`) pass "not derived" and keep today's refusals. (Rev 2 also named "the BODY walk"
and "G2's OFS and STMT families": neither calls `ofs_fn_applies`. G2's families are SITES that
reach it through the kit callers above; a site that states no run presence span never gets the
scope, so their tableless predicates keep today's refusals, which P12's two-sided pin holds, §5.1
D2.) The renderers' rules are
general; only the admission is scoped. **G3 holds by construction**: no today predicate reaches the
new admissions.
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

### 2.2 K-2: the window site's R, BY ROLE `[r1pd F11]`, scoped to a window site's alternative `[r2pd P14]`

**Today.** `run_shaped` identifies R by shape alone (the F-8 ruling: "two or more positions, each one
member or a cube"), in `merge` and in `wf_check` (at most one per alternative). pcrec states R in
`pf_window_of`, verify NO, grown over walk-proven positions.

**The ruling (joint, kit manager + main, 2026-11-12; plan [RUN-POS-SET] note, re-scoped by main for
P14).** R is identified by its ROLE: **any span of two or more positions that pcrec states verify
NO IN A WINDOW SITE'S ALTERNATIVE is R** `[r2pd P14]`. The run PRESENCE span (`req_pres_spans`, the
presence site's LAST span, stated `pcrec_memfn_wspan(sp, 0, whole_len, MF_VERIFY_NO)`, which the kit
REQUIRES verify NO) is a second multi-position verify-NO span pcrec states; it is NOT R: it lives on a
presence site, never in a window site's alternative, and never reaches `merge`. pcrec decides how
far R reaches (`pf_window_of` grows it over walk-proven positions, readiness memo §2.1, now by a
subset-of-set test with `pcrec_memfn_wpos_bits`); the kit never infers R from shape, and pcrec never
reads the kit's scan capability (D157). An `MF_SITE_ABI` meaning event inside S2's single landing.

**Why it moves no byte today** (review SEAM-2, enumeration re-verified; count corrected
`[r2pd P14]`): pcrec's statements are 8 `pcrec_memfn_wspan` calls; TWO of them state a
multi-position verify-NO span: R (`pf_window_of`, a window site's alternative, shape-only today)
and the run presence span (`req_pres_spans`, a presence site's span, not R by the scope above). The
one other verify-NO kind is a ONE-position walked span. `run_member` already treats a verify-NO R by EXACT_AROUND (member and pinned stretch exact
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
0 where R has no one-member position". `mf_wspan.verify`'s text gains "in a window site's
alternative, a verify-NO span of two or more positions IS the run R (at most one per alternative);
a presence site's run span is not R" `[r2pd P14]`.

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
   **Its facts** `[r2pd P20]`: OPTIONAL and `SF_RUN_NOSCAN`. In `fd_rows[]`' columns: `facts` =
   `SF_RUN_NOSCAN` (set on the run span only, so the row never holds on a member), `nofacts` 0; the
   need is its `FD_CT` contract's `CM(N_OPTIONAL)`, as P2's (there is no OPTIONAL fact bit:
   `SF_REQUIRED` is set from `need`, and P0 precedes the row on REQUIRED). No `nofacts`: P2 precedes
   it, so a proven run span never reaches it, and `SF_PROVEN` in `nofacts` would only duplicate
   first-match order.
   **P2 on a no-scan run** `[r2pd P3]`: where the run span carries `SF_RUN_NOSCAN` (known before P2,
   from the same run answer), P2 treats the run span as RUN-LESS: the dominance test is the set
   pick's (as on a site with no run: the lead is the set's pick, and `proof->run` is NOT required),
   and where it holds the run span is `proven_by` with every other span (P2's "every span, or
   none"). Reason: pcrec's `proof.run` is `run_verified`, set only on offset rows and only where an
   earlier ask TESTED the run, so on a run the kit cannot scan it is 0 on every route; requiring it
   made `dominated` unreachable on exactly the runs the decline serves, and `x.(?:cat|dog)` (today
   `_REQ_WHY "dominated"`, MEASURED this rev) would have gained a `memchr('x')` pre-check in front of
   a `memchr('x')` body (the double pass the dominated row exists to remove). A dominated no-scan
   run claims nothing about the run: dominance there means "the start search's proof already
   dismisses every start the set's pick would", which is the run-less meaning. On REQUIRED, P0
   precedes P2 (contracts `N_REQUIRED` vs `N_OPTIONAL`), so the K66 scan-less run is never dropped
   by this rule.
   **The row literal** `[r3pd FIX-8]` (every mandatory column of `fd_rows[]`; the id is the
   builder's, here `PD`; the basis is the kit's choice, `FB_DERIVED` as P0's, since the row follows
   from the reply contract and prices nothing):

       { "PD", FD_PRES, KN_P, SF_RUN_NOSCAN, 0, { { FL_NONE, NULL, 0, NULL, NULL } },
         FF_UNSTATED, FF_UNSTATED, { 0, 0, 0, 0 }, NULL, FB_DERIVED, "Part D",
         "a run with no findable position on an OPTIONAL route: declined, the run untested "
         "(part_d §2.4 item 2)",
         "none: derived from the reply contract (no find tests the run)", &ct_pd },
       FD_CT(ct_pd, "PD", use_none, KD_ALL, CM(N_OPTIONAL), MF_ANY, LY_ALL)

   Knowledge key `KN_P` only (findability reads no rate); link `{0, 0, 0, 0}` (verify 0, `proven_by`
   0); `opt` NULL (no deny, above); `step` the R-38 Part D unit; `FD_CT` kinds `KD_ALL` and layers
   `LY_ALL` as every PRES row. The FD record prints `basis=derived`, which `tests/memfn/rows.tsv`'s
   line for the row matches (D1's row obligations, §5.1). Control: `rows_check.py` reds a row whose
   printed basis or link differs from its `rows.tsv` line (the existing row check; the plant is the
   row's basis left `FB_UNSTATED`, which `mf_finder_rows`' self-check refuses).

3. **REQUIRED: no decline; P0 verifies the whole run SCAN-LESS** `[r1pd F4]`. A REQUIRED span's run
   keeps K66's linear no-match proof: P0's reply on a run with no findable position is
   `{has_scan 0, scan 0, ver_lo 0, ver_len n}` (the whole run verified at every candidate, no find),
   written as the P0 row's `no_scan` column in `fd_run_modes[]` (P0: the whole run, scan-less; P3,
   P9: unreachable, the decline row precedes them, a loud refusal if reached). The part renders by
   §2.1 item 4 and ofsskip's `fn-every-pos` body `[r2pd P9]`. Chosen over the alternative "pcrec prefers a run with a
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
   - `kit_pres_picks`: where the run has no scan (`SF_RUN_NOSCAN`), P4's `set_leads` is -1 (no run
     scan to compare, as with no run) and P2's `dominated` treats the run as absent: the set's pick
     leads and `proof->run` is not required `[r2pd P3]` (item 2's paragraph; rev 2 still required
     it, which made `dominated` unreachable on a decline). `rr.scan` is read only where `has_scan`
     is 1. memfn.h's `set_leads`/`dominated` text says both; pcrec's readers are
     `req_set_leads_applies` (through its lead reader, §9 item 5) and the pick shadow, whose
     `leads`/`rlead` records RETIRE on runs with a non-cube position (§9 item 6, `[r2pd P8]`), and
     so do its `dominated`/`rdom` records `[r3pd FIX-1]`: pcrec's `req_byte_dominated_by`
     (emit_dfa.c) still requires `run_verified` on a stated run, so after P3 the shadow's `rdom` is 0
     where the kit's `dominated` is 1 on every dominated no-scan run (`x.(?:cat|dog)`); following
     the kit would need its findability (D157) or the reply itself (K35), the bind P8 ruled on.

5. **The twin's landmark is the head member where the run is not tested** `[r1pd F1]`. The FIFTH's
   mass in `kit_pres_picks` takes its byte branch where `!rs || !ext->ver_len` (a declined run has
   `ext` = none). A scan-less P0 run keeps the run branch (its part ships). This is the kit half of
   F1; pcrec's half is §9 item 2.

**Witnesses for the answer-level and G1 findings** (each FAILS without its change; python3 `re`
oracle for the answers, re-run this rev; the stage-3 halves INFERRED, stage 3 being unbuilt). Each
names the ROUTE it takes today, measured by a single compile at this rev's tree: a witness decided
upstream of the changed code is inert `[r2pd P5]`. `[a-z]{8}.q`, `\d{3}-\d{4}` and
`x.(?:cat|dog)` are `_REQ_WHY "dominated"` today on the default route AND under
`--memfn=no-window-search` (MEASURED; the review's "the deny route reaches the decline" did not
reproduce for `\d{3}-\d{4}`), so F2 and F7 move to a PREFIXED shape whose pre-check is emitted today:

| finding | pattern, subject (today's route, MEASURED) | right answer | without the change | with it |
|---|---|---|---|---|
| F1 | `(a\|bc)[a-z]{8}.q`, `bcabcdefgh-q` (`_REQ_WHY "emitted"`, `_REQ_HANDOFF "11"`: ASSIGN, VM) | match (0,12) | declined `[a-z]{8}`, landmark `q`, K = the run's 2: the attempt restarts at 9, NOMATCH | landmark `q`, K = `q`'s own 11 (pcrec reads `pres[run].verify`; the twin's byte branch): match |
| F2 `[r2pd P5]` | `(a\|bc)[a-z]{8}.q`, `zz bcabcdefgh-q` (the same emitted route; rev 2's `[a-z]{8}.q` is dominated before any kit ask) | match (3,15) | `set_leads` -1, no led, `run >= 0` keeps head -1: `q` is REST, pcrec's "verify nothing" internal error (G2 green) | head `q`; G2's new `pres_layout_check` clause reds the old rule |
| F3 `[r2pd P3]` | `x.(?:cat\|dog)`, `x-dog` (today `_REQ_WHY "dominated"`, `_REQ_RUN "none"`); stage 3 states the run `{c,d}{a,o}{t,g}` and pcrec's REAL proof: `pres_proof.run` 0 (`run_verified` is set only where an earlier ask tested the run) | match (0,5) | rev 2's P2 requires `proof->run`: `dominated` 0, the decline row takes the run, `x` is verified: a `memchr('x')` pre-check in front of a `memchr('x')` body, `_REQ_WHY` moves to `emitted` (a speed and stamp mover, not an answer error) | P2 treats the no-scan run as run-less: the set pick `x` is dominated, every span `proven_by`, `_REQ_WHY "dominated"` kept, no pre-check |
| F4 | `(x?)([a-z]+)+eeeeeeee~#~#~#~#.[0-7]{32}\1` (`--features all`), `e` + 36 `a` + `~#~#~#~#x` + 32 `8` | no match | stage 3 ranks `[0-7]{32}` (160 bits) above the exact 128-bit run; declined: `steps` (exit 3). Today's half MEASURED: default `nomatch` in 0.00 s; `-fno-req-run` `steps` in 2.24 s | P0 verifies the whole wide run scan-less: `nomatch` |
| P2, P9 `[r2pd P2, P9]` | F4's pattern on a MATCHING subject: `a` + `eeeeeeee~#~#~#~#x` + 32 `0` (today `_ENGINE "vm"`, `_REQ_WHY "emitted"`, the run `eeeeeeee~#~#~#~#`, MEASURED: the VM attempt route, REQUIRED) | match (0,50) | rev 2: `ofs_fn_scan` reads `term[255]` (out of bounds); a guard that only zeroes `x` leaves `x.b` 0, so first-match `fn-pair` holds and renders a pair body on byte 0: no candidate is ever found, NOMATCH (wrong) | `ofs_fn_scan` writes -1s, only `fn-every-pos` holds (disjoint `holds` facts, §2.1), every candidate is verified: match (0,50) |
| F7 `[r2pd P5]` | `(a\|bc)\d{3}-\d{4}` on the deny arm (`--memfn=no-run-verify-wide`), `tel bc555-1234` (`_REQ_WHY "emitted"`, `_REQ_HANDOFF "5"` today, by default and under `--memfn=no-window-search`; the deny arm is D2's); the cube case `(a\|bc)\d[aA]\d`, `xbc1A2`, both arms (today NO pre-check: `_REQ_WHY "none"`, no necessary byte; its stage-3 route INFERRED, so G2's deny-pass layouts are its reaching control and the stage-3 lane records its route) | (4,14); (1,6) | the stretch is one position: the family path makes it a SET term ofsskip refuses (one member: `checked` 0; a cube: a 2-member SET scan): `test-axes` reds | one RUN term of `run_len` 1 at `-` (`fn-memchr`) / at `[aA]` (`fn-pair`) |

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
| `ofsskip.c` `ofs_fn_applies`, `verify_chain`, `table_params`, the BODY rows | a multi-member SET term needs pcrec's table; a scan always | YES | §2.1: the scoped admission; `fn-every-pos` FIRST with disjoint `holds` facts `[r2pd P2, P9]` |
| `ofsskip.c` `ofs_fn_scan` and its callers `fn_define`, `legend_at`, `legend`, `ofs_fn_serves`; precheck.c `run_comment`; `fn_define`'s libc note | `term[plan_hint]` unguarded; "every body writes `memchr`" | YES | §2.1: -1 where `MF_NO_PRED`; the libc note is the BODY row's own `[r2pd P2]` |
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
  positions in a window site's alternative now means R whatever its sets (§2.2; the presence
  site's run span is not R, `[r2pd P14]`); no layout move. The scoped ofsskip admissions
  (§2.1) are kit-side rendering admissions on a predicate the kit itself writes, not a statement
  meaning: no event of their own.
- **`MF_CLASS_V`: ONE event**, chosen, with three reasons `[r1pd F13]`:
  1. the decline row joins the PRES slot between P2 and P3, so `pres_row`/`pres_led`'s indices
     move for P3, P4 and P9, the precedent of `MF_CLASS_V` 6, 7 and 8 (no layout move). pcrec's
     reader resolves rows by id (`memfn_sites.c`, through `mf_finder_rows`), so it survives. The
     row ORDER's pin is `finder_check.py`'s `PRES_ROWS` and its table-size check (§5.1.1 D1)
     `[r2pd P13e]`; rev 2's "re-pinned in `decider_census.tsv`, `arm_fixtures --finder-rows` and
     S1122" named no pin of a row INDEX: those re-pin only where they name a row whose id or
     `pres_row` value they record (found by `git grep` of the sibling id at build);
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
  4. **The window site**: R is pcrec's verify-NO span of two or more positions in the alternative
     (`[r2pd P14]`: never the presence site's run span); `run_stated` 0 only
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
  **Sentences that read "a run is stated" as "the run is the landmark / is scanned"** `[r2pd P16]`,
  added to the same list: `match_api.md` §6.3.7¶11 (the LANDMARK is the run where `_REQ_RUN` is not
  "none": it becomes "where the run is TESTED"; a declined run's landmark is the head member);
  `tuning.md` §2.41¶1 and ¶7a (the hand-off's K is read from the tested run, else the head member);
  §2.28¶1 (`-fno-req-run`'s "the run's search": a run with a scan; a scan-less run is verified at
  every candidate; a declined run has none); §2.29¶4 (the admission's run case reads the tested
  run).

## 5. Build units

Kit units, on a kit branch cut from main after K38-2, landing in ONE merge with pcrec's stage 3.
Sizes as span_runs_sheet §5: S under a day of lane work, M a lane, L a lane plus a fix round.
Sabotage ids are taken at build time from the top of the free range. Every heavy run is a boxqueue
job; existing sabotages are checked with `REACH_ONLY=1`.

### 5.1 The units, with what each finding moved

| unit | size | content | check (passes AT THIS UNIT) | the plant that makes it fail | existing sabotages |
|---|---|---|---|---|---|
| D0 | M | **G2 FIRST.** `g2_pres_gen.c`, `g2_pres.h` (`run`/`mask` arrays) and `g2_pres_run.c` (`in_set`, `members(..., m[2])`, `filler`) take positions as SETS `[r1pd F16]`; the wide strata are an ADDED stream on their own rng, so today's 354 sites stay byte-identical `[r1pd F18]`; C2's classifier probes every non-member byte of every verified position, with a per-position breaker (§5.2) `[r1pd F17]`; G2 computes "no findable position" from its own sets `[r1pd F21]`. The G2 window family's R model (`g_run_shaped`, `two_runs`' fix rule) is NOT changed here (D2 changes it with R by role) `[r1pd F22]`. COUNTS at the base: K-1 refusals, with the K-1 message only; G2 window alternatives with a verify-NO multi-position span holding a wide position (they become R at D2); the OFS/STMT tableless multi-member SET terms (Q3's population, `[r1pd F9]`) | the family runs; any refusal OTHER than the K-1 message FAILS; the base counts recorded as literals (K35: the script's, sharing no source with the kit); the K-1 count becomes D2's must-be-0 population | n/a (measures the base) | none |
| D1 | M | **THE DECISION.** `findable` column in `run_modes[]`; the decline row after P2 with `SF_RUN_NOSCAN` and its contract; P0's scan-less `no_scan` column; the run span decided first; P3's member rule, the head rule and `pres_layout_check` read `trun` (+ its headless-layout clause); `kit_pres_picks`' `has_scan` guards, `set_leads`/`dominated` on a run with no scan, the twin's byte branch. `MF_CLASS_V` moves; memfn.h text for `mf_link` (run span), `mf_run_reply`, `mf_pres_picks`. A new row's obligations `[r1pd F15]`: `tests/memfn/rows.tsv` and `row_floors.tsv` lines, `ROWS_FLOOR` +1 in `run_rows.sh`, `memfn/docs/finder_history.md` entry, an `FD_CT` contract, G2's `G2P_NROUTE`/`route_of` gain the route, its reach class `pending-site:` while stage 3 is absent, `decider_census.tsv` row + `MEMBER_COUNT`, `RUN_CALLERS` unchanged (no second `kit_run_decide`) | `emit_sweep`: zero movers on today's corpus, every arm, both layers (G3). G2 presence family, REPLY level `[r1pd F14]`: the scan is never a wide position (count = wide-position count); each decline equals G2's own "no findable position" on an OPTIONAL non-dominated route, per site (F21); REQUIRED no-findable runs come back scan-less tested; a dominated decline witness keeps `proven_by` on every span (F3); a declined run with a member has a HEAD (F2); the twin's landmark on a declined handoff site is the byte's (F1). Refusals are NOT gated here: the K-1 count may only fall | (p1) the `findable` column ignored: the scan lands on a wide position on the floored sites where a wide position is lighter than every findable one (F24's floor, moved here: p6 is deleted with its piece) `[r1pd F24]`. (p2) the decline row deleted: G2's decline equality reds. (p3) "decline when the scan is a cube" (F21's plant): per-site equality reds. (p4) the head rule back to `run >= 0`: `pres_layout_check`'s new clause reds | S3005 (twin mass: re-aimed if the byte branch moves its witness), S3008, S1122 (re-pin `pres_row`), S1104: REACH re-run. `[r3pd FIX-6]`: REACH re-run on EVERY presence.c and finder.c row (not only these); S286 and S288 (the P2 lines P3 rewrites, `else if (rs && !proof->run) dom = 0;` among them) and S1098 re-aimed to the rewritten lines; S278 and S3045 (anchored on the `fd_run_modes[]` rows that gain the `findable`/`no_scan` columns) re-anchored; a NEW plant (p13) on P3's run-less branch: P2 keeps `rs && !proof->run` on a no-scan run, which reds FIX-4's floor (§5.1.1 D1) |
| D2 | L | **THE RENDERING.** The direct translation (§2.1: `run_part_terms` with its `MF_TRACE` print on the define path, the record D3 reads `[r3pd RDY-4]`, the shared ranking function, `run_bytes` over a set accessor); `derive_run_part`'s family call and `wf_parts_prepare`'s check deleted; precheck's `run_part`/`run_comment`/row-contract comments; ofsskip's SCOPED admissions (tableless SET terms through `kit_set_test`; the scan-less `fn-every-pos` BODY row, FIRST, with disjoint `holds` facts and its own card, its row-table obligations in §5.1.1 D2 `[r2pd P2, P9, P10]`); **R by role** (§2.2: `merge`, `wf_check`, the verify-YES pinned span's spelling test, memfn.h `mf_wspan.verify`/`run_stated` text, `MF_SITE_ABI` moves); G2's window R model `g_run_shaped` AND its reference `run_of` (g2_win_ref.c) to R by role, and `two_runs`' fix rule (a second verify-NO multi-position span becomes verify YES; a second SPELLED verify-YES span keeps today's three-member fix) `[r1pd F22]` `[r2pd P11]`. Its DENY row in `options.def` (D174 name, e.g. `run-verify-wide`): denied, EVERY mode's stretch is clipped to the maximal findable stretch holding the scan, a decision option read by every reader of the decision on the art (reply extent, the twin, the part) `[r1pd F6]`; identity today (every position findable). A scan-less P0 run is not clipped (nothing to clip around; the K66 proof is undeniable, D158) | `emit_sweep` zero movers on today's corpus, every arm INCLUDING `--memfn=no-run-verify-wide` (G3, F6). G2 presence family on every target/level, both layers: refusals 0 (D0's K-1 population, `[r1pd F14]`), C2 (256-byte non-member probes), the occurrence oracle (`tests/memfn/occurrence_oracle.py`), the deny pass with its one-position-stretch layouts and a deny-arm refusal floor of 0 (F7). G2 window family: R-by-role alternatives (member exact, pinned stretch exact). `make test-memfn-g2`, `test-memfn-finder`, `test-axes` | (p5) a wide verified position rendered by its cube hull: C2 reds. (p6') one range dropped from `kit_set_test` in `verify_chain`: the occurrence oracle reds. (p7) the direct translation's stretch rule widened past a wide position: `run_bytes`' refusal reds G2's refusal floor. (p8) `run_shaped` restored for verify-NO spans: the G2 window family's wide-R alternatives lose their member (and the stage-3 `xy/users\d+` witness loses `run-pinned`). (p9) the scope dropped from `ofs_fn_applies`: G2's two-sided pin (OFS/STMT sites rendered by ofsskip with a tableless multi-member SET term or no scan: exactly 0) reds `[r2pd P12]` (rev 2's `emit_sweep`/`FORM_FLOORS` cannot: pcrec's population is 0 by C7's premise, and `FORM_FLOORS` are one-sided minimums). (p10) `fn-every-pos` placed after `fn-pair` with `pair_holds` left as `x->b >= 0` and `ofs_fn_scan` zeroing `x`: the P2/P9 witness layout (G2's "scan-less REQUIRED runs on a MATCHING subject" floor) answers NOMATCH and the occurrence oracle reds `[r2pd P2]` | S3006 (rank: re-targeted to the shared ranking function), S3012 (in-run filter: its detector, the derived part's refusal, is deleted with the family route; RE-AIM to a G2 window witness of a verify-YES pinned span under `run-tie-left`, or retire with that role if none detects it, decided by REACH), S3047 (second derived part, `wf_parts_check`: kept), S3007, S3011, S285, S279 (runcmp/ofsskip: kept, RUN terms spelled-only), S1104: REACH re-run on every window.c, ofsskip.c and precheck.c row; a row whose only reacher was the derived part's family route is re-aimed or its reach class re-stated (`rows_check.py`) |
| D3 | M (was S) | **THE MEASUREMENT'S FLOOR** `[r2pd P9, P15]`. One new form, `fn-every-pos`, whose card D2 adds (§5.3); D3 adds no card. THE RECORD: D2's `run_part_terms` prints, in the trace build (`MF_TRACE`), ONE line per derived part, on the DEFINE path only `[r3pd RDY-2]`: inside `wf_parts_prepare` where `quiet` is 0, after the direct translation writes the terms (the define-time query `ask_sel` walks with `quiet` 1 and writes no trace record, compose.c's house rule, so pcrec's `mf_ask` and the shadow ask print nothing): `MFTRACE run_part_terms art=A site=S part=I hint=H terms=OFF:KIND:VAL,...` (KIND `RUN` with VAL `run_len`, or `SET` with VAL the 32-byte set in hex; `hint` the RUN term's index or `-` scan-less). The print is D2's (listed in its cell, `[r3pd RDY-4]`); D3 writes the parser and the checks. **The production collector** `[r3pd RDY-1]`: `docs/dev/lanes/r33_sim/collect.py`'s `parse` gathers non-REACH `MFTRACE` lines, but `summarize` keeps only `END` (phase define/run), `FDROUTE` and `WPATH`, so the record is DROPPED today; D3 changes `summarize` to keep each `run_part_terms` record raw (a `parts` list beside `ends`), re-collects the sweep, and re-pins the goldens it moves (RDY-6's list). **The census never saw a derived part** `[r3pd RDY-3]`: r33_sim's `probe.c` writes a part's `alts` only `if (p->nalt)`, and a derived part is `nalt` 0 in the host's preds, so `census0.py`'s `units()` and `vcls.py` have never had a unit for it; D3 adds a NEW population branch (a `deleg:runpart` unit per record), it replaces nothing. The census's ONE parser of the record serves `vcls.py`'s population and `census0.py forecast`'s `class_measure`; r33_sim's `sim.py` (`today_method`, units by `alts` as census0's) skips a derived part the same way; it was not traced by the review, and the build reads it before calling the list complete. From each record the census counts: every multi-member `SET` term as (`settest`, `settest_cls(members)`); the `RUN` term as (`rc-*`, its row's class); a scan-less part as (`every-pos`, `-`). `settest`'s classes get a bound: `c1`, `c2`, `cn` = 3 to 7 compares (the measured `\w` instance), above 7 `cn+` UNMEASURED (or `lower-bound`), never priced by the 7-compare row `[r1pd F20]`. **Readers and goldens** `[r1pd F19]` `[r3pd RDY-6]`: readers `docs/design/memfn/span_cards/slot/vcls.py`, `docs/design/memfn/span_pick/census0.py`, `slot/link.py` (prices a class by its majority shape), `slot/plan.py` (plans TIMED cells from `vcls.out`: it does NOT plan `cn+`, an UNMEASURED class is listed and never scheduled), `slot/est.py` (regenerates `vcls.out`); goldens `vcls.out`, `census0_cards.out` (its data lines byte-equal to `vcls.out`'s) and `census0.out`. `settest_cls` exists twice (`vcls.py` and `census0.py`): both copies change in ONE commit, and the byte-equality of `census0_cards.out`'s data lines with `vcls.out`'s is the control (plant: one copy's `cn` bound changed alone: the two goldens differ) | THE CHECK, its POPULATION and FLOOR (pre-landing, on the kit branch): the trace-build G2 presence family (its wide strata, every target) is run with its `run_part_terms` records captured, and the census's parser counts them. **The join** `[r3pd RDY-4]`: the record's `art=` is the kit-internal trace id (1-3 arts per G2 site), so the G2 driver prints `G2SITE id=N` after each site's define in the trace build, and every record between two `G2SITE` lines is site N's. **The population** `[r3pd RDY-2]`: sites whose define CHOSE ofsskip's FUNC row for the derived part (read from the same define's `END`/`FDROUTE` records); G2's generic-pass sites (`forms == generic`, which C2's classifier skips) are counted SEPARATELY (records and G2 sites both, a reported line, outside the equality), so a correct build's generic-pass records cannot red it. Per site in the population, the census's count of unspelled `SET` terms (members not one byte and not a cube) EQUALS G2's own count of that site's positions inside C2's MEASURED extent (EXTENT's probe, reading the rendered text) whose set G2 knows from its own generator to be unspelled; and the census's `every-pos` count equals G2's own count of scan-less REQUIRED runs it rendered. Both totals are at least LITERAL floors in the D3 script, **recorded at D3's first green run** `[r3pd RDY-4]` (K35: G2's counts come from its own sets and the text C2 measured, sharing no source with the trace record). **The production path** `[r3pd RDY-1]`: in the re-collected sweep (`collect.py`, kit branch), every site whose ARTIFACT stamps a run (`_REQ_RUN` other than `none`, read from pcrec's emitted text) carries exactly one `run_part_terms` record; a count of 0 records with a non-zero stamped count reds. The artifact's art is the compile's LAST art (collect.py's `arts`): a compound walk's trial parts and a failed attempt begin earlier arts whose defines print their own records, counted and never joined (lane partdfix: corpus c01877 holds two records, one on a declined split part). AT THE JOINT LANDING the pcrec-artifact floor is ARMED `[r3pd RDY-5]`: the cell is `emit_sweep`'s `DIFFER_PINS` entry for `--memfn=no-run-verify-wide` at the landing (its count of DISTINCT corpus patterns whose artifact differs from the default arm, per (base, flag, stream)); the census quantity is, over `collect.py --sources corpus` at the same base and stream, the count of distinct patterns with at least one `run_part_terms` record holding an unspelled `SET` term inside the extent; the check is census >= movers, a literal raised in the landing commit (0 on the kit branch). Why >=: the deny clips every extent to the findable stretch and is the identity where every position is findable (§5.1 D2), so a pattern moves under the deny only if its part holds an unspelled verified position, which prints such a record; a pattern with such a record may still not move (two arms rendering equal text), so equality is not claimed (INFERRED direction, the review's) | (p11) the census's parser skips `SET` terms of `run_part_terms` records (rev 2's "drops the derived parts' settest terms"): census unspelled count 0, G2's count > 0 on the witness below: the per-site equality reds. (p12) `run_part_terms` not printed for a scan-less part: the `every-pos` equality reds. (p14) `summarize` drops the record again `[r3pd RDY-1]`: the production-path check reds (0 records against the stamped count) while p11/p12's G2-fed checks stay green, which is why both feeds are checked. (p15) the record printed on the quiet path too `[r3pd RDY-2]`: G2 asks every site with `mf_ask` before its define (`g2_pres_gen.c`), so wherever the asked site carries the derived part a quiet print doubles that site's records and the per-site equality reds; its reach (that the ask's site carries the part) is the build's REACH run to confirm, and if it does not reach, the plant is re-aimed to a G2 fixture that asks a site with the part attached | none (D3's ids taken at build) |

### 5.1.1 Rev 3's per-unit additions (the table's cells plus these)

**D0** (text fixes only):
- **The rate rule's SCOPE** `[r3pd FIX-3]`. P18's rule below applies ONLY to positions of THREE or
  more members, and only on the wide stream (its own rng). Today there is one `rnd(200000)` per
  position, on `run[j]` only; rating a cube's two members would take a second draw on the MAIN rng
  (shifting every later site) and make the RATE_TIES cube mass exactly 50000, tying one-member
  positions. So positions of one or two members (a cube or not), on either stream, keep today's one
  draw on `run[j]` (the scope the review proposed: 3+ members).
  **Byte identity of today's sites is a D0 CHECK**, not a claim: the sha-256 of the generated site
  file for today's stream (the 354 sites, `g2_pres_gen.c`'s output at the base, before D0's
  change) is a literal in `run_g2_pres.sh`, and D0's generator must reproduce it. Control: the plant
  "P18 applied to cubes too" changes the main rng's draw count and reds the hash.
- **The rate rule for a SET position** `[r2pd P18]`. `gen_rates` rates every MEMBER of each run
  position (of three or more members, above): RATE_SKEW draws each member of a position of `|S|` members from `rnd(200000 / |S|)`
  (so a position's summed mass is in a one-member position's range, and a wide position is lighter
  than every findable one on a counted share of sites); RATE_TIES gives each member `50000 / |S|`
  (the summed masses tie, the TIE rows' case); RATE_UNIFORM and RATE_FIXED unchanged. The other
  `run[]`/`mask[]` readers move with it: the scan's lead byte in the pick model (only where the
  scan position has one member, as today's `mask == 0xFF` test), the member draw that copies a run
  byte (a member of a random position's set), the repro print (each position's set in hex) and
  `g2_pres_run.c`'s filler (a member of a random position's set). **F24's count** (sites on rated
  arts where a wide position is lighter than every findable one) is recorded at the base and must be
  > 0 there, or p1 (D1) has no reach.
- **The base counts split by verify** `[r2pd P11]`: G2 window alternatives with a multi-position
  span holding a wide position, counted verify NO (they become R at D2) and verify YES (they stay
  C-yes) separately.
- **The second moved window population** `[r3pd FIX-9]`: alternatives that state a SPELLED
  verify-NO multi-position span (R) AND a spelled verify-YES multi-position span. Today
  `two_runs` sees two R-shaped spans and mutates one; from D2 (R by role) the verify-YES span is no
  longer R and is left intact, which puts the kit on a path (R the member, the YES span verified by
  C-yes) no check has seen. The population exists in `g2_win_gen.c` (FAM_MASS and FAM_REPORT draw
  both verify values); D0 COUNTS it at the base (as generated, before `two_runs`), a literal, and
  D2 floors it (§5.1.1 D2).
- **Floors armed AT D0** (the rest arm later, below): sites stating >= 1 wide position, "no
  background" sites, F24's count and its stratum of positions with THREE or more members
  `[r3pd FIX-2]`, per target, the K-1 refusal count (the base, any other message FAILS), and the
  site-file hash (above).

**D1**:
- **P7's message move** `[r2pd P7]`. `derive_run_part`'s refusal `!rr->has_scan || !rr->ver_len`
  relaxes at D1 to `!rr->ver_len`, so P0's new scan-less reply (`has_scan` 0, `ver_len` > 0) falls
  through to the family path and refuses under the K-1 message ("the derived run part's find is not
  at the run reply's scan position"); D0's "any other message FAILS" gate stays true at D1, and the
  landing condition "K-1 count at most D0's base" cannot be met by a message move. D2 deletes the
  function.
- **G2's decline branch** `[r2pd P6]`. The presence family's `if (!tested) { ... return; }` is
  SPLIT: an untested link by P2 (proven) keeps today's branch (C2's third clause: a laid-out run part
  must be refused); an untested link by the DECLINE lays the site out WITHOUT a run part (members
  only, the head by the kit's links), renders it and oracle-checks it, and still asserts C2's third
  clause on the declined link. The layout's head need reads `trun`, not `run >= 0` (P1's rule on
  G2's side). `g_p2_untested` counts the P2 route only (the decline is its own route in
  `G2P_NROUTE`/`route_of`).
- **Row obligations the rev 2 list missed** `[r2pd P13a]`: `tests/memfn/finder_check.py`'s
  `PRES_ROWS` gains the decline row's id between P2 and P3 (its table-size check, `FIND_ROWS` +
  `PRES_ROWS`, moves with it); `B3B_PRES` gains the decline fixture (a declined run with one
  verified member: link verify 0, `proven_by` 0, `pres_row[run]` the decline). Found by `git grep`
  of the sibling id `P3` over `tests/`, `memfn/tests/`, `scripts/`, `tests/mech/` (the review's
  lesson 3); any further file naming `P3` is an obligation the build lists.
- **memfn.h** `[r2pd P19]`: `mf_link`'s MEMBER text ("tested iff it is chosen and no run is stated")
  and ORDER text, and `mf_pres_picks`' `dominated` text ("byte where no run is stated"), read "no
  run is TESTED" / "no run with a scan" as §2.4 items 2 and 4 decide; the D27 author reads these.
- **Floors armed AT D1** (reply level) `[r2pd P22]`: declines equal per site to G2's own
  computation; declines WITH a verified member (p4's reach: the head rule); declines on ASSIGN sites
  (F1's twin check's reach); scan-less REQUIRED replies; wide positions never the scan; dominated
  no-scan sites with every span `proven_by` (P3).
- **P3's floor on pcrec's real proof** `[r3pd FIX-4]`. Today every G2 P2 site states
  `pres_proof = {lead, 0, 1, 1}` (`run` 1); under that proof the rev-2 rule (`proof->run` required)
  and P3's rule agree, so reverting P3 keeps the floor's count and the floor cannot red. G2 states
  `run` 0 (pcrec's real proof: `run_verified` is never set on a run the kit cannot scan) on its
  no-findable-position sites, and the floor "dominated no-scan sites with every span `proven_by`"
  counts ONLY those `run` 0 sites. Control: plant p13 (P2 keeps `rs && !proof->run` on a no-scan
  run) makes `dominated` 0 on every such site: the floor reds. Sites with a findable position keep
  today's `run` 1 proof (their count is unchanged).
- **The decline's own G2 counters** `[r3pd FIX-7]` (P6 split the untested counter; the refused
  counter stayed shared). `g_p2_refused++` is route-unconditional today, so decline-route refusals
  would satisfy `FLOOR_P2_REFUSED=70`. Each route gets its own pair: `g_p2_untested`/`g_p2_refused`
  count route P2 only; `g_dec_untested`/`g_dec_refused` count the decline route, with a floor of their
  own (`FLOOR_DEC_REFUSED`, recorded at D1's first green run); and the script asserts
  `p2_untested == p2_refused` (every P2 untested link's laid-out run part is refused). Control:
  restoring the route-unconditional increment makes `p2_refused` exceed `p2_untested` on any run
  with a decline: the equality reds. (FIX-S4's general form, one counter array indexed by
  `route_of`, is NOTED; the build may write it instead.)

**D2**:
- **`fn-every-pos`'s row obligations** `[r2pd P10]`. rows_check exempts only `fd` rows from a
  fixture witness, so the `fn` row takes an `arm_fixtures` site: a REQUIRED all-wide run (scan-less,
  `fn-every-pos`) with its CONTROL fixture, the same run with one findable position (`fn-memchr`);
  `FIXTURE_FLOOR` in `run_rows.sh` +2; `rows.tsv`/`row_floors.tsv` lines; `ROWS_FLOOR` +1; its
  `gate_contract` (the derived part's facts: tableless SET terms, no scan).
- **Its card** `[r2pd P9]` (§5.3): a formhash.c entry (id `every-pos`) and its card row,
  UNMEASURED; `finder_check.py`'s `CARD_FORMDEP_COUNT` +1. The instance's construction is §5.3's
  `[r3pd FIX-5]` (a fifth site shape, two SET terms minimum, the BODY row asserted).
- **The second moved window population's floor** `[r3pd FIX-9]`: chosen alternatives with R and a
  spelled verify-YES span, R the member (D0's count, §5.1.1 D0), a literal > 0 recorded at D2's first
  green run, checked against `run_of`'s reference decision. Control: plant p16, `merge` taking the
  verify-YES span as `m->run` (R's role lost to the YES span): the member is no longer R's, DECIDE
  reds against the reference on that population, and the floor's "R the member" count falls to 0.
- **Pins the shared ranking function moves** `[r2pd P13b]`: `decider_census.tsv`'s
  `translate:run-rank` row (its caller becomes the shared function, called from `translate` and
  `run_part_terms`), `decider_census.py`'s `RUN_CALLERS` (exact) and `MEMBER_COUNT`, S3006's anchor.
- **The deny's sweep cells** `[r2pd P13c]`: the new deny arm needs `emit_sweep` `ASSERT_ZERO` cells
  (zero movers today); at the joint landing they become `DIFFER_PINS` with a floor and a stage-3
  manifest (else the sweep prints "NO DIFFER FLOOR PINNED" for an arm that cannot fail).
- **R by role's pins** `[r2pd P13d]`: S1409's anchor in `run_g2_win.sh` is the `wf_check` message
  §2.2 rewrites (re-anchor it to the new text); the verify-YES pinned span's uniqueness rule ("at
  most one such span per alternative") gets its own plant (the rule dropped: G2's window family
  states two spelled verify-YES spans, which `two_runs` keeps fixing, so the plant is a fixture of
  two such spans that `wf_check` must refuse). The deny's carrier is `kit_run_opts_of` (the option
  every reader of the decision reads, §5.1 D2); if it carries the deny, S3009 re-anchors (SUSPECTED;
  REACH decides).
- **G2's window family** `[r2pd P11]`: `run_of` (the REFERENCE) moves with `g_run_shaped` (the
  generator) in the same unit, else the correct build reds DECIDE and p8 (`run_shaped` restored)
  agrees with an unchanged reference and stays green. New floor: chosen wide-R alternatives whose
  member is an exact position (p8's reach).
- **Floors armed AT D2**: sites with >= 1 wide VERIFIED position rendered; declined sites rendered
  and oracle-checked, and declined sites with no verified member: no pre-check `[r2pd P6]`;
  scan-less REQUIRED runs on a MATCHING subject `[r2pd P2]`; one-position stretches and deny-pass
  sites on the deny arm; chosen wide-R alternatives with an exact member `[r2pd P11]`; R plus a
  spelled verify-YES span with R the member `[r3pd FIX-9]`; and the
  TWO-SIDED pin `[r2pd P12]`: OFS/STMT sites rendered by ofsskip with a tableless multi-member SET
  term or no scan, EXACTLY 0 while the scope stands (C7's retirement re-pins it).

**D3, READY** `[r2pd P15]`. Its check, population, floor and plants are the table's D3 row. The
check can red, by reasoning on a named witness: G2's layout "a wide position between two findable
stretches", `ab\dcd` on an OPTIONAL route with the scan on `a`. The reply's extent is the whole
run; `run_part_terms` writes `RUN ab` at 0 (`plan_hint` 0), `SET {0-9}` at 2, `SET {c}` at 3,
`SET {d}` at 4 (each extent position outside the scan stretch is its own SET term, §2.1 item 2), and
prints that record. C2 reads the rendered text: position 2 admits exactly `0-9`; G2's own sets say
`{0-9}` is unspelled (10 members), so G2's count for the site is 1. The census, parsing the record,
counts one unspelled SET term (`settest`, `c2`: one inner range, two compares); the equality holds.
Under p11 (the parser skips SET terms) the census counts 0 against G2's 1: RED. Without D3's check
nothing reds under p11: the census has never had a unit for a derived part (`probe.c` writes no
`alts` for a `nalt` 0 part, `[r3pd RDY-3]`), so the card's forecast would simply not see the site,
silently (the gap F19 named). G2's count of 1 is joined to the site by its `G2SITE` line and read
from C2's MEASURED extent `[r3pd RDY-4]`; the site's define chose ofsskip's FUNC row, so it is in the
population `[r3pd RDY-2]`. A scan-less site (G2's REQUIRED all-wide
run, e.g. `\d\d\d`) prints `hint=-` and counts once as `every-pos` against G2's own scan-less
count; p12 reds that equality the same way.

**Order.** D0, then D1, then D2, then D3. **D1 lands alone only with its own reply-level check green
and the K-1 refusal count at most D0's base** (D1 changes the scan's candidates and adds the decline,
neither of which renders a wide extent); every stage-3 population needs D2, so D1 and D2 land together
whenever stage 3 lands `[r1pd F14]`. One kit branch, one landing with stage 3.

**Readiness after rev 3** (the r2 review's per-unit verdicts, and what moved them):
- **D0: READY.** P18 (the SET rate rule, the other `run[]`/`mask[]` readers, F24's count > 0 at
  the base), P11 (base count split by verify), the floors armed at D0 named (§5.1.1).
- **D1: READY.** P1 (§9 item 2: `gate_need`), P3 (P2 run-less on a no-scan run, its witness), P4
  (§9 item 5: the lead reader), P5 (witness routes), P6 (G2's decline branch), P7 (the message
  move), P13a (finder_check), P19 (memfn.h), P20 (the row's facts), P22 (floors).
- **D2: READY.** P2 (`fn-every-pos` first by fact, every scan reader guarded, the libc note), P9
  (its card and name), P10 (its fixture pair), P11 (`run_of`, `two_runs`), P12 (the two-sided pin),
  P13b-d (pins), P14 (R scoped), P21 (the scope's callers), P23 (one spelling accessor).
- **D3: READY** (was NOT READY). P15: the record (`run_part_terms`), the pre-landing population and
  floor (G2's rendered wide sites), the plant that reds at D3 on the kit branch (shown on `ab\dcd`,
  §5.1.1), and the pcrec-artifact floor armed at the joint landing. P9: the census counts the new
  form.
- **pcrec side** (stage 3's lane, not a kit unit): P1, P4, P8, P16, P17 are §9's facts.

**Readiness after rev 4** (the r3 review's verdict: READY WITH LISTED TEXT FIXES, all applied):
- **D0: READY.** FIX-3 (P18 scoped to 3+ members on the wide stream; the site-file hash check),
  FIX-9 (the second moved window population counted), FIX-2 (F24's 3+ stratum floor).
- **D1: READY.** FIX-4 (G2 states `run` 0 on no-findable sites; plant p13), FIX-6 (REACH on every
  presence.c/finder.c row; S286/S288/S1098 re-aimed; S278/S3045 re-anchored), FIX-7 (the decline's
  own counters, `p2_untested == p2_refused`), FIX-8 (the row literal, §2.4 item 2).
- **D2: READY.** FIX-5 (the `every-pos` instance: fifth shape, two SET terms, BODY row asserted,
  fold rule), FIX-9 (floor and plant p16), FIX-2 (P23's detectors are C2 and the occurrence oracle),
  RDY-4 (the print listed in D2).
- **D3: READY.** RDY-1 (`collect.py`'s `summarize` keeps the record; production-path check, p14),
  RDY-2 (define-path print; the population by chosen row; generic-pass counted apart; p15), RDY-3
  (a new population branch), RDY-4 (`G2SITE` join, C2's measured extent, floors at D3's first green
  run), RDY-5 (the `DIFFER_PINS` cell and the census quantity, census >= movers), RDY-6 (readers,
  goldens, both `settest_cls` copies, `plan.py` does not plan `cn+`).
- **pcrec side**: FIX-1 (the shadow's `dominated`/`rdom` retire on non-cube runs) joins §9.

**The D27 author (ruled YES, at build).** A spec-first author in a D27 cell (`scripts/mk_d27_cell.sh`),
denied `src/`, `tests/`, `memfn/src/` and `memfn/tests/`, writes decline and R-by-role witnesses from
the CONTRACT TEXT only (this §4, memfn.h's new `mf_link`/`mf_run_reply`/`mf_pres_picks`/`run_stated`/
`mf_wspan.verify` text, `match_api.md` §6.3.7's rows): handoff routes (F1), a member head (F2),
dominated sites (F3), REQUIRED routes (F4), the deny arm's one-position stretch (F7), a wide R that
keeps `run-pinned`. Answers oracle-verified (python3 `re`; libpcre2 where it applies). The witnesses
land with the joint stage-3 merge. **Caveat the author inherits** `[r2pd P5]`: a witness must reach
the pre-check on its route; unprefixed `[a-z]{8}.q`, `\d{3}-\d{4}`, `\d[aA]\d` are dominated or
pre-check-free today (§2.4's table), so the author is given §2.4's prefixed shapes and records, per
witness, the `_REQ_WHY` and `_REQ_HANDOFF` its compile shows; a witness with `_REQ_WHY` other than
`emitted` is inert for F1, F2, F7 and is re-shaped, not counted.

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
  stretches on the deny arm (F7); deny-pass sites; "no background" sites; per target. Rev 3 adds
  `[r2pd P2, P6, P11, P12, P22]`: scan-less REQUIRED runs on a MATCHING subject; declines with a
  verified member; declines on ASSIGN sites; declined sites rendered and oracle-checked; declined
  sites with no verified member and no pre-check; chosen wide-R alternatives with an exact member;
  the two-sided pin (tableless or scan-less OFS/STMT sites rendered by ofsskip: exactly 0). Which
  unit arms which floor: §5.1.1.
- **The window family** (D2): `g_run_shaped` (generator) AND `run_of` (reference, g2_win_ref.c)
  become R by role (verify NO, two or more positions) plus the verify-YES pinned span's spelling
  rule `[r2pd P11]`; `two_runs`' fix turns every verify-NO multi-position span after an
  alternative's first into verify YES (rev 1's three-member fix would now make a second R), THEN
  keeps today's three-member fix for every SPELLED verify-YES multi-position span after the first
  (the pinned span is unique per alternative, and the first step can create a second one). D0's
  base count of wide verify-NO spans is that family's moved population, by design.

### 5.3 The measurement cards (memory `pcrec-new-method-needs-measurement-card`)

D2 adds no find, scan or skip form. The per-candidate tests on new sites are `kit_set_test`
(`verify_cmp`, form `settest`, card in `kit-grid@3`, its classes bounded by D3) and the runcmp
rows. **The scan-less body is a NEW form with its OWN card** `[r2pd P9]`: rev 2 called it the
`walk` loop, but card `walk` measures `pf_walk` over a TABLE (`MF_FH_FIND`), and formhash.c says
the tableless loop "is not the walk". D2 adds, in the same change: a formhash.c entry, id
`every-pos`, and a card row. **Its instance, constructible** `[r3pd FIX-5]` (a small kit design
step): formhash.c's four shapes (`MF_FH_FIND`, `MF_FH_WINDOW`, `MF_FH_SETTEST`, `MF_FH_RUNCMP`)
cannot build an ALL_PRESENT site with a derived FUNC part, so the entry takes a FIFTH shape (name
the builder's; here `MF_FH_RUNPART`): an ALL_PRESENT site whose only span is a REQUIRED run presence
span of TWO wide positions (`{0-9}{0-9}`, no member), which the kit's own selection takes through
P0's scan-less reply and precheck's `run_part` to ofsskip's FUNC body. TWO SET terms is the minimum,
not one: a run presence span has 2..`MF_WSPAN_POS` positions (`pres_run_check`), and scan-less
means every extent position is a term. **The row source**: `fh_render` asserts the site's ARM id
(for a presence site, `precheck`), not the fn walk's BODY row, so the entry gains a second asserted
row, the BODY row the define chose (`fn-every-pos`), read from the define's own record; an instance
reaching another BODY row is REFUSED (-1), as today's rule for an arm. **On a fold**: if the
rendered text hashes equal to an existing id's (the `walk-set` precedent in formhash.c's entry
comment, "the hash decides"), `every-pos` is not an id: no card row is added, the D2 report records
the fold, and D3 counts scan-less parts under the id it folds into; if it folds into the tableless
generic loop, which has no id, the entry is refused and the build stops for a kit ruling (a form no
card can name). The card row sits in `memfn/data/cards/kit-grid.tsv` at the next
`kit-grid` version (a new version: committed rows never change), one quantity in `walkbytes` over
`form` with `deps` `kit:form.every-pos`, its header saying **UNMEASURED: no set holds a
`kit.*.every-pos` row and no box has run this card; every reader skips an absent key** (the
`kit-kernels@1` precedent); `CARD_FORMDEP_COUNT` +1. Nothing prices it (no pricing reads cards
yet), so UNMEASURED moves no byte. D3 counts every class the stage-3 artifacts use, `every-pos`
included. Each §6 candidate that is built adds its card in the same change.

## 6. Faster methods and retirements: candidates with triggers (not build; D77)

| # | candidate | trigger (the measurement that would start it) |
|---|---|---|
| C1 | scan a WIDE position with a set find (the set-FIND walk or a table/class find), so a declined run gets a pre-check and a scan-less P0 run a find | the stage-3 census counts declined and scan-less runs on corpus + bench, AND a bench G1 on those patterns shows an engine-only (or walk) artifact losing to a set-find prototype by more than noise |
| C2 | scan a NON-CUBE two-member position (`fn-pair` on any two bytes; the window family's B-pair does) | the census's declines whose best position is a non-cube pair (`cat\|dog`) are a counted population AND G1 shows a loss |
| C3 | several RUN terms per part (word compares of the findable stretches on both sides of a wide position) | `verify_cmp` shows per-byte compares of a side stretch cost more than `rc-words` by more than noise, on a counted population of stage-3 parts |
| C4 | `vrun` (SIMD) on a multi-term part | a SIMD-layer G1 on stage-3 wide runs loses against `vrun` on the same run with D2's deny |
| C5 | a covering prefilter (cube hull, vector range test) ahead of the exact `settest`, counted unverified | a SIMD measurement of the hull test against `settest` on the census's classes |
| C6 | RETIRED by F11 `[r1pd F11]`: rev 1's "stated R label" is what R by role gives, with no field | — |
| C7 | RETIRE the scoped ofsskip admission (§2.1) for the general rule (a tableless set is the kit's own test everywhere; scan-less bodies wherever stated), with its OWN deny (behavioural name) and G3 checked with it denied `[r1pd F9]` | D0's base count of today's refused tableless OFS/STMT predicates (pcrec's population, expected 0: its one tableless writer, `cover_window`, is REPORT and never translated; and G2's) is non-zero on pcrec's side, OR a second kit writer of tableless SET terms appears; the retirement re-pins `run_g2.sh`'s `FORM_FLOORS` and G2's two-sided pin (§5.1.1 D2, `[r2pd P12]`) |
| C8 | NOTED `[r2pd P24]`; threshold recorded `[r3pd FIX-S3]` (DOC): there are now three to four per-run special cases (the decline row, P0's `no_scan` column, P2's no-scan clause, the `findable` column), so the unification point is met; the deferral is CHOSEN, not missed: C8 builds at its trigger below, or at a fourth per-run special case added after this rev. The GENERAL FORM. A presence link's TEST KIND is a function of (need, findability), per span, not per run: findable: find + verify; not findable and REQUIRED: verify every candidate (`fn-every-pos`); not findable and OPTIONAL: untested (the decline). Unlocks: C1/C2 drop in as new find methods with no new state; P2's run-less reading (§2.4 item 2) reads the same table. A declared row table over the two facts, replacing the decline row + P0's `no_scan` column + P2's no-scan clause | C1's trigger, or the first MEMBER span stated with no find form (today every member is one byte) |

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
7. **ANSWERED by the r2 rulings** `[r2pd]`: P3 (a no-scan run is run-less in P2, §2.4 item 2); P9
   (`fn-every-pos`, its own UNMEASURED card, first by fact, §2.1, §5.3); P15 (D3's record
   `run_part_terms`, its G2 pre-landing floor, the pcrec floor at the joint landing, §5.1); P8
   (`leads`/`rlead` retired on non-cube runs, pcrec-side, §9 item 6); P14 (R scoped, §2.2).
8. **ANSWERED by the r3 joint ruling** `[r3pd FIX-1]`: P8's retirement extends to the shadow's
   `dominated`/`rdom` on non-cube runs (pcrec-side, in S2's landing); "`rdom` stays" is dropped; the
   family is main's plan row [SHADOW-TABLE] (§9 item 6).

## 8. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: RELEVANT.** D2 adds per-candidate membership tests, and P0's scan-less parts
   walk every candidate. Whether verifying a wide position pays (fewer engine entries) or costs (a
   compare per candidate on a hit-dense scan) depends on the regime; hit-dense Greek/Cyrillic text
   with a scan on `{CE,CF}` is the sharp case. Linux, `taskset`-pinned, both layers. The deny is
   D2's alpha OFF arm; the decline and the scan-less body are correctness and have none. The official
   verdict is pcrec's G1 (its timing vs its own deny, population from a pcrec-side artifact diff).
2. **Independent control: RELEVANT.** C2 reads the RENDERED text; the occurrence oracle is
   D27-written from the contract; G2 computes the decline from its own sets (F21); `emit_sweep`'s
   zero-mover gate is pcrec's artifact diff (never the kit's `moved`); D3's census is checked
   against G2's own counts (its generated sets and C2's reading of the rendered text, never the
   `run_part_terms` record it parses) before the landing, and against pcrec's artifact count of
   stage-3 run parts from the joint landing (F19, `[r2pd P15]`); the record is checked on BOTH its
   feeds, G2's capture and the production collector `collect.py` (`[r3pd RDY-1]`), against pcrec's
   stamped `_REQ_RUN` and `emit_sweep`'s `DIFFER_PINS` (`[r3pd RDY-5]`). The pick shadow's
   retired records (`leads`/`rlead`, `dominated`/`rdom` on non-cube runs) are replaced by named
   successor controls (§9 item 6, `[r3pd FIX-1]`). Each plant in §5.1 names the check that reds, and each existing row is
   REACH-rerun.
3. **What moves when data is regenerated: RELEVANT.** The byte-rate payload decides the scan
   (findable positions only), P3's window and the twin, so a rate regeneration can move a pick on a
   wide run: a pcrec abi event by its bytes, as today. A UCD bump moves pcrec's sets (pcrec's). The
   `verify_cmp` card's regeneration moves no byte (no pricing reads it yet); neither does the new
   `every-pos` card's first measurement (`[r2pd P9]`).

## 9. For main: the pcrec-side facts stage 3 must state or read (COMPLETE AND FINAL, rev 4)

Re-stated whole in rev 4 `[r3pd FIX-1]` so main's stage-3 brief can quote it; items 1-9 are the
complete list (nothing elsewhere in this note adds a pcrec-side obligation). Facts only (D157); the
how is stage 3's. Each is a statement pcrec makes, a reader of the reply, or a pcrec-side check or
pin the joint landing moves.

**One pcrec predicate** `[r2pd P23]`: "the pre-check TESTS the run" (`run >= 0 &&
cls->pres[run].verify`, the kit's `trun`) is written ONCE on pcrec's side and read by every reader
below that today reads "a run is stated" (`run >= 0`) or "a run shipped" (`whole_len >= 2`). One
plant (the predicate answering "stated") reds F1's, F2's and P1's witnesses together.

1. **R by role, in a window site's alternative** `[r1pd F11]` `[r2pd P14]`. pcrec states R as a
   verify-NO span of two or more positions over the walk-proven positions (`pf_window_of`'s
   subset-of-set test, `pcrec_memfn_wpos_bits`), and NEVER stops R at a non-shape position; it reads
   `pinned`/`run_stated` as today. The run PRESENCE span (`req_pres_spans`) is a multi-position
   verify-NO span too and is NOT R (a presence site, never merged); the [RUN-POS-SET] note is
   re-scoped the same way. The brief says "R by role, not shape, in a window site's alternative".
   Witness: `xy/users\d+` keeps `run-pinned`, offsets `0*,1,..,7`, and `_REQ_RUN`'s `@` (today
   `_REQ_RUN "78792f7573657273@0"`, MEASURED rev 3).

2. **The decline** `[r1pd F1, F2, F3]`. `pres[run].verify` 0, `proven_by` 0, `pres_row[run]` = the
   decline row (resolved by id through `mf_finder_rows`, never by index); `cls.run` unread. Every
   pcrec reader of "a run shipped" reads the one predicate above, never `whole_len`:
   `PF_REQ_LANDMARK_MAXOFF` (facts.c; computed before the kit replies, so stage 3 moves or re-reads
   it), `req_handoff_k`, `req_handoff_entry_applies`, `req_handoff_applies`,
   `req_landmark_hit_ppm`, and `req_site_define`'s head-vs-`req_byte` check (today skipped whenever
   `run >= 0`). **`req_site_define`'s head-part `gate_need`** `[r2pd P1]`: today
   `if (run >= 0) gate_need = s->pspans[head].need;`; the kit's `pres_layout_check` expects the head
   part's need by `trun` and `part_is_byte` compares `need` exactly, so it reads the TESTED run. On
   a decline the landmark is the head member (P3's set pick), never the run. These rows join the
   readiness memo §2.1 table. Witnesses F1, F2 (§2.4).

3. **Nothing to render.** A declined run with no verified member: pcrec's admission declines the
   pre-check (today `req_site_define`'s "verify nothing" internal error) and names its `_REQ_WHY`
   value (`match_api.md` §6.3.7¶8, `tuning.md` §2.29).

4. **The scan-less REQUIRED run** `[r1pd F4]`. `pres[run].verify` 1, `has_scan` 0, extent the whole
   run: the run part ships (landmark and K are the run's), `_REQ_RUN` carries no `@` (§6.3.7¶7 row 1
   needs a scan). Witnesses F4 and P2/P9 (§2.4). **Two emitted comments read the wrong field**
   `[r2pd P17]` (emitted text, so abi-carried, stage 3's event): `req_note_run` prints "the scan is
   on byte ... at offset 0" from `rr->scan` without reading `has_scan` (scan-less: it says every
   candidate is verified), and `emit_req_handoff_rest` names the whole run as the landmark on a
   decline (it names the head member there, by the predicate above).

5. **`mf_pres_picks` on a run with no scan** `[r1pd F5]` `[r2pd P3, P4]`. `set_leads` -1;
   `dominated` treats the no-scan run as absent (the set's pick leads, `proof->run` NOT required,
   §2.4 item 2), so a dominated no-scan site has every span `proven_by` and pcrec's dominated
   admission holds as today (`x.(?:cat|dog)` keeps `_REQ_WHY "dominated"`, witness F3).
   **The lead reader** `[r2pd P4]`: `req_pres_head(lead=true)` returns the verified order-0 member
   whenever `run >= 0`, and `req_set_leads_applies` never reads `set_leads`; on a decline that makes
   `set-leads` admit (its text "the set pick's memchr first, then the run search" false). The lead
   reader reads the TESTED run (the predicate above): a declined run has no run search to lead.

6. **The pick shadow's retirements on runs with ANY non-cube position** `[r2pd P8]` `[r3pd FIX-1]`
   (both ruled jointly, kit + main, 2026-11-12; pcrec-side, in S2's landing). The KW-8 shadow
   (`tests/memfn/run_pres_picks.sh`'s `PICKS`, `tests/codegen/run_cand_oracle.sh`) skips FOUR
   records on such runs, as K38-2 retired `scan`/`rwin`:
   - `leads`/`rlead`: `req_set_leads_own` ranks every position by pcrec's own scan index, which
     cannot follow the kit's private "findable" rule;
   - `dominated`/`rdom`: pcrec's `req_byte_dominated_by` (emit_dfa.c) requires `run_verified` on a
     stated run, which is 0 on every route of a run the kit cannot scan, while P3 makes the kit's
     `dominated` 1 there (`x.(?:cat|dog)`: pcrec `pd` 0, kit `dominated` 1). "`rdom` stays" (rev 3)
     is DROPPED: dominance on a no-scan run is the kit's run-less reading, not pcrec's own fact.
   Following the kit in either pair would need its findability (D157) or the reply itself (K35).
   `PICKS`' comment names the retirement. **Successor controls**: C2 (the rendered-text classifier,
   §5.2); G2's decline equality (D1, per site against G2's own "no findable position"); P3's floor on
   pcrec's REAL proof (G2 states `pres_proof.run` 0 on its no-findable sites, `[r3pd FIX-4]`, plant
   p13); and pcrec's artifact witness F3 (`_REQ_WHY "dominated"` kept). The family (scan/rwin,
   leads/rlead, dominated/rdom) is main's plan row [SHADOW-TABLE]: one declared table of the shadow's
   expectations, each live, retired or replaced by a named successor; S2's landing may write these
   two retirements as its first rows if [SHADOW-TABLE] builds first.

7. **Version events** at landing: `MF_SITE_ABI` (R by role) and `MF_CLASS_V` (the row index shift,
   the decline's place, the scan-less state), the next numbers, readers by grep; pcrec's abi event
   is stage 3's own, and every kit byte move rides it (memfn/CLAUDE.md, Q36).

8. **Spec hunks** `[r1pd F25]` `[r2pd P16]` (D80, in the landing commit): `match_api.md` §6.3.7¶7
   rows 1 and 3, §6.3.7¶8, §6.3.7¶11; `tuning.md` §2.28¶1, §2.29 (¶4 among it), §2.30, §2.41¶1 and
   ¶7a; the `--list-axes` memfn-section floor literal (+1 for the deny row). The list is §4's, in the
   readiness memo §2.3's list.

9. **Pins and floors the joint landing raises on pcrec's side** `[r2pd P13c]` `[r3pd RDY-1, RDY-5]`:
   - `emit_sweep`'s deny arm `--memfn=no-run-verify-wide`: its `ASSERT_ZERO` cells (kit branch)
     become `DIFFER_PINS` entries with a floor and a stage-3 manifest (else "NO DIFFER FLOOR
     PINNED" for an arm that cannot fail);
   - D3's pcrec-artifact floor: census over `collect.py --sources corpus` (patterns with an
     unspelled SET term in a `run_part_terms` record) >= that `DIFFER_PINS` cell's movers, at the
     same base and stream, a literal raised from 0 in the landing commit (§5.1 D3);
   - D3's production-path check stays armed: every artifact stamping a run (`_REQ_RUN` not `none`)
     carries one `run_part_terms` record in the re-collected sweep;
   - the D27 author's decline and R-by-role witnesses land with the merge (§5.1.1, "The D27
     author"), each recording its `_REQ_WHY`/`_REQ_HANDOFF`.

# CRITIC premise: memfn-r45

## Findings

### PREMISE-1 — CONFIRMED (by code read) — severity: answer/design — effort: small (one definition) — blast: every cover whose after side does not constrain
`r45_reply.md §1` (table row "proof range forward (per reply)", and "The proof range" bullet), `§8` (1).
Claim: `proof_n = stated_end - MF_PROOF_LO`, `stated_end` = 1 + the largest offset the site STATES; "For a cover,
`proof_n = k + 1 + MF_MAX_BACK`: the range always reaches offset `k`".
Code: pcrec states the after-context span at offset `k` ONLY when that side constrains:
`src/gen/known.c:614-625` (`cover_window`: `n += cover_side_stated(...)`; `if (!cover_side_stated(...)) continue;`)
and `cover_side_stated` (`known.c:563-569`) is false for an all-ones set whose absence SATISFIES (e.g. an
unanchored `[0-9a-f]{24}` with nothing after it). The `known.h:72-79` comment says the same ("one span per
constrained context side"). For such a cover the largest stated offset is `k-1`, so the subject's own formula gives
`stated_end = k`, `proof_n = k + MF_MAX_BACK` (= k+8), range `[-8, k)` — it does NOT reach offset `k`.
Expected (cover_cap.md §11.1 B5, frozen copy line 999-1001): "The reply's range must reach `k + 1` (offset `k`
included); a shorter range is a named internal error". So under the subject's definition pcrec's B5 defence fires on
every unconstrained-after cover (the kit's own "proof_n covers the stated extent" check passes at the same time — the
two checks disagree by construction). Fix: define the per-reply range end as max(stated_end, the span-0 end + 1) for a
REPORT/cover site, or have B5 require `k+1` only where `after` is stated (and want all-ones beyond the range), or have
pcrec always state the after span (an all-ones, empty-core span). Say which in the reply.

### PREMISE-2 — CONFIRMED (by code read) — severity: design (trace/check builds red) — effort: small-medium — blast: every window site in MF_TRACE and PCREC_CAND_TRACE builds
`r45_reply.md §5` (table rows `mf_class`, `mf_wreply`: "a by-value copy of the class shares them"; "KIT writes into the
CALLER's arena (a FRAMED or NONE ask alike)"). The subject lists no whole-struct comparison reader, and three exist that
compare these structs BYTE FOR BYTE, including the new pointer members:
- `memfn/src/compose.c:1260-1263` (MF_TRACE, §4.5 rule 2): `mf_class q; ask_sel(...,&q) || memcmp(&q, &r->cls, sizeof q)`
  — a re-ask writes its proof rows to NEW arena storage, so `q.proof != r->cls.proof` and the define fails on EVERY site
  ("the define-time query's class differs").
- `memfn/src/window.c:2812-2857` (`wf_agree`, MF_TRACE): `memcmp(&asked, &held, sizeof asked)` over two `mf_wreply`s,
  `held` built by a fresh `decide`+`reply_of` — `plan`/`plan_term`/`plan_test` pointers differ by construction;
  `wr_first_diff`'s member table (`window.c:2780-2786`) compares `plan`, `plan_term`, `plan_test` by `sizeof` member, i.e.
  the pointer, not the rows.
- `src/gen/emit_dfa.c:7756-7763` (PCREC_CAND_TRACE, "the WHOLE reply equals `us->wr` byte for byte"):
  `memcmp(&again, &f->us->wr, sizeof again)` — same failure, pcrec side.
Also by field: `compose.c:1266-1276` iterates `proven[d]` for `d < MF_MAX_FWD - MF_PROOF_LO` (would read 4104 rows of a
`proof_n`-row array at the ceiling); `emit_dfa.c:1665` memcmps `mf_run_reply`, which under "fields widen to `uint16_t`"
with `has_scan` left `uint8_t` gets a padding byte (benign only while every producer memsets).
Expected: the reply names these readers and says the comparisons become deep (count + rows) comparisons, in the same
build; pointer-equality must never stand for row equality. Repro: `grep -n 'memcmp(&q, &r->cls\|memcmp(&asked\|memcmp(&again'`
in the build tree.

### PREMISE-3 — CONFIRMED (by code read) — severity: design (API/contract) — effort: medium — blast: mf_ask, mf_wdecide, mf_defined signatures + every caller
`r45_reply.md §5` ("KIT writes, into the CALLER's arena, during `mf_ask`/`mf_defined`"; `mf_wreply` "KIT writes into the
CALLER's arena (a FRAMED or NONE ask alike)"). The asks are declared PURE on a CONST art and have no arena parameter:
- `memfn.h:1527` `int mf_defined(const mf_art *, ...)`; `memfn.h:1538` `int mf_ask(const mf_art *, ...)` whose contract
  (`memfn.h:1528-1537`) says "PURE: ... changes no art state ... Asked and never defined, a site leaves nothing behind";
  `memfn.h:1737` `mf_wdecide(const mf_art *, ...)`, contract `memfn.h:1729-1735` "PURE: no text, no handle, no art state".
- The NONE ask deliberately avoids the art's arena: `window.c:2768-2770` "the ask is pure, so not the art's arena"
  (calloc/free); the FRAMED body uses a private heap freed before return (`window.c:2713-2737`, `wd_free(blks)`), and
  `wf_agree` (MF_TRACE) builds a reply with no arena at all.
- `wf_plan_class` (`window.c:3840`) and `compose.c:395-411` fill the class with no allocator in reach.
So "rows in the caller's arena during an ask" requires either a new `mf_arena *` parameter on mf_ask/mf_wdecide (an
abi/signature event on every caller: ~16 class-ask arena sites + the 3 wdecide sites in emit_dfa.c) or allocating
through the const art's arena, which breaks the PURE contract (every ask now leaves memory behind; re-asks in trace
builds double it). The reply must pick one and name it in the abi list (§5 "abi events" lists only layouts/values). A
caller-supplied buffer of `proof_n` rows (count asked first, or bounded by the statement the caller made) would keep
the asks pure.

### PREMISE-4 — CONFIRMED (by code read; reasoning on the subject's own definition) — severity: answer (latent; a control goes blind) — effort: small — blast: pcrec's B5 / C14 control on every cover
`r45_reply.md §1` "What the count promises" ("The kit's text tests no offset outside the site's stated extent ... So
'nothing proven outside the range' is TRUE BY CONSTRUCTION"), `§6` item 2 ("The two share no source").
The rows are computed from what the text TESTS (`wf_plan_class`, `window.c:3840-3858`: loops `w->off[i]`, the tested
plan, and drops `d >= MF_MAX_FWD`), but the subject sizes the range from what the site STATES (`stated_end`). The claim
"tests only stated offsets" is exactly the property pcrec's B5 exists to CHECK (cover_cap.md §11.1 B5, frozen line
1002-1005: today's loop "wants all ones past `k` ... so a kit text that tests a byte past the after-context reads
`under@d`/`over@d` and declines C14 ...; rev 5's [narrower] range would never look there, and a kit over-read at `k + 1`
that NARROWS a set would silently drop matches" — rev 5's `[MF_PROOF_LO, k+1)` was STRUCK for this reason). With
`proof_n` = stated extent, a defective kit text testing `k+1` (or any offset past the statement) is clipped out of the
rows and pcrec reads "all ones" there = its want: B5 passes, the defect is invisible. That is rev 5's struck range
re-introduced, now chosen by the party under test (the control shares its source with what it controls; learnings §3).
The kit's own proposed check ("`proof_n` must cover the stated extent", §1) checks range >= statement, not
tested ⊆ range, so it does not close this. (Note: at k = 32 today offset 33 = k+1 is already outside the fixed
41-row range, so the gap exists at the top width now; the proposal makes it every width.)
Fix: size the range from the TESTED offsets as well — `proof_n` = 1 + max(largest stated offset, largest tested offset)
- `MF_PROOF_LO` (and refuse the reply if a tested offset falls outside `[MF_PROOF_LO, MF_MAX_FWD)`), so a tested
over-read lands inside the range where B5 sees it. "By construction" should be stated as the kit's promise that B5
checks, not as a reason the range may stop at the statement.

### PREMISE-5 — CONFIRMED — severity: doc/maintenance — effort: small — blast: pcrec test readers of `proven[]`
`r45_reply.md §2` "What moves on pcrec's side" lists `proof_meta.h`'s `PM_NPROOF` (and `G2W_NPROOF`) only. Other readers
index `mf_class.proven[]` directly and break at `MF_CLASS_V` 11: `tests/memfn/proof_run.c:147,206,210,357,364`
(`x->proven[k]`, bounded by `PM_NPROOF`), `tests/memfn/proof_check.c:409-419` (`cls.proven[d - MF_PROOF_LO]`), the
kit's `compose.c:395,406,410-411,1088,1269-1274`, `window.c:3848-3857`, and pcrec's `known.c:649-656` (B5 itself).
Mech rows planting on these (`tests/mech/sabotages/S1083_*`, `S1018_*` name proven0/proven_prev) need a REACH re-read.
Repro: `grep -rn 'proven\[' src memfn/src tests memfn/tests`. Expected: the reply's reader list names them (the D94 rule:
every reader found by grep).

### PREMISE-6 — CONFIRMED — severity: design (check design) — effort: small — blast: mech row S526 + the MF_MAX_TERM witness
`r45_reply.md §2` "Mech row S526 ... Re-aim: plant `MF_WSPAN_POS` 4095 -> 4094 and expect BUILD-REFUSED through B2's
assertion". S526 is the "MF_MAX_TERM LOWERED" row (`tests/mech/sabotages/S526_c14_max_term_lowered.sh`, SAB_ID
`S526-c14-max-term-lowered`, SAB_BEFORE `#define MF_MAX_TERM 32`). Re-aiming it at a different constant leaves
`MF_MAX_TERM` 32 -> 31 with no witness once decoupled (SAB_FILE2 removes emit_vm.c's stride assert, the only other build
refuser; C14's stride clause is "no longer this row's detector" per the row's own header). Also the K38-2 assert
(`emit_dfa.c:1446`, `PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS`) becomes 32 <= 4095 and non-binding: it then has no live
witness at all. Expected: keep S526 on `MF_MAX_TERM` (re-aim its detector back to emit_vm.c's stride assert or C14) and
file a NEW row for `MF_WSPAN_POS` below the ceiling (B2). The subject's REACH description is also inexact: the REACH
greps four lines (`emit_dfa.c` assert, `limits.def`, `MF_WSPAN_POS MF_MAX_SPAN_POS`, `MF_MAX_SPAN_POS MF_MAX_TERM`), not
one.

### PREMISE-7 — CONFIRMED — severity: doc — effort: trivial — blast: §5 stack/arena prose
`r45_reply.md §5` "The 3 `mf_wreply` stack locals (`emit_dfa.c:4670, 7757, 16318`) take 408 B, down from 1,596 B".
`emit_dfa.c:4670` is not a local: it is the `wr` MEMBER of `UnanchStart` (`emit_dfa.c:4660-4672`), and `UnanchStart` is a
stack local at ~10 sites (`emit_dfa.c:4872, 8600, 9325, 9399, 9980, 11499, 12153, 13926, 14825`, plus the by-value copy
`UnanchStart rus = us;` at 14851). So the stack holders of `mf_wreply` are ~12, not 3; the saving is larger than stated
and the "by-value copy shares the rows" lifetime question applies to `rus = us` too (held: same arena, same attempt).
Also "131 KB per answer ... for the attempt's life": the rows go to `cx->arena` (`memfn_sites.c:186-188`), freed only at
Ctx teardown (`compile.c:332`), so rows of EVERY size-ladder attempt live for the whole compile and accumulate across
attempts. Not unsafe; the arena figure in Q6 should say "per compile, summed over attempts".

### PREMISE-8 — CONFIRMED — severity: doc/maintenance (ordering) — effort: trivial (merge main first) — blast: every pcrec-side cite
The subject's cites hold at the build tree (ea83fbc01; origin/main has since moved to d4ec209b9 with no code-path change).
They do NOT all hold on `lane/memfn-k1108`: `git diff --stat ea83fbc01...lane/memfn-k1108 -- memfn/src memfn/include src
tests memfn/tests` is EMPTY (the kit's 71 commits change no code), so the kit branch's code is its merge-base 9798d196,
which LACKS main's stage 1 and the mfind lever. On the lane: `cc_fits` does not exist (`known.c:336` cite absent; the
lane has `#define KN_CAP MF_MAX_SPAN_POS` at known.c:34), `known.h:27` is `absent_before` (MkEnd.set is at :28),
`memfn.h` from ~1601 is shifted -10 (`mf_wreply` ends at :1709 not :1719; RESTART text :1657 not :1666-1667;
`mf_wdecide` :1727 not :1737), `window.c` from ~1895 shifted -7 (`:2768`->2761, `:2816`->2809, `:3013`->3006,
`:3287-3313`->~3280). Repro: `git -C . show lane/memfn-k1108:src/gen/known.c | grep -n cc_fits` (no output). Expected:
the reply says the kit build starts by merging main (it depends on stage 1's `cc_fits`/`cover_window`/MkEnd), or cites
both trees.

### PREMISE-9 — CONFIRMED (arithmetic) — severity: doc — effort: trivial — blast: §4 / §8 (4) figures
`r45_reply.md §4` "the candidate at period offset `i` tests `31 - i` positions before it meets `g`. That is 496 tests per
32 bytes, about 15.5 per byte". Counting the failing test too (the `&&` chain evaluates it), candidate `i` makes
`32 - i` tests, sum over i = 0..31 = 528, 16.5 per byte (and the candidate AT `g` costs one test, which 496 omits as 0).
The conclusion (O(n·k), fits x6.65) is unchanged; state which count is meant.

## PROBED-AND-HELD
- SIZES, today (own probe `premise/sz.c`, includes the build tree's `memfn/src/window.c`, gcc 15.2.0, `-std=gnu11`):
  14/14 held — mf_class 2,932 (proven 1,312), mf_result 3,000, mf_wspan 1,164, mf_walt 16, mf_wreply 532, mf_site 2,968,
  mf_pred 2,808 (term[] 32x80 = 2,560), wf_pos 76, wf_alt 6,064, wf_dec 12,568, struct wf_plan 3,424, wf_legacy 5,016;
  MF_PROOF_LO = -8 (NEGATIVE: -MF_MAX_BACK), MF_MAX_FWD 33, MF_WREACH 64, MF_WSPAN_POS 32, MF_WPLAN_MAX 72.
- SIZES, proposed (own twin `premise/prop.c` built per the §5 table): 10/10 held — class 1,640 (with mf_run_reply all-u16
  or has_scan u8: both 1,640), mf_result 1,712, mf_wspan 32, mf_wreply 136, 8 classes 23,456 -> 13,120, 3 wreplies
  1,596 -> 408; arena rows 1,312 / 16,288 / 131,328 B at k = 32/500/4095 (proof_n 41/509/4104 WHEN the after span is
  stated, see PREMISE-1); host span arrays 36 B/pos: 1,152 / 18,000 / 147,420; inline class at 4104 offsets 132,948
  (x8 = 1.06 MB); wf_legacy at 4095 262,080; find_groups key[] 16,416; wf_dec ~644 KB; plan arena ~7-8 B/entry (28.7 KB
  at 4104 entries vs "about 32 KB": approximate, held).
- SIGN/FORMULA: `proof_n = k + 1 + MF_MAX_BACK` = `(k+1) - MF_PROOF_LO` is algebraically right (MF_PROOF_LO = -8) when the
  after span is stated; fails when it is not (PREMISE-1).
- FILE:LINE cites at the build tree: 45/45 held (memfn.h 277, 286, 302-315, 650-667, 653, 658, 669-685, 689, 722,
  1005-1012, 1280-1285, 1288-1343, 1346-1372, 1666-1667, 1695-1719; window.c 183, 219-220, 1323-1354, 1354, 1440-1441,
  1463, 1772, 1773-1825, 1775, 1786, 1846-1862, 1850, 2475, 2556, 2768, 2816, 3013, 3287-3313; compose.c 406, 470;
  ofsskip.c 115; gate.c 314, 532; generic.c 180; g2_win.h 23; proof_meta.h PM_NPROOF 41; emit_dfa.c 1446, 4670 (a member,
  PREMISE-7), 7757, 16318; memfn_sites.c 590-600; known.c 336, 347-351; known.h 27). On lane/memfn-k1108 ~14 moved or
  absent (PREMISE-8). origin/main moved ea83fbc01 -> d4ec209b9 with no code-path change (held).
- "E-find and the floor test plan offsets only": held for the CHECK (`wf_test_to` iterates `w->off`, the plan;
  `wf_plan_class` proves only those) — but it is the kit's promise, not a by-construction property of the range (PREMISE-4).
- MF_MAX_SPAN_POS/MF_MAX_AHEAD readers: grep found memfn.h, window.c:1850, known.c:347-351, known.h:27, S526, S1131 (all
  named by the subject) plus `docs/dev/kvcensus/kvdfa.py:25` (`CAP = 32`, a comment-level reader; doc tool, minor).
- HOLDERS / LIFETIME (b): 16/16 arena sites counted (10 `mf_class` + 6 `mf_result` `pcrec_arena_alloc` in emit_dfa.c and
  memfn_sites.c); 7 CandScan stack locals + 1 trace-only local (emit_dfa.c:7157, inside PCREC_CAND_TRACE 7109-7168, so a
  non-trace build has 7) — R-45's "8" is the trace build's count; CandAsked is ARENA (emit_dfa.c:7140), not stack.
  The kit's art arena IS `cx->arena` (memfn_sites.c:186-188), freed only at Ctx teardown (compile.c:332) after the Job:
  no holder (stack, CandScan, CandAsked, PcrecCover on the Job, UnanchStart incl. `rus = us`, mf_result) outlives it;
  compound parts publish heap TEXT only (comp_shell->text), never classes. No class/wreply is hashed or printed: the
  KITPROOF record (known.c:519-522) prints why/k/routed/role only; `cand_class_eq` (emit_dfa.c:7124-7130) compares
  fields (proven0/proven_prev by value) — held; the three WHOLE-struct memcmps are PREMISE-2.
- PRINCIPLE 9 (text round trip): pointer + count lists in mf_wspan/mf_class/mf_wreply serialize as lists, same shape as
  today's `mf_walt.spans` pointer and `mf_term.run/mask` — held; the purity/arena-parameter problem is PREMISE-3.
- PER-REPLY proof_n vs B5 soundness: offsets below 0 held (window_bounds_check refuses start < -MF_MAX_BACK, so nothing
  stated or tested below MF_PROOF_LO; rows 0 and -1 always in range since stated_end >= 1); out-of-range-as-all-ones is
  SOUND as membership (claims nothing) — but blinds the equality check past the statement (PREMISE-4) and the range can
  stop before k (PREMISE-1).
- Arithmetic §4: k/2 re-tests, ~2,047/byte at 4095, x850 = 6.65 x 4095/32 — held (count convention PREMISE-9).
Counts: 24 sizes held, 45 cites held at build tree, 16+8 holders held, 5 lifetime/serialization checks held; 9 findings.

CRITIC COMPLETE

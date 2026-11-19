# READYL3 findings — round r51 spanarms7

## Findings


### READYL3-1 — D-8 keeps the entry's `if (k > 0 || round.len > 0)` guard in the caller, so under `byte` a K<0 entry emits NO move and attempts begin at the raw hit, before the start offset
CONFIRMED (model of the text read literally; oracle-checked). D-8 (span_arms.md l.1527-1529) lists "(1) the entry's
`if (k > 0 || round.len > 0)` guard" among the differences that STAY in the caller, and neither the K<0 row
(l.1542) nor L3's Feature bullet (l.1720-1727) says the guard changes. At B the guard is emit_dfa.c:1115
(`if (k > 0 || round.len > 0) {`); under `byte` `round.len` is 0 (no ROUNDUP), so at K = -B the whole block,
including the new `if (hit >= pos || pos - hit < B) hit += B; else hit = pos;`, is NOT emitted:
`handoff_position` stays the run's occurrence, B bytes before its match and possibly BELOW `posvar`, and the
body/attempt loop starts there (p4.c at B: `attempt_position = handoff_position;` line 319 straight after the gate).
Repro (bin/d8_guard.py, the D-8 model with the guard kept literally, VM attempt loop and body-from-t forms):
`(?<=a)a(\w)\1` (L3 run `aa[\w]` by the BACK row, K -1, omin -1, B 1, floor max(0,pos-1)):
subject `-aaaaaq-b` start 3: floor 2, hit 2, guard false -> attempt at 2 -> (2,5); oracle
`p2probe '' <hex> 3:<hex>` -> `M 3 6`. 22 mismatches over 1857 starts (subjects to 22 bytes); with the guard
honoured (bin/d8.py) 0. Patterns whose run cannot recur within B bytes ((?<=foo)bar..., e{10}) hide it, so
§14.2's L3 rows alone would not catch it.
Fix (text): D-8/L3 Feature: at L3 the entry guard becomes `k != 0 || round.len > 0` (the K<0 row always emits),
and a witness with a self-overlapping lookbehind run (period < B+1, e.g. `(?<=a)a(\w)\1` from 3 on `-aaaaaq-b`)
joins W-L10..W-L14; RM-3's S470-style plant on the guard should be named.
Severity: answer. Effort: S (one condition + one witness row). Blast radius: every K<0 entry under `byte`
(the DFA scan, the hybrid prefilter and the VM attempt loop). Location: span_arms.md §14.3 D-8 l.1527-1542,
§14.4 L3 Feature l.1724; emit_dfa.c:1115 at B.

### READYL3-2 — K's test readers are not listed: run_prechecks.sh [5.12a] (the hand-K pin table) and [5.12b] (`s512_presence`) read K and pass a K<0 artifact through their "0" arm unchecked
CONFIRMED (read at B; the subject names run_prechecks.sh only as RM-4's binding, l.1719). At B,
tests/codegen/run_prechecks.sh:1779-1797 `s512_presence` branches on the stamp: `unbounded`, `[ "$st" -gt 0 ]`
(checks `handoff_position -= $st;` and `if (handoff_position - search_from > $st) {`), else the K=0 arm, which only
checks that the block does NOT subtract. A stamp `"-3"` falls into the K=0 arm: D-8's `hit += B` /
`pos - hit < B` text is never matched against the stamp's K, so a wrong B (e.g. the comment or the add printing
K's magnitude off by one) passes [5.12b] — its stated duty is "the subtraction and the comparison carry the
stamp's K". [5.12a]'s ROWS (l.1813-1829) are THE independent control of K ("never to the walk that computed K",
l.1725-1729) and hold no lookbehind row, so L3 adds negative K with no hand-derived pin; W-L* rows read answers
and the HANDOFF stamp, which share the walk's source (learnings §3). [5.12b]'s attempt-loop arm `[ "$st" -le "$k" ]`
is fine for signed values.
Fix (text, L3 Tests): add (1) a K<0 arm to `s512_presence` (the add and the distance test carry `-$st`), and
(2) [5.12a] rows `(?<=foo)bar(\w)\1%-e byte%-3%-3%...`, `(?<=e{10})eeeeeqzx%-e byte%-10%-10%...` (and a utf8 row
where B is bytes of a multibyte lookbehind, D-11), hand-derived from the text.
Severity: maintenance (a check that goes blind exactly where L3 acts). Effort: S. Blast radius: the K<0
population. Location: span_arms.md §14.4 L3 Tests l.1734-1744; run_prechecks.sh:1779-1797, :1813-1829 at B.

### READYL3-3 — D-13's L3 row misses two spec sentences L3 makes false: facts_listing §4.1.2¶8 ("at or after the attempt start ... No byte of it lies inside a lookbehind") and match_api §6.3.7¶6 ("consumes the run ... between that position and the end of its match")
CONFIRMED (read at B, docs/spec in the review tree). facts_listing.md [4.1.2¶8]: "The run occurs inside every
match, at or after the attempt start, whatever that K is ... No byte of it lies inside a lookbehind (one may lie
before the match start)". At L3 `(?<=foo)bar`'s `req_whole_run` is `foobar` at K -3: three of its bytes lie inside
the lookbehind and before the attempt start. D-13's L3 row (span_arms.md l.1616) changes only ¶8b of that file.
match_api.md [6.3.7¶6]: "a successful attempt consumes the run, contiguous, between that position and the end
of its match" (the `\K` caveat covers the REPORTED start only); D-13 assigns ¶6 to E2 ("every successful attempt
contains the run") and to L2's past-the-end clause, but the before-the-attempt case is L3's and no row edits it.
tuning.md [2.28¶1] also defines the run as positions "every successful attempt must contain" with only the
`\K` caveat; D-13's L3 cell edits that paragraph for bit 31 only. Between L3's landing and L2's (and after, since
L2's clause is the other end) the contract states the opposite of the artifact.
Fix (text): add to D-13's L3 row: facts_listing §4.1.2¶8 (the run may begin before the attempt start, inside a
positive lookbehind, by -K bytes; drop "No byte of it lies inside a lookbehind"), match_api §6.3.7¶6 (a run may
begin up to the declared lookbehind length before the attempt start; consumed part unchanged), tuning §2.28¶1's
definition sentence. Severity: doc (D80 contract; a reviewer rejects the landing without it). Effort: S.
Blast radius: three spec paragraphs. Location: span_arms.md §14.3 D-13 l.1609-1617.

### READYL3-4 — D-8's "`hit + B` cannot pass the subject's end, since ... the occurrence at `hit` holds the whole run" is false on a DFA-scan route: there the candidate holds only the kit's verified STRETCH
Premise CONFIRMED false at B; consequence SUSPECTED (needs the L3 kit's stretch choice on a BACK run). At B, on
routes where a DFA scan fronts the pre-check, the run part returns a CANDIDATE that guarantees only the stretch the
kit verifies (tuning.md [2.41¶1]: "`c` holds the stretch of the run the pre-check verifies (where that is the
whole run, `c` is the least occurrence"). Emitted at B (`build/pcrec -p rx --features all --emit-main`):
`[a-z]{1,3}abcdefqrstuvwxyz0123456789` (RX_DFA_SCAN "unanchored", RX_REQ_HANDOFF "2", 27-position run) emits
`if (cand + 21 >= n) return n; if (!memcmp(subject + cand + 14, "xyz01234", 8)) return cand;` — positions 22..26
are never known to lie inside the subject. D191.2 lets the kit place the scan (and so the stretch) on ANY run
position, including wholly inside the lookbehind prefix [0, B). If the verified stretch ends at index e < B-1, a
candidate at `n - 1 - e` is returned and D-8's entry sets `hit += B` = n - 1 - e + B > n (e.g. a BACK run
`Content-Length: [\d]` (K -16) whose stretch is `-Length:` [7,15) over a subject ending in `...Content-Length:`
gives hit + B = n + 1). The body/prefilter then starts past the end; the DFA reseed reads `subject[pos - 1]`
(one past the end: an ASan report), the same at `pf_emit_handoff`'s re-entry `pos = landmark_position + B`. The
VM attempt loop (no DFA scan: whole run verified, p4.c's `rx_reqrun` at B) is not affected, which is why the hand
execution over (?<=foo)bar etc. does not show it.
The ANSWER is still NOMATCH (no match can start past n), so the fix is cheap: the K<0 rows add the clamp
`hit + B > n -> NOMATCH` (or `hit = n` before the body's own `> n` test), or the design states a kit-side
obligation (the BACK run's verified stretch reaches index B-1) as a request/ruling — today it has neither, and §14.1
item 2 says "nothing is asked of the kit by L1-L3". A witness: a BACK run whose rarest bytes sit at the
lookbehind's left end, subject ending inside the lookbehind's bytes, under `make asan`.
Severity: answer/safety (out-of-bounds read under the sanitizer; a startpos > n into the body). Effort: S (one
clause per caller + witness). Blast radius: K<0 on the DFA scan, hybrid prefilter and forward re-entry.
Location: span_arms.md §14.3 D-8 table l.1542 (both cells' claims); emit_dfa.c:1108-1131, :7932-7938 at B.

### READYL3-5 — an unlisted reader of the stamp's value set: tests/startset/vmhat_checks.py requires `REQ_HANDOFF` to be "none", "unbounded" or `isdigit()`, which "-3" fails
CONFIRMED (read at B). `git show 1403873df:tests/startset/vmhat_checks.py` l.220-222:
`if ho != "none" and ho != "unbounded" and not (ho or "").isdigit(): viol["handoff"].append(...)`; its header
(l.25) states the contract "`RX_REQ_HANDOFF` is `"none"` or a decimal K". `"-3".isdigit()` is False, so every
VM start-set mover at L3 with a BACK run (the attempt-loop route `(?<=foo)bar(\w)\1` predicts `RX_REQ_HANDOFF "-3"`,
§14.2) is a `handoff` violation. Not silent (a red at `make test`), but L3's reader list (Feature, Tests, D-13) does
not name it, so the build meets it as an unexplained red mid-gate. Other value readers checked and fine with a
sign: run_prechecks.sh [5.12b] (`-le`, `-gt`: see READYL3-2 for its blind arm), emit_sweep.py (masks K as `<K>`),
run_encoding_checks.sh (`[^"]*`), run_handoff_reach.sh (fixed strings).
Fix (text): L3 Tests: "vmhat_checks.py's handoff value rule admits a signed decimal". Severity: maintenance.
Effort: XS. Location: span_arms.md §14.4 L3 Tests; vmhat_checks.py:220-222 at B.

### READYL3-6 — a BACK run can have an EMPTY consumed extent, and D-6's accessor over `[lo, lo)` calls `pcrec_find_run_scan_index(…, 0)`, which reads an uninitialised `cand[0]`
CONFIRMED in the code at B; reachability by hand from D-4's row (no compiler for L3). D-4's BACK row has
`when` = `lg.n > 0 and lg.n <= lb_bytes`, no `head.n > 0`, extent `[lg.n, lg.n + head.n)`, "clipped at the
stored bound" (`PCREC_MAX_REQ_RUN_SCAN` = 32, limits.def:408). Two shapes give `[t, t)`:
(1) `head.n = 0`: `(?<=foobar)\d*x` (BACK `foobar` at -6, 6 positions, against the default `x`: BACK is the
longer, by `rn_choice_rows` it wins), `(?<=foo)` alone (`all`, candidate `foo`, nothing consumed);
(2) `lg.n` at the bound: `(?<=a{32})b` (lg keeps its last 32, `lg ++ head` clipped to 32 = lg).
D-6 then has `pcrec_req_pick` call `pcrec_run_scan_index(rate, run, lo, hi)` with `lo == hi`; at B the primitive
is findings.c:757-774: `cand[]` is filled for `i < n` only, then `pcrec_find_pos_pick(rate, cand, 0, 0)`
(findings.c:664-668) does `best = rightmost; lo = pcrec_find_pos_mass(rate, cand[best])` — an uninitialised
pointer read — and returns 0, so the index is `n - 1 - 0 = -1`, i.e. `lo - 1` (a lookbehind position, not
consumed: `req_byte` would name a byte no match consumes, breaking ¶4) or garbage. The pin is safe (it needs 2).
The subject never says what an empty extent answers (grep of span_arms.md for "empty extent", "head.n = 0":
nothing).
Fix (text): D-6: "an empty consumed extent has no run pick: `pcrec_req_pick` falls to the set's pick (or -1), the
accessor returns none at `lo == hi`, and the pin states nothing"; D-4 either keeps the row (a lookbehind-only run
is still a valid presence fact) with that rule or adds `head.n > 0`; witnesses `(?<=foobar)\d*x` (`req_byte` 120)
and `(?<=foo)` (`req_byte` none, matches `(3,3)` on `foo` — p2probe: M 3 3), plus a 32+-byte lookbehind.
Severity: answer/safety (UB in the compiler; a non-consumed `req_byte`). Effort: S. Blast radius: BACK runs with
a variable or empty consumed start, or a lookbehind of 32+ bytes. Location: span_arms.md §14.3 D-4 l.1467,
D-6 l.1496-1499; findings.c:664-668, :757-774 at B.

### READYL3-7 — the `rn_cmp` split: the text puts it in two commits, and its binding sabotage S474 (anchored on the very line it moves) is in neither list
CONFIRMED (read at B). D-4 (l.1473-1474): "`rn_better`'s row scan is split into a comparator `rn_cmp` ...: a
byte-identical split that lands with L3's FEATURE commit". §14.4 L3 remodel 4 (l.1716-1717): "RM-4 (D-6):
`pcrec_run_scan_index` ...; and `rn_better`'s comparator split `rn_cmp` (D-4)" — a REMODEL commit. The rn_cmp
split is not part of the note's RM-4 (the note's RM-4 is the scan-index primitive only, ranges req.c:1278-1290,
:410-425; anchors_at_B.out RM4a: S453 only), so the anchor map was never run over it. At B,
tests/mech/sabotages/S474_run_choice_prefers_bounded.sh plants `SAB_BEFORE='    RB_ROW_SCAN(i, w, rn_choice_rows,'`
— req.c:488, the row scan inside `rn_better` that the split moves into `rn_cmp`; S1930 anchors the table row
(:478, not moved). `grep -n S474` over span_arms.md: no hit. S474's anchor must be re-aimed (at `rn_cmp`) and shown
red there in whichever commit moves it, else it goes UNREACHED (or keeps planting the shell of `rn_better`).
Fix (text): pick ONE home (the remodel commit, so its byte identity is gated alone), add "req.c:483-492 range to
the anchor map; binding S474 (re-aimed), S1930 checked" to that commit's Binding list.
Severity: maintenance (a control loses its site). Effort: XS. Location: span_arms.md l.1473-1474, l.1716-1719;
req.c:483-492 at B.

### READYL3-8 — the feature's re-ask edit (emit_dfa.c:7923) moves S3075's anchor, which the subject binds only to RM-3 (where that line does not move); the anchor map mislocates S3075 at :1087
CONFIRMED (read at B). S3075's SAB_BEFORE is TWO lines: `    long long k = req_handoff_k(cx);` +
`    pcrec_sb_printf(c, "%s    if (landmark_position < %s) {\n", ind, pos);` — that pair exists only at
emit_dfa.c:7922-7923 (`grep -n -A1` shows :1087's next line is a comment). kit/firstunit_anchors.py matches the
FIRST line only and breaks on the first in-range hit, so anchors_at_B.out prints `S3075@1087` (the note's RM-3 list
repeats ":1087"). D-8 keeps "the re-ask block" in the caller (RM-3 does not move :7923), but L3's FEATURE rewrites
exactly that printf (the K<0 re-ask condition `landmark_position < pos && pos - landmark_position > B`). So the
commit that moves S3075's anchor is the feature, whose binding text names S1706, S1956, S1887, S3076 but not S3075;
RM-2's change of `req_handoff_k`'s return (a state, D-7) also moves its first line at both :1087 and :7922 (S463
shares :1087's line and IS listed for RM-2). Also, the anchor tool's first-line rule can mislocate any multi-line
anchor whose first line recurs (the remodel lists were built on it).
Fix (text): L3 Feature binding: S3075 re-aimed with the re-ask edit (and S3074/S3076/S1702's REACH greps on
`if (landmark_position < attempt_position) {` checked: they stay valid only because their patterns have K >= 0 —
say so); note the tool's first-line limitation where the lists are cited.
Severity: maintenance. Effort: XS. Location: span_arms.md l.1710-1713, l.1720-1727; emit_dfa.c:7922-7923 at B.

### READYL3-9 — premises L3 falsifies that its restate/delete lists miss: invariant F's interval `[p, p + whole_maxoff]` (facts.h:70-74), "c is the LEFTMOST position >= posvar" (emit_dfa.c:1067), the in-flight "landmark at or after scan_position" (:7890-7891), the trace shadow's "req_byte's derivation" (:11342-11343), and D-13's "`@idx` stays consumed"
CONFIRMED (read at B). L3's Feature/Deletes restate only "cannot underflow", the presence comment :1543-1546, the
three K comments (D-16) and `rn_scan_mass`'s comment. Still stating the opposite of L3 afterwards:
(1) facts.h:70-74 `ReqRun.whole_maxoff`: "every successful attempt at `p` holds the run at some `q` in
`[p, p + whole_maxoff]`" — at K = -3 that interval is empty; the true statement is `q = p + K` exactly for BACK
(`[p + omin, p + K]` in general). This is the field D-5/D-7 build on.
(2) emit_dfa.c:1067-1072: "`c`, the LEFTMOST position >= `posvar`" — at L3 `c >= max(0, posvar + omin)`.
(3) emit_dfa.c:7880-7891 (`pf_emit_handoff`): "An in-flight thread the start state carries there completes only
with a landmark at or after `scan_position`" — at K<0 its run begins B bytes before its start. The move is still
sound (my argument: equal DFA states have equal futures, so any completion implies a fresh match at s'' >= q whose
run lies at >= q - B, found by the kit floor, and h + B <= s''), but the comment's reason no longer holds.
(4) emit_dfa.c:11342-11343: the shadow's cand "pcrec's own pick (`req_byte`'s derivation ...)" — D-6 keeps the
shadow on the whole run while `req_byte` moves to the consumed extent, so the two stop being the same derivation.
(5) D-13 (l.1616) checks match_api §6.3.7¶7 unchanged "(`req_byte` and `@idx` stay consumed: D-6)": ¶7 row 1's
`@idx` is the KIT's scan position (match_api.md, emit_dfa.c:16256-16258), which D191.2 lets the kit
place on any run position, lookbehind bytes included; D-6 constrains `req_byte` and the pin only. ¶7's text may
still hold, but the stated reason is false and nothing should test "@idx inside the consumed extent".
Fix (text): add (1)-(4) to L3's Feature "restated" list and fix D-13's parenthesis. Severity: doc. Effort: S.
Location: span_arms.md l.1724-1727, l.1749-1752, l.1616.

VERDICT L3: READY WITH LISTED TEXT FIXES (READYL3-1, -4, -6 are answer/safety and must land in the text before the build; -2, -3, -5, -7, -8, -9 are list/doc fixes)

## PROBED-AND-HELD

- (b) D-8's K<0 rows hand-executed LITERALLY (bin/d8.py; the VM attempt loop form = entry row, anchored attempt,
  `+1`, re-ask condition, re-entry move; and the DFA/hybrid form = entry row then leftmost match from the moved
  start), against libpcre2 (kit/p2probe) at EVERY start offset 0..len of each subject (so inside the lookbehind's
  bytes, just past them, at 0, and at len), plus a find-all chain per subject. Kit floor modelled as the least
  occurrence of the whole run at or after `max(0, pos + omin)`. Cases (K = omin = -B; B):
  `(?<=foo)bar` K -3 B 3 (1892-1962 starts per run), `(?<=ab|b)c` K -1 B 1 (~1800), `(?<=e{10})eeeeeqzx` K -10
  B 10 (~2000, subjects to 46 bytes incl. e^25qzx e^15qzx and e^15qzxe^15qzx overlaps), `(?<=foo)bar(\w)\1` K -3
  B 3 (~1900, 529-598 re-asks), plus `(?<=foo)bar.*z`, `(?<=a)a(\w)\1`, `(?<=ab|b)c(\w)\1`, `(?<=foo)foo(\w)\1`,
  `(?<=foo)`, `(?<=foobar)\d*x` (re-entry-heavy: 366-1136 re-asks each). Random subjects to 22 bytes (150 per
  pattern, 60% with a planted run) plus hand subjects (foofoobar, foobarbar, fofoobarfoobarbar, bcbcbc, abcbc,
  e^20qzx ...). Result: 0 answer mismatches, 0 find-all mismatches; 0 violations of: entry/re-entry never moves
  back, `pos - hit` formed only when `hit < pos`, a re-asked hit is never stale (W-L14: the re-ask cannot repeat),
  `hit + B <= n` (holds on these routes because the model's candidate IS a whole-run occurrence; see READYL3-4
  for the stretch route). Minimum witness lengths reached: 22 bytes (46 for e{10}); B up to 10.
- The `else hit = pos` branch is reached only at `pos - hit == B` (the kit floor), where it equals `hit + B`: correct.
- §14.2's "today at T" L3 rows re-run at B (review tree build/pcrec, --emit-facts): `(?<=foo)bar` 626172/K0/
  dominated/none; `(?<=ab|b)c` none/dominated; `(?<=e{10})eeeeeqzx` 6565656565717a78/emitted/"0";
  `(?<=foo)bar(\w)\1` 626172[\w]/emitted/"0", VM_PREFILTER none; `(?<=ab)ab[a-z]*q` 6162/dominated;
  `(?<=qz)ab` 6162, req_byte 98; `(?<=fo{1,3})bar` 626172; `(?<=abc)x` run none (S1887's premise): all as stated.
- Code cites at B (all hold): facts.c:97-100, :106, :253-262, :354-356, :868-869; emit_dfa.c:55 (abi 108), :1099,
  :1115, :1117-1121, :1469, :1479, :1543-1546, :1640, :1644, :3643-3644, :7898-7900, :7926, :7961, :7965-7967,
  :8990, :9085, :9174, :9293, :9360-9361, :11345; req.c:423, :1284; findings.c:757 (src/core/).
- RM-2/RM-3/RM-4/RM-5 binding lists vs kit/anchors_at_B.out: RM3 (10 + S74 false hit) = subject's list; RM2e 5
  (S1706 with L3, S467, S476, S529, S1957) + the subject's hand additions S811/S1707/S1712 (the margin/pf rows) and
  S463/S809 = the note's list; RM4a S453 (+S280 kset); RM5 S901. Sabotage-text grep for every reader of K, the
  sentinel, the move, lb_max, the scan index and omin (31 hits, 9 false): the only unlisted movers are S474
  (READYL3-7) and S3075's real site (READYL3-8). S1702/S3074/S3076/S808 sit outside the moved text.
- K's code readers (git grep at B): all of site 12's list; :9113 and :9084 keep `whole_maxoff`'s encoding and
  read correctly at negative K (`>= W_UNBOUNDED`); `pcrec_landmark_margin`'s `k > 0 ? k : 0` (:9293) and the kit's
  signed `head_max` (memfn.h, C-R4) admit K < 0. Stamp/fact test readers: emit_sweep.py, run_encoding_checks.sh,
  run_handoff_reach.sh accept a sign; vmhat_checks.py and run_prechecks.sh do not (READYL3-5, -2).
- omin: one pcrec writer (emit_dfa.c:1479); lb_max: one read site to move (:3643-3644) + `pcrec_lb_raise`
  (nesting is max, so a nested lookbehind's guard can exceed lb_bytes: the BACK row then declines, a sound loss).
- The run pin (kset.c:302-337) and `pf_window_of`/`ofs_test_verifies_run` read the pin through `o - at`; with the
  pick restricted to the consumed extent (D-6) and `walk_proves`' `d >= 0`, BACK runs stay sound
  (`ofs_test_verifies_run` declines `pin.o < pin.at`: a speed loss at most).
CRITIC COMPLETE READYL3 19:02

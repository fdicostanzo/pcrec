# verify.md — round r51 spanarms7


Verifier: opus, 2026-11-18. Tree B = 1403873df (review tree build/pcrec), subject = R/subject/span_arms.md (rev 3).
Oracle = kit/p2probe (libpcre2-8). Scratch: VERIFY/c/.

## V1 — READYL3-1 (+ READYL2-6 item 4, READYL2-2's premise): K<0 entry move left unemitted by the kept guard
**HOLDS.**
- Text: span_arms.md l.1527-1529 (D-8): "Every other difference stays in its caller (the note's list): (1) the entry's
  `if (k > 0 || round.len > 0)` guard, (3) its `else`, ...". The K<0 entry cell (l.1542) gives
  `if (hit >= pos || pos - hit < B) hit += B; else hit = pos;` but neither D-8 nor L3 Feature (l.1720-1727) says the
  guard changes ("the signed move (D-8 table) at both callers").
- Code at B: `git show 1403873df:src/gen/emit_dfa.c | sed -n 1108-1131`: l.1112-1114 builds `round` via
  `pcrec_emit_start_zero(..., PCREC_START0_ROUNDUP)`; l.1115 `if (k > 0 || round.len > 0) {` wraps the whole block
  (comment, `if (handoff_position - posvar > k)`, the `-= k`, the `else handoff_position = posvar`).
  `pcrec_emit_start_zero` (emit_dfa.c:896-920): when `pcrec_enc_start_guard` is false ("this encoding places no
  restriction: emit nothing", l.913) it returns before writing; under `byte` round.len is 0. So at K = -B under byte,
  read literally, no move (and no `else` clamp) is emitted.
- Shape of the attempt route at B (K = 0, same guard false): `build/pcrec -p rx --features all --emit-main -o VERIFY/c/v1b.c
  --pattern '(?<=foo)bar(\w)\1'` (header `Pattern: (?<=foo)bar(\w)\1`): l.316 `size_t handoff_position = rx_reqrun(...)`,
  l.319 `attempt_position = handoff_position;` with nothing between. A K<0 entry under the literal text is the same.
- Oracle: `p2probe '' $(printf '(?<=a)a(\w)\\1'|xxd -p) {0,1,2,3,4}:$(printf -- '-aaaaaq-b'|xxd -p)` →
  `M 2 5`, `M 2 5`, `M 2 5`, `M 3 6`, `N`.
- Hand derivation from 3 (subject idx: 0 '-', 1-5 'a', 6 'q', 7 '-', 8 'b'; L3 run `aa[\w]` by BACK, K -1, B 1, kit floor
  max(0, 3-1) = 2): least occurrence of `aa\w` at >= 2 is 2 (bytes 2,3,4 = aaa). Literal text: no move, attempt at 2:
  lookbehind s[1]='a', `a`@2, `\w`@3='a', `\1`@4='a' → (2,5), a match BEFORE the start offset; oracle (3,6). WRONG.
  With the D-8 cell emitted: hit 2 < pos 3, pos-hit = 1 not < B=1 → hit = pos = 3 → attempt at 3 → (3,6) = oracle.
- READYL2-6 item 4 and READYL2-2's premise ("today's entry text moves nothing at K < 0") rest on the same l.1115
  guard: HOLD. Minimum witness length reached: 9 bytes.
- Caveat on severity: the D-8 table cell states the K<0 text, so the defect is "the text is internally inconsistent
  (guard kept vs cell emitted)", fixed by one condition; a careful builder would likely notice, a literal one would not.

## V2 — READYL3-4: the DFA-scan candidate holds only the verified stretch; D-8's "`hit + B` cannot pass the subject's end"
**HOLDS (the claim's stated reason is unsupported); the out-of-bounds consequence is not verified (needs an L3 build and
the kit's stretch choice on a BACK run).**
- tuning §2.41¶1 at B (`git show 1403873df:docs/spec/tuning.md`, §2.41¶1): "The pre-check finds the least CANDIDATE
  `c >= startpos`: no occurrence of the landmark has its position 0 in `[startpos, c)`, and `c` holds the stretch of the
  run the pre-check verifies (where that is the whole run, `c` is the least occurrence; ...)".
- Re-compiled: `build/pcrec -p rx --features all --emit-main -o VERIFY/c/v2.c --pattern '[a-z]{1,3}abcdefqrstuvwxyz0123456789'`
  (header checked): `RX_DFA_SCAN "unanchored"`, `RX_REQ_HANDOFF "2"`, `RX_REQ_RUN "[61-7a]6162...3839@16"` (27 positions).
  `rx_reqrun__body` l.79-83: `memchr(subject + pos + 16, 122, ...)`; `if (cand + 21 >= n) return n;`
  `if (!memcmp(subject + cand + 14, "xyz01234", 8)) return cand;` — run positions 14..21 verified; 0..13 and 22..26 are
  never read, and only `cand + 21 < n` is known. Exactly as the critic cites.
- Contrast (attempt-loop route, VM_PREFILTER none): VERIFY/c/v1b.c (`(?<=foo)bar(\w)\1`) l.295-297 tests `cand + 3 >= n`
  and all four run positions: there the candidate IS a whole-run occurrence.
- D-8 l.1542 justifies `hit + B <= n` by "the occurrence at `hit` holds the whole run"; that is true only where the
  stretch is the whole run. D-6 (l.1500-1502) itself says the kit "scans any run position" of the WHOLE run (D191.2),
  so the kit's stretch may sit inside the lookbehind prefix [0, B); if it ends at index e < B-1 the candidate guarantees
  only `cand + e < n`, and `cand + B` can exceed n by up to B-1-e. So the claim is unsupported by the text.
- Not verified: that the kit at L3 actually picks such a stretch for some BACK run, and the claimed ASan read at the
  DFA reseed / `pf_emit_handoff` re-entry (no L3 code exists). The answer (NOMATCH) is unaffected, as the critic says.

## V3 — READYL3-6: an empty consumed extent from D-4's BACK row, and findings.c at n == 0
**HOLDS (code defect at n == 0 confirmed by reading; reachability from the text confirmed by hand, not by a build).**
- D-4 BACK row (span_arms.md l.1467): when "`lg.n > 0` and `lg.n <= lb_bytes`" (no `head.n > 0`), candidate
  "`lg ++ head` at offset `−lg.n`", consumed extent "`[lg.n, lg.n + head.n)`"; l.1471 "an extent is clipped at the stored
  bound". So head.n = 0 (or lg.n at the bound 32, `PCREC_MAX_REQ_RUN_SCAN`, limits.def:408) gives `[t, t)`.
  D-6 (l.1497-1499): "At L3 `pcrec_req_pick` calls it over the CONSUMED extent (`pcrec_run_cons(run, &lo, &hi)`)". The
  subject never states an empty-extent rule: `grep -n -i "empty extent\|empty consumed\|head.n = 0\|head\.n > 0\|lo == hi"`
  prints only l.1434 (EMPTY-MEET, unrelated).
- findings.c at B (`git show 1403873df:src/core/findings.c`): l.757-774 `pcrec_find_run_scan_index(rate, pos, n)`: guard
  is only `if (n > PCREC_MAX_REQ_RUN_SCAN) abort();`, `cand[]` filled for `i < n` (none at n = 0), then
  `return n - 1 - pcrec_find_pos_pick(rate, cand, n, 0);`. l.664-668 `pcrec_find_pos_pick`: `int best = rightmost;
  uint32_t lo = pcrec_find_pos_mass(rate, cand[best]);` — at n = 0 this passes the UNINITIALISED `cand[0]` to
  `pcrec_find_pos_mass`, which dereferences it (`pos[b >> 3]`, l.656): UB; the loop does not run, it returns 0, and the
  index is 0 - 1 - 0 = -1. Misbehaves on n == 0: yes.
- Reachability, hand: `(?<=foobar)\d*x`: lg = `foobar` (6 <= lb 6), head stops at the variable `\d*`, so head.n = 0 and
  BACK's candidate `foobar` at -6 has extent [6,6). At B its run is none (`--emit-facts`: `req_whole_run ... none`), so a
  6-byte candidate is a plausible winner. Oracle for the critic's lookbehind-only witness: `p2probe '' (?<=foo) 0:foo` →
  `M 3 3`. Whether `rn_choice_rows` actually picks BACK there is not verified (no L3 build).

## V4 — READYL2-1: W-T2's correct and sabotaged runs emit the same kit verify at default flags
**HOLDS** (for W-T2, on the critic's spelled equivalents; W-T3 not verified, it needs a negative-K run no tree states).
- Commands (headers checked): `build/pcrec -p rx --features all --emit-main -o VERIFY/c/v4_*.c --pattern 'a{20}b{12}(?=b{8})'`
  and `... 'a{12}b{20}(?=b{8})'`. Both: `RX_REQ_WHY "emitted"`, `RX_REQ_HANDOFF "0"`, `RX_VM_PREFILTER "hybrid"`,
  `RX_DFA_SCAN "unanchored"`; RX_REQ_RUN `61^20 62^12@31` vs `61^12 62^20@31`. The `rx_reqrun__body` is
  BYTE-IDENTICAL in both: `memchr(subject + pos + 31, 98, n - pos - 31)`, `if (cand + 31 >= n) return n;`,
  `if (!memcmp(subject + cand + 24, "bbbbbbbb", 8)) return cand;`.
- With `--memfn=no-fd-pres-pick` the two differ: `memcmp(subject + cand, "a^20 b^12", 32)` vs `memcmp(subject + cand,
  "a^12 b^20", 32)`.
- Hand derivation on a^20 b^20 from 0: default flags, both bodies: memchr from 31 hits 31, cand 0, subject[24..31] = b^8 →
  c = 0, K 0, prefilter from 0 → (0,20) both ways. Under the flag: correct c = 0 → (0,20); sabotaged first matches at
  c = 8 (subject[8..39] = a^12 b^20) → body from 8 → NOMATCH. Oracle: `p2probe '' a{20}(?=b{20}) 0:<a^20b^20> 8:<..>` →
  `M 0 20`, `N`.
- So §14.1 item 6 (l.1360, "is found at 8 by the presence scan") is false at default flags; W-T2 can only fail on the
  answer under `--memfn=no-fd-pres-pick`. Caveat: the spelled runs stand in for L2's TOP candidate; the kit's choice is a
  function of the stated run, so the same run text gives the same verify. Minimum witness length: 40 bytes.

## V5 — READYL2-2: W-L11 at K -10 cannot fail on the answer
**HOLDS.**
- Text: §14.1 item 7 (l.1361) "W-L11 kept with K = −10"; L3 Tests (l.1735) "W-L11 (K −10)"; the row (l.890): plant
  "today's move kept at K = 0 (no text: the body starts at the hit)", correct column still argued from the retired window
  ("window at `at` 10, K = 0; from 11: floor 1, hit c = 10").
- Oracle: `p2probe '' $(printf '(?<=e{10})eeeeeqzx'|xxd -p) {0,5,10,11,12}:<e^15 qzx>` → `M 10 18` ×3, `N`, `N`.
- Hand derivation at L3 (whole run `e^15 qzx`, K -10, B 10, floor max(0, pos-10); subject 18 bytes holds exactly ONE
  occurrence of the 18-byte run, at 0):
  - correct (D-8 K<0 cell): from 0 hit 0 >= pos → 10; from 5 pos-hit 5 < 10 → 10; from 10 pos-hit 10 → hit = pos = 10;
    body from 10 → (10,18) ×3. From 11/12: floor 1/2, no occurrence → NOMATCH.
  - sabotaged (body at the hit c = 0): from 0/5/10 the body scans forward from 0 and its leftmost match is (10,18), which
    is >= every one of those starts → (10,18), same; from 11/12 no hit → NOMATCH, same.
  - At any start the only match begins at 10; a start-at-hit body can report a wrong answer only if a match begins in
    [c, pos), impossible here for pos <= 10 (the match is at 10) and unreachable for pos > 10 (no hit). The plant can
    never go red on this subject. The rev-2.2 failure needed the window's hit c = 10, which no longer exists.
- Minimum witness length: 18 bytes, starts 0,5,10,11,12.

## V6 — READYL2-3: `[a-z]?[a-z]abc` at B gives run `[61-7a]616263`, K 1
**HOLDS.**
- `build/pcrec -p rx --features all --emit-facts --pattern '[a-z]?[a-z]abc'`: `req_whole_run ... [61-7a]616263`,
  `req_landmark_maxoff ... 1`, `req_set 97,98,99`, `req_byte 98`. `--emit-main` (header `Pattern: [a-z]?[a-z]abc`):
  `RX_REQ_RUN "[61-7a]616263@2"`, `RX_REQ_HANDOFF "1"`, `RX_REQ_WHY "emitted"`.
- `[a-z]?[a-z]a(?=bc)` and `[a-z]?[a-z]a` at B: run none, `req_landmark_maxoff 2` (the byte's), `req_byte 97`.
- The subject predicts `abc` at maxoff 2: §14.2 l.1398 "L2: `abc` at `maxoff` 2", L2 census l.1759 "(`abc` at 2)",
  W-L9 l.888 correct column "`abc` at `maxoff` 2". The consumed spelling's walk keeps the 26-member set position in
  the run, so AHEAD's `tail ++ rg` is `[a-z]a ++ bc` = `[a-z]abc` at offset 1 (= the spelled measurement), not `abc` at 2.
  The L2 prediction is wrong. (Basis: the spelled equivalent; no L2 build. W-L9's failure arithmetic under the plant is
  the critic's hand derivation, not re-checked here beyond the run/K values.)

## V7 — READYL2-5: D-4's BACK row says "where `all`, `lg ++ head ++ rg`" and is built by L3
**HOLDS.**
- span_arms.md l.1467 (D-4 table): "| BACK | `lg.n > 0` and `lg.n <= lb_bytes` | `lg ++ head` at offset `−lg.n`; where
  `all`, `lg ++ head ++ rg` | `[lg.n, lg.n + head.n)` | `look` | L3 |".
- §5.2 TOP row l.626 (REV 3 marked): "BACK admitted (L3): a candidate `lg ++ head` at offset `−t` ...; where `all`,
  `lg ++ head ++ rg`."
- D-13 (l.1616-1617) gives the past-the-consumed-end clause ("which may extend past the attempt's consumed end") to the
  L2 row only; L3's row does not carry it. So, read literally, L3 ships a run that may extend past the consumed end
  (`rg`) with no L3 spec clause for it. (The consequence that `(?<=foo)bar(?=baz)` → `foobarbaz` at -3 at L3 follows
  from the row; no L3 build exists to measure it.)

## V8 — READYL1-1: E-5i on arm `look` only turns restore=zero's [facts-arm] expectation red
**HOLDS** (hand derivation from D-1's table and req.c at B; no L1 build).
- Check at B: `git show 1403873df:tests/codegen/run_facts_checks.sh | sed -n 708-731`: ZP=`xyz(?<=yz)ab\Bcd`, run under
  `--harness=restore=zero`; expectation row `'zr	req_whole_run	78797a	harness:zero'`; its comment: "A row that ignored
  the arm lists all seven bytes `78797a61626364` (E-4's, S1928) or `78797a6162` (E-5's) instead."
- req.c at B l.393-397: `if (!((tab)[i].arm & (w)->restored) && (test)) break;` — a row is passed over only when its
  arm is restored. T3 (l.1072-1082): E-5 `{ rb_zero_look_pos, RB_ZERO_UNIT, PCREC_WALK_ARM(ZERO) }`, E-4
  `{ rb_zero_any, RB_ZERO_UNIT, PCREC_WALK_ARM(ZERO) }`, default the cut.
- Subject D-1 (l.1414): "| **E-5i (L1, new)** | `rb_zero_look_pos` ... | `look` (new, walk_arms.def) |", placed BEFORE E-5
  (l.1408). §5.8 (l.924): "`zero` restores E-4's cut only".
- Derivation under restore=zero at L1: `(?<=yz)`: E-5i's arm `look` is not restored, `rb_zero_look_pos` holds → the item
  (guard `yz` meets `xyz`'s tail) → the run continues `xyz`+`ab`; `\B`: E-4 passed over (zero restored), no later row →
  default cut. Run `78797a6162` ≠ the check's `78797a` → the check goes RED at L1 unless edited.
- The subject does not list it: `grep -n "run_facts_checks\|facts-arm" span_arms.md` → l.446, l.1570 only (both about
  the `dead`/`harness:` why pairs), not the [facts-arm] zero expectation.

## V9 — READYL1-5: re-measure two rows (`x(?=qr)[pq]r` vs `xqr`; `a(?=b)[bc]` vs `ab`)
**HOLDS** (both rows reproduce exactly; the "L1 value = the spelling's value" step is the critic's hand reading of D-3's
set step, not a build).
- `build/pcrec -p rx --features all --emit-facts --pattern P` (fields req_set / req_whole_run / req_byte):
  - `x(?=qr)[pq]r`: `114,120` / `787072/fffeff` / `120`;  `xqr`: `113,114,120` / `787172` / `113`.
  - `a(?=b)[bc]`: `97` / `none` / `97`;  `ab`: `97,98` / `6162` / `98`.
- `--emit-main` stamps (headers checked): `a(?=b)[bc]` `RX_REQ_BYTE "97"`, `ab` `"98"`; `x(?=qr)[pq]r` `"120"`, `xqr`
  `"113"`. So the req_byte move is an emitted-stamp mover too.
- Subject: §14.2 l.1390 `x(?=qr)[pq]r` L1 cell "`xqr`; `req_set` gains 113 (the TOP set step)" — the req_byte 120→113 move
  is not in §14.2 (W-S4's row l.907 does name `req_byte 113` in its plant column). l.1383 `a(?=b)[bc]` L1 cell "`ab`
  (listing only: `cover`)" — states neither `req_set` +98 nor `req_byte` 97→98. Under-prediction confirmed for these two.

## V10 — READYL1-7: `whole_maxoff` at the walk's exit
**HOLDS.**
- Subject D-3 (l.1453-1455): "At the walk's exit, after TOP: every CONSUMED position of the chosen run that is ONE byte
  joins the necessary set at its offset (the run's `whole_maxoff` plus its index)".
- The walk's exit at B (req.c l.1234-1250, `pcrec_req_walk`): `rb_walk(w, root, v); *set = v->set; *run = v->runs.best;
  *pieces = v->desc;` — it holds an `RbRun` (`.off`) and an `RbSet`; `git grep -n whole_maxoff 1403873df -- src/facts/`
  finds NO hit in req.c; the field is `ReqRun`'s (facts.h:76) and written only in facts.c (l.100, 256, 261).
- facts.c l.254-262 at B: `pf->req_run.whole_maxoff = 0; if (bits >= PCREC_MIN_REQ_RUN_BITS) { ... whole_maxoff = run.off; }`
  — 0 below the floor. So, read literally, the step names a value that does not exist at its site and would be 0 for a
  sub-floor run; the sound spelling is `RbRun.off + i` (saturating). The answer-risk consequence (a too-small
  `req_set_maxoff`) is the critic's reasoning, plausible, not built.

## V11 — READYL1-4: run_cpset_structure.sh's ALLOW_FN names derive.c:is_never_leaf; a moved function goes STALE → red
**HOLDS.**
- `git show 1403873df:tests/codegen/run_cpset_structure.sh`: l.457 `ALLOW_FN='src/opt/possessify.c:cls_polarity
  src/opt/derive.c:is_never_leaf ...'`. `cls_scan` (l.472-494): for each entry, `fn_span` empty →
  `echo "STALE: $ent — no such function definition in $f"`; a function with no `u.cls` read → `echo "STALE: ... holds no
  u.cls read; delete the allowance"`. Those lines go to stdout, which l.498 captures: `OFFENDERS="$(cls_scan ...)"`;
  l.499-500 `if [ -n "$OFFENDERS" ]; then bad "[2b] ..."`. So removing or moving `is_never_leaf` out of derive.c (or
  leaving it without its `u.cls` read) fails [2b].
- derive.c at B l.154-156: `static bool is_never_leaf(const Ast *a) { return a->k == A_CLASS && a->u.cls.n == 0;` — the
  allowed read.
- Subject D-9 (l.1550-1558) extracts the never rows, including "leaf: the empty class (`is_never_leaf`)", "in the AST's
  own area"; `grep -n run_cpset_structure span_arms.md` → no hit. Whether the move actually leaves derive.c without the
  function depends on the build (a wrapper could stay), but the gate is unnamed: HOLDS as a listing gap.

## V12 — READYL3-7 / CONFORM-3: S474's anchor sits in rn_better; D-4 vs §14.4 on where rn_cmp lands; S474 absent
**HOLDS** (all three parts). Nuance on S1930 below.
- `git show 1403873df:tests/mech/sabotages/S474_run_choice_prefers_bounded.sh` l.16:
  `SAB_BEFORE='    RB_ROW_SCAN(i, w, rn_choice_rows,'`, SAB_FILE src/facts/req.c, SAB_EXPECT=DETECTED. req.c at B l.490
  `    RB_ROW_SCAN(i, w, rn_choice_rows,` is the only such line, inside `static RbRun rn_better(...)` (l.486-494) — the
  row scan D-4 says is split into `rn_cmp`.
- Disagreement: D-4 l.1473-1474 "`rn_better`'s row scan is split into a comparator `rn_cmp` ...: a byte-identical split
  that lands with L3's feature commit"; §14.4 L3 remodel 4 l.1716-1717 "RM-4 (D-6): `pcrec_run_scan_index` ...; and
  `rn_better`'s comparator split `rn_cmp` (D-4)", with binding "S453, S280, `S461_pick_none_ignores_size`, ..." — no S474.
- `grep -n "S474\|S1930" R/subject/span_arms.md` → no hit; kit/anchors_at_B.out has no S474 (the note's RM-4 ranges do
  not cover req.c:483-494).
- S1930 (`SAB_BEFORE='    { rn_rarer,     PCREC_WALK_ARM(TIE) },'`) anchors the `rn_choice_rows` table row (l.478),
  which a comparator split need not move: READYL3-7's "S1930 checked, not moved" is the more precise reading; CONFORM-3's
  "add S474 and S1930 to the binding list" is right for S474, and S1930 needs only a reach check.

## V13 — READYL3-3 / READYL2-4 / CONFORM-4: match_api §6.3.7¶6 and facts_listing §4.1.2¶8 vs D-13's L3 row
**HOLDS** (both paragraphs are false at L3 and no rev-3 row assigns them to L3).
- match_api.md at B, [6.3.7¶6]: "**`<PREFIX>_REQ_RUN`** — a literal run every successful attempt must contain. An
  attempt is the search's try at one start position; a successful attempt consumes the run, contiguous, between that
  position and the end of its match. The reported match can begin later than the attempt (`\K`), ..."
- facts_listing.md at B, [4.1.2¶8]: "... The run occurs inside every match, at or after the attempt start, whatever
  that K is: ... No byte of it lies inside a lookbehind (one may lie before the match start), and `\K` does not move the
  attempt start it is counted from."
- Subject's L3 prediction: l.1380 "| `(?<=foo)bar` | ... | L3: `foobar`, K −3 |" — `foo` lies before the attempt start,
  inside the lookbehind, not consumed: both sentences are false of the L3 artifact.
- D-13 (l.1609-1617): preamble "E2 owns match_api §6.3.7¶6 and tuning §2.28¶1's run definition ...; `facts_listing.md`
  §4.1.2¶8 already lists the run once with K in ¶8b". L3 row changes: ¶10, ¶11, tuning §2.41¶1, ¶8b, §2.28¶1 ("bit 31
  also removes a scan that begins before the start offset"), facts_listing §4.1.2¶8b only; checked unchanged: ¶4, ¶5,
  ¶7, findings.md §4 — ¶6 and §4.1.2¶8 appear in neither column. L2 row: ¶6 and §2.28¶1 "the clause 'which may extend
  past the attempt's consumed end'" — the AFTER side only. With rev 3's unit order L1, L3, L2 (§14.0), the BEFORE side
  is unassigned. (The rev-2.2 §8 L3 row l.995 named "facts_listing §4.1.2¶8/¶8b" per r2 S11, but §14's D-13 is the
  operative rev-3 list and drops ¶8.)
- READYL2-4's further paragraphs (tuning §2.27¶4, §2.28¶7, §2.41¶8c) were not re-quoted here; the item asked ¶6/¶8.

## V14 — READYL3-5: tests/startset/vmhat_checks.py rejects a `-3` handoff value
**HOLDS** (the rule rejects it; whether an L3 BACK artifact enters this check's mover population is not verified).
- `git show 1403873df:tests/startset/vmhat_checks.py` l.220-222:
  `ho = st.get("REQ_HANDOFF")` / `if ho != "none" and ho != "unbounded" and not (ho or "").isdigit():` /
  `viol["handoff"].append("%s: REQ_HANDOFF %s" % (key, ho))`; header l.24-25: "`RX_REQ_HANDOFF` is `"none"` or a decimal K".
- `python3 -I -c 'print("-3".isdigit())'` → `False`. So "-3" is a `handoff` violation for any artifact in the check's
  population (VM engine, VM_PREFILTER none, VM_START unanchored, l.216-219). The subject's L3 Tests/Feature/D-13 do not
  name vmhat_checks.py (no hit in span_arms.md).

## V15 — CONFORM-1: architecture.md register rows 26 and 27 at B; which is P5
**HOLDS: P5 is row 27; the subject's "row 26 (P5)" names the wrong row.**
- `git show 1403873df:docs/dev/guide/architecture.md | grep -n -E '^\| *(26|27) *\|'`:
  l.639 "| 26 | The scan member `req_byte` answers, asked once | One question, one primitive | req.c:1284, emit_dfa.c:11345
  (C18) | [REQ-LOOKAROUND] L2 or L3, whichever lands first (unit RM-4); ..." ;
  l.640 "| 27 | One per-offset-head primitive for the description and the item | One question, one primitive, from the
  second caller | `pcrec_ph_*` (desc.h, altnf.c) beside L1's item (C22, C43) | L1 ...".
- The note (R/record/req_lookaround_arch.md) maps P4 = 26, P5 = 27 (l.177: "ENTERED at landing, 2026-11-18, as register rows: P1 = 23, P2 = 24, P3 = 25, P4 = 26, P5 = 27").
- Subject l.1589 "row 26 (P5) is DISCHARGED by L1 (one per-offset-head primitive for the description ..." and l.1696
  "register row 26's second per-offset union (D-10)": the description matches row 27, the number is 26 (RM-4's row).

## V16 — RULING-4: can a census run on the unit's BASE observe movers; does the text say the stop reads the model?
**HOLDS, with one reading caveat.**
- §14.4 common (1) (l.1634-1636): "the CENSUS runs first, on the unit's base, as its measurement record; a unit whose
  census finds no mover anywhere (corpus and bench) STOPS and reports, and lands no remodel commit".
- L1 Census (l.1649-1660): "... predicts the reach-0 run and whether the root is never. Observed movers: the facts
  stream's `req_whole_run`, `req_set`, `req_byte`, `req_set_maxoff`, why; compared two-sided. Expected movers (§14.2's
  L1 column): ... STOP if the observed population is empty in corpus and bench."
- L3 Census (l.1700-1704): "predicted movers by the L1 model plus the BACK row ...; observed: the facts stream
  (`req_whole_run`, `req_landmark_maxoff`, `req_byte`) and `RX_REQ_HANDOFF`/`RX_REQ_WHY`. ... STOP if empty."
- L2 Census (l.1756-1760): "observed `req_whole_run`, `req_byte`, `run_pin`, `RX_REQ_WHY`, `RX_DFA_PREFILTER`. Expected
  movers: ... STOP if empty."
- At the base no feature exists, so the facts stream / stamps observed there are today's values with nothing to differ
  from: an observed MOVER population at the base is empty by construction. No bullet says the stop reads the model's
  PREDICTED population (L1 says "the observed population"; L3/L2 "STOP if empty" right after the observed list).
- Caveat: "the observed population" can also be read as the census CLASS population (patterns observed to hold a
  positive lookaround reaching the run edge), which is non-empty at the base; under that reading the stop is "no
  candidate pattern", not "no mover", and the common rule's "finds no mover" still needs the model's prediction. Either
  way the text does not say which population the base-time stop reads: the finding's fix (say "predicted by the model"
  per unit, two-sided comparison after the feature) stands.

## V17 — RULING-1: D-9's quote vs ARCH-STEP.md at B
**HOLDS: the quoted words are the record's restatement, not the owner's.**
- Subject D-9 (l.1552-1553): "(beside the kind rows; the owner, 2026-11-18: such functionality "can be built in that
  structure's own area")".
- `git show 1403873df:docs/design/plan_row_bodies/ARCH-STEP.md` (section "2026-11-18, accessor-grain closed ..."):
  "HIS WORDS: "I agree. Also, looking for functionality wholly dependent on eg the AST, can be built in the AST area. Eg
  a graph walk"." then "RECORD: ... (2) AN ADDITION, his: functionality that depends WHOLLY on a structure (his example:
  a graph walk over the AST) can be built in that structure's own area."
- The owner's own phrase is "can be built in the AST area"; "can be built in that structure's own area" is the RECORD's
  paraphrase, attributed in D-9 with quotation marks to "the owner". (The note, R/record/req_lookaround_arch.md l.71,
  likewise carries the record form.) The placement it supports is unaffected (derive.c's never rows are AST-dependent);
  only the attribution is wrong.

## V18 — CONFORM-8: `x.?bcd` at B; does rev 3 say min(0, K) is an under-estimate?
**HOLDS.**
- `build/pcrec -p rx --features all --emit-facts --pattern 'x.?bcd'`: `req_whole_run 626364`, `req_landmark_maxoff 2`.
  Oracle: `p2probe '' x.?bcd 0:xbcd 0:xabcd` → `M 0 4`, `M 0 5`: `bcd` begins at attempt offset 1 or 2, so the run's
  true position-0 interval is [1, 2]; rev 3's `pcrec_run_omin = min(0, whole_maxoff)` = 0. (Witness length 4-5 bytes.)
- Rev 3 text: D-7 (l.1511-1514) "`omin` is a FUNCTION of K, `pcrec_run_omin(run) = min(0, whole_maxoff)`, because every
  candidate TOP builds has either `omin = maxoff = −t` (BACK ...) or `omin = 0 <= maxoff` (default, AHEAD), so storing
  the interval would state one fact twice"; §14.1 item 5 (l.1359) "a stored `omin` is a second spelling of K"; §12 rev 3
  (l.1195-1196) "`omin` is `min(0, K)`". `grep -n "under-estimate\|underestimate" span_arms.md` → no hit; [PRES-OMIN-TRUE]
  appears only in rev-2.2 text (l.163, l.1114 "the kit's true positive presence `omin` ... from the run's `[omin, maxoff]`"),
  not in §14. So rev 3 does not say that min(0, K) is the sound under-estimate rather than the true interval's lower end
  (the "omin = 0" of the default row is the stated value, not the true one: `x.?bcd` has true omin 1). The choice itself
  (no field until a reader) is not refuted; only the unstated narrowing.

## Summary
V1 HOLDS; V2 HOLDS (claim unsupported; OOB consequence not verified); V3 HOLDS (code; reach hand-derived); V4 HOLDS
(W-T2; W-T3 not verified); V5 HOLDS; V6 HOLDS; V7 HOLDS; V8 HOLDS; V9 HOLDS; V10 HOLDS; V11 HOLDS; V12 HOLDS (S1930 needs
only a reach check); V13 HOLDS; V14 HOLDS (population not verified); V15 HOLDS (P5 = row 27); V16 HOLDS (reading caveat);
V17 HOLDS; V18 HOLDS. Nothing REFUTED.
VERIFY COMPLETE 19:09

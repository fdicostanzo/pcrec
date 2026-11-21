# CRITIC EMIT: l3fix (review r66)

## Findings


### EMIT-1 — CONFIRMED — doc (contract) + speed vs REVIEWED: a ONE-BYTE consumed part is "no run" in the spec but blocks BACK in the code
- Spec of record, facts_listing.md §4.1.2¶8 (SUBJECT): on a fwd_reentry compile the lookbehind's run "is listed only where the
  consumed part states no run, or states one with an unbounded K ...". `rb_top_back_displaces` (src/facts/req.c ~1708) tests
  `best->n == 0` — an EMPTY consumed best, not "no stated run". A one-byte consumed best (n == 1) states no run
  (`req_whole_run none` at BASE: a run is whole_len >= 2) yet blocks BACK.
- Repro: `kit/pc {base,reviewed,subject} --features all --emit-facts --pattern '(?<=foo)b'`:
  base `req_whole_run none`, K 0; reviewed `666f6f62`, K -3; subject `none`, K 0. Stamps (bin/st.sh, kit/cmp.sh):
  base = subject `RX_REQ_RUN "none" RX_REQ_WHY "dominated" RX_REQ_HANDOFF "none"` (0 non-abi diff lines);
  reviewed `RX_REQ_RUN "666f6f62@3" RX_REQ_WHY "emitted" RX_REQ_HANDOFF "-3"`. Expected per ¶8: `666f6f62` at K -3.
- So either the spec sentence is wrong (it should say "states no consumed run byte" / "is empty"), or the code drops a
  case the spec promises. BASE had NO forward re-entry here (dominated, memchr on `b`), so the BACK run cost nothing the
  rule protects: the delta silently drops L3's gain (a 4-byte memmem pre-check vs memchr on one byte, the same shape as
  the measured `(?<=foo)` x8) on every `(?<=LIT)c` / `(?<=LIT)[set]` pattern, unpriced (the re-measure list names none).
- Severity: doc (contract mismatch) certain; speed vs REVIEWED plausible (unmeasured). Not a loss vs BASE. Effort: small
  (spec wording, or key `displaces` on "best states no run" = `best->n < 2`, with a check that a one-byte K>=0 landmark
  handoff is not traded away — `(?<=foo)x?b` style). Blast radius: every lookbehind followed by a single consumed byte/set.
  - EMIT-1 addendum: the code's reading (`best->n == 0`, "EMPTY") matches span_arms §14.4 L3's own wording; only
    facts_listing §4.1.2¶8's "states no run" disagrees. The speed half (a bounded one-byte best that hands off nothing:
    `(?<=foo)b`, `(?<=foo)[bc]`, `(?<=foo)x?b`, and DFA-engine `(?<=x)ab` with a 2-byte `dominated` run) is the shape
    plan row [L3-BOUNDED-RUN-REFINE] already holds (trigger: a measured loss), so the ACTIONABLE part is the spec sentence.

### EMIT-2 — CONFIRMED — speed (loss vs BASE, the r65 x10 shape returns) + doc: `--engine=vm -fprefilter` HAS a hybrid prefilter that re-enters, yet `fwd_reentry` is false there
- `fwd_reentry = engine != VM && !-fno-req-handoff` (src/facts/facts.c:259) and its comment (facts_derive.h ReqWalkParams:
  "`--engine=vm` (no hybrid prefilter)"), span_arms §14.4 L3 pick-rule addendum ("false only under `--engine=vm` (no hybrid
  prefilter) and `-fno-req-handoff` ... the two compiles where no forward re-entry exists whatever route the engine
  selection takes") and facts_listing §4.1.2¶8 all assume a forced VM has no prefilter. `-fprefilter`
  (PCREC_FORCE_PREFILTER, src/opt/select_engine.c pf_admits `forced-on` ahead of the engine-VM default row) gives the
  forced VM a hybrid prefilter whose forward scan takes the `handoff` row.
- Repro (bin/tri.sh = kit/pc in base/reviewed/subject, `--features all -p rx`):
  `'(?<=qz)x?a:' --engine=vm -fprefilter`: base `RX_REQ_RUN "613a@1" RX_REQ_HANDOFF "1" RX_DFA_PREFILTER "handoff"
  RX_VM_PREFILTER "hybrid"`; subject = reviewed `"717a@1" "-2" "memchr" "hybrid"` (65 non-abi lines vs base).
  `'(?<=item )done' -i --engine=vm -fprefilter`: base `handoff` K 0 -> subject `byte-class` K -5 (120 lines).
  Instructions (perf stat instructions:u, 1 MB buffer x 5 searches, same driver, gcc -O2; floor = the buffer fill
  ~9.0M): English-like text (no `:`, no `qz`) base 8,998,866 -> subject 12,284,760 (+3.29M, base's search cost is at
  the fill floor); `bbbb..` 8,998,851 -> 8,998,867; `qz qz bqz ` 8,998,852 -> 8,999,329. Answers held (ans.sh, 59
  start-offset cells vs libpcre2, 0 mismatches).
- This is exactly the loss the pick rule was written to remove (span_arms "x10.3 ... 0.74-0.87 on English-like text"),
  reachable through two public flags. Fix: key the parameter on the options that DO decide whether a forward scan can
  exist — `fwd_reentry = !no_req_handoff && (engine != VM || has(PCREC_FORCE_PREFILTER))` still "reads the options,
  never the route" — and restate the three texts; add the `-fprefilter` cell to [facts-look]'s route cells.
- Severity: speed (opt-in flag pair) + doc. Effort: one conjunct + three sentences + a check cell. Blast radius: every
  lookbehind pattern compiled `--engine=vm -fprefilter` whose BASE run handed off (the r65 mover list).

### EMIT-3 — CONFIRMED — speed (unpriced mover vs BASE on the DEFAULT route) + design: "consumed best EMPTY" is not "no landmark the re-entry keeps"; a BYTE landmark (no run) is handed off at BASE and lost
- The rule's premise (span_arms §14.4 L3 pick rule: "a K >= 0 run at a bounded offset is the one the re-entry keeps")
  treats an EMPTY consumed `best` as "nothing to keep". But the landmark is "the run's where one is stated, ELSE the
  req_byte member" (facts_listing §4.1.2¶8b): with no consumed run, BASE's forward scan hands off on the necessary BYTE.
  `rb_top_back_displaces` (src/facts/req.c ~1708) lets BACK displace any `best->n == 0`, so the subject trades that
  re-entry away — RX_DFA_PREFILTER moves, which span_arms' census says happens on "NO pattern on any stream".
- Repro (bin/tri.sh, default route, byte): `'(?<=qz)(?:a.|.a)'`: base `RX_REQ_RUN "none" RX_REQ_HANDOFF "1"
  RX_DFA_PREFILTER "handoff"`; subject = reviewed `"717a@1" "-2" "byte-class"` (64 non-abi lines). Same for
  `'(?<=qz)(?::.|.:)'`. (Controls: `(?<=qz)(?:x?:)`, `(?<=qz)(?:[^:]:|:)` stay at BASE: their `best` is a 1-byte run.)
- Instructions (perf stat instructions:u, 1 MB x 5 searches, gcc -O2, fill floor ~9.0M), `(?<=qz)(?:a.|.a)`:
  `qz bqz cqz ` (qz dense, no `a`): base 8,998,856 -> subject 39,964,802 (LOSS, base at the floor);
  English-like text (a common, no qz): base 370,482,672 -> subject 12,284,788 (win: BASE's re-entry thrashes on `a`);
  `qzb qzc a `: 240.8M -> 224.5M; `bbbb..`: equal. So MIXED, not a clean loss — but it is exactly the class the rule
  exists to keep at BASE (D191 add. 1(b): an unpredicted mover is fixed before landing), and nobody measured it.
- Answers held (43 start-offset cells vs libpcre2, 0 mismatches).
- Fix direction: key `displaces` on the landmark, not the run: "BACK displaces only where the consumed part states NO
  landmark at a bounded K" (no run AND no req_byte member at a bounded req_set_maxoff), or state the byte-landmark case
  as accepted with this measurement. Corpus reach: a census over `(?<=` patterns whose BASE `RX_REQ_RUN` is `none` with
  `RX_DFA_PREFILTER "handoff"` (none of the 428 corpus patterns per the census, so the reach is crafted shapes:
  alternations whose branches put the necessary byte at different offsets after a lookbehind).
- Severity: speed (mixed; default route) + design. Effort: small (one more fact read in `displaces`, or a recorded
  acceptance). Blast radius: lookbehind + an alternation with no fixed consumed position.

### EMIT-4 — CONFIRMED (held, no defect) — the two internal errors are unreachable by construction
- `pf_emit_handoff` fails on `pcrec_bound_negative(req_handoff_k)`; its only caller is NEXT's `handoff-reentry` row,
  whose `pf_handoff_applies` returns false on `!u->whole` failing and on `!req_k_reentry_sound(req_landmark_k)`;
  `req_handoff_k` == `req_landmark_k` whenever `req_use_whole` is false, and both read FIRST through the same
  CandSel (route DFA, opt flags). `emit_unanchored`'s prefilter check sits under `pcrec_req_site_in_prefilter` ->
  `req_scan_reentered` -> NEXT's scan == PF_SCAN_LANDMARK, the same row. `drop-handoff` (`req_handoff_dropped`)
  declines before the K test. No probe below refused (every refusal seen: `--engine=dfa` on a multi-char
  lookbehind, BASE-identical text).

### Sub-part (b): route table for `fwd_reentry` (each probed BASE/REVIEWED/SUBJECT, bin/tri.sh)
| route | fwd_reentry | a forward re-entry exists? | subject vs BASE |
|---|---|---|---|
| default, hybrid VM / DFA engine | true | yes | BASE run except the rule's movers (EMIT-3 adds an unpriced one) |
| default engine -> VM, no prefilter (backref: `(?<=ab)ab(\w)\1`) | true | no (attempt loop only, sound at K<0) | BASE (conservative, stated in span_arms) |
| `-fno-prefilter`, size-cap prefilter drop / `drop-handoff` | true | no | BASE by construction (facts read options only) |
| `\G(?<=foo)bar`, `(?<=foo)bar$` (one-attempt / dominated) | true | no | BASE (REVIEWED's longer run lost, no re-entry was at stake: [L3-BOUNDED-RUN-REFINE]) |
| `--engine=dfa` (`(?<=x)ab`, `(?m)^(?<=\n)abc`) | true | yes | BASE |
| `-i`, `-e utf8` (8 patterns each) | true | yes | BASE except rule movers (`(?<=xyz)a+xyz`, `(?<=qz)a\w*bc`) |
| `--engine=vm` | false | no | REVIEWED (L3's effect) |
| `--engine=vm -fprefilter` | **false** | **YES** | REVIEWED: BASE's handoff lost (EMIT-2) |
| `-fno-req-handoff` | false | no | REVIEWED; presence pre-check only on both sides, shape kept (rate choice decides) |

## Standing questions
- SIBLING FAMILY: yes. `displaces` is a per-row column of TOP's combining table (RbTopRow), the same shape as the
  start table's `applies` predicates (CandRow) and pf_admits' rows; L2's AHEAD row will be its first sibling. As a
  walk parameter, `fwd_reentry` joins `onebyte_max` and `lb_bytes` in ReqWalkParams, but it is the FIRST option/route-
  keyed one (the others are encoding facts), and it restates downstream knowledge: NEXT's `req_k_reentry_sound`
  (emit_dfa.c) and the prefilter admission (select_engine.c) are re-predicted in the facts layer, which is why it
  drifts from them (EMIT-2: forced prefilter; EMIT-3: byte landmark; EMIT-1/[L3-BOUNDED-RUN-REFINE]: dominated or
  one-attempt routes). Note `rb_top` passes `&root->best`, not the running `best`, to `displaces`: right for one
  row, a decision to state when AHEAD lands.
- GENERAL FORM: TOP states BOTH runs (the consumed best and each BACK/AHEAD candidate, with extents) and the start
  table's FIRST/NEXT rows, which know whether THIS artifact re-enters, pick per route (the one find-the-span choice
  set, kit basic units). Unlocks: (1) the exact pick (removes `fwd_reentry`, EMIT-1/2/3 and [L3-BOUNDED-RUN-REFINE]
  at once) — trigger: L2's AHEAD row needing its own `displaces`, or the next measured mover; (2) gate on the longer
  BACK run while re-entering on the consumed run (two needles, one presence + one re-entry) — trigger:
  [L3-CONS-REENTRY]'s design; (3) the same record carries AHEAD's extent ([REQ-CAND-STRUCT]'s trigger).

## PROBED-AND-HELD
- Default route, byte: 13 seed witnesses + 49 crafted (lookbehinds of length 1-30, nested `(?<=a(?<=xa))bc`
  `(?<=f(?<=f)oo)bar` `(?<=abc)(?<=bc)d`, alternations `(?<=ab|cde)xy` `(?<=ab|xyz|q)rs`, `\K` in and after,
  atomic, backrefs inside/after, `(?<!..)` mixes, empty extents `(?<=foo)`, unbounded runs `(?<=qz)a\w*bc`
  `(?<=xy)\w+@\w+`): 62 patterns x 3 trees; every BASE mover is a rule mover except EMIT-3's two.
- `-i` 8, `-e utf8` 8, `--engine=dfa` 4, `--engine=vm` 4, `-fno-req-handoff` 5, `--engine=vm -fprefilter` 2 (x 3 trees).
- Answers: 37 ans.sh runs (every start offset 0..n of 2-3 subjects each, vs libpcre2): ~950 cells, 0 mismatches,
  across default, `--engine=vm`, `-fno-req-handoff`, `-i`, `-i --engine=vm`, `-e utf8`, `--engine=vm -fprefilter`.
- perf: 2 patterns x 2 trees x 3-4 texts (EMIT-2, EMIT-3).
- Compile count: ~360 of 800.
- Shortest witness: `(?<=foo)b` (EMIT-1); longest: `(?<=x)(?:ab|cd)(?:ef|gh)` / `(?<=a{30})bc` (held).

CRITIC COMPLETE

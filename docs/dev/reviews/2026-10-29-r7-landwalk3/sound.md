# landwalk3 critic: SOUND (opus): is rev 2's selection and hand-off sound as written?

Subject: docs/dev/lanes/p1dsg3_report.md @ cdb5717d9. Code read in worktrees/crit-landwalk3
(main ffb9254cb). Probes and scripts: /var/tmp/pcrec-pcrec/scratch/crit-landwalk3/sound/.
Compiles used: about 45, run one at a time, all before 19:00.

## Findings

### SOUND-1: the relocated composite under the walk loses its RECOVER row (falls back to `reverse-pass`)
- CONFIRMED by code reading (no walk build exists, so there is no run-time repro). Severity: speed/design
  (no answer moves: `reverse-pass` is the total, sound fallback). Effort: small. Blast radius: every
  admitted pattern whose composite would take `pinned`/`end-minus-width`/`landing`, on the LOWER
  (reach-guard) path. Subject: §A2 table, row LOWER: "composite's cells (NEXT, RECOVER) and `CAND_MF`
  join the path".
- Mechanism: every non-fallback RECOVER predicate gates on `cand_recover_asked(cx)`
  (emit_dfa.c:11817 `cand_locate_of(cx)->needs[cand_locate_route(cx)].cells & CN(CAND_SLOT_RECOVER)`):
  `start_pinned_applies` P4 (:9613), `start_width_applies` W0 (:9648), `start_landing_applies` L0'
  (:9667). The same gate is on `pcrec_dfa_landing_guard` (:9741) and on `emit_orientation_block`'s axis-J
  read (:14983). It reads the SELECTED LOCATE row's own `.needs` cells. Rev 2's walk row declares
  `.needs[CAND_ROUTE_DFA] = { CAND_ML | CAND_MA, 0, CN(CAND_SLOT_PRESENCE) }` (§A2 ".needs"), so its
  cells hold no RECOVER. With the walk selected, `cand_recover_asked` is false, and RECOVER is
  `reverse-pass` for the composite that the LOWER relocate runs. The same composite selected
  directly (the cf world, `-fno-landmark-walk`) can take `end-minus-width` / `landing` / `pinned`.
  The cell joins the path through `cand_path_finish`, but its ROW comes from a predicate that asks
  "is RECOVER on the selected LOCATE row?", not "is RECOVER on the path?".
- Observable today, by proxy: `[a-z][a-z]@x` with `-fno-anchored-dfa` takes RECOVER `end-minus-width`
  (facts.sh, below). The same composite reached from a LOCATE row whose cells omit RECOVER would stamp
  `reverse-pass`. RECOVER's selection is consistent across its readers (all go through the same
  gate), so it is not two-valued. It is a selection the design says does not move (G4,
  "composite's cells join the path") and that does move.
- Fix: the RECOVER predicates read path membership (`cand_path_of(...).asks[DFA] & CN(RECOVER)`)
  instead of the selected row's cells, or the walk's `.needs` cells name RECOVER. Either way a
  `cand_recover_asked` reader census belongs in Build plan step 7, and an acceptance cell (a
  fixed-width P with `end-minus-width` today, admitted, LOWER forced by T6's shape) should assert
  `RX_DFA_START`.

### SOUND-2: SLOT-10's recommended `_match` call makes the seed AT pay the caller prologue per hit (quadratic under `-futf-check`)
- CONFIRMED (twin, mine). Severity: speed (quadratic). Effort: small (choose the inline form, or
  call a prologue-free internal entry). Blast radius: every admitted pattern compiled with
  `-e utf8 -futf-check`, plus the K50 startpos guard on every hit. Subject: Disposition SLOT-10
  ("Recommendation: the `_match` call"); §A2 item 3 asks whether a seed AT is answered "identically"
  to the caller's AT.
- The answer IS identical: same A, same anchoring, captures by the same pass. \G cannot reach the
  unanchored DFA body (`req_handoff_assert_body`), and R is not nullable, so there is no empty-match
  rule. The COST is not identical. `rx_match` is a CALLER entry, and its prologue runs
  `rx__valid_upto(subject, n, pos)` from `pos` to `n` under `-futf-check` (emitted u.c:285). Rev-end's
  tie pays that once per search. The walk would pay it once per landmark HIT.
- Twin: `sound/seedcall.c`. It builds `[a-z]+@x` with `-e utf8 -futf-check` (u.c) and without (n.c),
  then calls `rx_match` at s*(j) for every `@` of "ab@"×N, which is what the call form does on a
  no-match subject:

| N (hits) | with -futf-check | without |
|---|---|---|
| 10,000 | 6.1 ms | 0.0 ms |
| 20,000 | 22.6 ms | 0.1 ms |
| 40,000 | 89.5 ms | 0.2 ms |

  Doubling the hits quadruples the time, so the cost is O(hits·n). The reach guard does not bound it:
  `reach` is what A read, not what the validation read. Taking the validation into `reach` would
  instead force LOWER on every hit after the first, so the walk would degenerate to composite.
- Fix: the build takes the inline form (A's run at s*, no caller prologue). Otherwise, the seed calls
  an internal anchored entry with no prologue (the caller's search has already validated
  `[search_from, n)`). Add a utf8 `-futf-check` row to the acceptance cells (T6's shape under utf8).

### SOUND-3: the PRE gate's memo fill moves the `--emit-facts` `used` record on cover/rev-end patterns ("no mover expected" is false)
- CONFIRMED (listing plus code). Severity: maintenance/doc (a DEBUG listing; no answer, no
  emitted byte). Effort: trivial (correct the row; declare the mover in the build commit as C1's is).
  Blast radius: every pattern where `rev-end` or `cover` is selected and rows 1-7 pass. Subject:
  §Checks that fire, row "`--emit-facts` used record" ("the same facts as the walk-off compile (the
  lemma: same NEXT row); no mover expected"), and §Mechanism ("the gate does not read LOCATE",
  so it runs where `rev-end`/`cover` outrank the walk).
- The lemma compares the walk-ON and walk-OFF worlds where the walk is ADMITTED. The gate also
  runs where a higher LOCATE row is selected, and there today's compile never asks NEXT. Examples:
  `[a-z][a-z]@x` (`RX_DFA_SCAN "cover"`) and `[a-z]+@x$` (`"rev-end"`). Both pass rows 1-7: a DFA
  finisher, A built, `@` at a top-level concat position, one branch, `@` outside P's alphabet. Today
  both list `run_pin used=no` (`sound/facts.sh`). The fill selects NEXT for the forward machine;
  `pf_run_applies_common` (emit_dfa.c:7335) reads `pcrec_fact_run_pin` through `us_run_pin`
  wherever `kind != NONE` and `req_run.len >= 2`. Both hold here (`req_run` "@x"; the
  `-fno-anchored-dfa` compile of the same pattern selects `run-pinned` and lists `run_pin used=yes`).
  So walk-on flips `run_pin` to `used=yes` on these patterns, and walk-off (the row denied, no gate)
  does not.
- Fix: the row reads "moves on every compile whose gate fills the memo (rows 1-7 pass), including
  `cover`/`rev-end`-selected ones; declared in the build commit". Count it in [LANDWALK-CENSUS]
  beside the ML build cost on outranked patterns.

### SOUND-4: L8's start set is a NEW kit ask by LOCATE, but §Checks says "no new kit ask"
- SUSPECTED (a design ambiguity; the trace build would show which way it falls). Severity:
  maintenance (trace build only). Effort: trivial. Subject: §The NEXT read cycle ("The memo also holds
  the start set NEXT_cf's row proves (`cand_row_scan`, as `req_start_set` reads it)"); §Checks,
  `table-read-unasked`/`table-ask-unread` ("no new kit ask").
- `cand_row_scan` on a PF_SCAN_BYTE/SET row calls `cand_ask(cx, reader, ...)` (emit_dfa.c:8381). In
  the trace build that calls `cand_ask_check(reader, NEXT, route)`, which traps `undeclared-ask`
  unless `cand_nodes[reader].kask[NEXT]` has the route. `cand_ask_field` likewise needs `kfields`
  EXISTS|PROVEN0. `req_start_set` passes `CAND_SLOT_NEXT` legitimately: its caller is NEXT's own
  handoff predicate. The memo's start set is asked for the walk's L8 (reader LOCATE), outside any
  NEXT predicate. Either it passes LOCATE and traps (rev 2 adds only `reads`/`under`/`by` to
  `cand_nodes[LOCATE]`, "3 fields"), or it passes NEXT and misattributes the ask, which hides it
  from the very check that inventories asks.
- Fix: declare `cand_nodes[LOCATE].kask[NEXT] = CAND_ON(DFA)` and `.kfields = EXISTS|PROVEN0`, pass
  LOCATE, and re-evaluate `table-ask-unread` on the declared ask (LOCATE now reads NEXT, so it should
  pass).

## PROBED-AND-HELD

1. **NEXT_cf lemma (the walk world's NEXT equals NEXT_cf when admitted).** HELD, by reading every
   NEXT row's predicate (emit_dfa.c:10328-10425; `pf_*_applies` at :6599-6608, :7295-7349, :7918,
   :8026, :9040; `cand_pred_memchr_applies` :10070):
   - Every row except `handoff-reentry` reads only `UnanchStart` (`kind`, `views`, the window
     reply's keys), facts (`req_run`, `run_pin`) and the selection's own fields. None reads a slot,
     the path, or the `PCREC_NO_REQ_HANDOFF`/walk bits.
   - `handoff-reentry` reads FIRST through `req_use_read`. In the walk world, FIRST `handoff` needs
     PRESENCE `emitted|set-leads` (`req_handoff_applies` :8790), but `dominated` (or a row above it)
     is selected, so it declines. Its ATTEMPT siblings carry `.whole = true`, which
     `pf_handoff_applies` refuses.
   - With L6 excluding `handoff`, the first applying row is the same in both worlds.
     `dfa_form_derive` (:12669) and `req_scan_reentered` (:9063) select with the same
     `cx->opt->flags`. `PCREC_NO_REQ_HANDOFF` has no other reader (grep: 4 table rows plus
     `req_start_set`).
   - Proxy run (`sound/lemma.sh`, default vs `-fno-req-handoff`, `RX_DFA_PREFILTER`): 13 admitted-shape
     patterns covering byte-class, memchr, first-class-bounded (lookbehind and `\b` starts),
     caseless and utf8. 12 have identical NEXT. The 13th, `[a-z0-9]{2,5}=[0-9]`, is `handoff` by
     default and moves (byte-class under the proxy), which L6 declines. That move is the proxy's
     control and shows the twin can see a difference.
2. **Memo key across options and attempts.** HELD:
   - Each fit-ladder attempt builds a fresh `Ctx`/`Job` (compile.c:2267-2273; `job_cleanup` before
     the `sets` routine, :2577), and the rung's `flags_or` goes into `defo` for the NEXT attempt.
     So deny flags, the ladder's `sets`, `-fno-anchored-dfa`, utf8/caseless and `-p` never share a
     Job with a memo filled under other options. The only in-attempt `cx->opt` swap besides the
     fill is the facts hook (:3506), and it changes only `prefix`.
   - Within an attempt: `tagged` swaps `dfa`/`rdfa`/`adfa` (compile.c:559-563), which the key holds.
     `anchored_ok`/`adfa` are keyed, which covers `pcrec_cand_drop_anchored_shrinks`.
   - The early NEXT read for the scan-edge precondition (`pcrec_dfa_scan_state_written`, before
     `build_anchored_dfa`) cannot fill: row 2 `anchored-A` declines first.
   - `pcrec_revend_form_asked` selects LOCATE before `revend_choose_form`. Where it reaches the
     walk, rev-end did not apply, the form is never chosen, and nothing the fill read moves afterwards.
3. **Hit-stream fact (§Hit stream).** HELD on reading:
   - "At or after search_from" is right for occurrence STARTS. A match starting at `s >=
     search_from` holds its L occurrence at `j >= s`, so an occurrence straddling `search_from`
     can own no start in range, nullable P included.
   - Overlapping inclusion covers periodic runs (`aa` in `aaa`) and run L.
   - Under utf8, `utf8-l0` (L[0] ASCII) makes every byte occurrence a character start. Under
     `-e utf8 -i`, a letter that folds outside ASCII (`s`/U+017F) has no required literal at all
     (`[0-9]+s[0-9]`: req_* none), so no candidate is offered (1 compile).
4. **Asker split (§A2).** Answer-identity HELD; cost did not (SOUND-2).
   - `verify-at`'s predicate `finish_available` (:9417) is `anchored_ok` on the DFA route, the same
     field row 2 reads, so no config admits the walk with verify-at unavailable.
   - `prio-const` (first in FINISH) takes no AT on DFA.
   - \G cannot reach an unanchored DFA body (`req_handoff_assert_body`). `\G[a-z]+@x` is ATTEMPT
     (`RX_DFA_SCAN "attempt"`) and declines at row 1 via the route.
   - R is never nullable (L non-empty), so no empty-match rule applies. A seed at `s* >=
     search_from` reads the same left context a caller AT at `s*` would.
5. **Row 1 `finisher-dfa` (§Admission).** HELD.
   - `pcrec_cand_finisher_dfa` = `fit.chosen == ENGM_DFA && cand_route_of == DFA` (:11770, :3846).
     Both are final within an attempt before the gate (engine selection precedes the DFA build; a
     change is a new attempt).
   - Probes (`--features all`, 13 compiles):
     - `(?=[a-z]*@)[a-z]+@x`, `(?<=\d{2})[a-z]+@x`, `[a-z]+\K@x` are `vm` + `hybrid`, so they decline.
     - `[a-z]+(?C1)@x` is `vm`, no prefilter, so it declines.
     - `\G[a-z]+@x` is ATTEMPT, so it declines.
     - `(?<=a)…`, `(?<![0-9])…`, `\b…`, `(?:(?=a)ab|cd)+@x`, `(?>[a-z]+)@x`, `[a-z]++@x` are exact DFA
       finishers (D67/SR-8: an erasure that widens forces the VM, `pcrec_cand_lang_exact` :11677),
       so they are correctly NOT declined by row 1. The atomic/possessive pair is row 4's (`g1`).
   - No DFA-finisher artifact carries an erased body.

No ANSWER-level finding survived, so no libpcre2 twin was needed. SOUND-2's timing twin carries its
own control (the same calls without `-futf-check`).

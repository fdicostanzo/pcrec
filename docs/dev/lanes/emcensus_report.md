# emcensus — does forward `$` lower to the match-end mark? (D164 add. 1 Q1)

Lane emcensus, 2026-10-12, main `e8401f155`, abi 76. Read-only: nothing under `src/` changed.
Instrument: `docs/design/endmark/census/cost.py` (output `census/results/cost.txt`).
Frank's rule: forward `$` lowers ONLY if it SIMPLIFIES and does not COST.

## Verdict: COSTS, and only PARTLY SIMPLIFIES

- COST: every path-final-`$` artifact that has DFA tables grows. Median +3 states per artifact (ratio
  1.38x, p90 1.75x, max 4.50x); corpus states 3,887 -> 4,954 (+27%), bench 114 -> 155 (+36%).
  Table bytes: +6% corpus, +13% bench; `(?m)$` artifacts +24% (a few +400..+740 B each).
  Endmark.md's E3 gate ("no machine grows by more than one state") FAILS on 271 of 360 artifacts.
- SIMPLIFIES: the `eol_ok`/`eolvar` view and its readers DELETE (nothing else builds an EOL view), but
  the `\z` view (`endvar`) STAYS and every lowered `$` now rides it, and the rev-end tie machinery is
  REPLACED by a tag-set plus `mark_prio` fact, not removed (endmark.md §2.3).
- Under the rule: do NOT lower forward `$` uniformly. The reverse-walk lowering (B3) is a separate
  question (below) and the cost there is the tagged reverse machine, up to 2x its states.

## 1. COST

### Population (K35: every denominator)

| step | bench | corpus |
|---|---|---|
| rows (byte+utf8) | 291+76 = 367 | 4,956+689 = 5,645 |
| parsed by the tail probe | 351 | 5,236 |
| probe: path-final `$`/`\Z`/`(?m)$`/`\z` (`neol\|nmeol\|nz` > 0) | 44 | 1,017 |
| text scanner rewrote at least one `$`/`\Z` | 986 of 1,061 together (75 left alone: all `\z`-only or `\Z\z`/`\z`-in-group shapes, none containing a path-final `$`) | |
| shipped-default engine of the rewritten (captures on) | dfa 23 / vm 16 / compile-failed 1 | dfa 332 / vm 604 / compile-failed 10 |
| compared under `--no-captures`, engine before->after | dfa->dfa 36, vm->vm 3, failed 1 | dfa->dfa 577, vm->dfa 1, vm->vm 358, failed 10 |
| of those: BOTH sides have emitted DFA tables | 11 | 349 |
| no tables (goto-coded or VM, not measurable here) | 28 | 326 |

The 360 table-bearing artifacts are the measured set. The 354 without tables are NOT evidence either way
(they are mostly small machines emitted as code, plus VM artifacts); a code-shaped DFA's growth is not
counted. The shipped-default compare is not possible with this proxy (the `()` is a capture group and
forces the VM), so every number is `--no-captures` on both sides.

### Distribution (lowered - today, total states over the artifact's tabulated machines, n=360)

`-6:2  -5:1  -3:1  +0:23  +1:14  +2:24  +3:227  +4:21  +5:17  +6:12  +7:7  +8:4  +9:7`

Same-role deltas, by machine (count of artifacts): reverse `+0:37 +1:256 +2:19 +3:16 +4:3`;
anchored `-3:1 +0:26 +1:64 +2:242 +3:11 +4:2 +6:2`; forward (the unanchored scan) `+0:5 +1:42 +2:6 +3:7`.
The 284 `anchored+reverse rev-end` artifacts dominate; the FORWARD unanchored population is only 60.

Worst by states: `(?m)done$` bench 12->21 (+9), `a|b$` 6->15 (+9), `(?m)abc$` 10->18, `(?m)$` 2->9, `a.*|b$` 12->19.
Worst by table bytes: `(\p{L}+)$` +3,177 B (228,220 -> 231,397, +3 states), `(?m)[^c]+$` +741 B,
`(?m).$` +548 B. Shrinkers (4 of 360): `(?m:[^c]{1,3}$)` -6 states (21->15), `\s+$` 6->6 (-238 B).

### Proxy and its fidelity limits (read before quoting)

Proxy: each path-final `$`/`\Z` -> `()(?:\n)?\z`, each `(?m)$` -> `()(?:\n|\z)`, compiled `--features all
--no-captures`; `()` is epsilon there, so the machine equals `X(?:\n)?\z`. Text scanner, not the lowering pass.
1. It models the UNTAGGED machine. The real forward machine adds `ACC(back)`, and the real reverse walk
   carries mark distances. endmark.md's own twin (part C) puts the tagged reverse at up to 2x the untagged
   (`[a-z]+\.txt` 7 -> 12): the proxy is a LOWER bound for reverse and anchored states where tags apply.
   The twin's untagged column (`\s+` 2->3, `[a-z]+\.txt` 6->7) matches this census's +1 reverse.
2. The growth is intrinsic to replacing a position VIEW with a consumed tail: a `$`-accept that cost
   zero states (eolvar accept) becomes a state for "after the final `\n`" plus the `\z`-view variant of it.
   That is the "+1 / +2" seen. endmark.md §3.4 predicted "about the same"; it is not.
3. Scanner limits: `(?m)` detected textually; `\Q..\E` patterns skipped; lookaround/conditional groups
   never path-final; a trailing inline-option `(?-m)` is skipped. The 75 unrewritten are listed in the log.
4. Tables only: the byte count is the `static const` arrays (`rx_<role>_*`); goto-coded machines are out.
5. Not measured: time. Counted loads (twin, endmark.md §2) are a separate question; this lane ran no clock.
6. Control: the `()`-vs-no-`()` text compile to identical arrays (spot-checked `abc$`, `\d+$`); the
   baseline for each rewritten pattern is the same pattern compiled by the same binary.

## 2. SIMPLIFIES: readers of the `$`-specific machinery

Under uniform lowering `A_EOL` (non-multiline) is gone, so `N_EOL`/`eol_ok` has no producer
(`src/parse/definitions.c:196-241` already classes `A_EOL` as "replaced away under full reduction").
`N_EOL_M` reads `end_ok` and the class axis, not `eol_ok` (`src/ir/dfa.c:1070`).

DELETES (eol view, once nothing builds `eol_ok`):
- `src/core/internal.h:2022` `DState.eolvar`; `src/ir/nfa.c:615` N_EOL emission (the non-ml arm).
- `src/ir/dfa.c:694`, `:1018-1020` (N_EOL closure arm), `:1475-1514` V_EOL view and its intern, `:1160-1231,1383`
  (hash/intern params), `:1437-1440` (the eolvar canonicalization rule).
- `src/opt/minimize.c:4,49-61,67,212-216` (eolvar in the partition key / remap).
- `src/opt/scanedge.c:66,250,261,318,746` (the "no position view" conjuncts become endvar-only).
- `src/gen/emit_dfa.c:3832` `dfa_has_eolvar`, `:3927` eol table, `:4407,11793` `o->eol`, `:4496`, `:5974-6047`
  (the `eol`/`endv` start-view selection rows `eol_only`/`both`), `:10980` `emit_eol_table`, `:12456-12565`
  (per-state eolvar emission blocks), `:551-553` emitted `*_eol_view` names.
- `src/facts/endwin.c:159-217` `PCREC_EPIN_EOL`/`EW_EOL_SLACK` (re-derived: the fact sees `\z`; endmark.md §4.3).
- `src/gen/emit_dfa.c:11548-11577` `revend_nl_last`/`revend_ties`, `:11651,~11700` the `eol ? 2 : 1` seed loop and
  `revend_tie` bookkeeping (endmark.md §5.3: 4/18 and 4/10 hits).

REPLACED, not removed (new code of equal weight):
- the tie decision: `mark_prio` fact (anchored NFA closure exploration, charged to the state cap) + the
  tag-set accepting states in the reverse machine (endmark.md §2.3). `dfa_matches[]` was folded into
  `cand_rows[]` FINISH (`src/gen/emit_dfa.c:9225`); the ENDSET hand (`CAND_HAND_ENDSET`, `:9428`) STAYS for
  state-dependent ties.
- accept tables gain a `back` table; `last_accept_position` gains `- back[state]`.

STAYS:
- `endvar` and `N_END`/`has_end` machinery (`src/ir/dfa.c:1480,1519,1569`; `emit_dfa.c:3884-3942`): `\z`, `(?m)$`
  and K50 need it, and the lowered `\n?\z` tail now REQUIRES it on every `$` artifact (this is where the
  extra states come from).
- the VM and every non-DFA consumer already treat `$` as a position test; they save nothing and gain the
  slot-1 mark write only on mark artifacts.
- `end_pin` as a fact (answers `z` instead of `eol`), `nl_last`'s question as "accepting reverse state with
  >= 2 distances".

UNSURE: the exact line counts of the `emit_dfa.c:5974-6047` view-selection rows after `eolvar` goes
(`endv`-only rows might simplify further); `scanedge.c` conjuncts reduce but the file keeps both views for `\z`.

## 3. Verdict against Frank's rule

Not SIMPLIFIES-AND-FREE. The deleted surface is real but modest (one view's plumbing across ~8 files; the
`\z` view and the tie decision stay, the latter reimplemented), and the price is paid by ~86% of the measured
population, every anchored and reverse machine for plain `$`: +1 to +3 states typical, +4..+9 on `(?m)$` and
alternation shapes, +6% table bytes (+24% for `(?m)`). The E3 gate in endmark.md is not met by the untagged
proxy and would be further missed by the tagged machine. Recommendation: leave forward `$` on its view;
decide B3 (reverse-only lowering) separately, with the tagged reverse size as its cost — Frank's Q1
"reverse-only form is smaller and ships B3 sooner" now has the census behind it.

OWED (not run, labelled): a clock on the lowered forward machines (not needed to reject on COST); a
real-mark prototype to replace the proxy's lower bound with the tagged number.

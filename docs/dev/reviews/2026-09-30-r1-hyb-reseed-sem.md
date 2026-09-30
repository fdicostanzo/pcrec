# [OPT-HYB-RESEED] critic R1 — engine semantics and answer soundness

Read-only critic, 2026-09-29/30, lane `reseed` at 8f6007b8 (abi 47) against the
abi-46 base. Method: 50+ hybrid patterns (byte and utf8, clamp-free and
clamped, frameless and framed, `adaptive` and `adaptive-dense`) compiled with
base and head `pcrec`, run through one driver that records the result and all
captures at EVERY startpos (sampled at ~40 positions for subjects over 150 B)
plus a find-all loop, on ~1,000 subjects per pattern: random, pattern-derived
tokens, dense/sparse/bursty structures with failing candidates at gaps
1..100, the xx-then-long-gap adversary, multi-byte tokens. Scratch:
/tmp/reseed_crit (nothing tracked touched, no `make`).

## Verdict

The claim "the adaptive re-seed never changes a MATCH/NO-MATCH answer or a
span" is NOT refuted: 0 differences across ~185 (pattern, encoding) runs.
The claim "no answer moves" without qualification IS refuted once give-ups
count as answers: F1 below, which the spec discloses but the abi paragraph
and design §4 understate.

## Findings

| # | sev | claim attacked | witness | measured | status |
|---|---|---|---|---|---|
| F1 | low-med | give-up boundary unchanged on clamped hybrids | `(?<=a\|bc)[a-c]{2,4}d`, `--work-budget=100000`, subject `xabd`x20000 + `aabd` (80 KB) | base: `1,80001-80004`; head: `PCREC_ERR_WORK` (-4). Base needs ~80k work, head between 80k and 100k (~1.1-1.25x). Same at `--work-budget=80000`. | CONFIRMED (documented in tuning.md §2.33 and design §4, but match_api.md abi-47 paragraph says "no answer moves"; §6.3 says "give-ups aside"). Match -> give-up is the bad direction; only reachable near the budget (default 500M work, hundreds of MB). |
| F2 | info | clamp-free adaptive "can only remove attempts" | `(?>a\|ab)c`, `abc` + 80k `q` + `ac`, work budgets 10k/50k | base and head both answer: failed attempts at non-candidates cost ~0 work, so the give-up-to-answer direction did not show. Claim holds structurally (head's attempts are a subset of base's) | not reproduced as a flip; no defect |
| F3 | info | soundness of re-seed mid-subject | all patterns, every startpos, find-all | identical | refuted |
| F4 | info | startpos mid-subject, `\b`, `(?m)^`, `$`/`\z`/`\Z`, lookbehind at seed, `\K`, `\G` | patterns 8, 28, 29, 30, 201-212, 301-303 | identical. `\G` and anchored patterns return through `attempt_max` before the tail, so the new tail is unreachable there | refuted |
| F5 | info | match begins inside a stepped block; probe gap lands exactly on the true start; gap == N, N-1, N+1 | gap families 1,2,3,5,8,13,16,17,31,64,65,100 with a matching tail, both class calibrations | identical. Block end always probes, so the true start is never skipped: stepping visits every position, re-seed lands on a start >= the position asked from | refuted |
| F6 | info | caseless and utf8 multi-byte candidates (byte gap vs char boundary) | `(?i)(?<=AB)x`, `(?<=é)x`, `(?>日\|日本)語(?=!)`, `[é日](?>x\|xy)z`, `(?>é\|éa)c`, utf8 driver incl. mid-character startpos | identical. The gap is a byte count used only as a HEURISTIC input; the advance is the backend's `retry_adv`, and a re-seed answer is a boundary the prefilter produced. Wrong units can cost speed, never an answer | refuted (note: the 日本語 pattern's subjects had 0 matches, my token generator omitted 語, so that row is weak; `(?<=é)x`, `x(?=é)é`, `(?>é\|éa)c` had thousands) |
| F7 | info | overflow in doubling blocks / counters | read `emit_vm.c` tail: `reseed_block *= 2` guarded by `< cap`, caps 1024 and 64 are 64*2^k and 16*2^k, so it never exceeds cap; `steps_left` decremented only when > 0; `short_gaps` saturates at 2; `attempt_position - reseed_from` is size_t and if a prefilter ever answered BELOW its `from` it reads as a huge "long gap" (answer-neutral, and the loop would already fail to progress on the base clamped retry) | 80 KB and 100 KB+ subjects fine | refuted |
| F8 | info | reentrancy | `diff` of base/head artifact: the only new state is three `unsigned` locals in `<p>_search_run`; no statics, no `rx_ctx` field | find-all in one driver process identical to per-call | refuted |
| F9 | info | adaptive tail on an EXACT clamped artifact would carry a stale window | row 1 first and undeniable; emitter has an internal-error guard `if (v->mrl_win)`. `(?<=a)(x{2,3}){2}y` stamps `exact` | ok | refuted |
| F10 | low | forward risk: callouts, conditionals, backtracking verbs | not implemented today (`(?C)`, `(?(?=..)`, `(*SKIP)`, `(*COMMIT)` all refused), so nothing observable is skipped | If `callouts` lands on hybrids, a re-seed skips positions where the callout prefix matches but the whole cannot, and a step does not. The entry prefilter already skips the same way, so such a module must already decline the prefilter; worth one sentence in the design's out-of-scope list | note, no defect today |
| F11 | low | table is first-match rows as data | `pcrec_reseed_rows[]` with `deny`/`pred`/`action` tags, one `vm_reseed_holds` switch, one walk in `vm_plan_reseed`, exported to `--list-axes`. The only remaining branching is the emitter reading `action` (`dense` starting state: `steps_left = cap`, `short_gaps = 2`). That start state is code, not row data | conforms; the dense start state being a `bool dense` in the emitter rather than columns in the table is a small leak of the "rows as data" idiom | minor nit |
| F12 | info | D77 census split derived soundly | `census.py` classifies `over:` from `--emit-facts` kinds (`atomic`, `lookaround`) and `VM_PREFILTER_LANG`; `Vm.mrl_win` (`emit_vm.c:9948`) is the same three conjuncts via `pcrec_fact_kinds` and `prefilter_collapsed`. So the split and the row-1 predicate agree by construction. The weakness is the shared source: a fourth erasure added elsewhere would be invisible to both, but the failure direction is the safe one (row 1 keeps today's retry). One-char lookarounds that U2 made context nodes no longer set `PF_KIND_LOOK` (`(?<=a)(x{2,3}){2}y` reads `exact`), so the census does not overcount them | sound; the 439/455 figures are internally consistent with the table |
| F13 | info | very long subjects | 80 KB and multi-KB dense subjects, size_t throughout | fine; 100 MB+ not run | not refuted, not exercised past 100 KB |

## Not attacked

Timing (out of lens), `make test-axes`, and the byte-identity sweep (the lane's
own). No data on `--tune`, since none exists.

## Suggested actions

1. F1: add the witness to the spec so the give-up direction is stated in
   match_api.md's abi-47 paragraph ("no answer moves, give-ups aside"), not only
   in tuning.md.
2. F10: one line in design §6 that a future `callouts`/verb module must decline
   the re-seed exactly as it must decline the entry prefilter.
3. Optional: move the `dense` start state into row data (F11).

## Coverage caveats (mine)

- Rows 301-304 (`\K`, `\G`) were compiled from the correct pattern text, but the
  subject generator saw the pattern with backslashes stripped (a shell `read`
  without `-r`), so `K`/`G` appeared as extra literal tokens. Subjects still
  produced thousands of matches, all identical.
- `(?>a|ab)c(?<=bc)` (309) and `(?>日|日本)語(?=!)` (314) produced zero matches, so
  they only exercise the no-match path (still identical).
- Only ~40 sampled startpos on subjects over 150 B; every startpos below that.

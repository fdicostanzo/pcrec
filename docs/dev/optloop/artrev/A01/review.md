# A01 loglines_stack_frame — blind review (rvA01)

Pattern `\bat (?:[A-Za-z_$][A-Za-z0-9_$]*\.){2,}[A-Za-z_$][A-Za-z0-9_$]*\((?:[A-Za-z0-9_$]+\.java:[0-9]+|Native Method|Unknown Source)\)`,
DFA engine, pin 57db5152, abi 62, gcc-16 -O2 (Mac M1, scratch tier).
**No timing was run** (brief: suite lock + load). Every lead is identity-verified
plain AND under ASan/UBSan and marked "scratch timing owed"; expected effects are
ordered from work counts (an instrumented scratch copy, `build-artrev/scratch/cnt/`,
never a twin) and from the `-S` asm.

## 1. What the artifact does, as read

`rx_search` (artifact.c:83-626), per call:

1. `memchr(')')` over `[search_from, n)` — dismisses a subject with no `)` (the
   4 `syslog` subjects end here: one memchr pass, nothing else).
2. `rx_reqrun`: memchr `'a'`, then two overlapping 16-bit compares for `"at"`,
   `"t "`; returns the first `"at "` (the handoff). None -> return 0.
3. Unanchored forward DFA (58 states x 28 classes, `unsigned short`,
   premultiplied) from the handoff, seeded from the previous byte's class (that
   is the `\b`). In state 0 with no accept pending it calls `rx_ofsskip`
   (memchr `'t'`, test `'a'` before it — a 2-byte "at" filter, weaker than the
   entry's "at "). Per byte: subject load, class load, transition load, dead
   test, the state-0/skip test, an accept-table load + csel (asm L16/L20/L61:
   ~18 instructions; the critical path is the state -> `ldrh` chain).
   The only accepting state (1316) is terminal (all successors dead), so the
   loop stops one byte after the first match end.
4. Reverse DFA (45 states) from the match end back to the start
   (`rx_reverse_is_accepting_by_class` folds the `\b` lookbehind).
5. Write caps[0], return 1.

`rx_match` is a separate anchored DFA (46 states, accept state 980 also terminal),
a tight 12-instruction loop. `_in` entries forward; `next_pos` is `pos+1`.

Work counts per call shape (instrumented copy, find-all walk as `bench_t.c`):

| subject (1 MiB) | calls | memchr `)` | memchr `a` | memchr `t` | fwd steps | rev steps |
|---|---|---|---|---|---|---|
| fail | 1 | 1 | 33,377 | 0 | 0 | 0 |
| hit (659 matches) | 660 | 660 | 33,155 | 659 | 44,359 | 44,359 |
| syslog | 1 | 1 | 0 | 0 | 0 | 0 |

The cell number is the median of twelve ns/byte values: 4 syslog (one memchr), 4
fail, 4 hit. Positions 6 and 7 fall in the fail group, so **the cell's median is
the fail path, and the fail path is nothing but rx_reqrun's memchr('a') walk**
(one call per `'a'`, mean span 31 B). Only a lead that changes the required-run
scan can move the cell number; the per-byte DFA loops never run on fail.

## 2. Leads

### L1 — anchor on the rarer required byte `(` (algorithmic) — PASS, timing owed

The pattern requires `(` and `)`; both are 8.7x rarer than `'a'` on fail
(3,819 vs 33,376 per MiB). Every match is `"at "` + a run over
`[A-Za-z0-9_$.]` + `"("` + body + `")"`, and `(` is outside the run set, so a
match start p has exactly one `(` (the first after p), and the start is recovered
from that `(` by walking back over the run and requiring `"at "` immediately
before it. The twin: memchr(`(`), backward run (a 256-byte table), 3 byte tests,
then the artifact's own anchored DFA (`rx_match`) at the candidate; on failure
continue after the `(`. Unanchored forward DFA, reverse pass and both prefilters
leave `rx_search`.

- Correctness: candidates are monotone in their `(`; the first candidate the
  anchored automaton accepts is the leftmost start; the end is unique per start
  (no `(` in the run; each body ends at its first `)`), so the anchored entry's
  longest accept is the PCRE answer. `\b` comes from `rx_match`'s seed. Linear
  in n: backward runs are disjoint (each stops at the previous `(` at the
  latest) and an anchored run dies by the next `(`. A candidate below
  `search_from` is refused (`k >= search_from + 3`); the walk never reads below
  `search_from`.
- Identity: PASS plain, PASS `--san` (149 supplied subjects = the 124 bench
  files + 25 hand edge cases in `edge_subjects/`, battery 3000, block 16,
  match examples, libpcre2 10.48 sample 1500: 0 disagreements).
- Sabotage controls (uncounted): `ctldollar` (`$` dropped from the run set)
  FAILS (also with the battery alone, no supplied subjects); `ctlfrom` (a
  match starting exactly at `search_from` refused) FAILS.
- Counts: fail 33,377 memchr -> 3,820 memchr + 6,932 back steps; hit
  33,155 + 659 memchr + 88,718 DFA steps -> 3,633 memchr + 31,103 back steps +
  44,359 anchored DFA steps (+660 out-of-line `rx_match` calls).
- Expected: largest effect of the set, on both fail (the median) and hit.
- Refinements considered, not made: start the anchored DFA after the already
  verified `"at "` (3 of ~67 steps per match); inline the anchored loop (one
  call per candidate, 660/MiB). Both < 5% of the remaining hit work.

### L2 — memchr the run's rarest byte (redundant-work) — PASS, timing owed

`rx_reqrun` keys memchr on `'a'` (offset 0) though `'t'` is rarer on fail and
hit (27,760 vs 33,376 per MiB on fail), and its check re-tests the found byte
with two overlapping 16-bit compares. Twin: memchr `'t'` from pos+1, test
`s[c]=='a' && s[c+2]==' '`. Same candidate set in the same order. Identity
PASS plain + `--san`. Expected: -17% memchr calls on fail, -15% on hit; small,
superseded by L1. The `'t'` choice is DERIVED from these subjects' counts and
unmeasured as a general default.

### L3 — the reverse pass re-finds a start the literal already pins (redundant-work) — PASS, timing owed

After the forward accept at E, the reverse DFA walks the whole match (67
steps per match, a load-latency chain) to find the start. A match contains
exactly one `"at "`, at its start (no space in the run; the bodies' spaces in
"Native Method"/"Unknown Source" are not preceded by "at"), so the start is the
last `"at "` ending before E. Twin: backward byte-compare scan. Identity PASS
plain + `--san`; control `ctlat` (match "at" without the space — body
identifiers like `data`/`format` contain it) FAILS. Expected: hit only (44,359
chained DFA steps -> ~44k independent compares per MiB), 0 on fail, so the
cell median should not move. Subsumed by L1.

### L4 — the first loop iteration re-runs the skip the handoff already did (redundant-work) — PASS, timing owed

The handoff lands with state 0 and no accept, so iteration 1 calls `rx_ofsskip`,
which re-finds the handoff (`ofsskip` invocations counted = calls = 659 on
1 MiB hit). Twin: add `scan_position != handoff_position` to the skip test.
Identity PASS plain + `--san`. Expected NOISE on this cell (1 memchr per call,
~2% of hit's memchr calls, 0 on fail); listed because every call of every
artifact with this handoff + prefilter shape pays it, which weighs more in the
short-call regime.

Expected order of effect on the cell number (fail-dominated median):
**L1 >> L2 > L3 ~ L4 ~ 0**. On hit alone: L1 > L3 > L2 > L4.

## 3. Rejected ideas (results)

- **Tighten the forward/anchored per-byte loops** (accept-table load per byte,
  the per-iteration `add ..@PAGEOFF` gcc re-materializes in L16, compare the
  terminal accept state against a constant). Rejected by asm: both loops are
  bound by the state -> `ldrh` latency chain (~6 cycles/byte); the accept load
  and the skip/accept tests are off that chain, and on fail neither loop runs.
- **Two-byte-stride transition tables** to halve the chain: 28x28 class pairs x
  58 states x 2 B = ~90 KB, far beyond L1; and it is not where the median is.
- **Drop the per-call `memchr(')')`** (on hit it re-scans up to the next `)`,
  ~275 B per call): under L1 removing it moves the syslog cost to the `(`
  memchr, an equal full pass; on hit it is ~180 KB/MiB of memchr at full
  vector speed. No gain. (`origin = notebook:capability_doubled_word-rvA07a`:
  its "restart cost per find-all match: negligible" finding transferred.)
- **Stronger in-loop prefilter** (`rx_ofsskip` checks "at" via memchr `'t'`,
  weaker than the entry's "at ", and runs only in state 0, not in the in-word
  state 28 where it walks the rest of a word byte by byte): real, but never hot
  on these subjects — every `"at "` in them is a match, so the forward loop
  never returns to state 0 after the handoff. Not twinned (count: 0 non-first
  ofsskip calls on all 12 subjects). Worth a look on a subject where `"at"`
  occurs without a match.
- **Scalar Horspool over `"at "`** instead of memchr: a 3-byte needle shifts
  ~3 bytes per step (~350k iterations/MiB) — worse than 33k memchr calls, and
  far worse than L1.
- **Combined twin**: L1 removes everything L2, L3 and L4 touch, so no combined
  arm was built.

## 4. Process notes

- Null twin first (identity PASS plain + `--san`), 4 counted leads at rev 1
  (no revisions needed), 3 uncounted sabotage controls, all FAIL as intended.
- `--corpus` finds 0 cases (as CELL.md says); identity rests on the bench
  subjects, the edge set and the battery. The battery's random identifier
  generator does reach `$` (ctldollar FAILS on the battery alone).
- The edge subjects (`edge_subjects/e*.bin`, `edge.bin`) cover: `\b` failing
  before `at` (`xat`, `_at`, `9at`) and passing (`$at`, `.at`), back-to-back
  matches, nested `((`, start at offset 0, a match at end of subject,
  truncated matches, `\xff`/NUL neighbours, a 26-segment chain.

## 5. Disclosure (charter §3: spawn-time injected text)

Injected before I started: the project CLAUDE.md and a memory index. What may
have influenced me: (a) the CLAUDE.md row that search/scan emission is
delegated to a separate kit (`memfn`) told me the scan/skip code is a distinct
component, which reinforced (but did not originate) reading the prefilters
first — the brief itself lists "the candidate scan/skip"; (b) the memory-index
line "suspect tuning constants" made me label L2's `'t'` choice as derived;
(c) "no SIMD / SIMD last" restated the brief. No lead's idea came from the
injected text; `match_api.md` §3.1 (necessary-literal handoff) is in my
allowed set and informed the correctness wording of L1/L4.

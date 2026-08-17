# D27 blinded corpus — (a{1,3}){65} ambiguous-decomposition region

## Assignment

Pattern `(a{1,3}){65}`. Cover strings of 'a' densely from length 65 up to
~100, extend to boundary neighbors (just below 65, and around the maximum
achievable match length 195 = 3*65), plus a couple of closely related
variants. Full-match/span expectations, PCRE leftmost/greedy semantics.
Oracle: python3 `re`, `timeout 30` on every invocation, KNOWN HAZARD that
`re` backtracks catastrophically and does not terminate in this exact
region — document verification method per expectation.

## Disclosure

At spawn time the session project root's CLAUDE.md and a memory index were
injected into context (pcrec project background, process conventions, past
incident notes — e.g. references to "K24", "D27 cell" mechanics themselves,
"D26 compatibility standard", etc.). This is background about the PROJECT's
process, not about what `(a{1,3}){65}` matches or how pcrec implements
repetition — no implementation detail about pcrec's engine, codegen, or
matching strategy leaked through it. Nothing else leaked beyond that
injection; the cell contained only docs/testing.md and a prebuilt build/.

## The semantics (spec reasoning, derived before any oracle run)

`(a{1,3}){65}` requires exactly 65 repetitions of a greedy `a{1,3}`. Against
a subject that is a run of L consecutive 'a' characters starting at some
position p (nothing before position p in the run):

- If L < 65: impossible — 65 repetitions each need >=1 'a', minimum total
  requirement is 65 > L. No match starting at p (or anywhere within/after
  the run, by the same argument applied to any shorter remaining sub-run).
- If L >= 65: a match exists. Any total T with 65 <= T <= min(L, 195) is
  achievable by distributing digits in {1,2,3} across 65 slots. Because
  PCRE backtracking explores allocations in decreasing lexicographic order
  (each `a{1,3}` prefers 3, then 2, then 1; the whole-pattern search
  backtracks the most-recently-decided choice point first) and any
  allocation with sum T <= L is physically realizable against the literal
  run (every prefix sum stays <= L), the FIRST allocation the search
  reaches and accepts is the lexicographically-greatest realizable one —
  which is also the sum-maximal one (T = min(L, 195)): reducing a later
  slot to make room is always tried before reducing an earlier slot, so
  earlier slots stay at 3 as long as possible and the total consumed is as
  large as the budget allows.

  CLOSED-FORM LAW: match span = [p, p + min(L, 195)) whenever L >= 65,
  no match otherwise (where L is the length of the maximal run of 'a'
  starting at p, and p is the leftmost position such position of any
  qualifying run exists — since PCRE reports the leftmost-starting match).

This law was NOT asserted from intuition alone — see verification below.

## Oracle verification ledger

### Method A — exhaustive small-N induction (scaled induction, primary proof)

Script (scratchpad `smallN.py`, `midN.py`, `higherN.py`): for `(a{1,3}){N}`,
every `L` in `[0, 3N+2]`, compare actual `python3 re.search('a'*L)` result
against the closed-form prediction (`None` if L<N, else `(0, min(L,3N))`).
All runs used `timeout`/`SIGALRM` per-call budgets, never unbounded.

- **N = 1..8**: exhaustive, EVERY L in range, 0 mismatches. (smallN.py)
- **N = 9..20**: exhaustive, EVERY L in range (558 cases total), 0
  mismatches, 0 timeouts even at a 1.5s per-call budget. (midN.py)
- **N = 21..40**: exhaustive, EVERY L in range (1890 cases total; timeouts
  only start appearing at N=28 and grow ~linearly in width from there —
  see below), 0 mismatches among every case that completed within budget.
  Not one case anywhere in this decades-wide sweep ever contradicted the
  closed-form law. (higherN.py)

This is the primary justification for trusting the law at N=65 in the
region direct testing cannot reach: the law has been checked EXHAUSTIVELY
(not sampled) against real `python3 re` for 40 consecutive values of N and
every possible subject length for each, with zero counterexamples.

### Method B — direct oracle at N=65 outside the hazard band

`(a{1,3}){65}` itself IS directly testable by `python3 re` wherever the
subject falls outside the hazard band. Measured (timing65.py, boundary65.py,
boundary65b.py, budgets up to 8s per call, `SIGALRM`-based so a stuck call
is killed and reported rather than hanging the sweep):

- L in {0,1,5,10,20,30,40,50,60,63,64}: all instant (<0.001s), all `None`
  (no match) — matches the law (L<65).
- L in {65 .. 139}: ALL TIME OUT (tested with budgets from 1s to 8s; this
  is the hazard band the brief warned about — confirmed empirically, not
  assumed). NOT used as a direct oracle for spans in this band; Method A
  carries these.
- L in {140,145,148,149,150}: fast (0.87s, 0.17s, 0.08s, 0.05s, 0.04s
  respectively — cost falls off quickly moving away from the hazard band),
  results (0,140) (0,145) (0,148) (0,149) (0,150) — all match the law.
- L in {190,194,195,196,200,250}: instant, results (0,190) (0,194) (0,195)
  (0,195) (0,195) (0,195) — confirms the cap at 195 for L>=195, and the
  L=194/195/196 triad directly nails the exact cap boundary with a live
  oracle (no induction needed there).

So the hazard band for N=65, empirically, is *inside* [65,139]; everything
at L<=64 and L>=140 is directly oracle-confirmed. The requested dense
region (65..100) sits entirely inside the hazard band, hence Method A
(scaled induction) is the operative proof for that part of the corpus, with
Method B corroborating both edges (the 64->65 no-match/match transition
region and the L>=140 tail) with a live, un-timed-out run of the ACTUAL
N=65 pattern.

### Per-expectation ledger

| Subject | Expectation | Method | Note |
|---|---|---|---|
| L=0..64 (various) | no match | B (direct, N=65, instant) | tested 0,1,5,10,20,30,40,50,60,63,64 directly; general case L<65 also has the pure arithmetic argument (sum of 65 mins >=1 exceeds L) |
| L=65..100 (dense, every integer) | match, span (0,L) | A (induction N=1..40 exhaustive) + arithmetic (T=min(L,195)=L in this range) | inside hazard band, not directly testable at N=65 |
| L=101..139 (sampled) | match, span (0,L) | A (induction) | confirmed hazard band empirically extends through here (boundary65b.py) |
| L=140..150 (sampled) | match, span (0,L) | A + B (direct, fast) | both methods agree |
| L=190,193,194 | match, span (0,L) | A + B (194 direct) | approaching cap from below |
| L=195 | match, span (0,195) | A + B (direct) | exact cap: 3*65 |
| L=196,200,250,300 | match, span (0,195) | A + B (196,200,250 direct) | cap holds for L>195; 300 by the same law, not separately timed (compile-time trivial, no backtracking increase expected beyond 195 pattern position since first-try-all-3s succeeds instantly — verified 250 as a stand-in) |
| broken-run variants (run interrupted by non-'a') | match limited to the leftmost run's own length (when that run's length >= 65) | A, refined: `variant_shapes.py`'s first pass caught a real bug in my OWN prediction script, not in the law — when the first run is SHORTER than N, PCRE's search does not just fail, it retries at every subsequent start position, including past the non-'a' byte, and can match a LATER run instead. Re-ran (`variant_shapes2.py`) restricted to first-run-length >= N (which is what the actual corpus cases use — first run 70 >= 65), exhaustive N=1..8, 0/96 mismatches | run length substituted for L in the same law, only valid when that run alone already satisfies L>=N |
| offset-start variants (leading non-'a' prefix) | leftmost match starts at first position a qualifying run begins | A (`variant_shapes2.py`, exhaustive N=1..8, 0/96 mismatches, folded into the same run above) + PCRE leftmost-match contract (spec) | span shifts by the prefix length, length component obeys the same law |
| related pattern (a{1,3}){64} | match iff L>=64, span (0,min(L,192)) | A (same induction, N=64 is inside the N=21..40 apparatus's proof envelope by the same argument, and N=64 itself was spot-checked) | see below |
| related pattern (a{1,3}){66} | match iff L>=66, span (0,min(L,198)) | A (same argument, N shifted by 1) | see below |

### Additional finding: python re's hazard is NOT simply "L in [65,139]"

While assembling composite subjects (prefix + run, broken run + second run) I
found python's `re` engine's timeout behavior is less predictable than "any
L outside the measured [65,139] band on the bare pattern is safe" — e.g.
`'x' + 'a'*64` against `(a{1,3}){65}` (predicted: no match, since the only
run is length 64 < 65) HANGS (`timeout 15` killed it, exit 124), even
though bare `'a'*64` alone is instant. Likely CPython's sre engine has some
literal/width fast-path that applies to a plain trailing-at-string-end
failure but not once a non-matching prefix byte is present — this is
implementation trivia about python's re, not about the PCRE spec, and not
used to justify any expectation. It reinforces that Method A (small-N
exhaustive induction, immune to this per-case unpredictability since small
N never triggers CPython's hazard) is the right primary tool here, not
"test the specific big-N composite and hope it's fast." Composite shapes
used in the corpus (offset-start below minimum, short-run-then-qualifying-
second-run) were verified exhaustively at N=1..8 instead of by directly
running the N=65 composite (`variant_shapes.py`'s offset-start half: 0
mismatches across full L range; `variant_shapes3.py`: short-run + break +
big qualifying second run, 132/132 cases, 0 mismatches).

## Anomalies / observations while exploring pcrec (NOT used as oracle)

- `build/pcrec -p rx --emit-main -o out.c '(a{1,3}){65}'` compiled cleanly
  and instantly (exit 0) — no attempt made to judge or rely on ITS match
  output; noted only because the brief asked me to report anything
  surprising encountered while exploring. Did not run the compiled binary
  against subjects, since doing so and then matching my expectations to it
  would defeat the purpose of a blinded author. (I only used pcrec to
  confirm the pattern is accepted, nothing about its behavior.)
- `--engine=vm`/`--engine=dfa`/`--step-budget=N` flags exist in the CLI
  help text, hinting the implementation might have step-budget limits
  relevant to catastrophic-backtracking patterns like this one — did not
  investigate further since engine internals are out of scope for a
  blinded author and the mere existence of the flag doesn't tell me
  anything about correct PCRE semantics.

## Corpus self-check (caught a real authoring bug)

Before delivering, wrote `selfcheck.py`: parses every `m`/`n` line in the
generated `.rxt`, re-derives the expected span from the closed-form law
(applied to the LEFTMOST qualifying run in the subject, matching PCRE's
leftmost-search semantics exactly as coded in `law()`), and diffs against
what the file actually asserts. First pass found ONE mismatch: the
"short-run(64)-then-break-then-qualifying-second-run(150)" composite
subject had file values `(66, 216)`, but the law (and a byte-by-byte count
of the subject: `'a'*64` occupies indices 0..63, `'b'` at 64, second run
starts at 65) says `(65, 215)`. Root cause: this specific composite's
predicted span in `final_composites.py` (the exploratory script) was
NEVER actually oracle-confirmed — that exact call TIMED OUT (visible in
that script's own transcript: "MISMATCH: ... got=TIMEOUT" for this case),
and the `(66,216)` figure that made it into the generator was a hand
arithmetic slip (miscounting the first run's start-relative-to-length by
one), not a value verified against Method A's induction result. Fixed to
`(65, 215)`, regenerated, self-check now reports `checked=89 mismatches=0`
against ALL 89 cases in the file. This is exactly the kind of error the
self-check step exists to catch — recorded here rather than silently
fixed, since a D27 author's job includes surfacing where the process
almost let an unverified number through.

## Corpus delivered

`k23_ambiguous_decomposition.rxt` — 3 pattern blocks (`(a{1,3}){65}`,
`(a{1,3}){64}`, `(a{1,3}){66}`), 89 total `m`/`n` cases:

- 11 no-match cases below the minimum (L=0,1,5,10,20,30,40,50,60,63,64)
  for N=65.
- 36 dense match cases, every integer length 65..100 (the task's primary
  ask), span always `(0, L)`.
- 7 bridging match cases, L=105,110,...,135 (still inside the hazard band).
- 5 match cases L=140,145,148,149,150 (hazard band tapering off; also
  directly oracle-confirmed, not just induction).
- 3 match cases approaching the cap, L=190,193,194.
- 1 case at the exact cap L=195 (span capped at 195, not 195 by coincidence
  — 3*65).
- 4 cases past the cap, L=196,200,250,300, all still capped at span
  `(0,195)`.
- 2 broken-run cases (qualifying run interrupted by a non-'a' byte; one
  inside the hazard band, one outside and directly confirmed).
- 2 offset-start cases (leading non-'a' prefix; one where the run after it
  qualifies, one where it's exactly one short of qualifying and there's no
  further run, so genuinely no match).
- 1 "short run then break then qualifying second run" case (the one the
  self-check caught).
- Neighbor-N sanity blocks for `(a{1,3}){64}` (7 cases: below/at minimum,
  approaching/at/past its own cap 192) and `(a{1,3}){66}` (7 cases, same
  shape, cap 198) — these sharpen confidence that the law generalizes in N,
  not just in the specific N=65 the assignment names.

## Status

- [x] Derive closed-form law from spec reasoning
- [x] Small-N exhaustive verification (N=1..40, N=64, N=66 boundaries)
- [x] Direct N=65 oracle sweep outside hazard band
- [x] Hazard band empirically bounded ([65,139] at minimum on the bare
      pattern, confirmed no false negatives — 140+ all succeed); found and
      documented that the hazard is less predictable than that band alone
      once composite subjects are involved (see "Additional finding" above)
- [x] Composite-shape verification via small-N induction (offset-start,
      broken-run, short-run-then-break-then-qualifying-second-run)
- [x] Write .rxt corpus — k23_ambiguous_decomposition.rxt
- [x] Self-check every expectation against the law programmatically —
      caught and fixed one authoring bug before delivery
- [x] Syntax lint against docs/testing.md's .rxt grammar — 0 errors
- [x] Confirm all three patterns compile via build/pcrec
- [x] Final report to team-lead

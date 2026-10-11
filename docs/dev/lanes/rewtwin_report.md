# rewtwin — the `rev-end-width` twin, measured (2026-10-11, lane rewtwin)

[OPT-REVEND]'s filed sibling `rev-end-width` is K103's fix shape (b). Frank
approved its MEASUREMENT on 2026-10-11, with no build for merge. The
question: an end-pinned FIXED-WIDTH pattern needs no reverse walk, only a
direct test at n − W. Does that remove K103's entry floor on bench O-96
(c)2's litrun cells, and by how much? Scratch tier, Linux dev box (Ryzen 7
7700X, gcc 15.2), main 2f438878 (abi 74).

Branches:
- `lane/rewtwin` (this report and `docs/dev/optloop/rewtwin/`).
- `lane/rewtwin-scratch` (the twin, `src/gen/emit_dfa.c` only, NOT for
  merge; tip 71ebfc5b, patch in `docs/dev/optloop/rewtwin/twin.patch`).

## 0. Verdict

**On this box there is no K103 entry floor on these cells for rev-end-width
to remove.** The bench's regression does not reproduce here.
- Today's `rev-end` walk is already 1.7-2.6x FASTER than `-fno-rev-end` (the
  pre-REVEND end window) on every cell O-96 (c)2 names, except
  `wild-secrets-github-pat`.
- That holds for `alt-foo-tails`, `lit-l2/l4/l8/l31/l40`, aws and `abc$`, in
  caps and nocaps, on short and long subjects.

**Measured against today, rev-end-width is a real but selective win, and only
when the verify is inlined.** Short-subject medians, nocaps; layout bands are
within ±2% of each median:

| cell | W | today | twin, verify-at CALL | twin, verify-at INLINED | -fno-rev-end |
|---|---|---|---|---|---|
| `lit-l2` whole | 2 | 2.07 ns | 2.80 (x1.35) | 2.09 (x1.01) | 4.56 (x2.21) |
| `lit-l4` whole | 4 | 2.04 | 2.59 (x1.27) | 2.09 (x1.02) | 4.03 (x1.97) |
| `lit-l8` whole | 8 | 2.18 | 1.94 (x0.89) | 1.78 (x0.81) | 3.72 (x1.70) |
| `lit-l31` whole | 31 | 1.91 | 1.38 (x0.73) | 1.44 (x0.76) | 2.21 (x1.16) |
| `lit-l40` whole | 40 | 2.05 | 1.35 (x0.66) | 1.41 (x0.69) | 3.85 (x1.88) |
| aws whole (nocaps) | 20 | 3.78 | 2.28 (x0.60) | 2.12 (x0.56) | 9.97 (x2.64) |
| github-pat whole (nocaps) | 93 | 17.02 | 4.83 (x0.28) | 4.81 (x0.28) | 13.68 (x0.80) |
| `(?:abc$)\z` (ctrl-abc-dollar whole) | 3 | 1.97 | 2.63 (x1.34) | 2.08 (x1.06) | 4.11 (x2.09) |
| `abc$` plain (two seeds) | 3 | 3.19 | 4.03 (x1.26) | 2.51 (x0.79) | 4.65 (x1.46) |
| `alt-foo-tails` whole | 4..6, not fixed | 2.57 | n/a | n/a | 5.58 (x2.17) |

The rows break into four groups:
- **K103's named floor is real in the `$` two-seed loop.** `abc$` plain loses
  21% (3.19 → 2.51 ns) with the inlined twin. That is the one cell here where
  the rev-end entry itself is the cost.
- **The walk is the cost where W is long or the tail is unselective.**
  - `lit-l31`/`lit-l40` lose 24-31%.
  - aws (nocaps) loses 44%.
  - github-pat (nocaps) loses 72%.
- **The short literals (W ≤ 4) gain nothing.** The inlined twin reads +1..+6%,
  at the edge of the band. As a CALL to `rx_match`, the simplest spelling,
  they lose 27-35%. So a build must emit the verify inline.
- **`alt-foo-tails` is out of scope.** It is not fixed width. Its bounded-width
  generalization (AT over n−6..n−4) IS the old end window, which reads 2.2x
  slower here.

On the long regime (the ~64 KiB throughput subjects, which for `lit-lN` are
tiled FULL matches), the inlined twin costs:
- +2..+14% on literals: `lit-l40` is the worst at x1.14, because a W-byte
  forward verify replaces a W-byte reverse walk, plus the verify's prologue.
- −7% on aws and −93% on github-pat.

**A finding the brief did not ask for:** github-pat shows a REVEND
regression of its own, separate from K103's entry floor.
- The reverse walk reads the 82-byte `[0-9a-zA-Z_]` tail before it reaches
  the selective `github_pat_` head.
- Today costs 32.9 ns per call on letter-tile subjects. The pre-REVEND window
  (a memchr/run-pinned dismissal) costs 3.3 ns, and the twin 2.4-2.9 ns.
- On the bench's own short subjects, today is x1.24 slower than
  `-fno-rev-end` here, against x1.022 at the bench.
- The **auto (caps) artifact is a VM hybrid**, which the scratch twin does not
  reach (it is DFA-entry only), so auto still pays it: 34.2 ns against 3.4 ns
  at `-fno-rev-end` on the long regime.
- A build must cover the hybrid's inlined body. The VM hat's `verify-at`
  already takes `AT` (`locate_finish.md` §2.3; FINISH take cells, VM
  {SPAN, AT}).

Against [OPT-REVEND]'s CHOSEN 10% trigger, the walk's share of the cell
(today minus the inlined twin, over today) is:
- github-pat 72%;
- aws 44%;
- `lit-l40` 31%, `lit-l31` 25%;
- `abc$` plain 21%, `lit-l8` 18%.

The trigger is MET on this box for those six cells, and not met for
`lit-l2`/`lit-l4`/`(?:abc$)\z`.

## 1. Scope: which cells are fixed width, and the smallest general change

| cell (bench name) | pattern (bench `bench/litrun/patterns/*.rx`, published) | form | fixed W | end pin |
|---|---|---|---|---|
| `alt-foo-tails` | `foo.x\|foobar\|foo.` | `(?:P)\z` | no (4..6) | `\z` |
| `lit-l2/l4/l8/l31/l40` | the first L bytes of `a..zA..Z` | `(?:P)\z` | L | `\z` |
| `wild-secrets-aws-access-key-id` | `\b((?:A3T[A-Z0-9]\|AKIA\|…)[A-Z0-9]{16})\b` | `(?:P)\z` | 20 | `\z` |
| `wild-secrets-github-pat` | `\b(github_pat_[0-9a-zA-Z_]{82})\b` | `(?:P)\z` | 93 | `\z` |
| `ctrl-abc-dollar` (control, not in (c)2) | `abc$` | plain and whole | 3 | `$` plain / `\z` whole |

The pattern texts ARE published, in pcrec-bench `bench/litrun/patterns/` at
08985d99, read-only. The whole form is `(?:P)\z` (the bench's probes). So
I-146's relay ask (1) can be closed from the bench's own tree, and nothing
here needs relaying for it.

**The smallest general change is a guard relaxation in the RECOVER row
family plus one hand, not a new item.**
- `end-minus-width` (START-LANDING SL2) already holds the fact: W, from the
  `width` interval `[W,W]`.
- It takes only `EXISTS` today. `rev-end` asks RECOVER with the speculative
  `WINDOW` hand, and `n − W` for an unverified end would be a wrong answer
  (`start_landing.md` §3.3).
- The relaxation: `end-minus-width` also takes `WINDOW`. Under `WINDOW` it
  hands FINISH `AT` (a candidate start) rather than `START`. FINISH
  `verify-at` already takes `AT` on both CAND_ROUTE_DFA and the VM route.
- The `rev-end` walk's emitter reads RECOVER's action. On
  `CRA_END_MINUS_W` it writes the AT arms in place of the reverse block.
- So this is FACT REUSE at RECOVER plus a hand composition at FINISH. No new
  fact, no new LOCATE row, no new deny bit beyond the row's own
  (`-fno-start-width` would then deny both uses).

Three rules move with it:
- `emit_rev_end`'s assertion that the walk selected a walking RECOVER row
  (revend.md X3, `start_landing.md` §4.3).
- `table-recover-start-unproved`, the self-check that a non-walking row
  takes only hands carrying `CT_START`. It needs the row's WINDOW take to
  declare `CT_AT`.
- `start_landing.md` §3.3's "the three rows that answer without walking take
  only an ask that carries existence". That rule is still true: under
  `WINDOW` this row does not ANSWER, it proposes a point that FINISH verifies.

**`$` and its two seeds.** Fixed width makes the two seeds independent:
- A match ending at n−1 starts at n−1−W, and one ending at n starts at n−W.
- So the leftmost candidate is n−1−W. It exists only when `s[n−1] == '\n'`
  and the pin is `$`/`\Z`.
- The twin tries n−1−W first, then n−W. The first verify that matches is
  the leftmost match. Its end is START + W by the width fact, so no ENDSET
  or tie arm exists: K103 fix shape (a)'s single-seed fast path falls out
  for free.
- Witnesses in the identity sweep: `(?:a\s)$`, `(?:a\n)$`, `\n$`,
  `(?:\n\n)$`, `a\b$`, `(?:x$|y\z)` (mixed pins), `\bab$`, `(?<=x)ab\z`
  (context before the start) and `a(?=b)b$`.

**Encoding obligation (found by the sweep).** Under `-e utf8`, n − W can sit
inside a character.
- The match-here entry then refuses with `PCREC_ERR_STARTPOS`, which the
  first twin returned as an error. That is 890-4,779 differing cells per
  utf8 row.
- The scratch twin therefore declines where the encoding has non-boundary
  positions (`PcrecEnc.start_cls`, the end window's own decline).
- A build owes either that decline or a boundary test at the candidate. A
  candidate that is not a character start is "no match starts here", never an
  error.

## 2. The twin and its identity

The scratch change (`twin.patch`, 50 lines) sits in `emit_rev_end`. The
conditions are:
- a fixed width, from `pcrec_fact_width` with `bmin == bmax`;
- a DFA-hat entry (`cand_finish_of != CAND_ROUTE_VM`);
- no relocate;
- a byte-boundary encoding.

Under those conditions the search body is the seed loop above, with each
candidate handed to `<prefix>_match` (the existing T2 tie arm's own spelling).
It is the real emitter's output, not a hand edit.

The `twininl` timing arm is the only hand edit: `__attribute__((flatten))` on
`rx_search`, so gcc inlines the verify. It cannot change an answer, and it was
not separately swept.

Identity (`identity.py`, transcript `identity.log`): today, the twin and
`-fno-rev-end` were each compared with libpcre2-8 10.46 at every start
position:
- 70 rows: 14 litrun whole forms, `abc$` plain, 16 `$`/`\Z`/`\z` witnesses
  and 4 utf8 rows, each in caps and nocaps.
- 6,072,394 cells per artifact.
- **0 differences** on any artifact.
- The subjects were the bench's 27 short and 27 throughput subjects (the
  last 200 bytes of each throughput subject), six edits of each (appended
  `\n`, `\n\n`, a prefix byte, truncation, and others), and an exhaustive
  sweep to length 5-6 over a per-row alphabet that includes `\n`.

## 3. Timing method

- `timing_pad.py`: each arm is alone in its own binary, behind 8 `.skip`
  pads (0..112 step 16, K87's control), built with `-O2
  -falign-functions=64`.
- Runs were pinned with `taskset -c 3`: 3 rounds x 8 pads with the arms
  rotated, each launch the median of 9 timed passes.
- One `rx_search(s, n, 0)` call per subject. Short = the 27 litrun short
  subjects (the whole-subject cell's call); long = the 27 throughput subjects.
- Two runs: run 1 (three arms, load1 0.98) and run 2 (four arms, load1
  1.06-1.13). Their shared arms agree to about 1%.
- Layout bands (min..max of the per-pad medians) are ±1-2% except one pad
  of `lit-l2` twin in run 1 (4.50).
- The first shape, four artifacts in one binary (`timing_onebinary.tsv`), is
  kept but NOT the record. In that binary a second copy of today's identical
  text read x1.21-x1.30 off the first, which is the scale of every K103
  number.

Full tables: `summary_run2.txt` (of record) and `summary_run1.txt`.

## 4. Open, and for relay

- **The bench's litrun regression does not reproduce on Zen 4.** Here
  `-fno-rev-end` is x1.7-x2.6 SLOWER than rev-end where O-96 (c)2 read rev-end
  2-8% slower. Two causes are possible:
  - the box: the bench's Ryzen 5 1600 is Zen 1;
  - the comparison: the bench compared a15fb77b with 7388f1c0, while
    `-fno-rev-end` on main also carries START-LANDING's `end-minus-width`
    and today's prefilter rows.

  For relay: does the bench's whole-form short cell call `rx_search(s, n, 0)`
  once per subject? A same-pin `-fno-rev-end` arm at the bench would settle
  the box question.
- **The github-pat class-tail cost is a REVEND cost on AUTO.** The VM hybrid's
  inlined walk costs x1.24 on short subjects and x10 on a class-tail subject.
  It should be filed with REVEND's remainder. rev-end-width covers it only if
  the build reaches the hybrid's inlined body.
- **Not measured:** the Mac, utf8 (declined), and a cost row choosing between
  the walk and the width test. The data show the inlined width test is never
  worse than +14% (`lit-l40`, tiled full matches) and usually a win, so no
  selector is indicated by this evidence.

## 5. Validation

- Identity: COMPLETE, 0 differences (`docs/dev/optloop/rewtwin/identity.log`).
- Timing: COMPLETE, two runs, transcripts in the same directory.
- `make test-spec-history`: run at delivery (the docs this lane adds). Its
  result is in the handback message.
- No `make test`: nothing under `src/` on `lane/rewtwin`.

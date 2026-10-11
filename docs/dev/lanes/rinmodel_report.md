# rinmodel — G2's factor-free arm: the soundness re-run (D151 addendum 5)

**Lane `rinmodel`, 2026-10-11, sonnet. Model + transcripts + docs only: nothing under `src/`.**
Pin: main `96474022`. Linux dev box, python 3.14.4, **libpcre2 10.46 2025-08-27** (the
reference; `PCRE2_LIB=/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0`). Instrument and outputs:
`docs/design/where_to_start/` (`rinner_model.py`, `rinner_model_{byte,utf8}.txt` regenerated,
`rinner_model_{byte,utf8}_xl.txt`, `rinner_model_shaped.txt`, `rinner_model_checkarm.txt`).

## 0. Verdict

**The factor-free arm is sound on every population run: 0 wrong answers among the splits
admitted ONLY by it, and the checks can fail.**

| population | seed x n | arm-3-ONLY cases / single-search checks / find-all | wrong (tactic, lowerbound, rust_guard, fallback, floor; single + find-all) |
|---|---|---|---|
| byte (previous population) | 1 x 6000 | 200 / 13,940 / 2,400 | **0** |
| utf8 (previous population) | 2 x 4000 | 93 / 6,484 / 1,116 | **0** |
| byte XL (longer + bordered L) | 3 x 6000 | 200 / 13,733 / 2,400 | **0** |
| utf8 XL | 5 x 6000 | 111 / 7,661 / 1,332 | **0** |
| shaped (altwide/sfx-64, sfx-256, `[a-z]+xy` family) | seed 7, 200 subj/case | sfx-64/256 (+ hot-pool twins) admitted ONLY by arm 3 | **0** |

(The `tactic(c)` end, `c_end[factor-free]`: 252 / 52 / 86 / 63 checks, 0 wrong.) The literal
arms' own rows are unchanged: `tactic` 192,079 checks byte and 137,692 utf8, 0 wrong. Libpcre2
10.46 IS the model's oracle (the oracle is its unanchored `pcre2_match` loop), so "the model's
own oracle" and "libpcre2 10.46" are one check, not two; the independent controls on the ARM
itself are in section 3.

## 1. What changed in the model

- **The arm, as its own conjunct, decided on P's automaton.** `factor_witness(P, L)`: parse
  the generator's P text to an AST, Thompson-NFA it (views and lookarounds become epsilon, a
  SUPERSET of P's language, so the arm only errs toward declining; lazy/possessive/atomic do
  not change the language), then a Dijkstra over (NFA state, KMP state of L's occurrence
  automaton). L is a factor of some string of P iff `(accepting, L fully matched)` is
  reachable; the distance is the shortest witness. `border_free(L)` is a property of L alone.
  `arm = no factor AND border_free`. No pattern list is consulted.
- **`gate()` has three arms** (`fixed-width`, `cannot-contain-L`, `factor-free`) in that
  order; reasons are the old ones plus `P-factor-free`. `--arms literal` switches arm 3 off
  and reproduces the committed pre-arm transcripts: every row of the old byte and utf8
  transcripts is identical (`diff -w`) except the informational "reverse-walk bytes" counter,
  which the new `floor` variants also feed.
- **Rows keyed `[factor-free]`** for every sound variant (`tactic`, `lowerbound`, `rust_guard`,
  `fallback`, `c_end`, `floor`) are the splits ONLY arm 3 admits; the unkeyed rows are the
  literal arms' (so they cannot be diluted by the new population).
- **New variant `floor`**: the reverse walk stops at the previous hit's first byte
  (`lo = prev_j + 1`), the linearity argument of `where_to_start.md` 2.7 that the arm must
  also deliver. Applied where P is not fixed width (a fixed-width P's one start can lie
  before the previous hit; its walk is bounded by w instead).
- **Per-arm report** at the top of every transcript (cases and single-search checks, arms
  overlap), plus `factor-free ONLY`.

## 2. How many extra splits the arm admits

Over the previous populations (G1-passing cases; "literal" = fixed-width or cannot-contain-L):

| | literal arms | arm 3 (all) | **arm 3 ONLY** | gain |
|---|---|---|---|---|
| byte 6000 | 2,769 cases / 192,079 checks | 2,235 / 154,912 | **200 / 13,940** | +7.2% cases, +7.3% checks |
| utf8 4000 | 1,998 cases / 137,692 checks | 1,533 / 105,866 | **93 / 6,484** | +4.7% cases, +4.7% checks |

The random P-alphabet is 3-4 characters, so arm 3 rarely separates from the alphabet arm;
on the bench's shapes (a wide alphabet, a multi-byte L no stem contains) it is the ONLY
admitting arm: the shaped run decides sfx-64 and sfx-256 on the automaton (P width 3..9,
alphabet 26, no string of P contains `ing`, `ing` border-free) and reports
`admitted by literal arms=False, ONLY by arm 3=True`.

## 3. Controls

1. **The arm's decision procedure against two independent sources** (`--check-arm`,
   `rinner_model_checkarm.txt`; 3,000 cases byte + 3,000 utf8; libpcre2 not involved):
   (a) brute-force enumeration with python `re` of every string over the alphabet up to
   length 6, for view/lookaround/atomic-free P (1,627 + 1,624 cases, 610 + 543 with a factor):
   0 UNSOUND (brute found a factor string the automaton denies) and 0 INCOMPLETE (automaton
   witness of length <= 6 that brute cannot find); (b) the generator's own width/alphabet
   bookkeeping against the parsed AST's `ast_info`: 0 mismatches over 6,000. Sabotage: with
   the factor test's accepting condition disabled, `--check-arm` FAILS (factor-present 0).
2. **Negative controls (admit a split the arm refuses; the model must find wrong answers):**

   | control | byte 1 | utf8 2 | byte XL 3 | utf8 XL 5 |
   |---|---|---|---|---|
   | `neg_factor` (P contains L, L border-free), plain tactic | 19 / 60,443 | 1 / 34,454 | 0 / 31,323 | 1 / 27,171 |
   | `neg_factor_floor` (same, walk floored at the previous hit) | **702** | **214** | **256** | **226** |
   | `neg_border` (P factor-free, L bordered), plain tactic | 0 / 5,738 | 0 / 3,752 | 0 / 18,158 | 0 / 15,104 |
   | `neg_border_floor` | 13 | 0 | 18 | 9 |

   Both conjuncts of the arm are therefore LOAD-BEARING for the floored walk, and the check
   demonstrably fails when a conjunct is dropped. Honest nuance: the PLAIN (unfloored)
   tactic is wrong only rarely without the factor conjunct (the same ~1-in-7,000 rate as
   the ungated population) and never in this population without the border conjunct; the
   border conjunct is what the FLOORED walk needs (a crossing occurrence puts a legitimate
   start at or before the previous hit). If the build ships the floored walk (it does,
   locate_finish 4.6 / D151: "stops at the previous hit"), both conjuncts are required.
3. **Shaped cases (`--shaped`, `rinner_model_shaped.txt`)**, arm decided on the automaton,
   libpcre2 10.46 oracle, every startpos plus find-all:
   - `sfx-64-shaped`, `sfx-256-shaped` (+ `-hot` pools of near-misses `in`/`g`/`ng`, stems and
     `ing`): arm 3 = true, admitted ONLY by it; plain/floor/lowerbound **0 wrong**.
   - `sfx-64-NEG-stem-has-ing` (one stem `sing`): the automaton finds a 4-byte string of P
     containing `ing`, arm declines; floor walk WRONG (`ingsingingsinging3`: truth (10,18),
     got none).
   - `sfx-64-NEG-bordered-L` (L = `nin`, border `n`; stems ending `ni`): arm declines
     (border); floor walk WRONG (`3kaninin7kanikani`).
   - `[a-z]+xy` (S = `[0-9]`) and `[a-z]+xy`, S empty: arm declines (P contains `xy`); floor
     walk WRONG (`3xyxyyxy3` truth (1,9) got (2,9); `277xyoxy` truth (3,8) got (4,8)).
   - `[a-wz]+xy`, `[a-w]+xy`: admitted by the literal arm (and arm 3 agrees); 0 wrong.
   - `[a-z]{3}xy`: fixed width; 0 wrong.
4. **Sabotage of the gate itself** (below, section 5).

## 4. Findings worth acting on

- **`floor_end` is UNSOUND: the walk must stop at the previous hit's FIRST byte + 1, not at
  its END.** Informational variant (reverse walk floored at `prev_j + |L|`): wrong under the
  LITERAL arms too (byte: 17 / 64,336 single + 6 find-all, e.g. `(?:b{1,3}?)ab(?:...)` on
  `bababa` from 1: truth (2,6), got none), and under arm 3 (6 / 13,940). A true start can
  lie INSIDE the previous occurrence of L. Whoever builds the floor (locate_finish 4.6) must
  use "no start at or before the previous occurrence's first byte" (`floor`: 0 wrong in every
  population), NOT "after its end".
- **D151 add. 5's "today 0 / 145,598 ungated-split failures"** reads backwards: 145,598 is
  the byte + utf8 UNGATED split-ambiguous check count and the ungated tactic is wrong on it
  19 + 1 times (where_to_start 2.3); the 0 is the GATED tactic's. The control that must hold
  is the gated, `[factor-free]`-keyed rows (all 0, above).
- In UTF mode the model's `fixed-width` arm uses CHARACTER widths (the generator's); the
  design says BYTE width (K49/K50). Unchanged by this lane; the utf8 rows are 0 wrong either
  way. The arm-3 factor test is character-level, which equals the byte-level test for a
  well-formed L in valid UTF-8 (self-synchronizing).
- A fixed-width P can lie before the previous hit, so `floor` is not asserted there; arm 3
  and the alphabet arm both deliver it. Arm 3 inherits the alphabet arm's linearity
  (`where_to_start` 2.7: a walk reads a suffix of a P string that contains no whole earlier
  occurrence and, L being border-free, none that crosses one).

## 5. Sabotage rows (the model's own)

Both conjuncts were disabled in scratch copies (`build/`, not committed) and the
byte seed-1 / XL seed-3 populations re-run; `--selftest` must go red and the
`[factor-free]` rows must find wrong answers:

| sabotage | where | result |
|---|---|---|
| factor test blind (`factor_witness` never reaches its accepting target, so every P is "factor-free") | byte 1 x 6000: arm-3 admits 3,503 cases (was 2,235) | `tactic[factor-free]` **19** wrong / 74,383 (find-all 6 / 12,840), `floor[factor-free]` **702** / 74,383 (find-all 225); selftest FAIL |
| border test blind (`border_free` always true) | XL 3 x 6000: arm-3 admits 3,129 cases (was 1,687) | `tactic[factor-free]` 0, `floor[factor-free]` **18** / 31,891 (find-all 7); selftest FAIL (gated floor, gated c_end, neg_border never wrong) |
| `factor_witness` blind, `--check-arm` | 1,500 cases | factor-present 0 vs 288, FAIL |

(The sabotage runs exposed one model defect, fixed: `find_all` could loop forever on a
WRONG variant whose answers do not advance, which blind-factor made reachable; it now caps
the list at `4*len(subject)+8` entries. A sound variant yields at most `len+1`; both
committed transcripts regenerate byte-identically with the cap.)

## 6. Validation

- `rinner_model.py --selftest` PASS on all four populations (gated rows 0, every mutation
  detected, ungated wrong at least once, arm-3 population non-empty, `neg_factor` wrong
  somewhere; XL runs also require `neg_border` wrong somewhere).
- `--shaped 200 --seed 7` PASS; `--check-arm` PASS x2.
- `make test-spec-history`: `make test-spec-history` 145 passed / 0 failed (run async, `build/spechist2.log`, after the report and both CLAUDE.md edits).

Re-run: `PCRE2_LIB=<10.46 so> python3 docs/design/where_to_start/rinner_model.py --n 6000 --seed 1 --selftest`
(~15 s); `--n 4000 --seed 2 --utf8`; `--xl` with seeds 3 / `--utf8` 5 (6000); `--shaped 200 --seed 7`;
`--check-arm 3000 --seed 5` and `--check-arm 3000 --seed 6 --utf8`.

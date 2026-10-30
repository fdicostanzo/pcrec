# Critic SOUND (landwalk2): the stage-1 rules applied to pcrec's real machines vs libpcre2 10.46

Lens: soundness. Subject: docs/dev/lanes/p1dsg2_report.md @ 99447aa2a. Tree: worktrees/crit-landwalk2 (main 02a054851).

**Method (the twin is mine, `sound/drv.c` + `sound/run.sh`).** For each witness R = P·L·S:
- ML is pcrec's OWN machine: `pcrec -p m --features all --pattern '(?:P)L\z'`. Every one of these
  artifacts stamped `M_DFA_SCAN "rev-end"`, i.e. pcrec's `emit_rev_end_one_seed` walk over the reverse
  DFA of P·L, seeded at the end and floored at `search_from` with the existing floor code
  (`dir_rev_bound_accept`). Calling it as `m_search(s, j+|L|, search_from)` on the subject TRUNCATED at
  j+|L| returns exactly s*(j) = min starts(j) ∩ [search_from, j] (the walk the design describes, seed
  = the hit's end). Caveat: truncation hides bytes past j+|L| from ML; that is the design's model too
  (ML = rev(P·L) reads nothing past L), and no admitted witness of mine has a lookaround in P reaching
  past L.
- The verify A is pcrec's own anchored entry `r_match` (R's artifact, default flags); the LOWER
  hand-off is `r_search(s, n, s*(j))` (a correct search from the bound).
- Hits: every position of L, overlapping, ascending from search_from.
- Find-all restarts at the previous match end. Truth: libpcre2 10.46 `pcre2_match` find-all on R.
- Two guard modes bracket the reach guard: G0 = never fires (pure per-hit), G1 = fires on EVERY hit
  after the first failed verify (reach = n), so every later hit hands LOWER(s*(j)) → search from s*(j).
- Control: an EXCLUSION-violating pattern `(?:c[a-z]*d|e)k[a-z!]*!` (L = `k` ∈ alphabet(P)) — the twin
  reports 22 wrong / 97,656 subjects in both modes (e.g. "cekcdk!": pcre2 (0,7), per-hit (1,7)): the
  twin sees the which-occurrence failure.

## Findings

**Bottom line.** Applied as written to pcrec's real machines, stage 1 moved NO answer: 0 wrong over
7,274,578 subjects across 15 admitted-shape patterns (table below). Every subject ran as a full
find-all under both guard modes (14.5M tactic find-alls), the 4 bench rows included. The argument is sound for the reason the design gives, and I re-derived
it: with EXCLUSION, every start for a later hit j' > j lies above j, because P's span would otherwise
cover L or a whole period of a self-overlapping L, which contains the excluded byte. With G4, a failed
verify at s\*(j) rules out every start in starts(j). So the first hit whose verify succeeds is the
leftmost match, and composite from s\*(j) after LOWER cannot miss a start below the bound. The
findings are about wording the build depends on, not the mechanism.

### SOUND-1 — §A1's "reach" must mean REACHABLE (one or more steps); read as one step, the rule calls a two-start machine UNIQUE
- **CONFIRMED** on pcrec's own reverse tables. Severity: answer (stage 2 only; stage 1 reads no
  UNIQUE), and doc now: §A1 is the D27 cell's brief. Effort: one word, plus one net row.
  Blast radius: stage 2's form choice F1/F2. § A1 "The rule".
- The rule reads "does `step(s, c)` reach a state `s'` that has ANY accepting pair". The DIRECT
  reading (s' = step(s,c)) and the TRANSITIVE reading (s' reachable from step(s,c)) differ.
- Witness: P·L = `(?:xy)?ab=`. In pcrec's reverse table of it (`sound/w/u-xyab/m.c`, 6 classes,
  6 states), the accept after `ab` steps on `y` to a NON-accepting state, which steps on `x` to an
  accepting one. DIRECT says UNIQUE; TRANSITIVE says NOT. A brute-force walk over every class
  string finds max |starts| = 2.
- Consequence, libpcre2 10.46 vs the per-hit tactic run on pcrec's ML and pcrec's VM verify, for
  R = `((?:xy)?ab)=\1`: **11 wrong / 488,281 subjects** (alphabet {x,y,a,b,=}, length ≤ 8). For example
  "xyab=aba": pcre2 (2,7), per-hit NOMATCH (one attempt at s\* = 0, where the group is "xyab").
- TRANSITIVE agreed with the brute-force truth on all 7 edge-free machines I checked: u-xyab, u-sim1
  (`\b\w*=x`: NOT, max 2, matching the design's SIM-1 row), wb-start (`\b[a-z]+@`, the dup-param
  shape: UNIQUE, max 1), nwb-start, nwb-null, alt-in, cls-s-ucp. DIRECT was wrong only on u-xyab.
  The design's own witness table has no accept → non-accept → accept shape, which is why its nine
  rows do not tell the readings apart.
- Fix: write "has a path from `step(s, c)` (zero or more further steps) to a state `s'` with ANY
  accepting pair", and add `((?:xy)?ab)=\1` / "xyab=aba" to [LANDWALK-VM]'s net.
- Repro: `sound/unique_tables.py sound/w/u-xyab/m.c`; `sound/w/u-xyab/drv '((?:xy)?ab)=\1' - 3d 0 x 'enum:78,79,61,62,3d:8'`.

### SOUND-2 — the hit stream MUST be every position of L, overlapping included; nothing in the build pins that
- **CONFIRMED** (sabotage of my own twin). Severity: answer, if the build's kit site does what a
  memmem loop does by default. Effort: one phrase in the kit-site fact, plus one sabotage row.
  Blast radius: every admitted L that overlaps itself (any periodic run). § Mechanism "The hits are
  ONE window request", Build plan step 8.
- The design says "the positions of L from `search_from`, ascending". A hit stream that resumes
  after a hit (`j + |L|`) skips overlapping occurrences. With EXCLUSION, an overlapping later hit can
  still own the leftmost start: with P nullable, or with P's span starting inside the earlier hit
  (L = `xa`-periodic, P ⊇ {a}).
- Witness on the admitted shape R = `[0-9]*aa[bc]` (L = `aa`, P = `[0-9]*`; pcrec: DFA, NEXT
  `memchr`, so it passes L1 and L6; EXCLUSION holds since `a` ∉ digits). With every overlapping hit:
  **0 wrong / 1,398,101 subjects**. With a non-overlapping stream: **59,658 wrong (G0) / 55,734 (G1)**.
  For example "00000aaabb": pcre2 (6,9), per-hit NOMATCH.
- D157 says facts only, so the fact must carry it: "every occurrence of L at or after
  `search_from`, overlapping occurrences included". Add the sabotage row "non-overlapping hit
  stream" to Build plan step 8, with this witness.
- Repro: `sound/w/nullper/drv '[0-9]*aa[bc]' - 6161 0 nov 'enum:30,61,62,63:10'` (`nov` = the
  sabotage; `x` = as designed).

### SOUND-3 — the (state, class) rule must read ML's table BEFORE the scan edge is applied
- **CONFIRMED** (by reading the emitted artifacts). Severity: doc. Effort: one sentence.
  § A1 / § Mechanism "The walk".
- The design gives ML `pcrec_scanedge_dfa`'s plain edge. In pcrec's emitted reverse walks, the edge
  adds STOP states (`m_reverse_is_stop`, `s >= 9u` in `sound/w/csv5b/m.c`) and a run loop
  (`m_reverse_scan3`) whose transitions are not in `next_state[]`.
- Applied naively to that emitted table, the rule reports `[^,\n]{0,2},` UNIQUE with a single start,
  but the true count is 3. The table hides the run.
- Of my 14 machines, 7 carry the edge (5b, qnt-plus, csv5b, periodic, lazy-bnd, wb-end, utf8-tail).
  I excluded them from SOUND-1's table check.
- Say that UNIQUE is decided on ML's DfaForm before `pcrec_scanedge_dfa`. That is stage 2's
  concern, but the sentence belongs in §A1 now.

### SOUND-4 — csv5's landmark is inside `(?:…){4}`, not at a top-level concat position (SUSPECTED)
- Severity: doc (population). Effort: small. § Selection rule "The landmark choice rule"; §Baselines
  row csv5.
- The choice rule takes "an inner required literal … at a top-level concat position `i` of R's
  single branch". csv5 = `(?:[^,\n]{0,32},){4}[^,\n]{0,32}` has no top-level literal unless the
  tree view unrolls `{4}`.
- If the view does unroll it, the only candidate that passes L7 is the FIRST `,` (P = `[^,\n]{0,32}`).
  Every later `,` has `,` in P's alphabet. With that L, the tactic is sound on csv5 (below).
- If the view does not unroll it, csv5 is a `split` decline, and stage 1 admits 3 bench rows, not 4.
- What would confirm it: the build's `back_walk` candidate list for csv5. I spent no compile on it.

## PROBED-AND-HELD

All rows: per-hit tactic on pcrec's own ML (`rev-end` of `(?:P)L\z`) + pcrec's own anchored verify of R,
find-all, vs libpcre2 10.46 find-all; G0 and G1 guard modes; "wrong" counts BOTH modes. Every R
stamped `R_ENGINE "dfa"` (route L1 passes) and an `R_DFA_PREFILTER` outside L6's decline list
(memchr / byte-class / byte-class-bounded / first-class-bounded). Enumerations are exhaustive over
every string up to the stated length on the stated alphabet. Repro: `sound/run.sh`, `sound/batch1.sh`;
binaries and the emitted C under `sound/w/<name>/`.

| witness (what it hunts) | R ; P / L | subjects | truth matches | wrong |
|---|---|---|---|---|
| bench qnt-plus | `a+b` ; `a+` / `b` | 29,524 ({a,b,c} ≤ 9) | 24,604 | 0 |
| bench 5b mask-email, real subject | 5b ; `[A-Za-z0-9._%+-]+` / `@` | acc-small whole file (3.93 MB, sha 7f97…e0a3) + its 17,500 lines | 830 + 830 | 0 |
| 5b, adversarial | same | 2,015,539 ({a,A,.,@,space,-} ≤ 8) | 12,096 | 0 |
| bench csv5 (L = first `,`, see SOUND-4) | csv5 ; `[^,\n]{0,32}` / `,` | 88,573 ({a,`,`,\n} ≤ 10) + 49 bench `bounded/subjects` files whole and per line | 12,012 + 3 | 0 |
| csv5 with a tight bound (P's {0,k} cap reached) | `(?:[^,\n]{0,2},){4}[^,\n]{0,2}` | 265,720 (≤ 11) | 39,637 | 0 |
| bench cls-s-ucp, utf8 (multi-byte P, ASCII L) | `a\sb` -e utf8 --ucp ; `a\s` / `b` | 299,593 ({a,b,sp,NBSP,U+2028,U+0085,é,\n} ≤ 6) + 91 `utf8/subjects` files | 11,285 + 1 | 0 |
| `\b` at P's start, the floor context in find-all | `\b[a-z]+@[a-z]+` | 88,573 ({a,@,-} ≤ 10) | 22,093 | 0 |
| `\B` at P's start | `\B[a-z]+@[a-z]+` | 88,573 | 6,925 | 0 |
| nullable P that starts with `\B` (accept AT the floor) | `\B[a-z]*@x` | 349,525 ({a,@,-,x} ≤ 9) | 125,611 | 0 |
| `\b` at P's end and at S's start (the j+\|L\| seam) | `[a-z]+\b=\b[a-z]*` | 88,573 ({a,=,sp} ≤ 10) | 22,093 | 0 |
| alternation inside one branch, several P parses | `(?:ab\|a)(?:c\|bc)*@(?:x\|xy)` | 2,015,539 ≤ 8 | 71,593 | 0 |
| lazy + bounded quantifiers in P | `[a-z]+?[0-9]{1,3}?@[a-z]+` | 88,573 ≤ 10 | 9,367 | 0 |
| periodic multi-byte L, restart inside a hit | `[0-9]+aa[0-9]?a?` ; L = `aa` | 265,720 ({0,a,b} ≤ 11) | 81,682 | 0 |
| periodic L with nullable P (SOUND-2's control) | `[0-9]*aa[bc]` ; L = `aa` | 1,398,101 ({0,a,b,c} ≤ 10) | 334,962 | 0 |
| utf8, ASCII L[0] with a multi-byte tail sharing a lead byte | `[a-z]+aé[a-z]*` -e utf8 ; L = `a`+`é` | 87,381 ({a,b,é,ê} ≤ 8) | 15,158 | 0 |
| utf8, negated class P over multi-byte bytes | `[^@\n]+@[^@\n]+` -e utf8 | 87,381 ({a,@,é,\n} ≤ 8) | 27,388 | 0 |

**Total: 7,274,578 subjects × 15 patterns-as-run, 0 wrong, 0 errors** (no give-up, no STARTPOS refusal
from composite entered at s\*(j) under utf8: the LOWER bound always landed on a character start).

**Held by the route or by the facts, so it never reaches the walk (1 compile or emit-facts each):**
- A lookahead in P whose window crosses past L (`[a-z]+(?=@[a-z])@[a-z]*`) is `RX_ENGINE "vm"`, so
  L1 declines it. Every DFA-viewable assertion has a one-character window. One placed at P's end
  reads only L[0], so ML = rev(P·L) never needs a byte past j+|L|. The seed needs no right-context
  view: L is a literal, and no assertion follows it inside P·L.
- A two-byte lookbehind at P's start (`(?<=ab)[a-z]+@x`) is `vm`, so L1 declines it and the
  one-byte floor context `subject[search_from-1]` is enough on every DFA-routed P. My twin still
  ran it (349,525 subjects, 9,696 matches, 0 wrong).
- UCP `\b` under utf8, where a one-byte floor class could not decide word-ness, is REFUSED at
  compile ("UCP \b is not built yet under encoding 'utf8'"), so it cannot reach the walk today.
  Re-probe at [UCP] U3/U4.
- Caseless landmarks (Kelvin U+212A / long s for `k`/`s` under `-e utf8 -i`, and the ASCII pair
  under byte `-i`): `--emit-facts` gives `req_set`/`req_byte`/`req_run` = none for `-i [0-9]+kx[0-9]`
  in both encodings, so L2 finds no candidate. `[a-z]+(?i:K)!` offers only `!`. No case-folded
  letter can become L on stage 1, so the hit stream never has to fold.
- The reach-guard hand-off: G1 enters composite from s\*(j) at EVERY hit after the first failed
  verify. It matched G0 and libpcre2 on every row above. No match starts below the bound, by the
  EXCLUSION argument.

**Controls (each proves the twin can see the failure):**
- EXCLUSION violated, `(?:c[a-z]*d|e)k[a-z!]*!`: 22 wrong / 97,656 in both modes.
- The non-overlapping hit stream: 59,658 / 55,734 wrong (SOUND-2).
- `((?:xy)?ab)=\1` under F1: 11 wrong / 488,281 (SOUND-1).

**UNIQUE rule on pcrec's reverse tables** (`sound/unique_tables.py`; DIRECT / TRANSITIVE / brute
max |starts| over every class string, capped at about 400k strings per machine):

| machine | DIRECT | TRANSITIVE | brute max |
|---|---|---|---|
| u-xyab `(?:xy)?ab=` | UNIQUE (wrong) | NOT | 2 |
| u-sim1 `\b\w*=x` | NOT | NOT | 2 |
| wb-start `\b[a-z]+@` | UNIQUE | UNIQUE | 1 |
| nwb-start, nwb-null | NOT | NOT | 7 |
| alt-in | UNIQUE | UNIQUE | 1 |
| cls-s-ucp `a\sb` | UNIQUE | UNIQUE | 1 |

The 7 edge-bearing machines are excluded (SOUND-3).

**Compile budget:** about 59 pcrec invocations (compiles and emit-facts), one process at a time,
all before 19:00. No `make` and no repo writes. Everything is under
`/var/tmp/pcrec-pcrec/scratch/crit-landwalk2/sound/`.

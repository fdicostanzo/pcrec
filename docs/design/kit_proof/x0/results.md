# X0 results: conj.py's reading against libpcre2 (kit_proof.md §6.4, §7 step X0)

## Revision 2.2 re-run (lane `x0fix` setup, lane `x0read` reading, 2026-10-21)

Reading of the queued job `530-x0fix-x0run` (rc 0, 1,063 s, 13:55-14:13; log ends
`== X0FIX RUN COMPLETE`; the earlier `110004` job was cancelled by hand), on lane `x0fix` at main `63a7c3315` + the revision 2.2 reading (kvdfa
reads the EMITTED entry constant; the eol view's gated final newline is in the hull;
C6 on both arms), `build/pcrec` of that tree, libpcre2-8 **10.46** (`10.46 2025-08-27`).
Instruments unchanged from x0oracle's (`x0pcre.c`, `x0.py`) plus the `plain-walk` plant.
Transcripts in `out/` (rev 2.2 names replace revision 2.1's; the 2.1 run is the section
below and git history). Population counted by `conj.py census` F (`conj.txt`).

### Verdict

**X0 PASSES on revision 2.2's reading.** Every check the brief names reads as follows:

- **Part 1** (per-position, per-byte set equality + the context x prefix x tail grid):
  **0 differences on every role**, including admitted (1,197 patterns: 43,800 prefix
  nodes x 256 bytes, 443,947,845 grid cells, 0 inconclusive).
- **Part 2** (the differential): **0 differences beyond U1.** The only red cell is
  `(()|^){0}[b]`, native and utf8 (975 + 614 differing cells, e.g. `"0b"` from 0: cover
  (1,2), PCRE2 none); no other item in any role differs.
- **R1** is closed: the six R1 patterns (ten items at default flags) now DECLINE at
  `entry-const` / `no-eol-view` and are no longer in any admitted role. **R2** is closed:
  the sites run reads 0 red (`(a$\n)|ab`, both encodings, was the red cell).
- **Witnesses** (32): 0 differences (28 admitted ones run, 4 declined ones are the
  decline controls).
- **Plants**: every conj.py plant and `plain-walk` is red on every mover that reaches
  it; every X0 self-plant is red (tables below).

One caveat, not a difference: **175 inconclusive part-1 cells per run on ONE pattern,
`(?:[a-z]{0,3}\z|x)[0-9]{3}`** (both encodings; roles admitted-R and admitted-out, so
four items). It reads `cover k=4` and both parts report 0 differences on it (its first
alternative can never match, so the language is `x[0-9]{3}`); the cells are bytes `[a-z]`
at depth 0 where hard partial matching reports a prefix but the witness search finds no
complete match (the over-approximation x0oracle's defect 1 describes), so they are
counted and compared on neither side. The admitted role proper has **0** inconclusive.
This pattern is new in the population: the revision 2.1 reading declined it at
`end-at-k` (the row-0 entry misread); revision 2.2's liveness and entry admit it.

### Population (`out/population.txt`)

| role | native flags | utf8 | revision 2.1 (x0oracle) | what |
|---|---:|---:|---|---|
| admitted | 613 | 584 | 613 / 584 | the 1,197 census whole-cover / context-join patterns (unchanged) |
| admitted-R | 57 | 56 | 62 / 59 | the `-fno-rev-end` arm; the 8 fewer are R1 items now declining |
| admitted-out | 46 | 45 | 51 / 48 | every other census DFA pattern the table admits at its own flags (K35) |
| site | 814 | 1,127 | 814 / 1,127 | every start-origin FIND site of a non-admitted artifact with a machine-stated exact prefix; 1,939 of 1,941 completed, the two utf8 stragglers (`\b[0-9a-f]{32}\b`, the `\b` UUID) are NOT RUN again |
| witness | 30 | 2 | 30 / 2 | `witnesses.txt` plus the plants' own witnesses |

admitted-out is 91 = 99 - 10 (R1 items now declined) + 2 (the new
`(?:[a-z]{0,3}\z|x)[0-9]{3}` items above).

### Counts

| role | items | part-1 nodes | part-1 grid cells | part-1 inconclusive | part-2 subjects | part-2 cells | differences |
|---|---:|---:|---:|---:|---:|---:|---|
| admitted | 1,197 | 43,800 | 443,947,845 | 0 | 3,145,314 | 18,948,760 | 1,589, all `(()|^){0}[b]` (U1) |
| admitted-R | 113 | 1,833 | 36,171,108 | 350 (one pattern) | 236,346 | 1,234,758 | 0 |
| admitted-out | 91 | 1,257 | 29,375,004 | 350 (one pattern) | 206,334 | 1,078,321 | 0 |
| site | 1,939 | 43,738 | n/a | 8,896 byte cells (4,697 native, 4,199 utf8; deep counted repeats and long alternation words, as at revision 2.1) | n/a | n/a | 0 |
| witness | 32 | 753 | 3,601,644 | 0 | 41,366 | 251,814 | 0 |

### The plants (X2 for X0), revision 2.2

Each plant's population is every census pattern (default and `-fno-rev-end` arms) whose
verdict or plan MOVES under the plant (`out/plantpop.txt`; capped at a seeded 300), plus
every witness. "red" = at least one part-1 or part-2 difference.

| plant | id | movers (red / run) | its witness |
|---|---|---|---|
| `cm1-all` | S1130 | 239 / 239 | `\bcat\b` red |
| `c8-skip` | S1131 | 54 / 54 | `ac|bd` red |
| `c9-depth-k` | S1136 | 0 census movers (as kit_proof says) | `ab|a$\n`, `ab|a\Z\n`, `ab|a$\n\z`: all red |
| `c9-eol-as-end` | S1139 | 53 / 55 | `cat$`, `cat\Z`, `\bcat$` under R red; the 2 green are `\d$(?!\n)` under R (both encodings), where the plant changes no answer (unchanged from 2.1) |
| `e0-row0` | S1140 | 76 / 76 (was 67 / 67: it now reaches the unseeded R1 shapes) | `(?<=x)cat` red |
| `c10-drop` | S1132 | 300 / 300 | `abc|ab` red |
| `absb-flip` | S1133 | 300 / 300 | `\bcat` red |
| `absa-flip` | S1134 | 300 / 300 | `(?m)done$` red |
| `plain-walk` | none (the S1130-S1150 range is full) | sites: red on `(a$\n)|ab` (both encodings), 2 of 77 movers; witnesses: red on the three K1 witnesses | R2's control |
| S1143 | | UNREACHED by design (kit_proof §6.3) | not run |
| S1150 | | `out/stated.txt`: the union-narrowing statements RED (3 lines), the per-thread slice green (2) | |
| S1149 | | the pass-through statements RED (3), the in-span slice green (3) | |

`plain-walk`'s 75 green movers are sites whose stated set moves under the plant but
still equal libpcre2's witnessed set; of the five R2 exposure shapes (`exposure.txt`:
`(a$\n)|ab`, `[ab]{2,}$\W`, `[ab]{2,}\Z\W`, `\w{0,2}?$\W`, `a$\n`) only `(a$\n)|ab` turns
red among the sites. I did not trace why the other four stay green (they are census
DFA patterns; whichever of them is a site is among the 75 green movers or inconclusive,
and `a$\n` now reads `no-eol-view` in `conj.txt` D).

**X0's own plants** (a seeded 150-pattern sample of the admitted set; native / utf8):
`drop-Ck` 80 / 70 red of 80 / 70, `flip-absA` 80 / 70, `over-S` 80 / 70, `under-S`
80 / 70, `k-plus-1` 80 / 70, `add-Cm1` 5 / 6 reached and 5 / 6 red (the other 75 / 64
are unseeded, whose `C_{-1}` is already all 256 bytes).

### Exposure (`out/exposure.txt`, `x0.py`'s sibling `exposure.py`)

Over every census pattern at its own flags (4,527 native / 4,938 utf8 patterns at default
flags, 2,099 / 2,392 DFA ones again under `-fno-rev-end`), the machines whose EMITTED
entry is not row 0: anchored machines 7 seeded + 74 unseeded (native, same utf8), forward
machines 1 + 33 at default and 9 + 80 under R, anchored-LANGUAGE machines 32 unseeded; all
of them view-carrying. R2's reach: 5 patterns at default flags (4 under R) whose language
gains a byte through an eol view. kvcensus's committed `sites.tsv.gz`/`patterns.tsv.gz`
were produced with the old reading, so their entry-derived columns (`starts()`, `whole()`,
`forward_path()`) and the hull of those view-carrying machines can move; regeneration is
filed as a follow-up, not run here.

---

# Revision 2.1 run (lane `x0oracle`) -- kept as the record the section above replaces


Lane `x0oracle`, 2026-10-21, worktree at main `d970abbbc` (abi 81), `build/pcrec` of
that tree, libpcre2-8 **10.46** (`10.46 2025-08-27`, the system `libpcre2-8.so.0.14.0`,
the only 8-bit library on the dev box, and the reference oracle kit_proof names).
gcc 15.2, Linux dev box. Compile-side and match-call only: nothing was timed. Instruments
`x0pcre.c`, `x0.py`, `stated.tsv`; transcripts `out/`. The reading is `conj.py` revision
2.1 unchanged (the `CONJ_PLANT`s added for X0 are off unless named; `conj.py census`
reproduces `conj.txt` A and B byte for byte on this tree).

## Verdict

**X0 does NOT pass.** On the population kit_proof §1.2 counts (the 1,197 census
whole-cover / context-join patterns `cover_conj[]` admits) the reading and libpcre2 agree
everywhere except the known U1 class: 0 differences beyond `(()|^){0}[b]`
(both encodings). But the same reading, applied where kit_proof says it will be applied
(every artifact, and the `-fno-rev-end` arm), has **two real defects**, each a
non-plant disagreement with libpcre2 beyond U1. Per the stop rule, `conj.py` is not
patched; the cells are below.

- **R1, the unseeded entry read as row 0** (wrong answers, admission). On an unseeded
  anchored machine `conj.py`'s `k_entry` takes `r0 = 0`, and kvdfa renumbers states
  assuming "row 0 = start". The emitter does not promise that: on `\Zx` it emits
  `anchored_state = 2;` (row 1), and row 0 is the eol view's TARGET. The reading walks
  from the wrong row, reads `S_0 = {x}`, and C9 never sees the view on the real entry,
  so an impossible body reads `cover k=1`. The `cover` entry would then answer (1,2) on
  `"Zx"` and (0,1) on `"x"`, where PCRE2 and pcrec's own artifact both give no match
  (checked on the emitted artifact, both flag arms). Six patterns, ten (flags, pattern)
  items at default flags and twenty with the `-fno-rev-end` arm:
  `\Zx`, `\zx`, `\zabc`, `-{0,}?\Z-` (native and utf8), `[ab]*\z\W`, `\w{0,2}?$\W`
  (native). Each has an unseeded entry constant ≠ 0 (2, 2, 4, 2, 3, 2) and a view table.
  This is sound-M1's error (`e(⊥)` is the emitted constant, never row 0) on the
  UNSEEDED arm, which revision 2 fixed only for seeded machines.
- **R2, the plain walk's hull drops eol-view transitions** (under-stated sets, sites).
  On a non-cover site the reading's `S_d` is kvdfa's walk over A's PLAIN table. A byte
  consumed only through an eol view is missing: `(a$\n)|ab` (a census site, native
  and utf8) reads `S_1 = {b}` where libpcre2's witnessed set is `{b, \n}` (`"a\n"`
  matches at the subject end). Used as a SENT set, that is a filter that skips a match.
  The three K1 witnesses (`ab|a$\n`, `ab|a\Z\n`, `ab|a$\n\z`) read the same way: their
  `cover` verdict correctly DECLINES at C9, but the hull `S_1` they would state is short.
  Consequence for kit_proof §5.2: its sentence "C8's equality of the two producers'
  `S_d` holds on such a body" is refuted. The slice states `S_1 = {b, \n}`, A's plain
  walk `{b}`, so C8 reads `exact/producers-disagree` on these bodies, which the trace
  build asserts never happens. Either C8's machine half must read through the eol view,
  or the assertion must exempt bodies that C9 declines.
- **K35: the census population undercounts what the table admits.** Run over every
  census DFA pattern at its own flags, `cover_conj[]` admits **99** (flags, pattern)
  items outside the census whole-cover / context-join population (51 native-flag, 48
  utf8), on top of the 1,197. Of those, 89 agree with libpcre2 everywhere; the 10 that
  do not are R1's default-flag items. kit_proof §1.2's "admitted patterns, all" row
  (77 / 665, 50 / 485) and B1's mover count are therefore low by these (they are not in
  kvcensus's whole/ctx text classes), and X1 at B1 must take its population from the
  table, not from the census classes.

## Population (`out/population.txt`)

| role | native flags | utf8 | what |
|---|---:|---:|---|
| admitted | 613 | 584 | the 1,197 census whole-cover / context-join patterns `cover_conj[]` admits (= kit_proof §1.2's 77+665 / 50+485 deduplicated) |
| admitted-R | 62 | 59 | the `-fno-rev-end` arm: every census DFA pattern admitted under the deny whose verdict or plan moves |
| admitted-out | 51 | 48 | every other census DFA pattern the table admits at its own flags (K35, above) |
| site | 814 | 1,127 | every start-origin FIND site of a non-admitted artifact whose machine reading states an exact prefix (census `exact` > 0, a machine source); 1,939 of 1,941 completed |
| witness | 30 | 2 | `witnesses.txt` plus the plants' own §6.3 witnesses |

## Part 1, the per-position, per-byte set equality

For d < k, every prefix node the oracle explores (the tree grows only through bytes
libpcre2 itself accepts, up to 64 nodes per depth native, 16 utf8) has all 256 bytes
asked, and its witnessed next set must EQUAL the reading's `S_d` (an under-stated set,
an over-stated set and a non-product language all fail at a node). At every node below
`k`, every tail is tried and no match may end below `k`. After every full-length prefix,
PCRE2's witnessed next set must be empty (no match runs past `k`). The context × prefix
× tail grid at `k` covers 257 contexts native and 449 under utf8 (each continuation byte
as the last byte of a 2-, 3- and 4-byte character and bare), 12 full-length prefixes,
and 257 tails (plus 3 completed characters per lead byte under utf8). It must give
length `k` or no match, and it must reproduce `C_{−1}` with absent-before and `C_k`
with absent-after. Further live contexts get their own tree.

| role | nodes | grid cells | red |
|---|---:|---:|---|
| admitted (1,197) | 43,764 | 443,943,231 | **0** |
| admitted-R (121) | 1,578 | 33,933,274 | R1: the 10 items (5,938 cells) |
| admitted-out (99) | 1,002 | 27,135,426 | R1: the 10 items (5,938 cells) |
| site (1,939) | 43,596 | n/a | R2 only (`(a$\n)|ab`, both encodings); 8,896 byte cells inconclusive |
| witness (32) | 740 | 3,601,901 | R2 hull on the three K1 witnesses only (15 cells) |

**Inconclusive cells** (a witness search that ran out of budget, or a site byte with no
witnessed match within `exact + 8` bytes) are compared on neither side and counted. There are
**0** on the admitted roles (the horizon there is `k`, the claimed match width). On sites there are 4,697 native and 4,199 utf8
such byte cells (deep counted repeats such as `a{500}` and `(ab){300}`, and long
alternation words). Two utf8 sites did not complete: `\b[0-9a-f]{32}\b` and the
`\b`-bounded UUID, both seeded, where every node asks 133 contexts × 256 bytes × a
20,000-call budget. They are recorded as NOT RUN.

## Part 2, the differential

The `cover` entry is simulated from the reading's plan against `pcre2_match` at every
startoffset (a continuation-byte startoffset under utf8 is skipped: the K50 guard
refuses it first) and through the find-all loop. Subjects: PCRE2's own full-length
prefixes alone, after and before every one of the 256 bytes, and between bytes; two
matches; every byte after a prefix and then an after-context byte (a match running past
`k`); every literal path of the body (text-derived, and PCRE2's prefixes) placed at the
subject end, alone, after every byte and before a final `\n`; set-edge-adjacent bytes
at every position; 150 random subjects with whole-alphabet noise; and under utf8, nine
ill-formed sequences and five multi-byte characters around each prefix.

| role | subjects | cells | differences |
|---|---:|---:|---|
| admitted | 3,146,435 | 18,953,560 | 1,509, every one on `(()|^){0}[b]` (U1; e.g. `"0b"` from 0: cover (1,2), PCRE2 none) |
| admitted-R | 237,289 | 1,220,517 | 29,158, all on R1's 10 items |
| admitted-out | 207,627 | 1,066,742 | 29,123, all on R1's 10 items |
| witness | 41,381 | 251,937 | 0 |

## The OWED witnesses

- **Per-thread** (`[r4rc R2]`): `a(?=b)[a-z]|ac` and `[ab](?<=a)c|bc` both read
  `cover k=2` on the machine half (now in `conj.txt` D and `witnesses.txt`). X0 finds
  both set-equal to libpcre2 with 0 differential cells. S1150's check, the stated-set
  equality (`stated.tsv`, `out/stated.txt`), reads the union-narrowing plant's
  statements RED (`S_1 = {b}`: libpcre2's witnessed `S_1 = {b, c}`; `S_0 = {a}`:
  libpcre2 `{a, b}`; red as a HULL under-statement, whatever `exact_len` the plant
  claims). The correct per-thread slice statements (`S_1 = {b, c}`, exact_len 2;
  `S_0 = {a, b}`, exact_len 0) read green. **So the S1150 check can fail and can pass.**
- **In-span** (`[r4 B9]`): S1149's pass-through statements read RED (`a(?=b)[a-z]`
  with `S_1 = [a-z]`, `\w(?=\d)\w` with `S_1 = \w`, `[a-z0-9_ ]\b[a-z ]` with exact_len
  2) and the slice's in-span statements green.
- **K1**: `ab|a$\n`, `ab|a\Z\n` and `ab|a$\n\z` DECLINE at `no-eol-view` (unchanged)
  and their hull is R2.

## The plants (X2 for X0)

Each plant's population is every census pattern (B and `-fno-rev-end` arm) whose verdict
or plan MOVES under the plant (capped at a seeded sample of 300), plus every witness.
"red" means at least one part-1 or part-2 difference.

| plant | id | movers (red / run) | its §6.3 witness |
|---|---|---|---|
| `cm1-all` | S1130 | 239 / 239 | `\bcat\b`: red (`"0cat"` from 0: cover (1,4), PCRE2 none) |
| `c8-skip` | S1131 | 54 / 54 | `ac\|bd`: red (`"bc"`: cover (0,2), PCRE2 none) |
| `c9-depth-k` | S1136 | 0 movers in the census (as kit_proof says) | `ab\|a$\n`, `ab\|a\Z\n`, `ab\|a$\n\z`: all red (`"a\n"` from 0: cover none, PCRE2 (0,2)) |
| `c9-eol-as-end` | S1139 | 53 / 55 | `cat$`, `cat\Z`, `\bcat$` under R: all red (`"cat\n"`: cover none, PCRE2 (0,3)) |
| `e0-row0` | S1140 | 67 / 67 | `(?<=x)cat`: red (`"cat"` from 0: cover (0,3), PCRE2 none) |
| `c10-drop` | S1132 | 300 / 300 | `abc\|ab`: red (`"abc"`: cover (0,2), PCRE2 (0,3)) |
| `absb-flip` | S1133 | 300 / 300 | `\bcat` red |
| `absa-flip` | S1134 | 300 / 300 | `(?m)done$` red |
| S1143 | — | UNREACHED by design (kit_proof §6.3) | not run |
| S1150 | — | the stated-set check above | red; the correct slice green |

The two `c9-eol-as-end` movers that stay green are `\d$(?!\n)` (both encodings). There
the eol view read as the end gives exactly PCRE2's language, because `$(?!\n)` holds
only at the very end, so that plant changes no answer on them. The first `c10-drop`
run let two movers through (`[a-z]+(?=@)`, `\x{e9}+\b`): nothing in X0 then asked
whether a match runs LONGER than `k` past a full-length prefix. That check (part 1) and
its subject family (part 2) were added, and both now go red (`"aa@"`: cover (1,2),
PCRE2 (0,2)).

**X0's own plants** on a seeded 150-pattern sample of the admitted set, each mutating
the reading's plan so X0 must go red: drop a byte from `S_{k−1}` (under-state) 150 /
150; add a byte to `S_0` (over-state) 150 / 150; drop a byte from `C_k` 150 / 150; flip
absent-after 150 / 150; report `c + k + 1` (S1144's plant) 150 / 150; add a byte to
`C_{−1}` 11 / 11 reached (the 139 others are unseeded, whose `C_{−1}` is already all
256 bytes, so the plant changes nothing there).

## Oracle defects found and fixed (each produced confident wrong cells first)

1. **Hard partial matching over-approximates "prefix of a match".** libpcre2 reports
   PARTIAL whenever the subject ends with an assertion pending: `(?:a*\b)*b` reads `a` as
   a prefix, `[a-c]*\ba` reads `b`, `\d*(?<=a)\w` reads digits after a digit context.
   The first full run (`build/x0/res_v1_partial.jsonl`, not kept as evidence) flagged
   these as reading under-statements. Every byte in the next set now needs a WITNESS: a
   complete match anchored at the origin whose span covers the prefix (`x0pcre.c` `Q`).
   kvcensus's `kvpcre.is_prefix` has the same over-approximation; its census cross-check
   sampled only 15% of rows (`docs/dev/kvcensus/census.py`), so that is a note for
   kvcensus, not a finding against this run.
2. **Under `MATCH_INVALID_UTF`, PARTIAL at the end of every valid fragment.** `@é` read
   `"@\xC3@"` as a prefix (`@` at position 2). The witness rule fixes it.
3. **libpcre2 10.46 answers an `ANCHORED` match that starts past a leading invalid
   sequence under `MATCH_INVALID_UTF`.** `a` on `"\x80a"` from 0 returns (1,2), and
   `(?(DEFINE)(?<g>a))(?&g)` on `"\x80"` returns PARTIAL at 1. Every anchored probe now
   requires the match to start at the origin. Such answers are counted (`K`, cumulative
   per oracle process, so no per-item figure) and refused. They are frequent under utf8,
   where every context and tail grid meets ill-formed bytes. This is an upstream observation, worth an
   `upstream_issues.md` entry; it does not touch pcrec, which never asks PCRE2.
4. **The witness horizon on sites.** A byte with no witnessed match within `exact + 8`
   bytes is INCONCLUSIVE, not "absent". It first read as an over-statement on `a{500}`,
   `(ab){300}` and `(?:yoslwssiyybw|…)`.
5. **`--plant` did not reach the workers.** Python 3.14's default start method is
   forkserver, so workers re-import `conj.py`. The plant now travels in
   `CONJ_PLANT`, and the invalid runs were discarded.

## The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime.** Not relevant: no clock is read. Every number is a count of
   match calls, nodes, cells and items, on one box with one library version (10.46).
2. **Independent control.** This IS the control. `x0pcre.c` shares no code with kvdfa or
   conj.py. Its sets grow only from libpcre2's answers, and the reading's sets choose no
   prefix and no node. They enter part 2 only as the plan under test and as extra
   subject material that libpcre2 then decides. K35: the population is recounted from the
   table itself (admitted-out). [MECH-REACH]: every plant's witness reaches (table above),
   S1143 is UNREACHED by design, and `add-Cm1`'s reach is counted.
3. **What moves when regenerated.** Nothing emitted. A new pcrec build, a new census or
   another libpcre2 version moves only these counts. X0 re-runs at Z2 on the slice
   (`stated` takes any producer's sets) and at B1 per kit_proof §7's re-run condition.

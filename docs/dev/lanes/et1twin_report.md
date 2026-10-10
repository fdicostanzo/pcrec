# et1twin — [ENG-TACTICS] stage 1's D77 trigger: K12 recount under G2 + reverse-inner hand twins

**Lane `et1twin`, 2026-10-10, opus. MEASUREMENT ONLY: nothing under `src/` changes.**
Pin: main `c87d20af` (abi 74), Linux dev box (Ryzen 7700X, gcc 15.2, libpcre2-8 10.46).
pcrec-bench at `f68448a6`, read only (subjects regenerated in a `git archive` copy,
throughput hashes checked against its manifests). Instruments and raw outputs:
`docs/dev/optloop/et1twin/` (own `CLAUDE.md`). **Every number is SCRATCH TIER.**

Charter: D151 addendum 4 — stage 1 = rev-inner's DFA hat, triggered by a hand twin on
the top K12 cells, counted after G2.

## 0. Answers first

@@ANSWERS@@

## 1. Step A — the recount

### 1.1 Method

- **Population.** `studies/walk_survey/k12_census.py` re-run at the pin over every
  bench pattern export: still **24 patterns** flagged K12. Two moved off the list's
  substance since the survey: `capability/tail-ext-lower-txt` and
  `tail-dotstar-txt` now compile `RX_DFA_SCAN "rev-end"` ([OPT-REVEND] 7388f1c0);
  the survey already excluded their cells as K1-owned, so the total does not move.
  `syntax/rec-define`, `loglines/uuid` and `wild-validator-uuid-grok` read
  `RX_DFA_START "end-minus-width"`.
- **Measure.** walk_survey's own instrument (`wsdrv5.c`, `m_gap` = forward-machine bytes
  stepped before each call's match start) re-run over the K12 patterns' bench cells at
  the pin (`run_pop.py`, config `default`), then `analyze.py` with the survey's own
  weights (`bench_times.tsv`): `est = bench median × m_gap / T`, K1-owned cells excluded.
  **Every surviving cell's `m_gap` is byte-identical to the survey's**: neither
  [OPT-REVEND] nor [START-LANDING] (b8337c33) touched a K12 cell's forward walk — the
  K12 cells still read `reverse-pass` (or `attempt-start`/`end-minus-width`) and the
  total re-measures at 15.786 ms (survey: 15.8).
- **The gates.** No `inner_split` fact exists yet, so G1/G2 are read by hand off each
  pattern's text, one row per pattern in `recount.py`'s table (the table IS the reading;
  it names the `P · L` split each verdict was read on). G2 is applied as
  `where_to_start.md` §2.4 states it: `fixed_width(P) ∨ ¬(bytes(L) ⊆ alphabet(P))`.
  A second column applies the FACTOR-FREE refinement this lane found necessary to
  read altwide (§1.3); it is reported, not counted as G2.

### 1.2 The recount table (`docs/dev/optloop/et1twin/recount.txt`)

Estimates are walk_survey's weights (ms, default config, K1-owned cells excluded).

| pattern | split P · L | G1 | G2 (formula) | G2 (factor-free) | today (DFA_START, handoff) | cells: regime est ms | verdict | note |
|---|---|---|---|---|---|---|---|---|
| `loglines/ipv6` | [0-9a-f]{1,4} · ':' (head of both branches) | y | y | y | reverse-pass, none | search_short 0.1430; throughput 5.6864 | **SURVIVES** | ':' not in [0-9a-f]; the split reads through the top-level alternation's common head |
| `altwide/sfx-64` | 64 stems · 'ing' (S empty) | y | n | y | reverse-pass, 9 | search_short 0.0000; throughput 2.2592 | **REFINED-ONLY** | stems span a-z (i,n,g in alphabet(P)), widths 3-9; no stem contains 'ing', 'ing' border-free |
| `altwide/sfx-256` | 256 stems · 'ing' | y | n | y | reverse-pass, 9 | search_short 0.0000; throughput 2.1245 | **REFINED-ONLY** | as sfx-64 |
| `altwide/sfx-512` | 512 stems · 'ing' | y | n | y | reverse-pass, 9 | search_short 0.0000; throughput 1.4328 | **REFINED-ONLY** | as sfx-64 |
| `syntax/cls-s-uc` | \S+ · '@' | y | n | n | reverse-pass, none | search_short 0.0000; throughput 1.4140 | **FAILS-G2** | '@' is in \S; P contains '@' as a factor |
| `email/orig` | local part · '@' | y | n | n | reverse-pass, none | search_short 0.0007; throughput 0.8973 | **FAILS-G2** | the quoted local part's class \x23-\x5b holds '@': genuinely ambiguous split |
| `email/factored` | local part · '@' | y | n | n | reverse-pass, none | search_short 0.0007; throughput 0.8939 | **FAILS-G2** | as email/orig |
| `capability/wild-logparse-syslogbase-expanded` | timestamp prefix · ':' | n | y | y | reverse-pass, none | search_short 0.0001; throughput 0.8045 | **OFF-ROUTE** | VM hybrid (captures; size-cap retry); P holds (?!<[0-9]) lookahead: stage 2 at most |
| `capability/wild-datetime-moment-iso8601` | - | - | - | - | attempt-start, none | search_short 0.0008; throughput 0.0691 | **ANCHORED** | start-anchored (^ / one attempt): the tactic declines (where_to_start.md §2.5) |
| `capability/wild-validator-email-owasp` | - | - | - | - | attempt-start, none | search_short 0.0010; throughput 0.0461 | **ANCHORED** | start-anchored (^ / one attempt): the tactic declines (where_to_start.md §2.5) |
| `loglines/kv-quoted` | \b[a-z_][a-z0-9_]{0,31} · '="' | y | y | y | reverse-pass, 32 | search_short 0.0000; throughput 0.0085 | **SURVIVES** | '=' not in alphabet(P); today: K82 handoff at c-32 already |
| `capability/email-nested-plus` | - | - | - | - | attempt-start, none | search_short 0.0012; throughput 0.0000 | **ANCHORED** | start-anchored (^ / one attempt): the tactic declines (where_to_start.md §2.5) |
| `loglines/uuid` | \b[0-9a-f]{8} · '-' | y | y | y | end-minus-width, none | search_short 0.0001; throughput 0.0010 | **SURVIVES** | fixed width 8; today end-minus-width (start exact, K3) |
| `capability/winpath-near-miss` | - | - | - | - | attempt-start, none | search_short 0.0004; throughput 0.0001 | **ANCHORED** | start-anchored (^ / one attempt): the tactic declines (where_to_start.md §2.5) |
| `capability/uuid-near-miss` | - | - | - | - | attempt-start, none | search_short 0.0005 | **ANCHORED** | start-anchored (^ / one attempt): the tactic declines (where_to_start.md §2.5) |
| `capability/wild-logparse-winpath-grok` | (?>...) · '\\' | n | - | - | reverse-pass, none | search_short 0.0000 | **OFF-ROUTE** | atomic group in P; VM |
| `bounded/csv5` | [^,\n]{0,32} · ',' | y | y | y | reverse-pass, none | search_short 0.0000 | **SURVIVES** | search_short only |
| `capability/wild-validator-uuid-grok` | [A-Fa-f0-9]{8} · '-' | y | y | y | end-minus-width, none | throughput 0.0000 | **SURVIVES** | as loglines/uuid |
| `sentinel/uuid-near-miss` | - | - | - | - | attempt-start, none | search_short 0.0000 | **ANCHORED** | start-anchored (^ / one attempt): the tactic declines (where_to_start.md §2.5) |
| `sentinel/wild-validator-email-owasp` | - | - | - | - | attempt-start, none | search_short 0.0000 | **ANCHORED** | start-anchored (^ / one attempt): the tactic declines (where_to_start.md §2.5) |
| `sentinel/winpath-near-miss` | - | - | - | - | attempt-start, none | search_short 0.0000 | **ANCHORED** | start-anchored (^ / one attempt): the tactic declines (where_to_start.md §2.5) |

| verdict | est ms (walk_survey weights) |
|---|---|
| SURVIVES | 5.839 |
| REFINED-ONLY | 5.817 |
| FAILS-G2 | 3.207 |
| OFF-ROUTE | 0.805 |
| ANCHORED | 0.119 |
| **all K12 cells (cf. walk_survey 15.8)** | **15.786** |

### 1.3 Reading

- **Under G2 as stated, the stage-1 population is 5.84 ms of the 15.8 ms (37%)**, and
  it is essentially ONE pattern: `loglines/ipv6` carries 5.83 ms of it (throughput
  5.69 + search_short 0.14). The other survivors are crumbs: `kv-quoted` 8.5 µs (it
  already has the K82 handoff at `c − 32`), the uuid pair ~1 µs (start already exact,
  `end-minus-width`), `csv5` 7 ns.
- **altwide/sfx-\* (5.82 ms) FAIL G2's formula** — the stems span all 26 letters, so
  `{i,n,g} ⊆ alphabet(P)`, and their widths are 3-9, not fixed — **but the split is
  NOT ambiguous.** G2's literal arm is rust's sufficient condition for "no occurrence of
  `L` lies inside a string `P` matches"; the exact condition (§2.2 step 2's own
  argument) is that no string of `P` CONTAINS `L` as a factor (the `j + |L| ≤ j'`
  case), plus no crossing occurrence (`j < j' < j + |L|`, which needs `L` to have a
  border; `ing` has none). No stem of sfx-64/256/512 contains `ing` (checked over all
  64/256/512). This FACTOR-FREE arm is decidable on `P`'s DFA (a product with the
  `L`-occurrence automaton) and strictly weaker than the alphabet arm. It is NOT
  rust's third (disjoint-separator) arm, which D151 item 3 ruled NO on; it is a new
  question (§5 Q1).
- **`\S+@\S+` and email/\* fail every arm.** `'@'` is a factor of `\S+`; the quoted local
  part of the email patterns admits `'@'` (`\x23-\x5b`), a genuinely ambiguous split.
  (`\S+@\S+` happens to be monotone for a different reason — `P` is one class-plus that
  contains `L` — but no arm on file or proposed here admits it, and its 1.41 ms is
  K7-shaped: the presence `memchr('@')` then the DFA re-steps the gap.)
- **Off the stage-1 route:** the two VM hybrids (syslogbase: lookahead in `P`; winpath-
  grok: an atomic group in `P` — G1 fails on both) and eight `^`-anchored patterns (one
  attempt; the tactic declines, `where_to_start.md` §2.5).
- **Recounted estimate: 5.84 ms under G2 as written; 11.66 ms if the factor-free arm is
  admitted.** Both are walk_survey's upper-estimate weights (old-pin bench medians on the
  Ryzen 1600, uniform per-byte cost), so the TWINS (§2) are the price, not these.

## 2. Step B — the hand twins

### 2.1 Cells chosen

The formal-G2 survivors ranked by estimate are ipv6 (5.83 ms), kv-quoted (8.5 µs), then
crumbs; D151 add. 4 names ipv6 and altwide/sfx-64. Twinned: **`loglines/ipv6`** (the
population), **`altwide/sfx-64`** (named by the ruling; admitted only under the
factor-free arm), and **`loglines/kv-quoted`** (the second formal survivor, and the
one cell where today's artifact already scans the landmark: it isolates what EXACT
buys over the K82 handoff's `c − K` WINDOW).

### 2.2 The twin (`twin.c`)

One generic file around each cell's UNMODIFIED artifacts, so no emitted line is
hand-edited:

- `rx.c` — today's artifact for `R`: supplies the landmark scan where it already emits
  one (`rx_reqrun`: kv-quoted's `="`, sfx-64's `ing`) and the ANCHORED forward finish
  `rx_match_caps` (the anchored DFA, `start_table.md` §4.1's DFA hat).
- `rxpl.c` — pcrec's own artifact for `(?:P·L)\z`, which [OPT-REVEND] compiles to a
  pure reverse walk from the subject end (`build.sh` asserts `RXPL_DFA_SCAN
  "rev-end"`). Called with length `j + |L|` it is exactly the reverse DFA over `P·L`
  seeded at the landmark occurrence `j`, floored at `search_from`, recording the
  smallest accepting start `s*(j)` — the walk `where_to_start.md` §2.1 defines, and
  the PREFIX reverse machine `start_table.md` §4.1 says the build needs, here borrowed
  from REVEND's emitter (`locate_finish.md` §7.2's "rev-end as rev-inner with
  landmark = end", read the other way round).
- `tw_search`: for each occurrence `j ≥ pos` of `L` in order — `s*(j)` by the reverse
  walk; if non-empty, `rx_match_caps` anchored at `s*(j)`; a match is the answer, else
  `pos = j + 1`. ipv6's landmark is a plain `memchr(':')` (its artifact emits only a
  presence pre-check).
- Donors: ipv6 `[0-9a-f]{1,4}:\z` (P = the alternation's common head, `L = ':'`);
  kv-quoted `\b[a-z_][a-z0-9_]{0,31}="\z`; sfx-64 the pattern itself `+ \z` (`S` empty).

### 2.3 Answer identity (`ident.txt`)

`ident.sh`: three-way (today `o`, twin `t`, libpcre2-8 10.46 `p2`, linked directly per
D98) over every subject the bench set has (short subjects + throughput subjects,
regenerated and sha-checked) plus 400 adversarial subjects per cell from `gen_adv.py`
(landmark-dense runs, overlapping/adjacent occurrences, `P` runs longer than `P`'s bound,
landmarks with empty `starts(j)`, failing verifies after a non-empty `starts(j)`).
Per subject: the bench's find-all loop, and single searches from every startpos
(stride 1 up to 4 KiB, then every 4099th byte), hashed over `(pos, rc, s, e)`.

| cell | subjects | find-all matches | startpos searches (hits) | diff o/t | diff o/p2 | diff t/p2 |
|---|---|---|---|---|---|---|
| ipv6 | 524 | 3,264 | 275,231 (77,910) | 0 | 0 | 0 |
| kv-quoted | 524 | 1,632 | 250,279 (45,919) | 0 | 0 | 0 |
| sfx-64 | 444 | 1,490 | 48,110 (32,327) | 0 | 0 | 0 |

**Failing-direction control** (`plant_lo0.txt`): `twin.c -DET_PLANT_LO0` is
`where_to_start.md` §2.6's `lo0` mutant (the walk may accept a start below
`search_from`). Over the short + adversarial subjects it differs from today's artifact on
383/512 (ipv6), 335/512 (kv-quoted) and 342/440 (sfx-64) subject lines, so the
identity check sees a wrong start.

sfx-64's identity is the empirical half of the factor-free argument (§1.3): its adversarial
subjects include stems followed by `inging` and stem suffixes glued to `ing`, and nothing
differs.

### 2.4 Timing (`times.tsv`, `times_summary.txt`)

@@TIMING@@

## 3. TRIGGER VERDICT

@@VERDICT@@

## 4. What stage 1's build is if it fires

The slot first. D151 addendum 1 names the row `handoff-rev` in FIRST (`start_table.md`
§4.1). `locate_finish.md` §4.6 (F-5, rev 2) moved it: rev-inner already HAS the start and
needs an end and a verdict, so it is a **LOCATE row**, and FIRST's `handoff-rev` "is not
needed" (its give-up is FIN4 `search-from`). The twin is exactly that LOCATE shape, so
stage 1 is **one LOCATE row on `CR_DFA`**, added to `cand_rows[]` after `rev-end` and
before `composite`:

| column | stage 1 (DFA hat) | what the twin used |
|---|---|---|
| row | `rev-inner` (and `rev-inner-bounded` ahead of it if `P` reads a view) | — |
| route | `CR_DFA` only (stage 2, the VM LOWER form, stays on its own trigger) | DFA artifacts |
| predicate | G1 ∧ G2 ∧ G3, each a separate conjunct with its sabotage row; G4 true by construction on the DFA route | hand reading |
| landmark scan | a FIND over `L` that RETURNS each hit and resumes at `hit + 1` — the one memfn request `start_table.md` §4.1 already names | `memchr(':')`; the artifact's own `rx_reqrun` for `="` / `ing` |
| reverse walk | the PREFIX reverse machine over `P·L`, seeded at `j + |L|`, floored at `lo`, recording the smallest accepting start — built with REVEND's parameterized reverse block (`emit_reverse_block`, revbuild L1), a third seed of the same emitter | pcrec's own `(?:P·L)\z` rev-end artifact, unmodified |
| hand | `SPAN` from FIN `verify-at` (the anchored DFA, `rx_match`'s machine) at `s*(j)`; on failure the next occurrence | `rx_match_caps` |
| give-up | the forward-verify guard (`where_to_start.md` §2.7) relocates `s*` as `lo` to `composite` (FIN4 `search-from`), ONE_WAY | not exercised (see below) |
| fact | `inner_split` (`facts.def`, E2, `PF_CORE`): the landmark, `P`'s byte width, G1/G2 bits, **read per top-level branch** (Q2) | hand split |
| deny / stamp | `-fno-rev-inner` (next free bit), the LOCATE stamp value, one abi event | — |
| sabotage | §2.6's mutants as rows: `lo0`, `max_start`, `slice`, `noverify`, `skipL`, `restart_s1`, plus one per G-conjunct | `lo0` planted here (§2.3) |

Two things the twin settles for the build:

- **The prefix machine is not new machinery.** Seeding the reverse walk of `P·L` at
  `j + |L|` (rather than of `P` at `j`) folds `L`'s own verify into the walk and lets the
  build reuse the reverse block REVEND already parameterized; the twin did exactly this
  with an unmodified REVEND artifact. `where_to_start.md` §1.3 item 4's "build it once as
  a parameter of the existing builder" is already true.
- **The split must be read per top-level branch.** The population's one large cell,
  `loglines/ipv6`, is a top-level alternation `(?:(?:H:){4,7}H|(?:H:){1,7}:H{0,4})`; there
  is no top-level `P·L·S` concatenation. Each branch's first necessary `L` is the same
  `':'` after the same `P = H`. The general form is a split per branch, `R = ⋃ Pᵢ·L·Sᵢ`,
  with the reverse walk over `(⋃ Pᵢ)·L` and G2 over `⋃ Pᵢ`; the verify runs the whole
  `R` anchored, so it needs nothing per branch. walk_survey's stand-in reader (85% bench
  parse) would not have found ipv6 as a P·L·S split.

Not exercised by the twin, owed to the build's checks: the quadratic forward-verify hazard
(§2.7: kv-quoted's `S = (?:[^"\\]|\\.)*"` re-reads to the end per `="` when no closing quote
follows; the bench subjects are not hostile), so the build's guard needs a hostile cell of
its own; and the `-e utf8` landmark round-up (no utf8 K12 cell survives).

## 5. Questions (with recommendations) and bench-only questions for relay

**For Frank (each with a recommendation):**

- **Q1. Admit the factor-free G2 arm?** `fixed_width(P) ∨ ¬(bytes(L) ⊆ alphabet(P)) ∨
  (L is not a factor of any string of P ∧ L is border-free)`. It is the exact condition
  §2.2 step 2's argument uses (an occurrence inside `P`'s string, or crossing into the
  next occurrence), of which rust's literal arm is a sufficient special case; it is
  decidable on `P`'s DFA (a product with `L`'s occurrence automaton; border-freeness is
  a property of `L` alone). It is NOT rust's disjoint-separator arm that D151 item 3 ruled
  NO on. It admits altwide/sfx-64/256/512 (5.82 ms, the twin's largest win).
  *Recommendation: yes, as its own conjunct with a sabotage row and a soundness re-run of
  `rinner_model.py` with the arm swapped in for the literal arm* — the model's 0 /
  145,598 ungated-split result is the control that would catch a wrong argument, and it
  must be re-run against 10.46 anyway (D151's owed item).
- **Q2. Read `inner_split` per top-level branch?** Without it the stage-1 population is
  empty: ipv6 is the only large formal-G2 cell. *Recommendation: yes* (the general form;
  a common-head factoring would be a special case of it).
- **Q3. Is `\S+@\S+` (1.41 ms) a rev-inner customer?** It fails every arm, though its
  `starts` is monotone for a reason of its own (`P = C+` with `L ∈ C`). *Recommendation:
  no — it is K7-shaped (the presence `memchr('@')` then the DFA re-steps), and K7's own
  handoff (the K82 window, unbounded here) is the better owner.*

**Bench-only questions for relay** (not reverse-engineered from the ledgers):

1. The official verdict is a bench run on the targeted box (D144 add. 4: ubuntubudu,
   Zen 1); every number here is the dev box (7700X). Can loglines/ipv6 (throughput +
   search_short) and altwide/sfx-64 (throughput) be timed with a twin build when the row
   is built?
2. walk_survey's weights are the newest set-grain medians it found (round 1 `c4c70f2c`,
   capability `255bcdd8`). Are there loglines/altwide medians at a post-[START-LANDING]
   pin to re-weight §1.2?

## 6. Reproduction

```
make -j16
B=/home/pcrec/projects/pcrec-bench; W=build/et1; mkdir -p $W/bc
git -C $B archive HEAD bench pcrecbench | tar -x -C $W/bc
(cd $W/bc/bench/<set> && python3 -I gen_subjects.py && python3 -I gen_throughput_subjects.py)   # altwide loglines (+ the K12 sets for Step A)
# Step A: studies/walk_survey/{pop_bench.py,run_pop.py (WSDRV=wsdrv5.c CONFIGS=default),analyze.py,k12_census.py}
python3 docs/dev/optloop/et1twin/recount.py docs/dev/optloop/et1twin/k12_cells_now.tsv
# Step B
PCREC=$PWD/build/pcrec BENCH=$B OUT=$PWD/build/et1twin docs/dev/optloop/et1twin/build.sh
OUT=$PWD/build/et1twin BENCHCOPY=$PWD/$W/bc BENCH=$B docs/dev/optloop/et1twin/ident.sh
OUT=$PWD/build/et1twin BENCHCOPY=$PWD/$W/bc docs/dev/optloop/et1twin/time.sh > times.tsv
python3 docs/dev/optloop/et1twin/summarize.py times.tsv
```

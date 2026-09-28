# [UCP] lookaround SHAPE census — how much of the VM-forcing lookaround
# population is a bounded-context position VIEW the DFA already knows how
# to be

Lane `lacensus` (sonnet), branch `lane/lacensus`, worktree
`worktrees/lacensus`, on `main` at `9399d927`. MEASUREMENT lane: nothing
under `src/`, `tests/` or `docs/spec/`. Answers the question docs/dev/plan.md
[UCP]'s row poses after Frank's normalize-then-recognize clarification
(Q1-Q3, `docs/dev/ucp_study.md` S:D, lane ucpthink 2026-09-28): **how many
patterns that go to the VM today ONLY because of lookarounds could the DFA
implement instead, if it treated a bounded-context lookaround as a position
VIEW** (the `eolvar`/`endvar` mechanism `ucp_study.md` S:D.2 already
generalizes)?

Every script and derived TSV is committed under
`docs/dev/lookaround_census/` (own CLAUDE.md).

---

## 0. Headline

Of the **493** corpus+bench patterns that compile to the VM today with
lookaround as their **only** DFA-excluding construct (S2):

| | n | ALL-(a) (single char/class) | ALL-(a)-or-(b,k≤2) |
|---|---:|---:|---:|
| all | 493 | 172 (34.9%) | 280 (56.8%) |
| corpus | 475 | 164 (34.5%) | 270 (56.8%) |
| corpus, excl. one adversarial D27 matrix file (S3) | 187 | 92 (49.2%) | 126 (67.4%) |
| bench (the least test-biased population, ucp_study.md's own reading) | 18 | 8 (44.4%) | 10 (55.6%) |

**That answers Q2/Q3 (plan.md [UCP]): a position-view predicate covering
only one-character-class lookarounds (shape a) already reaches a third to a
half of this population; widening it to fixed-width bodies of two
characters or fewer (shape b, k≤2) reaches over half — 56-67% depending on
how the adversarial test-matrix file is weighted.** The general mechanism
(idea 1/2, `ucp_study.md` S:D) is not needed to cover the bulk of it: a
DFA-side check bounded to width ≤2 already reaches the majority.

Per-occurrence (not per-pattern) shape totals over the same population,
worst-first: **e 113, d 6, c 52, b 155, a 234** (S3). Shape (b)'s own width
distribution is k=0:45, k=1:7, k=2:56, k=3:40, k=4:2, k=5:5 — the width-0
group (an EMPTY lookaround body, e.g. `(?=)`) is a boundary-matrix
artifact, not a real-pattern shape (S3).

---

## 1. Method

**Population, reused rather than recompiled.** `studies/ucp_study/
census_13b7c202.tsv` (captures ON, the default) and `census_nocap_
13b7c202.tsv` (`--no-captures`) are ucp_study.md's own committed,
already-compiled census over the corpus (`tests/`+`examples/`) plus
pcrec-bench's `bench/*/patterns/*.rx` (read-only), one row per unique
(pattern, encoding, caseless) with the engine stamps of one `--features
all` compile at commit `13b7c202`. `main` is 18 commits ahead of that pin;
`git diff --stat 13b7c202..9399d927 -- tests/ examples/` touches only
`tests/findings/` and `tests/codegen/run_prechecks.sh` ([FINDINGS] B6 /
[FIND-TIE], both unrelated to lookaround/UTF-8 corpus content) — so the
committed engine stamps are current for this population, and no
whole-corpus recompile (and no boxlock) was needed. `--list-source` calls
(to re-gather the RAW pattern text, next paragraph) are light per-file
metadata reads, not compiles.

**Raw text, not the census TSV's own pattern column.** census.py's TSV
truncates its `pattern` column to 200 characters and re-renders it through
`backslashreplace` — fine for a quick read, wrong for a structural parse of
a pattern that continues past byte 200 (S2 below found exactly this
undercounting the original 492 by one). So `build_census.py` **re-gathers
every pattern's full, untruncated bytes fresh**, by ID, using the same
`--list-source`/bench-directory walk `census.py` itself uses (copied
verbatim, not re-derived) — the escaping trap `docs/dev/optloop/
cycle1_analysis.md`'s own extraction bug hit (a pattern taken from
`--list-source`'s escaped column and handed back undecoded) is sidestepped
by construction: the only escape-decoding that happens is `census.py`'s own
`decode_escape`, applied once, at population-gather time, identically for
both scripts.

**Selecting the population.** A pattern is in scope if its engine is `vm`
AND a **lexical family scan over its own full text** (the census's D2 FAM
table, `studies/ucp_study/census_analyze.py`, reused verbatim for the
no-captures census) is non-empty and a SUBSET of `{lookahead, lookbehind,
nonatomic-look}` — i.e. lookaround is PROVABLY the only construct the
census's own family regexes can find, not merely the first one
`RX_ENGINE_WHY` happened to name (the WHY kind/offset mismatch
`ucp_study.md` S:G.2 already warns is unreliable). For the DEFAULT
(captures-on) census, the FAM table gains ONE more family, `capture` (a
plain `(` that is neither a `(?...)` construct nor a `(*verb:`/alpha-lookaround
opener — see S2's own found-and-fixed bug on that last exclusion), so a
pattern whose text ALSO carries a real capturing group is correctly
excluded from "lookaround is the only reason", per the brief's DO item 1
("captures force the VM on their own").

**Classifying each occurrence.** `shape_classify.py` is a from-scratch
recursive-descent parser over the pattern TEXT (not derived from pcrec's
AST or `--emit-ir`'s VM-program listing — the listing states a
lookbehind's fixed width directly but not a lookahead's, and generalizing
that reading across nested/alternated bodies was judged more work and less
checkable than a small dedicated parser; see S4 for why the listing was
tried first). It recognizes all six of pcrec's accepted lookaround
spellings (`src/parse/mod_lookaround.c`'s `la_rows`: `(?=` `(?!` `(?*`
`(?<=` `(?<!` `(?<*`) plus their alpha-verb aliases (`(*pla:` etc., which
the registry resolves to the same six before the parser proper ever runs),
computes each occurrence's body (min, max) width and whether it contains a
capturing group / backreference / subroutine call / nested lookaround
anywhere inside, then classifies:

- **(e)** — the body contains a capture, backref, call, or nested
  lookaround: worst, overrides width entirely (a bounded-context predicate
  cannot express these without the VM's own capture/backtrack state).
- **(d)** — unbounded width (an unbounded quantifier, or `\X`, reaches the
  body).
- **(c)** — bounded but VARIABLE width (min ≠ max, both finite) —
  e.g. `(?<=a|bc|def)x`, three branches of width 1/2/3.
- **(b)** — FIXED width k (min = max) but not a single atom of width 1 —
  e.g. `(?<=abc)`, or `(?<=ab|cd)` (two branches, both width 2: fixed width
  even though it's an alternation).
- **(a)** — FIXED width 1 as a SINGLE atom: one character, one class
  (`[...]`, a POSIX name inside one), or one escape shorthand (`\d \w \s
  \D \W \S \h \H \v \V \p{...} \P{...} \N`) or `.` — no alternation, no
  concatenation, no quantifier: "C is one character or class" (the brief's
  own spelling), matched STRUCTURALLY as well as by width, so
  `(?=a|b)` (two one-char branches) is (c), not (a) — it is not textually a
  single C.

A pattern is classified by the WORST shape among its own occurrences
(worst-first order e > d > c > b > a); a nested lookaround is also its own,
separately-classified occurrence (so `(?<=a(?!b))c` records TWO rows: the
inner `(?!b)` at shape a, the outer at shape e because its body contains a
nested lookaround). Widths are counted in **characters/atoms**, matching
PCRE2's own width rule for lookbehind (`(?<=[\x{0}-\x{10FFFF}])x` is width
1, not the 1-4 UTF-8 bytes that class can occupy) — a deliberate choice,
not an oversight; see S5's sample for a witness.

**What this census is NOT.** It does not build the DFA's predicate-view
mechanism, and it does not measure whether an occurrence's body ITSELF is
buildable on the DFA today (e.g. a shape-(a) class the size of `\p{Xwd}` —
that is [CLS-TREE]'s own dependency, `ucp_study.md` S:E, untouched here).
It answers only "does this occurrence's WIDTH SHAPE fit a bounded-context
predicate view", the Q2/Q3 question as posed.

---

## 2. S2: reproducing 492/1,101, and the two bugs the reproduction found

`docs/dev/lookaround_census/build_census.py`, section S2:

```
no-captures: vm=1101, lookaround-only (own lexical scan)=493  [ucp_study.md: 492 of 1101]
default:     vm=1647, lookaround-only AND capture-free (own lexical scan)=378, naive WHY-names-a-lookaround=12
default_sel == nocap_sel (same pattern set): False (symmetric diff 115)
```

**The +1 (493 vs. 492) is a genuine correction, not noise.**
`capability/wild-logparse-syslogbase-expanded` is a 1,948-byte pattern
whose only DFA-excluding constructs are a `(?=...)` at offset 19 and a
`(?!...)` at offset 298 (both past the census TSV's 200-byte truncation
window). `ucp_study.md`'s own D2 scan operates on the truncated,
re-rendered `pattern` column, where this pattern's visible 200 bytes
contain NO lookaround token at all — the truncated scan finds an EMPTY
family set (not "some other excluding family"), and `census_analyze.py`'s
own `only_look` filter (`fams(r["pat"]) and fams(r["pat"]) <= look`) treats
an empty set as `not f`, i.e. FALSE, silently dropping the pattern from the
492 despite it genuinely being lookaround-only. Re-gathering the FULL text
(S1) finds both constructs and correctly includes it; the reproduction's
own +1 is the fix, not a discrepancy to explain away. **493, not 492, is
the corrected no-captures headline; the memo's 0.9% delta does not move
`ucp_study.md`'s own conclusions.**

**"Do it both with captures (default) and with `--no-captures`" (brief DO
item 1), answered with a set relation, not two independent counts.** Under
DEFAULT, `default_sel` (378) is an EXACT SUBSET of `nocap_sel` (493) — the
symmetric difference is 115, all "only in nocap_sel", none the reverse.
That is the expected shape: for a pattern with literally zero capturing
groups, `--no-captures` changes nothing (there is nothing to strip), so its
compiled engine/WHY are IDENTICAL between the two census runs; the only way
a pattern can be "lookaround-only" under `--no-captures` but not under
default is that its text ALSO carries a plain capturing group, which
independently routes it to the VM once captures are live. All 115 are
exactly that: `tests/lookaround/captures.rxt`'s own 9 fixtures (named for
the property) plus `wild-logparse-syslogbase-expanded` again, whose
`(?<timestamp>...)` head is a real capturing group and whose DEFAULT-census
WHY genuinely reads `capture group at pattern offset 0` (not a lookaround)
— captures really are "forcing the VM on their own" there, confirmed by
reading the WHY string directly rather than assumed from the text alone.
The naive count anyone would get from trusting `RX_ENGINE_WHY` alone under
DEFAULT (any VM row whose WHY string merely LOOKS like a lookaround) is
only **12** — three orders of magnitude off the real 378/493, because under
DEFAULT the overwhelming majority of VM routing is captures (949 of 1,647
per `ucp_study.md` S:D.3), and WHY names only the first excluding
construct it finds, which for most capture-bearing patterns is the capture
itself, not any lookaround present. The 378-vs-493 set relation, not either
raw count, is the honest way to read "with captures" here.

**Bug found while building this: the FAM `capture` regex's first draft
false-positived on the alpha-verb spellings.** `rb"(?<!\\)\((?!\?)"` (a
literal `(` not preceded by `\` and not followed by `?`) also matches the
`(` of `(*pla:...)`/`(*positive_lookbehind:...)` — those start with `(*`,
not `(?`, so the naive regex reads them as capturing-group opens. This
wrongly excluded `tests/lookaround/alpha_spellings.rxt`'s ten fixtures and
the bench's `syntax/lka-verb` from the DEFAULT population (they have no
real capturing group — the alpha spelling IS the whole construct). Fixed
by excluding BOTH `?` and `*` after the `(` (`rb"(?<!\\)\((?![?*])"`) —
caught by comparing `default_sel`'s membership against expectation, not by
inspection; see S5 for how the shape classifier ALSO needed its own
alpha-spelling support (a separate bug, S4).

---

## 3. S3: shape distribution

Full breakdown, worst-shape-per-pattern (`shapes_9399d927.tsv`,
`report_9399d927.txt`):

| population | n | a | b | c | d | e |
|---|---:|---:|---:|---:|---:|---:|
| all (no-captures 493) | 493 | 172 | 155 | 52 | 3 | 111 |
| corpus | 475 | 164 | 147 | 52 | 1 | 111 |
| bench | 18 | 8 | 8 | 0 | 2 | 0 |
| corpus, excl. `tests/lookaround/d27/matrix.rxt` | 187 | 92 | 39 | 16 | 1 | 39 |
| `tests/lookaround/d27/matrix.rxt` ALONE | 288 | 72 | 108 | 36 | 0 | 72 |
| default (captures-on, 378) | 378 | 154 | 135 | 46 | 3 | 40 |
| default, corpus | 361 | 146 | 128 | 46 | 1 | 40 |
| default, bench | 17 | 8 | 7 | 0 | 2 | 0 |

**One systematically-enumerated adversarial test file, `tests/lookaround/
d27/matrix.rxt` (a D27-blinded boundary-case matrix), is 288 of the 493
no-captures population — 58.4%.** It exhaustively varies polarity, anchor
position, alternation, nesting and quantification of small lookarounds
(`ucp_study.md` itself already flags corpus lookaround-module
over-representation, S:D.3: "the corpus is a test corpus and over-represents
lookaround-module tests"). Its own shape mix is the CASELESS one in the
headline table (25.0% ALL-a vs. 49.2% for the rest of the corpus and 44.4%
for the bench) because its own charter is to hit every boundary condition,
including the ones with captures/backrefs/nested lookarounds this census's
(e) exists to catch. **Reading the headline: the bench (18 patterns, the
population `ucp_study.md` S:D.3 itself calls "the less biased number") and
the non-matrix corpus (187 patterns) agree with each other (44-49% ALL-a,
56-67% ALL-a-or-(b,k≤2)) and both read materially higher than the
matrix-inflated "all" number** — so 56.8% is a LOWER bound on the real-pattern
share, not the honest headline on its own.

**Per-occurrence totals** (every lookaround occurrence counted once, not
per worst-pattern): a 234, b 155, c 52, d 6, e 113. Shape (b)'s own k
(fixed width) distribution: k=0 → 45, k=1 → 7, k=2 → 56, k=3 → 40, k=4 → 2,
k=5 → 5. **The 45 k=0 rows (an empty lookaround body, `(?=)` `(?<=)` `(?<!)`
`(?*)`) are ALL from `matrix.rxt`'s boundary enumeration** — not a real
pattern shape; a zero-width predicate is trivially cheaper than a
one-character one (no decode at all), and this census folds it into the
"k≤2" headline bucket accordingly (0 ≤ 2), stated explicitly rather than
silently decided.

---

## 4. Why a text parser, not `--emit-ir`

`--emit-ir --features all` DOES carry a per-occurrence width fact for
LOOKBEHIND directly in its program listing (a `note` line reading e.g.
"lookbehind branch 1 of 1, fixed width 3" per branch, one line per
alternation branch — `docs/spec/ir_listing.md`'s own contract). It carries
NO equivalent width statement for LOOKAHEAD; a lookahead's width is
implicit in its VM rung shape (a plain `compare`/`consume` chain for a
fixed body, a `cursor` rung with `{m,n}` for a bounded one, an unbounded
`{m,}` rung otherwise) and would have to be read back OUT of the emitted
program structure per occurrence, across nesting and alternation, which is
strictly more machinery than parsing the pattern text directly — and
harder to verify by hand, since a reader would be re-deriving "does this
program shape correspond to width w" rather than reading a width off the
pattern. `shape_classify.py` is therefore an INDEPENDENT parse (not derived
from pcrec's own AST or IR), which is also why it needed its OWN
alpha-spelling support (the same bug class as S2's FAM regex, found the
same way — a false EMPTY-occurrence result on `tests/lookaround/
alpha_spellings.rxt` when the parser recognized `(?` constructs only, since
`(*pla:...)` does not start with `(?` at all and the first draft silently
mis-parsed it as an ordinary capturing group containing the literal text
`*pla:foo`). Fixed by giving `_group()` its own alpha-verb branch,
resolving the six known alpha names to the same six canonical kinds
`la_rows` uses (`docs/dev/lookaround_census/shape_classify.py`'s
`_ALPHA_LOOK_KIND` table) — verified by re-running S2/S3 and confirming
`alpha_spellings.rxt`'s 18 rows (S3's corpus count) now classify instead of
falling into the "no real lookaround found" bucket.

---

## 5. Hand sample (10 patterns per class)

Sampled with a fixed seed from `shapes_9399d927.tsv`, verified by hand
against `shape_classify.py`'s own stated rule (S1) — none of these went
through `--list-source`'s escaped pattern column (S1's escaping-trap
paragraph); the text below is exactly the bytes the classifier parsed.

**(a) — single char/class, width 1, no alternation/concatenation/quantifier**

| pattern | occurrence body | why (a) |
|---|---|---|
| `z(?<=[ab])` | `[ab]` | one class |
| `y(?*[ab])z` | `[ab]` | one class (non-atomic lookahead) |
| `(?=a){0,3}a` | `a` | quantifier `{0,3}` is on the LOOKAHEAD itself (external), not on the body — the body `a` is unquantified |
| `(?=a)b` | `a` | one literal char |
| `(?*a)*a` | `a` | ditto (external `*` on the construct) |
| `((?<![ab])z)` | `[ab]` | wrapped in an outer CAPTURING group, but that capture is outside the lookaround's own body, so this occurrence is unaffected — the pattern still routes to `--no-captures`-only, `default_sel`'s exclusion is by the outer group, not this shape |
| `^(?:(?!x))*a$` | `x` | one literal char |
| `[\xc2-\xdf](?![\x80-\xbf])` (bench) | `[\x80-\xbf]` | one class |
| `(?<=[\x{0}-\x{10FFFF}])x` (utf8 axis) | `[\x{0}-\x{10FFFF}]` | one class, width 1 CHARACTER (not 1-4 UTF-8 bytes — S1's width-in-characters rule) |
| `((?*[ab])z)` | `[ab]` | one class |

**(b) — fixed width k, not a single atom**

| pattern | body | min=max | why not (a) |
|---|---|---|---|
| `(?!)*z` | (empty) | 0 | k=0, the matrix's empty-body edge case |
| `(?<=ab\|cd\|ef\|gh)x\|q` | `ab\|cd\|ef\|gh` | 2 | FOUR branches, all width 2 — alternation of EQUAL-width branches is still fixed, not (c) |
| `(?<=a{3})x` | `a{3}` | 3 | quantified repeat of a fixed count |
| `(?<=a)b\|(?<=bc)d` | TWO occurrences: `a` (w1, shape a) and `bc` (w2, shape b) | — | pattern's WORST is b (from the second occurrence) |
| `z(?=abc)` | `abc` | 3 | three literals concatenated |
| `(?<=a{2})b` | `a{2}` | 2 | k=2 |
| `(?<!ab\|cd)z` | `ab\|cd` | 2 | two equal-width branches |
| `y(?=abc)z` | `abc` | 3 | three literals |
| `y(?<*)z` | (empty) | 0 | non-atomic lookbehind, empty body |
| `(?<=)*z` | (empty) | 0 | empty body |

**(c) — bounded but variable width (alternation of UNEQUAL widths)**

| pattern | branches (width) | min,max |
|---|---|---|
| `(?<=a\|bc\|def)x` | 1,2,3 | 1,3 |
| `y(?<!a\|bc)z` | 1,2 | 1,2 |
| `(?<=a\|bb\|ccc\|dddd)X` | 1,2,3,4 | 1,4 |
| `z(?<*a\|bc)` | 1,2 | 1,2 |
| `(?=a\|bc)z` | 1,2 | 1,2 |
| `y(?<*a\|bc)z` | 1,2 | 1,2 |
| `(?<=x\|abc)y` | 1,3 | 1,3 |
| `((?*a\|bc)z)` | 1,2 | 1,2 |
| `z(?=a\|bc)` | 1,2 | 1,2 |
| `(?<=(?:a{2})\|(?:a{3}))x` | 2,3 (non-capturing groups as branches) | 2,3 |

**(d) — unbounded (only 3 in the whole population)**

| pattern | which occurrence is unbounded |
|---|---|
| `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$` (bench, password strength) | all four lookaheads: `.*[class]` is `(0,∞)` |
| `^(?!.*\.\.)[A-Za-z0-9.]+(?=@)` (bench, email-local-nodup) | the FIRST lookahead, `.*\.\.` — the second, `@`, is shape (a); pattern's worst is (d) |
| `(?=a+b)aab` | `a+b`: `a+` is `(1,∞)` |

**(e) — contains capture / backref / call / nested lookaround**

| pattern | why |
|---|---|
| `((?!a(?!b))z)` | outer lookahead's body contains a NESTED lookahead `(?!b)` (itself its own occurrence, shape a) |
| `(?:(?<!a(?!b))z\|w)` | nested lookahead inside a lookbehind body |
| `z(?!(a))` | body is `(a)` — a CAPTURING group |
| `y(?<=a(?!b))z` | nested lookahead inside lookbehind |
| `((?*a(?!b))z)` | nested lookahead inside non-atomic lookahead |
| `(?<=(a)\|(bc))x` | BOTH alternation branches are capturing groups — (e) overrides the width computation entirely (would have been (c) by width alone) |
| `(?=(a)(b))ab` | body is two capturing groups |
| `y(?!(a))z` | capturing group in body |
| `^(?:(?=(a)))*a$` | capturing group in body |
| `(?:(?=(a))z\|w)` | capturing group in body |

---

## 6. Relation to the plan row

Direct inputs to `docs/dev/plan.md` [UCP]'s Q2/Q3:

- **Q2** ("is the DFA's DETECTION SET LARGER than `\b` — a subset of
  lookarounds... the DFA can implement instead of the VM"): yes, and this
  census gives it a SIZE. A predicate view for shape (a) alone reaches
  34.9% of the no-captures VM-because-of-lookaround population (44-49% on
  the two less test-biased sub-populations); widening to shape (b) with
  k≤2 reaches 56.8% (55.6-67.4%).
- **Q3** ("does that general mechanism widen the set of features that
  build as DFA rather than VM"): yes, materially, but the marginal cost
  curve is steep — the (e) population (111 of 493, 22.5%) needs the FULL
  general mechanism (or is structurally out of reach of a pure predicate:
  captures/backrefs need VM state, calls need expansion) regardless of how
  wide the width bound goes, and (d) (unbounded) is the classic
  linearity-loss hazard `ucp_study.md` S:D.2's H6 already names.
- This census does NOT touch [CLS-TREE] (whether a shape-(a) occurrence's
  own CLASS is affordable on the DFA — `\p{Xwd}` is not, today,
  `ucp_study.md` S:E) or throughput (open question 7 there). Both stay
  open.

---

## Reproduction

`docs/dev/lookaround_census/build_census.py build/pcrec . /path/to/pcrec-bench OUTDIR`
(re-gathers the population fresh via `--list-source`/bench directory walk,
~1.3s; no compile, no boxlock needed) writes `OUTDIR/shapes.tsv` and prints
the S2-S4 tables above to stdout. `shape_classify.py` is a standalone
library (`classify_pattern(pattern_bytes) -> [occurrence, ...]`,
`worst_shape(occurrences)`) with no pcrec dependency; also runnable as a
one-pattern-per-stdin-line filter for spot checks (`python3
shape_classify.py <<< '(?<=abc)x'`).

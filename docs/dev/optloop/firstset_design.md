# `[OPT-FIRSTSET]` — the candidate-start set derived from the AST

**[OPTLOOP.2] cycle-2 preparation, lane `c2prep`, 2026-09-22.** Design note
only: nothing under `src/`, `lib/` or `cli/` changed in the delivery that
carries it, and no mechanism is built. Every number below is a COUNT taken on
this Mac or a timing quoted from the I-85 Linux profile pass
(`runs/2026-09-22-i85-405668e9/`); no clock was read on darwin.

Reproduction pieces: `c2/` (its own `CLAUDE.md`).

---

## 0. Read this first

The row was ratified on `cycle1_analysis.md` M3 and then **partially refuted
by its own profile**: `cycle1_profile.md` M3.c records the `json-constant`
hand-twin running ×1.10 SLOWER with answer identity intact, which by that
block's own written criterion refutes M3 for that row. This note was
chartered to supply the missing cost model that would decline such a row.

**It delivers the cost model, and it also delivers two findings that change
what the model is for.**

1. **The mechanism as M3 states it is UNSOUND, and its own proposed identity
   check passes anyway.** Narrowing `rx_can_begin_match` to the AST-level
   first-byte set makes `\b(?:true|false|null)\b` report a SPURIOUS match on
   `"atrue xnull "` — the shipped artifact answers `matches=0`, the twin
   answers a match at offset 1. §4 is the witness, the mechanism and the
   one-line repair, all three reproducible from `c2/scanloop_sim.py`.
2. **Under a cost model that reproduces three of the four measured
   configurations to within 0.03%, narrowing the set is monotonically
   non-harmful for any parameter values** — so the model as calibrated
   produces NO decline rule, and the sole measurement contradicting it is
   `json-constant`'s, which no accounting over that artifact's own counts
   reproduces (§3.4 misses it by 2.36×). §7's D77 gate is therefore
   "re-run M3.c on `json-constant` first", not "build the decline rule".

The findings-file consumer interface, the named value and the static default
are delivered as chartered (§5), because a second, independent consumer for
them turned up in the same census and does not depend on any of the above:
three `capability` patterns carry a necessary byte that is ABSENT from the
bench subject while the byte pcrec actually picks is PRESENT (§5.5).

---

## 1. The mechanism

pcrec derives `rx_can_begin_match[256]` from the bytes that leave the DFA's
start state to a live state. A leading `\b` makes that state track word
context, so every word byte leaves it live and the set becomes the 63-byte
word class — **77.2128% of the bench throughput text** (`c2/subject_freq.json`,
`t-1m`), i.e. a skip loop that can almost never skip. That is the named cause
of `opt3_dfa_scan_measurement.md`'s own measured symptom, *"the skip loop is
entered 190,651 times and skips ZERO bytes"*.

The mechanism is to compute the candidate-start set from **the bytes that can
begin a match** — an AST-level first-byte analysis looking *through* leading
zero-width assertions (`\b`, `\B`, `^`, `\A`, lookaround) to the first
byte-consuming element — and to intersect it with today's derivation, never
widening it.

Two consumers, one analysis:

* **(i) the DFA route's existing skip loop**, whose representation, table
  sizes and stamps do not change — only the set's contents;
* **(ii) the VM route**, where the eleven `RX_VM_PREFILTER "none"` artifacts
  have no candidate-start skip at all. `nested-comment-rec` is the case that
  shows (ii) matters on its own: first byte `/`, **2.8610%** of the subject.

It shares its bottom-up AST walk with `[OPT-REQBYTE]`, which is why M1+M3 was
proposed as one batch.

---

## 2. What the emitted scan loop actually is

Everything below depends on this, so it is quoted rather than described
(`--features all --no-captures -p rx` on `\b(?:true|false|null)\b`,
`RX_DFA_PREFILTER "byte-class-bounded"`, `RX_DFA_TABLE "premultiplied"`):

```c
rx_forward_state forward_state =
    search_from ? rx_forward_seed_state[rx_forward_byte_class[subject[search_from - 1]]] : 0;
for (;;) {
    if (forward_state == 0 && last_accept_position == (size_t)-1) {
        while (scan_position + 1 < subject_length
               && !rx_can_begin_match[subject[scan_position]]) scan_position++;
    }
    ...one transition step...
}
```

Three properties matter and only one of them is obvious.

* The skip loop is **gated on `forward_state == 0`**, so the candidate set is
  not its reach; the machine's state-0 residency is.
* **The entry line already reconstructs the machine's state from the byte
  before the start position.** `rx_forward_seed_state` is an emitted table
  that exists today. §4's repair is that expression, reused.
* `skipped + steps == n` **exactly**, on every configuration measured — the
  loop either skips a byte or steps on it.

---

## 3. The cost model

### 3.1 The shape, derived rather than fitted

Let, for a candidate set `S` on a given subject:

| symbol | meaning |
|---|---|
| `d` | `S`'s summed byte frequency in the subject (the findings value, §5) |
| `L` | mean bytes the skip loop advances per entry |
| `w` | mean transition steps the machine takes per skip-loop entry |
| `a` | cost of one transition step |
| `b` | cost of one skipped byte |
| `c` | fixed cost of one skip-loop entry/exit |

Each pass through the outer loop consumes `L + w` subject bytes, so

```
    cost per subject byte  =  (L·b + w·a + c) / (L + w)
    skipped fraction       =  L / (L + w)
    L                      ≈  (1 − d) / d
```

**That is not a fit; it is an identity, and it reproduces the measured counts
exactly.** Predicted skipped fraction `L/(L+w)` against measured, over four
configurations of the same subject (`c2/scanloop_sim.py` on `t-1m`):

| candidate set | `d` | `L` meas. | `L` from `(1−d)/d` | `w` | `L/(L+w)` | skipped, measured |
|---|---|---|---|---|---|---|
| word-63 (as emitted) | 77.2128% | 0.2944 | 0.2950 | 5.386 | 0.0518 | **0.0518** |
| dbnames 14 | 22.2281% | 4.6313 | 3.4988 | 5.170 | 0.4724 | **0.4726** |
| json `{t,f,n}` | 7.8872% | 13.1672 | 11.6805 | 4.490 | 0.7457 | **0.7457** |
| aws `{A}` | 0.1673% | 593.4288 | 596.8173 | 3.712 | 0.9938 | **0.9938** |

`w` is the one term compile time cannot read off the pattern, and it is
empirically narrow: **3.71 to 5.39 across three very different machines and
four set sizes.**

### 3.2 The two coefficients that are measured

Solving the identity against the I-85 timings for the two configurations that
bracket it — all three baselines (94.82% steps) and the `aws` twin (99.38%
skipped) — gives

```
    a = 3.2095 ns per transition step
    b = 0.8375 ns per skipped byte
```

and `a` **independently reproduces `opt3_dfa_scan_measurement.md`'s own
`~3.2 ns / 10.7 cycles per table step`**, measured by a different lane on a
different witness set. The skip loop is therefore about 3.8× cheaper per byte
than the transition loop, which is the direction the mechanism assumes.

### 3.3 And the model then declines nothing

```
    d/dL [ (L·b + w·a + c) / (L + w) ]  =  [ w·(b − a) − c ] / (L + w)²
```

`b < a` and `c ≥ 0`, so the derivative is **negative for every admissible
parameter value**: cost falls monotonically as the expected skip run grows.
Under this model a narrower candidate set never costs, whatever threshold one
would like to put on `d`.

### 3.4 The one measurement the model does not reproduce

| configuration | steps | skipped | entries | predicted ns | measured ns | |
|---|---|---|---|---|---|---|
| baselines (mean) | 994,230 | 54,346 | 184,596 | 3,235,997 | 3,236,385 | +0.01% |
| `aws` twin | 6,515 | 1,042,061 | 1,756 | 893,643 | 893,643 | fitted |
| `dbnames` twin | 553,065 | 495,511 | 106,991 | 2,190,072 | 2,873,100 | **+31%** |
| `json` twin | 266,667 | 781,909 | 59,383 | 1,510,743 | 3,571,873 | **+136%** |

(last column: how far the MEASURED time exceeds what the model predicts.)

The residual is not a per-entry cost either: dividing it by the entry count
gives 0.002 ns for the baselines, 6.38 ns for `dbnames` and **34.71 ns** for
`json` — three values spanning four orders of magnitude for one line of
emitted C. **No linear accounting over that artifact's own counts reproduces
`json-constant`'s regression**, and §4 supplies a reason to distrust the twin
itself rather than to model around it.

**Consequence for the row: the cost model is delivered, and the decline rule
it was chartered to justify is NOT, because the calibration point that would
justify it is the one point that does not reconcile.** §7 states the gate.

---

## 4. The soundness finding: M3's narrowing is not sound, and M3's own identity check passes it

### 4.1 The witness

```
subject                     "atrue xnull "
emitted artifact (63-byte)  matches = 0          ← correct
M3 hand-twin  {t,f,n}       match at offset 1    ← SPURIOUS
```

`true` sits at offset 1 preceded by `a`; `null` at offset 7 preceded by `x`.
Both are word bytes, so the leading `\b` is FALSE at both and the pattern
matches nothing. pcrec's shipped artifact agrees (verified by compiling and
running it, not by reading the tables). The narrowed twin reports a match.

Reproduce:

```sh
python3 c2/scanloop_sim.py <art>/json.c '@atrue xnull '        # last_accept -1
python3 c2/scanloop_sim.py <art>/json.c '@atrue xnull ' tfn    # last_accept 5
```

### 4.2 The mechanism

The DFA's start state is not "nothing has happened yet". For a `\b`-leading
pattern it encodes *"the preceding byte was not a word byte, or there is
none"*. The bytes that leave it to a live state therefore include **every word
byte** — not because a match can start on them, but because **consuming one
moves the machine to a different CONTEXT state**. Today's skip loop advances
only past bytes that lead to DEAD from state 0, which are exactly the bytes
the machine does not need to read.

The AST-level first-byte set answers a different question — *which bytes can a
match BEGIN with* — and substituting it into that loop makes the scan skip
bytes the machine needed in order to know its own context. The error direction
is **spurious matches**, not lost ones, which is the direction no "the new set
must be a subset" argument can catch.

### 4.3 And that is exactly the check M3 proposes

M3's text offers the subset property as *"a free compile-time assertion and
the natural identity check"*. `{t,f,n} ⊂ word-63` — **the check passes on the
unsound narrowing.** The proposed guard is sound as a statement about the
LANGUAGE and says nothing about the CONTEXT the automaton carries, which is
the property that was actually violated. This is `learnings.md` §3's shape
again: a control that shares a source with the thing it controls.

### 4.4 The repair, and it is one line of already-emitted text

On leaving the skip loop, reconstruct the state from the byte the scan landed
after — the expression the artifact's own entry line already contains:

```c
    while (scan_position + 1 < subject_length
           && !rx_can_begin_match[subject[scan_position]]) scan_position++;
    if (scan_position > entry_position)                       /* something was skipped */
        forward_state = rx_forward_seed_state[rx_forward_byte_class[subject[scan_position - 1]]];
```

Measured (`c2/scanloop_sim.py ... tfn -reseed`):

| | `"atrue xnull "` | `t-1m` steps | skipped | entries |
|---|---|---|---|---|
| emitted, 63-byte set | no match | 994,230 | 54,346 | 184,596 |
| M3 twin, `{t,f,n}` | **match at 1** | 266,667 | 781,909 | 59,383 |
| repaired, `{t,f,n}` + re-seed | no match | 266,667 | 781,909 | 59,383 |

**The repair restores the answer and changes no count** — it is one table
lookup per skip-loop exit that actually skipped, 59,383 of them across
1,048,576 bytes, amortized over a mean run of 13.17 bytes.

### 4.5 What this does to consumer (ii)

Nothing. The VM route has no start-state context to lose: it has no candidate
skip at all today, and a first-byte set used to advance the VM's attempt
position is sound on its own terms because a first-byte set IS a necessary
condition on the match's own first byte. Consumer (ii) is unaffected by §4 and
remains the cleaner half of the row.

---

## 5. The findings value and the consumer interface

D83's 2026-09-22 addendum rules the shape: **the findings file is a set of
NAMED ANALYSIS VALUES, not a frequency table**; `freq` is the first value, not
the shape; the block is an open set a target's config references; a later
analysis is a new named value in the same file, never a new mechanism. This
note proposes the value and the consumer interface **and not the format**,
which stays `[DD-13b]`'s.

### 5.1 The value, and the format for it ALREADY SHIPPED

**Name: `freq`** — and the note's charter to "name the value and define its
schema line" is discharged by reporting that the schema line exists. `[DD-13b]`
wave 23 landed it; `src/parse/rxt_schema.def:146` reads

```
PCREC_RXT_SCHEMA(FILE, "freq", TOKEN, 0, DATA, REPEAT, "", FORMAT, PCREC, 23)
```

with a whole `DATA` scope under it (`question`, `reader`, `analyzer`, `row`,
`provenance`), a `--list-schema` row a caller can already fetch, and a spec
section (`docs/spec/rxt_format.md`, "`freq` — the data block"). The open-set
property the D83 addendum rules is the `REPEAT` cardinality plus the `defname`
namespace: a later named analysis is another `freq <name>` block, never a new
mechanism.

**Two things in that shipped row bear directly on this design.**

* The body requires a **`reader <text>`** line — *"the selection point that
  consumes it"* — *"exactly one, required"*, and the spec says why: it is what
  makes *"a block nobody reads is not emitted"* a parse-time fact rather than a
  review convention. **`[OPT-FIRSTSET]` is the first mechanism that can put a
  value in that field.** The `reader` for this note's consumer is
  `rx_can_begin_match` derivation, `src/opt/` (§5.2's accessor).
* The spec records the one half that is NOT done: a `config` body's
  `analysis <list>` line names data blocks, and *"its value shape is checked;
  the names are not resolved in this build."* **That resolution — not a format
  — is what this row would need**, and it is exactly the place where D83
  addendum item (4)'s design consideration lands (resolve a named analysis the
  way `include`/`lib` resolve, through the `-I` library path, rather than
  inventing a parallel lookup). §10 leaves the decision with the format.

The only content question left for the value itself is the `row` shape, and
the smallest honest one is two columns — `byte` (0..255) and `count` — with
the denominator on its own row, read through `docs/spec/table_contract.md`'s
declared-column rule rather than positionally.

### 5.2 The consumer interface

One accessor, read at analysis time and nowhere else:

```
    double pcrec_findings_density(const Ctx *cx, const unsigned char set[32]);
```

— the summed relative frequency of a byte set under the attached findings, or
the STATIC DEFAULT (§5.3) when none is attached. Three properties make it the
DEFAULT path rather than an expert path, which is what the addendum's item (3)
requires:

* it never fails: no findings, or a findings file with no `freq` block, falls
  back to the static table, so no call site needs a "do we have a profile"
  branch;
* it is the **only** reader of the findings data in the compiler, so a second
  consumer (`[OPT-A]`'s rarest-byte prior, `[OPT-4]`'s collapse decision,
  §5.5's pick rule) is a second CALL and not a second mechanism;
* it is pattern-blind by construction — it takes a byte set, never an AST —
  which is the addendum's item (2) boundary made structural instead of
  remembered.

### 5.3 The static default, and its justification

`pcrec` ships a small set of **named static analyses** (addendum item 3) —
each a shipped `.rxt` carrying one `freq <name>` block, which is what §5.1's
already-landed format makes free:
`html`, `tsv`, `json`, `log`, `prose`, ..., each a `freq` table derived by a
generator beside a reference corpus sample, following `third_party/`'s own
derived-data shape. A target's config references one by name; a caller's own
findings file is the same shape and overrides it.

When no name and no file is given, the default table is **`prose`**, and the
number the cost model reads from it is a DENSITY. From the bench's own subject
census (`cycle1_analysis.md` §2.1, re-measured here):

| set | density in `t-1m` | `L = (1−d)/d` |
|---|---|---|
| word-63 | 77.2128% | 0.30 B |
| `{d,D,i,I,m,M,n,N,p,P,t,T,s,S}` | 22.2281% | 3.50 B |
| `{t,f,n}` | 7.8872% | 11.68 B |
| `{/}` | 2.8610% | 33.95 B |
| `{A}` | 0.1673% | 596.82 B |

**The threshold the charter asks for is stated as a bracket and not as a
number, deliberately.** The three hand-twins measured bracket it only if
`json-constant`'s reading survives §7's re-run: accepted at `d = 0.167%`,
refuted at `d = 7.89%`, improved-anyway at `d = 22.2%` — a non-monotone
ordering that no density threshold can fit. **If the re-run reproduces**, the
conservative default is `decline when d ≥ 5%` (which declines `{t,f,n}` and
the 14-byte set, and accepts `{A}` and `{/}`), with the ×1.12 `dbnames` win
knowingly forgone: it is inside its own cell's IQR under D119's landing bar,
and a one-sided guard that never accepts a regression is worth more than a
1.12×. **If the re-run does not reproduce**, §3.3 stands and the model ships
as a SANITY FLOOR with no decline arm, because there is then nothing measured
for a threshold to separate.

### 5.4 Why the pair filter (§6) needs none of this

A run's occurrence count is bounded above by the count of its rarest byte, for
every subject, by construction. So a pair filter's selectivity is **never
worse** than the single byte's, and the only thing a findings file could add
is WHICH member to `memchr` — a refinement, not a precondition. That is what
the plan row means by "the remedy WITHOUT a findings file".

### 5.5 A second consumer, found in the same census

`c2/reqpos_census.tsv` joined against the subject census shows that of the 36
`capability` patterns with a necessary byte, **14 have a rarer necessary byte
than the one `[OPT-REQBYTE]` picks**, and for **three of them the rarer byte
is ABSENT from the subject while the picked byte is PRESENT**:

| pattern | picked (PCRE2's rightmost rule) | hits | rarest necessary | hits |
|---|---|---|---|---|
| `nested-comment-rec` | `/` | 30,000 | `*` | **0** |
| `wild-validator-email-owasp` | `.` | 14,826 | `@` | **0** |
| `wild-waf-crs-942500-comment-obfuscation` | `/` | 30,000 | `*` | **0** |

On those three, batch 1's shipped pre-check cannot fire and a
frequency-informed pick would answer the entire find-all call in one pass.
This is a `freq` consumer with a measured population and no design work beyond
"pick the rarest member instead of the rightmost", and it argues for shipping
the interface even if §3.3's verdict stands and `[OPT-FIRSTSET]` needs no
threshold.

---

## 6. The pair extension

Where the single-byte candidate set is dense but a two-byte pair at a fixed
delta is rare, the remedy is a **pair filter**: `memchr` the chosen byte `A`,
then ONE unaligned word load compared against a constant at `p + δ`, before
any attempt or reverse walk. Frank's rulings of 2026-09-22, recorded in the
`[OPT-REQPOS]` row, fix its shape:

* `B` need not be a byte: it is a known-offset RUN of 1/2/4/8 bytes compared
  as one word load — a 2-byte pair and an 8-byte run cost the same instruction
  pair;
* the run MAY OVERLAP `A`: load the word at `p` minus `A`'s position within
  the run, so one compare re-checks `A` with its neighbours (`https://`:
  `memchr` `:`, one 8-byte compare at `p−5`);
* where the run is small CLASSES rather than exact bytes, the same compare is
  load + AND-mask + compare — `[WORD-FOLD]`'s cube compare, which is why the
  two rows share that primitive;
* with a findings value it picks the rarest pair; without one, the leftmost.

**On `json-constant` the pair filter is the whole answer and the single-byte
set is not.** Measured on `t-1m`:

| filter | occurrences | density | `L` |
|---|---|---|---|
| `{t,f,n}` (M3's set) | 82,703 | 7.8872% | 11.68 B |
| `{tr, fa, nu}` (the pairs) | **3,443** | **0.3284%** | **303.55 B** |
| `{true, fals, null}` | **0** | 0% | ∞ |

A 24× reduction in candidate rate at the pair grain and a complete answer at
the quad grain — on a pattern whose single-byte narrowing the profile
refuted. `json-constant` is an alternation of three literals with disjoint
first bytes, so the sound emitted form is the existing byte-class skip loop
followed by one 16-bit word compare against three constants at each hit, which
is the cube-compare primitive at `n = 3`.

The contrast that shows the filter is not free selectivity everywhere: on
`aws-access-key-id` the pairs `{A3, AK, AG, AI, AR, AN, AS}` read 0.1433%
against `{A}`'s 0.1673% — **1.17×, nothing.** The pair pays exactly where the
single byte is dense, which is the same place the §3 model says the skip loop
struggles.

---

## 7. The D77 measurement, before anything is built

`[OPT-5]` STEP 0's method and `cycle1_analysis.md` §3's block form; the shared
setup (0.1–0.5) is that document's and is not repeated. Linux, via the
executor; nothing timed on darwin.

```sh
cd "$OPT1"
# F1  THE RE-RUN THAT GATES THE DECLINE RULE.  cycle1_profile.md M3.c reads
#     json-constant's twin at 3.4064 ns/byte where its own artifact's counts
#     predict 1.4408 (firstset_design.md 3.4).  Re-run M3.c EXACTLY as
#     cycle1_analysis.md M3.c states it -- same artifacts, same overwrite,
#     same subject -- five trials rather than one, reporting each trial.
for T in 1 2 3 4 5; do
  "$OPT1/twin_wild-codegrammar-json-constant" "$OPT1/subj/t-1m.bin" 5
  "$OPT1/base_wild-codegrammar-json-constant" "$OPT1/subj/t-1m.bin" 5
done
# EXPECT if the published reading is right: twin ~3.41, base ~3.09, on every
#   trial.  EXPECT if it was a one-sample artefact: twin at or below ~1.6.
#   A twin that lands near 1.44 ns/byte REPRODUCES firstset_design.md 3.1's
#   model and RETIRES the decline rule; a twin that reproduces 3.41 refutes
#   the model and the missing term must be named before the row proceeds.

# F2  THE SOUNDNESS ARM, and it is a CORRECTNESS run, not a timing one.
#     Build both twins and the repaired twin, and run all three on the
#     witness firstset_design.md 4.1 names.
printf 'atrue xnull ' > "$OPT1/subj/ctx.bin"
for B in base_wild-codegrammar-json-constant twin_wild-codegrammar-json-constant \
         reseed_wild-codegrammar-json-constant; do
  "$OPT1/$B" "$OPT1/subj/ctx.bin" 1
done
# The reseed_ artifact is twin_ plus firstset_design.md 4.4's two lines.
# EXPECT: matches=0, matches=1, matches=0.  A twin reading matches=0 here
#   refutes 4.2 and the whole soundness finding with it -- which is the
#   outcome that would make M3's own identity check sufficient after all.

# F3  WHAT THE REPAIR COSTS, once F2 has shown it is needed.  Same subjects
#     as M3.b, reseed_ against twin_.
for S in t-64k t-256k t-1m; do
  "$OPT1/twin_wild-codegrammar-json-constant"   "$OPT1/subj/$S.bin" 5
  "$OPT1/reseed_wild-codegrammar-json-constant" "$OPT1/subj/$S.bin" 5
done
# EXPECT: within noise.  The counts are IDENTICAL (firstset_design.md 4.4),
#   so the only difference is one table lookup per skip-loop exit that
#   skipped -- 59,383 over 1,048,576 bytes.  A reseed_ artifact more than
#   ~2% slower than twin_ is the carve-out failing and is a finding.

# F4  CONSUMER (ii), which 4.5 leaves untouched and which nothing has timed.
#     nested-comment-rec is the row the mechanism is claimed on: first byte
#     '/', 2.8610% of the subject, against an every-position VM walk today.
"$OPT1/pcrec/build/pcrec" --features all -p rx -o "$OPT1/ncr.c" \
    --pattern "$(cat $BENCH/bench/capability/patterns/nested-comment-rec.rx)"
grep -E 'RX_ENGINE |RX_VM_PREFILTER ' "$OPT1/ncr.c"
# EXPECT: "vm" and "none" -- the artifact this consumer exists for.
# Then hand-twin rx_search_run's attempt loop with a memchr('/') skip and
# time both on t-1m, checking matches= first.
# EXPECT: ~35x fewer attempts (1/0.0286).  A twin that is not materially
#   faster refutes consumer (ii) independently of everything above.
```

---

## 8. The four lenses

| lens | verdict |
|---|---|
| **specific vs general** | GENERAL. It replaces one derivation inside an existing pass with a better one and adds one consumer; it names no pattern and no construct. The pair extension (§6) is the same analysis read at a coarser grain, which is a widening and not a sibling. |
| **core vs derived** | DERIVED. The set is an analysis over the AST; both automata, both emitters and every table size are untouched. §4's repair is derived too — it reuses `rx_forward_seed_state`, an emitted table that exists today. |
| **applicable vs assumption-changing** | APPLICABLE as repaired, ASSUMPTION-CHANGING as stated. §4 is the whole of this cell: M3's version quietly changes the assumption that the scan loop's state is a faithful function of the bytes consumed. With the re-seed it does not, and a denied build is byte-identical to today. |
| **fits-arch vs refactor** | FITS. One `src/opt/` analysis, one emitted table's contents, one deny flag. Consumer (ii) adds a skip to the VM entry, which is where the hybrid prefilter's own skip already lives. |

---

## 9. The axis, the stamp and the sabotage direction

**Axis.** `-fno-first-set` / `PCREC_NO_FIRST_SET`, plus `PCREC_FORCE_FIRST_SET`
— one row in `src/core/axes.def`. Denial falls back to today's start-state
derivation, which is what makes the change bisectable and what makes
`make test-axes` answer-identity denied/forced the correctness bar.

**Stamp.** On the DFA route the existing `RX_DFA_PREFILTER` value moves on the
reached population and IS the observable; no new stamp. Consumer (ii) needs
one: `<PREFIX>_VM_PREFILTER` gains the value `first-byte`. **If §4's repair
lands, the emitted scan loop gains a line and that is a `D76`/`D94` `abi`
event** — the bump ritual's grep over every reader of the current number, the
identity-gate re-pin, `make test-codegen` before delivery, and then the suites
that count (registry, codegen, rxtsource), because a reader that never cites
the number still moves with it.

**Sabotage direction.** Widening the derived set by one byte that cannot begin
a match is invisible to every answer check — it only costs time — so the row
is a **stamp/count** detector, pinned against a corpus census of
`|rx_can_begin_match|`. §4 adds a SECOND row that a count cannot see and an
answer check can: **delete the re-seed**. Its reach witness is any
`\b`-leading pattern with a narrowed set, and `tests/` has no subject that
reaches it today — `"atrue xnull "` is the shape the row's own fixture must
carry, because the bench's throughput subjects answer `matches=0` either way
and are structurally blind to it.

---

## 10. What this note does not settle

* **Whether `json-constant`'s regression is real.** §7 F1 is the gate. Until
  it runs, both the decline rule and its absence are unsupported.
* **Any throughput claim for the repair or for consumer (ii).** No clock was
  read on darwin. §4.4's "changes no count" is a count statement and not a
  timing one; F3 and F4 are owed.
* **`w`'s stability beyond four configurations of one subject.** §3.1's model
  rests on it being 3.7–5.4, and every one of those numbers comes from
  `t-1m`. A pattern whose machine walks far from a false candidate would move
  the model and nothing here bounds it.
* **The findings-file FORMAT**, which is `[DD-13b]`'s and is deliberately not
  proposed here — §5.1 gives the VALUE and §5.2 the consumer interface only.
  Whether a named analysis resolves through the `-I` library path and the
  include opcode (D83 addendum item 4, a design CONSIDERATION and not a
  ruling) is weighed in §5.1's favour — one lookup mechanism, no parallel
  one — but the decision belongs with the format, and the concrete unfinished
  item is `config`'s `analysis <list>` name resolution, which
  `docs/spec/rxt_format.md` already records as unresolved in this build.
* **Whether a size term should price the pair filter's constants.** §6's word
  compares add emitted bytes on a route (`[OPT-REQPOS]` tier 2b) whose row is
  not this one.

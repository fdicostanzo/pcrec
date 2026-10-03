# [OPT-GAPREPORT] first instance: where pcrec is really behind (2026-10-03)

This is lane `gaprep`'s report, on branch `lane/gaprep` from `d986874b`. Its
contract is D144 addendum 2. It is the pre-round-2 bench outlier read that
D144 item 6 asks for. The work is analysis only: nothing under `src/`,
`cli/`, `lib/` or `tests/` changed. Nothing was written in pcrec-bench, and
no timing was taken on this box. Every number in this file comes from the
bench's published reports for the `fc719ca4` window, or from a compile-side
read of emitted stamps. The scripts and data are in `gapreport/` (see its
`CLAUDE.md`).

## Summary (one screen)

**Scope.** 603 throughput and search cells compare like with like (same
subject, same regime, both sides `measured`) between pcrec's shipped default
(`auto`) and **pcre2-jit**, the primary peer. pcrec **leads on 501, is level
on 15, and trails on 87**. A further 158 match-regime cells compare only
across forms; there pcrec leads 152 and trails 3 (§4). Most of the 87
trailing cells are not algorithmic. On **80 of them, pcre2-interp is slower
than pcrec** (by more than the null band). That means the JIT is winning on code generation and SIMD
search, not on a mechanism pcrec lacks.

**The five largest gaps, grouped by cause:**

| # | cause group (§2) | worst cells | algorithmic evidence | owner row |
|---|---|---|---|---|
| 1 | **START-SET**: no first-byte start skip. On the DFA, a leading `\b` defeats it; on the VM, backreference and recursion routes have no candidate scan at all | aws-access-key-id **x44.0** behind jit (pcre2-interp is x18.5 faster than pcrec); quoted-delim-match **x21.7**; balanced-parens-rec **x9.1**; loglines stack-frame **x4.8**; json-constant x2.1 | yes, on 7 cells (interp, pcre2-dfa, re2, onig) | [OPT-FIRSTSET] + [OPT-VMSEED]: one question, two consumers (D124) |
| 2 | **CTX**: `\bA\b.{0,N}?\bB\b` overflows the DFA and runs as a count-collapsed hybrid | loglines level-context **x3.8** behind jit (x10.5 behind rust); bounded ctx-* x1.5 | yes (interp x1.9) | [OPT-VMLIT]'s named trigger (now measured); [ENG-TACTICS] |
| 3 | **NULLABLE-ANCH**: an anchored, nullable, capture-forced VM gets no DFA gate | evil-alt-nested x6.1 behind jit, **x38 behind re2**; trim-nested-star x3.0 behind jit, **x1081 behind re2** | yes (re2, which captures) | **NEW** |
| 4 | **U8-PICK**: under `-e utf8`, every literal's DFA prefilter is `offset-set "0,1*"`, and the run-pinned and memchr forms never appear | Straße **x15.6 behind re2**; `@é` x7.9; `😀` x5.5 (pcrec is still ahead of jit) | yes (re2) | **NEW** |
| 5 | **CI**: a caseless literal scans as a byte-class | union-select **x16.6** behind jit; slack-webhook x6.9; `(?i)cat` x2.3 | yes (re2-longest, re2) | round 1: [OPT-LITSCAN] S4 + [WORD-FOLD], in flight |

**The largest non-algorithmic gap is SCAN-SIMD** (19 cells; jit x1.9 to
x3.8, rust up to x5.7 ahead). On these cells pcrec already beats every
scalar engine, and what is missing is the JIT's and rust's vectorized
character-pair search. That is a SIMD-phase deferral (D119), not a round-2
item. **WIDE-ALT** (31 cells, rust Teddy) is in the same position, and
**BACKTRACK** (14 cells, where interp is slower than pcrec everywhere) is a
FUNDAMENTAL disposition.

**Recommended round-2 slate (§5):**

1. START-SET as one mechanism with two consumers (FIRSTSET re-seed narrowing
   on the DFA side, a first-byte seed on the VM side).
2. U8-PICK, opened by a cheap pcrec-side twin that compares the `-e byte`
   and `-e utf8` artifacts of the same literal.
3. NULLABLE-ANCH, after a compile-side census.
4. CTX as a profile-then-design item, not yet a build.

**Pins.** The pcrec cells were measured at `fc719ca4` (abi 50), 2026-10-01/02.
Main is now abi 55. A stamp census of all 331 bench patterns finds **no
selection fact moved** since the pin (§1.3). Round 1, which is landing as
abi 56-58, will move CI, LKA and the BCLS match cells, so those groups are
"re-measure after round 1", not slate candidates.

---

## 1. Method, pins, comparators

### 1.1 Input

Each sub-bench uses its LATEST measured pin. That is the `b120b121-fc719ca4`
report group for all seven sets in O-82's A5: capability@0.1, syntax@0.1,
utf8@0.1, loglines@0.1, bounded@0.3, email-specimen@0.2 and altwide@0.3.

These groups do not carry a `.matrix.tsv` (only the olevel group does). So
the input is each group's own report `.tsv`, `rank` section only. That is
the same query and set grain the bench's matrix derives from. Cells are read
by `gapreport/extract.py` and nothing is re-derived from ledgers or the
store.

The only other bench files read are bench INPUTS:

- `manifest_throughput.tsv`, for subject bytes;
- `expectations.tsv`'s oracle `nmatches`, for ns/B and ns/match (`nmatch.py`);
- `patterns/*.rx`, which were compiled for stamps.

**What was measured when:**

| set | pcrec (`fc719ca4`) | pcre2-jit / interp | rust | re2 / onig / tre / vectorscan / pcre2-dfa |
|---|---|---|---|---|
| capability | 10-01/02 | 09-17 | 09-22 | 09-17..22 |
| syntax | 10-01/02 | 09-07 | 09-20 | **not in roster** |
| utf8 | 10-02 | 09-26 | 09-26 | 09-26 (re2, onig, vectorscan, pcre2-dfa) |
| loglines | 10-02 | 09-02 | 09-20 | **not in roster** |
| bounded | 10-02 | 09-04/05 | 09-20 | **not in roster** |
| email-specimen | 10-02 | 09-02 | 09-20 | **not in roster** |
| altwide | 10-02 | 10-02 (jit only) | 10-02 | **not in roster** |

Every comparison except altwide therefore spans two windows.

### 1.2 The metric (D144 addendum 2 items 2-3, addendum 1)

- **pcrec side**: the shipped default, engine `auto`.
  - Against a capturing comparator, it is `auto-caps`.
  - Against a NO-class comparator, it is the better of `auto-caps` and
    `auto-nocaps`. The NO-class comparators are rust-default, vectorscan and
    pcre2-dfa, per the bench's I-99/I-100 classes.
  - The forced `vm-*` and `dfa-*` arms are carried only as explanation.
- **MEASURED only.** A testee whose row is `inconclusive-spread`, excluded,
  refused or unsupported is not a side. The only inconclusive rows (syntax
  `vm-nocaps`) never touch `auto`.
- **Scale tiers**, set by the smaller side's per-subject mean:

  | tier | per-subject mean | how it is read |
  |---|---|---|
  | **A** | ≥1 µs | ratio, null band x1.10 |
  | **B** | 100 ns to 1 µs | ratio, null band x1.15 |
  | **C** | <100 ns | absolute delta per call, never scored. NULL when the delta is under 41% of the comparator's per-call figure |

  The bands are `cycle2_batch2_reading.md` §1's cross-window,
  program-identical null bands: +8.77% µs throughput, +11.16% search,
  +41.09% below 100 ns. They are the right noise model because every
  comparison spans two windows.
- **Comparator grouping (item 2).** pcre2-jit is the **PEER**. The REFERENCE
  CEILINGS each carry a semantic flag:

  | ceiling | semantic flag |
  |---|---|
  | pcre2-interp | same semantics, an interpreter |
  | pcre2-dfa | longest match, no captures |
  | re2 | leftmost-first, no backtracking features |
  | re2-longest | LEFTMOST-LONGEST |
  | oniguruma | backtracker, Ruby dialect |
  | tre | POSIX longest |
  | rust | no backtracking features, NO-class driver, **SIMD prefilters** |
  | vectorscan | excluded as a target: SIMD-first, nosom/nocaps (cycle1 §0 rule 2) |

- **Algorithmic evidence (D119).** A gap is algorithmic only where a SCALAR
  engine also beats `auto` on some cell of the group. The scalar engines
  are pcre2-interp, pcre2-dfa, re2, re2-longest, onig and tre. This is
  cycle 1 §0's discriminator, applied per group.
- **Priority (item 4).** Score = Σ realism × log2(ratio) over a group's tier
  A/B cells, computed separately against the peer and against the worst
  ceiling. Realism by set is a stated judgement:

  | set | realism |
  |---|---|
  | loglines, email | 1.0 |
  | capability (curated wild patterns) | 0.75 |
  | utf8 (real-prose mix) | 0.6 |
  | syntax, bounded, altwide (synthetic or hazard) | 0.4 |

  Breadth is the number of distinct cells sharing one cause.
- **Cause assignment** is a judgement, recorded line by line in
  `gapreport/causes.tsv`. It comes from reading each losing pattern's D81
  stamps, its text, its forced, interp and ceiling columns, and the
  compiler's own `--emit-ir` prefilter reason. The scripts compute, and
  `causes.tsv` decides.

### 1.3 What landed between the pin and main (abi 50 → 55)

| change | abi | could move |
|---|---|---|
| [CLS-TREE] S2 (`22d150a8`..`2c45260a`): VM byte classes chosen by the kit's ROWS; scan-edge axis-I kit body | 51-53 | VM class-heavy cells, and scan-edge cells (BCLS `edge=bitmap/range`, WIDE-ALT `edge=range`, iso-ts, altorder) |
| K78 (`6b86a29b`): the DFA dead-group fill moves to the success sites | 55 | DFA artifacts with dead capture groups, per-match, small |
| K79/K80 | 54 | prefix rendering and the abi guard: scaffolding only |

Compiling all 331 bench patterns with both `fc719ca4` and main
(`gapreport/stamp_diff.txt`) gives **zero selection-stamp differences**:
engine, prefilter, scan, edge, req and reseed are all unchanged. The only
difference is a refusal's byte count. The emitted text does change, for
example CLS-TREE S2's `(unsigned)(…) <= 9u` spelling. Whether the machine
code moved is the bench's program-identity census to say (bench Q4).

**Round 1, now landing as abi 56-58:**

- [OPT-HYB-RESEED-XCALL] moves LKA, and match-dense hybrids generally.
- [OPT-LITSCAN] S4 + [WORD-FOLD] moves CI.
- [OPT-VEDGE] moves the `\z` match cells in BCLS (`cls-upto-2048/4096`) and
  the altwide whole forms.

[SEL-COST] step 1 was replaced by VEDGE (plan.md `[OPT-VEDGE]`).

---

## 2. The ranked cause groups

The columns are:

- **peer**: cells behind jit, the worst ratio, and the score.
- **ceiling**: cells behind a reference ceiling, the worst ratio with the
  engine, and the score.
- **alg.**: whether a scalar engine also wins.

The cells are listed inside each group below. All numbers come from
`gapreport/rank.json`.

| rank | group | breadth (sets) | peer: n / worst / score | ceiling: n / worst / score | alg. | row | disposition |
|---|---|---|---|---|---|---|---|
| 1 | START-SET = FS-DFA + FS-VM | 16 (cap, logl, syn, utf8) | 12 / **x44.0** / 16.40 | 15 / x29.4 rust / 17.15 | **yes** | [OPT-FIRSTSET] + [OPT-VMSEED] | **slate** |
| 2 | CTX | 10 (logl, bnd) | 10 / x3.83 / 5.05 | 7 / x10.5 rust / 10.96 | **yes** (interp) | [OPT-VMLIT] trigger; [ENG-TACTICS] | **slate (profile first)** |
| 3 | NULLABLE-ANCH | 2 (cap) | 2 / x6.09 / 3.15 | 2 / **x1081 re2** / 11.50 | **yes** (re2) | **NEW** | **slate (census first)** |
| 4 | U8-PICK | 10 (utf8) | 0 (pcrec leads jit) | 10 / x15.8 rust, x15.6 re2 / 10.88 | **yes** (re2) | **NEW** | **slate** |
| 5 | CI | 12 (cap, syn, utf8) | 5 / x16.6 / 6.35 | 10 / x4.7 rust / 8.18 | **yes** (re2) | round 1: S4 + [WORD-FOLD] | re-measure after round 1 |
| 6 | SCAN-SIMD | 19 (cap, logl, syn) | 15 / x3.75 / 9.69 | 13 / x5.7 rust / 9.25 | no (rust-only) | [OPT-SIMD] | SIMD-phase deferral |
| 7 | WIDE-ALT | 31 (altw, utf8) | 0 (pcrec 10-500x ahead) | 31 / x11.6 rust / 8.21 | no (rust-only) | [OPT-SIMD], [OPT-ALTHASH] | SIMD-phase deferral |
| 8 | DENSE | 15 (cap, syn) | 15 / x1.81 / 3.26 | 8 / x2.4 rust / 3.14 | no | [OPT-LITSCAN] F6 (partial) + **NEW** profile | profile ask |
| 9 | LKA | 9 (cap, syn) | 9 / x3.47 / 4.77 | 0 | no | round 1: [OPT-HYB-RESEED-XCALL]; [CTX-PREFILTER] | re-measure after round 1 |
| 10 | INNER-LIT | 2 (logl) | 0 (pcrec x3 ahead) | 2 / **x23.7 rust** / 4.57 | **unknown**: no scalar ceiling in the loglines roster | [ENG-TACTICS]; [OPT-REQPOS] tier 2 | bench Q2 first |
| 11 | BACKTRACK | 14 (cap, syn) | 14 / x2.99 / 4.04 | 0 | no: interp slower on all 14 | none ([ENG-DIRECT] at most) | FUNDAMENTAL (D119) |
| 12 | CARET | 2 (cap) | 0 | 2 / x5.45 re2-longest / 1.83 | **yes** | [OPT-ATTEMPT-SPLIT], [ENG-ABS-CARET] | candidate, 1 cell |
| 13 | BCLS | 9 (bnd, cap) | 5 / x2.34 / 1.21 | 4 / x28 rust (ns-scale) / 0.18 | no | [OPT-NEG], [OPT-3-RUNEND]; match cells → [OPT-VEDGE] | low |
| – | CALL-FLOOR, ENDWIN-ENC | 4 | ns-scale only | rust +3.3..3.9 ns/call; +7.3 ns/call | no | [OPT-ENDWIN-ENC] | NULL-scale; nothing filed (addendum 1) |

The "combined" view double-counts a cell that is behind both the peer and a
ceiling, so read the two scores separately. The order above is the
D119-filtered judgement: algorithmic groups first, then by score, realism
and breadth. Raw combined scores are listed for transparency:

| group | combined score |
|---|---|
| START-SET | 33.6 |
| SCAN-SIMD | 18.9 |
| CTX | 16.0 |
| NULLABLE-ANCH | 14.6 |
| CI | 14.5 |
| U8-PICK | 10.9 |
| WIDE-ALT | 8.2 |

### 2.1 START-SET: where can a match start (compare_stack L3), two consumers

This is one question with two consumers, so per D124 it gets one table and
two engine hats.

**FS-DFA (the DFA hat): a leading `\b`/`\B` defeats the first-byte skip.**
The stamps read `byte-class-bounded` or `offset-set-bounded "0,1*"`, never a
first-byte memchr.

| cell | gap |
|---|---|
| cap `wild-secrets-aws-access-key-id` thr | jit x44.0, interp x18.5, pcre2-dfa x18.8, rust x29.4; 2.92 ns/B against jit's 0.066 |
| cap `wild-codegrammar-json-constant` thr | jit x2.12, re2 x1.88, rust x15.0 |
| cap `wild-waf-crs-942140-dbnames` thr | re2 x1.82 (pcrec ahead of jit) |
| cap `wild-secrets-github-pat` thr | jit x1.28, rust x2.69 |
| loglines `stack-frame` thr / short | jit x4.83 / x2.06, rust x4.17 / x2.80 |
| loglines `bignum` thr | jit x1.16 |
| loglines `hex32-id` thr / short | rust x1.77 / x1.46 |
| syntax `asr-wb` / `asr-nwb` thr | jit x2.87 / x3.21 |
| utf8 `asr-b-ascii` thr | rust x5.06 |

- **Row:** [OPT-FIRSTSET]. The narrowing plus the re-seed is ratified as
  batch-3 material, and its soundness repair already ships as
  `pf_emit_ofs_reseed`. stack-frame is also [OPT-A]'s O-8 witness, which was
  3.0-6.5x then and is 4.8x now.
- **Upside basis:**
  - pcre2-interp and pcre2-dfa are scalar, carry PCRE2's compile-time
    start-up optimisation, and are already **x18.5-18.8 faster on aws**.
    That is a floor for what a first-byte skip buys there.
    `firstset_design.md` §2 puts aws's candidate density at 0.17%.
  - json-constant: x1.9, measured on the twin (O-46 F1: 1.52-1.66 against
    3.09 ns/B).
  - dbnames: re2's x1.82.
  - The `asr-*` and stack-frame cells are JIT- and rust-only. The FIRSTSET
    cost model prices them, but no scalar comparator in the roster bounds
    them.
- **Settling:** O-46's twin method on aws and stack-frame (F3, "what the
  repair costs", is still owed). Then the alpha loop on the Linux box.

**FS-VM (the VM hat): VM routes with NO candidate scan.** The compiler's own
reason is `no-backreference` / `no-linked-call`: "the erased approximation is
neither a sound superset nor the true span". That rule is right for a
*span* prefilter. A *first-byte start set*, however, is sound without
erasure, and PCRE2 computes it for exactly these patterns.

| cell | gap |
|---|---|
| cap `quoted-delim-match` thr / short | jit x21.7 / x3.33 (C: +103 ns/call), onig x2.59, interp x2.37 |
| cap `balanced-parens-rec` thr | jit x9.11, interp x1.76 |
| syntax `bak-k-named` thr | jit x3.38, interp x1.24 |

- **Row:** [OPT-VMSEED]. As chartered it seeds from a necessary RUN. These
  cells need it widened to the first-byte set: `["']`, `(` and `<` here.
  This is the same set FS-DFA needs, which is why the two are one item.
- **Upside basis:** the interp/onig ratios are lower bounds (x1.24-x2.6),
  and the JIT ratios are the reach (x3.4-x21.7).
- **Settling:** the VMSEED row's own census, re-run under the first-byte
  framing (compile-side), plus one hand twin on quoted-delim-match.
  `firstset_design.md` §4 shows the narrowing is unsound without a re-seed
  for the DFA consumer, so the VM consumer's contract (K64's step budget)
  must be stated in the shared row, per D124 item 3.

### 2.2 CTX: the "two keywords within N" family

| cell | gap |
|---|---|
| loglines `level-context` thr / short | jit x3.83 / x2.97, **interp x1.91 / x1.59**, rust x10.5 / x7.96 |
| bounded `ctx-lazy-64/256/1024`, `ctx-greedy-256` thr | jit x1.52-1.56, rust x7.1-7.4 |
| the same four, short | jit x1.18-1.38 |

Every one stamps `vm/hybrid/count-collapsed`, `RX_VM_RESEED "clamped"` and
`dfa overflowed: >32000 states`, and starts with `\b(?:alt)\b`.

- **Rows:** [OPT-VMLIT]. Its named trigger is "ctx/level-context vs
  pcre2-jit, 1.5-2.9× residual", and it is **now measured at the current
  pin: x3.83 on real log text**. Also [ENG-TACTICS]: P·L·S around the
  necessary inner literals (`timeout|refused|…`). Part of the gap is the
  leading `\b` (START-SET).
- **Upside basis:** interp is x1.9 faster on level-context, so a scalar
  engine does it, and that is the lower bound. The reach is jit x3.8 and
  rust x10.5.
- **Settling:** first a profile of where level-context's time goes:
  hybrid scan, clamped re-seed, or VM verify. That needs the Linux executor
  ([OPT-B]'s profile-channel note applies). Only then a mechanism choice.
  It is realworld (loglines), so it ranks above its raw score.

### 2.3 NULLABLE-ANCH (NEW): an anchored nullable VM with no DFA gate

| cell | gap |
|---|---|
| cap `evil-alt-nested` (`^(([a-z]+)*)+$`) thr | jit x6.09, **re2 x38.3**; the shipped `dfa-nocaps` arm is x408 faster than auto. On the short-subject regime, auto is EXCLUDED: 10 give-ups at pass rate 0.9733 |
| cap `trim-nested-star` (`^(\s+)*$`) short | jit x3.00, **re2 x1081** |

`--emit-ir` gives the reason `no-nullable-exact`: "would admit a zero-length
match at every position and could never dismiss one". With a `^` anchor
there is only one position. A DFA gate answers no-match in linear time, and
the VM then runs only on subjects that match. re2 is a capturing engine and
is this far ahead.

- **Row: NEW**, proposed `[OPT-NULLABLE-ANCH]`: refine [OPT-4.2]'s
  nullable decline for start-anchored one-attempt machines. K64's lesson
  applies: state the gate's guarantee to the VM consumer.
- **Upside basis:** the measured `dfa-nocaps` arm is two to four orders of
  magnitude faster on these subjects, and the cells' only give-ups go away.
  Breadth is 2 synthetic-hazard cells. They are ReDoS shapes, which is
  exactly what users hit.
- **Settling:** first a compile-side census: how many corpus and bench
  artifacts stamp `no-nullable-exact` with a start-anchored machine. Then
  one hand twin with `-fprefilter`, which already overrides the decline.

### 2.4 U8-PICK (NEW): `-e utf8` literals always scan at byte offset 1

**The finding.** Under `-e utf8`, none of the 76 utf8 patterns gets a
`run-pinned` prefilter, and 21 stamp `offset-set "0,1*"`. syntax, in byte
mode, has 19 run-pinned out of 95.

`gapreport/u8pick_probe.txt` shows the same literal in both encodings:

| literal | byte mode | `-e utf8` |
|---|---|---|
| `cat`, `Strasse`, `item done` | run-pinned | `offset-set "0,1*"` |
| `@é`, `😀` | memchr | `offset-set "0,1*"` |

Also under utf8, `item done`'s `RX_REQ_RUN` becomes `74656d20646f6e65@7`
("tem done", starting at byte 1), and `cat`'s run pick moves from `@0` to
`@2`.

So the utf8 analysis appears to lose offset 0 for literal runs. **This is a
suspected defect, not verified**: the cause was not traced in `src/`.

| cell | gap |
|---|---|
| utf8 `lit-sharp-s` (`Straße`) | 0.568 ns/B against re2 0.036 (**x15.6**) and rust x15.8 |
| utf8 `lit-offset-at-head` | re2 x7.9 |
| utf8 `lit-1ch-4b` | re2 x5.5 |
| utf8 `lit-nfc-pair` | re2 x1.9, rust x8.5 |
| utf8 `lit-1ch-3b`, `qnt-bounded-4b`, `qnt-counted-3b` (O-82 A2's cell) | rust x2.2-2.7 |
| utf8 `alt-nearmiss`, `lit-cyr-run`, `lit-mixed-ascii` | rust x1.2-1.9; harmless when the offset-1 byte happens to be rare |

pcrec is still x3-x11 ahead of pcre2-jit on all of these, because the utf8
JIT is slow here, so the peer view misses this group entirely.

- **Row: NEW**, proposed `[U8-PICK]`. It is adjacent to [TIE-ALIGN] (48
  artifacts left run-pinned after [FIND-TIE]), [OPT-REQRUN-ENC] and
  [FIND-UTF8-DEFAULT]. Whichever of those owns the cause should absorb it.
- **Upside basis:** the byte-mode artifact of the same pure literal already
  takes run-pinned or memchr. For valid UTF-8 input a pure literal matches
  identically in either encoding. re2's 0.017-0.043 ns/B is the scalar
  target, which means up to x5-x16 on the four re2 cells.
- **Settling:** a pcrec-side alpha twin on the Linux box, `taskset`, using
  the bench's utf8 throughput subjects. It compares the `-e byte` and
  `-e utf8` artifacts of `Straße` and `@é`. Then trace why the utf8 k-set or
  run reader drops offset 0.

### 2.5 CI: caseless literal starts (round 1 owns this)

| cell | gap |
|---|---|
| cap `wild-waf-crs-942270-union-select` | jit x16.6, re2-longest x2.27, rust x3.55 |
| cap `wild-secrets-slack-webhook-url` | jit x6.87; pcrec beats re2, rust and onig |
| cap `wild-waf-crs-942160-sleep-benchmark` | jit x1.29, rust x3.49 |
| syntax `mod-i` / `mod-r` (`(?i)cat`) | jit x2.27 / x2.30 |
| syntax `cls-i-class` | rust x1.49 |
| utf8 `ci-ascii-control` | re2 x2.20, rust x4.69 |
| utf8 `ci-sigma`, `ci-strasse`, `ci-moskva`, `ci-kelvin`, `ci-turkish-i` | rust x1.3-3.4 |

- **Rows:** round 1's [OPT-LITSCAN] S4 + [WORD-FOLD]. `waf_attribution.md`
  predicts union-select at 0.12-0.27 ns/B, against 0.724 at the pin.
  Whether 3-byte caseless runs such as `(?i)cat` clear S4's run floor is
  for S4's own census to say.
- **Disposition:** re-measure at round 1's batch gate. Not a round-2 slot.

### 2.6 SCAN-SIMD: sparse literal or class scans where only vector search wins

| cell | gap |
|---|---|
| cap `router-prefix-order`, `file-ext-order`, `altorder-foo-foobar` | jit x2.75-3.75; pcrec beats re2 or ties it (x0.86-1.08), and beats onig, interp and tre |
| loglines `iso-ts` | jit x1.20, interp x0.02 |
| loglines `ipv6` | rust x1.41 |
| syntax `esc-octal-0`, `esc-nl`, `mod-s`, `cls-v`, `cls-h`, `cls-s-lc`, `esc-quote`, `anc-m-caret`, `anc-m-dollar`, `cls-n-uc`, `qnt-quest` | jit x1.94-2.75; interp 3-8x SLOWER than pcrec |
| syntax `cls-pair-ctl`, `esc-tab` | rust x1.2 |

The pattern is consistent. pcrec runs at 0.19-0.88 ns/B, the JIT at
0.06-0.32, and interp at 1.2-1.5. **pcrec leads every scalar engine.** What
the JIT has is SIMD-accelerated first-character and character-pair search;
rust's memchr/memmem/Teddy is the same idea.

- **Row:** [OPT-SIMD], held to the END by D91/D119.
- **Scalar residual:** [OPT-LITSCAN] F6. Per `b108_reading.md` §5, each
  `rx_search` call pays 5-6 ns per pre-check memchr pass, and on these
  sparse cells that is per call, not per byte.
- **Disposition:** SIMD-phase deferral. Recorded as a result, not left as a
  gap.

### 2.7 WIDE-ALT: wide literal alternations (rust's Teddy)

There are 31 cells: altwide `w-*`, `wb-*`, `cnt-*`, `cls[ad]-*`, `s-*`,
`sfx-*`, `srt-*`, `nar4-64`, `pfx3-512`, plus utf8 `alt-distinct-lead`.
pcrec is **10x to 500x ahead of pcre2-jit** on every altwide throughput
cell, and trails only rust: x1.16-1.8 on most, x2.9 on `nar4-64`, x3.8 on
`sfx-64`, **x11.6 on `w-8`**, and x7.3 on `alt-distinct-lead` (where re2 is
level with pcrec). The match-regime cells trail rust by +7 to +22 ns/call,
which is tier C.

- **Rows:** [OPT-SIMD]. [OPT-ALTHASH] (Wu-Manber) is the scalar algorithm
  that could close part of the `w-8`/`sfx-64` gap. Its D77 trigger asks for
  the 512-2048 curve, which has not been measured.
- **Disposition:** SIMD-phase. `w-8` is noted as the one cell large enough
  to test ALTHASH's scalar claim if it is ever opened.

### 2.8 DENSE: match-dense find-all, per-match cost

| cell | gap |
|---|---|
| syntax `lit-cat`, `esc-hex`, `mod-x`, `mod-n`, `grp-noncap` | jit x1.25-1.32 |
| syntax `grp-cap`, `grp-named`, `grp-named-quote` | jit x1.39-1.40 (VM hybrid, captures) |
| syntax `mod-reset`, `mod-unset` | jit x1.32 |
| syntax `cls-dot`, `cls-fold-pair` | jit x1.71-1.81 |
| syntax `alt-two`, `alt-nested` | jit x1.69-1.77 |
| cap `keyword-prefix-order` | jit x1.34 |

Each cell has 2,000 to 11,400 matches. The gap is **+18 to +90 ns per
match** against jit, and interp is slower on all of them. The emitted
artifacts carry `RX_DFA_START "reverse-pass"`, and each find-all call
re-enters `rx_search` with its pre-checks.

- **Rows:** [OPT-LITSCAN] F6 explains 5-10 ns of the per-call share.
  **NEW**: a per-match profile that splits a dense find-all into reverse
  pass, call entry and pre-check, scan restart.
- **Disposition:** a profile ask (Linux executor), not a build. Subject-grain
  data would separate per-byte from per-match cost (bench Q5).

### 2.9 The rest

- **LKA**:
  - Cells: syntax `lka-pos`, `lka-verb`, `lkb-pos`, `lkb-neg`, `lka-neg`,
    `lka-nonatomic`, `grp-atomic-alt` and `qnt-poss-quest` (jit x1.75-3.47),
    plus cap `pwd-strength-chain` short (x1.46). Interp is 2-7x slower on
    every one.
  - Cause: these are SCAN-SIMD's literal scan plus the hybrid hand-off.
    O-81 measured adaptive re-seed costing 5-23% on several of them.
  - Disposition: round 1's [OPT-HYB-RESEED-XCALL]; re-measure.
- **INNER-LIT**:
  - Cell: loglines `kv-quoted`, rust **x23.7** thr (0.050 against 1.19
    ns/B), while pcrec is x3 ahead of jit.
  - The necessary `="` sits at a bounded variable offset 1..32 behind a
    leading `\b`.
  - The loglines roster has no re2 or onig, so whether a scalar algorithm
    gets near rust cannot be judged (bench Q2).
  - Rows: [ENG-TACTICS], [OPT-REQPOS] tier 2.
- **BACKTRACK**:
  - Cells: cap `doubled-word`, `phone-palindrome-6`; syntax `bak-1`,
    `bak-2`, `bak-g-rel`, `bak-py`, `mod-j-uc`. jit is x1.17-2.99 ahead,
    and interp is slower than pcrec on all 14 cells.
  - D119's FUNDAMENTAL bucket (backtracking against a JIT). Recorded
    disposition: no row. [ENG-DIRECT] is the only architecture-compatible
    lever, and it has its own trigger.
- **CARET**:
  - Cell: cap `wild-waf-crs-942360-concat-sqli`, re2-longest x5.45 and re2
    x5.4 (pcrec ahead of jit).
  - `waf_attribution.md` attributes it to [OPT-ATTEMPT-SPLIT] (measured
    x3.51) plus a per-step residual. [ENG-ABS-CARET] is the general row
    (O-82 A3: still the single non-top-level `^`).
  - A clean, algorithmic, one-cell candidate. It narrowly misses the ≤4
    slate.
- **BCLS**:
  - bounded `line-80` (`.{80,}`, jit x2.34), `pw-8-64` (x1.48),
    `cls-atleast-4096` (x1.47), `nest3-16` (x1.15); cap `high-byte-run`
    (x1.19). Interp is slower everywhere, and rust is x14 *slower* on
    `line-80`.
  - [OPT-NEG] covers `.` as not-`\n`, which is a memchr. [OPT-3-RUNEND] is
    priced at ~4 c/B.
  - The match cells `cls-upto-2048/4096` (rust x1.16, cross-form jit x1.8)
    belong to round 1's [OPT-VEDGE]. `cls-atleast-4096` match trails rust
    by +153 ns/call (tier C).
  - Low priority.

---

## 3. Where pcrec LEADS (a sanity check on the comparison)

Against pcre2-jit, over the 603 like-for-like throughput and search cells:

| set | ahead | level | behind | geomean auto/jit |
|---|---|---|---|---|
| altwide@0.3 | 68 | 0 | 0 | **0.024** |
| utf8@0.1 | 136 | 2 | 0 | **0.155** |
| capability@0.1 | 100 | 2 | 21 | 0.359 |
| email-specimen@0.2 | 4 | 1 | 0 | 0.389 |
| bounded@0.3 | 67 | 5 | 12 | 0.431 |
| syntax@0.1 | 112 | 3 | 48 | 0.497 |
| loglines@0.1 | 14 | 2 | 6 | 0.572 |

**The largest leads are O(1) rejects** that the JIT pays a full scan for:

- `anc-dollar`/`anc-z-*`, the utf8 `lit-anchored-run`/`asr-a-z`/`cls-dot-rep`,
  and cap `wild-semdiv-dollar-trailing-newline-pcre2`. These are ns-scale
  per call against a JIT pass over MB subjects, so they are reported as
  absolute deltas (tier C), not ratios.
- The nested-plus give-up shapes, `phone-list-`/`numeric-id-nested-plus`
  short, around 1/4000.
- The altwide wide rungs: `s-2048` at x0.001-0.002.

On the match regime (cross-form, §4) pcrec leads 152 of 158. The comparison
is sane: the pin's pcrec is the faster engine on 83% of like-for-like cells,
and its losses cluster into a few causes.

---

## 4. What could NOT be judged (the honest denominator)

- **Match regime: no same-form peer.** pcre2-jit is measured only in
  `plain` form, and pcrec only in `whole-subject` (separate artifact). That
  affects 158 cells.
  - Read across forms, pcrec leads 152, ties 3 and trails 3:
    `cls-atleast-4096` x5.2, `cls-upto-2048/4096` x1.8.
  - Against rust, which is measured in the same form, see the BCLS and
    WIDE-ALT tier-C rows.
  - This view is flagged and was not ranked (bench Q3).
- **pcrec not measured** (throughput and search):

  | set | pcrec patterns not measured | why |
  |---|---|---|
  | altwide | 5 | refused at the 1 MB emit cap: `w-1024`, `w-2048`, `clsa-1024`, `clsd-1024`, `s-4096` |
  | bounded | 1 | `cls-upto-65535`, NFA state cap |
  | capability | 2 | `wild-datetime-datefinder-alternation`, VM code cap (O-78); `negation-scope-lookbehind-var`, variable-length lookbehind not implemented |
  | syntax | 12 | unimplemented constructs (conditionals, `\c`, `\o`, branch reset, callouts, `(?#`, `\C`, `\R`, `\X`, verbs, extended classes, plus out-of-scope `(*SKIP)`) |
  | syntax | 3 | `rec-1`, `rec-name`, `rec-r-uc` have no auto row in the report |
  | utf8 | 3 refused | UCP `\b`, UCP `\w` wide set, size cap |
  | utf8 | 3 undeclared | `cls-d-ucp`, `cls-s-ucp`, `ci-ucp-invariance` are `unsupported-by-declaration`. The bench's pcrec testee does not declare ucp, although [UCP] U2 merged 09-30 (bench Q6) |

- **No peer:** email `factored` throughput (jit not measured).
- **Missing scalar ceilings.** re2, onig, tre, vectorscan and pcre2-dfa are
  in the roster only for capability and utf8. On syntax, loglines, bounded,
  email and altwide, the algorithmic-evidence test can use only
  pcre2-interp. That is why INNER-LIT (rust x23.7) and the SCAN-SIMD,
  DENSE and LKA cells on those sets cannot be called scalar-reachable or
  not (bench Q2).
- **Cross-window noise.** Every comparator outside altwide was measured 1-4
  weeks before pcrec's window. The null bands of §1.2 absorb this, but a
  ratio near a band edge is not a verdict. 15 cells sit inside the band.
- **ns-scale cells** (tier C): 285 against the peer, of which 7 are NULL.
  They are reported only as absolute deltas, never scored (addendum 1).
- **Machine-code movement since the pin.** The selection stamps are
  identical. The emitted text differs (CLS-TREE S2, K78-K80), and whether
  the machine code moved needs the bench's identity census (bench Q4).

---

## 5. Recommended round-2 slate (≤4)

1. **START-SET: one mechanism, two consumers** ([OPT-FIRSTSET]'s re-seeded
   narrowing for the DFA hat + [OPT-VMSEED] widened from the necessary run
   to the first-byte set for the VM hat).
   - It is the largest, broadest, most clearly algorithmic gap: 16 cells
     across four sets, including realworld loglines.
   - Scalar engines already do it, at x18.5 on aws and x1.24-2.6 on the VM
     cells.
   - The DFA half is ratified and its soundness repair already ships.
   - Doing both hats at once is D124's "one question, one table" applied,
     and it avoids building a second, VM-local start table.
2. **U8-PICK (NEW).**
   - It is probably the cheapest win on the list: a selection or analysis
     fault, not a new mechanism.
   - It has a clean scalar target (re2, x5-16).
   - It is self-settling with a two-artifact twin on the Linux box, so the
     twin should come first.
   - It also tests a suspected analysis defect (offset 0 dropped under
     utf8), which matters for correctness hygiene beyond speed.
3. **NULLABLE-ANCH (NEW).**
   - Only 2 cells, but two to four orders of magnitude against a capturing
     scalar engine, plus a give-up removed on ReDoS shapes.
   - The override flag (`-fprefilter`) already exists, so the twin costs
     nothing.
   - Gate it on the compile-side census so its breadth is known before
     building.
4. **CTX, as a profile-and-design item.**
   - It is realworld (loglines), algorithmic (interp x1.9), and the named
     trigger of an existing row, now measured at x3.8.
   - The mechanism is not yet known, so round 2 should profile it and pick
     between [OPT-VMLIT], [ENG-TACTICS] and START-SET's share, not build
     blind.

**Not slated, with reasons:**

- CI, LKA and the BCLS match cells: round 1 owns them; re-measure at its
  batch gate.
- SCAN-SIMD and WIDE-ALT: SIMD-phase.
- BACKTRACK: FUNDAMENTAL.
- DENSE: profile ask.
- INNER-LIT: needs bench Q2.
- CARET: a good candidate for round 3, or for round 2 if CTX's profile
  slips.

---

## 6. Bench questions for relay

1. **A `.matrix.tsv` for the `b120b121-fc719ca4` groups.** Only the olevel
   group carries one. This report read each group's `rank` section
   directly. Same query, but the canonical surface is the matrix.
2. **Scalar ceilings on the real-text sets.** Add re2 (and onig) to the
   loglines, email, bounded and syntax rosters. Without them, the
   loglines `kv-quoted` x23.7-behind-rust cell and the SCAN-SIMD, DENSE and
   LKA cells cannot be judged scalar-reachable or SIMD-only.
3. **A same-form match-regime peer.** Either measure pcre2-jit in
   `whole-subject` form (PCRE2_ANCHORED|ENDANCHORED), or confirm that the
   two forms answer the same question, so the 158 match cells can be
   ranked rather than flagged.
4. **The program-identity census `fc719ca4 → round-1 pin`**, both engines,
   at the next wide window. It says which cells' machine code moved under
   CLS-TREE S2, K78 and round 1, so the round-1 reading can tell a
   mechanism's effect from the null band.
5. **Subject-grain files for the `fc719ca4` groups.** Only the olevel
   capability group has one. The three subject sizes per throughput set
   allow a per-byte against per-match split for DENSE and SCAN-SIMD.
6. **The pcrec utf8 testee's ucp declaration.** [UCP] U2 merged 2026-09-30.
   `cls-d-ucp`, `cls-s-ucp` and `ci-ucp-invariance` are still
   `unsupported-by-declaration` for pcrec. Is a declaration update due?
7. **Re-measure comparators in the same window when cheap.** Every
   comparator outside altwide predates pcrec's records by 1-4 weeks. A
   same-window jit/rust/re2 pass on capability, utf8 and loglines would
   shrink the null band this report had to apply.

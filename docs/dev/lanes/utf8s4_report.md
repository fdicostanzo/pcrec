# [M5.0] STAGE 4 — DD-1's FOLD CLOSURE (lane `utf8s4`)

2026-09-08, opus, `worktrees/utf8s4`, branch `lane/utf8s4`, branch point
`b14c89a4`.

**Delivered: `(?i)k` under `-e utf8` matches U+212A.** Unicode DEFAULT SIMPLE
case folding ships for literals, ranges and classes; the `byte` encoding's
ASCII fold is untouched and PROVEN untouched; the caseless backreference folds
code points in the artifact; the standing 1:n fold check stage 1 owed and never
built is live; four sabotage rows are DETECTED.

**Read §3 first.** The stage's sharpest result is not in the design at all: the
fold applies PER CONTRIBUTION, not to a class's merged set, and folding the
merged set is a measurable divergence in two directions at once.

---

## 1. What landed

| | |
|---|---|
| `third_party/ucd-16.0.0/CaseFolding.txt` | vendored at Unicode 16.0.0, unmodified, SHA-256 recorded |
| `third_party/ucd-16.0.0/generate.py` | extended; `main()` now emits a LIST of products, so a third source file is a row rather than a rewrite |
| `src/core/fold_tables.inc` | GENERATED: the fold as a CYCLIC NEXT-MEMBER relation, 1,454 classes / 2,938 members |
| `src/gen/enc/utf8_fold_pairs.inc` | GENERATED: the same fold as a sorted `{from, to}` map, spelled as C SOURCE TEXT for the artifact |
| `src/core/internal.h` | `PcrecFoldLink`, `PcrecFold`, and the two objects' declarations |
| `src/core/fold.c` | `pcrec_fold_ascii` (the existing 256-byte loop, MOVED not rewritten) and `pcrec_fold_ucd_simple` |
| `src/gen/enc/enc.h` | `PcrecEnc.fold` — a second scalar, a second D58 seam event, recorded |
| `src/gen/enc/enc_utf8.c` | the caseless-backreference residual rewritten: decode, fold, compare, per character |
| `src/parse/parse.c` | `cls_casefold` takes the fold as a PARAMETER; `p_class` folds its OWN members and unions the produced ones after |
| `tests/utf8/axis06_caseless_fold.rxt` | the D27 corpus PROMOTED to its recorded oracle (4 blocks corrected — §3.4) |
| `tests/utf8/fold.rxt` | NEW, 18 blocks / 45 cells: the range, negate-over-range, `byte`-arm and per-contribution cells the D27 axis could not hold |
| `tests/registry/pc4_check.c` | `check_1n_fold` — the standing 1:n check (§4.1.1, ASK 3), owed since stage 1 |
| `tests/backrefs/fold_agreement_utf8_check.c` | the fold-agreement obligation for `utf8`, wired as `run_backref_diff.sh` §9b |
| `tests/mech/sabotages/` | `S-U1`, `S-U2`, `S-U3`, `S-U11` |
| `docs/spec/cli.md` | D80: `-i` restated as a per-encoding fold, with the four consequences |
| `third_party/` docs | `PROVENANCE.md` gains the file and its two derivations; the directory's *"nothing here reaches a generated artifact"* rule gains its one ruled exception |

**NO `abi` BUMP.** `.abi` reads 24 on both sides and a `byte` artifact is
BYTE-IDENTICAL to the branch point's compiler. What changed in emitted text is
one BACKEND's residual body under one encoding — stage 2's own precedent, which
added four whole residual bodies for `utf8` with no bump. Flagged for the
manager rather than assumed: if the ruling is that a residual body is
scaffolding, the bump and its D94 grep are a merge-time act.

---

## 2. Acceptance, with numbers

| bar | result |
|---|---|
| **byte-encoding answer identity** | **0 differing over 3,120 corpus patterns on all four axes** (`--features all`, `+--engine=vm`, `+-fno-prefilter`, `+--no-captures`), against a compiler built from the branch point by `git archive` — no shared sources |
| `tests/utf8/` (whole directory) | **1,668 passed / 0 failed** |
| `tests/utf8/fold.rxt` (new) | **45 / 0**, green on its first run |
| `tests/utf8/axis06` promotion | **178 of 178 non-`\p` cells green on the FIRST run**, zero semantic divergences; the 8 remaining were the corpus's own wrong oracle (§3.4) |
| `tests/codegen/run_encoding_checks.sh` | **11 / 0** — after the DD12a(i) region fix of §3.11, which the first run found |
| `tests/backrefs/run_backref_diff.sh` | **checks failed: 0**, including §9 (byte, unchanged) and the new §9b |
| §9b's own numbers | 2,938 folding code points / 5,972 ordered pairs compare EQUAL; 63,486 adjacent-pair controls agree; the ASCII restriction ties to 52 bytes exactly |
| PC-4 with the fold check | `pc4: 1:n fold — 22 assertions (11 cells x 2 option words), 0 matching`; PASS |
| **S-U1** | **DETECTED** — 215 passed / 22 FAILED (237/0 clean) |
| **S-U2** | **DETECTED** — 211 / 26 |
| **S-U3** | **DETECTED** — 207 / 30 |
| **S-U11** | **DETECTED** — `run_pc4.sh` exits 1 with exactly 22 FAIL lines naming the design event |

**Owed, and named:** the `make test`/`san`/`mech` battery is the manager's at
merge, per the delivery bar. The 10.46 reference arm is §6.

---

## 3. Findings

### 3.1 THE FOLD APPLIES PER CONTRIBUTION, and the design has no section for it

This is the stage's real result and it is not in `utf8_design.md` anywhere.
§4.2/§4.3 describe folding "the SET", and `p_class` accumulated every class
member — literals, ranges, `\d`'s bits, `\p{L}`'s intervals — into ONE set and
folded that. Under the ASCII fold that was harmless: every producer had already
folded its own contribution, and re-folding was idempotent. Under a Unicode
fold it stops being harmless in **both directions at once**, MEASURED against
libpcre2 (10.48 Homebrew; the structural behaviours are stable across
versions and the 10.46 confirmation is requested in §6):

| cell | oracle | what folding the MERGED set gives |
|---|---|---|
| `(?i)[\p{Lu}x]` on U+0345 | **no** | **match** — U+0345 is an `Mn` that folds with Greek iota, and `L&`'s span holds Ι |
| `(?i)[[:lower:]]` on U+212A | **no** | **match** — a POSIX class would gain Unicode partners |
| `(?i)\w` on U+212A | **no** | **match** — same |
| `(?i)[\p{Lu}k]` on U+212A | **match** | match (the literal `k`) |
| `(?i)[[:lower:]k]` on U+212A | **match** | match |

The last two are why "fold nothing produced" is equally wrong: a literal
sitting BESIDE a produced set must still reach its partner. Only a
per-contribution fold answers all five.

**The rule that falls out, and it is checkable rather than stylistic:**

- a LITERAL or a RANGE written in the pattern folds by **the encoding's**
  relation — it denotes code points in that encoding's repertoire;
- a NAMED BYTE SET (`\d`, `\w`, `\s`, POSIX) folds by **`pcrec_fold_ascii` at
  every encoding** — it is named in the ASCII alphabet, and PCRE2 widens it no
  further without `PCRE2_UCP`, which pcrec has no axis for (§4.5);
- a PROPERTY set folds **not at all** — stage 3's measured substitution
  (`\p{Lu}` under `-i` IS `\p{L&}`) already answered the caseless question, and
  folding on top of it is exactly the U+0345 error.

Implemented as: `cls_casefold` takes the fold as a parameter (each of its three
call sites states which it means), and `p_class` accumulates produced
`EXT_MEMBERS` into a SECOND set that is unioned in AFTER the fold and BEFORE
the negation. §4.3's fold-before-negate order is untouched; what moved is that
the union now happens between them.

**All of `tests/utf8/fold.rxt` section 4 is this finding**, and the byte
identity gate is what says the restructure costs `byte` nothing.

### 3.2 THE TWO FOLDS DISAGREE, so no clamp derives one from the other

The obvious implementation is one Unicode table clamped to the encoding's
`max_cp`. It is wrong at `max_cp == 0xFF`: the Unicode relation folds U+00E9 to
U+00C9, both under 0xFF, and libpcre2's 8-bit non-UTF build folds neither
(§4.5, re-measured here). So the fold is a per-encoding OBJECT — `PcrecEnc`
gains a second scalar, `src/opt/lower_enc.c`'s `LowerOps` shape one seam over,
and `cls_casefold` has no encoding test in it.

`tests/utf8/fold.rxt` section 3 is that discriminator as cells: `\xe9` under
`-e byte -i` must match `\xe9` and NOT `\xc9`. **An implementation that took
the clamp passes every other cell in this delivery and fails those two.**

### 3.3 THE ASCII RESTRICTION OF THE UNICODE RELATION *IS* `pcrec_ascii_fold`, and that is now a check rather than a coincidence

MEASURED: restricted to `[0, 0x7F]`, the vendored relation is exactly the 52
ASCII letters in 26 pairs, and no byte `>= 0x80` has an ASCII fold partner.
That is a happy fact and also a hazard — it means a UCD version bump could
silently move `--encoding=byte`'s answers, which are `options=0`-family
semantics that must not drift with a data file.

`fold_agreement_utf8_check.c` part C asserts it, naming the byte on failure and
calling it a D26 re-measurement event. **This check does not exist in §4.6**;
stage 4 created the hazard it guards by introducing the second fold object.

### 3.4 THE D27 CORPUS'S `[^\p{Ll}]` BLOCKS CARRY A WRONG ORACLE, and the provenance says why

axis06's four `[^\p{Ll}]` blocks record `m "A"` and `m U+212A` under
`PCRE2_UTF|PCRE2_CASELESS`. The live oracle answers **`n` to both** (and to
`"a"`; `"5"` matches). `utf8_design.md` §4.3's own measured table already
carried the `A` cell as *no match* — **the corpus and the design disagreed, and
the design is the one that was measured.**

The cause is visible in the file's own history: those four blocks were `perr`
from authoring until this stage, because `[^\p{Ll}]` needed module
`unicode-props`. **Their oracle values had therefore never been exercised
against anything** — they were reasoned out rather than read off, and reasoning
this cell out is precisely where it goes wrong (under `-i`, `\p{Ll}` becomes
`\p{L&}`, `A` and U+212A are both IN it, and the negation is over that closed
set).

Corrected in place with the original comment kept UNCHANGED for provenance and
the re-measurement recorded beside it, per the directory's own rule. **The
transferable lesson is one this tree has met before at a different level: a
`perr` block's carried oracle is an UNCHECKED CLAIM until the construct
compiles, and promoting it is the first time anything reads it.**

### 3.5 THE D27 AXIS COULD NOT HOLD THE DESIGN'S SHARPEST CELL

axis06 is 48 blocks and **every one of them is a single character** — bare
literals, `\x{...}` escapes, negated singletons. Measured: zero range blocks,
zero blocks mixing a literal with a produced set. So `[a-z]` caseless matching
U+212A — §4.2(c), the result that forces the fold to run on CODE POINTS and the
whole population of sabotage row S-U3 — **had no witness anywhere in the tree**,
and neither did fold-before-negate over a range, nor the `byte` arm's §4.5
discriminator.

`tests/utf8/fold.rxt` is those witnesses: 18 blocks, 45 cells, every expectation
read from the oracle before it was written, 45/45 on the first run.

### 3.6 §4.6's SAMPLE IS WEAKER THAN A SWEEP, AND A SAMPLE CANNOT ASK THE SECOND QUESTION

§4.6 proposes the utf8 fold-agreement check be *"a sampled differential whose
sample is the measured interesting set"* — eight hand-picked pairs. Sweeping
the RELATION instead costs 2,938 residual calls (milliseconds) and contains
those eight by construction. More importantly a sample is structurally
one-directional: **it only ever names pairs that DO fold**, so it cannot see a
residual that folds too MUCH — a decoder losing its bounds, a binary search
returning a neighbour. §9b sweeps 63,486 adjacent-pair controls for exactly
that.

### 3.7 S-U11's PROPOSED GREP FLOOR CANNOT SEE WHAT IT IS FOR

§8.2 gives S-U11 `SAB_REACH_POP` = `tests/registry/pc4_check.c | 1:n fold | 22`
and argues, correctly, that a floor of 11 *"would pass a check that had
silently dropped the UCP arm"*. But 22 is a count of ASSERTIONS and the pop
line greps LINES — in this implementation the string `1:n fold` appears four
times, and any implementation's line count is unrelated to its assertion count.

Resolved by moving the number where it can be true: `check_1n_fold` **asserts
`asserted == 22` itself**, which sees a lost UCP arm directly. The row's floor
is 11 (the cells table) and its header says why.

### 3.8 S-U3's SABOTAGE AS WRITTEN IS NOT A TEXT HUNK

§8.2 spells S-U3's sabotage as *"move it after the byte lowering"*. The lowering
is a separate pass (`src/opt/lower_enc.c`) running after the parser has
published the node, so "moving" the fold there is a rewrite, not a hunk. What
the row DEFENDS is an observable — can the fold reach a partner outside the
byte range — and a fold running after the lowering has exactly one reach.
The shipped row clamps the added partners to `0xFF`, which produces the
design's own stated symptom verbatim (*"`[a-z]` still folds to `[A-Z]`; only
U+212A/U+017F are lost"*). Stated in the row's header rather than substituted
quietly.

### 3.9 THE EMITTED FOLD TABLE IS 2.1x THE DESIGN'S ESTIMATE, and still fine

§4.6 sizes the artifact-side map at *"~12 KB of table text"* for *"the ~1,500
simple-fold pairs"*. The pair count is right (1,484) and the text is
**25,675 bytes** — the estimate assumed a tighter spelling than
`{0x41,0x61}, ` costs. Against D84's caps that is 2.6% of the 1,000,000 total
and NONE of the 500,000 code cap (a table initializer is excluded by
definition), so the conclusion is unchanged. A whole caseless-backref artifact
under `-e utf8` measures 55,053 bytes.

### 3.10 A CYCLIC NEXT-MEMBER TABLE LETS ONE WALKER SERVE BOTH FOLDS

Worth recording because the obvious representation is a partner map and it
cannot express a class of three. Representing the relation as a CYCLE means
`pcrec_ascii_fold` — 26 two-member classes — **is already its own cyclic link
table**, so the ASCII data needs no second spelling and there is no new
agreement obligation on the compiler side. It also changes what S-U2's "one
round" sabotage does: from `k` it adds U+212A and LOSES `K`, which is a
different wrong answer from the partner-map one the design imagined and is red
on the same cells.

### 3.11 THE SEAM'S STRUCTURAL CHECK KEYS ON ENTRY NAMES, and an entry that grows a helper grows the region without it

**Found by the check going red, and it is the most interesting red in the
delivery.** `run_encoding_checks.sh`'s DD12a(i) is DD-12(7)(a)'s instrument:
it excises the NAMED encoding-owned regions from a byte artifact and a utf8
one and requires what is left to be identical, so that an encoding conditional
reaching the hot path is a loud failure. The named regions are found by a
CLOSED LIST OF ENTRY SIGNATURES (`next_pos`, `back_step`, `bref_match`,
`bref_match_caseless`).

The stage-4 caseless compare needs a fold TABLE and two private helpers beside
it — a character decode and a binary search — because folding a code point is
not expressible inline. Those are encoding-owned by construction (they exist
only in that backend's text and nowhere else), but they carry none of the four
names, so they landed in the compared text and the check reported
**"6 of 243 strict-identity pairs differ OUTSIDE the named encoding-owned
regions — an encoding conditional reached the hot path"** plus an
undeclared-form list mismatch. Both were the same cause and neither was a real
encoding conditional.

**The check was right to fire and its region definition was what needed
widening**, so the fix is on both sides and each half is small: `SIG_RE` gains
the three helper names and folds them into `bref_match_caseless`'s own counter
(a counter of their own would be a vacuity row the `byte` backend can never
satisfy, which the check's own guard would then fail), and the emitted table's
opening brace moved to its own line so ONE brace-matching walk serves a
function body and an array initializer alike. **11 / 0 after**, with the
gate-refinement and undeclared-form manifests matching exactly and unmoved.

The generalisable form, and it is this directory's own lesson one level up: a
region identified by the NAME OF ITS ENTRY POINT stops covering that region the
moment the entry needs a helper. The next backend whose residual body needs
more than one function will meet it again.

### 3.12 A PROCESS NEAR-MISS, recorded because it is the mandate

At 17:16 I ran `cd <worktree> && (heavy run) & git add -A && git commit …`.
The `&` backgrounds only the first half, so **`git add -A` and `git commit` ran
in the MAIN tree**, not the worktree. The main tree was clean, so nothing was
staged and the commit was refused (`nothing to commit, working tree clean`);
verified immediately afterwards — main is at `b45225c0`, untouched, status
clean. Every later git call in this lane uses `git -C`. This is the same
`cd`-in-a-compound-command hazard CLAUDE.md records for the pcrec-bench inbox,
in its other orientation: there the `cd` persisted into the tail, here it did
not persist far enough.

---

## 4. Design-text hunks OWED to the manager (D80, stage 1's precedent)

The lane did not edit `docs/design/utf8_design.md`. These are what the delivery
contradicts or completes:

1. **§4.2/§4.3 need the per-contribution rule** (§3.1 above). As written they
   say the fold applies to "the set", which is measurably wrong for a class
   holding a produced set. This is the largest hunk and the one a future
   reader most needs.
2. **§4.6's sampled differential** is superseded by a relation sweep, and its
   ~12 KB size estimate reads 25,675 bytes (§3.6, §3.9).
3. **§4.6 has no ASCII-restriction tie**, which the second fold object makes
   necessary (§3.3).
4. **§8.2 row S-U11's `SAB_REACH_POP`** cannot be satisfied as specified
   (§3.7); §8.2 row S-U3's sabotage is not expressible as a hunk (§3.8).
5. **§9.2's stage-4 acceptance names `tests/utf8/fold.rxt`** and the file now
   exists; its stage-1 entry places S-U11 at stage 1, where it was not built —
   worth a line saying it landed at stage 4 and why that cost three stages of
   unwatched premise.
6. **§4.1's 0-of-11 result now has a standing instrument**, which §4.1.1 asked
   for and can be marked discharged.

---

## 5. What a reviewer should attack first

- **The per-contribution split in `p_class`** (§3.1). It is the only change in
  this delivery that moves the parser's structure rather than adding to it, and
  its byte-identity argument rests on the claim that every producer already
  folded its own contribution. The gate says 0/3,120 on four axes; the argument
  is written at the `prod` declaration.
- **`ucd_partners`' cycle walk** — the `guard` bound is belt to the generator's
  braces, and a cycle that did not close would otherwise be an infinite loop
  inside a library.
- **The utf8 residual's decoder.** It is a SECOND UTF-8 decoder in the artifact,
  which `back_step`'s own comment argues against — but a fold needs code points
  and there is no way around that. Its ill-formed set is deliberately the
  automaton's (overlong, surrogate, out-of-range all rejected) so a subject this
  compare rejects is one nothing else in the artifact would have matched.

---

## 6. OWED TO THE 10.46 REFERENCE (the executor channel)

Every oracle number in this delivery was read from the Mac's Homebrew libpcre2
**10.48**, not the reference 10.46, and — per U15 — the dlopen-based checks
(PC-4, hence S-U11) resolve the macOS SYSTEM **10.42**. The behaviours involved
are structural rather than version-sensitive, and stage 4's gate note records
10.46 agreeing exactly with the pinned Unicode 16.0.0 on the uprops arm. Still
owed, as exact commands:

```sh
cd <pcrec checkout at the merge commit>
make -j CC=gcc                                   # or the box's usual
bash tests/harness/run.sh tests/utf8/            # expect 1668 passed / 0 failed
bash tests/harness/run.sh tests/utf8/fold.rxt    # expect 45 passed / 0 failed
bash tests/backrefs/run_backref_diff.sh          # expect "checks failed: 0";
                                                 # §9b must print
                                                 #   2938 folding code points / 5972 ordered pairs
                                                 #   63486 adjacent-pair controls
                                                 #   52 ASCII bytes tied
bash tests/registry/run_pc4.sh                   # expect
                                                 #   pc4: 1:n fold — 22 assertions (11 cells x 2 option words), 0 matching
                                                 # and PASS: pc4 semantic differential
```

**The one that genuinely needs 10.46 is the last.** `check_1n_fold`'s subject
IS the oracle, so its answer on 10.42 certifies 10.42. A 0-matching result on
10.46 is what discharges §4.1's premise against the version the project pins.

Also owed and NOT run here: `make test`, `make strict`, `make san`, `make mech`
(the four sabotage rows validated SOLO, not through the matrix) — the manager's
at merge.

---

## 7. Rulings received

None. No `utf8s4_rulings.md` was written during the lane's working period, and
the lane asked for none: every scope decision the brief delegated (the
simple-vs-full subset, the interval-payload interaction, the encoding clamp,
whether the ASCII fast path stays literal) was answerable from measurement.

The brief asked whether the population demands a D27-blinded corpus round for
this stage. **It does not.** The blinded round already happened — axis06/axis07
were written blind at stage 2 and carried their oracle to this stage, which is
where §3.4's finding came from. What the population was missing was not
blindness but SHAPE: single characters only. A second blinded author working
from the same design section would most likely write the same axis again;
`fold.rxt` is what was actually missing, and it is written from the design's own
§4.2(c)/§4.3/§4.5 cells plus the per-contribution finding, oracle-first.

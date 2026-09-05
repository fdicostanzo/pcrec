# [M5.0] UTF-8 — design

**STATUS: PROPOSED. Nothing in this document is built.** No file under `src/`
or `tests/` is touched by the lane that wrote it. A D6 adversarial panel
reviews it before any [M5.0] implementation wave opens, and §12 is this
document's own list of where to attack, written before the panel rather than
after.

The charter is `docs/dev/plan.md`'s `[M5.0]` row, its `CROSS-NOTE`, and the
`[DD-12]` and `[DD-1]` rows it names. The architecture being instantiated is
`APPROACH.md` §4 and §10.3; the seam being consumed is `[M5-SEAM]`/D58, which
already shipped.

---

## PANEL OUTCOME — r54, and READ THIS BEFORE ANY SECTION

`docs/dev/reviews/2026-09-04-r54-utf8-design.md`. Three read-only critics
(engine semantics against the shipped tree, checks/validation, measurement
verification): **5 BLOCKING, 10 MUST-FIX, 8 SHOULD, 6 NOTE.** Verdict: the
design revises before it merges (the R33 lookaround precedent). This block is
the revision's map; every row names where the change landed.

**THE THREE THINGS A READER OF THE FIRST VERSION MUST NOT TRUST THEIR MEMORY
OF**, because the revision moved them rather than annotating them:

1. **§2.1's pipeline diagram was wrong about where the lowering runs, and the
   position it implied silently miscompiles every VM artifact.** `compile.c`
   hands the VM emitter the **AST ROOT**, not the IR, and `emit_vm.c` reads
   the class payload directly at four sites. §2.1 is rewritten against
   `compile.c`'s real pass chain with a pass-order diagram, and the position
   is **forced** rather than chosen — §2.1.2 derives it from three ordering
   constraints that admit exactly one slot. Everything §2.3, §2.5, §5.6 and
   §6.2 concluded is re-derived under it.
2. **§2.4's "there is no blowup" was measured in the wrong unit, and the
   design's own quantified table contained the refuting row.** The binding cap
   for an emitted DFA is `PREMUL_MAX_ENTRIES` (65,535 **entries** =
   states × ncls), and the lowering's characteristic effect is on **ncls**,
   not on states. `\p{L}{1,3}` reads 847 states — 2.6% of the 32,000-state cap
   — and **80,465 entries, 123% of the entries cap**. §2.4 is re-stated in
   every binding cap's own units with the arithmetic shown per row.
3. **§5's headline "the seam needs no interface change" is RETRACTED.** It is
   true of the ENTRIES TABLE, which is what the third-encoding recipe is
   about, and false of `PcrecEnc` itself, which must carry a per-encoding
   maximum code point or every negated class refuses under `--encoding=byte`.
   §2.7 and §5.0 carry the corrected claim; ASK 7 routes the D58 record.

### Disposition table

| # | finding | disposition | where |
|---|---|---|---|
| **E1** | the lowering never reaches the VM emitter | **ACCEPTED**, repaired as an AST→AST rewrite at a **forced** position | §2.1, §2.1.2, §2.1.3, §6.2 |
| **E2** | negation universe refuses every negated class under `byte` | **ACCEPTED**; per-encoding complement universe chosen over symbolic negation, with the argument | §2.7.1, §2.7.2, ASK 7 |
| **C1** | stage 1's identity gate stands alone | **ACCEPTED**; paired with three structural checks | §8.1.1 |
| **C2** | the §8.1 positive control is unfloored (K35) | **ACCEPTED**; floors stated on lookaround §9.2's model | §8.1.2 |
| **C3** | no sabotage row declares `SAB_REACH` | **ACCEPTED**; all eight rows gain reach declarations at birth | §8.2 |
| **M1/meas-1** | `_BUNDLED_SHA` computed, never printed | **FIXED AND RE-RUN**; all eight transcripts re-archived | `probes/u8_oracle.py`, `out/` |
| **E3** | §5.6 unimplementable in three ways | **ACCEPTED**; the maxw chain RETIRES, the fixpoints and both timings are specified | §5.6.3, §5.6.4, §5.6.5 |
| **E4** | §2.6 collides with the negative lookbehind end-check | **ACCEPTED**; `back_step` validates declared length | §5.2, §5.2.1 |
| **E5** | the consumer census is incomplete by six files | **ACCEPTED**; full grep-derived census, per-site verdict | §2.5.1 |
| **E6** | §2.4 sizes in the wrong unit | **ACCEPTED**, and it **changes a conclusion** | §2.4.1, §2.4.2 |
| **C4** | S-U8 orphaned | **ACCEPTED**; assigned to stage 2 | §8.2, §9.2 |
| **C5** | S-U7 needs a subject-level witness | **ACCEPTED** | §8.2, §8.3 |
| **C6** | §8.3 compares mismatched units | **ACCEPTED**; blocks vs cases separated | §8.3 |
| **C7** | five population rows show no arithmetic | **ACCEPTED**; derivation per row | §8.3 |
| **C8** | the UCP-SPLIT row names no oracle | **ACCEPTED**; python-**bytes** named and defended | §7.1.1 |
| meas-2 | `sizing.txt`'s blank RUN DATE | **FIXED**; cause found (a `date -Is` that fails on BSD), re-run | `out/sizing.txt` |
| meas-3 | `archive.sh`'s dead fallback | **FIXED**; the test was on exit status, the fact is emptiness | `probes/archive.sh` |
| E7 | suffix sharing vs the A_CAT/A_ALT vocabulary | **ACCEPTED**; near-linearity re-priced, Frag-direct declined | §2.3.1 |
| E8 | the VM's cost/capacity axes unpriced | **ACCEPTED**; §6.4 is new | §6.4 |
| E9 | the caseless fold table in emitted text | **ACCEPTED**; artifact vs compiler separated, the agreement check redesigned | §4.6 |
| E10 | §2.2's re-layout re-derives the D70 survey | **ACCEPTED** | §2.2.3 |
| E11 | self-synchronization is the prefilter premise | **ACCEPTED** | §6.3 |
| C9 | curate the D27 extract with an exclusion list | **ACCEPTED** | §8.3.1 |
| C10 | justify the absence of a pcrec-vs-pcrec differential | **ACCEPTED**, and one is **designed** rather than declined | §8.5 |
| meas-4 | a "5,460 mismatches" anecdote under a MEASURED banner | **FOLDED**; re-marked | §2.4 |
| meas-5 | dead ternary in `probe_uprops.py` | **FIXED** | `probes/probe_uprops.py` |
| E12 | write down P-4's second leg | **ACCEPTED** | §5.4.1, P-4 |
| E13 | `pcrec_cls_word_esc` survives as bytes | **ACCEPTED WITH A REFINEMENT** — both readings are right about different consumers, and that is itself the hazard | §2.2.2 |
| E14 | mid-character "no path" inverts for negative assertions | **ACCEPTED**; per-entry promise stated | §2.6.1 |
| E15 | P-1's file list omits `src/parse/` | **ACCEPTED, and P-1 is REFUTED** — by this revision's own findings, which is the prediction working | §12 P-1 |
| C11 | stage 2's corpus bar depends on ASK 1 | **ACCEPTED**; precondition named | §9.2 |

**Nothing was refuted outright.** One finding is accepted with a correction to
its reasoning (E13, §2.2.2), and one prediction of the design's own is refuted
by the revision rather than by the panel (P-1). §16 is the full what-changed
record.

**What SURVIVED adversarial reading**, verified independently and unchanged
here: §5.6's refutation of the `[M5.0]` cross-note (confirmed at
`mod_lookaround.c:298`/`mrl.c:282-284` by the engine lens on its own), §2.6's
`MATCH_INVALID_UTF`-for-free semantics, `\p`-without-`PCRE2_UTF`,
simple-fold-only at 10.46, the 283-state `\p{L}` machine, and the
refuted-then-vindicated backref cell. All five headline numbers reproduced
number-for-number by the measurement lens.

---

## 0. How to read this

### 0.1 Claim marking

Every claim below carries one of four marks, and the mark is load-bearing —
a panel's first job is to attack the ones that are not `MEASURED`.

| mark | means |
|---|---|
| **MEASURED** | a probe ran and its verbatim output is archived under `utf8_measurements/out/`. The cell names the file. |
| **STRUCTURAL** | true by the shape of code quoted in this document, verifiable by reading `src/` — not a measurement, but not a judgement either. |
| **ARGUED** | a derivation from measured facts. The premises are marked; the step is mine. |
| **ASSERTED** | a design choice or an unverified belief. If it is load-bearing it is also in §12. |

**Every MEASURED-against-libpcre2 claim in this document was measured against
libpcre2 10.46 on the OLD BOX**, which is the project's reference oracle. It
was NOT measured against this Mac's library. §0.4 explains why that mattered
more than it usually does.

### 0.2 The design in one paragraph

The parser stops producing a 256-bit byte bitmap and starts producing a
**sorted list of code-point intervals**; the encoding becomes a **lowering
instance** that turns that list into byte-level NFA fragments, and the byte
backend's instance is the identity map it already is. Everything downstream —
subset construction, minimisation, both emitters, every prefilter — stays
byte-wise and never learns that UTF-8 exists. `\p{...}` is a producer of
intervals and is therefore **not gated on the encoding at all**; case folding
is a **closure over the interval set** applied in the one constructor that
already applies it (D23), before negation, exactly as today. The seam gains no
new interface: its four residual entries get UTF-8 bodies under their existing
signatures, and the one place the design has to change something outside the
backend is an **analysis**, not a mechanism — the lookbehind width rule is
measured to be in CHARACTERS where pcrec computes BYTES, and under the byte
encoding nothing can tell those apart.

### 0.3 Measurements this lane produced

**Seven probes, eight transcripts** — the divergence probe is archived twice,
once against each of the two pythons this project's machines carry, because
§7.2 needed that comparison rather than an assumption. Each transcript
carries a provenance header naming the oracle host, the libpcre2, the python
and (per row) the options word that produced it.

| file | what it settles | oracle |
|---|---|---|
| `out/premises.txt` | what pcrec refuses today; the code this design argues against, quoted | pcrec on HEAD |
| `out/invalid_utf.txt` | charter (i)'s invalid-UTF decision, three modes | libpcre2 10.46 |
| `out/uprops.txt` | charter (ii): which `\p` spellings 10.46 accepts; the UTF-gating question; the interval census | libpcre2 10.46 |
| `out/caseless.txt` | charter (iii): simple vs full folding, the closure, fold-before-negate | libpcre2 10.46 |
| `out/width.txt` | charter (iv): the lookbehind width UNIT, and the seam's other entries | libpcre2 10.46 |
| `out/sizing.txt` | charter (v): byte-automaton state counts against pcrec's caps | pure construction |
| `out/divergence.txt` | charter (vi): the D27 goal-facts list, 28 rows four ways | libpcre2 10.46 + python |
| `out/divergence_local_py311.txt` | the same 28 rows on the OTHER python this project uses | libpcre2 + python 3.11 |

### 0.4 THE ORACLE PROBLEM THIS LANE HAD, and why it is worth a section

Every earlier design gate in this house ran its probes on the machine that had
the reference libpcre2. This one could not: **the reference is 10.46 and it is
on the old box**, while the lane runs on a Mac whose library is a different
version. PC-3 measured the two diverging on the same day this lane opened.

So every oracle probe here executes REMOTELY, and the mechanism is worth
stating because a panel should attack it before it attacks any number that
came through it:

- `probes/bundle.py` embeds the borrowed oracle chain — `pcre2_ctypes.py` →
  `br_oracle.py` → this lane's `u8_oracle.py` — **verbatim**, as the `repr()`
  of each file's source, and shims `importlib` so the same import chain runs
  on the far end against the same bytes. **The binding is borrowed, not
  copied**, which is the rule `br_oracle.py`'s own header states and
  `la_oracle.py` repeats: *a lane that re-implements the binding it is
  checking cannot detect that the original moved*. Edit `pcre2_ctypes.py`
  tomorrow and the next bundle carries the edit.
- The payload arrives on **stdin**. Nothing is written on the old box — no
  temp file, no checkout — which is also what keeps the scope mandate clean
  on a machine this lane does not own.
- `probes/archive.sh` is the ONLY writer of `out/` (R30 M7's rule) and its
  header names the **oracle host** as well as the usual commit/version block,
  because for this lane an archived number is meaningless without it.

**Three instrument defects came out of this, and each is recorded at its own
site rather than only here** (the full list is `out/CLAUDE.md`):

1. **A transcript that printed a pattern nobody ran.** `probe_caseless.py`
   rendered its patterns with `.decode("latin-1")`, so the two UTF-8 bytes of
   U+00DF appeared as `Ã` plus a control. A reader cannot be expected to
   notice that the *pattern* column is lying. Cured by `u8_oracle.pshow()`, a
   function rather than a habit.
2. **A vacuity guard whose pass condition could not be met.**
   `probe_invalid.py`'s F3 asked `not isinstance(utf_result, tuple)` to mean
   "UTF did not answer" — but an error row IS a tuple, so the guard was
   unsatisfiable and reported `0 of 9` against a column that plainly differs.
   It announced itself only because it was written in the failing direction.
3. **`-o /dev/null`, reproduced verbatim.** pcrec writes `OUT.c` *and*
   `OUT.h`, so a `/dev/null` sink tries to create `/dev/null.h` and every
   COMPILING cell reads "Operation not permitted" — i.e. as a refusal.
   `docs/design/subroutines_measurements/CLAUDE.md` had already recorded this
   exact defect; this lane hit it anyway, on its first run, which is the R30
   M6 shape (*a defect reproduced verbatim by someone who had read the entry
   naming it*).

And one finding about the LOCAL side, which matters for anyone re-running
these probes here: `ctypes.util.find_library("pcre2-8")` on this Mac resolves
to **miniconda's** libpcre2, version **10.37** — not Homebrew's 10.48 and not
the reference 10.46. A "local comparison" run silently measures a *third*
version. The archiver prints `libpcre2:` from the library that actually
answered, which is what caught it.

---

## 1. Premises, re-verified on HEAD rather than inherited

`out/premises.txt`. This section exists because a design built on what a plan
row *says* the code does is a design built on a document, and the documents in
this tree have been wrong before. Two of the three claims below were wrong.

### 1.1 What ships today

**MEASURED** (`out/premises.txt` §1, §2, §6):

- `-e utf8` is refused **by the registry row's own name**:
  `encoding 'utf8' arrives with milestone M5 (an engine axis, not a module: no
  --features name enables it)`. `-e utf16` and `-e UTF8` are refused as
  unknown, with the menu rendered from the table. The seam's third-encoding
  recipe is real and this lane is its first test.
- `\x{...}`, `\p`, `\P`, `\N{U+...}` all refuse with **`requires module
  'unicode-props'`** — including inside a class, and including under `(?i)`.
  `\X` and `\R` refuse with `requires module 'misc'`, a **different module**,
  which §9 takes as a scope boundary rather than a detail.
- `\x41` (bare two-digit hex) **compiles**: only the braced form is gated.
- The registry's `\p`/`\P` rows read `built = unbuilt` (D65's derived column),
  `engines = dfa|vm`, `module = unicode-props`.
- The seam ships four residual entries (`next_pos`, `bref_match`,
  `bref_match_caseless`, `back_step`) behind a per-artifact mask.

### 1.2 THREE CLAIMS IN THIS LANE'S OWN CHARTER, CHECKED

**(a) `[DD-12]` assigns the CharSet widening to MOD-0.6. That is STALE, and
this milestone owns it.** The row says *"the CharSet widening is MOD-0.6's
(D33 §7)"*. D33 §7 itself carries an amendment dated the same session MOD-0.6
ran:

> **AMENDED 2026-08-12 (Frank, thirteenth session).** Widening DEFERS to the
> first milestone that PRODUCES a wide set (M5-era `\p` matching). MOD-0.6 as
> scoped in plan.md is recogniser-only — no producer lands, so a widened
> structure built there would itself be the unexercised structure this section
> warns about. Ownership split: MOD-0.6 owns the `\p`/`\P`/`\N{U+` REFUSAL
> surface; **the first wide producer owns the structure.**

**STRUCTURAL**, confirmed in the tree: `src/core/internal.h`'s `A_CLASS`
payload is still `struct { uint8_t bits[32]; } cls;` and `src/ir/nfa.c`'s
`A_CLASS` arm is still a `memcpy` of 32 bytes into one `N_CLASS` state. **This
milestone is the first wide producer, so §2.2 is this design's work and not an
inherited dependency.** The `[DD-12]` row should be corrected at merge.

**(b) The `[M5.0]` CROSS-NOTE's prescription for `pcrec_maxw` is REFUTED.**
The row says the `A_CLASS` arm *"must become the encoding's maximum code-unit
length"*. §5.6 shows, from a measurement, that doing exactly that would refuse
**every** lookbehind under UTF-8 including `(?<=a)`. The cross-note is right
that the arm is a hazard and right that the byte refusal is what makes it
exact today; its cure is wrong. This is the sharpest single finding in the
document.

**(c) `[DD-12] (3)`'s characterisation of `PCRE2_MATCH_INVALID_UTF` is
REFUTED as worded.** The row says that mode *"is essentially the byte-wise
semantics"*. §2.6 measures it and it is not — it is essentially the byte-wise
**UTF-8 automaton's** semantics, which is a different thing and happens to be
the one pcrec wants. The row's conclusion (*measure against THAT mode and pick
deliberately*) survives; its reason does not.

### 1.3 THE CONSTRUCT TABLE

D26's obligation: for every construct in this milestone's neighbourhood,
whether it SHIPS, whether it REFUSES, and **which module owns it** — the tier
that is exact. `refuses today` is **MEASURED** (`out/premises.txt` §2);
`10.46` is **MEASURED** (`out/uprops.txt` §1, `out/width.txt` §1); the landing
column is this design's **ASSERTED** staging (§9.2).

| construct | 10.46 | owner | refuses today as | lands |
|---|---|---|---|---|
| `--encoding=utf8` | n/a (an option there) | **encoding**, not a module | `encoding 'utf8' arrives with milestone M5 (an engine axis, not a module)` | **stage 2** |
| `\x{HH...}` ≤ 0xFF | compiles at any options | base grammar | `\x{...} requires module 'unicode-props'` | **stage 1** |
| `\x{HH...}` > 0xFF | UTF only (err 134 otherwise) | base grammar, encoding-sensitive | same | **stage 2** (refuses under `byte`, as 10.46 does) |
| `\xHH` (bare, 2 digits) | compiles | base grammar | **already ships** | — |
| `\p{X}` / `\P{X}`, general categories | compiles at ANY options (§3.2) | `unicode-props` | `\p requires module 'unicode-props'` | **stage 3** |
| `\p{X}`, `Xan Xps Xsp Xuc Xwd L& Any Assigned` | compiles | `unicode-props` | same | **stage 3** (derived, no new data) |
| `\p{Greek}`, `\p{Script=…}`, `\p{sc=…}` | compiles | `unicode-props` | same | **stage 5** |
| `\p{scx=…}`, `\p{Script_Extensions=…}` | compiles | `unicode-props` | same | **stage 5** |
| `\p{Alphabetic}` and the boolean family | compiles | `unicode-props` | same | **REFUSES** at first landing (§3.4) |
| `\p{bc=…}`, `\p{Bidi_Class=…}` | compiles | `unicode-props` | same | **REFUSES** at first landing |
| `\p{InGreek}`, `\p{blk=…}` — **blocks** | **err 147** | `unicode-props` | same | **REFUSES PERMANENTLY** — reproducing 10.46's own refusal |
| `\p{^L}` (caret inside braces) | compiles | `unicode-props` | same | **stage 3**, with its family |
| `\N{U+HHHH}` | compiles under UTF | `unicode-props` | `\N requires module 'unicode-props'` | **stage 2** (it is `\x{}` by another spelling) |
| `(?i)` over non-ASCII | simple fold only (§4.1) | the one class constructor — **not a module** | n/a (the fold ships; its non-ASCII half does not exist yet) | **stage 4** |
| `\w \d \s \b` under UCP semantics | needs `PCRE2_UCP` | — | pcrec has **no UCP axis** (§4.5) | **NOT IN M5** — §14 ASK 4 |
| `\X` (grapheme cluster) | compiles under UTF | **`misc`** — a different module | `\X requires module 'misc'` | **out of scope** (§11) |
| `\R` | compiles | **`misc`** | `\R requires module 'misc'` | **out of scope** |
| UTF-16 / UTF-32 | PCRE2 has separate libraries | — | `unknown encoding 'utf16' (want byte, utf8)` | **never** — `[DD-12] (6)`, D18 earn-its-axis |

Two rows are worth reading twice. **`\p` is owned by a module and gated on
nothing else** — §3.2 measures that it works without `PCRE2_UTF`, which is
what lets stage 3 be independent of stage 2. And **`\X`/`\R` belong to
`misc`**, measured, not to `unicode-props` — so the natural-looking
"everything Unicode" scope is not the module boundary this tree actually has.

---

## 2. THE LOWERING (charter (i))

### 2.1 Where code points live, and where they stop

> **REWRITTEN AT r54 (BLOCKING E1).** The first version drew this pipeline
> from `APPROACH.md`'s architecture rather than from `src/core/compile.c`, and
> the two are not the same shape. **The IR is not the only thing downstream of
> the parser: `compile.c:1228` reads
> `if (cx.job->fit.chosen == ENGM_VM) pcrec_emit_vm(&cx, root);` — the VM
> emitter is handed the AST ROOT.** A lowering placed "between the parser and
> the IR" is therefore not between the parser and the VM emitter at all, and
> `emit_vm.c` reads the class payload directly at four sites (`:1515`
> `out[0] = a->u.cls.bits`, `:3287` `cls_has(a->u.cls.bits, c)`, `:4608` and
> `:7055` `vm_cls(v, a->u.cls.bits)` interning a 256-entry table). Under the
> position the old diagram implied, **every VM artifact — every
> capture-bearing pattern, and modules `backrefs`, `lookaround`,
> `atomic-groups`, `recursion` — would compile a code-point interval list
> through a path that can only express bytes.** `vm_cls` interns whatever the
> first 32 bytes of the widened payload happen to be, so the failure is a
> **silent miscompile, not a refusal**, which is the one outcome
> `CLAUDE.md`'s module rule forbids by name. All four citations were
> re-verified against this tree before this rewrite; so was the pass chain
> below, line by line.

#### 2.1.1 The pass chain as it actually is

Every line number is `src/core/compile.c` at this tree, read rather than
recalled. **STRUCTURAL.**

```
 :901   root = pcrec_parse(&cx);                    AST, CODE-POINT intervals
 :924   root = pcrec_rxt_compose(&cx, root);        injects definition subtrees
 :926   root = pcrec_altcls(&cx, root);             reads u.cls.bits ×4
 :942   root = pcrec_discharge_atomic(&cx, root);   no class payload
 :961   pcrec_callgraph_build(&cx, root);           binds u.call.body — MUST
                                                    run after the last pass
                                                    that REBUILDS a node
 :988   pcrec_select_engine(&cx, root);             → possessify (:456) reads
                                                      u.cls.bits ×2
                                                    → revdet   (:477) reads
                                                      u.cls.bits ×1
 :999   pcrec_postresolve(&cx, root);               the lookbehind WIDTH rule,
                                                    2nd timing — needs
                                                    CHARACTERS (§5.6)
────────────────────────────────────────────────────────────────────────────
 ????   ◄══════ THE ENCODING LOWERING GOES HERE ══════►
────────────────────────────────────────────────────────────────────────────
 :1018  pcrec_build_nfa(&cx, root, ...);            reads u.cls.bits ×2
        (:1128/:1134 forward+reverse, :1135/:1138 subset, :1141/:1142 minimise)
 :1228  if (chosen == ENGM_VM) pcrec_emit_vm(&cx, root);   ← THE AST, NOT THE IR
 :1229  else                   pcrec_emit_dfa(&cx);        ← reads the machines
```

#### 2.1.2 The position is FORCED, not chosen

Three ordering constraints, each read off the tree, and together they admit
exactly one slot. This is the section to attack: if one constraint is wrong,
the position moves.

1. **The lowering must run before `pcrec_build_nfa` (:1018) and before
   `pcrec_emit_vm` (:1228)**, which is E1 itself. Those are the two consumers
   that can only express bytes.
2. **`pcrec_callgraph_build` (:961) must run AFTER the lowering — so the
   lowering cannot run before :961.** `compile.c:947-955` states the rule and
   its reason: `.body` is a cache of *"which subtree is that group's, IN THE
   TREE THE EMITTER WILL WALK"*, and a `.body` captured before a pass that
   REBUILDS nodes names a subtree that is no longer there — *"two programs for
   one group"*. **The lowering is exactly such a pass**: it replaces an
   `A_CLASS` with an `A_CAT`/`A_ALT` of byte-range classes. So it is bound by
   the same rule `altcls` and `discharge_atomic` are bound by. This is the
   constraint that kills the otherwise-attractive "lower immediately after the
   parser" position.
3. **`pcrec_postresolve` (:999) must run BEFORE the lowering.** It asks the
   lookbehind fixed-width rule in **CHARACTERS** (§5.6), and after the
   lowering a two-byte character is an `A_CAT` of two byte classes, so a
   character-width walk over a lowered tree would answer 2 where the truth is
   1. It cannot run earlier than :961 either, because its whole reason for
   existing is that a call's width cannot be answered until the graph binds
   the callee.

Constraints 2 and 3 put the lowering after :999; constraint 1 puts it before
:1018. **There is exactly one line between them.**

```
 :999   pcrec_postresolve(&cx, root);
 :1000  root = pcrec_lower_enc(&cx, root);   ◄── the encoding lowering
 :1018  pcrec_build_nfa(&cx, root, ...);
```

**And the assignment is to `root`, not to a local.** `compile.c:942`'s own
comment records the bug that makes this worth writing down: `discharge_atomic`
"now PUBLISHES the rewritten root — inside `select_engine` the assignment was
to a local, so a discharge at the very root was discarded." A lowering that
did the same would leave `emit_vm` walking the un-lowered tree, which is E1
again by a different route.

#### 2.1.3 What the position costs, stated rather than hidden

The position is forced, and it is **not** the convenient one. Three passes run
BEFORE it and therefore see code-point intervals rather than bytes:
`pcrec_altcls` (:926), and `possessify`/`revdet` through `pcrec_select_engine`
(:988). §2.5.1 gives each site its own verdict. That is the honest cost of
constraint 2, and the first version of this document avoided it only by
placing the lowering somewhere that miscompiles.

**A second-lowering-in-the-VM-emitter is not an option and is named here so
nobody proposes it later.** Two lowerings for one rule is the parallel
mechanism `CLAUDE.md`'s situation index forbids, and it would put the DFA path
and the VM path on two independently-maintained decompositions of the same
character set — a divergence no answer check could localise, because both
would be *plausible* UTF-8.

#### 2.1.4 Making E1's failure mode inexpressible

The repair above puts the lowering in the right place. This makes it
**impossible to have put it in the wrong one**, which is the stronger form and
costs one function.

After the lowering every `A_CLASS` still carries an interval list (§2.2 keeps
one representation), but every interval is confined to `0..0xFF`. Consumers
that need the 32-byte bitmap — `nfa.c:542`, `emit_vm.c:1515/:3287/:4608/:7055`
— do not read `u.cls.bits`; they call

```c
/* Render a BYTE-CONFINED class node into the 32-byte bitmap every byte-tier
 * consumer wants. The assertion is the point: an interval above 0xFF here
 * means the encoding lowering did not run on this subtree, and the caller is
 * about to intern the first 32 bytes of a code-point interval list as if it
 * were a bitmap. That is r54 E1's silent miscompile, and this turns it into a
 * compiler assertion at the site that would have committed it. */
void pcrec_cls_bits(const Ctx *cx, const Ast *a, uint8_t out[32]);
```

**This is what turns E1 from a bug that shipped once into a bug that cannot
ship.** The failure the panel found is invisible to every answer check —
`vm_cls` interns *something* and the artifact compiles and matches *something*
— so an assertion at the read site is the only instrument that sees it. §8.1.1
makes it a structural check as well, because an assertion in a build nobody
runs with assertions on is a comment.

### 2.2 The class structure widens HERE

The `Ast` `A_CLASS` payload becomes an interval list. **ASSERTED** shape,
offered for the panel to improve:

```c
/* A_CLASS: a set of CODE POINTS as sorted, disjoint, non-adjacent
 * intervals. The invariant is what makes every consumer simple:
 * lo[i] <= hi[i] < lo[i+1] - 1. */
struct {
    PcrecCpRange *iv;    /* arena-allocated */
    int           n;
} cls;
```

Three notes, each of which is a decision rather than a detail:

- **Why intervals and not a bitset.** A bitset over 0x110000 code points is
  136 KB per class node. The measured interval counts (§3.3) are 44 to 770.
- **Why not keep the 32-byte bitmap for sub-0x100 sets.** Two
  representations means two code paths in every consumer and a predicate
  deciding which — the special-case shape this project has a standing rule
  against. The byte backend's lowering reads intervals and emits a bitmap;
  the bitmap survives where it belongs, in the IR.
- **What this deletes** — and the first version overstated it; see §2.2.2.
  `cls_set`/`cls_has` and the `pcrec_cls_*[32]` tables are the byte-tier
  producers' OUTPUT FORMAT, and that format becomes interval literals. It does
  **not** follow that the tables stop existing. §8.1 makes the no-op-ness of
  the conversion a gate rather than a claim.

**The parser is otherwise unchanged**, and that is `[DD-12] (1)`'s point:
there is no encoding parameter in the grammar. The parser changes only where
UTF changes the LANGUAGE (§2.7).

#### 2.2.2 `pcrec_cls_word_esc` survives AS BYTES (r54 E13)

**ACCEPTED, with a correction to the finding's reasoning that makes it a
sharper point than either version had.** The panel says the table must come
off the deletion list because `\b`'s mechanism consumes it. **Both readings
are right, about different consumers**, and that is the finding:

| consumer | what it wants | fate |
|---|---|---|
| `src/parse/registry.c:507`/`:508` — the `\w`/`\W` PRODUCER rows | a set of characters, to build an `A_CLASS` | becomes an **interval literal**; the design's bullet is right here |
| `src/ir/dfa.c:173` — `refine_by(d, ncls, pcrec_cls_word_esc)` | a set of BYTES, to refine the byte alphabet | **survives as bytes**; runs after the lowering, on the byte alphabet |
| `src/gen/emit_vm.c:7247` — `vm_cls(v, pcrec_cls_word_esc)` | a set of BYTES, to intern `\b`'s class | **survives as bytes**, same reason |

**STRUCTURAL**, all three by grep at this tree; `emit_vm.c:7244`'s own comment
names it *"the SAME table `\w` compiles from"*.

**So the set acquires two representations — which is the hazard §2.2's second
bullet exists to forbid.** The resolution is not to pick one: the two
consumers genuinely want different things, and under `--encoding=utf8` they
are no longer even the same set (`\w`'s characters vs the BYTES a `\b` context
partitions on, which §5.4's ASCII ruling makes the ASCII word bytes and
nothing else). The resolution is that **both forms are generated from ONE
source**, which is a mechanism this tree already has: `src/parse/cls_bits.inc`
is a generated file, and `[DD-11]`/D85 already rules it *"a DERIVED
artifact"*. The interval literal and the 32-byte table become two renderings
of one generator's input, and a second hand-maintained spelling of the word
set is what would be forbidden.

#### 2.2.3 The re-layout re-derives the D70 clobber survey (r54 E10)

**ACCEPTED.** `u.cls` shrinks from 32 bytes to 16 (a pointer and an `int`),
so **every offset in the `Ast` union moves**, and `internal.h:487-500` records
what depends on those offsets — the D70 migration survey, whose two findings
were both *unconditional per-kind writes on generic paths*:

- `src/opt/revdet.c`'s `rd_node` cleared `A_REP`'s `revbody`/`possessive` on
  every kind it copies. Through `u.rep` that landed on `u.cls.bits` —
  `possessive` at `+49` is bitmap byte 9, `revbody` at `+56..+63` is bitmap
  bytes 16-23 — and the measured symptom was that a reversed `A_CLASS`'s
  bitmap lost those bytes, so the backward walk's class tests read all-zero
  and `((H)|I){3}J` on `"HHHJ"` came back with **groups UNSET and the
  whole-match span unchanged**. Only a capture-aware check saw it.
  `revdet.c:255-266` now guards on `n->k == A_REP` — **verified present at
  this tree.**
- `src/parse/mod_assertions.c`'s multiline pin, harmless only because five of
  its eight kinds had no payload yet.

**The obligation this milestone inherits is not "keep the guards".** It is
that the survey's QUESTION — *which generic walker writes a per-kind field
without switching on `k`* — must be **re-asked against the new layout in the
same change**, because a 16-byte `u.cls` puts different fields over different
bytes and the second finding above is explicitly *"a clobber waiting for its
payload"*. A guard that is correct today is correct for a reason that is about
`k`, not about offsets, so the guards survive; what does not survive is the
SURVEY's coverage claim, which was taken over a layout that no longer exists.
`internal.h`'s own note that *"the arena zeroes the whole allocation, union
included"* also needs re-reading: a 16-byte `u.cls` read as all-zero is
`{iv = NULL, n = 0}`, the EMPTY class — where a 32-byte all-zero bitmap was
also the empty class, so this one happens to survive, and saying so is
cheaper than leaving a reader to work it out.

### 2.3 CharSet → byte-sequence fragments: the construction

The classic range-to-byte-sequence decomposition, used by RE2 and generated by
Ragel; cited as [Cox07] and [Ragel] in `REFERENCES.md` (entries added in this
change, per the citation rule that file's own header states). In one
paragraph:

Split each code-point interval at the UTF-8 length boundaries (0x7F, 0x7FF,
0xFFFF), and split out the surrogate range U+D800–U+DFFF, which has no UTF-8
encoding. Within one length class, an interval becomes a small set of
**byte-range sequences**: a chain of `N_CLASS` states whose bitmaps are
contiguous byte ranges. `U+0800–U+FFFF` minus surrogates is the canonical
four-row table

```
E0     A0-BF  80-BF
E1-EC  80-BF  80-BF
ED     80-9F  80-BF
EE-EF  80-BF  80-BF
```

and the whole construction is that table generalised.

**THIS IS ALL EXISTING IR VOCABULARY.** A byte-range is a 256-bit bitmap with
a contiguous run set; a sequence is an `A_CAT` of them; a set of sequences is
an `A_ALT`. The lowering emits nodes `src/ir/nfa.c` already knows how to
compile, which is why §6 finds no downstream consequences: **there is nothing
downstream to change.**

#### 2.3.1 The near-linearity claim, re-priced (r54 E7)

**ACCEPTED; the claim as written was incoherent with the vocabulary four
lines above it.** The first version said *"**Suffix sharing** — a trie built
from the END, so alternatives with common trailing byte-range chains share
states — is what keeps a `\p{L}`-sized set near-linear."* **A TREE CANNOT
SHARE SUFFIXES.** `A_CAT`/`A_ALT` is a tree; the measured 2,205 comes from
`probe_sizing.py`'s own hash-consed **DAG**, which the probe discloses in its
conventions block (*"(d) suffix-shared NFA states = a trie built from the END
… hash-consing identical (byte-range, target) pairs"*) and which caveat 1
already flagged as *not pcrec's lowering*. And `src/ir/nfa.c:192`'s trie is a
**PREFIX** trie keyed on bitmaps, factoring lead bytes — the other end of the
string.

Two ways out, and the design takes the second:

- **Emit `Frag`s directly**, bypassing the AST so the lowering can build a DAG
  the way `nfa.c` builds one internally. **DECLINED.** It contradicts §2.1.2:
  a `Frag`-direct lowering has no AST to hand `pcrec_emit_vm` at `:1228`, so
  it re-creates E1 exactly — the DFA path would get the shared machine and the
  VM path would get nothing. The whole reason the lowering is an AST→AST
  rewrite is that the AST is what BOTH backends read.
- **Drop the near-linearity claim and re-price on the tree.** **TAKEN.** The
  lowering emits an `A_ALT` of `A_CAT`s with no sharing, and the sharing is
  recovered where this tree already recovers it: `nfa.c:192`'s prefix trie
  factors the lead bytes on the way into the NFA, and **subset construction
  and Hopcroft minimisation recover the rest** — which is why the numbers that
  matter are the DFA ones and not the NFA ones.

**The re-priced claim, MEASURED** (`out/sizing.txt` summary table): the tree
the lowering emits for `\p{L}` is 786 alternatives, whose **unshared** NFA is
**2,636** states against the DAG's 2,205 — **a ratio of 0.836, so the suffix
sharing the first version credited with near-linearity is worth 16%.** Both
determinise to the same **283**-state DFA and the same 283-state minimal DFA.
The sharing is therefore worth a small constant in the NFA and **nothing at
all** in the artifact, which is what §6.1 and §2.4 size against.
`PCREC_MAX_NFA_STATES` (131,072) is the only cap the unshared count is visible
to, and 2,636 sits at **2.0%** of it.

The same column is worth reading down: on four of the ten rows the "shared"
count is **larger** than the naive one (`[a-z]` 4 vs 2, `\p{Greek}` 120 vs
122 the other way), because the DAG pays a shared start and a shared terminal
that the private-chain form does not. **A construction whose sharing is worth
16% at its best and negative at its worst was never what kept these numbers
small.** What keeps them small is determinisation, which is where the
2,636 → 283 factor of 9.3 actually happens — and that is a pass this design
does not touch.

**What this costs honestly**: the compiler builds a bigger intermediate than
it needed to, on `\p`-bearing patterns only. It is a compile-TIME question,
it has no artifact consequence, and §12 P-3 is the prediction that catches it
if the constant factor is worse than the probe suggests.

Ill-formed input needs no handling because it has no path: an overlong
encoding, a truncated sequence, a surrogate encoding and a byte above 0xF4 are
all simply absent from the automaton. §2.6 turns that into a promise.

### 2.4 The sizing measurement: no blowup IN STATES

> **RE-STATED AT r54 (MUST-FIX E6), and the conclusion moved.** This section
> sized in STATES. **Not one of the caps that actually binds an emitted DFA is
> denominated in states**, and the lowering's characteristic effect is on the
> other factor. §2.4.1 is the same measurement in the binding caps' own units,
> and it contains a row that **does not fit** — a row that was printed in this
> section's own quantified table all along, reading 2.6% of a cap it clears
> and 123% of a cap nobody had asked it about. The state numbers below are
> unchanged and correct; what was wrong was calling them the answer.

**MEASURED** (`out/sizing.txt`), and this is the result that most changes the
shape of the milestone, because the charter asks about "state-count blowup"
and the honest answer is that there is none **in that unit**.

| class | intervals | byte-seq alternatives | NFA (shared) | DFA | min-DFA | lead bytes |
|---|---|---|---|---|---|---|
| `[a-z]` | 1 | 1 | 4 | 2 | 2 | 26 |
| `[\x{80}-\x{7FF}]` | 1 | 1 | 5 | 3 | 3 | 30 |
| `[α-ω]` | 1 | 2 | 7 | 4 | 4 | 2 |
| `[\x{100}-\x{10FFFF}]` | 2 | 8 | 18 | 9 | 9 | 49 |
| `.` (UTF, no DOTALL) | 3 | 10 | 20 | 9 | 9 | 178 |
| `[^a]` (UTF) | 3 | 10 | 20 | 9 | 9 | 178 |
| `\p{L}` | 648 | 786 | 2,205 | 283 | 283 | 97 |
| `\p{Lu}` | 646 | 659 | 1,246 | 74 | 74 | 47 |
| `\w` (UCP, approximated) | 883 | 1,056 | 2,958 | 332 | 332 | 110 |

Against pcrec's caps — `PCREC_MAX_NFA_STATES` 131,072,
`PCREC_MAX_DFA_STATES_GOTO` 10,000, `PCREC_MAX_DFA_STATES_TABLE` 32,000
(`out/premises.txt` §7) — **every row clears every cap by more than an order
of magnitude.** The largest minimised DFA in the table is 332 states.

And quantified, which is the sharper question because a class never appears
alone:

| form | DFA | min-DFA |
|---|---|---|
| `\p{L}` | 283 | 283 |
| `\p{L}*` | 283 | **282** |
| `\p{L}{1,3}` | 952 | 847 |
| `.*` (UTF) | 9 | 9 |

`\p{L}*` is **smaller** than `\p{L}`, which is not a typo and is worth
understanding rather than just recording: the star's back-edge merges the
accept state into the start state, and a DFA over a self-similar byte
structure has almost nothing left to distinguish. **A UTF-8 `.*` does not
blow the DFA cap; it is nine states.**

**The self-check is what makes these numbers usable.** **MEASURED**, and it is
the only claim in this paragraph that is: 10,916 sample points — every interval
endpoint and its neighbours, interior points, out-of-class points, hand-built
surrogate encodings, truncations of every multi-byte sample, and deliberate
overlong re-encodings at every extra length — checked for accept/reject
against the built automaton, **0 mismatches**, reproduced at every re-run
including this revision's.

> **r54 meas-4, folded.** The sentences that followed — *"It was not 0 on the
> first run… found by the self-check at 5,460 mismatches and fixed"* — sat
> under the same **MEASURED** banner as the 0, and they are not the same kind
> of claim. The 5,460 is a **LANE ANECDOTE**: it describes a build of the
> probe that no longer exists and that nothing archived ever captured, so a
> reader cannot check it and a re-run cannot reproduce it. It is kept, because
> the lesson (*a sizing number from a wrong construction is worse than no
> number, and the self-check is what separated the two*) is worth more than
> the number — but it is marked **ASSERTED (lane record)**, and the panel's
> point stands: an unverifiable figure printed in the same voice as a verified
> one borrows the verified one's authority. The current result is independently
> verified; the story of how it got there is not, and now says so.

#### 2.4.1 The same rows in the BINDING caps' own units (r54 E6)

**MEASURED** (`out/sizing.txt`, "CAP-FIT IN THE CAPS' OWN UNITS" — sections
(h)-(k), added to `probe_sizing.py` in this revision). The caps, read off the
tree rather than recalled:

| cap | value | unit | site |
|---|---|---|---|
| `PREMUL_MAX_ENTRIES` | 65,535 | **entries** = min-states × ncls | `emit_dfa.c:2081`, tested `:2522` |
| `PCREC_MAX_SUBSET_ELEMS` | 48,000,000 | **interned state-set elements**, summed over BOTH machines | `dfa.c:934` |
| D84 code / total | 500,000 / 1,000,000 | **emitted C bytes** | `limits.def:157`/`:159` |
| `PCREC_MAX_DFA_STATES_GOTO`/`_TABLE` | 10,000 / 32,000 | states | `limits.def:137`/`:138` |

`ncls` is `src/ir/dfa.c`'s own `eqclasses` partition — two bytes are one class
iff every state sends them to the same target — computed by the probe by the
same rule. **This is the axis the lowering moves.** A UTF-8 decomposition's
transitions are lead-byte and continuation-byte RANGES, so it refines the byte
alphabet in a way an ASCII class never does; sizing in states measured the one
factor the lowering barely touches.

| class | min-states | ncls | entries | vs 65,535 | +`\b` ncls | entries +`\b` | subset elems |
|---|---|---|---|---|---|---|---|
| `[a-z]` | 2 | 2 | 2×2 = 4 | premul | 3 | 6 | 4 |
| `[\x{80}-\x{7FF}]` | 3 | 3 | 3×3 = 9 | premul | 4 | 12 | 5 |
| `[α-ω]` | 4 | 5 | 4×5 = 20 | premul | 6 | 24 | 7 |
| `[\x{100}-\x{10FFFF}]` | 9 | 11 | 9×11 = 99 | premul | 12 | 108 | 18 |
| `.` (UTF, no DOTALL) | 9 | 12 | 9×12 = 108 | premul | 13 | 117 | 20 |
| `[^a]` (UTF) | 9 | 12 | 9×12 = 108 | premul | 14 | 126 | 20 |
| `\p{L}` | 283 | 95 | 283×95 = **26,885** | premul (41.0%) | 96 | 27,168 | 2,533 |
| `\p{Lu}` | 74 | 87 | 74×87 = 6,438 | premul | 88 | 6,512 | 1,655 |
| `\p{Greek}` | 26 | 49 | 26×49 = 1,274 | premul | 50 | 1,300 | 123 |
| `\w` (UCP, approximated) | 332 | 96 | 332×96 = **31,872** | premul (48.6%) | 96 | 31,872 | 3,476 |

and the quantified forms, which is where it bites:

| form | min-states | ncls | entries | vs 65,535 |
|---|---|---|---|---|
| `\p{L}*` | 282 | 95 | 26,790 | premul (40.9%) |
| **`\p{L}{1,3}`** | **847** | **95** | **847×95 = 80,465** | **PLAIN — 122.8%** |
| `.*` (UTF) | 8 | 12 | 96 | premul |
| `.{1,3}` (UTF) | 25 | 12 | 300 | premul |

**THREE THINGS FOLLOW, AND ONLY THE FIRST IS COMFORTABLE.**

**(a) K7's element cap is not in the conversation.** The worst row interns
3,476 elements against 48,000,000 — **0.0072%**, four orders of magnitude of
headroom, and that is the cap `[M4.7b]` added because the subset construction
could exhaust memory. Nothing here goes near it.

**(b) `PREMUL_MAX_ENTRIES` IS THE BINDING CAP AND IT IS ALREADY HALF SPENT BY
ONE CLASS IN ISOLATION.** `\w` under UCP reads **48.6%** of it — where the
state column reads 332 against 32,000, which is 1.0%. The two units disagree
by a factor of 47, and the state column is the one the first version of this
section reported.

**(c) `\p{L}{1,3}` EXCEEDS IT — 80,465 against 65,535 — and this row was
printed in §2.4's own quantified table from the first draft, reading "847"
next to a 32,000-state cap.** The number was never wrong; it was never
converted into the unit that decides anything.

**WHAT EXCEEDING IT COSTS, precisely, because "cap" invites the wrong
reading.** `emit_dfa.c:2522` sits inside `dfa_premul`, which is an
`[ENG-FORM]`/D82 **form-selection predicate**: `return false` removes the
pre-multiplied table from the candidate list. **The machine still compiles**,
in the plain-table form, and what is lost is `[OPT-3]`'s measured 1.27×. It is
a THROUGHPUT consequence, not a refusal and not a miscompile. So the honest
statement is:

> Under UTF-8, a quantified property class can silently drop off `[OPT-3]`'s
> premultiplied form. Nothing breaks; the artifact is slower than a reader of
> §2.4's state table would predict, and no existing check would say so.

**AND IT PROMOTES P-5 FROM A CAUTION TO THE MILESTONE'S LIKELIEST SURPRISE.**
§12 P-5 already said §2.4 measures classes in isolation and not the products a
real pattern builds. With `ncls` at 95-96 for any `\p`-sized class, a product
of two such classes multiplies STATES while `ncls` stays high, so the entries
figure is where a two-class pattern lands first. P-5 is re-stated in entries
and bytes in §12 accordingly, and stage 2's acceptance gains a **stamp
census** (§8.1.1 check 3) rather than trusting this table.

**WHAT THIS MEASUREMENT CANNOT REACH, stated rather than estimated quietly.**
D84's two caps are on EMITTED C BYTES, and `probe_sizing.py` emits no C.
A derived figure — 80,465 entries × ~6 bytes per `short` initializer cell and
separator ≈ 480 KB of table text, against D84's 1,000,000-byte total cap and
outside its 500,000-byte CODE cap by construction (table initializers are
excluded from the code figure by D84's own definition) — is **ARGUED, not
MEASURED**, and is in this document only so nobody mistakes its absence for
comfort. Only pcrec's own emitter settles it, and it cannot compile a UTF-8
pattern until stage 2 lands. That is P-5's territory and §8.1.1's check 3.

#### 2.4.2 Why the alphabet refinement is the term to watch

**ARGUED**, from §2.3's construction. An ASCII class contributes at most a
handful of equivalence classes because its transitions are one contiguous
byte range. A UTF-8 lowered class contributes one class per distinct
lead-byte range plus one per distinct continuation-byte range **per position**,
and the decomposition's whole job is to produce many such ranges — the
canonical 3-byte table alone has four lead ranges. The measured 95-96 for
`\p{L}`/`\w` is that, and it is close to the ceiling a single class can reach:
`.` under UTF, which touches every encodable code point, reads only 12,
because a class that covers everything needs almost no distinctions. **The
refinement is worst for a class that is large and IRREGULAR**, which is
exactly what a Unicode general category is.

**TWO CAVEATS, both stated rather than buried.**

1. **This is not pcrec's lowering, because pcrec has no UTF-8 lowering.** It
   is an independent from-scratch construction. It bounds what a correct
   implementation of the standard construction costs; it does not predict what
   pcrec's own will cost. §12 P-3 makes that falsifiable.
2. **The `\p{L}` row is Unicode 14.0.0 and PCRE2 10.46 is Unicode 16.0.0.**
   `out/sizing.txt` ran under this Mac's python 3.11 (`unicodedata` 14.0.0);
   `out/uprops.txt` §0 derives PCRE2's own version as **16.0.0**. The
   oracle-swept interval census (§3.3) gives `L` = **677** intervals against
   this table's 648 — a real 4.5% drift, quantified rather than hand-waved.
   It does not move any conclusion here (283 states versus a 10,000 cap), and
   §3.3's numbers are the ones §9 sizes tables from.

### 2.5 What happens to the byte-tier class machinery

Four consumers were named in the charter. **STRUCTURAL** in each case:

- **The 256-entry class bitmap machinery** is *below* the lowering and is
  untouched. `NState.cls[32]`, the DFA's `eqclasses` partition and its
  `d->rep[c]` representative-byte trick all operate on the byte alphabet, and
  after lowering the byte alphabet is all there is.
- **The class-axis views** (`upc_of_class`, `Dfa.s1w`, the `\b` context bit)
  ask "is the byte this class selects a word byte / a newline byte". Under
  UTF-8 the classes reaching them are byte-RANGE classes, and the question
  still has a well-defined answer — but *the answer is no longer the one the
  assertion needs*, because word-ness is a property of a CHARACTER. This is
  §5.4, and it is the one genuinely open engine question in the milestone.
- **`[OPT-CLSPACK]`'s forms** are helped rather than hurt. Its STEP 0 measured
  (`docs/dev/form_char_step0.md`) that range compares win on size and the
  shared-atom table wins at N≥16. A UTF-8 lowering produces byte-RANGE classes
  almost exclusively — the decomposition's output *is* contiguous ranges — so
  the form `[OPT-CLSPACK]` found cheapest is the form this lowering naturally
  emits. **ARGUED**; the measurement that would confirm it is a form census
  over a UTF-8 corpus, which cannot run until stage 2 lands.
- **`[FORM-CHAR]`'s object list loses one member.** §4.1 measures that 10.46
  does simple folding only, so object (5) `utf8-full-fold` has no PCRE2
  behaviour to reproduce.

#### 2.5.1 The FULL class-payload consumer census (r54 E5)

**ACCEPTED.** The four consumers above came from the charter's list, and the
charter's list is not the tree's. The census below is **grep-derived**, run in
this revision:

```
$ grep -rn 'u\.cls' src/            # every reader and writer, whole tree
```

**Nine live sites in six files**, plus two definition/comment sites. Each gets
a verdict against §2.1.2's forced position, and **the position is what decides
every row**: a site after `compile.c:1000` sees byte-confined intervals and
needs only the render helper; a site before it sees code points and must
widen or decline.

| # | site | what it reads it for | runs | verdict |
|---|---|---|---|---|
| 1 | `src/opt/altcls.c:158` | `memcpy(c->u.cls.bits, bits, 32)` — writes a merged class | :926, **BEFORE** | **WIDEN** |
| 2 | `src/opt/altcls.c:189` | `altcls_single_bit(arr[0]->u.cls.bits)` — is this branch one character? | :926, **BEFORE** | **WIDEN** |
| 3 | `src/opt/altcls.c:331`/`:333` | copies then ORs branch bitmaps — the union that factors an alternation | :926, **BEFORE** | **WIDEN** |
| 4 | `src/opt/possessify.c:168` | `memcpy(r.f, a->u.cls.bits, 32)` — the FIRST set | :988 → `:456`, **BEFORE** | **DECLINE** |
| 5 | `src/opt/possessify.c:529` | `gk_newpos(g, a->u.cls.bits)` — a Glushkov position's label | :988 → `:456`, **BEFORE** | **DECLINE** |
| 6 | `src/opt/revdet.c:451` | `memcpy(out, a->u.cls.bits, 32)` in `pcrec_revdet_first` | :988 → `:477`, **BEFORE** | **DECLINE** (the fallback already exists) |
| 7 | `src/ir/nfa.c:524-528` | `leaf[...]->u.cls.bits` — the trie's per-leaf bitmap | :1018, **AFTER** | render helper |
| 8 | `src/ir/nfa.c:542` | `memcpy(st[f.start].cls, a->u.cls.bits, 32)` — the `A_CLASS` arm | :1018, **AFTER** | render helper |
| 9 | `src/gen/emit_vm.c:1515`, `:3287`, `:4608`, `:7055` | the four sites E1 is about | :1228, **AFTER** | render helper |

Two further `u.cls` mentions are **not consumers**: `src/core/internal.h:487`
is the D70 layout comment (§2.2.3) and `src/opt/revdet.c:261` is the comment
on the kind guard beside it. Sites reading a `bits` PARAMETER rather than a
node — `emit_vm.c:1462`, `:7573`, `:7581`, `:7583`, `:10510`, and
`:7247`'s `pcrec_cls_word_esc` — are inside the emitter on already-rendered
arrays and are untouched (§2.2.2).

**THE THREE WIDEN ROWS (altcls).** All three operations have exact
interval-list forms, and none is new machinery: a union of two sorted
interval lists is a merge; "is this branch a single character" is
`n == 1 && iv[0].lo == iv[0].hi`; a copy is a copy. **Under
`--encoding=byte` every answer is identical to today's by construction**,
because complementing and unioning within `[0, 0xFF]` (§2.7.1) is the same
function as `~bits[i]` and `bits[b] |= …`. §8.1's identity gate is what
proves it rather than this sentence.

**THE THREE DECLINE ROWS (possessify, revdet), and why declining is honest
here and not lazy.** Both passes compute a FIRST-byte set to prove a
disjointness property, and **both have a safe direction that already exists in
the tree**: `internal.h:595` records that `pcrec_revdet_first` *"WIDENS to all
bytes, the sound"* answer, and possessify's whole §2.2 verdict is one it may
always decline to give. So the first landing's rule is:

> A node whose interval list touches anything above `0xFF` contributes the
> ALL-BYTES set to `pcrec_revdet_first`, and makes `possessify`'s
> disjointness test answer "not disjoint".

**The cost is a VERDICT, not an answer** — fewer possessifications and fewer
reverse-deterministic rungs on non-ASCII patterns, which is throughput and
artifact size, never correctness. **The cost is also entirely absent under
`--encoding=byte`**, where no interval can exceed `0xFF`, which is why §8.1's
identity gate still reads 100%.

**Widening them is DEFERRED under D77, with the measurement named.** The
trigger is a form census over a UTF-8 corpus reporting what fraction of
non-ASCII patterns lose a rung to the decline — and **that corpus does not
exist until stage 2 lands**, which is the same reason §2.5's `[OPT-CLSPACK]`
bullet and §6.3's two-value scan are recorded rather than built. Building the
interval-disjointness analysis now, against no measured loss, is the
unexercised structure D24/SR-2 warns about.

**WHAT THE CENSUS CHANGES ABOUT §2.5's OPENING CLAIM.** The first version said
the byte-tier class machinery *"is below the lowering and is untouched"*. That
is true of the six AFTER rows and **false of the three altcls rows and the
three verdict rows**, which sit above it because `pcrec_callgraph_build`
forces the lowering down past them (§2.1.2 constraint 2). The claim now reads:
everything below `compile.c:1000` is untouched, and everything above it is
enumerated in this table.

### 2.6 Invalid UTF-8: the decision, taken deliberately

`[DD-12] (3)` leaves this open and asks for a measurement against
`PCRE2_MATCH_INVALID_UTF`. **MEASURED** (`out/invalid_utf.txt`):

**(a) The PATTERN is validated at COMPILE time**, with nine distinct error
codes naming the specific clause violated — `-22` isolated continuation byte,
`-23` illegal 0xFE/0xFF, `-8`/`-9` truncation, `-17` overlong, `-16`
surrogate, `-15` above U+10FFFF, `-13` five-byte form. **This costs the
emitted artifact nothing** and pcrec's compiler owes it. (D26 tier: pcrec owes
the *refusal*, not the wording.)

**(b) Under `PCRE2_UTF` alone, an ill-formed SUBJECT is a whole-subject
precondition, checked before matching.** The discriminating cell: pattern `a`
on subject `61 FF 61` returns `ERRM -23`, **not** a match at offset 0 — even
though a valid `a` sits before the bad byte. So `PCRE2_UTF` pays an O(n)
validation pass on every match call.

**(c) `PCRE2_MATCH_INVALID_UTF` differs on all nine ill-formed subjects**, and
what it does is make ill-formed bytes a **barrier**: matches on either side
are found (`a` on `61 FF` gives `(0,1)`; on `FF 63` gives `(1,2)`), matches
*through* them are not (`a.c` on `61 FF 63` → no match; `\w+` on
`61 62 FF 63 64` → `(0,2)`, stopping at the barrier).

**(d) `[DD-12] (3)`'s wording is refuted and its instinct is right.** Under
`options=0` — pcrec's actual byte encoding — `a.c` on `61 FF 63` **matches
`(0,3)`**: a byte engine is delighted to consume `0xFF` as a character. So
`MATCH_INVALID_UTF` is *not* the byte-wise semantics. It is the semantics of a
**byte-wise UTF-8 automaton**, which has no path for an ill-formed sequence
and therefore cannot match through one — precisely what §2.3 builds.

**THE RULING THIS DESIGN PROPOSES** (and §14 ASK 1 puts to Frank, because it
is a user-visible semantic and not an implementation detail):

> Under `--encoding=utf8`, pcrec's artifact **treats an ill-formed byte
> sequence as matching nothing**. There is no validation pass, no error
> return, and no `RX_ERR_*` code for bad input. This is
> `PCRE2_MATCH_INVALID_UTF`'s answer on every cell measured, and pcrec gets it
> **for free from the automaton's structure** rather than from a check.

Three reasons, in order of weight. It is what the construction does anyway, so
the alternative costs *more* code, not less. It preserves the streaming
promise (M3): a whole-subject precondition cannot be checked on a chunk. And
it keeps DD-12 (7) — a validation pass would be encoding-conditional code on
the hot path, which is the thing the seam exists to forbid.

**The cost is a stated divergence from PCRE2's DEFAULT UTF mode**, and the
design does not hide it: a caller who wants "tell me the subject is broken"
gets "no match" instead. §14 ASK 1 asks whether that is acceptable or whether
an opt-in validation entry point is owed.

**AND THAT ANSWERS THE CHARTER'S "IS A NO-VALIDATE MODE A GENERATION AXIS?"
IN THE ONLY WAY THAT KEEPS D18.** The charter asks whether validation should
be a generation-time switch. Under the ruling above **there is no validation
to switch off**, so a `--no-validate` flag would be an axis with one value —
the definition of an axis that has not earned itself (D18), and a flag whose
`-fno-` form is a no-op is worse than no flag because it implies a behaviour
that does not exist. The axis becomes real only if ASK 1 is ruled the other
way, and in that case it is not a *no-validate* axis but a *validate* one:
the default stays the automaton's free answer and the opt-in adds a pass. The
design records the direction because getting it backwards would put the cost
on every artifact by default, which is exactly what `PCRE2_UTF` does and what
§2.6(b) measures as an O(n) pass per match call.

**(e) The mid-character cursor.** `out/invalid_utf.txt` §E: a `startoffset`
inside a character is `ERRM -36 "bad offset into UTF string"` under
`PCRE2_UTF`, and under `MATCH_INVALID_UTF` it silently advances to the next
character boundary (start=1 on `αβ` returns `(2,4)`). pcrec's own answer falls
out of the same rule as (d) — a cursor mid-character has no path — but §5.1
shows this is exactly what `next_pos` exists to make unreachable for the one
caller who could hit it.

#### 2.6.1 "No path" INVERTS for a negative assertion (r54 E14)

**ACCEPTED, and it narrows (e) rather than contradicting it.** "A cursor
mid-character has no path" is a SAFE answer for a positive match — no path
means no match, which is a miss and never a false hit. **For a negative
assertion it is the opposite.** `(?!X)` succeeds exactly when `X` has no
path, so at a mid-character position `(?!α)` **SUCCEEDS**, where a validating
engine skips the position (`MATCH_INVALID_UTF`, measured: start=1 on `αβ`
returns `(2,4)`) or refuses it (`PCRE2_UTF`, `ERRM -36`). The same inversion
applies to `(?<!X)`, and §5.2.1's repaired `back_step` is where it is actually
delivered.

**§2.6(e)'s cure covers ONE of the three ways a cursor gets to a
mid-character position, and the first version implied it covered all three.**
Stated per entry, which is what `docs/spec/match_api.md` §3.1 needs to gain
under D80:

| how the cursor gets there | protected by | the artifact's promise under `utf8` |
|---|---|---|
| the **find-all loop's own advance** (`match_api.md` §3.1) | **YES** — the loop advances by `<prefix>_next_pos`, which §5.1 makes a boundary walk. This is the entry `[M5-SEAM]` was built for | boundary by construction; the `+1` a pre-seam caller would have written is exactly the bug the entry deletes |
| a **caller-supplied `startpos`** to `<prefix>_search` | **NO** | the automaton's answer, which for a negative assertion differs from both PCRE2 UTF modes |
| `<prefix>_match`'s **anchored** entry at a caller-supplied position | **NO** | same |

**THE DESIGN'S POSITION, and it is the one §2.6's ruling forces.** Adding a
boundary check to the entries would be a validation pass by another name — a
branch on every call, encoding-conditional, on the hot path, which is what
§2.6 declines and what DD-12 (7) forbids. So:

> **`startpos` must be a character boundary of the artifact's encoding.**
> A caller who passes a non-boundary gets a DEFINED answer — the automaton's
> — which is not PCRE2's answer in either UTF mode, and which for a leading
> negative assertion differs in the SUCCEEDING direction. `next_pos` is the
> supported way to produce a valid `startpos`, and the find-all loop already
> uses it.

**This is a contract sentence, not an implementation note**, so it lands in
`docs/spec/match_api.md` §3.1 in stage 2's own change (§13 obligation 1), not
later. And **it is contingent on ASK 1**: if Frank rules that ill-formed input
must be reported rather than silently unmatched, this row changes with it, and
the opt-in validation entry that ASK 1 names is also where a `startpos`
boundary check would belong.

**What makes this cheap to get wrong**: every instrument a corpus author
naturally writes starts at `startpos = 0`, which is a boundary on every
subject. §8.3's `next_pos`/find-all axis therefore gains an explicit
**non-zero mid-character `startpos`** cell on a leading `(?!` and a leading
`(?<!` — the two shapes where the answer inverts — rather than leaving the
axis to be covered by find-all cells that structurally cannot reach it.

### 2.7 The parser changes, and only where UTF changes the language

`[DD-12] (1)`'s rule. **MEASURED** boundaries from `out/premises.txt` §2 and
`out/width.txt` §1:

- **`\x{...}` becomes meaningful above 0xFF.** Today it refuses with
  `unicode-props`; 10.46 gives error 134 (*"character code point value in
  \x{} or \o{} is too large"*) for `\x{3b1}` at `options=0` and accepts it
  under `PCRE2_UTF`. So `\x{...}` is **encoding-sensitive at the parser**:
  the same spelling is legal or not depending on a per-compile scalar. That is
  the one place this design puts an encoding question into the parser, and it
  is a RANGE CHECK on a value, not a conditional on behaviour.
- **A multi-byte atom quantifies as one unit.** Free: `\x{3b1}{2}` parses as a
  quantified atom and the atom lowers to a fragment. Nothing in `p_rep` cares
  how many bytes a fragment consumes.
- **`.` and `[^...]` change what they mean**, but only through the interval
  set. **The first version wrote that negation "complements within the
  code-point space rather than within 0..255" and that sentence is a
  BLOCKING defect — see §2.7.1.**

#### 2.7.1 The complement universe is PER ENCODING (r54 BLOCKING E2)

**ACCEPTED. As written, §2.1 and §2.7 together refuse every negated class
under `--encoding=byte` — which is stage 1's entire acceptance corpus.**

The collision, in two sentences that were four hundred lines apart:

- §2.1: the byte backend's lowering is *"code point c ≤ 0xFF becomes the
  one-byte sequence c, and **an interval touching anything above 0xFF is a
  compile error**"*.
- §2.7: *"negation complements within the **code-point space**"*.

So under `--encoding=byte`, `[^a]` becomes
`[\x{0}-\x{60}\x{62}-\x{10FFFF}]`, whose top interval touches `0x10FFFF`, and
the lowering **refuses it**. The same for `\D`, `\W`, `\S`, `\H`, `\V` and
`.`. **STRUCTURAL**, and the producers are three lines in one file, verified
at this tree: `src/parse/parse.c:449` and `:898` are the two
`a->u.cls.bits[i] = (uint8_t)~a->u.cls.bits[i]` negation loops (the
`from_bits` constructor and `p_class`'s own), and `:1115` is `.`, which fills
all 32 bytes and clears `\n`. Every one of them complements within `0..255`
TODAY, because a 256-bit bitmap has no other universe available — which is
exactly why nothing in the tree could have caught the design's error.

**THE REPAIR: the complement universe is a property of the ENCODING, and the
parser asks for it.**

```
negate(S)  =  [0, MAXCP(enc)] \ S
```

with `MAXCP(byte) = 0xFF` and `MAXCP(utf8) = 0x10FFFF`.

**Under `--encoding=byte` this is byte-identical to today by construction**,
not by measurement: complementing within `[0, 0xFF]` and `~bits[i]` are the
same function on the same set, so `[^a]`, `\D`, `\W`, `\S`, `\H`, `\V` and `.`
all produce the interval list whose rendering (§2.1.4's `pcrec_cls_bits`) is
the identical 32 bytes. §8.1's identity gate is the check; the argument is
that there is nothing for it to catch.

**THE BLAST RADIUS, MEASURED**, because "stage 1's whole acceptance corpus" is
a claim with a number behind it and the number is worth having. Over the
`pattern` lines of every `.rxt` file in `tests/` at this tree, excluding
`known_fail/`:

| | count | of 3,350 |
|---|---|---|
| patterns containing a negation-producing construct | **198** | 5.9% |
| — `[^…]` | 105 | |
| — an unescaped `.` (approximate: an in-class `.` is counted) | 95 | |
| — `\D` / `\S` / `\W` / `\H` / `\V` | 2 / 1 / 1 / 1 / 1 | |

**198 patterns is the direct damage and it is not the interesting number.**
Stage 1's acceptance is §8.1's identity gate at **100% byte-identity over the
whole corpus** (§9.2), so 198 refusals do not fail 5.9% of the bar — they fail
**the bar**, entirely, and stage 1 cannot land. That is what the panel meant,
and the 5.9% is the honest way to say it: a small population, a total
consequence.

**Note also what this population is NOT.** It is not exotic. `.` and `[^…]`
are the two most ordinary constructs in the list, present in a twentieth of a
corpus that was never built to exercise negation — so the un-repaired rule
would have been caught by the first patterns anyone tried, which is a fair
criticism of the design and not a defence of it. The defect survived because
the two sentences that produce it are four hundred lines apart and each is
correct in isolation.

#### 2.7.2 Why a universe field and not symbolic negation

The panel offered two repairs. **The design takes the universe field**, and
the argument against the other one is §2.2's own:

**REJECTED — carry negation symbolically to the lowering** (`A_CLASS` gains a
`negated` flag; the complement is taken where the encoding is known). It is
the more obviously encoding-agnostic shape, and it fails three ways:

1. **It reintroduces two representations of one set**, which is precisely
   what §2.2's second bullet refuses for the bitmap. Every consumer in
   §2.5.1's census — `altcls`'s union and single-character test,
   `possessify`'s FIRST set, `revdet_first` — would need a second code path
   for the negated case, and a predicate deciding which. That is the
   special-case shape `CLAUDE.md`'s situation index has a standing rule
   against.
2. **It breaks set identity, and the identity gate is what would report it.**
   `[^a]` and `[\x{0}-\x{60}\x{62}-\x{10FFFF}]` denote one set and would
   become two distinct nodes, so the artifact would depend on which SPELLING
   the pattern used. §8.1's gate is byte-identity over the whole corpus; a
   representation that varies with spelling makes that gate's 100% an
   accident of which spellings the corpus happens to contain.
3. **It puts D23's ordering rule at risk for no gain.** OS-1/D23 requires the
   caseless fold to be applied to the set BEFORE the negation, and §4.3
   measures that PCRE2 agrees including across blocks (`[^k]` caseless does
   not match U+212A). With an eager complement the order is visible in one
   constructor and §4.3's cells check it. With a deferred one, the fold is at
   parse time and the complement is at the lowering, a thousand lines apart in
   two files, and S-U1's sabotage — *"swap the order in the one constructor"*
   — no longer has one constructor to swap.

**TAKEN — a per-encoding maximum code point, read from the encoding.**
`PcrecEnc` gains one scalar:

```c
typedef struct {
    int         id;
    const char *name;
    unsigned    max_cp;   /* [M5.0] the complement universe: 0xFF for byte,
                           * 0x10FFFF for utf8. NOT a code-unit width and not
                           * a validity predicate — it is the answer to
                           * "what does `[^x]` mean here", and that is the
                           * only question that reads it. */
    const PcrecEncEntry *entries;
} PcrecEnc;
```

**AND THIS RETRACTS §5's HEADLINE, which the revision states plainly rather
than qualifying.** §5 opened *"the seam needs no interface change — D58's
revisit clause is honoured by having nothing to record."* **That is now false
as written.** What survives, and it is the claim the third-encoding recipe
actually makes, is:

> The seam's **ENTRIES TABLE** needs no interface change: four residual
> entries get UTF-8 bodies under their existing signatures, no
> `PcrecEncEntry` field is added, `pcrec_enc_ready` is untouched, and both
> emit functions are untouched — the property `[M6.6.2]` wave D demonstrated
> for `back_step`. **`PcrecEnc` itself gains one scalar**, which IS a D58
> seam change and IS a thing to record.

§12 P-1 is re-stated accordingly, and **ASK 7 routes the D58 record to
Frank** — not the mechanism, which is this design's call, but the decision-log
event.

#### 2.7.3 The explicit-`\x{>FF}` refusal stays DISTINCT

**And keeping the two apart is the whole of E2's second half.** The rule is on
the parser's LITERAL INPUT, never on a derived set:

| what | under `byte` | under `utf8` | why |
|---|---|---|---|
| `\x{3b1}`, or a range endpoint, WRITTEN above `MAXCP(enc)` | **compile error** | compiles | 10.46's own answer: err 134 *"character code point value in \x{} or \o{} is too large"* at `options=0`, accepted under `PCRE2_UTF` (`out/premises.txt` §2, `out/width.txt` §1) |
| an interval reaching `MAXCP(enc)` because a COMPLEMENT put it there | compiles | compiles | the user wrote `[^a]`; nothing above `0xFF` was named, and there is nothing to refuse |

**One test, one place, and it is the range check §2.7 already describes** —
*"a RANGE CHECK on a value, not a conditional on behaviour"* — applied at the
escape's own parse site, where the written value is in hand. A derived set
never passes through it, because by then there is no written value to check.
The two cells above are the discriminating pair a stage-2 corpus owes
(§8.3), and they are one line apart in the same file: `\x{3b1}` under `byte`
refuses, `[^a]` under `byte` compiles.

---

## 3. `\p{...}` / `\P{...}` — module `unicode-props` (charter (ii))

### 3.1 What 10.46 actually accepts

**MEASURED** (`out/uprops.txt` §1): 114 spellings tried, **83 compile, 30 are
error 147 (unknown property), 1 is error 146 (malformed)**. The 146/147 split
is the refusal surface `src/parse/mod_uprops.c` already ships, so this
extends a measurement the tree already depends on.

| axis | verdict |
|---|---|
| one-letter general categories `C L M N P S Z` | **compile** (the 7 pcrec's table already knows) |
| the other 19 letters | error 147 |
| two-letter categories (`Lu Ll Lt Lm Lo Mn Mc Me Nd Nl No Pc Pd Ps Pe Pi Pf Po Sm Sc Sk So Zs Zl Zp Cc Cf Cs Co Cn`) | **all 30 compile** |
| `L&`, `Any`, `Xan`, `Xps`, `Xsp`, `Xuc`, `Xwd`, `Assigned` | **compile** |
| bare script names (`Greek Latin Cyrillic Han Arabic Hebrew Hiragana Katakana Common Inherited Unknown Thai Deseret`) | **all compile** |
| `Script=`, `sc=`, `Script:`, `sc:` | **compile** |
| `Script_Extensions=`, `scx=`, `scx:`, `Script_Extensions:` | **compile** |
| boolean properties (`Alphabetic Uppercase Lowercase White_Space Bidi_Control Math Emoji ASCII_Hex_Digit Alpha Upper`) | **all compile** |
| `Bidi_Class=`, `bc=`, `bc:` | **compile** |
| **BLOCKS** (`InGreek`, `Block=Greek`, `blk=Greek`, `IsGreek`) | **error 147 — the one axis 10.46 does not have** |
| `\p{^L}` (caret negation inside braces) | **compiles** |
| `\p{grEEk}`, `\p{l a t i n}` | **compile** — case and separators insignificant, exactly the normalisation `mod_uprops.c` already implements |

The property surface is therefore **much larger than the charter's list**
(`\p{L}`, `\p{Lu}`, script names, `\p{scx:...}`): booleans and `Bidi_Class`
are two whole axes the charter did not name. §3.4 is where that gets staged
rather than shipped.

### 3.2 THE FINDING: `\p` does not require `PCRE2_UTF`

**MEASURED** (`out/uprops.txt` §2), and it changes the module's staging:

| options | compile `\p{L}` | `'a'` | U+00E9 as UTF-8 | U+00E9 as ONE BYTE | U+03B1 as UTF-8 |
|---|---|---|---|---|---|
| `options=0` | yes | MATCH | MATCH | **MATCH** | MATCH |
| `PCRE2_UCP` | yes | MATCH | MATCH | **MATCH** | MATCH |
| `PCRE2_UTF` | yes | MATCH | MATCH | ERRM −4 | MATCH |
| `PCRE2_UTF\|PCRE2_UCP` | yes | MATCH | MATCH | ERRM −4 | MATCH |

In an 8-bit non-UTF build, `\p{L}` matches the **single byte** 0xE9 — PCRE2
treats bytes 0–255 as code points 0–255, which is exactly what pcrec's `byte`
encoding is ("every byte is a character, 8-bit clean", D58's rename
rationale).

**Consequence: `unicode-props` is not an encoding-gated module.** Under
`--encoding=byte` a `\p{L}` is a 256-bit bitmap over the Latin-1 letters — an
ordinary bitmap producer exactly like `\d`, needing **no** structural
widening, **no** byte-sequence lowering, and no UTF-8 backend. This is what
lets §9 land `unicode-props` *before* the utf8 backend, on a stage whose
acceptance is entirely within today's machinery.

**A second, sharper consequence.** `[DD-11]`/D85's ruled-in class-escape
family (`\d \D \s \S \w \W \h \H \v \V \N \R` + POSIX classes) carries
*"predicate `always` today with UTF/UCP as the chartered second row"*. The
measurement above says the second predicate is **UCP, not UTF** — they are
independent bits and it is UCP that redefines `\w`/`\d`/`\s`/`\b`
(`out/uprops.txt` §2's second table, and every `UCP-SPLIT` row in
`out/divergence.txt`). A `[DD-11]` row keyed on the encoding would be keyed on
the wrong axis.

### 3.3 The table-size problem

The charter asks for a sizing estimate per property family "against the
artifact-size log's sensibilities". **MEASURED** by sweeping all 1,114,112
code points against a compiled `^\p{X}$` on the oracle itself
(`out/uprops.txt` §3) — so these are 10.46's own membership under Unicode
16.0.0, immune to the version caveat of §2.4:

| property | intervals | code points | sweep |
|---|---|---|---|
| `L` | **677** | 141,028 | 4.1 s |
| `Lu` | **651** | 1,858 | 3.8 s |
| `Nd` | **71** | 760 | 3.8 s |
| `Greek` | **44** | 531 | 3.8 s |
| `Han` | **42** | 99,338 | 4.0 s |
| `Xan` | **770** | 142,939 | 4.1 s |

The unit that matters is **intervals**, not code points: `Han` has 99,338 code
points in 42 intervals, and it is the 42 that the lowering and any table pay
for.

**What an artifact actually carries.** Not the interval table — that is
*compile-time* data inside pcrec. The artifact carries the **lowered
automaton**, and §2.4 measures it: `\p{L}` is 283 DFA states. Against
`[ART-SIZE]`/D84's caps (code-bytes 500,000, total-bytes 1,000,000) a
283-state DFA is unremarkable; the corpus already contains larger machines.
**So the "table-size problem" the charter names is, for the DFA route,
measured not to be a problem.**

It IS a problem in one place, and the design should say which: **pcrec's own
binary** must contain the property data for every property it can compile.
`\p{L}` at 677 intervals × 8 bytes is ~5.4 KB; the full general-category set
is roughly 5,000 intervals (~40 KB); adding all ~160 scripts and the boolean
properties would be several hundred KB of static tables in `libpcrec.a`. That
is a real cost and it is the reason §3.4 stages rather than ships everything.

**WHERE THE DATA COMES FROM IS THE HARD QUESTION, and it is an ASK.** There
are three sources and two of them are disqualified:

- **Generate from python's `unicodedata`** — disqualified by version drift,
  now quantified: python 3.11 says `L` has 648 intervals, 10.46 says 677
  (§2.4 caveat 2). And the two boxes this project uses carry *different*
  pythons (3.11/Unicode 14.0.0 here, 3.14/Unicode 16.0.0 there), so the
  generated table would depend on which machine ran the generator.
- **Generate by sweeping libpcre2** — disqualified by the rule
  `src/parse/mod_uprops.c`'s own header states, in the manager ruling that
  made its short-name table hand-written: *"a table generated from libpcre2
  and then checked by a differential against the SAME libpcre2 install is one
  source wearing two hats"*. PC-3 and PC-4 are the independent checks; making
  them check their own generator's output would delete them.
- **Vendor the UCD data files** (`UnicodeData.txt`, `Scripts.txt`,
  `ScriptExtensions.txt`, `PropList.txt`, `DerivedCoreProperties.txt`) at a
  **pinned Unicode version**, generate into a `.inc` at build time exactly as
  `cls_bits.inc` is generated today, and let PC-3/PC-4's libpcre2 differential
  remain the independent check. **This is the design's recommendation** and
  §14 ASK 2 puts it to Frank, because it is the first third-party data this
  repository would vendor and `third_party/` currently holds only PCRE2's
  BSD-licensed testdata.

The version pin is itself a decision: pinning to 16.0.0 matches 10.46 today
and will drift when the reference libpcre2 moves, which D26's addendum already
treats as a re-measurement event.

### 3.4 What ships, what refuses

**ASSERTED** staging, on the sizing above:

| family | first landing | why |
|---|---|---|
| one- and two-letter general categories, `L&`, `Any`, `Assigned` | **SHIP** | ~5,000 intervals total; one UCD file; the family every `\p` user reaches for first |
| `Xan Xps Xsp Xuc Xwd` | **SHIP** | PCRE2-specific, defined in terms of the categories above — derived, no new data |
| script names, `Script=`/`sc=` | **stage 5** | one more UCD file, ~160 names; nothing structural, purely table weight |
| `Script_Extensions=`/`scx=` | **stage 5, with scripts** | same file family; the charter names `scx:` explicitly |
| boolean properties (`Alphabetic`, `Math`, `Emoji`, …) | **REFUSE at first landing** | a third data family; no measured demand |
| `Bidi_Class=`/`bc=` | **REFUSE** | a fourth; no measured demand |
| **blocks** (`InGreek`, `blk=`) | **REFUSE PERMANENTLY** | 10.46 refuses them too (error 147). Reproducing a refusal is free and correct. |

A refused-but-well-formed body must refuse **as `unicode-props` not
implementing it**, never as unknown — the wording rule `mod_uprops.c`'s header
already states (pcrec may only claim "not recognised" where its own table is
exhaustive for the axis). The 146/147 distinction it ships is unchanged.

---

## 4. DD-1: caseless under UTF (charter (iii))

`[DD-1]`'s remaining half is *"multi-byte fold pairs, one-to-many foldings and
the fold-before-negate rule over byte-range trees rather than a 256-bit
bitmap"*. Three questions; the measurement answers all three and **deletes
one of them**.

### 4.1 10.46 does SIMPLE folding only — so there are no one-to-many foldings

**MEASURED** (`out/caseless.txt` §2). Eleven one-to-many cells — ß/SS, ß/ss,
SS/ß, ss/ß, U+FB01/fi, fi/U+FB01, U+FB03/ffi, U+0149, U+01F0, U+1E96, U+0390 —
under `PCRE2_UTF|PCRE2_CASELESS` and under `…|PCRE2_UCP`:

> **1:n cells that matched under some caseless option: 0 of 11**

And from the other side, `[ß]` caseless does not match `"ss"` or `"SS"`, and
`[s]` does not match `ß`.

**This is the section's most valuable result because of what it removes.** A
1:n fold cannot live in a set — it is a *sequence*, so it would force a
caseless literal to become an alternation and a caseless class to hold
something a class cannot hold. `[FORM-CHAR]`'s object (5) `utf8-full-fold`
(*"1:n folds (ß ↔ SS): a small NFA step"*) has **no PCRE2 behaviour to
reproduce** and should not be built. Object (4) `utf8-simple-fold` is the
whole job.

**D23's rule therefore survives verbatim**: the fold is applied to the SET, in
the one constructor, at parse time. Only the set is now code points.

### 4.2 It is a CLOSURE, not a pairing — and it reaches outside the range

**MEASURED** (`out/caseless.txt` §3, §3b, §5). Three findings that constrain
the implementation:

**(a) Equivalence classes have more than two members.** `k` ↔ `K` ↔ U+212A
(KELVIN) all match each other; so do `s` ↔ `S` ↔ U+017F (LONG S). A
constructor that "adds the other case" from a single case-mapping table gets
these wrong. It must compute the **closure** of the set under the fold
relation.

**(b) The partner is often in a different block.** Measured matching pairs:
KELVIN U+212A ↔ k, ANGSTROM U+212B ↔ å, OHM U+2126 ↔ ω, MICRO U+00B5 ↔ μ,
LONG S U+017F ↔ s, final sigma U+03C2 ↔ σ ↔ Σ. And two that **do not** fold:
U+0130 (dotted capital I) and U+0131 (dotless i) match neither `i` nor `I` —
which is Unicode's default simple case folding, and a naive
`toupper`/`tolower` table would get both wrong in opposite directions.

**(c) THE CLOSURE ADDS INTERVALS FAR FROM THE WRITTEN ONES.** The sharpest
cell in the section: **`[a-z]` under caseless matches U+212A** (3 bytes) and
**U+017F** (2 bytes). So the fold cannot be a post-pass over byte ranges — by
the time the set is byte ranges, U+212A is not adjacent to anything in
`[a-z]`. **The fold must happen while the set is still code points**, which is
`[DD-12] (5)`'s prediction confirmed and is the ordering constraint the
implementation must not get wrong.

**(d) A consequence for literals nobody had written down.** Because folding is
1:1 but the partners have different encoded lengths, **a caseless
single-character match consumes a variable number of bytes**: `(?i)k` against
U+212A matches `(0,3)`. Under UTF-8 a caseless literal is a code-point class
whose members encode to different byte counts — and §2.3's construction
handles that with no new machinery, because an alternation of byte-sequences
of differing length is exactly what it already builds. **No special case is
needed**; the fact is recorded because it is surprising and because §5.3 needs
it.

### 4.3 Fold before negate, over UTF

**MEASURED** (`out/caseless.txt` §4). OS-1/D23's ordering rule holds under
UTF, including across blocks:

| cell | result |
|---|---|
| `[^k]` caseless on `K` | no match |
| `[^k]` caseless on **U+212A** | **no match** ← the whole test |
| `[^K]` caseless on `k`, on U+212A | no match |
| `[^s]` caseless on U+017F | no match |
| `[^a-z]` caseless on `A` | no match |
| `[^\p{Ll}]` caseless on `A` | no match |

The negation is over the **closed** set. Since §4.2(c) puts the closure before
the byte lowering and the negation is a complement of the interval list, the
existing constructor's order — fold, then negate, then lower — is unchanged.
`pcrec_ast_class_node`'s single-constructor discipline is what carries this,
exactly as it does today.

### 4.4 The ruled subset for first landing

**ASSERTED**, and deliberately not a subset at all:

> **Full simple case folding ships**, because the measurement shows that IS
> the whole of PCRE2 10.46's behaviour. There is no 1:n tier to defer.

The boundary that *does* need stating is the **data**, and it is §3.3's
question one axis over: the fold closure needs `CaseFolding.txt` (the `C` and
`S` status lines — simple folding), a fifth UCD file, pinned to the same
version. Under `--encoding=byte` the closure is the ASCII one pcrec already
has (`src/core/fold.c`), unchanged and byte-identical.

### 4.5 The UCP wrinkle, and pcrec has no UCP axis

**MEASURED** (`out/caseless.txt` §7): without `PCRE2_UTF`,
`PCRE2_CASELESS` alone folds **only the 52 ASCII letters** (byte 0xE9 does not
match 0xC9), which is exactly `enc_byte.c`'s residual contract and exactly
`src/core/fold.c`. But `PCRE2_UCP|PCRE2_CASELESS` **does** fold them.

pcrec has no `UCP` axis today, so pcrec's `byte` encoding reproduces PCRE2 at
`CASELESS` and diverges at `UCP|CASELESS`. That is a **pre-existing, correct**
state of affairs — pcrec's byte semantics are `options=0`-family — and this
design does not change it. It is recorded because §7's corpus author will meet
it as eight `UCP-SPLIT` rows and needs to know pcrec has no lever there.
§14 ASK 4 asks whether a UCP axis is owed at all.

### 4.6 Where the fold DATA lives, and it is two places (r54 SHOULD E9)

**ACCEPTED, and the finding is that §4.4 conflated two costs.** §4.4 named
`CaseFolding.txt` as *"the data"*, singular. There are two consumers with two
different lifetimes, and only one of them was priced.

**(a) pcrec's own binary — a COMPILE-TIME table.** The fold closure is applied
to the interval set at parse time (§4.2c, D23), inside pcrec. This is §3.3's
cost one axis over, it lives in `libpcrec.a`, and it never reaches an
artifact. Simple case folding is ~1,500 mappings; as sorted pairs that is a
few tens of KB, on the same order as §3.3's general-category tables and priced
by the same ASK 2.

**(b) THE EMITTED ARTIFACT — a RUN-TIME table, and this is the one that was
missing.** A caseless **backreference** cannot fold at compile time, because
the thing being folded is subject bytes read at match time. That is the whole
reason `PCREC_ENCE_BREF_CASELESS` is a seam entry at all
(`backrefs_design.md`'s spine: *"a backreference is not a class-membership
test, so caselessness cannot fold away at parse time"*). Under `byte` the
entry's body carries `src/core/fold.c`'s 52-byte ASCII set. **Under `utf8` it
must fold arbitrary code points, in the artifact's own residual text.**

**Sized against D84** (`limits.def:157`/`:159` — 500,000 code bytes,
1,000,000 total), **ARGUED**:

| form | size | against D84 |
|---|---|---|
| a full 0x110000-entry mapping | ~4.4 MB | **4.4× the TOTAL cap** — impossible |
| the ~1,500 simple-fold pairs, as a sorted `{from, to}` table with a binary search | ~12 KB of table text | 1.2% of the total cap; **outside** the code cap, since D84 excludes table initializers by definition |
| the pairs, restricted to code points the PATTERN's referenced groups can contain | pattern-dependent, usually 0 | free where it applies, and it does not apply to `(\w+)\1` |

**So the design's answer is the middle row and it is a real constraint on the
entry's body**: the UTF-8 `bref_match_caseless` decodes one character from
each side, folds each through a sorted table with a binary search, and
compares — it may **not** carry a direct-indexed map. That is a sentence the
first version owed and did not write, and it is the difference between a
12 KB artifact and one D84 refuses outright.

**AND `fold_agreement_check.c` MUST BE REDESIGNED, NOT RE-RUN.** Its present
population is the 52 ASCII letters, and it checks byte-for-byte that pcrec's
fold set and libpcre2's agree. Under UTF-8 the domain is 1.1M code points, so:

- **re-running it as written is a 1.1M-cell sweep** on every `make test`,
  which is §3.3's own oracle-sweep cost (3.8-4.1 s per property, measured) and
  is not a per-suite price this project pays;
- and the sweep would compare **pcrec's vendored `CaseFolding.txt` against
  libpcre2's own Unicode data**, which is a version comparison wearing a
  correctness check's clothes — it would go red on a libpcre2 bump for a
  reason that is not a pcrec defect. That is D26's addendum territory (a
  re-measurement event), not a `make test` failure.

The design's proposal: the check keeps its **byte-tier** population exactly as
it is (it is cheap and it guards `fold.c`, which does not move), and the UTF-8
tier gets a **pinned-version equality check** against the vendored data plus a
**sampled** differential against libpcre2 whose sample is the measured
interesting set — §4.2's cross-block pairs (K/U+212A, S/U+017F, ω/U+2126,
µ/U+00B5, å/U+212B, σ/ς/Σ) and the two measured NON-folds (U+0130, U+0131),
which are the cells a naive `toupper`/`tolower` table gets wrong in both
directions. **The full sweep becomes a version-bump ritual, not a suite
member**, which is what ASK 3 is already asking about for §4.1's own result.

The seam is `src/gen/enc/enc.h`'s `PcrecEncEntry` table, four entries today.
**The headline of this section is that the seam needs no interface change** —
D58's revisit clause is honoured by having nothing to record — **and that the
one thing that does have to change is an ANALYSIS outside the backend, which
the seam was never going to catch.**

### 5.1 `next_pos` — the entry the seam was built for

**STRUCTURAL.** The contract is already encoding-neutral: *"the smallest
position strictly greater than `pos` that is a character boundary of this
artifact's encoding, counting every position ≥ n as a boundary"*. The UTF-8
body:

```c
size_t $_next_pos(const unsigned char *s, size_t n, size_t pos)
{
    size_t i = pos + 1;
    while (i < n && (s[i] & 0xC0) == 0x80) i++;
    return i;
}
```

Reads `s` only in `[pos, n)`, as the contract promises; `pos >= n` returns
`pos + 1` because the loop does not run. **No caller changes a character** —
`docs/spec/match_api.md` §3.1's find-all loop is already final.

**Why this is not merely cosmetic.** `out/width.txt` §4a runs PCRE2's own
find-all over `αβγ` advancing by `+1` past an empty match: the second
iteration lands mid-character and PCRE2 returns `ERRM -36`. The `+1` a caller
would have written before `[M5-SEAM]` is exactly the bug this entry deletes.

**It stays `engine_callable = false`.** Unanchoredness is the automaton's own
self-loop; there is no external advance for an engine to route through, and
`tests/codegen`'s `[M5-SEAM]` check keeps enforcing that.

### 5.2 `back_step`, and THE WIDTH FINDING

The contract already says the right thing — *"the position exactly `k`
CHARACTERS before `pos`"* — and `enc_byte.c`'s own comment explains that `s`
and `n` are parameters this backend ignores *because* "a UTF-8 backend walking
back over continuation bytes must reject a MALFORMED sequence". The body:

> **THE BODY BELOW IS THE FIRST VERSION'S AND IT IS WRONG (r54 MUST-FIX E4).**
> It is kept for one paragraph because the defect is instructive and the
> repair is a two-line addition to it, not a rewrite. §5.2.1 is the shipping
> body.

```c
/* r54: SUPERSEDED — see §5.2.1. Walks back over continuation bytes without
 * ever checking that the lead byte DECLARES the length of the run it walked. */
size_t $_back_step(const unsigned char *s, size_t n, size_t pos, size_t k)
{
    (void)n;
    while (k--) {
        if (pos == 0) return $_BACK_STEP_NONE;
        do { pos--; } while (pos > 0 && (s[pos] & 0xC0) == 0x80);
        if ((s[pos] & 0xC0) == 0x80) return $_BACK_STEP_NONE;  /* ran off */
    }
    return pos;
}
```

**MEASURED** boundary cells (`out/width.txt` §4b): one character precedes →
succeeds; nothing precedes → clean fail; **a continuation byte precedes with
no lead byte** → PCRE2 answers `ERRM -22`, and this body answers
`BACK_STEP_NONE`, which under §2.6's ruling is the right pcrec answer (no
path, no match). Fewer than `k` characters precede → clean fail.

#### 5.2.1 The malformed-run defect, and the repair (r54 E4)

**ACCEPTED.** §2.6's ruling is that an ill-formed sequence *"matches
nothing"*, and §2.3's argument is that this costs nothing because ill-formed
input *"has no path"*. **That is true of the forward automaton and NOT of
`back_step`**, which is not the automaton — it is byte arithmetic that walks
the other way. Where the two disagree, the artifact does not silently
no-match: it **traps**.

**THE WORKED CELL**, from the panel and re-derived here against the body
above. Subject `C2 80 80` (a two-byte lead followed by *two* continuations —
one continuation byte too many), `pos = 3`, `k = 1`, body `.`:

| step | value |
|---|---|
| `pos=3`, not 0; walk back | `pos=2` (`0x80`, continuation), `pos=1` (`0x80`), `pos=0` (`0xC2`, not a continuation) — loop exits on `pos > 0` |
| lead check `(s[0] & 0xC0) == 0x80`? | `0xC2 & 0xC0 == 0xC0` — **not** a continuation, so no `BACK_STEP_NONE` |
| **returns** | **0** |
| the body `.` runs forward from 0 | `C2 80` is a well-formed 2-byte character; the automaton accepts it and **ends at 2** |
| the emitted end-check (`emit_vm.c:6335-6352`) | `scan_position (2) != slot_values[…] (3)` |
| on `(?<=` | `goto rx_fail` — a clean decline |
| **on `(?<!`** | **`return RX_R_INTERNAL`** |

`RX_R_INTERNAL` is `PCREC_ERR_INTERNAL`, `-6`, deliberately **below**
`PCREC_ERR_FLOOR`, and `emit_vm.c`'s own note 3 says why: it means *"the
artifact catching its own analysis disagreeing with its own emission"*, and
a composed call site honouring F2's `if (ret < PCREC_ERR_FLOOR)
__builtin_trap();` **traps on it**. So a subject §2.6 promises will merely not
match aborts the process instead. **STRUCTURAL**, all three sites verified at
this tree.

**THE CAUSE IS ONE MISSING CHECK, and `enc_byte.c` predicted it by name.**
The shipped comment at `src/gen/enc/enc_byte.c:205-209` explains why `s` and
`n` are parameters a byte backend ignores:

> *"a UTF-8 backend walking back over continuation bytes must reject a
> MALFORMED sequence, which is a failure mode the byte backend cannot have
> and needs the subject's bounds to detect."*

The first version's body rejects **one** malformed shape — a continuation run
with no lead byte at all — and misses the other: a run whose lead byte
declares a length different from the number of bytes actually walked. It never
reads the lead byte's declared length.

**THE REPAIR: `back_step` validates the declared length of every character it
steps over.**

```c
size_t $_back_step(const unsigned char *s, size_t n, size_t pos, size_t k)
{
    (void)n;                       /* reads only below `pos`, as the contract says */
    while (k--) {
        size_t end = pos;          /* one past the character being stepped over */
        size_t want;
        unsigned char lead;

        if (pos == 0) return $_BACK_STEP_NONE;
        /* At most 3 continuation bytes may precede a lead byte. Stopping at 3
         * is not a guard against long runs -- it is the encoding: a 5-byte
         * form is not UTF-8, so a 4th continuation means the run is malformed
         * and the length test below rejects it anyway. */
        do { pos--; } while (pos > 0 && (s[pos] & 0xC0) == 0x80 && end - pos < 4);

        lead = s[pos];
        if      (lead < 0x80)            want = 1;
        else if ((lead & 0xE0) == 0xC0)  want = 2;
        else if ((lead & 0xF0) == 0xE0)  want = 3;
        else if ((lead & 0xF8) == 0xF0)  want = 4;
        else return $_BACK_STEP_NONE;   /* a continuation byte, or 0xF8..0xFF */

        /* THE LINE THE FIRST VERSION DID NOT HAVE. The lead byte must DECLARE
         * exactly the run this loop walked. Without it a `C2 80 80` run
         * answers "one character back = 0", the forward body consumes the
         * well-formed `C2 80` and ends at 1 past where it started, and the
         * lookbehind end-check -- whose redundancy proof assumes back_step and
         * the forward parse agree -- fires. On a NEGATIVE lookbehind that is
         * RX_R_INTERNAL, below PCREC_ERR_FLOOR, and a composed site traps.
         * r54 E4. */
        if (want != end - pos) return $_BACK_STEP_NONE;
    }
    return pos;
}
```

**THE INVARIANT IT BUYS, which is the thing worth having and is stronger than
"the E4 cell now passes".**

> If `back_step(s, n, pos, k)` returns `q`, then `s[q..pos)` decomposes into
> exactly `k` length-consistent UTF-8 runs. A `k`-character-wide body started
> at `q` therefore ends at `pos` **on every input**, well-formed or not — so
> `emit_vm.c`'s note-3 redundancy proof, which the first version made true
> only on well-formed subjects, becomes true unconditionally, and
> `RX_R_INTERNAL` becomes unreachable from this construct.

**ARGUED**, and the step is: each iteration validates its own run
independently and the runs tile `[q, pos)` exactly (each iteration's `end` is
the previous `pos`), so the backward decomposition is forced; UTF-8 is a
prefix code, so a forward parse of a well-formed run agrees with it; and where
a run is NOT well-formed the forward automaton has no accepting path over it
(§2.3), so there is no body success to mis-check.

**Worked, in both directions:**

| subject | `pos`,`k` | old body | repaired body | why |
|---|---|---|---|---|
| `C2 80 80` (E4's cell) | 3, 1 | **0** → trap | `BACK_STEP_NONE` | lead `C2` declares 2, run is 3 |
| `61 CE B1` (`"aα"`) | 3, 1 | 1 | **1** | `CE` declares 2, run is 2 — unchanged |
| `61 CE B1` | 3, 2 | 0 | **0** | second run: `61` declares 1, run is 1 — unchanged |
| `80 80` (no lead) | 2, 1 | `NONE` | `NONE` | `0x80` is a continuation — unchanged |
| `C0 80` (overlong NUL) | 2, 1 | 0 | **0** | length-consistent, so `back_step` accepts it; **the forward automaton does not** (overlongs are absent, §2.3), the body fails, the end-check is never reached |

The last row is deliberate and is where the invariant is doing real work.
`back_step` is a **length** test, not a validity test, and it is a strict
SUPERSET of the automaton's character set — it accepts overlong and surrogate
encodings. That is safe, and stronger than making it a validator would be: the
invariant only needs "body success implies end == pos", and length-tiling
gives it, while a full validity check in `back_step` would be a second,
independently-maintained UTF-8 decoder beside the automaton — two definitions
of well-formedness that could drift, which is the parallel mechanism §2.1.3
already refuses once.

**Consequences for the rest of the document, all applied:**

- §5.2's "**MEASURED** boundary cells" list gains a fourth row — a
  length-inconsistent run → `BACK_STEP_NONE` — and it is **ARGUED**, not
  measured, because PCRE2 has no comparable entry point to measure it against;
  what `out/width.txt` §4b measures is PCRE2's whole-match answer on those
  subjects, which is a different question.
- **S-U5's sabotage is now under-powered and is strengthened** (§8.2): "make
  it `pos - k`" is detected by any multi-byte subject. The failure this
  section is about needs its own row, **S-U9**, deleting the length test
  alone — which is invisible on every well-formed subject and, on the E4 cell
  under `(?<!`, is an abort rather than a wrong answer.
- §12 gains **P-9**: no subject exists on which a `(?<!X)` artifact returns
  `RX_R_INTERNAL`. Refuted by one.

**AND NOW THE FINDING.** `k` is in CHARACTERS. Where does pcrec's `k` come
from? `src/parse/mod_lookaround.c`'s `la_widths`:

```c
long long lo = pcrec_minw(a->r), hi = pcrec_maxw(a->r);
if (lo != hi || hi >= PCREC_W_UNBOUNDED || hi > INT_MAX) { ... refuse ... }
out[i] = (int)hi;
```

and `pcrec_minw`/`pcrec_maxw` are documented, in their own headers, as
counting **BYTES**. Under the byte encoding the two units coincide and nothing
in the tree can tell them apart. Under UTF-8 they do not. §5.6 is the
resolution.

### 5.3 The backreference compares

`enc_byte.c`'s comment makes a specific prediction about why the entry returns
a LENGTH rather than a bool:

> `(?i)^(ss)\1$` on `"ss\xdf"` is the cell a UTF-8 build has to answer
> differently, with one captured character folding to two and the consumed
> length no longer equalling the captured one.

**MEASURED** (`out/caseless.txt` §6): that cell is **no match** under
`PCRE2_UTF|PCRE2_CASELESS`, exactly as it is in the 8-bit build. **The
prediction is refuted**, and it is refuted by §4.1 — there is no 1:n folding,
so the sharp-s family does not behave that way.

**But the design decision it justified is CORRECT, for a different reason this
lane measured.** Same section:

> `^(k)\1$` on `6B E2 84 AA` (`k` then U+212A) → **MATCH(0, 4)**

The captured group is **one byte** (`k`); the backreference consumed **three**
(U+212A). The compare is **not length-preserving**, because §4.2's 1:1
cross-block folds pair code points of different encoded lengths. So:

- The `ptrdiff_t` length return is vindicated. A `bool` could not express it,
  and the shared emitter "never computes a length, it only adds the one it is
  given" — DD-12 (7) working as designed.
- **`enc_byte.c`'s comment should be corrected at the [M5.0] merge**, not
  deleted: it names the right mechanism and the wrong witness. The design's
  §12 P-6 turns that into a check.
- The UTF-8 caseless compare walks CHARACTERS on both sides, folding each,
  and returns the SUBJECT bytes consumed. On failure it returns
  `-(prefix) - 1` where `prefix` is subject bytes compared equal — the
  protocol is unchanged.

The case-sensitive compare is a plain `memcmp` under any encoding (UTF-8 is
self-synchronising; equal bytes ⇔ equal code points), which is `[FORM-CHAR]`
object (3) `utf8-exact` and is worth stating because it means the
non-caseless entry's body is **literally unchanged** between backends.

### 5.4 `\b` and word classification — the entry that does not exist

**This is the milestone's one genuinely open engine question**, and the design
states it as such rather than resolving it cheaply.

`\b` is shipped (`[M6.2]` wave B) as a **class-axis context bit** in the DFA
state identity: `upc_of_class` asks whether a byte class is a word class by
testing its representative byte against `pcrec_cls_word_esc[32]`. That
mechanism is exact when one byte is one character. Under UTF-8 the classes
reaching it are byte-RANGE classes and word-ness is a property of the
**character**, so the representative-byte test is asking the wrong question.

**MEASURED** (`out/width.txt` §4c), the cells a UTF-8 build must answer:

| cell | `PCRE2_UTF` | `PCRE2_UTF\|PCRE2_UCP` |
|---|---|---|
| `\bx` on `αx` | `(2,3)` | no match |
| `\Bx` on `αx` | no match | `(2,3)` |
| `\b` on `αβ` | no match | `(0,0)` |

Note the two columns **disagree**, which is §4.5's UCP wrinkle arriving in the
engine: without UCP, `\w` is ASCII-only and α is a non-word character, so
there IS a boundary; with UCP there is not.

**THE DESIGN'S POSITION**, and it is deliberately the modest one:

> **Without `UCP`, `\b`'s alphabet is ASCII-only, and the shipped mechanism is
> already correct under UTF-8.** `\w` is `[A-Za-z0-9_]`, every member is a
> one-byte character, and every byte of a multi-byte character is a
> non-word byte — so the byte-level test and the character-level test agree
> on every input. **STRUCTURAL**, and §12 P-4 is the sweep that would refute
> it.

That is why this section proposes **no fifth seam entry** at first landing. A
seam entry for word classification becomes necessary exactly when a UCP axis
lands (§14 ASK 4), and building it now would be the unexercised structure
D24/SR-2 warns about. **The door is recorded as built, not walked through**:
the seam's entries table grows by one row, per `enc.h`'s own third-encoding
recipe, with no interface change — the property `[M6.6.2]` wave D already
demonstrated (prediction P-1).

#### 5.4.1 P-4's SECOND leg, written down (r54 NOTE E12)

**ACCEPTED.** The position above rests on **two** structural facts and the
first version wrote only one of them. Both must hold; they break under
different conditions, and the one that was written down is not the fragile
one.

**LEG 1 — the one §5.4 states.** Without `UCP`, `\w` is `[A-Za-z0-9_]`; every
member is a one-byte character; and every byte of a multi-byte character is a
continuation byte or a lead byte, none of which is in that set. So "is the
byte a word byte" and "is the character a word character" agree on every
input. **Breaks when:** a UCP axis lands (§14 ASK 4) — at which point the
question is about characters and no byte answers it.

**LEG 2 — the one that was missing.** `upc_of_class` (`internal.h:2850`)
answers the class-axis context by testing a **representative byte**:

```c
if (cls_has(pcrec_cls_word_esc, d->rep[c])) return UPC_WORD;
```

`d->rep[c]` is one byte standing for a whole equivalence class, and a
representative is only a legitimate answer if the class is **homogeneous** in
the property being tested. It is — but not by luck, and not because of
anything about `\w`. It is because `src/ir/dfa.c:173` refines the alphabet by
that very set first:

```c
if (has_word) ncls = refine_by(d, ncls, pcrec_cls_word_esc);
```

`internal.h:1144` says so in its own words — *"`upc_of_class` is exact rather
than a sample"*. **The refinement is what makes the representative exact**, and
it is a step in a different file from the test that depends on it.

**Breaks when:** the word set stops being expressible as a set of BYTES. Under
`UCP` it is not — "this character is a word character" partitions
*characters*, and the bytes `0x80-0xBF` appear inside both word and non-word
characters, so no `refine_by` over a 32-byte table can make the equivalence
classes homogeneous. **`refine_by` would still run and still return an answer**,
and `upc_of_class` would still test a representative, and the representative
would be a sample rather than a proof — silently.

**Why writing this down matters more than it looks.** Leg 1's failure under
UCP is obvious and §4.5 already flags it. **Leg 2's failure is the same
trigger and is invisible**, because nothing asserts homogeneity: the code that
establishes it and the code that consumes it are in two files and connected
only by a comment. So the UCP axis, if it is ever chartered, does not merely
need a seam entry for word classification (§5.4's own conclusion) — **it needs
`upc_of_class`'s representative-byte mechanism replaced, not extended**, and
that is a DFA state-identity change rather than a seam addition. §14 ASK 4 is
re-worded to say so, because "a word-classification seam entry becomes
necessary" understated what a UCP axis costs.

**P-4 accordingly becomes two predictions** (§12), one per leg, each with its
own refutation.

### 5.5 `\G` and the other advances

**STRUCTURAL.** `\G` is `pos == startpos`, an absolute position test that
reads no byte (`assertions_design.md` §4.2, and `internal.h`'s `N_GSTART`
comment). It has no encoding-sensitive residue at all. The charter lists it;
the answer is that there is nothing to instantiate.

`ENG_ATTEMPT`'s `for (start = startpos; start <= start_max; start++)` is a
genuine external byte-arithmetic advance loop in shared emitter code —
`assertions_design.md` already flagged it as outside D58's "the hot path has no
external advance loop" rationale. Under UTF-8 it would try starts
mid-character. **Those starts have no path** (§2.6) so they cannot produce a
wrong answer; they are wasted attempts, at up to 3 per character.
**ASSERTED**: correct but not optimal, and the optimisation (step the loop by
`next_pos`'s rule) is deliberately NOT taken here, because routing that loop
through a residual entry is precisely what `engine_callable = false` and
sabotage row S68 forbid. §14 ASK 5 raises it; §11 puts it out of scope.

### 5.6 The cross-note answered — and its prescription refuted

The `[M5.0]` row says:

> `pcrec_maxw`'s A_CLASS arm answers 1 BYTE and is EXACT only because
> `src/core/compile.c` refuses `PCREC_ENC_UTF8` by name; the day a UTF-8
> backend lands that arm **must become the encoding's maximum code-unit
> length**, or the lookbehind fixed-width rule silently accepts
> variable-width branches.

**The hazard is real. The cure is wrong, and following it would break every
lookbehind under UTF-8.**

**MEASURED** (`out/width.txt` §1, §2): PCRE2 measures lookbehind length in
**CHARACTERS**.

| pattern | compiles under UTF | `PCRE2_INFO_MAXLOOKBEHIND` |
|---|---|---|
| `(?<=a)x` | yes | 1 |
| `(?<=\x{3b1})x` | yes | **1** ← 2 bytes, reported as 1 |
| `(?<=[a\x{3b1}])x` | **yes** | **1** ← 1-or-2 bytes, ONE branch |
| `(?<=.)x` | yes | 1 |
| `(?<=a\x{3b1})x` | yes | 2 |
| `(?<=a*)x` | **err 125** | — |

The discriminating cell is row 3: **one branch, fixed at one character,
variable at one-or-two bytes, and 10.46 compiles it.** The
`MAXLOOKBEHIND` index was re-verified in the same run against
`la_oracle.py`'s own three-cell guard (3 / 0 / 2 for `(?<=abc)x` / `abc` /
`(?<=ab)x`), which is what separates it from `MINLENGTH`.

**So the prescription fails in two directions at once.** Set the `A_CLASS` arm
of `pcrec_maxw` to 4 (UTF-8's maximum code-unit length) and:

- `la_widths` tests `pcrec_minw(branch) == pcrec_maxw(branch)`. `minw`'s
  identical-looking arm stays at 1 (it is an under-estimate, its safe side —
  the row says so). So **every** class branch reads `1 != 4` and refuses.
  `(?<=a)x` — a pure-ASCII lookbehind that works today — would stop
  compiling under `--encoding=utf8`.
- Nothing is gained even in principle, because `k` is handed to `back_step`
  as CHARACTERS. The number the analysis must produce was never a byte count.

**THE POPULATION THAT MAKES THIS CONCRETE.** **MEASURED**
(`out/width.txt` §3) — every body below is accepted by 10.46 as fixed-width
(MAXLOOKBEHIND 1) and has more than one observed byte width:

| body | maxlb | byte widths observed |
|---|---|---|
| `[a\x{3b1}]` | 1 | 1, 2 |
| `.` | 1 | 1, 2, 3, 4 |
| `[^a]` | 1 | 1, 2, 4 |
| `\w` | 1 | 1, 2 |
| `\p{L}` | 1 | 1, 2, 4 |
| `[\x{0}-\x{10FFFF}]` | 1 | 1, 2, 4 |
| `(?i)s` | 1 | 1, 2 |
| `(?i)[a-z]` | 1 | 1, 2 |

**6 of 6** plain bodies are variable-byte-width, and the two caseless rows are
the same phenomenon arriving through §4.2(c)'s fold closure.

**THE RESOLUTION.** Two quantities, because there are two consumers asking
different questions.

> **REWRITTEN AT r54 (MUST-FIX E3).** The first version's resolution was right
> about the SHAPE and wrong about three concrete things, and one of them
> reverses a claim: it said `minw`/`maxw`'s *"real consumer is `[M4.6d]`'s MRL
> pruning"*. **`pcrec_maxw` has no MRL consumer and never had one.**
> §5.6.2 is the census. The other two are the callgraph memo fields the
> character pair needs (§5.6.3) and the fact that the width rule has had TWO
> TIMINGS since `[DD-14.LB]` and the first version moved one of them
> (§5.6.4).

#### 5.6.1 `pcrec_minw` stays, in BYTES, and becomes exact per class

**Unchanged from the first version and its consumer census holds.**
`pcrec_minw` has seven live callers, verified by grep at this tree:
`src/gen/emit_vm.c:4845`, `:5420`, `:5553`, `:5677`, `:7495`, `:8511` — the
MRL prune's own sites — plus `src/opt/select_engine.c:653`
(`prefilter_lang_nullable`), plus `src/opt/callgraph.c:775`'s fixpoint that
serves them. It genuinely wants BYTES ("how many subject bytes must any
accepting continuation still consume"), and under UTF-8
`minw(A_CLASS)` = the minimum encoded length over the class's intervals is
**exact** where today's constant `1` is a sound under-estimate. The MRL bound
gets *tighter* for a non-ASCII class. Its safe direction (down) is unchanged,
and its arena zero stays sound.

#### 5.6.2 `pcrec_maxw`'s WHOLE CHAIN RETIRES (r54 E3(a))

**MEASURED by grep**, and it is the finding that changes the shape of this
section. `pcrec_maxw` has exactly **three** call sites in the tree:

| site | what it is |
|---|---|
| `src/parse/mod_lookaround.c:298` | `la_widths`, per top-level branch — **the rule §5.6 is moving** |
| `src/parse/mod_lookaround.c:309` | `la_widths`, the whole body — **the same rule** |
| `src/opt/callgraph.c:795` | the `maxw` fixpoint, which exists **only** to publish `u.call.maxw` for the arm those two read |

Every other occurrence in `src/` is a COMMENT (`emit_vm.c:6128`, `:6152`,
`internal.h`'s field documentation, `mrl.c`'s own header) or `mrl.c`'s
internal recursion. **So once `la_widths` moves to the character pair,
`pcrec_maxw` has no reader at all** — and neither does anything downstream of
it: `u.call.maxw`, `u.call.maxw_known`, `cg_maxw_publish`, the fixpoint at
`callgraph.c:786-800`, and sabotage row `S171`
(`tests/mech/sabotages/S171_maxw_fixpoint_one_round.sh`).

**D77 says a mechanism with no consumer does not stay.** But the honest move
is not deletion, because the character pair needs a fixpoint of exactly this
shape for exactly this consumer:

> **`maxw`'s fixpoint is RE-AIMED, not retired.** Its recurrence changes from
> bytes to characters and it becomes `cwmax`; `u.call.maxw`/`maxw_known`
> become `u.call.cwmax`/`cwmax_known`; `S171` keeps its row and re-points its
> `SAB_FILE` at the renamed fixpoint. `pcrec_maxw` the FUNCTION — `mrl.c`'s
> byte-maximum recurrence — is what actually goes, along with its header's
> claim to a consumer it does not have.

**The net cost is therefore much smaller than the panel's count**, and the
difference is worth stating because it changes whether this is a big change:
not *"two more fixpoints and two more memo fields"* on top of what exists, but
**one new fixpoint (`cwmin`) and one new memo field**, with the `maxw` pair
renamed and re-recurred in place.

| | today | after |
|---|---|---|
| callgraph fixpoints | `minw`, `maxw` | `minw` (bytes, MRL), `cwmin` (chars, **new**), `cwmax` (chars, **re-aimed from `maxw`**) |
| `A_CALL` memo fields | `minw`, `maxw`, `maxw_known` | `minw`, `cwmin` (**new**), `cwmax`, `cwmax_known` (**renamed**) |
| sabotage rows | S171 | S171 (**re-pointed**) + S-U10 (§8.2, the `cwmin` fixpoint's own round bound) |

#### 5.6.3 The character pair, and its arena-zero obligation (r54 E3(b))

`pcrec_cwmin`/`pcrec_cwmax` are a new pair over the same AST, identical in
shape to `mrl.c`'s (same saturating arithmetic, same `default:`-less
exhaustive switch — `mrl.c:18-24`'s rule, so a node kind added later is a
compile error here). The `A_CLASS` arm answers **exactly 1 in every
encoding**, because a class is one character by definition, and that is what
makes §5.6's whole population table compile.

**THE OBLIGATION THE FIRST VERSION DID NOT DISCHARGE**, and
`internal.h:934-963` states it for `maxw` in terms that transfer verbatim:

> *"`pcrec_maxw`'s safe direction is the OPPOSITE of `minw`'s, so a plain
> `long long maxw` whose arena zero is `0` would be its SILENT MISCOMPILE — an
> under-estimated maximum lets a variable-width branch through the lookbehind
> rule as fixed, which on a NEGATIVE lookbehind is a false match."*

The arena zeroes every allocation, so a memo field's zero is the answer any
walker legitimately running before the fixpoint sees. Therefore:

| field | safe direction | arena zero is | shape |
|---|---|---|---|
| `u.call.cwmin` | DOWN (under-estimate is free) | `0` — sound | **one** `long long` |
| `u.call.cwmax` | UP (over-estimate is free; under-estimating is a false match on `(?<!`) | `0` — **an under-estimate, UNSOUND** | **two** fields: `cwmax` plus `cwmax_known`, and the arm reads `cwmax` ONLY through it |

This is not a new pattern, it is `maxw`/`maxw_known`'s own, and the reason it
transfers exactly is that the consumer is the same consumer. `cwmax_known`
false means "answer `PCREC_W_UNBOUNDED`", which is what `la_widths` already
treats as "refuse this body" — so a walker running before the fixpoint gets
the refusal, never a false fixed-width verdict.

#### 5.6.4 BOTH TIMINGS MOVE TOGETHER (r54 E3(c))

**ACCEPTED, and it was a real gap.** Since `[DD-14.LB]` the width rule is
asked **twice**, and `src/parse/mod_lookaround.c:319-338` is the comment that
says so — *"§2.5's REFUSAL SENTENCE — ONE HOME, TWO TIMINGS"*:

1. **the parse hook**, `la_widths` inside the `(?<` doorway, which owes an
   `ExtResult`; and
2. **`pcrec_postresolve`** (`compile.c:999`), which re-asks it for a
   lookbehind body containing a subroutine call, because `maxw`'s `A_CALL` arm
   cannot answer until `pcrec_callgraph_build` (`:961`) binds the callee, and
   which calls `ctx_fail`.

The two *"must produce the SAME BYTES"*, and the file's own comment explains
that this is byte-identical **by construction and not by transcription** —
the doorway epilogue is `ctx_fail(cx, r->at, "%s", r->msg)`, so `REFUSE(at,
"%s", buf)` and `ctx_fail(cx, at, "%s", buf)` render the same string through
the same formatter, and the three-arm ORDER (unbounded first) is part of the
rule rather than of either caller.

> **So the move is to the RULE, not to a call site.** Both timings switch to
> `cwmin`/`cwmax` in the same change, the shared refusal text is unchanged
> (the rule's WORDING is about fixed-vs-variable width, which is still what it
> refuses), and the three-arm order is untouched. Moving one timing and not
> the other would make a lookbehind containing a call refuse differently from
> one that does not — the exact divergence `[DD-14.LB]` built this structure
> to prevent.

**And S-U4's sabotage gets sharper for it** (§8.2): "point it back at
`pcrec_maxw`" must be applied at **one** timing, so the row detects the
divergence between the two paths as well as the refusal itself. A row that
sabotaged both would be detected by any `(?<=[a\x{3b1}])` cell; a row that
sabotages one is detected only by a cell whose lookbehind body carries a
call, which is a population the corpus must be told to contain.

#### 5.6.5 Why this is coherent with §2.1.2's forced position

This is the join between the two BLOCKING findings, and it is the reason
§2.1.2's position works at all.

**Both timings run BEFORE the lowering**, and they must:

```
 :901   pcrec_parse            → the parse hook's la_widths runs in here
 :961   pcrec_callgraph_build  → the cwmin/cwmax fixpoints run here
 :999   pcrec_postresolve      → the second timing runs here
 :1000  pcrec_lower_enc        ◄── the lowering
```

**After `:1000` a character is not a node.** A two-byte character is an
`A_CAT` of two byte classes, so a character-width walk over a lowered tree
would answer 2 where the truth is 1 — and it would do so *plausibly*, which is
the worst kind of wrong. Constraint 3 of §2.1.2 IS this fact, and §5.6 is
where it comes from.

**This also disposes of the tempting alternative.** One could imagine lowering
immediately after the parser (§2.1.2 shows why `callgraph_build` forbids it)
and having the lowering STAMP each lowered character's width onto its node so
`cwmax` could recover it. That is a marker node or a shadow field carrying a
fact the tree used to hold structurally — a parallel mechanism, and one whose
failure mode is a wrong lookbehind width, which on `(?<!` is a false match.
**The position that avoids it is free**, so the design takes the free one.

**Why this is not two sources for one fact.** `minw` (bytes) and
`cwmin`/`cwmax` (characters) are two different facts with two different
consumers. Under `--encoding=byte` they are numerically equal, and §8.1's
identity gate is what proves the byte-encoding answers did not move. The
alternative — one parameterised `pcrec_width(a, UNIT_BYTES|UNIT_CHARS)` — is
**declined** on `mrl.c`'s own argument: an exhaustive switch per analysis is
the alarm that fires when a node kind is added, and a unit parameter threaded
through every arm makes each arm answer two questions where today it answers
one. §10 keeps this open for Frank if he disagrees.

**A consequence worth pricing.** The `end-check` the emitter emits on both
lookbehind arms (`[M6.6.2]` wave D, ASK 2's ruling) keeps working and gets
**more** valuable: it is the runtime evidence that the character analysis
agrees with what the emitter did, and under UTF-8 it stops being redundant —
which `emit_vm.c`'s own note 3 predicts in those words. §5.2.1 is the other
half of that sentence: the end-check only stops being a **trap** once
`back_step` validates declared length, so E3 and E4 are one change, not two.

---

## 6. Engine and selection consequences (charter (v))

### 6.1 State counts — answered in §2.4

No blowup. Largest measured minimised DFA is 332 states (`\w` under UCP)
against a 10,000-state computed-goto cap and a 32,000-state table cap.
`.*` under UTF is 9 states.

### 6.2 UTF-8 artifacts are DFA-eligible on day one

**ARGUED** from §2.3 and §2.4, and the argument is short because the
construction makes it short: **the lowering emits nodes the IR already has.**
A byte-range class is an `N_CLASS`; a sequence is a concatenation; a set of
sequences is an alternation. Subset construction, Hopcroft minimisation, the
`eqclasses` partition, both emitters and every optimisation pass see exactly
what they see today.

So the answer to "DFA-eligible day one or VM-first" is **day one, and not as a
choice**. The one thing that *would* force the VM by CONSTRUCT is `\X`
(grapheme clusters), which is module `misc` and out of scope (§11).

#### 6.2.1 Re-derived under §2.1.2's forced position (r54 E1)

The conclusion above survives, and under the forced position it gets a
**better reason than the one the first version gave** — plus one exception the
first version's reason concealed.

**The better reason: engine selection never sees the lowering's output at
all.** `pcrec_select_engine` runs at `compile.c:988`, the lowering at `:1000`,
so selection reads the CODE-POINT tree — which is structurally the same tree
as today (the same `A_CLASS`/`A_CAT`/`A_ALT`/`A_REP` kinds, differing only in
one node's payload). The forcing analyses `forces_captures` and
`forces_registry` read node kinds and registry rows, and the lowering
introduces neither, so their verdicts are **byte-identical to today's on every
pattern** — which is stronger than "the lowering emits nodes the IR already
has", because it does not depend on the lowering's output being benign. It
depends on selection not having run yet.

**THE EXCEPTION, which is my own finding against §6.2's first version.** It
said *"there is no mechanism by which an encoding could make a pattern
VM-only."* **There is one, and `[SEL-1]` is it.**
`forces_dfa_overflow` (`src/opt/select_engine.c:356`, in the same fixpoint at
`:396`) excludes `ENGM_DFA` when a DFA build has already overflowed a state
cap, and `compile.c:1000`'s comment records the retry. That path reads a
MACHINE SIZE, and a machine size is exactly what the encoding changes. So:

> Under `--encoding=utf8` a pattern whose lowered DFA exceeds
> `PCREC_MAX_DFA_STATES_TABLE` (32,000) falls back to the VM through
> `[SEL-1]`'s retry — **a pattern that is DFA-compiled under `byte` and
> VM-compiled under `utf8`, decided by the encoding.** The claim "the encoding
> cannot change the engine" is false; the true claim is "the encoding cannot
> change the engine *except through size*, which is `[SEL-1]`'s existing and
> already-designed path."

**This is not a defect** — `[SEL-1]` exists precisely to make a cap overflow a
selection outcome rather than a refusal, and the fallback is correct. It is a
**consequence that must be stated**, for two reasons. It means §6.1's "no
blowup" and §2.4.1's entries table are not merely comfort: they are the
argument that this path is rarely taken. And it means a UTF-8 artifact's
`RX_ENGINE_WHY` stamp can read `dfa_overflow` where the same pattern under
`byte` reads otherwise, which stage 2's acceptance should **expect** rather
than treat as a regression. §8.1.1's check 3 is the census that measures how
often it happens; **P-5 is refuted-or-confirmed by exactly that number.**

### 6.3 The prefilter: is `memchr` on a lead byte still sound?

**The soundness argument is one line and does not mention UTF-8.** The
prefilter derives a set of bytes any match can START with, from the automaton
pcrec built. Under UTF-8 that automaton's start states are lead-byte ranges.
The derivation is unchanged and its output is correct **by construction**,
because it reads the machine rather than the pattern. There is no
"superset" step to justify: it is the same computation on a different machine.

**AND THE PREMISE THAT MAKES IT USEFUL HAS A NAME (r54 E11).** The argument
above establishes that the filter is SOUND. It does not establish that it is
worth running, and the property that does is **self-synchronization**: in
UTF-8, **a lead byte or an ASCII byte never occurs in the middle of a
character** — the two ranges are disjoint (`0x00-0x7F` and `0xC2-0xF4` for
leads, `0x80-0xBF` for continuations). So a candidate-start scan that finds a
lead byte has found a real character boundary, and it can never be led to a
mid-character position that a subsequent scan has to re-synchronise from.

**This is worth writing down because it is the property the SEAM exists for,
and the next backend does not have it.** UTF-16 is not self-synchronizing in
the byte sense: a high surrogate's second byte can equal a low surrogate's
first, so a byte-level scan can land inside a code unit and a byte-oriented
prefilter is unsound there without an alignment argument this design never
has to make. `[DD-12] (6)` rules UTF-16 out and §11 keeps it out — but the
reason a UTF-8 backend gets the prefilter for free is a property of UTF-8, not
a property of "encodings", and a future reader porting this section to a third
backend must re-derive it rather than inherit it. **STRUCTURAL** (the byte
ranges are the encoding's definition), and it is the one premise of §6.3 that
does not survive a change of encoding.

What changes is the filter's **quality**, and that is measured
(`out/sizing.txt`, lead-byte column):

| class | lead bytes | consequence |
|---|---|---|
| `[α-ω]` | **2** (0xCE, 0xCF) | excellent filter; but `memchr` takes ONE byte, so the single-byte arm declines and the bitmap-skip arm takes it |
| `\p{Lu}` | 47 | a usable bitmap filter |
| `\p{L}` | 97 | weak |
| `.` | 178 | useless — but `.` is useless under the byte encoding too |

**The finding for the design is the first row**: a two-byte lead set is a
*strong* filter that the current `memchr` arm cannot use, because `memchr`
takes a single byte. The `byte-class` bitmap arm handles it (`RX_DFA_SCAN`'s
measured five values, D81), so nothing is broken — but a two-value scan is a
real optimisation opportunity that UTF-8 makes common where the byte tier made
it rare. **Recorded, not built** (D77): the measurement that would trigger it
is a throughput comparison of `memchr`-on-one-byte versus a two-value scan on
a UTF-8 corpus, and that corpus does not exist until stage 2.

**`[OPT-K]`'s offset-k skip gets better, and for free.** A 2-byte character's
second byte is a continuation byte in `80-BF`, so a UTF-8 pattern starting
with a specific non-ASCII character has an *exact* byte at offset 1 — the
richest possible input for that mechanism. **ASSERTED**; same trigger.

### 6.4 The VM's cost and capacity axes (r54 SHOULD E8)

**ACCEPTED, and this section is new.** §6 priced the DFA and said nothing
about the VM, which E1 has just made the more urgent half: the VM emitter is
handed the lowered AST directly (`compile.c:1228`), so **the lowering's output
shape is the VM's input shape**, and §2.4.1's alphabet argument does not
transfer — the VM has no alphabet, it has nodes and frames.

**WHAT THE LOWERING HANDS THE VM.** A class becomes an `A_ALT` of `A_CAT`s of
byte classes: §2.4's own table gives the alternative counts —
`.` and `[^a]` are **10-way**, `[\x{100}-\x{10FFFF}]` is **8-way**, `\p{L}` is
**786-way**, `\w` under UCP is **1,056-way**. Where the byte tier gave the VM
one `A_CLASS` node, UTF-8 gives it an alternation.

| axis | cap / cost | consequence, and its mark |
|---|---|---|
| `PCREC_MAX_VM_NODES` | 131,072 nodes | a `\p{L}` class alone is ~2,600 nodes unshared (§2.3.1's naive column). **2.0%** — comfortable alone, and the term to watch is the product below. **ARGUED** from §2.3.1 |
| `PCREC_MAX_VM_REPEAT_COPIES` | 64 copies | unchanged: it counts ITERATIONS of a bounded repeat, not the body's size. **STRUCTURAL** |
| `PCREC_MAX_VM_REPLICATION_PRODUCT` | 131,072 (a literal alias of `MAX_VM_NODES`, `limits.def:143`) | **this is the one that moves.** The product is body-nodes × copies, so a `\p{L}`-bodied bounded repeat multiplies a ~2,600-node body: `\p{L}{2,4}` is a quantified 786-way alternation and **`\p{L}{1,50}` crosses the cap** at ~50 copies where an ASCII class would cross at ~43,000. **ARGUED**; K22's shape, one class wider |
| `vm_alt` resume frames | `VM_DEFAULT_RESUME_FRAMES` / `VM_DEFAULT_TRAIL_FRAMES` 3072 | **a byte-sequence alternation is DETERMINISTIC on its first byte** — the lead-byte ranges of the decomposition's alternatives are disjoint by construction — so `[ENG-ISL]`'s trie walk resolves it in one path and pushes at most one frame (`alt_dispatch_study.md` §3.2). **ARGUED**, and it is the reason this row is not the disaster the 786 suggests |
| `vm_cost`'s charge | selection input | 786 alternatives read as 786 branches by a cost model that has never seen one. **ASSERTED** — this is the row most likely to be wrong |

**THE TWO INTERACTIONS THE PANEL NAMED, each answered.**

**`[ENG-ISL]`'s island predicate.** Its predicate is *"does this alternation's
whole subtree match a finite set of literal byte strings"* (the LANGUAGE form,
which `isl1_report.md` §2.2 records was chosen after the per-branch form
measured wrong). **A lowered class is exactly that** — a finite set of literal
byte strings, by construction — so **every lowered non-ASCII class becomes an
island**, and the trie walk is what makes the frame row above benign. This is
the happiest interaction in the milestone and it is also **the one to
distrust**: `[ENG-ISL]`'s own landing found a build that stamped eleven
islands, fired on nothing, and grew the artifact 3.0% while passing every
answer check. §8.1.1's check 3 reads the `RX_VM_ISLANDS` stamp for that
reason.

**`possessify`'s (U1)/(U2) verdicts** are §2.5.1 row 4/5's **DECLINE**, so
they are unaffected here: a non-ASCII class never reaches the island question
with a possessification verdict attached, because possessify ran before the
lowering and declined. Under `--encoding=byte` nothing changes at all.

**WHAT THIS SECTION DOES NOT DO, deliberately.** It does not propose a cap
change, a cost-model change or an island-predicate change. Every row above is
**ARGUED or ASSERTED**, none is measured, and the measurement that would
settle all five is the same one §2.5.1 and §6.3 already owe: a form and stamp
census over a UTF-8 corpus, which does not exist until stage 2. **D77 applies
to this whole section**: it is written so the implementation wave knows where
to look, not so it can build against it. §8.1.1's check 3 is the census, and
§12 gains **P-10**: no corpus pattern's VM artifact crosses
`PCREC_MAX_VM_REPLICATION_PRODUCT` under `utf8` that does not cross it under
`byte`. Refuted by one, and the `\p{L}{1,50}` row above predicts it will be.

---

## 7. The oracle plan (charter (vi))

### 7.1 The D27 goal-facts list

**MEASURED** (`out/divergence.txt`): 28 cells, each in four columns —
libpcre2 at `PCRE2_UTF`, at `PCRE2_UTF|PCRE2_UCP`, python `re` over `str`, and
python `re` over `bytes`.

**The four-column structure is itself the finding.** python has one engine per
subject type and PCRE2 has two UTF modes, so "python vs PCRE2" is not one
comparison. `\w` over a Greek letter is FALSE in python-bytes, FALSE in
PCRE2/UTF, and TRUE in both python-str and PCRE2/UTF|UCP. **A corpus author
told only "python disagrees" would mark the wrong cells.**

Verdict tally over the 28 rows: **10 PCRE2-ONLY, 8 UCP-SPLIT, 5 PY-STR-ONLY,
5 ALL-AGREE.** Twenty-three of twenty-eight are not all-agree, against the
charter's "at least 10".

**The list the blinded author gets** (the design's §7 extract, cut at cell
level):

| verdict | count | what the author does |
|---|---|---|
| `PCRE2-ONLY` | 10 | mark `# pcre2-only`; libpcre2 rules the cell. These are `\p{...}`, `\x{...}`, `\X`, `\R`, class ranges over non-ASCII, quantified multi-byte characters, an ill-formed subject — **python `re` cannot express the syntax at all**, which is a stronger reason than "disagrees" |
| `UCP-SPLIT` | 8 | `\w \d \s \b \W` over non-ASCII. **pcrec has no UCP axis** (§4.5), so the corpus must state which semantics it expects — pcrec's answer is the non-UCP column, and **python `re` over BYTES is the arbitrating oracle; see §7.1.1** |
| `PY-STR-ONLY` | 5 | `.`, `.{2}`, `[^a]` over multi-byte characters, caseless LONG S. python's `str` engine is the right oracle; **the suite's `bytes` engine is not** |
| `ALL-AGREE` | 5 | write the cell, python verifies it |

**The `PY-STR-ONLY` row is the one that changes test infrastructure**, and it
is why §7.4 exists: the suite's python oracle today compares bytes, which is
correct for the byte tier and wrong for the UTF tier on 5 of 28 measured
cells — silently, in the direction that loses the oracle (R32 C3's shape).

#### 7.1.1 The UCP-SPLIT rows' ARBITRATING ORACLE (r54 MUST-FIX C8)

**ACCEPTED, and the table above already contained the answer.** The
`UCP-SPLIT` row said what pcrec's answer IS (the non-UCP column) and named no
oracle to check it against — the one shape R32 C3 exists to prevent, and the
panel is right that leaving it would be its third recurrence.

**THE ORACLE IS PYTHON `re` OVER `bytes` ON SEVEN OF THE EIGHT ROWS, AND THE
EIGHTH IS THE INTERESTING ONE.** The panel's evidence pointed at python-bytes
and it was right; **working the whole column rather than the cited example
found one row where it is wrong**, and the reason it is wrong generalises.

`out/divergence.txt` lines 54-63, every `UCP-SPLIT` row, `py/bytes` against
`pcre2/UTF` — the non-UCP column, which is pcrec's semantics (§4.5):

| cell | `pcre2/UTF` = pcrec | `py/bytes` | |
|---|---|---|---|
| `\w` over a Greek letter | no | no | ✓ |
| `\w` over an Arabic-Indic digit | no | no | ✓ |
| `\d` over an Arabic-Indic digit | no | no | ✓ |
| `\s` over NBSP U+00A0 | no | no | ✓ |
| `\s` over U+2028 line sep | no | no | ✓ |
| `\b` before a Greek letter | no | no | ✓ |
| **`\b` between ASCII and Greek** | **MATCH(0,3)** | **MATCH(0,3)** | ✓ |
| **`\W` over a Greek letter** | **MATCH(0,2)** | **no** | **✗** |

**7 of 8.**

**THE SEVENTH ROW IS WHY THE SEVEN ARE A RESULT AND NOT A COINCIDENCE.** Six
of the agreeing cells are `no` on both sides, and an oracle that simply
refused everything non-ASCII would score six. `\b` between ASCII and Greek is
the **discriminating** one: the non-UCP answer is MATCH and the UCP answer is
`no` — the opposite direction from every other row — and `py/bytes` gives
MATCH. So it is tracking the non-UCP SEMANTICS, not exhibiting a bias that
happens to agree. **That row is the control**, and a corpus that drops it
loses the evidence for this ruling; §8.3 pins it by name.

**THE EIGHTH ROW FAILS FOR A UNIT REASON, AND THE UNIT REASON IS THE WHOLE
POINT OF THIS MILESTONE.** `\W` over `α` (`CE B1`):

- **PCRE2/UTF** — and pcrec under `--encoding=utf8` — asks "is this
  CHARACTER a non-word character", answers yes, and **consumes both bytes**:
  `MATCH(0, 2)`.
- **python-bytes** asks "is this BYTE a non-word byte", answers yes for `0xCE`,
  and consumes **one** byte; against the probe's anchored `^\W$` that leaves
  `0xB1` unmatched, so the cell reads `no`.

The two agree perfectly on the PREDICATE (α is not a word character) and
disagree on the UNIT. **python-bytes has no character notion at all**, so it
can verify a UCP-SPLIT cell exactly when the cell's answer does not depend on
one class consuming a multi-byte character.

**AND `py/str` DOES NOT RESCUE IT** — the same row reads `no` there too, for
the opposite reason: python's `str` engine gives `\w` Unicode semantics, so α
IS a word character and `\W` does not match at all. **Neither python engine
gives pcrec's answer on this cell.**

**SO THE RULE THE BLINDED AUTHOR GETS IS A PREDICATE, NOT A VERDICT LABEL:**

> A `UCP-SPLIT` cell is **python-verifiable through the `bytes` engine** — and
> must NOT be marked `# pcre2-only` — **unless the expected answer is a MATCH
> that consumes a multi-byte character.** Those cells are `# pcre2-only`:
> `\W`, `\D`, `\S` and `[^…]` over non-ASCII. The complemented forms, in other
> words, and only when they match.

**THIS IS A FINDING AGAINST §7.1's OWN TAXONOMY**, and the design states it
rather than patching one row. **The verdict column and the oracle column are
different partitions.** `VERDICT` answers *"which engines' semantics diverge
here"* — an engine-comparison question, computed by the probe. `ORACLE`
answers *"who can check pcrec's expected answer"* — a corpus-authoring
question, and it depends on the UNIT each candidate oracle counts in, which no
verdict label carries. The `\W`-over-Greek cell is `UCP-SPLIT` by verdict and
`PCRE2-ONLY` by oracle, and the first version's table let the label imply the
oracle. **`PY-STR-ONLY`'s own row already contained the same phenomenon** —
it lists *"`[^a]` over multi-byte characters"*, which is `\W`'s cell one
spelling over — and nothing connected the two.

`probe_divergence.py` computes the verdict from the columns, which is right,
and **it does not compute an oracle**; §8.3.1's extract carries the predicate
above in prose, and §7.4's third `.rxt` oracle value (ASK 6) is where this
eventually becomes machine-checked rather than a rule an author applies by
hand.

**THE ONE THING THIS DOES NOT SETTLE**, stated so nobody reads it as more than
it is: the oracle confirms pcrec's answer is *self-consistent with the
non-UCP definition*. It does not make the non-UCP answer the RIGHT one for a
user who wanted UCP — that is §14 ASK 4, and no oracle decides it.

### 7.2 The python version is itself an axis

**MEASURED**, and it is a hazard nobody had named. The suite's oracle is
"python3 `re`" with no version pinned, and the two machines this project uses
do not carry the same one:

| box | python | `unicodedata` |
|---|---|---|
| old box (the reference oracle's home) | 3.14.4 | **16.0.0** |
| this Mac | 3.11.4 | **14.0.0** |

libpcre2 10.46 is Unicode **16.0.0** (`out/uprops.txt` §0, derived by sweeping
`pcre2_config_8` slots rather than guessed — the method
`pcre2_ctypes.py` used for `PCRE2_CONFIG_VERSION`, forced by this box having
no `pcre2.h`).

So on the old box the python oracle and the PCRE2 oracle share a Unicode
version, and **on this Mac they do not**.

**THE OBVIOUS ALARM WAS RUNG AND IT DID NOT SOUND, WHICH IS THE HONEST
RESULT.** The whole 28-row divergence table was re-run under python 3.11 /
Unicode 14.0.0 (`out/divergence_local_py311.txt`) and compared row by row
against the 3.14 / 16.0.0 run: **the two are identical, cell for cell, on all
28 rows.** So the version axis, real as it is, does **not** move any cell in
§7.1's list, and this section must not imply that it does. The rows were
chosen for engine-semantic divergence (`\w` under UCP, `.` over multi-byte,
syntax python lacks), and none of them sits near a code point whose properties
changed between Unicode 14 and 16.

**Where the version axis IS live is §3.3's tables**, and there it is
quantified rather than feared: `\p{L}` is **648** intervals under Unicode
14.0.0 and **677** under 16.0.0. That is a property-DATA question, which is
why ASK 2 pins a version for the vendored UCD files and why §3.3's census is
swept from the oracle rather than from python.

**The design's requirement is therefore narrower than it first appears**, and
§8 makes it a check rather than a note: any generator that derives `\p`
membership records the `unicodedata.unidata_version` it ran under and the
verifier **fails loudly** on a mismatch — the same skip-loudly convention PC-3
uses for a missing libpcre2. Generators that only exercise engine semantics
need no such pin, on this measurement.

### 7.3 The PC-4 oracle twin

`[DD-12] (4)` names it and carries R13/R14's warning verbatim: *a UTF sweep
needs generators that can PRODUCE multi-byte constructs, or it counts the
generator.* The design has nothing to add to that warning and repeats it
because it is the failure this lane's own sizing sub-lane nearly made in a
different form. Concretely, the UTF twin of PC-4 must generate: multi-byte
literals, classes with non-ASCII endpoints, classes spanning the 1-byte/2-byte
boundary (`[a\x{3b1}]` — the §5.6 shape), `\p{...}` bodies, caseless
non-ASCII, and subjects containing characters of all four encoded lengths. An
ASCII-only generator run under `--encoding=utf8` would report a clean sweep
over patterns whose UTF-8 lowering is the identity.

### 7.4 `.rxt` encoding directives — flagged, not written

The charter says to flag rather than write, and the flag has three parts:

1. **A per-block `encoding` directive** is needed, because the encoding is a
   per-compile scalar and a corpus must exercise both.
2. **The oracle-selection line needs a third value.** Today a block is
   python-verifiable or `# pcre2-only`. §7.1 measures a **third** state:
   python-verifiable *but only through the `str` engine*. `docs/spec/
   rxt_format.md` needs a design note for it, and getting it wrong is silent.
3. **Subject bytes**: a `.rxt` subject line must be able to carry arbitrary
   bytes including ill-formed sequences (§2.6's cells are exactly the tests
   worth writing). Whether today's escape vocabulary covers that is a
   question for the format's owner, not this lane.

`docs/spec/rxt_format.md` is not edited by this lane. §14 ASK 6 routes it.

---

## 8. The validation plan (charter (vii))

### 8.1 The identity gate

**The module's no-op proof**, on the `[M6.6.2]` wave-0 and `[M6.5]` precedent:
every artifact pcrec emits under `--encoding=byte` (the default) is
**byte-identical** to what the pinned pre-M5 binary emits, over the whole
corpus, on four axes: default, the standard second, `-fno-prefilter`, and
`--no-captures`.

**This gate is doing more work here than in any previous module**, and the
reason is §2.2: this milestone changes the **class representation**, which
every pattern in the corpus goes through. A lookaround module touches patterns
containing lookaround; this touches every pattern that contains a character.
The gate is therefore the primary instrument, not a formality.

**The positive control** — the half that can actually fail — is that the
pinned pre-module binary **refuses** every pattern the new corpus adds
(`-e utf8`, `\p{...}`, `\x{...}`), which `out/premises.txt` §1/§2 already
records as the current behaviour.

**A stated gap.** The gate cannot cover the `--encoding=utf8` artifacts,
because there is no prior binary to compare them against. Those are covered by
the corpus and the differential, not by identity. Saying so is the point:
`[M6.6.2]` wave E's identity gate caught a 37-byte generated-comment
regression precisely because its scope was known.

### 8.2 The sabotage rows

One per load-bearing claim, following D69's shape. **ASSERTED** list, with the
failing direction each needs:

| # | claim | sabotage | why only this instrument sees it |
|---|---|---|---|
| S-U1 | the fold is applied BEFORE negation (§4.3) | swap the order in the one constructor | both orders produce case-closed sets; only behaviour on `[^k]`/U+212A differs |
| S-U2 | the fold is a CLOSURE, not a pairing (§4.2a) | replace the closure with one round of "add the partner" | `k`↔`K` still works; only U+212A fails |
| S-U3 | the fold happens on CODE POINTS, before lowering (§4.2c) | move it after the byte lowering | `[a-z]` still folds to `[A-Z]`; only U+212A/U+017F are lost |
| S-U4 | `la_widths` uses CHARACTER width (§5.6) | point it back at `pcrec_maxw` | every ASCII lookbehind still compiles; only `(?<=[a\x{3b1}])` refuses |
| S-U5 | `back_step` walks characters (§5.2) | make it `pos - k` | identical under `byte`; under utf8 it lands mid-character |
| S-U6 | `next_pos` finds a boundary (§5.1) | make it `pos + 1` | only a find-all over an empty match on a multi-byte subject sees it |
| S-U7 | the surrogate range is excluded from every lowered set (§2.3) | include it | only a subject containing a CESU-8-shaped sequence sees it |
| S-U8 | `minw`/`maxw` are per-class exact (§5.6.1) | return the old constant 1 | answers unchanged (a looser bound is sound); only the MRL stamp moves |

**S-U8 is the one worth noticing**: it changes **no answer**, because a looser
MRL bound prunes less and can never delete a match. Only a structural or
stamp-reading check can see it — the S68 shape, and the reason the design
names it rather than assuming the corpus covers it.

### 8.3 Population sizing for the blinded corpus

**ASSERTED**, sized from the measured surfaces rather than guessed:

| axis | cells | source |
|---|---|---|
| encoded-length coverage (1/2/3/4-byte characters × literal/class/quantified/negated) | ~64 | §2.3 |
| the 1-byte↔multi-byte class boundary (`[a\x{3b1}]` shapes) | ~24 | §5.6's population |
| invalid UTF-8 (9 ill-formed kinds × before/after/through) | ~27 | `out/invalid_utf.txt` |
| `\p{...}` general categories (37 accepted spellings × 2 polarities × in/out members) | ~150 | `out/uprops.txt` §1 |
| `\p` refusals (30 measured error-147 bodies + blocks) | ~34 | `out/uprops.txt` §1 |
| caseless: 1:1 pairs, cross-block folds, the closure, fold-before-negate | ~60 | `out/caseless.txt` §1/§3/§4 |
| caseless 1:n NON-matching (the §4.1 result as tests) | ~11 | `out/caseless.txt` §2 |
| lookbehind over variable-byte-width bodies | ~24 | `out/width.txt` §3 |
| `next_pos` / find-all over multi-byte subjects | ~20 | §5.1 |
| the byte-encoding control arm (every above pattern under `-e byte`) | mirror | §8.1 |

**~420 cells**, comparable to `lookaround`'s 457 blocks / 1,819 cases. The
D27 author gets an extract of §2.6, §3.1, §4.1–4.3, §5.6 and §7.1 — the
construct table, the measured semantics and the oracle rules — and **not**
§2.3, §5, §8 or §9, which are the implementation.

### 8.4 The compatibility question the cross-note names

The `[M5.0]` row asks this design to own the `maxw` change. §5.6 owns it, and
the **compatibility** half is: under `--encoding=byte`, `pcrec_minw` and
`pcrec_maxw` must answer **exactly what they answer today** for every pattern
in the corpus. That is not an argument, it is §8.1's gate — the MRL bound is
baked into emitted literals (`RX_PRUNE_*`), so a changed bound is a changed
artifact and the byte-identity gate fails. **The gate is the check; no
separate instrument is needed.**

---

## 9. Module and staging (charter (viii))

### 9.1 What is a module and what is not

**MEASURED** (`out/premises.txt` §1): pcrec's own refusal already rules this —
`encoding 'utf8' arrives with milestone M5 (**an engine axis, not a module**:
no `--features` name enables it)`.

| thing | kind | registry / gate |
|---|---|---|
| the UTF-8 **encoding backend** | an **encoding**, not a module | one `enc_utf8.c` + one row in `enc.c`'s table. `--encoding=utf8`. No `--features` name. |
| `unicode-props` (`\p` `\P` `\N{U+}` `\x{}`) | a **module**, already registered, `built = unbuilt` today | `--features unicode-props`; rows exist |
| the **fold** | **neither** | it is inside the one class constructor (D23). A module for it would be a second home for one rule. |
| `\X`, `\R` | module **`misc`** | measured, different module, out of scope (§11) |

**The third-encoding recipe is this milestone's own test**, and it is a
falsifiable prediction rather than a compliment: adding `enc_utf8.c` and its
row should touch **nothing** in `src/core`, `src/gen`, `cli/` or `lib/`.
§12 P-1 states what happens if it does.

**But the recipe does not cover the lowering**, and the design should be
honest that this is where DD-12 (7)'s "derailment signal" needs
interpretation. §2.1 puts the encoding lowering behind the same one-file-per-
backend rule; whether it lives in `src/gen/enc/` alongside the residual text
or in `src/ir/` behind a table of function pointers is an implementation
choice the panel should rule on. What is NOT negotiable is that no shared file
acquires an `if (enc == UTF8)`.

### 9.2 The staged landing order

Five stages, each with an acceptance that can be run before the next opens.

**STAGE 1 — the CharSet widening.** `A_CLASS` becomes intervals; every
producer (`\d`, `\w`, POSIX classes, ranges, literals) emits intervals; the
byte backend's lowering turns intervals back into the 32-byte bitmap.
`\x{...}` above 0xFF still refuses. **Nothing user-visible changes.**
*Acceptance:* §8.1's identity gate at 100% byte-identity on all four axes —
the whole corpus, since every pattern goes through this. This stage is a pure
refactor and its gate is total.

**STAGE 2 — the utf8 backend.** `enc_utf8.c` (four residual bodies), the
byte-sequence lowering, `\x{...}` above 0xFF under `--encoding=utf8`,
`-e utf8` starts compiling. §5.6's `pcrec_cwmin`/`pcrec_cwmax` land here
because lookbehind is already shipped and would otherwise be wrong the moment
utf8 compiles. *Acceptance:* the UTF `.rxt` corpus green; identity gate still
100% on `byte`; DD-12 (7)(a)'s **two M5-time structural checks** — hot-loop
shape identity ASCII-vs-UTF-8, and the second-backend validation of D58's
"revisit-when" names; S-U4/5/6/7 detected.

**STAGE 3 — `unicode-props`, general categories.** The UCD vendoring (§3.3),
the generated `.inc`, the category families of §3.4. **This stage does not
require stage 2** (§3.2) and could land in parallel; it is sequenced after it
only so that its corpus can test both encodings at once. *Acceptance:* PC-3's
name-axis sweep green; PC-4 differential over the category population; the
D65 `built` column flips for the `\p`/`\P` rows.

**STAGE 4 — DD-1, the fold closure.** `CaseFolding.txt`, the closure in the
one constructor, before negation. *Acceptance:* `out/caseless.txt`'s cells as
a corpus; S-U1/2/3 detected; the `byte` encoding's ASCII fold byte-identical.

**STAGE 5 — scripts and `Script_Extensions`.** Table weight only, no new
mechanism. *Acceptance:* PC-3/PC-4 over the script population.

**What is NOT staged, deliberately:** a UCP axis (§14 ASK 4), a word-class
seam entry (§5.4), `\X`/`\R` (module `misc`), UTF-16/32 (D18 earn-its-axis;
`[DD-12] (6)` already rules them out and no consumer asks).

---

## 10. What this design does NOT resolve

Stated plainly so the panel attacks the right things:

- **Whether `unicodedata`-free UCD vendoring is acceptable in this repo** —
  §3.3, ASK 2. Everything in §3.4 and §4.4 depends on the answer.
- **Whether pcrec may diverge from PCRE2's default UTF mode on ill-formed
  subjects** — §2.6, ASK 1. The design recommends yes and the recommendation
  is a user-visible semantic.
- **Where the encoding lowering lives** — §9.1. `src/gen/enc/` and `src/ir/`
  are both defensible; the panel should rule.
- **Whether one parameterised width function beats two** — §5.6.
- **The `.rxt` third oracle value** — §7.4, ASK 6, owned by the format.

---

## 11. Explicitly out of scope

`\X` (extended grapheme clusters) and `\R` — **MEASURED** as module `misc`,
not `unicode-props` (`out/premises.txt` §2). `\X` is the one construct in the
UTF neighbourhood that is genuinely not a class: a grapheme cluster is a
variable-length sequence with its own break algorithm, and it would be the
first construct whose width is unbounded at the character level. It belongs to
its own module and its own design gate.

UTF-16 and UTF-32 (`[DD-12] (6)`). PCRE2's `PCRE2_UCP` as a pcrec axis
(§14 ASK 4). Optimising `ENG_ATTEMPT`'s start loop for character boundaries
(§5.5). A two-value scan arm for the prefilter (§6.3) — measured as an
opportunity, declined under D77 until a UTF corpus exists to measure it on.

---

## 12. What would refute this — predictions for the panel

Written before the panel rather than after. Each is falsifiable.

- **P-1 — the third-encoding recipe holds.** Adding `enc_utf8.c` plus its
  registry row touches no file in `src/core`, `src/gen`, `cli/` or `lib/`.
  *Refuted by:* any shared file needing an edit. **If refuted, that is the
  design-stop signal DD-12 names, not a patch to write** — and the honest
  prediction is that the LOWERING (§9.1) is where it will bite, because the
  recipe was written for residual text and a lowering is not text.
- **P-2 — the identity gate is 100% at stage 1.** *Refuted by:* one
  non-identical artifact. The likeliest cause is an ordering difference in
  interval→bitmap conversion for a class whose producers overlap.
- **P-3 — pcrec's own lowering produces state counts within 2× of
  `out/sizing.txt`.** *Refuted by:* a `\p{L}` DFA over 566 states. The
  prototype shares no code with pcrec, so this is a real prediction.
- **P-4 — `\b` needs no seam entry without UCP** (§5.4). *Refuted by:* one
  subject where the byte-level word test and the character-level test disagree
  under `--encoding=utf8` at `\w = [A-Za-z0-9_]`. I believe no such subject
  exists; a sweep over multi-byte characters adjacent to word characters is
  the instrument.
- **P-5 — no corpus pattern's minimised DFA grows past a cap under utf8.**
  *Refuted by:* any corpus pattern that compiles under `byte` and hits
  `PCREC_MAX_DFA_STATES_TABLE` under `utf8`. §2.4 measures classes in
  isolation, **not** the products a real pattern builds — this is the
  measurement §2.4 does not make and the most likely place its comfort is
  misplaced.
- **P-6 — the `(?i)^(ss)\1$` witness in `enc_byte.c` is wrong and
  `^(k)\1$` is right** (§5.3). *Refuted by:* 10.46 matching the sharp-s cell
  under some options word this lane did not try.
- **P-7 — `\p{...}` under `--encoding=byte` needs no widening** (§3.2).
  *Refuted by:* a property whose sub-0x100 membership cannot be expressed as a
  256-bit bitmap, which is impossible, so the real refutation is a property
  whose *name* pcrec accepts and whose byte-tier answer diverges from 10.46's
  8-bit answer.
- **P-8 — 10.46 does simple folding only** (§4.1). *Refuted by:* any 1:n
  cell matching under any options word. This is the single result the most
  design depends on; §14 ASK 3 asks whether to make it a standing check rather
  than a one-time measurement, since a future PCRE2 could add full folding.

---

## 13. The implementation brief

Deliberately short: the stages in §9.2 are the brief, and each names its own
acceptance. Three cross-cutting obligations belong to every wave:

1. **D80** — anything a caller can observe updates `docs/spec/` in the SAME
   change. Stage 2 alone touches `match_api.md` §3.1.1 (the `next_pos`
   contract's "byte encoding" paragraph), §8.2 (`utf8` stops being refused),
   and `limits.md` if any cap moves.
2. **D76/D94** — any change to emitted scaffolding is an `abi` bump plus an
   identity-gate re-pin **in the same change**, with the site list found by
   grepping for the current abi number's readers, not hand-enumerated.
3. **Every wave states its own population.** The recurring defect in this
   house is a check whose population nobody counted (`learnings.md` §3); the
   sizing sub-lane in this very lane found a construction bug only because
   its self-check counted 10,916 samples rather than asserting correctness.

---

## 14. ASKs for Frank

Six. None is a ruling contradiction; each is a decision this lane deliberately
did not take.

**ASK 1 — invalid UTF-8 semantics (§2.6).** The design proposes that a
pcrec UTF-8 artifact treats an ill-formed sequence as **matching nothing**,
with no validation pass and no error return — which is what the automaton does
for free, what `PCRE2_MATCH_INVALID_UTF` does, and what M3 streaming requires.
It **diverges from PCRE2's default `PCRE2_UTF` mode**, which reports an error
for the whole subject. Accept the divergence? If not, an opt-in validation
entry point is owed and it is a new seam entry.

**ASK 2 — vendoring UCD data (§3.3).** `\p{...}` needs Unicode property
tables. Generating them from python is disqualified (version drift, measured);
generating them from libpcre2 is disqualified (one source wearing two hats —
`mod_uprops.c`'s own rule). The recommendation is to **vendor the UCD data
files at a pinned version** into `third_party/` and generate a `.inc` at build
time, as `cls_bits.inc` already is. This would be the first non-PCRE2
third-party data in the repository. Approve, and approve the pin (16.0.0,
matching libpcre2 10.46)?

**ASK 3 — should "simple folding only" become a standing check? (§4.1)** The
whole of §4 rests on a one-time measurement that 10.46 does no 1:n folding.
A future PCRE2 could add full folding, and the failure would be silent. Worth
a permanent cell in the PC-3/PC-4 differential, or accept it as a
re-measurement event on version bump (D26's addendum)?

**ASK 4 — is a UCP axis owed? (§4.5, §5.4, §7.1)** `PCRE2_UCP` re-defines
`\w \d \s \b` over the whole code-point space and accounts for **8 of 28**
measured divergence rows. pcrec has no such axis. Without one, pcrec's UTF-8
answers for those constructs are the non-UCP ones and the corpus must say so.
With one, §5.4's word-classification seam entry becomes necessary. The design
recommends **no UCP axis at M5** (D18 earn-its-axis; no consumer has asked)
and flags that it is the largest single divergence family.

**ASK 5 — `ENG_ATTEMPT`'s start loop (§5.5).** Under UTF-8 it tries
mid-character starts, which are harmless (no path) but wasted, up to 3 per
character. Fixing it means routing a shared emitter loop through a residual
entry, which S68 and `engine_callable = false` currently forbid. Leave it
(the design's recommendation, D77 — measure the loss first), or charter it?

**ASK 6 — the `.rxt` third oracle value (§7.4).** The format has
python-verifiable and `# pcre2-only`. UTF needs a third: python-verifiable
**through the `str` engine only** (5 of 28 measured cells). This lane did not
edit `docs/spec/rxt_format.md`. Route it to `[DD-13b]`, or charter a small
amendment now so stage 2's corpus has somewhere to live?

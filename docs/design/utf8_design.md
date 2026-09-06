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

### FRANK RULED FOUR ASKs WHILE THIS REVISION WAS RUNNING (2026-09-04)

Relayed by the manager into `docs/dev/lanes/utf8design_rulings.md`, polled and
consumed here. **Each ruling is written into the section it governs as well as
into §14** — a ruling that lives only in the ASK list is a ruling the
implementation wave will not find, which is the gap `lanes/CLAUDE.md` records
lane `macport` falling into.

| ASK | ruling | consumed at |
|---|---|---|
| **1** — invalid-UTF semantics | **AGREED**: ill-formed matches nothing, no validation pass, no error return | §2.6, and §9.2's stage-2 precondition (C11) is **DISCHARGED** |
| **2** — vendor UCD 16.0.0 | **AGREED, RELUCTANTLY**, conditional on the usage summary being carried prominently at the specification | **§3.3.1 is that condition discharged** |
| **4** — a UCP axis | **NO AXIS AT M5, door EXPLICITLY open** — r54's re-priced cost (§5.4.1) is the charter price for whoever opens it | §14 ASK 4, §5.4.1 |
| **5** — `ENG_ATTEMPT`'s start loop | **AGREED, leave it** — with the addendum **VALIDATE AGAINST ORACLES**. ⚠ **RE-OPENABLE (2026-09-05, K49/K50)**: the ruling was given §5.5's claim that a mid-character start "cannot produce a wrong answer", and that claim is REFUTED — see the boxed note at §5.5. The addendum was the half that held | **§2.6.1.1**, a new probe section run against 10.46; §5.5's refutation box |

**ASK 5's addendum was the expensive one and it earned its cost.** It turned
§2.6.1's entry-promise table from ARGUED into MEASURED, and the measurement
found **three oracle answers where the design had assumed two** — plus a
**second, independent witness for §5.2.1's `back_step` repair on a WELL-FORMED
subject**, which widens P-9's instrument.

**A SECOND RULINGS BLOCK (R-ASKS-2) LANDED MINUTES LATER**, and closes the
list:

| ASK | ruling | consumed at |
|---|---|---|
| **3** — standing fold check | **RULED: YES.** The 11 one-to-many candidates become a permanent cell on the PC-3/PC-4 differential | **§4.1.1** specifies it (22 assertions, both option words); **§8.2 row S-U11**; **§9.2 places it at STAGE 1**, four stages before the fold it defends, because its subject is libpcre2 rather than pcrec |
| **6** — the `.rxt` oracle value | **RULED: the small `rxt_format.md` amendment route**; the manager charters it, spelling is the manager's, §7.1.1's predicate is the input | **§7.4.1** — this lane does not write the spec, and hands over the correction that the amendment needs **at least four** states, not the three the ASK asked for |
| — | **NEW, from Frank's width question**: record what the door to UTF-16/32 costs | **§5.7**, a note beside the seam discussion — and §11 now carries the technical reason beside the policy one |

**All seven ASKs are now ruled.** **A THIRD BLOCK (R-ASKS-3) then extended
ASK 2 and widened the width note**, and it is the one that changed a claim
rather than adding a section:

| ruling | consumed at |
|---|---|
| **(a)** `third_party/` gets a GENERAL organizational shape from day one — one directory per source, a `PROVENANCE.md` naming what DERIVES from it, and the derivation step named generically (*"a data source compiles to generated tables"*), **UCD being the first instance and not the pattern** | **§3.3.2** |
| **(b)** the door is not 16/32-wide but **ENCODING-wide** — single-byte codepages are a different data KIND and a nearly-free backend; multi-byte legacy encodings ride the same lowering | **§5.7.3**, and §5.7 is retitled |

**AND (b) PRODUCED TWO FINDINGS AGAINST THE REST OF THIS REVISION.** A
codepage's repertoire is 256 code points **scattered** across Unicode, so
`[^a]` complements within an arbitrary SET and **no maximum describes it** —
`PcrecEnc.max_cp`, introduced one section earlier by E2's own repair, is the
CONTIGUOUS-repertoire form of a more general question. And §2.3's *"an
interval becomes a small set of byte-range sequences"* rests on an unstated
**MONOTONICITY** premise that UTF-16 and every legacy encoding lack. Both are
recorded with their triggers rather than built for (D77).

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
backend's instance is the identity map it already is. The lowering is an
**AST→AST rewrite at one forced point in `compile.c`'s pass chain** (§2.1.2),
because both the IR builder and the VM emitter read the class payload and the
VM emitter is handed the AST itself. Everything below that point — subset
construction, minimisation, both emitters, every prefilter — stays byte-wise
and never learns that UTF-8 exists; **three passes above it** (`altcls`,
`possessify`, `revdet`) see code points and are widened or decline (§2.5.1).
`\p{...}` is a producer of intervals and is therefore **not gated on the
encoding at all**; case folding is a **closure over the interval set** applied
in the one constructor that already applies it (D23), before negation, exactly
as today, where negation complements within **the encoding's own universe**
(§2.7.1). The seam's **entries table** gains no new interface — its four
residual entries get UTF-8 bodies under their existing signatures — while
`PcrecEnc` itself gains one scalar for that universe; and the one place the
design has to change an ANALYSIS rather than a mechanism is the lookbehind
width rule, measured to be in CHARACTERS where pcrec computes BYTES, under the
byte encoding indistinguishable.

> **This paragraph was re-written at r54.** The first version said "the seam
> gains no new interface" and placed the lowering "between the parser and the
> IR", and both were load-bearing and wrong. Read the PANEL OUTCOME block
> above before trusting any summary sentence in this document.

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

> **ALL EIGHT TRANSCRIPTS WERE RE-ARCHIVED AT r54 (MUST-FIX M1/meas-1, SHOULD
> meas-2/meas-3), and the reason is that the first round's provenance was
> decorative.** `probes/bundle.py` computed a `_BUNDLED_SHA` of every borrowed
> file and embedded it in the payload, and **nothing ever read it** — not
> `u8_oracle.header()`, not `archive.sh`, not any probe. Meanwhile every
> header's `RUN FROM REPO COMMIT` named a commit at which
> `utf8_measurements/` was **untracked**, so the commit line pinned nothing
> either: a reader could not recover the bytes that produced any number in
> this document.
>
> Three fixes, then a re-run of all eight:
>
> - `u8_oracle.header()` now prints a **source sha256 block** in one of two
>   labelled modes — `bundled` (the hashes of the bytes that actually executed
>   on the far end, which is the authoritative case) or `local` (hashed from
>   disk, weaker, and it says so). Verified agreeing across the machine
>   boundary: `probe_width.py` produces the identical four hashes run locally
>   and run over `ssh`.
> - `archive.sh`'s `PROBE LAST CHANGED AT COMMIT` field had a
>   `|| echo uncommitted` fallback that **never fired**, because `git log` on
>   a never-tracked path exits 0 with empty stdout — the test was on exit
>   status where the fact lives in emptiness. It came out **blank**, which
>   reads as a formatting glitch rather than as the fact it is.
> - `probe_uprops.py`'s dead ternary (meas-5) removed.
>
> **meas-2's blank `RUN DATE` on `sizing.txt` had a cause, now found**: that
> transcript was archived by a version of `archive.sh` that used GNU
> `date -Is`, which fails on this Mac's BSD `date` and emitted nothing. The
> spelled-out `date +%Y-%m-%dT%H:%M:%S%z` that replaced it was already in the
> script by the time the panel read it, so only a re-run could show it. Every
> header now carries a real date, a real probe commit, and the source hashes.
>
> **`probe_sizing.py` also gained sections (h)-(k)** — the alphabet partition,
> the premultiplied entry count, the same with `\b`'s refinement, and the
> interned subset-element count — which is MUST-FIX E6's measurement and is
> what §2.4.1 reports.

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
document, and **it was the one headline result the r54 panel confirmed
independently** — the engine critic reproduced it at
`mod_lookaround.c:298`/`mrl.c:282-284` without relying on this document's
citations. **What r54 changed is the RESOLUTION, not the refutation**: §5.6.2
finds `pcrec_maxw` has no consumer at all besides the rule being moved, so the
cross-note's arm does not get a new value — the whole chain retires.

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
 :1017  if (chosen == ENGM_DFA || fit.prefilter)    ← the NFA build is GUARDED
 :1018      pcrec_build_nfa(&cx, root, ...);        reads u.cls.bits ×2
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
2. **The lowering must not REALLOCATE a node that is or contains a group
   root** — a PROPERTY of the pass, not a constraint on its position.
   [CORRECTED 2026-09-05, stage-1 lane utf8s1's wave-task-(a) measurement +
   ruling R2; the original clause here read "callgraph_build (:961) must run
   AFTER the lowering — so the lowering cannot run before :961", which was a
   non-sequitur that MEASURED FALSE: a rebuilding lowering placed at :1000
   differs on 45 of 179 recursion artifacts and is byte-identical only ABOVE
   :961, and taken with constraint 3 it left NO legal slot at all.]
   `compile.c:947-955` states the real rule: `.body` is a cache of *"which
   subtree is that group's, IN THE TREE THE EMITTER WILL WALK"*, captured by
   `pcrec_callgraph_build` at :961, and a `.body` captured before a pass that
   REALLOCATES those nodes names a subtree that is no longer there — *"two
   programs for one group"* (empty `W`, §5.3b's lost match). The cure is the
   pass's SHAPE: `pcrec_lower_enc` SPLICES IN PLACE — it replaces a leaf
   `A_CLASS` by mutating the parent's child pointer (or reassigns the driver's
   `root` for a bare-class root, which is never a group root), and never
   reallocates a node that is or contains a group root. Leaves are never group
   roots, so callgraph_build's bindings stay valid and the lowering runs at
   :1000, AFTER the graph binds — the position `altcls` and `discharge_atomic`
   would have forced is not required once the pass cannot strand a capture.
   Stage 2 enforces this with a check that no group-root node's ADDRESS moves
   across the pass (§9.2).
3. **`pcrec_postresolve` (:999) must run BEFORE the lowering.** It asks the
   lookbehind fixed-width rule in **CHARACTERS** (§5.6), and after the
   lowering a two-byte character is an `A_CAT` of two byte classes, so a
   character-width walk over a lowered tree would answer 2 where the truth is
   1. It cannot run earlier than :961 either, because its whole reason for
   existing is that a call's width cannot be answered until the graph binds
   the callee.

Constraint 3 puts the lowering after :999; constraint 1 puts it before
:1018; constraint 2 is now a PROPERTY (splice-in-place) the pass carries at
whatever slot those two allow. `:1000` is that slot. [The original text here
claimed "there is exactly one line between them" from three positional
constraints; that was an artifact of constraint 2's mis-statement — corrected
with constraint 2 above, stage-1 lane utf8s1 / R2.]

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
compile.

> **AND THE CONCLUSION THE FIRST VERSION DREW FROM THAT IS NARROWED (r54).**
> It read: *"which is why §6 finds no downstream consequences: there is
> nothing downstream to change."* **The premise is right and the conclusion
> over-reached in two directions**, both of which this revision found by
> looking rather than by argument. **DOWNSTREAM** of §2.1.2's forced position
> there is indeed nothing to change *in kind* — but §2.4.1 measures that the
> ALPHABET those nodes induce is a different size, and `\p{L}{1,3}` drops off
> `[OPT-3]`'s premultiplied form because of it, which is a downstream
> consequence in every sense except node kinds. And **UPSTREAM** of it,
> §2.5.1 finds six sites in three files that see code points and must widen or
> decline, which the phrase "nothing downstream" quietly excluded by choosing
> the word "downstream". The honest form: **the lowering introduces no new
> node kind, so no consumer needs a new case; what it changes is the SIZE and
> SHAPE of what existing consumers see, and §2.4.1, §2.5.1 and §6.4 are where
> that is priced.**

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

Four consumers were named in the charter, and they are answered below.
**STRUCTURAL** in each case — but **the charter's four are not the tree's
nine**, which is r54 E5 and is why §2.5.1 exists. Read this list for what each
named consumer does, and §2.5.1 for the census that decides them.

- **The 256-entry class bitmap machinery** is *below* the lowering and is
  untouched. `NState.cls[32]`, the DFA's `eqclasses` partition and its
  `d->rep[c]` representative-byte trick all operate on the byte alphabet, and
  after lowering the byte alphabet is all there is. (**Its SIZE is not
  untouched** — §2.4.1 measures `ncls` at 95-96 for a `\p`-sized class where
  an ASCII class gives a handful — but no code changes.)
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

##### 2.6.1.1 MEASURED — and there are THREE answers, not two

**Frank's ASK 5 ruling (below, §14) is "leave `ENG_ATTEMPT`'s start loop
alone" with the addendum "VALIDATE AGAINST ORACLES", so this stopped being an
argument and became a measurement.** `out/invalid_utf.txt` **§E2**, added in
this revision: subject `αβ` (`CE B1 CE B2`, boundaries at 0/2/4), every cell
in all three option words.

The first version's §2.6(e) measured only `.` — **a POSITIVE pattern, which is
the direction that cannot invert.** §E2 measures the direction that does:

| pattern | start | `PCRE2_UTF` | `MATCH_INVALID_UTF` | `options=0` (byte) | **pcrec/utf8 (ARGUED)** |
|---|---|---|---|---|---|
| `(?<!.)` | 0 bnd | `(0,0)` | `(0,0)` | `(0,0)` | `(0,0)` |
| **`(?<!.)`** | **1 MID** | **`ERRM -36`** | **`(2,2)`** | **no match** | **`(1,1)`** |
| `(?<!.)` | 2 bnd | no match | no match | no match | no match |
| `(?!.)` | 1 MID | `ERRM -36` | `(4,4)` | `(4,4)` | `(1,1)` |

**THREE DIFFERENT ANSWERS ON ONE CELL, and pcrec's is a fourth.**

- **`PCRE2_UTF` REFUSES** — `ERRM -36 "bad offset into UTF string"`, and
  **uniformly**: every mid-character start in §E2's table is `-36` regardless
  of pattern. It never answers at all.
- **`MATCH_INVALID_UTF` ADVANCES to the next boundary and then answers** —
  and it does **not** give the same answer as starting at that boundary. At
  start=1 it reports `(2,2)` where a start of 2 reports **no match**. The
  mid-character entry point acts as a **barrier** the lookbehind cannot cross,
  which is `MATCH_INVALID_UTF`'s own ill-formed-bytes rule applied to a
  truncated leading character. A reader who assumed "it just rounds the offset
  up" would have got this wrong.
- **`options=0`** has no notion of a boundary, so every offset is one.
- **pcrec under `--encoding=utf8`** answers `(1,1)`: §5.2.1's `back_step` at
  `pos=1, k=1` walks to 0, finds lead `0xCE` declaring 2 bytes against a run
  of 1, and returns `BACK_STEP_NONE` — so the lookbehind body cannot run, the
  negative assertion succeeds, and the match is the empty one at 1.

**THE VACUITY GUARD, in the failing direction as this lane's own rule
requires**: a mid-character start differs from the boundary below it on
**8 of 8** negative-assertion cells under `PCRE2_UTF`. A 0 would have meant
the table could not see the phenomenon it exists for.

> **WHERE THIS TABLE'S CELLS LIVE NOW (2026-09-06, [K50], lane `k50bnd`).**
> The mid-character rows are still RULED and still checked, and they moved
> rather than changed. Frank's 2026-09-05 follow-up gives the emitted entries a
> DEFAULT-ON boundary guard that refuses a mid-character caller `startpos` with
> `PCREC_ERR_STARTPOS` — which is what `PCRE2_UTF` does, measured uniform over
> ten patterns (`out/startbnd.txt` §2) — and retains the permissive answers
> above VERBATIM behind `-fno-startpos-guard`. So the `pcrec/utf8 (ARGUED)`
> column is this document's position for the DENIED arm, and the default arm's
> column would read `REFUSED` throughout. `tests/utf8/axis09_nextpos_findall.rxt`'s
> two mid-character blocks moved to `tests/utf8/run_startbnd_diff.sh` §6, which
> can express the flag where a `.rxt` block cannot; that file carries a pointer
> where each stood.
>
> One clause of the guard is NOT in the table above and is worth knowing here,
> because this table is where a reader looks for the rule: **offset 0 is always
> a valid start**, even on a subject that begins with a continuation byte. The
> local byte test alone refused it, which turns §2.6's ruled "an ill-formed
> sequence matches nothing" into "ill-formed input is an error" — libpcre2 can
> ask the local question safely only because its whole-subject validation pass
> has already rejected such a subject, and §2.6 declines that pass.

**AND THIS CELL IS A SECOND, INDEPENDENT WITNESS FOR §5.2.1's REPAIR** — one
this revision did not go looking for. Run `(?<!.)` at `startpos=1` against the
**un-repaired** `back_step` of §5.2: it walks to 0, sees `0xCE` is not a
continuation byte, and returns **0**; the body `.` then matches `α` and ends
at **2 ≠ 1**; the end-check fires; and on the negative arm that is
`RX_R_INTERNAL`, below `PCREC_ERR_FLOOR`, so a composed site **traps**. The
E4 defect is therefore reachable **on a well-formed subject** through a
caller-supplied `startpos`, not only on ill-formed input as the panel's cell
had it. **§12 P-9's instrument is widened accordingly**: mid-character
`startpos` cells, not just the nine ill-formed kinds.

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

#### 3.3.1 WHAT THE VENDORED DATA IS ACTUALLY USED FOR — the ruling's own condition

> **ASK 2 IS RULED (2026-09-04): AGREED, RELUCTANTLY** — and the reluctance is
> part of the ruling. Frank's condition, verbatim in intent: *the design should
> carry the usage summary prominently where the vendoring is specified, so the
> reluctance stays priced.* **This subsection is that condition discharged.**
> It is here, at the specification, and not only in §14.

**THE VENDORED UCD FILES ARE COMPILE-TIME DATA IN `libpcrec.a`. THEY ARE NOT
SHIPPED TO USERS AND THEY ARE NOT EMBEDDED IN ARTIFACTS.** Concretely:

| where | what | size |
|---|---|---|
| `third_party/ucd-16.0.0/` | the source files: `UnicodeData.txt`, `Scripts.txt`, `ScriptExtensions.txt`, `PropList.txt`, `DerivedCoreProperties.txt`, `CaseFolding.txt` | vendored text, built into a `.inc` exactly as `cls_bits.inc` already is |
| `libpcrec.a` | the generated interval tables — what `pcrec` consults to turn `\p{L}` into an interval list | ~40 KB for the general categories; scripts and `scx` add more at stage 5 |
| **a generated artifact** | **nothing of it.** The artifact carries the LOWERED AUTOMATON (§2.4 — `\p{L}` is 283 DFA states), which is a machine over bytes and contains no property data at all | — |

**THE ONE EXCEPTION, stated because a summary that hid it would be worthless**:
§4.6(b), the **caseless backreference fold table**. A caseless backref folds
subject bytes at MATCH time, so it cannot fold away at compile time, and its
fold pairs do reach the artifact's residual text — **~12 KB** as sorted pairs
with a binary search, 1.2% of D84's total cap. That is the whole of what a
user's compiled matcher inherits from the vendored data, and §4.6 constrains
the form (a direct-indexed map would be 4.4 MB and D84 refuses it outright).

#### 3.3.2 `third_party/` GETS A GENERAL SHAPE FROM DAY ONE (R-ASKS-3(a))

> **Frank's extension to ASK 2's ruling**: do **not** architect as if UCD is
> the only outside data file this repository will ever hold. `third_party/`
> gets a general organizational shape from day one, and the derivation step is
> named in its general form — *"a data source compiles to generated tables"* —
> with **UCD properties as the FIRST INSTANCE, not as the pattern.**

**THE SHAPE**, and the point of writing it down before there is a second
source is that the second source is when it becomes expensive to change:

```
third_party/
  README.md                  the index: one row per source, what it is for
  ucd-16.0.0/                ONE DIRECTORY PER SOURCE, versioned in its name
    PROVENANCE.md            source URL, version, licence, retrieval date,
                             and WHAT DERIVES FROM IT (the generated tables,
                             by name, so a reader can go the other way)
    UnicodeData.txt          the vendored files, unmodified
    Scripts.txt
    ...
  <next-source>-<version>/   the same five things, whatever it is
```

Two properties are the whole of the requirement, and neither is about
Unicode:

1. **One directory per SOURCE, version in the directory name.** Two versions
   of one source can coexist during a bump, and nothing has to be renamed to
   make that true. `pcre2-testdata/` — the repository's existing vendored
   data — is retro-fitted into the same shape rather than left as the
   exception that proves a rule nobody wrote down.
2. **`PROVENANCE.md` names what DERIVES from the source**, not only where the
   source came from. That direction is the one a maintainer actually needs
   ("this table looks wrong — what produced it, and from what?") and it is the
   direction a licence audit needs too. The generation step reads it; nothing
   else does.

**AND THE DERIVATION IS NAMED GENERICALLY.** The build rule is *"a data source
compiles to generated tables"* — the same shape `src/parse/cls_bits.inc`
already has, which `[DD-11]`/D85 rules is a DERIVED artifact. The UCD
interval tables are the first instance of that rule and are **not** its
definition: a rule spelled `ucd_to_intervals` would have to be renamed the day
a second source arrives, which is exactly the re-plumbing this ruling exists
to prevent.

**§5.7.3 is the other half of this ruling** — the data KINDS beyond
interval-shaped property tables, which is where a second source most plausibly
comes from.

**WHY THE RELUCTANCE IS THE RIGHT INSTINCT AND THE ANSWER IS STILL YES.**
Vendoring third-party data is a permanent maintenance and licensing surface,
and `third_party/` today holds only PCRE2's BSD-licensed testdata. The two
alternatives were **disqualified on measurement, not on taste**: generating
from python's `unicodedata` makes the table depend on which machine ran the
generator (**measured: `\p{L}` is 648 intervals under Unicode 14.0.0 and 677
under 16.0.0**, and this project's two boxes carry both), and generating from
libpcre2 would make PC-3/PC-4's differential check its own generator's output
— *"one source wearing two hats"*, `mod_uprops.c`'s own rule. **The pin is
16.0.0 because that is what the reference oracle is**, derived by sweep rather
than assumed (`out/uprops.txt` §0), and a libpcre2 version bump is a D26
re-measurement event that moves the pin deliberately.

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

#### 4.1.1 The 0-of-11 becomes a STANDING CHECK (ASK 3, RULED 2026-09-04)

> **Frank's ruling**: the eleven one-to-many candidates become **a permanent
> cell riding the existing PC-3/PC-4 differential**, firing the day the
> oracle's folding behaviour changes.

**WHY THIS IS THE RIGHT SHAPE AND NOT BELT-AND-BRACES.** §12 P-8 already
called this *"the single result the most design depends on"*, and the
dependency is structural rather than incidental: **the absence of 1:n folding
is what lets a caseless class stay a CLASS.** A 1:n fold is a sequence, so
its existence would force a caseless literal into an alternation and a
caseless class into something a class cannot hold — which is not a tuning
change, it is a different lowering. **And the failure would be silent**: a
future PCRE2 that added full folding would simply start matching cells pcrec
answers `no` to, with nothing in this tree noticing, because a one-time
measurement leaves no instrument behind.

**THE CHECK, specified** (the implementation wave builds it; this is what it
must be):

| | |
|---|---|
| **rides** | PC-3/PC-4's existing libpcre2 differential (`tests/registry/pcre2_check.c`, `tests/registry/pc4_check.c`), so it inherits their *skip-loudly-if-libpcre2-is-absent* convention rather than inventing one |
| **population** | the **11 measured cells** of `out/caseless.txt` §2, by name — ß/SS, ß/ss, SS/ß, ss/ß, U+FB01/fi, fi/U+FB01, U+FB03/ffi, U+0149, U+01F0, U+1E96, U+0390 — **each under both `PCRE2_UTF\|PCRE2_CASELESS` and `…\|PCRE2_UCP`**, which is 22 assertions, because §4.1 measured both and a check that dropped the UCP arm would not cover what the design read |
| **asserts** | every cell does **not** match. A cell that starts matching is a **RED**, not a skip |
| **the diagnostic** | must name what it means, not just what failed: *"libpcre2 has gained 1:n case folding; `docs/design/utf8_design.md` §4.1 and `[FORM-CHAR]` object (5) are invalidated"* — the D26 re-measurement event this fires for is a design event, and a check that says only "cell 7 failed" makes a reader rediscover that |

**WHICH STAGE — AND IT IS NOT THE ONE THE FOLD LANDS IN.** The obvious home is
stage 4, where the fold closure is built. **That is wrong, and the design says
so rather than defaulting**: this check tests **the ORACLE's behaviour, not
pcrec's**, so it has no dependency on any pcrec code and can run today. Put it
at stage 4 and stages 1-3 are built on an unwatched premise for the whole
milestone — precisely the window in which a libpcre2 bump would be cheapest to
absorb and most expensive to discover late.

> **The standing fold check lands at STAGE 1**, with the rest of §4 unbuilt.
> It is the only check in this plan whose subject is not pcrec, and that is
> exactly why it can and should go first.

§8.2 gives it sabotage row **S-U11** with the `SAB_REACH`/`SAB_REACH_POP`
discipline every other row now carries, and §14 ASK 3 records the ruling.

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

---

## 5. THE SEAM'S SECOND INSTANCE (charter (iv))

### 5.0 The headline, RETRACTED and re-stated (r54 E2)

The seam is `src/gen/enc/enc.h`'s `PcrecEncEntry` table, four entries today.

> **THE FIRST VERSION'S HEADLINE WAS: "the seam needs no interface change —
> D58's revisit clause is honoured by having nothing to record." THAT IS
> FALSE**, and §2.7.1 is why: the complement universe must be per-encoding,
> `PcrecEnc` carries `{id, name, entries}` and nothing else
> (`enc.h:98-106`, verified), so **one scalar field is added** and that is a
> D58 seam change with something to record (ASK 7).

**What survives is the claim the third-encoding recipe actually makes, and it
is the load-bearing half:**

- **THE ENTRIES TABLE'S INTERFACE IS UNCHANGED.** Four residual entries get
  UTF-8 bodies under their existing signatures; no `PcrecEncEntry` field is
  added; `pcrec_enc_ready` is untouched; both emit functions are untouched.
  That is the property `[M6.6.2]` wave D demonstrated when `back_step` landed,
  and §12 P-1′ is what keeps it falsifiable.
- **`PcrecEnc` ITSELF GAINS ONE SCALAR** (`max_cp`), read by exactly one
  caller — the parser's negation site.
- **AND THE ONE THING THAT HAS TO CHANGE OUTSIDE THE BACKEND IS AN ANALYSIS,
  WHICH THE SEAM WAS NEVER GOING TO CATCH** — the lookbehind width rule
  (§5.6), which is the original headline's real content and is unaffected by
  the retraction.

**Why the distinction is worth a section rather than a footnote.** "No
interface change" and "no change to the entries table" are different promises,
and the first version used the stronger one as a summary of the weaker one's
evidence. The seam's VALUE is the entries table — that is what a third backend
plugs into, and it is what `enc.h`'s recipe describes. A scalar on the
registry struct is a much smaller thing, but it is not nothing, and D58's
revisit clause exists precisely so that "much smaller" is written down rather
than assumed.

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

> ### ⚠ THE PARAGRAPH ABOVE IS REFUTED (2026-09-05, lane `k49fix`, K49/K50)
>
> **"Those starts have no path, so they cannot produce a wrong answer" is
> FALSE**, and this document had already written down the reason one section
> earlier without connecting it. §2.6.1 — *"'No path' INVERTS for a negative
> assertion"* — is exactly the counterexample: an assertion that succeeds
> where its body has no path SUCCEEDS at a mid-character start, so such a
> start does not merely waste an attempt, it ANSWERS, with a reported position
> inside a character. The paragraph above was written from the positive-only
> premise §2.6(e) measured (`.`), which is the direction that cannot invert.
>
> **The two witnesses**, both measured on the shipped stage-2 tree:
>
> - **K49** — `(?<!.)` over `CE B1 CE B2` at `startpos=2` reported `(3,3)`.
>   The VM's own external advance (`attempt_position++` in the emitted
>   `<prefix>_search_run`), not `ENG_ATTEMPT`'s, which means this section
>   under-counted the external advance loops that exist: there are at least
>   three (the VM retry, `ENG_ATTEMPT`'s `start++`, and the DFA self-loop that
>   plays the same role in `ENG_UNANCH`). **FIXED** — the advance is now the
>   encoding backend's own text, `enc.h`'s `advance` field.
> - **K50** — `\B` over `61 CE B1` at `startpos=0` reports `(2,2)`, a
>   mid-character position from an ORDINARY boundary-aligned start, on the
>   DFA. libpcre2 answers `(3,3)` under both UTF option words and `(2,2)` under
>   `options=0`, so pcrec's UTF-8 build is returning the BYTE answer. **OPEN.**
>
> **§14 ASK 5's ruling rests on the refuted claim and is re-openable on that
> ground** — see the note in its row. Nothing here says Frank would rule
> differently; it says the ruling was given the wrong facts. What replaces the
> claim: a mid-character start is not merely suboptimal, it is unsound for any
> pattern that can match empty at it, and the general rule the fix spells is
> that an unanchored search's candidate match STARTS are exactly the
> encoding's character boundaries.
>
> ### BOTH HALVES ARE NOW CLOSED, AND THE SECOND HALF CAME WITH A WITNESS
> THIS BOX DID NOT HAVE (2026-09-06, lane `k50bnd`)
>
> **THE WASTED-ATTEMPT CLAIM UNDERSTATED IT, and the box above understated it
> too.** This annotation was written after K49 and it refuted §5.5's *reason*
> — "no path" inverts — while leaving the impression that
> `ENG_ATTEMPT`'s loop was the remaining THEORETICAL case, K50's own site list
> filing no witness for it. It is not theoretical.
>
> `ENG_ATTEMPT`'s `start++` loop — the loop this section is actually about —
> was a LIVE WRONG-ANSWER PRODUCER and not a wasted attempt. `(?m)^a|\B` over
> `61 CE B1` at `startpos = 1`, a real character boundary, reported `(2,2)`
> where libpcre2 10.46 under `PCRE2_UTF` answers `(3,3)`. The witness needs
> two branches and neither is optional: the BOT-family branch is what routes
> the pattern to this engine, and the nullable second branch is what keeps an
> interior start state live so `start_max` is the subject length. **A pure
> `(?m)^` or `\G` pattern is SELF-GATING** — `(?m)^` can hold only after a
> newline and a newline is a character-start byte — which is why the site
> stood unwitnessed while this section asserted it was harmless.
>
> ### THE TWO PLACEMENTS THAT LOOK RIGHT AND ARE NOT
>
> Recorded here so a reviewer starts from the refutations rather than
> re-deriving them, and because both are the first thing a reader proposes.
> The gate is on the SPLIT INTO THE PATTERN — the placement K50's own entry
> recommends — and the alternatives fail for reasons that are about the
> automaton rather than about taste:
>
> - **Gate the self-loop's RE-ENTRY** (`any -> gate -> sp`) rather than the
>   split. It kills the scan: the self-loop is the only forward advance, so a
>   thread blocked at a continuation byte DIES, and `a` on `CE B1 61` is never
>   found at all. The gate must sit where a thread is CHOOSING, not where it
>   is travelling.
> - **Make the self-loop consume whole CHARACTERS.** "Consume the lead, then
>   its continuations" needs a greedy, deterministic skip, and a priority
>   SPLIT cannot force one — the nondeterministic spelling still reaches every
>   byte offset, so the wrong answers survive the restructure. (It also has to
>   handle `CE 61`, where the lead's declared length and the boundary
>   predicate disagree; §2.6(c) is what makes the predicate the authority.)
>
> A third refinement is forced by the DENY ARM rather than by the automaton,
> and it is why the wrap has TWO split states: gating the caller's own entry
> too would make `-fno-startpos-guard` answer no-match where §2.6.1.1 rules
> `(1,1)`, i.e. the axis would become a second AUTOMATON rather than a guard
> on the entries. Keeping `nfa->start` ungated is what lets ONE machine serve
> both arms.
>
> ### AND THE OPTIMISATION THIS SECTION CLAIMED IS REFUTED TOO — MEASURED
>
> The paragraph calls the fix *"the optimisation (step the loop by
> `next_pos`'s rule)"*, and K50's own entry repeated it (*"skipping
> mid-character starts is also the OPTIMIZATION §5.5 called not optimal"*).
> **It is not an optimisation.** Nine interleaved trials per cell, gcc-16 -O2,
> M1, against a scratch build of the same tree with the gate removed:
>
> | route | witness | subject | gated vs ungated |
> |---|---|---|---|
> | `ENG_ATTEMPT` | `(?m)^zzz\|\bqqq` | 4,000 × 2-byte chars | **1.33× SLOWER** (10,450 vs 7,865 ns/search, no trial overlapping) |
> | `ENG_ATTEMPT` | same | 4,000 × 4-byte chars | a wash (15,468 vs 15,538 ns, 0.4%) |
> | `ENG_UNANCH` | `\Bqqq` | 4,000 × 2-byte chars | a wash (194.6 vs 195.6 ns, inside the spread) |
>
> **The mechanism is a branch, not the skipped work.** The guard is evaluated
> on EVERY iteration and skips work on only some, and the work it skips is one
> seed dispatch into a computed goto that dies immediately — a few
> instructions. On a 2-byte-character subject the guard's own branch alternates
> taken/not-taken every iteration, which is the worst case for a predictor; on
> a 4-byte subject it is taken 3 times in 4, more predictable and skipping
> more, and the two effects cancel. The DFA route pays nothing in TIME and pays
> in SIZE instead: the gate is a real automaton state, and `\Bqqq`'s forward
> transition table grows from 15 entries to 20.
>
> **This changes nothing about the fix**, which is a correctness fix and is
> paid for whatever it costs. What it changes is the sentence: the cost is
> real, small, and on the shape where mid-character starts are commonest it is
> a LOSS rather than the saving this section predicted. Anyone reaching for
> §5.5 as evidence that a boundary-stepping loop is faster should read this
> table instead.

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
section. `pcrec_maxw` has exactly **four** call sites — three in `src/`
and one shipped INSTRUMENT in `tests/` the verifier pass (r54) caught this
census omitting, the panel's E5 defect recurring one directory over:

| site | what it is |
|---|---|
| `src/parse/mod_lookaround.c:298` | `la_widths`, per top-level branch — **the rule §5.6 is moving** |
| `src/parse/mod_lookaround.c:309` | `la_widths`, the whole body — **the same rule** |
| `src/opt/callgraph.c:795` | the `maxw` fixpoint, which exists **only** to publish `u.call.maxw` for the arm those two read |
| `tests/mrl/maxw_check.c:77` | the [M6.6.2] wave-A instrument reading `pcrec_maxw` over the whole `.rxt` corpus — `run_mrl_tests.sh` section 8, with its own three-way sabotage channel |

Every other occurrence in `src/` (the scope actually grepped, plus the one
test-side consumer named above) is a COMMENT (`emit_vm.c:6128`, `:6152`,
`internal.h`'s field documentation, `mrl.c`'s own header) or `mrl.c`'s
internal recursion. **So once `la_widths` moves to the character pair,
`pcrec_maxw` has no reader in the product at all** — and neither does
anything downstream of it: `u.call.maxw`, `u.call.maxw_known`,
`cg_maxw_publish`, the fixpoint at `callgraph.c:786-800`, and sabotage row
`S171` (`tests/mech/sabotages/S171_maxw_fixpoint_one_round.sh`). The
retirement therefore also RETIRES OR RE-AIMS the test side in the same
change: `maxw_check.c` and its `run_mrl_tests.sh` section 8 (re-aim at
`pcrec_cwmax` — the corpus-wide over-estimate assertion transfers to the
character pair unchanged in spirit), and
`tests/mech/sabotages/S136_width_rule_accepts_variable.sh`, whose
`SAB_DESC` names both functions and moves with the rule. `tests/mrl/CLAUDE.md`
and `tests/CLAUDE.md` document `maxw_check` as a shipped instrument and are
updated in the same change.

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

### 5.7 THE DOOR TO OTHER ENCODINGS — what stays open, and what it costs

> **A NOTE, NOT A DESIGN (Frank's width question, 2026-09-04, R-ASKS-2;
> WIDENED by R-ASKS-3(b) the same evening).** UTF-16/32 are out of scope
> (§11) and `[DD-12] (6)` rules them out. This section exists because "out of
> scope" and "architecturally foreclosed" are different states, and the first
> version of this document said only the first. **Nothing here is built or
> proposed for building**; D77 governs, and the trigger is at the end.
>
> **AND THE DOOR IS NOT 16/32-WIDE, IT IS ENCODING-WIDE** (R-ASKS-3(b),
> Frank: *"some freak might want to build in native support for that IBM
> encoding or some non-US encoding"*). §5.7.3 is that half: single-byte
> codepages, and multi-byte legacy encodings. It is where this note earns its
> page, because the codepage case turns out to be nearly free **and** to be
> the first thing that would strain a field §2.7.1 introduces.

#### 5.7.1 What the architecture already carries

**The expensive half of a 16/32 backend is already paid for, and paid for by
this milestone rather than by that one.** The reason is §2.1's spine: code
points exist above the encoding, and only below it does anything become
units.

| what | where it sits | transfers? |
|---|---|---|
| the UCD interval tables (§3.3) | compile-time data in `libpcrec.a`, indexed by CODE POINT | **YES, unchanged** — `\p{L}` is the same set of code points whatever the encoding |
| the fold closure (§4.2) | applied to the interval SET, before any lowering, in the one constructor (D23) | **YES, unchanged** — §4.2(c)'s whole point is that the fold must happen while the set is still code points, which is encoding-agnostic by construction |
| the character-width analysis `cwmin`/`cwmax` (§5.6.3) | over the code-point AST, `A_CLASS` answering exactly 1 | **YES** — "a class is one character" is true in every encoding, which is the property that made §5.6's repair work |
| `PcrecEnc.max_cp` (§2.7.1) | the complement universe | **YES** — it is already a per-encoding field; UTF-16/32 read `0x10FFFF`, the same value utf8 reads |
| the residual entries table (§5.0) | four bodies per backend | **YES** — the third-encoding recipe is what it is for |
| the CharSet→unit-sequence lowering (§2.3) | one instance per backend | **THE SHAPE TRANSFERS**; the instance does not, and §5.7.2 is why |

**AND THE NATURAL SHAPE FOR A UTF-16 BACKEND HERE IS UNITS-AS-BYTE-PAIRS, NOT
A 16-BIT ALPHABET ENGINE.** This is the observation worth recording, because
the instinct runs the other way. §2.3's construction decomposes a code-point
interval into sequences of RANGES over the alphabet; nothing in it requires
the alphabet to be bytes — but everything BELOW it does. The subset
construction, `eqclasses`, `d->rep[c]`, the 256-entry class bitmaps, both
emitters, `memchr`, the premultiplied table: all of it is a byte machine, and
§2.4.1 has just measured how sensitive its caps are to the alphabet's size. A
native 16-bit alphabet would multiply `ncls`'s domain by 256 against a
65,535-**entry** cap that a single `\p{L}` class already spends 41% of.

> So a UTF-16 backend's lowering emits **two byte-range steps per code unit**
> — the unit's high byte then its low byte — and everything below the lowering
> is the machine that already exists. A code point becomes 2 or 4 byte steps
> instead of UTF-8's 1 to 4. **The architecture does not need a second engine;
> it needs a second lowering instance**, which is exactly what the seam
> promises.

#### 5.7.2 The three transfer-blockers, which are not small

A 16/32 author re-checks these three before anything else. Each is stated as
the blocker it is rather than as a caveat.

**(1) THE PREFILTER'S SELF-SYNCHRONIZATION PREMISE FAILS.** §6.3 establishes
that pcrec's candidate-start scan is sound under UTF-8 *and* useful, and the
useful half rests on a property UTF-8 has and **UTF-16 does not**: a lead byte
never appears mid-character. In UTF-16-as-byte-pairs, **any byte value can
appear in either position of a unit** — `0x00 0x41` is `A`, and `0x41` is also
the high byte of U+41xx — so a byte-level scan can land inside a code unit and
report a candidate start that is not a character boundary. **The scan stays
SOUND** (it reads the machine, §6.3's one-line argument does not mention
UTF-8) **and stops being a filter**: every second byte is a false candidate,
and the verification cost that §6.3's quality table prices goes with it. This
is E11's finding stated as what it is — **not a note about UTF-16, but the
named premise §6.3 depends on**, and the reason a 16/32 backend cannot inherit
§6.3's conclusion by reading it.

**(2) THE ENDIANNESS AXIS APPEARS, AND IT IS A NEW AXIS.** UTF-8 has one byte
order. UTF-16 has two (and a BOM convention), and PCRE2 ships them as
**separate libraries** (`libpcre2-16`), not as a mode. For pcrec that is a
question `--encoding` alone cannot answer: either `utf16le`/`utf16be` are two
registry rows (two lowering instances differing by byte order, which is
cheap and D18-honest — each earns its name) or one row plus a parameter,
which D18's earn-its-axis rule would have to be argued against. **The design
has no recommendation**; it records that the axis exists and that the
one-scalar-per-compile `--encoding` shape already accommodates the two-row
answer.

**(3) SURROGATES MOVE FROM "EXCLUDED CODE POINTS" TO LIVE MECHANICS.** Under
UTF-8, U+D800–U+DFFF are simply **absent** from every lowered set (§2.3), and
that absence is a one-line exclusion plus S-U7's sabotage row. Under UTF-16
they are **the encoding of every astral code point** — a surrogate PAIR is how
U+10000+ is spelled — so the same range flips from "has no encoding" to "is
the mechanism". Everything §2.3, §8.2 (S-U7) and §8.3.1's subject witness say
about surrogates is UTF-8-specific and **must be re-derived, not ported**. A
16/32 author who carried S-U7 across unchanged would be asserting the opposite
of what that encoding requires.

#### 5.7.3 THE OTHER ENCODINGS — codepages are nearly free, legacy multi-byte is not (R-ASKS-3(b))

**A SINGLE-BYTE CODEPAGE (EBCDIC, KOI8-R, Latin-N) IS ALMOST A NO-OP UNDER
THIS ARCHITECTURE, and that is a real result rather than a compliment.** Such
an encoding is a **256-entry byte ↔ code-point mapping** — a different data
KIND from §3.3's intervals, and a nearly-free backend:

- the parser produces code-point intervals, exactly as for UTF-8 (§2.2);
- the **lowering** maps each code point in the set to its single byte, and
  drops the ones the repertoire does not contain;
- the output is a plain 256-bit byte set — **byte-for-byte the same shape
  `enc_byte`'s lowering already emits.** Everything below is unchanged, and
  unlike UTF-8 there is not even a sequence: one character is one byte.

> **So a codepage backend is `enc_byte` with a different classification and
> fold mapping.** `pcrec`'s existing `byte` encoding is the IDENTITY codepage
> (Latin-1, "every byte is a character" — D58's own rename rationale), which
> means this is not a new mechanism at all: it is the shipped one with its
> table made a parameter.

**AND IT IS THE FIRST THING THAT STRAINS `PcrecEnc.max_cp`** — a finding of
this note's own, recorded because §2.7.1 introduced that field one section
ago and this is the case that outgrows it. The complement universe for
`byte`/`utf8`/`utf16`/`utf32` is a **contiguous range** `[0, max_cp]`, which
is why one scalar suffices. **A codepage's repertoire is 256 code points
SCATTERED across Unicode** — KOI8-R holds ASCII plus a block of Cyrillic — so
`[^a]` under it complements within an arbitrary SET, and no maximum describes
it.

> `max_cp` is therefore the **contiguous-repertoire form** of a more general
> question ("what does this encoding's universe contain"), and a codepage
> backend is what would generalize it — most cheaply by letting the field be a
> repertoire descriptor whose contiguous case is a range. **This design keeps
> the scalar** (D77: every encoding this milestone and its named successors
> need has a contiguous repertoire) and names the trigger rather than building
> for it. **The seam's shape is unaffected either way** — it is one field's
> type, not an interface.

**MULTI-BYTE LEGACY ENCODINGS (Shift-JIS, GB18030) RIDE THE SAME
CharSet→UNIT-SEQUENCE LOWERING** — the shape transfers exactly as it does for
UTF-16 (§5.7.1). Two costs are theirs alone and are worth stating so nobody
prices them at UTF-8's rate:

1. **THE MAPPING IS A TABLE, NOT ARITHMETIC — so the lowering itself becomes a
   DATA SOURCE.** UTF-8/16/32 compute a code point's units from the code point
   (§2.3's mixed-radix decomposition); Shift-JIS and GB18030 need a vendored
   mapping table. **This is exactly where R-ASKS-3's two halves meet**: such a
   backend's lowering is a `third_party/` source compiled to generated tables
   by the same generic derivation §3.3.2 names, and it is the second instance
   that rule exists for.
2. **THE DECOMPOSITION STOPS BEING SMALL, because it depends on ORDER
   PRESERVATION nobody stated.** §2.3's efficiency — an interval becomes *"a
   small set of byte-range sequences"* — rests on the encoding being
   **monotone**: contiguous code points encode to contiguous unit sequences,
   so a range stays a range. UTF-8 and UTF-32 are monotone; **UTF-16 is not**
   (astral code points encode as surrogate pairs numerically below
   U+E000–U+FFFF's units), and legacy encodings are wildly non-monotone. A
   non-monotone encoding turns one interval into many alternatives, so
   §2.4.1's `ncls` and entry counts — already the binding term — get worse in
   a way this document has measured for nobody. **That is the number a legacy
   backend owes before it is chartered**, and §2.4.1's probe is the instrument
   that would produce it.

**Blocker (1) of §5.7.2 applies to them too, and harder**: Shift-JIS is not
self-synchronizing either — a trail byte can hold a value that is also a lead
byte — so the prefilter's usefulness argument fails for the same reason it
fails for UTF-16, which is the point at which "self-synchronization" stops
looking like a UTF-8 detail and starts looking like the property §6.3 should
have named from the beginning.

#### 5.7.4 D77: built when a consumer exists, and here is where one comes from

**No UTF-16/32 backend is built, designed, or scheduled**, and §11 keeps it
out of scope. D77's rule is that a mechanism is built when a measurement or a
consumer demands it, and this one has neither today — `[DD-12] (6)`'s original
reason (no consumer asks) is unchanged and is still the operative one.

**Where a consumer would come from, so the trigger is nameable rather than
hypothetical**: `[V-A]` (the PCRE2 compatibility layer, including the POSIX
`regex.h` shim) and `[V-B]` (bindings for other languages) — **and, for the
codepage family, a caller with legacy data rather than a legacy runtime**
(mainframe EBCDIC records, KOI8 archives), which is a different and more
plausible consumer than "someone wants EBCDIC regexes". A caller who
already speaks PCRE2 may hold `PCRE2_SPTR16` buffers, and a language binding
for a runtime whose native string is UTF-16 — Java, C#, JavaScript — hands
pcrec UTF-16 without being asked. **That is the shape of a real consumer**:
not "someone wants UTF-16 regexes" but "a caller already has UTF-16 bytes and
transcoding them is the cost we would be imposing." Neither row is started.

**What this note buys, stated plainly**: if that day comes, the answer is a
lowering instance, a registry row or two, §5.7.2's three re-derivations, and —
for a codepage — a repertoire descriptor where §2.7.1 has a scalar. **Not** a
second engine and not a re-architecture. And if it does not come,
this section cost a page and prevented a future reader from concluding, from
§11's one line, that the door had been shut.

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

#### 7.4.1 ASK 6 RULED (2026-09-04): the small amendment route

> **Frank's ruling**: the small `rxt_format.md` amendment route. The manager
> charters it with the implementation waves; **spelling is the manager's**,
> per the standing `[DD-13b]` ruling; **and §7.1.1's match-units predicate is
> the input.**

**This lane still does not write the spec** — that is the ruling's own
division — but it owes the amendment a correct statement of what must be
expressible, and **r54 changed that statement**. The first version asked for
a third value beside python-verifiable and `# pcre2-only`:
*python-verifiable through the `str` engine only.* §7.1.1 found that the
oracle question is **not a three-valued label at all**:

> A cell's oracle depends on **which unit the candidate oracle counts in**.
> python-`bytes` verifies a `UCP-SPLIT` cell **unless the expected answer is a
> MATCH that consumes a multi-byte character** — the complemented forms
> (`\W`, `\D`, `\S`, `[^…]`) over non-ASCII, and only when they match.
> `\W` over a Greek letter is `UCP-SPLIT` by VERDICT and `PCRE2-ONLY` by
> ORACLE, and the two are different partitions of the same table.

So the amendment has **at least four** states to express, not three
(python-str, python-bytes, either, neither), and the honest observation is
that a flat label set may be the wrong shape entirely — the fact is a
property of the CELL's expected answer, which the format could in principle
derive rather than have an author declare. **This design does not know which
of those the format should do**, and §10 records that as an open item rather
than guessing on the format owner's behalf. What it hands the amendment is
§7.1.1's predicate and the measured 7-of-8 that produced it.

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

#### 8.1.1 The gate does NOT stand alone (r54 BLOCKING C1)

**ACCEPTED.** Stage 1 is a pure refactor whose acceptance was *one* instrument
— byte-identity — and **byte-identity is exactly the bar a NO-OP passes.**
A stage-1 branch that changed nothing at all, or that built the interval
pipeline and then never used it, scores 100%. `learnings.md` §4 names the
combination this house has found necessary rather than either half:

> *"The nets that work: structural/codegen checks, byte-identity gates against
> a pristine `git archive HEAD` build, output-preserving differentials with
> positive controls…"*

The gate is the second of those. Stage 1 gains the first, and **the three
checks below are what a no-op refactor fails**:

**CHECK 1 — THE INTERVAL PIPELINE EXISTS AND EVERY PRODUCER GOES THROUGH IT.**
A structural check that `struct Ast`'s `A_CLASS` payload is the interval form
(no `bits[32]` member survives), and that the byte-tier producers
(`\d`, `\w`, `\s`, POSIX classes, ranges, literals, `.`, the two negation
sites) reach it. Its failing direction is the whole point: **on today's tree
it must go RED**, and the wave that lands stage 1 runs it against
`git archive HEAD` first to prove that.

**CHECK 2 — THE RENDER HELPER IS THE ONLY READER, AND IT ASSERTS.** §2.1.4's
`pcrec_cls_bits` is the sole path from a class node to a 32-byte bitmap. The
check is a **grep with a floor and a negative needle**: every site in §2.5.1's
AFTER rows calls it (count ≥ 6), and **no site outside it reads `u.cls.bits`
directly** — the negative half is the one that catches E1's recurrence, since
a new emitter site added later would otherwise reintroduce exactly the read
the panel found. `registry_check`'s own count/manifest guard is the model
(R15), and the negative-needle discipline is R15's too.

**CHECK 3 — THE STAMP CENSUS, and it belongs to stage 2 rather than stage 1.**
Over the corpus compiled under BOTH encodings, record per artifact:
`RX_ENGINE`/`RX_ENGINE_WHY` (§6.2.1's `[SEL-1]` fallback), `RX_DFA_TABLE`
(§2.4.1's premultiplied decline), `RX_VM_ISLANDS` (§6.4), `RX_VM_STRATS`
(§2.5.1's possessify declines) and the emitted size. **This is a MANIFEST, not
a threshold** — r49's ruling that a check pinned to a count expires when the
count is re-measured — so it names the shape (*"no `byte`-encoding artifact's
stamps move; every `utf8` artifact whose stamps differ from its `byte` twin is
listed with its reason"*) and the list is a reviewed diff. It is the only
instrument that would see §2.4.1's premul decline, §6.2.1's engine change or
§6.4's island claim, **none of which changes an answer.**

#### 8.1.2 The positive control's FLOORS (r54 BLOCKING C2)

**ACCEPTED — K35's shape, and the design had it.** "The pinned pre-module
binary refuses every pattern the new corpus adds" is a control with **no
stated population**, so it passes identically whether the corpus adds four
hundred such patterns or zero. `lookaround_design.md` §9.2 is the model, and
it states its own: *"Floors: ≥ 700 lookaround-free patterns, ≥ 60
lookaround-bearing."*

**The floors, per stage**, derived from §8.3's population and stated so a
corpus that silently stops reaching the control fails rather than passes:

| stage | the control | floor |
|---|---|---|
| 1 | (none — stage 1 adds no pattern the old binary refuses; **that is why §8.1.1's structural checks are stage 1's real control**, and saying so is C1's answer) | n/a |
| 2 | pinned pre-M5 binary REFUSES every `-e utf8` and every `\x{>FF}` pattern | **≥ 200** utf8-bearing, **≥ 2,800** byte-encoding patterns unchanged |
| 3 | …refuses every `\p{…}` pattern | **≥ 150** `\p`-bearing |
| 4 | …refuses every non-ASCII caseless pattern the fold corpus adds | **≥ 60** fold-bearing |
| 5 | …refuses every script/`scx` pattern | **≥ 40** script-bearing |

and in every stage the control must additionally read `ctl_bad == 0` — the
pre-module binary refuses **all** of them and miscompiles **none** — which is
`run_backref_identity.sh`'s own shape and is what proves the reference is a
different compiler rather than a rebuild of the same tree compared with
itself.

**A floor is a floor and not a target.** Each is set at roughly 70% of §8.3's
own sized population for that stage, so ordinary authoring variance does not
trip it and a corpus that loses a third of an axis does.

### 8.2 The sabotage rows

One per load-bearing claim, following D69's shape.

> **REVISED AT r54 (BLOCKING C3, MUST-FIX C4).** The first version's table had
> **no `SAB_REACH`/`SAB_REACH_POP` on any row**, which is `[MECH-REACH]`'s
> standing obligation since 2026-08-25 and which
> `opt5_step2_twopass.md` (S218-S222) already shows adopted at BIRTH rather
> than retrofitted. It also left **S-U8 assigned to no stage's acceptance**.
> Both fixed below; the table gains three columns and two rows.

**WHY A REACH DECLARATION AT BIRTH IS NOT PAPERWORK.** A sabotage row proves a
check can go red. `SAB_REACH` proves the WITNESS still arrives at the SITE,
and `SAB_REACH_POP` proves the POPULATION is still there — on a **clean
reference tree, before the sabotage** (`tests/mech/CLAUDE.md`). Without them a
row silently becomes vacuous when the corpus moves, and the matrix reports
DETECTED for a check nothing reaches. **This milestone is unusually exposed to
that**: eight of these ten rows are invisible under `--encoding=byte` by
construction, so their whole population lives in a corpus that does not exist
until stage 2 — precisely the shape `lookaround_measurements`' own ninth
instrument defect records ("a sweep population that could not contain a
qualifying shape, reporting 0 qualifying over a space in which 0 was the only
possible answer").

| # | claim | sabotage | why only this instrument sees it | `SAB_REACH` (clean-tree witness) | `SAB_REACH_POP` (`FILE\|EREGEX\|MIN`) | stage |
|---|---|---|---|---|---|---|
| S-U1 | the fold is applied BEFORE negation (§4.3) | swap the order in the one constructor | both orders produce case-closed sets; only behaviour on `[^k]`/U+212A differs | `pcrec -e utf8 '(?i)[^k]'` compiles and its artifact rejects `E2 84 AA` | `tests/utf8/fold.rxt` \| `^pattern .*\(\?i\).*\[\^` \| **6** | 4 |
| S-U2 | the fold is a CLOSURE, not a pairing (§4.2a) | replace the closure with one round of "add the partner" | `k`↔`K` still works; only U+212A fails | artifact for `(?i)k` matches `E2 84 AA` | `tests/utf8/fold.rxt` \| `^pattern .*\(\?i\)` \| **20** | 4 |
| S-U3 | the fold happens on CODE POINTS, before lowering (§4.2c) | move it after the byte lowering | `[a-z]` still folds to `[A-Z]`; only U+212A/U+017F are lost | artifact for `(?i)[a-z]` matches `E2 84 AA` **and** `C5 BF` | `tests/utf8/fold.rxt` \| `^pattern .*\[a-z\]` \| **4** | 4 |
| S-U4 | `la_widths` uses CHARACTER width (§5.6) — **sabotage ONE timing only** (§5.6.4) | point the **parse hook** back at a byte-width walk, leaving `postresolve` on the character pair | every ASCII lookbehind still compiles; only `(?<=[a\x{3b1}])` refuses, **and only through the hook** — a call-bearing body still compiles, so the row detects the DIVERGENCE between the two paths | `pcrec -e utf8 --features all '(?<=[a\x{3b1}])x'` compiles | `tests/utf8/lookbehind.rxt` \| `^pattern .*\(\?<` \| **18** | 2 |
| S-U5 | `back_step` walks characters (§5.2) | make it `pos - k` | identical under `byte`; under utf8 it lands mid-character | artifact for `(?<=α)x` matches `CE B1 78` | `tests/utf8/lookbehind.rxt` \| `^pattern .*\(\?<` \| **18** | 2 |
| **S-U9** | **`back_step` validates each run's DECLARED LENGTH (§5.2.1)** | **delete the `want != end - pos` test alone** | **invisible on every well-formed subject; on `(?<!.)` over `C2 80 80` the unsabotaged artifact answers, the sabotaged one returns `RX_R_INTERNAL` — an ABORT at a composed site, not a wrong answer** | **artifact for `(?<!.)x` returns 0 (no abort) on `C2 80 80 78`** | `tests/utf8/invalid.rxt` \| `^pattern .*\(\?<!` \| **6** | 2 |
| S-U6 | `next_pos` finds a boundary (§5.1) | make it `pos + 1` | only a find-all over an empty match on a multi-byte subject sees it | find-all over `αβγ` with `pcrec -e utf8 ''` reports 4 matches | `tests/utf8/nextpos.rxt` \| `^pattern` \| **14** | 2 |
| S-U7 | the surrogate range is excluded from every lowered set (§2.3) | include it | **at the SUBJECT level** — a compiled `.`-artifact must REJECT `ED A0 BD` (§8.3's C5 note) | artifact for `-e utf8 '^.$'` rejects `ED A0 BD` | `tests/utf8/invalid.rxt` \| `^m\|^n .*ED A0` \| **9** | 2 |
| S-U8 | `pcrec_minw` is per-class exact (§5.6.1) | return the old constant 1 | **changes no answer** — a looser MRL bound prunes less and can never delete a match. Only a stamp-reading check sees it: the `RX_PRUNE_*` literal moves | `pcrec -e utf8 --emit-ir '(?:α){3}x'` prints a prune bound > 3 | `tests/utf8/mrl.rxt` \| `^pattern` \| **8** | **2** (C4) |
| **S-U11** | **the standing 1:n fold check is live (§4.1.1, ASK 3 RULED)** | **invert one of the 22 assertions** (assert that ß/SS DOES match caseless) | the check's subject is **libpcre2, not pcrec**, so no corpus cell and no identity gate can see it — the only row here whose sabotage is a change to a check's own expectation rather than to the compiler | `run_pc4.sh` (or the PC-3 arm) prints the fold-cell block and its count | `tests/registry/pc4_check.c` \| `1:n fold` \| **22** | **1** |
| **S-U10** | **the `cwmin` fixpoint runs to settlement (§5.6.2)** | **`break` after one round** (S171's own shape, re-aimed) | a one-round fixpoint is right for a call graph of depth 1, so only a lookbehind whose body calls a group that itself calls one sees it | `pcrec -e utf8 --features all '(?<=(?1))x(a(?2))(b)'` compiles | `tests/utf8/lookbehind.rxt` \| `^pattern .*\(\?<.*\(\?[0-9&]` \| **4** | 2 |

**S-U11 IS THE ODD ONE AND IS DELIBERATELY IN THIS TABLE.** Every other row
sabotages the COMPILER and asks whether a check notices. S-U11 sabotages a
CHECK'S OWN EXPECTATION and asks whether the matrix notices — because the fact
it defends is a fact about libpcre2, which no amount of pcrec-side testing can
reach. It is in this table rather than filed elsewhere so that the count of
load-bearing claims and the count of sabotage rows stay equal, which is the
property D69's shape exists for. Its `SAB_REACH_POP` floor of **22** is the
number §4.1.1 specifies (11 cells × 2 option words); **a floor of 11 would
pass a check that had silently dropped the UCP arm**, which is the arm §4.1
measured second and a later reader is likeliest to lose.

**S-U8 IS THE ONE WORTH NOTICING, AND IT WAS ORPHANED (C4).** It changes no
answer at all, so neither the corpus nor the identity gate can see it — the
S68 shape. It is now **assigned to stage 2's acceptance** alongside
S-U4/5/6/7/9/10, and its detector is named: §8.1.1's **check 3**, the stamp
census, which is the only instrument in the plan that reads a number no answer
depends on. An unassigned sabotage row is a row nobody runs, which is worse
than no row, because it reads as coverage.

**Note also what S-U8 lost in the r54 revision**: the first version's claim was
about `minw`/`maxw` together, and §5.6.2 retires `pcrec_maxw`. The row is
`minw`-only now, and `maxw`'s replacement is covered by S-U4 (the character
pair's consumer) and S-U10 (its fixpoint).

**Every row above is `SAB_EXPECT=DETECTED` at birth except none** — there is no
`UNREACHED` row in this plan, deliberately. Where `opt5i` had to ship S219
`UNREACHED` with a derivation, every row here has a witness that exists once
its stage's corpus does, which is why the `stage` column is part of the table:
a row whose stage has not landed is not yet added, rather than added and
declared unreachable.

### 8.3 Population sizing for the blinded corpus

> **RE-DERIVED AT r54 (MUST-FIX C6, C7).** The first version's table compared
> its total against **mismatched units** — "~420 cells, comparable to
> lookaround's 457 blocks / 1,819 cases" puts one number beside two of
> different kinds — and **five of its nine rows showed no arithmetic**, which
> is ASSERTED dressed as sized. Both fixed: the unit is stated, the
> multiplier is stated, and every row shows its derivation.

**THE UNIT, first, because C6 is really about that.** `lookaround`'s §10.1
separates **457 BLOCKS** from **1,819 CASES** with the multiplier shown
(≈ 6 × 9 × 7 ≈ 380 blocks from its axes, ~4 subjects per block). A `.rxt`
**block** is one `pattern` plus its directives; a **case** is one `m`/`n`/`g`
line. **This design sizes in BLOCKS**, and the case count follows from a
subjects-per-block multiplier that has to be stated rather than assumed:

> **Subjects per block: 4** — for a UTF-8 axis the discriminating subjects are
> a member, a non-member, a member at a different encoded length, and a
> boundary or ill-formed neighbour. That is the smallest set that
> distinguishes "the class is right" from "the class is right for one-byte
> members", which is the failure §2.3's decomposition actually risks.

| axis | derivation | blocks | cases (×4) |
|---|---|---|---|
| encoded-length coverage | 4 lengths × 4 contexts (literal / class / quantified / negated) × 4 shapes (bare, in a class, in a range, after a quantifier) | **64** | 256 |
| the 1-byte↔multi-byte class boundary (`[a\x{3b1}]`) | 6 boundary shapes × 4 spellings (explicit `\x{}`, literal UTF-8, range endpoint, `\p`) | **24** | 96 |
| invalid UTF-8 | 9 measured ill-formed kinds × 3 positions (before / after / through the bad bytes) | **27** | 108 |
| `\p{…}` general categories | 30 two-letter + 7 one-letter = **37** accepted spellings × 2 polarities (`\p`/`\P`) × 2 (in-member, out-member) = 148, rounded | **150** | 600 |
| `\p` refusals | 30 measured error-147 bodies + 4 block spellings (`InGreek`, `Block=Greek`, `blk=Greek`, `IsGreek`) | **34** | 34 (a refusal has one case) |
| caseless: pairs, cross-block folds, closure, fold-before-negate | 6 measured cross-block pairs + 2 measured non-folds + 4 closure shapes (`k`/`K`/U+212A three ways) + 3 fold-before-negate shapes × 4 spellings ≈ 60 | **60** | 240 |
| caseless 1:n NON-matching | the 11 measured cells of `out/caseless.txt` §2, one block each | **11** | 22 (match + reverse direction) |
| lookbehind over variable-byte-width bodies | the 8 measured bodies of `out/width.txt` §3 × 3 (positive, negative, call-bearing per §5.6.4) | **24** | 96 |
| `next_pos` / find-all over multi-byte subjects | 4 subject shapes × 4 patterns (empty, nullable, anchored, unanchored) + **4 mid-character-`startpos` cells on leading `(?!`/`(?<!`** (§2.6.1) | **20** | 80 |
| **the surrogate SUBJECT witness (C5)** | **3 surrogate encodings (`ED A0 80` low, `ED BF BF` high, a CESU-8 pair) × 3 patterns (`.`, `[^a]`, `\p{L}`)** | **9** | 27 |
| the byte-encoding control arm | every block above re-run under `-e byte`, expecting refusal-or-identity | mirror | mirror |
| **TOTAL** | | **423 blocks** | **≈ 1,559 cases** |

**423 blocks against `lookaround`'s 457 blocks, and ≈1,559 cases against its
1,819** — like against like, which is what C6 asked for, and the comparison
now says something: this corpus is about 93% of the lookaround corpus's size
on both axes, which is the right order for a milestone of comparable surface.

#### 8.3.1 S-U7 needs a SUBJECT witness, not a compile-time one (r54 C5)

**ACCEPTED, and the first version cited the wrong population.** S-U7's claim
is that *the surrogate range is excluded from every lowered set*, and the
sabotage is *include it*. §8.3's original table pointed at the ~27
invalid-UTF-8 cells, and **those are COMPILE-TIME refusals** read from
`out/invalid_utf.txt` — patterns PCRE2 rejects at compile. They cannot see
S-U7, because S-U7 does not change what compiles: it changes what a compiled
automaton **accepts**.

> The witness is a **SUBJECT**: `ED A0 80` … `ED BF BF` (the UTF-8-shaped
> encoding of a surrogate scalar, which is not valid UTF-8 and has no path)
> fed to a compiled `-e utf8 '^.$'`, `'^[^a]$'` and `'^\p{L}$'`. The
> unsabotaged artifact **rejects**; the sabotaged one **accepts**. Nothing in
> a compile-time refusal corpus distinguishes them.

That is the new row in §8.3's table (9 blocks), and it is what S-U7's
`SAB_REACH` in §8.2 asserts.

#### 8.3.2 The D27 extract is CURATED, with an exclusion list (r54 C9)

**ACCEPTED.** The first version named the sections to hand the blinded author
— §2.6, §3.1, §4.1–4.3, §5.6, §7.1 — and named them by NUMBER, which after
this revision is a different set of text than it was when it was written.
`lookaround_design.md` §7.3's curated extract with an explicit negative space
is the model (`la_d27_extract.md` is the artifact).

**INCLUDED** (the promise, and the measured semantics that define it):

- §1.3's construct table — what ships, what refuses, and which module owns it
- §2.6(a)-(e) **and §2.6.1** — the invalid-UTF-8 ruling and the per-entry
  `startpos` promise, both of which are user-visible semantics
- §2.7.3's two-cell refusal rule — `\x{>FF}` under `byte` refuses, `[^a]`
  under `byte` compiles
- §3.1's measured `\p` acceptance surface and §3.4's ship/refuse staging
- §4.1-§4.3 — simple-folding-only, the closure, fold-before-negate
- §5.6's **measured population table** (the 8 variable-byte-width bodies) —
  the *table*, not the resolution
- §7.1 **and §7.1.1** — the verdict tally and the oracle predicate, which the
  author cannot write correct expectations without

**EXCLUDED, and the reason each is excluded is that knowing it would let the
author derive tests from the implementation rather than from the promise —
which is the whole of D27:**

| excluded | why |
|---|---|
| §2.1, §2.1.2-§2.1.4 | the pass position and the render helper — the mechanism, and §2.1.4's assertion is a thing the author might otherwise test FOR rather than testing the behaviour it protects |
| §2.2, §2.3, §2.3.1 | the payload shape and the decomposition. **An author who knows the four-row canonical table writes tests at its boundaries**, which is the code author's alphabet arriving by the back door |
| §2.4, §2.4.1, §2.4.2 | sizing; no promise in it |
| §2.5.1 | the consumer census — names files |
| §2.7.1, §2.7.2 | the universe field and the rejected alternative; the author gets §2.7.3's cells, which are the promise |
| §5.1-§5.5, §5.6's resolution (§5.6.1-§5.6.5) | seam bodies and the width analysis. **§5.2.1's `back_step` body is the sharpest exclusion**: an author holding it writes the `C2 80 80` cell from the code, and that cell is exactly the one D27 exists to have found independently |
| §6 entire | engine and selection consequences |
| §8 entire | the validation plan — an author who knows the sabotage rows writes the corpus that detects them, which inverts the instrument |
| §9, §12, §13 | staging, predictions, brief |

**THE ONE JUDGEMENT CALL, recorded rather than hidden.** §5.6's population
table is IN and §5.6's resolution is OUT, which splits one section. The table
is a measured fact about PCRE2 (*these 8 bodies are fixed-width to 10.46 and
have 1-4 byte widths*) and the author needs it to know that
`(?<=[a\x{3b1}])x` must compile. The resolution is pcrec's mechanism. Cutting
mid-section is what `la_d27_extract.md` already does, and the extract is
**regenerated by re-cutting, never edited independently of this document** —
the rule that file's own header states.

### 8.4 The compatibility question the cross-note names

The `[M5.0]` row asks this design to own the `maxw` change. §5.6 owns it, and
the **compatibility** half is: under `--encoding=byte`, **`pcrec_minw` must
answer exactly what it answers today** for every pattern in the corpus. That
is not an argument, it is §8.1's gate — the MRL bound is baked into emitted
literals (`RX_PRUNE_*`), so a changed bound is a changed artifact and the
byte-identity gate fails. **The gate is the check; no separate instrument is
needed.**

**REVISED AT r54.** The first version wrote *"`pcrec_minw` and `pcrec_maxw`
must answer exactly what they answer today"*, and §5.6.2 **retires
`pcrec_maxw`** — so half of that sentence names a function the change deletes.
The compatibility obligation splits accordingly, and the second half is not
the gate's:

- **`pcrec_minw`** — unchanged answers under `byte`, proved by the identity
  gate through the `RX_PRUNE_*` literals, exactly as above.
- **`pcrec_maxw`'s consumer** — the lookbehind fixed-width rule — must reach
  the same VERDICT on every corpus pattern under `byte` after moving to
  `cwmin`/`cwmax`. Under `byte` one character is one byte, so the two analyses
  are numerically equal and every verdict coincides; but **the artifact does
  not record the verdict**, only its consequence (a refusal, or an emitted
  back-step literal), so the identity gate sees it only where a lookbehind
  exists. The gate's population is therefore the check for lookbehind-bearing
  patterns and **S-U4 is the check for the rest** — which is why §8.2's S-U4
  row carries a `SAB_REACH_POP` floor of 18 rather than trusting the gate to
  have reached the rule at all.

### 8.5 The pcrec-vs-pcrec differential (r54 SHOULD C10)

**ACCEPTED, and the answer is that one EXISTS — the first version simply did
not look for it.** The panel's observation is right and sharp: every recent
module pairs its corpus with a `-fno-X` or two-lowering differential, this one
does not, and **§2.2's single-representation ruling looks like it forecloses
the possibility** — with one representation there is no second lowering to
compare against.

**That reasoning is correct about CLASSES and wrong about the milestone**,
because this design has a second axis that is not a representation choice:

> **THE ENCODING ITSELF IS THE TWO LOWERINGS.** Every ASCII-only pattern has a
> `byte` artifact and a `utf8` artifact, and **on an ASCII-only subject they
> must give the same answer** — same span, same captures, same give-up
> behaviour. The `utf8` artifact reaches that answer through the byte-sequence
> decomposition (a one-byte "sequence" per character) and the `byte` artifact
> through the identity map. Two independently-derived machines, one expected
> answer.

**This is a real differential and it is nearly free**, because its population
is a corpus that already exists: the whole existing `.rxt` corpus, whose
patterns and subjects are ASCII, re-run under `-e utf8`. Its properties:

| | |
|---|---|
| **population** | **MEASURED at this tree: 3,319 of 3,350 blocks** are fully ASCII — pattern and every decoded subject. 1 block is excluded for a non-ASCII pattern, **30 for non-ASCII subjects** |
| **what it catches** | any lowering bug on the one-byte path: an off-by-one in the length split at 0x7F, a mis-set lead-byte range, a start state that consumes its first byte twice (**the exact bug `probe_sizing.py`'s self-check caught, §2.4**) |
| **what it CANNOT catch** | anything the multi-byte path does. It is a control on the boundary case, not a proof of the construction — the new corpus is what tests the rest |
| **its positive control** | the 31 excluded blocks must be excluded **by the harness's own decode**, not by a text scan, and the count is asserted rather than assumed: `ctl_ascii == 3319 && ctl_excluded == 31` |

> **THE POPULATION COUNT HAS A METHOD NOTE, because getting it wrong was one
> line of code away and this house has a name for the failure.** Counting
> "blocks whose bytes are all below 0x80" by scanning the `.rxt` FILES gives
> **3,349 of 3,350, with zero subject exclusions** — and it is wrong, because
> a subject containing a high byte is WRITTEN as an escape (`\xNN`), which is
> ASCII text. Decoding through `tests/harness/verify_rxt.py`'s own parser
> gives 3,319 and finds the **30 subject exclusions the text scan could not
> see** — and those 30 are exactly the blocks most likely to differ between
> the two encodings, i.e. the ones whose exclusion the differential depends
> on. R13's lesson, third recurrence in this document's own lane:
> *counting a population by an instrument that cannot express it counts the
> instrument.* The check reads the corpus the way the harness does, or it does
> not read it.

**AND IT HAS A SECOND ARM WORTH MORE THAN THE FIRST.** §8.1's identity gate
proves the `byte` artifact did not move. This differential proves the `utf8`
artifact AGREES with it. **Together they are transitive to the pre-M5
binary** — a `utf8` artifact's answers are pinned to a compiler that predates
the milestone entirely, over 3,319 patterns, without any new expectation being
authored. That is a stronger statement than either half, and it costs one
harness axis.

**Where it goes**: stage 2's acceptance, beside the identity gate, as a new
`--encoding=utf8` arm of `make test-axes` (which already walks the
optimization-axis product for ANSWER identity and is the right home — its own
`docs/testing.md` entry calls it "answer-identical to default over the whole
corpus"). **§9.2's stage-2 acceptance gains it**, and §12 gains **P-11**: the
ASCII corpus is answer-identical under `-e byte` and `-e utf8`. Refuted by one
differing cell — and the likeliest cause, stated so a debugger starts in the
right place, is the length-split boundary at exactly 0x7F.

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
interpretation. **This paragraph was right and §12 P-1 contradicted it; r54
resolved the contradiction in this paragraph's favour** (§12 P-1(iii)).

**WHAT r54 SETTLED, AND WHAT IT DID NOT.** The first version left *"whether it
lives in `src/gen/enc/` … or in `src/ir/` behind a table of function
pointers"* as a question for the panel, and §10 listed it as unresolved. **It
is resolved, and not by choosing** — the question was mis-posed. §2.1.2 shows
**WHEN the lowering runs is forced** to one line of `compile.c`, from three
ordering constraints in the shipped tree. Given that, *where the code lives*
follows from the rule §2.1 already states — a per-backend instance, one
instance per backend, dispatched through the encoding — rather than being an
independent decision anyone needs to rule on. The lowering's **call site** is
`compile.c:1000`; its **bodies** live with their backends in `src/gen/enc/`,
beside the residual text that is the other thing a backend owns.

**What is NOT negotiable is unchanged and is the only part that was ever
DD-12 (7)'s**: no shared file acquires an `if (enc == UTF8)`. The dispatch at
`compile.c:1000` selects an instance from the encoding; it does not branch on
which one. §12 P-1′ is that promise made falsifiable by grep, replacing the
P-1 that predicted the wrong rule.

### 9.2 The staged landing order

Five stages, each with an acceptance that can be run before the next opens.

**STAGE 1 — the CharSet widening.** `A_CLASS` becomes intervals; every
producer (`\d`, `\w`, POSIX classes, ranges, literals, `.`, **and both
negation sites, complementing within `[0, MAXCP(enc)]` per §2.7.1**) emits
intervals; the byte backend's lowering turns intervals back into the 32-byte
bitmap through §2.1.4's render helper. `\x{...}` above 0xFF still refuses.
**Nothing user-visible changes.**

*Acceptance:* §8.1's identity gate at 100% byte-identity on all four axes —
the whole corpus, since every pattern goes through this — **AND §8.1.1's
checks 1 and 2**, which are what a no-op refactor fails and the gate does not
(r54 C1). Check 1 must be demonstrated RED against `git archive HEAD` in the
same wave, or it is a check nobody has seen fail. **`PcrecEnc.max_cp` lands
here**, not in stage 2, because stage 1's negation needs it — under `byte` it
reads `0xFF` and every answer is unchanged, which is the whole of §2.7.1's
byte-identity argument.

**AND THE STANDING 1:n FOLD CHECK LANDS HERE TOO** (§4.1.1, ASK 3 RULED), with
sabotage row **S-U11** — four stages before the fold it defends. Its subject is
libpcre2, not pcrec, so it depends on nothing stage 1 builds, and deferring it
to stage 4 would leave the milestone's most load-bearing measured premise
unwatched for three stages.

**STAGE 2 — the utf8 backend.** `enc_utf8.c` (four residual bodies,
`back_step` per §5.2.1), the byte-sequence lowering placed at
`compile.c:1000` per §2.1.2 — and now GENUINELY REBUILDING (stage 1's byte
instance was a no-op) **UNDER THE SPLICE-IN-PLACE INVARIANT**: the
decomposition replaces a leaf `A_CLASS` by mutating the parent's child pointer
and never reallocates a node that is or contains a group root (§2.1.2
constraint 2 as corrected). `\x{...}` above 0xFF under `--encoding=utf8`,
`-e utf8` starts compiling. §5.6's `pcrec_cwmin`/`pcrec_cwmax` land here —
at **both timings together** (§5.6.4) — because lookbehind is already shipped
and would otherwise be wrong the moment utf8 compiles; `pcrec_maxw` and its
chain retire in the same change (§5.6.2, incl. the test-side census —
`tests/mrl/maxw_check.c`, `run_mrl_tests.sh` §8 re-aimed at `cwmax`, S136),
with S171 re-pointed. **AND it must resolve `u.rep.revbody`** — stage 1
measured 413 corpus classes whose reversed copy (`revdet`) is built BEFORE
the lowering and is NOT visited by the splice walk, so a stage-2
decomposition that ignores it lowers the forward class and leaves the reverse
one byte-wise (inert in stage 1, a miscompile in stage 2); the lane's finding,
loud never silent.

*Acceptance:* the UTF `.rxt` corpus green; identity gate still 100% on `byte`;
**the group-root-address check** (no group-root node's address moves across
`pcrec_lower_enc` — the splice-in-place invariant made mechanical, R2); the
`u.rep.revbody` resolution proven (the 413 classes' reverse machines lowered
consistently with their forward ones);
DD-12 (7)(a)'s **two M5-time structural checks** — hot-loop shape identity
ASCII-vs-UTF-8, and the second-backend validation of D58's "revisit-when"
names; **§8.5's ASCII-corpus encoding differential** at 3,319 blocks / 0
divergences with its 31-block exclusion asserted; **§8.1.1's check 3**, the
stamp census, reviewed as a diff rather than as a threshold; and sabotage rows
**S-U4, S-U5, S-U6, S-U7, S-U8, S-U9, S-U10** detected (r54 C3/C4 — S-U8 and
the two new rows are stage 2's, and S-U8's detector is check 3, not the
corpus).

> **STAGE 2's CORPUS BAR HAD A PRECONDITION (r54 C11) — NOW DISCHARGED.**
> Roughly **27 of its 423 blocks** — the invalid-UTF-8 axis, §8.3's third row
> — encode §2.6's ruling that an ill-formed sequence matches nothing, and that
> ruling was §14 ASK 1: Frank's, not this design's. Had it been ruled the
> other way (an error return, or an opt-in validation entry point), those 27
> blocks' expectations would INVERT and the seam would gain a fifth entry — so
> stage 2 could not open until it was answered, not because the code depended
> on it but because the blinded author would have written 27 blocks against a
> promise that had changed.
>
> **RULED 2026-09-04: AGREED** (§14 ASK 1). Ill-formed matches nothing, no
> validation pass, no error return. **The precondition is discharged, the 27
> blocks can be written, §8.3.2's extract is safe to cut, and no fifth seam
> entry is owed.** The paragraph is kept rather than deleted because the
> DEPENDENCY is still real and a future re-opening of ASK 1 re-opens these 27
> blocks with it.
>
> **Stage 2's acceptance additionally gains ASK 5's addendum** (Frank, same
> ruling set): the `startpos`-at-mid-character cells are **corpus rows checked
> against the oracle**, not design assumptions. §2.6.1.1 is the measurement
> they are written from — and it is worth noting for whoever writes them that
> the three oracle columns there give three different answers, so a cell that
> names no options word names nothing.

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
  is a user-visible semantic. **r54 adds a consequence**: §9.2 makes it a
  PRECONDITION on stage 2 opening, because ~27 corpus blocks encode it.
- ~~**Where the encoding lowering lives** — §9.1.~~ **RESOLVED AT r54 (E1).**
  Not by choosing between `src/gen/enc/` and `src/ir/`, which was the wrong
  question: **WHEN it runs is forced** (§2.1.2, between `compile.c:999` and
  `:1018`), and where the code lives follows from the per-backend-instance
  rule rather than being an independent decision. The panel does not need to
  rule; the tree already did.
- ~~**Whether one parameterised width function beats two** — §5.6.~~
  **NARROWED AT r54.** §5.6.2 retires `pcrec_maxw`, so the question is no
  longer "two functions or one parameterised one" but "does `cwmin`/`cwmax`
  share a walk with `minw`". The design says no, on `mrl.c`'s exhaustive-switch
  argument (§5.6.5), and this stays open for Frank if he disagrees — but the
  scope shrank with the chain.
- **The `.rxt` third oracle value** — §7.4, ASK 6, owned by the format. **r54
  makes it larger**: §7.1.1 finds the oracle question is a PREDICATE about
  match units, not a three-valued label, so the format amendment has more to
  express than "python-str-only" and the design does not know what shape that
  should take.

**ADDED AT r54, each a thing this revision surfaced and deliberately did not
settle:**

- **The FILING of the `PcrecEnc` seam change** — ASK 7. The mechanism is
  chosen (§2.7.2); whether it is a D58 addendum or its own row is not.
- **Whether the three DECLINE verdicts (§2.5.1) should be widened at first
  landing.** The design defers under D77 with the measurement named, and the
  measurement cannot run until stage 2 exists. A reader who thinks the verdict
  cost is unacceptable should say so before stage 2, not after.
- **`\p{L}{1,3}`'s premultiplied decline (§2.4.1).** The design records it,
  states the cost precisely, and proposes **no cap change** — 65,535 is a
  `short`-range constraint, not a tuning knob. Whether `[OPT-3]` should gain a
  wider-index form for UTF-8-sized machines is a question for that row, and
  P-5b is the census that would open it.

## 11. Explicitly out of scope

`\X` (extended grapheme clusters) and `\R` — **MEASURED** as module `misc`,
not `unicode-props` (`out/premises.txt` §2). `\X` is the one construct in the
UTF neighbourhood that is genuinely not a class: a grapheme cluster is a
variable-length sequence with its own break algorithm, and it would be the
first construct whose width is unbounded at the character level. It belongs to
its own module and its own design gate.

UTF-16, UTF-32, **and every other encoding** (`[DD-12] (6)`) — **and §5.7 is
the note recording that "out of scope" is not "architecturally foreclosed"**
(Frank's width question, 2026-09-04, widened by R-ASKS-3(b) to codepages and
legacy multi-byte encodings). What transfers (the UCD data, the fold closure,
the character widths, `max_cp`, the entries table, and the lowering's SHAPE —
with units-as-byte-pairs the natural in-architecture form), the three
transfer-blockers a 16/32 author re-checks (**self-synchronization FAILS for
UTF-16**, which is E11's premise stated as the blocker it is; the endianness
axis; surrogates moving from excluded code points to live mechanics), the
codepage and legacy-multi-byte cases (§5.7.3 — a codepage is nearly free and
is what would outgrow `max_cp`'s scalar), and the D77 trigger —
`[V-A]`/`[V-B]` interop, and for codepages a caller with legacy DATA rather
than a legacy runtime. **Still not built, designed or scheduled.** PCRE2's
`PCRE2_UCP` as a pcrec axis (§14 ASK 4, **re-priced at r54** — it costs
`upc_of_class`'s mechanism replaced, not a seam entry added; §5.4.1).
Optimising `ENG_ATTEMPT`'s start loop for character boundaries (§5.5). A
two-value scan arm for the prefilter (§6.3) — measured as an opportunity,
declined under D77 until a UTF corpus exists to measure it on.

**ADDED AT r54, three things this revision deliberately did not build:**

- **Widening `possessify`/`revdet` to interval FIRST-sets** (§2.5.1). They
  DECLINE on any class touching above `0xFF` — a verdict cost, never a
  correctness one, and absent entirely under `--encoding=byte`. Deferred under
  D77 with the measurement named: a form census over a UTF-8 corpus, which
  does not exist until stage 2.
- **Any change to `PREMUL_MAX_ENTRIES` or to `[OPT-3]`'s index width**
  (§2.4.1). `\p{L}{1,3}` exceeds the cap and falls back to the plain table;
  65,535 is a `short`-range constraint rather than a tuning knob, and whether
  `[OPT-3]` should gain a wider-index form is that row's question. P-5b is the
  census that would open it.
- **A `startpos` boundary check at the entries** (§2.6.1). It would be a
  validation branch on every call, encoding-conditional, on the hot path —
  which is what §2.6's ruling declines and DD-12 (7) forbids. The contract
  says `startpos` must be a character boundary; ASK 1 is where that could
  change.

---

## 12. What would refute this — predictions for the panel

Written before the panel rather than after. Each is falsifiable.

- **P-1 — REFUTED AT r54, BY THIS REVISION'S OWN FINDINGS (r54 E15).** The
  prediction read: *"Adding `enc_utf8.c` plus its registry row touches no file
  in `src/core`, `src/gen`, `cli/` or `lib/`."* Three things are wrong with
  it and the third is the one that matters.

  **(i) It was unsatisfiable as WORDED.** `enc_utf8.c` lives in
  `src/gen/enc/`, so adding it touches `src/gen` by construction. The panel's
  restatement — *"no file outside `src/gen/enc/`"* — is what was meant, and
  the file list also omitted **`src/parse/`**, which is where §2.2 and §2.7
  put real work.

  **(ii) Restated, it is REFUTED by three findings of this revision**, each
  naming a file outside `src/gen/enc/`: E1 puts the lowering call in
  `src/core/compile.c` and a render helper at nine sites across `src/ir/`,
  `src/opt/` and `src/gen/` (§2.1, §2.5.1); E2 adds a field to
  `src/gen/enc/enc.h` and changes three sites in `src/parse/parse.c`
  (§2.7.1); E3 retires a function in `src/opt/mrl.c` and re-aims a fixpoint
  in `src/opt/callgraph.c` (§5.6.2).

  **(iii) AND THAT IS NOT THE DESIGN-STOP SIGNAL, because the prediction
  conflated two different rules.** The first version said a refutation *"is
  the design-stop signal DD-12 names"*. It is not. DD-12 (7)'s derailment
  signal is **`if (enc == UTF8)` in a shared file** — a CONDITIONAL on the
  encoding in code that serves every backend. The third-encoding recipe in
  `enc.h` is a separate and narrower promise about the **entries table**, and
  that promise **HOLDS**: four residual entries get UTF-8 bodies under their
  existing signatures, no `PcrecEncEntry` field is added, `pcrec_enc_ready` is
  untouched, both emit functions are untouched (§2.7.2). What the recipe never
  covered is the LOWERING, and §9.1 already said so in its own words — *"the
  recipe does not cover the lowering"* — while §12 P-1 predicted it would.
  **The two sections contradicted each other and §9.1 was right.**

  **P-1 is therefore REPLACED, not repaired**, by the prediction that carries
  the rule that actually matters:

  > **P-1′ — no shared file acquires an encoding CONDITIONAL.** After stage 2,
  > `grep -rn 'ENC_UTF8\|enc == \|enc->id ==' src/` outside `src/gen/enc/`
  > returns nothing but the one dispatch site that selects the backend
  > instance. *Refuted by:* one `if` on the encoding in `src/core`, `src/ir`,
  > `src/opt` or `src/gen` outside `enc/`. **That** is DD-12 (7)'s signal, and
  > unlike P-1 it is a property this design can actually keep.

  **This is the design's own prediction mechanism working**, and it is worth
  saying plainly: P-1 was written before the panel, it was falsifiable, and it
  was falsified — by reading `compile.c` rather than by an argument. §12's
  value is entirely in that being possible.
- **P-2 — the identity gate is 100% at stage 1.** *Refuted by:* one
  non-identical artifact. The likeliest cause is an ordering difference in
  interval→bitmap conversion for a class whose producers overlap.
- **P-3 — pcrec's own lowering produces state counts within 2× of
  `out/sizing.txt`.** *Refuted by:* a `\p{L}` DFA over 566 states. The
  prototype shares no code with pcrec, so this is a real prediction.
- **P-4 — SPLIT INTO TWO, one per leg (r54 E12, §5.4.1).** The first version
  stated one prediction where the position rests on two facts that fail under
  the same trigger but with opposite visibility.
  - **P-4a — the PREDICATE agrees.** Without UCP, no subject exists where
    "is this byte a word byte" and "is this character a word character"
    disagree under `--encoding=utf8` at `\w = [A-Za-z0-9_]`. *Refuted by:* one
    such subject; the instrument is a sweep over multi-byte characters
    adjacent to word characters. I believe none exists.
  - **P-4b — the REPRESENTATIVE is exact.** Every equivalence class in
    `Dfa.clsmap` is homogeneous in word-ness, so `upc_of_class`'s
    `d->rep[c]` test is a proof and not a sample. *Refuted by:* one
    `--encoding=utf8` machine with an equivalence class containing both a word
    byte and a non-word byte. **This one has an assertion, not just a
    prediction**: `dfa.c:173`'s `refine_by` establishes it and nothing checks
    it, so stage 2 adds the assertion at `upc_of_class` — the cheapest
    possible instrument for the leg that fails silently.
- **P-5 — RE-STATED IN THE BINDING CAPS' UNITS (r54 E6, §2.4.1).** The first
  version predicted about **states**, which §2.4.1 shows is not the unit that
  binds. Three sub-predictions, in increasing order of how much I doubt them:
  - **P-5a (states)** — no corpus pattern's minimised DFA hits
    `PCREC_MAX_DFA_STATES_TABLE` (32,000) under `utf8` having cleared it under
    `byte`. *Refuted by:* one. This one I believe.
  - **P-5b (entries)** — **I EXPECT THIS TO BE REFUTED.** §2.4.1 measures
    `\p{L}{1,3}` at 80,465 entries against `PREMUL_MAX_ENTRIES` 65,535, so any
    corpus pattern of that shape drops off the premultiplied form. The
    prediction is stated in the direction that makes the census meaningful:
    **fewer than 5% of `utf8` artifacts lose `RX_DFA_TABLE`'s premultiplied
    value relative to their `byte` twin.** *Refuted by:* a census above 5%.
    §8.1.1's check 3 is the census, and this is the number it exists to
    produce.
  - **P-5c (bytes)** — no corpus pattern crosses D84's 1,000,000-byte total
    cap under `utf8` having cleared it under `byte`. *Refuted by:* one. §2.4.1
    states plainly that this is the one figure no measurement in this document
    reaches, so it is a prediction in the weakest sense — a thing to go and
    look at, not a thing I have evidence for.
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

**FOUR PREDICTIONS ADDED AT r54**, one per repair that could be wrong in a way
its own section cannot see:

- **P-9 — no subject makes a `(?<!X)` artifact return `RX_R_INTERNAL`**
  (§5.2.1). *Refuted by:* one. This is E4's repair stated as a property rather
  than as a code change, and it is the strongest form the claim can take,
  because `RX_R_INTERNAL` is below `PCREC_ERR_FLOOR` and a composed site traps
  on it — so a refutation is an ABORT, not a wrong answer, and no answer sweep
  finds it. The instrument is a sweep of the nine measured ill-formed kinds ×
  every position × both lookbehind polarities, which is §8.3's invalid-UTF-8
  axis crossed with its lookbehind axis — **a product neither axis generates
  on its own**, which is why it is written here.
- **P-10 — the VM's replication product does not move** (§6.4). No corpus
  pattern's VM artifact crosses `PCREC_MAX_VM_REPLICATION_PRODUCT` (131,072)
  under `utf8` having cleared it under `byte`. *Refuted by:* one — **and §6.4
  predicts `\p{L}{1,50}` will refute it** the moment such a pattern exists,
  since a ~2,600-node body at 50 copies crosses. The prediction is stated
  anyway because the question that matters is whether it happens on the
  CORPUS, i.e. on shapes people write, or only on shapes constructed to break
  it.
- **P-11 — the ASCII corpus is answer-identical across encodings** (§8.5).
  3,319 blocks, `-e byte` against `-e utf8`, 0 divergences. *Refuted by:* one
  differing cell — and the likeliest cause, stated so a debugger starts in the
  right place, is the length-split boundary at exactly `0x7F`.
- **P-12 — the lowering's position is the only one that works** (§2.1.2).
  Each of the three ordering constraints is load-bearing: moving the lowering
  above `pcrec_callgraph_build` (`:961`) produces a stale `.body` on a
  call-bearing pattern whose lookbehind contains a class, and moving it below
  `pcrec_postresolve` (`:999`) makes `cwmax` answer 2 for a two-byte character.
  *Refuted by:* a working pass order this document did not consider — which is
  the most valuable thing a reader could find here, since §2.1.3 pays a real
  price (three passes widened or declined) for constraint 2 alone.

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
   **And r54 adds the sharper form of the same rule**: §8.5 counts the ASCII
   corpus at 3,319 blocks through the harness's own parser, where the obvious
   text scan says 3,349 and misses 30 — so "state your population" is not
   enough, the instrument that counts it must be able to express what it is
   counting.

**FOUR OBLIGATIONS ADDED AT r54**, each because a repair in this revision is
the kind of thing an implementation wave silently drops:

4. **The lowering's SPLICE-IN-PLACE INVARIANT is a reviewable fact, not an
   implementation detail.** [P-12 DISCHARGED, 2026-09-05, stage-1 lane utf8s1:
   a constraint WAS wrong — the original obligation asked a wave that moved
   the pass to justify itself against three positional constraints, and the
   measurement found constraint 2 mis-stated; the reviewable fact is now the
   PROPERTY (§2.1.2 constraint 2 as corrected), not the position.] The pass
   splices in place and never reallocates a node that is or contains a group
   root; a wave that makes it REBUILD instead owes §4's recursion-artifact
   measurement a new answer (it differs on 45 of 179 at :1000). The
   pass-chain comment at the call site states the invariant it upholds, in
   the style `compile.c`'s existing pass comments already use.
5. **`pcrec_cls_bits`'s assertion ships ENABLED, or §8.1.1's check 2 is the
   only thing standing between the tree and E1's recurrence.** An assertion
   compiled out in the build everyone runs is a comment.
6. **Both width timings move in ONE change** (§5.6.4), and `pcrec_maxw`'s
   retirement is part of that change rather than a follow-up. A tree with
   `la_widths` on the character pair and `pcrec_maxw` still present is a tree
   with a dead analysis that a later reader will assume is live. The
   retirement INCLUDES the test side (§5.6.2, the r54 verifier's insisted
   addition): `tests/mrl/maxw_check.c` + `run_mrl_tests.sh` section 8
   (re-aimed at `pcrec_cwmax`), S136's re-aim, and the two CLAUDE.md
   entries documenting the instrument — same change, never a follow-up.
7. **Every sabotage row is born with its `SAB_REACH`/`SAB_REACH_POP`**
   (§8.2), not retrofitted. `[MECH-REACH]` has been standing since
   2026-08-25 and `opt5_step2_twopass.md` is the precedent for adopting it at
   birth; this milestone is unusually exposed because eight of its ten rows
   have no population at all until stage 2's corpus exists.

---

## 14. ASKs for Frank

**Seven** (r54 added ASK 7). None is a ruling contradiction; each is a decision
this lane deliberately did not take.

> **FOUR ARE NOW RULED (2026-09-04, Frank, relayed by the manager into
> `docs/dev/lanes/utf8design_rulings.md` while this revision was running).**
> ASK 1 **AGREED**, ASK 2 **AGREED reluctantly** with a documentation
> obligation, ASK 4 **RULED** (no axis at M5, door explicitly open), ASK 5
> **AGREED** with a validate-against-oracles addendum this lane discharged.
> **ASK 3 and ASK 6 remain OPEN**; the manager's recommendations are recorded
> at each. Each ruling is written into its own ASK below AND into the section
> it governs, rather than only here — a ruling that lives only in the ASK list
> is a ruling the implementation wave will not find.

**ASK 1 — invalid UTF-8 semantics (§2.6). RULED 2026-09-04: AGREED.**

> **Frank's ruling, relayed by the manager**: ill-formed matches nothing, no
> validation pass, no error return. **The design's proposal is the ruling.**
> So §2.6's ruling block is no longer a proposal, §9.2's stage-2 precondition
> (r54 C11) is **DISCHARGED**, the ~27 invalid-UTF blocks of §8.3 can be
> written, and §8.3.2's extract is safe to cut. The `--no-validate` axis stays
> dead for §2.6's own reason — there is no validation to switch off — and D18
> keeps its earn-its-axis rule intact.
>
> **Two obligations follow and are recorded here rather than left implicit**:
> the divergence from PCRE2's default `PCRE2_UTF` mode is now a RULED,
> user-visible semantic and belongs in `docs/spec/match_api.md` in stage 2's
> own change (D80, §13 obligation 1); and §2.6.1's per-entry `startpos`
> promise rides with it, since both describe what the artifact does at a
> position PCRE2 would refuse.

The design proposed that a
pcrec UTF-8 artifact treats an ill-formed sequence as **matching nothing**,
with no validation pass and no error return — which is what the automaton does
for free, what `PCRE2_MATCH_INVALID_UTF` does, and what M3 streaming requires.
It **diverges from PCRE2's default `PCRE2_UTF` mode**, which reports an error
for the whole subject. Accept the divergence? If not, an opt-in validation
entry point is owed and it is a new seam entry.

**ASK 2 — vendoring UCD data (§3.3). RULED 2026-09-04: AGREED, RELUCTANTLY.**

> **Frank's ruling**: agreed after the usage explanation, and the reluctance is
> part of the ruling — *"the design should carry that usage summary
> prominently where the vendoring is specified, so the reluctance stays
> priced."* **§3.3.1 is that summary**, placed at the vendoring specification
> rather than here. The pin is **16.0.0**, matching the reference oracle's own
> Unicode version.

`\p{...}` needs Unicode property
tables. Generating them from python is disqualified (version drift, measured);
generating them from libpcre2 is disqualified (one source wearing two hats —
`mod_uprops.c`'s own rule). The recommendation is to **vendor the UCD data
files at a pinned version** into `third_party/` and generate a `.inc` at build
time, as `cls_bits.inc` already is. This would be the first non-PCRE2
third-party data in the repository. Approve, and approve the pin (16.0.0,
matching libpcre2 10.46)?

**ASK 3 — should "simple folding only" become a standing check? (§4.1)
RULED 2026-09-04: YES, THE STANDING CHECK.**

> **Frank's ruling**: the 11 one-to-many fold candidates become **a permanent
> cell riding the existing PC-3/PC-4 differential**, firing the day the
> oracle's folding behaviour changes.
>
> **§4.1.1 specifies it** — 11 cells × 2 option words = 22 assertions, the
> skip-loudly convention inherited from PC-3, and a diagnostic that names the
> DESIGN consequence rather than the failing cell. **§8.2 gives it sabotage
> row S-U11** with the `SAB_REACH`/`SAB_REACH_POP` discipline every other row
> now carries. **And the design places it at STAGE 1, not stage 4** — its
> subject is libpcre2 rather than pcrec, so it depends on nothing the fold
> stage builds, and holding it back would leave §4's whole foundation
> unwatched for three stages. That placement is this design's call on the
> ruling's implementation, and §9.2 states it where the wave will find it.

The original question: the whole of §4 rests on a one-time measurement that
10.46 does no 1:n folding, a future PCRE2 could add full folding, and the
failure would be silent.

**ASK 4 — is a UCP axis owed? RULED 2026-09-04: NO UCP AXIS AT M5, DOOR
EXPLICITLY OPEN.**

> **Frank's ruling**: no UCP axis at M5, and the door is *explicitly* open —
> *"our forms were meant for this"*: the module/axis architecture accommodates
> it on demand, and **r54's re-priced cost note (§5.4.1) is the charter price
> for whoever opens it.** So the design's recommendation stands, the corpus
> states the non-UCP semantics (§7.1.1's oracle predicate verifies 7 of the 8
> rows), and §5.4's "no fifth seam entry" holds — but the price of the door is
> now recorded as a DFA state-identity change rather than a seam addition, and
> that number travels with the row that opens it.

The original text and its analysis: (§4.5, §5.4, §5.4.1, §7.1, §7.1.1)
`PCRE2_UCP` re-defines `\w \d \s \b` over the whole code-point space and
accounts for **8 of 28** measured divergence rows. pcrec has no such axis.
Without one, pcrec's UTF-8 answers for those constructs are the non-UCP ones,
the corpus must say so, and **python `re` over `bytes` verifies 7 of those 8
rows** (§7.1.1) — so the absence is checkable rather than merely asserted. The
design recommends **no UCP axis at M5** (D18 earn-its-axis; no consumer has
asked) and flags that it is the largest single divergence family.

> **RE-PRICED AT r54 (E12, §5.4.1), because the first version understated what
> a UCP axis costs and an ASK priced wrong is an ASK answered wrong.** It said
> *"with one, §5.4's word-classification seam entry becomes necessary"* — as
> though the cost were one more row in the entries table, which is the cheap
> and well-understood shape this milestone has already demonstrated twice.
> **It is not.** `upc_of_class`'s representative-byte test (`internal.h:2850`)
> is exact only because `dfa.c:173` refines the byte alphabet by
> `pcrec_cls_word_esc` first, and **under UCP the word set is not a set of
> bytes at all** — the continuation bytes `0x80-0xBF` appear inside both word
> and non-word characters, so no `refine_by` over any 32-byte table can make
> the equivalence classes homogeneous. A UCP axis therefore needs
> **`upc_of_class`'s mechanism replaced, which is a change to DFA STATE
> IDENTITY**, not a seam entry added beside it. That is a different order of
> work, and Frank should be answering this ASK with that number rather than
> with the seam-entry one.

**ASK 7 — the D58 seam-field record (§2.7.1, §2.7.2). NEW AT r54.**
E2 established that the complement universe must be per-encoding, and the
design chooses a scalar `max_cp` field on `PcrecEnc` over symbolic negation,
with the argument in §2.7.2. **The MECHANISM is this design's call and is not
what is being asked.** What is asked is the record: `PcrecEnc` has carried
`{id, name, entries}` since D58, whose revisit clause the first version of
this document claimed to honour *"by having nothing to record"*. There is now
something to record —

> the **entries table**'s interface is unchanged (the third-encoding recipe
> holds, and `[M6.6.2]` wave D's property is preserved); **`PcrecEnc` itself
> gains one scalar**, read by exactly one caller, the parser's negation site.

— and the question is whether that lands as a D58 **addendum** (the shape D47
and D71 used for rulings that narrow an existing decision) or as its **own
decision row**. The design has no preference and states the fact rather than
choosing the filing. **The r54 verifier folded a SECOND D58 fact into the
same ask** (its lens-3 finding): §5.5 establishes that D58's rationale
sentence — "the hot path has NO external advance loop" — is true of
`ENG_UNANCH` only, and `ENG_ATTEMPT`'s start loop is a genuine external
byte-arithmetic advance in shared emitter code that the second encoding
exposes (the first structurally could not). Whatever filing shape ASK 7
gets, it records both: the `max_cp` field and the rationale's narrowing.
**RULED AT MERGE (manager, 2026-09-04): a D58 ADDENDUM carrying both
facts** — the seam's own decision record is where seam-contract changes
live, and neither fact reverses D58, both narrow it (D47/D71's shape).

**ASK 5 — `ENG_ATTEMPT`'s start loop (§5.5). RULED 2026-09-04: LEAVE IT,
WITH AN ADDENDUM THAT COST THIS LANE A MEASUREMENT.**

> **Frank's ruling**: agreed, leave it — the design's recommendation, D77,
> measure the loss first. **Addendum: VALIDATE AGAINST ORACLES.** The corpus
> must carry `startpos`-at-mid-character cells checked against the oracle, so
> §5.5's and §2.6.1's entry-promise cells become **measured corpus rows, not
> assumptions.**
>
> **DISCHARGED IN THIS REVISION**, and it was worth the addendum: probe
> section `E2` was added and run against 10.46, and §2.6.1.1 is the result.
> **It found more than the addendum asked for.** There are THREE oracle
> answers on one cell, not two — `PCRE2_UTF` refuses uniformly, and
> `MATCH_INVALID_UTF` advances to the next boundary but does **not** answer
> what a start AT that boundary answers, because the mid-character entry acts
> as a barrier the lookbehind cannot cross. And the cell is a **second,
> independent witness for §5.2.1's `back_step` repair**, on a WELL-FORMED
> subject — so E4's abort is reachable through a caller-supplied `startpos`
> and not only through ill-formed input, which widens §12 P-9's instrument.
> The addendum found a real thing; the assumption it replaced was wrong about
> the shape of the answer, not just unverified.

The original question: under UTF-8 the loop tries
mid-character starts, which are harmless (no path) but wasted, up to 3 per
character. Fixing it means routing a shared emitter loop through a residual
entry, which S68 and `engine_callable = false` currently forbid.

**ASK 6 — the `.rxt` third oracle value (§7.4). RULED 2026-09-04: THE SMALL
AMENDMENT ROUTE.**

> **Frank's ruling**: the small `rxt_format.md` amendment; the manager
> charters it with the implementation waves, spelling is the manager's per the
> standing `[DD-13b]` ruling, and **§7.1.1's match-units predicate is the
> input**. **This lane does not write the spec**, and §7.4.1 is what it hands
> over instead — including the correction that the amendment needs **at least
> four** states rather than the three the ASK asked for, because §7.1.1 found
> the oracle question is a predicate about match UNITS and not a label.

The original question: the format has python-verifiable and `# pcre2-only`,
and UTF needs at least one more.

---

## 15. Where this document is still weakest

Not the same list as §10, which is about decisions deferred. This is about
**claims that are load-bearing and thin**, ranked by how much would break if
each were wrong — written after the r54 revision, in the same spirit §12 was
written before the panel.

1. **§2.1.2's three constraints.** The whole pass position rests on them, and
   two are read off comments (`compile.c:947-955` on `.body`, and §5.6.4's
   two-timings rule) rather than off a check. If constraint 2 is weaker than
   its comment claims — if a `.body` captured before the lowering is in fact
   fine — the lowering can move above `altcls` and §2.5.1's three WIDEN rows
   and three DECLINE rows all disappear. **That is the single largest
   simplification available to this design**, and P-12 is the invitation to
   find it.
2. **§6.4 entire.** Every row is ARGUED or ASSERTED, none is measured, and the
   `vm_cost` row is flagged in its own table as the most likely to be wrong.
3. **§2.4.1's byte figure.** The entries and elements columns are measured;
   the D84 byte column is a back-of-envelope derivation stated as such. P-5c
   is a prediction with no evidence behind it and the document says so.
4. **§8.3's subjects-per-block multiplier of 4.** It is a judgement, stated so
   it can be argued with, and it moves the case total by ±400 if it is wrong.
5. **§4.6's 12 KB fold-table figure**, derived from a mapping count rather
   than from an emitted artifact, because no emitted artifact exists.

---

---

## 16. THE r54 WHAT-CHANGED RECORD

The panel-outcome block at the top maps finding → disposition → section. This
is the other direction: what a reader of the first version must **un-learn**,
and what is genuinely new. House convention (R33's shape): the refutations
stay inline where they bit, and this section is the index to them.

### 16.1 Claims of the first version that are now FALSE

| first version said | now | where |
|---|---|---|
| the lowering sits "between the parser and the IR" | it sits between `pcrec_postresolve` and `pcrec_build_nfa`, at `compile.c:1000`, and the position is **forced** by three constraints | §2.1.2 |
| negation "complements within the code-point space" | it complements within `[0, MAXCP(enc)]`; the unqualified form refuses every negated class under `byte` | §2.7.1 |
| "the seam needs no interface change" | the **entries table** needs none; `PcrecEnc` gains one scalar | §2.7.2, ASK 7 |
| `minw`/`maxw`'s "real consumer is `[M4.6d]`'s MRL pruning" | true of `minw` (7 sites); **`maxw` has no MRL consumer at all** and its whole chain retires | §5.6.2 |
| suffix sharing "keeps a `\p{L}`-sized set near-linear" | a tree cannot share suffixes; sharing is worth **16%** and nothing in the artifact | §2.3.1 |
| "every row clears every cap by more than an order of magnitude" | true in **states**; `\p{L}{1,3}` is **123%** of the entries cap | §2.4.1 |
| "there is no mechanism by which an encoding could make a pattern VM-only" | `[SEL-1]`'s `forces_dfa_overflow` is one — it reads a machine size, and size is what the encoding changes | §6.2.1 |
| the byte-tier class machinery "is below the lowering and is untouched" | true of six sites; **six others sit above it** and are enumerated | §2.5.1 |
| `pcrec_cls_word_esc` "becomes an interval literal" | its PRODUCER form does; the table **survives as bytes** for `\b`'s mechanism | §2.2.2 |
| P-1 (the third-encoding recipe touches nothing outside the backend) | **REFUTED**, and it was the wrong rule to predict on | §12 P-1 |
| §8.3's "~420 cells, comparable to lookaround's 457 blocks / 1,819 cases" | **423 blocks / ≈1,559 cases**, against 457 / 1,819 — like against like | §8.3 |
| S-U7's witness is the ~27 invalid-UTF-8 cells | those are **compile-time refusals** and cannot see S-U7; the witness is a subject | §8.3.1 |
| a UCP axis costs "a word-classification seam entry" | it costs `upc_of_class`'s mechanism **replaced** — a DFA state-identity change | §5.4.1, ASK 4 |

### 16.2 What is genuinely new

- **§2.1.4's render helper and its assertion** — the mechanism that makes E1's
  miscompile inexpressible rather than merely absent. Not asked for by the
  panel; it is the difference between fixing a bug and closing a class.
- **§2.4.1/§2.4.2** — the caps' own units, and the alphabet-refinement
  argument for why `ncls` is the term to watch.
- **§4.6** — the artifact's run-time fold table, sized against D84, with the
  agreement check redesigned rather than re-run at 1.1M cells.
- **§5.2.1's `back_step`** — the length-validating body, its invariant, and
  the deliberate decision that it be a LENGTH test rather than a second
  UTF-8 validator.
- **§6.4** — the VM's cost and capacity axes, priced for the first time.
- **§7.1.1** — the UCP-SPLIT oracle, and the finding that VERDICT and ORACLE
  are different partitions of the divergence table.
- **§8.1.1, §8.1.2, §8.5** — the structural checks, the floors, and the
  encoding differential (which composes with the identity gate to pin `utf8`
  answers to a pre-M5 compiler transitively).
- **§15** — where this document is still weakest, written after the revision
  as §12 was written before the panel.
- **§4.1.1** — the standing 1:n fold check (ASK 3 RULED), placed at stage 1
  rather than at the stage that builds the fold, because its subject is the
  ORACLE and not pcrec.
- **§5.7** — the OTHER-ENCODINGS door note (Frank's width question, widened by
  R-ASKS-3(b)): what the architecture already carries, the three
  transfer-blockers, the codepage and legacy-multi-byte cases, and the D77
  trigger. It is the one section written to prevent a future MIS-reading
  rather than to fix a present defect — and §5.7.3 nonetheless produced two
  findings against the rest of the document (`max_cp`'s contiguity
  assumption, and §2.3's unstated monotonicity premise).
- **§3.3.2** — `third_party/`'s general shape (R-ASKS-3(a)), with UCD named
  as the first instance rather than as the pattern.

### 16.3 Findings this revision made against ITSELF

Recorded separately because they were not the panel's, and the panel-outcome
block would otherwise take credit for them:

1. **`[SEL-1]` is an encoding→engine mechanism** (§6.2.1) — found by
   re-deriving §6.2 under the forced position rather than by re-reading the
   critique.
2. **The UCP-SPLIT oracle is 7 of 8, not 8 of 8** (§7.1.1) — the panel cited
   one agreeing example and the family holds, but working the whole column
   found `\W` over a Greek letter, where python-bytes disagrees for a UNIT
   reason and python-str disagrees for the opposite reason. That row also
   produced the verdict-vs-oracle finding.
3. **E13 is right about a different consumer than the design was** (§2.2.2) —
   both readings were correct, which makes the two-representation hazard the
   actual finding.
4. **The `maxw` chain can be RE-AIMED rather than retired-and-replaced**
   (§5.6.2), which halves E3(b)'s stated cost.
5. **The ASCII-corpus population is 3,319, not 3,349** (§8.5) — the obvious
   text scan cannot see escaped high bytes in subjects, and the 30 blocks it
   misses are exactly the ones the differential must exclude. R13's lesson,
   reproduced in this lane after being cited in it.

# Module `lookaround` — design

**[M6.6.1]**, the design gate in front of [M6.6.2]. Covers `(?=X)` `(?!X)`
`(?<=X)` `(?<!X)`, the non-atomic `(?*X)` `(?<*X)`, and PCRE2's twelve
alpha-assertion spellings `(*pla:` `(*nla:` `(*plb:` `(*nlb:` `(*napla:`
`(*naplb:` and their four long forms.

**STATUS: PROPOSED.** No `src/` change belongs to this lane. Nothing here is
built. The D6 panel (R33) reviews this document before [M6.6.2] starts, and
Frank says go after.

**THIS IS THE LAST MODULE OF M6.** Three module designs precede it and each
was refuted somewhere central: `assertions` lost its engine-split spine (R30
E1/E2), `atomic-groups` lost its emitted form (R31), `backrefs` lost its
central premise (R32 E1). §12 is this document's own list of where to attack,
written before the panel rather than after.

---

## 0. How to read this

### 0.1 Claim marking

Adopted verbatim from `backrefs_design.md` §0.1, which took it from
`assertions_design.md` §0.1, which took it from `engine_m4.md` §0.1, so the
panel reads one vocabulary:

- **MEASURED** — a number or behaviour from an instrument, with its source
  cited. If the source is not cited it is not MEASURED.
- **RULED** — settled by a D-number in `../dev/decisions.md` or by a plan-row
  ruling of Frank's. Consumed here, not re-litigated.
- **STRUCTURAL** — true by inspection of code that exists today, file and line
  cited. Weaker than MEASURED (no instrument ran), stronger than ARGUED.
- **PROTOTYPE** — produced by a model or a throwaway build, not by the shipped
  compiler. Marked wherever it appears.
- **ARGUED** — the author's reasoning, unmeasured. Every ARGUED claim in a
  load-bearing position is repeated in §12 with the experiment that refutes it.

### 0.2 The design in one paragraph

A lookaround is **a sub-match whose result is a verdict and whose position is
discarded**, and every consequence in this document follows from that one
fact. It is not a new kind of matching — the body is the same AST the same
emitter already walks — so unlike a backreference it needs no new operation,
and unlike an atomic group it changes no quantifier's rung. What it needs is
**a cut and a position restore**: run the body, and on the body's first
success cut back to the frame depth recorded at entry (the `RX_CUT` substrate
[ENG-BREP] built and [M6.4.2] reused unchanged) and put the cursor back where
it was (§3). The **negative** form is the same shape with one frame pushed
first, and that frame is doing more work than it looks: the fail label already
restores `scan_position` from a popped frame and already rewinds the trail to
that frame's mark (`emit_vm.c:6063-6071`), so "on failure, succeed with the
cursor and the captures restored" costs **one push and no snapshot machinery
at all** — which is the single cheapest finding in this module and is what
makes §3 short. The **lookbehind** is the same again with a **back-step**
in front of the body, and that back-step is the [M5-SEAM]'s **third residual
entry** (§4) — the one D58 named in advance and `enc.h`'s own comment
predicted, so this module is also the [M6.5.2] entries-table refactor's first
validation and needs **zero interface change** to it. Three things are NOT
consequences of the mechanism and are the parts a panel should attack: the
**lookbehind length rule**, which PCRE2 10.46 implements with **two preference
orders that disagree with each other** — top-level branches in written order,
step-back lengths within a branch **longest first** (§2.3, measured) — and
which this design ships only the fixed-per-branch half of; the **prefilter**,
where erasing a lookaround is a genuine superset and its rejection and its
start survive that (**0 violations**) while its window END does not (**8
violations of 45**, and the hazard **coexists with a live prune ceiling on 16
of 30 swept shapes**), so this module keeps the prefilter and drops the
ceiling, which is exactly [M6.4.2]'s H3 one construct over (§5); and the
**DFA answer**, which is **not this module's**: Frank ruled the one-character
fold out as a duplicate code path, the general form is chartered as
`[ENG-LOOK]` (lookaround by PRODUCT CONSTRUCTION in the DFA), and this design
hands that row its three stated prerequisites — the soundness statement, the
measured component-automaton sizes, and a lowering whose every body is already
a self-contained sub-program (§5.7, §5.8, §6.4). One more thing follows from
the mechanism and is why §6 exists at all: **every member of the assertion
family IS a lookaround**, so the [DD-11]/D66 expansions (`\b`, `(?m)^`, `\Z`,
…) are this module's own design examples — all nine verified equivalent at
**972 cells / 0 disagreements** — and textually substituting them into the
assertions module's shipped corpus turns **8,495 of its 10,120
libpcre2-verified cells** into a lookaround corpus with a two-comparison
self-oracle (§6.3).

### 0.3 Measurements this lane produced

All under `lookaround_measurements/`, probes committed, outputs archived with
their repo commit by `probes/archive.sh` in ONE batch from a committed tree.

| instrument | kind | what it answers |
|---|---|---|
| `probes/la_oracle.py` | not a probe, the ORACLE HELPER | borrows `../backrefs_measurements/probes/br_oracle.py` (which borrows `pcre2_ctypes.py`) and adds the `max_varlookbehind` compile-context setter, `PCRE2_INFO_MAXLOOKBEHIND`, `PCRE2_INFO_CAPTURECOUNT` and a padded python `re` arm. **Two of its three constants were WRONG at the value a reader would take from the documentation's list order**, and its behavioural `SELFCHECK` is the only reason that is known |
| `probes/probe_premises.sh` | MEASURED + STRUCTURAL, in-pcrec | §1: every spelling's refusal on HEAD, the six registry rows and their `built` column, the `(*` doorway's module answer, `vm_cut`/`vm_atomic` quoted from `src/`, the seam's entries |
| `probes/probe_spellings.py` | MEASURED, both oracles | §2.1/§2.2: compile status and the DISCRIMINATORS (direction, polarity, width, atomicity); the degenerate bodies; quantified lookaround; nesting; the match-START cells |
| `probes/probe_lookbehind_length.py` | MEASURED, libpcre2 + python | §2.3: which bodies compile with which error number; the TWO preference orders; the bisected `max_varlookbehind` default (**255**) and the fixed ceiling (**32759**); `MAXLOOKBEHIND` for composite bodies; the subject-start and **startpos** cells |
| `probes/probe_captures.py` | MEASURED, both oracles | §2.4/§3.5: captures across all four polarity/outcome combinations; the empty-iteration cells; `\K`'s refusal and its extra-option bit; the BUDGET witness |
| `probes/probe_prefilter_hazard.py` | MEASURED, libpcre2 + in-pcrec | §5.3-§5.4: H1/H2/H3 over 45 cells, with the SHARP anchored-at-true-start form of H3 beside the naive one, a fixture-tested `erase()`, and two vacuity guards |
| `probes/probe_d66_subset.py` | MEASURED, libpcre2 + in-pcrec | §6.5/§9.2: the six equivalences (80 cells each); the `(?m)^` self-oracle in BOTH directions; and §5.5's sweep, which finds the H3 hazard **coexisting with a live prefilter-window ceiling on 16 of 30 shapes** |
| `probes/probe_expansions.py` | MEASURED, both oracles + in-pcrec | §6.1/§6.2: the nine [DD-11]/D66 expansions verified equivalent (**972 cells, 0 disagreements**, vacuity guard firing at 4/108); each body classified against §2.5; python's verdict per expansion; and pcrec's shipped FOLDED forms against libpcre2's EXPANSIONS (**0 over 324 cells**) |
| `probes/probe_substitution_population.py` | MEASURED, PURE TEXT | §6.3: how much of `tests/assertions/` the substitution driver gets — **270 of 468 blocks, 8,495 of 10,120 cells** — with each of the five qualification rules costed separately. Runs no compiler: the question is a property of the corpus text |
| `probes/probe_englook_sizing.py` | MEASURED, in-pcrec | §5.8: `[ENG-LOOK]`'s sizing inputs, read off the **emitter's own array dimensions** — every component 2-25 states, product bound **64 non-control rows / 0 over the 32,000 cap** against **62 control rows / 18 over** |

**`probes/archive.sh` is the ONLY writer of `out/`.** R30 M7's rule, inherited
through two lanes. R32 D1/C14 found the backrefs archiver stamping the wrong
module in all eight of its files; this lane's stamp was scoped at creation and
all six outputs were archived in one batch from a committed tree.

**SEVEN INSTRUMENT DEFECTS this lane found by running its own probes**, all
recorded in `out/CLAUDE.md` and each producing a confident wrong number rather
than an error. Two are worth naming here because they are the reason the
numbers in this document should be trusted more than a first draft's:

1. **`PCRE2_INFO_MAXLOOKBEHIND` at the documentation-order index 23 read a
   different field** and answered `0` for `(?<=abc)x`. The whole of §2.3's
   `maxlb` column would have been zeros. Caught by a behavioural self-check;
   the real index (15) was derived by sweeping 0..31 for the one that answers
   3/0/2/5 on four patterns, with a cell separating it from `MINLENGTH`.
2. **`PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK` at 0x8000 did nothing**, and the probe
   said so ("this block measured nothing") rather than reporting that the
   option does not work. A 32-bit sweep found exactly one bit — **0x40** —
   with two controls.

The other seven (a vacuous budget axis killed by PCRE2's own start
optimization; a `(?m)` on one arm only; a tail set blind to the defect a
sibling axis found; a sweep population that could not contain a qualifying
shape; two oracles compared across a report-shape difference; a probe that
reported the corpus's two cell counts THE WRONG WAY ROUND, understating its
own driver's reach; and a sizing table whose "0 over the cap" was over a
population in which no row could have been) are in `out/CLAUDE.md`. **The fourth is the one a panel should note**: §5.5's first
sweep reported "0 qualifying shapes" over a space in which 0 was the only
possible answer, and the reachability guard that now stands is what turned
that into the **16 of 30** this design's H3 ruling rests on.

---

## 1. Premises, re-verified on HEAD rather than inherited

Each of these was checked against **this worktree's build** rather than taken
from a document. Two of the charter's own premises did not survive.

MEASURED/STRUCTURAL, `out/premises.txt`, at `d1d4378`.

| # | premise | verification |
|---|---|---|
| P1 | The four `(?` lookaround spellings refuse today naming module `lookaround` | MEASURED, axis A: `(?=a)b` → "`(?=...)` requires module 'lookaround'"; `(?!a)b` likewise; `(?<=a)b` and `(?<!a)b` → "`(?<...)` requires module 'lookaround'" (the diagnostic renders the DOORWAY, not the tail — D26 tier 3, not a defect) |
| P2 | The two NON-ATOMIC `(?` spellings also refuse naming `lookaround` | MEASURED: `(?*a)b` → "`(?*...)`", `(?<*a)b` → "`(?<...)`", both `lookaround` |
| P3 | **The twelve ALPHA spellings refuse naming module `verbs`** | MEASURED, axis C: all twelve of `(*pla: (*nla: (*plb: (*nlb: (*napla: (*naplb:` and their long forms answer "`(*...)` requires module **'verbs'**". **This is a D26 tier-2 defect and this module owns it** — §8.2 |
| P4 | Exactly SIX registry rows carry module `lookaround`, all `VM_ONLY`, all `unbuilt` | MEASURED, axis B: `(?=...)` `(?!...)` `(?<=...)` `(?<!...)` `(?<*a)` `(?*a)`; row count 6; rows reading `built` 0 |
| P5 | `vm_cut` is reusable UNCHANGED and its interface is `(Vm *, int slot, const char *role)` | STRUCTURAL, `emit_vm.c:2119-2130` quoted in full in `out/premises.txt` axis D. It charges the discarded frames through `vm_work` and then emits `RX_CUT(slot)` |
| P6 | `vm_atomic` is the shape this module mirrors, and its mark `RX_SET` precedes every body push | STRUCTURAL, `emit_vm.c:4204-4292`, quoted in full |
| P7 | **The fail label restores `scan_position` from the popped frame AND rewinds the trail to that frame's mark** | STRUCTURAL, `emit_vm.c:6063-6071`: `scan_position = run->resume_stack[frame_index].resume_position;` then `while (run->trail_depth > ...trail_mark)`. **This is the premise §3.3 is built on and it is why the negative form needs no snapshot** |
| P8 | The seam carries THREE entry ids today and the entries table is a NULL-terminated array per backend | STRUCTURAL, `enc.h:78-88` (`PCREC_ENCE_NEXT_POS`, `_BREF`, `_BREF_CASELESS`), `enc_byte.c`'s `entries_byte[]` |
| P9 | `enc.h` PREDICTED this entry by name | STRUCTURAL, `enc.h`'s "THE ROAD NOT TAKEN" paragraph: *"lookbehind's back-step ([M6.6]) is the next residual entry D58 already names, and it would need a third pair"* |
| P10 | `pcrec_enc_entry_engine_callable` exists and the `A_BREF` arm consults it before emitting a call | STRUCTURAL, `enc.h:126-131`, `emit_vm.c:4655-4671` |
| P11 | `pcrec_minw` exists; **`pcrec_maxw` DOES NOT** | STRUCTURAL: `internal.h:2381` declares `long long pcrec_minw(const Ast *)`; a tree-wide grep finds no `maxw` anywhere. §2.5's width rule therefore needs NEW code, not a call |
| P12 | `mrl.c` has already written down what a lookaround contributes: **0** | STRUCTURAL, `src/opt/mrl.c:32-35`: *"Lookaround, backreferences and `(*ATOMIC)` have no producers today; when they gain one, each contributes 0 here until someone measures otherwise."* **§3.7 measures otherwise for the lookBEHIND and leaves the lookahead at 0** |
| P13 | The default feature set is `std1` and it does **NOT** enable module `assertions` | MEASURED, `out/d66_subset.txt` S1b: `\bfoo` under the default refuses "requires module 'assertions'"; under `--features all` it compiles. §9 and §10 both consume this |
| P14 | With module `lookaround` ENABLED, the refusal is the D65 **enabled-but-unbuilt** one | MEASURED, S1b: `--features all` on `(?<!\w)(?=\w)foo` gives "module 'lookaround' is **enabled but** `(?<...)` **is not implemented yet**" — a different diagnostic from P1's, and the one the built-status machinery reads |
| P15 | A residual seam entry may not be referenced from any file-scope function body but its own and `main()` — **unless the entry declares `engine_callable`** | STRUCTURAL, `tests/codegen/run_codegen_tests.sh:898ff`, and the fixture table's fourth column now declares `<suffix>:<count>` per fixture with an EXACT guard asserting **4** fixtures declare a `bref` entry |
| P16 | pcrec's own compiled artifact is leftmost-**FIRST**, not leftmost-longest | MEASURED: `(a|ab)` compiled with `--emit-main` and run on `"ab"` prints `match 0 1`. **This is what makes §5.4's PCRE2-anchored model of the prefilter faithful rather than a guess** |

**Two charter premises did not survive.** The [M6.6.1] row says the D27
goal-facts list should carry *"python lacks … the non-atomic forms; python's
treatment of captures in negative lookahead; quantified lookaround"* as
divergences. MEASURED (`out/spellings.txt` A4, `out/captures.txt` C1-C4):

- **python3 `re` ACCEPTS quantified lookaround**, on all fourteen forms tried
  (`(?=a)*`, `(?=a)+`, `(?=a){2}`, `(?!a)?`, `(?=a)*+`, `(?=(a))*` …) and
  agrees with libpcre2 on all nine behavioural cells. It is **not** a
  divergence and §7 says so.
- **python agrees with libpcre2 on every capture cell in this module**, all 27
  of them, including the negative-lookahead ones the row expects to differ.
  The divergence list is shorter and sharper than the charter guessed, and §7
  gives what it actually is.

---

## 2. The construct table (charter (i))

### 2.1 Every spelling, and whether pcrec ships it

MEASURED, `out/spellings.txt` axis A1/A2, 10.46 and python 3.14.4. The
`is it what it claims` column is the DISCRIMINATOR rule taken from
`backrefs_design.md` §2 and from `registry.c:692`'s own record: a construct
that merely compiles proves nothing about what it is.

| spelling | libpcre2 10.46 | is it what it claims? | python `re` | **this module** |
|---|---|---|---|---|
| `(?=X)` | ok | atomic positive lookahead — `(?=(a\|ab))\1$` is NOMATCH on `"abab"` | ok | **SHIPS** |
| `(?!X)` | ok | negative lookahead | ok | **SHIPS** |
| `(?<=X)` | ok | atomic positive lookbehind | ok, fixed-width only | **SHIPS**, fixed-per-branch (§2.5) |
| `(?<!X)` | ok | negative lookbehind | ok, fixed-width only | **SHIPS**, fixed-per-branch |
| `(?*X)` | ok | **NON-atomic** positive lookahead — `(?*(a\|ab))\1$` is **(2,4)** on the same subject | err | **SHIPS** (§3.6: the atomic shape MINUS the cut) |
| `(?<*X)` | ok | non-atomic positive lookbehind — `(?<*(a\|ba))c` is (2,3) g=(0,2) | err | **SHIPS** |
| `(*pla:X)` `(*positive_lookahead:X)` | ok | atomic — `(*pla:(a\|ab))\1$` NOMATCH, same as `(?=)` | err | **SHIPS** (§8.2) |
| `(*nla:X)` `(*negative_lookahead:X)` | ok | negative lookahead | err | **SHIPS** |
| `(*plb:X)` `(*positive_lookbehind:X)` | ok | positive lookbehind | err | **SHIPS** |
| `(*nlb:X)` `(*negative_lookbehind:X)` | ok | negative lookbehind — `(*nlb:a)\w` is (0,1) on `"ba"` | err | **SHIPS** |
| `(*napla:X)` `(*non_atomic_positive_lookahead:X)` | ok | non-atomic — **(2,4)**, the same answer as `(?*`, which is the proof they are one construct | err | **SHIPS** |
| `(*naplb:X)` `(*non_atomic_positive_lookbehind:X)` | ok | non-atomic positive lookbehind | err | **SHIPS** |
| `(*nanla:X)` `(*nanlb:X)` | **err 195** ("(*alpha_assertion) not recognized") | — **there is no non-atomic NEGATIVE form** | err | refuse — the row's own control |
| `(?<!*X)` | **err 109** | — the `*` is read as a quantifier | err | refuse |
| `(?=)` `(?!)` `(?<=)` `(?<!)` | ok, all four | zero-width with an empty body: `a(?=)b` is (0,2), `a(?!)b` is NOMATCH | ok | **SHIPS** (§2.6) |

**SHIP/REFUSE SPLIT: EIGHTEEN spellings ship and THREE refuse** — `(*nanla:`
and `(*nanlb:`, which PCRE2 does not have (err 195), and `(?<!*X)`, which
PCRE2 reads as a quantifier and rejects (err 109). **There is no spelling in
this module's territory that PCRE2 HAS and pcrec declines.** Every decline
this module makes is about a BODY (§2.5), not a spelling, and that is the
distinction D26 tier 1/2 cares about: which constructs are REAL and who owns
them is exact here, and the capability limits are stated separately.

### 2.2 The atomicity discriminator, because it is the whole difference

MEASURED, `out/spellings.txt` A2, on `"abab"`:

```
(?=(a|ab))\1$        NOMATCH    the lookahead keeps its FIRST success ("a"),
                                so \1 is "a" and "a" does not end the subject
(?*(a|ab))\1$        (2,4)      the non-atomic form RETRIES, finds "ab",
(*napla:(a|ab))\1$   (2,4)      and \1 = "ab" ends the subject
(*pla:(a|ab))\1$     NOMATCH    the verb spelling of (?=) — atomic
```

That table is four rows and it fixes four things at once: `(?=` is atomic,
`(?*` is not, `(*napla:` is `(?*`, and `(*pla:` is `(?=`. §3 emits the first
and third with a cut and the second and fourth without one, and there is
nothing else to the distinction.

### 2.3 The lookbehind length rule, cell by cell on 10.46

MEASURED, `out/lookbehind_length.txt` B1. The `err` numbers are the fact;
their wording is D26 tier 3.

| body | maxlb | libpcre2 10.46 | python `re` |
|---|---|---|---|
| `(?<=a)x` `(?<=abc)x` `(?<=\w)x` `(?<=[abc][def])x` | 1/3/1/2 | ok | ok |
| `(?<=a{3})x` `(?<=(?:ab){2})x` | 3/4 | ok — an EXACT count is fixed | ok |
| `(?<=ab\|cd)x` | 2 | ok — same length | ok |
| **`(?<=a\|bc)x`** | **2** | **ok — DIFFERENT fixed lengths per branch** | **ERROR** ("look-behind requires fixed-width pattern") |
| `(?<=(a\|bc))x` | 2 | ok — but this is ONE branch of VARIABLE width | ERROR |
| `(?<=a\|bc\|def)x` | 3 | ok | ERROR |
| `(?<=(?:a)(?:b))x` `(?<=(a)(b))x` | 2 | ok | ok |
| `(?<=(?:a\|bc)d)x` `(?<=((a\|bc)d))x` | 3 | ok | ERROR |
| `(?<=a{2,3})x` `(?<=a{0,3})x` `(?<=a?)x` | 3/3/1 | ok — BOUNDED variable | ERROR |
| `(?<=a*)x` `(?<=a+)x` `(?<=a{2,})x` `(?<=a*?)x` `(?<=a*+)x` `(?<=(?>a*))x` | — | **err 125** "length of lookbehind assertion is not limited" | ERROR |
| `(a)(?<=\1)x` | 1 | ok — a backref to a FIXED-width group | ok |
| **`(a\|bc)(?<=\1)x`** | **2** | **ok — a backref to a VARIABLE-width group** | ERROR |
| `(?<=(?=a)a)x` `(?<=(?<=a)b)x` `(?<=a(?!b))x` `(?=(?<=a)b)x` | 1 | ok — lookaround nests both ways | ok |
| `(?=(?<=a*)b)x` | — | err 125 — the inner rule applies through the outer | ERROR |
| `(?<=\Ka)x` `(?=a\K)x` `(?!a\K)x` `(?<!\Ka)x` | — | **err 199** "`\K` is not allowed in lookarounds" | ERROR (`\K` absent) |
| `a\Kb` (control) | 0 | ok | ERROR |
| `(?<!a\|bc)x` `(?<*a\|bc)x` | 2 | ok — the rule is polarity- and atomicity-blind | ERROR |
| `(?<!a*)x` `(?<*a*)x` | — | err 125 | ERROR |

**THE CAPS ARE TWO DIFFERENT NUMBERS AND ONE OF THEM IS NOT A PROPERTY OF THE
CONSTRUCT.** MEASURED, B3:

- The **variable** back-step is capped by the COMPILE CONTEXT's
  `max_varlookbehind`, whose **default bisects to 255** (`(?<=a{1,255})x` is
  ok; `(?<=a{1,256})x` is **err 200** "branch too long in variable-length
  lookbehind assertion"). Under an explicit cap of 4, `(?<=a{1,4})x` compiles
  and under 3 it does not — so the number is contextual, not intrinsic, and
  quoting 255 as "PCRE2's lookbehind limit" would be wrong.
- A **fixed** lookbehind is **not subject to that cap at all** (a 10-character
  literal body compiles under a cap of 1). Its own ceiling bisects to
  **32759**, past which it is **err 120** "regular expression is too large" —
  i.e. the pattern-size limit, not a lookbehind limit.

**`PCRE2_INFO_MAXLOOKBEHIND` for composite bodies**, MEASURED B4, because §3
and §5 both need this quantity: `(?<=a)(?<=bc)x` → 2 (the max, not the sum);
`(?<=a)x|(?<=bcd)y` → 3; `(?<=(a|aa)(b|bb))x` → 4 (the sum of the maxima);
`\babc` → **1**; `(?m)^abc` → **0**; `a\Kb` → 0. The `\b` row is the one §6
uses.

### 2.4 THE PREFERENCE ORDER — two levels that disagree

**This is the sharpest measurement in the module and the design's capture
semantics rest on it.** MEASURED, `out/lookbehind_length.txt` B2.

**Level 1 — top-level BRANCHES are tried in WRITTEN ORDER:**

```
(?<=(a)|(aa))c        on "aac"   ->  (2,3)  g1=(1,2)   branch 1 wins (shorter)
(?<=(aa)|(a))c        on "aac"   ->  (2,3)  g1=(0,2)   branch 1 wins (longer)
(?<=(a)|(aa)|(aaa))c  on "aaac"  ->  (3,4)  g1=(2,3)   branch 1 wins
(?<=(aaa)|(aa)|(a))c  on "aaac"  ->  (3,4)  g1=(0,3)   branch 1 wins
```

**Level 2 — within ONE branch the STEP-BACK LENGTH is tried LONGEST FIRST,
and the alternation's own written order does not decide it:**

```
(?<=(a|aa|aaa))c   on "aaac"  ->  g1=(0,3)   longest (3) wins, written LAST
(?<=(aaa|aa|a))c   on "aaac"  ->  g1=(0,3)   longest (3) wins, written first
(?<=(a|aa))c       on "aac"   ->  g1=(0,2)   longest (2) wins, written last
(?<=(x|aa|a))c     on "aac"   ->  g1=(0,2)   longest VIABLE wins
(?<=(a|ba))c       on "bac"   ->  g1=(0,2)   longest (2) wins, written last
(?<=(a|ba))c       on "xac"   ->  g1=(1,2)   only length 1 is viable there
(?<=(a{1,3}))c     on "aaac"  ->  g1=(0,3)   a bounded quantifier: longest first
```

For comparison, the LOOKAHEAD has ordinary leftmost-first alternation, because
it has no length to choose: `(?=(a|ab))ab` gives g1=(0,1) and `(?=(ab|a))ab`
gives g1=(0,2).

**WHY THIS MATTERS TO THE DESIGN, in one sentence:** an implementation that
lowered a lookbehind as "try each alternative in written order, stepping back
its own width" would be **exactly right at level 1 and exactly wrong at level
2** — and it would be exactly right at level 2 too *for the fixed-per-branch
subset this module ships*, because a branch of fixed width has one length and
the loop that would order them has one iteration. **That is the whole argument
for the subset boundary this design draws**, and §2.5 draws it there for that
reason rather than for effort.

### 2.5 THE RULE THIS MODULE SHIPS

> **A lookbehind body's every TOP-LEVEL BRANCH must have a fixed width:**
> `minw(branch) == maxw(branch)`, both finite. Widths may DIFFER between
> branches. A body with any variable-width branch is REFUSED with pcrec's own
> reason.

Consequences, each checkable against §2.3's table:

- `(?<=a)x`, `(?<=abc)x`, `(?<=[ab][cd])x`, `(?<=a{3})x` — **ship**.
- `(?<=a|bc)x`, `(?<=a|bc|def)x` — **ship**. Two branches, each fixed, widths
  1 and 2. This is the charter's "fixed-length alternatives of DIFFERENT
  lengths" cell and the answer is yes.
- `(?<=(a|bc))x` — **REFUSED**. One branch, width 1..2. It looks like the row
  above and is a different shape, and the difference is exactly the level-1 /
  level-2 split §2.4 measured. **This asymmetry is the single most likely
  thing in this document to be called a defect, and §12 P-3 says how to refute
  it.**
- `(?<=a{2,3})x`, `(?<=a?)x` — **REFUSED** (bounded variable).
- `(?<=a*)x` and family — **REFUSED**, and here pcrec AGREES WITH PCRE2, which
  is err 125.
- `(a)(?<=\1)x` — **REFUSED** in [M6.6.2]. A backreference's width is decided
  at MATCH time by which alternative the referenced group took. For a
  fixed-width referenced group it is computable and this refusal is
  conservative; §11's follow-on row carries the refinement.
- `(?<=(?=a)b)x`, `(?<=(?<=a)b)x`, `(?<=a(?!b))x` — **ship**: a nested
  lookaround is zero-width, so it contributes 0 to both `minw` and `maxw`.

**`pcrec_maxw` DOES NOT EXIST (P11) and this module writes it**, beside
`pcrec_minw` in `src/opt/mrl.c`, with that file's `default:`-less exhaustive
switch so a node kind added later is a build failure there (R26 V7, the rule
`mrl.c:18-24` states and `altcls.c:405` cites). It returns a saturating
`PCREC_W_UNBOUNDED` for `A_REP` with `rmax < 0`, and — per the bullet above —
for `A_BREF`. **Writing `maxw` is the module's one piece of genuinely new
analysis and §12 P-4 is how to attack it.**

**WHY REFUSE VARIABLE-LENGTH RATHER THAN SHIP IT.** The machine is not large —
a loop over `k` from `maxw` down to `minw`, the same back-step entry, the same
end-check, which at that point stops being redundant (§3.4). Three reasons to
charter it instead of shipping it:

1. **The loop runs in the OPPOSITE direction to everything else the emitter
   does.** Every other ordered choice in `emit_vm.c` is preference-first, and
   §2.4 measures this one as longest-first over a range whose ends come from a
   NEW analysis (`maxw`). Shipping a reversed loop over an unvalidated
   analysis in the same wave is how the [M4.6d] counter-rung defect happened
   (a compile-time follow-min that topped out at `K + residue`, found by a
   D27-blinded author).
2. **The cost is per-position and unbounded by the pattern.** A body of width
   1..255 runs the body up to 255 times per candidate start, and D42 item 6's
   two bounds (steps and frames) do not see a frameless re-run — the same gap
   [ENG-BREP counter-K] settlement 4 opened `RX_ERR_WORK` for.
3. **The refusal is honest and PCRE2-shaped.** PCRE2 itself refuses the
   unbounded case with err 125 and caps the bounded case at a
   context-dependent 255; a pcrec that ships fixed and names the limit is one
   step, not a different kind of thing.

**The refusal's WORDING is D26 tier 3 and its EXISTENCE is not.** The
construct is real and the module is enabled, so this is not "requires module
'lookaround'" — it is the capability limit P14 already has a diagnostic shape
for. Proposed text, for the panel to attack on content and not on prose:
*"variable-length lookbehind is not implemented: every alternative of a
lookbehind must have a fixed length (this one can match N..M characters)"*.

### 2.6 The degenerate bodies, quantifiers, and the empty-iteration rule

MEASURED, `out/spellings.txt` A3/A4 and `out/captures.txt` C4.

- **`(?=)` `(?!)` `(?<=)` `(?<!)` all compile in BOTH oracles.** `a(?=)b` is
  (0,2), `a(?!)b` is NOMATCH, `a(?<=)b` is (0,2), `a(?<!)b` is NOMATCH — i.e.
  the empty body always succeeds, so the positive forms are no-ops and the
  negative forms are `(*FAIL)`. `(?:(?!))|a` is (0,1). **They ship**, and they
  fall out of §3's shapes with no special case: an empty body is `A_EMPTY`.
- **Quantified lookaround compiles in BOTH oracles** — all fourteen forms
  tried, including `(?=a)*+`. **This refutes the charter's expectation** that
  python lacks it (§1).
- **The empty-iteration cells terminate**, MEASURED with a clock because "it
  did not hang" is the measurement: `^(?=a)*a$`, `^(?:(?=a))*a$`,
  `^(?:(?=a)|b)*a$`, `^(?:(?!x))*a$`, `^(?:(?=(a)))*a$` all answer in 0.0000 s
  and all agree with python.
- **A quantified lookaround's captures behave like one iteration**:
  `^(?=(a))*a$` → g1=(0,1); `^(?=(a))*b$` → g1 unset; `^(?!(a))*b$` → g1
  unset.

**The design consequence is one line and getting it wrong HANGS the emitted
matcher.** `vm_nullable` (`emit_vm.c:875-899`) must answer **true** for the
new node, exactly as it answers true for `A_ATOMIC` and for the same reason
(`emit_vm.c:877-881`: the cut removes MATCHES, never BYTES). A lookaround
consumes nothing on every path, so a `*` above it must get the
empty-iteration guard. §9's sabotage row S-LA9 removes the arm.

### 2.7 `\K` inside a lookaround

MEASURED, `out/lookbehind_length.txt` B1 and `out/captures.txt` C5. **PCRE2
10.46 REFUSES `\K` in every lookaround, all four polarities, err 199**, whose
own text names `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK`. That option **exists and is
bit 0x40 on this build** (derived by sweep after the documentation-order guess
0x8000 measured nothing); with it set, `(?=a\K)x` and `(?<=\Ka)x` compile,
while an unrelated lookbehind error (err 125) survives and plain `a\Kb` stays
legal — the two controls that separate "this bit enables `\K` in lookarounds"
from "this bit disables checking".

**RULING: pcrec REFUSES `\K` inside a lookaround**, matching PCRE2's default,
and does not implement the extra option (D38's option survey territory, not
this module's). The refusal is a parse-time check in the module's hook: while
parsing a lookaround body, an `A_KRESET` node is an error. **The check is
NEEDED rather than free** — `\K` is module `assertions`, already shipped, so
without it `(?=a\K)b` would compile today's `\K` inside tomorrow's lookaround
and quietly change the reported match start. §9's S-LA10.

---

## 3. The VM lowering (charter (ii))

### 3.1 The one new AST kind, and its three fields

```c
A_LOOK,      /* a lookaround: run the body as a sub-match, keep the VERDICT
                and throw the POSITION away */
```

with, on `struct Ast`:

```c
    bool look_behind;    /* A_LOOK: direction  — false = ahead, true = behind */
    bool look_neg;       /* A_LOOK: polarity   — true = the body must FAIL   */
    bool look_atomic;    /* A_LOOK: (?= (?! (?<= (?<! are true;
                                     (?* (?<* (*napla: (*naplb: are false   */
    int  look_widths[];  /* A_LOOK && look_behind: the fixed width of each
                            top-level branch, in branch order (§2.5).
                            Arena-allocated; NULL for a lookahead.          */
    int  look_nbranch;
```

Four decisions, each with its reason.

**(a) ONE KIND, NOT FOUR (or eight).** The measured argument for a node kind
over a flag is `assertions_design.md`'s: a new `AKind` enumerator raises
**15 `-Wswitch` diagnostics across 6 files** where a struct field raises none,
so a kind's failure mode is a build diagnostic and a flag's is the silent bug.
That argument says *at least one* kind; it does not say four. Four kinds would
make three of them **silently handled by a `case` written for the first**,
which is the failure the alarm exists to prevent, one level in. So: one kind,
and D62's own principle then governs the rest — *node KINDS encode structure,
node FIELDS encode parse-resolved state*.

**This is a judgement call and §14 ASK 1 puts it to Frank**, because the honest
counter-argument is real: `look_behind` changes the emitted control flow more
than `Ast.multiline` changes `$`'s, so calling it "modifier state" is
generous. What settles it for this design is that **all three fields are read
at exactly ONE site** (`vm_look`, §3.2), so there is no second reader to drift
— which is not true of `.multiline` and is why D62 needed three controls.

**(b) D62 CONTROL 3'S OBLIGATION COMES WITH THE FIELDS.** An analysis that
pattern-matches `case A_LOOK:` and does not read `.look_neg` reproduces
`possessify.c`'s pre-D62 bug, and no compiler diagnostic will say so. §9 makes
that **three sabotage rows** (one per field) rather than a comment.

**(c) THE WIDTHS ARE COMPUTED AT PARSE TIME AND STORED.** They could be
recomputed in the emitter from `maxw`. They are stored because the *refusal*
in §2.5 has to happen in the module's parse hook — a body pcrec will not
compile must be rejected with a pattern offset, not discovered by the emitter
— and once the hook has computed them, recomputing them downstream is a second
derivation that can disagree with the first. Same rule as `Ast.caseless` on
`A_BREF` (D62): resolved once, at the position that knows.

**(d) `mrl.c` GAINS AN `A_LOOK` ARM AND THE ANSWER IS 0 — BUT IT IS NOW 0
BECAUSE IT WAS CHECKED.** P12 records the inherited default, written before
any producer existed: *"Lookaround, backreferences and `(*ATOMIC)` have no
producers today; when they gain one, each contributes 0 here until someone
measures otherwise."* Checked: it is right for a **lookahead**, which consumes
nothing and inspects bytes ahead of the cursor, so it adds nothing to the
minimum remaining length; and it is right for a **lookbehind** too, because
those bytes are *behind* the cursor and `minw` counts bytes still to be
consumed. `pcrec_maxw`'s new arm answers 0 for the same reason. **The value
does not change and the claim's status does** — from an inherited placeholder
to a checked answer — which is the whole content of this bullet and is why it
is a bullet rather than a silent `return 0;`.

### 3.2 The shape, and it is `vm_atomic`'s with two lines added

The whole lowering is one emitter function, `vm_look`, and its positive-
lookahead arm is `vm_atomic` (`emit_vm.c:4204-4292`) plus a saved position.

```
    L_entry:  RX_SET(SLOT_LOOK_MARKk, run->resume_depth)   // BEFORE any push
              RX_SET(SLOT_LOOK_POSk,  scan_position)       // trailed, like the mark
              goto L_body
    L_body:   <X>                              -> L_ok      // ordinary emission
    L_ok:     RX_CHARGE_WORK(depth - mark);  RX_CUT(SLOT_LOOK_MARKk)
              scan_position = (size_t)slot_values[SLOT_LOOK_POSk];
              goto L_next
```

Emitted C. **This is not a hand-drawn sample**: it is the SHIPPED emitter's
own output for `((?>ab)c)` (`--features all`, `build/pcrec` at `d1d4378`) with
the two `A_LOOK` lines added and the group wrapper kept so the artifact is
VM-routed. Everything else — the one-line class tests, the decimal byte
constants, the numeric slot index inside `RX_CUT`, the `__attribute__((unused))`
on every label — is reproduced rather than invented, because a design whose
emitted code does not look like the emitter's is a design a panel cannot
check.

```c
rx_L0: __attribute__((unused));
    RX_SET(RX_SLOT_GROUP1_START, (ptrdiff_t)scan_position);
    goto rx_L2;
// lookahead: record the resume-stack depth to cut back to (BEFORE the body pushes anything)
rx_L2: __attribute__((unused));
    RX_SET(RX_SLOT_LOOK_MARK0, (ptrdiff_t)run->resume_depth);
    RX_SET(RX_SLOT_LOOK_POS0, (ptrdiff_t)scan_position);      // <-- ADDED vs (?>ab)
    goto rx_L5;
rx_L5: __attribute__((unused));
    if (scan_position < subject_length && (subject[scan_position] == 97)) { scan_position++; goto rx_L7; }
    goto rx_fail;
rx_L7: __attribute__((unused));
    if (scan_position < subject_length && (subject[scan_position] == 98)) { scan_position++; goto rx_L6; }
    goto rx_fail;
// lookahead: the body's FIRST success -- cut, restore the cursor, and never reconsider
rx_L6: __attribute__((unused));
    RX_CHARGE_WORK((ptrdiff_t)run->resume_depth - slot_values[4]);
    RX_CUT(4);
    scan_position = (size_t)slot_values[5];                   // <-- ADDED vs (?>ab)
    goto rx_L4;
rx_L4: __attribute__((unused));
    if (scan_position < subject_length && (subject[scan_position] == 99)) { scan_position++; goto rx_L3; }
    goto rx_fail;
// group 1 closes
rx_L3: __attribute__((unused));
    RX_SET(RX_SLOT_GROUP1_END, (ptrdiff_t)scan_position);
```

**THE TWO ADDED LINES ARE THE ENTIRE DIFFERENCE between `(?>ab)c` and
`(?=ab)c`,** which is the strongest form §3's central claim can take: the
positive lookahead is the atomic group plus a saved cursor. Note the
asymmetry the real output shows and a hand-drawn sample would have hidden —
`vm_set` emits the NAMED slot (`RX_SLOT_LOOK_MARK0`) while `vm_cut` emits the
NUMERIC one (`RX_CUT(4)`), because `vm_slot_name` names the family and
`vm_cut` formats an index. Reading `slot_values[5]` for the position is the
same convention.

**Three properties, each with the line that makes it true.** They are
`atomic_groups_design.md` §3.3's three, re-stated for this construct because a
reader must not have to go and check that they still hold:

1. **THE MARK'S `RX_SET` PRECEDES EVERY `RX_PUSH` IN THE BODY.** It also makes
   the mark itself TRAILED (`vm_set` is the trailing writer), which is what
   makes NESTING and RE-ENTRY work: an outer backtrack restores the mark slot
   and this entry label re-sets it on every entry, so `(?=a|b)*c` marks
   independently per iteration. The same is true of the POS slot, and it has
   to be: `(?=(?=a)b)c` has two live position slots at once.
2. **`RX_CUT` IS AN ASSIGNMENT, NOT A `min()`.** Correct while
   `resume_depth >= mark` at every cut site, which holds because control
   cannot reach `L_ok` after a pop below the entry frame — such a pop jumps to
   a resume label OUTSIDE the assertion — and nested marks are monotone by
   construction.
3. **NOTHING REWINDS THE TRAIL, and that is the semantics.** Captures written
   inside a POSITIVE lookaround are RETAINED on success and UNDONE on an outer
   failure. MEASURED both ways (`out/captures.txt` C1, C3): `(?=(a))a` on
   `"a"` is (0,1) with g1=(0,1); `(?:(?=(a))x|(a))` on `"ab"` is (0,1) with g1
   **unset** and g2=(0,1). **Only RETENTION discriminates**, because a cut that
   wrongly rewound the trail gets the UNDO half right by accident.

**`vm_cut` IS REUSED UNCHANGED**, and the reason is the one
`atomic_groups_design.md` §3.1 established and this design consumes rather
than re-proves: the no-trail-rewind invariant rests on frame arithmetic, not
on possessify's §2.2 verdict. The one thing to state is that a lookahead's cut
discards frames that are **not dead**, exactly as an atomic group's does —
which is the semantics, and is what §2.2's discriminator measures.

### 3.3 The NEGATIVE form, and why it needs no snapshot at all

This is the finding that makes §3 short. The requirement is: if the body
succeeds the assertion fails; if the body fails the assertion succeeds **with
the cursor and the captures restored**.

```
    L_entry:  RX_SET(SLOT_LOOK_MARKk, run->resume_depth)   // BEFORE any push
              RX_PUSH(&&L_neg_ok, scan_position)           // the "body failed" continuation
              goto L_body
    L_body:   <X>                              -> L_body_won
    L_body_won:   // the body SUCCEEDED, so the ASSERTION FAILS
              RX_CHARGE_WORK(depth - mark);  RX_CUT(SLOT_LOOK_MARKk)
              goto rx_fail
    L_neg_ok: // reached only by POPPING the frame above: the body is exhausted
              goto L_next
```

**There is no capture snapshot and no position slot, and P7 is why. Here are
the two macros, quoted from a real artifact rather than described** (`build/
pcrec` at `d1d4378`, `((a|b)c)`):

```c
#define RX_PUSH(lbl_, p_) do {                                \
        if (run->resume_depth >= RX_RESUME_FRAMES) return RX_R_FRAMES;  \
        run->resume_stack[run->resume_depth].resume_label    = (lbl_);  \
        run->resume_stack[run->resume_depth].resume_position = (p_);    \
        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth; \
        run->resume_depth++;                                            \
    } while (0)
```

and the fail label (`emit_vm.c:6061-6073`, emitted verbatim into every VM
artifact):

```c
    {
        const unsigned frame_index = --run->resume_depth;
        scan_position = run->resume_stack[frame_index].resume_position;
        while (run->trail_depth > run->resume_stack[frame_index].trail_mark) {
            run->trail_depth--;
            slot_values[run->trail[run->trail_depth].slot_index] =
                run->trail[run->trail_depth].saved_value;
        }
        goto *run->resume_stack[frame_index].resume_label;
    }
```

Put those two side by side and the negative form's whole requirement is
discharged by the push: `RX_PUSH` records the cursor **and** `trail_depth` at
entry, and the fail label restores the first and rewinds to the second before
jumping. So arriving at `L_neg_ok` means the cursor is already back and every
capture the body wrote is already undone. **MEASURED that this is the right
semantics**, `out/captures.txt` C2: `(?!(a)x)ab` on `"ab"` is (0,2) with g1
**unset** — the body captured `"a"` and then failed on `x`, and the capture
does not survive; `(?!(a)x)(a)` on `"ab"` is (0,1) with g1 unset and
g2=(0,1), which proves the answer is being read rather than truncated by
libpcre2's trailing-unset rule (the padding `la_oracle.ngroups()` exists for).

**The `L_body_won` cut is not an optimisation.** It discards the body's frames
**and the `L_neg_ok` frame**, because the mark was taken before the push. If
it did not, the failing assertion would leave a live choice point that later
resumes at `L_neg_ok` and lets the whole pattern proceed **as if the negative
assertion had held** — the exact wrong answer. §9's S-LA3 removes the cut and
the row's prediction is that the negative corpus goes red while every positive
cell stays green.

**The negative form is ATOMIC in every spelling PCRE2 has** (§2.1: there is no
`(*nanla:`), so this shape has no non-atomic variant to design.

### 3.4 The LOOKBEHIND: back-step, forward body, end-check

Per top-level branch `i` of fixed width `k_i`, in **written order** (§2.4
level 1):

```
    L_entry:  RX_SET(SLOT_LOOK_MARKk, run->resume_depth)
              RX_SET(SLOT_LOOK_POSk,  scan_position)
              goto L_b1
    L_b1:     if (scan_position < k_1) goto L_b2;            // not enough subject
              RX_PUSH(&&L_b2, scan_position)                 // try branch 2 on failure
              RX_CHARGE_WORK(k_1)                            // the back-step's own work
              scan_position = $_back_step(subject, subject_length, scan_position, k_1);
              goto L_body1
    L_body1:  <B_1>                          -> L_end1
    L_end1:   if (scan_position != (size_t)slot_values[SLOT_LOOK_POSk]) goto rx_fail;
              goto L_ok
    ...
    L_bm:     if (scan_position < k_m) goto rx_fail;          // LAST branch: no push
              RX_CHARGE_WORK(k_m)
              scan_position = $_back_step(subject, subject_length, scan_position, k_m);
              goto L_bodym
    L_bodym:  <B_m>                          -> L_endm
    L_endm:   if (scan_position != (size_t)slot_values[SLOT_LOOK_POSk]) goto rx_fail;
              goto L_ok
    L_ok:     RX_CHARGE_WORK(depth - mark);  RX_CUT(SLOT_LOOK_MARKk)
              scan_position = (size_t)slot_values[SLOT_LOOK_POSk];
              goto L_next
```

The NEGATIVE lookbehind is §3.3's shape wrapped round this one: the entry
pushes `L_neg_ok` first, every branch's success falls into `L_body_won`, and
running out of branches falls through to `L_neg_ok` by ordinary failure.

**`scan_position < k_i` IS THE START-OF-SUBJECT GUARD and it is emitted rather
than delegated.** The seam entry could carry it (§4 gives it a sentinel), and
the guard is here **as well** because a `size_t` comparison against a
compile-time constant is free and because the branch has somewhere to go — the
NEXT branch, not a failure. MEASURED that this is the right semantics
(`out/lookbehind_length.txt` B5): `(?<=a)b` on `"b"` is NOMATCH, `(?<!a)b` on
`"b"` is (0,1), `(?<=abc)x` on `"bcx"` is NOMATCH, and — the cell that shows
branches are independent — `(?<=a|bc)x` on `"cx"` is NOMATCH while `",ab"`-
shaped subjects match through the branch that fits.

**THE END-CHECK IS PROVABLY REDUNDANT FOR THE SUBSET THIS MODULE SHIPS, AND IS
EMITTED ANYWAY. Here is the argument and here is why it stays.** A branch with
`minw == maxw == k` consumes exactly `k` bytes on every successful path (width
is a property of the path, and equal bounds leave one value), so a body
started at `pos - k` that succeeds ends at `pos`. The check therefore cannot
fail on a correct compiler. It is emitted because it is **the only runtime
evidence that the new `pcrec_maxw` analysis agrees with the emitter**: if the
width table is wrong, this comparison turns a silent wrong answer into a
clean no-match at that branch. That is a weaker outcome than an abort and a
much better one than a miscompile. It also **stops being redundant** the day
the variable-length follow-on (§11) lands, which is the second argument for
adopting PCRE2's shape now rather than a shape that has to be replaced.
§14 ASK 2 offers Frank the alternative: `assert()`-style abort under a debug
build, silence under `-DNDEBUG`.

### 3.5 Why forward-plus-end-check rather than a reverse machine

The charter asks this explicitly. Four reasons, the first two structural and
the last two the decisive ones:

1. **pcrec's reverse machine cannot carry the body.** The reverse pass
   (`emit_dfa.c`) is a DFA over the capture-erased pattern (D31's erasure).
   A lookbehind body may contain captures — MEASURED, `out/captures.txt` C1:
   `(?<=(a)(b))c` on `"abc"` reports g1=(0,1) and g2=(1,2) — and may contain
   a backreference (§2.3) and nested lookaround. None of those survive
   erasure.
2. **A reverse VM would be a second emitter over a mirrored AST.** The
   measured cost of that shape is on the record: `revdet.c`'s `rd_node`
   **clears `Ast.possessive` on the reversed copy the emitter walks**
   (`revdet.c:178-179`), which `atomic_groups_design.md` §6.5 found and called
   structural. A second mirrored walk for lookbehind would put the same class
   of bug in front of every construct the body may contain, forever.
3. **The forward body reuses `vm_emit` UNCHANGED.** This is the design's
   single most load-bearing property and it is the same one
   `atomic_groups_design.md` §3.3 named for `vm_cut`: everything inside the
   assertion is ordinary emission, so every rung, every prune, every budget
   charge and every future construct works inside a lookbehind on the day it
   works outside one, with no second implementation to keep in step.
4. **Capture spans come out forward.** A reverse machine would produce
   mirrored offsets needing a fix-up at exactly the place `rd_shape` already
   shows how expensive that is to get right.

**The cost is stated rather than hidden.** For `m` branches the emitted code
runs the body up to `m` times per candidate position, once per branch, and
each run costs its branch's own width. Bounded by `sum(k_i)`, a compile-time
constant. That is worse than a reverse DFA would be and it is bounded, which
is the trade this design takes.

### 3.6 The NON-ATOMIC forms are the atomic shape MINUS the cut

`(?*X)` and `(?<*X)` (and their `(*napla:` / `(*naplb:` spellings) differ from
`(?=X)` / `(?<=X)` in exactly one way: the body's choice points stay live, so
a later failure can re-enter the body and produce a **different** success.
MEASURED, §2.2.

The emitted shape is §3.2's with `vm_cut` not called:

```
    L_entry:  RX_SET(SLOT_LOOK_POSk, scan_position)     // no mark: nothing is cut
              goto L_body
    L_body:   <X>                        -> L_ok
    L_ok:     scan_position = (size_t)slot_values[SLOT_LOOK_POSk];
              goto L_next
```

**And it is correct without any further machinery, for a reason worth
stating.** When the follow fails, a frame inside the body resumes, the body
reaches a second success, and control arrives at `L_ok` **again** — where the
position slot is re-read and the cursor is restored again. The slot survives
that round trip because it was written by `vm_set` (trailed) **before** any
body frame was pushed, so every body frame's `trail_mark` is above the slot's
trail entry and no rewind to a body frame can undo it. The slot IS undone by a
rewind to a frame below the assertion, which is exactly when it should be.

**No mark slot is allocated for a non-atomic form**, which is how a reader
tells the two apart in the emitted C and in `--emit-ir`.

### 3.7 The budgets (D42 item 6, D47's second addendum)

**MEASURED that a lookaround body's work is real and unbounded in the
subject**, `out/captures.txt` C6:

```
^(a+)+$        n=16  0.0064 s   n=20  0.0987 s   n=24  match limit (-47)
^(?=(a+)+$)    n=16  0.0053 s   n=20  0.0956 s   n=24  match limit (-47)
^(a|a)+$       n=16  0.0170 s   n=20  0.2634 s   n=24  match limit (-47)
^(?=(a|a)+$)   n=16  0.0146 s   n=20  0.2592 s   n=24  match limit (-47)
```

The assertion costs **what its body costs**, at every size, and reaches
libpcre2's own match limit at the same `n`. A budget that did not count a
lookaround body's steps would not be a budget.

**Nothing new is needed to count them, and that is the point.** The body is
emitted by `vm_emit`, so every push, pop and cut inside it goes through the
same primitives, and `emit_vm.c:6051`'s single decrement — *"a step is one
backtrack resumption, counted at exactly this place"* — already sees them all.
Two charges are this module's own:

- **The cut**, via `vm_cut`, which already charges `depth - mark` ("work
  charge: frames discarded by this cut"). The positive and negative forms both
  cut; the non-atomic forms do not, and correctly charge nothing, because
  their frames pop through the fail label 1:1 and are charged there.
- **The back-step**, `RX_CHARGE_WORK(k_i)` with `k_i` a literal. Under the
  byte backend the back-step is one subtraction and the charge overstates it;
  under a UTF-8 backend it walks `k_i` characters and the charge is exact.
  **Charging the compile-time constant rather than the runtime cost is
  deliberate**: it makes the artifact's work accounting independent of the
  encoding backend, which is DD-12 (7)'s whole posture.

**FRAMES.** A positive/negative lookaround adds at most **one** frame beyond
what its body needs (the negative form's `L_neg_ok`); a lookbehind adds at
most `m-1` (one per non-final branch), all of which the cut discards on
success. The mark and position slots are two `stv` slots per lookaround, which
is the same accounting `SLOT_CUT_MARK<n>` already has and joins the same
greppable family (`src/gen/CLAUDE.md`'s two rules): **`SLOT_LOOK_MARK<n>` and
`SLOT_LOOK_POS<n>`**, spelled in one place, named in the slot legend.

### 3.8 What a lookaround does to `\G` and to the reported start

MEASURED, `out/captures.txt` C5: `(?=\Ga)a` on `"aa"` is (0,1) at startpos 0
and (1,2) at startpos 1; `(?<=\Ga)b` on `"ab"` is (1,2). `\G` inside a
lookaround means what it means outside one — it is an absolute position test
against `startpos` — and needs nothing from this module. `\K` is refused
(§2.7), so the reported match start is untouched by any lookaround.

**But a lookbehind READS SUBJECT BYTES BEFORE `startpos`, and that is a
contract question rather than a syntax one.** MEASURED, `out/lookbehind_
length.txt` B5: `(?<=a)b` on `"ab"` **at startpos 1** MATCHES (1,2), and
`(?<!a)b` on the same input at the same startpos does NOT. python `re` agrees
on both. So the assertion is evaluated against the real subject, not against
the search window. **This is `assertions_design.md` §3.8's mechanism 4 — the
one R30 raised as E1 and whose reverse-pass half was N1 — arriving for a
second construct**, and for the VM it is free: the VM's `subject` pointer is
the whole subject and `scan_position` is an absolute offset, so `pos - k`
reaches before `startpos` with no extra plumbing. §9's S-LA8 clamps the
back-step to `startpos` and the row's prediction is that the corpus's
`ms`-startpos cells go red while every startpos-0 cell stays green. **§12 P-8
is the honest statement of what this does NOT cover**: the DFA prefilter's
own start seeding is a different mechanism and §5 handles it separately.

---

## 4. The seam's THIRD residual entry (charter (iii))

### 4.1 The signature, designed for the backend that does not exist yet

```c
/* $_back_step -- the ENCODING RESIDUAL entry for a LOOKBEHIND BACK-STEP
 * (pcrec DD-12/D58).
 *
 * Returns the position exactly `k` CHARACTERS before `pos`, or
 * $_BACK_STEP_NONE when fewer than k characters precede pos.
 *
 * Reads s only at offsets in [0, pos).
 *
 * THIS artifact was compiled for the `byte` encoding, where one byte is one
 * character, so the answer is pos - k and the subject is never read. An
 * artifact compiled for another encoding exports this same entry with that
 * encoding's body and no engine code changes.
 */
size_t $_back_step(const unsigned char *s, size_t n, size_t pos, size_t k);
#define $_BACK_STEP_NONE ((size_t)-1)
```

Byte backend:

```c
size_t $_back_step(const unsigned char *s, size_t n, size_t pos, size_t k)
{
    (void)s; (void)n;
    return k > pos ? $_BACK_STEP_NONE : pos - k;
}
```

**THE RETURN PROTOCOL DIVERGES FROM ENTRY 2's AND THE PANEL SHOULD ASK WHY.**
`$_bref_match` returns a `ptrdiff_t` whose sign carries a second fact (the
compared prefix, which the caller charges). A back-step's failure carries no
second fact: "fewer than k characters precede pos" is one bit, and the WORK
the entry did is `k`, which the **caller already knows at compile time** and
charges with a literal (§3.7). A sentinel is therefore the honest encoding,
and `(size_t)-1` cannot collide with a legal position because a legal position
is `<= n` and `n == SIZE_MAX` is not a representable subject.

**WHY `n` IS A PARAMETER AT ALL** when the byte backend ignores it and the
entry reads only below `pos`: a UTF-8 backend validating a sequence needs the
subject's bounds to reject a truncated one, and adding a parameter later is an
ABI break the seam's whole point is to avoid. The unused-parameter cast is the
same one `$_next_pos` already carries and for the same reason.

### 4.2 What a UTF-8 backend has to do differently

Recorded now, because D58's honest risk statement was that a seam with one
backend is unvalidated until the second arrives, and the concrete enumeration
is the mitigant:

1. Walk back `k` times, each time skipping continuation bytes (`0x80..0xBF`)
   until a lead byte is found.
2. Return `$_BACK_STEP_NONE` if the walk runs off the start **or** if it
   encounters a malformed sequence — the second is a case the byte backend
   cannot have and the reason this entry has `s` and `n` at all.
3. **The CALLER'S `scan_position < k` guard (§3.4) is then a fast path and not
   the answer.** Under UTF-8, `k` characters is at least `k` bytes, so the
   guard still soundly rejects; it just stops being exact, and the entry's
   sentinel is what makes it correct. **§9's S-LA7 deletes the sentinel check
   at the call site**, and it is a row precisely because under the byte
   backend it changes no answer.
4. The **width** `k_i` computed at parse time is in CHARACTERS, not bytes. For
   the byte backend those are the same number. `pcrec_maxw`/`pcrec_minw`
   count bytes today (`mrl.c`'s whole contract is in bytes), so **a UTF-8
   backend needs the width analysis in characters as well** — an obligation
   this design records against D58 rather than solving, since M5's lowering
   instance does not exist.

### 4.3 The mask bit, and the interface change that ISN'T

```c
    /* In the mask only when the artifact contains a LOOKBEHIND. */
    PCREC_ENCE_BACK_STEP = 1u << 3
```

One new enumerator, one new `PcrecEncEntry` row in `entries_byte[]` with
`engine_callable = true`, and the `A_LOOK` arm ORs the bit when
`look_behind`. **That is the entire seam change.**

**D58's revisit clause is honoured by having nothing to record**, and that is
itself the finding. D58 says *"any interface change it forces gets recorded
against this entry"*. The [M6.5.2] entries-table refactor was justified in
`enc.h`'s own comment by predicting **this** construct: *"THE ROAD NOT TAKEN:
two more string fields (`bref_decls`/`bref_defs`). Simpler, and it does not
generalise — lookbehind's back-step ([M6.6]) is the next residual entry D58
already names, and it would need a third pair."* This module is that
prediction's test, and it passes: no field is added, no signature changes,
`pcrec_enc_ready` is untouched, the two emit functions are untouched, and the
third-encoding recipe is unchanged. **§12 P-1 makes this a falsifiable
prediction rather than a compliment.**

### 4.4 The [M5-SEAM] codegen check, and the number it asserts

STRUCTURAL, `tests/codegen/run_codegen_tests.sh` from line 898. The check as
[M6.5.2] left it is exactly what this module needs and needs **three
additions, none of them to its mechanism**:

1. **The entry declares itself callable**, so the check reads
   `engine_callable` off the backend row (`enc.h`) rather than from a list of
   its own. Already built.
2. **New fixture rows** in the 4-column TAB-separated table, whose fourth
   column is the declared `<suffix>:<count>` set. A lookbehind fixture
   declares `back_step:<n>` where `n` is **the number of top-level branches**
   — a human-written integer beside the pattern, never derived. R32 C2(a)'s
   ruling applies here with a sharper edge than it had for backrefs: deriving
   the count by counting `|` in the body would be **a second implementation of
   §2.5's branch-splitting rule**, and it would get `(?<=(a|bc))x` (refused,
   one branch) and `(?<=a|bc)x` (two branches) exactly backwards — which are
   the two cells §2.5 exists to distinguish.
3. **The EXACT non-vacuity guard's literal moves**, and this design states the
   number rather than leaving it to be discovered. Today the guard asserts
   **exactly 4** fixtures declare a `bref` entry. This module adds a
   **second** such guard — *"exactly N fixtures declare >= 1 `back_step`
   entry"* — with its own literal, rather than folding lookbehind fixtures
   into the existing count. Two reasons: the counts measure different things,
   and R32's own argument against a floor applies within a family, not across
   families. **§11's landing bar carries N as a deliverable**, because R32 C5
   found "the built column gains this module's rows for free" asserted by
   nothing, and a guard whose literal nobody wrote down is the same shape.

**The alternative, named and rejected:** emit `pos - k` inline in
`vm_look`. It keeps the check untouched and puts encoding-sensitive byte
arithmetic in shared emitter code — precisely what D58 exists to prevent, what
the [M6.6] plan row forbids in its own text (*"a seam entry, never raw
`pos - k` byte arithmetic in shared emitter code"*), and what is **correct
today and silently wrong under a UTF-8 backend**. §9's S-LA6 is the sabotage
that inlines it, and — like S109 for the bref compare — the fixture-declared
per-site count is its **only possible detector**, because inlining changes no
answer under the byte backend.

---

## 5. Engine selection and the prefilter (charter (iv))

### 5.1 Every row stays VM_ONLY, and SR-8 does the consulting

MEASURED (P4): all six rows are `VM_ONLY` today. They stay so. D67 rules SR-8
built as of [M6.4.2] — every AST node from an `RS_MODULE` row is stamped with
its row's `engines` mask at construction and one generic `EngineAnalysis` ANDs
the stamps over the post-discharge tree — so **this module writes no
`forces_lookaround` predicate**. It stamps, and SR-8 consults.

That is not a small saving. R32 M-1/C1 found that a `forces_backref` predicate
would have been a **third** hand exception covering **twelve** registry rows
to a check whose own text says the second one builds SR-8. This module would
have been the fourth, covering six more.

**`--engine=dfa` refuses** and needs no new code: SR-8's consultation over a
tree containing an `A_LOOK` yields VM, and the existing override path reports
it. There is one thing to check rather than assume — `backrefs_design.md` §6.2
recorded a **pre-existing defect** in which `--engine=dfa` advises
`--no-captures` for every capture-bearing pattern, which for that module's
whole population is advice that cannot help. **For this module the advice is
sometimes right and sometimes not**: `--no-captures '(?=a)b'` is still
VM-forced (the lookaround is, independent of captures), so the advice does not
help; `--no-captures` on a lookaround-free capture pattern is unaffected. §11
carries "check the `--engine=dfa` diagnostic on a lookaround pattern and do
not repeat backrefs' unhelpful advice" as a landing item, not a fix.

### 5.2 There IS a prefilter, and this module is not backrefs

`backrefs` turned the prefilter **off** (`select_engine.c:484-541`) because a
backref-erased pattern is not even a superset once the referenced group's
transitive closure holds an assertion. `atomic-groups` **kept** the prefilter
and dropped only the window-end ceiling. **This module is the atomic-groups
case**, and §5.4 measures it rather than reasoning by analogy.

**The lowering that makes the prefilter exist**: `src/ir/nfa.c` gains an
`A_LOOK` arm that lowers the node to **epsilon** — the assertion is simply
dropped. That is the erasure §5.3 argues about, and it is what makes the
prefilter's DFA answer for the lookaround-free language.

**THE HAZARD THAT CREATES, NAMED RATHER THAN BURIED.** One lowering now serves
two consumers with different soundness requirements: as a **prefilter** the
erasure is sound (§5.4), and as **the DFA engine's own machine** it is a
miscompile. Only SR-8's `VM_ONLY` stamp stands between them. `atomic-groups`
has the identical coupling (`nfa.c` lowers an atomic body transparently) and
the identical guard, so this is precedent rather than novelty — but with one
difference in this module's favour worth recording: **an erased lookaround is
loudly detectable**, because `(?=a)b` erased is `b` and answers (0,1) on
`"b"` where the truth is NOMATCH. Backrefs' `next_pos` hazard was undetectable
by every oracle in the tree; this one is caught by the first corpus cell.
§9's S-LA5 removes the stamp.

### 5.3 The soundness argument, stated before it is measured

**A lookaround is zero-width and purely a constraint**, so for any pattern `P`
and any string `s`, if `P` matches `s` at position `p` then `erase(P)` matches
`s` at `p`: every path through `P`'s machine is a path through `erase(P)`'s
with the assertion's verdict removed, and removing a conjunct cannot fail a
path that succeeded. **`L(P) ⊆ L(erase(P))` at every position. ARGUED, and it
is a one-line proof.**

**That is not the property the hybrid needs**, which is the lesson
`atomic_groups_design.md` §4 and `backrefs_design.md` §7 both paid for. The
emitter uses three separate things from the prefilter and they are separately
falsifiable:

| | what the emitter does with it | where |
|---|---|---|
| **H1 REJECTION** | no prefilter match ⇒ the search returns no match without running the VM | `emit_vm.c`'s prefilter block, `:5884` |
| **H2 START** | the prefilter's window start seeds the VM's candidate position, and the loop re-asks on every retry | `emit_vm.c:5283-5300`'s own note |
| **H3 END** | `min(n, window[0][1])` becomes the **[M4.6d] MRL pruning CEILING** when `v.mrl_win` | `emit_vm.c:5319`, `:2177-2179` |

### 5.4 What was measured

MEASURED, `out/prefilter_hazard.txt`, **45 cells over 11 families**, with a
fixture-tested `erase()` printed in full, and both vacuity guards passing (14
cells exercise the erasure; the positive control produces 8 violations, so a
zero would have been a real result).

```
H1 violations (rejection unsound)            : 0
H2 violations (erased start too LATE)        : 0
H3 violations, NAIVE leftmost-vs-leftmost    : 12
H3 violations, SHARP anchored-at-true-start  : 8
```

**H3 IS REPORTED TWICE AND ONLY THE SECOND NUMBER IS THE ONE THAT MATTERS.**
The naive comparison — leftmost end of `erase(P)` against leftmost end of `P`
— conflates two failures, because when the erased match sits at an EARLIER
start the two ends are not about the same candidate and the emitted retry loop
re-asks the prefilter at every start it advances to. The sharp form fixes the
start: at the candidate start the true match uses, does the erasure **anchored
there** end at or after the true end? **12 becomes 8, and all eight are in the
planted controls** — the eight natural families (leading and trailing, positive
and negative, lookahead and lookbehind, the `\b`-shaped word-pair) produce
**zero** sharp violations.

**So the hazard has a NAME and a SHAPE rather than being a blanket.** Every
sharp violation is a lookaround **inside an alternation**, positioned so that
erasing it lets an **earlier-preferred branch succeed to the end of the
pattern** at the same start:

```
a(?!b)|ab        on "ab"    true (0,2)   erased-anchored-at-0 (0,1)
a(?<=xa)|ab      on "ab"    true (0,2)   erased-anchored-at-0 (0,1)
(?:a(?=c)|ab)c?  on "abc"   true (0,3)   erased-anchored-at-0 (0,1)
```

The model is faithful rather than assumed: **P16** measured pcrec's own
artifact for `(a|ab)` on `"ab"` printing `match 0 1` — leftmost-FIRST — which
is what makes an anchored PCRE2 search the right stand-in for what pcrec's
prefilter would report.

### 5.5 And it coexists with a LIVE ceiling, on 16 of 30 shapes

The question that decides the ruling is not whether H3 can fail but whether it
can fail **on a pattern whose artifact actually carries a prefilter-window
ceiling**, since `v.mrl_win` is only live when the emitter raised a clamp
site. MEASURED, `out/d66_subset.txt` S3, sweeping 5 heads × 6 tails against 12
subjects, with the erasure compiled by the **shipped** pcrec and its
`RX_VM_PRUNE_CEILING` stamp read off the artifact:

```
VACUITY GUARD: 20 of 30 erasures carry a LIVE prefilter-window ceiling
SHAPES TRIED: 30.  QUALIFYING (ceiling live AND H3-sharp violated): 16

  ((?:a(?!q)|aq)(?:xy){0,4}q)   erasure ((?:a|aq)(?:xy){0,4}q)
      subj='aqq'    true=(0,3)  erased-anchored-there=(0,2)
      subj='aqxyq'  true=(0,5)  erased-anchored-there=(0,2)
      subj='aaqq'   true=(1,4)  erased-anchored-there=(1,3)
```

**THE FIRST VERSION OF THIS SWEEP REPORTED 0 QUALIFYING OVER A SPACE IN WHICH
0 WAS THE ONLY POSSIBLE ANSWER**, because every tail it used was nullable and
the emitter raises no clamp site for a nullable-follow bounded repeat, so
condition (a) read `"none"` on all 36 shapes. The reachability guard that now
stands — *at least one erasure must really stamp `"prefilter-window"`* — is
what turned an unfalsifiable zero into the number above. It is recorded here
and in `out/CLAUDE.md` because publishing that zero would have made §5.6's
ruling look free when it is necessary.

### 5.6 THE RULING

1. **The prefilter SHIPS.** H1 and H2 hold at 0 violations over 45 cells, so
   rejection and start-seeding are sound. Dropping the prefilter would be a
   DD-2 regression by `engine_m4.md` §4.7's own standard and would cost the
   one-to-two orders of magnitude `backrefs_design.md` §7.3 measured for the
   module that had to.
2. **The WINDOW-END CEILING IS DROPPED for any pattern containing a
   lookaround.** One predicate, at the one place [M6.4.2] already put the
   analogous one:

   ```c
   v.mrl_win = job->fit.prefilter && !pcrec_has_atomic(root)
                                  && !pcrec_has_lookaround(root);
   ```

3. **AND THE PREDICATE IS READ AT ALL THREE SITES, NOT ONE.** This is R31 E3's
   finding consumed rather than repeated: the first design of the atomic fix
   edited `v.mrl_win` alone, while the lines that BUILD the ceiling (the
   search entry's `window_end = min(window[0][1], n)` and the retry recompute)
   were gated on `prefn` and `v.nclamp > 0` and never on the flag — **so
   flipping it would have stamped `"subject-end"` on an artifact whose ceiling
   was still live, and the check would have agreed with the bug.** Codegen
   rule 1 asserts on both sources for the atomic case; this module extends the
   same assertion rather than adding a parallel one.
4. **`pcrec_has_lookaround` is asked of the POST-DISCHARGE tree**, for the same
   reason `pcrec_has_atomic` is: if a future pass ever deletes a provably
   vacuous lookaround (§5.7), the pattern should get its ceiling back.

**The narrower alternative, named and rejected.** §5.4 shows the hazard needs
a lookaround inside an alternation, so a predicate could ask for that shape
instead of for any lookaround. Rejected: the shape condition is a second
analysis with no independent check, the atomic precedent is a flat predicate,
and the measured cost of the flat one is that a pattern loses a pruning
ceiling it would rarely have had — against a silent match loss if the shape
analysis is wrong anywhere.

### 5.7 THE DFA ANSWER IS [ENG-LOOK], AND THERE IS NO FOLD

**RULED by Frank, 2026-08-23 13:5x, and this section is a rewrite rather than
a recommendation.** An earlier revision of this design proposed a
ONE-CHARACTER FOLD: recognize a lookaround whose body is a single class and
rewrite it into the assertions module's existing context-assertion node, so
`(?<=\n)`-shaped lookarounds stayed DFA-eligible. **That is refused.** Frank's
words, recorded in the `[ENG-LOOK]` plan row: *"my concern is unnecessary
special handling code and duplicate code paths … is the one character
optimization the best form, or merely one that works for the immediate
need?"* It is the latter. **No one-character fold ships anywhere.**

**THE GENERAL FORM IS CHARTERED AS `[ENG-LOOK]`** (plan.md, `43a3125`):
lookaround by PRODUCT CONSTRUCTION in the DFA. `(?<=L)` at `p` holds iff
`subject[..p] ∈ Σ*·L` — a property of text the forward scan has ALREADY
CONSUMED — so the main automaton is product-constructed with each body's
recognizer during determinization and the assertion becomes a predicate on the
product state; `(?=L)` is the same property in the REVERSE machine; bounded
lookahead in the forward pass is a k-byte delayed acceptance; unbounded
lookahead in the forward pass is DROPPED (a superset — §5.3, and sound for
end-finding) and resolved in the reverse pass or by the VM. **Today's
assertions machinery IS that construction for one-class bodies** and becomes
an INSTANCE, then gets deleted under an identity gate — which is exactly why a
fold would have been the duplicate path rather than a step toward it.

**SO THIS MODULE'S §5 IS THREE SENTENCES.**

1. **[M6.6.2] ships the VM lowering as THE SEMANTICS.** Every lookaround
   pattern is VM-routed: the six registry rows stay `VM_ONLY` and SR-8 stamps
   (§5.1). The VM remains the exact verifier and the only engine that can
   carry captures, backreferences and nested lookaround inside a body — a
   fact §3.5 already measured (`(?<=(a)(b))c` reports both groups).
2. **The DFA answer is `[ENG-LOOK]`**, a follow-on ENGINE row with its own
   design gate and its own D6 panel. Not this module's to build and not this
   module's to prejudge.
3. **What this design HANDS [ENG-LOOK]** is §5.3-§5.6's prefilter soundness
   statement and hazard measurement, §5.8's sizing inputs, and §3's sub-program
   requirement (§6.4). Those three are the row's own stated prerequisites and
   they are discharged here.

### 5.8 SIZING INPUTS FOR [ENG-LOOK]

The `[ENG-LOOK]` row says **MEASUREMENT FIRST** and names the number: the size
of each body's component automaton and the expected product growth against the
caps, with wave B's 38,009-against-32,000 as the precedent. MEASURED,
`out/englook_sizing.txt`.

**THE METHOD, stated so a panel can reject it.** The component a lookBEHIND
body `L` needs is the recognizer for `Σ*·L`, and **pcrec's UNANCHORED FORWARD
DFA for the pattern `L` IS that machine** — unanchoredness is the automaton's
own self-loop (D58's "Why" paragraph), which is precisely the `Σ*` prefix. The
component a lookAHEAD needs is `reverse(L)·Σ*`, and pcrec's REVERSE machine
for the same pattern is that. So the probe compiles the BODY ALONE and reads
**the emitter's own array dimensions** out of the emitted C —
`len(rx_forward_is_accepting[])` for states, `len(rx_forward_next_state[]) /
states` for classes — with no model in between and nothing derived by the
probe itself. The caps are `PCREC_MAX_DFA_STATES_GOTO = 10000` and
`PCREC_MAX_DFA_STATES_TABLE = 32000` (`src/core/limits.h:47-49`).

**THE COMPONENTS ARE SMALL.** Every body in the assertion-family expansions
and every body in an enumerable real-lookaround population:

| body | origin | forward st × cls | reverse st × cls |
|---|---|---|---|
| `\w` | `\b`, `\B`'s four bodies | 2 × 2 | 2 × 2 |
| `\n` | `(?m)^`, `(?m)$` | 2 × 2 | 2 × 2 |
| `\n?\z` | `\Z` and default `$` | 5 × 2 | 3 × 2 |
| `foo` | ENG-LOOK's own `(?<=foo)bar` | 4 × 3 | 4 × 3 |
| `\d` | ENG-LOOK's own `(?<!\d)\d{4}(?!\d)` | 2 × 2 | 2 × 2 |
| `,` `[a-z]` `[^"']` `\w+` | the construct table's | 2 × 2 | 2 × 2 |
| `ab` / `abc` / `a\|bc` | fixed bodies, incl. §2.5's two-branch cell | 3-4 × 3-4 | same |
| `\d{3}` / `\d{4}` | counted | 4-5 × 2 | same |
| `https?` | a realistic literal-ish body | 6 × 5 | 6 × 5 |
| **controls** | `\d{4}-\d{2}-\d{2}` / `[a-z]{12}` / `(?:ab\|cd){8}` / `(?:a\|b\|c\|d){10}` | 11-25 × 2-5 | same |
| **control** | `[01]*1[01]{12}` — bench case (f)'s shape | **12288 × 3** | 14 × 3 |

**THE PRODUCT BOUND, and the split is the result.** The bound is
`|D(main)| × Π|D(component)|` — an UPPER bound, which is the right quantity
because the row's decline rule ([ENG-CUT]'s shape: ESTIMATE BEFORE COMMITTING)
must be written against a bound and not a hope. Reported beside the
**states × classes** product, because wave B's own over-cap number was that
second quantity and not the first.

```
ROWS: 126.  Over the 32,000 STATE cap: 18.
  CONTROL rows     (a deliberately huge body or main): 62, 18 over cap
  NON-CONTROL rows (the assertion expansions + the enumerable
                    real lookaround population)      : 64,  0 over cap
  largest state product in the population: 150,994,944 -- 4,719x the cap
```

**The vacuity guard is what makes the zero worth reading.** A table of
"0 over cap" over a population containing no cell that COULD be over measures
nothing — this lane published exactly that once already (§5.5). The control
bodies exist so the guard can pass, and it does: the population reaches
4,719x the cap.

**THE HONEST READING, which is an input rather than a verdict this lane is
entitled to give:**

- Every component the assertion family and an enumerable real population
  produce is **2 to 25 states**, so the product's STATE growth on that
  population is multiplicative by a small constant. Largest non-control
  `states × classes`: **720**.
- The explosion, when it comes, comes from a body or a main that is **already
  a state-explosion shape** (`[01]*1[01]{12}` at 12,288 states — DD-9's own
  case (f)). That is a real population for the decline rule to decline on, and
  it means the rule is load-bearing rather than ceremonial.
- **NOTHING HERE MEASURES A PRODUCT.** pcrec cannot build one, so every number
  is a bound computed from two separately-measured machines. A real product is
  smaller wherever the components share structure — which is [ENG-LOOK]'s own
  first measurement to make, and §12 P-11 says so.

---

## 6. THE ASSERTION-FAMILY REPLACEMENTS, and the D66 / DD-14 hand-off

**Frank, 2026-08-23:** *"for lookaround, consider as test cases/design
examples the replacements we were discussing, e.g. `^` under `(?m)`."*

The replacements are [DD-11]/D66's definition-expansion forms: each member of
the assertion family rewritten as the lookaround it IS. This section uses them
three ways — as DESIGN EXAMPLES worked through §3's lowering (§6.2), as a
TEST-CORPUS GENERATOR (§6.3), and as ORACLE-DIVERGENCE input for §7 (§6.5) —
and states what the PRODUCT-side substitution is and is not (§6.4).

### 6.1 The table, measured rather than transcribed

MEASURED, `out/expansions.txt` E1: **972 cells, 0 disagreements**, over 18
subjects × 6 tails, with **both arms carrying the same option state**.

| construct | expansion | cells | disagreements |
|---|---|---|---|
| `\b` | `(?:(?<=\w)(?!\w)\|(?<!\w)(?=\w))` | 108 | **0** |
| `\B` | `(?:(?<=\w)(?=\w)\|(?<!\w)(?!\w))` | 108 | **0** |
| `(?m)^` | `(?:\A\|(?<=\n)(?!\z))` | 108 | **0** |
| `(?m)$` | `(?:(?=\n)\|\z)` | 108 | **0** |
| `\Z` | `(?=\n?\z)` | 108 | **0** |
| `$` (default flags) | `(?=\n?\z)` — i.e. `$` IS `\Z`, measured | 108 | **0** |
| `^` (default flags) | `\A` | 108 | **0** |
| `\A`, `\z` | PRIMITIVES — they are the floor, no expansion | — | — |
| `\G` | **NO EXPANSION**: a primitive against `startpos` | — | — |
| `\K` | **NO EXPANSION**: a match-START operator, and PCRE2 refuses it inside a lookaround (err 199, §2.7) | — | — |

**THE VACUITY GUARD FIRES**: `\A|(?<=\n)` — the D66 expansion with the
`(?!\z)` term dropped — disagrees with `(?m)^` on **4 of 108** cells. So a
wrong expansion CAN show up in this table, and the zeros above are results.

**AND pcrec's SHIPPED FOLDED FORMS AGREE WITH libpcre2's EXPANSIONS**:
`out/expansions.txt` E4, **0 disagreements over 324 cells**, on artifacts
compiled `--features all --emit-main` and run. That is the D66 self-oracle
run on the expansions themselves, and it is what makes §6.3's corpus-wide
driver worth building rather than speculative.

### 6.2 Each replacement worked through §3's lowering

The design examples the charter asks for. Every expansion's bodies, and what
§3 emits for each.

| expansion | its lookaround bodies | direction | §2.5 verdict | §3's emitted shape |
|---|---|---|---|---|
| `\b`, `\B` | `(?<=\w)`, `(?<!\w)`, `(?=\w)`, `(?!\w)` | two behind, two ahead | **SHIPS** — one class, fixed width 1 | the lookbehinds take §3.4 with `m == 1, k == 1`: guard `scan_position < 1`, one back-step, one class test, the end-check. The lookaheads take §3.2/§3.3 with a one-node body |
| `(?m)^` | `(?<=\n)`, `(?!\z)` | one behind, one ahead | **SHIPS** — width 1; `(?!\z)`'s body is an ANCHOR, width 0 | `(?!\z)` is §3.3's negative shape over an `A_END` body: one push, an anchor test, the cut. **The narrowest instance of the negative form in the whole module** |
| `(?m)$` | `(?=\n)`, plus a bare `\z` | one ahead | **SHIPS** | §3.2 over one class |
| `\Z`, `$` | `(?=\n?\z)` | ahead | **SHIPS** — and it is the interesting one | the body is `\n?\z`: an OPTIONAL then an anchor, widths 1..2. **A lookAHEAD has no width rule at all**, so this compiles; the SAME body as a lookbehind would be refused by §2.5 |
| `^`, `\A`, `\z` | none | — | — | no lookaround is emitted; these are the primitives |

**THE ONE CELL WORTH THE PANEL'S ATTENTION is `(?=\n?\z)`.** It is the only
expansion whose body is variable-width, and it ships **because the width rule
is a property of DIRECTION and not of the body** (§2.5 constrains lookbehind
branches only). MEASURED, `out/expansions.txt` E2, with the discriminating
column written out: `(?<=\n?\z)x`, `(?<=\n?)x` and `(?<=\w?)x` all compile in
PCRE2 (maxlb 1) and all have `minw 0, maxw 1`, so **pcrec refuses all three as
LOOKBEHINDS** while accepting the identical body inside a lookahead.
`PCRE2_INFO_MAXLOOKBEHIND` alone cannot show this — it publishes only the max
— which is why the classification is stated from the body's shape and marked
as such rather than read off the oracle.

**CONSEQUENCE, and it is the section's main design result: every assertion in
the family expands to a lookaround [M6.6.2] CAN COMPILE.** Nothing in the
expansion set needs variable-length lookbehind, a backreference in a
lookbehind, or `\K` in a lookaround. The subset §2.5 ships is exactly big
enough for the D66 chain, which is a coincidence worth checking rather than
assuming — and §12 P-12 is how to refute it.

**AND EACH BODY'S ENG-LOOK COMPONENT IS TINY** (§5.8): `\w` and `\n` are 2×2,
`\n?\z` is 5×2 forward and 3×2 reverse. The expanded corpus is therefore also
the cheapest possible population for `[ENG-LOOK]`'s product construction to be
measured on first.

### 6.3 THE SUBSTITUTION DRIVER — a corpus generator, designed here, built in [M6.6.2]

**Textually replacing each assertion by its expansion turns the assertions
module's corpus into a LOOKAROUND corpus for free.** The assertions corpus is
468 blocks and **10,120 behavioural cells**, every one libpcre2-verified. It
is also, by construction, the corpus of a module that already ships — so its
expectations are not this lane's guesses.

**IT IS A CORPUS GENERATOR, NOT A PRODUCT MECHANISM** (Frank, 13:4x; the
[DD-14] row's own text). It emits PATTERNS that the compiler sees as ordinary
user-written lookarounds. §6.4 is where the product side goes.

**THE THREE-WAY CHECK, per cell:**

```
  A  the EXPANDED pattern compiled by pcrec        (the new lookaround path)
  B  the FOLDED pattern compiled by pcrec          (the shipped assertions path)
  C  libpcre2 on the EXPANDED pattern              (the external oracle)

  A == B  is the SELF-ORACLE D66 describes: pcrec's two lowerings of one
          language must agree. It needs no external oracle at all, which is
          what makes it usable on every cell including the ones python cannot
          take.
  A == C  is the ordinary differential, and it is what stops A == B passing
          because BOTH lowerings are wrong the same way.
```

**Both comparisons are required and neither is sufficient**, and that is the
whole design of the check: `A == B` alone is satisfiable by a compiler that is
consistently wrong, and `A == C` alone does not test the folded path the
expansion is supposed to be equivalent to.

**WHICH CELLS QUALIFY.** MEASURED (pure text; no compiler ran),
`out/substitution_population.txt`:

```
  blocks                          468
  behavioural cells            10,120     (+ 67 capture-slot cells = 10,187)

  QUALIFYING blocks               270 of 468   (58%)
  QUALIFYING behavioural cells  8,495 of 10,120 (84%)

  disqualified, by rule:
    Q1 perr / no behavioural cell     87 blocks     0 cells
    Q2 no substitutable assertion     87 blocks   754 cells
    Q3 assertion inside a class        0 blocks     0 cells
    Q4 scoped (?m: or (?-m)           24 blocks   871 cells
    Q5 \K inside a substituted body    0 blocks     0 cells
```

**THE FIVE QUALIFICATION RULES, each with the reason it exists:**

- **Q1 — the block must have a behavioural cell.** A `perr` block asserts
  pcrec REFUSES the pattern; the expansion changes the reason for the refusal,
  so the assertion under test is gone. 87 blocks, and they cost 0 cells
  precisely because they have none.
- **Q2 — the pattern must contain a substitutable assertion.** `\G` and `\K`
  have no lookaround definition (§6.1). 87 blocks, 754 cells.
- **Q3 — no substitutable assertion inside a CHARACTER CLASS.** `[\b]` is the
  BACKSPACE byte and `[^a]` is a negation; substituting either produces a
  different pattern, not a rewritten one. **It costs 0 blocks on this corpus
  and the rule is still required** — a `sed`-based driver would be wrong the
  first time a class contained one, and the backrefs lane's own `sed 's/\\1//'`
  defect is the precedent for exactly this.
- **Q4 — no scoped `(?m:` or `(?-m)`.** `^` and `$` mean different things
  under different multiline states, so a textual driver must know the state at
  each occurrence. With `(?m)` leading and unscoped the state is constant and
  knowable; with a scoped group it is not, and resolving it is a parser — which
  is what the driver is trying not to be. **The most expensive rule: 24
  blocks, 871 cells.** A driver that later grows a scope tracker recovers
  them, and §11's follow-on says so.
- **Q5 — `\K` must not land inside a substituted body**, since PCRE2 refuses
  it (err 199). It cannot, given the bracketing rule below, and it is counted
  anyway so the claim is a number rather than an argument: 0.

**THE BRACKETING RULE, and it is what keeps the corpus's cells reusable.**
Every multi-branch expansion is wrapped `(?:...)` before insertion, so `a\bc`
becomes `a(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))c` and not the top-level-alternation
pattern a naive splice produces. **`(?:` is NON-CAPTURING, so group numbers
are unchanged and every `g`/`gp` capture-slot expectation survives untouched**
— which is why the driver reuses the corpus's cells verbatim instead of
re-deriving them. 13 capture-slot cells ride along.

**TWO SUBSTITUTION POLICIES, and the second is the one that finds bugs:**

- **P1 ALL-AT-ONCE** — every occurrence in the pattern replaced. **270
  patterns.** A half-substituted pattern tests neither form, so this is the
  baseline policy.
- **P2 ONE-AT-A-TIME** — one occurrence replaced per generated pattern, the
  rest left folded. **368 patterns** (one per occurrence). This is the MIXED
  form, where a folded assertion and an expanded one must agree INSIDE ONE
  PATTERN, and it is where an interaction between the two lowerings would show
  — a `\b` lowered to `A_WORDB` beside a `(?<=\w)(?!\w)` lowered to `A_LOOK`,
  in the same artifact, sharing the same alphabet refinement.

**638 generated patterns over ~8,495 cells each.** The driver's own home is
`tests/lookaround/run_expansion_diff.sh`, and it is **also [DD-11]'s
regression harness** — the row's substitutions have to keep this green.

**THE DRIVER'S OWN FAILURE MODE, named because every check in this project
that has failed has failed this way:** the expansion table it substitutes FROM
must not be derived from the compiler. It is a literal table in the driver,
transcribed from D66 and [DD-11] and independently verified against libpcre2
(§6.1). If [DD-11] later rewrites the assertions to their definitions on the
[DD-14] primitive, **the driver's table and the compiler's must remain two
sources**, or `A == B` becomes a tautology.

### 6.4 THE PRODUCT-SIDE SUBSTITUTION IS [DD-14]'s, NOT THIS MODULE'S

**RULED (Frank, 13:4x):** *"for the actual substitutions, let's get the group
reference piece in so that they share code/handling before we do the
substitutions. I don't want parallel mechanisms if we can avoid it."* The
order is `[M6.6]` lookaround → `[DD-14]` subroutine calls (`(?1)`, `(?&n)`,
`\g<n>`, `(?R)` — module `recursion`, the label-call primitive) → `[DD-11]`'s
definition substitutions IMPLEMENTED ON that primitive (an insertion is a
NON-RECURSIVE CALL to the inserted body's entry label; compile-time splicing
is an optimization of it, never a second mechanism) → D66's core
lookbehind-anchor optimizer.

**SO THIS DESIGN PROPOSES NO PARSE-TIME OR IR-TIME DESUGAR MECHANISM FOR
ASSERTIONS.** Not a fold (§5.7), not an expansion. What it owes instead is to
make §3's lowering a shape the call primitive can target.

**WHAT LOOKAROUND MUST PROVIDE, and §3 already provides it:**

1. **EVERY LOOKAROUND BODY IS A SELF-CONTAINED SUB-PROGRAM WITH A CLEAN ENTRY
   AND EXIT LABEL.** §3.2's shape is `L_entry → L_body → L_ok`, where
   `L_body` is the body's own entry produced by an ordinary `vm_emit` call and
   `L_ok` is the single exit. The body has **exactly one entry** (nothing
   jumps into its middle) and **exactly one success exit** (`L_ok`); failure
   leaves through the shared fail label like every other construct. That is
   precisely a call target: push a return label, `goto L_body`, and
   pop-and-`goto*` at `L_ok`.
2. **THE SUB-PROGRAM'S STATE IS IN TRAILED SLOTS, NOT IN LOCALS.**
   `SLOT_LOOK_MARK<n>` and `SLOT_LOOK_POS<n>` are `stv` slots written by
   `vm_set` (§3.2), so a call that re-enters the same body from a different
   site re-initialises them at the entry label and an outer backtrack restores
   them. A design that had put the saved cursor in a C local would have been
   correct for one entry and wrong for a call primitive — the same reason
   [ENG-BREP counter-K] ruled its counter a trailed slot rather than a local.
3. **NO LABEL IS SHARED BETWEEN TWO LOOKAROUNDS.** `vm_label()` allocates per
   emission, and the slot families are indexed per node (`v->nmark++`), so two
   lookarounds over the same body text get two sub-programs. **[DD-14]'s
   sharing is a later optimization and must not be assumed here** — but
   nothing in §3 prevents it, because the entry label is the only way in.

**WHAT A SUBROUTINE CALL INTO A LOOKBEHIND ALTERNATIVE WOULD ADDITIONALLY
NEED, stated because it is the non-obvious half.** §3.4's branch structure is
`L_b1 … L_bm`, and each branch carries **its own compile-time width `k_i`**
used three times: the `scan_position < k_i` guard, the `$_back_step(..., k_i)`
argument, and the `RX_CHARGE_WORK(k_i)` literal. A call that targets a
lookbehind BRANCH therefore needs the width to travel with the call, and there
are only two honest ways:

- **(a) the width is a property of the CALL SITE**, i.e. each call site emits
  its own guard/back-step/charge and jumps to `L_body_i` (the branch's forward
  body, past the back-step). That keeps the sub-program width-free and is what
  §3.4's label layout already permits, because `L_body_i` is a distinct label
  from `L_b_i`.
- **(b) the width travels in a slot**, which turns three compile-time
  constants into runtime reads and costs the emitted code its `k` literals.

**RECOMMENDATION (a)**, and §3.4's labels are laid out for it: the back-step
and its guard sit in `L_b_i` and the body starts at `L_body_i`, so a call can
target either. This is recorded as a hand-off obligation rather than built —
[DD-14] rules it — and §12 P-13 is the prediction that the split is enough.

### 6.5 The `(?m)^` self-oracle, and both directions are already measured

The check [DD-11] and D66 need is §6.3's driver restricted to the multiline
family. Its shape:

- **Driver**: the §6.3 driver, run over
  `tests/assertions/multiline.rxt` + `d27/multiline.rxt` (89 + 16 blocks,
  3,325 + 28 cells; 69 + 12 qualifying).
- **Oracle**: **neither arm** — the two arms must agree with each other, which
  is what makes it usable before [DD-11] exists and after.
- **Subjects**: the corpus's own, plus the boundary set §6.1 measured on.

**Both directions measured, `out/d66_subset.txt` S2 and `out/expansions.txt`
E1/E4:**

- libpcre2 folded vs libpcre2 expanded: **0 disagreements**.
- pcrec's shipped `(?m)^` vs libpcre2: **0 disagreements over 24 cells**.
- pcrec folded vs libpcre2 expanded, over the whole expansion table: **0 over
  324 cells**.
- the `(?!\z)` conjunct's necessity: **4 of 36** cells — non-vacuous.

**AND THE FIRST VERSION OF THIS MEASUREMENT WAS WRONG IN THE INTERESTING
DIRECTION**, which is why it is stated twice in this document. It put `(?m)`
on the folded arm only, so a `$` tail meant `(?m)$` on one side and plain `$`
on the other, and it reported **3 disagreements** — which, published, would
have read as *"the D66 expansion is not equivalent to `(?m)^`"* and would have
killed the hand-off. Both numbers are in the archive.

### 6.6 What [DD-11] and [ENG-LOOK] each get, in one list

| consumer | what this module hands it | where |
|---|---|---|
| **[DD-14]** | a lookaround body that is already a self-contained sub-program with one entry and one exit; the width-at-the-call-site recommendation for lookbehind branches | §6.4 |
| **[DD-11]** | the verified expansion table; the substitution driver's design and its 8,495-cell population; the self-oracle's two-comparison shape | §6.1, §6.3 |
| **D66** | a one-character fixed lookbehind that lowers correctly (§3.4 at `m=1, k=1`); `PCREC_ENCE_BACK_STEP` so a UTF-8 backend never revisits the anchor optimizer | §3.4, §4 |
| **[ENG-LOOK]** | the prefilter-soundness statement and the measured match-START hazard; the component-automaton sizes and product bounds; the sub-program shape it will LIFT | §5.3-§5.6, §5.8, §6.4 |

---

## 7. The D27 goal-facts list (charter (vi))

For the [M6.6.3] blinded author, who is denied `src/` and `tests/` and writes
the corpus from PCRE2 semantics and this document's §2. **Every row is a
divergence between python3 `re` and libpcre2 10.46, MEASURED, with the one
probe line that shows it.** Rows the charter expected and that are NOT
divergences are listed too, because a goal-facts list that omits a refuted
expectation invites the author to write it in anyway.

### 7.1 REAL divergences — libpcre2 rules these cells; mark them `# pcre2-only`

| # | divergence | probe line |
|---|---|---|
| G1 | **A lookbehind whose branches have DIFFERENT fixed lengths is legal in PCRE2 and an ERROR in python.** | `(?<=a\|bc)x` — pcre2 ok, python "look-behind requires fixed-width pattern" |
| G2 | **Any variable-width lookbehind body is legal in PCRE2 up to `max_varlookbehind` and an error in python** — `(?<=(a\|bc))x`, `(?<=a{2,3})x`, `(?<=a?)x`, `(?<=(?:a\|bc)d)x`. **pcrec REFUSES these too** (§2.5), so a cell here is a `perr` cell for pcrec and an `ok` cell for PCRE2, and the author must not write a match expectation for it | `(?<=a{2,3})x` — pcre2 ok, python error, pcrec `perr` |
| G3 | **A backreference to a VARIABLE-width group inside a lookbehind is legal in PCRE2, error in python** — and pcrec refuses it (§2.5) | `(a\|bc)(?<=\1)x` — pcre2 ok (maxlb 2), python error |
| G4 | **The alpha spellings do not exist in python at all.** All twelve produce "nothing to repeat at position 1", because python reads `(*` as a quantified `(` | `(*pla:a)b` |
| G5 | **The non-atomic forms do not exist in python.** `(?*` and `(?<*` are "unknown extension" | `(?*a)b`, `(?<*a)b` |
| G6 | **`\K` does not exist in python**, so every `\K` cell in this module (all of which are pcre2 COMPILE ERRORS, err 199) is a compile error in python for a **different reason** — "bad escape \K". The author must not treat the agreement as agreement | `(?=a\K)x` |
| G7a | **THE ASSERTION-FAMILY EXPANSIONS ARE ALL PYTHON-COMPATIBLE, and this refutes the charter's own warning.** Every one of the nine (§6.1) compiles in python: `(?<=\w)`, `(?<!\w)`, `(?<=\n)` are fixed-width-1 lookbehinds, and `\Z`/`$`'s optional body sits in a lookAHEAD (`(?=\n?\z)`) where python has no width rule. **So the expanded corpus stays python-verifiable and `# pcre2-only` must NOT be put on it** | `(?=\n?\z)x` — python ok; `(?<=\n?\z)x` — python "look-behind requires fixed-width pattern". The DIRECTION is the whole difference |
| G7 | **`\A`/`\Z`/`\z` differ between the oracles** (inherited from `assertions_design.md`, not this module's, and it bites here because lookaround bodies contain them): python's `\Z` is PCRE2's `\z` | `(?<=a)b\Z` vs `(?<=a)b\z` |

### 7.2 NOT divergences — the charter expected these and they are refuted

| # | the expectation | what was measured |
|---|---|---|
| G8 | *"python lacks quantified lookaround"* | **FALSE.** python compiles all fourteen forms tried (`(?=a)*`, `(?=a)+`, `(?=a){2}`, `(?!a)?`, `(?=a)*+`, `(?=(a))*`, …) and **agrees with libpcre2 on all nine behavioural cells** (`out/spellings.txt` A4). `# pcre2-only` on a quantified-lookaround cell would throw away a working oracle — which is R32 C3's finding (two corpus files marked python-verifiable in the direction that LOSES the oracle), in the other direction |
| G9 | *"python's handling of captures in negative lookahead"* differs | **FALSE.** The two oracles agree on **all 27 capture cells** in `out/captures.txt` — C1 (positive, retained), C2 (negative, discarded), C3 (positive that fails after capturing, unset), C4 (under a quantifier). python is a usable oracle for the whole capture axis |
| G9a | *"python `re` cannot take several expansions"* (the 2026-08-23 charter addition) | **FALSE for every expansion in the family.** MEASURED, `out/expansions.txt` E3: all nine compile in python. The variable-width lookbehind python rejects — `(?<=\n?\z)` — appears in NO expansion, because `\Z`'s definition is a lookAHEAD. The warning is real about the CONSTRUCT and wrong about the SET |
| G10 | *"python's same-width lookbehind rule"* is one rule | **It is narrower than "same width".** python accepts `(?<=ab\|cd)x` (two branches, same length) and rejects `(?<=a\|bc)x`. So the divergence is about **differing** widths, not about alternation |

### 7.3 What the blinded author should be told about pcrec, and nothing more

- The construct table §2.1 (which spellings exist and what each one IS).
- The rule §2.5 (which lookbehind bodies pcrec compiles), stated as a promise,
  not as an implementation.
- That captures inside a positive lookaround are retained, inside a negative
  one are discarded, and are unset when a positive one fails (§2.4/§2.6's
  cells, stated as behaviour).
- That `\K` inside a lookaround is refused.
- That a lookbehind reads subject bytes before `startpos` (§3.8) — so the
  corpus should contain `ms`/`ns` cells, which is the axis a startpos-blind
  corpus would miss entirely.
- That the ASSERTION FAMILY has lookaround definitions (§6.1's table), because
  the author's corpus should contain the expansions as ordinary patterns — they
  are the most heavily-exercised real lookarounds this module will ever see and
  they are the [M6.6.3] author's cheapest source of non-invented cells.
- **Nothing about the cut, the seam entry, the slots, the prefilter, the
  substitution driver, or `[ENG-LOOK]`.** The driver is a TEST-side generator
  built from the same table; an author who knew about it would be writing the
  driver's corpus a second time instead of an independent one.

---

## 8. Registry visibility and D65's `built` column (charter (vii))

### 8.1 The six existing rows

MEASURED (P4): six rows, module `lookaround`, `VM_ONLY`, `RS_MODULE`,
`RD_MODULE`, `ROADMAP_PLANNED`, `QF_YES`, all reading **`unbuilt`**.

After [M6.6.2] **all six read `built`**, because D65's status is derived
per-construct at dump time by driving each row's own `syntax` through a
gate-forced-open doorway call — not declared. The four `(?` forms and the two
non-atomic ones all ship (§2.1). Each row needs a **wired `PORT_FN`** in the
`aport` slot, exactly as `(?>...)` and `(?P=n)` have:

```c
{RK_GROUP, '=', NULL, "(?=...)", M_lookaround, FLAV_PCRE2, VM_ONLY,
 RS_MODULE, RD_MODULE, NULL, NULL, 0,
 "positive lookahead",
 ROADMAP_PLANNED, QF_YES, NULL, 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_laport_group}, NO_PORT},
```

with `ExtResult pcrec_laport_group(Ctx *, const RegRow *, ExtWant, size_t,
size_t)` in a new `src/parse/mod_lookaround.c`, dispatching on the row's
selector and tail. **One port function for all six rows**, because the six
constructs differ only in the three `A_LOOK` fields the port sets — and a
second port function would be a second place the `(?<*` / `(?<!` tail split
is decided.

### 8.2 The `(*` DOORWAY DEFECT — twelve spellings answering the wrong module

**MEASURED (P3), and it is a D26 tier-2 defect this module owns.** All twelve
lookaround alpha spellings answer *"`(*...)` requires module **'verbs'**"*.
The names are already in the VERB NAME table (`mod_verbs.c:178-189`, with
`ROADMAP_NONE`), but the `(*` DOORWAY is a single `FIXED(RK_VERB,
REG_SEL_ANY, "(*ACCEPT)", verbs, ...)` row (`registry.c:831`) whose module
answers for every name.

This is **the same defect one doorway over** from the one `registry.c:692`
already records for `(?*...)`: *"only this table did not, so the `(?`
catch-all answered 'requires module modifiers' for it — the wrong module,
which is the one fact the diagnostic exists to carry."*

**RECOMMENDATION: the VERB NAME table gains an optional module/feature pair,
defaulting to the doorway row's.** Twelve names take `M_lookaround`;
everything else inherits `verbs` and no other row changes. Reasons:

- The name→construct mapping **already lives there** — D25/Q1 deliberately
  split names out of the row, and the module is a property of the name, not of
  the doorway.
- The alternative (twelve tail-keyed `RK_VERB` rows) puts twelve names in a
  table whose header says names live elsewhere, and would need a tail-matching
  mechanism `RK_VERB` does not have.

**AND THEY NEED WITNESSES, which is where the count comes from.** R32/C1's
precedent is explicit: *"the SR-8 generic capability check WILL catch rows
lacking witnesses — the backrefs precedent found twelve."* Whether each alpha
name gets its own DUMP ROW is a second question and this design recommends
**yes for the six short names** (`pla nla plb nlb napla naplb`), because those
are the spellings a user writes and `--list-syntax`/the compliance index
otherwise say module `lookaround` ships six constructs while twelve more
spellings of the same six exist and are invisible. The six long forms are
aliases of the short ones and are covered by the same name-table module,
without rows. **§14 ASK 3 puts the row/no-row half to Frank**, because it is a
surface-inventory question rather than a correctness one.

### 8.3 What the D65 `built` column will read, and the tally is a deliverable

R32 C5 found *"the built column gains this module's rows for free"* asserted
by nothing. So: **[M6.6.2] delivers the before/after tally as a measured
number**, from `--list-syntax` on the merge, not as a prediction here. What
this design does commit to is the SHAPE: six rows move `unbuilt → built`; zero
rows move in the other direction; the `(*` doorway row itself stays
`verbs`/`unbuilt` (it is `(*ACCEPT)`'s row and this module does not build
verbs); and any alpha row added by §8.2 is born `built`.

---

## 9. The identity gate and the sabotage rows (charter (viii))

### 9.1 The gate

Modelled on `tests/codegen/run_backref_identity.sh`, whose shape this design
adopts rather than reinvents.

**THREE AXES**: `default`, `--engine=vm`, and **`-fno-prefilter`** — the
module's OWN axis, replacing backrefs' `--no-captures`. It is the right third
axis because §5.6's ruling changes exactly one thing about a lookaround-free
artifact: nothing. Under `-fno-prefilter` the ceiling is `subject-end` on
every artifact, so **if the `v.mrl_win` predicate is edited wrongly the
default axis moves and this axis does not**, which is the pair that localises
the failure.

**THE REFERENCE** is a `git archive` of `src lib cli` at a pinned pre-module
SHA — the [M6.5] close — asserted to contain **no `A_LOOK` anywhere in
`src/`**, built with `gcc -O0 -std=gnu11 -Wall -Wextra`. Not a `-D` knob: a
knob-gated comparison is blind under a sabotage, because lookaround-free
patterns exercise no gated path at all (`run_backref_identity.sh` measured
that blindness at 1175/1175).

**BYTE-IDENTICAL** is defined over the stdout of
`pcrec --features all -p rx <axis> -o - -- '<pattern>'` past exactly the three
D37 feature-stamp lines, with the strip itself asserted to have removed
exactly three (a `STAMP FILTER` failure otherwise). The stamp is expected to
differ because `render_modules` reorders.

**THE POPULATION** is every `pattern` line from every `.rxt` under `tests/`,
split lookaround-bearing vs lookaround-free by a grammar-aware classifier that
**fails safe toward the lookaround bucket**.

### 9.2 The positive control, which is the half that can actually fail

**"No lookaround exists today, so this module changes nothing for the existing
population" is TRIVIALLY TRUE and therefore worth nothing.** The gate needs a
control that can go red.

**THE CONTROL IS THE ORDINARY ONE**, inherited from
`run_backref_identity.sh`: the pre-module reference must **REFUSE every
lookaround-bearing pattern** (`ctl_bad == 0 && ctl_ok == nb`), which proves
the reference really is a different compiler and not a rebuild of the same
tree compared against itself. Floors: **≥ 700 lookaround-free patterns,
≥ 60 lookaround-bearing.**

**AN EARLIER REVISION PROPOSED A SECOND, EQUIVALENCE-BASED CONTROL and it is
WITHDRAWN.** It rested on the one-character FOLD — a lookaround whose body is
a single class rewritten into the assertions module's context-assertion node —
so that `\bfoo` and `(?<!\w)(?=\w)foo` could be compared. **Frank ruled the
fold out entirely** (§5.7): it is a duplicate code path, and the general form
is `[ENG-LOOK]`'s product construction. With no fold there is no artifact
relationship to assert, and a control built on a mechanism that does not exist
is worse than no second control — it would have gone green by construction.

**WHAT SURVIVES THE WITHDRAWAL, and it belongs to §6 rather than §9**: the
measured equivalences themselves. `\b`, `\B`, `(?m)^`, `(?m)$` against their
lookaround decompositions are **0 disagreements over 80 cells each**
(`out/d66_subset.txt` S1), and the whole expansion table is **0 over 972**
(`out/expansions.txt` E1). Those numbers are not an identity control; they are
the correctness statement of §6.3's SUBSTITUTION DRIVER, whose `A == B` arm is
a far stronger check of the same territory over **8,495 cells** rather than 80
— and one that runs on the shipped compiler instead of comparing two
compilers. **§6.3 is therefore where this module's real cross-lowering
assurance lives**, and §9 is the ordinary byte-identity gate it always was.

**THE BASELINE THIS RECORDS FOR LATER.** MEASURED, `out/d66_subset.txt` S1b:
today `\bfoo` compiles to a 21,287-byte artifact and `foo` to 18,792, and
`(?<!\w)(?=\w)foo` refuses with the D65 enabled-but-unbuilt diagnostic. After
[M6.6.2] the second will compile and will **NOT** be byte-identical to the
first: `\b` is `A_WORDB` and DFA-carryable, `A_LOOK` is `VM_ONLY`, so the two
differ in engine, in `RX_ENGINE_WHY`, in slot count and in size. **That
difference is the expected outcome, not a defect** — and the day `[ENG-LOOK]`
lands and deletes the special machinery, byte identity between them becomes
that row's own identity gate rather than this one's.

### 9.3 The sabotage rows

One row per claim, in `tests/mech/sabotages/`, following S105's shape (`SAB_ID
SAB_FILE SAB_SUITES SAB_DESC SAB_BEFORE SAB_AFTER SAB_COUNT`), anchors copied
from `git show HEAD:<path>` because the matrix builds from `git archive HEAD`.
Numbering starts at the highest existing id + 1 (to be taken at [M6.6.2], not
guessed here). D69 makes a module CLOSE a **full-matrix** run.

| id | the CLAIM it defends | file | the sabotage | prediction |
|---|---|---|---|---|
| **S-LA1** | §3.2: the positive lookahead CUTS | `src/gen/emit_vm.c` | delete the `vm_cut` call from `vm_look`'s atomic arm | the atomicity discriminator cells go red (`(?=(a\|ab))\1$` starts matching); every non-alternating cell stays green — which is what makes it a row |
| **S-LA2** | §3.2: the cursor is RESTORED after a positive lookaround | `src/gen/emit_vm.c` | drop the `scan_position = slot_values[POS]` line | every lookahead becomes width-consuming; the whole corpus goes red — a coarse row, kept because its absence would be worse |
| **S-LA3** | §3.3: the negative form CUTS on body success | `src/gen/emit_vm.c` | replace `RX_CUT(MARK); goto rx_fail` with `goto rx_fail` | the negative corpus goes red **while the positive cells stay green**; the failing assertion leaves a live choice point that later succeeds |
| **S-LA4** | §3.3: the negative form's frame is pushed BEFORE the body | `src/gen/emit_vm.c` | move the `RX_PUSH` after the first body emission | captures written by a failing negative body survive — `(?!(a)x)ab` reports g1=(0,1) where PCRE2 says unset |
| **S-LA5** | §5.2: SR-8's `VM_ONLY` stamp is what stops the DFA compiling an erased lookaround | `src/parse/registry.c` | flip one lookaround row's `engines` to `ANY_ENGINE` | the corpus goes red loudly (`(?=a)b` on `"b"` answers (0,1)) — **unlike backrefs' `next_pos` hazard, this one is detectable, and the row proves it** |
| **S-LA6** | §4.4: the back-step routes through the SEAM, not inline arithmetic | `src/gen/emit_vm.c` | replace the `$_back_step(...)` call with `scan_position - k` | **NO ANSWER CHANGES** under the byte backend. The fixture-declared per-site count in `run_codegen_tests.sh` is the ONLY detector — S109's shape exactly |
| **S-LA7** | §4.2(3): the seam's sentinel is checked at the call site | `src/gen/emit_vm.c` | drop the `$_BACK_STEP_NONE` comparison, keeping the `scan_position < k` guard | **no answer changes today** (the guard is exact under the byte backend); the codegen check for the sentinel comparison is the detector. A row that exists FOR THE BACKEND THAT DOES NOT EXIST YET, and says so |
| **S-LA8** | §3.8: a lookbehind reads bytes BEFORE `startpos` | `src/gen/emit_vm.c` | clamp the back-step guard to `scan_position - startpos < k` | the corpus's `ms`-startpos cells go red; every startpos-0 cell stays green |
| **S-LA9** | §2.6: `vm_nullable` answers TRUE for `A_LOOK` | `src/gen/emit_vm.c` | return `false` from the `A_LOOK` arm | `(?:(?=a))*b` loses its empty-iteration guard and the matcher **HANGS**. The row's suite assignment must therefore be one with a per-case timeout (D45), and the row says so |
| **S-LA10** | §2.7: `\K` inside a lookaround is refused | `src/parse/mod_lookaround.c` | delete the `A_KRESET`-in-body check | `(?=a\K)b` compiles and silently reports a different match start; the reject-table cell goes red |
| **S-LA11** | §2.5: the width rule is per-BRANCH and the branches are TOP-LEVEL | `src/parse/mod_lookaround.c` | accept a branch whose `minw != maxw` | `(?<=(a\|bc))x` compiles and answers with the WRONG alternative's captures on the `bac`-shaped cells (§2.4 level 2) |
| **S-LA12** | §5.6: the `v.mrl_win` predicate excludes lookaround | `src/gen/emit_vm.c` | drop `&& !pcrec_has_lookaround(root)` | the 16 qualifying shapes from `out/d66_subset.txt` S3 lose their matches. **This row needs the corpus to CONTAIN one of those shapes**, which §10 makes a population requirement rather than a hope |
| **S-LA13** | §5.6(3): the predicate is read at ALL THREE sites | `src/gen/emit_vm.c` (**two sites**) | flip the STAMP's source while leaving the two ceiling-building sites live | the stamp says `subject-end` while the ceiling is live — **detectable only by codegen rule 1's both-sources assertion**, which is R31 E3's finding as a row |
| **S-LA14** | §3.1(b)/D62 control 3: `.look_neg` is READ | `src/gen/emit_vm.c` | ignore `.look_neg` in `vm_look` (always emit the positive shape) | every negative cell goes red. Three rows, one per field — `.look_behind` and `.look_atomic` get **S-LA15** and **S-LA16** on the same principle |

**Two of these need the TWO-SITE mechanism** (`tests/mech/CLAUDE.md`'s S108,
`SAB_FILE2/BEFORE2/AFTER2/COUNT2` through the same `replace.py`): **S-LA6**,
because the emitter change and the enc-mask OR must move together or the
artifact declares an entry it never calls and the check fires for the wrong
reason; and **S-LA13**, which is two sites by construction.

**ANCHOR DRIFT is an ANOMALY, not a failure**, and `replace.py` refuses to run
when the anchor is not found exactly `SAB_COUNT` times. Every row above must
have its anchor re-derived at [M6.6.2] against the code as landed, never
against this document's sketch — the seven drifted anchors tranche A had to
re-home are the precedent.

---

## 10. The population and the acceptance run (charter (ix))

### 10.1 The construct population for the blinded corpus

Counting **spellings × contexts**, which is what the [M6.6.3] author sizes
against:

| axis | count | what it is |
|---|---|---|
| spellings | **18** | 4 `(?` forms + 2 non-atomic `(?` forms + 6 short alpha + 6 long alpha (§2.1) |
| distinct CONSTRUCTS behind them | **6** | pos/neg × ahead/behind, plus non-atomic pos ahead/behind |
| body shapes per construct | **9** | empty; a literal; a class; a fixed multi-character; same-length alternatives; different-length alternatives (lookbehind only); a capture; a nested lookaround; a backreference |
| contexts | **7** | pattern start; pattern end; mid-pattern; inside an alternation branch; under `*`, `+`, `{n,m}`; inside a capture; inside an atomic group |
| refusal cells | **8** | unbounded body; bounded-variable body; single-branch variable body; backref to a variable group; `\K` in each of the four polarities |
| oracle axis | **2** | python-verifiable vs `# pcre2-only` (§7) |

**Corpus size: ≈ 6 × 9 × 7 ≈ 380 behavioural cells plus ≈ 40 refusal cells**,
before subjects. At 4-6 subjects per block that is **1,500-2,300 match
expectations** — the same order as `tests/backrefs/` and `tests/atomic_groups/`.

**THREE POPULATION REQUIREMENTS THAT ARE NOT SIZE**, each because a sabotage
row above is otherwise unfalsifiable:

1. **The corpus MUST contain at least one of §5.5's 16 qualifying shapes** —
   a lookaround inside an alternation with a bounded-repeat, mandatory-tail
   follow — or **S-LA12 cannot go red** and §5.6's ruling has no test.
   `((?:a(?!q)|aq)(?:xy){0,4}q)` on `"aqq"` is the measured witness and
   belongs in `tests/lookaround/prefilter.rxt` by name.
2. **The corpus MUST contain `ms`/`ns` startpos cells over a lookbehind**, or
   **S-LA8** cannot go red and §3.8's contract claim is untested.
3. **The corpus MUST contain an EMPTY capture inside a lookaround and a
   re-entered group across one**, because those are where the trail discipline
   §3.2(3) and §3.3 rely on is discriminating rather than incidental — S105's
   own lesson one construct over.

### 10.1a THE SECOND POPULATION: the expanded assertions corpus

§10.1's ~380 blocks are the module's OWN corpus, written by the [M6.6.3]
blinded author. **§6.3's substitution driver contributes a second population
an order of magnitude larger and costs nothing to author**: 638 generated
patterns over **8,495 libpcre2-verified behavioural cells**, every expectation
inherited from a module that already ships.

The two populations are complementary rather than redundant, and the
difference is worth stating because a reader could take the larger one as a
reason to shrink the smaller:

| | the module corpus (§10.1) | the expanded corpus (§6.3) |
|---|---|---|
| authored by | a D27-blinded author, from §2 and §7 | nobody — generated from a shipped corpus |
| covers | every SPELLING, every body shape, the refusals, the alpha forms, `ms` startpos, the prefilter witness | **one body shape**: the assertion family's, which is one class or one literal |
| its oracle | python where §7 allows, libpcre2 otherwise | the two-comparison self-oracle, plus libpcre2 |
| what it would MISS alone | — | every construct §2 ships that no expansion uses: variable bodies, captures inside a lookaround, the non-atomic forms, quantified lookaround, nesting, the alpha spellings |

**So the expanded corpus is a DEPTH instrument on one shape and the module
corpus is a BREADTH instrument**, and §11's landing bar asks for both.

### 10.2 `tests/lookaround/` — the files

| file | what it holds | oracle |
|---|---|---|
| `lookahead.rxt` | `(?=` and `(?!`: bodies, contexts, degenerate forms | python-verifiable |
| `lookbehind.rxt` | `(?<=` and `(?<!`: fixed bodies, same-length alternatives | python-verifiable |
| `lookbehind_widths.rxt` | **different-length branches** — G1's cells | **`# pcre2-only`** |
| `nonatomic.rxt` | `(?*` `(?<*` and their `(*napla:`/`(*naplb:` spellings | **`# pcre2-only`** (G5) |
| `alpha_spellings.rxt` | all twelve alpha spellings, one cell each proving the construct | **`# pcre2-only`** (G4) |
| `captures.rxt` | the four polarity/outcome combinations, with `g` lines | python-verifiable (G9) |
| `quantified.rxt` | `(?=a)*` and family, including the empty-iteration cells | python-verifiable (G8) |
| `nesting.rxt` | lookaround in lookaround, backref in lookaround, atomic in lookaround | mixed; per-block |
| `startpos.rxt` | `ms`/`ns` cells over a lookbehind | python-verifiable |
| `prefilter.rxt` | §10.1(1)'s qualifying shapes | python-verifiable |
| `refused.rxt` | the `perr` cells: variable bodies, `\K`, backref-to-variable | n/a (`perr`) |
| `gated.rxt` | the enabled-but-unbuilt and module-disabled diagnostics | n/a |

Plus `tests/lookaround/run_lookaround_diff.sh` and `la_oracle.py`, modelled on
`run_backref_diff.sh` / `bref_oracle.py`, for the `# pcre2-only` blocks the
`re`-based harness cannot verify — and
`tests/lookaround/run_expansion_diff.sh`, §6.3's substitution driver, which is
also [DD-11]'s regression harness.

### 10.3 The acceptance run

The [M6.6.3] shape, from the backrefs precedent: the blinded author's corpus
is written in a D27 CELL against §2 and §7 only, then run against the merge
**without the author's involvement**, and every failure is triaged into
*corpus wrong* / *pcrec wrong* before anything is edited. The acceptance
number is reported as **cells / failures / triage outcomes**, not as a pass.

---

## 11. The implementation brief (charter — what [M6.6.2] builds)

In order, each wave landable and testable on its own.

**WAVE A — the width analysis, alone.** `pcrec_maxw` in `src/opt/mrl.c` beside
`pcrec_minw`, with that file's `default:`-less exhaustive switch and
`PCREC_W_UNBOUNDED`. **No lookaround anywhere.** It is testable on its own
against `pcrec_minw` on the whole corpus (`maxw >= minw` for every node of
every pattern in `tests/`), and landing it first means the analysis §2.5 rests
on has a green suite behind it before any construct depends on it.
*Landing bar: `make test` green; a `maxw >= minw` sweep over the corpus; the
`-Wswitch` alarm demonstrated (add a dummy enumerator, count, revert).*

**WAVE B — the parse hook and the refusals.** `src/parse/mod_lookaround.c`,
`pcrec_laport_group`, the six registry rows wired, the `A_LOOK` node kind with
its three fields and its widths, §2.5's per-branch check, §2.7's `\K` check.
**No emitter arm yet** — every accepted pattern hits the emitter's
`ctx_fail`. *Landing bar: `tests/lookaround/refused.rxt` and `gated.rxt`
green; the reject table green; `--list-syntax` shows six rows still `unbuilt`;
the identity gate green on all three axes (nothing compiles differently yet,
so this is the wave where byte-identity is cheapest to establish).*

**WAVE C — the LOOKAHEAD lowering.** `vm_look`'s positive, negative and
non-atomic arms; `vm_nullable`'s `A_LOOK` arm; the two slot families; `mrl.c`
and `maxw`'s `A_LOOK` arms; `nfa.c`'s epsilon arm; SR-8 already stamps.
*Landing bar: `lookahead.rxt`, `captures.rxt`, `quantified.rxt`,
`nonatomic.rxt` green; the four lookahead rows read `built`; S-LA1..S-LA5,
S-LA9, S-LA14..S-LA16 all DETECTED.*

**WAVE D — the SEAM ENTRY and the LOOKBEHIND.** `PCREC_ENCE_BACK_STEP`, the
`enc_byte.c` row, the `A_LOOK` arm's mask OR, §3.4's emitted shape, the
codegen fixture rows and **the second exact-count guard with its literal N
written into the check**. *Landing bar: `lookbehind.rxt`,
`lookbehind_widths.rxt`, `startpos.rxt` green; all six rows `built`; the
[M5-SEAM] check green with the new fixtures and its guard's N stated in the
commit message; S-LA6..S-LA8, S-LA11 DETECTED.*

**WAVE E — the PREFILTER predicate.** §5.6's one predicate at **three** sites,
codegen rule 1 extended to assert on both sources for lookaround as it does
for atomic. *Landing bar: `prefilter.rxt` green — including the measured
witness `((?:a(?!q)|aq)(?:xy){0,4}q)` on `"aqq"`; S-LA12 and S-LA13 DETECTED;
the identity gate green on all three axes including `-fno-prefilter`.*

**WAVE E2 — THE SUBSTITUTION DRIVER (§6.3).** `tests/lookaround/
run_expansion_diff.sh`: the literal expansion table (transcribed from D66 /
[DD-11], NOT derived from the compiler), the five qualification rules, the
`(?:...)` bracketing, both substitution policies, and the two-comparison check.
Landable the moment Wave D closes, because the expansions need lookbehind.
*Landing bar: the driver green over its measured population — **270 blocks /
8,495 cells**, P1 and P2 — with the per-rule disqualification counts printed
and asserted against §6.3's numbers, so a driver that silently stopped
substituting shows up as a population change rather than as a pass. A
`--policy=none` control arm (substitute nothing) must report 8,495 trivially
equal cells, or `A == B` is not comparing two lowerings at all.*

**WAVE F — the alpha spellings.** §8.2's name-table module field, the twelve
names, the six proposed rows if Frank rules for them (§14 ASK 3).
*Landing bar: `alpha_spellings.rxt` green; all twelve refuse-or-compile with
module `lookaround`; the SR-8 capability check green with witnesses for every
new row; the compliance page refreshed via the `compliance-refresh` skill.*

**THE CLOSE ([M6.6.4])** is D69-tier: a module close is the **FULL** 118-row
matrix, plus the battery, the gate, the compliance refresh and the archive.

---

## 12. What would refute this — predictions for the panel

Each is a claim this design would rather have attacked than believed.

**P-1 (the seam).** *The [M6.5.2] entries-table refactor needs ZERO interface
change to carry this module's entry.* Refute by finding a field, signature or
caller in `src/gen/enc/` that §4's entry forces to move. `enc.h` predicted
this construct by name, so a change here would refute the refactor's own
stated justification as well as this section.

**P-2 (the negative form).** *The negative lookaround needs no capture
snapshot, because the fail label already restores the cursor and rewinds the
trail (P7).* Refute by exhibiting a subject on which a negative lookaround's
body writes a capture that survives, with the shape of §3.3 emitted. The
sharpest attack is a capture written by a body that succeeds **partially**
across a re-entered outer group — R32 E1's territory, one construct over.

**P-3 (the subset asymmetry).** *`(?<=a|bc)x` ships and `(?<=(a|bc))x` does
not, and the difference is §2.4's two preference orders rather than an
accident.* Refute by showing the two forms are the same shape to PCRE2 — e.g.
by finding a subject on which `(?<=a|bc)x` picks the LONGER branch, which
would collapse the level-1/level-2 distinction the ruling rests on.

**P-4 (`pcrec_maxw`).** *A branch with `minw == maxw == k` consumes exactly
`k` bytes on every successful path, so §3.4's end-check cannot fire.* Refute
by exhibiting a node kind for which `minw == maxw` and the consumed width
varies — `A_BREF` is the obvious candidate and is why §2.5 refuses it; the
attack is to find a second one. **A green end-check over the whole corpus is
NOT evidence for this**, because the check is what would catch it.

**P-5 (the positive control).** *A one-character lookaround and its `\b`-half
equivalent produce the same ANSWERS and NOT the same artifact.* Refute either
way: by finding a subject where the answers differ (which would kill §5.7's
door and §6's hand-off), or by finding that the artifacts ARE byte-identical
(which would mean the `VM_ONLY` stamp is not doing what §5.1 says).

**P-6 (the D66 expansion).** *`(?m)^ == \A|(?<=\n)(?!\z)` at 0 disagreements
over 36 cells.* This lane's first measurement of it said **3** and was wrong
because it put `(?m)` on one arm. Refute by finding a subject class the 12
used do not cover — `\r\n`-only input, a subject ending in `\n\n`, and a
subject with no `\n` at all are in the set; a subject containing `\0` is not.

**P-7 (H1/H2).** *Erasing a lookaround never makes the prefilter reject a real
match (H1) and never puts the candidate start too late (H2), 0 violations over
45 cells.* The attack that would work is the one that worked on backrefs (R32
E2): find a structural reason the erasure is not a superset. For a lookaround
the proof is one line (§5.3) — so refuting it means finding a construct
INSIDE a lookaround body that makes the erasure non-monotone. `\K` is refused;
`(*ACCEPT)`-family verbs are not in this module and would be the place to look
if they ever are.

**P-8 (startpos).** *A lookbehind reading before `startpos` is free for the
VM.* Refute by finding a path where the VM's `subject`/`scan_position` are not
absolute — the hybrid's prefilter window is the candidate, and §5's ruling
touches the ceiling but not the start seed. `assertions_design.md` §3.8.3.1's
reverse-pass finding is the precedent for how this kind of thing hides.

**P-9 (the node-kind call).** *One `A_LOOK` kind with three fields is right
because all three are read at ONE site.* Refute by finding a second reader —
`revdet.c`, `possessify.c`, `altcls.c` and `atomic.c` are the four places
`atomic_groups_design.md` §6.5 found one, and `revdet.c`'s clearing of
`Ast.possessive` on a reversed copy is the exact shape to look for.

**P-11 (the ENG-LOOK sizing).** *Every assertion-family and enumerable-real
lookaround body has a component automaton of 2-25 states, so the product bound
clears the 32,000 cap on all 64 non-control rows.* Refute by exhibiting a
realistic lookaround body whose component is large — a long alternation of
literals (a keyword set) is the obvious candidate and is NOT in the population,
which §5.8 should be attacked for. The controls show the failure mode is real
(18 of 62 over cap), so the gap is in the population, not the method.

**P-12 (the subset is exactly big enough).** *Every one of the nine
[DD-11]/D66 expansions compiles under §2.5's rule — none needs variable-length
lookbehind, a backreference in a lookbehind, or `\K` in a lookaround.* This
is a COINCIDENCE the design leans on and it is checkable: refute by finding a
member of the assertion family whose lookaround definition needs a
variable-width LOOKBEHIND. `\Z`'s `(?=\n?\z)` is the near miss — the same
body one direction over would be refused — so the attack is to find a
definition where the optional sits behind rather than ahead.

**P-13 (the DD-14 hand-off).** *§3.4's label layout is enough for a subroutine
call to target a lookbehind branch's forward body, with the width staying a
property of the CALL SITE (§6.4(a)).* Refute by finding state the branch body
reads that the call site cannot supply — `SLOT_LOOK_POS<n>`, which the
end-check compares against, is the candidate: it is set at `L_entry`, which a
call targeting `L_body_i` would skip.

**P-10 (the budget).** *A lookaround body's work is counted by the existing
single decrement, and this module adds only the cut charge and the back-step
literal.* Refute by finding a shape where the assertion's cost is not visible
to `steps_left` — a frameless scan inside a lookbehind branch is the
candidate, since [ENG-BREP counter-K] settlement 4 exists precisely because
frameless work was invisible once before.

---

## 13. Explicitly out of scope

- **Variable-length lookbehind** (§2.5). Refused, chartered, the loop shape
  written down.
- **A backreference inside a lookbehind** (§2.5). Refused conservatively even
  where the referenced group is fixed-width; the refinement is chartered.
- **`PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK`** (§2.7). The bit is measured and named;
  adopting an extra-option is D38's survey territory.
- **The one-character FOLD.** RULED OUT by Frank (§5.7) — a duplicate code
  path. Nothing in this design recognizes a lookaround in order to rewrite it
  into an assertion node.
- **Lookaround in the DFA at all.** `[ENG-LOOK]`'s product construction, its
  own row with its own design gate. This module hands it §5.3-§5.6, §5.8 and
  §6.4 and prejudges nothing else.
- **Any PRODUCT-side substitution of assertions by their definitions** (§6.4).
  RULED: it is built on [DD-14]'s subroutine-call primitive, after lookaround
  lands. This design proposes no parse-time or IR-time desugar mechanism.
- **The substitution driver's IMPLEMENTATION** — designed in §6.3, built in
  [M6.6.2] wave E2.
- **`(*ACCEPT)`-family verbs inside a lookaround.** Module `verbs` has no
  producer; nothing here anticipates one.
- **A DFA lowering of lookaround as a cut construction.** The `[ENG-CUT]`
  chartered row would be its home; a lookaround is not a cut over the same
  alphabet and would need its own.
- **The `--engine=dfa` advice defect** (§5.1). Pre-existing, reproduced, not
  fixed here; do not repeat it.

---

## 14. ASKs for Frank

**ASK 1 — ONE node kind with three fields, or four kinds?** §3.1(a)
recommends one, on the ground that all three fields are read at a single site
and that four kinds would let three be silently handled by a `case` written
for the first. The counter-argument is that `look_behind` changes control flow
more than D62's motivating flag did. *Recommendation: one kind, with §9's
three per-field sabotage rows as the control D62 requires.*

**ASK 2 — the end-check: emit, or assert-and-elide?** §3.4 shows it is
provably redundant for the shipped subset and emits it anyway as the width
analysis's only runtime evidence. The alternative is an `assert()`-shaped
abort under a debug build and nothing under `-DNDEBUG`. *Recommendation: emit
it, because it is one comparison per branch and it becomes load-bearing the
day variable-length lands.*

**ASK 3 — do the six short alpha spellings get their own DUMP ROWS?** §8.2's
module-attribution fix is a correctness matter and is not in question. Whether
`(*pla:` and its five siblings each get a `--list-syntax` row is a
surface-inventory question. *Recommendation: yes — otherwise the compliance
index says the module ships six constructs while twelve more spellings of the
same six are invisible, and SR-8's capability check will want witnesses
either way.*

**ASK 3a — does the substitution driver land in [M6.6.2] or [DD-11]?** §6.3
designs it and §11 puts it in wave E2, on the ground that it is this module's
cheapest and largest correctness instrument and that [DD-11] then inherits a
harness rather than writing one. The alternative is to design it here and let
[DD-11] build it. *Recommendation: build it in [M6.6.2]. A generator whose
population is 8,495 already-verified cells is worth more to the module that
introduces the construct than to the row that later rewrites the other side of
it — and if it lands later, [M6.6.2] ships with only the ~380-cell corpus a
blinded author could write.*

**ASK 4 — is `-fno-prefilter` the right third identity axis?** §9.1 replaces
backrefs' `--no-captures` with it because §5.6's ruling is the only thing this
module changes about a lookaround-free artifact. *Recommendation: yes, and add
`--no-captures` as a fourth if the run is cheap — the gate is a compile-only
sweep.*

# Module `assertions` — design

**[M6.1]**, the design gate in front of [M6.2]. Covers `\b` `\B`, `\A` `\z`
`\Z`, `(?m)` multiline `^`/`$`, `\G`, `\K`.

**STATUS: PROPOSED, REVISED AFTER R30.** No `src/` change belongs to this
lane. Nothing here is built.

---

## PANEL OUTCOME — R30 (2026-08-18)

`../dev/reviews/2026-08-18-r30-assertions-design.md`, three read-only critics
against commit 4f0dafe. **Read this block before any section.**

**BUILD ANNOTATIONS EXIST BELOW THIS BLOCK** ([M6.2] waves A–C, 2026-08-19):
§3.2 (the NOTBOL/NOTEOL erasure the alias is silent on), §3.5.1 (the 38,009
forecast refuted as an observation), §3.6.1 (the skip-union sentence refuted;
wave B ships DECLINE — and wave C's per-mechanism postures, measured), §3.7
(the class axis is THREE-VALUED, not a second bool), §3.7.2 (D63's candidate
set is the LIVE-SEED set, which is strictly more general than "the newline
set" and is what makes `(?m)^a|b` correct), §7.2 (the seam question contested
and settled the design's way), §8.3 (the four `default:` sites inspected;
none needs the flag, and the reason generalizes). A reader who stops at this
block misses all of them.

**What survived**, on the panel's own independent instruments rather than
re-runs of this lane's: the D47.5 scope-blind miscompile (§8, "the single
best-supported claim in the document", both cell tables reproduced by two
critics); the `\A`/`\Z` exact-alias claim (§3.2, a 1,008-cell differential at
zero disagreements); `\G`'s semantics and mechanism (§4); the `\Z` python-oracle
divergence (§3.2.1); the `mods` blast radius (§8.4); all six committed probes;
and the `mrl.c` house-rule footing for §8.3.

**What did not.** The ENGINE-SPLIT half took two HIGH refutations and six
mediums, and the corrections are substantial enough that a reader of the first
draft should not trust their memory of these sections:

| finding | what was wrong | where it is now |
|---|---|---|
| **E1 (HIGH)** | §0.2's spine claimed "exactly three" mechanisms and had **no mechanism at all** for assertion context at `startpos > 0`, forward or reverse | §0.2, §2's fourth row, **§3.8** (new), Wave B |
| **E2 (HIGH)** | "`(?m)^` inherits D8's shape and nothing else changes" — false twice; it is a permanent move into an **O(n²)** class, now measured | §3.7, Q3 |
| E3 | `\z`'s byte-identity argument canonicalized against the wrong reference | §3.3 |
| E4 | §3.4 and §3.5 were never composed; composed, the state cap is **exceeded** | §3.5.1 (new) |
| E5 | the skip hazard was attributed to `\b`, which cannot suffer it; Wave B's sabotage could not fire | §3.6.1, Wave B/C |
| E6 | the zero-cost accept measurement is scoped to ENG_UNANCH and has no `pos == n` column | §3.6, §3.6.2 (new) |
| E7 | "\K is structurally impossible on a DFA" overstated a true conclusion | §6.1 |
| E8 | §9.3's match-here paragraph was **factually wrong**; Wave D's differential had nothing to find; `\K` breaks the match-here filter | §6.3, §9.3, Waves D/E |
| M2 | the state prototype has a **second** fidelity gap, in the opposite direction | §3.5 |
| M5 | Q1's "semantic namespace" exemption is unsound against D18's own precedent | §11 Q1 |
| M6 | the corpus harvest reproduced a NAMED project defect (locale `sort -u`) | §3.4, `probes/harvest_rxt_patterns.sh` |
| M7 | one provenance header was **hand-written to imitate** the archiver | §0.3 |
| M8 | the `-Wswitch` experiment was unverifiable | `probes/probe_wswitch_alarm.sh` |

**THE FOCUSED RE-CHECK (both critics resumed against the revision).** Seven of
eight engine discharges held on substance and five of six measurement ones;
what did not is recorded here rather than only in the review, because one of
them is a second defect in this design:

| finding | what the re-check found | where it is now |
|---|---|---|
| **N1 (MEDIUM-HIGH)** | §3.8 filled mechanism 4 at three of the **four** places it is needed. The missing one is the REVERSE machine's TERMINATION boundary: at `pp == startpos` the loop breaks (`emit_dfa.c:1056`) before `s[startpos-1]` is read, so a **leading `\B`** evaluates blind — and on this document's own §3.8.1 cell the forward pass finds the match and the reverse pass **throws it away**. `\b` is safe by accident, which is why a trailing-only sweep cannot see it. | **§3.8.3.1** (new), §12 item 6, Wave B |
| M5 (PARTIAL) | the Q1 withdrawal was applied at §11 but **§5.2 still carried the withdrawn recommendation verbatim** — a live contradiction at the section a skimmer stops at | §5.2, rewritten |
| N2 | §3.7.1's inline table came from a different run than the archive it cited (M7's class again, in miniature) | §3.7.1, re-pasted from the archive |
| N3 | the `memchr('\n')` mitigation was justified on the quadratic arm; its real benefit is the **linear non-crossing** case | §3.7.2, new probe arm, Q3(b) |
| N4–N8 | "three mechanisms" over a four-row table; Wave D's agreement test unscoped; §6.1's heading contradicting its own body; two orphaned paragraphs; mechanism-table cite drift | applied in place |

N1 is the one that matters: **this design's own forward fix is what made the
reverse defect reachable.** Before §3.8.2 the forward pass never found the
match, so the blind reverse evaluation never got the chance to discard it.

Two of those deserve naming rather than tabulating, because they are this
lane's own failures of the kind the project keeps cataloguing:

- **M7 — provenance imitation.** A header in `out/` was hand-edited into the
  archiver's format. R30's words: a hand-written block imitating a mechanical
  archiver "is a sharper instance of *a control sharing a source with what it
  controls* than anything the archiver guards against — a reader cannot tell it
  from the real five without git archaeology." The file is now genuinely
  produced by `archive.sh`, and the rule this lane broke is now written down:
  **the archiver is the only writer of `out/`; a hand edit there is a red line.**
- **M6 — a named defect is not a fixed defect.** R24 M-F1 found, named and
  fixed the locale-collation `sort -u` undercount; this lane reproduced it
  verbatim in an uncommitted one-liner. Measured here: the corpus is **1030**
  patterns, the defect reports **609**, and **421 patterns were silently merged
  away**. The fix now travels as committed tooling.

**Everything R30 asked for is applied below.** Four items are explicitly NOT
this lane's to fix and are left alone: `eng_brep_design.md` §2.5's stale
figures, `../dev/decisions.md`, and the four other sites citing 0/720+180/720
(M3) — all manager-at-merge.

---

## 0. How to read this

### 0.1 Claim marking

Adopted verbatim from `engine_m4.md` §0.1, so the panel reads one vocabulary:

- **MEASURED** — a number or behaviour from an instrument, with its source
  cited. If the source is not cited it is not MEASURED.
- **RULED** — settled by a D-number in `../dev/decisions.md` or by a plan-row
  ruling of Frank's. Consumed here, not re-litigated.
- **STRUCTURAL** — true by inspection of code that exists today, file and line
  cited. Weaker than MEASURED (no instrument ran), stronger than BELIEVED (no
  inference chain).
- **BELIEVED** — the author's reasoning, unmeasured. Every BELIEVED claim in a
  load-bearing position is repeated in §12 with the experiment that refutes it.

### 0.2 The design in one paragraph

**REWRITTEN AFTER R30 E1**, which refuted the first draft's "exactly three".

The design turns on **four** mechanisms, and every construct is built from one
or more of them:

1. an **absolute position test** — `\A`, `\z`, `\G`: free, evaluated where the
   machine already knows the position;
2. a **next-byte view** — `$` and `(?m)$` in the forward machine, `\b`'s
   right-hand side: folds into the transition and accept tables *by byte
   equivalence class*, so it costs table width and no hot-path instructions;
3. a **previous-byte context bit** — `\b`'s left-hand side, `(?m)^`: folds into
   the DFA *state identity*, so it costs states;
4. **runtime start-state selection from a byte outside the search window** —
   the mechanism the first draft was missing entirely. At `startpos > 0` the
   context that mechanism 3 carries has to be *seeded* from `s[startpos-1]`,
   which is not in `[startpos, n)`; symmetrically the reverse machine's
   trailing-`\b` context must be seeded from `s[end]`, a byte that walk never
   consumes. Neither engine has this today: both start states are emitted as
   compile-time constants (`src/gen/emit_dfa.c:946`, `:1029`). §3.8 designs it.

**A construct may need more than one**, and saying "exactly three things" hid
that: `\b` needs 2 *and* 3 *and* 4, which is why it is the module's real work.
The forward and reverse machines swap which of 2 and 3 a given assertion
needs, because they consume bytes in opposite directions.

`\K` is the one construct built from none of them: it reports a
*path-dependent* position that subset construction has erased, so it is
VM-only — which the shipped registry already says
(`src/parse/registry.c:365`, `VM_ONLY`).

### 0.3 Measurements this lane produced

All under `assertions_measurements/`, probes committed, outputs archived with
their repo commit:

| instrument | kind | what it answers |
|---|---|---|
| `probes/probe_ncls_refine.py` | EXACT, in-pcrec | what the word/newline alphabet refinement costs (§3.4) |
| `probes/probe_wordctx_states.py` | PROTOTYPE, calibrated | what `\b`'s context bit costs in states (§3.5) |
| `probes/probe_acc_by_class.sh` | MEASURED, artifact benchmark | what a next-byte-sensitive accept costs the hot loop (§3.6) |
| `probes/probe_z_oracle.py` | MEASURED, both oracles | that python `re` is the WRONG oracle for `\Z` (§3.2.1) |
| `probes/probe_d475_scope.py` | MEASURED, both oracles | the scope-blind D47.5 gate, as concrete miscompile cells (§8.1.1) |
| `probes/probe_startpos_context.py` | MEASURED, libpcre2 | E1: assertion context at `startpos > 0`, and the find-all loop (§3.8) |
| `probes/probe_mline_caret_cost.sh` | MEASURED, artifact benchmark | E2: what `(?m)^` on ENG_ATTEMPT costs (§3.7) |
| `probes/probe_wswitch_alarm.sh` | MEASURED, self-restoring | M8: whether a new `AKind` raises a build alarm (§8.3) |
| `probes/harvest_rxt_patterns.sh` | the corpus population | M6: `LC_ALL=C`, and what the defect costs (§3.4) |
| `eng_brep_measurements/probes/probe_dollar_multiline_pcre2.py` | re-run, not rebuilt | the D47.5 gate's justification, today (§8.8) |

Every file in `assertions_measurements/out/` is written by
`probes/archive.sh`, which stamps one provenance header on all of them — probe
path, the commit the probe was last changed at, the commit and branch the run
was made from, whether the working tree was clean, date, and the python3,
libpcre2 and gcc versions. A number in this document can therefore be traced to
a run, not merely to a claim.

**Two provenance corrections R30 made, both this lane's own defects:**

- **M7.** `out/dollar_multiline_rerun.txt` was **hand-written into the
  archiver's format** rather than produced by it. That is worse than no header:
  a reader cannot distinguish a stamped file from an asserted one without git
  archaeology, which makes it a sharper instance of *a control sharing a source
  with what it controls* than anything the archiver guards against. The file is
  now genuinely re-run through `archive.sh` — and its header honestly records
  that the working tree was DIRTY at run time, which is the transparency the
  stamp exists for. **The rule, now written down: `archive.sh` is the only
  writer of `out/`. A hand edit there is a red line, not a formatting choice.**
- **M8.** §8.3's `-Wswitch` measurement was originally a hand edit reverted by
  hand, promising "its command and its output" and delivering output — nothing
  a read-only critic could re-run. It is now
  `probes/probe_wswitch_alarm.sh`: it appends the enumerator, runs
  `gcc -fsyntax-only`, counts, and restores the header under an EXIT trap that
  verifies the restore. It also refuses to report zero when it compiled
  nothing, because a broken invocation reading as "no warnings" is this probe's
  own version of the failure mode the document keeps finding elsewhere — a
  defect its first run actually had.

---

## 1. Premises, re-verified on HEAD rather than inherited

Every one of these was measured in this lane against the built binary, because
[M6.0]'s own expansion rule (constraint (a)) is that premises are re-verified at
use, and because one premise handed to this lane in its brief was **wrong**.

**MEASURED** (`build/pcrec` at `99e27ef`, one invocation per row):

| pattern | diagnostic |
|---|---|
| `\ba` | `\b requires module 'assertions' (pattern offset 0)` |
| `\Ba` | `\B requires module 'assertions' (pattern offset 0)` |
| `\Aa` | `\A requires module 'assertions' (pattern offset 0)` |
| `a\z` | `\z requires module 'assertions' (pattern offset 1)` |
| `a\Z` | `\Z requires module 'assertions' (pattern offset 1)` |
| `(?m)a$` | `inline option 'm' (multiline) requires module 'assertions' (pattern offset 2)` |
| `(?m:a$)` | `inline option 'm' (multiline) requires module 'assertions' (pattern offset 2)` |
| `\Ga` | `\G requires module 'assertions' (pattern offset 0)` |
| `a\Kb` | `\K requires module 'assertions' (pattern offset 1)` |

**The corrected premise.** This lane was told, on a source survey, that `(?m)`
is administratively owned by module `modifiers` (via `GROUP_OPT`'s hardcoded
`M_modifiers` at `src/parse/registry.c:230`) and would therefore need
re-attributing to `assertions`. **That is false.** The `GROUP_OPT` row at
`src/parse/registry.c:643` is the *recogniser*; the refusal is produced by the
`modifiers` module's own per-letter arm at `src/parse/mod_modifiers.c:280`:

```c
        case 'm':
            if (!hyphen)
                return modport_refuse(want, i,
                    "inline option 'm' (multiline) requires module 'assertions'");
            break;                        /* -m: true today, accepted */
```

So **question (vii) is already satisfied on HEAD for all eight constructs**: the
shipped diagnostics attribute every one of them to `assertions`, and no
re-attribution is part of this module's work. §9 covers what *is*.

**Three more premises, STRUCTURAL:**

- `\K` is the only row of the six escape rows carrying `VM_ONLY` rather than
  `ANY_ENGINE` (`src/parse/registry.c:358-365`). The engine split §3 arrives at
  is therefore *already recorded* in the registry for the one construct where it
  matters most.
- `cx->mods.multiline` **already exists** (`src/core/internal.h:310`) with the
  whole inline-option scoping machinery around it — `(?m:...)`'s
  set-parse-restore, `(?^)`'s reset-to-hardwired-defaults, `-m` accepted as a
  no-op — all built and tested at MOD-0.5. Only the letter's *acceptance* is
  refused. It has exactly **one consumer** in `src/`: `src/opt/possessify.c`.
- `\w`'s byte set is oracle-generated and re-measured every suite run:
  `pcrec_cls_word_esc[32]`, `src/parse/cls_bits.inc:19`, "63 members", generated
  by `tests/probes/probe_cls_bits.c --emit` against libpcre2 10.46, with PC-4
  re-measuring it against the live oracle. `pcrec_cls_newline[32]` is in the
  same file. §7 turns this into a requirement.

---

## 2. The mechanism, stated once

The whole module reduces to extending machinery `src/ir/dfa.c` already has. The
existing shape, **STRUCTURAL** (`src/ir/dfa.c:632-651`):

```c
static int make_state(Ctx *cx, Nfa *nfa, Dfa *d, bool prune,
                      const int *pre, int npre, bool bot_ok,
                      CloScratch *sc, int *scratch)
{
    ...
    closure(nfa, pre, npre, bot_ok, false, prune, sc, scratch,  &nout,  &accept);
    closure(nfa, pre, npre, bot_ok, true,  prune, sc, scratch2, &nout2, &accept2);

    if (!accept && !accept2 && nout == 0 && nout2 == 0) return -1;

    int eolvar = -1;
    if (accept2 != accept || nout2 != nout ||
        memcmp(scratch, scratch2, (size_t)nout * sizeof(int)) != 0)
        eolvar = intern(cx, d, scratch2, nout2, accept2, -1);

    return intern(cx, d, scratch, nout, accept, eolvar);
}
```

Two things are already true here and both are load-bearing for this module:

1. **A closure is parameterised by assertion context.** `eol_ok` is exactly a
   "may an EOL assertion pass here" bit, and the *second view is interned only
   when it differs* — `eolvar = -1` otherwise. Every assertion this module adds
   is another such bit, and every one of them inherits that
   pay-only-when-it-differs property for free.
2. **`bot_ok` is a start-state property, not a transition property.** It is
   passed `true`/`false` at the two start states (`src/ir/dfa.c:678-679`) and
   **hardcoded `false` in the worklist** — the loop spans
   `src/ir/dfa.c:681-695` and the call itself is at **`:692`**,
   `make_state(cx, nfa, d, prune, pre, npre, false, &sc, scratch)`. That is precisely why plain `^`
   works and why `(?m)^` cannot work without touching that line: multiline `^`
   is satisfiable *after consuming a byte*, which is a transition property.

So the four mechanisms of §0.2 map onto the existing code as:

| mechanism | where it lives | what it costs |
|---|---|---|
| 1. absolute position test | start-state selection (`s0`/`s1`), and the `pos >= n` boundary | nothing; evaluated once per attempt or once per search |
| 2. **next-byte view** | the closure's `eol_ok`-shaped bit, resolved **per byte equivalence class** at the transition | table WIDTH (§3.4), no hot-path instructions (§3.6) |
| 3. **previous-byte context bit** | the DFA STATE IDENTITY (`make_state`'s pre-set gains a bit) | STATES (§3.5) |
| 4. **runtime start-state selection** (R30 E1) | the emitted `int st = <const>;` / `int rst = <const>;` become a **dispatch** off `s[startpos-1]` (forward) and `s[end]` (reverse) | one lookup **once per search**, off the inner loop (§3.8) |

The reverse machine swaps mechanisms 2 and 3, because it walks backwards: what
is a next-byte view forward is a previous-byte context bit in reverse, and vice
versa. This is not an analogy — `src/gen/emit_dfa.c:1052-1056` already emits a
reverse EOL-variant selection (`<p>_rev[]`) mirroring the forward one
(`<p>_fev[]`).

**Mechanism 4 is the one the first draft was missing, and its absence was not
a gap in the prose — it was a gap in the design.** Mechanism 3 says the context
bit lives in the state identity; it does not say where the bit's *initial value*
comes from. Inside the loop it comes from the byte just consumed. At the START
of a search there is no such byte, and `startpos > 0` means the answer is
`s[startpos-1]` — outside the window the search is defined over. Both engines
emit that start state as a compile-time constant today
(`src/gen/emit_dfa.c:946` forward, `:1029` reverse), which is exactly the
encoding of "assume start of subject" that §3.8 measures wrong.

---

## 3. (i) The engine split

### 3.1 The table

Mechanism numbers are §0.2's / §2's. Note that **no context-bearing construct
uses only one** — the "exactly three things" framing R30 E1 struck was hiding
exactly this column.

| construct | DFA-representable? | mechanisms | forward engine | notes |
|---|---|---|---|---|
| `\A` | **yes — an exact alias of an existing node** | 1 | ENG_ATTEMPT | §3.2 |
| `\Z` | **yes — an exact alias of an existing node** | 2 (the existing `eolvar`) | ENG_UNANCH + ENG_ATTEMPT | §3.2 |
| `\z` | yes | 2 (a THIRD closure view) | ENG_UNANCH + ENG_ATTEMPT | §3.3 |
| `\b` `\B` | yes | **2 + 3 + 4** | ENG_UNANCH + ENG_ATTEMPT | §3.4–3.6, §3.8 |
| `(?m)$` | yes | 2 (fwd) + 3 (rev) | ENG_UNANCH + ENG_ATTEMPT | §3.7 |
| `(?m)^` | yes in principle | 3 + 4 (fwd) / needs the reverse BOT variant D8 deferred | **ENG_ATTEMPT** — and this is a **measured O(n²) class change**, not a free inheritance | §3.7 |
| `\G` | yes | 1 (start-state property + `start_max`) | **ENG_ATTEMPT** | §4 |
| `\K` | **no** | none of the four | **VM only** | §6 |

Both engines carry every row: the VM already emits `A_BOL`/`A_EOL`
(`src/gen/emit_vm.c:3458-3474`) and every construct here has a trivial VM
spelling (§9.3). The column above is which *DFA* engine a pattern lands on.

### 3.2 `\A` and `\Z` are aliases, and this is the cheapest finding in the module

**STRUCTURAL.** pcrec's existing nodes already have exactly PCRE2's `\A` and
`\Z` semantics, in their own comments:

- `src/core/internal.h:152-159`: `N_BOT, /* assert start of subject, goto t1 */`
  and `N_EOL, /* assert end-of-subject or before-final-\n, goto t1 */`.
- `src/gen/emit_vm.c:3458`: "`^` is start of SUBJECT, absolute — it anchors to
  offset 0 whatever startpos was".

PCRE2's `\A` is "start of subject, unaffected by multiline"; `\Z` is "end of
subject, or before a final newline, unaffected by multiline". Those are
character-for-character the two comments above. So:

> `\A` lowers to `A_BOL`, `\Z` lowers to `A_EOL`, and **no engine work exists**
> for either. They are parser rows.

**ANNOTATED [M6.2] WAVE A, 2026-08-19 (implementation lane; Frank surfaced the
paragraph, manager brief addendum).** Two things this section does not say, and
the second is a real gap rather than a detail. The section's own source
paragraph (pcre2pattern, "Simple assertions") reads in full: `\A`, `\Z` and
`\z` *"only ever match at the very start and end of the subject string,
whatever options are set. Thus, they are independent of multiline mode."*

1. **The alias must PIN multiline false, not inherit it.** §3.2's argument is
   about the node's SEMANTICS and §8's cure adds a parse-resolved
   `Ast.multiline` FIELD to that same node; put together, the `\A`/`\Z`
   producer has to write `false` where `^`/`$` write the scoped state, or
   wave C's acceptance of the `m` letter leaks multiline-`$` machinery into
   `\Z`. Landed as an explicit assignment plus a comment
   (src/parse/mod_assertions.c) rather than as a reliance on the arena's
   zero, because with `(?m)` refused the two versions are indistinguishable
   by every test in the tree until the day the bug arrives.

2. **The alias ERASES a distinction a RULED future surface needs, and this
   section is silent on it.** `PCRE2_NOTBOL`/`PCRE2_NOTEOL` affect `^` and `$`
   ONLY; `\A`/`\Z`/`\z` are unaffected. Both are RULED **API-PARAM**
   (`../pcre2_options.md` rows 200-201, RATIFIED D38) — a match-CALL
   parameter, so a committed future surface rather than a NEVER. An artifact
   compiles once and that parameter arrives at match time, so the emitter will
   have to know which `A_BOL` nodes came from `\A` and which from `^` —
   information a pure alias throws away.

   **MEASURED** (libpcre2 10.46, this lane; a documentation paragraph is not a
   measurement, and the distinction is the whole point):

   ```
   pattern  subject   options=0   NOTBOL     NOTEOL
   ^a       "ab"      (0,1)       NO MATCH   (0,1)      <- affected
   \Aa      "ab"      (0,1)       (0,1)      (0,1)      <- not
   b$       "ab"      (1,2)       (1,2)      NO MATCH   <- affected
   b\Z      "ab"      (1,2)       (1,2)      (1,2)      <- not
   b$       "ab\n"    (1,2)       (1,2)      NO MATCH   <- affected
   b\Z      "ab\n"    (1,2)       (1,2)      (1,2)      <- not
   ```

   So **"no engine work exists" holds at options = 0 and is where the claim
   ends.** The fix, when it has a customer, is a PARSE-RESOLVED PROVENANCE
   FIELD in D62's shape, beside `multiline`. Wave A deliberately does NOT
   build it: a field with no consumer has no test that can go red, which is
   the discipline D18/OS-0/D53 state and [M4.7a] applied when it declined
   SR-8's socket. What wave A owed was that the requirement be recorded where
   the erasure happens, which is this annotation and the comment at the
   producer.

3. **A test-axis confirmation, not a correction.** The same paragraph notes
   that with a non-zero `startoffset` `\A` can never match. That is already
   pcrec's `A_BOL` semantics (`emit_vm.c:3458`) and R30's 1,008-cell
   differential swept every startpos, but the property is now also pinned by
   the module's OWN corpus rather than only by the design lane's archived
   probe: `tests/assertions/absolute.rxt` carries six `ns <P>` cells at
   `P > 0` for `\A` and `ms <P>` cells for `\z` and `\Z` at the same
   offsets — including the `"ab\n"` rows, where `\Z` reports (2,2) and `\z`
   reports (3,3) at an identical nonzero startpos, so the three-way
   distinction is pinned under `startpos` and not only at 0.

#### 3.2.1 `\Z` cannot be oracle-verified against python `re` — MEASURED

CLAUDE.md's standing rule is that expectations are oracle-verified with python3
`re` for the base tier. **For `\Z` that rule produces wrong expectations**, and
silently.

**MEASURED this session, both oracles, `out/z_oracle.txt`
(`probes/probe_z_oracle.py`, libpcre2 10.46, python 3.14.4):**

```
pattern        subject  pcre2      python     verdict
b\Z            'ab\n'   (1, 2)     None       *** DISAGREE ***
b\Z            'ab'     (1, 2)     (1, 2)     agree
b\z            'ab\n'   None       None       agree
b\z            'ab'     (1, 2)     (1, 2)     agree
b$             'ab\n'   (1, 2)     (1, 2)     agree
b$             'ab'     (1, 2)     (1, 2)     agree
b(?=\n?\Z)     'ab\n'   (1, 2)     (1, 2)     agree
```

**python's `\Z` IS PCRE2's `\z`.** Python has no single escape for PCRE2's `\Z`
at all — the last row shows the only python spelling, `(?=\n?\Z)`, and it needs
lookahead, which is module `lookaround` and not available in this module's
tests. The disagreement is in the dangerous direction: python reports **no
match** exactly where PCRE2 matches, so a `.rxt` cell written from python would
encode `\Z` as `\z` and the suite would go green on a miscompile.

**Consequence for Wave A (§10):** `\Z` expectations must come from the libpcre2
differential, not from python, and the wave's brief must say so. This is the
same class of trap [M6.3]'s row already records for named groups (python speaks
only `(?P<n>...)`), which is why it is stated here rather than left to be
rediscovered.

This is also the reason the multiline design in §3.7 resolves at parse time:
once `(?m)` exists, `^` is *sometimes* `A_BOL` and `$` is *sometimes* `A_EOL`,
but `\A`/`\Z` are **always** those nodes. A design that made multiline a
whole-pattern flag consulted downstream would have to re-derive that
distinction at every consumer; resolving it in the parser makes it inexpressible.

### 3.3 `\z` needs one more view, and it costs nothing when absent

`\z` is "end of subject", strictly stronger than `\Z`. Three position views
therefore exist where `make_state` computes two:

| position | `\Z` / `$` | `\z` |
|---|---|---|
| interior | no | no |
| `pos + 1 == n && s[pos] == '\n'` | **yes** | no |
| `pos == n` | **yes** | **yes** |

**Proposed:** `closure` gains an `end_ok` bit (with `end_ok ⇒ eol_ok`), and
`make_state` computes three closures and interns up to two variants, `eolvar`
and a new `endvar`, each `-1` when identical — the existing convention at
`src/core/internal.h:181-183`.

**CORRECTED AFTER R30 E3 — the first draft canonicalized against the wrong
reference, and the error was one sentence wide.** It said `endvar` is `-1`
"when identical to the base", then argued zero-regression from
`(T,T) == (T,F)`. Those are different comparisons. `endvar`'s view is
`(eol_ok, end_ok) = (T,T)`; the view it must be compared against is the **EOL
view** `(T,F)`, not the base view `(F,F)`. Canonicalizing against the base makes
every eol-differing state of every `$`-bearing pattern intern a live `endvar`,
and the artifact is **not** byte-identical — the exact opposite of the claim.

**The corrected rule, three-way:**

```
base  = closure(pre, eol_ok=F, end_ok=F)
eolv  = closure(pre, eol_ok=T, end_ok=F)   ; interned iff eolv  != base
endv  = closure(pre, eol_ok=T, end_ok=T)   ; interned iff endv  != eolv
                                           ;   (and reuses eolvar's id if
                                           ;    eolv == base, so a `\z`-free
                                           ;    pattern interns nothing new)
```

**The zero-regression property now holds, and still by construction rather
than by a flag.** With no `\z` in the pattern, `end_ok` gates nothing, so
`endv == eolv` at every state, `endvar` is `-1` everywhere, and the emitter
emits today's code byte-for-byte. No `has_z` conditional is needed.

**What this episode is evidence FOR**, and R30 said so explicitly: Wave A's
proposed byte-identity check (§10) would have caught this. The check was right;
the claim was wrong. That is the argument for landing the check even where the
prose says it cannot fail — a claim of the form "X is impossible by
construction" is exactly the claim a construction check is for.

### 3.4 `\b`'s alphabet cost — EXACT, and it is at most one class

Carrying "the previous byte was a word character" requires the word set to be a
**union of byte equivalence classes**, because the context bit must be constant
inside a class. That is an alphabet refinement, and refinement costs
`states × ncls` table entries against `PCREC_MAX_TABLE_ENTRIES`
(`src/core/limits.h:50`, 2,000,000).

**MEASURED, EXACTLY, in pcrec** — `probes/probe_ncls_refine.py` reads the
emitted artifact's own `<prefix>_fcls[256]` map and `<prefix>_facc[]` length, so
these are pcrec's post-minimisation numbers (`src/core/compile.c:224`), not a
model's. Two denominators, following `eng_brep_design.md` §2.6's rule that
either alone misleads:

| corpus | n | word refinement | newline refinement | both |
|---|---|---|---|---|
| realistic set (`eng_brep_measurements/probes/realistic_patterns.txt`) | 38 | delta min/median/max **0 / +1 / +1** | 0 / +1 / +1 | 0 / +2 / +2 |
| the `.rxt` corpus (**962 of 1030**, corrected — see below) | 962 | **0 / +1 / +2** | 0 / +1 / +1 | **+1 / +2 / +3** |

Largest `states × ncls` over the `.rxt` corpus **after both refinements**:
**48,012**, on `((a)|ab){4000}c` — **2.4% of the 2,000,000 budget**. Archived:
`out/ncls_refine_realistic.txt`, `out/ncls_refine_rxt.txt`.

The reason the delta is so small is worth stating, because it is the sort of
result that looks too good: refining a partition by one set can in principle
split *every* class, but a pattern's class map already separates the bytes it
mentions, and the only class that straddles the word boundary is the catch-all
of bytes the pattern never names. Adding a second set (newline) adds at most one
more for the same reason.

Two patterns were skipped and both are pre-existing facts, not assertion facts:
`\[[^\]]{1,80}\]` refuses today with `pattern too complex for the DFA engine
(>32000 states; try --engine=vm)`, and `\b\w{5,}\b` refuses because `\b`
refuses.

**THE CORPUS POPULATION WAS WRONG, AND THE DEFECT HAS A NAME (R30 M6).** The
first draft said "574 of 609", harvested by an uncommitted one-liner whose
`sort -u` ran under `en_US.UTF-8`. That collation treats strings differing only
in punctuation as equal — and for a corpus of *regexes*, where punctuation is
the content, that is close to a worst case. This is R24 M-F1 verbatim: a defect
`eng_brep` already found, named, and fixed with `LC_ALL=C`, reproduced here by
a lane that had read the entry.

**MEASURED** (`probes/harvest_rxt_patterns.sh`, `out/rxt_harvest.txt`):

```
raw 'pattern' lines            : 1165
distinct under LC_ALL=C        : 1030   <- the population
distinct under en_US.UTF-8     : 609    <- what the defect reports
patterns the UTF-8 collation would have SILENTLY MERGED AWAY: 421
```

**The conclusion is unchanged and the numbers are identical.** Re-run on the
corrected 1030-pattern corpus: word `0/+1/+2`, newline `0/+1/+1`, both
`+1/+2/+3`, largest `states × ncls` **48,012 on the same pattern** — the figures
above. R30's own critic re-derived this independently and got the same. The
provenance defect was real; the finding it supports did not move.

The fix travels as **committed tooling**, not as knowledge, which is R30's
process lesson 3: a named defect is not a fixed defect. The harvest script
prints both counts every run, so the failure is visible rather than latent.

#### 3.4.1 What this corpus does NOT cover — disclosed after R30 E4

The probe reads `<prefix>_facc[]`, which **only ENG_UNANCH emits**. ENG_ATTEMPT
emits computed-goto label blocks and no accept array
(`src/gen/emit_dfa.c:1126-1150`), so every `^`-bearing pattern in the corpus
contributes a class-map row and **no state count at all**.

That matters more here than it would in another section, and R30 put it
sharply: the state budget was measured **only on the engine that `(?m)^` and
`\G` do not use**. §3.7 routes `(?m)^` to ENG_ATTEMPT and §4 routes `\G` there,
so the two constructs whose engine choice this design argues hardest about are
the two the budget evidence is silent on.

It is a real gap and this note does not close it. What it does instead is state
the consequence as a **Wave B landing condition** (§10): the composed-budget
check must run against `PCREC_MAX_DFA_STATES_GOTO` (10,000,
`src/core/limits.h:48`) for ENG_ATTEMPT patterns as well as against
`PCREC_MAX_DFA_STATES_TABLE` (32,000) for ENG_UNANCH ones — and the goto cap is
**3.2x tighter**, so an ENG_ATTEMPT pattern has proportionally less headroom
than every number above suggests.


### 3.5 `\b`'s state cost — PROTOTYPE, calibrated, and the ratio is the number

pcrec cannot compile `\b`, so this number cannot be read off an artifact. It is
therefore a **PROTOTYPE**, `probes/probe_wordctx_states.py`, and the document
says so in three places rather than once.

The prototype builds exactly the automaton this design proposes — DFA state =
(NFA pre-set, previous byte was a word character), closure parameterised by
`(prev_is_word, next_is_word)` in the same way `src/ir/dfa.c:640-641`
parameterises by `eol_ok`, with the unanchored self-loop
(`nfa_wrap_unanchored`, `src/ir/nfa.c:652` — corrected here; `engine_m4.md`
§7.3 still cites the pre-move `:590`, see §4.1's cite note) and **Moore
minimisation**, because
pcrec minimises and an unminimised count would overstate the cost: the entire
question is how many context-split states *survive being distinguished*.

**The number that carries weight is the RATIO**, `\bPAT\b` against `PAT`, since
both arms come out of the same constructor and any divergence from
`src/ir/dfa.c` cancels.

**MEASURED** (n = 35 of the realistic set; `out/wordctx_states_realistic.txt`):

> minimised state ratio min / median / max = **1.00x / 1.11x / 4.75x**
> — 2 patterns at ≤ 1.00x, and (**corrected after R30 M2**) **1** pattern
> above 2.00x, not 2.

Representative rows:

```
pattern (measured as \bPAT\b)             base wordctx  ratio  ncls0  ncls1
[0-9a-f]{64}                                65      66  1.02x      2      3
[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0      37      38  1.03x      3      4
\d{4}-\d{2}-\d{2}                           11      12  1.09x      3      4
https?://[a-zA-Z0-9.-]+/[a-zA-Z0-9/_-]      21      24  1.14x     10     11
\b\w{5,}\b                                   6       6  1.00x      2      2
\w{3,16}                                     4      18  4.50x      2      2
(?:ab){1,8}c                                 4      19  4.75x      4      5
```

The theoretical bound is 2x (the state gains one bit). Two rows exceed it,
which is not a contradiction: minimisation of the *baseline* arm collapses
states that the context bit then re-distinguishes, so the ratio is measured
against a smaller denominator than the bound assumes. Both offenders are
patterns whose body is drawn from the word alphabet itself — exactly where a
word-boundary context is real information.

**CALIBRATION, and its honest residual.** On the assertion-free arm the
prototype reproduces pcrec's own `<prefix>_facc[]` length on **29 of 33**
patterns pcrec compiles. The four disagreements are reported in the archived
output and here:

```
https?://[a-zA-Z0-9.-]+/[a-zA-Z0-9 prototype   21  pcrec   16
\w{3,16}                           prototype    4  pcrec   17
\d{1,3}(?:,\d{3})+                 prototype    6  pcrec    9
(?:[A-Za-z]+ ){2,4}[A-Za-z]+       prototype    6  pcrec   10
```

They disagree in **both** directions. The first draft noted that and drew no
conclusion from it; R30 M2 did, and it was the right one — **there are TWO
fidelity gaps, in opposite directions, and the first draft named only one.**

**Gap 1 (disclosed originally): no priority pruning.** `src/core/compile.c:216`
builds the forward DFA with `prune=true` and this constructor does not prune.
This makes the prototype **OVER**count, and is why five corpus patterns are
reported over-cap rather than half-measured — on `[a-z][a-z0-9_]{2,31}` pruning
is the difference between pcrec's 33 states and a subset blow-up here.

**Gap 2 (found by R30, in the opposite direction): the prototype minimises a
LANGUAGE, pcrec does not.** pcrec's `DState.list` is a *priority-ordered* list
of NFA states (`src/core/internal.h:177-185`), so pcrec distinguishes states
that accept the same language but order their threads differently — it has to,
because it reports leftmost-first spans, not membership. Moore minimisation over
accept-signatures merges exactly those. So the prototype **UNDER**counts
wherever a bounded repeat over a wide alphabet produces many priority-distinct
but language-equivalent states.

**MEASURED, and it is the outlier that carried the second ">2.00x" row:**

| pattern | prototype base | pcrec's real base | agree? |
|---|---|---|---|
| `\w{3,16}` | 4 | **17** | **no — 4.25x undercount** |
| `(?:ab){1,8}c` | 4 | 4 | yes |
| `"[^"]*"` | 3 | 3 | yes |
| `[aeiou]{2,3}[^aeiou]{1,2}` | 5 | 5 | yes |
| `[A-Z]{4,8} [0-9]{3}` | 9 | 9 | yes |
| `\d{1,3}(?:,\d{3})+` | 6 | 9 | no |

`\w{3,16}` is minimal-language 4 (any run of 3+ word characters) and pcrec's 17;
against pcrec's real baseline its `\b` arm of 18 is **≈1.06x, not 4.50x**. So
that row is not an outlier at all, and the ">2.00x: 2 patterns" line is
corrected to **1**.

**The headline max survives, and survives better than before.** The remaining
>2.00x pattern is `(?:ab){1,8}c` at **4.75x** — and the table above shows its
prototype baseline is **verified against pcrec exactly** (4 = 4). The number
this design leans on is the one whose denominator is confirmed; the number that
fell is the one whose denominator was not.

### 3.5.1 Composing §3.4 with §3.5 — and the state cap is EXCEEDED

**NEW AFTER R30 E4**, which is the finding this note is least comfortable
with: §3.4 measured the alphabet cost, §3.5 measured the state cost, and the
first draft **never multiplied them**. It concluded "`\b` does not move the
budget question" from two numbers neither of which is the budget.

Composed at this document's own worst measured values:

| quantity | value | source |
|---|---|---|
| worst corpus state count | **8,002** on `((a)|ab){4000}c` | §3.4's corpus, `out/ncls_refine_rxt.txt` |
| worst measured `\b` state ratio | **4.75x** | §3.5 |
| composed | **38,009 states** | |
| `PCREC_MAX_DFA_STATES_TABLE` | **32,000** (`src/core/limits.h:49`) | |

> **38,009 > 32,000: the composed worst case EXCEEDS the state cap.** The table
> budget goes from 2.4% to **11.4%**. The binding constraint is *not* comfortably
> `states × ncls` after all.

**And one table this section has to count now that it exists (R30 item 2):**
§3.8.3.1's reverse boundary accept is `states x (ncls + 1)` — the `+1` is the
`RX_CLS_BOT` sentinel for `startpos == 0`, where there is no byte to classify.
It is consulted **once per search**, so it is not a hot-path cost, but it is a
per-artifact table and this section just made a point of counting those. At the
corpus's worst state count it is ~8,002 x 7 bytes — negligible against the
2,000,000-entry transition budget, and stated rather than omitted because a
section that counts tables should count all of them.

Three honest qualifications, none of which rescue the original claim:

1. The two worst values come from different patterns. `((a)|ab){4000}c` is
   inside §3.5's named worst-ratio class (a bounded repeat over an ambiguous
   body), but no single measured pattern is both simultaneously — the
   composition is a **bound**, not an observation.
2. A pattern at the cap does not miscompile; it **refuses** with
   `pattern too complex for the DFA engine`. The failure is a compile-time
   refusal of a pattern that compiles today — a regression in capability, not
   in correctness.
3. §3.4.1's exclusion makes this *worse*, not better, for the ENG_ATTEMPT
   half: that cap is 10,000, not 32,000.

**Consequence, replacing the struck claim:** `\b` DOES move the budget
question, and by how much is a **Wave B landing condition** rather than
something this design can settle from a prototype — the composed measurement
has to be taken on the built compiler, against both caps, with the refusal
boundary located rather than predicted (§10).

> **MEASURED BY [M6.2] WAVE B (2026-08-19, lane/asrtwaveb). THE 38,009
> FORECAST IS REFUTED AS AN OBSERVATION AND STANDS AS A BOUND.** Numbers and
> provenance: `assertions_measurements/out/wordctx_budget.txt`
> (`probes/probe_wordctx_budget.py`, both arms on pcrec rather than a model on
> both); the alphabet half re-confirmed in `out/ncls_refine_rxt.txt`.
>
> - **The ratio held at the top and broke at the bottom.** Measured
>   min/median/max **0.67x / 1.10x / 4.75x**. The max reproduces §3.5's
>   headline exactly, on the pattern whose baseline §3.5 verified against
>   pcrec — the number this section leans on is the one that survived. The
>   MIN is **below 1**: the word context can SHRINK a machine
>   (`[01]*1[01]{8}` is 768 states bare and 513 with it), an outcome the
>   prototype could not express and this section's arithmetic could not
>   contain. The alphabet delta measured +0/+1/+1, inside §3.4's 0/+1/+2.
> - **On THIS SECTION'S OWN worst family the word context RAISES the
>   ceiling.** `((a)|ab){N}c` refuses at N=5655 and `\b((a)|ab){N}c\b`
>   compiles to N=15998 (31,999 states). The reason is the one qualification
>   this section did not have: the bare arm is bound by
>   `PCREC_MAX_SUBSET_ELEMS`, not by the state cap, because the unanchored
>   self-loop keeps every offset's threads alive — and a leading `\b` PRUNES
>   most start positions, so the wrapped arm's state SETS are smaller and the
>   binding constraint moves to the state COUNT. Composing a state-count
>   ratio against a state-count cap silently assumed the state count was what
>   binds.
> - **ENG_ATTEMPT's boundary is IDENTICAL with and without the context**
>   (N=4999, 10,000 states), so qualification 3 above — that §3.4.1's
>   exclusion makes this worse for the goto half — did not materialise
>   either.
> - **The genuine regression had to be looked for, and is ONE REPEAT COUNT
>   WIDE.** It needs a family the state COUNT binds, i.e. a linear chain:
>   `[a-z]{1,31999}` compiles at exactly 32,000 states and
>   `\b[a-z]{1,31999}\b` refuses. Qualification 2 holds exactly as written —
>   a clean states-cap refusal, no output file — and
>   `tests/assertions/run_assertions_tests.sh` pins that PROPERTY on both
>   engines rather than pinning the boundary's location, which moves with any
>   legitimate change to the construction.

### 3.6 The hot-path cost of a next-byte view — MEASURED at zero

A next-byte-sensitive assertion changes the forward loop's accept test. Today
(`src/gen/emit_dfa.c:961`):

```c
        if (rx_facc[st]) last = pos;
```

Under `\b` or `(?m)$` the accept bit depends on the byte at `pos`, so it becomes
a `states × ncls` lookup indexed by the class of that byte — the class the very
next line already computes for the transition
(`st = rx_ftr[st * ncls + rx_fcls[s[pos++]]]`).

`probes/probe_acc_by_class.sh` measures that on `[01]*1[01]{8}` (D11's own
shape, and one with a live skip loop) using an **answer-preserving** variant:
every row of the wide table is that state's old bit, so both artifacts report
identical matches and the only difference is the lookup.

**MEASURED** (`out/acc_by_class.txt`, 768 states, ncls 3, best of 5, three
repetitions, 8 MB subject, identical `matches=54424` both arms):

```
A facc[st]              0.0405 s  197.5 MB/s  matches=54424
B facc2[st*ncls+cls]    0.0395 s  202.5 MB/s  matches=54424
A facc[st]              0.0405 s  197.3 MB/s  matches=54424
B facc2[st*ncls+cls]    0.0395 s  202.4 MB/s  matches=54424
A facc[st]              0.0405 s  197.3 MB/s  matches=54424
B facc2[st*ncls+cls]    0.0395 s  202.4 MB/s  matches=54424
```

(An earlier run of the same probe, before the archive header existed, read
197.4/197.6/197.5 against 202.9/203.0/202.7 — the same result at the same
spread. The archived numbers are the ones quoted, so the document and
`out/acc_by_class.txt` agree line for line.)

**The wide table is not slower.** The spreads do not overlap and B is
consistently ~2.6% *faster*, which this note does not claim as a speedup — it
claims the honest thing, that **the cost is not measurable on this shape** and
that a design predicting a per-byte penalty here would be wrong. The likely
reason is that the index is already in a register for the transition.

**SCOPE, stated after R30 E6 — this measurement covers ENG_UNANCH and nothing
else.** ENG_ATTEMPT has no `facc[]` array to widen: it bakes acceptance into
the computed-goto body as a literal `last = pos;` at each accepting label
(`src/gen/emit_dfa.c:1143-1149`). The A/B variant above is not even expressible
there. So the engine `(?m)^` and `\G` route to is **the one this number does not
cover**, and that engine's EOL-variant branch carries no `__builtin_expect`
guard either (`:1131-1136`). The class-indexed accept on ENG_ATTEMPT is an
un-measured cost, and §13 now lists it.

### 3.6.1 The D11 hazard this design must NOT walk into

**STRUCTURAL, and it is the most dangerous item in the module.** D11 rule 1: a
prefilter or self-loop skip advances `pos` without consulting accept flags, and
is unsound exactly when a state can accept at a position the skip passes. Today
that is only EOL positions, which is why the bound is `n-1`.

With a **class-indexed** accept, the accept bit *can* vary within a skipped run,
so the existing scan avoidance can become unsound in a way D11's `n-1` bound
does not fix. **Which patterns "can" covers is the whole of R30 E5, and the
first draft got it backwards.**

#### The attribution was WRONG — R30 E5

The first draft blamed this on `\b`, made it Wave B's headline hazard, and
proposed a Wave B sabotage row for it. **`\b` cannot suffer this hazard at
all**, and the reason is this document's own §3.5:

> Within a skipped run the DFA state is constant, so **prev-is-word is
> constant** — it is part of the state identity (§3.5). The refinement of §3.4
> makes the word set a union of byte equivalence classes, and a skip set is a
> union of classes too, so every byte in the run has the same **next-is-word**
> value as well. Both of `\b`'s inputs are pinned across the run, so its accept
> bit is CONSTANT across it, so the skip is sound.

The hazard is real, but it belongs to the **`(?m)$` / `\Z` family**, whose
accept depends on "is the next byte a newline" — a predicate that genuinely
varies inside a run a skip set admits.

> **REFUTED IN PART BY [M6.2] WAVE B (2026-08-19, lane/asrtwaveb) — READ THIS
> BEFORE INHERITING THE ARGUMENT ABOVE, WAVE C ESPECIALLY.**
>
> The block quote's **second sentence is FALSE**. "A skip set is a union of
> classes too, so every byte in the run has the same next-is-word value" does
> not follow: a union of byte equivalence classes may perfectly well contain
> both word and non-word classes. A state that stays put on `a` and on a space
> has exactly such a stay set, and `next-is-word` then varies inside the run
> the skip passes.
>
> The FIRST sentence survives untouched — `prev-is-word` really is constant
> across a skipped run, because it is part of the state identity. So the
> attribution correction R30 E5 makes (the hazard is not `\b`'s *headline*
> hazard, and a Wave B sabotage of the intersection would have no failing
> direction on any pattern Wave B lands) STANDS. What does not stand is the
> stronger claim that `\b`'s accept bit is pinned across a skipped run and the
> skip is therefore sound by construction.
>
> **WHAT WAVE B SHIPPED IS A DECLINE, NOT AN INTERSECTION.**
> `pick_skip_states` (`src/gen/emit_dfa.c`) drops any state whose two accept
> bits differ, so a state whose accept depends on the next byte is simply not
> skip-eligible. Declining is always available and always safe, and it costs
> nothing on any pattern without a next-byte-sensitive accept — i.e. nothing
> in the pre-wave corpus, where the test is false at every state, which the
> byte-identity gate measures at 1039/1039.
>
> **WHY THIS MATTERS TO WAVE C RATHER THAN TO WAVE B.** Wave C inherits the
> five-mechanism table below and its cure (intersect rows 2-5) from a section
> whose stated soundness argument for the `\b` half does not hold. A Wave C
> author re-deriving "the run pins both inputs" from the un-annotated text
> would build an intersection on a premise this lane measured false. The two
> available postures are DECLINE (wave B's, cheap, provably safe) and a real
> INTERSECTION (wave C's, which must not lean on the quoted sentence for its
> `\b` arm).

>
> **[M6.2] WAVE C, 2026-08-19 — WHAT EACH MECHANISM ACTUALLY SHIPS, AND WHICH
> OF THE FIVE HAS A FAILING DIRECTION AT ALL.** The section proposes
> INTERSECTION for rows 2-5 and DECLINE for row 1. Wave C decided per
> mechanism ON MEASUREMENT, and **not one of the five ships an intersection** —
> but the more useful finding is that **only one of the five turns out to be a
> live hazard**:
>
> | # | mechanism | posture SHIPPED | is it a live hazard? |
> |---|---|---|---|
> | 1 | memchr prefilter | DECLINE, via the widened `start_acc` | **NO — the guard is REDUNDANT**, see below |
> | 2 | bitmap prefilter | DECLINE, same `start_acc` (rows 1 and 2 ride ONE emit gate) | **NO**, same argument |
> | 3 | forward self-loop skip | DECLINE (`pick_skip_states` drops a state whose accept varies) | **YES — sabotage S78, measured** |
> | 4 | post-skip compensating accept | not emitted under `views`; the cure is the evaluation ORDER | **NO — it can only UNDER-report**, see below |
> | 5 | reverse self-loop skip | DECLINE, same `pick_skip_states` | **YES**, covered by S78 |
>
> **ROWS 1 AND 2: `start_acc` IS REDUNDANT, BY THIS FILE'S OWN RECORDED
> ARGUMENT.** §3.6.1 predicts that a narrowed `start_acc` makes `\bx*` on
> `'a x'` report only `(2,3)`. It does not, and the reason is D3's
> accept-pruning: the unanchored start self-loop is the LOWEST-priority
> thread, so any closure that reaches ACCEPT prunes it — therefore a class the
> start state ACCEPTS on cannot transition back to the start state, therefore
> that class ESCAPES, therefore the prefilter's stay set excludes it and the
> skip never passes an accepting position. `src/gen/emit_dfa.c` already states
> that argument, for the neighbouring `last == (size_t)-1` gate, and records
> that two independent critics attacked that gate and neither could build a
> witness.
>
> MEASURED the same way, this lane: narrowing `start_acc` to one class's bit
> changes **21 corpus artifacts** and **0 answers** over 2,247 find-all cells
> (21 patterns x 107 subjects, against the unsabotaged compiler). So the
> widening is kept — it is free, and it is the honest reading of "accepts on
> any class" — but it is NOT cited as load-bearing and it ships NO sabotage
> row, because a row with no failing direction is this project's recorded
> check-design failure and writing one here would have been the section's own
> mistake repeated.
>
> **ROW 4 CAN ONLY UNDER-REPORT.** Under `views` the compensating `last = pos;`
> is not emitted at all (the accept check already runs after the skip), and
> even when the guard is removed the line records the state's UPC_PLAIN accept
> at the landing position — which is never GREATER than the correct bit, since
> the EOL view's closure is a superset of the base's and a skip-eligible
> state's accept does not vary by class. Measured: re-emitting it changes **13
> corpus artifacts** and **0 answers** over 1,391 cells, and **still 0 new
> answers when combined with row 3's sabotage**. No row.
>
> **THE COST OF DECLINING (rows 3/5) WAS MEASURED, NOT ASSUMED.** On the
> pre-wave corpus it is exactly zero — the eligibility test is false at every
> state, so not one artifact moves, which the byte-identity gate measures at
> 1039/1039. On the `(?m)$` family it is not zero: `(?m)[^c]*$` keeps its skip
> tables for the states whose accept does not vary and loses them for the one
> that does. That is a real loss and it is accepted, because an intersection
> for rows 3/5 would have to compute "the accept row masked by the stay set"
> per state and emit a per-class stay table to exploit it — new machinery, on
> the hot path, for a population no benchmark in this project measures.
> **Recorded here rather than left implicit so a later lane can price it.**
>
> **S78's WITNESSES, since the section calls this the module's most dangerous
> item and a claim of danger deserves a demonstration:**
>
> ```
> (?m)[^c]*$  on "\n\nc"     (0,1) becomes (0,0)          -- a SHORT match
> (?m)[^c]*$  on "a\nb\nc"    (0,3) becomes (0,1)
> (?m)[^c]+$  on "a\nb\nc"    [(0,3)] becomes [(0,1), (1,3)]
> ```
>
> None of those subjects was in the corpus's first draft; all three are in it
> now, by name, because the sabotage would otherwise have come back
> UNDETECTED against single-newline subjects.

**The consequence is worse than the misattribution.** A Wave B sabotage row
disabling the intersection would be a **no-op on every pattern Wave B lands** —
a check with no failing direction, in the wave this document calls most
dangerous, which is exactly the project's recorded check-design failure mode.
The cure and its sabotage therefore **move to Wave C** (§10); if Wave B wants
the machinery early it must land with a `(?m)$`-shaped stand-in that can
actually go red.

#### All FIVE scan-avoidance mechanisms, with individual fates

The first draft named one. There are five, and they do not share a fate:

| # | mechanism | site(s) | fate under a class-indexed accept |
|---|---|---|---|
| 1 | **memchr prefilter** | `emit_dfa.c:988` (non-EOL) and **`:971`** (the EOL arm — a SECOND emission site the first draft's cite missed) | **CANNOT be intersected** — it seeks one byte VALUE, not a bitmap walk (see below) |
| 2 | **bitmap prefilter** | `:993` | intersectable: `first[]` becomes `first[] AND NOT accepts-here` |
| 3 | **forward self-loop skip** | `:1002` | intersectable: `fs<K>[] AND NOT K-accepts-on-this-class` |
| 4 | **post-skip compensating accept** | `:1006-1007` | reads a **SCALAR** `fd->st[K].accept` — must become the class-indexed read, or the recorded `last` is wrong for the run's final byte |
| 5 | **reverse self-loop skip** | `:1042`, with its own accept write at `:1044` | intersectable, mirrored (the reverse accept is `racc`) — and `:1044` is a second blind `sfound` writer, see §3.8.3.1 |

**Cites re-derived after R30 N8**; the first draft's `:1000`/`:1003-1004`/
`:1046-1048` were each a line or two off and missed the memchr EOL arm entirely.

**Why `fbound` is not a sixth row.** `fbound`
(`:942`, `eol ? "pos + 1 < n" : "pos < n"`) appears in the emitted text of
mechanisms 2 and 3 and looks like a sixth entry in a grep. It is not a
scan-avoidance mechanism — it is **D11 rule 1's bound**, the `n-1` clamp that
keeps those two mechanisms from skipping past a position where the EOL view
could accept. It is a *parameter of* rows 2 and 3, and it is load-bearing for
exactly the reason this section exists: under a class-indexed accept the bound
is no longer sufficient on its own, which is what rows 2-5's intersections
repair. Stated here rather than left out, because "the union of the two
enumerations is six" is a fair thing for a reader to notice.

**Mechanism 1 has no cheap cure, and it is gated by a flag that must change.**
Today the prefilter is disabled outright whenever the start state accepts:

```c
    bool start_acc = fd->st[fs].accept;                              /* :877 */
    ...
    bool prefilter = !start_acc && esc_count > 0 && esc_count < 256; /* :912 */
```

which is why `x*` emits no prefilter at all (measured: an emitted `x*` artifact
contains no `memchr` and no `first[]` walk). Under a class-indexed accept
`fd->st[fs].accept` is no longer a bool, so **`start_acc` must widen to
"accepts on ANY class"** — the OR over the state's accept row. If it instead
read one class's bit, a pattern whose start state accepts on *some* classes
would keep its prefilter and the memchr would jump straight past accepting
positions.

The concrete cell, MEASURED against libpcre2 through the §3.1 find-all loop:

```
\bx*   'a x'  ->  [(0, 0), (1, 1), (2, 3), (3, 3)]
```

`\bx*`'s start state accepts (an empty `x*` at a word boundary), and three of
those four matches are empty ones at positions a `memchr('x')` would jump over.
A `start_acc` that failed to widen would report only `(2,3)`.

**None of this may be assumed.** D11's own record is that the first attempt at
M2.12 got rule 1 right, still produced 53 divergences over 27 patterns x 69
subjects, and that a later unconditional reorder cost **43%** on this exact
pattern. **Wave C** therefore carries the differential sweep over `(?m)$`
patterns *with a live prefilter and skip states*, the widened `start_acc`, and
a sabotage row per intersected mechanism — each validated against a pattern
class that can actually make it fire.

### 3.6.2 The composition rule: the view axis × the class axis

**NEW AFTER R30 E6.** Two axes now select an accept bit and no section said how
they compose:

- the **VIEW** axis — `{base, eolvar, endvar}` (§3.3), selected by *position*;
- the **CLASS** axis — the byte at `pos` (§3.6), selected by *the next byte*.

The rule, and the case that forces it: **at `pos == n` there is no next byte, so
the accept bit is the view's SCALAR accept and is never class-indexed.**

```
accept_at(st, pos) =
    pos <  n  ->  acc_cls[ view(st, pos) ][ fcls[s[pos]] ]     /* class-indexed */
    pos == n  ->  acc    [ view(st, n)   ]                     /* SCALAR       */

where view(st, pos) = endvar(st)  if pos == n
                      eolvar(st)  if the EOL condition holds at pos
                      st          otherwise
```

This is not a tidiness point. `probe_acc_by_class.sh:33` papers over `pos == n`
by indexing with **class 0** — legal only because that probe's variant is
answer-preserving, so every class of a state carries the same bit and the choice
cannot show. **In the real design the classes differ**, and class 0 at `pos == n`
would be reading the accept bit for "the next byte is whatever byte happens to
sit in equivalence class 0", which is meaningless at end of subject. A
`\b`-terminated match at end of subject is exactly the case: out-of-subject
counts as non-word, which is a property of the *position*, not of any byte.

The probe's shortcut is disclosed in place rather than fixed, because fixing it
would change what the probe measures (it exists to price the lookup, not to be
the design). The **design** takes the rule above, and Wave B owes a structural
check that no emitted artifact indexes an accept table at `pos == n`.

### 3.7 `(?m)` — why `$` is easy and `^` is not

**`(?m)$`** is true at `pos == n` or when `s[pos] == '\n'`. Forward, that is a
next-byte view (§3.6), so it folds into the class-indexed accept and transition
tables. Reverse, the byte to the right of `pp` has already been consumed, so it
is a previous-byte context bit carried in the reverse state (§3.5's mechanism,
mirrored). Both machines are buildable with the machinery this module already
adds for `\b`, and `(?m)$` may stay on ENG_UNANCH.

Note the specific thing that *stops* working: today's view selection is guarded
by `__builtin_expect(pos + 1 >= n, 0)` (`src/gen/emit_dfa.c:1013`), which is why
the EOL view is free — it is consulted at the last two positions only. Under
`(?m)` there is no such guard to have, because `$` is true before *every*
newline. That is exactly why the view must move **into the class-indexed
tables** rather than stay a per-position branch, and §3.6 measures that move at
zero.

> **BUILT, [M6.2] WAVE C (2026-08-19, lane/asrtwavec) — WITH ONE STRUCTURAL
> CORRECTION THIS SECTION DOES NOT STATE.**
>
> The paragraph above is right that `(?m)$` folds into the class-indexed
> tables, and that is what shipped. What it leaves implicit is that the class
> axis wave B built is a **BOOL** — "the upcoming byte is a word character" —
> and `(?m)$` does not add a second bool beside it. Word-ness and
> newline-ness are properties of THE SAME BYTE, so the axis becomes a
> three-valued partition of the alphabet (`UPC_PLAIN` / `UPC_WORD` /
> `UPC_NL`, `src/core/internal.h`), disjoint and exhaustive because a newline
> is not a word character. A design that read this section as "add an
> `up_nl` beside `up_word`" would build four combinations where three exist,
> and would have to decide what the impossible fourth means.
>
> **`(?m)$` ALSO NEEDS THE `pos == n` VIEW, which this section does not
> mention.** Its truth is "end of subject OR the next byte is a newline", and
> the first half is a POSITION fact with no byte to ask about. So `N_EOL_M`
> reads `end_ok` — `\z`'s own closure bit, wave A's third view — plus the
> class axis, and a pure-`(?m)$` machine therefore has `endvar >= 0` and
> `eolvar == -1` everywhere. That combination had never occurred before (it
> is `emit_view_select`'s `has_end && !has_eol` arm, written for `\z` with no
> `$` anywhere) and it is exactly the right selector: only `pos == n` picks a
> view, and every other position's accept comes from the class axis.
>
> **AND THE REVERSE MACHINE READS THE OTHER SIDE.** `\b`'s test is symmetric
> in its two operands, so wave B's closure could name them by WALK order
> (consumed / upcoming) and let both machines share one expression. `(?m)$`
> is not symmetric: forward, the byte it reads is the one about to be
> consumed; reverse, it is the one already consumed. The closure therefore
> names its operands by SIDE (`left_*` / `right_*`, i.e. `s[pos-1]` and
> `s[pos]`) and exactly one function — `make_state`'s `reverse` mapping —
> knows a machine has a direction. That is the whole of the "mirrored"
> in this section's own reverse sentence, made concrete.

> **REFUTED BY [M6.2] WAVE C (2026-08-19), AND IT WAS A LIVE MISCOMPILE
> BEFORE IT WAS A DOCUMENTATION ERROR — READ THIS BEFORE THE SENTENCE BELOW.**
>
> `(?m)^` is **NOT** true at every position after a newline. PCRE2's
> pcre2pattern is explicit: under multiline, `^` "does not match after a
> newline that **ends the string**". So the rule is
>
>     pos == 0  ||  (pos < n && s[pos-1] == '\n')
>
> and `(?m)^` is **not** the mirror of `(?m)$`, which this section and §9.3
> both present it as. On `"a\n"`, `(?m)^` holds at 0 only; `(?m)$` holds at 1
> AND at 2.
>
> **python3 `re` implements the sentence below rather than PCRE2's rule**
> (docs/dev/upstream_issues.md U11b), which is why the error was invisible to
> the base-tier oracle and why every `(?m)`-with-`^` corpus block is now
> `# pcre2-only`. pcrec shipped the design's rule and was WRONG for it; the
> defect was found by `tests/assertions/run_mline_diff.sh` at `startpos > 0`,
> because from `startpos 0` an earlier match masks the trailing position on
> almost every subject. `(?m)^$` on `"a\n"` is the one shape that shows it
> from 0.
>
> In the closure the exclusion is `end_ok` — wave A's `pos == n` view, which
> `(?m)^` therefore consumes as well as `(?m)$` does, for the opposite
> purpose: `(?m)$` reads it to be TRUE at end of subject, `(?m)^` reads it to
> be FALSE there.
>
> **THE EVIDENCE WAS ALREADY IN THIS REPOSITORY**, which is the part worth
> keeping. `docs/pcre2_options.md`'s `PCRE2_ALT_CIRCUMFLEX` row — surveyed and
> RATIFIED under D38 on 2026-08-14, four days before this design was written
> — reads "under `MULTILINE`, `^` ALSO matches immediately after a final
> trailing newline", and an option whose whole content is turning that on is
> only meaningful if the default is off. That row and this section describe
> the same construct, disagree, and sat one document apart until a subject
> sweep at `startpos > 0` forced them together. A design lane that consulted
> the project's own option survey for the construct it was designing would
> have caught it before any code existed.

**`(?m)^`** is true at `pos == 0` or when `s[pos-1] == '\n'`. Forward that is a
previous-byte context bit — cheap, and it requires changing the one hardcoded
`false` in the worklist (`src/ir/dfa.c:692`) into "this byte class is the
newline class". But the **reverse** machine is the problem, and it is the same
problem D8 recorded for plain `^`:

> `^` (N_BOT) needs a position-dependent BOT variant in the REVERSE machine
> (checked at pp == 0), which the DFA does not build — so `^` patterns stay on
> ENG_ATTEMPT. (D8)

`(?m)^` needs **that variant AND a byte-selected view** on top of it. It needs
strictly more than plain `^`, not less.

**Proposed:** `(?m)^` routes to **ENG_ATTEMPT**. `nfa_has_bot()`
(`src/ir/nfa.c:668`) extends to "contains any BOT-family node". Under
ENG_ATTEMPT the start-state dispatch generalises from
`src/gen/emit_dfa.c:1113-1120`'s two-way `(start == 0) ? s0 : s1` to a
three-way test that also asks `s[start-1] == '\n'` — once per attempt, off the
inner loop (and see §3.8: at `start == startpos > 0` that byte is outside the
search window, which is mechanism 4).

#### 3.7.1 What that routing costs — STRUCK AND RE-MEASURED (R30 E2)

The first draft said a `(?m)^` pattern "inherits D8's known-slow shape and
nothing else changes". **That sentence is struck. It was false twice over**, and
the correction is the second HIGH finding of R30.

**False the first time:** plain `^` does *not* have a slow shape in the usual
case — a fully-`^`-anchored pattern takes M2.1's fast path, `d->s1 < 0`, and
`start_max` is the literal `0` (`src/gen/emit_dfa.c:1105-1108`). One attempt,
not `n+1`.

**False the second time:** `(?m)^` can **never** take that path. Its interior
start state is live *by definition* — that is what multiline `^` means — so
`d->s1 >= 0` and `start_max = n` always. And ENG_ATTEMPT emits **no prefilter
and no skip loops at all**, so those `n+1` attempts run with zero scan
avoidance.

**MEASURED** (`probes/probe_mline_caret_cost.sh`, `out/mline_caret_cost.txt`;
best of 5 per cell, 200 inner repeats; subject = lines of `'a'` separated by
`'\n'`, no `'b'`, so every enterable attempt runs to the end). **Pasted from
the archive rather than from a separate run — R30 N2 caught the first draft
quoting a different run than the file it cited:**

```
n        A (?m)^shape   B anchored     C unanch       A/B        A growth per doubling
4000     0.00077760     0.00000595     0.00000008     131x
8000     0.00121612     0.00000474     0.00000032     257x       1.56x
16000    0.00479799     0.00000943     0.00000062     509x       3.95x
32000    0.01903308     0.00004654     0.00000192     409x       3.97x
64000    0.07586102     0.00003767     0.00000267     2014x      3.99x
```

A is `^[^b]*b|\n[^b]*b` (the `(?m)^` engine shape), B is `^[^b]*b` (the anchored
twin), C is `[^b]*b` (ENG_UNANCH). **The load-bearing column is GROWTH, not the
ratio: 3.95x / 3.97x / 3.99x per doubling is the O(n²) signature.** C, which
keeps memchr and the skip loops, is flat and fastest throughout.

**Two honesty notes on this table**, both of which the first draft lacked:

- **The A/B column is NOISE-DOMINATED and is not the claim; GROWTH is the
  load-bearing column.** B and C sit at microseconds and tens of nanoseconds,
  where clock resolution and cache effects dominate, so A/B reads
  131x → 257x → 509x → 409x → 2014x rather than climbing monotonically.
  **Measured across runs, the n = 32,000 ratio moved from 1001x to 409x on B's
  jitter alone** — B's own time went 0.000019 to 0.00004654 while A barely
  moved — which is a factor-of-2.4 swing in a number nothing about the design
  changed. Quote the growth column (3.95x / 3.97x / 3.99x, stable across every
  run) and treat **2014x at n = 64,000** as "the largest separation observed",
  never as a measurement of the ratio.
- **The 8000-row growth of 1.56x is an outlier against the 3.9x trend**, and it
  is a small-n artifact rather than a result: at 4,000 and 8,000 bytes A's
  absolute time (0.8 ms, 1.2 ms) is still close enough to fixed overheads that
  the quadratic term has not dominated. The curve only settles from 16,000
  onward, which is why the three settled rows are the ones quoted as evidence.

**The probe's own first finding, disclosed because it nearly produced the
opposite conclusion:** an all-`'a'` subject with no newline measures *nothing*.
Every interior attempt dies on its first byte, A is O(n), and the curve is flat.
A draft of this probe used exactly that subject and **would have reported the
struck sentence as correct.** The quadratic requires the interior branch to be
*enterable*, which is precisely the subject a real `(?m)^` pattern runs on.

#### 3.7.2 The mitigation, and the case it is actually for

R30 supplied the mitigation and this design adopts it as a proposal: **a
`memchr('\n')` candidate-start prefilter in `emit_attempt`.** A `(?m)^`-anchored
attempt can only begin at offset 0 or immediately after a `'\n'`, so the attempt
loop does not need to visit every start — it can jump between newlines exactly
as ENG_UNANCH's prefilter jumps between first-set bytes.

**The first draft justified this on the WRONG arm — R30 N3.** It cited §3.7.1's
quadratic numbers, but a prefilter helps *least* there: the quadratic case's
cost is the scanning each attempt does, and skipping to line starts still leaves
each surviving attempt scanning to the end of the subject.

**The arm it actually helps is the LINEAR, non-crossing one — which is what most
real `(?m)^` patterns are.** `(?m)^ERROR` matches within a line; every attempt
dies in a byte or two; the shape is linear with a large constant, and that
constant is exactly what a candidate-start prefilter removes.

**MEASURED** (same probe, non-crossing arm; `out/mline_caret_cost.txt`):

```
n        D (?m)^ERROR   E unanch       D/E ratio
8000     0.00002458     0.00000028     88x
32000    0.00009803     0.00000115     85x
128000   0.00039255     0.00000212     185x
```

D is `^ERROR|\nERROR` (the `(?m)^ERROR` engine shape), E is `ERROR` on
ENG_UNANCH. **Both are linear — the D/E gap is a constant factor of roughly
85-185x, not a curve** — and that factor is the mitigation's target: it is the
difference between visiting every offset and visiting every line start, which is
the same jump E already gets from its own first-byte memchr.

**This arm's own instrument defect, promoted here because it would have
fabricated the number Q3(b) rests on.** E is a single `memchr` and is below this
clock's resolution at one search, so the driver times 200 inner repeats — and
gcc -O2 **deleted all but the last iteration**, the return value being otherwise
dead. E measured `0.000000` over 200 searches and the D/E column printed `n/a`
and then a meaningless `580x`. A `volatile` sink fixes it, and the driver says
so at the site. The near-miss is the same shape as §3.7.1's all-`'a'` subject:
in both cases a plausible-looking instrument returned a number that would have
been quoted, and in both cases the tell was a value too good to be true rather
than an error. This one is the more dangerous of the two, because an
*infinite* ratio reads as a stronger result for the mitigation, not a weaker
one — the direction a reviewer is least likely to challenge.

**Proposed as a design element with a stated fallback**: if Wave C measures the
prefilter as not worth its complexity, `(?m)^` still ships — routed to
ENG_ATTEMPT, with both curves above recorded in the plan row rather than
discovered by a user. What is NOT acceptable is the first draft's position:
shipping the routing while describing its cost as "nothing else changes".

> **BUILT, [M6.2] WAVE C (2026-08-19, lane/asrtwavec) — AND THE CANDIDATE SET
> IS NOT WHAT THIS SECTION SAYS IT IS.**
>
> The sentence "a `(?m)^`-anchored attempt can only begin at offset 0 or
> immediately after a `'\n'`" is **true of a FULLY-`(?m)^`-anchored pattern
> and false of the general case**, and `nfa_has_bot` routes ANY pattern
> containing a BOT-family node to this engine — `(?m)^a|b` included, where the
> `b` branch can begin anywhere. Implementing the sentence literally loses
> that branch's matches entirely; it is the sabotage row S81 precisely because
> it is the reading this text invites.
>
> **What shipped derives the candidate set from WHICH SEEDED START STATES ARE
> LIVE**: an attempt at `start > 0` enters `s1u[upc_of_class(s[start-1])]`, so
> a predecessor byte whose seeded state is DEAD cannot begin a match, and only
> those bytes are candidates. For `(?m)^ERROR` only the `UPC_NL` seed is live,
> the set is the newline definition, and the derivation picks `memchr` — the
> same artifact the sentence describes. For `(?m)^a|b` every seed is live, the
> set is all 256, `cand_derive` reports it unusable, and **no prefilter is
> emitted at all**, which is correct rather than merely safe.
>
> The generalization costs nothing and buys D63's other two named instances
> for free: D8's `^`-on-some-branches shape and partial `\G` are the same
> question about the same seed row, so they become CALLERS of
> `cand_from_live_seeds` rather than new derivations. That is the "tool, not a
> one-off" half of D63's charter discharged by construction rather than by
> intention.

#### 3.7.3 The [DD-7] question this reopens

Building the reverse BOT variant would let both plain `^` and `(?m)^` join
ENG_UNANCH and delete this whole section. That is [DD-7]'s parked item, and this
design still does not unpark it — but the argument for parking it has weakened
in a way worth putting to Frank rather than deciding here. When the row was
parked, `^` on some branches was one known-slow shape. With `(?m)^`, the slow
shape becomes the *normal* case for a common construct, at a measured 1996x.
**Q3 (§11) is reframed on this footing**, and R30 marks whether it unparks
[DD-7] as Frank's ruling once the framing exists.

---

### 3.8 Mechanism 4 — seeding assertion context from outside the search window

**NEW SECTION, R30 E1.** The first draft had no mechanism for this at all, and
called its inventory exhaustive. This is the correction.

#### 3.8.1 The problem, measured

`<prefix>_search(s, n, startpos, caps)` searches `s[startpos, n)`. But `\b`,
`\B` and `(?m)^` at position `startpos` depend on `s[startpos-1]` — a byte in
the subject and *outside the window*. Symmetrically, a trailing `\b` at the
match end depends on `s[end]`, a byte the reverse walk never consumes.

Neither engine has a mechanism. Both start states are compile-time constants:

```c
    sb_printf(c, "    int st = %d;\n", fs);        /* emit_dfa.c:946  forward */
    sb_printf(c, "        int rst = %d;\n", rs);   /* emit_dfa.c:1029 reverse */
```

A constant start state encodes exactly one assumption — "the context here is
start-of-subject" — which is the assumption a *slice* makes.

**MEASURED** (`probes/probe_startpos_context.py`, `out/startpos_context.txt`,
libpcre2 10.46). "whole@spos" is searching `s` from `startpos`; "slice@0" is
searching `s[startpos:]` from 0, rebased. **5 of 10 cells differ:**

```
pattern   subject     spos whole@spos  slice@0     verdict
\bfoo     'xfoo'      1    None        (1, 4)      *** DIFFER ***
\bfoo     ' foo'      1    (1, 4)      (1, 4)      same
\Bfoo     'xfoo'      1    (1, 4)      None        *** DIFFER ***
\Bfoo     ' foo'      1    None        None        same
foo\b     'foox'      0    None        None        same
foo\b     'foo '      0    (0, 3)      (0, 3)      same
(?m)^b    'ab\nb'     1    (3, 4)      (1, 2)      *** DIFFER ***
(?m)^b    'ab\nb'     3    (3, 4)      (3, 4)      same
\bfoo     'xfoo foo'  1    (5, 8)      (1, 4)      *** DIFFER ***
\Afoo     'xfoo'      1    None        (1, 4)      *** DIFFER ***
```

The sharpest cell is `\bfoo` on `"xfoo foo"` at `startpos 1`: a context-blind
engine does not merely over-match, it **reports the wrong occurrence** — `(1,4)`
where the answer is `(5,8)`. The `\B` row differs in the *opposite* direction
(no match where PCRE2 matches), so neither a conservative nor a permissive
shortcut is available.

The `\Afoo` row is included to **bound** the claim rather than support it: `\A`
differs under slicing too, but pcrec never slices — it passes `startpos`, and
`\A`/`^` route to ENG_ATTEMPT whose start state is *already* chosen at runtime
by `start == 0` (`emit_dfa.c:1113-1120`). Mechanism 4 is needed for the context
assertions, not for that one.

**Through the find-all loop**, which is where this reaches an ordinary consumer
because §3.1's loop passes its resume position as `startpos`:

```
  \Bfoo    'xfoofoo'    true [(1, 4), (4, 7)]   context-blind [(1, 4)]   *** DIFFER ***
  \Boo     'foofoofoo'  true [(1, 3), (4, 6), (7, 9)]   context-blind: same
  \bfoo    'foo xfoo foo'  CONTROL: every resume lands at a boundary — same
```

A **lost match**, not a shifted one. The control row is in the probe
deliberately: a find-all suite whose resume positions all land at word
boundaries reports "same" everywhere and proves nothing — which is what this
probe's own first draft did.

#### 3.8.2 The mechanism, forward

**Proposed.** The forward start state stops being a constant and becomes a
once-per-search dispatch on the seed byte's equivalence class:

```c
    /* today */            int st = FS;
    /* proposed */         int st = startpos ? FS_ctx[fcls[s[startpos - 1]]] : FS_bot;
```

Three properties make this cheap and safe:

- **It runs once per search, not once per byte.** It is not in the loop; the
  emitted hot path is unchanged.
- **`FS_ctx[]` is `ncls` entries wide**, not 256 — the seed only has to
  distinguish classes, and §3.4 already guarantees the word set and the newline
  set are unions of classes. Most entries collide, so the table is small.
- **It is the same shape §3.7 already proposes** for ENG_ATTEMPT's three-way
  start dispatch, and the same shape `s0`/`s1` has had since M2.1. This is a
  generalisation of existing machinery, not a new kind of thing.

`FS_bot` is the existing `fs`: at `startpos == 0` the context is genuinely
start-of-subject, which is what the constant already encodes.

**On ENG_ATTEMPT this is not once per search.** That engine re-initializes at
every attempt — `n+1` of them (§3.7.1) — and only the FIRST is at `startpos`;
the rest begin at `start > startpos`, where the seed byte is `s[start-1]`, a
byte squarely inside the window. So the dispatch is per-attempt there rather
than per-search, which is the same `once per attempt, off the inner loop` cost
§3.7 already describes for its three-way start selection, and it composes with
that dispatch rather than adding a second one. The `n+1`-attempts problem is
§3.7's territory, not this section's.

#### 3.8.3 The mechanism, reverse — and it is the harder half

**Mechanism 4 is needed at FOUR boundaries, not two.** Each machine has an
initialization boundary and a termination boundary, and the first draft of this
section covered only the two initialization ones. R30's focused re-check (N1)
found the gap:

| machine | boundary | context byte needed | in the window? | covered by |
|---|---|---|---|---|
| forward | init, `pos = startpos` | `s[startpos-1]` | **no** | §3.8.2 — mechanism 4 |
| forward | term, `pos = n` | *none exists* | n/a | §3.6.2's SCALAR rule |
| reverse | init, `pp = end` | `s[end]` | in the subject, **never consumed** | below — mechanism 4 |
| reverse | term, `pp = startpos` | `s[startpos-1]` | **no** | **§3.8.3.1 — the gap** |

##### The initialization half

The reverse walk starts at `pp = end` and consumes leftward, so the byte that
seeds a **trailing** `\b`'s context is `s[end]` — one to the *right* of where
the walk begins, and never consumed by it. The mirror of §3.8.2:

```c
    /* today */            int rst = RS;
    /* proposed */         int rst = (end < n) ? RS_ctx[rcls[s[end]]] : RS_eos;
```

with `RS_eos` the out-of-subject seed (non-word for `\b`'s purposes, and the
same position `\z`/`\Z` reason about).

**This is the half that is least certain, and §12 carries it as BELIEVED.**
Two reasons to attack it first in Wave B:

1. The reverse DFA is built with `prune=false` (`src/core/compile.c:219`)
   because it must keep every thread alive to find the earliest accepting
   position. Seeding its start state by context interacts with that in a way no
   measurement here covers.
2. `end` is not a fixed value: the forward pass produces it. So the reverse
   seed is data-dependent in a way the forward seed is not, and the emitted
   code must read `s[end]` *after* the forward loop — a site that does not exist
   today.

##### 3.8.3.1 The TERMINATION half — a LOST MATCH the first draft would have shipped

**R30 N1, and it is a real defect in this design rather than in the prose.**

The reverse loop evaluates its accept and *then* tests for termination
(`src/gen/emit_dfa.c`):

```c
1032:   if (rx_racc[rst]) sfound = pp;          /* non-EOL accept        */
1054:   if (rx_racc[erst]) sfound = pp;         /* EOL accept            */
1056:   if (pp <= startpos) break;              /* EXIT 1: the boundary  */
1057:   rst = rx_rtr[... rx_rcls[s[--pp]]];     /* consume leftward      */
1059:   if (rst < 0) break;                     /* EXIT 2: dead state    */
```

So at `pp == startpos` the accept **is** evaluated, and the loop breaks before
`s[startpos-1]` is ever read. A **leading** `\b`/`\B` at the match start is
therefore evaluated with no left context at all — the walk assumes
start-of-subject.

**`\b` is safe by accident, and that is why a trailing-only sweep cannot see
this.** `\b`'s blind assumption (prev is non-word) happens to coincide with the
cases the forward pass lets through, so nothing diverges. **`\B` inverts it**,
and this document's own §3.8.1 cell is the counterexample:

> `\Bfoo` on `"xfoo"` at `startpos 1` → PCRE2 gives **(1,4)**.
>
> The forward pass, correctly seeded per §3.8.2, finds `last = 4`. The reverse
> walk runs back to `pp == 1 == startpos`, where accepting requires `\B`:
> `s[0] = 'x'` (word) and `s[1] = 'f'` (word), so `\B` holds and `sfound` should
> become 1. Blind, the walk assumes `s[0]` is start-of-subject (non-word), `\B`
> fails, `sfound` stays `-1`, and `<prefix>_search` returns **0**.
>
> **A LOST MATCH** — and one this design's own forward fix makes *reachable*,
> because before §3.8.2 the forward pass never found the match to begin with.

**Proposed: a boundary view at `pp == startpos`, seeded from `s[startpos-1]`.**
The mirror of §3.8.2, applied at the other end of the same walk:

```c
    /* the terminal position's accept is CONTEXT-INDEXED, not the plain row */
    rcls_t seed = startpos ? rx_rcls[s[startpos - 1]] : RX_CLS_BOT;
    if (rx_racc_ctx[rst * RX_NRCLS + seed]) sfound = startpos;
```

**Emit it ATTACHED TO THE BOUNDARY BREAK, not after the loop** — and the
distinction is load-bearing, because the obvious placement is wrong:

```c
    if (pp <= startpos) { <context-indexed accept>; break; }   /* correct */
```

`pp == startpos` happens exactly once, and the loop already tests for it at
`:1056`, so this costs one emitted site and **zero per-byte work** — putting the
test inside the loop body would add a compare to every byte of the reverse walk.

**Why not "after the loop" (R30 N9).** An earlier draft of this section said
"peeled epilogue … below that break", which reads as *after the loop*. The loop
has **two** exits, and the excerpt above now quotes both. On `:1059`'s dead-state
exit, `pp > startpos` and `rst < 0`, so an epilogue placed after the loop would:

- write `sfound = startpos` at a position **the walk never reached** — a wrong
  answer rather than a lost match, which is the worse failure of the two; and
- index `rx_racc_ctx[rst * RX_NRCLS + seed]` with a **negative `rst`** — an
  out-of-bounds read in emitted code, which is **K27's exact class**: a
  generated matcher whose UB carries pcrec's name into a user's sanitizer run.

Attaching the accept to the boundary break makes both unreachable by
construction, because that arm is only entered when `pp <= startpos` and `rst`
is a live state.

**The subtlety that makes this more than a one-line fix**, and it is the reason
this note states an invariant rather than a patch: the reverse **skip** can also
land on the boundary. `:1042-1044` reads

```c
    while (pp > startpos && rx_rs<K>[s[pp - 1]]) pp--;
    sfound = pp;                    /* NO runtime guard -- see below */
```

and that `sfound = pp` is equally blind when the skip stops exactly at
`startpos`. **It is worse than a first reading suggests**, and worth spelling
out: the emitter's `if (!eol && rd->st[K].accept)` at `:1043` is a
**compile-time** condition on whether to *emit* the line. What lands in the
artifact is a **bare, unconditional** `sfound = pp;` inside the skip block — so
on any pattern where that block is emitted, every skip that stops at `startpos`
writes a blind `sfound`, with no runtime test to fail. So the rule has to cover
every writer, not just the one at `:1032`:

> **INVARIANT: no `sfound` may be recorded at `pp == startpos` except through
> the context-indexed accept.** Wave B owes a structural check for this — it is
> checkable by reading the emitted text, which is the same instrument class as
> §3.6.2's "never index an accept at `pos == n`".

Note the pleasing symmetry with §3.6.2, and the difference: the forward
machine's termination boundary needs a **scalar** accept because no byte exists
past `n`; the reverse machine's termination boundary needs a **context-indexed**
one because the byte exists and is merely outside the window. Two boundaries
that look alike and take opposite fixes.

#### 3.8.4 Why this does not reopen the D58 residue question

`s[startpos-1]` and `s[end]` are **byte reads at computed offsets**, not
character-boundary questions, so mechanism 4 adds no encoding residue (§7). Under
a UTF-8 backend the *seed classification* is the same front-end-lowered word-set
question §7.2 already answers; what changes is only which lowered automaton the
class map came from. The seed itself is `s[k]` for an integer `k`, in both
backends.

---

## 4. (ii) DD-4 — `\G` against the startpos contract

**PCRE2's semantics**, and the shipped registry already states them
(`src/parse/registry.c:364`): `\G` is "first matching position in the subject",
i.e. it asserts that the current position equals the `start_offset` the match
call was given.

**pcrec's contract makes this direct.** `<prefix>_search(s, n, startpos, caps)`
(`docs/spec/match_api.md` §3.1) takes `startpos` as a parameter, so `\G` is
exactly `pos == startpos`. It is an **absolute position test** of a runtime
value — not a compile-time constant like `\A`'s `pos == 0`, but equally free.

### 4.1 §7.3's structural finding does not block this, and the toggle is not needed

`engine_m4.md` §7.3 records, confirmed STRUCTURAL, that
`nfa_wrap_unanchored` bakes the self-loop into the NFA in place with no way to
recover the anchored machine, and concludes that "`\G` wants the unanchored
engine's SHAPE without the self-loop, which is a toggle on the wrap".

> **Cite note.** §7.3 locates `nfa_wrap_unanchored` at `src/ir/nfa.c:590`, and
> this document repeated that line verbatim in §3.5 and in
> `probe_wordctx_states.py` without re-deriving it. **It is stale**: the
> function is at **`:652`** today, and `:590` is now inside the K7
> bounded-repeat fix, unrelated code. Corrected here; `engine_m4.md` is not
> this lane's to edit, so the stale cite there joins the M3 list of
> manager-at-merge items. This is the carried-forward-comment failure the R20
> checkpoint already named, and it reached this document because a cite copied
> from a trusted sibling doc was not re-run against the file.

**This design does not need the toggle**, and that is the substantive DD-4
answer. pcrec already emits an un-self-looped machine: ENG_ATTEMPT is a
per-start attempt loop over an *anchored* DFA
(`src/gen/emit_dfa.c:1108`):

```c
    size_t start;
    const size_t start_max = n;             /* or "0 /* fully ^-anchored */" */
    for (start = startpos; start <= start_max; start++) {
```

`start_max` is already emitted as one of two compile-time strings, and the
`0` case is the existing fully-`^`-anchored fast path (M2.1). **A `\G`-anchored
pattern is the same shape with a third value: `start_max = startpos`** — one
attempt, at exactly the position `\G` names. No new engine, no wrap toggle, and
no loss: a pattern anchored to a single start position is O(n) trivially.

### 4.2 `\G` in only some branches

`\Gfoo|bar` is not anchored — `bar` must still be searched for. This is the
`bot_ok` pattern exactly: `\G` is satisfiable only at `pos == start == startpos`,
i.e. only at the *first* position of the *one* attempt whose `start ==
startpos`, and never after consuming a byte (the worklist already passes
assertion context `false` for successors). So `\G` is a **start-state property**,
resolved by generalising the start-state dispatch:

| `start == 0` | `start == startpos` | which assertions pass |
|---|---|---|
| yes | yes (`startpos == 0`) | `\A` and `\G` |
| yes | no | impossible |
| no | yes | `\G` only |
| no | no | neither |

Three reachable start states instead of two, each interned only if it differs —
the same pay-only-when-it-differs rule as `eolvar`. Mid-pattern `\G` (`a\Gb`)
falls out correctly with no special case: after consuming `a`, `pos > startpos`,
the assertion never passes, and the branch dies in the closure.

### 4.3 What `\G` means in the find-all loop — the DD-4 half worth writing down

`docs/spec/match_api.md` §3.1's find-all loop passes its resume position as
`startpos`:

```c
    int r = <prefix>_search(s, n, p, caps);
```

So under that loop, **`\G` means "contiguous with the previous match"**, which is
precisely PCRE2's global-iteration semantics (where each `pcre2_match` call
advances `start_offset`). The two agree with no work, because pcrec's search
entry already threads the parameter PCRE2 threads.

**Proposed:** `match_api.md` §3.1 gains one sentence saying so, when `\G` lands.
Without it a reader has to derive the correspondence, and it is the sort of
thing that is obvious to whoever writes `\G` and to nobody afterwards.

---

## 5. (iii) DD-11 — which newline convention `(?m)` and `\Z` bind to

### 5.1 The answer

**They bind to the PATTERN's newline convention, which is LF today and is
ANCHORED, not assumed** — DD-11's own row records why: every oracle measurement
runs libpcre2 at `options=0`, so `pcrec_cls_newline`'s bitmap is measured, `.`
is every-byte-but-`0x0A`, and `$` is before-final-`\n`; a convention change on
either side fails PC-4 and the census probe loudly.

**This is a different axis from D58's encoding axis and the two must not be
conflated.** Encoding answers "how many bytes is a character"; newline answers
"which byte sequence ends a line". `\Z`, `$`, `(?m)^`, `(?m)$` and `.` bind to
the newline axis; **none of them binds to the encoding axis** (§7). Under
UTF-8, U+000A is still one self-synchronising byte, so `\Z`'s test
`pos + 1 == n && s[pos] == '\n'` is unchanged. Under a **CRLF** convention it is
not — it becomes a two-byte sequence — and DD-11's row already predicts exactly
that as the engine work.

### 5.2 Where the axis should be declared — an OPEN QUESTION, not a recommendation

**REWRITTEN AFTER R30 M5. The first draft's recommendation here is WITHDRAWN**,
and the re-check (M5 PARTIAL) caught that the withdrawal had been applied at
§11 Q1 while this section still carried the superseded argument verbatim — a
live internal contradiction at the section a skimming reader stops at. That is
the same stale-as-current-fact failure this document catalogues elsewhere,
committed inside the fix for it.

DD-11 says decide "with the assertions module or a real consumer, whichever asks
first". `(?m)` is the first real consumer of the newline *concept* beyond `$`,
so this module is where the ask lands. **What this note now says about it is:
the ask lands here, and the answer needs a measurement this lane did not take.**

**What was withdrawn, and why** (full argument at §11 Q1):

- ~~"Recommended: declare the namespace now, ship one member, refuse the rest
  by their own names — the `--encoding` shape, exactly."~~
- ~~"This is not an *optimisation* axis (D18's subject) but a *semantic
  namespace*, which is the `--encoding` case rather than the OS-1..OS-4
  case."~~

The exemption is unsound on D18's own worked example: **D23 ran the
earn-its-axis test on case-folding — a semantic dimension — and it FAILED into
the parser.** "Semantic" is not a category D18 exempts. And the `--encoding`
comparison cuts the other way too: encoding was justified by a **committed
second customer** (M5 is the next milestone), which newline does not have.

**What survives, because it is description rather than recommendation.** If the
axis is ever declared, the `--encoding` machinery is the right *shape* for it —
a per-pattern scalar (`pcrec_options` field + `--newline=NAME`, never global),
one table listing `lf`/`cr`/`crlf`/`anycrlf`/`any`/`nul` with only `lf`
implemented, the rest refused BY THEIR OWN NAMES with the rendered menu
([SR-10]'s single-namespace rule), and the `(*CR)`-family verbs mapped onto that
same table so there is one namespace rather than two. **That is what the axis
would look like, not an argument that it should exist.**

**The open question, and the measurement it needs: §11 Q1.** The honest test is
D23's — hardwire LF, try to express the other five conventions in the front end,
and see which way it fails. DD-11's own row predicts the split (`.`/`\N` fold
like OS-1's caseless; `$`, `\Z` and `(?m)`'s anchors do not fold for
CR/ANYCRLF, which are set-valued, or CRLF, which is a two-byte sequence in both
DFAs). If that prediction holds, the axis earns itself on the engine half and
folds on the class half — a better answer than either "declare it" or "defer
it", and one nobody has yet measured.

---

## 6. (iv) `\K` against the match-start contract and the reverse pass

### 6.1 Why pcrec's DFA cannot do it — and why that is a choice, not a theorem

`\K` resets the *reported* start of the match to the position where `\K` was
passed **on the winning path**. The DFA derives match start by a reverse walk
that finds the *earliest accepting position* (`src/gen/emit_dfa.c:1024-1063`;
`prune=false` for the reverse DFA precisely "so the reverse scan must keep every
thread alive to find the EARLIEST accepting position", `src/ir/dfa.c:6-9`), then
writes it:

```c
        if (sfound == (size_t)-1) return 0;
        if (caps) { caps[0][0] = (ptrdiff_t)sfound; caps[0][1] = (ptrdiff_t)end; }
```

`\K`'s position is not "the earliest position from which the whole pattern
matches" — it is "where the winning path crossed the `\K`". Subset construction
erases exactly that.

**WORDING CORRECTED — R30 E7.** The first draft said the DFA "structurally
cannot" do this and argued from ambiguity: "for `A\KB` with an ambiguous
`A`/`B` boundary there is no unique answer to recover". **That argument is
wrong.** PCRE2's leftmost-first preference is a *total* order, so the answer is
always unique — R30 measured six cells including this document's own
ambiguous-boundary shape. Ambiguity is not the obstruction.

**The real obstruction, stated correctly:** the `\K` position is not a function
of the subset state. pcrec's DFA state is a priority-ordered set of NFA states;
the crossing position is a property of the *path*, and the state does not carry
it.

**And that is a property of THIS DFA, not of DFAs.** Tagged DFAs (Laurikari's
construction and its descendants) recover exactly such positions by attaching
registers to transitions. So the honest sentence is:

> **pcrec's DFA is not a tagged DFA, and this design does not propose making it
> one.** `\K` is therefore VM-only *in pcrec*.

The conclusion is unchanged and the shipped registry already agrees
(`src/parse/registry.c:365`, `VM_ONLY`). What changes is that the door is
recorded as **closed by choice rather than by mathematics** — R30's point being
that "structurally cannot" is the kind of sentence a later lane cites to avoid
re-opening a question that was never actually settled. Tagging the DFA would be
a large change with its own costs (registers on every transition, a second
minimisation story); it is not proposed here, and it is not refuted here either.

### 6.2 How it lands

`src/opt/select_engine.c:74-82` is a socket with, by its own comment, "exactly
one row" (`forces_captures()`), and `engine_m4.md` §5.2 designed it for
customers that did not exist. `\K` is the second row: a pattern containing `\K`
forces `ENGM_VM`. In the VM the construct is one line — `caps[0][0] = pos`,
trailed like any other capture write (`src/gen/emit_vm.c` §3.2's write-and-undo
discipline), because `\K` inside a quantifier must be undone on backtrack
exactly as a group start is.

### 6.3 The hybrid interaction, which is the part that can silently break

**STRUCTURAL and load-bearing.** The default path for a capture-bearing pattern
is the DFA *prefilter* plus the VM (`engine_m4.md` §6): the DFA derives the span
and the VM derives the captures. With `\K`, the DFA's span start is the
**pre-`\K`** start and the VM's `caps[0][0]` is the **post-`\K`** start. These
disagree by design.

**Proposed rules, both testable:**

1. On a `\K` pattern, `caps[0][0]` comes from the VM alone; the prefilter's
   start is used only to bound the search, never written out. A structural check
   in `tests/codegen/` asserts no emitted `\K` artifact writes `caps[0][0]` from
   the reverse pass.
2. `--engine=dfa` **refuses** a `\K` pattern rather than silently downgrading —
   the D44.6 precedent, where `--engine=dfa` refuses a captures-default pattern,
   and the CLI's own stated rule that "a request the pattern cannot honour is
   REFUSED, never silently downgraded".

**3. The match-here entry needs its own rule — R30 E8, and this is the live
hazard the first draft missed entirely.**

The emitted `rx_match` is not a separate engine; it is `rx_search` plus a
start-equality filter, quoted verbatim from an emitted artifact:

```c
ptrdiff_t rx_match(const rx_ctx *ctx)
{
    ptrdiff_t caps[RX_NCAPS][2];
    int found = rx_search(ctx->subject, ctx->len, ctx->pos, caps);
    if (found < 0) return (ptrdiff_t)found;
    if (found != 1 || (size_t)caps[0][0] != ctx->pos) return -1;
    return caps[0][1] - caps[0][0];
}
```

Both lines break under `\K`:

- **the filter** `caps[0][0] != ctx->pos` compares against the **post-`\K`**
  start, so a genuine anchored match is **rejected**. `a\Kb` at `pos == 0`
  returns `-1` where PCRE2 matches `(1,2)`.
- **the return value** `caps[0][1] - caps[0][0]` is the **post-`\K` length**,
  not the length consumed from `ctx->pos`. A D38 callout uses that return as
  its advance, so a `\K` pattern used as a callout would advance by the wrong
  amount — silently.

**Proposed rule:** on a `\K` pattern the match-here entry must filter on the
**pre-`\K`** start and return the **consumed** length, which means the VM has to
report both positions rather than overwrite one. The cheapest form is for the VM
to keep the pre-`\K` start in a slot the entry can read; the alternative
(refusing `\K` on the match-here entries) is worse, because F1/F2 make the
match-here export unconditional.

**Wave E owes tests on both entries**, not just on `<prefix>_search` (§10).

A fourth consequence for the spec: `\K` makes "the reported start is where
matching began" false. It is where *reporting* begins. PCRE2 has the same
property and the same warning.

---

## 7. (v) D58 residue enumeration

D58's genuine coupling is "the enumerable RESIDUE", and the [M6.0] row names
"word-character classification for `\b`" as one item. This section answers per
construct, and the headline answer is deliberately unflattering to the
expectation:

> **No construct in module `assertions` introduces a new residual entry under
> the byte backend, and none should.** The one encoding-sensitive item —
> `\b`'s word-character classification — is a **front-end lowering** question,
> not a runtime-identity question, and routing it through `src/gen/enc/` would
> put encoding-dependent code in the hot path, which DD-12 (7) forbids.

### 7.1 The enumeration

| construct | encoding-sensitive residue? | where it is resolved | seam entry |
|---|---|---|---|
| `\A` | **none** — `pos == 0`, an integer compare | engine | — |
| `\z` | **none** — `pos == n`, an integer compare | engine | — |
| `\Z` | **none** — `\n` is one self-synchronising byte in both backends | engine | — |
| `(?m)^` `(?m)$` | **none** (encoding); binds to the NEWLINE axis instead (§5) | engine | — |
| `\G` | **none** — `pos == startpos`, an integer compare | engine | — |
| `\K` | **none** — `caps[0][0] = pos`, an integer store | VM | — |
| `\b` `\B` | **YES — word-character classification is a CHARACTER question** | **front-end lowering** (§7.2) | none, by design |

### 7.2 Why `\b`'s residue belongs to the front end and not to the seam

Three independent arguments, and the panel should attack all three:

1. **D58's own architecture statement says so.** "UTF-8 is lowered INTO the byte
   automaton upstream of the engine split, and engines stay encoding-blind." A
   word character under UTF-8 is a multi-byte sequence; deciding whether the
   previous *character* was a word character is decided by the automaton that
   consumed it. That is lowering, not a runtime call.
2. **DD-12 (7) forbids the alternative.** A residual entry is "caller-facing
   residue, not hot-path code" (`enc_byte.c`'s own contract comment), and
   `tests/codegen/run_codegen_tests.sh`'s `[M5-SEAM/DD-12(7)]` check reads every
   emitted engine body for a residual reference, sabotage-validated by
   `S68_residual_in_hot_loop.sh`. A `\b` test calling `<prefix>_is_word_before()`
   from the DFA transition path or the VM body would **trip that check** — which
   is the check working, not a check to route around.
3. **pcrec already has the front-end answer and `\b` must reuse it, not copy
   it.** `\w` compiles today under module `classes` from
   `pcrec_cls_word_esc[32]` (`src/parse/cls_bits.inc:19`), oracle-generated
   against libpcre2 and re-measured by PC-4 every run. **Whatever `\w` means,
   `\b` must agree with**, and the only way to guarantee that is one definition
   with two readers. A second word-set spelling anywhere is this project's
   recorded check-design failure in its purest form.

> **BUILT AS STATED BY [M6.2] WAVE B (2026-08-19, lane/asrtwaveb) — AND THE
> POINT WAS CONTESTED BEFORE IT WAS SETTLED, WHICH IS WHY THIS NOTE EXISTS.**
> The wave brief instructed the lane to route word-character classification
> through a `src/gen/enc/` residual entry, restating [M6.0]'s general D58
> obligation without consulting this section's per-construct answer. The lane
> stopped on the item rather than improvising, and the manager ruled in the
> DESIGN's favour: item 2 above is not merely an argument but a shipping
> check, so the brief's instruction would have tripped `[M5-SEAM/DD-12(7)]`
> rather than satisfied D58. Shipped: one `pcrec_cls_word_esc`, refining the
> DFA's byte equivalence classes (`src/ir/dfa.c`'s `eqclasses`) and interned
> by the VM's own class pool (`src/gen/emit_vm.c`), so `\b` and `\w` are one
> definition with two readers. No residual entry; the enumeration in §7.1 is
> unchanged. Item 3 is now checked rather than argued —
> `run_codegen_tests.sh`'s `[M6.2-WORDB rule 3]`, whose failing direction is
> sabotage S75, and whose own first two formulations were measured BLIND
> before the third worked (see that check's comment).

### 7.3 What the UTF-8 backend will need — stated concretely, as the charter asks

Under the byte backend `\b` is: refine the class map by
`pcrec_cls_word_esc`, carry one bit in the DFA state, and in the VM read one
256-entry table the front end emitted. Under UTF-8, three things change and
**none of them is a residual entry**:

- The word set becomes a **character** set (a UTF-8 word character includes
  non-ASCII letters once `\p{...}`/UCP lands at M5), which lowers into the byte
  automaton as a byte-sequence fragment — the same lowering `\w` itself will
  need. `\b` inherits it for free *if and only if* §7.2 item 3 holds.
- The DFA context bit becomes "the last *character* completed was a word
  character", which is still determined by the transition taken, because the
  lowered automaton is the thing consuming the continuation bytes.
- **The VM's `\b` test is the one that needs real work**: it is a position test
  that must look at the character *ending* at `pos`, i.e. a bounded backward
  scan of at most 3 continuation bytes using UTF-8 self-synchronisation. This is
  the same back-step DD-12 already enumerates for lookbehind. It is hot-path
  code, so it must be emitted from a **front-end-supplied** table/fragment, not
  called through the seam.

**BELIEVED, and §12 carries its refutation:** that the VM's `\b` can be served by
a front-end-emitted fragment without an encoding conditional in shared emitter
code. If it cannot, that is the DD-12 (7) design-stop signal, not a patch — and
it should surface at M5, not be discovered inside a `\b` lane.

### 7.4 A residue this lane found that is NOT an assertion's — reported, not owned

**STRUCTURAL.** D58's rationale says "the hot path has NO external advance loop
to rewrite — unanchoredness is the automaton's state-0 self-loop plus the memchr
skip". That is true of **ENG_UNANCH**. **ENG_ATTEMPT has one**
(`src/gen/emit_dfa.c:1108`):

```c
    for (start = startpos; start <= start_max; start++) {
```

`start++` is byte arithmetic in shared emitter code, and it is in a hot loop —
so it cannot be routed through `<prefix>_next_pos` without tripping the S68
structural check. It exists today and is not created by this module, but this
module makes it **more prominent**, because `(?m)^` and `\G` both route patterns
onto ENG_ATTEMPT (§3.7, §4).

**BELIEVED:** under UTF-8 this is a performance issue and not a correctness one
— a lowered UTF-8 automaton accepts only well-formed sequences, so an attempt
begun at a continuation byte dies immediately rather than matching. The
refutation experiment is in §12. Either way this belongs to [DD-12]/M5's ledger,
not to [M6.2]; it is recorded here because this lane is where it was noticed.

---

## 8. (vi) The D47.5 gate for `(?m)`

### 8.1 The gate already ships — and it is UNSOUND under scoped `(?m)`

This is the most important finding in the document, and it is **STRUCTURAL**.

D47 ruling 5 requires that `eng_brep_design.md` §2.5's `$`-follow
possessification exemption "consults the multiline option bit at verdict time (a
real branch, not a comment)". That branch is built and shipping
(`src/opt/possessify.c:167-178`):

```c
    case A_EOL:
        /* D47.5's LIVE GATE. Transparent while `$` means "the subject end (or
         * before a final newline)" — a set no retreat can reach from further
         * left; all bytes once `(?m)` makes it true before every newline. */
        if (multiline) {
            First r;
            bs_all(r.f);
            r.nullable = false;
            return r;
        }
        return fst_empty(true);
```

But the value it reads is captured **once for the whole pass**
(`src/opt/possessify.c:579`):

```c
    P.multiline = cx->mods.multiline;
```

and `pcrec_possessify` runs from `src/opt/select_engine.c:145`, i.e. **after the
parse has completed**. So `cx->mods.multiline` holds the parser's
*end-of-pattern* multiline state — while `(?m)` in PCRE2 is **scoped**.

Four consequences, derived from the shipped scoping rules documented at
`src/parse/mod_modifiers.c:212-226`:

| pattern | end-of-parse `mods.multiline` | the `$`'s real multiline state | verdict |
|---|---|---|---|
| `(?m)a{0,4}$` | true | true | correct (declines) |
| `(?m:a{0,4}$)` | **false** (restored at `)`) | **true** | **UNSOUND — exempts a multiline `$`** |
| `(?m)a{0,4}$(?-m)b` | **false** | **true** | **UNSOUND** |
| `a{0,4}$(?m)` | true | false | merely conservative (safe) |

Two of the four are miscompiles, and they arrive the day the `m` letter is
accepted — before any of `(?m)`'s own engine work is even reachable. D47.5's
recorded obligation ("a `(?m)` pattern whose `$`-follow quantifier must NOT
possessify") would be discharged by a test on row 1 and would **miss both
unsound rows**, because row 1 is the case the shipped code gets right.

§8.1.1 turns that table into measured cells with subjects and spans, which is
the form the panel should attack.

### 8.1.1 The miscompile as CELLS — the thing to attack

MEASURED, `probes/probe_d475_scope.py`, output `out/d475_scope.txt`
(libpcre2 10.46, python 3.14.4). Read the columns as: **as-written** is the
correct answer; **possessive** is what a wrongly-exempting gate compiles the
pattern to.

```
shape               pattern (as written)   subject as-written possessive pcre2 poss verdict
leading (?m)        (?m)[^c]{1,3}$         'a\nc'  (0, 1)    None      None      ok
SCOPED (?m:...)     (?m:[^c]{1,3}$)        'a\nc'  (0, 1)    None      None      *** MISCOMPILE ***
(?m) then (?-m)     (?m)[^c]{1,3}$(?-m)    'a\nc'  (0, 1)    None      None      *** MISCOMPILE ***
(?m) AFTER the $    [^c]{1,3}$(?m)         'ab'    (0, 2)    (0, 2)    (0, 2)    ok
no (?m) at all      [^c]{1,3}$             'ab'    (0, 2)    (0, 2)    (0, 2)    ok
```

**2 of 5 cells miscompile**, and the failure is the strongest kind available:
the correct answer is a match at `(0,1)` and the possessified compile returns
**no match at all**. That is a lost match, not a shifted span, so a guard cell
on it cannot pass by an off-by-one.

Why `[^c]{1,3}$` on `"a\nc"` diverges, spelled out: greedy takes `a\n` to
position 2, `$` fails there (`s[2]` is `c`), retreats to position 1 where under
`(?m)` `$` succeeds before the newline, and reports `(0,1)`. Possessified there
is no retreat, so the match is lost. This is exactly §2.5's upward-closure
argument collapsing per-line.

**The two miscompiling shapes are the two where the end-of-parse state and the
`$`'s own state DISAGREE in the unsafe direction:**

```
  leading (?m)        end-of-parse=True   the $ is multiline=True   AGREE
  SCOPED (?m:...)     end-of-parse=False  the $ is multiline=True   DISAGREE -> unsound
  (?m) then (?-m)     end-of-parse=False  the $ is multiline=True   DISAGREE -> unsound
  (?m) AFTER the $    end-of-parse=True   the $ is multiline=False  DISAGREE -> merely conservative
  no (?m) at all      end-of-parse=False  the $ is multiline=False  AGREE
```

**Note which row is `ok`:** `leading (?m)`, the only shape D47.5's recorded
obligation names. The obligation as written would be discharged by a green test
while both defects stayed live.

**An oracle finding that rides along.** Two of the five cells are
**libpcre2-only**: python3 `re` rejects a bare `(?-m)` (`missing :`) and rejects
`[^c]{1,3}$(?m)` (`global flags not at the start of the expression`). Combined
with §3.2.1's `\Z` result, this module's corpus is substantially
libpcre2-dependent, and the wave briefs must say so rather than let an author
discover it.

### 8.2 The REQUIREMENT this establishes, stated before the spelling

Both candidate fixes below satisfy one invariant, and the invariant is what the
panel should hold the implementation to — not the spelling:

> **Scoped modifier state is resolved AT PARSE TIME, onto the node. No
> post-parse pass reads `cx->mods`.**

That is a statement about *where a fact lives*, and it is already how every
other modifier works (§8.4). `multiline` is the sole exception, and the
exception is the defect.

### 8.3 The spelling: a flag on the node, or a distinct node kind?

Frank asked whether a **flag** on the AST node would suffice rather than a
distinct **node kind**. Both satisfy §8.2. The argument each way, with the
deciding evidence measured rather than asserted.

**Spelling A — a flag on the node.** `$` stays `A_EOL` and gains a bool, set at
parse from the state in force:

```c
    case '$': { Ast *a = node(cx, A_EOL); a->multiline = cx->mods.multiline; return a; }
```

*For:* it is **the house pattern**, and exactly the shape of the modifier
resolution one line away — `r->greedy = !cx->mods.ungreedy` at
`src/parse/parse.c:908`, with `ungreedy` scoped precisely as `multiline` is. No
new enumerator; `Ast` already carries per-node fields (`greedy`, `possessive`,
`not_repeatable`, `capno`). Every consumer that does not care about multiline —
which is most of them — needs no edit at all.

**Spelling B — a distinct node kind** (`A_EOL_M`, `A_BOL_M`).

*For:* a consumer **cannot forget it**. That is not a stylistic preference here,
because the defect being repaired is precisely *a consumer treating a multiline
`$` as a plain `$`*. A flag reproduces the SHAPE of the bug it fixes: any
`case A_EOL:` that does not read the new field silently keeps today's
transparent behaviour, and `src/opt/possessify.c:167`'s arm is exactly such a
site. A new kind cannot be silently ignored.

**The deciding measurement.** *Does the compiler actually catch a new kind?*
`Ast.k` is enum-typed (`AKind k;`, `src/core/internal.h:89`) and the build is
`-Wall -Wextra`, so `-Wswitch` should fire at any switch lacking the case and
lacking a `default:`. Measured rather than assumed, and — **corrected after R30
M8** — measured by a COMMITTED INSTRUMENT rather than by a hand edit anyone
would have to take on trust: `probes/probe_wswitch_alarm.sh` appends the
enumerator, runs `gcc -fsyntax-only`, counts the diagnostics, and restores the
header under an EXIT trap that verifies the restore. Archived at
`out/wswitch_alarm.txt`; a read-only critic can re-run it.

| | sites that fail to compile-warn | |
|---|---|---|
| **new node kind** | **15 warnings across 6 files** — `src/gen/emit_vm.c` 5, `src/opt/revdet.c` 4, `src/opt/possessify.c` 3, `src/opt/mrl.c` 1, `src/opt/altcls.c` 1, `src/ir/nfa.c` 1 | every one is a site that would have to *decide* about multiline |
| **new flag** | **0** | a new struct field warns nowhere, by construction |

Sample, verbatim:

```
src/gen/emit_vm.c:655:9: warning: enumeration value 'A_PROBE_ONLY_M6_1' not handled in switch [-Wswitch]
src/opt/mrl.c:90:9:      warning: enumeration value 'A_PROBE_ONLY_M6_1' not handled in switch [-Wswitch]
src/opt/altcls.c:378:5:  warning: enumeration value 'A_PROBE_ONLY_M6_1' not handled in switch [-Wswitch]
```

The instrument also refuses to report zero when it compiled nothing — its own
first run produced `0 diagnostics` because the include paths were wrong, which
is this probe's version of the failure mode this document keeps finding in
other people's checks.

>
> **[M6.2] WAVE C, 2026-08-19 — THE FOUR-SITE INSPECTION, DISCHARGED.** D62
> chose the flag, so this section's residual is live and its landing condition
> was to inspect the four `default:`-carrying switches by hand. **None of the
> four needs the flag**, and the reason is one fact with three shapes:
>
> | site | what it does with `A_BOL`/`A_EOL` | why the flag cannot change it |
> |---|---|---|
> | `vm_det_seq` (emit_vm.c) | `default: return 0` — DECLINES | a `$` is zero-width under either spelling, so "scan ahead by stride" is wrong for both |
> | `vm_cap_offsets` (emit_vm.c) | `default: return -1` | UNREACHABLE: it runs only on bodies `vm_det_seq` approved, which excludes both |
> | `vm_rev_emit` (emit_vm.c) | `default:` -> `ctx_fail` | UNREACHABLE: `revdet.c`'s `rd_shape` declines every `A_BOL`/`A_EOL` before this walk starts |
> | `pcrec_revdet_first` (revdet.c) | `default:` WIDENS to all bytes | widening is opaque to what an assertion means; it makes the disjointness test fail, which is the sound direction |
>
> **The generalization, which is the part worth carrying to the fifth
> analysis** (D62's own revisit-when): an analysis is at risk exactly when it
> treats `$` as TRANSPARENT — reasoning about WHERE it is true and concluding
> it may be skipped over. All four treat it as OPAQUE (decline, widen, or
> unreachable), and opacity is multiline-blind by construction.
> `src/opt/possessify.c` was the tree's one transparent consumer, which is why
> it was the one site the defect lived at. The inspection and this rule are
> recorded at the field itself (`src/core/internal.h`, `Ast.multiline`), where
> D62 control 3 points a reader, rather than only here.

**Nineteen switches over `Ast.k` exist** — `src/opt/possessify.c` 3,
`src/ir/nfa.c` 1, `src/gen/emit_vm.c` 8, `src/opt/mrl.c` 1, `src/opt/revdet.c`
5, `src/opt/altcls.c` 1 (a twentieth switch at `src/gen/emit_vm.c:3855` is over
`e->k`, a different enum, and correctly did not warn). **15 have no `default:`
arm**, so 15 of 19 become build diagnostics — and under `make strict`
(`-Werror`) a hard build failure. The four that fall through silently are the
residual this spelling does not cover: `src/gen/emit_vm.c` (3) and
`src/opt/revdet.c` (1). The correspondence is exact — each file's silent count
equals its `default:` count — and a wave-C landing condition should be to
inspect those four by hand.

#### The house rule that already exists, and settles this

The `-Wswitch` behaviour above is not an incidental property this note
discovered — **pcrec already has a named, deliberately-designed rule that
depends on it**, introduced by the R26 V7 review and cited by name from a
second file. `src/opt/mrl.c:18-24`, verbatim:

```
 * THE SWITCH IS EXHAUSTIVE WITH NO DEFAULT ARM, and that is a design
 * obligation rather than a style preference (§4.2's failure mode 1, sharpened
 * by R26 V7). A node kind added after this file is written must be a COMPILE
 * ERROR here, not a silent inheritance of whatever a default arm returned.
 * Under -Wswitch (which `make strict` promotes to an error) a new AKind
 * member makes this function fail to build, which is exactly the alarm the
 * analysis cannot otherwise raise.
```

and `src/opt/altcls.c:405` refers to it as settled practice:

```c
    return a;   /* unreachable under -Wswitch (make strict); mrl.c's rule */
```

That last clause of mrl.c's comment — *"exactly the alarm the analysis cannot
otherwise raise"* — describes `src/opt/possessify.c`'s situation word for word.
A possessification analysis cannot detect from the outside that a `$` it is
treating as transparent has become a different kind of `$`; that is what §8.1
is. mrl.c's rule exists to make precisely that undetectable-by-analysis change
into a build failure.

**RECOMMENDATION: spelling B, the distinct node kind.** Not on taste, and not
as a new convention: it is **the project's own existing rule applied to the
case the rule was written for**. The manager's argument for A is real — it *is*
the house pattern for resolving a modifier onto a node, and `r->greedy` is
exactly that shape. But `greedy` is a property no analysis is silently
transparent about, whereas multiline-ness of a `$` is one that four analyses are
transparent about today. The two spellings are not symmetric in failure: **A's
failure mode is the silent bug being fixed; B's is a compile error under
`make strict` at 15 of 19 sites.**

**The disagreement is recorded rather than resolved here** — the manager leans
A, this note recommends B, and the panel should treat it as contested. §8.2's
invariant is satisfied by either, so choosing A is not wrong; it is choosing
review where B chooses the compiler. If the panel does prefer A, this note asks
that it come with the two compensating controls B gets for free: the
`default:`-less exhaustive-switch discipline extended to the four sites that
currently have a `default:` arm, and a permanent sabotage row that flips the
flag's reader off and must turn §8.7's cells red.

Under either spelling `P.multiline` disappears from `Pss` and
`cx->mods.multiline`'s only post-parse read goes with it.

### 8.4 Blast radius, and how it was verified

The claim "`cx->mods` has exactly one consumer outside the parser" is this
lane's own grep, re-run in this worktree rather than inherited:

```
$ grep -rn "mods\." src/ --include=*.c --include=*.h --include=*.inc
src/opt/possessify.c:57      (a comment)
src/opt/possessify.c:579     P.multiline = cx->mods.multiline;
src/parse/parse.c:80,105,117 xlevel
src/parse/parse.c:164,179,494 caseless
src/parse/parse.c:631        nocap
src/parse/parse.c:693        dotall
src/parse/parse.c:908,910    ungreedy
```

`mods.` appears in exactly **two files** in all of `src/`. Nothing in
`src/ir/`, `src/gen/`, `src/core/` or `cli/` reads it.

**And the structural point that follows, which answers Frank's (b) — "are there
other flags that need the same notice?" — with NO, for a reason:** every one of
the ten parser reads above is at **parse position**, i.e. every other modifier
already resolves onto the AST as it is built and is therefore scope-correct by
construction. `caseless` folds into the class as the class is built
(`cls_casefold`); `dotall` shapes the dot's class; `ungreedy` resolves into
`r->greedy`; `nocap` and `xlevel` likewise. **`multiline` is the only modifier
consumed after the parse, and that is the whole defect.**

The write side, for completeness, since a fix touches it:

- **initialised** at `src/core/compile.c:117` and `:324` from the compile
  options (`.caseless = (defo.flags & PCREC_CASELESS) != 0`) — two sites, both
  outside `src/parse/`, which matters for §8.6.
- **scoped** at `src/parse/parse.c:645-649` (`p_group_body`'s
  save/parse/restore) and `src/parse/mod_modifiers.c:308-364` (the option run's
  own set-parse-restore and the `)`-applies-to-enclosing-scope rule).

### 8.5 The alternative that loses: plumb scoped state to the gate

The other way to fix §8.1 is to keep the analysis reading multiline state and
make that state *scope-aware* — thread a multiline stack through `pss_walk`,
pushing and popping at the nodes that carry option scopes.

It loses on three counts:

1. **The AST does not record option scopes.** `(?m:...)`'s group is
   set-parse-restore at parse time (`src/parse/mod_modifiers.c:352-364`) and
   leaves **no node** behind saying "multiline was on in here" — a
   non-capturing group with an option run produces the same tree as one
   without. So this alternative must FIRST add scope markers to the AST, which
   is strictly more surgery than resolving the fact onto the node and is the
   same information stored in a worse place.
2. **It preserves the failure mode.** The analysis would still be
   re-deriving a property of a node from a separate source it must keep in
   sync — this project's recorded check-design failure — instead of reading the
   node it is already holding.
3. **It does not generalise.** Every future consumer of "is this `$`
   multiline?" (the DFA lowering in wave C, the VM emitter, a future
   lookbehind analysis) would need its own copy of the same threading. Resolving
   at parse means each of them just reads the node.

### 8.6 Making the invariant STRUCTURAL rather than a discipline rule

§8.2's invariant is currently a sentence someone must remember. It can be a
construction, and this is the durable answer to Frank's (b): not "no other
modifier is affected today" but **"no future modifier CAN be affected"**.

**Proposed:** once possessify's read is gone, `cx->mods` has **zero legitimate
consumers outside `src/parse/`**, so make an out-of-parse read a *compile
error* rather than a review finding. The cleanest form, given the write sites in
§8.4, is that **`ModState` stops being a `Ctx` member and becomes state owned by
the parse driver** — it is only live during the parse anyway. `src/core/compile.c`
already treats the option as a *seed* rather than the state (its own comment at
`:112-116`: "the CLI option is the SEED for the parse state, not the state
itself"), so those two sites pass the seed into the parse entry point instead of
writing a member. After that, `cx->mods` does not exist to be read, and a future
`(?X)` modifier physically cannot be consulted after the parse.

Blast radius of that move: the two `compile.c` initialisations, the `Ctx`
member, and the save/restore sites in `src/parse/` which already pass `cx`
around. **Nothing in `src/ir/`, `src/gen/`, `src/opt/` (after the fix) or
`cli/` touches it.** This is proposed as a wave-A item riding the gate refactor;
if the panel judges it out of scope for [M6.2] it should become its own row
rather than be dropped, because the invariant is the finding and the enforcement
is what stops it decaying.

### 8.7 The test shape — measured cells, both oracles

D47.5's obligation is a `(?m)` pattern whose `$`-follow bounded quantifier must
NOT possessify. This lane re-ran **eng_brep's own instrument**
(`eng_brep_measurements/probes/probe_dollar_multiline_pcre2.py`) rather than
building a second one, and extracted the cells.

**MEASURED** (`out/dollar_multiline_rerun.txt`). The greedy population — the one
the exemption is *about*, since the lazy conjunct already declines — splits
exactly as §2.5's argument predicts:

| preference | arm | multiline | python | libpcre2 | cells |
|---|---|---|---|---|---|
| greedy | disjoint | **false** | same | same | **168 (0 diverging)** |
| greedy | disjoint | **true** | DIVERGES | DIVERGES | **12** |
| greedy | disjoint | true | same | same | 156 |
| greedy | exact-count | either | same | same | 24 + 24 |

All twelve diverging greedy cells have body `[^c]`, counts `{0,2}` `{1,3}`
`{0,4}` `?`, prefixes `""` / `z` / `(?:z|)`.

**Concrete cells, oracle-verified against python3 `re` this session** (which
supports possessive quantifiers natively at 3.14, so greedy and possessive are
the same instrument):

| pattern | subject | greedy | possessified |
|---|---|---|---|
| `(?m)[^c]{1,3}$` | `"a\nc"` | `(0,1)` | **no match** |
| `(?m)[^c]{0,2}$` | `"\nc"` | `(0,0)` | `(2,2)` |
| `(?m)[^c]{0,4}$` | `"\nc"` | `(0,0)` | `(2,2)` |
| `(?m)[^c]?$` | `"\na"` | `(0,0)` | `(1,2)` |

**Recommended `.rxt` guard cell: `(?m)[^c]{1,3}$` on `"a\nc"`, expecting
`(0,1)`.** It is the strongest of the four because a possessified compile
produces **no match at all**, so the cell cannot pass by accident on an
off-by-one.

**The controls the cell needs**, since a test with no failing direction is not a
test:

- **the non-multiline twin**: `[^c]{1,3}$` on `"ab"` → `(0,2)`, where the
  exemption *does* fire and must keep firing (a regression that disables the
  exemption wholesale would otherwise pass).
- **the SCOPED cell §8.1 found**: `(?m:[^c]{1,3}$)` on `"a\nc"` → `(0,1)`. This
  is the one that fails today's shipped gate design and passes §8.2's invariant.
  It is the
  cell D47.5's own wording does not ask for.
- **a sabotage row** (`tests/mech/sabotages/`) that forces `A_EOL_M` to be
  treated as `A_EOL` in `first_of`, which must turn the cells red.

### 8.8 A discrepancy this lane will not smooth over

`eng_brep_design.md` §2.5 cites **0 of 720** (multiline off) and **180 of 720**
(multiline on). Re-running that section's own probe today gives **21 of 384**
and **33 of 384** overall, and the greedy figures above.

The **qualitative claim is fully intact** — zero divergence with multiline off,
non-zero with it on, on the population the exemption covers, with both oracles
agreeing — and the lazy divergences that appear at multiline=false are explained
by the probe's own trailer as the pre-existing lazy+nullable-rest rule rather
than a `$` defect. But the numbers in §2.5 are stale (D47.6's fixed subject
generator is recorded in §2.7 as having moved figures elsewhere in that note).

**This design cites today's numbers.** Correcting `eng_brep_design.md` is out of
this lane's scope; it is flagged in §11 Q6.

---

## 9. (vii) Module gating

### 9.1 The module name is already right

§1 measured it: all eight constructs already refuse with `requires module
'assertions'` on HEAD. `FEAT_ASSERTIONS` exists (`src/core/internal.h:449`) and
is simply not a member of the `std1` named set (`src/parse/enabled.c`), so
`--features assertions` is the switch and it already gates every one of them.
No re-attribution work exists.

### 9.2 Partial implementation across waves — the real question

The waves in §10 land constructs incrementally, so there is an interval where
`--features assertions` is enabled and `\K` (say) is not built. **A construct in
an enabled module must not compile to something wrong, and must not claim the
module is missing.** "Requires module 'assertions'" would be a lie once the user
has enabled it.

**Proposed, on the `--encoding=utf8` precedent** (`src/gen/enc/enc.c`'s table
carries a `utf8` row with a NULL backend so "a name pcrec knows but cannot
compile must be refused BY ITS OWN NAME, never fall out of a lookup as
unknown"): the registry row gains a *built* predicate, and an enabled-but-unbuilt
construct refuses with a distinct diagnostic naming the construct — not the
module.

**The precedent transfers by analogy, not verbatim — R30 C7.** `--encoding`'s
gate is a **single whole-pattern** decision made once in `src/core/compile.c`
against a one-row-per-encoding table. Module `assertions` needs a
**per-construct** decision made at the registry dispatch, because a half-landed
module has some constructs built and others not *within the same pattern*. The
shape this design proposes — a `built` predicate on the registry row, consulted
where the module gate is consulted today — is the right one; what carries over
from `--encoding` is only the *principle* (a name the tool knows but cannot
compile is refused by its own name, never as "unknown"), not the mechanism.

Under D26 the exact wording is tier 3 and the manager may pick it; the
*structure* is not tier 3, because it decides whether a half-landed module can
miscompile. §11 Q2 puts the shape to Frank.

### 9.3 Both engines carry every construct

`--engine=vm` must answer every `assertions` pattern, because it is the
cross-check that makes the DFA's answers trustworthy (the CLI's own words:
"which is what makes it usable as a cross-check against the DFA rather than an
echo of it"). Every construct here has a one-line VM spelling on the model of
the shipped `A_BOL`/`A_EOL` arms (`src/gen/emit_vm.c:3458-3474`):

| construct | VM test at `pos` |
|---|---|
| `\A` | `pos == 0` |
| `\z` | `pos == n` |
| `\Z` | `pos == n \|\| (pos + 1 == n && s[pos] == '\n')` |
| `(?m)^` | `pos == 0 \|\| s[pos-1] == '\n'` — **WRONG, see §3.7's wave C annotation**: PCRE2 excludes a newline that ENDS the string, so the shipped arm is `pos == 0 \|\| (pos < n && s[pos-1] == '\n')` |
| `(?m)$` | `pos == n \|\| s[pos] == '\n'` |
| `\G` | `pos == startpos` |
| `\b` | see below — the naive spelling reads out of bounds at both edges |
| `\K` | `caps[0][0] = pos` (trailed) |

**`\b`'s spelling must carry its guards, R30 m2.** The first draft wrote
`wordtbl[s[pos-1]] != wordtbl[s[pos]]` with the out-of-subject rule in prose.
That spelling reads `s[-1]` at `pos == 0` and `s[n]` at `pos == n` — K27's exact
class, in a document whose §7 cites K27's fix approvingly. Out-of-subject counts
as non-word, so the guards belong in the expression:

```c
    ((pos > 0 && wordtbl[s[pos-1]]) != (pos < n && wordtbl[s[pos]]))
```

and `\B` is the same with `==`. `match_api.md` §3.1 makes `(s == NULL, n == 0)`
a legal subject, so this is not defensive padding: at `n == 0` both operands
must short-circuit before any dereference.

`\b`'s `wordtbl` is the front-end-emitted table of §7.2, and it is the only row
with an encoding future.

> **BUILT, [M6.2] WAVE C (2026-08-19) — the two `(?m)` rows, with `\b`'s two
> corrections applied to them rather than rediscovered.** Both ship with the
> guard IN THE EXPRESSION (R30 m2's rule, K27's class): `pos == 0` and
> `pos == n` short-circuit before `s[pos-1]` and `s[pos]` are formed, so
> `match_api.md` §3.1's legal `(s == NULL, n == 0)` subject dereferences
> nothing. And both take their newline from the CLASS POOL — `vm_cls(v,
> pcrec_cls_newline)`, the same interning `\b` uses for `pcrec_cls_word_esc`
> — rather than from a `'\n'` written into the emitted comparison. That is
> D64's definition-shaped constraint discharged the way §7.2 item 3 discharges
> `\w`'s: one table, three readers (this arm, `src/ir/dfa.c`'s alphabet
> refinement, and `\N`), and no site that could disagree with another about
> what a line break is.

**`\G` and the match-here entry — CORRECTED, R30 E8.** The first draft said the
`rx_ctx` "has no `startpos`" and built a spec consequence and a Wave D test on
top of that. **The premise is factually wrong.** The DFA artifact's match-here
entry *is* `rx_search` called with `ctx->pos` as `startpos`, plus a
start-equality filter — quoted in §6.3 from a real artifact. `startpos` is
threaded; it is `ctx->pos`.

So `\G` under the match-here entry means `pos == ctx->pos`, which is trivially
true at entry — the same *answer* the first draft reached, by an argument that
did not hold. And for a **fully-`\G`** pattern the two entries agree exactly,
which is why **Wave D's owed differential is withdrawn: it had nothing to
find.** What replaces it in §10 is a test that the two entries agree, which is
the property actually worth pinning.

Two further corrections that follow from the same artifact:

- The two engines' match-here entries do **not** share a shape. The DFA's wraps
  `rx_search`; the VM's calls `rx_match_impl` directly. A design statement about
  "the match-here entry" has to say which.
- The interesting `\K` interaction lives here, not in `\G` (§6.3 rule 3).

---

## 10. Proposed wave structure for [M6.2]

Ordered, disjoint, each with its own landing conditions. The ordering rule is
**cheapest-and-most-enabling first**, and the one deliberate inversion is that
the D47.5 gate refactor lands in Wave A — *before* `(?m)` is accepted — so it is
provably behaviour-preserving when it lands.

### Wave A — `\A` `\z` `\Z`, the third view, and the gate refactor

**Scope.** Parser rows for `\A`/`\Z` (aliases, §3.2) and `\z`; `closure`'s
`end_ok` bit and `make_state`'s **three-way canonicalization** (§3.3, corrected
per R30 E3 — `endvar` against the EOL view, not the base); the parse-time
resolution of §8.2–§8.3 as a pure refactor (`A_BOL_M`/`A_EOL_M` introduced but
**unreachable**, since `(?m)` is still refused); possessify's gate becomes a
node-kind whitelist; `--features assertions` and §9.2's enabled-but-unbuilt
refusal.

**Why first.** No state-count risk, no hot-path change, and it builds the view
machinery `\b` and `(?m)` both extend. The gate refactor is provably a no-op
here and impossible to prove later.

**Tests / landing conditions.**
- `.rxt` cells for `\A`/`\z`/`\Z` including the three-way position distinction
  (`"ab\n"`: `b\Z` matches at `(1,2)`, `b\z` does not) — **verified against
  libpcre2, NOT python, per §3.2.1; the wave brief must carry that constraint
  explicitly.**
- A structural check that a `\z`-free pattern's artifact is **byte-identical**
  to the pre-wave artifact, corpus-wide. **R30 E3 is the argument for this
  check**: the first draft's byte-identity claim was WRONG and this check is
  what would have caught it.
- **SABOTAGE (R30 C3):** break the three-way canonicalization back to the
  first draft's base-reference form; the byte-identity check must go **red** on
  any `$`-bearing pattern. Without this row the check has no measured failing
  direction.
- The non-multiline possessify controls of §8.7 must stay green.

### Wave B — `\b` `\B`

**Scope.** Word-set alphabet refinement (§3.4); the previous-byte context bit in
the state identity, forward and reverse (§3.5); **mechanism 4's start-state
seeding, forward and reverse (§3.8)**; the class-indexed accept table (§3.6)
emitted **only** where a next-byte-sensitive assertion is reachable at an
accepting position, so every existing pattern's artifact is unchanged; the
composition rule of §3.6.2; the VM's guarded `\b` spelling (§9.3) on the shared
`pcrec_cls_word_esc` table (§7.2 item 3).

**Why second.** It is the module's only real engine work and everything else is
smaller. It must precede `(?m)` because `(?m)$` reuses the same mechanisms.

**Tests / landing conditions.**
- **The `startpos > 0` cells of §3.8** — ten cells, five of them differing —
  and the same patterns driven through the §3.1 find-all loop. Strongest: `\bfoo` on `"xfoo"` at `startpos 1`
  must NOT match (a context-blind implementation matches), and `\bfoo` on
  `"xfoo foo"` at `startpos 1` must report `(5,8)` and not `(1,4)`. The find-all
  arm must include a case whose resume lands **mid-word** (`\Bfoo` on
  `"xfoofoo"` → two matches, context-blind → one); a find-all suite whose
  resumes all land at boundaries proves nothing.
- **The REVERSE machine's BOTH mechanism-4 sites** (§3.8.3, this design's least
  certain area), swept against libpcre2 as two separate arms because they fail
  on disjoint populations:
  - **initialization** (`s[end]`): **trailing** `\b`/`\B` patterns.
  - **termination** (`s[startpos-1]`, §3.8.3.1): **LEADING `\B`** patterns at
    `startpos > 0`. **A leading-`\b`-only sweep CANNOT see this** — `\b`'s
    blind assumption coincides with its truth condition, so it reports clean
    against a design that throws matches away. The named cell is `\Bfoo` on
    `"xfoo"` at `startpos 1`, which must report `(1,4)` and not "no match".
- A structural check for §3.8.3.1's invariant: **no `sfound` is recorded at
  `pp == startpos` except through the context-indexed accept** — every writer,
  including the reverse skip's own `sfound = pp`, not just the loop-top one.
- **The COMPOSED budget measurement of §3.5.1**, taken on the built compiler
  against **both** caps — `PCREC_MAX_DFA_STATES_TABLE` (32,000) for ENG_UNANCH
  and `PCREC_MAX_DFA_STATES_GOTO` (10,000) for ENG_ATTEMPT — with the refusal
  boundary **located, not predicted**. §3.5.1 puts the composed worst case at
  38,009 states, which is over the larger cap; a wave that does not measure this
  is shipping a capability regression it has already been warned about.
- `probe_ncls_refine.py` re-run against the built compiler, with §3.4's measured
  deltas as the prediction to confirm or refute.
- A structural check that no artifact contains a second word-set spelling.
- A structural check that no artifact indexes an accept table at `pos == n`
  (§3.6.2).
- **NOT the skip-intersection sabotage.** It moves to Wave C — see below.

### Wave C — `(?m)`

**Scope.** Accept the `m` letter (`src/parse/mod_modifiers.c:280`);
`A_BOL_M`/`A_EOL_M` become reachable; `(?m)$` on the Wave B machinery; `(?m)^`
routed to ENG_ATTEMPT via an extended `nfa_has_bot` and the three-way start
dispatch (§3.7); **the scan-avoidance cure of §3.6.1** — all five mechanisms,
the widened `start_acc`, and the class-indexed post-skip accept.

**Why third, and why the skip cure lives HERE (R30 E5).** `\b`'s accept is
constant across any skipped run, so a Wave B sabotage of the intersection could
not fire on a single pattern Wave B lands. The `(?m)$`/`\Z` family is the
population that can actually break, so the cure and its sabotage belong to the
wave that lands it. If Wave B wants the machinery early it must carry a
`(?m)$`-shaped stand-in pattern that can go red.

**Tests / landing conditions.**
- D47.5's obligation in full — §8.7's four cells, the non-multiline control,
  **the scoped `(?m:...)` cell**, and the gate sabotage.
- A differential sweep of `(?m)$` patterns **with a live prefilter and skip
  states** against both oracles (D11's own failure shape).
- **SABOTAGE, one per intersected mechanism** (§3.6.1's table rows 2, 3, 4, 5),
  each validated against a `(?m)$`-family pattern that makes it fire. Row 1
  (memchr) is not intersectable; its guard is the widened `start_acc`, whose
  sabotage is narrowing it back to one class's bit — the `\bx*`-shaped cell in
  §3.6.1 must then lose three of its four matches.
- **The `(?m)^` cost recorded as a NUMBER, not a shrug**: re-run
  `probe_mline_caret_cost.sh` against the built compiler, and either land the
  `memchr('\n')` candidate-start prefilter (§3.7.2) or record the measured
  O(n²) in the plan row as shipped behaviour.

> **[M6.2] WAVE C LANDED, 2026-08-19 (lane/asrtwavec).** All of the above
> discharged; the four inline annotations that correct or extend this section
> are at §3.6.1 (the five mechanisms' SHIPPED postures — not one of them is an
> intersection), §3.7 (the class axis is three-valued, `(?m)$` needs the
> `pos == n` view, and the closure names its operands by SIDE), §3.7.2 (D63's
> candidate set is the LIVE-SEED set, strictly more general than the newline
> set), §8.3 (the four `default:` sites inspected, none needs the flag) and
> §9.3 (the two VM rows, guards in the expression, newline from the class
> pool). What this section did NOT predict, recorded here because it is the
> only structural surprise: `(?m)$` reaches `emit_view_select`'s
> `has_end && !has_eol` arm — the branch wave A wrote for "`\z` with no `$`
> anywhere" — because `N_EOL_M` never consults `eol_ok`. A construct the
> section treats as `$`'s sibling therefore shares an emitted selector with
> `\z` and none with `$`.

### Wave D — `\G`

**Scope.** `start_max = startpos` (§4.1); the three-way start-state dispatch for
partial `\G` (§4.2); the VM's `pos == startpos`; the `match_api.md` §3.1
sentence of §4.3.

**Tests / landing conditions.**
- Contiguity through the find-all loop (`\G` under §3.1's loop reports only
  contiguous matches).
- `\Gfoo|bar` on both engines; `a\Gb` never matching, agreeing with PCRE2.
- **The first draft's owed `search`-vs-`match` differential is WITHDRAWN**
  (R30 E8): for a fully-`\G` pattern the two entries agree exactly, so it had
  nothing to find. What replaces it is a test that they DO agree **for a
  FULLY-`\G` pattern** — the property actually worth pinning, and the scope
  matters: a **partial** `\G` pattern (`\Gfoo|bar`) legitimately DISAGREES
  between the two entries, because `<prefix>_search` may match `bar` at a later
  offset while the match-here entry's start filter rejects it. An unscoped
  "the entries agree" test would therefore be red on correct behaviour. So:
  agreement asserted for fully-`\G` patterns, and a `\G`-in-some-branches
  pattern at `startpos > 0` tested for its own expected DISagreement, which is
  also where the three start states of §4.2 are distinguishable.

### Wave E — `\K`

**Scope.** The second `forces_*` row in `src/opt/select_engine.c` (§6.2); the
trailed `caps[0][0] = pos`; **all three rules of §6.3** — the hybrid's
`caps[0][0]` provenance, the `--engine=dfa` refusal, and the match-here entry's
pre-`\K` filter and consumed-length return.

**Why last.** It is the only construct with no DFA path, so it shares no
machinery with A–D and can move if scheduling requires.

**Tests / landing conditions.**
- **The match-here entries, both of them** (R30 E8): `a\Kb` at `ctx->pos == 0`
  must match with length 2 consumed, where the unfixed filter returns `-1`; and
  the VM's entry must be tested separately from the DFA's, because they do not
  share a shape.
- A structural check that no `\K` artifact takes `caps[0][0]` from the reverse
  pass.
- **SABOTAGE (R30 C3):** make the emitted `\K` artifact write `caps[0][0]` from
  the prefilter's span; the structural check must go **red**. Without this the
  check is the only one in the module with no measured failing direction.
- `\K` inside a quantifier (the undo-on-backtrack case); `--engine=dfa` refusal.
- **Oracle constraint:** python `re` has no `\K` at all, so this wave rides the
  libpcre2 differential entirely. The brief must say so — with §3.2.1's `\Z`
  result and §8.1.1's two libpcre2-only cells, that is the third place in this
  module where the base-tier oracle cannot answer.

**A D27-blinded corpus rides the module's close**, per the [M6.2] row.

---

## 11. Open questions for Frank

**Q1 — the newline axis (§5.2), REFRAMED after R30 M5.** Declare
`pcrec_options.newline` + `--newline=NAME` now, per-pattern on D58's precedent,
shipping `lf` only and refusing the other five by name (and mapping the `(*CR)`
verbs onto the same namespace)? Or leave the axis implicit until a consumer
asks?

**The first draft's argument for declaring it is WITHDRAWN.** It claimed an
exemption from D18's earn-its-axis rule on the grounds that this is "a semantic
namespace, not an optimisation axis". R30 refuted that on D18's own worked
example: **D23 ran the earn-its-axis test on case-folding — a semantic
dimension — and it FAILED into the parser.** So "semantic" is not a category
D18 exempts; if it were, every future customerless axis with a semantic flavour
would inherit the exemption. And the D58 comparison cuts the other way too:
encoding was justified by a **committed second customer** (M5 is the next
milestone), which newline does not have.

**The honest test is the one D23 ran: try to FOLD it.** Hardwire LF, attempt to
express the other five conventions in the front end, and see which way it fails
— that is a measurement, and this lane did not take it. The prediction DD-11's
own row already records is that `.`/`\N` fold cleanly (byte-set swap, like
OS-1's caseless) while `$`, `\Z` and `(?m)`'s anchors do **not** fold for
CR/ANYCRLF (set-valued) or CRLF (a two-byte sequence in both the forward and
reverse DFAs). If that prediction holds, the axis earns itself on the engine
half and folds on the class half — which is a more useful answer than either
"declare it" or "defer it".

**Recommendation, revised: run the fold test before ruling.** It is a
measurement, not a decision, and it belongs to whichever wave lands `(?m)` —
which is the first consumer of the newline concept beyond `$`.

**Q2 — enabled-but-unbuilt diagnostics (§9.2).** During waves A–E the module is
enabled while some constructs are unbuilt. Confirm the shape: a per-construct
"not yet implemented" refusal naming the construct, distinct from "requires
module". Wording is D26 tier 3; the *structure* is a ruling because it decides
whether a half-landed module can miscompile.

**Q3 — `(?m)^`'s cost (§3.7), REFRAMED after R30 E2.** The first draft asked
this question on a false premise ("inherits D8's shape and nothing else
changes") and recommended accepting it. Re-posed on the measured footing:

`(?m)^` cannot take the `start_max = 0` fast path — its interior start state is
live by definition — and ENG_ATTEMPT has no prefilter and no skips, so the
measured cost is **O(n²): 3.99x per doubling, 1996x slower than the anchored
twin at n = 64,000** (§3.7.1). Three options, and this design does not pick
between the last two:

- **(a) Ship the routing and record the cost.** `(?m)^` works, is correct, and
  is quadratic on large subjects. Cheapest; the number goes in the plan row so a
  user meets it in documentation rather than in production.
- **(b) Ship the routing plus the `memchr('\n')` candidate-start prefilter**
  (§3.7.2). Its evidence is the **non-crossing linear arm** — the shape most
  real `(?m)^` patterns have — where ENG_ATTEMPT measures **85-185x** slower
  than the ENG_UNANCH equivalent purely from visiting every offset instead of
  every line start. Contained in `emit_attempt`, no new engine. Note this does
  NOT rescue the quadratic arm, where each surviving attempt still scans to the
  end; option (b) buys the common case, not the worst one.
- **(c) Unpark [DD-7]** and build the reverse BOT variant, after which both
  plain `^` and `(?m)^` join ENG_UNANCH and this section disappears. Largest,
  and the argument for it is stronger than when DD-7 was parked: the slow shape
  stops being an edge case and becomes the normal case for a common construct.

*Recommendation: (b), with (c) explicitly not foreclosed.* R30 marks the DD-7
half as **Frank's ruling** once this framing exists, which it now does.

**Q4 — `\K` and the hybrid (§6.3).** Confirm both rules: `caps[0][0]` from the
VM alone on a `\K` pattern, and `--engine=dfa` refuses `\K` (the D44.6 shape).

**Q5 — `\G` in the spec (§4.3).** Add the sentence to `match_api.md` §3.1
recording that the find-all loop's `startpos` is what gives `\G` its
global-iteration meaning?

**Q6 — `eng_brep_design.md` §2.5's stale figures (§8.8).** This lane re-ran that
section's own probe and got different numbers with the same qualitative result.
Correct §2.5 in place (house style is annotate, not rewrite), or leave it and let
this document carry the current reading? **This lane deliberately did not edit
`eng_brep_design.md`**; the archived re-run (`out/dollar_multiline_rerun.txt`)
carries full provenance so the annotation can be written from it directly.

**Q7 — does D47.5 need an ADDENDUM? (§8.1–§8.6).** D47 ruling 5 says the
exemption's condition must be "a real branch, not a comment". That was built,
and §8.1 shows the branch reads a value that is *wrong for two scoped shapes* —
so the ruling is satisfied in letter and defeated in fact. The substance of the
proposed repair goes beyond what D47.5 says: it makes the multiline fact a
property of the NODE, and (§8.6) proposes removing `cx->mods` from post-parse
reach entirely so the class of defect cannot recur. **Recommendation: D47.5
gains an addendum at merge, recording (a) that the live-branch requirement is
necessary but not sufficient, (b) the invariant of §8.2 as the actual
requirement, and (c) the spelling the panel picks in §8.3.** This lane
deliberately does not edit `../dev/decisions.md`; the addendum is the manager's
to write once the panel rules.

**Q8 — the spelling, if the panel does not settle it (§8.3).** This note
recommends the distinct node kind and records that the manager leans to the
flag. Both satisfy §8.2's invariant; they differ in whether the failure mode is
a build diagnostic (15 of 19 switch sites, measured) or a silent omission. If
the panel splits, Frank picks.

---

## 12. BELIEVED claims, with the experiment that refutes each

Per §0.1, every BELIEVED claim in a load-bearing position, collected:

1. **§3.6.1's skip-set intersection is sound.** *Refutation:* build a `\b`
   pattern whose prefilter state has a skip set overlapping the word/non-word
   boundary, sweep against both oracles over subjects that place a match end
   inside a skipped run. If the intersection is wrong, D11's 53-divergence shape
   recurs. Wave B's landing condition.
2. **§7.2: `\b`'s classification belongs to the front end, and the VM's `\b`
   under UTF-8 can be served by a front-end-emitted fragment without an encoding
   conditional in shared emitter code.** *Refutation:* attempt the UTF-8 `\b`
   fragment at M5; if it requires a conditional in `src/gen/`, DD-12 (7)'s
   design-stop applies and the seam, not the fragment, is what changes.
3. **§7.4: ENG_ATTEMPT's `start++` is a performance issue under UTF-8, not a
   correctness one.** *Refutation:* compile a UTF-8 pattern once M5 lands and
   search a subject where a match begins at a continuation-byte offset; if any
   match is reported at a non-character boundary, it is a correctness bug and
   belongs to [DD-12].
4. **§3.7: `(?m)$` can stay on ENG_UNANCH with the class-indexed view.**
   *Refutation:* the reverse machine's `(?m)$` context bit is the mirrored
   mechanism and has not been prototyped; build the reverse arm first in Wave C
   and sweep, rather than assuming symmetry holds.
5. **§4.2: three start states suffice for partial `\G`.** *Refutation:* sweep
   `\G`-in-some-branches patterns **at `startpos > 0`** against PCRE2.
   **CORRECTED after R30 S4:** the first draft said the divergence "would show
   at `startpos == 0`", which is exactly where it CANNOT show — at
   `startpos == 0` the `\A` and `\G` conditions coincide and the four
   combinations collapse to two. A sweep pinned at 0 is a sweep that cannot
   fire.
6. **§3.8.3: the REVERSE machine's mechanism-4 sites work — BOTH of them.**
   *Refutation:* sweep against libpcre2 at **both ends**, because the two ends
   fail on disjoint pattern classes and a sweep of either alone is blind to the
   other:
   - the **initialization** seed (`s[end]`) — sweep **trailing** `\b`/`\B`
     patterns, since a forward seed can be right while this one is wrong and
     only a trailing assertion can tell;
   - the **termination** boundary (`s[startpos-1]`, §3.8.3.1) — sweep
     **LEADING `\B`** patterns at `startpos > 0`. Leading `\b` is
     *accidentally safe* here, so a `\b`-only sweep reports clean on a design
     that loses matches; `\Bfoo` on `"xfoo"` at `startpos 1` is the cell.
   The reverse DFA is additionally built `prune=false`, which no measurement
   here covers.
7. **§3.7.2: the `memchr('\n')` candidate-start prefilter recovers the common
   case.** *Refutation:* build it and re-run `probe_mline_caret_cost.sh`; if the
   curve stays quadratic on the linear-case shape, option (b) of Q3 collapses
   into option (a).

## 13. What this design does NOT measure

Named rather than discovered by the panel. **Item 3 was on this list in the
first draft and R30 measured it anyway** — which is the honest reading of what
a "not measured" list is worth: it discharges nothing, it only says where to
look first. Items 8-11 are new after R30.

1. **The reverse machine's state cost for `\b`.** §3.5's prototype measures the
   forward, unanchored DFA only. The reverse DFA is built with `prune=false`
   (`src/core/compile.c:219`) and is where `eng_brep_design.md` found the whole
   quadratic compile cost of bounded repeats living. The reverse arm could be
   the expensive one and this document does not know.
2. **Compile-time cost.** Three closures instead of two, and a doubled state
   space before minimisation, cost pcrec's own compile time. Not measured.
3. ~~**`(?m)^` throughput on ENG_ATTEMPT.**~~ **MEASURED after R30 E2** — it was
   on this list, the panel measured it, and it was an O(n²) HIGH finding
   (§3.7.1). Left in place struck through rather than deleted, because the
   lesson is that this list is a to-do, not a disclosure that discharges.
4. **The VM's cost for any of these constructs.** Every VM spelling in §9.3 is
   one comparison, and none was benchmarked.
5. **`\b` interaction with `-i` (caseless).** Case folding happens at parse time
   (`cls_casefold`); the word set is case-closed already, so this is *believed*
   free and was not checked.
6. **Anything about `\K` empirically.** No `\K` prototype was built; §6 is
   entirely STRUCTURAL plus the shipped `VM_ONLY` row.
7. **The `.rxt` corpus arm of §3.5.** The prototype ran on the realistic set
   only; the adversarial corpus would likely exceed its caps, which is itself an
   untested claim.
8. **The class-indexed accept on ENG_ATTEMPT** (R30 E6). §3.6's zero-cost
   measurement covers ENG_UNANCH only; ENG_ATTEMPT bakes acceptance into its
   computed-goto body and cannot express the A/B variant, so the cost there is
   unknown — on the engine `(?m)^` and `\G` actually use.
9. **The state budget for ENG_ATTEMPT patterns** (R30 E4). §3.4's corpus
   silently excluded all 22 `^`-bearing rows, because the probe reads `facc[]`
   and that engine does not emit it. Every budget number in this document is an
   ENG_UNANCH number, against the looser of the two caps.
10. **The composed budget on the built compiler** (§3.5.1). 38,009 > 32,000 is a
    bound assembled from two patterns, not an observation of one. Where the real
    refusal boundary sits is a Wave B measurement.
11. **Whether the newline convention folds** (§11 Q1, R30 M5). The test D23 ran
    for case-folding — hardwire LF and see which way it fails — was not run
    here, and Q1 cannot be ruled on properly until it is.

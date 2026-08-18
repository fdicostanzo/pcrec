# Module `assertions` — design

**[M6.1]**, the design gate in front of [M6.2]. Covers `\b` `\B`, `\A` `\z`
`\Z`, `(?m)` multiline `^`/`$`, `\G`, `\K`.

**STATUS: PROPOSED.** No `src/` change belongs to this lane. Nothing here is
built. A D6 adversarial panel reviews this document before [M6.2] starts, so
every claim below is marked, cited, and refutable.

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

Every construct in this module is one of exactly three things, and the whole
design follows from which: an **absolute position test** (`\A`, `\z`, `\G` —
free, evaluated where the machine already knows the position); a **next-byte
view** (`$` and `(?m)$` in the forward machine, `\b`'s right-hand side — folds
into the transition and accept tables *by byte equivalence class*, so it costs
table width and no hot-path instructions); or a **previous-byte context bit**
(`\b`'s left-hand side, `(?m)^` — folds into the DFA *state identity*, so it
costs states). The forward and reverse machines swap which mechanism a given
assertion needs, because they consume bytes in opposite directions. `\K` is the
one construct that is none of the three: it reports a *path-dependent* position
that subset construction has erased, so it is VM-only — which the shipped
registry already says (`src/parse/registry.c:365`, `VM_ONLY`).

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
| `eng_brep_measurements/probes/probe_dollar_multiline_pcre2.py` | re-run, not rebuilt | the D47.5 gate's justification, today (§8.8) |

Every file in `assertions_measurements/out/` is written by
`probes/archive.sh`, which stamps one provenance header on all of them — probe
path, the commit the probe was last changed at, the commit and branch the run
was made from, whether the working tree was clean, date, and the python3,
libpcre2 and gcc versions. A number in this document can therefore be traced to
a run, not merely to a claim.

One measurement in §8.3 is not a probe: it required a temporary edit to
`src/core/internal.h` (a probe enumerator added to `AKind`, the tree rebuilt,
the warnings counted, the edit reverted — tree verified clean before and after).
It is reported with its command and its output so it can be repeated, but it
leaves no committed instrument, and that is stated rather than hidden.

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
   **hardcoded `false` in the worklist** (`src/ir/dfa.c:684-690` calls
   `make_state(..., pre, npre, false, ...)`). That is precisely why plain `^`
   works and why `(?m)^` cannot work without touching that line: multiline `^`
   is satisfiable *after consuming a byte*, which is a transition property.

So the three mechanisms of §0.2 map onto the existing code as:

| mechanism | where it lives | what it costs |
|---|---|---|
| absolute position test | start-state selection (`s0`/`s1`), and the `pos >= n` boundary | nothing; evaluated once per attempt or once per search |
| **next-byte view** | the closure's `eol_ok`-shaped bit, resolved **per byte equivalence class** at the transition | table WIDTH (§3.4), no hot-path instructions (§3.6) |
| **previous-byte context bit** | the DFA STATE IDENTITY (`make_state`'s pre-set gains a bit) | STATES (§3.5) |

The reverse machine swaps the last two, because it walks backwards: what is a
next-byte view forward is a previous-byte context bit in reverse, and vice
versa. This is not an analogy — `src/gen/emit_dfa.c:1052-1056` already emits a
reverse EOL-variant selection (`<p>_rev[]`) mirroring the forward one
(`<p>_fev[]`).

---

## 3. (i) The engine split

### 3.1 The table

| construct | DFA-representable? | mechanism | forward engine | notes |
|---|---|---|---|---|
| `\A` | **yes — an exact alias of an existing node** | absolute (start state) | ENG_ATTEMPT | §3.2 |
| `\Z` | **yes — an exact alias of an existing node** | existing `eolvar` | ENG_UNANCH + ENG_ATTEMPT | §3.2 |
| `\z` | yes | a THIRD closure view | ENG_UNANCH + ENG_ATTEMPT | §3.3 |
| `\b` `\B` | yes | prev-byte context bit **and** next-byte view | ENG_UNANCH + ENG_ATTEMPT | §3.4–3.6 |
| `(?m)$` | yes | next-byte view (fwd) / context bit (rev) | ENG_UNANCH + ENG_ATTEMPT | §3.7 |
| `(?m)^` | yes in principle | context bit (fwd) / needs the reverse BOT variant D8 deferred | **ENG_ATTEMPT** (proposed) | §3.7 |
| `\G` | yes | start-state property + `start_max` | **ENG_ATTEMPT** | §4 |
| `\K` | **no** | path-dependent reported start | **VM only** | §6 |

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
and a new `endvar`, each `-1` when identical to the base — the existing
convention at `src/core/internal.h:181-183`.

**The zero-regression property is by construction, not by a flag.** A pattern
with no `\z` has view `(eol_ok, end_ok) = (T,T)` identical to `(T,F)` at every
state, so `endvar` is `-1` everywhere and the emitter emits today's code
byte-for-byte. No `has_z` conditional is needed anywhere, which matters because
this project's recorded check-design failure is controls that share a source
with what they control: a construction that *cannot* differ is stronger than a
flag that says it does not.

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
| the `.rxt` corpus (609 harvested `pattern` lines, `sort -u`) | 574 | **0 / +1 / +2** | 0 / +1 / +1 | **+1 / +2 / +3** |

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

### 3.5 `\b`'s state cost — PROTOTYPE, calibrated, and the ratio is the number

pcrec cannot compile `\b`, so this number cannot be read off an artifact. It is
therefore a **PROTOTYPE**, `probes/probe_wordctx_states.py`, and the document
says so in three places rather than once.

The prototype builds exactly the automaton this design proposes — DFA state =
(NFA pre-set, previous byte was a word character), closure parameterised by
`(prev_is_word, next_is_word)` in the same way `src/ir/dfa.c:640-641`
parameterises by `eol_ok`, with the unanchored self-loop
(`nfa_wrap_unanchored`, `src/ir/nfa.c:590`) and **Moore minimisation**, because
pcrec minimises and an unminimised count would overstate the cost: the entire
question is how many context-split states *survive being distinguished*.

**The number that carries weight is the RATIO**, `\bPAT\b` against `PAT`, since
both arms come out of the same constructor and any divergence from
`src/ir/dfa.c` cancels.

**MEASURED** (n = 35 of the realistic set; `out/wordctx_states_realistic.txt`):

> minimised state ratio min / median / max = **1.00x / 1.11x / 4.75x**
> — 2 patterns at ≤ 1.00x, 2 patterns above 2.00x.

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

They disagree in **both** directions, which rules out a single systematic
offset. The prototype's **one known fidelity gap is stated in the file itself**:
`src/core/compile.c:216` builds the forward DFA with `prune=true` (priority
pruning) and this constructor does not prune. That gap is also why five corpus
patterns are reported over-cap rather than half-measured — on an unanchored
bounded repeat over an overlapping alphabet (`[a-z][a-z0-9_]{2,31}`) pruning is
the difference between pcrec's 33 states and a subset blow-up here.

**Consequence for the state budget:** at a median 1.11x and a worst measured
4.75x, against `PCREC_MAX_DFA_STATES_TABLE = 32000`
(`src/core/limits.h:49`), `\b` does not move the budget question. The binding
constraint stays `states × ncls` (§3.4), which measures at 2.4% of its cap.

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

### 3.6.1 The D11 hazard this design must NOT walk into

**STRUCTURAL, and it is the most dangerous item in the module.** D11 rule 1: a
prefilter or self-loop skip advances `pos` without consulting accept flags, and
is unsound exactly when a state can accept at a position the skip passes. Today
that is only EOL positions, which is why the bound is `n-1`.

With a **class-indexed** accept, the accept bit varies *within* a skipped run —
same state, different bytes — so the existing skips
(`src/gen/emit_dfa.c:999-1005`) become unsound for `\b`/`(?m)$` patterns in a
way that is *not* fixed by D11's `n-1` bound.

**Proposed fix, and it costs nothing:** the skip set for state `K` is already a
256-entry bitmap (`<p>_fs<K>[]`). Intersect it at compile time with "and `K`
does not accept on this byte". The skip then stops at the first position where a
match could end, and D11 rule 2's evaluate-after-the-skip ordering covers that
final position. Still one bitmap, still one load, no new hot-path instruction.

**This must not be assumed.** D11's own record is that the first attempt at
M2.12 got rule 1 right, still produced 53 divergences over 27 patterns × 69
subjects, and that a later unconditional reorder cost **43%** on this exact
pattern. Wave B (§10) therefore carries a differential sweep over `\b` patterns
*with a live prefilter and skip states*, plus a sabotage row that disables the
intersection, as landing conditions.

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

**`(?m)^`** is true at `pos == 0` or when `s[pos-1] == '\n'`. Forward that is a
previous-byte context bit — cheap, and it requires changing the one hardcoded
`false` in the worklist (`src/ir/dfa.c:689`) into "this byte class is the
newline class". But the **reverse** machine is the problem, and it is the same
problem D8 recorded for plain `^`:

> `^` (N_BOT) needs a position-dependent BOT variant in the REVERSE machine
> (checked at pp == 0), which the DFA does not build — so `^` patterns stay on
> ENG_ATTEMPT. (D8)

`(?m)^` needs **that variant AND a byte-selected view** on top of it. It needs
strictly more than plain `^`, not less.

**Proposed, and deliberately conservative:** `(?m)^` routes to **ENG_ATTEMPT**,
exactly as plain `^` does today. `nfa_has_bot()` (`src/ir/nfa.c:668`) extends to
"contains any BOT-family node". A `(?m)^` pattern then inherits D8's known-slow
shape and nothing else changes. Building the reverse BOT variant would let both
plain `^` and `(?m)^` join ENG_UNANCH — that is [DD-7]'s parked item, and this
design **does not** unpark it, it only observes that a second consumer now
exists. Under ENG_ATTEMPT the start-state dispatch generalises from
`src/gen/emit_dfa.c:1113-1120`'s two-way `(start == 0) ? s0 : s1` to a
three-way test that also asks `s[start-1] == '\n'` — once per attempt, off the
inner loop.

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

### 5.2 Where the axis should be declared — a recommendation, and an OPEN QUESTION

DD-11 says decide "with the assertions module or a real consumer, whichever asks
first". `(?m)` is the first real consumer of the newline *concept* beyond `$`,
so this module is where the ask lands.

**Recommended: declare the namespace now, ship one member, refuse the rest by
their own names — the `--encoding` shape, exactly.** D58 ruling 2 made encoding
a **per-pattern scalar** (`pcrec_options` field + `--encoding`, never global);
`src/gen/enc/enc.c`'s table carries a row for `utf8` with **no backend on
purpose**, so that "a name pcrec knows but cannot compile must be refused BY ITS
OWN NAME, never fall out of a lookup as unknown" ([SR-10]'s single-namespace
rule). That precedent transfers without modification:

- `pcrec_options.newline` + `--newline=NAME`, per-pattern, never global.
- One table listing `lf`, `cr`, `crlf`, `anycrlf`, `any`, `nul`; only `lf` has
  an implementation; the rest are refused by name with the rendered menu.
- The `(*CR)`-family start-of-pattern verbs — refused cleanly today, per DD-11 —
  map onto **that same table**, so there is one namespace rather than two.

The cost is a table and a refusal. The benefit is that the axis stops being
implicit at exactly the moment a construct starts depending on it, and that
`(?m)`'s semantics have a name to bind to in the spec.

**The counter-argument is real and is why this is an OPEN QUESTION (§11 Q1):**
D18's earn-its-axis rule says a dimension is an axis only when a caller names
2+ values, and today nobody does. The honest framing is that this is not an
*optimisation* axis (D18's subject) but a *semantic namespace*, which is the
`--encoding` case rather than the OS-1..OS-4 case. Frank rules.

---

## 6. (iv) `\K` against the match-start contract and the reverse pass

### 6.1 Why the DFA structurally cannot do it

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
matches" — it is "where the winning backtracking path happened to be when it
crossed the `\K`". Subset construction erases exactly that. For `A\KB` with an
ambiguous `A`/`B` boundary there is no unique answer to recover, and PCRE2's
answer is determined by its backtracking order.

**So `\K` is VM-only.** This is not a new conclusion: `src/parse/registry.c:365`
already ships it as `VM_ONLY`, which is the one place in this design where the
implementation's existing text predicted the answer.

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

A third consequence to write into the spec: `\K` can make `caps[0][0] >
caps[0][1]`-adjacent reasoning wrong for callers who assume the reported start
is where matching began. It is not; it is where reporting begins. PCRE2 has the
same property and the same warning.

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
`Ast.k` is enum-typed (`AKind k;`, `src/core/internal.h:87`) and the build is
`-Wall -Wextra`, so `-Wswitch` should fire at any switch lacking the case and
lacking a `default:`. Measured rather than assumed — a probe enumerator was
added to `AKind`, the tree rebuilt, the warnings counted, and the edit reverted
(the tree was clean before and after):

| | sites that fail to compile-warn | |
|---|---|---|
| **new node kind** | **15 warnings across 6 files** — `src/gen/emit_vm.c` 5, `src/opt/revdet.c` 4, `src/opt/possessify.c` 3, `src/opt/mrl.c` 1, `src/opt/altcls.c` 1, `src/ir/nfa.c` 1 | every one is a site that would have to *decide* about multiline |
| **new flag** | **0** | a new struct field warns nowhere, by construction |

Sample, verbatim:

```
src/ir/nfa.c:492:5: warning: enumeration value 'A_EOL_M' not handled in switch [-Wswitch]
src/opt/altcls.c:378:5: warning: enumeration value 'A_EOL_M' not handled in switch [-Wswitch]
src/opt/mrl.c:90:9: warning: enumeration value 'A_EOL_M' not handled in switch [-Wswitch]
```

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
| `(?m)^` | `pos == 0 \|\| s[pos-1] == '\n'` |
| `(?m)$` | `pos == n \|\| s[pos] == '\n'` |
| `\G` | `pos == startpos` |
| `\b` | `wordtbl[s[pos-1]] != wordtbl[s[pos]]`, out-of-subject counting as non-word |
| `\K` | `caps[0][0] = pos` (trailed) |

`\b`'s `wordtbl` is the front-end-emitted table of §7.2, and it is the only row
with an encoding future.

**`\G` needs a value the anchored entry does not have, and the resolution is
not a workaround.** `<prefix>_search` takes `startpos` as a parameter, but the
anchored match-here entry `<prefix>_match(const rx_ctx *)` (`match_api.md` §3.2)
takes an `rx_ctx` whose fields are subject / len / pos / ncap / caps / user —
**there is no `startpos`**. So `\G` under the anchored entry can only mean
`pos == ctx->pos`, which is *trivially true at entry*.

That is the correct semantics rather than a degradation: PCRE2's `\G` is
relative to the start offset of the match call, and for an anchored match-here
the match call starts exactly at `ctx->pos`. The consequence to state in the
spec is that **`\Gfoo` compiled as a match-here entry is `foo`**, and that a
caller who wants pcrec's search-loop `\G` semantics must use
`<prefix>_search`. Wave D (§10) owes a test on both entries showing they differ
in exactly this way and no other, because a reader who assumes `\G` is
"anchored" will otherwise expect the match-here entry to refuse.

---

## 10. Proposed wave structure for [M6.2]

Ordered, disjoint, each with its own landing conditions. The ordering rule is
**cheapest-and-most-enabling first**, and the one deliberate inversion is that
the D47.5 gate refactor lands in Wave A — *before* `(?m)` is accepted — so it is
provably behaviour-preserving when it lands.

### Wave A — `\A` `\z` `\Z`, the third view, and the gate refactor

**Scope.** Parser rows for `\A`/`\Z` (aliases, §3.2) and `\z`; `closure`'s
`end_ok` bit and `make_state`'s third closure + `endvar` (§3.3); the
parse-time resolution of §8.2-§8.3 as a pure refactor (`A_BOL_M`/`A_EOL_M`
introduced but **unreachable**, since `(?m)` is still refused); possessify's gate
becomes a node-kind whitelist; `--features assertions` and §9.2's
enabled-but-unbuilt refusal.

**Why first.** No state-count risk, no hot-path change, and it builds the view
machinery `\b` and `(?m)` both extend. The gate refactor is provably a no-op
here and impossible to prove later.

**Tests.** `.rxt` cells for `\A`/`\z`/`\Z` including the three-way position
distinction (`"ab\n"`: `b\Z` matches at `(1,2)`, `b\z` does not — **verified
against libpcre2, NOT python, per §3.2.1, and the wave brief must carry that
constraint explicitly**); a structural check that a
`\z`-free pattern's artifact is **byte-identical** to the pre-wave artifact (the
zero-regression claim of §3.3, checked rather than asserted); the non-multiline
possessify controls of §8.7 must stay green; a corpus-wide byte-identity sweep
across the refactor.

### Wave B — `\b` `\B`

**Scope.** Word-set alphabet refinement (§3.4); the previous-byte context bit in
the state identity, forward and reverse (§3.5); the class-indexed accept table
(§3.6) emitted **only** when a next-byte-sensitive assertion is reachable at an
accepting position, so every existing pattern's artifact is unchanged; the
skip-set intersection of §3.6.1; the VM's `\b` on the shared `pcrec_cls_word_esc`
table (§7.2 item 3).

**Why second.** It is the module's only real engine work and everything else is
smaller. It must precede `(?m)` because `(?m)$` reuses the same two mechanisms.

**Tests.** A differential sweep of `\b`/`\B` patterns **with a live prefilter and
skip states** against both oracles — D11's record is that this is where a
silently-wrong skip hides for a whole milestone. A sabotage disabling the
skip-set intersection must go red. A structural check that no artifact contains
a second word-set spelling. `probe_ncls_refine.py` re-run against the built
compiler, with the measured deltas of §3.4 as the prediction to confirm or
refute.

### Wave C — `(?m)`

**Scope.** Accept the `m` letter (`src/parse/mod_modifiers.c:280`); `A_BOL_M`/
`A_EOL_M` become reachable; `(?m)$` on the Wave B machinery; `(?m)^` routed to
ENG_ATTEMPT via an extended `nfa_has_bot` and the three-way start dispatch
(§3.7).

**Why third.** It is the wave that makes Wave A's refactor load-bearing and Wave
B's mechanism reused. Landing it earlier would mean landing `(?m)` on top of a
gate whose unsound rows §8.1 identifies.

**Tests.** D47.5's obligation in full — §8.7's four cells, the non-multiline
control, **the scoped `(?m:...)` cell**, and the sabotage row. Plus a `(?m)^`
throughput note against D8's known-slow shape, so the ENG_ATTEMPT routing is
recorded with a number rather than a shrug.

### Wave D — `\G`

**Scope.** `start_max = startpos` (§4.1); the three-way start-state dispatch for
partial `\G` (§4.2); the VM's `pos == startpos`; the `match_api.md` §3.1
sentence of §4.3.

**Tests.** Contiguity semantics through the find-all loop (`\G` under the §3.1
loop must report only contiguous matches); `\Gfoo|bar` on both engines;
`a\Gb` never matching, agreeing with PCRE2; and the §9.3 pair — the same `\G`
pattern through `<prefix>_search` and through `<prefix>_match`, showing they
differ in exactly the documented way and no other.

### Wave E — `\K`

**Scope.** The second `forces_*` row in `src/opt/select_engine.c` (§6.2); the
trailed `caps[0][0] = pos`; the two hybrid rules of §6.3; `--engine=dfa` refusal.

**Why last.** It is the only construct with no DFA path, so it shares no
machinery with A–D and can move if scheduling requires.

**Tests.** A structural check that no `\K` artifact takes `caps[0][0]` from the
reverse pass; `\K` inside a quantifier (the undo-on-backtrack case);
`--engine=dfa` refusal; a differential against PCRE2 specifically, since python
`re` does not support `\K` — this wave is oracle-constrained and the brief should
say so.

**A D27-blinded corpus rides the module's close**, per the [M6.2] row.

---

## 11. Open questions for Frank

**Q1 — the newline axis (§5.2).** Declare `pcrec_options.newline` +
`--newline=NAME` now, per-pattern on D58's precedent, shipping `lf` only and
refusing the other five by name (and mapping the `(*CR)` verbs onto the same
namespace)? Or leave the axis implicit until a consumer asks? *Recommendation:
declare it.* This is a semantic namespace, not a D18 optimisation axis, and the
`--encoding=utf8` row is the exact precedent.

**Q2 — enabled-but-unbuilt diagnostics (§9.2).** During waves A–E the module is
enabled while some constructs are unbuilt. Confirm the shape: a per-construct
"not yet implemented" refusal naming the construct, distinct from "requires
module". Wording is D26 tier 3; the *structure* is a ruling because it decides
whether a half-landed module can miscompile.

**Q3 — `(?m)^` on ENG_ATTEMPT (§3.7).** Accept that `(?m)^` inherits plain
`^`'s engine and D8's known-slow shape, leaving [DD-7]'s reverse BOT variant
parked? *Recommendation: yes*, with the observation recorded that DD-7 now has
two consumers rather than one.

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
   `\G`-in-some-branches patterns at `startpos > 0` against PCRE2; a fourth
   reachable combination would show as a divergence at `startpos == 0`.

## 13. What this design does NOT measure

Named rather than discovered by the panel:

1. **The reverse machine's state cost for `\b`.** §3.5's prototype measures the
   forward, unanchored DFA only. The reverse DFA is built with `prune=false`
   (`src/core/compile.c:219`) and is where `eng_brep_design.md` found the whole
   quadratic compile cost of bounded repeats living. The reverse arm could be
   the expensive one and this document does not know.
2. **Compile-time cost.** Three closures instead of two, and a doubled state
   space before minimisation, cost pcrec's own compile time. Not measured.
3. **`(?m)^` throughput on ENG_ATTEMPT.** §3.7 routes it there on D8's
   precedent without re-measuring D8's shape.
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

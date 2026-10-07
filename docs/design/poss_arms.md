# [ART-POSS-ARMS] — two possessify arms, widened soundly

Lane `possarms`, 2026-10-07. DESIGN ONLY: nothing under `src/` changes on
this branch. The plan row is `docs/dev/plan.md` [ART-POSS-ARMS]. Its evidence
is `docs/dev/optloop/artrev/report_pilot.md` §5 item 1 and `generalize.md`
I6, and its rank is `docs/dev/optloop/round3_selection.md` 3a-2. The
possessify design of record is `eng_brep_design.md` §2, and the analysis is
`src/opt/possessify.c`. Probes, sweeps, the census instrument and the 10.46
transcript are in `poss_arms_measurements/` (see its CLAUDE.md).

**Headline.**

- **Arm A** (`\b` after a word-pure loop) is **SOUND once restated**. The row's
  wording ("a single-class repeat whose class is a subset of `\w` or `\W`") is
  refuted twice by measurement: under `-e utf8` with `(?i)`, and by the
  polarity of a multi-character body. The restated predicate is narrower in one
  place and wider in two.
- **Arm B** (a backreference's FIRST is its group's FIRST) is **SOUND once
  restated**. "The group" must be EVERY group the reference can read. The fold
  applies when the REFERENCE is caseless. "Non-nullable" must be read from the
  member bodies, not assumed. Two future modules (`verbs` for `(*ACCEPT)` and
  `branch-reset` for `(?|`) each break one conjunct, and each needs a tripwire.
- **A PRE-EXISTING MISCOMPILE blocks both arms** (§1). It is on main today: a
  quantifier inside a SUBROUTINE-CALL TARGET is possessified against the
  group's lexical follow. Both arms widen exactly that verdict, so they must not
  ship before the fix.
- **The give-up surface does NOT move one way** (§6). The STEPS and FRAMES
  give-ups can only disappear. A WORK give-up can APPEAR. This is a property
  of possessification in general, not of these arms. `tuning.md` §2.1's
  "changes no answer" is true only under default budgets.
- **Census (K35, §5):** with a scratch prototype of both arms, the DEFAULT
  route's frames move on **3 bench / 3 corpus** patterns. Over all
  `--engine=vm` compiles, arm A fires on 6 bench / 12 corpus and arm B on
  1 / 1. ARTREV's reader found 1 / 2 at 56% / 37% parser coverage, and its
  three are all in this list.
- **abi event: yes** (§9), by the [OPT-VEDGE] / [OPT-REQRUN-ENC] precedent.
  Program text, `RX_VM_STRATS` and the frame capacities move on the movers. No
  layout moves.

---

## 0. The verdict this extends, restated

`pss_verdict` (`possessify.c:823`) is a first-match ladder over one `A_REP`
`Q = X{m,n}`, with `base_ok = uniq(X) && !nullable(X)`:

| # | row | fires when |
|---|---|---|
| 1 | exact-count | `base_ok && m == n` |
| 2 | lazy decline | `base_ok && disjoint && lazy && may_end` (returns NO) |
| 3 | disjointness | `base_ok && disjoint` |
| 4 | default | NO |

Here `disjoint` means `FIRST(X) ∩ (FOLLOW(Q) ∪ ENCL) = ∅`. FOLLOW is built
from `first_of`. Both arms are changes to what `first_of` answers for two
node kinds, so neither adds a row to this table.

- **Arm B** changes `first_of`'s `A_BREF` arm. It is context-free.
- **Arm A** changes `first_of`'s `A_CTX` arm in two ways:
  - **A0**, a context-free refinement;
  - **A1**, a Q-relative refinement, sound only for row 3 on a greedy `Q`.

That is the main structural decision here: row 3 needs no `\b` special case.
§7 carries the lens argument.

## 1. PREREQUISITE — the call-target miscompile (pre-existing, on main)

The `A_CALL` arm of `pss_walk` (`possessify.c:958-986`) says: "the `A_REP`
nodes in the callee still get their verdict, computed at the callee's own
LEXICAL position where the enclosing follow is the real one". That is the
false premise. The callee's body is emitted once, with one
`u.rep.possessive` mark, and that mark was computed against the follow of the
GROUP's lexical position. A call site runs the same loop under ITS follow.
PCRE2 ≥ 10.30 calls are not atomic, so the loop must be able to give back
inside the call.

Measured: `--features recursion`, `--engine=vm` (the default route is the VM
anyway, since there are captures). Answers from 10.46 on ubuntubudu,
`witnesses_10.46.out`:

| pattern | subject | pcrec default | `-fno-possessify` | libpcre2 10.46 |
|---|---|---|---|---|
| `(a+)b(?1)a` | `abaa` | NOMATCH | (0,4) | (0,4) |
| `(a+)b(?1)a` | `aabaaa` | NOMATCH | (0,6) | (0,6) |
| `(?<n>a{1,3})b(?&n)a` | `abaa` | NOMATCH | (0,4) | (0,4) |
| `(?:(a+)b\|x)(?1)a` | `xaa` | NOMATCH | (0,3) | (0,3) |

The result is the same under `-fno-splice-calls`, so the linkage does not
matter.

**Two related findings, recorded here and not fixed here:**

1. **`atomic.c`'s free discharge has the same hole.** It asks the same verdict
   transparently. `((?>a+))b(?1)a` on `abaa` is NOMATCH in 10.46. pcrec
   default is right by accident: possessify re-marks the loop the discharge
   unwrapped. Under `-fno-possessify` the discharge still runs, and pcrec
   answers (0,4).
2. **PCRE2's own auto-possessification is not call-aware at the END OF THE
   PATTERN.** `(?:b(?R)a|a+)` on `baa` answers (1,3) in 10.46 by default and
   (0,3) under `no_auto_possess`. pcrec default answers (1,3), which agrees
   with 10.46. `-fno-possessify` answers (0,3). So `run_possdiff.sh`'s premise
   — "the denied build IS the shipped semantics" — fails against 10.46 on
   `(?R)` shapes. This is a D26 question for the panel: which side is pcrec's
   contract? It is also a candidate `upstream_issues.md` entry, since
   `no_auto_possess` changes an answer.

**Shape of the fix (for its own K-row, not this lane):** a group that is any
call's target gets its body walked with follow = ALL BYTES and
`may_end = true`. This is the A_ATOMIC arm's "self-contained" treatment with
the follow widened instead of emptied. For `(?R)`/`(?0)` the target is the
whole pattern, so the top-level follow also widens. The call graph
(`callgraph.c`) already knows the targets. The fix must also reach
`pcrec_poss_survey`, the discharge's question. **Both arms below assume it has
landed**, or else that they decline inside call targets, which comes to the
same thing.

## 2. Arm A — a context assertion in the follow

### 2.1 The fact

`A_CTX(C, fn)` covers `\b`, `\B` and every single-character lookaround
(`internal.h:484`). Its truth function `fn` is a 4-bit table indexed by
`(p << 1) | q`, where:

- `p` means the previous character is in `C`;
- `q` means the next character is in `C`;
- an absent character (subject start or end) reads as NOT in `C`.

Suppose the analysis knows a set `P ⊆ {0,1}` of possible `p` values at a
position. Then the gate can be passed only where the next character's
membership `q` is in

    Q(P) = { q : ∃ p ∈ P, fn(p, q) }

So the gate's sound FIRST value is "the characters with membership in `Q(P)`".
It is nullable exactly when `fn(p, 0)` holds for some `p ∈ P`, because end of
subject reads `q = 0`.

**Representation, for `first_of`.** `first_of` is in code-point space capped
at 0xFF. Members above 0xFF are represented by widening the whole set to all
256 (`pcrec_cls_bits_widen`). So:

- `S(P) = { c ≤ 0xFF : (c ∈ C) ∈ Q(P) }`;
- if `Q(P) = {0,1}`, keep today's answer (all bytes, non-nullable).

This keeps the change byte-identical for every gate it cannot narrow.

### 2.2 The two rows

| row | P | where it is sound | what it reaches |
|---|---|---|---|
| **A0** | `{0,1}` (nothing known about the left) | everywhere `first_of` is read: rows 1-3, the lazy conjunct, the free discharge's survey | lookaround-born gates whose `fn` ignores `p`: `(?=C)` gives `S = C`, non-nullable; `(?!C)` gives `S = ¬C`, nullable |
| **A1** | `{ pol_C(c) : c ∈ LAST(X) }` | ONLY row 3, ONLY for `Q` greedy with `m ≥ 1` and `base_ok`, ONLY for the gates `Q`'s own follow reaches at zero consumption | `\b` after a loop whose last characters share one wordness |

A0 needs no argument beyond §2.1. Its values are exact for every position,
end of subject included. `\b` and `\B` get nothing from A0, because their
`fn` depends on `p` and `Q({0,1}) = {0,1}`.

### 2.3 Why A1 is sound (the precise predicate)

**Premise (from `base_ok`, §2.3 of eng_brep).** With `X` admitting a unique
iteration and non-nullable, the loop's reachable exits from a given start form
a strictly increasing chain `e_m < … < e_K`. The greedy loop takes `e_K`
first. A possessive `Q` differs from a greedy one only if some retreat exit
`e_k` (`k < K`) leads to a match while `e_K` does not.

**At every retreat exit `e_k` with `k ≥ 1`:**

- the character before `e_k` is the last character of iteration `k`, so it is
  in `LAST(X)`;
- the character at `e_k` exists, and it is the first character of iteration
  `k+1`, so it is in `FIRST(X)`.

The loop's own characters are consumed, so neither side reads outside the
subject or before `startpos`. `m ≥ 1` makes `k ≥ 1` hold for every exit. With
`m = 0`, `e_0` is a retreat exit whose left character is whatever precedes
`Q`.

**The conclusion.** Every continuation from `e_k` that reaches the gate before
consuming a character tests that gate at `e_k`. It passes only if `s[e_k]`
has a membership in `Q(P)`. The FIRST of the continuation, computed with `P`
at those gates, is therefore a sound over-approximation of "the characters at
which the continuation can start at `e_k`". This is exactly the quantity
row 3's disjointness test needs. If `FIRST(X)` is disjoint from it (and from
`ENCL`), the continuation fails at every retreat exit. So `Q` lands at `e_K`
or fails, whichever way it is spelled.

**Why A1 is greedy-only, and why not row 2.** A1's value is not valid at
`e_K`, whose left character is still in `LAST(X)` but whose right character
need not be in `FIRST(X)`. It is also not valid at end of subject. Row 3 never
reads the continuation at `e_K`, while the lazy conjunct (row 2) reads
`may_end`, which is a statement about `e_K` too. So A1 is fed to row 3's
disjointness test and to nothing else. A lazy `Q` is left to A0 and row 2.

**Gates reached "at zero consumption".** A1's `P` is valid only at `e_k`
itself. So when `first_of` computes `Q`'s follow, `P` passes only through
nodes on their EMPTY path:

- along `A_CAT` past a nullable item (the empty path does not move);
- into `A_ALT` branches, `A_CAP`, and `A_ATOMIC` (FIRST is transparent there,
  as today);
- into `A_REP` iteration 1, and into iteration 2 after an empty iteration 1.

A gate reached after a consuming item sees a different left character. It
must get `P = {0,1}`, which is A0. That is the shape `fst_seq` already folds
in. `P` is a parameter of the fold. It is never a fact about a node.

**The enclosing-loop term.** `ENCL` is unioned UNGATED, exactly as today.
Re-entering an enclosing loop does not pass `Q`'s follow gate, and the
§2.2 / R24 H1 line stays load-bearing. Measured: `(?:\w+)+\b` declines and
does not diverge. `(?:\w+\bx)+` also declines, because `ENCL` contains
`\w`. That conservatism is inherited, not new, and nobody has measured
whether it costs anything.

**The full predicate, as one sentence.** For `Q = X{m,n}` greedy with
`m ≥ 1` and `base_ok`, let `P_C` be the polarities with respect to `C` of the
code points in the classes at `X`'s Glushkov LAST positions. Recompute `Q`'s
continuation FIRST with every `A_CTX(C, fn)` reached at zero consumption
valued `S(P_C)`, union `ENCL`, and grant row 3 if `FIRST(X)` is disjoint from
the result. Also require that `FIRST(X)` contain no code point above 0xFF.
That conjunct is belt and braces: `S`'s truncation at 0xFF is exact only
against a byte-range `FIRST(X)`. No witness reaches it today (§8), so it is a
stated invariant, not a sabotage row.

### 2.4 What the row's wording got wrong — the counterexamples tried

Each line below was a candidate rule, either the row's own wording or a
simpler one. Each was refuted by a libpcre2 equivalence check: the greedy
spelling under `no_auto_possess` against the possessive spelling, on the same
subjects. Every row was confirmed on 10.46 (`witnesses_10.46.out`).

| candidate | witness | greedy | possessive | the conjunct it buys |
|---|---|---|---|---|
| "a subset of `\w`" tested on the LITERAL | `k+\b`, `utf,i`, subject `k` U+212A | (0,1) | NOMATCH | wordness is read on the FOLDED code-point class. `(?i)k` under UTF folds to {k, K, U+212A}, and U+212A is not `\w` without UCP. pcrec is safe structurally, because `cls_casefold` folds at parse time and the class carries the code points. |
| `m ≥ 0` | ` \w?\b`, subject ` aa` | (0,1) | NOMATCH | `m ≥ 1`. The `e_0` exit has an unknown left character. |
| polarity read from FIRST(X) | `(?:a\.)+\b`, subject `a.a.` | (0,2) | NOMATCH | polarity is read from LAST(X), not FIRST(X) |
| a mixed LAST read as one polarity | `(?:a[a.])+\b`, subject `a.a.` | (0,2) | NOMATCH | `P_C` is the SET of polarities, and a mixed set gives `Q(P) = {0,1}`, which declines |
| `\B` treated like `\b` | `\w+\B`, subject `aa` | (0,1) | NOMATCH | none: for a pure `P`, `\B` admits the SAME wordness, which `FIRST(X)` meets, so A1 declines by itself |
| an impure class | `[a .]+\b`, subject `a ` | (0,1) | NOMATCH | none needed: `P = {0,1}`, so A1 declines |

What the row's wording gets right: `\B` and `m = 0` stay declined, and
nothing beyond the purity test is needed for them.

What the restatement makes WIDER:

- **Multi-character bodies.** `(?:ak)+\b` and `\B(x|ab){1,2}\b` are sound.
  The latter is `tests/startset/hybrid.rxt:280` and fires.
- **Lookaround-born gates through A0.** `[A-Za-z0-9.]+(?=@)` (bench
  `email-local-nodup`) and `\d+(?![\d.])` (bench `float-literal-bound`) both
  fire. A0 is sound for lazy and `m = 0` too (`real_gates.tsv`: 0 diverging
  over 1,665-9,631 subjects).

**Sweep, arm A** (`gen_a.py` → `eqcheck.py`, libpcre2 10.48 local):

- **Population:** 22,680 pattern pairs = 14 bodies × 6 quantifiers × 9
  follows × 5 wrappers × 6 modes (byte, `i`, `ucp`, `utf`, `utf,ucp`,
  `utf,i`).
- **Subjects:** 241 or 261 per pair, every string of length ≤ 2 over 9-10
  characters (`a k K x 1 _ space . é`, plus U+212A under UTF), plus 150 random
  strings of length 3-7.
- **Claims and divergences:**
  - **3,294 cells CLAIMED, 0 diverging.** Re-swept at length ≤ 3 plus 300
    random: 1,165-1,411 subjects per pattern, still **0 diverging**
    (`armA_claims_deep.summary`).
  - **7,413 non-claimed cells DIVERGE.** That is the non-vacuity of the
    controls. By factor: `m = 0` 3,670; `\B` 1,593; impure 3,774; enclosing
    loop 2,598; lazy 954.
- **Independence:** the CLAIM column is computed in Python from class
  membership asked of libpcre2 itself (`^(?:C)$` per character per mode). It
  is never computed from pcrec.
- **Caveat:** at length ≤ 2 the multi-character-body controls are weak.
  `(?:a\.)+\b` shows 0 divergence in the sweep, because `a.a.` is not
  generated, but diverges directly (the table above). The claims were re-swept
  at length ≤ 3. The controls were not.

### 2.5 Flags, one line each

- **caseless:** classes are folded at parse time and `C` is not affected
  (`\w` under `(?i)` is `\w`). The polarity is read from the folded class.
  This is the `k+\b` row.
- **utf:** `FIRST`/`S` are code points ≤ 0xFF, and anything above widens.
  Under `-e utf8` without UCP, `\w` is ASCII, so `\w+\b` fires.
- **ucp:**
  - Under `-e utf8 --ucp`, `\w` reaches above 0xFF, `FIRST(X)` widens, and
    A1 declines. That is a lost opportunity, not an error.
  - Under `byte --ucp`, `\w` includes Latin-1 letters. `C` comes from the same
    resolution, so `é+\b` fires correctly.
- **multiline:** irrelevant to the gate. A `$` after the gate is never reached
  at a retreat exit.
- **ungreedy `(?U)`:** read the node's parse-resolved `greedy` (D62). Never
  re-derive it.
- **`(?|`, duplicate names, backrefs:** irrelevant to arm A.
- **recursion / calls:** §1. Inside a call target the follow widens, so A1
  never sees a gate there.
- **empty subject / startpos:** a retreat exit always has both neighbours
  inside the loop's own text.

## 3. Arm B — a backreference's FIRST

### 3.1 The fact

PCRE2 reads a backreference `\n` (`A_BREF`, `refs[]`) as follows: the text
of the FIRST SET member of `refs[]`, in ascending group number, compared
caselessly if the REFERENCE is caseless (`u.bref.caseless`, D62). An unset
reference FAILS (`emit_vm.c:8409`; `PCRE2_MATCH_UNSET_BACKREF` is out of
scope, §3.3 of backrefs_design).

Every value a published capture can hold is a string some `A_CAP` node with
that number matched:

- captures written inside a subroutine call are RESTORED on return
  (`subroutines_design.md` §3.1);
- a negative assertion keeps no capture.

**The rule:**

    FIRST(\n)    = fold_ref( ∪_{g ∈ refs} ∪_{A_CAP c : c.no == g} FIRST(c.body) )
    nullable(\n) = ∃ such c with nullable(c.body)

- `fold_ref` is applied only when `u.bref.caseless` is set.
- An unset member contributes nothing, because it fails.
- Inside `FIRST(c.body)`, a nested `A_BREF`/`A_CALL`/`A_VAR` keeps today's
  widen. That is depth-1 resolution, and it also ends cycles such as
  `(a\2)(b\1)`.

### 3.2 Why each clause is there — the counterexamples tried

Same instrument as §2.4, over a 6-character alphabet (`a b x space A .`),
every string of length ≤ 5 plus 300 random strings, 9,631 subjects each:

| narrower spelling | witness | greedy | possessive | clause |
|---|---|---|---|---|
| no fold at a caseless reference | `(a)A+(?i:\1)`, subject `aAA` | (0,3) | NOMATCH | `fold_ref` keyed on the REFERENCE |
| the group's unfolded literal | `(?i:(a))A+\1`, subject `AAA` | (0,3) | NOMATCH | `FIRST(c.body)` is the folded class |
| the first member of a name run | `(?J)(?:(?<n>a)\|(?<n>x))x+\k<n>`, subject `xxx` | (0,3) | NOMATCH | union over ALL of `refs[]` |
| the first `A_CAP` with the number | `(?\|(a)\|(x))x+\1`, subject `xxx` | (0,3) | NOMATCH | union over every `A_CAP` with that number |
| "non-nullable group" assumed | `(a?)x+\1x`, subject `xx` | (0,2) | NOMATCH | nullability is read from the member bodies |
| unset reads as empty | `(?:(a)\|b)x+\1x` under `match_unset_backref`, subject `bxx` | (0,3) | NOMATCH | correct only while the option is out of scope |
| body non-nullable ⇒ capture non-empty | `(?=((*ACCEPT)a))x+\1x`, subject `xx` | (0,2) | NOMATCH | `(*ACCEPT)` closes a group early, even EMPTY |

The row says "closed, non-nullable group". Neither word survives as stated:

- **"Closed" is not needed.** A reference to a group that is open (the
  self-reference `(a|x+\1)+`), unset, or set in an earlier iteration still
  reads a string some member body matched, or fails.
- **"Non-nullable" is the wrong condition.** A nullable member makes the
  reference nullable, and the existing outward fold then adds what follows.
  That is sound and declines correctly (`(a?)x+\1x`).

**Sweep, arm B** (`gen_b.py` → `eqcheck.py`):

- 660 pairs: a 630-cell cross product (9 groups × 7 quantifiers × 5 tails × 2
  separators) plus 30 hand cells.
- **399 claimed, 0 diverging.** 220 non-claimed cells diverge.
- **Every narrower spelling in the table diverges.** Its 7 hand cells
  diverge 7 of 7, and the cross product's nullable-group rows diverge as
  well.
- The claim column applies the EXISTING ladder, lazy conjunct included. Arm B
  is context-free, so lazy loops benefit (`(a)x+?\1` is a claim and
  diverges nowhere).

### 3.3 Flags and the tripwires

- **caseless:** use the fold relation T2 selects for a LITERAL at the
  reference's scope. That is `pcrec_ast_class_from_cpset`'s own relation, so
  build a cpset from FIRST and publish it through that producer. Do not
  re-implement the fold.
- **SIDE FINDING, pre-existing:** pcrec's byte backend folds the 52 ASCII
  letters in `$_span_match_caseless` (`enc_byte.c:183`). It also folds
  Latin-1 for classes under `--ucp` (`pcrec_fold_latin1`), and libpcre2 folds
  Latin-1 in BOTH places. Witness: `(\xe9)\1` with `-i --ucp`, subject
  `\xe9\xc9`. 10.48 matches, and pcrec answers NOMATCH.
- **Why T2's relation is the safe choice anyway.** It is a superset of the
  seam's relation, so it is sound for today's compare and for the corrected
  one. A FIRST computed from the SEAM's relation would become unsound the day
  the seam is fixed.
- **utf:** a fold that leaves ASCII (k → U+212A, s → U+017F) or any member
  above 0xFF widens to all bytes. That is the existing convention.
- **duplicate names / `(?|`:** these are the union clauses above. `(?|` is
  unbuilt in pcrec (`--list-syntax`: `branch-reset … unbuilt`), so its clause
  is satisfied by construction today. Resolving `refs` → `A_CAP` by NUMBER,
  never by a single stored pointer, makes it correct on arrival too.
- **`(*ACCEPT)`:** module `verbs` is unbuilt (`--list-verbs`: "pcrec
  implements none of these yet"). When it gains a producer, `nullable(\n)`
  must become true for any group containing an `(*ACCEPT)`. That obligation is
  a TRIPWIRE, not prose: `tests/registry`'s producer check fails when `verbs`
  gains a producer while arm B lacks the clause, the way
  `check_engine_capability_tripwire` works.
- **`MATCH_UNSET_BACKREF`:** out of scope (§3.3 of backrefs_design). If it
  ever ships, an unset member contributes "nullable". That is the same
  tripwire, keyed on the option.
- **recursion / calls:** captures set in a call are restored. This is
  measured in the subroutines design, and `(?(DEFINE)(?<w>(a)))(?&w)x+\2` is
  a claim with no divergence. §1's prerequisite governs a `Q` INSIDE a call
  target.
- **`A_VAR`:** keeps today's widen. Its bytes are not from the subject
  (`internal.h`'s A_VAR note), so no group-FIRST argument applies.

## 4. The combined witness: `doubled-word`

`\b(\w+)\b\s+\1\b` has:

- `\w+`, followed by `\b`: arm A1 marks it, with `P = {in}` and `S = ¬W`;
- `\s+`, followed by `\1`: arm B marks it, with `FIRST(\1) = W`.

With both marked, the emitted program is frameless. The prototype
reproduces I8: textual `RX_PUSH(` sites go 3 → 1 and the artifact stamps
`RX_VM_FRAMELESS 1`. Its answers
equal the user-written `\b(\w++)\b\s++\1\b` in libpcre2 on the sweep, and both
spellings answer `the the cat` → (0,7) on 10.46.

## 5. Population (K35) — counted, not inherited

**The instrument.** `poss_census.py` drives a SCRATCH prototype of both arms
(`proto_census_instrument.patch`, environment-switched; NOT the
implementation and NOT reviewed as one). It runs over [ARTREV]'s own
populations, via `census.py`'s loaders:

- every pcrec-bench `bench/*/patterns/*.rx`: 345;
- every corpus `pattern`/`pattern-esc` block, distinct by (pattern,
  encoding, `-i`): 3,764.

For each pattern it reads:

- `possessify marked/total` from `--engine=vm --emit-ir`, under no arm, A, B
  and A+B;
- the default artifact's `RX_PUSH` site count and `RX_VM_FRAMELESS`, under no
  arm and A+B.

**Results** (`census.tsv.gz`, `census_firing.tsv`):

| | bench | corpus |
|---|---|---|
| arm A fires (`--engine=vm`) | 6 | 12 |
| arm B fires (`--engine=vm`) | 1 | 1 |
| either | 6 | 13 |
| DEFAULT route, frames move | **3** | **3** |
| DEFAULT route DFA (frames moot) | 3 | 10 |

The default-route movers:

- **bench `doubled-word`:** both arms, 3 push sites → 1, and it becomes
  FRAMELESS.
- **bench `email-local-nodup`:** A0, `(?=@)`, 4 → 3.
- **bench `wild-logparse-syslogbase-expanded`:** A1, 265 → 261.
- **corpus `wordb_vm.rxt:339`:** A1, 2 → 1, FRAMELESS.
- **corpus `startset/vmhat.rxt:381`:** B, 2 → 1, FRAMELESS.
- **corpus `startset/hybrid.rxt:280`:** A1 on `(x|ab){1,2}`, 4 → 3.

**Against ARTREV's count** (1 bench / 2 corpus):

- all three of ARTREV's patterns are in this list;
- the three new ones are outside ARTREV's reader grammar or its arm
  definition (A0's lookaround-born gates, a multi-character body);
- the counts come from two sources that share no code, and they agree on the
  overlap. That is the K35 cross-check.

**The arm-B population is ONE pattern per side.** That is a small reason to
carry a fold, a union and two tripwires. But arm B is the half that removes
`doubled-word`'s second loop's frames. Arm A alone leaves it framed.

**Differential on the real firing set.** `run_possdiff.sh`, driven through a
`--features all` shim with the prototype armed, on the 18 byte-encoded firing
patterns: **18 agreed, 0 diverged, 19,368 cells, 18 of 18 possessified**
(`possdiff_runs.txt`). On the designed family `possdiff_armpats.txt`:
36 agreed, 0 diverged, 17,526 cells.

## 6. The give-up surface — NOT one-way

The row says "changes-giveup-surface (one-way: a give-up becomes a correct
answer)". **That is true for two of the three counters.**

Measured on `doubled-word` (`workbudget.tsv`, `minwb.sh`, deterministic counts
with no timing):

| subject | budget | no arms | arms A+B |
|---|---|---|---|
| 200 words + `last last` (1.5 KB) | `--step-budget` 10…1000 | `steps` | answers (1490,1499) |
| same | minimum `--work-budget` | **1,070** | **2,565** |
| `a`×300 ` ` `a`×299 `b` | minimum `--work-budget` | 299 | 900 |

At `--work-budget=1500` the denied build answers and the armed build gives up
on WORK. **So does the user-written `\b(\w++)\b\s++\1\b`.** That makes it a
property of POSSESSIFICATION: the possessive scan is charged per iteration to
the WORK counter, while the backtracking form spent STEPS on retreats.
`tuning.md` §2.1 ("changes no answer") and the ARTREV repair counts were
measured under default budgets, where neither counter is near its limit.

**Spec sentences (D80), drafts for the build commit:**

- **`docs/spec/tuning.md` §2.1, appended:**

  > Answer identity holds under the default budgets. Under a caller-tuned
  > budget the rewrite moves the give-up surface, and in two directions. A
  > possessified loop keeps no resume frames and spends no backtrack steps on
  > retreats, so a `PCREC_ERR_STEPS` or frame-exhaustion give-up of the denied
  > build can only become an answer. Its forward scan is charged to the work
  > budget per iteration, so a `PCREC_ERR_WORK` give-up can appear where the
  > denied build answered. Measured: `\b(\w+)\b\s+\1\b` on a 1.5 KB subject
  > needs a work budget of 1,070 denied and 2,565 possessified. The
  > `[ART-POSS-ARMS]` arms (§2.x) widen which loops this applies to and add no
  > third direction.

- **`docs/spec/limits.md` §7, a new bullet:**

  > **Possessification trades one counter for another.** The step and work
  > budgets are not independent of the optimizer. Any change to which loops
  > `src/opt/possessify.c` marks (a new arm, `-fno-possessify`, or a
  > call-target exclusion) moves a STEPS or FRAMES give-up towards an answer
  > and a WORK give-up towards appearing. A caller who has tuned
  > `--work-budget` to the edge should re-check it after a possessify change,
  > as §7 already advises for `K`. `<PREFIX>_VM_STRATS` shows whether the
  > artifact carries a possessive loop.

## 7. Lenses

**Sibling of a family? Yes, twice. The recommendation is to share the two
facts, not the walks.**

**The FIRST-byte family.** `decision_families_survey.md` §3.7 lists five
derivations of "first bytes":

- `startset.c`'s `start_set`;
- `kset_walk`;
- the DFA escape set;
- `possessify.c`'s `first_of`;
- the K50 check.

D148 Q4 ruled that `first_of` is NOT merged with `start_set` (different tier,
different question). This note does not reopen that.

Both arms, though, introduce a sub-fact that is not possessify's:

- **A0/A1 ask "which next characters does a context gate admit, given what is
  known about the previous one".** `startset.c:126` treats `A_CTX` as
  transparent. A0 would narrow a start set behind `(?=C)` exactly as it
  narrows a follow. Recommended primitive: `pcrec_ctx_admits(const Ast *ctx,
  unsigned pmask, PcrecCpSet *out, bool *at_end)`. It is a code-point fact
  beside `pcrec_cpset_*`, and each walk widens it to its own tier.
- **B asks "which `A_CAP` nodes can this reference read".** That is a pure
  tree fact (number → node list, with `(?|` and duplicate names included).
  `startset.c`, `req.c` and `revdet.c` each answer `A_BREF` with
  "all bytes, nullable" today. Recommended: a facts-layer record
  (`src/facts/`, D120/D126) of the capture-number → `A_CAP` list, which
  possessify reads first. A second reader is then a one-line change.

That makes three walks (possessify, startset, revdet) that could read each
primitive, which is the "~3 members" threshold (memory
`pcrec-forest-for-trees`). **Recommended:**

- build both primitives with the arms;
- make possessify their only reader in the build commit;
- file one row for the startset reader, with its own census.

**General mechanism, not special case** (memory
`pcrec-general-mechanisms-not-special-cases`):

- neither arm adds a ladder row or a `\b` case;
- A0 and A1 are one function `S(P)` with one parameter, and A1's parameter
  comes from the Glushkov LAST set `gk_build` already computes;
- B is the existing `first_of` asked of the group bodies.

**First-match table** (memory `pcrec-decisions-as-first-match-tables`): the
ladder in §0 is unchanged. A1 is an INPUT to row 3, not a row.

**Engine hat / applicability:** VM only, because possessify is VM only.
Under stage 3 the DFA rows are moot (10 corpus / 3 bench firing patterns are
DFA-routed). Algorithmic (D119).

**G1 interaction** (round3_selection.md (c) item 6, Q4 RULED): 3b-5's
reverse-inner G1 must read the PRE-possessify tree. The arms enlarge the set
of `u.rep.possessive` marks, and `doubled-word` becomes fully possessive. So
the hazard grows, and the panel should check that G1 reads no
`possessive` field.

## 8. Checks, sabotage, harness

### 8.1 `run_possdiff.sh` extension plan

Today the harness has three gaps for these arms.

1. **It cannot compile either arm's shapes.** It passes no `--features`, and
   both `\b` (module `assertions`) and `\1` (module `backrefs`) need a module.
   Measured: 36 of 36 arm patterns were refused until a shim added
   `--features all`. **Fix:** an optional leading `flags<TAB>` column in the
   pattern file, defaulting to empty, so the existing 155-line
   `patterns.txt` is untouched. Each row also gets an encoding (`-e utf8`)
   and `--ucp` option.
2. **Its subject generator cannot discriminate the arms.**
   - The alphabet is the pattern's own characters minus metacharacters, so
     `\b(\w+)\b\s+\1\b` gets the alphabet `bsw` and no non-word character
     except the fixed `q` and `\n` subjects.
   - Measured: a sabotaged prototype with the fold removed (S563's plant) is
     **MISSED** (7 agreed, 0 diverged). `aAA` is never generated.
   - **Fix:** add these families:
     - (a) for any pattern with `\b`/`\B`/a lookaround: one word and one
       non-word representative from each side of `C` (space, `.`, `_`, a
       digit; under `-e utf8`, `é` and U+212A);
     - (b) for a backreference: `w SEP w`, `w SEP w[:-1]`, `w w`, and
       `w SEP flip_case(w)` for alphabet tokens `w`;
     - (c) under `(?i)` or a caseless reference: every subject case-flipped.
3. **Non-vacuity per arm.** The existing control counts patterns with any
   possessive loop. Each arm needs its own "this ARM fired" count. That
   requires the deny bit (§9): diff the possessive counts of armed and
   arm-denied builds, and fail if an arm's population is 0.

**Acceptance for the extension:** each of S560-S565 below is DETECTED by
`run_possdiff.sh` on its own witness. S563 is the one today's generator
misses, which is the measured reason for item 2.

### 8.2 Sabotage rows (S560-S565 reserved; the highest on main is S556)

| id | plant | witness (10.46-confirmed) | detector |
|---|---|---|---|
| S560 | A1 drops `m ≥ 1` | ` \w?\b` on ` aa` | possdiff (DETECTED by the prototype: 2 FAIL) |
| S561 | A1 reads polarity from FIRST(X) | `(?:a\.)+\b` on `a.a.` | possdiff (needs `a.a.`: family 2a) |
| S562 | A1 collapses a mixed LAST to one polarity | `(?:a[a.])+\b` on `a.a.` | possdiff, family 2a |
| S563 | B ignores `u.bref.caseless` | `(a)A+(?i:\1)` on `aAA` | possdiff, family 2c (MISSED today, measured) |
| S564 | B reads only `refs[0]` | `(?J)(?:(?<n>a)\|(?<n>x))x+\k<n>` on `xxx` | possdiff (DETECTED by the prototype: 2 FAIL) |
| S565 | B forces `nullable(\n) = false` | `(a?)x+\1x` on `xx` | possdiff + `.rxt` cell |

**[MECH-REACH] notes:**

- **Each witness must be in the swept population.** Put the six witnesses in
  `tests/possessify/patterns.txt` (with the flags column) AND as
  oracle-verified `.rxt` cells in `tests/possessify/possessify.rxt`. The
  `.rxt` half is the oracle-independent detector, because possdiff compares
  pcrec with pcrec.
- **The "FIRST(X) above 0xFF" conjunct (§2.3) has no witness**, so it gets no
  row. It is stated as an invariant.
- **The §1 prerequisite needs its own sabotage row** in its own K-lane's
  range: drop the call-target exclusion, witness `(a+)b(?1)a` on `abaa`.

### 8.3 K65-style give-up check

This is a new section of `tests/possessify/`, not a mech row. For every
census-firing pattern plus the six witnesses:

- **Builds:** armed versus arm-denied (the deny bits, §9).
- **Subjects:** the extended generator's set, plus one long subject per
  pattern.
- **Budget ladders:** `--step-budget` {1, 10, 100, 1000}, `--work-budget`
  {10, 100, 1,000, 10,000} and `--backtrack-frames` {1, 4, 16}.
- **Classify each cell** as SAME, ANSWER→GIVEUP or GIVEUP→ANSWER, per
  counter.

**Assertions:**

1. Where both builds answer, the answers are identical. This is the
   answer-identity half.
2. Zero ANSWER→GIVEUP cells under STEPS and FRAMES.
3. ANSWER→GIVEUP under WORK is COUNTED and must be > 0 on `doubled-word`.
   That is the positive control proving the check can see the direction §6
   documents. Its count is printed, not floored.
4. GIVEUP→ANSWER > 0 somewhere. This is non-vacuity.

**Independent control:** S560 must turn assertion 1 red. That keeps a
give-up-direction check from passing on a broken arm. This is the lesson of
learnings.md §3 GIVEUP1: `run_axes.sh` counted a one-sided give-up as
"budget-bound".

## 9. abi, flags, spec, docs — what the build commit carries

**abi event: YES.**

- **Precedent:** [OPT-VEDGE] (abi 56 → 57) and [OPT-REQRUN-ENC] (37 → 38)
  were analysis relaxations that moved emitted program text on their movers
  and were bumped. This is the same class.
- **What moves on a mover:**
  - the loop's emitted body (no `RX_PUSH` / retreat for a marked loop);
  - `<PREFIX>_VM_STRATS`;
  - `rx_info`'s `frame_capacity` / trail VALUES;
  - `RX_VM_FRAMELESS` and the entry shape where the program becomes
    frameless.
- **What does not move:** no struct offset and no `rx_info` member. Every
  non-mover differs in its abi digits only.
- **The site list is found BY GREP at build time** (D94). It is not
  enumerated here.

**Deny bits — recommended: one per arm**, `-fno-poss-ctx-follow` (A0+A1) and
`-fno-poss-bref-first` (B). They are D46 deny-only bits, masked out of
`rx_info.flags` by the derived strategy mask ([FLAGBITS]). Reasons:

1. The two arms are independent facts with independent refutation surfaces.
   A bit each gives each its own `make test-axes` row and its own non-vacuity
   count (§8.1 item 3).
2. The denied build is the byte-identity control for every non-mover.
   `-fno-possessify` is too coarse for that, because it also removes every
   pre-existing mark.

Each bit's `--list-axes` row and its `tuning.md` §2.x entry are D80 hunks.
This is **Q2 for the panel**: whether A0 deserves its own bit apart from A1.

**Spec (D80):**

- §6's two sentences;
- the new `tuning.md` §2.x entries for the bits;
- `match_api.md` §6's abi change-log paragraph;
- `eng_brep_design.md` §2.5 (the assertion rule) gains a pointer here,
  because its statement "an assertion in the follow widens FOLLOW to all
  bytes" stops being true for `A_CTX`.

**Docs:**

- `src/opt/CLAUDE.md`'s possessify entry;
- the `possessify.c` header's conjunct list (two new lines, each with its
  witness);
- `tests/possessify/CLAUDE.md` (the flags column and the new families).

## 10. The three standing questions

1. **Measurement regime. RELEVANT, narrowly.**
   - This lane measured no timing.
   - The -57.6% is ARTREV's: ubuntubudu x86, gcc, 7/7 pads, dense and sparse
     WIN, throughput regime.
   - The census, the sweeps and the work-budget minimums are DETERMINISTIC
     COUNTS, independent of box and load. They depend on the subject (the
     §6 minimums are per-subject) and on the compiler revision (the census
     is at bcb7b128).
   - A latency regime could not flip the decision, because the change
     removes machinery. The WORK-budget direction is the one regime-like
     dependence, and §6 states it.
2. **Independent control. RELEVANT.**
   - **The soundness sweeps** check libpcre2 against libpcre2: the greedy and
     possessive spellings of one pattern. The CLAIM column comes from Python
     with class membership asked of libpcre2. No pcrec code is in that loop.
   - **possdiff** checks pcrec against pcrec-denied. It shares a source with
     the subject, and is kept because it is the only check of the EMITTED
     code. The `.rxt` cells (§8.2) are the oracle-side complement.
   - **The census** is counted by a prototype that will share a source with
     the build. K35's guard is the cross-check against ARTREV's independent
     reader: it agrees on the overlap and the new members are explained. The
     build must re-count with its own `--emit-ir` and diff against
     `census_firing.tsv`.
   - **Sabotage reach:** two of six rows were run against the prototype and
     DETECTED. One (S563) was MISSED by today's harness, which is the
     extension's acceptance test.
3. **What moves when data is regenerated. NOT RELEVANT as data.** No table,
   calibration or generated file is introduced. The emitted-byte movement is
   the abi event in §9. The census TSV is a measurement, re-run, not
   regenerated into anything.

## 11. Questions for the D6 panel

- **Q1. §1 first?** Recommend: yes. File the call-target miscompile as a K
  row with its own lane. The arms are built on top of it, or decline inside
  call targets if they land first.
- **Q2. One deny bit per arm, or a third for A0?** Recommend: two bits (A0
  rides with A1). A0 is the context-free half of the same function.
- **Q3. Should A0 ship at all?** It is not in the row's text. Its population
  is bench `email-local-nodup` and `float-literal-bound` (DFA-routed by
  default, so one VM mover), and it is sound for lazy loops and `m = 0` too.
  Recommend: yes. It is the same function, and leaving it out would be the
  special case.
- **Q4. `(?R)` against PCRE2's auto-possessify (§1 item 2).** Which answer is
  pcrec's contract on `(?:b(?R)a|a+)`? Recommend: 10.46's default (1,3),
  recorded in `upstream_issues.md`. The §1 fix must then KEEP the top-level
  follow for `(?R)` as PCRE2 does, and widen only for numbered and named call
  targets. That needs its own measured cells.
- **Q5. The seam's Latin-1 fold gap (§3.3).** File it as a separate K row.
  Arm B uses T2's superset relation, so it is sound for both states of the
  seam.
- **Q6. Tripwires for `verbs` / `branch-reset` / `MATCH_UNSET_BACKREF`.**
  Agree to the registry-producer tripwire form.
- **Q7. Share `pcrec_ctx_admits` and the reference-reads fact (§7) in the
  build commit, or later?** Recommend: in the build commit, with possessify
  as the only reader.

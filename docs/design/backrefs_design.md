# Module `backrefs` — design

**[M6.5.1]**, the design gate in front of [M6.5.2]. Covers the numeric
backreferences `\N` for any N (R32 E3: references above `\99` exist and are
measured to `\812`) with PCRE2's octal disambiguation, the `\g`
spellings, the `\k` spellings, `(?P=name)`, and — per the [M6.5] row's own
ruling — **`(?J)`/DUPNAMES, which is implemented here**.

**STATUS: PROPOSED.** No `src/` change belongs to this lane. Nothing here is
built. The D6 panel (R32) reviews this document before [M6.5.2] starts.

**LANDING ORDER.** [M6.4] (`atomic-groups`) lands FIRST and owns the first
implementation of `engine_m4.md` §5.2's `discharge` socket. This module's
finite-language expansion would be that socket's SECOND customer — and §6
below recommends it NOT be built in this module at all, on measured grounds,
so the cross-dependency reduces to reading whatever shape [M6.4] lands.

---

## 0. How to read this

### 0.1 Claim marking

Adopted verbatim from `assertions_design.md` §0.1, which took it from
`engine_m4.md` §0.1, so the panel reads one vocabulary:

- **MEASURED** — a number or behaviour from an instrument, with its source
  cited. If the source is not cited it is not MEASURED.
- **RULED** — settled by a D-number in `../dev/decisions.md` or by a plan-row
  ruling of Frank's. Consumed here, not re-litigated.
- **STRUCTURAL** — true by inspection of code that exists today, file and line
  cited. Weaker than MEASURED (no instrument ran), stronger than BELIEVED.
- **PROTOTYPE** — produced by a model or a throwaway build, not by the shipped
  compiler. Marked wherever it appears.
- **BELIEVED** — the author's reasoning, unmeasured. Every BELIEVED claim in a
  load-bearing position is repeated in §13 with the experiment that refutes it.

### 0.2 The design in one paragraph

A backreference is **not a class-membership test**, and every consequence in
this document follows from that one fact. Everything pcrec compiles today —
literals, classes, `.`, quantifiers, alternation, the assertions module's
whole surface — is either a 256-bit bitmap or a position predicate, which is
why caselessness folds away at parse time (D23), why the DFA can carry every
construct, and why the encoding seam has needed exactly one residual entry so
far. A backreference compares **subject text against subject text**, at a pair
of positions the *backtracking state* holds at that instant. So it: (1) needs
a new AST kind and a new emitted operation in the VM, reading the two capture
slots through the trail discipline that already exists (§3); (2) has a
caseless form that cannot fold into anything and must therefore become the
[M5-SEAM]'s **second** residual entry — the one D58 said would be the seam's
validation event, and it forces an interface change (§4); (3) is
**VM-forcing** for every pattern the module can actually ship, because the
finite-language expansion's only possible customer is a `--no-captures` build
and a backreference pattern is capture-bearing by construction (§6); and (4)
**cannot have a DFA prefilter**, because a backref-erased approximation is a
genuine superset whose leftmost span differs from the true one on a large
fraction of subjects — measured, §7. Two things are NOT consequences of that
fact and are ordinary parser work: PCRE2's context-sensitive octal
disambiguation (§5, measured cell by cell), and DUPNAMES (§8), whose
resolution rule turns out to be **first-of-the-name-run-by-number that is
SET**, and whose reflection-table layout turns out to be **exactly libpcre2's
own `PCRE2_INFO_NAMETABLE` order** — both measured, neither invented.

### 0.3 Measurements this lane produced

All under `backrefs_measurements/`, probes committed, outputs archived with
their repo commit by `probes/archive.sh`.

| instrument | kind | what it answers |
|---|---|---|
| `probes/br_oracle.py` | not a probe, the ORACLE HELPER | borrows `../eng_brep_measurements/probes/pcre2_ctypes.py` and adds compile-error NUMBERS, the name table, and three option bits — each **behaviourally self-checked at import** |
| `probes/probe_br_semantics.py` | MEASURED, both oracles | §3: unset / empty / self / forward / quantified / nested-rewrite semantics, and the python divergences (§12) |
| `probes/probe_octal_rule.py` | MEASURED, libpcre2 + in-pcrec | §5: the whole `\N` disambiguation, and pcrec's base-tier class answers as the must-not-change baseline |
| `probes/probe_spellings.py` | MEASURED, both oracles | §2: every spelling, and the backref-vs-subroutine split of the `\g` doorway |
| `probes/probe_dupnames.py` | MEASURED, libpcre2 | §8: the name table's order, the refusal matrix, and the resolution rule |
| `probes/probe_caseless_fold.py` | MEASURED, libpcre2 + in-pcrec | §4: which bytes the compare folds, where `(?i)` is read, and whether the compare is length-preserving |
| `probes/probe_prefilter_cost.sh` | MEASURED, artifact benchmark | §7: what VM-only search costs, on the SHIPPED compiler's own prefilter axis |
| `probes/probe_erasure_hazard.py` | MEASURED, libpcre2 | §7: that the erasure is a superset (sound) and that its SPAN is not (unusable for the hybrid) |
| `probes/probe_expand_cost.py` | MEASURED, in-pcrec | §6: the finite-language expansion compiled by the shipped compiler, and the DECLINE boundary bisected |

**`probes/archive.sh` is the ONLY writer of `out/`.** That rule is inherited
from R30 M7, where a hand-written header imitating the archiver was named "a
sharper instance of a control sharing a source with what it controls than
anything the archiver guards against". No header in this directory was
hand-written; every one of the nine files in `out/` came out of `archive.sh`.

**Four defects this lane's own instruments had, found by running them.** They
are recorded because each is a shape this project keeps cataloguing, and
because a probe that reports confidently wrong numbers is worse than none:

1. `probe_caseless_fold.py`'s in-pcrec arm reported **all 256 bytes
   disagreeing** on its first run. It was diffing emitted C past a filter that
   stripped comments only, so it was measuring the `.flags` stamp (`-i` sets
   `PCREC_CASELESS`) and the embedded pattern text, never a transition table.
   The corrected filter reports **zero** disagreements.
2. `probe_prefilter_cost.sh` derived its erased patterns with
   `sed 's/\\1//'`, which erases a backreference to **epsilon** — a different
   and *unsound* approximation from the one APPROACH §2 names. The population
   is now written out in full.
3. The same probe used `echo "$IDIOMS"`, and `/bin/sh`'s `echo` **interprets
   backslash escapes**: `\b` became a backspace byte, so the dupword arm
   silently compiled a pattern with both word boundaries gone. `printf '%s\n'`
   is the fix, and it is load-bearing rather than style.
4. `probe_erasure_hazard.py` reported the `tag` family at **100% selectivity
   over a population containing zero positives** — the vacuity shape. It now
   carries a VACUOUS guard and a structured subject generator for families
   whose positives a random walk never produces.

A fifth is not a defect but a result: `probe_expand_cost.py` crashed on
`([a-z]{4})\1`'s 4.1 MB expansion with `E2BIG`. That is now reported as a row
("cannot be passed at all"), because "the expansion cannot be handed to a
compiler through argv" is a genuine cost of the rewrite §6 declines.

---

## 1. Premises, re-verified on HEAD rather than inherited

Each of these was checked against this worktree's build rather than taken from
a document, because a design whose premises are quotations inherits every
staleness in the quoted text.

| # | premise | verification |
|---|---|---|
| P1 | Every backref spelling refuses today, naming module `backrefs` | MEASURED: `x\0`, `x\1`, `(a)\1` → "`\N` (backreference/octal) requires module 'backrefs'"; `\g1` → "`\g` requires module 'backrefs'"; `\k<n>` → "`\k` requires module 'backrefs'"; `(?P=n)` → "`(?P...)` requires module 'backrefs'" |
| P2 | `FEAT_BACKREFS` exists and has no producer | STRUCTURAL: `src/core/internal.h:753` (`1u << 2`); no `mod_backrefs.c` in `src/parse/` |
| P3 | The ten digit rows are `M_backrefs`, `RD_MODULE_OCTAL`, and `\1`..`\9` are `VM_ONLY` while `\0` is `ANY_ENGINE` | STRUCTURAL: `src/parse/registry.c:512-521`, macros at `:207-214` |
| P4 | `\k` and `\g` are `ESC_CLASS_SCALAR` rows — a base class port giving the literal letter, no atom port | STRUCTURAL: `src/parse/registry.c:444-445` |
| P5 | `(?P=n)` is a `GROUP_T` row, `M_backrefs`, `VM_ONLY` | STRUCTURAL: `src/parse/registry.c:611` |
| P6 | The class position is BASE syntax and already implements PCRE2's octal exactly | MEASURED, `out/octal_rule.txt` axis D: 12 cells, `[\1]`=0x01, `[\10]`=0x08, `[\8]`='8', `[\377]`=0xff, `[\400]` refused — pcrec's base tier agrees with libpcre2 on all 12 |
| P7 | The VM's mutable state is one flat `slot_values` array, a `resume_stack` of frames and an exact-undo `trail` | STRUCTURAL: `src/gen/emit_vm.c:4667-4676` (the `rx_run_state` type), `:4771-4790` (`_TRAIL`/`_SET`/`_PUSH`), `:5075-5081` (the fail label's rewind loop) |
| P8 | `forces_captures` sends every captures-wanted group-bearing pattern to the VM | STRUCTURAL `src/opt/select_engine.c:84-92`; MEASURED: `(abc)(abc)` stamps `RX_ENGINE "vm"`, `RX_ENGINE_WHY "capture group at pattern offset 0"`, while `--no-captures` on the same pattern selects the DFA (`out/expand_cost.txt` §0) |
| P9 | `--engine=vm` suppresses the prefilter; `auto` attaches it | MEASURED: `(a+)b` stamps `RX_VM_PREFILTER "hybrid"` by default and `"none"` under `--engine=vm` |
| P10 | The `\K` row is the socket's only real customer today, and `forces_kreset` walks the AST | STRUCTURAL: `src/opt/select_engine.c:160-166`, `:176-179` |
| P11 | pcrec's ASCII fold is 52 bytes, applied at class-construction sites | STRUCTURAL: `src/parse/parse.c:223-230` (`cls_casefold`), called at `:236`, `:251`, `:566`; RULED D23 |
| P12 | `mrl.c` already decides what a backreference contributes: **0**, by an explicit written inheritance | STRUCTURAL: `src/opt/mrl.c:32-35` ("Lookaround, backreferences and `(*ATOMIC)` have no producers today; when they gain one, each contributes 0 here until someone measures otherwise") |
| P13 | `(?J)` reads `unbuilt` in D65's built-status column today | STRUCTURAL: `docs/design/registry_built_status_memo.md`'s implementation record — "exactly one — `(?J)` … reads `unbuilt`"; `docs/pcre2_compliance.md:1643` |
| P14 | A residual seam entry may NOT be referenced from any file-scope function body but its own and `main()` | STRUCTURAL: `tests/codegen/run_codegen_tests.sh:895-995`, the `[M5-SEAM]/DD-12(7)` check; sabotage `tests/mech/sabotages/S68_residual_in_hot_loop.sh` |

P14 is the premise that changes this design, and §4.4 is where it is dealt
with rather than worked around.

---

## 2. The construct table — every spelling, and who owns it

MEASURED, `out/spellings.txt` (25 spellings against libpcre2 10.46 and python
3.14.4, each with a discriminator subject chosen so "it compiled" is never
mistaken for "it is a backreference").

| spelling | libpcre2 | is it a backreference? | this module? | python `re` |
|---|---|---|---|---|
| `\1` .. `\9` | ok (err 115 if no such group) | yes | **yes** | yes |
| `\10` .. `\99` | ok, or octal — §5 | yes when the count allows | **yes** | yes |
| `\100` and above | ok, or octal — §5 | yes when the count allows (measured to `\812`) | **yes** | yes |
| `\8N` / `\9N` (any N) | ok | **always decimal**, never octal — §5 rule 3' | **yes** | yes |
| `\g1`, `\g10` | ok | yes | **yes** | no (`bad escape \g`) |
| `\g{1}`, `\g{10}` | ok | yes | **yes** | no |
| `\g{-1}`, `\g-1` | ok | yes, relative back | **yes** | no |
| `\g{+1}` | ok | yes, relative FORWARD | **yes** | no |
| `\g{name}` | ok | yes | **yes** | no |
| `\g{0}` | **err 115** | — (no group 0) | refuse, err-115 class | no |
| `\g<1>` `\g'1'` `\g<name>` `\g'name'` | ok | **NO — a SUBROUTINE CALL** | **no: module `recursion`** | no |
| `\k<name>` `\k'name'` `\k{name}` | ok | yes | **yes** | no |
| `\k<1>` `\k{1}` | **err 144** | — (a name may not start with a digit) | refuse | no |
| `\kname` | **err 169** | — (a delimiter is required) | refuse | no |
| `(?P=name)` | ok | yes | **yes** | **yes** |
| `(?P=1)` | **err 144** | — | refuse | no |

**The `\g` doorway carries two different constructs and today's registry has
one row for it.** MEASURED discriminator (`out/spellings.txt`, the SUBROUTINE
block): a subroutine call re-runs the group's *pattern*, so `^(a|b)\g<1>$`
matches `"ab"` at (0,2); a backreference compares the captured *text*, so
`^(a|b)\1$`, `^(a|b)\g{1}$` and `^(a|b)\g1$` all report **no match** on the
same subject. `\g<name>` matches; `\k<name>` does not. So the split runs
exactly along the DELIMITER: braces and bare digits are backreferences,
angle brackets and single quotes are subroutine calls.

**Consequence for the registry (§9):** the `\g` row's own note today reads
"backreference by number or relative position: `\g1` `\g{-1}` `\g{name}`"
(`registry.c:445`) — correct for the half it names, silent about the other
half. This module claims the backreference half and must leave a truthful
refusal naming module `recursion` for `\g<` and `\g'`, exactly as
`registry.c:612`'s `(?P>n)` row already does for the `(?P` doorway.

---

## 3. The VM lowering (charter (a))

### 3.1 The one new AST kind, and its two new fields

```c
A_BREF,      /* a backreference: compare the subject at the cursor against
                the text some earlier group captured, AT THIS INSTANT of
                the backtracking state */
```

with, on `struct Ast`:

```c
    const int *refs;   /* A_BREF: the candidate group numbers, ASCENDING */
    int        nrefs;  /* A_BREF: how many. 1 for every reference that is
                          not to a DUPLICATED name (§8) */
    bool       caseless;  /* A_BREF: parse-resolved, D62 */
```

Three decisions, each with its reason:

**(a) A KIND, not a flag on `A_CLASS`.** D62's principle as `\z`, `\b` and
`\G` each applied it: node kinds encode STRUCTURE, node fields encode
parse-resolved modifier state. A backreference is not a class under an
option — it consumes a *variable* number of bytes decided at match time,
which no `A_CLASS` can express. `src/opt/mrl.c`'s exhaustive-switch-no-default
rule then earns its keep for the fourth time: adding this member is a compile
error THERE (`src/opt/mrl.c:19-24`), and `mrl.c:32-35` has already written
down what the decision is (**0**, P12). It is **not** a compile error
everywhere — `vm_det_seq` (`emit_vm.c:880`) is one of the four documented
`default:` sites and declines silently (correctly, §3.6) — so §3.6 and §11.4
enumerate the sites the alarm does not cover rather than assuming it does.

**(b) `refs`/`nrefs` rather than a single `capno`, UNIFORMLY.** A reference to
a duplicated name resolves against a *set* of groups (§8.3), and those numbers
are not contiguous — MEASURED: `(?J)(?<a>x)(q)(?<a>y)` gives the name `a` the
numbers **1 and 3** (`out/dupnames.txt`, the numbering block). Carrying the
set even when it has one element is deliberate: it means the dupnames path is
the SAME emitted code path as the ordinary one with the loop trip count at 1,
rather than a second, rarer, less-tested path. `capno` is left alone — on an
`A_CAP` it means "this node IS group k", a different fact, and overloading it
would make two facts compete for one field (the reason `VmStratKind` sits
beside `VmRungKind` instead of inside it, `emit_vm.c:255-262`).

**(c) `caseless` is a FIELD, and D62 control 3's obligation comes with it.**
MEASURED (`out/caseless_fold.txt` axis B, 9 cells): the compare's
caselessness is the option in force **at the backreference**, not at the
group. `^(a)(?i:\1)$` matches `"aA"`; `^(?i:(a))\1$` does not; `^((?i)a)\1$`
does not, in either subject order; `^(?i)(a)(?-i)\1$` does not. That is
exactly `Ast.multiline`'s relationship to `$`, so it gets exactly
`Ast.multiline`'s treatment — set from the scoped `(?i)` state in force AT THE
BACKREFERENCE, never re-derived downstream — and it inherits D62's accepted
residual: **an analysis that pattern-matches `case A_BREF:` and does not read
`.caseless` reproduces `src/opt/possessify.c`'s pre-D62 bug and no compiler
diagnostic will say so.** §11.4 makes that a sabotage row rather than a
comment.

### 3.2 The emitted shape, and PUBLISH-AT-CLOSE

**REWRITTEN AFTER R32 E1, which refuted the first draft's central premise.**
That draft said "a slot is UNSET iff no live path has written it", made the
two-slot UNSET test total on that basis, and concluded a self-reference needs
no special handling. The premise is false while a group is RE-ENTERED, the
design's own archived cell refutes it, and one consequence is a memory-safety
defect in emitted code. Read this subsection before §3.3-§3.7; all four
depend on it.

#### 3.2.1 What E1 found

`src/gen/emit_vm.c:3813-3835` writes a group's START when control traverses
its OPENING position and its END at the CLOSING one — "WRITE ON TRAVERSE", as
that site's own comment says. So on iteration *n* > 1 of a quantified group,
`slot_values[2k]` holds iteration *n*'s start and `slot_values[2k+1]` holds
iteration *n-1*'s end. **Neither is `PCREC_UNSET`**, so the first draft's test
passes and the compare runs against a span that is not a capture.

The refutation was already sitting in this document's own archive. Cell S3,
`(a|b\1)+` on `"ab"` (`out/br_semantics.txt`): libpcre2 answers **(0,1) with
group 1 = (0,1)**; the first draft's model answers **(0,2) with group 1 =
(1,2)**.

And the failure is not confined to wrong answers. On `^(?:(a|b\1)y)+` over
`"aybay"`, iteration 2 opens the group at 2 while iteration 1's end is 1, so
`ref_s = 2 > ref_e = 1`. The emitted `(size_t)(ref_e - ref_s)` **underflows to
`SIZE_MAX`** and the compare reads out of bounds — K27's class, in a matcher
someone else compiles, with pcrec's name on it.

#### 3.2.2 The correction

**PUBLISH-AT-CLOSE.** The opening position is written to a per-group PENDING
slot; the `(start, end)` PAIR is published together when control traverses the
closing position. Both writes are trailed and exactly restored, exactly as
today's two writes are. A backreference then reads only PUBLISHED pairs, and
"published" means "some iteration of this group COMPLETED", which is precisely
what libpcre2's reference sees.

MEASURED, `out/publish_discipline.txt` — an arm-vs-arm sweep in which both
arms are the SAME simulator, the same AST, the same search order and the same
trail discipline, differing only in publication:

| population | cells | `publish=open` | `publish=close` |
|---|---|---|---|
| re-entry shapes (E1's class) | 2,178 | **138 divergences, 40 reversed-span** | **0, 0** |
| ordinary backrefs, no re-entry | 1,452 | 0, 0 | 0, 0 |
| backref-free control | 2,178 | 0, 0 | 0, 0 |
| **total** | **5,808** | **138 divergences, 40 reversed-span** | **0 divergences, 0 reversed-span** |

Three things that table establishes, and the third is the one that keeps the
correction cheap:

- publish-at-close reproduces libpcre2 on every cell, including both of E1's.
- the reversed-span column goes to zero, so the `size_t` underflow is not
  mitigated but **structurally absent**: a published pair always has
  `start <= end`, because the start was recorded before the body ran and the
  end after it.
- **the backref-free control is 0/0 in BOTH modes.** Publication discipline is
  unobservable without a backreference, because at match completion every
  group is closed and the published pair equals what write-on-traverse leaves.
  That is what lets the correction be scoped (§3.2.4) instead of rewriting
  capture semantics for every pattern pcrec compiles.

#### 3.2.3 The emitted shape

```c
// backreference \1 to group 1
rx_L7: __attribute__((unused));
    {
        const ptrdiff_t ref_s = slot_values[RX_SLOT_GROUP1_START];
        const ptrdiff_t ref_e = slot_values[RX_SLOT_GROUP1_END];
        ptrdiff_t took;
        /* Group 1 has no PUBLISHED capture on this path. PCRE2 fails. */
        if (ref_s == PCREC_UNSET || ref_e == PCREC_UNSET) goto rx_fail;
        took = rx_bref_match(subject, subject_length,
                             (size_t)ref_s, (size_t)ref_e, scan_position);
        if (took < 0) goto rx_fail;
        scan_position += (size_t)took;
        goto rx_L8;
    }
```

Unchanged from the first draft — which is the point. **The correction is
entirely in `A_CAP`'s emission, not in `A_BREF`'s**, and the reference's own
code is the same three tests it always was. What changed is that the two slots
it reads now mean "the last COMPLETED capture" instead of "whatever the two
writes last left".

`A_CAP`'s emission becomes, for a group this module marks (§3.2.4):

```c
// group 1 opens
rx_L3: __attribute__((unused));
    RX_SET(RX_SLOT_GROUP1_PENDING, (ptrdiff_t)scan_position);
    goto rx_L4;
    ...
// group 1 closes -- the PAIR is published here, together
rx_L5: __attribute__((unused));
    RX_SET(RX_SLOT_GROUP1_START, slot_values[RX_SLOT_GROUP1_PENDING]);
    RX_SET(RX_SLOT_GROUP1_END,   (ptrdiff_t)scan_position);
    goto rx_L6;
```

#### 3.2.4 What it costs, and why it is scoped

| | today | publish-at-close |
|---|---|---|
| slots per marked group | 2 | **3** (a pending slot) |
| trailed writes per traverse | 2 | **3** (one at open, two at close) |
| frames | 0 | 0 |
| emitted labels | 2 | 2 |

**The extra slot and write apply ONLY to groups this pattern actually
references**, which is a compile-time property (§5.3's resolution pass already
computes the referenced set). Three consequences:

- A pattern with no backreference emits byte-identical C — §11.3's identity
  gate holds by construction rather than by inspection, and §3.2.2's control
  arm is the measurement that says the two disciplines are indistinguishable
  there.
- A backref pattern pays 1 slot + 1 trail entry per referenced group per
  traverse. `vm_cost`'s `A_CAP` arm gains `+1` to `trail` for a marked group
  (`emit_vm.c:1242`'s `2 * nc` term becomes `3 * nc` over marked groups), and
  `vm_count_slots` allocates the third slot. Both sites already exist and both
  already read one flag; this adds a second.
- **The `--no-captures` interaction is real and is §6.3's, not this
  section's**: under `--no-captures` no `A_CAP` node is created at all
  (R32 E6), so a referenced group needs its slots reinstated. §6.3 carries the
  ruling.

#### 3.2.5 The properties, restated

1. **It reads the two published slots, never a saved copy.** P7's trail
   discipline is what makes that safe: the fail label rewinds to the popped
   frame's `trail_mark` *before* transferring control
   (`emit_vm.c:5075-5081`), so by the time any label runs `slot_values` holds
   exactly what that path published. §3.7 is where this becomes the
   correctness argument.
2. **The reference writes nothing and pushes no frame.** `vm_cost`'s new
   `A_BREF` arm is the zero arm the zero-width assertions take
   (`emit_vm.c:1316-1320`). The capacity cost of this module is entirely in
   `A_CAP`'s marked groups (§3.2.4), not here — which is the opposite of
   where the first draft put it, and worth saying because the reference is
   the construct that looks expensive.
3. **A backreference is deterministic**: for a given state there is exactly
   one length it can consume, so there is no choice point and `vm_alt` is not
   involved. (`\1*` is a *quantifier over* this node — §3.6.)
4. **`took` is a length, not a bool** (§4.2), and `ref_s <= ref_e` is now a
   STRUCTURAL precondition the signature may assert rather than a hope.
5. **`vm_nullable` must return TRUE for `A_BREF`** (`emit_vm.c:732-770`): a
   group can publish an empty capture and the reference then consumes
   nothing — MEASURED, cells E1/E4/E5. Getting this wrong is not a wrong
   answer but an unguarded nullable quantifier body, i.e. a hang. S-BR3.
6. **`pcrec_minw(A_BREF)` is 0** (P12), the safe direction, already written
   down as the intended answer in `mrl.c`'s header.

### 3.3 Unset groups: PCRE2 FAILS, and `PCREC_UNSET` already says so

**RULED by PCRE2 and MEASURED**, `out/br_semantics.txt` cells U1-U8 and the
`PCRE2_MATCH_UNSET_BACKREF` arm:

- `^(a)?\1$` on `""` → **no match**. On `"aa"` → (0,2).
- `^(?:(a)|b)\1$` on `"b"` → **no match**.
- `^(?:(a)x|(b)y)\1$` on `"byb"` → **no match**, while `\2` on the same
  subject is (0,3) with group 1 unset and group 2 = (0,1).
- python3 `re` **agrees on every one of the eight U cells**, so this half of
  the semantics is base-tier-oracle-verifiable.

The emitted test is the two `PCREC_UNSET` comparisons in §3.2.3 — **and it is
total only because of publish-at-close.** `run_state_init` fills every slot
with `PCREC_UNSET` once per search (`emit_vm.c:4841-4852`) and the trail
restores it on every rewind to mark 0, so a PUBLISHED slot is `PCREC_UNSET`
iff no live path has published it. **Under the first draft's write-on-traverse
model the same sentence was FALSE** (R32 E1): a re-entered group leaves both
slots non-UNSET while holding no capture at all, and the test passed on a span
that was not one. The argument wave E made for `\K`'s slot 0
(`emit_vm.c:3752-3765`) does carry over — but only to a slot with ONE writer
and one meaning, which is what publishing the pair together restores.

**`PCRE2_MATCH_UNSET_BACKREF` is OUT OF SCOPE**, and it is not free.
MEASURED: 2 of the 8 U cells flip under the bit (`^(a)?\1$` on `""` becomes
(0,0); `^(?:(a)|b)\1$` on `"b"` becomes (0,1)). Implementing it would mean a
second emitted shape for the same node (unset ⇒ match empty), selected by an
option pcrec does not have, on a `pcrec_options.flags` word D44.8 froze. Two
emitted shapes for one construct is precisely the axis D18 says must earn
itself, and this one has no customer. Refused explicitly rather than
forgotten. `docs/pcre2_options.md`'s row for it is where the disposition
belongs.

### 3.4 Empty groups: the reference advances zero and must still SUCCEED

MEASURED (E1-E5). A group that captured the empty string is **set**, and the
reference matches vacuously — `^(x?)y\1z$` on `"yz"` is (0,2) with group 1 =
(0,0). The emitted code gets this for free: `ref_s == ref_e` is not
`PCREC_UNSET`, `took` is 0, `scan_position` is unchanged, control falls to
`next`. The failure mode to guard is the *opposite* one — an implementation
that tests `ref_e > ref_s` as a proxy for "is it set" turns every empty
capture into a failure, and every one of E1-E5 catches it.

The interaction with §8's dupnames rule is sharper and is measured there: a
name-run whose **first set** entry captured the empty string resolves to that
entry, not to a later non-empty one (`out/dupnames.txt`: `(?J)^(?<a>x?)(?<a>y)\k<a>$`
on `"yy"` is **no match**, on `"y"` is (0,1)).

### 3.5 Self-reference `(a\1)` and forward reference `\2(a)(b)`

**Both COMPILE in PCRE2 and are governed entirely by §3.3's unset rule.**
There is no separate mechanism, and that is the finding: MEASURED
(`out/br_semantics.txt` S1-S4, F1-F5) —

| cell | pattern | subject | libpcre2 | python3 `re` |
|---|---|---|---|---|
| S1 | `(a\1)` | `"a"` | no match | **compile ERROR** |
| S3 | `(a\|b\1)+` | `"ab"` | (0,1), g1=(0,1) | **compile ERROR** |
| S4 | `^(\1a)$` | `"a"` | no match | **compile ERROR** |
| F1 | `\2(a)(b)` | `"ab"` | no match | **compile ERROR** |
| F3 | `(\2(a)\|b)+` | `"ba"` | (0,1), g1=(0,1) | **compile ERROR** |
| F4 | `(\2(a)\|b)+` | `"baa"` | (0,1), g1=(0,1) | **compile ERROR** |
| F5 | `^(?:\1(a))+$` | `"aa"` | no match | **compile ERROR** |

**The charter asks specifically what PCRE2 does on the FIRST iteration of a
`(\2(a)|b)+`-style shape, and F3/F4 answer it:** on iteration 1 group 2 is
unset, the `\2(a)` branch fails at the reference, the `b` branch matches, and
the loop then cannot continue (iteration 2's `\2` is *still* unset because the
branch that would set it never ran, and `b` no longer matches) — so the whole
match is (0,1), on `"baa"` as well as on `"ba"`. Nothing in this needs a
special rule. `A_CAP`'s slot writes happen on traverse (`emit_vm.c:3813-3835`),
a group that has not been traversed has `PCREC_UNSET` in both slots, and §3.2's
first line fails. **S3 is the same fact for a self-reference**: `(a|b\1)+` on
`"ab"` takes the `a` branch, sets group 1 to (0,1), and the `b\1` branch is
never usefully reachable — (0,1).

**The parser must therefore NOT reject either shape**, which is a real
instruction because the natural implementation does. But "no rejection" is
not sufficient on its own, and R32 E1 is why: a self-reference is the shape
that puts a live reference INSIDE the group it names, so it is exactly where
write-on-traverse exposes an unpublished pair. `(a|b\1)+` is both the S3 cell
and E1's headline counterexample. **Under publish-at-close the reference sees
the last COMPLETED iteration and both cells are correct** (§3.2.2's sweep:
0 divergences over the whole re-entry population). Three rules fall out:

- **A reference inside its own group is legal.** `pcrec_ngport_declare`'s
  sibling for numeric references must not check "is group k closed".
- **A forward reference is legal and its VALIDITY is a whole-pattern
  question**, deferred to end of parse — §5.3.
- **A group that is referenced from INSIDE itself is a marked group** (§3.2.4)
  like any other referenced group, and needs no additional treatment. The
  pending slot is written on each open and the pair published on each close;
  a reference reached before the first close reads `PCREC_UNSET` and fails,
  which is F3's measured answer.

This is also the module's **largest oracle divergence**: python3 `re` refuses
all seven of these patterns at compile time, so **no S or F cell can be
python-verified**. §12 carries that to the D27 author.

### 3.6 Backreferences inside quantifiers

MEASURED (Q1-Q7): `^(a)\1*$` on `"aaaa"` is (0,4); `^(\w)\1+$` on `"bbbb"` is
(0,4); `(\w)\1+` on `"abbbc"` is (1,4) with group 1 = (1,2); `^(a*)\1*$` on
`"aaa"` is (0,3) with group 1 = (0,3); `^(a?)\1{3}$` on `""` is (0,0) and on
`"aaaa"` is (0,4). python agrees on all seven.

Structurally there is nothing new: `A_REP` over an `A_BREF` body goes through
the same `vm_rep` ladder every other body does. Three specific interactions,
each of which is a claim the panel can check:

- **The cursor rung DECLINES**, correctly and without a new rule.
  `vm_det_seq` (`emit_vm.c:853`) returns 0 for any kind it does not
  recognise, and its `default:` arm is right here for the same reason §8.3 of
  `assertions_design.md` found it right for `$`: a backreference is not a
  fixed-length byte sequence, so "scan ahead by stride" is wrong for it, and
  declining on the kind needs no field read. **Adding `A_BREF` to
  `vm_det_seq` would be a miscompile**, because the length is a match-time
  quantity.
- **The revdet rung DECLINES, and — CORRECTED — it does so BY CONSTRUCTION
  and with an alarm.** An earlier revision of this section claimed
  `src/opt/revdet.c`'s `rd_shape` has a `default:` arm from which a new kind
  would inherit something. **It does not.** Its switch covers the kinds it
  accepts and *falls out* of the switch into `S->ok = false; return;`
  (`src/opt/revdet.c:89-140`, the two statements after the `A_ALT` arm), so an
  unlisted kind declines — the safe direction. And because the switch is on an
  enum with no `default:`, adding `A_BREF` raises `-Wswitch`, which
  `make strict` promotes to an error. So this site both declines correctly and
  says so, which is strictly better than the first draft claimed. S-BR4 stays
  a sabotage row (§11.4) because the failing direction — someone *adding* an
  `A_BREF` arm that accepts — is the mistake the alarm invites.
- **The counter rung is fine**, because it replicates the body without
  reasoning about its width.

`^(a*)\1*$` on `"aaa"` deserves its own line because it is the shape that
looks paradoxical: the outer `\1*` iterates over a body whose *length changes
as group 1 is re-decided by backtracking*. It works because §3.2 property 1
holds — each iteration reads the slots as they are at that instant, and the
loop's own frames restore them.

### 3.7 Nested repeats: the trail restores the OLD slot values, and here is the code

This is the charter's sharpest question and it has a citable answer.

MEASURED (N1-N6, all six agreeing with python):

| cell | pattern | subject | answer |
|---|---|---|---|
| N1 | `^(?:(a\|b)\1)+$` | `"aabb"` | (0,4), g1 = **(2,3)** |
| N2 | `^(?:(a\|b)\1)+$` | `"aab"` | no match |
| N3 | `^((a)\|(b))+\2$` | `"aba"` | (0,3), g1=(1,2) g2=(0,1) g3=(1,2) |
| N4 | `^(?:(a)(b)\2\1)+$` | `"abba"` | (0,4) |
| N5 | `(?:(a\|bb)x)+\1` | `"axbbxbb"` | (0,7), g1=(2,4) |
| N6 | `(?:(a\|bb)x)+\1` | `"axbbxa"` | no match |

N1 is the load-bearing one: the reference must compare against **this**
iteration's capture (`b`, at (2,3)), not the first iteration's (`a`), and on
backtracking the *previous* iteration's value must come back.

**The code that guarantees it, cited rather than asserted.** Three lines in
`src/gen/emit_vm.c`, and they already exist:

1. **`RX_SET` is a trailed write.** `#define <PREFIX>_SET(slot_, v_)` expands
   to `<PREFIX>_TRAIL(slot_); slot_values[(slot_)] = (v_);`
   (`emit_vm.c:4778-4780`), and `_TRAIL` (`:4772-4777`) pushes `{slot_index, saved_value}`
   where `saved_value` is `slot_values[slot_]` **before** the write. So every capture write records the value it displaced.
2. **`RX_PUSH` stamps the trail depth into the frame.**
   `resume_stack[depth].trail_mark = trail_depth` (`emit_vm.c:4781-4790`,
   the mark written at `:4785`).
3. **The fail label rewinds to that mark before jumping.**
   ```c
   while (run->trail_depth > run->resume_stack[frame_index].trail_mark) {
       run->trail_depth--;
       slot_values[run->trail[run->trail_depth].slot_index] =
           run->trail[run->trail_depth].saved_value;
   }
   goto *run->resume_stack[frame_index].resume_label;
   ```
   (`emit_vm.c:5075-5081`.)

That is an **exact restore, not a clear**, which is precisely what N1 needs
and what `emit_vm.c:3813-3817`'s own comment on `A_CAP` already says ("Undo is
EXACT RESTORE of the previous value, never a clear").

**The trail is therefore sufficient for RESTORE and was never the problem —
R32 E1 was about PUBLICATION, a different question.** The trail guarantees
that the slots hold what the current path wrote; publish-at-close is what
makes what the path wrote a *capture* rather than a half-open pair. The two
mechanisms compose without interacting: the pending slot is trailed like any
other (`RX_SET`), so a retreat out of an iteration restores the previous
iteration's pending value along with its published pair, and N1's requirement
— that iteration 2's reference compare against iteration 2's capture and that
backtracking bring iteration 1's back — is met by the trail exactly as the
first draft argued. What the first draft got wrong was not the restore; it was
believing the pair was a capture at every instant.

**The one place that contract is deliberately weakened, and why it is still
safe.** `RX_CUT` (`emit_vm.c:4792-4795`, `vm_cut` at `:1726-1740`) truncates
the resume stack **without rewinding the trail**. `vm_cut`'s own comment
argues this is safe because "a frame below the cut carries a trail mark from
before the loop ran, so unwinding to it still rewinds everything the loop
wrote". That argument is about what happens on a LATER failure, and it holds
for a backreference too — but it has a consequence this module must state:
**after a cut, `slot_values` holds the CUT PATH's writes, which is exactly
right**, because the cut path is the only surviving one. A possessive
quantifier followed by a backreference into it (`(a|b)++\1` — module
`atomic-groups`' surface, landing first) therefore compares against the
committed iteration. This is a cross-module cell, and §11.2 puts it in the
corpus rather than leaving it to be discovered.

### 3.8 The budgets

- **Step budget** (one backtrack resumption, `emit_vm.c:5045-5059`):
  unchanged. A backreference pushes no frame, so it costs zero steps directly.
- **Work budget** (D47 second addendum, `emit_vm.c:1718-1724`): a
  backreference performs O(length) byte comparisons that the fail label never
  sees, which is the *exact* definition of a work unit ("per-iteration work
  the fail label NEVER SEES", `emit_vm.c:1695-1712`). **RECOMMENDATION: charge
  `took` work units on success and the compared prefix length on failure**,
  through the existing `vm_work` primitive — one call, one truth. Without it,
  `(a*)\1` over a long subject does unbounded byte comparison per step, and
  DD-2's robustness claim is quietly false for this module's whole population.
  This is BELIEVED-with-a-gate: §13 P-3 names the measurement.
- **Frames/trail capacity**: unchanged (§3.2 property 2).
- **MRL**: contributes 0 (P12).

---

## 4. The caseless compare: the [M5-SEAM]'s second residual entry (charter (b))

### 4.1 Which fold — measured, and it is pcrec's own

**MEASURED, `out/caseless_fold.txt` axis A**, over all 256 bytes: under
libpcre2 10.46's 8-bit **non-UTF** build, the bytes a caseless backreference
compare folds are **exactly the 52 ASCII letters, each with exactly one
partner, and no non-ASCII byte folds at all**.

**MEASURED, axis A′**, over the same 256 bytes against the SHIPPED compiler
(`-i '[X]'` compared to the explicit pair `'[X Y]'`, past the metadata):
**zero disagreements** — pcrec's `cls_casefold` (`src/parse/parse.c:223-230`)
folds precisely that set and no other.

**So the module uses `cls_casefold`'s table and there is nothing to choose.**
D23's boundary 1 said a caseless backreference "needs a case-insensitive
comparison at MATCH time" and that this is "where this dimension would have to
be re-examined against D18's rule". It is re-examined here and the answer is:
the fold *set* is unchanged and shared; only the *place* it is applied moves,
from parse time to match time, for this one construct.

**The `\b` precedent is the right INTENT and the wrong MECHANISM, which R32
E8 corrected.** `\b` reads `pcrec_cls_word_esc`, a shared 32-byte BITMAP, and
emits a membership test from it. `cls_casefold` (`src/parse/parse.c:223-230`)
is `static`, takes a 32-byte bitmap and WIDENS it in place; it is not a
byte-to-byte fold and nothing in `src/gen/enc/` can call it. So "reuse the
same table" is not available as written: the residual entry would carry a
SECOND spelling of A-Z <-> a-z with nothing checking that the two agree.

**RECOMMENDATION: one shared fold TABLE object, and a 256-byte agreement
check.** A `const unsigned char pcrec_ascii_fold[256]` in `src/core` (identity
except that each ASCII letter maps to its counterpart), with `cls_casefold`
rewritten to derive its widening from it and the byte backend's residual text
emitting it. If that refactor is judged too wide for this module, the fallback
is the check alone: a test that walks all 256 bytes and asserts
`cls_casefold`'s widening and the residual entry's fold induce the SAME
partition. Either way the obligation is discharged by a mechanism rather than
by a comment — the design's own §0.2 complaint about controls that share a
source with what they control applies here in the other direction, where two
sources have no control at all. §11.4's S-BR11 is the sabotage.

**A `tolower()` in the emitted text would be a defect, not a shortcut**, and
D23's own scope note says why: pcrec's fold is ASCII-only *deliberately*,
because "in the C locale bytes >= 0x80 have no case" — but `tolower()` is
locale-dependent at the CALLER's run time, in the caller's locale, which
pcrec does not control. An artifact whose answers change with `setlocale` is
not the self-contained matcher APPROACH promises. The byte backend spells the
fold arithmetically or as a 256-byte table.

### 4.2 The signature, designed for the backend that does not exist yet

```c
/* $_bref_match -- the ENCODING RESIDUAL entry for a CASE-SENSITIVE
 * backreference compare (pcrec DD-12/D58).
 *
 * PRECONDITION: ref_start <= ref_end <= n. The caller passes a PUBLISHED
 * capture pair (pcrec backrefs_design.md S3.2), and a published pair is
 * ordered by construction -- the start was recorded before the group's body
 * ran and the end after it. The entry may assert it.
 *
 * RETURNS, and the sign carries two different facts:
 *     >= 0   the number of SUBJECT bytes consumed at `at`. This need not
 *            equal ref_end - ref_start: under an encoding whose case
 *            folding is not length-preserving it may differ, which is why
 *            the entry returns a length rather than a bool.
 *     <  0   no match, and -(result) - 1 is the number of subject bytes
 *            that DID compare equal before the mismatch (0 when the very
 *            first unit differs, or when fewer than the needed bytes
 *            remain). That prefix is the WORK the compare actually did and
 *            is what the caller charges against the work budget.
 *
 * Reads s only at offsets in [ref_start, ref_end) and [at, n).
 */
ptrdiff_t $_bref_match(const unsigned char *s, size_t n,
                       size_t ref_start, size_t ref_end, size_t at);

/* $_bref_match_caseless -- the same, folding case. */
ptrdiff_t $_bref_match_caseless(const unsigned char *s, size_t n,
                                size_t ref_start, size_t ref_end, size_t at);
```

**The negative encoding is R32 E4's correction and it is not decoration.**
The first draft returned a bare `-1` and separately recommended (§3.8)
charging "the compared prefix length on failure" — a quantity a single
sentinel cannot carry, so the recommendation was inexpressible in its own
signature. The failing case is the one that matters: `(a*)\1` over a long
subject fails the compare after doing O(n) byte comparisons, and a budget
that cannot see them is not a budget. `-(r) - 1` rather than `-r` so that a
zero-length prefix is representable as `-1`, keeping the ordinary "no match,
nothing compared" case at the value the first draft used.

**Why a LENGTH and not a bool.** MEASURED, `out/caseless_fold.txt` axis C: in
the 8-bit non-UTF build every fold pair is one byte to one byte, so the
compare cannot change length — `(?i)^(\xdf)\1$` on `"\xdf\xdf"` is (0,2) and
`(?i)^(ss)\1$` on `"ss\xdf"` is **no match**. That last cell is the point: it
is the sharp-s case a UTF-8 backend *would* have to answer differently, where
one captured character folds to two, and the consumed length stops equalling
`ref_end - ref_start`. Returning the length rather than a bool is what lets the
UTF-8 backend give a different answer **without the emitted engine code
changing a character** — the shared emitter never computes a length, it only
adds the one it is given. That is DD-12 (7) working as designed rather than
being worked around.

**Why TWO entries and not one with a flag.** D18/D23's rule is that an option
compiles away: "the generated code has no flag, no branch and no `tolower()`"
(`src/parse/parse.c:203`). A `int caseless` parameter would put a runtime
branch on a compile-time constant into the compare — D23 measured that exact
mechanism (a runtime `lc[]` indirection) costing 26% on a pattern with **no
letters at all**. Two entries, chosen at emit time, costs nothing.

**Why no `caseless` fold inside the emitter.** The compare must route through
the seam FROM BIRTH: an inline `(s[i] | 32) == (s[j] | 32)` in shared emitter
code is byte arithmetic that is *correct today and silently wrong under a
UTF-8 backend*, which is the exact residue class D58 scope item 3 enumerated
("caseless backref comparison when M6 lands"). §11.4's sabotage S-BR5 is a
codegen check that the compare is a CALL and not an inlined loop.

### 4.3 What a UTF-8 backend has to do differently

Recorded now, because D58's honest risk statement was that "a seam with one
backend is unvalidated until the second arrives" and the concrete enumeration
is the mitigant:

1. Walk both operands by **character**, using the backend's own decoder, not
   by byte.
2. Apply DD-1's fold rules, which are **not a bijection on characters** —
   one-to-many foldings (`ß` → `ss`), and pairs whose members have different
   UTF-8 lengths (`K` U+212A is 3 bytes, `k` is 1). D23 boundary 2 already
   says the bitmap argument does not carry over; this entry is where that
   stops being abstract.
3. Return the **subject** bytes consumed, which is why the signature returns
   a length. The captured operand's length is an input, not the answer.
4. Never assume `ref_end - ref_start == took`.

### 4.4 P14: the shipped codegen check FORBIDS what this design needs

**STRUCTURAL, and this is the finding the panel should attack first.**
`tests/codegen/run_codegen_tests.sh:922-926` states its allowlist: a residual
entry's name "may appear (a) in a comment, (b) as its own declaration, and (c)
inside its OWN definition. Anywhere else inside a file-scope function body is
a violation — which for a generated artifact means an engine body". The
`<prefix>_match_impl` function IS an engine body. **A backreference compare
routed through the seam trips this check on every artifact this module
produces.**

It is not a stale check: `tests/mech/sabotages/S68_residual_in_hot_loop.sh`
backs it, and its rationale is exactly right for `next_pos` — under the byte
backend the residual is the identity, so an engine that advanced through it
"would MATCH IDENTICALLY and every oracle in this tree would stay green"
(`run_codegen_tests.sh:906-912`).

**The check's IMPLEMENTATION is stricter than the rule it enforces.** D58
scope item 3 asks for "a codegen structural check that residual entries are
never called from **hot-loop labels**". The implementation says *any file-scope
function body*, which was a faithful and free tightening while the only entry
was `next_pos` — an entry that genuinely has no business anywhere inside the
matcher, because unanchoredness is the automaton's own self-loop and there is
no external advance to rewrite (D58's "Why" paragraph, measured that session).
A backreference compare has no automaton representation whatsoever. There is
nothing else it could be, and forbidding it forbids the construct.

**RECOMMENDATION, REWRITTEN AFTER R32 E7 AND C2 — the first draft's version
shared a source with its subject, which is this project's named failure.**

The first draft proposed deriving the complement check's population from the
backend table and asserting "the name appears in an engine body, and not in a
scan loop". Both halves were wrong:

- **The population was self-certifying.** The population would come from the
  artifact's own residual declarations — i.e. from the emitter. An
  implementation that inlines the compare AND drops the entry from the
  artifact's mask leaves the check with nothing to assert, and
  `run_codegen_tests.sh:1013`'s empty-population guard does not catch it,
  because that guard is global and `next_pos` is unconditional, so it stays
  green. The check would go green exactly when the thing it guards is broken.
- **The "not in a scan loop" clause has no mechanism.** `calls_in_bodies()`
  (`run_codegen_tests.sh:986-1004`) tracks a single `inbody` boolean; there is
  no loop or label awareness in it at all. And its violation rule is a raw
  `index($0, want)` with NO comment stripping — so a COMMENT naming
  `rx_bref_match`, which §3.2.3's emitted shape puts directly beside the
  call, satisfies the complement on its own. S-BR5 would pass by construction.

**The corrected design, and its principle is that the expectation must come
from the TEST, not from the artifact:**

- The fixture table (`run_codegen_tests.sh`'s TAB-separated rows) gains a
  column DECLARING which residual entries each fixture's artifact must carry,
  and the module adds backref-bearing rows. That is test-authored truth: an
  emitter change cannot edit it.
- Counting is **per A_BREF SITE and comment-stripped**: the number of calls to
  `<prefix>_bref_match*` in the engine body must equal the number of
  backreferences in the fixture's PATTERN, which the test knows because the
  test wrote the pattern. Comments are stripped before counting, so the
  emitted intent comment beside each call cannot stand in for the call.
- The **"not in a scan loop" clause is DROPPED.** No mechanism exists to
  express it and inventing an awk loop-tracker to check one clause would be a
  second control with the same author as the thing it checks.
- `next_pos` keeps `engine_callable = false` and its check is UNCHANGED,
  including S68 — verified by the panel to survive this refactor.

**The alternative, named and rejected:** emit the compare as an ordinary
`static` helper in the emitter's own output, outside the seam. That keeps the
check untouched and puts encoding-sensitive byte arithmetic in shared emitter
code, which is the thing D58 exists to prevent and which the [M6.5] row
forbids in its own text ("routes through a seam entry from birth").

### 4.5 The seam interface change, recorded against D58 as D58 asked

D58's revisit clause: "M5's UTF-8 backend lands — the second consumer is the
seam's validation event; **any interface change it forces gets recorded
against this entry**." The second consumer arrived early, and it forces one.

Today `PcrecEnc` carries exactly two text blobs (`src/gen/enc/enc.h:37-43`:
`decls`, `defs`) emitted unconditionally for every artifact. With three
entries that means every artifact — including one with no backreference —
grows two exported functions of dead code. They cannot be `static` (an unused
`static` fails the harness's `-Werror` generated-code build, which is why
`next_pos` is exported), so they would be *linked* dead weight in every
artifact pcrec has ever emitted.

**RECOMMENDATION**, and it stays inside `src/gen/enc/`:

```c
typedef struct {
    unsigned    id;           /* PCREC_ENCE_* */
    bool        engine_callable;   /* §4.4 */
    const char *decls, *defs;      /* `$` = prefix, as today */
} PcrecEncEntry;

typedef struct {
    int  id; const char *name;
    const PcrecEncEntry *entries;  /* NULL-terminated */
} PcrecEnc;

void pcrec_enc_emit_decls(StrBuf *, const PcrecEnc *, unsigned mask,
                          const char *prefix);
void pcrec_enc_emit_defs (StrBuf *, const PcrecEnc *, unsigned mask,
                          const char *prefix);
```

`PCREC_ENCE_NEXT_POS` is always in the mask (spec §3.1 promises it
unconditionally, and `tests/codegen`'s K27 fixture calls it directly,
`run_codegen_tests.sh:1043`); the two bref entries are in the mask only when
the artifact contains a backreference of that caselessness. The
third-encoding recipe is unchanged in shape — one new `enc_<name>.c`, its
`extern`, its row — which is the property `enc.h:26-32` says must survive.

**Cost accepted, stated — and R32 E11 found the list short.**
`emit_residual_decls`/`emit_residual_defs` (`src/gen/emit_dfa.c`, per
`src/gen/CLAUDE.md`'s [M5-SEAM] section) each gain a mask argument, and the
cross-prefix byte-identity check on the ABI block re-baselines. **Additionally:
`pcrec_enc_ready()` (`src/gen/enc/enc.h:54`) tests `e->decls != NULL`, and the
`entries` array REMOVES that field** — so the readiness predicate becomes
"has a non-empty entries array", and every caller of `decls`/`defs` moves with
it. That is a small set (the two emit functions and the readiness test) but it
is three sites, not one, and the `-e utf8` refusal path reads the predicate.

**The road not taken:** two more string fields on `PcrecEnc`
(`bref_decls`/`bref_defs`). Simpler, and it does not generalise — lookbehind's
back-step ([M6.6]) is the next residual entry D58 already names, and it would
need a third pair.

---

## 5. The octal disambiguation rule (charter (d))

### 5.1 The rule, measured cell by cell

**MEASURED, `out/octal_rule.txt`.** Everything below is a table row, not a
transcription of `pcre2pattern`.

**Rule 1 — `\0` is always octal.** `\0`, `\00`, `\000` are NUL; `\012` is LF;
`\0377` is `\037` followed by a literal `'7'` (so at most **three** digits
total, counting the leading `0`). `(a)\0` is still octal even with a group in
scope. There is no group 0 to address, so no ambiguity exists.

**Rule 2 — a single digit `\1`..`\9` is ALWAYS a backreference, and the group
count is over the WHOLE pattern.** `\1` with no groups → **error 115**;
`(a)\1` → ok; **`\1(a)` → ok** (the group is AFTER the escape);
`\9(a)(b)(c)(d)(e)(f)(g)(h)(i)` → ok. `\8` and `\9` are in this rule and are
**not** octal and **not** literal: `\8` with no group is error 115. The
discriminator confirms the reading: `(a)\1` matches `"aa"` at (0,2) and does
not match `"a\x01"`.

**Rule 3 — two or more digits: a backreference if that many groups exist SO
FAR, otherwise re-read as octal.** This is the asymmetry with rule 2 and it is
the finding:

| pattern | groups | verdict | discriminator |
|---|---|---|---|
| `(a)..(j)\10` | 10 BEFORE | backref to 10 | `"abcdefghijj"` → (0,11); `"abcdefghij\x08"` → no |
| `\10(a)..(j)` | 10 AFTER | **OCTAL 010** | `"\x08abcdefghij"` → (0,11); `"jabcdefghij"` → no |
| `(a)\10` | 1 BEFORE | **OCTAL 010** | `"a\x08"` → (0,2); `"aa0"` → no |
| `(a)\18` | 1 BEFORE | **octal `\01` then literal `'8'`** | `"a\x018"` → (0,3); `"aa8"` → no |
| `\12(a)..(l)` | 12 AFTER | **OCTAL 012** | `"\nabcdefghijkl"` → (0,13) |

So: **`\1`..`\9` see the whole pattern; `\10`+ see only what precedes them.**
A design that implements one count for both is wrong in one direction or the
other, and no test that only uses groups-before will notice.

**RULE 3' — A DIGIT RUN BEGINNING WITH 8 OR 9 IS ALWAYS A DECIMAL
BACKREFERENCE (R32 E3).** Rule 3 as first stated is incomplete, and the gap
is structural rather than a missing cell: `8` and `9` are not octal digits, so
for a run starting with one of them the "re-read as octal" branch consumes
ZERO digits and produces nothing at all. PCRE2 reads the whole decimal number
instead. MEASURED, `out/octal_rule.txt` axis E — each row varies the group
count and the boundary is exactly the run's own decimal value:

| escape | g=0 | g=8 | g=9 | g=12 | g=81 | g=82 | g=90 | g=91 | g=100 |
|---|---|---|---|---|---|---|---|---|---|
| `\8` | e115 | **ok** | ok | ok | ok | ok | ok | ok | ok |
| `\9` | e115 | e115 | **ok** | ok | ok | ok | ok | ok | ok |
| `\81` | e115 | e115 | e115 | e115 | **ok** | ok | ok | ok | ok |
| `\89` | e115 | e115 | e115 | e115 | e115 | e115 | **ok** | ok | ok |
| `\91` | e115 | e115 | e115 | e115 | e115 | e115 | e115 | **ok** | ok |
| `\812` | e115 | e115 | e115 | e115 | e115 | e115 | e115 | e115 | e115 (ok at 812) |

and the count is over the **WHOLE pattern**, like rule 2's and unlike rule 3's:
`\81` followed by 81 groups compiles and then fails at match time on the unset
rule — a forward reference — where `\100` followed by 100 groups reads as
OCTAL `'@'`. The two behave differently *because* `\100` has an octal reading
and `\81` does not.

**So the disambiguation is one question asked in one order**, and stating it
this way is what makes rule 3' fall out instead of being a special case:

1. Does the run start with `0`? → octal, at most three digits (rule 1).
2. Is it a single digit `1`-`9`? → backreference, whole-pattern count (rule 2).
3. Does the run have a valid octal reading at all (i.e. start with `1`-`7`)?
   → backreference if that many groups exist SO FAR, else octal (rule 3).
4. Otherwise (the run starts with `8` or `9`) → decimal backreference,
   whole-pattern count (rule 3').

**RIDER, also R32 E3: references above `\99` exist.** `\100` with 100 groups
before it is a backreference to group 100 (measured). A construct table that
stops at `\99` is too narrow — §2's does not any more.

**Rule 4 — the octal re-read's shape**, which applies only where rule 3 sends
control (a run starting `1`-`7`). Up to three octal digits from the first
digit; `8` and `9` TERMINATE it (`\18` is `\01` + `'8'`) — note that
terminating a run that has already started is a different thing from BEGINNING
a run, which is rule 3'; the value must
be ≤ `\377` (`\400` → **error 151**); remaining digits stand for themselves
(`\1234` with no groups is `\123` + `'4'`). `\o{101}` is the unambiguous form
and `\o{400}` is error 134 — a different number from `\400`'s, which is D26
tier 3 and not this module's to match.

**Rule 5 — the explicit forms never take the octal branch.** `\g10` and
`\g{10}` with no groups are **error 115**, not octal. `\g{10}` with 10 groups
AFTER compiles as a forward reference (and then fails at match time on §3.3's
unset rule — measured: neither the backref subject nor the octal subject
matches). Relative forms: `(a)\g{-1}` ok, `(a)\g{-2}` error 115, `\g{+1}(a)`
ok, `\g{+2}(a)` error 115 — so relative resolution happens at compile time
against the whole pattern in both directions.

### 5.2 What the module CHANGES, and what it must not touch

**Changes (the ATOM position only).** Today `src/parse/ext.c:308-315` renders
`RD_MODULE_OCTAL` as "`\N` (backreference/octal) requires module 'backrefs'"
for all ten digit rows. With a producer wired, the digit rows' `aport` gains a
`PORT_FN` implementing rules 1-4. `docs/dev/known_issues.md`'s note that
pcrec "still PRINTS `(backreference/octal)` for all ten" while `\0` is *only*
octal (`registry.c:492-496`) closes here: `\0`'s row and the nine others stop
sharing a diagnostic because they stop sharing a code path.

**Must not touch (the CLASS position).** `pcrec_clsport_octal`
(`src/parse/parse.c:384-407`) and the `PORT_SCALAR` class ports for `\8`/`\9`
(`registry.c:213-214`) are `ExtPort.base == true` — PCRE2 base facts the gate
never touches (`src/core/internal.h:1182-1188`). MEASURED, P6: pcrec's base
tier already agrees with libpcre2 on all 12 class cells, **including
`[\400]`'s refusal**. A module that "improves" the class answer breaks 12
measured cells and the 127 corpus pins MOD-0.3d's migration held
byte-identical. §11.4's sabotage S-BR6 pins this: with the module ENABLED,
every class cell's answer must be byte-identical to the base tier's.

`[\k]` and `[\g]` are the literal letters `k` and `g` (`registry.c:444-445`,
MEASURED P6) and stay that way with the module on.

### 5.3 The deferred validity check, and where it lives

Rule 2 makes `\1`..`\9`'s *validity* a whole-pattern question the parser
cannot answer at the escape. Rules 3 and 5 make relative and multi-digit
resolution answerable immediately (rule 3 by `cx->ncap` at the escape; rule 5
by... **not** immediately — `\g{+1}` and `\g{10}` both need the final count
too).

**RECOMMENDATION: one deferred list, checked once at end of parse.** The
module records `(kind, requested_number_or_name, pattern_offset)` per
reference into a `Ctx`-owned arena list — the same shape and the same tier as
`Ctx.named_groups` (`src/core/internal.h:664-665`), which is already "a
LEXICAL fact about the pattern text… populated unconditionally" — and a single
end-of-parse pass resolves every entry, raising pcrec's own error-115-class
diagnostic at the recorded offset. Three properties this buys:

- forward references (§3.5) are legal by construction, not by an exception;
- there is **one** resolution site, so numeric, relative and by-name
  references cannot disagree about what "group k exists" means;
- the dupnames name-run resolution (§8.3) happens in the same pass, after
  every declaration is known, which is required — a name's run is not
  complete until the pattern ends.

**Rule 3 is the exception and must stay one**: the backref-vs-octal decision
is made AT the escape from the count SO FAR, and cannot be deferred, because
deferring it would let a later group retroactively turn an octal literal into
a backreference. `\10(a)..(j)`'s measured answer is exactly that boundary.

---

## 6. Engine selection, the socket, and the expansion (charter (c))

### 6.1 `A_BREF` is STAMPED; SR-8 does the consulting

**REWRITTEN AFTER R32 M-1/C1, which the lane's own measurement refuted.**
The first draft proposed a `forces_backref` entry in `analyses[]` — the `\K`
exception's shape — and §11.5 claimed the tripwire population would "drop by
the rows this module builds". Both were wrong, and the second was wrong in a
way that hid the first.

**What the measurement found.** `tests/registry/registry_check.c:1379-1458`'s
engine-capability tripwire fires for any `RS_MODULE` row whose `engines` mask
excludes `ENGM_DFA` and which carries a wired atom-position producer. Its
population, read off the shipped binary (`--list-syntax`, module column x
engines column): **48 rows, of which backrefs owns TWELVE** — `\k<name>`,
`\g{-1}`, `\1`..`\7`, `\8`, `\9` and `(?P=n)` — against recursion 24,
lookaround 6 and one each for verbs, conditionals, callouts, branch-reset,
atomic-groups and assertions. The check's own comment (`:1422-1424`) says: *"If
a SECOND construct arrives here, do not add a second exception: two is when
the generic consultation has earned its axis and SR-8 is the right build."*
`\K` is the first, `(?>` ([M6.4]) is the second, and backrefs would be a third
exception covering twelve rows.

**RULED (D67, shared with R31 M-1): SR-8 IS BUILT IN [M6.4.2].** This module
consumes it and registers nothing.

So the design here is one sentence: **every `A_BREF` node is stamped at
construction with its producing row's `engines` mask** (`VM_ONLY` for all
twelve rows), and SR-8's single generic `EngineAnalysis` ANDs the stamps over
the post-discharge tree, taking `why_pos`/`why` from the first DFA-excluding
node's row. There is no backrefs-specific selection code at all. `\0`'s row is
`ANY_ENGINE` and produces an `A_CLASS` (rule 1), so it stamps DFA-capable and
nothing about it reaches the VM path — which is the stamping rule getting a
per-ROW answer right that a per-MODULE one would have got wrong.

Three properties this module needs from the contract, and all three are
recorded as contract notes in R31 M-1 rather than re-argued here:

- SR-8 subsumes `forces_kreset`, **not** `forces_captures` — §6.2 depends on
  that distinction.
- A forgotten stamp defaults to `ANY_ENGINE`, i.e. fails in the UNSOUND
  direction, which is what keeps the generic tripwire's demand (a VM_ONLY row
  with a producer must refuse `--engine=dfa` by name) load-bearing rather than
  ceremonial. §11.4's S-BR12 is this module's instance.
- Discharge output is born `ANY_ENGINE`; copied body nodes keep their stamps.
  This module registers no `discharge` hook (§6.3), so it is a consumer of
  that rule, not a customer.

**The twelve rows keep `VM_ONLY`, and that is now MEASURED rather than
provisional.** Frank's 2026-08-12 note called the blanket `VM_ONLY` "design
intent" that "splits under an AOT compiler"; §6.3 measures the split and finds
its DFA arm has no reachable customer on a default build, so `VM_ONLY` is the
rows' actual classification. Unlike `named-groups`' three rows (D59 part 2)
they do NOT get that module's free ride — an `A_BREF` is not an ordinary
`A_CAP` node, which is exactly the trigger D59's revisit clause named.

### 6.2 THE `--engine=dfa` REFUSAL, AND A PRE-EXISTING DEFECT THIS MODULE MAKES LOUD

The `\K` precedent (`select_engine.c:326-336`) is a two-branch switch: the
captures conflict fires when `cx->want_caps && cx->ncap > 0`, naming
`--no-captures` as the way out; only otherwise does the VM_ONLY-construct
branch name the construct.

**Every backreference pattern has `ncap > 0` by construction.** So on a
default build, `--engine=dfa` on ANY backref pattern takes the CAPTURES
branch and advises `--no-captures` — advice that does not solve the problem.

MEASURED, on the shipped compiler, using `\K` because backrefs do not compile
yet:

```
$ pcrec -p rx --features assertions --engine=dfa '(a)\Kb'
pcrec: this pattern requires captures (on by default); pass --no-captures
       for a DFA-only artifact, or omit --engine=dfa (pattern offset 0)
$ pcrec -p rx --features assertions --engine=dfa --no-captures '(a)\Kb'
pcrec: \K requires the VM engine, which --engine=dfa excludes (offset 3)
```

Two refusals in sequence, the first pointing at a flag that does not help.
Today the population is small (a `\K` pattern that also has a group).
**With this module it becomes the module's entire population**, since a
backreference without a capturing group cannot exist.

**THE DEFECT SURVIVED R32; THE FIRST DRAFT'S FIX DID NOT (E5).** That draft
said "the loop already records the first DFA-excluding `why`, so the
information is in hand". It records only the FIRST, and `analyses[]` is
captures-first *deliberately* (`select_engine.c:168-175` carries the
rationale), so for `(a)\Kb` the recorded `why` is "capture group at offset 0"
and the construct's own `why` is never computed at all. Reordering the two
BRANCHES instead would regress the plain-captures case, which needs exactly
the `--no-captures` advice the branch exists to give.

**RULING (travels to [M6.4.2] with ASK-3, alongside SR-8):** selection records
a SECOND `why` — the first **node-derived** exclusion — and takes the captures
branch only when that second `why` is ABSENT. `RX_ENGINE_WHY`'s first-row rule
is unchanged, so no artifact stamp moves and no identity gate re-baselines.
The distinction the fix turns on is R31 M-1's contract note 1: after SR-8
there are still two kinds of forcing, request-derived (`forces_captures`) and
node-derived (the stamps), and only the second may suppress the captures
advice.

**This section stays as the DEFECT RECORD.** The fix is not this module's to
land — it lands in [M6.4.2]'s engine slice, which lands first and shares the
population shape. What this module contributes is the measurement that the
defect's population is about to become universal: every backreference pattern
has `ncap > 0` by construction, so on a default build every one of them takes
the branch that gives advice which does not help.

### 6.3 The expansion: measured, and the recommendation is DO NOT SHIP IT HERE

Frank's 2026-08-12 design note (plan.md, the backrefs paragraph) is right in
its premise: when the referenced group's language is FINITE the backreference
is regular and compiles away — `(abc)\1` is `abcabc`, `(a|b)\1` is `aa|bb`.
`engine_m4.md` §5.2 makes it a `discharge` hook with a size-estimate
obligation. The question this gate must answer is whether it ships now.

**MEASUREMENT 1 — the customer set is empty on a default build.** MEASURED,
`out/expand_cost.txt` §0, on the shipped compiler:

| pattern | flags | engine chosen |
|---|---|---|
| `(abc)(abc)` | (default) | **vm** — "capture group at pattern offset 0" |
| `(abc)(abc)` | `--no-captures` | dfa |
| `abcabc` | (default) | dfa |
| `(a\|b)(a\|b)` | (default) | **vm** — "capture group at pattern offset 0" |
| `(a\|b)(a\|b)` | `--no-captures` | dfa |

The expansion's OUTPUT is itself capture-bearing, and even if it were not, the
INPUT is: a backreference pattern has a capturing group by construction, so
`forces_captures` (P8) returns `ENGM_VM` for it on every captures-on build no
matter what the backrefs stamps say. Captures are ON by default (D42.1). **The
expansion's entire customer set is `--no-captures` builds of backreference
patterns** — a small and self-selected population, since a caller who passed
`--no-captures` has already said they do not want the groups.

**AND `--no-captures` IS NOT FREE FOR THIS MODULE, which R32 E6 found and the
first draft simply had backwards.** Under `--no-captures` **no `A_CAP` node is
created at all** (`src/parse/parse.c:704-708`; the tree is identical to the
non-capturing one, and a `--no-captures` artifact emits ZERO `RX_SLOT_*`). So
a backreference under that flag has nothing to read: §3.2.3's two slots do not
exist. The first draft's §10 matrix had no `--no-captures` row and never
noticed.

**RULING: a backreference pattern under `--no-captures` KEEPS INTERNAL SLOTS
FOR REFERENCED GROUPS AND REPORTS NONE.** The precedent is `\K`'s exactly:
the flag drops the group slots a caller can SEE, not the machinery a match
needs. Concretely — `--no-captures` continues to suppress `A_CAP` for
unreferenced groups, but a group named by some `A_BREF` is built with its
three slots (§3.2.4's pending pair), those slots never reach `caps_out`,
`rx_info.ncaps` stays 1, and `rx_group_entry.slot` stays -1. Without that,
`--no-captures '(a)\1'` either miscompiles or has to be refused, and refusing
it would delete the expansion's only customer set along with it.

This does not disturb §6.3's conclusion — the expansion is still deferred —
but it does mean the flag is an axis this module must TEST rather than one it
can note in passing. §10 gains the row and §11.2's driver gains the arm.

**MEASUREMENT 2 — the cost, on the shipped compiler.** MEASURED,
`out/expand_cost.txt` §1. Each row hands the rewrite's actual output to
today's binary on the DFA path:

Pasted from `out/expand_cost.txt` rather than re-typed (R30 N2):

| family | source | \|L(G)\| | pattern | emitted | gcc | outcome |
|---|---|---|---|---|---|---|
| `(a\|b)\1` | alt2 | 2 | 5 B | 13,657 B | 0.05 s | compiled |
| `(abc)\1` | lit3 | 1 | 6 B | 12,351 B | 0.06 s | compiled |
| `([a-z])\1` | cls26 | 26 | 77 B | 22,113 B | 0.05 s | compiled |
| `((?:a\|b\|c\|d\|e){3})\1` | alt5x3 | 125 | 874 B | 35,261 B | 0.06 s | compiled |
| `([a-z]{2})\1` | cls26x2 | 676 | 3,379 B | **321,302 B** | 0.14 s | compiled |
| `([a-z]{3})\1` | cls26x3 | 17,576 | 123,031 B | — | — | **REFUSED**: >32000 DFA states |
| `([a-z]{4})\1` | cls26x4 | 456,976 | 4,112,783 B | — | — | **cannot even be passed**: `E2BIG` |

**MEASUREMENT 3 — the DECLINE boundary, bisected rather than estimated.**
MEASURED, `out/expand_cost.txt` §2, on the shipped compiler with endpoints
checked first so the bisection is known to bracket a boundary:

> `endpoint check: k=1 compiles=True ; k=17576 compiles=False`
> **largest `|L(G)|` that compiles: 10,525** — a 73,674-byte pattern producing
> **7,116,509 bytes of emitted C** and 2.07 s of gcc.

**The boundary REPRODUCES.** Two independent runs of this probe, from
different working trees, both bisect to 10,525/10,526 with identical pattern
and emitted-C byte counts; only the gcc seconds jitter (1.99 vs 2.07). So the
number is a property of the compiler's caps, not of a run.
> **smallest that does not: 10,526** — "pattern too complex for the DFA
> engine (>32000 states)".

The *cap* is at 10,525 words. The *usable* budget is far below it: 676 words
already costs 321 KB of source. So `engine_m4.md` §5.2's "the rewrite author
must size-estimate before committing and DECLINE rather than blow the caps"
is not a formality — the honest threshold is a **source-size** budget in the
low thousands of words, not the state cap, and choosing it needs the
`--no-captures` corpus evidence nobody has.

**RECOMMENDATION (the manager's prior, confirmed by the numbers): VM-ONLY
SEMANTICS SHIP IN [M6.5]; THE EXPANSION IS CHARTERED AS A FOLLOW-ON ROW.**
Four reasons, in order:

1. Its only customer is `--no-captures`, which is not the default (D42.1).
2. Its payoff on that customer is bounded by §7's numbers — 6.2x to 160x on
   scanning — which is real, but is the *same* payoff a sound nomatch-only
   prefilter (§7.3) would deliver with no rewrite, no size estimate and no
   fixpoint interaction.
3. It is the socket's SECOND customer and [M6.4] has not landed the first.
   Writing against an unlanded shape is how a design inherits a shape that
   changed.
4. The size estimate it needs is a *judgement about generated source size*,
   and D18's rule is that an axis must earn itself with evidence. The
   evidence would be a `--no-captures` backref corpus, which does not exist
   until this module ships.

**What the follow-on row inherits, so it is not started from zero:** the
finiteness test is "no unbounded `A_REP` beneath the referenced `A_CAP`",
`|L(G)|` is computable by the same walk, the synchronized-choice expansion is
the one this probe implements (`probes/probe_expand_cost.py`'s `expansion()`),
and the DECLINE threshold's measurement instrument exists and is committed.

---

## 7. The hybrid hazard (charter (f))

### 7.1 The rule

**An `A_BREF`-bearing pattern gets NO prefilter: `fit.prefilter = false`,
VM-only search.**

`engine_m4.md` §6.1's hybrid does not merely need a filter that cannot
false-negative. It needs the forward+reverse pair to hand the VM the **exact**
anchored window `[start, end)`, and that section marks the erasure half
STRUCTURAL for capture-only patterns *because there is no approximation step*:
`(a|b)` and `(?:a|b)` build the identical `Ast` (D31), so the prefilter's DFA
IS the pattern's DFA. A backreference has no such identity. APPROACH §2's
"backrefs → their referenced sub-pattern" is a real approximation, and this
section measures both halves of what that costs.

### 7.2 The erasure is SOUND as a language and USELESS as a window

MEASURED, `out/erasure_hazard.txt`: seven idiom families, each with a
generated subject population (exhaustive to length 4 over the family's
alphabet, then sampled, plus structured extras where a random walk produces no
positives).

| idiom | subjects | true hits | FALSE-NEG | **SPAN DIFF** | nomatch agreement |
|---|---|---|---|---|---|
| `(["'])[^"']*\1` | 4000 | 1716 | **0** | **367** | 1359/2284 (60%) |
| `<([a-z]+)>[^<]*</\1>` | 4160 | 24 | **0** | 0 | 4064/4136 (98%) |
| `\b([a-z]+)\s+\1\b` | 4000 | 419 | **0** | **100** | 1426/3581 (40%) |
| `([0-9]+)-\1` | 4000 | 1058 | **0** | **786** | 2176/2942 (74%) |
| `(\w)\1` | 4000 | 3808 | **0** | **1785** | 3/192 (2%) |
| `(a\|b)\1` | 4000 | 3808 | **0** | **1785** | 3/192 (2%) |
| `(a*)b\1` | 4000 | 3912 | **0** | **2525** | 88/88 (100%) |

Two conclusions, and they point in opposite directions:

- **FALSE-NEG is 0 in all seven families.** The erasure is a genuine
  SUPERSET — as it must be, since the captured text is always in the
  referenced group's language — so a `nomatch` verdict from it is
  trustworthy.
- **SPAN DIFF is large in six of seven.** Concrete cells, from the archive:
  `(["'])[^"']*\1` on `"\"''"` is truly (1,3) and the erasure says (0,2);
  `([0-9]+)-\1` on `"11-1"` is truly (1,4) and the erasure says (0,4);
  `(a*)b\1` on `"ba"` is truly (0,1) and the erasure says (0,2). **Every one
  of those is a window the hybrid would hand the VM wrong.** A VM run
  anchored to `(0,2)` on `"\"''"` does not find the (1,3) match.

So the erasure cannot serve `engine_m4.md` §6.1's role. The rule stands.

### 7.3 What it costs, measured on the shipped compiler

MEASURED, `out/prefilter_cost.txt`. The measurement is EXACT rather than a
proxy: the prefilter is a separate axis from the construct, so both arms
compile the IDENTICAL erased pattern with the IDENTICAL engine and differ only
in `RX_VM_PREFILTER` (`"hybrid"` under `auto`, `"none"` under `--engine=vm`,
P9). 256 KB of filler whose 7-letter words all differ (so the TRUE backref
patterns have no match), best of 5 trials × 3 reps.

**Pasted from `out/prefilter_cost.txt`, not from a separate run** — R30 N2's
correction, which found an inline table in the assertions design that came
from a different run than the archive it cited:

| idiom | subject | hybrid (s) | vm-only (s) | **vm-only is** |
|---|---|---|---|---|
| quote | nomatch | 0.00022810 | 0.00191457 | **8.4x slower** |
| quote | latematch | 0.00009122 | 0.00191623 | **21.0x** |
| tag | nomatch | 0.00000436 | 0.00069634 | **159.7x** |
| tag | latematch | 0.00001092 | 0.00069780 | **63.9x** |
| digits | nomatch | 0.00010991 | 0.00192808 | **17.5x** |
| digits | latematch | 0.00008925 | 0.00139532 | **15.6x** |
| dupword | nomatch / latematch | 0.00000028 / 0.00000011 | 0.00000009 / 0.00000004 | **NOISE** (see below) |
| letter | nomatch / latematch | 0.00000007 / 0.00000004 | 0.00000005 / 0.00000004 | **NOISE** |

**The RATIOS ARE STABLE IN ORDER OF MAGNITUDE AND NOT IN THEIR DIGITS, and a
reader should not quote one.** Five runs of this probe during the lane gave
quote **8.4-21.7x**, tag **63.9-159.7x** and digits **6.2-20.9x**. The
vm-only arm barely moves between runs; the HYBRID arm is multi-modal across
roughly 0.000004-0.00023 s, and that is what makes the ratio jump — a
prefilter that skips almost the whole subject is measuring a memchr whose
cost depends on where the first candidate byte lands, which the filler's
period decides. Treat the DIRECTION and the ORDER as established and the
digits as not. The design's ruling does not turn on which end of those ranges
is right, and this document deliberately quotes the range rather than a
run.

**The two NOISE rows are a RESULT, not a failed measurement**, and they are
the honest counterweight to the 157x: for `\b([a-z]+)\s+\1\b` and `(\w)\1` the
*erasure matches at offset 0* on a subject the true pattern never matches, so
the over-approximation filters nothing and a hybrid built on it would buy
nothing **even if it were sound**. That is the same fact §7.2's last column
reports as 40% and 2% selectivity.

**So the cost of the ruling is roughly one to two orders of magnitude
(6.2x-160x measured across five runs) on the families where a prefilter
would have helped, and
zero on the families where it would not** — and there
is no way to tell which is which without the very analysis §7.4 charters.

### 7.4 What is chartered rather than built

Two sound weaker uses, neither in this module:

- **A NOMATCH-ONLY prefilter.** The erasure never false-negatives (§7.2), so
  running it and answering `nomatch` outright is sound. It buys 40%–98% on
  four of the six non-vacuous families and 2% on two. It needs a second AST
  (the erasure is a real rewrite), a second NFA/DFA build, and its own
  selectivity measurement to decide whether the second build pays for itself
  — a `discharge`-socket-shaped piece of work, and the same follow-on row
  §6.3 charters is the natural home.
- **A literal-prefix skip.** `<([a-z]+)>...` cannot start anywhere but at a
  `<`. That is the DFA's existing memchr machinery over a prefix the pattern
  already has, and it is sound with no approximation at all. Not built here
  because the VM search loop has no prefix-skip today and adding one is an
  engine change, not a module.

Both are recorded so that "VM-only, no prefilter" is read as *this module's*
answer rather than as a permanent verdict.

---

## 8. DUPNAMES, implemented here (charter (e))

### 8.1 The refusal/acceptance matrix

MEASURED, `out/dupnames.txt` §2, libpcre2 with and without `PCRE2_DUPNAMES`
(the bit's value is behaviourally self-checked at oracle import):

| pattern | options=0 | DUPNAMES | what it decides |
|---|---|---|---|
| `(?<a>x)(?<a>y)` | err 143 | ok | the base case |
| `(?<a>x)\|(?<a>y)` | err 143 | ok | **different branches are still duplicates** |
| `(?:(?<a>x)\|(?<a>y))` | err 143 | ok | same, inside a group |
| `(?P<a>x)(?P<a>y)` | err 143 | ok | the python spelling |
| `(?'a'x)(?'a'y)` | err 143 | ok | the quoted spelling |
| `(?<a>x)(?<A>y)` | **ok** | ok | case-sensitive names (D59, reconfirmed) |
| `(?J)(?<a>x)(?<a>y)` | **ok** | ok | inline, at the start |
| `(?<a>x)(?J)(?<a>y)` | **ok** | ok | **inline AFTER the first declaration** |
| `(?J:(?<a>x)(?<a>y))` | **ok** | ok | scoped, both inside |
| `(?J:(?<a>x))(?<a>y)` | **err 143** | ok | **scoped, second OUTSIDE** |
| `(?J:(?<a>x)(?<a>y))(?<a>z)` | **err 143** | ok | third outside |
| `((?J)(?<a>x))(?<a>y)` | **err 143** | ok | `(?J)` inside a group |
| `(?-J)(?J)(?<a>x)(?<a>y)` | ok | ok | re-enabled |
| `(?<a>x)(?<a>y)(?J)` | **err 143** | ok | **`(?J)` AFTER both declarations does not help** |
| `(?<a>x)(?<a>y)(?J)\k<a>` | **err 143** | ok | same, with the reference present |
| `(?J)(?<a>x)(?-J)(?<a>y)` | **err 143** | **err 143** | **an inline `(?-J)` BEATS the API bit** |
| `(?J)(?<a>x)(?:(?-J)q)(?<a>y)` | **ok** | ok | the `(?-J)` is SCOPED away before the second declaration |

**The rule those seventeen rows determine: the duplicate check is made AT EACH
DECLARATION, against the SCOPED `(?J)` state in force AT THAT DECLARATION.**
Not at the pattern's start, not globally, and not once for the whole compile.
The last four rows are the separating cells and each kills a plausible
alternative reading:

- `(?<a>x)(?<a>y)(?J)` is **error 143**, which kills "`(?J)` anywhere in the
  pattern legalises everything" — the reading the first three rows are equally
  consistent with.
- `(?J)(?<a>x)(?-J)(?<a>y)` is **error 143 EVEN WITH `PCRE2_DUPNAMES` SET**,
  which is the sharpest cell in the matrix: the *inline* letter is not a way
  of turning the option on, it is the authoritative scoped state, and it can
  turn the API option OFF. Every other row in this table leaves that
  ambiguous.
- `(?J)(?<a>x)(?:(?-J)q)(?<a>y)` is **ok**, so the `(?-J)` really is scoped to
  its group and restored at the closing paren — the ordinary modifier-scope
  discipline, not a special case.

`(?<a>x)(?J)(?<a>y)` is legal because the *second* declaration is under
`(?J)`; `(?J:(?<a>x))(?<a>y)` is not, because the second is not.

That is `Ast.multiline`'s and `caseless`'s shape once more, one layer up: a
scoped parser-state bool saved and restored at group boundaries. So
`ParseMods` (`src/parse/parse_mods.h`) gains `bool dupnames`,
`mod_modifiers.c`'s `case 'J'` (`src/parse/mod_modifiers.c:323-354`) sets and
clears it instead of refusing, and `ng_is_duplicate`'s refusal
(`src/parse/mod_named_groups.c:89-95`, `:131-135`) becomes conditional on the
flag at the declaration site.

**The `(?J)` refusal's long comment retires with it.** That comment
(`mod_modifiers.c:324-353`) records two earlier wordings that were both wrong
and the reasoning that produced the third; it should be *replaced by a
pointer to this section*, not deleted, on the same house rule that keeps
refutations inline.

**pcrec gets NO `PCREC_DUPNAMES` option bit.** `(?J)` inline only. `(?i)` has
both spellings because `pcrec_options.caseless` predates D44.8's flags word;
`(?J)` has no such history and no consumer asking. §15 ASK-2 puts it to Frank
rather than deciding it silently.

### 8.2 The reflection table, and the proof of no ABI change

**MEASURED, and the ruled layout is libpcre2's own.**
`out/dupnames.txt` §1 reads `PCRE2_INFO_NAMETABLE` — the construct
`rx_info.groups` mirrors (D59) — for five patterns, in libpcre2's own table
order:

| pattern | `PCRE2_INFO_NAMETABLE` |
|---|---|
| `(?<a>x)(?<a>y)` | `[(1,'a'), (2,'a')]` |
| `(?<b>x)(?<a>y)(?<b>z)` | `[(2,'a'), (1,'b'), (3,'b')]` |
| `(?<z>1)(?<a>2)(?<z>3)(?<a>4)` | `[(2,'a'), (4,'a'), (1,'z'), (3,'z')]` |
| `(?<a>1)(?<aa>2)(?<a>3)` | `[(1,'a'), (3,'a'), (2,'aa')]` |
| `(?<n>1)\|(?<n>2)\|(?<n>3)` | `[(1,'n'), (2,'n'), (3,'n')]` |

That is **(name ascending, then number ascending)** — exactly the layout the
[M6.5] row rules, including the within-run number tiebreak D59 left unpinned.
So this is a reproduction of an external precedent, not a pcrec convention,
which is the same footing D59 put the name-sort itself on.

**No ABI change, and here is the argument.** `rx_group_entry` is emitted, not
declared in `lib/pcrec.h` (`lib/pcrec.h:396-401`), and its definition
(`src/gen/emit_dfa.c:420`) is `{ const char *name; int number; int slot;
const char *ref; }` — unchanged. The array's declaration
(`emit_dfa.c:456`, `:681`) is unchanged. What changes is **content**: `nnames`
counts more rows, and the array may contain adjacent rows with equal `name`.
`.abi` does not move (spec §6: it is 2 today and "not yet a compatibility
promise"), because no field is added, removed, reordered or retyped.

**One CONSUMER-VISIBLE change, and it must be written into the contract.**
`rx_info.groups` is documented "sorted, bsearch-able" (`emit_dfa.c:456`), and
`bsearch` on a table with duplicate keys returns **some** matching row, not
the first. So `docs/spec/match_api.md` §6 gains the caller algorithm — and it
is the *same* algorithm the emitted code uses (§8.3), which is the [M6.5]
row's own requirement that both consumers share one rule:

> Find any row with the name (`bsearch`), walk BACKWARD to the first row with
> that name, then walk FORWARD and take the first row whose `slot` is not -1
> and whose `caps[slot]` start is not `PCREC_UNSET`.

The comparator in `emit_info_def`'s `qsort` gains the number tiebreak. That
tiebreak is worth having *today*, duplicates or not: `qsort` is not stable, so
without it two rows that compare equal have an unspecified order and the
emitted artifact is not reproducible. D59 left it unpinned; this module pins
it.

### 8.3 The resolution rule: FIRST OF THE NAME-RUN, BY NUMBER, THAT IS SET

**MEASURED, `out/dupnames.txt` §3, 18 cells designed to separate four
candidate rules.** Every pattern declares two (or three) groups named `a` and
then references the name; the subject decides which participated.

| cell | subject | result | what it eliminates |
|---|---|---|---|
| `(?J)^(?:(?<a>x)\|(?<a>y))\k<a>$` | `"xx"` | (0,2) | — |
| same | `"yy"` | **(0,2)**, g1 unset g2=(0,1) | eliminates "first BY NUMBER" (plain): #1 is unset and the reference used #2 |
| same | `"xy"` | no match | eliminates "any one of them" |
| same | `"yx"` | no match | eliminates "any one of them" |
| `(?J)^(?<a>x)(?<a>y)\k<a>$` | `"xyx"` | **(0,3)** | **BOTH set: it used #1 ('x')** |
| same | `"xyy"` | **no match** | **eliminates "last set" / "highest number"** |
| `(?J)^(?:(?<a>x)\|(?<a>y)\|z)\k<a>$` | `"z"` | no match | NONE set → §3.3's unset rule |
| same | `"zz"` | no match | same, with text available |
| `(?J)^(?:(?<a>p)\|(?<a>q)\|(?<a>r))\k<a>$` | `"qq"` | (0,2) | three dups, MIDDLE set |
| same | `"rr"` | (0,2) | three dups, LAST set |

**The rule is: walk the name's run in ASCENDING GROUP NUMBER and take the
FIRST entry whose slot is SET.** Not the first by number unconditionally
(the `"yy"` cell), not the last set (the `"xyy"` cell), not "any" (`"xy"`).
When none is set, §3.3's ordinary unset-backreference failure applies — there
is no separate rule for names.

**"Set" includes set-to-empty.** MEASURED: `(?J)^(?<a>x?)(?<a>y)\k<a>$` on
`"yy"` is **no match** and on `"y"` is (0,1) with g1=(0,0). The run's first
entry captured the empty string, the resolution stopped there, and the
reference consumed nothing. A "first NON-EMPTY" reading gets both cells wrong.

**All four by-name spellings agree**: `\k<a>`, `\k'a'`, `\k{a}` and `(?P=a)`
give the identical answer on the `"yy"` cell. **Numeric references are
unaffected**: `(?J)^(?:(?<a>x)|(?<a>y))\2$` on `"yy"` matches and `\1` on the
same subject does not — a number names one group, duplicated name or not.

**The emitted shape** is §3.2's, with the unset test over the run instead of
over one pair — which is why §3.1(b) makes `refs`/`nrefs` uniform:

```c
// backreference \k<a> to the name-run {group 1, group 3}
rx_L11: __attribute__((unused));
    {
        ptrdiff_t ref_s = PCREC_UNSET, ref_e = PCREC_UNSET, took;
        if (slot_values[RX_SLOT_GROUP1_START] != PCREC_UNSET) {
            ref_s = slot_values[RX_SLOT_GROUP1_START];
            ref_e = slot_values[RX_SLOT_GROUP1_END];
        } else if (slot_values[RX_SLOT_GROUP3_START] != PCREC_UNSET) {
            ref_s = slot_values[RX_SLOT_GROUP3_START];
            ref_e = slot_values[RX_SLOT_GROUP3_END];
        }
        if (ref_s == PCREC_UNSET) goto rx_fail;
        took = rx_bref_match(subject, subject_length,
                             (size_t)ref_s, (size_t)ref_e, scan_position);
        if (took < 0) goto rx_fail;
        scan_position += (size_t)took;
        goto rx_L12;
    }
```

An `else if` chain in ascending number, unrolled at compile time (D18:
options compile away; the run is a compile-time fact). For `nrefs == 1` it
degenerates to §3.2's two lines, which is the shape argument for carrying the
set uniformly.

### 8.4 The compliance page

`docs/pcre2_compliance.md` is now an annotated derivation ([DOC-DRV]), so
these are keyed annotations plus generated facts and the module runs the
`compliance-refresh` skill rather than hand-editing:

| line | what it says today | what must change |
|---|---|---|
| 747-750 | "A duplicate name is a compile error (PCRE2 error 143, no DUPNAMES); `(?J)`/DUPNAMES itself stays OUT OF SCOPE — see its own row below" | duplicates become legal under `(?J)`; the "out of scope" clause is deleted |
| 795 | the prose row `\| (?J) dup names \| REJECTED \| planned \|` | becomes supported |
| 877-891 | the `(?J)` annotation, with its full "two earlier wordings were wrong" history | the history STAYS (house rule); the disposition flips, pointing here |
| 953, 1001 | the deferral analysis's revisit trigger — "`J`'s 4 cells DO NOT close when `named-groups` lands… they close only when a FUTURE dupnames producer lands" | **this module IS that event**; the trigger fires and the entry closes |
| 1528, 1539 | the built-status prose naming `(?J)` as the one shipped-module row reading `unbuilt` | that sentence stops being true — §9 |
| 1643 | the generated index row `(?J) \| REJECTED \| unbuilt \| planned \| modifiers` | regenerated: `built` |

Note line 1001's wording carefully: it says the `J` cells close when "a FUTURE
dupnames producer lands **inside** [named-groups]". This module lands the
producer in `backrefs`, not in `named-groups`, because the by-name resolution
machinery is here. The compliance text's *attribution* of the letter to module
`named-groups` (877-880: "duplicate NAMES are named-group semantics") stays
correct for the DECLARING half and must be reconciled with the RESOLVING half
landing here. §15 ASK-1.

---

## 9. Registry visibility and D65's `built` column (charter (viii))

D65's `built` column is DERIVED, not declared: `pcrec_construct_built_status`
(`src/parse/syntax_dump.c`, declared `src/core/internal.h:1754`) drives the
doorway with all features forced open and reads `ExtResult.answered_at`. So a
row flips to `built` **by gaining a producer**, and nothing is hand-maintained
— which is the property the memo's implementation record establishes.

**Rows this module must make visible, one per spelling, so the column can see
them:**

| row | today | after |
|---|---|---|
| `\0` (`registry.c:512`) | `M_backrefs`, `ANY_ENGINE`, `RD_MODULE_OCTAL`, unbuilt | **built** — and its note is already correct ("octal escape `\0dd` — never a backreference") |
| `\1`..`\9` (`:513-521`) | `M_backrefs`, `VM_ONLY`, unbuilt | **built** |
| `\k` (`:444`) | `ESC_CLASS_SCALAR`, class port only, unbuilt | **built** — gains a `PORT_FN` atom port |
| `\g` (`:445`) | as above | **built** for the backreference tails |
| `(?P=n)` (`:611`) | `GROUP_T`, `VM_ONLY`, unbuilt | **built** |
| `(?J)` (modifiers) | `unbuilt` (P13) | **built** |
| `\g<` `\g'` | **no row at all** | **NEW rows**, module `recursion`, unbuilt |

The last line is the one that needs argument. Today `\g<name>` reaches the
single `\g` row and would be claimed by this module's port. It is a
SUBROUTINE CALL (§2, measured), so claiming it would be a miscompile of the
kind D26 tier 1 forbids. Two ways to be truthful:

- **(preferred, and STRUCTURAL — the mechanism exists and is in use) two new
  `RK_ESC` rows with tails `<` and `'`**, module `recursion`, mirroring
  `registry.c:611-612`'s `(?P=` / `(?P>` split exactly.

  Verified rather than assumed, because the first draft of this section marked
  it as the document's weakest claim: `esc_answer` (`src/parse/ext.c:193-200`)
  reads the tail at the cursor and passes it to
  `pcrec_registry_arbitrate(RK_ESC, c, tl, avail, &amb)`, and that function
  (`src/parse/registry.c`) is **kind-agnostic** — it matches `sel`, then calls
  `pcrec_registry_row_answers`, which delegates to the row's `recognise` hook
  or to `pcrec_recognise_tail_default(at, avail, r->tail)`, and breaks ties by
  `rank`. **The shipped precedent is `\N`**: `registry.c:333` is
  `{RK_ESC, 'N', "{", ...}` and `registry.c:349` is
  `{RK_ESC, 'N', "{U+", ...}` — two `RK_ESC` rows in ONE `(kind, sel)` bucket,
  arbitrated by tail and rank, exactly the shape `\g<` and `\g'` need.
- **(fallback, no longer needed) one row, and the atom port refuses the `<`/`'`
  tails** naming module `recursion` in its own message. Truthful, but
  invisible to `--list-syntax` and therefore to D65's column and to the
  compliance index — which is exactly the "34 rows read identically" problem
  the memo was written about. Recorded because it is the answer if the panel
  finds something wrong with the arbitration reading above.

**`--features backrefs` gating.** The module is `FEAT_BACKREFS`
(`internal.h:753`), already allocated. Partial enable follows every other
module: with the module ON, every spelling in §2's "this module" column
produces; with it OFF, every one refuses naming `backrefs`, which is P1's
measured behaviour today and must be byte-identical after (§11.4's S-BR7).
`(?J)` is the one construct whose gate is a *different* module's letter
(`mod_modifiers.c`'s `case 'J'`), the same cross-module shape `(?m)` already
has for `assertions` — and D65's implementation record already records that
shape and why the classifier forces `"all"` open rather than one module. §10's
measured matrix is the whole story, including the part that is easy to get
wrong: `(?J)`'s refusal comes from **two different places** depending on which
modules are on, and only one of them is the letter this module changes.

---

## 10. Module gating, and what a partial enable means

**The bare default is `--features std1`, and `std1` is `{classes,
modifiers}`** (`src/parse/enabled.c:80-95`, `:112`) — not "nothing". An
explicit `--features` REPLACES the set rather than adding to it, and a named
set cannot be combined with module names (`--features std1,backrefs` is
"unknown module 'std1'", MEASURED). That is a real constraint on how this
module's `.rxt` `features:` directives must be written, and it is stated here
because the natural assumption is the opposite one.

MEASURED on the shipped compiler, four spelled-out sets:

| `--features` | `(a)\1` | `(?J)(?<a>x)(?<a>y)` | `\k<n>` | `[\1]` |
|---|---|---|---|---|
| `std1` (the bare default) | `\1 (backreference/octal) requires module 'backrefs'` | `inline option 'J' (dupnames): module 'named-groups' does not implement duplicate group names` | `\k requires module 'backrefs'` | **compiles, 0x01** |
| `none` | same | `(?J...) requires module 'modifiers'` | same | **compiles, 0x01** |
| `named-groups` | same | `(?J...) requires module 'modifiers'` | same | **compiles, 0x01** |

Two facts that table carries, and both matter to this module:

- **`(?J)`'s refusal comes from TWO different places depending on the set.**
  Under `std1` the `modifiers` module is ON, so the letter dispatch runs and
  hits `mod_modifiers.c`'s unconditional `case 'J'`; under `none` the
  `(?J...)` ROW's gate refuses first, naming `modifiers`. `mod_modifiers.c`'s
  own comment already says the letter's refusal is "unconditional either way",
  and this is what that looks like from outside. After this module, the letter
  must be gated on `FEAT_BACKREFS` — so the `none`/`named-groups` rows keep
  their `modifiers` answer and the `std1` row's answer becomes "requires
  module 'backrefs'".
- **The `[\1]` column does not move.** It compiles to 0x01 in every set,
  because the class position is base syntax (`ExtPort.base`, P6). That is the
  invariant §5.2 forbids the module to disturb and §11.4's S-BR6 pins.

**After this module lands**, the matrix the corpus must pin:

| `--features` | `(a)\1` | `(?J)(?<a>x)(?<a>y)` | `\k<n>` |
|---|---|---|---|
| `std1` | refuse: needs `backrefs` | refuse: needs `backrefs` | refuse: needs `backrefs` |
| `backrefs` | **compiles** | refuse: needs `modifiers` | refuse: needs `named-groups` |
| `backrefs,modifiers` | **compiles** | refuse: needs `named-groups` | refuse: needs `named-groups` |
| `backrefs,named-groups` | **compiles** | refuse: needs `modifiers` | **compiles** |
| `backrefs,modifiers,named-groups` | **compiles** | **compiles** | **compiles** |

`\k<name>`, `(?P=name)` and `\g{name}` need `named-groups` because there is
nothing to name otherwise; `(?J)` needs `modifiers` because the letter lives
in that module's dispatch; the numeric spellings need neither. That
three-module dependency is the module's real partial-enable boundary and
`gated.rxt` (§11.1) is where it is pinned.

**Whether `std1` should advance to `std2` including `backrefs` is NOT this
module's call** — D37 makes that an announced version boundary, and
`enabled.c:103-111` records that the next advance "changes this constant and
nothing else". §15 has no ASK for it because the answer is "not yet, and not
here".

---

## 11. Test plan (charter (ix))

### 11.1 `tests/backrefs/` — the corpus

Shaped on `tests/assertions/` (its `CLAUDE.md` is the model, and its oracle
discipline is the part that transfers):

| file | contents | oracle |
|---|---|---|
| `numeric.rxt` | `\1`..`\9`, unset, empty, quantified (§3.3, §3.4, §3.6 cells) | python-verifiable — MEASURED 0 divergences on all U/E/Q/N/P cells |
| `octal.rxt` | §5's rules 1-4, atom position, with the discriminator subjects | **`# pcre2-only`** — python's octal disambiguation is not measured here and must not be assumed |
| `octal_class.rxt` | §5.2's must-not-change class cells, run with the module ON | python-verifiable |
| `selfref.rxt` | §3.5's S and F cells | **`# pcre2-only`** — python REFUSES all seven at compile time |
| `spellings.rxt` | `\g`/`\k`/`(?P=n)` (§2) | **`# pcre2-only`** except the `(?P=name)` rows |
| `caseless.rxt` | §4's axis-B scoping cells and the 52-byte fold | python-verifiable |
| `dupnames.rxt` | §8's resolution cells | **`# pcre2-only`** — python has no `(?J)` and no `\k` |
| `nested.rxt` | §3.7's N cells and the cut interaction (§3.7's last paragraph) | python-verifiable for N1-N6 |
| `gated.rxt` | §10's matrix | n/a (refusal cells) |

**Every `# pcre2-only` marking must go into `docs/dev/upstream_issues.md`**
under the standing rule `tests/assertions/CLAUDE.md` states, and §12 is the
list.

### 11.2 The differential drivers

Two, following `run_kreset_diff.sh`'s shape and its central idea:

- **`run_backref_diff.sh`** — subjects × startpos, both pcrec engines against
  libpcre2, over a generated space with startpos taking every value in
  `[0, n]`. The startpos axis is not optional: `(a)\1` at startpos 1 on
  `"xaa"` is (1,3) and at startpos 2 is no match (MEASURED, cells P1/P2), and
  a suite that fixed startpos at 0 could not tell a correct implementation
  from one that ignores the argument.
- **`run_dupnames_diff.sh`** — §8.3's resolution rule swept over generated
  name-runs of size 1-4 with every subset of the run participating, against
  libpcre2. The rule is a *choice among candidates*, and a hand-picked cell
  set is exactly what §8.3's table shows is needed to separate four candidate
  rules; a sweep is what shows no fifth rule fits.

**The cross-module cell** from §3.7 — a possessive quantifier followed by a
backreference into it — goes in `run_backref_diff.sh` and not in a `.rxt`,
because it needs module `atomic-groups` and therefore a feature-set the base
corpus does not carry.

### 11.3 The identity gate

`tests/codegen/run_backref_identity.sh`, on the four shipped identity gates'
precedent — with the reference built from a **pinned pre-module commit via
`git archive`**, not from a `-D` knob.

That choice is not stylistic. `assertions_measurements/out/CLAUDE.md` records
the measurement behind it: under a sabotage a knob-built reference is *itself
sabotaged*, so an edit outside the knob's gated region CANCELS — "S83's first
form left the sweep at 1175/1175 identical". A commit-pinned reference shares
no sources with the subject. The claim to gate: **a backref-free pattern's
emitted C is byte-identical before and after this module**, on both engine
modes, with the backref patterns showing up as REFUSAL MISMATCHES — which is
the run's own positive control, because a run reporting zero differing AND
zero refusal mismatches has lost its population.

### 11.4 The sabotage rows

Per `tests/mech/CLAUDE.md`: one file per sabotage in `tests/mech/sabotages/`,
setting `SAB_ID`, `SAB_FILE`, `SAB_SUITES`, `SAB_DESC`, `SAB_BEFORE`,
`SAB_AFTER`, `SAB_COUNT`, applied through `lib/replace.py` to a fresh
`git archive HEAD` tree.

| id | sabotage | what must fail | why it is not covered otherwise |
|---|---|---|---|
| S-BR1 | the unset test becomes `ref_e > ref_s` | `numeric.rxt`'s E cells | turns every empty capture into a failure; every non-empty cell still passes |
| S-BR2 | the `caseless` field is ignored (always case-sensitive) | `caseless.rxt` | D62 control 3's exact residual; no compiler diagnostic |
| S-BR3 | `vm_nullable` returns false for `A_BREF` | `numeric.rxt` Q6 (`^(a?)\1{3}$` on `""`) | an unguarded nullable body is a hang, not a wrong answer |
| S-BR4 | `revdet.c`'s `rd_shape` gains an arm ACCEPTING `A_BREF` | `nested.rxt` | the `-Wswitch` alarm (§3.6) tells you an arm is missing; it does not tell you which arm is right |
| S-BR5 | the compare is inlined instead of calling the seam entry | `codegen` (§4.4's complement check) | **changes no answer** under the byte backend — the S68 shape |
| S-BR6 | the module's atom port also claims the CLASS position | `octal_class.rxt` | 12 base cells that a module-off run cannot see |
| S-BR7 | the gate check is dropped from the new atom port | `reject` | a construct that compiles with its module off |
| S-BR8 | rule 3's count uses the whole pattern instead of "so far" | `octal.rxt` | every groups-before cell still passes; only `\10(a)..(j)` fails |
| S-BR9 | §8.3's resolution takes the first by NUMBER rather than first SET | `dupnames.rxt` | the `"yy"` cell only |
| S-BR10 | §8.3's resolution takes the LAST set | `dupnames.rxt` | the `"xyy"` cell only |

S-BR8, S-BR9 and S-BR10 exist as three separate rows on purpose: each is a
plausible implementation, each passes the majority of the corpus, and each is
caught by exactly one cell. A single "resolution is wrong" sabotage would not
show that the corpus discriminates between them.

### 11.5 The registry checks

`tests/registry/registry_check.c` already asserts the row invariants. Two
additions:

- `check_engine_capability_tripwire`'s `qualifying` population drops by the
  rows this module builds — the same movement D59 recorded for
  `named-groups` (51 → 48). The number must be re-derived from the run, never
  copied into prose (`tests/mech/CLAUDE.md`'s founding complaint).
- `check_built_status_defects` gains this module's rows for free; the
  `--list-syntax` counts (33 built / 61 unbuilt today) move and
  `compliance-refresh` regenerates the index.

---

## 12. Appendix — the goal-facts list for the D27 blinded author (charter (g))

For the author of `tests/backrefs/d27/`, working from the PCRE2 goal with
`src/` and `tests/` denied. **libpcre2 10.46 is the oracle of record.** There
is no `pcre2test` binary on this box; drive libpcre2 through ctypes —
`tests/named_groups/d27/lib_pcre2.py` and `tests/assertions/verify_pcre2.py`
are the existing drivers, and this lane's `br_oracle.py` adds compile-error
NUMBERS and the name table.

**F1. An unset group's backreference FAILS.** Not "matches empty".
`^(a)?\1$` on `""` is no match. `PCRE2_MATCH_UNSET_BACKREF` flips 2 of 8 such
cells and is out of scope.

**F2. An EMPTY capture is SET.** `^(x?)y\1z$` on `"yz"` is (0,2). Distinguish
this from F1 in every cell you write; the two are one `if` apart.

**F3. Self-references and forward references COMPILE.** `(a\1)`, `^(\1a)$`,
`\2(a)(b)`, `(\2(a)|b)+` all compile in PCRE2 and are governed by F1.
`(\2(a)|b)+` on `"baa"` is (0,1). **python3 `re` REFUSES all of these at
compile time** ("cannot refer to an open group", "invalid group reference"),
so no python-derived expectation exists — these cells are libpcre2-only.

**F4. `\1`..`\9` count groups over the WHOLE pattern; `\10`+ count only
groups BEFORE the escape.** `\1(a)` compiles; `\10(a)..(j)` is the octal byte
0x08, not a backreference. `(a)\10` is octal 010, not "backref 1 then '0'".
`(a)\18` is octal `\01` then a literal `'8'`. `\8` and `\9` are always
backreferences (error 115 with no such group), never octal, never literal.
`\0` is always octal, at most three digits total. `\400` is error 151.

**F5. python3 3.14 lacks `\g`, `\k` and `(?J)` entirely.** It has `\1`,
`(?P<n>)` and `(?P=n)`. It also rejects `(?<n>...)` (only the `(?P<n>...)`
spelling), so `^(?<n>a)(?P=n)$` — legal in PCRE2 — is a python compile error.
Of 25 measured spellings, 20 are accepted by libpcre2 and **only 5 also work
in python**.

**F6. `\g<name>` and `\g'name'` are SUBROUTINE CALLS, not backreferences.**
`^(a|b)\g<1>$` matches `"ab"`; `^(a|b)\1$`, `^(a|b)\g{1}$` and `^(a|b)\g1$`
do not. If you write a `\g<...>` cell you are testing module `recursion`.

**F7. `(?i)` on a backreference is read AT THE BACKREFERENCE.**
`^(a)(?i:\1)$` matches `"aA"`; `^(?i:(a))\1$` does not; `^((?i)a)\1$` does
not.

**F8. The caseless compare folds the 52 ASCII letters and nothing else** in
an 8-bit non-UTF build. `(?i)^(\xdf)\1$` does not match `"\xdfss"`.

**F9. Under `(?J)`, a by-name backreference resolves to the FIRST group of
the name-run, IN ASCENDING NUMBER, THAT IS SET.** `(?J)^(?<a>x)(?<a>y)\k<a>$`
matches `"xyx"` and NOT `"xyy"`. `(?J)^(?:(?<a>x)|(?<a>y))\k<a>$` matches
`"yy"` (the first is unset, so the second is used). "Set" includes set to the
empty string: `(?J)^(?<a>x?)(?<a>y)\k<a>$` matches `"y"` and not `"yy"`.

**F10. `(?J)` is checked AT EACH DECLARATION.** `(?<a>x)(?J)(?<a>y)` is
legal; `(?J:(?<a>x))(?<a>y)` is error 143.

**F11. `PCRE2_INFO_NAMETABLE` under duplicates is sorted (name asc, number
asc).** `(?<z>1)(?<a>2)(?<z>3)(?<a>4)` reports `a`/1, `a`/3... — read it, do
not assume it; the exact pairs are in `out/dupnames.txt`.

**F12. startpos matters.** `(a)\1` on `"xaa"` is (1,3) at startpos 1 and no
match at startpos 2. Sweep it.

**F13. Nested repeats re-decide the referenced capture per iteration.**
`^(?:(a|b)\1)+$` on `"aabb"` is (0,4) with group 1 = **(2,3)**, not (0,1).
`(?:(a|bb)x)+\1` on `"axbbxbb"` is (0,7); on `"axbbxa"` it is no match.

---

## 13. What would refute this — predictions for the panel

Every load-bearing BELIEVED claim, with the experiment that kills it.

**P-1. The compare needs no frame and no trail entry (§3.2 properties 2-3).**
*Refuted by*: any PCRE2 cell where a backreference itself introduces a choice
point — i.e. where the same reference can consume two different lengths at one
state. Look for it in a UTF-8 build's fold ambiguity (`ß` vs `ss`), where a
one-character reference might match one or two subject characters. If such a
cell exists, the byte backend is still frame-free but the SIGNATURE in §4.2
is insufficient (it returns one length, not a set) and §4.3's list is wrong.

**P-2. `pcrec_minw(A_BREF) == 0` is safe (§3.2 property 6, P12).**
*Refuted by*: nothing — 0 is an under-estimate and under-estimates prune less.
The refutable half is the opposite claim I am NOT making: that a tighter bound
(the referenced group's own `minw`) is sound. It is not obviously sound, since
the group may be unset, and §14 keeps it out.

**P-3. Charging work units for the compare is necessary (§3.8).**
*Refuted or confirmed by*: instrument a prototype VM with the compare
uncharged and run `(a*)\1` against a growing subject, counting bytes compared
per step. If the ratio is bounded, the charge is unnecessary. I predict it is
not — it should grow linearly in subject length — but this is the one budget
claim in the document with no number behind it.

**P-4. `--engine=dfa`'s captures branch mis-advises (§6.2).**
*Already MEASURED* on the shipped binary with `\K`. The refutable part is the
FIX: that reordering the two branches does not break the `\K`-free captures
case. The check is the existing `tests/cli` refusal cells.

**P-5. `RK_ESC` rows honour a tail selector (§9). CHECKED, and it was the
document's weakest claim until it was.** The first draft left this unverified
and said so. It is now STRUCTURAL with a shipped precedent (`\N{` and `\N{U+`,
two `RK_ESC` rows in one bucket, `registry.c:333` and `:349`), and §9 carries
the chain. The residual named in an earlier revision — whether
`pcrec_recognise_tail_default` treats `RK_ESC` differently — is CLOSED by
reading it: its whole body is
`if (!tail) return true; return at && tl <= avail && memcmp(at, tail, tl) == 0;`
(`src/parse/registry.c`), which mentions no `RegKind` at all. *Refuted by*: a
`rank` interaction — the two new `\g` rows must outrank the tail-less `\g`
row, and the existing `\g` row's rank field must be checked at
implementation time.

**P-6. The expansion should not ship (§6.3).**
*Refuted by*: a corpus of real `--no-captures` backref patterns in which
finite-language references are common AND small. My measurement uses seven
synthetic families and five real idioms; four of the five real idioms
(`(\w)`, `([a-z]+)`, `([0-9]+)`, `(<[a-z]+>)`) reference INFINITE languages
and cannot expand at all. If someone produces a corpus where the finite case
dominates, the recommendation flips.

**P-7. The erasure never false-negatives (§7.2).**
*Refuted by*: one subject in any family where the true pattern matches and the
erasure does not. Zero found in 28,160 subject-family pairs. The argument is
that the captured text is always in the group's language — which is true, but
the erasure also DROPS the synchronization, and a construct that interacts
with the drop (a possessive group, an atomic group) might break it. **The
seven families contain no atomic or possessive group**, and that is this
measurement's real gap.

**P-8. The seam interface must change (§4.5).**
*Refuted by*: showing that two extra exported functions per artifact are
acceptable. That is a size measurement nobody has taken; today's smallest
artifact is ~12.4 KB (`out/expand_cost.txt`), so two ~15-line functions is
under 1%. If Frank rules that acceptable, §4.5's whole change collapses to
adding two strings to `decls_byte`/`defs_byte` and the design is simpler. **I
recommend against it on the lookbehind argument (§4.5's last paragraph), not
on size.**

**P-9. The `(?J)` scoping rule (§8.1). RESOLVED — the separating cells were
missing from the first draft and are now measured.** `(?<a>x)(?<a>y)(?J)` is
error 143, which kills "anywhere in the pattern"; `(?J)(?<a>x)(?-J)(?<a>y)` is
error 143 *even with `PCRE2_DUPNAMES` set*, which shows the inline letter is
authoritative over the API bit; `(?J)(?<a>x)(?:(?-J)q)(?<a>y)` compiles, which
shows the ordinary scope-restore applies. *Refuted by*: a cell where the state
at the declaration is not what decides — the obvious remaining one is a
declaration inside a `(?|...)` branch reset, which pcrec does not implement
and which is out of scope.

---

## 14. Explicitly out of scope

- `PCRE2_MATCH_UNSET_BACKREF` (§3.3) — measured, priced, declined.
- `\g<...>` / `\g'...'` subroutine calls — module `recursion` (§2, measured).
- `(?(1)...)` conditional-on-a-group — module `conditionals`, not in Frank's
  ruled M6 list.
- The finite-language expansion (§6.3) — chartered as a follow-on row.
- The nomatch-only prefilter and the literal-prefix skip (§7.4).
- A tighter `pcrec_minw` for `A_BREF` (§13 P-2).
- UTF-8's fold semantics (§4.3) — the entry's SIGNATURE is designed for it;
  the BODY is M5's.
- `PCRE2_EXTRA_CASELESS_RESTRICT` / `(?r)`, which `registry.c:741` already
  carries as a measured no-op at options=0.
- Matching PCRE2's specific error NUMBERS (115, 143, 144, 151, 164, 169).
  D26 tier 3: that a real syntax boundary refuses cleanly is exact; the
  wording and the number are not.

---

## 15. ASKs

**ASK-1 (Frank).** `docs/pcre2_compliance.md:877-880` attributes `(?J)` to
module `named-groups` ("duplicate NAMES are named-group semantics"), and
line 1001 says its cells close when a dupnames producer lands *inside that
module*. This design lands the producer in `backrefs`, because the by-name
resolution machinery is here and the [M6.5] row rules it here. Should the
compliance attribution move to `backrefs`, or stay `named-groups` with a
note that the two halves (declaring, resolving) live in different modules?
The latter is more truthful and more confusing.

**ASK-2 (Frank).** Should `pcrec_options.flags` gain `PCREC_DUPNAMES` beside
`PCREC_CASELESS`, or is inline `(?J)` the only spelling? No consumer asks for
the bit; `(?i)` has both only for historical reasons. Recommendation: inline
only.

**ASK-3 (manager).** §6.2's `--engine=dfa` branch-ordering fix is a
pre-existing defect in `src/opt/select_engine.c` that this module's population
makes universal. Fix it in this module's wave, or as its own small lane
before [M6.5.2] (the [ABI-NS] precedent)?

**ASK-4 (manager).** §11.3's identity gate uses a commit-pinned reference,
which `assertions_measurements/out/CLAUDE.md` records as strictly stronger but
which the four SHIPPED gates do not use (they use a `-D` knob, for cheapness
in an ongoing gate). This gate is ongoing, not one-shot. Accept the extra
cost, or follow the four gates' precedent and accept the measured
cancellation risk?

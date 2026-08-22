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

## PANEL OUTCOME — R32 (2026-08-22)

`../dev/reviews/2026-08-22-r32-backrefs-design.md`, three read-only critics
against commit 4cd461f. **Read this block before any section.**

**NOT APPROVED at 4cd461f: eight HIGH findings.** The MEASURED facts held
almost everywhere — the 52-byte fold set (re-measured at 256x256), the octal
matrix bar one rule, the dupnames resolution rule under a harder battery, the
`PCRE2_INFO_NAMETABLE` order, the expansion boundary (three independent
reproductions), the no-prefilter ruling, and this document's reading of the
shipped `[M5-SEAM]` check. What fell is the design's central premise and four
of its checks.

| finding | what was wrong | where it is now |
|---|---|---|
| **E1 (HIGH)** | §3.2's "a non-UNSET slot pair is a capture" is FALSE while a group is re-entered — the document's OWN archived cell S3 refutes it, and two shapes underflow a `size_t` in emitted code | **§3.2, rewritten as PUBLISH-AT-CLOSE**, with a 5,808-cell sweep |
| **E2 (HIGH)** | "the erasure is a genuine superset" — false once the referenced group holds an assertion | §7.2, §7.4, §13 P-7 |
| **M-1/C1 (HIGH)** | `forces_backref` would be a third exception covering TWELVE rows to a check whose text says the second builds SR-8 | §6.1 (stamping), §11.5 — **found by this lane against its own design** |
| **C2 (HIGH)** | the proposed complement check shares a source with its subject, and its "not in a scan loop" clause has no mechanism | §4.4 |
| **C3 (HIGH)** | two corpus files marked python-verifiable in the direction that LOSES the oracle | §11.1 |
| **C4 (HIGH)** | no sabotage row for the wrong-answer failure mode | §11.4 |
| **C5 (HIGH)** | "the built column gains this module's rows for free" — the tally is asserted by nothing | §11.5 |
| **E3 (MED-HIGH)** | rule 3 leaves an empty octal run for an 8/9-led digit run | §5 rule 3' |
| E4-E11, C6-C20 | the return protocol, the fold table, the revdet interaction, `-Wswitch`'s strength, the cost list, oracle pointers, distinct counts, the filler, the drivers, four probe defects | applied in place; §16 tabulates |

**What SURVIVED**, on the panel's own instruments rather than re-runs of this
lane's: the fold SET over 256x256 pairs; the length claim in byte mode; all
eight U cells and five E cells; `PCREC_UNSET` cannot collide with (0,0); the
§3.6/§3.7 mechanism as cited; the CUT paragraph; §5's rules 1, 2, 4, 5 and all
twelve class cells; the expansion boundary EXACTLY (10,525/10,526); §7.3's
axis; §8.1's seventeen rows and §8.3's rule under a harder battery — including
the decisive finding that **PCRE2 does not retry later name-run members when
the first-set one's compare fails**, which is what makes §8.3's frame-free
else-if chain the right shape; §8.2's NAMETABLE order over ten patterns;
`rx_group_entry` unchanged; §10's matrix; §9's `\N{` precedent, now MEASURED.

**THE FOCUSED RE-CHECK (r32chk, on the revision).** Seventeen of twenty items
CLOSED — every probe re-run byte-identical, the expansion boundary reproduced
a FOURTH time, the C9 filler verified no-match for all five true patterns, and
C12's positive control recorded as a strong closure because it "refuted the
lane's own superset claim". What did not close, and one item where the
re-check's own premise needed correcting:

| item | what the re-check found | where it is now |
|---|---|---|
| **C2 (still open, 3 residuals)** | the per-site COUNT's provenance was unspecified — deriving it by scanning for `\<digit>` is a SECOND implementation of §5's octal rule, wrong on `(a)\10` and `(a)\18`, which are S-BR8's own fixtures; no SCOPED non-vacuity guard (all six fixtures expect 0 and get 0); comment-stripping specified at line granularity where the call spans two lines | §4.4: a DECLARED INTEGER column, an exact "N fixtures declare >= 1 bref" guard, token-level stripping in one pass |
| **N1** | S-BR17 cannot go red — glibc's `qsort` is stable, so a name-only comparator preserves insertion order | §11.4, §8.2 — **and the re-check's premise is corrected**: its harness inserted in ASCENDING group order; pcrec PREPENDS (`mod_named_groups.c:154-155`) and walks from the head (`emit_dfa.c:676-677`), so the array is DESCENDING. The conclusion (make it structural) is right; the reason is that a behavioural row here needs two unspecified properties to agree. **Consequence: the tiebreak is a CORRECTNESS requirement**, since without it §8.2's caller algorithm selects the highest-numbered participating group — the rule §8.3's `"xyy"` cell rules out |
| **N2** | §13 P-11's "+12/-12 plus `(?J)`" wrong twice | §13 P-11, §11.5: **built 33→47, unbuilt 61→49, na 6, total 100→102**, and the tripwire's 48 and the tally's 94 are different sets |
| N3-N6, C18 residue | three stale figures in §7.3; §0.3's table still said "superset (sound)"; S-BR14 named a driver section that did not exist; a seventh run put `tag` at 172.9x above the stated ceiling; "all seven" over a 9-cell/8-pattern population | §7.3 (range now open-ended upward), §0.3, §11.2 (a named span-divergence section with its own guard), §3.5 |
| S-BR12 | observable only after [M6.4.2]'s SR-8 | §11.4, flagged CROSS-MILESTONE |

**The one finding worth naming rather than tabulating**, because it is this
lane's own failure of a kind the project keeps cataloguing: **E1's
counterexample was already in this document's archive.** Cell S3 of
`out/br_semantics.txt` disagreed with §3.2's model from the day both were
written, and the lane archived the cell, quoted the cell in §3.5, and did not
run the model against it. The instrument that found it is now committed here
(`probes/simvm.py`, adopted from the critic rather than rewritten) precisely
so the next revision cannot repeat that.

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
| `probes/probe_erasure_hazard.py` | MEASURED, libpcre2 | §7: that the erasure is a superset **only for an ASSERTION-FREE referenced group** (R32 E2 — its positive control refutes the unconditional claim, 6/10 cells) and that its SPAN is not (unusable for the hybrid either way) |
| `probes/probe_expand_cost.py` | MEASURED, in-pcrec | §6: the finite-language expansion compiled by the shipped compiler, and the DECLINE boundary bisected |
| `probes/simvm.py` | the SIMULATOR, **adopted from R32's critic** | §3.2: the emitted model in both publication disciplines, with the `publish` axis added and nothing else changed |
| `probes/probe_publish_discipline.py` | MEASURED, libpcre2 vs both models | §3.2: E1's 5,808-cell arm-vs-arm sweep, with a backref-FREE control arm |

**`probes/archive.sh` is the ONLY writer of `out/`.** That rule is inherited
from R30 M7, where a hand-written header imitating the archiver was named "a
sharper instance of a control sharing a source with what it controls than
anything the archiver guards against". No header in `out/` was hand-written.
**R32 D1/C14: every header nonetheless said "module `assertions`"** — a
copy-paste leftover from the archiver this one was derived from, wrong in all
eight files while their commit refs, dirty lists and content were independently
correct. The stamp is re-scoped and every output re-archived in ONE batch from
a committed tree. (`out/CLAUDE.md` is hand-written, says so, and is not an
archived output — the same distinction the assertions lane draws.)

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

**R32 found four more, and they are recorded in the same place for the same
reason.** `probe_erasure_hazard.py` sampled subjects WITH REPLACEMENT and
reported the draw count, inflating three families 31.5x, and carried a
`finite` family identical to `letter` — "seven families" was six. Its
FALSE-NEG column had no cell in which it could be non-zero, making a table of
zeros unfalsifiable; E2's assertion-in-group cells are now its POSITIVE
CONTROL, and the probe refuses to report if that control finds nothing.
`probe_prefilter_cost.sh`'s guard compared prefilter STAMPS rather than
ENGINES, so a DFA artifact's empty stamp would have passed, and its filler's
"7-letter words all differ" were seven IDENTICAL letters — true of the words,
false of the letters, so `(\w)\1` matched the "nomatch" subject at offset 0.
`probe_caseless_fold.py`'s axis A used `.`, which excludes 0x0a, so it swept
**255** bytes while reporting 256. All four are fixed and each fix is written
into the probe.

A ninth is not a defect but a result: `probe_expand_cost.py` crashed on
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
| P15 | `A_CAP` publishes its START when control traverses the opening position and its END at the closing one — so while a group is re-entered the two slots belong to DIFFERENT iterations | STRUCTURAL: `src/gen/emit_vm.c:3813-3835`, the `vm_set` calls at `:3826` and `:3832`; MEASURED consequence in `out/publish_discipline.txt` |
| P14 | A residual seam entry may NOT be referenced from any file-scope function body but its own and `main()` | STRUCTURAL: `tests/codegen/run_codegen_tests.sh:895-995`, the `[M5-SEAM]/DD-12(7)` check; sabotage `tests/mech/sabotages/S68_residual_in_hot_loop.sh` |

**P15 is the premise the first draft did not check, and §3.2 is where it is
now dealt with rather than assumed away.** P14 is the one that changes the
seam, and §4.4 is where that is dealt with rather than worked around.

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
        /* §3.8's WORK CHARGE. `took` on success; on failure the entry's
         * negative encoding carries the prefix it compared (§4.2), so the
         * work the fail label never sees is charged either way. Emitted
         * through the `vm_work` primitive, one call one truth. */
        RX_CHARGE_WORK(took >= 0 ? (size_t)took : (size_t)(-took - 1));
        if (took < 0) goto rx_fail;
        scan_position += (size_t)took;
        goto rx_L8;
    }
```

**The `RX_CHARGE_WORK` line is shown deliberately** (R32 re-check): an earlier
revision recommended the charge in §3.8 and omitted it from the emitted shape
here, so the two sections disagreed about what the artifact contains. It is
emitted only when the artifact has a work budget, exactly as `vm_work`'s
`has_budget` guard already does for every other charge site
(`emit_vm.c:1718-1724`).

Otherwise unchanged from the first draft — which is the point. **The correction is
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
computes the referenced set).

**THE MARKED SET IS THE UNION OF EVERY `A_BREF`'s `refs` ARRAY — every member
of a duplicated name's run, not merely the member a given match resolves to
(R32 re-check E13).** §8.3's resolution is a MATCH-TIME choice that reads
every member's pair in ascending number until it finds a published one, so an
unmarked member is read under write-on-traverse and E1 reappears through it.
MEASURED: `(?J)^(?:(?<a>q))?(?:(?<a>a|b\k<a>))+$` on `"aba"` is **(0,3) with
group 1 UNSET and group 2 = (1,3)** — the chain falls through the unset first
member to the second, which is the one being RE-ENTERED, so it is exactly the
member that must be marked. `(?J)^(?<a>x)(?:(?<a>a|b\k<a>))+$` on `"xbx"` is
(0,3) with both set, the same shape with the fall-through removed. Marking
only the statically "resolved" member is not merely incomplete — there is no
statically resolved member to speak of.

Three consequences:

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
every one of them at compile time, so **no S or F cell can be
python-verified**. The archive carries **9 cells over 8 distinct patterns**
(S1-S4 and F1-F5; `(\2(a)|b)+` appears twice, on `"ba"` and on `"baa"`) — the
table above shows seven of the nine, and an earlier revision called that "all
seven" of a population that is not seven (R32 C18 residue). §12 carries the
divergence to the D27 author.

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
- **The revdet rung declines a backreference IN THE BODY — but the rung is
  NOT declined for the group-in-body / reference-outside shape (R32 E9), and
  that interaction needs naming.** `(?:(a|bb)x)+y` takes the revdet rung with
  a capturing group inside the loop body; the forward scan SUPPRESSES the
  per-iteration capture writes (`v->nocap`, `emit_vm.c:3820-3824`) and the
  backward walk reconstructs the last iteration's values. A reference OUTSIDE
  that loop — `(?:(a|bb)x)+\1`, this document's own N5/N6 cells — therefore
  reads slots written by the backward walk rather than by the loop. The panel
  traced it as CORRECT and the N5/N6 cells agree with libpcre2, but it was
  unnamed and untested in the first draft. **Publish-at-close interacts here
  and the interaction must be designed, not assumed**: a marked group's
  pending slot is written per iteration, so the suppression rule must suppress
  or reconstruct it in step with the pair. §11.4's S-BR13 is the sabotage and
  §11.2's driver carries the shape.
- **The revdet rung DECLINES a backreference in the body, and — CORRECTED —
  it does so BY CONSTRUCTION and with an alarm.** An earlier revision of this section claimed
  `src/opt/revdet.c`'s `rd_shape` has a `default:` arm from which a new kind
  would inherit something. **It does not.** Its switch covers the kinds it
  accepts and *falls out* of the switch into `S->ok = false; return;`
  (`src/opt/revdet.c:89-140`, the two statements after the `A_ALT` arm), so an
  unlisted kind declines — the safe direction. And because the switch is on an
  enum with no `default:`, adding `A_BREF` raises `-Wswitch` — a WARNING,
  which `make strict` promotes to an error and a plain `make` does not (R32
  E10: the first draft called it "a compile error" without the qualifier). So
  this site declines correctly, and says so to anyone running the opt-in
  gate. S-BR4 stays
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
  the compare's actual work through the existing `vm_work` primitive** — one
  call, one truth — namely `took` on success and, on failure, the prefix
  length the entry now returns (§4.2's negative encoding, which exists
  BECAUSE of this charge: R32 E4 found the first draft recommending a charge
  its own signature could not express). Without it, `(a*)\1` over a long
  subject does unbounded byte comparison per step and DD-2's robustness claim
  is quietly false for this module's whole population. Still
  BELIEVED-with-a-gate on the SIZE of the effect: §13 P-3 names the
  measurement.
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
- **The expected call count is a DECLARED INTEGER COLUMN, not a count of
  anything.** (R32 re-check C2(a).) The revision said "equal to the number of
  backreferences in the fixture's PATTERN, which the test knows because the
  test wrote the pattern" — but "knows" was doing unearned work: a harness
  that DERIVES the count by scanning the pattern for `\<digit>` is a SECOND
  IMPLEMENTATION OF §5's octal rule, and it gets the same cells wrong that
  §5 exists to get right. `(a)\10` is octal and contains ZERO
  backreferences; `(a)\18` is `\01` + `'8'` and contains zero. Those are
  S-BR8's own fixtures. A scanner that counted them as one or two would make
  the complement check red on a correct compiler, or — worse, since the
  scanner and the emitter would drift in the same direction — green on an
  incorrect one. So the column holds an integer a human wrote beside the
  pattern, and **octal-ambiguous patterns are either kept out of the fixture
  set or carry an explicitly declared count with a comment saying why**.
- Counting on the ARTIFACT side is per-call and **token-level
  comment-stripped**, not line-level. (C2(c).) §3.2.3's emitted call spans
  two physical lines and carries an intent comment on the first, so a
  line-based strip leaves a trailing `// ... rx_bref_match ...` on the call
  line and a comment alone can satisfy the count. The strip removes `/* */`
  and `//` regions from the whole function body before any matching, in ONE
  pass over the body rather than a second walk: `calls_in_bodies()` gains the
  stripping and both its callers use the stripped text, so the existing
  violation rule and the new count rule cannot disagree about what a comment
  is. **S68 must still fire after that refactor** — it does, and the reason
  is that S68's sabotage puts a real CALL in a hot loop, not a comment, so
  stripping comments cannot hide it; the panel verified the anchor survives.
- **A SCOPED non-vacuity guard, asserted EXACT.** (C2(b).) All six existing
  fixtures declare zero bref entries and get zero, so the complement check is
  satisfied over an empty population — delete this module's fixture rows and
  it stays green. The guard is therefore not the global "found no residual
  entry" one (`run_codegen_tests.sh:1013`), which `next_pos` keeps satisfied
  unconditionally: it is **"at least N fixtures declare >= 1 bref entry", with
  N a literal asserted in the check**, in this file's own exact-count
  convention. A run that finds fewer has lost its population and says so.
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
`Ctx.named_groups` (the fields at `src/core/internal.h:665-666`; the
quoted characterisation is its comment at `:649-664`), which is already "a
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

**SELECTED AND REORDERED from `out/expand_cost.txt`, which R32 C15 was right
to flag**: the first draft said "pasted", and the figures are verbatim but the
rows are ordered by `|L(G)|` and three of the ten (`quote`, `cls3`, `cls2x2` —
all small and all compiling) are omitted. Read the file for all ten. The
distinction matters because "pasted" is this document's own promise that a
table and its archive cannot drift, and a selection is a weaker claim that
should be stated as one:

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
> **7,116,509 bytes of emitted C** and ~2 s of gcc (1.99 / 2.07 / 2.00 s
> across three runs of this lane's own).

**The boundary REPRODUCES — now four times, one of them independent.** Three
runs of this probe from different working trees and a FOURTH by the R32 panel
from a third tree all bisect to 10,525/10,526 with identical pattern and
emitted-C byte counts (73,674 B and 7,116,509 B); only the gcc seconds jitter.
So the number is a property of the compiler's caps, not of a run.
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

### 7.2 The erasure is a superset ONLY FOR AN ASSERTION-FREE GROUP, and its span is useless either way

**CORRECTED AFTER R32 E2.** The first draft claimed the erasure "is a genuine
SUPERSET — as it must be, since the captured text is always in the referenced
group's language". The premise is false when the group is not a *language* at
all.

MEASURED, `out/erasure_hazard.txt`'s POSITIVE CONTROL — cells that put a
POSITION PREDICATE inside the referenced group, every construct shipping in
pcrec today:

| true pattern | erasure | subject | true | erased | false negative? |
|---|---|---|---|---|---|
| `(\ba)\1` | `(\ba)\ba` | `"aa"` | (0,2) | **None** | **yes** |
| `^(\ba)\1$` | `^(\ba)\ba$` | `"aa"` | (0,2) | **None** | **yes** |
| `^(^a)\1$` | `^(^a)^a$` | `"aa"` | (0,2) | **None** | **yes** |
| `^(\Ga)\1$` | `^(\Ga)\Ga$` | `"aa"` | (0,2) | **None** | **yes** |
| `^x((?<=x)a)\1$` | `^x((?<=x)a)(?<=x)a$` | `"xaa"` | (0,3) | **None** | **yes** |
| `(\bfoo)\1` | `(\bfoo)\bfoo` | `"foofoo"` | (0,6) | **None** | **yes** |
| `(a)\1` | `(a)a` | `"aa"` | (0,2) | (0,2) | no |
| `(\w)\1` | `(\w)\w` | `"aa"` | (0,2) | (0,2) | no |
| `^(a\|b)\1$` | `^(a\|b)(a\|b)$` | `"aa"` | (0,2) | (0,2) | no |

**6 of 10 FALSE NEGATIVES.** The reason is one sentence: a group containing an
assertion does not denote a set of strings, it denotes a set of strings *at
positions*, and substituting a copy of the group re-evaluates the assertion at
the REFERENCE's position rather than at the group's. `\b` before the second
`a` of `"aa"` is false; `\b` before the first is true; the captured TEXT does
not carry that.

**AND ASSERTION-FREEDOM IS NECESSARY BUT NOT SUFFICIENT (R32 re-check E12).**
An ATOMIC group or POSSESSIVE quantifier beneath the referenced `A_CAP`
breaks the superset for a second structural reason, and the first revision of
this section replaced a GAP with a CONDITION and lost it — §13 P-7 still
named "no family contains an atomic or possessive group" as an open gap while
§7.2 stated a condition that did not mention them. MEASURED, same positive
control:

| true pattern | erasure | subject | true | erased | false negative? |
|---|---|---|---|---|---|
| `^(a*+)b\1a$` | `^(a*+)b(?:a*+)a$` | `"abaa"` | (0,4) | **None** | **yes** |
| `^(a*+)b\1a$` | `^(a*+)b(?:a*+)a$` | `"aabaaa"` | (0,6) | **None** | **yes** |
| `(a*+)b\1a` | `(a*+)b(?:a*+)a` | `"abaa"` | (0,4) | **None** | **yes** |
| `^((?>a*))b\1a$` | `^((?>a*))b(?:(?>a*))a$` | `"abaa"` | (0,4) | **None** | **yes** |
| `^([ab]*+)c\1a$` | `^([ab]*+)c(?:[ab]*+)a$` | `"abcaba"` | (0,6) | **None** | **yes** |
| `^(a++)b\1a$` | `^(a++)b(?:a++)a$` | `"aabaaa"` | (0,6) | **None** | **yes** |
| `^(a*)b\1a$` (greedy CONTROL) | `^(a*)b(?:a*)a$` | `"abaa"` | (0,4) | (0,4) | no |
| `^(a*?)b\1a$` (lazy CONTROL) | `^(a*?)b(?:a*?)a$` | `"abaa"` | (0,4) | (0,4) | no |

**6 of 8, with both non-possessive controls holding.** The reason is the same
shape as the assertion one: **the erased COPY commits without regard to what
follows it.** `(a*+)` captures all the `a`s; the reference then compares that
TEXT, which is a fixed string and re-decidable by the surrounding
backtracking. The erased copy is a fresh possessive loop that eats the
following `a` and cannot give it back. A backreference is never atomic even
when the group it names is.

**So the corrected gate is: the erasure is a superset IFF the referenced
group is ASSERTION-FREE *and* ATOMIC/POSSESSIVE-FREE.** Both halves are cheap
and syntactic — beneath the referenced `A_CAP`, no
`A_BOL`/`A_EOL`/`A_END`/`A_WORDB`/`A_NWORDB`/`A_GSTART`/`A_KRESET`, no
lookaround, and no atomic group or possessive quantifier. **[M6.4] lands
first, so the second half's population is LIVE from the day this module
ships** — it is not a future concern.

**This does NOT touch §7.1's ruling**, and the direction is why: §7.1 refuses
the prefilter outright, which is the safe side of an unsound approximation.
E2 makes the refusal MORE justified, not less. What it does touch is §7.4's
chartered follow-on, which assumed soundness it does not have.

**The family table, on DISTINCT subjects (R32 C8).** The first draft sampled
with replacement and reported the raw draw count, inflating three families
31.5x, and carried a `finite` family that is the same language pair as
`letter` over the same subject list — seven families were six:

| idiom | distinct subjects | true hits | FALSE-NEG | **SPAN DIFF** | nomatch agreement |
|---|---|---|---|---|---|
| `(["'])[^"']*\1` | 4,000 | 1,744 | **0** | **389** | 1322/2256 (59%) |
| `<([a-z]+)>[^<]*</\1>` | 4,160 | 24 | **0** | 0 | 4064/4136 (98%) |
| `\b([a-z]+)\s+\1\b` | 3,279 | 350 | **0** | **100** | 940/2929 (32%) |
| `([0-9]+)-\1` | 1,093 | 280 | **0** | **220** | 597/813 (73%) |
| `(\w)\1` | 127 | 114 | **0** | **52** | 3/13 (23%) |
| `(a*)b\1` | 127 | 120 | **0** | **78** | 7/7 (100%) |

12,786 distinct subject-family pairs over six families. Two conclusions,
pointing in opposite directions:

- **FALSE-NEG is 0 in all six** — and that zero is now a MEASUREMENT rather
  than a tautology, because the positive control above shows the column can
  move. None of the six families has an assertion inside the referenced
  group, which is exactly the condition the corrected claim names.
- **SPAN DIFF is large in five of six.** Concrete cells from the archive:
  `(["'])[^"']*\1` on `"\"''"` is truly (1,3) and the erasure says (0,2);
  `([0-9]+)-\1` on `"11-1"` is truly (1,4) and the erasure says (0,4);
  `(a*)b\1` on `"ba"` is truly (0,1) and the erasure says (0,2). **Every one
  is a window the hybrid would hand the VM wrong**, and a VM anchored to
  (0,2) on `"\"''"` does not find the (1,3) match.

Span divergence is independent of the assertion question: it is large even on
the families where the superset property holds. So the erasure fails
`engine_m4.md` §6.1's exact-window role twice over, and §7.1's rule stands.

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
| quote | nomatch | 0.00024435 | 0.00191383 | **7.8x slower** |
| quote | latematch | 0.00023128 | 0.00195345 | **8.4x** |
| tag | nomatch | 0.00001089 | 0.00077490 | **71.2x** |
| tag | latematch | 0.00000538 | 0.00077801 | **144.6x** |
| digits | nomatch | 0.00022515 | 0.00191765 | **8.5x** |
| digits | latematch | 0.00022821 | 0.00190879 | **8.4x** |
| dupword | nomatch / latematch | 0.00000011 / 0.00000028 | 0.00000008 / 0.00000008 | **NOISE** (see below) |
| letter | nomatch / latematch | 0.00000007 / 0.00000003 | 0.00000005 / 0.00000002 | **NOISE** |

**The RATIOS ARE STABLE IN ORDER OF MAGNITUDE AND NOT IN THEIR DIGITS, and a
reader should not quote one.** SEVEN runs of this probe across the lane and the R32
revision gave quote **7.8-21.7x**, tag **63.9x and upward — a seventh run
reached 172.9x, above what six runs had suggested was a ceiling** — and
digits **6.2-20.9x**. R32 independently reproduced ratios inside those
ranges, with rows swapping between runs exactly as this paragraph predicts.
**The tag range is stated as OPEN-ENDED UPWARD rather than closed** (R32
re-check N6): its hybrid arm is the fastest of all six and therefore the most
sensitive to where the filler's first candidate byte lands, so a bounded
ceiling is a claim the instrument does not support. Read the direction and
the order of magnitude; do not quote an endpoint. The
vm-only arm barely moves between runs; the HYBRID arm is multi-modal across
roughly 0.000004-0.00023 s, and that is what makes the ratio jump — a
prefilter that skips almost the whole subject is measuring a memchr whose
cost depends on where the first candidate byte lands, which the filler's
period decides. Treat the DIRECTION and the ORDER as established and the
digits as not. The design's ruling does not turn on which end of those ranges
is right, and this document deliberately quotes the range rather than a
run.

**The two NOISE rows are a RESULT, not a failed measurement**, and they are
the honest counterweight to the two-orders-of-magnitude rows: for
`\b([a-z]+)\s+\1\b` and `(\w)\1` the *erasure matches at offset 0* on a
subject the true pattern never matches, so the over-approximation filters
nothing and a hybrid built on it would buy nothing **even if it were sound**.
That is the same fact §7.2's last column reports as **32% (dupword) and 23%
(letter)** selectivity — figures the C8/C9 re-measurement moved, and which an
earlier revision of this paragraph still quoted as "40% and 2%" (R32 re-check
N3).

**So the cost of the ruling is roughly one to two orders of magnitude on the
families where a prefilter would have helped, and zero on the families where
it would not** — and there is no way to tell which is which without the very
analysis §7.4 charters.

### 7.4 What is chartered rather than built

Two sound weaker uses, neither in this module:

- **A NOMATCH-ONLY prefilter, GATED ON A REFERENCED GROUP THAT IS BOTH
  ASSERTION-FREE AND ATOMIC/POSSESSIVE-FREE.**
  The erasure never false-negatives *under BOTH conditions* (§7.2, corrected
  after R32 E2 and again after the re-check's E12), so running it and
  answering `nomatch` outright is sound there and UNSOUND without either half
  — the first draft chartered this with no condition at all, and the first
  revision with only the assertion half.
  Measured selectivity on the six families, all of which satisfy the
  condition: 23% to 98%, with three above 59%. It needs a second AST (the
  erasure is a real rewrite), a second NFA/DFA build, the assertion-free
  gate, and its own measurement of whether the second build pays for itself
  — a `discharge`-socket-shaped piece of work, and the same follow-on row
  §6.3 charters is the natural home. **The gate is not optional and is the
  first thing that row must build**: without it the feature deletes real
  matches, which is the one failure class D26 refuses outright.
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
`mod_modifiers.c`'s `case 'J'` (`src/parse/mod_modifiers.c:323-357`) sets and
clears it instead of refusing, and `ng_is_duplicate`'s refusal
(`src/parse/mod_named_groups.c:89-95`, `:131-135`) becomes conditional on the
flag at the declaration site.

**The `(?J)` refusal's long comment retires with it.** That comment
(`mod_modifiers.c:324-356`) records two earlier wordings that were both wrong
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

The comparator in `emit_info_def`'s `qsort` gains the number tiebreak — and
**it is a CORRECTNESS requirement, not the reproducibility nicety an earlier
revision of this paragraph called it.** R32's re-check (N1) prompted reading
the two sites together: `mod_named_groups.c:154-155` PREPENDS each
declaration onto `Ctx.named_groups`, and `emit_dfa.c:676-677` walks that list
from the head, so the array reaching `qsort` is in **descending** group
number. Under a name-only comparator and a stable sort — glibc's is a merge
sort — the emitted rows for one name would come out **(name asc, number
DESC)**, and §8.2's caller algorithm (walk back to the run's first row, then
forward to the first participating one) would then select the
HIGHEST-numbered participating group. That is exactly the rule §8.3's `"xyy"`
cell rules out.

So without the tiebreak the reflection table would encode the WRONG
resolution rule, silently, on the platform pcrec is developed on. The
reproducibility argument (an unstable `qsort` leaves equal rows in
unspecified order) is also true and is now the SECOND reason rather than the
first. D59 left the tiebreak unpinned; this module pins it, and §11.4's
S-BR17 detects its absence STRUCTURALLY — reading the emitted rows' order off
the artifact — rather than behaviourally, because a behavioural row here
depends on `qsort`'s stability and the list's direction agreeing, which is
not a control.

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
machinery is here.

**RULED (ASK-1): the attribution MOVES to `backrefs`, and the page notes the
SPLIT.** The compliance text at 877-880 currently attributes the letter to
`named-groups` ("duplicate NAMES are named-group semantics"), which is right
about the DECLARING half and silent about the RESOLVING half. The annotation
becomes: **declaring a duplicate name is `named-groups`; resolving a reference
to one, and the `(?J)` letter itself, is `backrefs`.** Because the page is a
derived artifact under [DOC-DRV], this is a keyed-annotation edit through the
`compliance-refresh` skill — the generated index regenerates from the registry
and the prose row is reconciled against it, so there is no way for the two to
drift. Line 1001's revisit trigger FIRES with this module and the entry
closes.

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

**Two caveats on that table, both R32 C6.** First, `built_status_probe` drives
each row's `syntax` field ALONE, and `\1`, `\k<name>` and `(?P=n)` are all
ERROR 115 standalone in PCRE2 (no such group). They classify `built` only
because §5.3 defers reference VALIDITY to end of parse, so the doorway
produces a node and the refusal comes later — the built-status classifier
reads `ExtResult.answered_at`, not the eventual verdict. That dependency is
real and is cited here rather than left implicit. Second, the column's
granularity is the ATOM POSITION only: `[\1]` compiles in every feature set
today (P6) while `\1` reads `unbuilt`, and after this module `\1` reads
`built` with `[\1]` unchanged. Neither is a defect; both are facts a reader
of the index needs.

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

| `--features` | `(a)\1` | `(?J)(?<a>x)(?<a>y)` | `\k<n>` | `(?<n>a)\k<n>` |
|---|---|---|---|---|
| `std1` | refuse: needs `backrefs` | refuse: needs `backrefs` | refuse: needs `backrefs` | refuse: needs `backrefs` |
| `backrefs` | **compiles** | refuse: needs `modifiers` | refuse: needs `named-groups` | refuse: needs `named-groups` |
| `backrefs,modifiers` | **compiles** | refuse: needs `named-groups` | refuse: needs `named-groups` | refuse: needs `named-groups` |
| `backrefs,named-groups` | **compiles** | refuse: needs `modifiers` | **REFUSE: error-115 class** | **compiles** |
| `backrefs,modifiers,named-groups` | **compiles** | **compiles** | **REFUSE: error-115 class** | **compiles** |

**R32 C7: the bare `\k<n>` cell is a REFUSAL, not a compile.** `\k<n>` names
a group `n` that the pattern never declares, and PCRE2 answers error 115
(measured, `out/spellings.txt`'s `\k<name>` row is `^(?<n>a)\k<n>$` — the
DECLARED form). The first draft's table pinned the undeclared form as
compiling, which `gated.rxt` would have turned into a tier-1 divergence
against libpcre2. The fourth column is the declared form and is the cell that
actually exercises the module. **Every accept cell in `gated.rxt` is
oracle-verified against libpcre2 before it is written** — a gating suite's
cells are as much a compatibility claim as a corpus's.

**AND THE `--no-captures` AXIS (R32 E6), which the first draft omitted
entirely:**

| build | `(a)\1` on `"aa"` | `rx_info.ncaps` | `caps[1]` |
|---|---|---|---|
| default (captures on) | (0,2) | 2 | (0,1) |
| `--no-captures` | **(0,2) — must still match** | **1** | not delivered |

Under `--no-captures` no `A_CAP` node is created at all
(`src/parse/parse.c:704-708`), so §6.3's ruling applies: a group NAMED BY A
BACKREFERENCE keeps its internal slots (§3.2.4's three) and reports none.
`--no-captures '(a)\1'` must match `"aa"` and must deliver no group offsets.
§11.2's driver carries the arm.

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

Shaped on `tests/assertions/`, whose `CLAUDE.md` is the model and whose oracle
discipline is the part that transfers. **The oracle column below is per FILE
and, where R32 C3 found the first draft wrong, per CELL** — a whole-file
marking that is right for most of a file and wrong for four cells loses the
oracle exactly where the module is load-bearing.

| file | contents | oracle |
|---|---|---|
| `numeric.rxt` | `\1`..`\9`, unset, empty, quantified (§3.3, §3.4, §3.6) | python-verifiable — MEASURED 0 divergences on all U/E/Q/N/P cells |
| `octal.rxt` | §5's rules 1-4 and 3', atom position, with discriminator subjects | **`# pcre2-only`** |
| `octal_class.rxt` | §5.2's must-not-change class cells, module ON | **MIXED — per cell.** 8 of 12 python-verifiable; `[\8]` `[\9]` `[\k]` `[\g]` are the LITERAL characters in PCRE2 and pcrec and are ERRORS in python; `[\400]` is a refusal cell |
| `selfref.rxt` | §3.5's S and F cells **plus §3.2's RE-ENTRY class** | **`# pcre2-only`** — python refuses all of them at compile time |
| `spellings.rxt` | `\g`/`\k`/`(?P=n)` (§2) | **`# pcre2-only`** except the `(?P=name)` rows |
| `caseless.rxt` | §4's axis-B scoping cells and the 52-byte fold | **MIXED — per cell.** 5 of 9 python-verifiable; `^(?i)(a)(?-i)\1$` and `^((?i)a)\1$` are ERRORS in python ("global flags not at the start"), and those two are precisely §3.1(c)'s and F7's load-bearing cells |
| `dupnames.rxt` | §8's resolution cells **plus RE-ENTRY cells over a name run** (R32 re-check E13 — the first draft's file had none, so S-BR15b would have had no detector): `(?J)^(?:(?<a>q))?(?:(?<a>a\|b\k<a>))+$` on `"aba"`, `(?J)^(?:(?<a>a\|b\k<a>))+$` on `"aba"`, `(?J)^(?<a>x)(?:(?<a>a\|b\k<a>))+$` on `"xbx"` | **`# pcre2-only`** — python has no `(?J)` and no `\k` |
| `nested.rxt` | §3.7's N cells, the cut interaction, and the revdet group-in-body shape (§3.6) | python-verifiable for N1-N6 |
| `nocaps.rxt` | §6.3/§10's `--no-captures` axis (R32 E6) | libpcre2 for the match; the ncaps/slot facts are pcrec-only reflection assertions |
| `gated.rxt` | §10's two matrices | n/a for refusals; **every ACCEPT cell oracle-verified against libpcre2 first** (R32 C7) |

**THE `selfref.rxt` ADDITION IS E1'S LANDING CONDITION.** The re-entry class —
`(a|b\1)+`, `^(?:(a|b\1)y)+`, `^(?:(a|b\1))+$` and their relatives — is the
population that refuted §3.2's first draft, and the first draft's `selfref.rxt`
took only the S/F cells that AGREED. Cells that agree under both publication
disciplines cannot detect the difference between them; the file must carry the
ones that do not.

**Every `# pcre2-only` marking and every per-cell exclusion goes into
`docs/dev/upstream_issues.md`** under the standing rule
`tests/assertions/CLAUDE.md` states. Four entries, not one: the S/F compile
refusals, the `(?i)`-placement refusals, the class-position literal
divergences, and the total `(?J)`/`\k` absence. §12 carries them to the D27
author.

### 11.2 The differential drivers

Two, and they follow `run_kreset_diff.sh` in a way the first draft's citation
did not: R32 C10 found that driver has **six sections and three population
guards**, where the first draft described one section and no guard.

**`run_backref_diff.sh`**, sections:

1. **The subject sweep**, both pcrec engines against libpcre2, over a
   generated space with startpos taking EVERY value in `[0, n]`. Not
   optional: `(a)\1` on `"xaa"` is (1,3) at startpos 1 and no match at
   startpos 2 (cells P1/P2), so a suite that fixed startpos could not tell a
   correct implementation from one that ignores the argument.
2. **The three entries** — `<prefix>_search`, `<prefix>_match`,
   `<prefix>_match_caps` — because a `.rxt` block drives only the first. The
   match-here oracle is `\G(?:PAT)` exactly as wave E used it.
3. **The RE-ENTRY arm** (§3.2), which is where publish-at-close is observable
   and nowhere else.
4. **The `--no-captures` arm** (R32 E6): the match must be identical and
   `rx_info.ncaps` must be 1.
5. **The find-all loop**, since a backreference's span feeds the next
   iteration's startpos.
6. **The `--engine=dfa` refusal** (§6.2), by name, with the module enabled.
7. **THE SPAN-DIVERGENCE SECTION**, which exists for exactly one sabotage and
   is named here so S-BR14 has a detector rather than a gesture (R32 re-check
   N5). Its population is the subjects on which the backref-ERASED
   approximation reports a DIFFERENT span from the true pattern — §7.2's
   measured cells, including `"\"''"` for `(["'])[^"']*\1` (true (1,3),
   erased (0,2)), `"11-1"` for `([0-9]+)-\1` (true (1,4), erased (0,4)) and
   `"ba"` for `(a*)b\1` (true (0,1), erased (0,2)). Each is asserted against
   libpcre2. **Its population guard is its own**: an EXACT count of
   span-diverging subjects present, because a prefilter sabotage is invisible
   on any subject where the two spans agree, and a section that quietly lost
   those subjects would pass while the compiler miscompiles.

Four POPULATION GUARDS, asserted EXACT rather than as floors, because every
one of them is a way for the suite to pass while measuring nothing:

- the number of cells whose pattern actually contains a backreference;
- the number of re-entry cells (section 3) — a run reporting zero divergences
  with an empty re-entry population is the first draft's `selfref.rxt`;
- the number of cells where the two engines DISAGREE, which must be 0, paired
  with a nonzero count of cells where both produced a match (an all-refusal
  run agrees trivially);
- the number of SPAN-DIVERGING subjects in section 7 (above), which is
  S-BR14's whole detector.

**`run_dupnames_diff.sh`** sweeps §8.3's resolution rule over generated
name-runs of size 1-4 with every subset participating, against libpcre2, with
the same exact-count guard on runs of size >= 2. The rule is a CHOICE AMONG
CANDIDATES; §8.3's table shows a hand-picked set is needed to separate four,
and a sweep is what shows no fifth fits.

The cross-module cell from §3.7 — a possessive quantifier followed by a
backreference into it — goes in `run_backref_diff.sh` rather than a `.rxt`,
because it needs module `atomic-groups`.

### 11.3 The identity gate

`tests/codegen/run_backref_identity.sh`, with the reference built from a
**pinned pre-module commit via `git archive`**, not from a `-D` knob — and
RULED (ASK-4) as a **ONE-SHOT sweep** rather than an ongoing gate, on the same
reasoning as R31/atomic §11.2: **no stage of this module runs on the control
population**, so a `-D` knob would gate dead code and the cheapness argument
that justifies the four shipped gates' knob does not apply. The first draft
argued the opposite ("this gate is ongoing, not one-shot"); the ruling
supersedes it.

The commit-pinned choice is not stylistic. `assertions_measurements/out/CLAUDE.md` records
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

**R32 C4 refuted the first draft's completeness**: it had no row for the
WRONG-ANSWER failure mode §7.2 measures, none for §5.3's deferred validity,
none for §8.2's qsort tiebreak, and none for engine registration. Those four
are added, S-BR14 first because it is the one whose failure is a wrong answer
rather than a refusal. E1, E8, E9 and SR-8 add four more.

| id | sabotage | what must fail | why it is not covered otherwise |
|---|---|---|---|
| **S-BR14** | **a DFA prefilter is attached to a backref pattern** (`fit.prefilter` forced true) | **`run_backref_diff.sh` §7, the SPAN-DIVERGENCE section** (§11.2) | **the wrong-answer mode.** §7.2 measures spans differing on up to 389 subjects in one family; nothing else in the suite would notice, because every refusal still refuses and every non-prefiltered pattern still passes |
| **S-BR15** | **publish-at-OPEN restored** (`A_CAP` writes the pair on traverse) | `selfref.rxt`'s re-entry cells, `run_backref_diff.sh` §3 | E1 exactly. 138 divergences and 40 reversed-span cells in the 5,808-cell sweep — and ZERO in the backref-free population, so no existing suite sees it |
| **S-BR15b** | **only the "resolved" member of a dup-name run is marked** (publish-at-close applied to one member, not the run) | `dupnames.rxt`'s re-entry cells, `run_dupnames_diff.sh` | R32 re-check E13: §8.3's chain reads EVERY member at match time, so an unmarked one is read under write-on-traverse and E1 returns through it. Invisible to every cell where the first member resolves |
| S-BR1 | the unset test becomes `ref_e > ref_s` | `numeric.rxt`'s E cells | turns every empty capture into a failure; every non-empty cell still passes |
| S-BR2 | the `caseless` field is ignored | `caseless.rxt` | D62 control 3's residual; no compiler diagnostic |
| S-BR3 | `vm_nullable` returns false for `A_BREF` | `numeric.rxt` Q6 | an unguarded nullable body is a hang, not a wrong answer — caught by the harness's derived timeout |
| S-BR4 | `revdet.c`'s `rd_shape` gains an arm ACCEPTING `A_BREF` | `nested.rxt` | the `-Wswitch` alarm says an arm is missing, not which arm is right |
| S-BR5 | the compare is inlined instead of calling the seam entry | `codegen` (§4.4's fixture-declared count) | **changes no answer** under the byte backend — the S68 shape |
| S-BR6 | the module's atom port also claims the CLASS position | `octal_class.rxt` | 12 base cells a module-off run cannot see |
| S-BR7 | the gate check is dropped from the new atom port | `reject` | a construct that compiles with its module off |
| S-BR8 | rule 3's count uses the whole pattern instead of "so far" | `octal.rxt` | every groups-before cell still passes; only `\10(a)..(j)` fails |
| **S-BR8b** | rule 3' routed through the octal branch (an 8/9-led run) | `octal.rxt` axis-E cells | the octal branch consumes zero digits, so the failure is a silent mis-parse, not an error |
| S-BR9 | §8.3's resolution takes the first by NUMBER rather than first SET | `dupnames.rxt` | the `"yy"` cell only |
| S-BR10 | §8.3's resolution takes the LAST set | `dupnames.rxt` | the `"xyy"` cell only |
| **S-BR11** | the residual entry's fold table diverges from `cls_casefold` by one byte | the 256-byte agreement check (§4.1) | two spellings of one fact with no control between them — R32 E8 |
| **S-BR12** | an `A_BREF` node is left UNSTAMPED (defaults to `ANY_ENGINE`) | `registry`/engine-selection, and §6.2's refusal by name — **only after [M6.4.2] lands SR-8** | SR-8's unsound-direction default (R31 M-1 note 2): the pattern silently routes to the DFA and miscompiles. **CROSS-MILESTONE: this row has no detector until the stamping mechanism it sabotages exists**, so it lands with [M6.5.2] but cannot be validated before [M6.4.2]; the mech matrix must not count it as passing in the interval |
| **S-BR13** | the revdet capture suppression drops the PENDING slot but keeps the pair | `nested.rxt`'s group-in-body cells | R32 E9's unnamed interaction; correct today by accident, and publish-at-close is what makes it designable |
| **S-BR16** | §5.3's deferred validity check is skipped | `octal.rxt`, `gated.rxt` | a reference to a nonexistent group is SILENTLY ACCEPTED and then reads `PCREC_UNSET` forever — a pattern that should be error-115 becomes one that never matches |
| **S-BR17** | §8.2's qsort number tiebreak removed | **a STRUCTURAL assertion** (see below), not a behavioural suite | R32 re-check N1: a behavioural row cannot be trusted to go red here, in EITHER direction |

**S-BR17 IS STRUCTURAL, AND THE RE-CHECK'S REASON IS NOT THE RIGHT ONE —
THE REAL ONE IS WORSE (R32 re-check N1).** The re-check measured glibc's
`qsort` preserving insertion order for equal keys (it is a merge sort unless
memory-starved) and concluded S-BR17 cannot go red. Its harness inserted rows
in ASCENDING group order. **pcrec does not.** `mod_named_groups.c:154-155`
PREPENDS each declaration (`g->next = cx->named_groups; cx->named_groups =
g;`) and `emit_dfa.c:676-677` walks that list from the head, so the array
handed to `qsort` is in DESCENDING group number. (STRUCTURAL, both sites
cited; no duplicate-name pattern compiles today, so it is not observable
behaviourally yet.)

Two consequences, and the second is a correction to §8.2:

- Under a stable sort with a name-only comparator, pcrec's array yields
  **(name asc, number DESCENDING)** — the wrong layout. So S-BR17 *would*
  go red on glibc, contrary to the re-check's conclusion, but only because
  glibc happens to be stable and the insertion order happens to be reversed.
  A row that depends on two unspecified properties agreeing is not a control.
- **Therefore the tiebreak is a CORRECTNESS requirement, not the
  reproducibility nicety §8.2 called it.** Without it the emitted table is in
  descending number within a name-run, and §8.2's caller algorithm — walk back
  to the run's first row, then forward to the first participating one — then
  selects the HIGHEST-numbered participating group. That is precisely the
  resolution rule §8.3's `"xyy"` cell exists to rule out. §8.2 is corrected.

**The detector is structural**: assert that the emitted `rx_group_entry` rows
are non-decreasing in `(name, number)` — read off the artifact, independent of
the comparator that produced them — plus a comparator-totality assertion (it
returns 0 only for rows equal in BOTH fields). Neither depends on `qsort`'s
stability, on the list's direction, or on a duplicate-name pattern existing.

S-BR8/S-BR8b, S-BR9 and S-BR10 exist as separate rows on purpose: each is a
plausible implementation, each passes the majority of the corpus, and each is
caught by exactly one cell. A single "the rule is wrong" sabotage would not
show that the corpus discriminates between them.

### 11.5 The registry checks, and what this module MOVES

**REWRITTEN AFTER R32 M-1/C1.** The first draft said this module's rows would
leave the tripwire population "the same movement D59 recorded for
`named-groups` (51 → 48)". That is wrong twice, and the second error hid the
first.

- `named-groups`' three rows left the population by **RECLASSIFICATION** to
  `ANY_ENGINE` — the `r->engines & ENGM_DFA` test at
  `registry_check.c:1389` skips them before the wired-producer branch is ever
  reached.
- This module's twelve rows correctly KEEP `VM_ONLY` (§6.1), so they do not
  leave. **`qualifying` stays 48 and `wired` goes from 1 to 13**, which under
  the shipped check is twelve `bad(...)` hits.

Under D67 (SR-8 built in [M6.4.2]) the check itself changes shape: the `\K`
exception retires, and the demand becomes generic — every `RS_MODULE`,
non-DFA row with a producer must be STAMPED and must refuse `--engine=dfa` by
name. This module then adds twelve rows to the stamped-and-refusing
population and needs no exception.

**Three pins this module MOVES, each of which is hand-typed today:**

| pin | today | after |
|---|---|---|
| `registry_check.c:1473-1477`'s exact `qualifying` count | **48, hand-typed**, with a hand-written breakdown naming "12 ESC rows (`\K \k \g`, `\1..\7`, `\8 \9`)" | unchanged at 48 — but the breakdown comment's module attribution must be re-derived, and the `wired` count it does not currently assert must |
| the built/unbuilt tally | **33 built / 61 unbuilt / 6 na**, 100 rows (`registry_built_status_memo.md:382-384`) | **47 / 49 / 6, 102 rows** — fourteen rows flip (the twelve tripwire rows, `\0`, `(?J)`) and TWO are added born unbuilt (`\g<`, `\g'`). §13 P-11 carries the arithmetic and the warning that the tripwire's 48 and the tally's 94 are different sets |
| `tests/reject/`'s `reject_gated` pins | `\k` pinned as an enabled-but-unbuilt control | `\k` leaves that population; the pin must move to a still-unbuilt row |

**AND THE BUILT-STATUS TALLY IS ASSERTED BY NOTHING TODAY (R32 C5).**
`check_built_status_defects` (`registry_check.c:1694-1744`) asserts
`defects == 0` only; the built/unbuilt counts are interpolated into the `ok()`
STRING and compared against nothing, and PC-3 never reads the column. So
"33/61" is a number in a memo with no test behind it, and §9's seven-row
prediction table would have had no check either.

**RULING (cross-panel, lands in [M6.4.2] as the first module to flip rows):**
`registry_check` asserts the built/unbuilt/na tallies EXACT, in this file's own
established convention (`check_class_ports`, `check_class_syntax_reach`), and
each module's landing moves them. R31 C8's pins join the same assertion. This
module's obligation is therefore to MOVE a number that will by then be
asserted, rather than to introduce the assertion — and to state its movement,
which is the table above.

`check_engine_capability_tripwire`'s counts must be **re-derived from a run,
never copied into prose** — `tests/mech/CLAUDE.md`'s founding complaint, and
the reason the twelve-row figure in §6.1 is cited to a `--list-syntax` query
rather than to this document.

---

## 12. Appendix — the goal-facts list for the D27 blinded author (charter (g))

For the author of `tests/backrefs/d27/`, working from the PCRE2 goal with
`src/` and `tests/` denied. **libpcre2 10.46 is the oracle of record.** There
is no `pcre2test` binary on this box; drive libpcre2 through ctypes.

**POINTERS THE CELL ALLOWLIST ACTUALLY PERMITS (R32 C11).** The first draft
pointed at `tests/named_groups/d27/lib_pcre2.py` and
`tests/assertions/verify_pcre2.py` — both under `tests/`, which a D27 cell
DENIES, so the brief named files its own reader cannot open. The usable
pointers are under `docs/`:
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py` (the binding) and
`docs/design/backrefs_measurements/probes/br_oracle.py` (this lane's
extension: compile-error NUMBERS, the name table, and three
behaviourally-self-checked option bits).

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

**F14. A REFERENCE INSIDE A RE-ENTERED GROUP SEES THE LAST *COMPLETED*
ITERATION, not the one in progress.** This is the module's sharpest cell class
and the one an implementation is most likely to get wrong: `(a|b\1)+` on
`"ab"` is **(0,1) with group 1 = (0,1)** — the second iteration's `b\1` fails
because `\1` still holds iteration 1's completed capture `"a"`, not because
anything is unset. `^(?:(a|b\1)y)+` on `"aybay"` is (0,5) with group 1 =
(2,4). Write several; they cost nothing and they are where a plausible
implementation diverges.

**F15. python3 `re` refuses `(?i)` anywhere but the pattern start.**
`^((?i)a)\1$` and `^(?i)(a)(?-i)\1$` are libpcre2-legal and python compile
errors ("global flags not at the start of the expression"), so the two cells
that decide WHERE the caseless flag is read (F7) have no python oracle at all.

**F16. The CLASS position diverges from python too.** `[\8]`, `[\9]`, `[\k]`
and `[\g]` are the LITERAL characters `8`, `9`, `k`, `g` in PCRE2; python
rejects all four as bad escapes. `[\400]` is a PCRE2 error. So a class-position
cell written from python is either absent or wrong.

---

## 13. What would refute this — predictions for the panel

**REVISED AFTER R32.** Eight of the eleven predictions below are new or
rewritten; the three the panel confirmed are marked. The four HIGH findings
against the first draft were E1, E2, and (with the manager) M-1/C1 — none of
which this list anticipated, which is itself the most useful thing to say
about it.

**P-1. Publish-at-close is correct and sufficient (§3.2).** *Refuted by*: any
libpcre2 cell where a reference sees something other than the last COMPLETED
iteration of the referenced group. The 5,808-cell sweep found none, but its
alphabet is `{a,b,y}` and its subjects stop at length 4. The shapes most
likely to break it are ones this sweep cannot express: **nested backreferences
(a reference inside a group that is itself referenced), a `\K` inside a
referenced group, and a possessive/atomic quantifier around one** — R32 C20
named the first two as population gaps and they are still gaps.

**P-2. The pending slot is the whole cost (§3.2.4).** *Refuted by*: a shape
needing MORE than one pending slot per group, which would mean a group open
twice simultaneously. That needs recursion, which this module does not
implement — but `atomic-groups`' cut and a future `recursion` module are both
places to re-ask.

**P-3. Charging the compare's work is necessary (§3.8).** *Refuted or
confirmed by*: instrumenting a prototype with the compare uncharged and
running `(a*)\1` against a growing subject, counting bytes compared per step.
If the ratio is bounded the charge is unnecessary. I predict it is not. This
is still the one budget claim with no number behind it; §4.2's return protocol
now makes it EXPRESSIBLE, which R32 E4 found the first draft's version was
not.

**P-4. `--engine=dfa`'s captures branch mis-advises (§6.2).** *MEASURED on the
shipped binary and CONFIRMED by the panel.* The first draft's proposed FIX was
refuted (E5) and the second-why ruling replaced it.

**P-5. `RK_ESC` rows honour a tail selector (§9).** *CONFIRMED by the panel,
and it went further than this document did*: higher `rank` wins, the
arbitration has no kind branch, and disjoint tails cannot tie — so the
`\g<`/`\g'` split is available and the residual this document left open
(whether the existing `\g` row's rank permits it) is answered: it is rank 0,
so the two new rows outrank it.

**P-6. The expansion should not ship (§6.3).** *CONFIRMED — the boundary
reproduced three times from three trees.* Still refutable by a corpus of real
`--no-captures` backref patterns in which finite-language references are
common AND small; four of the five real idioms measured reference INFINITE
languages and cannot expand at all.

**P-7. The erasure is a superset (§7.2). REFUTED TWICE AND CORRECTED TWICE.**
R32 E2: it is not a superset when the referenced group holds an ASSERTION.
The re-check's E12: nor when it holds an ATOMIC group or POSSESSIVE
quantifier. 12 of 18 positive-control cells are false negatives across the
two reasons, with 6 controls holding.

**The second correction is the more instructive failure and it is mine.** The
first draft named the atomic/possessive gap in this very prediction. The
first revision replaced the GAP with a CONDITION — and stated the condition
as assertion-freedom alone, while leaving the gap sentence sitting two lines
below it. A reader of that revision had both halves in front of them and the
document never joined them. **A named gap is not a discharged gap**, which is
R30 M6's lesson ("a named defect is not a fixed defect") arriving one level
up: there the lane reproduced a defect it had just read about, here it stated
a condition beside the evidence that the condition was incomplete.

The corrected gate is assertion-free AND atomic/possessive-free. *Refuted
by*: a false negative in a family satisfying BOTH halves — none found in
12,786 distinct pairs across six families, and none in the eighteen control
cells. **The remaining honest gap**: no family in the sweep contains a
NESTED backreference (a reference inside a referenced group), which is the
third structural way a group could stop being a language, and it is untested
in either direction.

**P-8. The seam interface must change (§4.5).** *Refutable by* a size ruling I
recommend against on generality grounds. R32 E11 made the change slightly
larger than the first draft priced (`pcrec_enc_ready` moves too).

**P-9. The `(?J)` scoping rule (§8.1).** *CONFIRMED under a harder battery*,
including the separating cells this document added and the finding that an
inline `(?-J)` beats the API bit.

**P-10 (NEW). The complement check as now designed (§4.4) does not share a
source with its subject.** *Refuted by*: showing that a fixture's declared
residual-entry expectation can be satisfied by an artifact that inlines the
compare — e.g. if the per-site count can be met by a call the emitter makes
for some other reason. The count is "one call per `A_BREF` in the fixture's
pattern", and the pattern is test-authored, so I believe it cannot; this is
the claim the re-check should attack hardest, because its first version was
refuted for exactly this reason.

**P-11 (NEW, and CORRECTED after the R32 re-check — it was wrong twice).**
The first version predicted "+12/-12 plus `(?J)`", which conflated two
different row sets and forgot the two rows this module ADDS.

**The corrected prediction, checkable by one `--list-syntax` run at landing:**

| | today | after this module |
|---|---|---|
| `built` | 33 | **47** |
| `unbuilt` | 61 | **49** |
| na (`-`) | 6 | 6 |
| **total rows** | **100** | **102** |

The arithmetic, because the first version's error was in the accounting and
not in the measurement: **fourteen** rows flip to `built` — the twelve
tripwire rows, PLUS `\0` (module `backrefs`, `built=unbuilt` today, and
`ANY_ENGINE`, so it is *not* one of the twelve), PLUS `(?J)`. And **two rows
are ADDED born UNBUILT**: `\g<` and `\g'`, module `recursion` (§9). So
unbuilt is `61 - 14 + 2 = 49` and the table grows by two.

**THE TWO POPULATIONS ARE DIFFERENT SETS, and saying so is the point.** The
engine-capability tripwire counts `RS_MODULE` rows whose `engines` mask
EXCLUDES `ENGM_DFA` — 48 rows, twelve of them backrefs', `\0` excluded. The
built-status tally counts ALL 94 `RS_MODULE` rows plus 6 `na`. The tripwire's
48 is a subset of the tally's 94, they move for different reasons, and the
first version of this prediction used one number for both.

*Refuted by*: any row this module builds that the classifier does not
reclassify — most likely `\g`, if the `\g<`/`\g'` split somehow leaves the
base `\g` row without an atom producer.

**KNOWN GAPS, listed rather than discovered (R32 C20).** The erasure families
lack nested backreferences and `\K`; the `star` family's nomatch column rests
on only 88 negatives; the publish-discipline sweep has no atomic/possessive
arm; and the `--no-captures` slot-retention ruling (§6.3) has no measurement
behind it at all, because no build can produce one until the module exists.

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
- **`\0`'s GATING SPLIT — DECIDED (R32 C20), and the decision is "no change".**
  `\0` is octal, `ANY_ENGINE`, and needs no VM; one could argue it should
  therefore stop requiring module `backrefs` at all. It does not: `\0` shares
  the digit doorway and today refuses with "requires module 'backrefs'"
  (P1, measured), a `--features none` build has always refused it, and moving
  it to base grammar would be a compatibility change to the BASE tier made as
  a side effect of a module landing. It stays gated on `backrefs`, gains a
  producer with the rest of the digit rows, and its diagnostic stops sharing
  a code path with the nine backreference rows (§5.2). Not a regression: no
  build that accepts `\0` today stops accepting it.
- Matching PCRE2's specific error NUMBERS (115, 143, 144, 151, 164, 169).
  D26 tier 3: that a real syntax boundary refuses cleanly is exact; the
  wording and the number are not.

---

## 15. ASKs — ALL RULED (2026-08-22, with R32)

Kept with their answers rather than deleted, on the house rule that a design
document records what was asked and how it was settled.

**ASK-1 — `(?J)`'s compliance attribution. RULED: it moves to `backrefs`,
with the split noted** (declaring = `named-groups`, resolving + `(?J)` =
`backrefs`). Because `docs/pcre2_compliance.md` is a derived page under
[DOC-DRV], this is a keyed-annotation edit through the `compliance-refresh`
skill, not prose drift. §8.4's table carries the six sites.

**ASK-2 — a `PCREC_DUPNAMES` option bit. RULED: inline `(?J)` only.** No
consumer asks for the bit and `pcrec_options.flags` stays as D44.8 froze it.

**ASK-3 — the `--engine=dfa` branch-ordering fix. RULED: it lands in
[M6.4.2]'s engine slice**, which lands first and shares the population shape.
§6.2 stays as the defect record and now carries the SECOND-WHY ruling that
replaced the first draft's refuted fix (R32 E5).

**ASK-4 — the identity gate's reference. RULED: a ONE-SHOT commit-pinned
sweep**, the same ruling and the same reason as R31/atomic §11.2: no stage of
this module runs on the control population, so a `-D` knob would gate dead
code. §11.3 is restated on that footing rather than on the first draft's
"ongoing gate" framing.

**ASK-5 (raised by this lane after the tripwire measurement) — build SR-8 or
argue the exception. RULED (D67): SR-8 IS BUILT IN [M6.4.2]**, in D55's
specified shape — producers stamp each module-produced AST node with its row's
`engines` mask, one generic `EngineAnalysis` ANDs the stamps over the
post-discharge tree, `forces_kreset` and the `registry_check` exception retire
into it. §6.1 is rewritten against that contract and this module registers
nothing. The three contract notes this lane raised are recorded in R31 M-1;
notes 1 and 3 are the ones §6.2 and §6.3 depend on.

---

## 16. What R32 changed, in one table

For a reader who knew the 4cd461f draft. Every row is a section that now says
something different, not merely more.

| finding | the first draft said | it now says |
|---|---|---|
| **E1** | a non-UNSET slot pair is a capture; the UNSET test is total; self-reference needs no handling | **§3.2 PUBLISH-AT-CLOSE.** A re-entered group holds a half-open pair; 138 divergences and 40 `size_t` underflows in 5,808 cells; the pair is published together at close |
| **E2** | the erasure is a genuine superset | **§7.2** superset **iff the referenced group is assertion-free**; 6/10 control cells are false negatives otherwise; §7.4's charter gains the gate |
| **E3** | `\10`+ is a backref if the count allows, else octal | **§5 rule 3'**: a run beginning `8`/`9` is ALWAYS decimal (no octal reading exists); the disambiguation is four ordered questions; references above `\99` exist |
| **M-1/C1** | `forces_backref`, SR-8 deferred | **§6.1** `A_BREF` is STAMPED; SR-8 built in [M6.4.2] (D67); §11.5 rewritten — `qualifying` stays 48, `wired` goes 1→13 |
| **E5** | reorder the two branches | **§6.2** record a SECOND, node-derived `why`; the defect record stays, the fix travels |
| **E6** | `--no-captures` is the expansion's customer set | **§6.3/§10** — and under it NO `A_CAP` exists, so a referenced group keeps internal slots and reports none |
| **E7/C2** | the complement check, "one field wider" | **§4.4** fixture-DECLARED expectations, comment-stripped per-site counting, the scan-loop clause dropped |
| **C3** | `caseless.rxt` and `octal_class.rxt` are python-verifiable | **§11.1** per-CELL markings; 4/9 and 4/12 are python errors, including both load-bearing `(?i)`-placement cells |
| **C4** | ten sabotage rows | **§11.4** eighteen, led by the prefilter-on-backref WRONG-ANSWER row and publish-at-open |
| **C5** | the built column "gains this module's rows for free" | **§11.5** the tally is asserted by NOTHING today; the assertion lands in [M6.4.2] and this module states its movement (+12/-12, plus `(?J)`) |
| E4, E8, E9, E10, E11 | — | the return protocol carries the failure prefix; one shared fold table + a 256-byte agreement check; the revdet group-in-body interaction named; `-Wswitch` is a warning `make strict` promotes; `pcrec_enc_ready` joins the cost list |
| **re-check C2/N1/N2** | the complement check's count had no provenance; S-BR17 was behavioural; the tally prediction conflated two row sets | §4.4 (declared column + scoped guard + token stripping), §11.4/§8.2 (structural detector; the tiebreak reclassified as CORRECTNESS), §13 P-11/§11.5 (47/49/6 over 102 rows) |
| C6-C14, C15-C20 | — | §9's built predictions cite §5.3; `\k<n>` undeclared is a REFUSAL; distinct-subject counts and one family removed; the filler's letters now differ; drivers specified with six sections and exact guards; §12's pointers moved under `docs/`; four probe defects fixed; `\0`'s gating decided |

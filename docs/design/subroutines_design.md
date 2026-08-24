# Module `recursion` — subroutine calls: design

`[DD-14]`'s design gate. The constructs are `(?1)` `(?+1)` `(?-1)` `(?&name)`
`(?P>name)` `\g<1>` `\g<name>` `\g'1'` `(?R)` `(?0)` — and two more the
charter's list does not have, `\g<0>` and `\g'0'` (§2.4). The module name is
`recursion`; the primitive it builds is the **label call**, and `[DD-11]`'s
definition substitutions and `[M6.5]`'s follow-up (f) are its second and third
consumers.

Status: DESIGN, not implementation. No file outside
`docs/design/subroutines_design.md` and `docs/design/subroutines_measurements/`
was written by this lane.

---

## 0. How to read this

### 0.1 Claim marking

Adopted verbatim from `lookaround_design.md` §0.1, which took it from
`backrefs_design.md`, which took it from `assertions_design.md`, which took it
from `engine_m4.md`, so the panel reads one vocabulary:

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

A subroutine call is **the same pattern text run again from a different place,
with the capture state put back on the way out**, and almost everything below
follows from four measurements. (1) The callee **writes** the capture slots and
the **return restores** them — seen live through `pcre2_set_callout` reading the
ovector inside the call, not inferred from the after-the-fact state, which
cannot tell "restored" from "never written" (§3.1). (2) The callee **inherits**
the caller's capture environment: a backreference inside a called body sees the
caller's groups (§3.1). (3) The call is **BACKTRACKABLE** on 10.46 — PCRE2 was
atomic here before 10.30 and is not now — measured on a body reachable *only*
by the call, with four atomic controls refusing (§3.2); so the return cannot be
an `RX_CUT` and the callee's choice points must stay live across it. (4) There
is **no compile-time left-recursion refusal in 10.46 at all**: error 140 is
*"invalid escape sequence in (*VERB) name"*, every left-recursive shape
compiles, and the guard is a match-time `rc -52` whose obvious reading is
**refuted** — `^(a|(?1)a)$` performs **199 nested recursions all entered at
offset 0** and matches, so "refuse a recursion at a position an ancestor holds"
is a miscompile rather than a conservative approximation (§3.3). Those four
force the lowering. (3) says the callee's frames survive the return, so **the
call record must survive it too** — and once that is true, the "explicit call
stack of label addresses" the plan row sketches turns out not to need an array
at all: **a call is a resume frame**, in the array pcrec already has, with a
return label in it (§5.1), because a separate array's entries get clobbered by
a second call made after the first returns and that is a real bug, derived and
shown in §5.2. (1) plus the measurement that **`\K` is NOT restored by a
return** (§3.4) says the restore is over a **compile-time capture-slot set**,
never a trail rewind, and the entry values are stored **in the trail itself** by
a trailed self-write at the call site — no new storage anywhere (§5.3). The
**addressable-body** question (charter addition (i)) collapses once written
out: "once-emitted-with-two-linkages" needs a per-*activation* answer at the
exit and the only per-activation channel is the call record, so the honest
three-way choice is SPLICE / HYBRID / CALL, and **PROTOTYPE-measured** they cost
~300 / ~80 / ~80 emitted bytes per call site, with SPLICE **smaller and faster
at one site** (§6). That last number is also the answer to charter addition
(ii): a lookaround body has exactly one use site by construction, so **no
lookaround body should compile as a call**, and the premise of charter addition
(iii) survives — `vm_look`'s disciplined splice **is** the inliner, one callee
contract with two linkages (§6.4). Engine selection is `VM_ONLY` structurally
and the prefilter is the one place this design costs a real number: erasing a
call is **not** a superset, so wave 1 drops the prefilter for call-bearing
patterns as `backrefs` does — and that is **MEASURED at 21×–350×** on the
sparse-candidate shape a prefilter exists for (§8), which is why the sound
construction that gets it back is designed here and scheduled rather than
waved at.

### 0.3 Measurements this lane produced

All under `subroutines_measurements/`, probes committed, outputs archived with
their repo commit by `probes/archive.sh` from a committed tree.

| instrument | kind | what it answers |
|---|---|---|
| `probes/sr_oracle.py` | not a probe, the ORACLE HELPER | borrows `../lookaround_measurements/probes/la_oracle.py` → `br_oracle.py` → `pcre2_ctypes.py` (three levels, no copy) and adds the three things this lane needs: `match_limits()` returning the **RAW** `pcre2_match` rc so a give-up is a CELL and not a traceback; `callout_trace()`, a `pcre2_set_callout` callback reading the **live ovector inside a call**; and `depth_of()`, a depth-limit bisector. Behavioural `SELFCHECK` on all three |
| `probes/probe_premises.sh` | MEASURED + STRUCTURAL, in-pcrec | §1: every spelling's refusal on HEAD under both feature sets, the 26 registry rows and their `built` column, the shared `\g` doorway, the give-up code space and **every site the `ERR_FLOOR` move touches**, `RX_TRAIL`/`RX_SET`/`RX_PUSH`/`RX_CUT` and the fail label quoted from `src/`, the `[M6.5]` resolution machinery, and the label-address/`goto *` census |
| `probes/probe_spellings.py` | MEASURED, both oracles | §2: the ten call spellings and the nine reference spellings separated by **one cell**; the relative and forward forms; `(?R)`/`(?0)`/`\g<0>`; two-digit group numbers; the `(?(DEFINE))` idiom and a DEFINE-less equivalent swept over 11 subjects; python's verdict on the whole vocabulary |
| `probes/probe_captures.py` | MEASURED, libpcre2 + CALLOUTS | §3.1/§3.4: the capture state after return, **during** the call, at depth > 1, after a failed call; inheritance; `\K`; `(?J)` duplicate names and the call/reference resolution split |
| `probes/probe_atomicity.py` | MEASURED | §3.2: the naive cell that decides nothing and the isolated cell that decides it; four atomic controls; quantified calls and the empty-body guard; calls inside lookaround/atomic/lookbehind; the retry COST against an inlined control |
| `probes/probe_leftrec.py` | MEASURED | §3.3: direct, indirect and nullable-prefix left recursion; the two guards; **the decisive sweep that refutes the same-position reading**; `(?R)` under a quantifier; a call inside a lookbehind; depth requirement vs subject; and the error-140 sweep that shows the charter's premise is not about recursion at all |
| `probes/probe_linkage.sh` + `prototype/gen_linkage.py` | PROTOTYPE | §6: three hand-written matchers in the emitter's own idiom, differing only in linkage; a 52-cell agreement control first, then emitted-size by call count and run time on two corpora (mixed, and lexical-only — the corpus HYBRID's whole claim rests on) |
| `probes/probe_prefilter.py` | MEASURED, libpcre2 + in-pcrec | §8: what a DFA prefilter is worth on call-**shaped** patterns, measured on their INLINED equivalents (which pcrec compiles today), each pair verified equivalent **420 cells / 0 disagreements** before any timing |
| `probes/probe_population.py` | MEASURED, PURE TEXT | §10: the census — **6** call spellings in `tests/**/*.rxt`'s 2,161 pattern lines, every one of them a `perr` row testing a refusal, against **226** backreferences |

**`probes/archive.sh` is the ONLY writer of `out/`**, R30 M7's rule inherited
through three lanes, with this lane's module stamp scoped at creation (R32
D1/C14 found the backrefs archiver stamping the wrong module in all eight of
its files).

**NINE INSTRUMENT DEFECTS this lane found by running its own probes**, each of
which produced a confident wrong number or silently measured nothing rather
than erroring:

1. **`probe_atomicity`'s cost axis measured no retry at all.** The body was
   `a|b|c|d|e|f|g|h` and the subject picked the LAST alternative, so every call
   succeeded on its eighth try and **no call was ever re-entered after a
   failing follow**. The numbers came out linear (8n+2) and the "atomic
   control" came out **higher** than the backtrackable one — which, published,
   would have read as *"the atomic linkage is more expensive"*. The
   retry-forcing shape (a body preferring the SHORT alternative, a follow that
   only succeeds when every call took the long one) gives 2ⁿ and a ratio of
   **2.0** against an inlined control.
2. **`probe_leftrec`'s depth bisection reported a limit it never reached.** It
   bisected [1, 400000] for the first FAILING subject size, found none, and
   printed *"largest n = 399999"* — a confident number about a default limit
   the sweep never hit. It now says so, and reports the heap limit, which is
   what actually stops PCRE2 (`rc -63`).
3. **`probe_atomicity` died at row 40 of 80.** `cell()` used the oracle's
   `search()`, which RAISES on any negative rc other than NOMATCH, and
   `^(?R)*$` on `""` is `rc -52`. Every row after it measured nothing. It now
   uses `match_limits()`, where a give-up is a value.
4. **A callout cell fired no callout.** `^(?(DEFINE)((a)(?C1)))(?2)$` calls the
   INNER group, which does not contain the callout. The reachability guard
   named it; the fixed cell calls `(?1)`.
5. **`probe_premises` reported "Permission denied" for every spelling that
   COMPILES.** `-o /dev/null` makes the header `/dev/null.h`. Three cells that
   should have read "compiles" read as an unexplained failure.
6. **`sr_oracle`'s match-limit self-check was vacuous** — the subject was one
   the pattern MATCHES, so the limit never fired and the check would have
   reported that `pcre2_set_match_limit_8` does nothing. Fixed with a
   non-matching subject **and** a control at a huge limit.
7. **`probe_prefilter` could not feed its own subject.** `--emit-main`'s
   generated `main()` takes the subject from `argv[1]`, and Linux's
   `MAX_ARG_STRLEN` caps one argv element at 128 KiB — a 1 MB subject never
   reaches the matcher. Replaced with a file-reading driver.
8. **`probe_prefilter`'s flag check grepped documentation.** `pcrec --help`
   does not list per-optimization `-fno-*` flags at all, so the check reported
   a problem on every run for a flag that works. It now invokes the flag.
9. **`probe_population` would have counted class escapes as calls.** A naive
   `\g<` scan counts `tests/backrefs/octal_class.rxt`'s `^[\g<1>]$` — where the
   class doorway makes those four literal one-byte escapes — as a subroutine
   call. Masked with a character-class pass.

**And one that the compiler caught rather than the probe**: `gen_linkage.py` at
`k = 0` emitted a `goto` to a label it did not define. It is listed because the
`k = 0` row is the prototype's own baseline control, and a baseline that does
not build is a baseline nobody checks.

---

## 1. Premises, re-verified on HEAD rather than inherited

Each was checked against **this worktree's build** and against `src/` at
`eacac76`, not taken from a document. MEASURED/STRUCTURAL,
`out/premises.txt`.

| # | premise | verification |
|---|---|---|
| P1 | Every subroutine spelling refuses today naming module `recursion` | MEASURED, axis A: under `--features all`, `(a)(?1)` → *"module 'recursion' is enabled but `(?1...)` is not implemented yet"*, and likewise `(?2)` `(?9)` `(?+1)` `(?-1)` `(?-2)` `(?-01)` `(?&n)` `(?P>n)` `(?R)` `(?0)`, and `\g<1>` `\g<n>` `\g'1'` `\g'n'` `\g<-1>` `\g<+1>` under the `\g` doorway. Under the default `std1` set the diagnostic is the other one, *"`(?1...)` requires module 'recursion'"* — D65's two sentences, both present |
| P2 | **`(?&name)` refuses naming `named-groups`, not `recursion`, under the default set** | MEASURED, axis A: `(?<n>a)(?&n)` under `std1` answers *"`(?<...)` requires module 'named-groups' (pattern offset 0)"* — the DECLARATION is refused before the call is reached. Not a defect; recorded because a corpus cell that expects the `recursion` sentence must enable `named-groups` too, and §9.3 says so |
| P3 | **The `\g` escape doorway is SHARED between two modules and the TAIL decides** | MEASURED, axis A: `--list-syntax` gives `\g{-1}` → module `backrefs`, `built`; `\g<1>` and `\g'1'` → module `recursion`, `unbuilt`. `(a)\g{1}`, `(a)\g1` and `(a)\1` all COMPILE on HEAD today. So `pcrec_brport_g` already discriminates, and this module extends that one port rather than adding a second |
| P4 | Exactly **26** registry rows carry module `recursion`, all `vm`, all `unbuilt` | MEASURED, axis B. The rows are per-selector at the `(?` doorway: `(?1)`…`(?9)` are **nine separate rows**, `(?-1)`…`(?-9)` **nine more**, and `(?+1)` is **one** — with no `(?+2)`…`(?+9)` sibling. §8.1 owns the asymmetry |
| P5 | **`(?(DEFINE)...)` is module `conditionals`, which has exactly ONE row and no producer** | MEASURED, axis B: `(?(DEFINE)(?<x>a))(?&x)` answers *"module 'conditionals' is enabled but `(?(...)` is not implemented yet"*, and `--list-syntax` shows one `conditionals` row, `(?(1)a|b)`. This module unlocks none of it — §2.5 |
| P6 | The give-up code space is `PCREC_ERR_STEPS (-2)`, `_FRAMES (-3)`, `_WORK (-4)`, `_FLOOR (-4)` | MEASURED, axis C, quoted from `emit_dfa.c:391-394` and from a real artifact. **The `ERR_FLOOR` move −4 → −5 touches EIGHT source-of-truth sites and four archived samples**, all enumerated in §5.6 from this axis's own grep |
| P7 | `RX_SET` is `RX_TRAIL` followed by the write, and **`RX_TRAIL` records the OLD value unconditionally** | STRUCTURAL, `emit_vm.c:5763-5771`, quoted in full. There is no same-value elision, which is what makes §5.3's **trailed self-write** a legal way to park an entry value on the trail |
| P8 | The fail label restores `scan_position` from the popped frame AND rewinds the trail to that frame's mark | STRUCTURAL, `emit_vm.c:6063-6072`. §5.1 adds exactly one line to it and §5.5 is why |
| P9 | **A label address is already a VALUE in emitted code, and there is exactly ONE indirect jump** | STRUCTURAL + MEASURED, axis F: the emitter has two `&&%s_L%d` sites (`emit_vm.c:2029` traced, `:2032` untraced), both inside `RX_PUSH`; one `goto *` (`:6072`); and a real artifact for `(a\|ab)(c\|cd)x` contains 2 label addresses, 1 `goto *`, 16 labels. **`emit_vm.c:14-18` states the one-indirect-jump property as a design decision** and says label addresses are function-local, *"which is fine WITHIN a call — APPROACH §6's A-4/A-5 'a `&&label` does not survive a return' is a STREAMING constraint, not a within-call one."* §5.2 adds the second indirect jump and amends that comment |
| P10 | A group that **nothing references** loses its slots under `--no-captures`; a referenced one keeps them | MEASURED, axis E: `(a)\1` under `--features all --no-captures` mentions `RX_SLOT_GROUP1` **9** times; `(a)b` mentions it **0** times. So a CALL TARGET must join the marked set or the group it calls is deleted out from under it — §4.3 |
| P11 | The `[M6.5]` end-of-parse resolution machinery exists and is reusable: four ports, a `PendingRef` list, `pcrec_bref_resolve`, `pcrec_bref_mark`, `pcrec_has_bref` | STRUCTURAL, axis E, `internal.h:1843-1904`, with `PendingRef`'s own comment quoted. `PendingRef` already carries `number`, `name`, `at` and `what`, which is exactly a call's resolution input — §4.2 |
| P12 | An artifact whose depth grows with the subject already gets a **stamped honest ceiling** rather than a silent cap | MEASURED, axis G: `((a\|ab)*)+z` stamps `RX_RESUME_FRAMES 2048`, `RX_TRAIL_FRAMES 3072`, `RX_VM_PRUNE_CEILING "subject-end"`. `Cost.unbounded`/`.growable` (`emit_vm.c:1331-1348`) is the analysis, and a recursive call is `unbounded` by the same definition — §5.6 consumes this rather than inventing a capacity story |
| P13 | `pcrec_maxw` **does not exist** and `pcrec_minw` does | STRUCTURAL, `internal.h:2381`; a tree-wide grep finds no `maxw`. `lookaround_design.md` §11 wave A builds it. §3.4's lookbehind rule and §11's wave ordering both depend on **whose** wave A that is, and §11 says so |
| P14 | python 3.14 `re` has **no subroutine call of any spelling** | MEASURED, `out/spellings.txt` A7: all nine call spellings are `PatternError`, including `(?-1)` which python reads as an inline-flag group (*"missing flag"*) and `\g<1>` which is a replacement-template escape, not a pattern one (*"bad escape \g"*). §10 is what that does to the D27 author |

**One charter premise did not survive, and it is the load-bearing one.** The
`[DD-14]` row says left recursion is *"refused at compile time (PCRE2's
could-loop-indefinitely check equivalent)"* and names *"err 140"*. MEASURED
(`out/leftrec.txt` L1–L3, L10): **PCRE2 10.46 refuses no left-recursive shape
at compile time**, and `pcre2_get_error_message(140)` is *"invalid escape
sequence in (\*VERB) name"* — a different construct entirely. §3.3 is what the
answer actually is, and §5.6 is the machinery it picks.

---

## 2. The construct table (charter — CONSTRUCTS)

### 2.1 The one cell that separates a call from a reference

`(a|b)\1` and `(a|b)(?1)` both compile, both look like "group 1 again", and
they are different constructs. The discriminator is one cell:

| pattern | on `"ab"` | verdict |
|---|---|---|
| `(a\|b)\1` | **nomatch** | a REFERENCE — it wants the same TEXT |
| `(a\|b)(?1)` | **(0,2)** | a CALL — it re-RUNS the alternation |

MEASURED, `out/spellings.txt` A1/A2. Every row of §2.2 carries it, and the
same table against `"aa"` — where both a call and a reference match — is
printed beside it precisely because a compile-status column would have told a
reader nothing.

### 2.2 Every spelling, and whether pcrec ships it

MEASURED on libpcre2 10.46 and python 3.14 `re`, `out/spellings.txt` A1/A2/A7.

| spelling | 10.46 | python | kind | pcrec | registry row today |
|---|---|---|---|---|---|
| `(?1)` … `(?9)` | call | ERR | call | **SHIPS** | nine rows, `unbuilt` |
| `(?10)`, `(?12)` … | call | ERR | call | **SHIPS** | **no row** (§8.1) |
| `(?-1)` … `(?-9)`, `(?-01)` | call, relative left | ERR *(read as a flag group)* | call | **SHIPS** | nine rows + the leading-zero row |
| `(?-10)` and beyond | call | ERR | call | **SHIPS** | **no row** (§8.1) |
| `(?+1)` | call, relative right | ERR | call | **SHIPS** | one row |
| `(?+2)` … `(?+9)` | call | ERR | call | **SHIPS** | **no row** (§8.1) |
| `(?&name)` | call | ERR | call | **SHIPS** | one row |
| `(?P>name)` | call | ERR | call | **SHIPS** | one row |
| `\g<1>`, `\g<name>`, `\g<-1>`, `\g<+1>` | call | ERR *(bad escape)* | call | **SHIPS** | one row (`\g<1>`) |
| `\g'1'`, `\g'name'`, `\g'-1'` | call | ERR | call | **SHIPS** | one row (`\g'1'`) |
| `(?R)`, `(?0)` | whole-pattern call | ERR | call | **SHIPS** | two rows |
| **`\g<0>`, `\g'0'`** | **whole-pattern call** | ERR | call | **SHIPS** | **no row** (§2.4, §8.1) |
| `\1`, `\g1`, `\g{1}`, `\g{-1}` | reference | `\1` only | reference | already ships | module `backrefs` |
| `\k<n>`, `\k'n'`, `\k{n}`, `(?P=n)`, `\g{n}` | reference | `(?P=n)` only | reference | already ships | module `backrefs` |
| `(?(DEFINE)…)` | a never-executed container | ERR | **conditional** | **REFUSES** — module `conditionals` | one row, `unbuilt` |

**TEN CALL SPELLINGS SHIP AND NOTHING IN THIS MODULE REFUSES A CONSTRUCT
PCRE2 HAS**, which is unusual for a pcrec module and is worth saying plainly:
there is no `recursion` analogue of lookaround's variable-length lookbehind.
The refusals this module leaves standing are `conditionals`' (`(?(DEFINE)`,
`(?(R)`, `(?(1)`) and they are that module's, not this one's — §13.

### 2.3 The relative and forward forms, and what they resolve to

MEASURED, `out/spellings.txt` A3, with subjects chosen so the WRONG target
gives a different answer rather than merely a different capture:

| pattern | subject | 10.46 | what it proves |
|---|---|---|---|
| `^(a)(b)(?-1)$` | `"abb"` | (0,3) | `(?-1)` is the NEAREST group to the left — group **2** |
| `^(a)(b)(?-2)$` | `"aba"` | (0,3) | `(?-2)` is group **1** |
| `^(?+1)(a)$` | `"aa"` | (0,2), g1=(1,2) | `(?+1)` is a **forward** call — group 1's pattern runs BEFORE group 1 does |
| `^(?+2)(a)(b)$` | `"bab"` | (0,3) | `(?+2)` counts forward past one group |
| `^(a)(?-01)$` | `"aa"` | (0,2) | a leading zero is accepted |
| `^\g<+1>(a)$` | `"aa"` | (0,2) | `\g<±N>` obeys the same relative rule |

**THE FORWARD CALL IS THE SHAPE THAT MAKES A CALL UNLIKE A REFERENCE**, and
it is one cell: `^(?+1)(a|b)$` on `"ab"` matches, while the forward
*reference* `^\2(a|b)(c)$` on `"abc"` does not — a forward reference can only
ever read an unset group, a forward call runs the group's pattern. The
resolution pass therefore cannot be a left-to-right one-pass thing; it is the
end-of-parse pass P11 already has.

Relative resolution is **at the call site's own group count**, so it is
computed in the port and stored as an absolute number, exactly as
`PendingRef.number` already stores `\g{-1}`'s computed value.

### 2.4 `(?R)`, `(?0)`, `\g<0>` — and "the whole pattern" INCLUDES the anchors

MEASURED, `out/spellings.txt` A4/A7a. One cell settles what "the whole
pattern" means:

| pattern | `"aabb"` | |
|---|---|---|
| `^(a(?1)?b)$` | **(0,4)** | `(?1)` calls GROUP 1 — the anchors are outside it |
| `^(a(?R)?b)$` | **nomatch** | `(?R)` re-runs `^(a(?R)?b)$`, **`^` and `$` included**, so the inner `^` fails at offset 1 |
| `^(a(?0)?b)$` | **nomatch** | `(?0)` is `(?R)` |
| `^(a\g<0>?b)$` | **nomatch** | and so is `\g<0>` |
| `(a(?R)?b)` unanchored | (0,4) | with the anchors gone, `(?R)` reaches depth 2 |

**`\g<0>` AND `\g'0'` ARE TWO SPELLINGS THE CHARTER'S LIST DOES NOT HAVE**,
they compile on 10.46, and they behave as `(?R)` on all four cells above. They
have **no registry row** today (§8.1) and they arrive through the `\g` port,
where the number `0` must mean "the root" rather than "group 0 does not exist".
`PendingRef.number`'s own comment already anticipates a zero — *"it may be ZERO
OR NEGATIVE: `\g{-1}` at a count of zero computes 0, and whether a number names
a group is the ONE question this list defers"* — so this is a rule in the
resolver, not a new field.

**THE CALL TARGET FOR THE ZERO FAMILY IS THE AST ROOT**, not a group body.
That is a structural consequence of the measurement and it is the reason §4.1's
node stores a *target group number* with `0` reserved, rather than a pointer to
an `A_CAP`.

### 2.5 The `(?(DEFINE)…)` idiom is `conditionals`', and what a DEFINE-less
### design costs

MEASURED, `out/spellings.txt` A5/A7b and `out/premises.txt` axis A/B.

`(?(DEFINE)(?<w>X))` is a **conditional group whose condition is never true**,
so its body never runs lexically and exists only to be called. It is module
`conditionals`' construct at pcrec's `(?(` doorway (P5) and **this module does
not unlock it**. A user who wants the library-pattern idiom therefore cannot
write it — so the honest question is what that costs, and it is measurable.

Three DEFINE-less spellings of the same intent, against the DEFINE form over
11 subjects (`out/spellings.txt` A7b):

| spelling | agrees with DEFINE | why |
|---|---|---|
| `^(?!)(?<w>X)\|^BODY$` | **11 / 11** | the `(?!)` kills the declaring branch, the name is still declared, the call still resolves — **an exact substitute** |
| `^(?:(?<w>X))?BODY$` | **9 / 11** | the optional group RUNS, so it eats input and leaves a capture: on `"foo-bar"` the DEFINE form gives g1 **unset** and this gives g1 **(0,2)** |
| `^(?<w>X)?+BODY$` | **fails outright** | the possessive optional consumes and will not give back |

**RULED: no DEFINE, and the cost is one line of documentation.** The
`(?!)`-guarded-branch spelling is an exact substitute on every measured cell,
it needs only `lookaround` (which lands first) and `named-groups`, and it is
what this module's own corpus uses wherever a call-only body is wanted (§10.2).
`conditionals` remains chartered; when it lands, `(?(DEFINE)` becomes a second
spelling of a thing that already works, which is the right order.

**THE ONE THING THAT IS LOST** is discoverability: `(?(DEFINE)…)` is what
users' existing patterns are written with, so a pattern copied from a library
will refuse. That is a `conditionals` refusal with a correct module name, which
is D26's tier-2 obligation discharged, and §14 ASK 4 asks whether Frank wants
the diagnostic to point at the substitute.

### 2.6 Quantified calls, and the empty-body guard

MEASURED, `out/atomicity.txt` T5:

| pattern | subject | 10.46 |
|---|---|---|
| `(?&g){2}`, `(?&g)+`, `(?&g)*` | as written | ordinary bounded/unbounded repeats of a call |
| `(?(DEFINE)(?<g>a?))(?&g)*` | `"aaa"` | (0,3) — a NULLABLE callee under `*` terminates |
| `(?(DEFINE)(?<g>))(?&g)*` | `""` | (0,0) — an EMPTY callee under `*` terminates |
| `^(a?)(?1)*$` | `"aaa"` | (0,3) |
| `^(?R)*$` | `""` | **`rc -52`** |

So a call is a repeatable item and the existing **empty-iteration guard** is
what stops a nullable callee's loop — `vm_nullable` needs an `A_CALL` arm and
its answer is *"nullable iff the callee's body is nullable"*, which for a
recursive callee is a fixpoint over the call graph and for a call to group 0
is *"is the whole pattern nullable"*. §4.4 owns it and S-SR9 defends it.

Note the registry's own `quant` column already claims this: `(?R)`, `(?0)`,
`(?+1)` and every `(?-N)` row read `quant=yes` while the `(?1)`…`(?9)` rows read
`quant=no` (`out/premises.txt` axis B). **That asymmetry is wrong** and §8.1
owns it: `(a)(?1)*` is as legal as `(a)(?-1)*`.

---

## 3. The semantics, measured on libpcre2 10.46

### 3.1 Captures: the callee WRITES and the RETURN restores (charter (i))

**The charter's three questions are all about the state AFTER the fact, and
after-the-fact measurement cannot answer them.** Two hypotheses produce the
same table and completely different emitted code:

- **H-NEVER** — a call runs the group's pattern with capturing switched off.
- **H-RESTORE** — the callee's writes happen and the return puts the entry
  values back.

Both answer *"g1 is the caller's value"* to every cell a `pcre2_match` return
can produce. So this lane built a third instrument: `sr_oracle.callout_trace`,
a `pcre2_set_callout` callback that reads the **live ovector** at a `(?C1)`
placed **inside the called body**.

**MEASURED, `out/captures.txt` C2 — H-RESTORE, and it is not an inference:**

```
^((a)(?C1))(?1)$   on "aa"  ->  (0,2)  g1=(0,1) g2=(0,1)
    C1 at pos 1  capture_top=3  caps=[None, (0,1)]     <- the LEXICAL run
    C1 at pos 2  capture_top=3  caps=[(0,1), (1,2)]     <- INSIDE the call
```

At the second firing **g2 is (1,2)** — the callee wrote it — and the final
answer is **g2 = (0,1)**. The write happened and the return undid it. A
design built on H-NEVER would have emitted no restore and no save.

**AND THE CALLEE INHERITS THE CALLER'S ENVIRONMENT.** MEASURED, C5, one cell:

| pattern | subject | 10.46 | |
|---|---|---|---|
| `^(a)(b\1)(?2)$` | `"ababa"` | **(0,5)** g1=(0,1) g2=(1,3) | group 2's body is `b\1`; the call re-ran it and **`\1` was still `"a"`** |
| `^(a)(b\1)(?2)$` | `"abab"` | nomatch | the control: an unset-and-empty `\1` would have matched this |

and the same under `PCRE2_MATCH_UNSET_BACKREF`, where an unset reference
matches empty, so the two designs would differ by LENGTH rather than by
match/no-match — still nomatch. **A call is not a fresh capture environment.**

**PER LEVEL, AND THE OUTERMOST LEVEL'S VALUES ARE THE ANSWER.** MEASURED, C3:

```
^((a)(?1)?(b)(?C1))$   on "aabb"  ->  (0,4)  g1=(0,4) g2=(0,1) g3=(3,4)
    C1 at pos 3  caps=[None, (1,2), (2,3)]    <- the INNER level's own values
    C1 at pos 4  caps=[None, (0,1), (3,4)]    <- restored, then the outer's own
```

and `^((a|b)(?1)?\2)$` matches `"abba"` and not `"abab"` — each level's `\2`
refers to **that level's** capture — with the callout showing g2 = (0,1),
(1,2), (2,3), (3,4) at successive levels (C5).

**AFTER A FAILED CALL, NOTHING SURVIVES.** MEASURED, C4:
`^(?:((a)(?C1))(?1)x|(?1)y)$` on `"ay"` is (0,2) with **g1 and g2 both unset**,
while the callout shows the body having written g2=(0,1) twice. The first
branch's call ran and died; the second branch's call ran and succeeded; neither
left a trace.

**THE ONE-SENTENCE RULE: a subroutine call is CAPTURE-TRANSPARENT — the
capture state after the call is exactly the state before it, whatever the call
did.** §5.3 is the machinery, and it is two trailed writes per capture slot in
the callee's static write set.

### 3.2 Atomicity: BACKTRACKABLE on 10.46 (charter (ii))

The charter is right that this changed: PCRE2 was atomic here before 10.30.
The measurement has to isolate the CALL, and **the obvious cell does not**.
`^(a|ab)(?1)c$` on `"ababc"` matches under both hypotheses, because the
LEXICAL group can retry too. `out/atomicity.txt` T1 carries it labelled as
deciding nothing, so a reader does not mistake it for the evidence.

**THE ISOLATED CELL** puts the body where only the call can reach it:

| pattern | subject | 10.46 | |
|---|---|---|---|
| `^(?(DEFINE)(?<g>a\|ab))(?&g)c$` | `"abc"` | **(0,3)** | **BACKTRACKABLE.** Atomic would be nomatch |
| `^(?!)(?<g>a\|ab)\|^(?&g)c$` | `"abc"` | (0,3) | the same without DEFINE, in case DEFINE is special |
| `^(?(DEFINE)(?<g>a+))(?&g)ab$` | `"aaab"` | (0,4) | a QUANTIFIER, not an alternation, as the callee's choice point |
| `^(?(DEFINE)(?<g>a{1,3}))(?&g)aa$` | `"aaa"` | (0,3) | and a bounded repeat |

**FOUR ATOMIC CONTROLS, all nomatch** (T4), which is what makes the four rows
above evidence rather than a coincidence: an atomic callee body
`(?>a|ab)`; an atomic wrapper on the call site `(?>(?&g))`; a possessive
quantifier on the call `(?&g)++`; and an atomic wrapper around a giving-back
callee.

**AND IT RETRIES ACROSS A RETURN, AT DEPTH** (T3):
`^(?(DEFINE)(?<g>a(?&g)?b|x|xy))(?&g)$` matches `"axyb"` — the retreat has to
re-enter the INNER call after the outer one returned.

**THE COST, against an inlined control** (T7, after the vacuous first version
described in §0.3). A body preferring the short alternative and a follow that
succeeds only when every call took the long one, so the answer is the LAST
combination the search reaches:

| n calls | via calls | body INLINED n times | ratio |
|---|---|---|---|
| 1 | 4 | 3 | 1.33 |
| 2 | 8 | 5 | 1.60 |
| 4 | 32 | 17 | 1.88 |
| 8 | **512** | **257** | **1.99** |

(the numbers are the smallest `match_limit` that still reaches the answer —
**PCRE2's own backtrack counter**, not pcrec's). The series is 2ⁿ⁺¹ against
2ⁿ+1: **a call costs its body's backtracks plus one, and the ratio tends to
2**. That extra one per call is the return, and §5.1's shape is where pcrec
pays the same.

**WHAT THIS RULES OUT.** `RX_CUT` at the return label — the shape the plan row
offers as the alternative — is wrong for 10.46. The return must leave the
callee's frames **live**, which is exactly why §5.1 cannot pop a call record
at return and §5.2 is a derivation rather than a preference.

### 3.3 Left recursion: there is no compile-time check, and the obvious
### runtime one is a MISCOMPILE (charter (iii))

**PCRE2 10.46 REFUSES NO LEFT-RECURSIVE SHAPE AT COMPILE TIME.** MEASURED,
`out/leftrec.txt` L1/L2/L3/L10. Every one of `((?1)a)`, `(a|(?1)a)`,
`((?1)?a)`, `((?1)*a)`, `(?R)a`, `(a?(?1)b)`, `((?:)(?1)b)`, `(\b(?1)b)`,
`(x*(?1)b)`, `((?:q|)(?1)b)`, `((){0}(?1)b)`, the two-node DEFINE cycle, and
the twelve historical err-140 candidates **compiles**. And
`pcre2_get_error_message(140)` is *"invalid escape sequence in (\*VERB) name"* —
the charter's error number belongs to a different construct.

The guard is **entirely at match time**: `rc -52`, *"nested recursion at the
same subject position"*.

**AND THE OBVIOUS READING OF THAT MESSAGE IS REFUTED.** MEASURED, L5b, the
sweep this section rests on. `^(a|(?C1)(?1)a)$` with the callout immediately
before the recursive call:

| subject | nested calls | entry offsets seen | result |
|---|---|---|---|
| `"a"×10` | 9 | `[0]` | (0,10) |
| `"a"×100` | 99 | `[0]` | (0,100) |
| **`"a"×200`** | **199** | **`[0]`** | **(0,200)** |
| `"a"×10 + "b"` | 12 | `[0]` | **rc −52** |
| `"a"×40 + "b"` | 42 | `[0]` | **rc −52** |

**199 nested recursions, every one entered at offset 0, and it matches.** A
pcrec that implemented *"refuse a recursion at a position an ancestor already
occupies"* — the reading a designer takes from −52's own wording, and the O(1)
per-callee entry-position slot that implements it cheaply — would answer
**nomatch where PCRE2 answers (0,200)**. That is a miscompile, not a
conservative approximation, and finding it is the reason this section exists.

Nor is −52 a fixed nesting cap: on the non-matching subjects the give-up depth
is **n + 2**, tracking the subject.

**THIS LANE DID NOT PIN 10.46's EXACT PREDICATE BY BLACK-BOX PROBING, AND SAYS
SO RATHER THAN GUESSING ONE.** What is pinned is enough to rule:

**RULED (§5.6): pcrec builds NO same-position guard and NO compile-time
left-recursion refusal. The DEPTH CAPACITY is the only guard, it is stamped in
the artifact, and it returns a new typed give-up code.** Every shape PCRE2
answers −52 on is non-terminating, so it exhausts pcrec's depth and gives up
loudly and boundedly; every shape PCRE2 matches, pcrec matches, up to the
stamped depth. The residual is the band between pcrec's stamped depth and
PCRE2's heap: §5.6 sizes it and §12 P-3 is the refutation.

**WHAT STOPS PCRE2 IS MEMORY, NOT A COUNTER.** MEASURED, L9:
`^(a(?1)?b)$` on `aⁿbⁿ` needs depth `2n+3` and **still matches at n = 400,000
(an 800 KB subject) at the defaults**; the sweep reports that it never reached
the default depth limit rather than inventing a number for it (§0.3 defect 2).
Under an explicit `heap_limit` it answers `rc −63` *"heap limit exceeded"*.
pcrec's is a **fixed emitted array** (P12), which is the honest structural
difference and the one a stamped ceiling exists to communicate.

### 3.4 The interactions (charter (iv))

#### (a) Backreferences to groups set inside a call

Covered by §3.1: the callee inherits, writes per level, and the return
restores. The consequence for `A_BREF` is that **nothing changes** — a
reference reads `slot_values` and the slots are correct at every instant. The
one new obligation is §4.3's: a group a CALL names must be in the marked set,
or `--no-captures` deletes it (P10).

#### (b) `\K` is NOT restored by a return, and that is what shapes §5.3

MEASURED, `out/captures.txt` C7:

| pattern | subject | 10.46 |
|---|---|---|
| `^(a\Kb)(?1)$` | `"abab"` | **(3,4)** |
| `^(?(DEFINE)(?<g>a\Kb))(?&g)$` | `"ab"` | **(1,2)** |
| `^(a(?1)?\Kb)$` | `"aabb"` | **(3,4)** |

A `\K` inside a called body **moves the reported match start**, and the
last one executed on the successful path wins — the outer level's, after the
inner level's has already fired. So `\K` is a **path fact**, not capture state,
and it survives the return.

**AND pcrec SPELLS `\K` AS A WRITE TO `RX_SLOT_WHOLE_START`** — STRUCTURAL,
measured on an artifact for `(a\Kb)+c`, where the `\K` sites are
`RX_SET(RX_SLOT_WHOLE_START, scan_position)`, the **same slot** as group 0's
start. So a return that restored "every slot the callee wrote" — the tempting
one-line implementation, a trail rewind to the call's mark — would **undo the
`\K`** and answer (0,4) where PCRE2 answers (3,4). §5.3's restore is over a
**capture-slot set that excludes slots 0 and 1 by construction**, and S-SR6 is
its detector. This is the second design the measurements killed.

#### (c) `(?J)` duplicate names: a CALL and a REFERENCE resolve DIFFERENTLY

MEASURED, `out/captures.txt` C8. The rows that separate them make the FIRST
declaration UNSET, which the naive rows cannot:

| pattern (all under `PCRE2_DUPNAMES`) | `"qyx"` | `"qyy"` |
|---|---|---|
| `^(?:(?<a>x)\|q)(?<a>y)(?&a)$` — a **CALL** | **(0,3)** | nomatch |
| `^(?:(?<a>x)\|q)(?<a>y)\k<a>$` — a **REFERENCE** | nomatch | **(0,3)** |

**A call by name to a duplicated name runs the FIRST DECLARATION's pattern,
statically, whether or not that group is set. A backreference by name reads the
first SET member of the run, dynamically.** They are two different resolutions
of one name.

And a call **does not retry into the later members**:
`^(?<a>x)(q)(?<a>y)(?&a)z$` matches `"xqyxz"` and not `"xqyyz"`.

**THE DESIGN CONSEQUENCE is that `A_CALL` DOES NOT REUSE `A_BREF`'s `refs[]`
SET.** `A_BREF` carries a set *"even when it has one element, deliberately"*
(`internal.h:385-400`) because a by-name reference resolves at MATCH time over
a run. A call resolves at PARSE time to **one number**. §4.2 puts the two rules
in the one resolver rather than building a second pending list — one mechanism,
two rules, which is the shape `PendingRef`'s own comment argues for.

#### (d) A call inside a lookbehind needs a WIDTH, and a recursive one has none

MEASURED, `out/leftrec.txt` L7:

| pattern | 10.46 |
|---|---|
| `^(?(DEFINE)(?<g>ab))ab(?<=(?&g))$` | (0,2) — fixed width 2, `MAXLOOKBEHIND=2` |
| `^(?(DEFINE)(?<g>a\|ab))ab(?<=(?&g))$` | (0,2) — widths 1 and 2, the variable-length lookbehind 10.43+ allows |
| `^(?(DEFINE)(?<g>a+))aa(?<=(?&g))$` | **ERR 125** *"length of lookbehind assertion is not limited"* |
| `^(?(DEFINE)(?<g>a{1,300}))aaaa(?<=(?&g))$` | **ERR 200** *"branch too long in variable-length lookbehind"* |
| `^(?(DEFINE)(?<g>a(?&g)?b))aabb(?<=(?&g))$` | **ERR 125** — a RECURSIVE callee has no bounded width |

So PCRE2 computes the callee's width **through the call**. pcrec's shipped
lookbehind subset is **fixed-per-branch** (`lookaround_design.md` §2.5), which
is stricter, and the rule composes without new machinery: the width analysis
descends into `A_CALL` by descending into the callee, and **refuses on a
recursive callee** because the fixpoint does not converge to a constant.
`pcrec_maxw` is `[M6.6.2]` wave A's (P13) and gains one `A_CALL` arm here.

#### (e) A call inside a lookahead or an atomic group is ordinary

MEASURED, L8: `(?=(?&g))`, `(?!(?&g))` and `(?>(?&g))` all behave as the
construct they are wrapped in, including the atomic wrapper suppressing the
call's retries (T4). Nothing in this module is special-cased for them, and
§6.4's callee contract is why: the callee's own follow scoping is the same rule
`lookaround_design.md` §3.2.1 states, for the same reason one construct over.

#### (f) `(?R)` under a quantifier, and the anchors again

MEASURED, L6: `^(?R)*$`, `^(?R)?$`, `^(?R){0,2}$` all give `rc −52`;
`^a(?R)*b$` on `"ab"` matches; `(a(?R)*b)` on `"aabb"` matches. There is no
special rule — `(?R)` is a repeatable item like any call, and its interaction
with `^`/`$` is §2.4's, not the quantifier's.

---

## 4. The parse side: one node kind, one resolver, two rules

### 4.1 `A_CALL`, and its D70 payload

```c
A_CALL,      /* a subroutine call: run another group's pattern here, and put
                the capture state back on the way out */
```

with, under D70's tagged union (`n->u.call.*` — D70 RULED that no module may
add a top-level per-kind field after the union lands, and this module lands
after it):

```c
    struct {
        int   target;      /* the group number to run. 0 = THE ROOT: (?R),
                              (?0), \g<0>, \g'0' -- §2.4 measured that the
                              root INCLUDES the anchors, so this is not a
                              pointer to an A_CAP */
        const Ast *body;   /* the resolved callee subtree, filled by the
                              end-of-parse pass (§4.2). SHARED, never owned */
        CallLink link;     /* SPLICE or LINKAGE -- §6.2, decided by
                              src/opt/callgraph.c, never by the parser */
        int   nsave;       /* |W|, the callee's transitive capture write set */
        const int *save;   /* W: the SLOT indices to save and restore, ascending
                              -- §5.3. Arena-allocated. EXCLUDES slots 0 and 1
                              BY CONSTRUCTION (§3.4(b) measured why) */
    } call;
```

Four decisions, each with its reason.

**(a) ONE KIND FOR ALL TEN SPELLINGS.** The spelling is not a semantic
difference — §2.1's discriminator is the same for all ten, §2.3's relative
forms compute to an absolute number in the port, and §2.4's zero family is
`target == 0`. `Ast.reg` already carries the `RegRow` for the diagnostics and
for D65, so the spelling is recoverable without a field.

**(b) `target` IS AN INT, NOT A SET.** §3.4(c) MEASURED that a call by name to
a duplicated name runs the **first declaration**, statically, and does not
retry into the run. `A_BREF.refs[]` is a set because a *reference* resolves at
match time; a call does not. Reusing `refs[]` here would make one field mean
two things and would invite an emitter to write the else-if chain
`backrefs_design.md` §8.3 designed for the other construct.

**(c) `body` IS RESOLVED ONCE AND STORED.** Same rule as `A_BREF.refs` and
`Ast.multiline` (D62): resolved at the position that knows, never re-derived.
The emitter, `vm_nullable`, `pcrec_maxw` and the call-graph pass all need it,
and four independent derivations of "which subtree does this call run" is four
chances to disagree.

**(d) `save`/`nsave` ARE COMPUTED BY A PASS, NOT BY THE PARSER.** They are a
fixpoint over the call graph (§5.3) and the parser does not have the graph.
D62's principle is about *parse-resolved modifier state*; this is derived
analysis, so it belongs where `possessify`'s and `mrl`'s results belong.

**D62 CONTROL 3'S OBLIGATION COMES WITH THE PAYLOAD.** An analysis that
pattern-matches `case A_CALL:` and does not read `.body` treats a call as an
opaque zero-width atom — which is *sound* for a decline and *wrong* for a
descent. §9.3 makes that three sabotage rows rather than a comment.

### 4.2 One resolver, two rules — extending `pcrec_bref_resolve`, not copying it

P11: the `[M6.5]` machinery is four ports leaving `PendingRef` records and one
end-of-parse pass resolving them. A call's resolution input is **exactly**
`PendingRef`'s existing fields — `number` (absolute, with relatives already
computed and zero meaningful), `name`, `at`, `what`.

So `PendingRef` gains **one field**, not a second list:

```c
    PendKind kind;   /* PEND_BREF or PEND_CALL: which RULE the resolver
                        applies. The LIST is one list, walked once, because
                        the pass's whole justification is that it is the ONE
                        site that knows both the final group count and every
                        declaration of a duplicated name -- and that is as
                        true of a call as of a reference. */
```

and the pass grows the two rules §3.4(c) measured:

| kind | number | name | zero |
|---|---|---|---|
| `PEND_BREF` | the set of groups with that number (one) | the **run** of groups with that name, ascending — resolved at match time to the first SET member | error 115-class |
| `PEND_CALL` | that group, one number | the **FIRST DECLARATION** with that name, statically | **the ROOT** (§2.4) |

The diagnostic for a call to a group that does not exist is the same
error-115-class one the pass already raises, at the same recorded offset —
MEASURED that PCRE2 agrees on the *number*: `(a)(?2)`, `(a)(?9)`, `(a)(?-2)`,
`(a)(?+2)`, `(?<n>a)(?&m)`, `(a)\g<2>`, `(a)\g<m>` are all **error 115**
*"reference to non-existent subpattern"* (`out/spellings.txt` A6), and
`(a)(?+0)`/`(a)(?-0)` are **error 126** *"a relative value of zero is not
allowed"* — a distinct check the port owns, because zero is legal as an
**absolute** target and illegal as a **relative** one.

**THE PORTS.** Four, mirroring the backref side, all in
`src/parse/mod_recursion.c`:

| port | rows it serves |
|---|---|
| `pcrec_rcport_num` | `(?1)`…`(?9)` and their multi-digit continuations, `(?0)` |
| `pcrec_rcport_rel` | `(?+N)`, `(?-N)`, with the leading-zero and relative-zero rules |
| `pcrec_rcport_name` | `(?&name)`, `(?P>name)` |
| `pcrec_rcport_g` | **NOT A NEW PORT** — P3 measured that `\g` is one doorway shared with `backrefs`, and `pcrec_brport_g` already discriminates the tail. It gains the `<`/`'` arms and produces a `PEND_CALL` |

The last row is the one worth arguing: `\g<1>` and `\g{1}` differ by **one
character**, they arrive at the same escape selector, and splitting them across
two translation units would put the tail-discrimination rule in a place where
neither module owns all of it. `PendingRef`'s own comment records that
splitting a check between the port and the resolver *"was a real defect, not a
hypothetical"*. One port, two `PendKind`s.

### 4.3 A CALL TARGET MUST JOIN THE MARKED SET

P10 MEASURED: `--no-captures` deletes the `A_CAP` wrapper of every group
nothing references, and a referenced group keeps its slots (9 mentions vs 0).
**A call names a group exactly as a reference does**, so
`pcrec_bref_mark`'s union must include every `A_CALL.target` — otherwise
`(a)(?1)` under `--no-captures` deletes group 1 and the call has no body.

Two properties, and the second is the one a panel should check:

1. **`target == 0` marks nothing** — the root is not an `A_CAP` and is never
   deleted.
2. **The mark is TRANSITIVE.** A call to group 1 keeps group 1; if group 1's
   body calls group 3, group 3 must be kept too. The fixpoint is the same one
   §5.3's write set needs, so it is computed **once**, in
   `src/opt/callgraph.c`, and both consumers read it.

`pcrec_has_bref`'s sibling `pcrec_has_call` is placed beside it in
`src/opt/atomic.c`, where the tree predicates live (`lookaround_design.md`
§11 wave A2 puts `pcrec_has_lookaround` there for the same reason).

### 4.4 The walker arms, budgeted by file

Adding `A_CALL` makes every exhaustive `AKind` switch a `-Wswitch` error under
`make strict`. STRUCTURAL, from the same census `lookaround_design.md` §11
wave A2 took (the file list is stable; the per-file arm counts are re-derived
at implementation, not guessed here):

| file | what the `A_CALL` arm must decide |
|---|---|
| `src/opt/atomic.c` | `pcrec_has_call` is PLACED here; `pcrec_has_atomic` and `pcrec_has_bref` must **descend into `.body`** — a call to a group containing an atomic group carries that atomic group's consequences |
| `src/opt/revdet.c` | **DECLINE.** The reverse walk has no notion of a call and `vm_rev_emit`'s `default:` is a hard `ctx_fail` — the arm must stop the tree from reaching it |
| `src/opt/possessify.c` | must not possessify ACROSS a call boundary, and must treat a call's follow set as the callee's FIRST set — `pcrec_revdet_first` has a `default:` that widens to all bytes, which is sound; possessify's own arm is not automatic |
| `src/gen/emit_vm.c` | `vm_emit` (§5), `vm_nullable` (§2.6: nullable iff the callee is, a fixpoint), `vm_cost` (§5.7), `vm_cuts`'s walk, the `--emit-ir` listing |
| `src/opt/altcls.c` | decline |
| `src/opt/mrl.c` | **NOT 0.** A call consumes what its callee consumes, so `pcrec_minw(A_CALL)` is the callee's `minw` — and for a recursive callee the fixpoint's least solution, which is the minimum over the non-recursive branches. `pcrec_maxw` is the callee's `maxw`, `PCREC_W_UNBOUNDED` when recursive (§3.4(d)) |
| `src/opt/select_engine.c` | forces `VM_ONLY` and, in wave 1, forces the prefilter OFF (§8) |
| `src/ir/nfa.c` | wave 1: the pattern never reaches the NFA (VM_ONLY, no prefilter). Wave 3 builds the sound approximation (§8.3) |
| `src/parse/parse.c` | `pcrec_is_bare_anchor` — §2.6 measured that every call spelling is quantifiable, so a bare call as a group's whole body must be wrapped so it can be quantified |
| `src/parse/mod_backrefs.c` | descend into `.body` |

**AND THE `default:`-CARRYING SWITCHES `-Wswitch` WILL NOT NAME.**
`lookaround_design.md` §11 names four (`revdet.c:370`, `emit_vm.c:1132`,
`:1176`, `:3132`) and re-inspects them by hand. **This module inherits that
obligation with a different verdict on one of them**: `vm_rev_emit`'s
`default:` is *"internal error: bad AST node in the backward walk"* — a hard
compile error, loud, and reachable if a call ever reaches the backward walk.
That is why `revdet.c`'s arm must DECLINE rather than descend, and S-SR12 is
its detector.

---

## 5. The VM lowering — the call linkage

### 5.1 A CALL IS A FRAME

The plan row sketches *"an explicit call stack of computed-goto LABEL
ADDRESSES inside the single emitted VM function — push the return label, goto
the subpattern's entry, pop-and-goto\* on subpattern success"*. **The label
addresses and the `goto *` survive that sketch. The separate stack does
not**, and §5.2 is the derivation.

The shape:

```
    L_site:   RX_SET(SLOT_SAVE_w0, slot_values[SLOT_SAVE_w0])   // §5.3: |W| trailed
              ...                                                //  SELF-writes
              RX_CALL(&&L_ret, scan_position)      // a resume frame with a return label
              goto L_entry_g
    L_entry_g:  <the callee's body>                -> L_exit_g
    L_exit_g: RX_RETURN                            // restore W, then goto* the frame's ret
    L_ret:    <the continuation>
```

and `RX_CALL` / `RX_RETURN` are `RX_PUSH` with one more field and one more
line:

```c
#define RX_CALL(ret_, p_) do {                                          \
        if (run->resume_depth >= RX_RESUME_FRAMES) return RX_R_FRAMES;  \
        if (run->call_depth  >= RX_CALL_DEPTH)     return RX_R_RECURSE; \
        run->resume_stack[run->resume_depth].resume_label = &&rx_fail;  \
        run->resume_stack[run->resume_depth].resume_position = (p_);    \
        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth; \
        run->resume_stack[run->resume_depth].call_top = run->call_top;  \
        run->resume_stack[run->resume_depth].call_ret = (ret_);         \
        run->call_top = run->resume_depth;                              \
        run->resume_depth++;  run->call_depth++;                        \
    } while (0)

#define RX_RETURN do {                                                  \
        const unsigned t_ = run->call_top;                              \
        run->call_top = run->resume_stack[t_].call_top;                 \
        run->call_depth--;                                              \
        goto *run->resume_stack[t_].call_ret;                           \
    } while (0)
```

**THE CALL FRAME IS NOT POPPED BY THE RETURN.** It stays live, which is the
whole point: §3.2 MEASURED that the call is backtrackable, so the callee's
choice points must survive the return — and so must the return label they will
come back through.

**ORDINARY FRAMES CARRY `call_top`,** and the fail label gains **one line**:

```c
        run->call_top = run->resume_stack[frame_index].call_top;
```

restoring which activation is current, exactly as the line above it restores
`scan_position` and the loop below it rewinds the trail. `call_depth` is
recomputed the same way — it is a **counter for the capacity check and for the
diagnostic**, not the structure, so it is restored from a per-frame `call_mark`
in the same line (§5.6).

**A CALL FRAME'S `resume_label` IS `rx_fail`.** When the frames inside a call
are exhausted, the call itself has no alternatives, so popping the call frame
must continue failing. Making its resume label `rx_fail` is not a placeholder:
it means the fail label needs **no knowledge of frame kinds** and no branch —
the one added line above runs for every frame and is correct for both. The
cost is one extra backtrack step per abandoned call, which is countable, is
charged to the step budget at the site the budget is already charged, and is
exactly the extra one per call §3.2's cost table MEASURED in PCRE2 (ratio →
2.0).

**THREE PROPERTIES, each with the line that makes it true.**

1. **The trailed self-writes precede the `RX_CALL`,** so the call frame's
   `trail_mark` is above them and abandoning the call rewinds them — the saves
   disappear with the call that made them.
2. **`call_top` is a resume-stack INDEX, not a depth,** so it is stable under
   the frame array's own growth and a nested activation's `call_top` chain is a
   linked list through frames that already exist.
3. **Nothing about this is conditional on the pattern being recursive.** The
   same three lines serve `(a)(?1)`, `(?R)`, and `[DD-11]`'s inserted-body
   call. One mechanism.

### 5.2 Why the separate call-stack array is WRONG, derived

The obvious implementation — `const void *call_stack[N]` indexed by
`call_depth`, pushed at the call and **popped at the return** — has a bug, and
it is worth writing out because the plan row proposes exactly that array and
because the bug needs three events to appear.

- The caller is at call depth `d`. It calls **A**: `call_stack[d] = &&retA`,
  depth `d+1`.
- A's callee pushes an ordinary frame **F** and eventually **returns**: depth
  back to `d`. Control is at `retA`.
- `retA`'s continuation calls **B**: `call_stack[d] = &&retB` — **overwriting
  `&&retA`** — depth `d+1`.
- B's callee fails entirely. The backtracker pops down to **F**, restoring
  depth to `d+1` from F's mark. A's callee resumes correctly…
- …and when it succeeds a second time it returns through
  `call_stack[d]`, which is now **`&&retB`**. Control lands in the wrong
  continuation.

The frame's depth mark restores the *depth* and cannot restore the *contents*.
Fixing it needs the contents to be undone too — a second trail, or a
non-popping stack with a separate "current activation" pointer and a
high-water mark that must itself be restored per frame. **Both are strictly
more machinery than putting the return label in the frame**, which is the
structure whose contents the backtracker already restores, by construction,
because a frame is never overwritten while it is live.

**This is also what PCRE2 does** — the return address lives in the recursion's
heap frame, and the frame chain is the backtrack stack — which is a
convergence rather than evidence, and is marked ARGUED where it appears.

### 5.3 The capture save/restore, and the trail IS the storage

§3.1 MEASURED H-RESTORE: the callee writes and the return puts the entry
values back. §3.4(b) MEASURED that **`\K` is not restored**, and pcrec spells
`\K` as a write to `RX_SLOT_WHOLE_START` — so the tempting one-liner, *rewind
the trail to the call frame's mark*, is a **miscompile**: it would undo the
`\K` and answer (0,4) where PCRE2 answers (3,4).

So the restore is over a **compile-time set W of CAPTURE slots**:

> **W(g)** = the slot indices of every capturing group lexically inside
> group `g`'s body, ∪ W(h) for every group `h` that `g`'s body calls —
> the least fixpoint over the call graph. `W(0)` is every capture slot.
> **Slots 0 and 1 are never members**, because `RX_SLOT_WHOLE_START` is
> `\K`'s and `RX_SLOT_WHOLE_END` is written at accept.

and the entry values are stored **in the trail**, with no new array:

- **At the call site, before `RX_CALL`:** for each `s ∈ W`, emit
  `RX_SET(s, slot_values[s])` — a **trailed self-write**. P7 STRUCTURAL: `RX_SET`
  is `RX_TRAIL` then the write, and `RX_TRAIL` records the old value
  **unconditionally**, with no same-value elision. So the entry value is now
  parked at a known trail offset and the slot is unchanged.
- **At the return, before the `goto *`:** for each `j` in `0…|W|−1`, emit
  `RX_SET(W[j], run->trail[run->resume_stack[run->call_top].trail_mark − |W| + j].saved_value)`.

Four properties:

1. **The restore is itself TRAILED**, so backtracking into the callee undoes
   the restore and re-establishes the callee's own values — which §3.2 requires
   and §3.1's per-level cells show is the observable semantics.
2. **The offsets are compile-time constants** off a runtime base. No search, no
   loop, no runtime slot test.
3. **NESTING IS AUTOMATIC.** A calls B; W(B) ⊆ W(A) by the fixpoint, so A's
   restore covers everything B could have touched, and B's own restore already
   ran.
4. **THE COST IS `2·|W|` TRAILED WRITES PER CALL**, known at compile time, and
   it joins `vm_cost`'s trail accounting (§5.7) rather than being discovered as
   a `PCREC_ERR_FRAMES` on a pattern the artifact can match — S87 and S95's
   shape, two constructs over.

**THE ALTERNATIVE THIS DESIGN DID NOT TAKE**, recorded because it is cheaper at
entry and a panel will think of it: a **runtime backward walk** of the trail
from the top down to the call frame's mark, re-applying `saved_value` for every
record whose `slot_index` is a capture slot, pushing new trail records as it
goes. It needs no `W`, no entry cost, and no fixpoint — but it costs O(the
callee's writes) at every return instead of O(|W|), doubles trail usage, and
needs a **runtime** slot-kind test that is exactly the `\K` distinction this
section was nearly wrong about. §12 P-5 is its refutation experiment.

### 5.4 The callee CONTRACT (charter addition (iii))

One contract, stated so that `[M6.6.2]`'s implementer and this one agree, and
so that `[DD-11]` and `[M6.5]`'s follow-up (f) can be held to it.

**A CALLEE BODY MAY ASSUME, ON ENTRY:**

| | |
|---|---|
| `scan_position` | the position the call is to be attempted at. Nothing else about it — **not** that it is ≥ any earlier position, because a lookbehind's back-step may have moved it |
| `slot_values` | the **caller's** capture state, inherited (§3.1 MEASURED). Every slot in `W` has just been parked on the trail; their VALUES are unchanged |
| frames | `resume_depth` is whatever it is. The body may push. Nothing below the call frame is its business |
| trail | `trail_depth` is whatever it is. Every write the body makes must go through `vm_set` |
| `v->fmin` / `v->fdyn` | **ZERO and NULL.** The emitter saves, zeroes and restores them across the body, on **every return path** — `lookaround_design.md` §3.2.1's rule, for the same reason and a different cause: there the follow OVERLAPS the body, here the follow is **UNKNOWN** because a shared body has many callers with different follows. A rung bound baked from one caller's follow is wrong for every other |
| budget | live and charged. The body's steps, work and frames all count (§5.7) |

**A CALLEE BODY GUARANTEES, ON ITS SUCCESS EXIT:**

| | |
|---|---|
| control | reaches **exactly one** exit label, which is the only way out on success. Failure leaves through the shared fail label like every other construct |
| `scan_position` | wherever the body matched to. The caller does **not** get it restored — a call CONSUMES (§2.1's discriminator) |
| frames | the body's choice points are **LIVE** (§3.2 MEASURED). It must not cut them |
| trail | every slot the body wrote is recorded, so an outer rewind undoes it |
| `slot_values` | whatever the body wrote. The **RETURN**, not the body, restores `W` |

**AND THE BODY HAS EXACTLY ONE ENTRY** — nothing jumps into its middle.

**THIS IS THE SAME CONTRACT `lookaround_design.md` §6.4 STATES,** point for
point, which is charter addition (iii)'s premise and the reason §6.4 can
conclude what it does. The one difference is the *reason* for the follow
scoping, and §6.4 says why that matters.

**THE ONE THING A SHARED BODY MAY NOT DO IS DEPEND ON ITS CALLER'S
COMPILE-TIME CONTEXT.** `lookaround_design.md` §6.4's lookbehind-branch
hand-off is the worked example: a branch's width `k` is used three times at the
back-step, and a shared body cannot carry it, so **the width belongs to the
CALL SITE** and the site jumps to `L_body_i` past the back-step. That design
recorded recommendation (a); **this design ratifies it**, and §3.4(d)'s
measurement is the second reason — PCRE2 computes a call's width through the
callee, so a call inside a lookbehind is a width question at the site.

### 5.5 The backtrack out of a returned call, drawn

The single hardest cell, and it is the one §5.2's bug lives in. Pattern
`^(?(DEFINE)(?<g>a|ab))(?&g)c$` on `"abc"` — §3.2's discriminator:

```
  RX_CALL(&&L_ret, 0)          frame#0 = {label rx_fail, pos 0, trail 0,
                                          call_top SENTINEL, ret &&L_ret}
                               call_top = 0, call_depth = 1
  L_entry_g:  RX_PUSH(&&L_alt2, 0)     frame#1 = {label &&L_alt2, pos 0,
                                                  trail 0, call_top 0}
              'a' matches, pos = 1
  L_exit_g:   RX_RETURN         call_top = SENTINEL, call_depth = 0,
                                goto *&&L_ret       <- frame#0 STAYS
  L_ret:      'c' vs subject[1] = 'b'  -> goto rx_fail
  rx_fail:    pop frame#1 -> pos = 0, trail rewound, call_top = 0,
                             goto *&&L_alt2
  L_alt2:     'ab' matches, pos = 2
  L_exit_g:   RX_RETURN         reads frame#call_top = frame#0 -> &&L_ret
  L_ret:      'c' vs subject[2] = 'c'  -> match (0,3)
```

**The pop of frame#1 restored `call_top` to 0, which is why the second
`RX_RETURN` finds the right label.** Delete that one line from the fail label
and the second return reads `resume_stack[SENTINEL]` — S-SR2's sabotage, and
its prediction is that every multi-alternative callee goes red while a
single-path callee stays green.

**Now the §5.2 bug, in the same notation**, on a pattern with a call after a
call (`^(?(DEFINE)(?<g>a|ab))(?&g)(?&g)y$` on `"xyxy"`, MEASURED (0,4),
`out/atomicity.txt` T3): with a separate array, the second `RX_CALL` writes
`call_stack[0]` and the first call's return label is gone. With frames, the
second call is **frame#2** and frame#0 is untouched.

### 5.6 The depth capacity, the new give-up code, and the `ERR_FLOOR` move

§3.3 RULED: **the depth capacity is the only guard.** No compile-time
left-recursion refusal (PCRE2 has none), no same-position runtime check (§3.3
MEASURED it would be a miscompile).

**TWO COUNTERS, TWO CODES, ONE ARRAY.**

- `resume_depth` against `RX_RESUME_FRAMES` → `PCREC_ERR_FRAMES`, unchanged.
- **`call_depth` against `RX_CALL_DEPTH` → `PCREC_ERR_RECURSE`**, new.

The second is a counter, an increment, a decrement and one compare — and it is
worth its cost for a reason a panel should weigh rather than accept: without
it, a runaway left recursion and a legitimately deep one both answer
*"frames"*, and the frame budget is sized for **choice points**, not depth. A
caller that gets `PCREC_ERR_RECURSE` knows to raise a recursion bound; one that
gets `PCREC_ERR_FRAMES` does not know which bound to raise. §14 ASK 1 puts it
to Frank, because **the plan row's premise for it — a separate bounded call
stack — did not survive §5.2**, and a reserved code whose original
justification is gone deserves to be re-asked rather than spent.

**THE ARTIFACT STAMPS IT**, joining `RX_RESUME_FRAMES` and `RX_TRAIL_FRAMES`
(P12): `#define RX_CALL_DEPTH n`, and `rx_info` gains the field beside
`work_budget`. `Cost` already has `unbounded`/`growable` and a recursive call is
`unbounded` by its own definition, so the honest-ceiling machinery is reused,
not rebuilt.

**THE `ERR_FLOOR` MOVE, −4 → −5, TOUCHES EIGHT SOURCE-OF-TRUTH SITES.**
MEASURED by grep, `out/premises.txt` axis C (the four `m6read_samples/` files
are archived samples of emitted output, listed separately because they are
evidence of a past emission and are **not** edited):

| # | site | what moves |
|---|---|---|
| 1 | `src/gen/emit_dfa.c:391-394` | the emitted `#define` block: `PCREC_ERR_RECURSE (-5)` added, `PCREC_ERR_FLOOR` becomes `(-5)` |
| 2 | `src/gen/emit_dfa.c:375-379` | the emitted comment naming the codes |
| 3 | `src/gen/emit_vm.c:5680-5682` | the per-prefix internal sentinels: `%s_R_RECURSE` joins `_R_STEPS`/`_R_FRAMES`/`_R_WORK` |
| 4 | `src/gen/emit_vm.c:6248-6250` | the search entry's collapse — the new code must PROPAGATE, D49's whole point |
| 5 | `src/gen/emit_vm.c:6314-6315` | the emitted eleven-line give-up comment block |
| 6 | `lib/pcrec.h:380` | the ABI prose naming `[<PREFIX>_ERR_FLOOR, -2]` |
| 7 | `docs/spec/match_api.md:171, 209, 213, 222, 822, 850` | the authoritative contract, including the `if (ret < PCREC_ERR_FLOOR) __builtin_trap();` obligation |
| 8 | `tests/codegen/run_codegen_tests.sh:848, 883` | the two name lists the `[ABI-NS]` check reads |

plus `docs/design/match_api_m4.md:303, 464, 510, 516` and
`docs/design/design_callout_abi.md:159, 164` as design records that cite the
floor by value.

**AND THE MOVE IS A CONTRACT CHANGE, SO IT IS D49'S OWN RE-OPEN CLAUSE BEING
EXERCISED**, not a free edit: D49 says *"getting the partition wrong
pre-release costs a renumber and nothing else"*, which is the licence, and
`design_callout_abi.md` F2's trap obligation is respelled against the new floor
in the same commit. **Zero generated files in the tree contain the trap line
today** (D49's own measurement), so the codegen that must change still does not
exist.

### 5.7 Budgets (D42 item 6)

**NOTHING NEW IS NEEDED TO COUNT A CALL'S WORK, and that is the point.** The
callee is emitted by `vm_emit`, so every push, pop and cut inside it goes
through the same primitives and `emit_vm.c:6051`'s single decrement —
*"a step is one backtrack resumption, counted at exactly this place"* — already
sees them all. Three charges are this module's own:

- **The call frame's own pop** — one step per abandoned call, at the fail
  label, already counted. §3.2 MEASURED that PCRE2 charges the same extra one
  per call (ratio → 2.0 against an inlined control), so pcrec's accounting and
  PCRE2's agree in SHAPE, which is what D42.6 asks for.
- **The save/restore** — `2·|W|` trail entries per call, a compile-time
  constant, added to `vm_cost`'s `trail` for the call site and to `pt` (the
  per-iteration trail) when the call sits under a growing quantifier. An
  artifact that under-sizes `trail_frames` returns `PCREC_ERR_FRAMES` on a
  pattern it can match — S87/S95's exact failure mode — so S-SR7 is a
  two-site row.
- **The recursion itself is `Cost.unbounded`**, so the artifact stamps a
  ceiling rather than silently capping (P12).

**AND `RX_CHARGE_WORK` IS NOT USED HERE.** A call does no work proportional to
anything discarded — it discards nothing (§3.2). The work counter's customers
are cuts and back-steps; a call is neither.

### 5.8 The SECOND indirect jump, and the emitter's own invariant

`emit_vm.c:9-12` and `:18` state, as a design decision, that there is
*"exactly ONE indirect jump in the whole function — the `goto *` at the fail
label, which fires once per backtrack and never per byte"*. MEASURED (P9): the
emitter has one `goto *` and a real artifact has one.

**`RX_RETURN` IS A SECOND, and it fires once per call return.** The comment
must be amended rather than quietly falsified, and the amendment is the honest
form of the same property: *two* indirect jumps, both off the hot path, one per
backtrack and one per call return, and **still no per-byte dispatch** — which
is the property `emit_vm.c:11-12` actually cares about (D13's
table-vs-computed-goto arbitration does not arise). Wave A owns the edit, and
**S-SR13 is a codegen row asserting the count**: a call-free artifact has
exactly one `goto *` and a call-bearing one has exactly two. That row is what
stops a future construct adding a third without anyone noticing.

**AND THE STREAMING CONSTRAINT GAINS A SECOND CONSUMER.** `emit_vm.c:15-17`
records that APPROACH §6's A-4/A-5 *"a `&&label` does not survive a return"* is
a **streaming** constraint, not a within-call one. A call stack of label
addresses is now the second thing in the emitter that would have to be
re-expressed if `[M3.0]`/`[OS-3]` ever suspends a match across a `feed()`.
§13 records it as out of scope and cross-notes `[M3.0]`.

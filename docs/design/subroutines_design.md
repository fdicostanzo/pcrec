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
a second call made after the first returns and that is a real bug — **derived
in §5.2 and then BUILT: the rejected design gets 3 of 50 cells wrong, one of
them a false match, while agreeing on the other 47** (§5.9). (1) plus the measurement that **`\K` is NOT restored by a
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
contract with two linkages (§6.4). **§5 was not left as prose** — the whole
lowering is hand-built in the emitter's idiom and run against libpcre2 on four
patterns at **45 cells agreeing, 4 agreed-in-kind (both engines refused), 0
disagreeing**, and that run is what found this design's own capture restore set
incomplete (§5.9), which is the argument for executing a design section that
can be executed. Engine selection is `VM_ONLY` structurally
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
| `probes/probe_spellings.py` | MEASURED, both oracles | §2: **ten call spellings and nine reference spellings separated by ONE cell** (`(a|b)X` on `"ab"`); the relative and forward forms; `(?R)`/`(?0)`/`\g<0>`; two-digit group numbers; the `(?(DEFINE))` idiom and a DEFINE-less equivalent swept over 11 subjects; python's verdict on the whole vocabulary |
| `probes/probe_captures.py` | MEASURED, libpcre2 + CALLOUTS | §3.1/§3.4: the capture state after return, **during** the call, at depth > 1, after a failed call; inheritance; `\K`; `(?J)` duplicate names and the call/reference resolution split |
| `probes/probe_atomicity.py` | MEASURED | §3.2: the naive cell that decides nothing and the isolated cell that decides it; four atomic controls; quantified calls and the empty-body guard; calls inside lookaround/atomic/lookbehind; the retry COST against an inlined control |
| `probes/probe_leftrec.py` | MEASURED | §3.3: direct, indirect and nullable-prefix left recursion; the two guards; **the decisive sweep that refutes the same-position reading**; `(?R)` under a quantifier; a call inside a lookbehind; depth requirement vs subject; and the error-140 sweep that shows the charter's premise is not about recursion at all |
| `probes/probe_linkage.sh` + `prototype/gen_linkage.py` | PROTOTYPE | §6: three hand-written matchers in the emitter's own idiom, differing only in linkage; a 52-cell agreement control first, then emitted-size by call count and run time on two corpora (mixed, and lexical-only — the corpus HYBRID's whole claim rests on) |
| `probes/probe_callproto.py` + `prototype/callproto.c` | PROTOTYPE + MEASURED | §5.9: **§5's whole lowering, built and run against libpcre2** — the frame that carries the return label, the non-popping return, the fail label's one added line, the `\|W\|` trailed save/restore — on four patterns each of which is a design claim; compiled TWICE, the second with `-DBROKEN_ARRAY` for §5.2's rejected design, so the bug is REPRODUCED rather than argued |
| `probes/probe_prefilter.py` | MEASURED, libpcre2 + in-pcrec | §8: what a DFA prefilter is worth on call-**shaped** patterns, measured on their INLINED equivalents (which pcrec compiles today), each pair verified equivalent **420 cells / 0 disagreements** before any timing |
| `probes/probe_population.py` | MEASURED, PURE TEXT | §10: the census — **6** call spellings in `tests/**/*.rxt`'s 2,161 pattern lines, every one of them a `perr` row testing a refusal, against **226** backreferences |

**`probes/archive.sh` is the ONLY writer of `out/`**, R30 M7's rule inherited
through three lanes, with this lane's module stamp scoped at creation (R32
D1/C14 found the backrefs archiver stamping the wrong module in all eight of
its files).

**TEN INSTRUMENT DEFECTS this lane found by running its own probes**, each of
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
10. **`probe_callproto` reported SIX false disagreements with libpcre2.** Its
   pattern table said the two `(?(DEFINE)…)` patterns had **0** capture groups
   while the C side printed **1**, so every matching cell compared
   `"match 0 3 -1 -1"` against `"match 0 3"` and the probe announced that
   §5's lowering does not reproduce 10.46. It is the same
   two-oracles-compared-across-a-report-shape-difference defect the lookaround
   lane logged, and the reason `la_oracle.ngroups()` exists at all.

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
| P5 | **`(?(DEFINE)...)` is module `conditionals`, which has exactly ONE row and no producer** | MEASURED, axis B: `(?(DEFINE)(?<x>a))(?&x)` answers *"module 'conditionals' is enabled but `(?(...)` is not implemented yet"*, and `--list-syntax` shows one `conditionals` row, `(?(1)a\|b)`. This module unlocks none of it — §2.5 |
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

**EVERY SPELLING SHIPS — the charter's TEN plus the TWO it did not have — AND
NOTHING IN THIS MODULE REFUSES A CONSTRUCT PCRE2 HAS**. (The count of
*spellings* is a matter of how finely `(?N)`/`(?±N)`/`\g<…>` are enumerated;
what is not a matter of counting is that **the whole table's `pcrec` column
reads SHIPS**.) which is unusual for a pcrec module and is worth saying plainly:
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
2ⁿ+1: **a call-linked search does TWICE the backtracks of the same language
inlined**, and the ratio is monotone and tending to 2.0 across 1…8 call sites.

**WHAT THE FACTOR OF 2 IS, and this reading is ARGUED rather than measured**
(§12 P-10): each *activation* of a call appears to cost one backtrack beyond
what the body itself costs — which is what §5.1's non-popping call frame also
costs, since an abandoned call frame pops through the fail label like any
other. What is MEASURED is the ratio; the attribution to the return is an
interpretation, and the experiment that would settle it is a callout count of
the activations against the limit.

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
    L_site:   RX_CALL(&&L_ret, scan_position)   // a resume frame with a return label
              RX_SET(W[0], slot_values[W[0]])   // §5.3: |W| trailed SELF-writes,
              ...                               //  parking the caller's values on
              RX_SET(W[n-1], slot_values[W[n-1]])  // the trail at fixed offsets
              goto L_entry_g
    L_entry_g:  <the callee's body>                -> L_exit_g
    L_exit_g: RX_RETURN                            // restore W, then goto* the frame's ret
    L_ret:    <the continuation>
```

**THE SAVES COME AFTER THE PUSH, and the order is load-bearing**: the call
frame's `trail_mark` is then exactly the index of the FIRST save, so the return
reads `W[j]`'s parked value at `trail[trail_mark + j]` with `j` a compile-time
constant. Saving first would work too and would put the block at
`trail_mark − |W| + j`; this order is chosen because the offset is simpler to
read in the emitted C and because a rewind that abandons the call then
discards the saves along with the frame that owned them.

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

**ORDINARY FRAMES CARRY `call_top` AND `call_mark`,** and the fail label gains
**two lines** — the shape §5.9's prototype ships:

```c
        run->call_top   = run->resume_stack[frame_index].call_top;
        run->call_depth = run->resume_stack[frame_index].call_mark;
```

restoring which activation is current and how deep the recursion is, exactly as
the line above them restores `scan_position` and the loop below them rewinds the
trail. **The second line is the capacity counter's, not the structure's**
(§5.6) — `call_top` alone is enough for correctness, and `call_depth` exists so
a give-up can name its cause. If §14 ASK 1 rules `PCREC_ERR_RECURSE` out, that
line and the field go with it and the mechanism is unaffected, which is the
cleanest evidence that the counter is separable.

**A CALL FRAME'S `resume_label` IS `rx_fail`.** When the frames inside a call
are exhausted, the call itself has no alternatives, so popping the call frame
must continue failing. Making its resume label `rx_fail` is not a placeholder:
it means the fail label needs **no knowledge of frame kinds** and no branch —
the two added lines above run for every frame and are correct for both. The
cost is one extra backtrack step per abandoned call, which is countable and is
charged to the step budget at the site the budget is already charged. §3.2
MEASURED PCRE2 doing **twice** the backtracks of an inlined control over 1…8
call sites, which is the same order of overhead — the RATIO is measured, the
attribution to the return is ARGUED (§12 P-10).

**THREE PROPERTIES, each with the line that makes it true.**

1. **The trailed self-writes follow the `RX_CALL`,** so the call frame's
   `trail_mark` is the index of the first of them (§5.3) and popping the call
   frame discards them with the activation that owned them.
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

> **W(g)** = **`g`'s OWN two slots**, ∪ the slot indices of every capturing
> group lexically inside `g`'s body, ∪ W(h) for every group `h` that `g`'s
> body calls — the least fixpoint over the call graph. `W(0)` is every
> capture slot. **Slots 0 and 1 are never members**, because
> `RX_SLOT_WHOLE_START` is `\K`'s and `RX_SLOT_WHOLE_END` is written at
> accept.

**`g`'s OWN SLOTS ARE IN `W(g)`, and this design's first draft left them
out.** MEASURED, `out/captures.txt` C3: `^((a)(?1)?(b))$` on `"aabb"` answers
g1 = **(0,4)**. Group 1's START is written at entry, so the recursive call
overwrites it with 1 — and the outer level's answer is 0. Without `g`'s own
slots in `W` the emitted matcher reports **g1 = (1,4)**, a wrong span on a
correct match, which no `m`/`n` expectation would catch and only a `g` line
would. §5.9's prototype is where the omission was found, by building the
mechanism and running it.

and the entry values are stored **in the trail**, with no new array:

- **At the call site, immediately after `RX_CALL`:** for each `s ∈ W`, emit
  `RX_SET(s, slot_values[s])` — a **trailed self-write**. P7 STRUCTURAL:
  `RX_SET` is `RX_TRAIL` then the write, and `RX_TRAIL` records the old value
  **unconditionally**, with no same-value elision. So the entry value is now
  parked at a known trail offset and the slot is unchanged.
- **At the return, before the `goto *`:** for each `j` in `0…|W|−1`, emit
  `RX_SET(W[j], run->trail[run->resume_stack[run->call_top].trail_mark + j].saved_value)`.

  and `trail_mark + j` is exact because §5.1 pushes the frame first: the
  frame's mark IS the index of the first save. **The saves cannot be rewound
  while the activation is live** — every frame the callee pushes has a
  `trail_mark` at or above `trail_mark + |W|`, so no rewind that keeps the
  call alive can reach them, and a rewind that does reach them has popped the
  call frame itself.

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
  RX_CALL(&&L_ret, 0)          frame#0 = {label rx_fail, pos 0, trail_mark 0,
                                          call_top SENTINEL, call_mark 0,
                                          ret &&L_ret}
                               call_top = 0, call_depth = 1
  RX_SET(2, slot_values[2])    trail[0] = {slot 2, g's OLD start}   |W| = 2
  RX_SET(3, slot_values[3])    trail[1] = {slot 3, g's OLD end}
  L_entry_g:  RX_PUSH(&&L_alt2, 0)     frame#1 = {label &&L_alt2, pos 0,
                                                  trail_mark 2, call_top 0,
                                                  call_mark 1}
              'a' matches, pos = 1;  RX_SET(3, 1)  -> trail[2]
  L_exit_g:   restore W from trail[0], trail[1]   -> trail[3], trail[4]
              RX_RETURN         call_top = SENTINEL, call_depth = 0,
                                goto *&&L_ret       <- frame#0 STAYS
  L_ret:      'c' vs subject[1] = 'b'  -> goto rx_fail
  rx_fail:    pop frame#1 -> pos = 0, trail rewound TO 2 (which UNDOES the
                             restore and re-establishes the callee's g),
                             call_top = 0, call_depth = 1,
                             goto *&&L_alt2
  L_alt2:     'ab' matches, pos = 2
  L_exit_g:   restore W from trail[0], trail[1]   (still there: they are
                             BELOW frame#1's mark and were never rewound)
              RX_RETURN         reads frame#call_top = frame#0 -> &&L_ret
  L_ret:      'c' vs subject[2] = 'c'  -> match (0,3)
```

**Two things in that trace are worth reading twice.** The rewind to frame#1's
mark **undoes the return's restore**, which is §5.3 property 1 doing exactly
what §3.2's measurement requires — the callee's own capture state comes back
when we re-enter it. And the two save records at `trail[0]`/`trail[1]` sit
**below** frame#1's mark, so no rewind that keeps the call alive can reach
them, which is why the second `RX_RETURN` finds them where it left them.

**The pop of frame#1 restored `call_top` to 0, which is why the second
`RX_RETURN` finds the right label.** Delete the `call_top` line from the fail label
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
  label, already counted. §3.2 MEASURED PCRE2 doing **twice** the backtracks of
  an inlined control over 1…8 call sites, so pcrec's accounting and PCRE2's
  agree in SHAPE (a bounded constant factor, not a different growth), which is
  what D42.6 asks for.
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

### 5.9 THE MECHANISM WAS BUILT AND RUN — PROTOTYPE

Everything above is executable, so this lane executed it.
`prototype/callproto.c` implements §5 by hand in the emitter's own idiom — the
frame carrying `call_ret`/`call_top`/`call_mark`, `RX_CALL` pushing a frame
whose `resume_label` is `rx_fail`, `RX_RETURN` **not** popping, the fail
label's one added line, and §5.3's `|W|` trailed self-writes and restores read
back at `trail_mark + j` — for four patterns, each of which is a claim in this
document:

| | pattern | the claim it executes |
|---|---|---|
| **P1** | `^((a)(?1)?(b))$` | §3.1's per-level capture save/restore, at depth 1..3, with the lexical occurrence SPLICED and the call site taking the LINKAGE — §6.3's ruling, built |
| **P2** | `^(?(DEFINE)(?<g>a\|ab))(?&g)c$` | §3.2's atomicity discriminator and §5.5's drawn cell: the follow fails after the callee's first success and must retreat INTO the returned call |
| **P3** | `^(a\|(?1)a)$` | §3.3's cell: `n−1` nested recursions ALL ENTERED AT OFFSET 0, which must MATCH |
| **P4** | `^(?(DEFINE)(?<g>x\|xy))(?&g)(?&g)y$` | §5.2's CLOBBER SEQUENCE |

and it is compiled **twice**: as designed, and with `-DBROKEN_ARRAY`, which
replaces the frame-carried return label with the plan row's separate
`call_stack[]` indexed by call depth and popped at the return. The two builds
differ in **one thing only** — where the return label lives and when it is
popped.

**THE RESULT** (`out/callproto.txt`, 50 cells):

| comparison | |
|---|---|
| prototype vs libpcre2 10.46 | **45 agree, 4 agreed-in-kind, 0 DISAGREE, 1 excluded** |
| designed vs `-DBROKEN_ARRAY` | **47 agree, 3 DISAGREE** |

- The **4 agreed-in-kind** cells are P3's non-terminating subjects, where
  libpcre2 answers `rc −52` and the prototype answers `PCREC_ERR_RECURSE` at
  its stamped depth. §3.3's ruling, working: both refuse, neither lies. The
  probe prints both codes rather than scoring them as a match.
- **P3 matches `"a"×1023` and `"a"×1024`** — 1023 nested same-position
  recursions — and gives up at `"a"×2000` with `RX_CALL_DEPTH` at 1024.
  §3.3's 199-deep measurement is reproduced by construction, and §5.6's
  capacity is the thing that ends it.

**AND §5.2's BUG IS NOW MEASURED RATHER THAN DERIVED.** The three cells the
broken build gets wrong are all P4's, and one of them is a **FALSE MATCH**:

| subject | designed | `-DBROKEN_ARRAY` | libpcre2 |
|---|---|---|---|
| `"xyxy"` | match (0,4) | **nomatch** | match (0,4) |
| `"xyy"` | nomatch | **match (0,3)** | nomatch |
| `"xyxyy"` | match (0,5) | **nomatch** | match (0,5) |

**and it agrees on the other 47**, which is what localises the failure to the
clobber sequence rather than to a second difference between the builds.

**ONE CELL IS EXCLUDED AND IT IS A FINDING RATHER THAN AN EXCUSE.**
`^(a|(?1)a)$` on `""`: libpcre2 answers **nomatch**, the prototype answers
`recurse`. libpcre2's own **start optimization** rejects a subject shorter
than the pattern's minimum length **before the recursion is entered**; the
prototype has no minimum-length prune. **pcrec DOES** — `pcrec_minw`, and
§4.4 gives `A_CALL` a least-fixpoint arm whose answer here is 1 — so the
shipped compiler agrees with libpcre2 where this prototype cannot. The cell is
listed by name in the probe rather than dropped, because a differential that
quietly excludes its own failures is not a differential; and it is the second
place this document's `minw` arm earns itself.

**WHAT THE PROTOTYPE DOES NOT COVER**, stated so it is not read as more than
it is: no prefilter, no MRL prune, no possessification, no revdet, no budget
counters other than the two capacities, and four patterns rather than a
corpus. It executes the **linkage and the capture discipline**, which are the
parts §5 invents, and nothing else.

---

## 6. The addressable body: two linkages, one contract (charter additions (i)–(iv))

### 6.1 "Once-emitted-with-two-linkages" collapses when it is written out

The charter names the alternative to a call as *"the lexical occurrence falls
through to a shared body whose exit dispatches on 'was I called?'"*. Writing
that exit out shows it is not a third design: **"was I called?" is a
per-ACTIVATION question**, the body can be entered from the fall-through and
from a call in the same match, and the only per-activation channel is the call
record itself. So the fall-through path must leave a record too — and a record
saying "return to my own continuation" **is** the call linkage.

The genuine three-way choice is therefore:

| | copies of the body | lexical path pays | called path pays |
|---|---|---|---|
| **SPLICE** | one per occurrence, `k+1` | nothing | nothing |
| **HYBRID** | 2 (the lexical one, plus one shared) | nothing | the linkage |
| **CALL** | 1 | the linkage | the linkage |

and HYBRID is what "two linkages" means once it is made to work. This is what
`prototype/gen_linkage.py` generates, and its header records the collapse so
the next reader does not re-derive it.

### 6.2 The three linkages, PROTOTYPE-measured

Three hand-written matchers in the emitter's own idiom (computed goto, the
resume array, the trail, `RX_SET`/`RX_PUSH` spelled as `emit_vm.c:5763-5786`
spells them), for one family — `^([a-z]+)` then `k` repetitions of
`.<the same body>` then `$`, i.e. one LEXICAL occurrence and `k` call sites.
Built with the same `gcc -O2 -std=gnu11`. `out/linkage.txt`.

**CONTROL FIRST: the three agree on 13 subjects × 4 call-counts = 52 cells.**
Three matchers that disagree are not three linkages for one pattern, and the
probe refuses to print a number until they agree.

**SIZE**, bytes of `rx_match_anchored` from `nm -S`:

| k | SPLICE | HYBRID | CALL |
|---|---|---|---|
| 0 | 779 | 779 | 708 |
| **1** | **1001** | 1090 | 804 |
| 2 | 1384 | 1191 | 884 |
| 4 | 1976 | 1350 | 1044 |
| 8 | 3179 | 1706 | 1356 |
| 16 | **5543** | **2320** | **1992** |

**~300 bytes per call site for SPLICE, ~80 for the other two.** The `k = 0`
baseline row is the reachability control: with no call site SPLICE and HYBRID
are literally the same code (779 = 779), so the axis is measuring the linkage
and not the generator's scaffolding.

**TIME**, best of three, 2,000,000 reps, two corpora:

| k | MIXED: SPLICE / HYBRID / CALL | LEXICAL-ONLY: SPLICE / HYBRID / CALL |
|---|---|---|
| 1 | 0.57 / 0.58 / 0.64 | 1.04 / 1.08 / 1.15 |
| 2 | 0.81 / 0.87 / 1.40 | 1.10 / 1.13 / 1.16 |
| 4 | 1.17 / 1.40 / 1.37 | 1.04 / 1.08 / 1.15 |
| 8 | 1.52 / 1.86 / 1.92 | 1.03 / 1.10 / 1.14 |

The **LEXICAL-ONLY** corpus is the one HYBRID's whole claim rests on — subjects
that die before the first call site. HYBRID tracks SPLICE within ~5% and beats
CALL by ~5–10% on every row; the residual gap between HYBRID and SPLICE on a
path that is literally the same code is layout and i-cache, and is reported
rather than smoothed. The MIXED column's `k = 2` CALL cell (1.40 against 0.87)
is out of line with its neighbours and is **noise this probe did not
eliminate**: best-of-three did not remove it, and it is left visible rather
than dropped.

### 6.3 THE RULING

**The LEXICAL occurrence of a called group is emitted EXACTLY AS IT IS TODAY.**
Not "spliced" as a new thing — *unchanged*. That is the HYBRID row, and it buys
three things beyond the ~5% on the lexical path: the existing group emission
needs no edit; a call-free pattern is byte-identical by construction (§9.1);
and the module's diff does not touch the code path that every other pattern in
the corpus goes through.

**A CALL SITE takes the CALL linkage into one shared copy — EXCEPT** where all
three hold, in which case it SPLICES:

1. the callee is **not** in a cycle of the call graph (not recursive, directly
   or mutually), **and**
2. the callee's target is statically resolved — which it always is (§4.2), so
   this condition is free and is listed to make the shape explicit for
   `[DD-11]`, and
3. the spliced expansion stays under a **size budget**, checked against the
   same `Cost` machinery that already sizes an artifact.

**SPLICING IS WAVE 3, NOT WAVE 1.** Wave 1 ships the CALL linkage for every
call site, because it is one path, it is correct for every shape including
recursion, and it is what the four gating questions are about. Wave 3 replaces
the eligible sites with a splice. That is implement-then-replace, which Frank's
2026-08-23 rule permits explicitly, and it is **not** a parallel mechanism: the
splice consumes the same callee contract (§5.4) and the same `W` (§5.3) and
differs only in how control reaches the body.

**AND SPLICING IS WHERE THE PREFILTER COMES BACK.** §8.3.

### 6.4 Should any LOOKAROUND body compile as a call? (charter addition (ii))

**NO, and the reason is the `k = 1` row.**

A lookaround body has **exactly one use site by construction** —
`lookaround_design.md` §6.4(3): *"`vm_label()` allocates per emission, and the
slot families are indexed per node, so two lookarounds over the same body text
get two sub-programs."* So `k = 1` always, and §6.2 measured `k = 1`:

- SPLICE **1001 bytes**, HYBRID **1090**, CALL **804**;
- SPLICE **0.57 s** mixed and **1.04 s** lexical, CALL **0.64** and **1.15**.

CALL is 197 bytes smaller and 10–12% slower. **A call to a body with one caller
buys a size saving that is smaller than the module's own scaffolding and costs
time on the only path that exists.** There is no reuse to amortise, because
there is no second caller.

**AND THE SECOND REASON IS THE CONTRACT.** §5.4's follow scoping is required
for a shared body because the follow is UNKNOWN; `lookaround_design.md`
§3.2.1's is required because the follow OVERLAPS. Both zero `fmin`/`fdyn`, so a
lookaround body already satisfies the callee contract **without** being a call.
Turning it into one would change the linkage and nothing else.

**RULED: no lookaround body compiles as a call, and §6.5's premise stands.**

### 6.5 The premise survives: `vm_look`'s splice IS the inliner (charter (iii))

Charter addition (iii) states it as a premise; §6.2 and §6.4 are what makes it
a finding.

> `[M6.6.2]`'s `vm_look` emits a **self-contained body region** with a scoped
> follow, one entry and one clean exit. §5.4 is that same contract, written
> from the caller's side. A statically-resolved, non-recursive, single-
> continuation call **splices through exactly that mechanism**; a recursive or
> shared body takes the call linkage. **One callee contract, two linkages.**

**THREE CONSUMERS, and they are the whole justification for building the
contract rather than the construct:**

| consumer | linkage | why |
|---|---|---|
| `[M6.6.2]` lookaround | SPLICE, always | `k = 1` by construction (§6.4) |
| `[DD-14]` calls | both (§6.3) | recursion forces the linkage; §8.3 wants the splice |
| `[M6.5]` follow-up (f), `A_BREF` → call under the singleton predicate | SPLICE where the predicate holds | a backreference to a group that can only have matched one way is a call to it — and it is `k = 1` per reference |

### 6.6 The reuse inventory, and the genuinely new list (charter (iv))

**REUSED FROM `[M6.6.2]` / `[M6.4]` / `[M6.5]`, unchanged:**

| mechanism | where it comes from | what this module does with it |
|---|---|---|
| the self-contained sub-program contract | `lookaround_design.md` §6.4 | §5.4 restates it from the caller's side; **no code** |
| the follow scoping (`fmin`/`fdyn` saved, zeroed, restored on **every** return path) | `lookaround_design.md` §3.2.1, `vm_atomic` `emit_vm.c:4244-4247/4285-4286` | same rule, different reason (unknown follow, not overlapping follow). §5.4 |
| the one-frame trail idiom — a pushed frame restores the cursor and rewinds the trail for free | P8, `lookaround_design.md` §3.3 | §5.1's call frame IS that idiom with a return label |
| `RX_CUT` / `vm_cut` | `[ENG-BREP]`, `[M6.4.2]` | **NOT USED.** §3.2 MEASURED the call is backtrackable. Recorded because the plan row offers it |
| the budget primitives | D42.6, `emit_vm.c:6051` | §5.7: nothing new to count |
| `Cost.unbounded` and the stamped ceiling | `emit_vm.c:1331-1348`, P12 | §5.6 |
| the `PendingRef` + end-of-parse resolver | `[M6.5.2]`, P11 | §4.2: **one field**, two rules |
| `pcrec_bref_mark`'s marked set | `[M6.5.2]`, P10 | §4.3: calls join it, transitively |
| the shared `\g` port | P3 | §4.2: two tails, one port |
| the identity-gate shape and the four axes | `[M6.6.2]` ASK 4 ruling | §9.1 |
| the verification template (a differential driver + a sabotage matrix arm) | `backrefs_design.md` §4, `lookaround_design.md` §9 | §9, §10 |

**GENUINELY NEW, AND ALL OF IT ON THE CALLER SIDE:**

| new thing | §  | why it could not be reused |
|---|---|---|
| the call record (return label + `call_top`), and the fail label's one added line | §5.1, §5.5 | nothing in the tree returns to a value-carried label |
| the second `goto *`, and the emitter invariant it amends | §5.8 | the file states one-indirect-jump as a decision |
| the per-level capture save/restore over a compile-time `W` | §5.3 | no construct today restores capture state on an exit |
| `W`, the call graph, and its fixpoint | §5.3, §4.3 | pcrec has no call graph |
| the depth capacity and `PCREC_ERR_RECURSE`, with the `ERR_FLOOR` move | §5.6 | the give-up space is frozen contract |
| left recursion: **the absence** of a check, and the measurement that says so | §3.3 | the charter asked for the opposite |
| the prefilter answer | §8 | erasure is not a superset |

**THE FOUR GATING QUESTIONS ALL LIVE IN THE RIGHT-HAND TABLE**, which is
charter addition (iv)'s claim, and it survives — with one correction: the
charter puts *"per-level captures"* on the new side, and it is; but it also
implies the **callee** side is fully paid for, and §5.4's follow-scoping row is
paid for only because `[M6.6.2]` lands first. If the two modules had been
sequenced the other way this module would have had to derive it, and
`lookaround_design.md` §3.2.1 records that its own first draft got it wrong.

---

## 7. The convergence with `[DD-11]`

`[DD-11]`'s row RULED the order: `[M6.6]` → `[DD-14]`'s call primitive →
`[DD-11]`'s definition substitutions **implemented on that primitive** → D66's
optimizer. Frank's words on 2026-08-23: *"I don't want parallel mechanisms if
we can avoid it."*

**WHAT `[DD-11]` GETS, AND IT NEEDS NO SECOND MECHANISM:**

1. **An insertion IS a non-recursive call** to the inserted body's entry label
   — `A_CALL` with `link = SPLICE` and a `body` that points at a template
   subtree rather than at an `A_CAP`. §4.1's `body` field is a `const Ast *`
   for exactly this reason: it is **not** typed as a group.
2. **Compile-time splicing is the optimization of the statically-resolved
   case**, which is §6.3's rule verbatim. A definition insertion is always
   statically resolved, so it always splices — and `[DD-11]` gets §6.2's
   measured size and time for free.
3. **The callee contract (§5.4) is the interface.** A template body must
   satisfy it: one entry, one success exit, scoped follow, trailed writes,
   frames left live. Every replacement `[DD-11]`'s table proposes
   (`\Z ≡ (?=\n?\z)`, `(?m)^ ≡ \A|(?<=\n)(?!\z)`, `\b ≡ …`) is a lookaround or
   an anchor, and `lookaround_design.md` §6.4 already certifies those.
4. **HYGIENE IS ALREADY RULED AND THIS DESIGN OBEYS IT.** `[DD-11]`(d):
   *"groups inside an insert are locally referenceable BY NUMBER only … and
   globally referenceable BY NAME."* §4.2's resolver is where that law is
   enforced, and the shape it needs is a **scope** on the number rule, not a
   new pass — a `PEND_CALL`/`PEND_BREF` record already carries the offset that
   says which insert it came from.

**WHAT `[DD-11]` STILL HAS TO BUILD, and this design deliberately does NOT:**

- **The environment model.** The journal's 2026-08-23 discussion RULED the
  resolution rule (propagate/capture-at-build, never walk-up) and the two entry
  kinds (replacement bindings and parameter bindings). None of it is designed
  here. The **interface** this module offers is exactly one function:

  > given a resolved template `const Ast *body`, an `A_CALL` node with
  > `link = SPLICE`, `target` unused, and `save`/`nsave` computed by
  > `src/opt/callgraph.c`, emits the body at the site with the callee contract
  > held.

- **The typed definitions table**, its parse-once discipline, and the
  three-way self-check the journal describes. Test infrastructure and a
  producer, neither of which is a call.
- **The composition RECOGNIZER** that gets the folded fast paths back. §8.3's
  approximation is this module's version of the same problem and is a
  precedent, not a solution.

**THE ONE THING THIS DESIGN ASKS `[DD-11]` NOT TO DO** is give a definition
insertion its own node kind. `A_CALL` with a `body` pointer is the same node;
a second kind would be the parallel mechanism the ordering exists to prevent,
and it would need its own arm in all ten files of §4.4.

---

## 8. Engine selection and the prefilter

### 8.1 Every row is `VM_ONLY`, and three row families are MISSING

The language a call generates is **not regular** — `^(a(?1)?b)$` is `aⁿbⁿ`,
MEASURED matching at n = 400,000 (`out/leftrec.txt` L9). So `VM_ONLY` is
structural, it joins the `forces_*` family, and `--engine=dfa` refuses. All 26
existing rows already read `engines=vm` (P4), so **no row's engine mask
changes** and SR-8's generic post-discharge consultation (D67) does the work
with no new predicate — `lookaround_design.md` §5.1's finding, one module over.

**THREE ROW FAMILIES ARE MISSING FROM THE REGISTRY AND THIS MODULE OWNS THEM**
(MEASURED, `out/premises.txt` axis B against `out/spellings.txt` A7a):

| missing | measured legal on 10.46 | why it is missing |
|---|---|---|
| `(?10)`, `(?12)`, … and `(?-10)`, … | yes — `(a)×10(?10)` matches `"a"×11` | the rows are keyed on the **character** after `(?`, so `(?1)`…`(?9)` are nine rows and multi-digit runs have no row of their own |
| `(?+2)` … `(?+9)` | yes — `^(?+2)(a)(b)$` matches `"bab"` | `(?+1)` has a row and its eight siblings do not, while `(?-1)`…`(?-9)` all do |
| **`\g<0>`, `\g'0'`** | yes — `(a\g<0>?b)` matches `"aabb"` | §2.4: two whole-pattern spellings nobody listed |

**AND ONE COLUMN IS WRONG.** The `quant` column reads `no` on the nine
`(?1)`…`(?9)` rows and `yes` on `(?R)`, `(?0)`, `(?+1)` and every `(?-N)`.
MEASURED (`out/atomicity.txt` T5): **all twelve quantified spellings compile** —
`^(a)(?1)*$`, `^(a)(?1)+$`, `^(a)(?1)?$`, `^(a)(?1){2}$`, `^(a)(?1)*+$`,
`^(a)(?1)*?$`, `^(?<n>a)(?&n)*$`, `^(a)\g<1>*$`, `^(a)\g'1'*$`,
`^(?P<n>a)(?P>n)*$`, `^(a)(?-1)*$`, `^(a\g<0>*b)$`. The nine `no`s are wrong
and wave B fixes them.

**THE D65 `built` COLUMN.** All 26 rows read `unbuilt` today (P4, 0 rows
`built`). D65 derives `built` from the PORT's `ExtResult` at `WANT_RESULT`
and **never runs the emitter** (`syntax_dump.c:544-575`) — which is the trap
`lookaround_design.md` §11 C2-2 found: a wave that wires the port flips every
row to `built` while the emitter still `ctx_fail`s, shipping a compliance index
that lies. **So the parse hook and the lowering land in ONE wave** (§11 wave
B+C), and the split within it is the port's own tail check: at B+C
`pcrec_rcport_*` recognises the numeric and name tails and **declines the `\g`
tails at `WANT_RESULT`** until wave D wires them, so the count moves in two
honest steps.

**THE TALLY IS A DELIVERABLE**: 26 rows today → **26 + the three missing
families** after wave F. The exact number is wave F's to state in its commit,
because the multi-digit families are a design choice about row GRANULARITY
(§14 ASK 3) and not a count this document can fix.

### 8.2 The prefilter: erasure is NOT a superset

`lookaround_design.md` §5.3 could argue that dropping a lookaround yields a
superset. **That argument does not transfer**, and the counterexample is one
line: `a(?1)b` with group 1 = `x` matches `"axb"`; erasing the call gives `ab`,
which does not. Erasure gives a **different** language, not a bigger one, so
the hybrid's DFA prefilter cannot be built from the call-erased pattern.

`backrefs_design.md` §7.1's precedent is the same shape and its ruling is the
same: `select_engine.c` forces `EngineFit.prefilter` OFF when
`pcrec_has_bref`. **Wave 1 does the same for `pcrec_has_call`.**

### 8.3 …and that costs 21×–350×, MEASURED, which is why §8.4 exists

pcrec cannot compile a call today, so the cost was measured on the **inlined
equivalents**, which it can. `out/prefilter.txt`.

**EQUIVALENCE FIRST**: 15 hand-written (call, inlined) pairs across the three
idioms, each verified against libpcre2 over 28 subjects — **420 cells, 0
disagreements** — before any timing. A pair that disagreed would have been
disqualified, not fixed.

**THE STRUCTURAL SURPRISE**: 8 of the 15 inlined patterns compile to pcrec's
**pure DFA** artifact, because dropping the DEFINE wrapper leaves no capturing
group — no `RX_ENGINE`, no prefilter question, and `-fno-prefilter` on them is
byte-identically a no-op (verified by diff, not assumed). The prefilter
question is live only on the 7 rows that keep a group, which is the realistic
shape (a callee **is** a capturing group).

**THE COST**, best/median/max of three, 1 MB subject with sparse candidate
starts, default arm vs `-fno-prefilter`, answers verified equal on every cell:

| row | inlined pattern | default | `-fno-prefilter` | ratio |
|---|---|---|---|---|
| R09 | `(cat)xcat` | 28.9 µs | 7.21 ms | **249×** |
| R10 | `(cat)xcatycat` | 33.0 µs | 7.31 ms | **221×** |
| R11 | `([a-z]+)#[a-z]+` | 349 µs | 7.38 ms | **21×** |
| R12 | `(cat\|dog)!(?:cat\|dog)` | 350 µs | 8.32 ms | **24×** |
| R13 | `(?<w>cat)midcat` | 26.7 µs | 7.20 ms | **269×** |
| R14 | `(?<w>cat)midcat-cat` | 27.6 µs | 7.21 ms | **262×** |
| R15 | `(?<w>[a-z]+)#[a-z]+` | 349 µs | 7.36 ms | **21×** |

**INDEPENDENTLY SPOT-CHECKED** by this lane with a different driver on R11's
inlined pattern: 0.0096 s vs 0.1621 s over 20 passes of a 1 MB subject —
**16.9×**, the same order. The relative noise on the sub-100 µs default-arm
rows is large (up to 176% on one row, reported per row rather than smoothed),
and every ratio is ≥ 21×, so noise does not reach the conclusion.

**THE RULING, in two parts:**

**(1) WAVE 1: no prefilter for a call-bearing pattern.** One predicate, the
backrefs precedent, one line in `select_engine.c`. It is correct and it is
slow, and the number above says exactly how slow, so nobody has to guess later.

**(2) WAVE 3: the SOUND APPROXIMATION, and it is not hard.** `nfa.c`'s
`A_CALL` arm:

- **the callee is not in a cycle** → splice the callee's NFA fragment. This is
  **EXACT**, not an approximation, and it is the same decision §6.3 makes for
  the emitted code — one rule, two consumers.
- **the callee is in a cycle** → emit `Σ*`. A recursion's language is a subset
  of `Σ*`, so the result is a **superset**, which is all a prefilter needs.
- **the spliced NFA exceeds a size budget** → `Σ*` for the remaining calls.
  Still a superset, so the budget is a performance knob and never a soundness
  one.

**THE HAZARD THAT MUST BE CHECKED AND IS NOT CHECKED HERE.**
`lookaround_design.md` §5.4 found that a superset preserves the REJECTION and
the match START but **not the window END** (8 violations of 45), and
`backrefs_design.md` §11.2's planted-window hazard is the same shape. §8.3's
`Σ*` arm makes a *much* looser superset than lookaround erasure, so the window
end is at least as exposed. **Wave 3 does not land without re-running
`lookaround_measurements/probes/probe_prefilter_hazard.py`'s H1/H2/H3 against
the call population**, and §12 P-7 is the prediction.

### 8.4 The population: there is none, and that is the finding

MEASURED, `out/population.txt`. Over `tests/**/*.rxt`'s **2,161 `pattern`
lines in 121 files**:

| construct | occurrences |
|---|---|
| **CALL, every spelling** | **6** — four `\g<1>` and two `\g'1'`, **every one of them in a `perr` block** testing that the spelling correctly refuses |
| BACKREF (scale reference) | 226 |
| LOOKAROUND (scale reference) | 1 — `[M6.6.2]` has not landed |

So **no in-tree pattern uses a subroutine call**, because they all refuse. The
census machinery is shown to work by the 226. §10.1 is the population this
module must therefore CREATE, and §9.2's positive control is what makes the
zero useful: every call pattern must refuse under the pinned pre-module binary.

The census's own instrument defect is §0.3 item 9 — a naive `\g<` scan counts
`tests/backrefs/octal_class.rxt`'s `^[\g<1>]$`, where the class doorway makes
those four literal escapes, as a call.

---

## 9. The identity gate and the sabotage rows

### 9.1 The gate

Modelled on `tests/codegen/run_backref_identity.sh` and on
`lookaround_design.md` §9.1, whose shape this design adopts rather than
reinvents.

**FOUR AXES**, mirroring the `[M6.6.2]` ASK 4 ruling because the reasoning
transfers exactly:

| axis | why this module needs it |
|---|---|
| `default` | the standard first |
| `--engine=vm` | the standard second |
| **`-fno-prefilter`** | §8.2 forces the prefilter OFF for call-bearing patterns. That is a touch on `select_engine.c`, which every pattern goes through, so the axis that pins the prefilter constant is the one that localises a wrong predicate |
| **`--no-captures`** | §4.3 edits `pcrec_bref_mark`'s union, which is `--no-captures`' own machinery (P10). This is the **backrefs-precedent axis** and here it is not ceremonial: a mark-set edit that over-marks makes `--no-captures` keep slots it used to delete, and only this axis sees it |

**THE REFERENCE** is a `git archive` of `src lib cli` at a pinned pre-module
SHA, asserted to contain **no `A_CALL` anywhere in `src/`**, built with
`gcc -O0 -std=gnu11 -Wall -Wextra`. Not a `-D` knob: a knob-gated comparison
is blind under a sabotage, because call-free patterns exercise no gated path
at all (`run_backref_identity.sh` measured that blindness at 1175/1175).

**BYTE-IDENTICAL** is defined over the stdout of
`pcrec --features all -p rx <axis> -o - -- '<pattern>'` past exactly the three
D37 feature-stamp lines, with the strip asserted to have removed exactly three.

**THE POPULATION** is every `pattern` line from every `.rxt` under `tests/`,
split call-bearing vs call-free by a classifier that **fails safe toward the
call bucket** — and which must mask character classes, because
`tests/backrefs/octal_class.rxt`'s `^[\g<1>]$` is not a call (§0.3 item 9, the
census's own defect, and the classifier inherits it).

### 9.2 The positive control, which is the half that can fail

*"No subroutine call exists today, so this module changes nothing for the
existing population"* is trivially true and therefore worth nothing. The
control that can go red: **the pre-module reference must REFUSE every
call-bearing pattern** (`ctl_bad == 0 && ctl_ok == nb`), which proves the
reference is a different compiler rather than a rebuild of the same tree.

**AND THIS MODULE'S CONTROL POPULATION HAS TO BE BUILT FROM NOTHING.** §8.4
MEASURED **6** call spellings in the whole corpus and all six are `perr` rows.
So the floors are stated against the corpus §10.1 creates: **≥ 700 call-free
patterns** (the existing corpus supplies them) and **≥ 60 call-bearing**,
which is a `[DD-14]` deliverable rather than an inherited one.

**THE SECOND CONTROL, and this module HAS one where lookaround did not.**
§6.3's splice/linkage split gives a genuine in-tree equivalence: **for every
non-recursive call-bearing pattern, the SPLICE-linked artifact and the
LINKAGE-linked artifact must agree on every cell of the corpus.** Both are
this compiler, both run, and the comparison is `A == B` over answers rather
than over bytes — `lookaround_design.md` §6.3's substitution-driver shape,
which that design calls its *"real cross-lowering assurance"*. It lands with
wave 3 (a `-fno-splice-calls` switch is the axis), and until then §9.3's rows
carry the load. §11 wave 3's landing bar states it.

### 9.3 The sabotage rows

One row per claim, in `tests/mech/sabotages/`, following S105's shape
(`SAB_ID SAB_FILE SAB_SUITES SAB_DESC SAB_BEFORE SAB_AFTER SAB_COUNT`), anchors
copied from `git show HEAD:<path>` because the matrix builds from
`git archive HEAD`. Numbering starts at the highest existing id + 1, **taken at
implementation, not guessed here**, so the ids below are `S-SR1..` placeholders.

**EVERY DETECTOR CELL DECLARES ITS FEATURES — ALL OF THEM.** `std1` is a frozen
named set `{classes, modifiers}`, so a cell needs `features recursion`, and P2
MEASURED that a `(?&name)` cell needs `named-groups` **as well** or the
declaration is refused before the call is reached and the row goes green by
refusal. That is S108's masking shape, and this module's version of it has a
measurement behind it rather than a worry.

| id | the CLAIM it defends | file | `SAB_SUITES` | the sabotage | prediction |
|---|---|---|---|---|---|
| **S-SR1** | §5.3: the return RESTORES `W` | `emit_vm.c` | `harness recursion` | delete the restore loop from `RX_RETURN`'s emission | `(a\|b)(?1)` on `"ab"` reports g1=(1,2) where PCRE2 says (0,1). **The detector body must contain a group the callee WRITES** — a callee with no capture inside it leaves `W` empty and the row goes green on a broken compiler |
| **S-SR2** | §5.1/§5.5: the fail label restores `call_top` | `emit_vm.c` | `harness recursion` | delete the one added line | §5.5's drawn cell goes red — every callee with more than one alternative — **while a single-path callee stays green**, which is the pair that names the failure |
| **S-SR3** | §5.1: the call frame is NOT popped by the return | `emit_vm.c` | `harness recursion` | make `RX_RETURN` decrement `resume_depth` | the backtrack-into-a-returned-call corpus goes red; `^(?(DEFINE)(?<g>a\|ab))(?&g)c$` on `"abc"` answers nomatch where 10.46 answers (0,3) |
| **S-SR4** | §3.2: the return does NOT cut | `emit_vm.c` | `harness recursion` | add `RX_CUT` at the return | the same cell, and **the four atomic controls of §3.2 stay green**, which is what distinguishes this row from S-SR3 |
| **S-SR5** | §3.1: the callee INHERITS the caller's captures | `emit_vm.c` | `harness recursion` | zero `W`'s slots at the call site instead of parking them | `^(a)(b\1)(?2)$` on `"ababa"` goes from (0,5) to nomatch |
| **S-SR6** | §3.4(b): `W` EXCLUDES slots 0 and 1, so a `\K` in a callee survives | `callgraph.c` | `harness recursion` | let `W` include slot 0 | `^(a\Kb)(?1)$` on `"abab"` answers (0,4) where 10.46 answers (3,4). **This is the row for the design the measurements killed**, and its cell needs `features assertions,recursion` |
| **S-SR7** | §5.7: `vm_cost` charges `2·\|W\|` trail entries per call | `emit_vm.c` **+ 2nd site** | `harness recursion codegen` | charge `\|W\|` instead of `2·\|W\|` | **no answer changes** until the trail is exhausted, then `PCREC_ERR_FRAMES` on a pattern the artifact can match — S87/S95's exact shape, so the detector is a deep-call cell **and** the codegen count |
| **S-SR8** | §5.6: the depth capacity FIRES and is its own code | `emit_vm.c` | `harness recursion` | return `RX_R_FRAMES` instead of `RX_R_RECURSE` | the left-recursion cells report the wrong give-up. **Only detectable if the corpus distinguishes the codes**, so §10.2's `.rxt` needs a give-up-code expectation — which does not exist today (`tests/harness/CLAUDE.md`: the driver prints `steps`/`frames`) and §11 wave A adds |
| **S-SR9** | §2.6: `vm_nullable` answers TRUE for a nullable callee | `emit_vm.c` | `harness recursion` | return `false` from the `A_CALL` arm | **`PCREC_ERR_STEPS` or `_FRAMES`, not a hang** — every VM artifact carries a step budget by default — on `^(?(DEFINE)(?<g>a?))(?&g)*$`. The harness must score the error return as the failure |
| **S-SR10** | §4.3: a CALL TARGET joins the marked set | `atomic.c` | `harness recursion` | drop `A_CALL.target` from `pcrec_bref_mark`'s union | **the `--no-captures` axis only.** `(a)(?1)` under `--no-captures` loses group 1's slots and the call has no body. Needs the gate's fourth axis to exist |
| **S-SR11** | §4.3: the mark is TRANSITIVE | `callgraph.c` | `harness recursion` | mark only the direct target | `(a(?3))(b)((c))` under `--no-captures` — a two-hop chain — goes red while a one-hop cell stays green |
| **S-SR12** | §4.4: `revdet.c`'s `A_CALL` arm DECLINES | `revdet.c` | `harness recursion` | descend instead of declining | `vm_rev_emit`'s `default:` fires: *"internal error: bad AST node in the backward walk"*. **A hard compile error, which is the right failure** — the row asserts it is reached, not that an answer changed |
| **S-SR13** | §5.8: exactly TWO indirect jumps in a call-bearing artifact, ONE in a call-free one | `emit_vm.c` **+ 2nd site** | `codegen` | make the return a `switch` over a return-site id | **no answer changes.** The codegen count is the only detector — S109's shape, and the row that stops a third `goto *` arriving unremarked |
| **S-SR14** | §4.2: a call by name to a DUPLICATED name takes the FIRST DECLARATION | `mod_recursion.c` | `harness recursion registry` | resolve like `A_BREF` (first SET member) | §3.4(c)'s discriminator: `^(?:(?<a>x)\|q)(?<a>y)(?&a)$` on `"qyx"` goes from (0,3) to nomatch. Needs `features named-groups,recursion` and `(?J)` |
| **S-SR15** | §4.2: `\g<0>` targets the ROOT, anchors included | `mod_backrefs.c` | `harness recursion` | resolve `0` as "group 0 does not exist" | `(a\g<0>?b)` on `"aabb"` refuses instead of matching. **Carries the anchor cell too** (`^(a\g<0>?b)$` on `"aabb"` must stay nomatch), or a resolver that targets the group-1 body passes |
| **S-SR16** | §5.4: the callee's follow is SCOPED | `emit_vm.c` | `harness recursion` | delete the save-zero-restore from the call emission | **THE ANCHOR MUST EXCEED THE TWO-LINE IDIOM** — `v->fmin = 0; v->fdyn = NULL;` is the same two lines `vm_atomic` carries at `:4246-4247` and `vm_look` will carry, so a two-line `SAB_BEFORE` matches three times and `replace.py` refuses on the count. The prediction: a shared callee gets one caller's prune bound baked in and **the OTHER caller loses matches** — a two-call-site cell, which no single-call-site cell can catch |
| **S-SR17** | §8.2: the prefilter is OFF for a call-bearing pattern | `select_engine.c` | `harness recursion` | drop `&& !pcrec_has_call(root)` | wave 1: the prefilter is built from a call-erased approximation that is **not a superset**, so a matching subject is skipped. `a(?1)b` with group 1 = `x` on `"axb"` answers nomatch |

**Two need the TWO-SITE mechanism** (`tests/mech/CLAUDE.md`'s S108,
`SAB_FILE2/BEFORE2/AFTER2/COUNT2`): **S-SR7**, because the cost arm and the
emission must move together or the artifact declares a capacity it does not
use; and **S-SR13**, which is two sites by construction.

**SEVENTEEN ROWS**, and the count is stated because
`lookaround_design.md` §9.3 records its own first version disagreeing with
itself three ways. **A `recursion` mech ARM must be wired** in
`run_sabotage_matrix.sh` with SKIP-is-not-a-pass exercised in the failing
direction, as `pc3` was — without it S-SR14's `(?J)` cells and S-SR6's `\K`
cells sit outside the matrix and score UNDETECTED.

**ANCHOR DRIFT IS AN ANOMALY, NOT A FAILURE.** Every anchor above is
re-derived against the code as landed, never against this document's sketch —
the seven drifted anchors tranche A had to re-home are the precedent.

---

## 10. The D27 goal-facts list, the population, and the harness gap

### 10.1 python `re` HAS NO SUBROUTINE CALL, and that changes what D27 is

D27's whole mechanism is a **spec-first author denied `src/` and `tests/`** who
tests the promise rather than the implementation. It works because the author
has an oracle the implementation's author did not write. For every module so
far that oracle has been **two** oracles — python `re` and libpcre2 — with the
divergences enumerated so the author knows which one rules each cell.

**For this module python rules NOTHING.** MEASURED, `out/spellings.txt` A7,
all nine call spellings plus both zero spellings:

| spelling | python 3.14 `re` |
|---|---|
| `(?1)`, `(?0)`, `(?R)` | `PatternError: unknown extension` |
| `(?-1)` | `PatternError: missing flag at position 8` — python reads it as an **inline-flag group**, so the error does not even mention a subpattern |
| `(?&n)`, `(?<n>…)` | `PatternError: unknown extension ?<n` — python needs `(?P<n>…)`, so the DECLARATION fails first |
| `(?P>n)` | `PatternError: unknown extension ?P>` |
| `\g<1>`, `\g'1'`, `\g<0>`, `\g{1}` | `PatternError: bad escape \g` — `\g` is a **replacement-template** escape in python, never a pattern one |
| `\1`, `(?P=n)` | **compiles** — the reference spellings, which are `backrefs`' |

**WHAT THE BLINDED AUTHOR MUST BE TOLD, and nothing more:**

1. **libpcre2 10.46 is the ONLY oracle for every cell of this module.** Use
   `tests/backrefs/bref_oracle.py` or `tests/assertions/verify_pcre2.py`; do
   not reach for python, and do not treat python's refusal as a divergence to
   record — it is an absence, and §7's whole table is that one fact.
2. **The two reference spellings python DOES have are a trap.** `\1` and
   `(?P=n)` compile in python and mean something *different* from `\g<1>` and
   `(?P>n)`. An author who checks *"does python agree"* on a cell containing
   `\1` is checking `backrefs`, not this module. §2.1's one-cell discriminator
   (`(a|b)X` on `"ab"`) is the tool, and the author should be given it.
3. **The constructs, and that EVERY spelling SHIPS.** No refusal list to
   test against, unlike every previous module — the refusals in this territory
   belong to `conditionals` (`(?(DEFINE)`) and are not this module's.
4. **`(?R)` re-runs the whole pattern INCLUDING the anchors** (§2.4), which is
   the single most counter-intuitive fact here and the one a promise-first
   author is most likely to get wrong in the same direction the implementer
   would.
5. **Nothing about the implementation.** Not the linkage, not the call graph,
   not `W`, not the depth capacity's value.

**AND THE SINGLE-ORACLE SITUATION IS A REAL WEAKENING, SO SAY SO.** The
project's own check-design lesson is that *controls sharing a source with what
they control do not control it*. Here the corpus and the compiler both answer
to libpcre2 — which is D26's design (PCRE2 **is** the source of truth), so it
is not the failure mode; the failure mode would be a corpus derived from
pcrec's own behaviour. The mitigations are (a) the D27 author never sees
`src/`, so the corpus cannot inherit the implementation's alphabet, and (b)
§9.2's second control (SPLICE artifact vs LINKAGE artifact) compares **two of
this compiler's own lowerings** against each other, which is a check libpcre2
is not a party to at all. §14 ASK 5 asks whether that is enough.

### 10.2 `tests/recursion/` — the files

| file | what it pins |
|---|---|
| `refused.rxt` | the `conditionals` refusals this module does NOT unlock: `(?(DEFINE)`, `(?(R)`, `(?(1)` — each with its module name, D26 tier 2 |
| `gated.rxt` | the two D65 diagnostics: `requires module 'recursion'` under `std1`, `enabled but … not implemented yet` under a partial set; **and P2's cell**, `(?&n)` refusing for `named-groups` first |
| `spellings.rxt` | every call spelling, each with §2.1's `(a\|b)X` on `"ab"` discriminator beside the same pattern on `"aa"` |
| `relative.rxt` | `(?±N)` and `\g<±N>` at four distances, forward and backward, with the leading-zero and relative-zero cells |
| `whole.rxt` | `(?R)`/`(?0)`/`\g<0>`/`\g'0'`, and **the anchor cells** — `^(a(?R)?b)$` on `"aabb"` is nomatch and `^(a(?1)?b)$` is (0,4) |
| `captures.rxt` | §3.1's cells: after return, at depth 3, after a failed call, and the INHERITANCE cell `^(a)(b\1)(?2)$` on `"ababa"` with its `"abab"` control |
| `atomicity.rxt` | §3.2's isolated discriminator and **all four atomic controls** — a file whose green depends on both directions |
| `leftrec.rxt` | the give-up cells: direct, indirect, and nullable-prefix left recursion, each expecting `PCREC_ERR_RECURSE`; **and the `^(a\|(?1)a)$` on `"a"×200` cell that must MATCH** (§3.3) |
| `dupnames.rxt` | §3.4(c)'s call/reference split, including the unset-first-declaration discriminator |
| `kreset.rxt` | §3.4(b)'s three `\K` cells, `features assertions,recursion` |
| `quantified.rxt` | §2.6's twelve quantified spellings and the nullable-callee guard |
| `inlookaround.rxt` | §3.4(d)/(e): a call in a lookahead, in an atomic group, and in a fixed-width lookbehind, plus the refusal for a recursive callee in a lookbehind |
| `nocaptures.rxt` | §4.3's marked-set cells, one-hop and two-hop, run on the `--no-captures` axis |
| `d27/` | the blinded corpus, §10.1's brief |

**Every expectation is oracle-verified against libpcre2 10.46** — the corpus
generator's shape is `tests/backrefs/gen_corpus.py`'s, and it uses
`bref_oracle.py` rather than a fourth copy of the binding.

### 10.3 THE HARNESS GAP: there is no way to EXPECT a give-up

STRUCTURAL, and it blocks `leftrec.rxt` and S-SR8. `docs/testing.md`'s block
vocabulary is `pattern` / `flags` / `features` / `perr` / `m` / `n` / `ms` /
`ns` / `g` / `gp`. **None of them can say "this pattern gives up".**
`tests/harness/driver.c:189` prints `"steps"` or `"frames"` and exits 3, and
`run.sh` scores exit 3 as a **HARD harness-level failure** (`:371-378`) —
deliberately, because a give-up taken for a match was K21.

So wave A adds **one directive**:

```
gu <code>    # asserts the search GAVE UP with this typed code
             # <code> in { steps, frames, work, recurse }
```

with the driver printing the new code and `run.sh` scoring `gu` against exit 3
instead of hard-failing. That is a harness change in a module's design, which
is unusual and is called out for the panel: it is **not** optional, because
`PCREC_ERR_RECURSE` is this module's only observable for every left-recursive
pattern, and a code no test can assert is a code nobody defends. `tests/vm/
run_vm_tests.sh:112/136` already asserts the other two codes **outside** the
`.rxt` corpus, which is the precedent for the shape and the reason the
directive is worth generalising rather than special-casing.

---

## 11. The implementation brief

In order, each wave landable and testable on its own.

**WAVE A — THE GIVE-UP CODE SPACE, ALONE.** `PCREC_ERR_RECURSE (-5)`,
`PCREC_ERR_FLOOR` −4 → −5, at §5.6's eight source-of-truth sites plus the two
design records; the `%s_R_RECURSE` sentinel and its propagation through the
search entry; `tests/codegen/run_codegen_tests.sh`'s two name lists; §10.3's
`gu` directive in the harness and `docs/testing.md`. **No `A_CALL` anywhere,
no producer for the new code.** The riskiest edit in the module is the frozen
ABI, so it lands by itself where a bisect can find it.
*Landing bar: `make test` green; `make strict` clean; the `[ABI-NS]` codegen
check green with the new name; a hand-built artifact shown to carry the new
`#define`; `gu` exercised in the FAILING direction (a `gu frames` block on a
pattern that matches must FAIL) before any cell relies on it.*

**WAVE A2 — `A_CALL` AND THE WALKER ARMS, NO PRODUCER.** The kind, its D70
union payload, and the arms in all ten files of §4.4 — every one of them
declining or descending, decided and recorded per file in the commit message.
The four `default:`-carrying switches re-inspected by hand against the landed
code, since `-Wswitch` will not name them.
*Landing bar: `make strict` clean; the `-Wswitch` alarm demonstrated (add a
dummy enumerator, count, revert); the identity gate green on all four axes,
which at this wave is trivially true and is run anyway to prove the harness
works before it is needed.*

**WAVE B+C — THE PORTS, THE RESOLVER, THE CALL GRAPH AND THE LINKAGE,
TOGETHER.** They are one wave for §8.1's reason: D65 flips a row to `built`
from the PORT's answer and never runs the emitter, so a port-only wave ships a
compliance index that says `built` for constructs that cannot compile.
Deliverables: `src/parse/mod_recursion.c` with `pcrec_rcport_num` /
`_rel` / `_name`; `PendingRef.kind` and the resolver's two rules (§4.2);
`src/opt/callgraph.c` — the graph, its SCCs, the transitive mark (§4.3) and the
`W` fixpoint (§5.3); `pcrec_has_call`; the frame's two new fields, `RX_CALL`,
`RX_RETURN`, the fail label's one line, the save/restore emission, the depth
capacity and `RX_CALL_DEPTH`'s stamp; `vm_cost`'s arm; `vm_nullable`'s
fixpoint arm; `pcrec_minw`/`pcrec_maxw`'s arms.
**The `\g` tails are DECLINED at `WANT_RESULT`** so their rows stay `unbuilt`
until wave D — one branch in `pcrec_brport_g`, not a throwaway path.
*Landing bar: `spellings.rxt`, `relative.rxt`, `whole.rxt` (the `(?R)`/`(?0)`
half), `captures.rxt`, `atomicity.rxt`, `leftrec.rxt`, `quantified.rxt`,
`nocaptures.rxt` green; `--list-syntax` shows the `(?` rows `built` and the two
`\g` rows still `unbuilt`; S-SR1..S-SR6, S-SR8..S-SR12, S-SR14, S-SR16
DETECTED.*

**WAVE D — THE `\g` TAILS AND THE ZERO FAMILY.** `pcrec_brport_g`'s `<` and
`'` arms produce `PEND_CALL`; `\g<0>`/`\g'0'` resolve to the root; the decline
deleted.
*Landing bar: `spellings.rxt`'s `\g` cells and `whole.rxt`'s zero cells green;
all existing rows `built`; S-SR15 DETECTED; **the `backrefs` corpus asserted
UNCHANGED**, because this wave edits a port `backrefs` owns.*

**WAVE E — ENGINE SELECTION, THE PREFILTER PREDICATE, AND THE GATE.** §8.2's
one line in `select_engine.c`; SR-8's stamps; the four-axis identity gate with
its floors and its positive control.
*Landing bar: `inlookaround.rxt` green; the identity gate green on all four
axes with `ctl_bad == 0`; S-SR17 DETECTED; the `--engine=dfa` refusal for a
call-bearing pattern pinned.*

**WAVE F — THE REGISTRY.** §8.1's three missing row families (subject to
ASK 3's granularity ruling), the `quant` column fix on nine rows, the D65
`built` tally, SR-8 witnesses for every new row, a `recursion` mech arm in
`run_sabotage_matrix.sh` with SKIP-is-not-a-pass exercised in the failing
direction, the compliance page refreshed via the `compliance-refresh` skill.
*Landing bar: `--list-syntax`'s row count stated in the commit message; the
SR-8 capability check green with a witness for every new row; `dupnames.rxt`
and `kreset.rxt` green; S-SR13 DETECTED.*

**WAVE G — THE SPLICE LINKAGE.** §6.3's eligibility rule driven from
`callgraph.c`'s SCCs and a size budget; `nfa.c`'s `A_CALL` arm (§8.3) and the
prefilter restored for spliceable patterns; the `-fno-splice-calls` axis; §9.2's
SPLICE-vs-LINKAGE `A == B` control over the whole corpus.
*Landing bar: `A == B` over every cell of `tests/recursion/` on both linkages;
`lookaround_measurements/probes/probe_prefilter_hazard.py`'s H1/H2/H3 re-run
against the call population with its window-end result stated; the §6.2 size
and time numbers re-measured on the SHIPPED emitter and compared against the
PROTOTYPE's, with the discrepancy recorded whichever way it goes.*

**THE CLOSE** is D69-tier: the FULL sabotage matrix, the battery, the gate, the
compliance refresh and the archive.

---

## 12. What would refute this — predictions for the panel

Each is a claim this design would rather have attacked than believed.

**P-1 (the frame IS the call record).** *A separate `call_stack[]` array cannot
be made correct more cheaply than putting the return label in the resume
frame.* §5.2 derives the clobber bug in three events and **§5.9 REPRODUCES it**
— the `-DBROKEN_ARRAY` build gets three of fifty cells wrong, one of them a
FALSE MATCH, and agrees on the other 47. **Refute** by exhibiting a
separate-array design that survives *call A → A returns → call B → B fails →
backtrack into A's callee → A returns again* without a second undo log or a
per-frame high-water mark; `prototype/callproto.c` is where such a design would
be built and run against the same 50 cells. The sharpest surviving attack is
on the MEMORY claim rather than the correctness one: ordinary frames already
pay for `call_top` and `call_mark`, so the array version's saving is smaller
than it looks, and if a corrected array design existed the row would have to be
re-argued on simplicity alone.

**P-2 (the restore set).** *`W` — `g`'s own slots plus the transitive
capture-slot write set, excluding slots 0 and 1 — is exactly the right restore
set.* **This design's first draft got it wrong** (it omitted `g`'s own slots)
and §5.9's prototype is what found it, by reporting `g1 = (1,4)` where libpcre2
says `(0,4)` — a wrong span on a correct match, which only a `g` expectation
line catches. **Refute** by
exhibiting a non-capture slot whose value must be restored by a return, or a
capture slot whose value must NOT be. `\K` is the second kind and §3.4(b)
measured it; the candidates for the first kind are the counter slots
`[ENG-BREP counter-K]` allocates and `SLOT_LOOK_MARK`/`_POS`. **The prediction
is that none of them needs restoring** because each is re-initialised at its own
entry label on every entry — but that is an inspection of code
`[M6.6.2]` has not landed yet, so it is ARGUED and this is where it is
recorded.

**P-3 (the depth capacity is enough).** *Every shape PCRE2 answers `rc −52` on
is non-terminating, so pcrec's depth capacity catches all of them, and pcrec's
answers agree with PCRE2's on every terminating shape up to the stamped depth.*
**Refute** by exhibiting a pattern PCRE2 answers −52 on that pcrec's depth
capacity does **not** catch (it would have to be a recursion that neither
terminates nor deepens), or a pattern that needs more depth than the stamped
value and that a user would reasonably write. §3.3 pinned that
`^(a(?1)?b)$` needs depth ≈ subject and PCRE2 satisfies it from the heap, so
**the second half of this prediction is the weak one** and §14 ASK 2 asks what
the default should be.

**P-4 (no same-position guard).** *Building the O(1) per-callee entry-position
guard would be a miscompile, not a conservative approximation.* Already
**refuted in the guard's favour** — §3.3's 199-deep matching cell is the
counterexample and it is measured. Recorded so nobody re-proposes it: the
attack that would revive it is a demonstration that PCRE2's own guard has the
same shape and that this lane's cell is somehow special, which the `n + 2`
give-up depths make unlikely.

**P-5 (the static `W` beats the runtime trail walk).** *Saving `|W|` values at
entry costs less than walking the callee's trail at return.* **Refute** by
measuring a population where `|W|` is large and the callee writes few slots —
a called group containing twenty capture groups of which one branch writes two.
The static version pays 40 writes; the walk pays 4. **The experiment is a
prototype in `gen_linkage.py`'s idiom with both restores**, and it is not run
here.

**P-6 (the lookaround body must not be a call).** *`k = 1` is the whole
argument, and it is measured.* **Refute** by finding a lookaround shape with
more than one use site — which `lookaround_design.md` §6.4(3) says cannot
happen because `vm_label()` allocates per emission — or by showing the emitted
size difference matters more than the 10–12% time difference at `k = 1`.

**P-7 (the wave-G prefilter is sound).** *Splicing a non-recursive callee's NFA
fragment is exact and `Σ*` for a recursive one is a superset, so the prefilter
is sound.* **Refute** by exhibiting a call-bearing pattern whose true leftmost
match START differs from the approximated pattern's — which is
`lookaround_design.md` §5.4's own finding one construct over (**0 violations on
the start, 8 of 45 on the window END**), and `Σ*` is a far looser superset than
lookaround erasure. **The prediction is that the window end is violated MORE
often here, not less**, and §11 wave G refuses to land without the re-run.

**P-8 (one wave, not two, for the port and the emitter).** *A port-only wave
would flip six rows to `built` while the emitter still fails.* **Refute** by
finding a way to make D65's `WANT_RESULT` answer "not yet" without a throwaway
refusal path — `lookaround_design.md` §11's C2-2 concluded there is none, and
this design consumes that conclusion rather than re-deriving it.

**P-9 (the second `goto *` is the last one).** *A call-bearing artifact has
exactly two indirect jumps and a call-free one exactly one.* **Refute** by
naming a chartered construct that needs a third — `[DD-11]`'s insertions
splice, `[ENG-CUT]` cuts, `callouts` calls a function pointer (**which is an
indirect CALL, not an indirect jump, and S-SR13's count must be written to
distinguish them or the row fires when `callouts` lands**).

**P-10 (PCRE2's cost shape).** *The factor of 2 §3.2 measures is one extra
backtrack per call ACTIVATION, which is what pcrec's non-popping call frame
also costs.* **The RATIO is MEASURED (2.0 over 1…8 call sites); the
ATTRIBUTION is ARGUED**, and this row exists because the two are easy to
conflate. **Refute** by counting activations with a callout and showing the
excess is not one per activation — or by finding a shape where PCRE2's ratio
diverges from pcrec's emitted step count, the obvious candidate being a callee
`src/opt/possessify.c` possessifies, where pcrec removes choice points PCRE2
keeps.

**P-11 (the harness directive is required).** *`PCREC_ERR_RECURSE` cannot be
asserted by any existing `.rxt` expectation.* **Refute** by finding a spelling
in `docs/testing.md` that can — the vocabulary is `perr`/`m`/`n`/`ms`/`ns`/`g`/
`gp` and `perr` is COMPILE-time, so the claim rests on a give-up being a
run-time outcome. If a `--step-budget`-style flag could make a left-recursive
pattern refuse at COMPILE time the directive would be unnecessary, and it
cannot: §3.3 measured that PCRE2 compiles them all and this design follows.

---

## 13. Explicitly out of scope

- **`(?(DEFINE)…)` and every other conditional.** Module `conditionals`,
  one registry row, no producer. §2.5 measures a DEFINE-less substitute that
  agrees on 11/11 subjects, so nothing here is blocked by it.
- **`(?(R)`, `(?(R1)`, `(?(R&name)` — the RECURSION CONDITIONS.** They are the
  natural companion of this module and they are `conditionals`' doorway, not
  this one's. `registry.c:57` already notes that `(?(R)` is *"a recursion
  condition or a NAMED-GROUP condition depending on"* context. **This module
  unlocks none of them** and §8.1's tally must not imply otherwise.
- **Reproducing `rc −52` cell for cell.** §3.3 RULED: the depth capacity is
  the guard, the code is pcrec's own, and the exact predicate 10.46 uses was
  not pinned by black-box probing.
- **A compile-time left-recursion refusal.** PCRE2 has none (§3.3, measured),
  and `^(a|(?1)a)$` proves a static refusal would lose matches.
- **The DFA.** A call-bearing pattern is `VM_ONLY` structurally. `[ENG-LOOK]`'s
  product construction has no analogue here — the language is not regular.
- **The prefilter, in wave 1.** §8.3 designs the sound construction and
  wave G builds it. The 21×–350× number is stated so the deferral is a decision
  rather than an omission.
- **The `[DD-11]` environment model.** §7 states the interface and designs none
  of it.
- **Streaming.** §5.8: a call stack of label addresses is the second consumer of
  APPROACH §6's A-4/A-5 constraint. `[M3.0]`'s design gate owns it; cross-noted
  there.
- **`(*ACCEPT)`-family verbs inside a callee.** Module `verbs` has no producer.
  PCRE2 gives `(*ACCEPT)` a special meaning inside a recursion; nothing here
  anticipates it, and the day `verbs` gains a producer this section is where it
  will be found.
- **Tail-call or self-recursion optimisation.** A recursive call whose
  continuation is empty could reuse its caller's frame. Not designed, not
  measured, and the K19/K22 lesson says an optimisation without a measurement
  is a code path without a customer.
- **A user-facing recursion-depth OPTION.** `RX_CALL_DEPTH` is a stamped
  artifact constant like `RX_RESUME_FRAMES`. Making it a `pcrec_options` field
  is D18/`[OS-0]` territory and needs a caller who asked.

---

## 14. ASKs for Frank

**ASK 1 — keep the new give-up code, now that its premise is gone?** The plan
row reserves *"a NEW typed give-up code below D49's ERR_FLOOR"* for *"a bounded
DEPTH capacity"* on *"an explicit call stack"*. §5.2 shows the separate call
stack is wrong and §5.1 puts the call record in the resume frame — so calls
consume ORDINARY FRAMES and the capacity failure is already
`PCREC_ERR_FRAMES`. `PCREC_ERR_RECURSE` is now a **second counter over the same
array**, bought for diagnosis: a caller that gets `_RECURSE` knows to raise a
recursion bound, one that gets `_FRAMES` does not know which bound to raise.
It costs an increment, a decrement, a compare, a per-frame `call_mark`, and an
`ERR_FLOOR` move across eight source-of-truth sites (§5.6).
*Recommendation: KEEP IT.* The move is cheap now and impossible after v1, D49's
own text says a pre-release renumber *"costs a renumber and nothing else"*, and
a give-up whose type does not name its cause is the failure mode D42.3's
collapse was superseded for. But the row's justification changed under it, so
it is asked rather than assumed.

**ASK 2 — what is `RX_CALL_DEPTH`'s default?** §3.3 MEASURED that PCRE2
satisfies `^(a(?1)?b)$` on an 800 KB subject — depth ≈ 400,000 — **from the
heap**, and that pcrec's array is fixed (P12: `RX_RESUME_FRAMES` defaults to
2048). A recursive pattern's depth is data-dependent by nature, so any fixed
number refuses some subject PCRE2 matches. Three shapes:
(a) a **small** default (say 256) — cheap, and a nested-structure parser gives
up on deep input;
(b) **derive it from `RX_RESUME_FRAMES`** — calls already consume frames, so
the depth ceiling is at most the frame ceiling and a separate number is
redundant, which is ASK 1's answer arriving from the other side;
(c) a **large** default with the memory cost stamped, following D49.2's
work-budget reasoning (*"too low refuses ordinary large-subject matches on the
shipped path, which is the worse error"*).
*Recommendation: (c), with a bring-up value calibrated at implementation the
way the step budget's 500M and the work budget's 10⁹ were, and the honest
ceiling stamped so a caller can read it.*

**ASK 3 — how granular are the registry rows for multi-digit calls?** §8.1
MEASURED three missing families: `(?10)`+, `(?-10)`+, `(?+2)`…`(?+9)`, and
`\g<0>`/`\g'0'`. The registry is keyed on the character after `(?`, so
`(?1)`…`(?9)` are nine rows and the two-digit forms have none — while
`(?-1)`…`(?-9)` are nine rows and `(?+1)` is one, an asymmetry nobody chose.
Options: (a) add the eight missing `(?+N)` rows and one row each for the
multi-digit families, keeping the per-digit shape; (b) **collapse** each family
to ONE row with a syntax like `(?N)`, `(?+N)`, `(?-N)`, deleting seventeen rows;
(c) leave the surface as it is and fix only the `quant` column.
*Recommendation: (b).* Nineteen rows for one construct is a compliance index
that reports the doorway's implementation rather than PCRE2's surface, and D65's
`built` column plus SR-8's witnesses make each row a real obligation. (b) is a
change to `backrefs`-adjacent rows too and is therefore Frank's call, not a
lane's.

**ASK 4 — should the `conditionals` refusal for `(?(DEFINE)` point at the
substitute?** §2.5 MEASURED that `^(?!)(?<w>X)|^BODY$` reproduces DEFINE's
semantics on 11/11 subjects. A user's library pattern will refuse with
*"module 'conditionals' is enabled but `(?(...)` is not implemented yet"*, which
is correct (D26 tier 2) and unhelpful. Options: (a) leave it — D26 tier 3 says
wording is not an obligation; (b) add a one-line hint to that specific
diagnostic; (c) document the substitute in `docs/pcre2_compliance.md` and leave
the diagnostic alone.
*Recommendation: (c).* A hint in a diagnostic is a second place the substitute
has to stay correct, and the compliance page is where a user with a refusing
pattern is already sent.

**ASK 5 — is a SINGLE-ORACLE D27 corpus acceptable for this module?** §10.1
MEASURED that python `re` has no subroutine call of any spelling, so for the
first time the blinded author has one oracle instead of two. The project's own
check-design lesson is about controls sharing a source with what they control;
here the shared source is **libpcre2**, which D26 makes the source of truth, so
it is the design rather than the defect — but the author's oracle and the
implementer's oracle are now the same document. Mitigations designed in: the
author still cannot see `src/`, and §9.2's second control compares two of
pcrec's OWN lowerings (SPLICE vs LINKAGE) against each other, which libpcre2 is
not a party to.
*Recommendation: PROCEED, with the SPLICE-vs-LINKAGE control promoted from
"nice" to a wave-G landing bar (§11 does that), and with the D27 brief saying
explicitly that python's refusal is an ABSENCE and not a divergence to record —
because an author told "compare both oracles" will otherwise record nine
divergences that are one fact.*

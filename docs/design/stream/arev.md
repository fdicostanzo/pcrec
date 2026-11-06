# A-REV: one reverse automaton kind with declared exits, hostable in a VM body

**Status: PROPOSED rev 0** (lane arevdesign, opus, 2026-11-05; plan row [STREAM], roadmap area
A-REV). Design only: no build go, no step built. A critic round follows. Anchors are at **main
7cebea04e** (abi 95; lane/p1build is MERGED there, dc6a40dfb, D184). Anchors move with code:
re-grep the symbol. The manifesto is not edited by this note; `roadmap.md`'s A-REV section is the
area plan and points here.

**The decision, in one paragraph.** Four reverse walks exist on main. Three of them (RECOVER's
reverse pass, the `rev-end` walk, the landmark walk) ALREADY share one renderer,
`emit_reverse_block` → `emit_scan_loop` over a `DfaForm`; what they do not share is how a walk is
DESCRIBED: the machine is a named `Job` field per client, the floor and the seed's context are
strings frozen into one `static const DfaDir` per client, the names are RECOVER's spellings, and the
exit is always "the smallest accepting position" with every other exit hand-written by the caller.
The fourth (revdet) is a reverse walk of a different representation, a reversed AST rendered as VM
records, already hosted INSIDE a VM body. The kind this note proposes is therefore not a new
renderer: it is ONE OPERAND RECORD for every reverse walk (machine per site, seed, floor, exit,
tags, names, host), filled by all four, rendered by the shared table renderer or by revdet's
structural renderer as a declared REPRESENTATION, and given one new host, a VM record kind, whose
first client is variable lookbehind's held `reverse-dfa` row. Two walk behaviours carry all five of
the manifesto's exits (§2.2). The lookbehind client is sound against the atomic counter-example
because the exit is admitted on the machine's recorded exactness, never on the kind: a superset
machine only GATES (§3.1).

## 0. Goals

Ranked; the higher goal wins a conflict.

1. **G1 Answers never move (every caller).** No step changes a match, a group or a give-up class
   except where a row's evidence says so. Measurable: each byte-identical step moves 0 bytes over
   the corpus (the comparator, `scripts/emit_sweep.py`, movers = 0); the one byte-moving step
   (lookbehind) is answer-identical to the `range` row under a libpcre2 10.46 differential, 0
   differences outside D142's ruled class.
2. **G2 One mechanism (maintainers; the general-mechanisms rule).** Every reverse walk is described
   by one record and rendered by one body per representation. Measurable: ratchet rows R28 (new,
   §4.3), R03 (restated) and R10 fall to 0 over the steps, no row rises; a new reverse walk adds an
   INSTANCE, never a §5 member.
3. **G3 Cross-engine pieces where needed (the owner's 2026-11-05 payoff).** A deterministic reverse
   walk can run inside a VM body between choice points, its result handed to a VM forward run.
   Measurable: one VM-hosted instance (the lookbehind gate) answer-identical to its fallback.
4. **G4 No blindness at the seam (F4).** The exit, the hand it gives and the fact that admitted it
   are declared operands a reader and a test can see. Measurable: every instance prints its
   operands in `--emit-ir` / the trace; each exit row has a sabotage witness.
5. **G5 Speed is a gate, not the case.** No regime slower beyond noise (D186's choice bar) for the
   one byte-moving step; the byte-identical steps carry no speed claim.

**Non-goals.** A reverse VM (owner, 2026-11-05). Tagged-capture DFA tables (TDFA) for revdet's
groups (§5, HELD). Unbounded lookbehind (the HELD row review r3-F16 files; §5). Building any step
ahead of its trigger (D77). Choosing between the open "VM base" frame and today's two-engine
reading (§6 uses it as a lens only).

## 1. Today, at main 7cebea04e

**Premise test (the cited symbols).** All exist on main: `src/opt/revdet.c`; `vm_revdet_rep`
(src/gen/emit_vm.c:5705) and `vm_rev_emit` (:5521) with its record `Rev` (:5500); `VK_CONSUME_BACK`
(src/gen/vm_stmt.h:59, renderer `vm_r_consume_back`, src/gen/vm_stmt.c:403);
`dfa_member_machines` (src/gen/emit_dfa.c:4916, FOUR machines now: F, R, A, ML); `struct DfaDir`
(:5787); `dfa_dir_reverse` (:9360), `dfa_dir_landmark` (:9442), `dfa_dir_lmverify` (:9460);
`emit_scan_loop` (:13244); `emit_reverse_block` (:13409); `emit_landmark_walk` (:14398);
`lmwalk_build` (src/core/compile.c:547) and `revend_build_one` (:454); `Job.lmnfa`/`Job.lmdfa`;
`CAND_ML` (src/core/internal.h:9285); `Nfa.erased` and `NFA_ERASED_*` (internal.h, the enum after
`Nfa`); `lmwalk_conj[]` (src/gen/lmwalk.c:276). One cited name does not exist:
`rx_reverse_accepts_class` (vlookbehind.md §3); the accessor is emitted per machine as
`<p>_<dir>_accepts_class` (emit_dfa.c, the accessor block). The roadmap's "p1build" anchors are now
main's.

| walk | machine (built by) | seed | floor | exit today | finisher | host |
|---|---|---|---|---|---|---|
| W1 RECOVER's reverse pass (`emit_unanchored`, the `CRA_REVERSE` arm) | `Job.rdfa`, mandatory | `match_end_position` = the forward accept | `search_from` (`dfa_dir_reverse.at_bound`), context byte below it read (S74) | farthest: smallest accepting position into `match_start_position`; D164 B3 adds a TAGGED accept (`DfaForm.accv`, a distance set) on lowered machines | report SPAN | inline in the DFA search body |
| W2 `rev-end` (`emit_rev_end` :14229, its one-seed and tagged forms) | `Job.rdfa`, or the lowered `Job.xrdfa` (`revend_build_marked`) | `n`, then `n − 1` before a final newline (speculative, may be dead: `dead_skip "continue;"`) | `search_from` | farthest per seed; the caller keeps the min over seeds and a tie bit | FINISH: report, or `verify-at` / `search-from` on a tie | inline |
| W3 the landmark walk (`emit_landmark_walk`) | `Job.lmdfa` from the cut P·L (`lmwalk_build`, optional, own cap; built only where `lmnfa.erased == 0`) | `landmark_position + 1` per LMHIT hit | `search_from` (`dfa_dir_landmark`, the reverse strings under another name) | farthest; dead → next hit | anchored A inline (`dfa_dir_lmverify`), or LOWER: relocate to `composite` | inline |
| W4 revdet (`vm_revdet_rep`, `vm_rev_emit`) | the REVERSED body AST (`Ast.u.rep.revbody`, set by `revdet.c` when the forward AND reverse unique-iteration checks hold) | the committed boundary (`<p>_rv<i>_cursor = scan_position`) | the loop's entry slot (`slot_values[se]`) | the ONE predecessor boundary (unique by the reverse check), plus group spans witnessed on the way (`*_revdet_group_span/seen`); the host loops step by step until all groups are seen or the floor | the VM body continues (the commit label publishes the recovered captures; the greedy retreat frame `VPOS_REVDET_PREV` reads the first step's landing) | INSIDE the VM body, as records (`VK_CONSUME_BACK`, `VK_BRANCH`, `VK_LSET`) |

**What they already share.** W1-W3: one renderer body (`emit_reverse_block`, which only sets the
form's `lbl` and `dead` and calls `emit_scan_loop`), one direction family (`DfaDir`), one optional
machine builder shape (`revend_build_one`: own cap, overflow record and subset budget restored;
`lmwalk_build` is its second caller). This is roadmap r1 U3's "one walk emitter", built in p1build.

**What they do not share (the parallel parts this note removes).**
- **Machine identity is a `Job` field per client** (`rdfa`, `xrdfa`, `lmdfa`) and a fixed-size
  member array (`dfa_member_machines`' `out[4]`, one `CAND_M*` bit each). A lookbehind needs one
  machine per variable branch per site: there is no place to put it.
- **The floor and the seed context are frozen strings.** `dfa_dir_landmark` repeats
  `dfa_dir_reverse` "character for character under its own name" (its own comment) to get a new
  state-variable name and indentation. A floor other than `search_from` (a lookbehind's is the
  subject start, review r3-WD5) needs a third copy.
- **Names are RECOVER's** (`match_end_position`, `match_start_position`, `rewind_position`):
  `emit_reverse_block`'s comment says the one caller needing others (rev-inner, D151) is filed. W3
  works only by opening its own C block.
- **The exit is implicit.** Every walk records the smallest accept; "first accept", "every accept
  in order", "existence" and "the tag at the accept" are written by callers, or not at all.
- **W4 has its own operand record**, `Rev` (cursor, floor, fail label, the group sinks, the
  instance number), describing the same five things in a VM spelling.

## 2. The kind

### 2.1 The operand record (`RevWalk`, a name for the review, not a ruling)

One record per walk INSTANCE. Every field is a fact the planner states; the renderer reads them.

| field | meaning | W1 | W2 | W3 | W4 | L (lookbehind) |
|---|---|---|---|---|---|---|
| `machine` | a reference to a built machine in a per-site table (§2.4), or the reversed AST | R | R or XR | ML | revbody | one per variable branch |
| `repr` | `table` (subset-built DFA, `DfaRepr` rows inside) or `structural` (deterministic Glushkov of a reversed AST, one VM state per node) | table | table | table | structural | table |
| `seed` | the position expression the walk starts at, and its right context (`DfaDir.seed_cond`/`seed_byte` today) | forward accept | `n` / `n − 1` | hit + 1 | cursor slot | VM cursor |
| `floor` | the lowest position consumed; the byte below it is read as context (S74's rule) | `search_from` | `search_from` | `search_from` | entry slot | `max(0, cursor − W)`, W the branch's widest byte width (§3.1) |
| `exit` | `farthest` (run to the floor or death, record the smallest accept) or `first` (stop at the first accept met) | farthest | farthest | farthest | first (unique) | per exit row (§3.1) |
| `tags` | none, `distance` (D164 B3's accept cell) or `groups` (the group positions a structural walk witnesses) | none / distance | none / distance | none | groups | none |
| `dead` | the hand on a dead seed or no accept: the NO-MATCH hand's action | NULL (seed is live) | `continue;` | next hit | the walk's fail label | the exit row's decided branch |
| `names` | the instance stem: state, position and result variable names, table names | `reverse` | `revend` | `landmark` | `rv<i>` | `lb<site>_<branch>` |
| `host` | `inline` (in an emitted function) or `vm-record` (a VM body record, §2.3) | inline | inline | inline | vm-record | vm-record |
| `charge` | the work charge per walk on a VM host (none inline) | — | — | — | per step, as today (`vm_charge`) | §3.1 |

The record is the seam document of principle 9: written as text and read back by another process,
it says which machine, from where, down to where, what comes back and in what type. Nothing in it
names a method of the kit (D157): the scan edges inside a table machine stay the kit's (D161 add.
17: the reverse DFA is the scaffolding, scan edges the optimization inside it).

### 2.2 The exits: two walk behaviours, five meanings

The manifesto names five automaton exits. A reverse walk has exactly two BEHAVIOURS; the five are
what the consumer does with the result, which is the TYPE of the hand at the seam.

| manifesto exit | walk behaviour | hand (seam type) | who needs it |
|---|---|---|---|
| commit to one end | `farthest`; or `first` where the machine has at most one accept per walk (W4: the reversed body is prefix-free, revdet's (U2)) | exact point | W1, W2, W3, W4 |
| enumerate ends in preference order | the HOST's loop over `farthest` with a moving floor (next candidate = the farthest accept above the last one tried) or a moving seed (the next hit, the next seed, the predecessor boundary) | candidate, re-enterable | L (non-atomic retry, superset confirm), [LANDWALK-ALLACC], W2's seeds, W3's hits, W4's iteration chain |
| act as a gate | `first`, result used as a filter (no accept decides; an accept passes to the finisher) | candidate or no match | L on a superset machine |
| test existence | `first`, result used as the answer | exact yes / no | L on an exact, capture-free branch |
| report a tagged end | either behaviour with `tags` | exact point plus the tag value | W1/W2 under D164 B3 (`distance`), W4 (`groups`) |

So "enumerate" needs no third walk behaviour: farthest-first enumeration is "farthest above t",
which is `farthest` with `floor = t + 1`, O(width) per retry and stateless (the re-walk
vlookbehind.md §3 recommends). A single-pass enumerator (a bit set of accepts) is a later
representation of the same exit, built only on a measurement ([LANDWALK-ALLACC]'s trigger). No
manifesto change is needed; an optional clarifying sentence is in the report.

### 2.3 Hosting inside a VM body

The VM body is written only by typed records (D182) and `VmKind` has no automaton kind. Two hosts
exist today and the kind keeps both:

- **inline** (W1-W3): the walk's text sits in the enclosing search function; its names are
  function-local. Byte identity requires this placement for W1-W3.
- **vm-record** (W4 today, structurally): the walk is records in the body.

The new combination the lookbehind needs is a TABLE machine in a VM body. Proposal: one new record
kind, `VK_AUTO` (name for the review), operands = one `RevWalk` plus its targets (the decided and
the passed hand's labels, or a result slot). Its renderer emits a call to a per-instance `static`
function defined at file scope whose body is `emit_reverse_block` over the instance's form, tables
and accessors at file scope under the instance stem. Reasons, in order:

1. **The function boundary IS the naming scope.** The renderer's local names stay RECOVER's inside
   each function, so G3 of vlookbehind §4 (names per instance) costs a function stem and a table
   stem, not a re-spelling of every `DfaDir` string. This is also why W1-W3 need no change of text.
2. **It is the hybrid's precedent.** The VM hybrid already emits DFA text with `static` storage as a
   separate part and calls it from the search loop (`pcrec_emit_dfa_engine`, emit_vm.c's entry
   shape `.hybrid`); this moves the call site from the loop into the body.
3. **It suits [VMREC] (c)'s analysis.** A call with DECLARED EFFECTS (reads `subject[floor − 1 ..
   seed]`, writes one result, transfers control only to its targets, never touches frames or the
   trail) is the r9 ruling's shape for kit windows; the analysis need not read DFA text.

Placement (inline or function) is decided by the host, a fact, not a priced choice; emit stays a
pure function of the plan (roadmap §0a). gcc inlines a one-caller `static` function, so no speed
claim rests on the call.

**The finisher contract.** The kind hands a typed position; the finisher is the host's, chosen by a
FINISH row (D156), never by the kind: report (W1), `verify-at` with the anchored machine (W3, W2
on a tie), `search-from` relocate (W2, W3), the VM body continuing (W4), and, new, a VM forward run
from the hand's position with the end pinned at the cursor (L: vlookbehind §5.1's per-candidate
step, the body run forward and kept only if it ends at the cursor). That last finisher is the
"VM forward run for captures" of the owner's example; it is the same shape [LANDWALK-VM] needs at
the search-loop level.

### 2.4 The machine per site

`Job.rdfa`, `Job.xrdfa`, `Job.lmdfa` become entries of one per-artifact machine table keyed by
(site, role), requested by the plan and built by one optional-machine builder of
`revend_build_one`'s shape (own cap; overflow and subset budget restored; an overflow is the row's
decline, never a refusal). The BUILD REQUEST is part of the operand: `exact` or `collapsed`
(`b->collapse`, src/ir/nfa.c's count-collapse arm: `X{m,n}` → `X{min(m,1),}`, recording
`NFA_ERASED_COUNT`). The realized `Nfa.erased` is recorded with the entry, because the exit rows
read it (§3.1). `dfa_member_machines` reads the table instead of four bits. This is H-FLAGS's end
state ("the plan requests machines, one builder"; R14) applied to reverse machines; the step that
lands it declares H-FLAGS's extension shape for machines.

### 2.5 The generalizations, against vlookbehind §4's checklist

| vlbdesign item | where it lands here | status |
|---|---|---|
| G1 machine per site | §2.4 | proposed |
| G2 floor and seed as operands | §2.1 `seed`, `floor` | proposed |
| G3 names per instance | §2.1 `names`; free inside a function host (§2.3 reason 1) | proposed |
| G4 the exits | §2.2: two behaviours, five meanings | proposed |
| G5 hosting in a VM body | §2.3 `VK_AUTO` | proposed |
| G6 the finisher on the VM route | §2.3 finisher contract (built by vlookbehind stage 1's range loop) | proposed |
| **G7 (new) the build request** | exact vs collapsed is an operand; exactness is read after the build | proposed |
| **G8 (new) representation** | `table` or `structural`; W4 is a reverse walk of the second representation | proposed |
| **G9 (new) tags** | `distance` (D164 B3) and `groups` (W4) are two tag kinds of one exit | named, not unified (two members) |
| **G10 (new) the work charge on a VM host** | a declared operand; the give-up direction is [GIVEUP-DIFF]'s | proposed |
| **G11 (new) the context rule at the floor** | the byte below the floor is read (S74); a floor that is a WIDTH bound and not a semantic one is sound only because accepts below it are lengths no branch can have | proposed, read from code, not executed |

## 3. Clients, in order

### 3.1 First client: lookbehind's `reverse-dfa` candidate-source row

The row (vlookbehind.md §5.4) admits on: the branch varies (`lo < hi`); its reverse machine builds
under its own cap; no backreference or variable in the body; the host can run it (G5, §2.3). It
becomes three EXIT ROWS, first match, each a D186 choice row with its own evidence:

| order | exit row | applies when | walk | hand | finisher |
|---|---|---|---|---|---|
| 1 | `exist` | machine built `exact` and `erased == 0`; the branch has no capturing group | `first` | yes / no, the answer for either polarity | none |
| 2 | `gate` | otherwise (a superset machine, or captures) | `first` | no accept: decided (positive branch fails, negative branch cannot match); an accept: passed | the `range` row's loop, unchanged |
| 3 | `commit` (HELD) | as `gate`, and a measurement shows the gate passes often while viable lengths are few | `farthest` with a moving floor | candidates farthest first | §5.1's per-candidate step |

**When D is only a FILTER and when it is the answer.** It is the answer only under row 1: an
exact machine accepts at s exactly when `subject[s .. cursor)` is in the branch's language with its
context, which is when the forward body run from s with the end-check succeeds, and with no group
nothing else is observable. Everywhere else it is a filter. **The atomic counter-example** (§2 of
vlookbehind.md, MEASURED there): `(?<=(?>a|ab)b)x` on `abbx` is nomatch in libpcre2, while the
machine (atomicity erased, `NFA_ERASED_ATOMIC`) accepts at 0; as an answer it would be a false
match, and the negative form `(?<!(?>a|ab)b)x` would lose its match (3,4). Under the rows above the
erasure makes row 1 decline; row 2's accept passes to `range`, which answers. A superset machine's
NO accept is always sound to act on (no accept in the superset, none in the truth). **The STOP RULE
does not fire:** a VM-hosted automaton is sound against the counter-example because exactness is a
conjunct of the exit row, read from the recorded fact, and not of the kind.

**The floor.** `max(0, cursor − W)`, W = the branch's widest length in bytes (hi characters times
the encoding's widest character). Not `search_from`: the body may lie before the start offset
(vlookbehind W7, review WD5). Accepts below `cursor − W` are lengths no branch has, so cutting them
is sound even on a collapsed (unbounded) superset machine; the context byte below the floor is read
as on every reverse walk (S74).

**The work charge.** `first` stops at the first accept or death within W bytes; the charge is one
unit per walk, declared, and the gate REMOVES range-loop body runs, so the row is a one-way give-up
change: [GIVEUP-DIFF] is its prerequisite (vlookbehind §5.4).

**Order inside one lookbehind.** Per-branch machines, branches in written order (branch order beats
length: one untagged machine for all branches is WRONG, `(?<=(a)|(aa))c` on `aac`). A tagged
single machine is a later representation ([LANDWALK-ALLACC]'s multi-branch form).

- **Byte identity:** NONE for artifacts that take a row (new emission, an abi event at the landing
  number, readers by grep); every other artifact identical. Stage 1's range artifacts are the base.
- **What it deletes:** nothing on main. Its ratchet movement is ZERO by construction: it is an
  instance of the kind (the shared renderer through `VK_AUTO`), not a third hand-written walk,
  which is the whole reason it waits for §4's S1 (vlookbehind §4 "why not now").
- **Witnesses** (each red under its sabotage in the default build, where the row admits; in the
  row's deny build the cell is the `range` row's and stage 1's W-rows are its control): WD1 (`exist` admitted
  on an erased machine: `(?<=(?>a|ab)b)x` on `abbx` nomatch; `(?<!(?>a|ab)b)x` on `abbx` (3,4));
  WD2 (one untagged machine: `(?<=(a)|(aa))c` on `aac`, g1=(1,2)); WD5 (floor at `search_from`:
  `(?<=a{1,2})b` on `aab` from 2, (2,3), re-measured this lane); WD6 (context at the floor ignored:
  `(?<=\ba{1,2})x` on `baax` nomatch, review F11: the ` aax` cell cannot fail); WD7 (new: the gate
  treats an accept as the answer: any capture-free superset cell, e.g. WD1's positive one, with row
  1 forced off). WD3/WD4 (nearest instead of farthest; farthest only on the non-atomic form) belong
  to row 3 and are owed only when it is built.

### 3.2 Second: revdet (W4)

- **The fit.** revdet's walk is a deterministic reverse automaton: `revdet.c`'s REVERSE check is
  the forward unique-iteration predicate on the reversed body, (U1) one-unambiguous makes its
  Glushkov automaton deterministic, (U2) prefix-free gives at most one accept per walk. `vm_rev_emit`
  renders that automaton with one VM state per position, which is the `structural` representation.
  Its exit is `first` with `groups` tags; its iteration chain is the host's moving-seed loop.
- **The step.** `Rev` becomes the shared `RevWalk` (cursor = `seed`, floor, fail label = `dead`,
  the group sinks = `tags`, the loop number = `names`); `vm_rev_emit` becomes the kind's structural
  renderer, unchanged in its text. `revdet.c` STAYS: it is the representation row's admission
  (forward and reverse unique iteration), not a walk.
- **Byte identity:** expected 0 movers (the records are the same; only their describing struct
  changes).
- **What it deletes:** the private record `Rev` (R03, restated in §4.3), a parallel description of
  the same five operands. It does NOT delete a renderer: the structural renderer stays beside the
  table one as a representation row. Whether that counts R03 to 0 is owner question 2.
- **Witnesses (red under the sabotage in BOTH the base build and the step's build, the anchor
  re-aimed):** S52 (the capture walk's first-seen guard: `((a)|b){0,4}c` on "abac"), S50 (no
  reverse check), S51 (no iteration cut), S94, S160 (tests/mech/sabotages/).

### 3.3 Third: the landmark walk (W3), and with it W1/W2

- **The step in two halves.** (a) W1-W3 fill `RevWalk` and `emit_reverse_block` takes it;
  `dfa_dir_landmark` folds into `dfa_dir_reverse` plus a `names` stem (its state variable,
  indentation and table comment become operands). (b) Later, the landmark walk's search body
  becomes records: a FIND record (the LMHIT site), the reverse walk, the anchored forward AUTO
  (verify), and the FINISH hands (roadmap P-d).
- **Byte identity:** both halves 0 movers; (b) is P-d's falsifier.
- **What it deletes:** (a) the second reverse `DfaDir` (R28, new, §4.3); (b) `emit_landmark_walk`
  (R10). The `pcrec_ctx_fail` asserts in `emit_landmark_walk` (the AT, LOWER, NOMATCH hands)
  become seam type checks of the records.
- **Witnesses (red in both builds):** S1825 (the walk takes the largest start: `a+b` on "aab",
  (0,3) vs (1,3)), S1827 (reach guard removed), S74 (reverse termination blind: the context below
  the floor), S759 / S760 (rev-end seeds), and two floor cells re-measured this lane against
  libpcre2 10.46: `a+b` on "aab" from offset 1 is (1,3) (route `landmark-walk` on main's build) and
  `[ab]+[bc]` on "aab" from 1 is (1,3) (route `unanchored`); a floor one byte low gives (0,3) on
  both. The floor cells are a proposed new row for (a), the one sabotage site that (a) moves from a
  string constant into an operand.

## 4. Steps

### 4.1 Byte-identical first

| step | what | bytes | prerequisites (status at 7cebea04e) | gate | trigger (ride-along, D77) | ratchet |
|---|---|---|---|---|---|---|
| S0 | this note; R03 restated, R28 added (§4.3); the D-next entry | none | none | the critic round | now | recipes only |
| S1 | `RevWalk` for W1-W3; `emit_reverse_block(RevWalk *)`; `dfa_dir_landmark` folded (§3.3 (a)) | 0 movers | p1build MERGED (dc6a40dfb) | `emit_sweep.py` identity, movers 0; `make test`; `make test-codegen`; the §3.3 witnesses re-aimed and DETECTED | the first change that opens a reverse walk: [REVBLOCK-VIEW] (form W in every composite's reverse pass, the likeliest), [LANDWALK-ALLACC], [LANDWALK-WINDOW], rev-inner (D151), or S3's build | R28 1 → 0 |
| S2 | W4 onto `RevWalk` (§3.2) | 0 movers | S1 | identity; `make test`; S50-S52, S94, S160 DETECTED | a change opening `vm_revdet_rep` ([VMREC] (b) or (c), a revdet widening) | R03 (restated) 1 → 0, subject to owner question 2 |
| S3 | the machine table (§2.4) + `VK_AUTO` (§2.3) + lookbehind rows `exist` and `gate` (§3.1) | moves only artifacts taking a row (abi event) | S1; vlookbehind stage 1 (`range`) shipped (rev 1 in progress, not built); [VMREC] (a) DONE (3bc599c92), `VK_AUTO`'s effects written to (c)'s declared-effects rule; [GIVEUP-DIFF] (not started) | vlookbehind §5.4 evidence (a)-(d) per regime, no regime slower beyond noise; libpcre2 differential 0 differences outside D142's class; WD1, WD2, WD5-WD7 | the measured cell of §4.2 | 0 (an instance); H-FLAGS (R14) declares its machine shape here |
| S4 | the landmark walk's body as records (§3.3 (b)), P-d | 0 movers | P-b (not started; waits on P-c) | P-d's: identity, one renderer body | P-b landed and a change opening the walk ([LANDWALK-VM], [LANDWALK-FWD], [LANDWALK-ALLACC]) | R10 1 → 0 |
| S5 (HELD) | lookbehind row `commit` (§3.1 row 3) | moves (abi) | S3 | the same choice bar; WD3, WD4 | a cell where the gate passes often but few lengths are viable (gate pass rate high, body runs per pass low) | 0 |

S1 and S2 are independent of S3 and cost nothing on the box; they land as ride-alongs and make S3
an instance. The owner's order (lookbehind first) is the order of DESIGN: the lookbehind is the
client whose needs set the operand list, and S3 is the first step built for a client rather than a
migration.

### 4.2 The measurement that prices the lookbehind client

**The cell.** The bench's `negation-scope-lookbehind-var` pattern (capability roster; body
`\bnot\s{1,3}(?:\w{1,12}\s{1,3}){0,3}`, widths 4..51), every subject of its roster group (e.g.
`br-doubled-word` under `short-subject-search`), `pcrec-auto` against `libpcre2_10.46_interp`, on
the dev box (7700X, gcc 15.2), both kit layers. **Today it is BLOCKED on pcrec** by the bench's
capability declaration `lookbehind-variable` (pcrec-bench `tools/selfcheck.py` checks the block);
it becomes measurable when vlookbehind stage 1 ships and the bench lifts the block (an inbox entry
the manager owes at that landing). **The trigger (D77):** pcrec slower than libpcre2 on that row
beyond noise with the lookbehind's candidate tries as the cause, or any regime (c) cell
(`(?<=\w{1,64}x)y`-like, candidates that do not fail at the first byte) in a real workload. **The
pricing A/B:** `range` against `gate` / `exist` behind a test-only lever (flag follows caller
effect: a public deny only if a regime can be slower) over vlookbehind §5.4's four regimes.

### 4.3 Ratchet recipes (proposed; the manager restates §5)

- **R03 restated.** Today's recipe, "`src/opt/revdet.c` present: 1", cannot fall: that file is the
  ANALYSIS (the structural representation's admission), which the end state keeps. Proposed:
  "`} Rev;` (revdet's private walk record) in `src/gen/emit_vm.c` present: 1, else 0". 1 at
  7cebea04e.
- **R28 new**, "reverse direction spellings": `static const DfaDir` objects in
  `src/gen/emit_dfa.c` whose `reverse` member is `true`, minus 1. At 7cebea04e: `dfa_dir_reverse`,
  `dfa_dir_landmark` → 1. Source: this note (a member the inventory did not list; per the roadmap's §8
  item 2, a found member is a row, not a free pass).
- **R10** unchanged ("`emit_landmark_walk` present: 1").

## 5. Siblings and the general form

- **The lookbehind candidate-source family has three members**: `range` (B), `reverse-dfa` (this
  note's rows), and [ENG-LOOK]'s forward `Σ*·L` existence machine (review r3-F16: the linear form,
  the one that unlocks unbounded lookbehind). The D186 row table of vlookbehind §5.4 IS their
  unification; the forward machine is a fourth exit row (`exist` from a forward AUTO run over the
  subject, its result read per position), filed with the HELD unbounded row. **The HELD row is NOT
  yet filed** (checked on lane/vlbrev1 at 2056360d7 and its working tree: no plan edit); when it
  is, it should name this note's `exist`/`gate` rows as the reverse form and [ENG-LOOK] as the
  forward one.
- **LOCATE × FINISH (D156).** Every reverse walk here is a LOCATE half handing a typed position to
  a FINISH row. The lookbehind is the same algebra inside a VM body: LOCATE = the reverse walk from
  the cursor, FINISH = a forward VM run pinned to end at the cursor. Proposal: FINISH's hand types
  (AT, LOWER, NOMATCH, SPAN) are the kind's hand types; no new vocabulary.
- **Moving-seed loops, three members** (W2's seeds {n, n − 1}, W3's LMHIT hits, W4's predecessor
  chain): **unification proposed** — the `seed` operand is a POSITION STREAM (a list, a FIND
  record's output, or the previous walk's result). [LANDWALK-WINDOW] (seed = the kit's window
  stream) is this form's next member and should be designed as it.
- **Moving-floor enumeration, two members** (lookbehind's retry, [LANDWALK-ALLACC]): one host loop
  (§2.2), noted; unify at the third.
- **Tagged exits, two members** (D164 B3's distance sets, W4's groups): noted. A TDFA-style group tag
  on table machines would let W4 change representation; HELD, trigger: a measurement showing a
  table walk faster than the structural one on revdet bodies.
- **Representation rows, three candidates** (table, structural, and [LANDWALK-FOLD]'s constant
  walks: `end-minus-width`, `offset-set`, the `pinned` rows are reverse walks of fixed-width
  languages): **unification proposed** as one representation axis of the kind; D161 add. 17's
  tiers (fixed k, one class run, a chain of runs, general reverse DFA) are its rows by prefix shape.
- **[LANDWALK-*].** ALLACC = enumerate; WINDOW = the seed stream; FWD = a forward AUTO replacing the
  verify; VM = the same function host as §2.3 placed in the VM search loop; FOLD = constant
  representation; CARD/CENSUS/EDGEPRICE ride the walk unchanged. Each is a ride-along trigger of S1.
- **rev-inner (D151, HELD under [ENG-TACTICS])**: a W3-shaped instance with a different seed;
  S1 removes the naming obstacle its filing names.

## 6. The "VM base" lens (owner's open frame; NOT a rule)

- **Where it helps.** The lookbehind client is exactly its shape: the plain VM `range` loop is the
  reference, the reverse walk an optimization section that must be answer-identical to it, its
  deny build the reference matcher. It also explains the exit rows' soundness in one sentence: a
  section may remove work the reference would do (`gate`), and may replace the reference's answer
  only where it is exact (`exist`). It reads [LANDWALK-VM] (VM finisher) as the general case and
  the landmark walk's anchored-DFA verify as its optimization, which is the right way round for
  the finisher contract (§2.3).
- **Where it is neutral.** W1-W3 live in artifacts with no VM in them; under the lens they are
  sections of a general matcher that is never emitted, and condition (a) (the all-DFA case emits
  today's bytes) is what S1's byte identity already demands. The kind keeps `host` as an operand so
  that nothing VM-specific (frames, work charge) leaks into an inline walk.
- **Where it could hurt.** Designing the kind around the VM host (charges, trail, give-up) would
  burden every pure-DFA walk; the `host` operand isolates it. And revdet is already a section
  INSIDE the choice family (it replaces frame-per-iteration), so the lens does not decide its
  representation question (owner question 2).

## 7. The standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** RELEVANT ONLY TO S3 (and S5): §4.2's cell and vlookbehind §5.4's four
   regimes, per-position cost of a lookbehind evaluation, hit and miss, throughput over subjects,
   dev box, both VM entries (the tiered default and `_search_in`), both kit layers. A regime where
   candidates do not fail at the first byte could flip the row, which is why (c) is required. S1,
   S2 and S4 are byte-identical: no number decides them.
2. **Independent control.** RELEVANT. Answers: libpcre2 10.46, which shares no source with pcrec;
   every witness answer cited here was measured against it (§3 and vlookbehind §2/§7). Bytes: the
   comparator's baseline is the previous commit's own output. The ratchet: its recipes, written
   here before the steps. Population: the D27 author and the generator of vlookbehind §6 gate 1
   count their own cells (K35). Reach: each witness states the row it clears; a choice row's
   witness is unreachable in its deny build by design, so its control is the default build alone,
   and the `range` row (the total fallback) is checked by stage 1's own witnesses.
3. **What moves when data is regenerated.** MOSTLY NOT RELEVANT: no table, calibration or measured
   set. Reverse machines are generated per artifact from the pattern; a rebuilt machine moves only
   that artifact's bytes. S3's new emission is an abi event (D76/D94, readers by grep) and a
   `tuning.md` section (D80); a future price card for `gate`/`exist` would move selections, never
   answers.

## 8. What this note does not decide

- The record's C names (`RevWalk`, `VK_AUTO`) and field layout: the build lane's.
- Whether the machine table (§2.4) lands with S1 (it can: W1-W3 read it) or with S3. Leaning S3.
- Inline vs function for a VM-hosted walk's TEXT beyond §2.3's reasons (gcc decides inlining).
- The `commit` row (S5) and a single-pass enumerator: HELD.
- TDFA tags for W4; tagged single machines for multi-branch lookbehinds; unbounded lookbehind.
- P-b's order relative to P-c (roadmap §6). Whether S4 is P-b's smallest instance (open question 3).
- Any change to the manifesto (none is needed) or to APPROACH.md.

## 9. Measured vs inferred

- MEASURED (this lane, libpcre2 10.46 as a library, the harness `vlbdesign_evidence/startpos.c`
  compiled in the lane scratch): `a+b`, `[a-z]+@x`, `[ab]+[bc]` from offset 1 ((1,3), (1,4),
  (1,3)); `(?<=a{1,2})b` on `aab` from 2 is (2,3). Routes read from main's `build/pcrec` stamps
  (`RX_DFA_SCAN "landmark-walk"` for the first two, `"unanchored"` for the third).
- READ from code at 7cebea04e (not executed): §1's table, §2's hosting precedents, the S74 context
  rule, the count-collapse arm.
- INFERRED: every byte-identity expectation (proved only by each step's comparator), the work
  charge in §3.1, the claim that `first` on the bench body dies within a few bytes at most
  positions.

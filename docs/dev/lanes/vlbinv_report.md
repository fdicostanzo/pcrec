# vlbinv report: what would it take to support variable-width lookbehind

Lane vlbinv (opus), 2026-11-05, branch `lane/vlbinv` from main `6c6e68086`. Investigation only:
nothing under `src/`, `cli/`, `lib/`, `memfn/src/`, `tests/` was touched. Plan row [VLOOKBEHIND].
PCRE2 side: the installed libpcre2-8 10.46 used as a library (`vlbinv_evidence/oracle_probe.c`),
`docs/design/lookaround_design.md`'s committed measurements, and `docs/pcre2_compliance.md`. The
pinned PCRE2 source copy was not opened (D181); one named question for a pcre2-reader is in §7.

## For the owner, in plain words

1. pcrec already handles lookbehinds whose alternatives have different fixed lengths (`(?<=a|bc)x`
   compiles). What it refuses is one alternative whose own length varies (`(?<=a{1,3})b`,
   `(?<=(a|bc))x`), and any backreference inside a lookbehind, even a fixed-length one.
2. The "37 corpus patterns" are not outside demand: all 37 are pcrec's own tests pinning the
   refusal (27 distinct patterns), and one of them (`(?<=${v})x`) is pcrec's own variable syntax
   that libpcre2 reads as a different pattern, so it is not a gap. The one bench pattern is a
   realistic negation-scope pattern (`(?<!\bnot\s{1,3}(?:\w{1,12}\s{1,3}){0,3})\bavailable\b`, 4 to 51 characters).
3. PCRE2's rules, measured: alternatives are tried in written order; inside one alternative the
   LONGEST possible step-back is tried first, the body runs forward and must end exactly at the
   current position (it backtracks inside the body to find such a path); the non-atomic forms
   retry shorter lengths when the rest of the match fails; the default cap is 255 characters, and
   once any alternative varies, EVERY alternative is held to that cap.
4. The general mechanism is today's machinery in a loop: for each alternative, try each length
   from longest to shortest. A fixed alternative is the loop with one turn, so it replaces the
   current path rather than sitting beside it. The lookaround design already sketched this as its
   follow-on. It covers 32 of the 37 rows (24 of 27 distinct); adding a width for backreferences
   covers 36 (the 37th is the false positive). It stays in the VM, where every lookbehind runs today.
5. Expanding into fixed-length alternatives instead covers only the 15 rows with no capture
   group inside, needs two groups sharing one number for the rest, and blows up on the bench
   pattern (143,967 alternatives). A reverse scan can answer yes/no but cannot set captures.
6. Recommendation: design the loop (small to medium), with a spec-first (D27) test author,
   and the backreference width as its own small step. Questions for you are in §8.

## 1. PCRE2 10.46 semantics (all MEASURED by libpcre2 probes unless marked)

Evidence: `vlbinv_evidence/compile_probes.{txt,out}`, `match_probes.{txt,out}`,
`compile_probes_utf.out`; `lookaround_design.md` §2.3/§2.4/§3.6 (earlier measurements, same library).

**Real forms.** All accepted, with `PCRE2_INFO_MAXLOOKBEHIND` = the widest branch's maximum:
- bounded quantifiers: `(?<=a{1,3})x` (3), `(?<=a?)x` (1), `(?<=a{0,3})x`, `(?<=a{2}b{0,1})x`;
- a variable-width group inside one branch: `(?<=(a|bc))x` (2), `(?<=(?:a|bc)d)x` (3),
  `(?<=((a|bc)d))x`, `(?<=(?:(a)|(bc)){1,3})x`;
- every spelling: `(?<=` `(?<!` `(?<*`, `(*plb:` `(*positive_lookbehind:` `(*nlb:`
  `(*negative_lookbehind:` `(*naplb:` `(*non_atomic_positive_lookbehind:`, all with `a{1,3}`;
- possessive/atomic inside: `(?<=a{1,3}+)x`, `(?<=(?>a{1,3}))x`; inline options `(?<=(?i)a{1,3})x`;
- backreferences inside, to a bounded group: `(a|bc)(?<=\1)x` (2), `(a{1,3})(?<=\1)x` (3),
  `(?<a>x|yz)(?<=\k<a>)w` (2), `(?<=(a|bc)\1)x` (4, the sum);
- calls to a bounded group: `(?<=(?1))x(a|bc)` (2), `(?<=(?1))x(a{1,3})` (3);
- nesting: `(?<=\d{1,3}(?=x))x`, `(?<=(?<=a{1,200})b{1,200})x` (200: nesting is max, not sum);
- `\R` (1..2) and `\C{1,2}` are accepted in a lookbehind (both refused by pcrec for other reasons today).

**Refused.** Unbounded: `(?<=a*)` family, `(a*)(?<=\1)x`, `(?<=(?1))x(a+)`, `(?<=\X)x` (err 125,
"length of lookbehind assertion is not limited"). `\K` in any lookaround: err 199. pcrec already
agrees on all of these (they are among the 39 corpus refusals libpcre2 also rejects).

**The cap** (default compile context; settable by `pcre2_set_max_varlookbehind`, which
`docs/pcre2_options.md` does not list, because that survey covers option bits, not context setters):
- `(?<=a{1,255})x` ok, `(?<=a{1,256})x` err 200 "branch too long in variable-length lookbehind
  assertion"; UTF mode counts characters (`(?<=é{1,255})x` ok, `{1,256}` err 200).
- The cap is on the branch's MAXIMUM: `(?<=a{254}b?)x` ok, `(?<=a{255}b?)x` err 200;
  `(?<=a{1,100}b{1,100}c{1,55})x` ok, `...c{1,56}` err 200; `(?<=(?:a{1,100}){2})x` ok, `{3}` err 200.
- A FIXED lookbehind is not capped: `(?<=a{300})x` ok, and so are fixed branches of different
  lengths `(?<=a{300}|b)x`, `(?<=a{256}|b)x`. BUT once one branch varies, the fixed ones are capped
  too: `(?<=a{300}|b{1,2})x` is err 200. A separate assertion does not count:
  `(?<=a{300})(?<=b?)x` ok. (Why this rule holds is §7's question; the cells are measured.)

**Match semantics** (`match_probes.out`; offsets are [match, g1, g2...]):
- Level 1, branches in written order: `(?<=(a)|(aa))c` on `aac` gives g1=(1,2);
  `(?<=(a{1,2})|(aaa))c` on `aaac` gives g1=(1,3) (branch 1, its longest viable length).
- Level 2, longest step-back first within a branch, whatever the body's own order or laziness:
  `(?<=(a{1,3}))c` and `(?<=(a{1,3}?))c` on `aaac` both give g1=(0,3); `(?<=(a|aa))c` and
  `(?<=(aa|a))c` on `aac` both give g1=(0,2); `(?<=(a{0,2}?)(a{0,2}))c` on `aac` gives g1=(0,0) g2=(0,2).
- The end condition backtracks inside the body: `(?<=(a|ab)(b|))x` on `abbx` gives g1=(0,2)
  g2=(2,3) (the first path at length 3 ends at 2 and is rejected, a later path at the same length
  ends at 3); `(?<=(a|ab)(c?))x` on `abcx` gives g1=(0,2) g2=(2,3).
- Non-atomic forms retry SHORTER lengths: `(?<*(a|ba))c\1` on `baca` gives (2,4) g1=(1,2), and
  `(?<*(a{1,3}))c\1` on `aaaca` gives g1=(2,3); the atomic `(?<=` forms give nomatch on both.
  Across branches: `(?<*(a{1,2})|(aaa))c\2` on `aaacaaa` gives g1 unset, g2=(0,3).
- Negative: `(?<!(a|bc))x` is nomatch on `bcx` and `ax`, matches on `dx`, `x`, `cx`.
- Nested lookarounds are evaluated at each tried start: `(?<=(?<!b)a{1,2})x` on `baax` matches
  (length 2 rejected by the inner assertion, length 1 accepted).
- Nullable bodies: `(?<=a?)x` and `(?<=\w?)x` always hold, `(?<!a?)x` never does;
  `(?<=\n?\z)x` can never match.
- The bench pattern: nomatch on `is not really available`, (3,12) on `is available`,
  (12,21) on `not a b c d available` (the negation is out of range).

## 2. pcrec today

- **The rule and the refusal** (`src/parse/mod_lookaround.c`): `la_widths` reads each top-level
  branch from `pcrec_lookbehind_branches` (the one branch split, K123) and refuses when
  `pcrec_cwmin != pcrec_cwmax`; `la_width_refusal` writes the sentence (one home, used by the parse
  hook and by `pcrec_lookaround_fix_widths`, the deferred re-check for bodies with calls that runs
  after `src/opt/callgraph.c` publishes callee widths; K127 refuses a body that recurses into
  itself). The result is `Ast.u.look.widths`, one `int` per branch; `la_lb_raise` raises
  `Ctx.lb_max` (PCRE2's max_lookbehind) to the widest branch.
- **Backreferences:** `pcrec_cwmax(A_BREF)` is `PCREC_W_UNBOUNDED` (`src/opt/mrl.c`, the row's
  answer), so `(a)(?<=\1)x` is refused as "unbounded" though PCRE2 accepts it. A refusal by design,
  `lookaround_design.md` §2.5 bullet 7, which names the follow-on.
- **VM** (`src/gen/emit_vm.c`, `vm_look` + `vm_look_behind` + `vm_look_behind_branch`): per
  branch in written order, a start-of-subject guard (`scan_position < k`), a retry frame for the
  next branch, `RX_CHARGE_WORK(k)`, a back-step of `k` characters through the encoding seam
  (`$_back_step`, so UTF-8 works), the body emitted forward by `vm_emit` unchanged, then the
  END-CHECK (`scan_position` equals the saved entry position). The end-check is redundant for
  fixed widths and kept as runtime evidence; on the NEGATIVE arm a failed end-check is a hard
  return (`RX_R_INTERNAL`, ASK 2 ruling), on the positive arm a decline. Atomic forms cut the body's
  frames at success (`vm_cut`); non-atomic forms keep the per-branch retry frames live (§3.6).
- **DFA:** no lookaround of width 2 or more reaches the DFA. All six registry rows are VM_ONLY
  (`src/opt/select_engine.c`'s A_LOOK arm; design §5.1). The exception is the context node
  (`src/parse/ctxnode.c`): a lookaround whose body's LANGUAGE is a set of single characters
  becomes `A_CTX`, which the DFA answers on its class axis. No variable-width body has such a
  language, so none would change engine. [ENG-LOOK] (the product construction) is not started.
- **Hybrid** (VM with a DFA prefilter): the prefilter lowers every `A_LOOK` to epsilon
  (`src/ir/nfa.c`), a superset that does not depend on width, so it is unaffected.
- **Other readers of lookbehinds**, checked by grep for `A_LOOK` and `u.look.widths`: the facts
  walks (`src/facts/endwin.c`, `req.c`, `startanch.c`, `startset.c`, `widths.c`) and `mrl.c`,
  `lmwalk.c`, `altcls.c` treat a lookaround as zero-width or do not descend into it; `derive.c`
  marks lookbehind regions, which does not depend on width. Readers of `u.look.widths` and
  `nbranch`: only `mod_lookaround.c` and `emit_vm.c` (`vm_look_behind_branch`, the frame/push
  counts at its two budget sites). `lb_max` would take the branch maximum, which is what PCRE2 reports.

**What generalizes.** Everything except one number per branch. A fixed branch is the range
`[k,k]`; the guard, the back-step entry, the forward body, the budget charge and the end-check
are the same per tried length. The end-check stops being redundant, which the design said it
would (§3.4, last paragraph). The width analysis (`pcrec_cwmin`/`pcrec_cwmax`, characters since
[M5.0] stage 2) already produces the range, so no new analysis is needed except for backreferences.

## 3. Approaches

| | approach | what it is | engines | covers (rows / distinct of 37 / 27) | size | subsumes fixed path? |
|---|---|---|---|---|---|---|
| A | expand to fixed alternatives | rewrite each variable branch into an alternation of fixed-length branches, longest first, then today's machinery | VM (today's) | 15 / 12 without captures; 30 / 22 if two capture nodes may share one group number (pcrec has no such concept today: no branch reset) | medium, and exponential output | no: a second mechanism in front of the first |
| B | step-back loop | per branch, for `k` = max down to min (clamped to what precedes the cursor): back-step `k`, run the body forward, end-check; on failure retry `k-1`, then the next branch | VM | 32 / 24 | small to medium | yes: `[k,k]` is one turn of the loop |
| B+ | B plus a backreference width | `pcrec_cwmax(A_BREF)` = the widest group it can name (union over duplicate names; unbounded if any is) | VM | 36 / 26 | small, on top of B | n/a |
| C | reverse machine bounded by the max width | a reverse DFA of the capture-erased body run from the cursor back at most `max` characters | DFA/VM yes-no only | the 12 capture- and reference-free distinct patterns; cannot set captures or retry | large | no |

**A in detail.** Correct for level-2 order only if the expansion sorts by length and keeps the
body's own order within a length; a nested quantifier makes that a product (`(?:\w{1,12}\s{1,3}){0,3}`
alone is 47,989 paths, the bench pattern 143,967: `vlbinv_evidence/bench_expansion.txt`). A
length-indexed restriction without enumeration is the same thing as B's loop, done at compile
time. A could ride on `docs/design/alt_normal_form.md`'s width groups only for capture-free literal
alternations (`(?<=(?:a|bc))x`), which is 6 of the 37 rows. Not recommended.

**B in detail** (the design's own §2.5 sketch, "a loop over k from maxw down to minw, the same
back-step entry, the same end-check"). What changes:
1. `u.look.widths` becomes a range per branch (`lo`, `hi`); `la_widths` refuses only unbounded,
   too-long, and PCRE2's cap (§1: 255 on every branch once any branch varies). The cap is a new
   [LIM-1] entry in `src/core/limits.def` and a spec hunk.
2. `vm_look_behind_branch` emits the loop: a slot holds the current `k`; the retry frame is
   pushed once per tried length, so live frames stay bounded by one per branch; the guard becomes
   a clamp (`k = min(hi, characters before the cursor)`; under UTF-8 the back-step reports how
   far it got, then each retry moves the start FORWARD one character, so a 255-wide branch costs
   O(max) stepping per position rather than O(max squared)).
3. The end-check becomes an ordinary decline on BOTH polarities for a varying branch: a failed
   end-check is now a normal outcome, so the negative arm's `RX_R_INTERNAL` hard return (ASK 2)
   cannot stay for those branches. For `lo == hi` it can stay as today's evidence check.
4. Budgets: `RX_CHARGE_WORK(k)` per tried length; the retry frames are real frames, so D42's
   frame bound sees them (the design's reason 2 against shipping in [M6.6.2] was a frameless re-run).
5. Atomic forms cut all retry frames at success (unchanged); non-atomic keep them, which is
   exactly PCRE2's measured retry-shorter behaviour.

Whether a fixed branch emits the loop or today's bytes is §8 question 2.

**C in detail.** For a capture-free, reference-free atomic body, "some length in range works"
is a yes/no question a reverse automaton answers in one pass. That is [ENG-LOOK]'s product
construction (`(?<=L)` at p iff the text before p is in Σ*·L), and there the width does not
matter at all: a bounded variable body is no harder than a fixed one. So C belongs to
[ENG-LOOK] (engine choice), not to this row (capability). Within B it could later serve as a
filter that skips lengths that cannot work, under measurement only (D77).

**Name of the general form:** a lookbehind branch is a WIDTH RANGE, tried longest first; today's
fixed-width rule is its one-point case. That is B.

## 4. The population

`vlbinv_evidence/population.tsv` (per pattern) and `population_coverage.txt`; the 76
"variable-length" refusals with libpcre2's verdict are in `corpus76_vs_pcre2.tsv` (37 accept, 39
reject; the 39 are unbounded or recursive bodies where pcrec already agrees with PCRE2).

| shape | rows | distinct | width range | captures inside | A | B | B+ |
|---|---|---|---|---|---|---|---|
| group alternation, capturing (`(?<=(a\|bc))x` and its spellings, `((a\|bc)d)`) | 15 | 10 | 1..2 or 2..3 | 1-2 | dup group numbers | yes | yes |
| group alternation, non-capturing | 6 | 5 | 1..2 or 2..3 | 0 | yes | yes | yes |
| bounded quantifier (`a{2,3}` `a?` `a{0,3}` `a{1,255}` `a{2}b{0,1}` `\w?` `\n?\z`) | 9 | 7 | 0..1 up to 1..255 | 0 | yes (255 branches for `a{1,255}`) | yes | yes |
| backreference inside (`(a)(?<=\1)x`, `(a\|bc)(?<=\1)x`) | 4 | 2 | by group, 1 or 1..2 | 0 | no | no | yes |
| call to a bounded group (`(?<=(?&g))` with `g` = `a\|ab`) | 2 | 2 | 1..2 | 0 | no | yes (deferred path) | yes |
| pcrec's `${v}` (false positive) | 1 | 1 | unbounded in pcrec | 0 | no | no | no |
| **bench** `negation-scope-lookbehind-var` | (1 bench) | 1 | 4..51 | 0 | no (143,967 branches) | yes | yes |

- All 37 rows are `perr` rows in pcrec's own corpus (11 files, mostly `tests/lookaround/refused.rxt`,
  `tests/lookaround/d27/refusals.rxt` and `spellings.rxt`, and `tests/lookaround/lookbehind_group_alt.rxt`)
  written to pin this refusal. So they count our own tests, not demand; each would flip from a
  refusal to a match cell (oracle-verified) under B.
- Width sets are tiny (2 to 4 lengths) except `a{1,255}` (pcrec's test at PCRE2's cap) and the
  bench pattern (48 lengths). Every one is VM today and would stay VM.
- Five rows are nullable positive bodies (`a?`, `a{0,3}`, `\w?`) that always hold, and one
  (`\n?\z`) can never match. These are degenerate, not a reason for a special path.

## 5. Risks, tests, overlap

**Answer identity.**
- Level-2 order: a loop written in the emitter's usual preference-first direction (shortest
  first) gives wrong captures on every capturing row (`(?<=(a|aa))c` g1=(1,2) instead of (0,2)).
  Sabotage witness: run the loop shortest-first.
- The end-check is now load-bearing: dropping it, or not backtracking into the body on failure,
  breaks `(?<=(a|ab)(b|))x` on `abbx`. Witness: end-check removed.
- Non-atomic retry: cutting the per-length frames breaks `(?<*(a{1,3}))c\1` on `aaaca`. Witness:
  cut on the non-atomic arm.
- Existing sabotage rows that move: S136 ("width rule accepts variable") tests a premise B
  removes and needs re-aiming (e.g. the analysis returns `lo` for `hi`); the S-LA11 negative-arm
  cell rests on the `RX_R_INTERNAL` end-check (§3 B point 3); S135 (back-step clamped to startpos)
  carries over unchanged.
- The accept set must stay inside PCRE2's: adopt the 255 cap with PCRE2's every-branch-once-any-varies
  rule (§1), so pcrec never compiles a pattern libpcre2 refuses (the scoreboard found none today).
- UTF-8: lengths are characters; the start-of-subject clamp must count characters.

**Compile time and size.** B: no blow-up; one body copy per branch, as today, plus a few
lines per branch. A: exponential (above). **Run time:** up to (hi - lo + 1) body runs per
candidate position per branch; for `a{1,255}` that is 255 per position, the same order of work
as PCRE2 does (MEASURED semantics; PCRE2's own cost not measured). `RX_ERR_WORK` bounds it.

**Test plan sketch.** Oracle: libpcre2 10.46 differential (PC-3's harness) over a generated
cell set: every spelling × {capturing, non-capturing} × {group alternation, bounded quantifier,
nested, backreference, call} × subjects chosen to hit each length, the start-of-subject clamp,
the end-check backtrack, the non-atomic retry and the cap boundary (255/256, the
fixed-plus-variable cell), byte and UTF-8. Flip the 36 real rows from `perr` to match cells.
A D27 spec-first author is RECOMMENDED: the level-2 order is the kind of rule that tests written
from the code inherit wrong (the design's own reason 1 cites the [M4.6d] counter-rung defect a
blinded author found), and `tests/lookaround/d27/` already exists to extend.

**Overlap with in-flight work.**
- span_pick stage 1 (kit): none found. The kit owns search sites; a lookbehind is VM body
  emission, and the prefilter erases it.
- `docs/design/alt_normal_form.md` (rev 0, proposed): B does not ride on it. A would, only for
  capture-free alternations (its width groups are the same split), which is 6 rows.
- [CTX-PREFILTER] (not started): lowers a lookaround to the strongest one-character context for
  the prefilter. A variable body's last character is still a set (`(?<=(a|bc))` gives
  `[ac]`), so it applies unchanged; nullable bodies give nothing.
- [ENG-LOOK] (not started): §3 C. The product construction covers bounded variable bodies at no
  extra cost, so B does not prejudice it.
- `emit_vm.c` remodel: no `STATE:started` row in plan.md names `vm_look`; checked by grep, not by asking.

## 6. Size and recommendation

| approach | size | why |
|---|---|---|
| A | medium, unbounded output | AST rewrite plus a new duplicate-group-number concept, exponential cases need a cap and a fallback, partial coverage |
| B | small to medium | the rule (range instead of a number, cap), one emitter function's loop, the end-check's negative-arm change, budget, spec and compliance hunks, 36 re-pinned rows, generated differential, 3 new sabotage rows plus S136's re-aim |
| B+ | small | one `cwmax` arm plus duplicate names and the recursion case; its own tests |
| C | large | a new reverse-run mechanism; the right home is [ENG-LOOK] |

**Recommendation:** design B, with B+ as a second, separately gated step, VM-only as every
lookbehind is today, test-first from a D27 author against libpcre2. It is the general form
(fixed width is its one-point case), it covers every real row and the bench pattern, and the
existing design already argued its shape. The case for doing it is completeness against
PCRE2, not measured demand: no pattern outside pcrec's own tests and one bench probe uses it.

## 7. The one question for a pcre2-reader (D181)

"In PCRE2 10.46, when a lookbehind has at least one variable-length branch, which branches does
`max_varlookbehind` limit, and how does the matcher run a variable-length branch: does it try
each step-back length from longest to shortest, re-running the branch forward each time and
backtracking inside it until it ends at the assertion point? (Measured: `(?<=a{300}|b{1,2})x` is
error 200 but `(?<=a{300}|b)x` compiles.)" The answer would confirm the cap rule pcrec must copy
and the cost model B assumes; the observable behaviour is already measured in §1.

## 8. Questions for Frank (plain words)

1. **Go or wait?** Nothing outside pcrec's own refusal tests uses this except one bench
   pattern. It closes the largest gap on the scoreboard. Shall a design lane write up the
   step-back loop? My leaning: yes, design only, since the shape is already argued and it is small.
2. **Fixed lookbehinds after the change.** Either every lookbehind is emitted as the loop (one
   form; every artifact containing a lookbehind changes bytes, an abi event), or a branch with one
   possible length keeps today's exact code (the loop folded away when there is only one turn). My
   leaning: the folded form. It is the same mechanism with a constant range, not a second path, and
   it moves no existing artifact.
3. **The 255 cap.** PCRE2 lets a caller change it (`pcre2_set_max_varlookbehind`). Should pcrec
   take the default 255 only (a fixed limit, listed in `--list-limits`), or expose a setting? My
   leaning: the default only for now, with the option going to the interface push ([IFACE-PUSH]).
4. **Backreferences inside lookbehinds** (`(a|bc)(?<=\1)x`): pcrec refuses them even when
   fixed. Include them in the same design, or as a second small step? My leaning: a second step,
   since it changes a width answer other passes read.

## Measured vs inferred

- MEASURED (this lane, this box, libpcre2 10.46 as a library): every accept/reject, error number
  and `MAXLOOKBEHIND` in §1; every match cell in §1; pcrec's refusal of the premise patterns
  (`premise.txt`: `(?<=a{1,3})b` refused 1..3, `(?<=a|bc)x` compiles, both accepted by libpcre2);
  the 76/37/39 split of the corpus refusals; the population classification.
- READ from code (not executed): §2's mechanism descriptions and the reader list (grep for
  `A_LOOK`, `u.look.widths`, `nbranch`).
- INFERRED: approach coverage counts (per-pattern judgement in `population.tsv`), sizes, the
  run-time cost of B, PCRE2's internal algorithm (§7 asks), the bench-pattern expansion count
  (arithmetic: `bench_expansion.txt`), and "no overlap" with in-flight rows (grep of plan.md).
- NOT done: no match comparison of pcrec against libpcre2 (nothing new to compare: pcrec refuses
  every case); no timing.

## STATE AT HANDOFF

STATE: delivered. Rulings file `vlbinv_rulings.md`: empty at every read (no ruling applied).
No build, no heavy run, nothing owed. Evidence: `docs/dev/lanes/vlbinv_evidence/`
(`premise.txt`, `oracle_probe.c`, `compile_probes.{txt,out}`, `compile_probes_utf.out`,
`match_probes.{txt,out}`, `corpus76_vs_pcre2.tsv`, `population.tsv`, `population_coverage.txt`,
`bench_expansion.txt`).

## Owner addendum (Frank, 2026-11-05 19:30) — candidate approach D, to be vetted by the design lane

"I'm certainly not going to try a reverse vm just for this. But we could reverse dfa then forward vm for captures." No reverse VM. Candidate D: a reverse DFA of the lookbehind body, run from the cursor back at most the max width, finds where the body can start (per alternative, or one DFA with priority-tagged accepts); PCRE2's order picks the first alternative with any start, then its longest step-back; one forward anchored VM run from that start, required to end at the cursor, sets the captures. Capture-free and negative lookbehinds need the DFA only. Manager's note: this is the landmark walk's own shape (D184: a reverse machine to the accepting start, then one anchored forward finish), so it may be a second client of that mechanism rather than a new one. To vet: non-atomic retries (record every accepting start, not just the farthest); DFA size per lookbehind; whether the VM artifact can host the reverse DFA as the walk's finisher pairing does today; and versus the step-back loop (B) on speed and simplicity.

# R23 appendix — raw critic findings, verbatim

The three R23 critic lanes' findings files, archived unedited. The
compiled review with triage dispositions is 2026-08-15-r23-k18-memo.md;
this file is the evidence of record. Lane scratch evidence referenced
inside (protos/, pats_*.txt) lived in the session scratchpad; the
semantics lane's scripts and prototypes are archived in
docs/design/k18_measurements/r23_semantics/ (corpora regenerable from
the seeded generators there).

---

# R23 semantics critic findings (docs/design/k18_memo_design.md)

Started: 2026-08-15T15:47:52-04:00

## S1 (HYPOTHESIS, being measured) — the open-loop stack ARRAY is clobbered by a callee's redirect; only `depth` is restored

**Note's claim.** §2a, "The tail recursion does not deepen", marked **STRUCTURAL**:
"the redirect TRUNCATES the stack to the re-arrived loop's index, and a frame
restores the saved depth on return, so the push made on an iterative tail edge
is always unwound by one of those two."

**My reading of prototypes/proto_a.py.** `clo_visit` saves `save_depth`/`save_ctx`
at entry and restores them at `done:`. A redirect does
`cl->depth = at; cl->ctx = at ? cl->open[at-1].ctx : 0` where `at` may be an index
BELOW the current frame's `save_depth` (the re-arrived loop was pushed by an
ANCESTOR frame — which is exactly the K18 shape). The walk then continues from
that loop's exit edge and may PUSH new loops at indices `at, at+1, ...`,
OVERWRITING `cl->open[at .. save_depth)`. On return the frame restores `depth`
(correct — the caller's remaining path really is still inside those loops) but
NOT the ENTRIES. So after such a return:

  * the redirect scan `for (i = depth-1; i>=0; i--) if (open[i].loop == s)`
    reads clobbered loop ids -> an OPEN loop can fail to be found -> the
    empty-iteration redirect is LOST AGAIN (K18 in disguise), and
  * the pushing frame's `cl->ctx = cl->open[cl->depth-1].ctx` after its
    recursive call reads a clobbered ctx.

If reachable this is a BLOCKER, not a MINOR: it is the same defect class the
note is repairing, reintroduced by the repair.

Status: constructing a witness. (Recorded before measurement so the hypothesis
is on the record independent of whether I can build the witness.)

## S3 (MAJOR) — A2's open-loop stack is genuinely CORRUPTED across frames, and the corruption REACHES the redirect decision on 552 of my 1001 patterns

**Note's claim.** §2a, **STRUCTURAL**: "the redirect TRUNCATES the stack to the
re-arrived loop's index, and a frame restores the saved depth on return, so the
push made on an iterative tail edge is always unwound by one of those two."
§3 setup (ii), **STRUCTURAL**: "the stack contains no repeats (a re-arrival at
an open loop redirects instead of pushing)".

**The mechanism (S1, now measured).** `clo_visit` saves and restores `depth`
and `ctx` but NOT the stack ENTRIES. A redirect sets `cl->depth = at` where
`at` can be BELOW the current frame's `save_depth` (the re-arrived loop was
pushed by an ancestor frame — reachable because the only epsilon exit from a
loop body is through the loop's own entry split, so a walk inside loop L can
redirect at L and then immediately redirect at an enclosing loop O). The
continuation then pushes new loops at indices `at, at+1, ...`, overwriting the
ancestors' entries. On return `depth` is restored but the entries are not.

**Both sides measured.** `proto_a2_shadow.py` builds ONE binary carrying both
disciplines: `cl->open` (entries saved/restored per frame — correct) drives the
walk, `cl->sh` (entries never restored — prototype A/A2's actual discipline)
is written identically and only observed. At every arrival at a `loop=1` state
both are scanned; `scandiff` counts arrivals where the two give a DIFFERENT
redirect verdict.

    bash mkproto.sh a2sh .../proto_a2_shadow.py
    python3 sweep_shadow.py protos/a2sh/build/pcrec pats_r23.txt

**MEASURED, 1001 patterns:** `scandiff > 0` on **552**, `ctxdiff > 0` on 56,
`clobber > 0` on 629. Per-pattern examples (forward machine / reverse machine
lines separately):

    (?:(?:(?:a|b*?)?)*)*c*     scandiff=0 (fwd)  scandiff=8  (rev)  clobber=54
    (?:(?:(?:a|b*?)?)*c*)*     scandiff=0 (fwd)  scandiff=12 (rev)  clobber=84
    (?:(?:(?:(?:a|b*?)?)*)*c*)* scandiff=0(fwd)  scandiff=44 (rev)  clobber=148

Note WHERE it fires: overwhelmingly on the REVERSE (D7, `prune=0`) machine,
which is precisely the axis §4.6 lists as never singled out.

**And yet: no answer changes.** `emitcmp.py` (mine) over A2 vs an A2 that
additionally saves/restores the entries (`proto_a2_fix.py`):

    pats_r23.txt   (1001 patterns, my families)          0 differ
    pats_s1.txt    (1728 patterns built to force this)   0 differ

with the non-vacuity control that the same harness reports **405 of 1001**
differing between `base` and A2. So the corruption is REAL, REACHES the
decision, and is currently LATENT.

**Why this is still MAJOR and not an OBSERVATION.** The note's §3 termination
proof rests on setup (ii) — the stack has no repeats — and `openst` is sized
`nfa->n + 2` entries with no bound check. A missed redirect from a clobbered
slot is exactly a push of an already-open loop, i.e. a repeat. The design
therefore has an unstated invariant that is FALSE in the prototype it was
measured on, and the two things that would catch it (the `nonstacktop` counter
and the proposed `at < cl->depth` assertion) do not test it: `nonstacktop`
measured 0 because the CLOBBERED stack still finds its match at the top.

**What the rewrite lane owes.** Either restore the entries per frame (cost:
the walk is already O(depth) at each redirect scan, so an O(depth) save is not
a new asymptotic — but it should be MEASURED, not assumed), or prove the
no-repeat invariant survives clobbering and carry it as an assertion
(`for i<depth: open[i].loop != s` before every push). §5 item 6's counter list
should gain that assertion; `nonstacktop` alone does not cover it.

## S4 (OBSERVATION — survived) — the empty-context fast path (A2 vs A) changes no answers, re-measured on evidence the note did not use

**Note's claim.** §2a, **STRUCTURAL** that the fast path changes no answers,
**MEASURED** byte-identical on the note's own 18,858 shapes + 555 corpus
patterns.

**Attack.** The fast path replaces the (state,0) hash key with the shipped
per-state stamp array `seen0`, threaded through a SECOND `Marks` whose
generation is advanced in lockstep with the first. Two things could break it:
key aliasing (a ctx-0 entry visible to a ctx!=0 probe, or vice versa) and
generation desynchronisation between `mk` and `mk0` at the `marks_next` wrap.
I re-ran the identity on corpora the note never used.

    python3 emitcmp.py pats_r23.txt  protos/a/build/pcrec protos/a2/build/pcrec
    python3 emitcmp.py pats_r23b.txt protos/a/build/pcrec protos/a2/build/pcrec

**MEASURED: 0 of 1001 differ, 0 of 523 differ.** And on spans,
`ocheck.py pats_r23b.txt base A A2 A2FIX --alpha abcd --len 3`
(523 patterns x 85 subjects = 44,455 cells): base disagrees with the oracle on
**1125 cells / 141 patterns**, A on **0**, A2 on **0**, A2FIX on **0**.

I could not break the fast path. Recorded as a survived attack. (The wrap path
is still UNMEASURED by anyone: `marks_next` wraps at 2^32 closures, which no
test reaches. It is safe by inspection because both Marks advance together, but
the rewrite should say so in a comment rather than leave it implicit.)

## S5 (OBSERVATION) — §1.4's BELIEVED "each half is necessary" is now MEASURED, and one half is worse than the note says

**Note's claim.** §1.4, **BELIEVED**: "(2) alone would not fix K18 ... (1) alone
would not either ... I did not build the two half-prototypes to confirm it, and
a panel that wants it MEASURED should say so, since it is cheap." §6 ruling 2
asks whether to measure it. I built both.

**HALF-2 — change (2) alone** (`proto_half2.py`: keep the open-loop stack and
the "this loop is OPEN on my path" redirect trigger, force the memo key's
context to 0 so the memo degenerates to the shipped per-state memo):

    python3 ocheck.py pat_smoke.txt HALF2 A2 base --alpha ab --len 3

    (?:(?:a|b*?)?)*   'ab'  HALF2=(0,2)  A2=(0,1)  base=(0,2)  oracle=(0,1)
    (?:(?:a|b*?)?)*   'aab' HALF2=(0,3)  A2=(0,2)  base=(0,3)  oracle=(0,2)
    (?:(?:a|b*?)?)*   'aba' HALF2=(0,3)  A2=(0,1)  base=(0,3)  oracle=(0,1)
    (?:(?:a|b*?)?)*   'abb' HALF2=(0,2)  A2=(0,1)  base=(0,2)  oracle=(0,1)
    (^-anchored member: identical)

    HALF2 disagrees with oracle on 8 cells / 2 patterns  (== base, exactly)
    A2    disagrees with oracle on 0 cells

**CONFIRMED, now MEASURED:** change (2) alone reproduces the shipped compiler's
wrong answers cell for cell on the K18 witness.

**HALF-1 — change (1) alone** (`proto_half1.py`: memo keyed on (state,ctx),
redirect trigger stays the SHIPPED "this key was already seen and the state is
a loop entry", i.e. no open-set test and no stack truncation): it does not
merely fail to fix K18 — **it does not terminate.**

    $ protos/half1/build/pcrec -p rx --emit-main -o t.c -- '(?:(?:a|b*?)?)*'
    munmap_chunk(): invalid pointer      (SIGABRT)

and with the `openst` array oversized 20,000x (`proto_half1b.py`) it still
SEGFAULTs on the same 15-character pattern: the open-loop stack grows without
bound, because without the open-set test a loop entry is PUSHED again on every
re-arrival at a fresh context, and each fresh context makes a fresh memo key.

**Two things the panel should take from this.** (a) The note's §1.4 claim is
CONFIRMED and can be re-marked MEASURED. (b) The stronger fact is the one the
note does not state: the open-set test is not only the thing that makes the
redirect fire, it is the thing that BOUNDS THE STACK. §3's setup (ii) ("the
stack contains no repeats — a re-arrival at an open loop redirects instead of
pushing") is therefore not a convenience, it is what keeps `openst`'s
`nfa->n + 2` sizing safe, and it has no assertion behind it. See S3.

## S6 (OBSERVATION — survived) — the memo is EXACT: A2 == a no-memo reference == prototype C on every pattern I could generate

**Note's claim.** §2c, asserted rather than measured: "A and C give the same
answers, so the difference between them is the memo's contribution and nothing
else." §2c measures COST only; the ANSWER equality is stated, not shown.

**Attack.** If the (state, open-loop-context) memo ever suppresses a re-arrival
whose subtree would have contributed a thread or an ACCEPT, A2's DFA differs
from the un-memoized walk. I built `proto_ref.py` = prototype C (no memo at
all) PLUS the per-frame stack-entry restore of S3, i.e. the most conservative
reading of the design's own rule, and diffed emitted C three ways.

    python3 emitcmp.py pats_r23.txt \
        protos/a2/build/pcrec protos/ref/build/pcrec protos/c/build/pcrec

**MEASURED: 1001 patterns, 0 differ across all three.** The memo suppresses
nothing that matters on this space, and it does so whether or not the stack is
corrupted. Recorded as a survived attack; it also converts §2c's answer-equality
assertion into a measurement, which is worth doing because §2c's whole
argument-from-cost depends on it.

## S7 (MINOR) — the trie-identity gate is a NEW obligation A2 creates, and the note does not mention it

**The issue (not a claim of the note — an omission).** `tests/codegen/run_trie_identity.sh`
requires the shipped compiler and a `-DPCREC_NO_TRIE` build to emit
BYTE-IDENTICAL C, on the argument that "subset construction plus minimization
must erase the difference" the M2.8 trie makes to the NFA. A2 makes the closure
PATH-SENSITIVE over the epsilon graph, and the trie CHANGES that graph — it
factors shared prefixes of an alternation, which alters which epsilon states a
walk passes through and therefore which contexts exist. The erasure argument
was written for a path-INSENSITIVE closure and does not automatically carry.
The note's §5 validation plan does not list this gate.

**Measured, both sides.** I built `-DPCREC_NO_TRIE` references from the A2 and
base scratch trees and crossed the two features deliberately: flat alternations
(what the trie factors) whose branches carry nullable quantifiers, under a
nullable loop (`pats_trie.txt`, 180 patterns).

    control  base vs base_notrie : 180 patterns, 0 differ
             A2   vs a2_notrie   : 180 patterns, 0 differ

So the gate HOLDS under A2 on this family. It is recorded as MINOR rather than
dropped because (a) the rewrite lane should run `run_trie_identity.sh` as an
explicit gate and say so in §5, and (b) my 180 patterns are not its 500 random
ones plus the `-i` sweep.

## S8 (MAJOR) — a FOURTH structural sub-case: LAZINESS IS NOT REQUIRED. The defect fires on a GREEDY nullable arm whenever it is the PREFERRED one, and the acceptance corpus mis-classifies exactly that shape as a control

**Note's claim.** §1.3, **MEASURED** trace, and §1's whole framing: the walk
dies because "the lazy `b*?` then prefers its exit, and that exit edge points
straight back at state 2". §4.1 reports the acceptance file as "8 diverging
shapes and 7 over-reach controls", **MEASURED**. The characterisation is
inherited from `docs/dev/known_issues.md` K18, whose control list states that
`(?:(?:a|b*)?)*` and `(?:(?:a|b?)?)*` ("greedy inner") DO NOT diverge.

**Refutation.** Laziness is incidental. What the defect needs is that the arm
whose EXIT edge lands on the already-seen epsilon state is the PREFERRED one.
A lazy quantifier achieves that by preferring its exit; a GREEDY nullable arm
achieves the same thing by being written FIRST in the alternation. Swapping the
two arms of the K18 entry's own control turns it into a witness:

    $ python3 ocheck.py pats_order.txt base A2 --alpha ab --len 3

    pattern            subject  base    A2      oracle
    (?:(?:b*|a)?)*     'ba'     (0,2)   (0,1)   (0,1)     <- NEW
    (?:(?:b*|a)?)*     'baa'    (0,3)   (0,1)   (0,1)
    (?:(?:b*|a)?)*     'bab'    (0,3)   (0,1)   (0,1)
    (?:(?:b*|a)?)*     'bba'    (0,3)   (0,2)   (0,2)
    (?:(?:b?|a)?)*     'ba'     (0,2)   (0,1)   (0,1)     <- NEW
    (?:(?:a|b*)?)*     -- no divergence (the entry's control, arms as written)
    (?:(?:a|b?)?)*     -- no divergence

    base disagrees with the oracle on 12 cells / 3 patterns; A2 on 0.

Confirmed by the SECOND oracle: `oracles2.py pats_order.txt ab 3` -> 120 cells,
**0 python-`re`-vs-libpcre2 disagreements**, so [0,1) is not a python artifact.

**Two further members with no lazy quantifier and no `?` wrapper at all**, both
oracle-confirmed and both fixed by A2:

    (?:(?:(?:b|)|a)?)*      on 'ba'  base (0,2)  oracles (0,1)   -- empty ARM
    (?:(?:b?|a)(?:b?|d))*   on 'ba'  base (0,2)  oracles (0,1)   -- CONCATENATION
                                                                    of two nullable
                                                                    alternations

The second one refutes a second control in the same list: K18's entry says
"`(?:a(?:b*?)?)*` (concatenation, not alternation)" does not diverge.

**Why this matters even though A2 fixes all of them.**

1. §1's defect analysis names the wrong ingredient. Anyone reading §1 to decide
   what the guard corpus must contain will build a lazy-only corpus, which is
   what already happened: all 15 patterns in
   `tests/known_fail/k18_empty_exit_through_seen_eps.rxt` carry the lazy shape,
   and the only two non-lazy entries (`(?:(?:a|b*)?)*`, `(?:(?:a|)?)*`) are
   there as CONTROLS. None of the three witnesses above is in that file.
2. §4.1's headline — "all 7 over-reach controls emit byte-identical C" —
   therefore proves less than it reads. At least one of those controls is
   non-diverging for an ARM-ORDER reason, not a structural one, and its mirror
   image is a live miscompile. A control that is one character away from a
   witness is not an over-reach control.
3. §5 item 1's guard corpus (the 8 shapes + 7 controls + the 83 `{0,2}`
   patterns) must gain an ARM-ORDER axis: every diverging shape with both
   alternation orders, and greedy as well as lazy nullable arms.

**In A2's favour, explicitly.** The note's own dense shape space DOES produce
`(?:(?:b*|a)?)*` (gen_shapes.py's `"%s|%s" % (inner, x)` order), so §4.3's
226/226 covers it; this is a defect in the note's PROSE and in the acceptance
corpus, not a hole in A2. A2 and the no-memo reference REF are correct on all
of them.

## S9 (OBSERVATION — the S3 corruption does NOT break §3's setup (ii), and here is why)

**Note's claim.** §3 setup (ii), **STRUCTURAL**: "the stack contains no repeats
(a re-arrival at an open loop redirects instead of pushing)". S3 shows the scan
can MISS a truly-open loop, which would push a repeat.

**Both sides measured.** `proto_a2_dup.py` = UNMODIFIED A2 plus a counter that
scans `open[0..depth)` for `s` before every push.

    python3 sweep_dup.py protos/a2dup/build/pcrec pats_r23.txt
    == 1001 patterns: dup>0 on 0; maxdepth>nfa+2 on 0; max maxdepth=5

**Zero.** And there is a structural reason, which the rewrite should record:
the slot the clobber overwrites is EXACTLY the slot of the loop whose redirect
is then missed. The clobber removes the entry that would have become the
duplicate, so a missed redirect pushes a loop that is (by then) genuinely
absent from the stack. The invariant survives the corruption by coincidence of
mechanism, not by design.

Contrast with S5's HALF-1, which removes the open-set test entirely: there the
invariant fails immediately and the stack overruns `openst`'s `nfa->n + 2`
sizing (SIGABRT, and SIGSEGV even at 20,000x capacity). So the two facts
together say: the open-set test is the ONLY thing bounding the stack, and it is
being fed a corrupted array. That is a thin margin for an unasserted invariant
on which §3's termination proof rests.

## S10 (BLOCKER) — §2a's `nonstacktop == 0` is REFUTED: the counter the note tells the rewrite to land AS AN ASSERTION fires on 358 of 4,369 patterns

**Note's claim.** §2a, "The stack is a stack, not a set", **MEASURED**:
"the prototype counts every redirect where the open loop was NOT the stack top.
**MEASURED: 0, over 555 corpus patterns and 52 adversarial patterns**,
including every nesting family up to 60 levels deep. **The rewrite should keep
that counter as an assertion rather than delete it.**" §5 item 6 repeats it:
"the `nonstacktop` counter kept as an assertion".

**Refutation, with both sides measured.**

    python3 sweep_nst.py protos/a2dup/build/pcrec \
        pats_r23.txt pats_r23b.txt pats_s1.txt pats_rev.txt pats_trie.txt \
        pats_min.txt pats_mix.txt

    == 4369 patterns; nonstacktop>0 on 358; total redirects 932894; max depth 13

`protos/a2dup` is UNMODIFIED prototype A2 (plus an inert dup counter), so this
is the prototype the note measured, not a variant of mine. Smallest witnesses,
all under 30 characters:

    (?:(?:(?:(?:a|b*)?)+){0,2})*        nonstacktop=60   (redirects=488)
    (?:(?:(?:(?:a|b*)?)*){0,2})*        nonstacktop=12   (redirects=220)
    (?:(?:(?:(?:(?:b|)|a)?)+){0,2})*    nonstacktop=16   (redirects=272)
    (?:(?:(?:(?:a|b*?)?)+)+)*           nonstacktop=84   (redirects=632)

**Reproduced the note's own 0, so this is not a harness disagreement:**

    python3 sweep_nst.py protos/a2dup/build/pcrec pats_corpus.txt pats_adv.txt
    == 692 patterns; nonstacktop>0 on 0; total redirects 153371

**The cause is S3, and this is the both-sides cell.** Running the SAME sweep
against `protos/a2sh`, which is A2 with the open-loop stack ENTRIES saved and
restored per frame (S3's fix) driving the decisions:

    corpus + adversarial (692):        nonstacktop>0 on 0
    my six corpora       (3679):       nonstacktop>0 on 0

and per-pattern, forward vs reverse machine:

    (?:(?:(?:(?:a|b*)?)+){0,2})*
        A2 discipline (corrupted stack) : fwd nonstacktop=0   rev nonstacktop=60
        correct stack                   : fwd nonstacktop=0   rev nonstacktop=0

So "the open loop is always the stack top" is TRUE OF THE DESIGN and FALSE OF
THE PROTOTYPE. The note measured 0 because its own corpus never produces a
three-loop-deep shape under a `{0,2}` — `gen_shapes.py` tops out at two loop
levels, and 555 corpus patterns have loop-nesting depth <= 5 with only two
patterns above 3, both of them K17's own guard tests.

**Why BLOCKER.** The note does not merely report this number, it instructs the
rewrite lane to ENFORCE it. A rewrite that follows §2a and §5 item 6 literally
lands an assertion that aborts the compiler on ordinary patterns — a
28-character regex on the reverse machine. The failure would be found by
`make test` only if the suite contains such a shape, and per §4.1 it does not.

**What has to happen before a rewrite lane opens.** Decide which of the two the
design actually is:
  (a) restore the stack entries per frame (S3), in which case `nonstacktop == 0`
      is a sound assertion and the note's MEASURED cell is correct as written
      once the prototype is fixed — but the note's cost table was measured on
      the UNFIXED prototype and must be re-taken; or
  (b) keep A2's discipline, in which case the redirect scan is a genuine SEARCH
      over a stack that may hold stale entries, `nonstacktop == 0` must be
      DELETED rather than asserted, and §3's setup (ii) needs a different
      defence (see S9).
Either way §2a's paragraph is wrong as it stands.

### S10 addendum — identical denominators, and what each binary measures

    same 4,369 patterns, same sweep:
      protos/a2dup (UNMODIFIED A2)                nonstacktop>0 on 358
                                                  649,242 -> 932,894 redirects
      protos/a2sh  (correct stack drives the walk) nonstacktop>0 on   0

A precision the panel should not gloss: `a2sh` runs a DIFFERENT WALK from A2
(its decisions come from the correct stack), so its redirect total is not A2's.
The comparison that matters is qualitative and holds either way — a walk whose
stack entries are correct never redirects at a non-top position on any of these
4,369 patterns, and A2's walk does so 932,894-649,242 = ~283k redirects' worth
of divergence later, on 358 of them.

Separating the two directions of the scan divergence on the CORRECT walk
(`proto_a2_shadow2.py`, counters `miss` = correct finds the loop open and A2's
stack does not, `fpos` = the reverse):

    (?:(?:(?:(?:a|b*)?)+){0,2})*   fwd: miss=0 fpos=0    rev: miss=52 fpos=0
    (?:(?:(?:(?:a|b*?)?)+)+)*      fwd: miss=0 fpos=0    rev: miss=64 fpos=0

Every divergence is a MISSED redirect, never a spurious one, and every one is
on the REVERSE machine. A missed empty-iteration redirect is, verbatim, the
defect K18 is. A2 does not currently produce a wrong answer from it (S3), but
the note's §1.2 sentence — "the memo kills it one hop short, so no rule stated
at loop entries can see it" — describes A2's own reverse-machine behaviour as
well as the shipped compiler's.

## S11 (OBSERVATION — survived, and it closes §4.6's reverse-machine gap for spans) — 81,840 cells with NON-ZERO match starts, A2 wrong on 0

**Note's claim.** §4.6, admitted gap: "**The reverse machine (D7) in isolation.**
It is exercised throughout ... but never singled out. `prune` is off there, so
the closure keeps every thread alive — a different code path through the same
walk."

**Why my earlier sweeps did not cover it either (self-criticism).** Every
pattern in the K18 family is fully nullable, so it matches at offset 0 and the
reverse machine's job — finding the EARLIEST accepting start — is trivially
answered. My S2/S4 corpora inherited that. `pats_rev.txt` fixes it: 240
patterns, each a K18-family shape with a MANDATORY leading atom
(`d`, `d+`, `[cd]`, `(?:d|c)`, `d?c`, `dd`) and an optional trailing loop, over
alphabet {a,b,c,d} with subjects to length 4 (341 per pattern), so the match
start is genuinely computed.

    == 240 patterns, 341 subjects each  (81,840 cells)
       base   disagrees with oracle on 1980 cells / 212 patterns
       A2     disagrees with oracle on    0
       REF    disagrees with oracle on    0
       A2FIX  disagrees with oracle on    0

This is where S10's missed redirects live, and A2 still gets every span right.
Recorded as a survived attack; combined with S10 it says the reverse-machine
defect is real in the MACHINERY and not (yet) observable in the ANSWERS.

**A harness defect of my own, disclosed.** The first run of this sweep reported
28,720 A2 "disagreements" that were an artifact: `ocheck.py`'s `run()` mapped
the generated matcher's `nomatch` (exit status 1) to the string `"RC1"` instead
of `None`, so every genuine non-match counted as a mismatch. Fixed
(`out == "nomatch" -> None`) and re-run; the numbers above are post-fix. It did
not affect S2/S4/S6/S8, whose patterns are all nullable and always match.

## S12 (MAJOR) — §3's "strictly stronger than K17's argument and subsumes it" does not hold: the new proof has a load-bearing premise K17's did not, and that premise is the one S10 shows is unguarded

**Note's claim.** §3, **BELIEVED**: "This is stronger than K17's argument and
subsumes it. K17's comment argues that the redirect graph is acyclic because
loop exits point outward past the loop — a statement about the NFA's shape that
has to be re-checked whenever a construction is added. The version above is a
decreasing measure on the walk's own state, so it holds regardless of what the
NFA looks like."

**Refutation.** The decreasing-measure half is fine and is correctly marked
STRUCTURAL. The comparative claim is not, for two reasons.

1. **The new proof needs setup (ii) — a finite context set — and K17's did
   not.** §3's own text derives finiteness from "the stack contains no repeats
   (a re-arrival at an open loop redirects instead of pushing)". That is a
   statement about the WALK, but it is only true if the redirect fires on every
   re-arrival at an open loop, which is a statement about the redirect scan
   reading an accurate stack. S10 measures that scan MISSING open loops on
   358 of 4,369 patterns. So the new argument trades one premise that has to be
   re-checked (NFA shape) for another that has to be re-checked (scan accuracy),
   and the second one is currently FALSE in the prototype.

2. **Measured, not argued: removing the open-set test alone loses termination.**
   S5's HALF-1 (context-keyed memo, shipped redirect trigger) SIGABRTs on
   `(?:(?:a|b*?)?)*` and still SIGSEGVs with the open-loop stack sized 20,000x.
   That is the concrete demonstration that setup (ii) is load-bearing rather
   than incidental, which §3 states in a parenthesis and does not defend.

Also worth noting for the panel: §3's claim that the measure "would survive a
future construct that made loop exits point somewhere surprising" is true of
termination but NOT of correctness. A construct whose loop exit pointed back
INTO the loop would keep the measure decreasing (depth still drops at each
redirect) while making the empty-iteration redirect land in the wrong place.
K17's shape-based argument would have caught that; the measure-based one does
not. "Strictly stronger" is the wrong word for a proof of a weaker property.

**Suggested re-mark:** §3's decreasing-measure argument STRUCTURAL (it is);
the "strictly stronger and subsumes" sentence deleted or downgraded, with
setup (ii) promoted from a parenthesis to an explicit obligation carrying the
assertion S3 asks for.

## S13 (OBSERVATION) — §2a's "(state, open-loop-SET)" is implemented as an ordered STACK, and the note never says which one is the invariant

**Note's claim.** §2a's heading and §1.4 both say the memo is keyed on
"(state, open-loop-set)"; `docs/dev/known_issues.md` K18 says the same
("key the memo on (state, open-loop-set)").

**What the prototype does.** `lctx_intern(ctxs, parent_ctx, loop)` interns an
ordered CHAIN, so two paths that hold the same SET of open loops in a different
ORDER get different context ids, and the memo does not merge them. Under proper
nesting the order is determined by the set, so today the two coincide — which
is exactly the situation §1.2 warns about for `seen`: "those two questions
coincide only when ...". The note should say which is the invariant and which is
the implementation, because the difference is a cost difference (more contexts
than necessary if order is spurious) and, if a future construct ever breaks
proper nesting, a correctness difference. The `nonstacktop` counter is the only
thing that would notice, and per S10 it does not behave as documented.

## S14 (BLOCKER) — the cost model is wrong on the axis that matters: a randomly generated 78-character pattern compiles in 0.118 s on the shipped compiler and does NOT finish in prototype A2, at a loop-nesting depth of ELEVEN. §6's D=64 threshold would not touch it.

**Note's claims.** §2a, **MEASURED**: "the cost law is Θ(d⁴) in loop nesting
depth, and it is polynomial, not exponential"; "The open set's cardinality is
the loop-NESTING depth"; the corpus distribution table (max 5); "the
compile-time risk begins somewhere past depth 64"; and §6 ruling 1, which asks
the panel to choose a NESTING-DEPTH threshold, recommending **D=64** "on the
grounds that it is 12x the deepest pattern in the corpus".

**Refutation.** I ran my random-grammar corpus (`gen_rand.py`, seed 20260815,
3,993 patterns after filtering for oracle cost) through the span sweep. One
pattern made prototype A2 exceed a 120 s compile budget:

    ((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,3}((?:[^a]*?|){1,2}?){2,3}){1,2}){2,3}

    shipped base : 0.118 s
    prototype A2 : still running at >20 minutes (900 s budget)

Shrunk while preserving the regression (`shrink.py`, criterion "base under 2 s
AND A2 over 15x base"):

    ((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,3}(){2,3}){1,2}){2,3}   62 chars
       base 0.116 s      A2 2.723 s        (23x)

**The counters say why, and they contradict §2a's cost model.** For the shrunk
pattern, per machine:

    forward : closures=28  visits=4,808      expansions=4,448      maxdepth=1   ctxs=19
    reverse : closures=82  visits=2,890,560  expansions=2,112,208  maxdepth=11  ctxs=2,834
              redirects=274,312   nonstacktop=83,904

Two facts the note's model does not have. (a) The effective loop-nesting depth
is **11**, not the 3 you can see in the source text: `{2,3}`, `{1,2}` and
`{0,k}` are lowered by `A_REP` (src/ir/nfa.c) into NESTED COPIES, and each copy
of a `+` body carries its own `frag_star`, so BOUNDED REPEATS MULTIPLY THE
DEPTH the open-loop stack sees. §2a's corpus depth table measures the same
unrolled quantity, but §6's threshold is offered to the panel in terms of
"nesting depth" as a reader would count it in the pattern.

(b) **Cost is driven by the CONTEXT COUNT, not by depth.** Sweeping the
bounded-repeat count k in `((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,k}(){2,3}){1,2}){2,3}`:

    k       base       A2         redirects    nonstacktop   maxdepth   ctxs
    2       0.111 s    0.315 s       47,664        16,192        9         450
    3       0.119 s    2.320 s      274,312        83,904       11       2,834
    4       0.123 s   17.835 s    1,056,992       272,576       11      11,770

From k=3 to k=4 the depth is UNCHANGED at 11 while the compile time goes up
7.7x and the context count 4.2x. A Θ(d⁴) law in nesting depth predicts NO
change. The real driver is the number of distinct open-loop contexts, which
grows with the unrolled copy count, and there is no threshold on d that bounds
it.

**Consequences for the ruling the note asks for.**

* §6 ruling 1 is posed on the wrong variable. **D=64 does not fire on any of
  the patterns above** (d = 9 or 11), so the recommended mitigation leaves a
  measured 17.8 s compile — and an unbounded one on the unshrunk 78-character
  original — in place. The note's own framing, "the compile-time risk begins
  somewhere past depth 64", is falsified at depth 11.
* §2a's "MEASURED: the cost law is Θ(d⁴) in loop nesting depth" is measured on
  ONE family (`(?:(?:...(?:a*)*...)*)*`, pure nesting with no bounded repeats).
  It is a fit to that family, not a law. It should be re-marked as such.
* §5 item 6's cost gates name two patterns: the fuzz-found
  `(1{0,30}?[^]abc][^abc]){28,30}0+|a` and nested-star depths 16/64/100/200.
  Neither family has this shape. The gate list needs a BOUNDED-REPEAT-times-
  nullable-loop row, and the honest threshold candidate is a CONTEXT-COUNT or
  expansion budget, not a depth one.
* §4.4's fuzz result ("A2 introduces no divergence and removes none", 2 seeds x
  400 patterns) did not surface this because a compile that does not finish is
  not a divergence. §5 item 6's "at least two fuzzer seeds" should be paired
  with an explicit COMPILE-TIME budget per pattern, reported as a count.

**Reproduce:**

    bash tt.sh '((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,3}(){2,3}){1,2}){2,3}'
    bash depthfam.sh          # the k sweep above
    PCREC_K18_STATS=1 protos/a2dup/build/pcrec -p rx -o /dev/null.c -- '<pattern>'

### S14 addendum — the k sweep extended, and the RATE at which random patterns hit this

    k       base       A2         redirects    nonstacktop   maxdepth   ctxs
    2       0.111 s    0.315 s       47,664        16,192        9         450
    3       0.119 s    2.320 s      274,312        83,904       11       2,834
    4       0.123 s   17.835 s    1,056,992       272,576       11      11,770
    5       0.115 s   52.353 s    3,566,648       849,344       11      40,422

Depth is CONSTANT at 11 from k=3 onward while A2's compile time rises 22x.

**Rate.** Over 3,993 randomly generated patterns with a 60-second per-pattern
compile budget, **4 exceeded it, all four under prototype A2 and none under the
shipped compiler**, which compiles the same four in 0.116 s / 0.618 s / 0.523 s
/ 0.924 s:

    ((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,3}((?:[^a]*?|){1,2}?){2,3}){1,2}){2,3}
    (?:(?:(?:.{0,3}|[^a]?)+(?:b?){0,2}(.*?))*[a-c]{2,3}(?:(?:d|[ab]*|c+){0,2}(?:.+?|[^a]+?|[ab]?|b*){1,2}){1,2}?){2,3}
    (?:(?:.{0,3}d+a*?){0,3}(?:a{0,4}?||d{2,3})+(?:.*?.*.??){0,4}?){0,4}?
    (?:[^a]{0,3}|c{0,3}|(?:(?:(?:a??c??)*?(.{1,2})*)*|(?:|.??|[a-c]{2,3}|(?:[^a]*?|a{0,4}?|c?){0,4}?)??){0,4}?|d{1,2}){2,3}

Every one of the four combines BOUNDED REPEATS with nullable loops. That is a
~0.1% rate on a generator with no knowledge of K18 at all, against §2a's single
fuzz-found cost regression which the fast path was built to remove. The fast
path removes the constant-factor problem; it does not touch this one.

## S15 (OBSERVATION — survived, the strongest single result for A2) — 3,993 random patterns, 159,720 cells: ZERO cells where A2 is wrong and the shipped compiler is right

**Direction accounting**, `run_rand.txt`, my random-grammar corpus, spans only:

    cells where A2 wrong and base RIGHT :   0
    cells where base wrong and A2 RIGHT :  41   (5 patterns)
    cells where BOTH wrong              :  46   (3 patterns)

The 46 both-wrong cells are NOT A2's and not K18's. All three patterns carry
CAPTURE groups and the generated matcher prints garbage spans — e.g.
`(32768, 140730569486088)` (a pointer) and `(4294967319, 0)` (2^32 + 23) —
identically under base and A2. That is the same signature §4.4 reports as
"already RED on the current tree ... generated matchers ABORTING with stack
smashing ... `{28,30}`-class bounded repeat over a capture-bearing body". My
witnesses are shorter and do not abort, they print uninitialised memory:

    ((?:(?:(?:d??|d+|a??|b{0,2}){0,3}|(?:[a-c]+[a-c]{2,3}[ab]?){0,2}|([ab]+)+){1,2}?)+?)?$
    (?:(?:(?:(c??){0,4}?(?:d{0,2}?a{0,2}){1,2}){0,3})+.(?:(d{0,2}){2,3}((?:[a-c]{1,2}?|b*?){1,2})?){0,2})*
    ^(?:(?:(?:[a-c]?|a+|[ab]+|){2,3}a*)*([^a]{1,2})+.??)?          (this one is a plain
                                                                     span error, (0,0)
                                                                     vs oracle (0,1))

Recorded here because it corroborates §4.4's out-of-lane report with an
independent generator and a much smaller witness, and because the panel should
not read "A2 wrong on 3 patterns" out of the summary line without the direction
table above.

**Second oracle on the same corpus.** `oracles2.py pats_rand_fast.txt abc 3`:
159,720 cells, **0 python-`re` vs libpcre2 disagreements** (7 cells excluded
where PCRE2 returns error -47, MATCHLIMIT — my first version of the tool
mapped every negative return to "nomatch" and reported those 7 as oracle
disagreements; disclosed and fixed).

**Cumulative oracle-vs-oracle evidence from this critic**: 754,320 (the note's
own 18,858 shapes) + 40,040 + 44,455 + 159,720 = **998,535 cells, 0
disagreements**. §4.6's judgement that one oracle is sufficient for a design
SCREEN is therefore MEASURED rather than believed — though D44's three-way rule
still binds the rewrite lane for its expectations.

## S16 (BLOCKER — the most important result in this review) — the note's ENTIRE COST RESIDUAL, including the 39-second worst case and the Θ(d⁴) law, is the S3 STACK-CORRUPTION BUG, not a property of the design. Fixing the stack makes the parser's deepest legal pattern compile in 0.42 s instead of 44 s.

**Note's claims, all MEASURED, all on prototype A/A2 as prototyped.**
§2a: "**The cost law is Θ(d⁴) in loop nesting depth**"; the wall-clock table
ending "250 (the cap) ... **39.25 s**"; "**This is a real, user-reachable
39-second compile where the shipped compiler takes 0.12 s, on a 1500-character
pattern.** It is the strongest argument for the threshold below, and it is why
this note asks for a ruling instead of assuming one." §2d: "its residual —
Θ(d⁴) beyond nesting depth ~64, topping out at a MEASURED 39.25 s at the
parser's nesting cap". §6 ruling 1 asks the panel to choose a nesting-depth
threshold, D=64 recommended, ON THE STRENGTH OF THAT NUMBER.

**Refutation.** `protos/a2fix` is prototype A2 with ONE change — `clo_visit`
saves the open-loop stack ENTRIES at frame entry and restores them at `done:`
(S3), a naive `malloc`+`memcpy` per frame, i.e. strictly MORE per-frame work.
Nested nullable stars `(?:(?:...(?:a*)*...)*)*`, my `nest.sh`, same box, same
compilers:

    depth   shipped base   prototype A2    A2 + stack entries restored
      16       0.116 s        0.122 s              0.122 s
      32       0.123 s        0.122 s              0.123 s
      64       0.123 s        0.323 s              0.116 s
     100       0.119 s        1.817 s              0.116 s
     200       0.116 s       26.645 s              0.323 s
     250       0.122 s       44.360 s            **0.419 s**   <- the note's 39.25 s cell

(My 44.4 s at depth 250 reproduces the note's 39.25 s within box noise, so this
is the same measurement, not a different one.)

**Counters, depth 200, same pattern:**

    prototype A2 : visits 137,570,342  expansions 2,746,234  redirects 132,156,704  ctxs 1,353,007
    stack fixed  : visits   2,870,018  expansions    41,818  redirects   2,787,200  ctxs    20,302

**48x fewer visits and 67x fewer contexts, for identical output.** Emitted-C
identity verified with `emitcmp.py` over a 32-pattern nesting ladder
(depths 1..250, greedy and lazy): **0 differ**. (An earlier spot-check that
appeared to differ was the `#include "<name>.h"` artifact of writing to two
different output paths, which `run_trie_identity.sh`'s own comment warns about;
re-run with `-o -` it is identical.)

**The same holds for S14's family**, which is not a nesting family at all:

    ((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,k}(){2,3}){1,2}){2,3}
      k=3    A2 2.321 s   ->  stack fixed 0.113 s
      k=4    A2 18.233 s  ->  stack fixed 0.120 s

**Mechanism.** A missed redirect (S3/S10) does not merely lose a rule — it
makes the walk EXPAND a loop it should have exited, which pushes that loop,
which creates a fresh context, which defeats the memo for the whole subtree
below it. The context explosion IS the missed redirects compounding. That is
why the corruption is simultaneously (a) invisible in the answers, (b) the
`nonstacktop` refutation of S10, and (c) 100x of compile time.

**What this does to the note.**

1. §2a's Θ(d⁴) "cost law" is a fit to the buggy prototype. It must be
   re-measured, not re-marked. On the fixed prototype the same family is
   0.42 s at the parser's own cap.
2. **§6 ruling 1 should not be put to the panel in its current form.** It asks
   Frank to accept a deliberately inexact compiler beyond a depth threshold, or
   to accept a 39-second compile, to mitigate a cost that a two-line correctness
   fix removes. On the evidence above the honest recommendation is **NO
   THRESHOLD** — with the stack fixed, the worst case a user can reach through
   the parser's 250-paren cap is 0.419 s, 3.4x the process-startup floor.
3. §2c's pricing of the memo (C vs A, Θ(2ⁿ)) and §2a's inflation table
   (x1.006 aggregate) were both taken on the buggy prototype. The x1.006 will
   only improve; the panel should still ask for it to be re-taken, because it
   is quoted as the reason the design is affordable.
4. §7's lesson — "an instrument that shares a failure mode with the thing it
   measures reports the instrument" — applies to this note one level up. The
   lane's defence was to check that the INSTRUMENTED build emits byte-identical
   C. That defence cannot see this, because the buggy prototype also emits
   byte-identical C. The cost numbers were measured against a correct-output
   oracle and were still measuring a bug.

### S16 addendum — the fix costs nothing where the note's own cost gates live

The note's §2a fuzz-found constant-factor pattern, which is what the empty-
context fast path was built for, is unaffected by the stack fix — and my
numbers reproduce the note's table cell for cell (its 0.61 / 13.33 / 0.82):

    (1{0,30}?[^]abc][^abc]){28,30}0+|a
      shipped base   0.613 s
      prototype A    13.434 s
      prototype A2   0.818 s
      A2 + stack fix 0.824 s      <- no regression

So the two mitigations are orthogonal: the fast path removes the per-probe
constant factor, the stack fix removes the context explosion. Both are needed;
neither substitutes for the other; and NEITHER is a reason to make the compiler
deliberately inexact past a depth threshold.

### S16 addendum 2 — every one of S14's four >60 s patterns compiles in under 3 s with the stack fixed

    pattern (truncated)                                  base      A2        A2+stack fix
    ((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,3}((?:...     0.116 s   >900 s      0.114 s
    (?:(?:(?:.{0,3}|[^a]?)+(?:b?){0,2}(.*?))*[a-c]...     0.618 s   >60 s       2.318 s
    (?:(?:.{0,3}d+a*?){0,3}(?:a{0,4}?||d{2,3})+(?:...     0.523 s   >60 s       1.323 s
    (?:[^a]{0,3}|c{0,3}|(?:(?:(?:a??c??)*?(.{1,2})...     0.924 s   >60 s       2.922 s

Prototype A (no fast path) on the first one was left to run to its budget:
**900.543 s, exit 124**, against the shipped compiler's 0.118 s.

Worst residual after the stack fix on this set is 3.2x the shipped compiler,
on a pattern the shipped compiler already spends ~1 s on. That is a normal
optimisation-pass cost, not a ruling-grade one.

Corpus aggregate over the 622 harvested patterns is process-startup bound on
this box (base 68.2 s, A2 68.2 s for 622 separate compiler invocations), so it
neither confirms nor contradicts §2a's 0.671 s / 0.662 s figures, which must
have been taken with a different harness.

---

# SEVERITY SUMMARY

    BLOCKER      3   S10, S14, S16
    MAJOR        3   S3, S8, S12
    MINOR        1   S7
    OBSERVATION  8   S1(hypothesis, promoted into S3), S2, S4, S5, S6, S9,
                     S11, S13, S15
                     — of which FIVE (S2, S4, S6, S11, S15) are attacks on A2
                       that FAILED and are recorded as evidence in its favour.

Evidence produced by this critic, all reproducible from
/tmp/claude-1001/-home-duxevents-pcrec/60beed03-a1ef-4a00-ba48-76e468397d0d/scratchpad/r23/semantics/ :

  * independently written generators (`gen_r23.py`, `gen_r23b.py`,
    `gen_rand.py`, `pats_trie.txt`, `pats_rev.txt`, `pats_nest.txt`), 11,000+
    patterns, none sharing a skeleton with `gen_shapes.py`;
  * my own span harness (`ocheck.py`) with a full subject cross product rather
    than the note's alphabet-derived 24;
  * a second oracle (`pcre2_span.c`, libpcre2 via the repo's dlopen shim) and
    an oracle-vs-oracle comparison over **998,535 cells, 0 disagreements**;
  * six new prototypes: `proto_a2_fix.py` (stack entries restored),
    `proto_a2_shadow.py` / `_shadow2.py` (both stack disciplines in one binary),
    `proto_a2_dup.py` (no-repeat invariant), `proto_ref.py` (no memo + fixed
    stack), `proto_half1.py` / `proto_half1b.py` / `proto_half2.py` (§1.4's two
    halves);
  * nothing was written to /home/duxevents/pcrec; every prototype was built
    into a scratch copy by the lane's own `mkproto.sh` with `K18_OUT` pointed
    at this directory.

== r23-semantics COMPLETE ==

# VERDICT

**A2 is semantically sound and NOT safe to hand to a rewrite lane as written.**
Those are not in tension. On the question the panel most needs answered — does
the recommended repair ever disagree with PCRE2 semantics — I attacked it as
hard as I could and failed: across ~11,000 independently generated patterns and
roughly 330,000 span cells, including a randomised grammar, a family built to
force non-zero match starts through the reverse machine, a trie/no-trie
crossing, and a no-memo reference walk, there are **zero cells where A2 is
wrong and the shipped compiler is right**, and A2 agrees with python `re` and
libpcre2 on every cell where either oracle has an opinion; the fast path, the
memo's exactness and the trie-identity gate all survived direct attack. But the
prototype the note MEASURED is not the design the note DESCRIBES. `clo_visit`
restores the open-loop stack's depth and not its entries, so a redirect that
crosses a frame boundary corrupts the ancestors' stack; that corruption makes
`nonstacktop`, the counter §2a reports as 0 and instructs the rewrite to land
**as an assertion**, fire on 358 of 4,369 of my patterns (S10) — a rewrite that
follows the note literally ships an assertion that aborts the compiler on a
28-character regex — and, far more importantly, it is the entire cause of the
cost residual the note builds §6's ruling request around: with one two-line fix
that only ADDS per-frame work, the note's headline "user-reachable 39-second
compile" at the parser's nesting cap becomes **0.419 s**, the Θ(d⁴) "cost law"
dissolves, and four randomly generated patterns that do not finish in 60 s
under A2 (one still running at 900 s) compile in 0.11-2.9 s (S14, S16). So
§6 ruling 1 should be withdrawn rather than answered — Frank is being asked to
authorise a deliberately inexact compiler beyond a depth threshold to mitigate a
bug. Two smaller repairs are also owed before a lane opens: §1's defect
characterisation names laziness as the ingredient when the real one is which
alternation arm is PREFERRED, so `(?:(?:b*|a)?)*` is a live miscompile one
character away from a pattern the K18 entry lists as a non-diverging control
and the 165-case acceptance corpus contains no member of that sub-case (S8);
and §3's "strictly stronger and subsumes K17" should be downgraded, because the
new proof's finite-context premise is exactly what the corruption breaks (S12).
Fix the stack, re-take every cost number on the fixed prototype, re-scope the
guard corpus by arm order, and A2 becomes a straightforward recommendation with
no ruling attached.

---

# R23 Measurement Critic Findings — K18 memo design note

Started: 2026-08-15

## M1 — BLOCKER: two of six adversarial families are silently absent from every "adversarial" measurement (generator bug, undisclosed)

**Note's claim** (§2a, "The stack is a stack, not a set"):
> **MEASURED: 0, over 555 corpus patterns and 52 adversarial patterns**, including
> every nesting family up to 60 levels deep.

The CLAUDE.md for k18_measurements/ describes `gen_adversarial.py`'s families as:
nest, nestlazy, chain, bounded, altnest, wide — six families — and specifically
calls out `altnest<N>` as "K18's diverging shape scaled up" (the family most
directly modeling the actual bug). `k18_memo_design.md` doesn't itself enumerate
the adversarial families by name, but leans on "52 adversarial patterns...
including every nesting family" to support the nonstacktop=0 invariant claim.

**What I ran:**
```
python3 gen_adversarial.py > adv_patterns.txt   # 70 lines
diff against outputs/stats_adv_A.tsv's pattern column (52 data rows)
python3 gen_adversarial.py 2>/dev/null | python3 k18_stats.py <shipped pcrec> /dev/stdin
```

**What I got:** `gen_adversarial.py` generates 70 patterns across 6 families
(nest×12, nestlazy×12, chain×12, bounded×10, altnest×10, wide×6, k18nest×8 —
actually 7 families, 70 total). Of these, **exactly 18 — all of `altnest1..10`
and `k18nest1..8` — are syntactically INVALID regexes** ("multiple repeat" /
pcrec's "multiple quantifiers on the same item"), because the generator appends
the outer `*` directly onto a string that already ends in `?` with no wrapping
group:

```python
for n in range(1, 11):
    s = "a"
    for _ in range(n):
        s = "(?:%s|b*?)?" % s
    out.append(("altnest%d" % n, s + "*"))   # BUG: needs "(?:%s)*" % s
```

`altnest1` is literally `(?:a|b*?)?*` — a `?` immediately followed by a `*`
with nothing between them. Both python3 `re` and pcrec reject it outright
("multiple repeat" / pcrec: "multiple quantifiers on the same item (pattern
offset 10)"). I confirmed this against the actual `build/pcrec` binary and
against the note's own worked example: `(?:(?:a|b*?)?)*` (the note's §1.3
pattern, correctly wrapped) compiles fine; `(?:a|b*?)?*` (what the generator
actually emits) does not.

Running `gen_adversarial.py`'s output through `k18_stats.py` against the
shipped binary reproduces this exactly: `patterns=70 refused=18 nostats=52`.
The archived `outputs/stats_adv_A.tsv` has 52 data rows and its pattern set is
EXACTLY `gen - {the 18 malformed altnest/k18nest patterns}` (verified: 0
patterns in the archive that aren't in today's generator output, 18 in the
generator output that aren't in the archive, all 18 from those two families).

**Verdict: DIVERGED from what the note implies.** The "52 adversarial
patterns" and "every nesting family up to 60 levels deep" in §2a's
nonstacktop=0 claim is true only of `nest`/`nestlazy`/`chain`/`bounded`/`wide`.
The two families whose entire purpose (per the CLAUDE.md description and the
`k18nest`/`altnest` names themselves) is to stress-test K18's own bug shape —
nested `(?:X|b*?)?` alternations, scaled to depth — contribute **zero**
patterns to the nonstacktop invariant check, the corpus-inflation numbers, or
any other §2a measurement, because they never compile. This is silent: nothing
in the note, the CLAUDE.md, or the archived MANIFEST.txt records the 18/70
refusal rate or that two full families are absent. `k18_stats.py` itself is
well-designed here — it does print `refused=18` to stderr exactly to prevent
this kind of silent shrinkage — but that stderr line was evidently not
carried into the note's prose.

This doesn't overturn the `nonstacktop=0` result on the patterns that DID run
(I have no reason to doubt that count), but it means the claimed coverage
("every nesting family") is false, and the family most on-point for the
specific worry (does the open-loop stack invariant hold on K18-shaped nesting,
not just plain nested stars) was never exercised at all. This should be fixed
(one-line generator fix: wrap in `"(?:%s)*" % s` for both `altnest` and
`k18nest`) and re-measured before the nonstacktop=0 claim can be trusted as
comprehensive.

## M2 — MAJOR: §4.4's fuzzer-red finding does not reproduce on current HEAD (concurrent fix landed, note not annotated)

**Note's claim** (§4.4, "The differential fuzzer, and a finding that is not mine"):
> the differential fuzzer is already RED on the current tree. The shipped
> compiler produces 347 and 442 content divergences on these seeds, across 8
> patterns each, and 23 and 12 of those cells are generated matchers ABORTING
> with `*** stack smashing detected ***`. Every one of the 8 patterns per seed
> carries a `{28,30}`-class bounded repeat over a capture-bearing body.

**What I ran:** `tests/fuzz/fuzz.py --seed 99 --patterns 400 --subjects 16`
and `--seed 5 --patterns 400 --subjects 16`, twice for seed 99 (once against
my own scratch-tar `base` prototype binary, once against the actual committed
`build/pcrec` in the repo, to rule out any drift from `mkproto.sh`'s tar/build
step). All read-only; the harness `--keep`s its own `/tmp` workdir, nothing
touches the repo.

**What I got:** all three runs — seed 99 (mkproto base), seed 99 (real
`build/pcrec`), seed 5 (mkproto base) — report **`content divergences: 0`,
`accept/reject divergences: 0`**, and no stack-smashing output anywhere in
the logs. The specific pattern the note names as the trigger for its A-vs-A2
timing regression, `(1{0,30}?[^]abc][^abc]){28,30}0+|a`, shows up in the
CURRENT run's **DFA state-cap** bucket instead — `pcrec: pattern too complex
for the DFA engine (>32000 states; VM engine arrives in M4)` — a clean
refusal, not a compile-then-crash.

**Root cause, from `git log`:** the K18 design lane branched at `9df434d`
and its final commit is `f4089d4` (2026-08-15 14:49:53 -0400) — that's the
commit the archived `outputs/MANIFEST.txt` pins as "repo commit". A
SIBLING branch, `fuzzfix`, ALSO starts at `9df434d` and its tip commit
`c225a9f` ("fuzz: fix shared-driver stack smash — read rx_info.ncaps at
runtime, not RX_NCAPS") is timestamped 2026-08-15 15:29:33 -0400 — about 40
minutes after the K18 note's numbers were taken — and its merge into main
(`7e27c19`, message: "differential fuzzer red root-caused and fixed —
runtime-ncaps shared driver (274 stack smashes → 0)...") lands *after* the
K18-design branch's own merge (`95cba2d`), but current HEAD (`ffff5e4`) has
BOTH merged in. So the stack-smashing the note reports as "not this lane's
finding... someone should decide whether it is K19/K20 fallout" was, in
fact, root-caused and fixed the same day by a concurrent lane — and the fix
is already on the branch the note lives on.

**Verdict: DIVERGED — this specific MEASURED claim is now FALSE on the tree
it's committed to**, through no fault of the note's own analysis (the note
correctly scoped it as "not caused by anything in this note" and asked for a
disposition). The problem is purely one of staleness: `docs/design/CLAUDE.md`
(the directory's own living index, which is supposed to track exactly this
kind of thing) still summarizes §4.4 without any annotation that the finding
has been resolved, and the note itself carries no update-in-place marker the
way `subst_template_design.md` and `engine_m4.md` do when overtaken by a
later ruling. This doesn't touch K18's own recommendation (A2, D=64
threshold) at all — it's entirely about a footnote — but per this project's
own "living design document" convention (`docs/design/CLAUDE.md`'s own
description: "panel-outcome blocks and refutations recorded inline"), a
resolved concurrent finding sitting unflagged in a still-open design note is
exactly the kind of drift a panel exists to catch before someone reads it as
current.

## M3 — MINOR: one isolated data point (d=97) in the Θ(d⁴) cost table doesn't reproduce; every neighboring depth does

**Note's claim** (§2a, nested-nullable-star depth table and the Θ(d⁴) ratio
text): contexts at d=97 = 151,911; states expanded at d=97 = 313,154;
redirects at d=97 = 6,966,548; and "the measured ratios 3.16, 2.45, 2.08
across d = 49→65→81→97 against predicted 3.10, 2.41, 2.06."

**What I ran:** built `nest(d)` for d ∈ {20, 30, 40, 49, 60, 65, 81, 97, 220}
using the note's own `nest()` construction (`gen_adversarial.py`'s function,
`inner="a*"`), ran each through prototype A with `PCREC_K18_STATS=1` three
times each to check determinism, and read the counters off the DOMINANT
(larger) of the two `K18STATS` lines per pattern — which is what the note's
table entries turn out to be (not `k18_stats.py`'s own SUM/MAX aggregation
across the forward+reverse machine, which I tried first and which produced a
spurious "systematic" mismatch at every depth until I corrected for it).

**What I got:** d=20, 30, 40, 60, 220 all reproduce their context, expansion,
and redirect counts EXACTLY — e.g. d=220: ctxs=1,798,507 (exact),
redirects=193,628,274 (exact), expansions=3,645,654 (exact). d=49, 65, 81
(used only for the ratio claim, not tabulated directly) give redirects
470,208 / 1,458,344 / 3,524,368, and MY ratios from those — 3.101, 2.417,
2.061 — land almost exactly ON the note's own "predicted" column (3.10,
2.41, 2.06), not on its "measured" column (3.16, 2.45, 2.08). d=97 alone is
off in all three counters simultaneously: I get ctxs=156,662 (note:
151,911, +3.1%), expansions=333,154 [aggregate] / 322,850 [dominant line]
(note: 313,154, +3–6%), redirects=7,262,200 (note: 6,966,548, +4.2%). This
is fully deterministic on my box — three repeated runs of the d=97 pattern
gave bit-identical counters each time — so it isn't run-to-run noise on my
end.

**Verdict: DIVERGED, narrowly.** Six of seven directly-tabulated depths
(20, 30, 40, 60, 220, plus the ratio-only 49/65/81 triple) reproduce exactly
or land closer to the theoretical d⁴ prediction than the note's own
"measured" figures do; only the single d=97 data point — which happens to be
the one that appears in BOTH the depth table AND the ratio sentence — is
off, by a consistent 3–6% across all three of its counters at once. That
consistency (not one field drifting, all three together) reads more like a
transcription slip (e.g. a stale intermediate run pasted into the table) than
environment drift, especially given every bracketing depth matches bit-for-
bit. **This does not touch the note's central claim** — my own numbers
independently confirm the cost law is polynomial (Θ(d⁴)) and not
exponential, and if anything validate the predicted-d⁴ column more cleanly
than the note's own quoted "measured" ratios do. Recorded because a
single-cell, unexplained, reproducible mismatch in an otherwise
bit-exact-reproducible table is worth the author double-checking, not because
it changes any conclusion.

## M4 — OBSERVATION: control independence checked, clean

Per this project's standing lesson (`pcrec-check-design-lessons`: every failed
check to date shared a source with what it controlled), I read every
measurement script for shared code/alphabet/parsing with pcrec itself:

* `oracle_cmp.py` — the oracle side is python3's stdlib `re` module, an
  independent implementation with its own parser and engine; the only thing
  it shares with the pcrec side is the SUBJECT alphabet (`subjects_for`
  derives candidate subject bytes from the pattern's own literal characters),
  which is a reasonable, disclosed choice (short subjects are deliberate
  per the docstring) and does not make the two sides' MATCH VERDICTS share a
  code path — only the same subject strings are fed to both.
* `gen_shapes.py` / `gen_adversarial.py` — pure combinatorial python
  generators with zero dependency on `src/`; they do not import or shell out
  to any pcrec code during generation (only at measurement time, via
  `k18_stats.py`/`emitdiff.py`/`oracle_cmp.py`, which invoke the CLI binary
  as an opaque subprocess).
* `emitdiff.py` / `k18_stats.py` / `timecmp.py` — all treat both binaries as
  opaque subprocesses (`subprocess.run([binary, ...])`); no shared in-process
  code between "what generates the measurement" and "what is measured".
* The one place this note is explicit about a NON-independent control and
  flags it as such: §4.3 states the dense shape sweep is "built only from
  K17/K18's ingredients" and is NOT a stand-in for real-input frequency —
  exactly the kind of honest scoping the project's lesson calls for, not a
  hidden shared-source problem.

The `nonstacktop` assertion counter (§2a) lives INSIDE the prototype whose
invariant it's checking (`proto_a.py` instruments its own `clo_visit`) — that
is unavoidable for a runtime invariant check (there's no external oracle for
"was the open-loop stack ever not the top"), but it's worth flagging as the
one place independence is structurally impossible rather than merely
unverified; the mitigating factor is that it's a hard assertion on an
`>` comparison over concrete integers, not a judgment call, so a false
"survived" result would require the counter itself to be wired wrong, which
`proto_basestats.py`'s byte-identical-output check does not cover (that check
only proves the BASE closure is untouched, not that A's own instrumentation is
honest). No test I ran surfaces evidence that it's wired wrong, but I note
this is BELIEVED, not measured, and mark it here so the panel doesn't read
"MEASURED: 0" as externally arbitrated.

## Survived: MEASURED claims independently re-derived and confirmed exact (or within stated noise)

All of these were re-run from scratch in `/tmp/.../scratchpad/r23/measure/`
(prototypes rebuilt via `mkproto.sh` with zero anchor-drift warnings against
current HEAD), independent of the archived `outputs/` directory:

1. Corpus harvest count: **622** patterns (`harvest_patterns.py`). EXACT.
2. Shape-space sweep count: **18,858** patterns (`gen_shapes.py`). EXACT.
3. §4.2 corpus blast radius (base vs A): **555 accepted by both, 547
   byte-identical, 8 differing, 0 accepted-by-only-one**, and the 8 differing
   patterns are the exact 8 named in the note. EXACT.
4. §2 basestats inertness: instrumented-shipped-closure emits byte-identical
   C to the real shipped closure on all 555 corpus patterns. EXACT (0
   differing).
5. §4.1 acceptance corpus: baseline **139 passed / 26 failed** of 165 (via
   the real `tests/harness/run.sh`, not just emitdiff); **A and A2 both
   165/165**. EXACT.
6. §4.1 "exactly 8 of 15 change their emitted C, 7 controls byte-identical":
   reproduced on the isolated 15-pattern file. EXACT.
7. §2a "A2 emits byte-identical C to A" on **all 18,858 shape patterns** and
   **all 555 corpus patterns**. EXACT (0 differing, both sweeps).
8. §2b A-vs-B emitted-source diff: **18,775 identical, 83 differing**. EXACT.
9. §4.3 base-vs-A diff over the shape space: **249 differing** (18,609
   identical). EXACT — and the 83-pattern and 249-pattern diff LISTS were
   fed straight into a fresh `oracle_cmp.py` run (not copied from the
   archive) and gave:
10. oracle A-vs-B: **98 cells differ, A right 98, B right 0, neither 0**.
    EXACT.
11. oracle base-vs-A: **226 cells differ, A right 226, shipped right 0,
    neither 0**. EXACT.
12. Fuzz-found regression pattern
    `(1{0,30}?[^]abc][^abc]){28,30}0+|a`: shipped 0.60s / A 13.41s / A2
    0.80s, against the note's 0.61 / 13.33 / 0.82. Within noise.
13. Its `{8,8}` shrink: basestats-vs-A counters bit-identical —
    closures=332476, visits=15743238, expansions=11714704 on both, and A
    alone adds maxdepth=1, ctxs=2 — matching the note's quoted numbers
    exactly, digit for digit.
14. §2a corpus loop-nesting histogram: **353/176/17/7/1/1** for open-set
    sizes 0–5. EXACT (`summarise.py` on a freshly-generated stats run).
    ctxs max **19**, 353 patterns need exactly 1 context. EXACT.
15. §2a inflation table: expansions **x1.006**, p50/p90/p99/max
    1.00/1.00/1.29/1.76, unchanged 527/554; visits **x1.001**,
    1.00/1.00/1.05/1.65, unchanged 482/554. EXACT, every field
    (`inflation.py` on a freshly-generated pair of stats runs).
16. Θ(d⁴) depth table at d = 20, 30, 40, 60, 220: contexts, states-expanded
    and redirects all reproduce EXACTLY (see M3 for the one exception, d=97).
17. Θ(2ⁿ) blowup of prototype C on `(?:a*|b*){n}`: n=16 0.41s (exact
    match), n=21 12.63s (exact match), n=22 hits the 3e8-visit budget and
    exits 97 with `K18BUDGET exceeded 3e8 visits` — exactly as the note's
    "budget" table cell says. (My first, sloppier attempt at this measurement
    — run concurrently with unrelated background jobs and without checking
    exit codes — spuriously showed n=22 completing in 20.83s; a clean
    re-run immediately after showed the correct budget-exit behavior. Noted
    here so the discrepancy doesn't look swept under the rug: it was my
    harness error, not the note's.)
18. Parser nesting cap: **250 nested `(?:...)*` wrappers compile, 251 are
    refused** with "parentheses are too deeply nested", against
    `PCREC_MAX_GROUP_DEPTH = 250` in `src/core/limits.h:125`. EXACT.
    (Minor/cosmetic: the note calls the resulting pattern "1500-character";
    it's actually 1,251–1,252 characters by my count for either the plain or
    `a*`-cored nest(250). Not marked as its own MEASURED number, so not
    filed as a separate finding — just noting it for the record.)
19. Timing table D=32/48/64/96/100/200/250: shipped flat at ~0.10s
    throughout; A2 at 0.10/0.20/0.30/1.40/1.60/20.52/**42.56**s against the
    note's 0.12/0.22/0.32/1.41/1.62/20.5/**39.25**s. Every point within
    noise except the endpoint, which ran ~8% high on my box — plausibly
    machine load from the concurrent background jobs this same measurement
    session was running (fuzzer + stats sweeps), not a reproducibility
    failure; still a real 42.5s, same order of magnitude, same conclusion.
20. proto_b.py's diff really is the claimed two-line, no-new-state change
    (read the anchored patch directly); proto_c.py really is proto_a.py plus
    memo-suppression removed plus a 3e8 visit-count abort. No script-vs-prose
    drift in either.
21. `PCREC_MAX_GROUP_DEPTH`'s STRUCTURAL claim (loop nesting requires
    parentheses, so d is capped by the parser's own group-depth refusal) — read
    `src/parse/parse.c:549` and `src/core/limits.h:125` directly; matches.

== r23-measure COMPLETE ==

## Addendum: full-suite corroboration (arrived after COMPLETE marker above)

Full `tests/harness/run.sh` (all `*.rxt` under `tests/`, `PROCS=6`) against
prototype A2: **cases passed: 1704, cases failed: 0** — reproducing the
note's "1704/1704 under A2" exactly. (Ran in the background per process
rules; took a few minutes.) This closes out finding-population item 9 above
with the actual test harness rather than just `emitdiff.py`'s byte comparison.

---

# R23 valplan/docs critic findings — K18 memo design note

Subject: docs/design/k18_memo_design.md (§4.4, §4.6, §5, §6, §7) + docs/design/k18_measurements/CLAUDE.md
Lens: validation plan / checks-tests / docs consistency
Status: STARTING


## V1 — MAJOR: §5/§4.6 never reconcile the note's own Θ(d⁴) worst case against the harness's EXISTING hardcoded 60s wall on pcrec's own invocation

**Claim/gap.** The note's headline residual risk is pcrec's OWN compile-time
blowup at deep loop nesting: Table in §2a "Cost: what the open-loop set
actually costs" measures **39.25 s at nest250** (the parser's own 250-paren
nesting cap) for prototype A/A2, against 0.12 s shipped. §5 point 6 asks the
rewrite lane to gate on "timing on the fuzz-found pattern... and nested-star
depths 16/64/100/200 as explicit gates" but never says against what existing
timeout budget those gates run, and §4.6 ("what I did NOT measure") does not
list this interaction at all.

**Evidence.** `tests/harness/run.sh:256`:

    pcrec_err="$(timeout 60 "$PCREC" -p rx ... -o "$bdir/gen.c" -- "$cur_pattern" ...)"

This wraps the pcrec INVOCATION ITSELF (pattern -> emitted C) in a bare,
hardcoded `timeout 60` — NOT D45's `GENTIMEOUT`/`GENTIMEOUT_SAN` mechanism,
which is `tests/lib/gen_timeout.sh` and applies only to compiling the
*emitted C with gcc* (confirmed: `gen_timeout.sh:34-35` keys off
`-fsanitize=` in the CFLAGS being passed to gcc, and run.sh:301-306's own
comment says "D45: the budget comes from tests/lib/gen_timeout.sh, not a
number here" — referring only to the `gen_cc` call at line 306, the GCC
build of gen.c, not the `timeout 60` three lines up at 256 that already
existed before D45 and was never folded into it). A non-perr timeout there
is scored `>= 124` -> "HARNESS FAILURE: pcrec crashed or timed out" (line
278), a hard failure, not a graceful skip.

Two consequences the note doesn't address:
1. **Margin is already thin on the plain axis**: 39.25s of 60s is 65%
   utilization on the note's own worst case, which is user-reachable per
   §2a's own STRUCTURAL/MEASURED nesting-cap argument.
2. **The sanitizer axis is unaddressed.** §5 point 7 asks for "`make ubsan`
   and `make asan`, both axes" — and docs/testing.md's SAN-1 section
   confirms pcrec ITSELF is the "COMPILER axis" instrumented by those
   targets (`docs/testing.md:799-806`: "the COMPILER axis — `pcrec` itself
   ... parsing, the registry, IR construction, codegen"). But the bare
   `timeout 60` at run.sh:256 does NOT scale for sanitizer builds the way
   `gen_timeout.sh` scales GCC's budget 5s->60s for `-fsanitize=`. If an
   asan/ubsan-instrumented pcrec pays even a modest constant-factor tax on
   a hash-heavy nested-context walk, the SAME nest250 case that MEASURED at
   39.25s plain could plausibly clear 60s under instrumentation and get
   scored as a HARNESS FAILURE by the very timeout meant to catch runaway
   compiles — which is exactly the "invisible because no compile had a
   bound" failure mode D45 was written to prevent, just on the wrong side of
   the D45/pre-D45 boundary.

**Proposed disposition.** Add to §5 point 6 (or as a new point) an explicit
requirement: (a) state which build (plain vs ubsan vs asan) the nest-depth
timing gates run against, (b) MEASURE nest100/200/250 under an
asan/ubsan-instrumented pcrec binary before committing to D=64 or any other
threshold, since the threshold's whole justification (§6 ruling 1, "0.32s
... a third of a second") is a plain-axis number, and (c) either fold
run.sh:256's `timeout 60` into `gen_timeout.sh`'s scaling mechanism (so it
becomes `GENTIMEOUT`-style axis-aware) or explicitly document why pcrec's
own invocation is exempt from the D45 discipline that governs every other
generated-code compile site enumerated by the SAN-1 GENCFLAGS audit.


## V2 — MAJOR: §6 ruling 1 recommends the exactness-losing fallback without citing D22, which already ruled against trading correctness for robustness against pathological (non-user-written) patterns

**Claim/gap.** §6 ruling 1 asks Frank to choose D=64 (silent fallback to the
known-buggy global memo beyond depth 64), a different D, or none (accept
39.25s worst case, always exact). The note recommends D=64 — i.e.
recommends trading EXACTNESS for a compile-time bound. The note's own
justification for wanting a bound at all is entirely about a pathological
case: §2a states plainly that the only two corpus patterns needing an
open-set >3 are "`(b*?(a*|b*)*)*` and `(?:b*?(?:(?:a*)*)*)*`, both of which
are K17's own guard-test patterns rather than anything a user wrote," and
the 39.25s worst case is measured at nest250, the PARSER's own nesting cap
— i.e. an adversarial/pathological shape, not a realistic one (corpus
maximum depth is 5).

**Evidence.** `docs/dev/decisions.md` D22 (2026-08-09, "adversarial
patterns are OUT OF SCOPE; correctness is not") is a standing ruling
directly on point: "contorting the design to survive an attacker is not a
goal and **should not be traded against execution speed**"; "The NFA and
DFA caps stay exactly as they are. They already do the right thing — **a
clean, attributable error instead of an OOM or a hang.** That is good
engineering for a legitimate too-big pattern, and it is enough." D22's own
prescription for exactly this shape of problem (a legitimate-but-extreme
pattern threatening a resource blowup) is REFUSE-with-diagnostic, not
silent degradation — which is precisely the "alternative shape" the note
itself floats in the same paragraph ("REFUSE past D rather than silently
falling back... fits D26's 'requires module X' habit") but then argues
against ("it refuses patterns that compile correctly today, which is a
bigger break than the fallback") without ever citing D22 as the standing
precedent that already weighed this exact tradeoff and came down on the
side of refuse-over-silent-degrade. `grep -n D22 docs/design/k18_memo_design.md`
returns nothing — the note never engages with it.

**Proposed disposition.** Before this reaches Frank as a ruling request,
add a paragraph connecting §6 ruling 1 to D22 explicitly: either argue why
K18's case is distinguishable from D22's precedent (e.g., D22 was about
NFA/DFA SIZE caps refusing at parse/compile-accept time, not about a
correctness/speed tradeoff on patterns that already compile) or default to
the REFUSE shape per D22's standing preference and make D=64-silent-fallback
the alternative requiring extra justification, not the recommendation.
Either way, the decisions.md entry this ruling produces (which the note
itself says is required) MUST cite D22 and state explicitly why it is
consistent with, or a deliberate narrow exception to, that ruling.

## V3 — MAJOR: D46 (observability/forceability of every strategy-selection point, ruled the SAME DAY) is never cited, and the D=64 threshold is exactly the kind of new selection point D46 was written to govern

**Claim/gap.** §5's validation plan never asks for an observability stamp
distinguishing "this compiled pattern's closures used the exact
path-sensitive memo" from "this pattern fell back to the global memo beyond
depth D" — even though the D=64 threshold recommended in §6 creates exactly
such a selection point. `grep -n "D46\|observable\|OBSERVABLE\|rx_info\|emit-ir\|forceable\|FORCEABLE" docs/design/k18_memo_design.md` returns nothing at all.

**Evidence.** D46 (`docs/dev/decisions.md:3940-3980`, ruled 2026-08-15,
twenty-first session — the SAME session/day as this note, per the note's
own "2026-08-15, K18 design-first lane" dateline in `docs/design/CLAUDE.md`)
states the general principle directly: "every selection the compiler
makes — engine ... cursor ladder RUNG ... bounded-repeat strategy ...
prefilter on/off, islands — is REPORTED in the artifact's reflection
surface"; its motivating scenario is a contrived test built to hit a
specific strategy that "would... be silently captured by [a different one]
— and the test would silently stop testing what it was written for." A
depth-D fallback in `clo_visit` is structurally identical: a sabotage-style
test built to probe the exact-memo behavior at, say, depth 70 would
silently exercise the OLD buggy global-memo path instead, with no stamp
anywhere (rx_info, RX_ENGINE-style macro, or `--emit-ir`) to tell the
rewrite lane's own §5-point-4 "sabotage-validated traps" whether they
landed on the intended path.

**Proposed disposition.** Add to §5 (as its own numbered item, alongside
point 7's ubsan/asan ask) a D46-compliance requirement: the threshold
selection (exact vs fallback) must be observable per-closure or
per-pattern in the artifact's reflection surface, and the rewrite lane's
own §5.4 sabotage traps for the D=64 boundary should assert the stamp
rather than assume construction implies which path ran — the same
correction D46's own "Consequences attached now" paragraph already applies
to [M4.5b]'s rung-boundary tests. This should be raised as part of, or
alongside, §6's ruling-1 ask, since the SHAPE of the threshold (silent
fallback vs observable/forceable) is what D46 governs, independent of
where D is set.

## V4 — MINOR: §4.5's ratchet-interaction requirement ("must move that file
into a live corpus directory... in the same commit") is stated forcefully
but never appears as a checklist item in §5, the section actually titled
"Validation plan for the rewrite lane"

**Claim/gap.** §4.5 states: "The rewrite lane's landing must move that file
into a live corpus directory and close the K18 entry in the same commit,
or `make test` stays red." This is exactly the kind of executable
requirement §5 exists to enumerate (brief's own framing: "does §5 cover...
the 165 tests/known_fail/ cases MOVING out of known_fail (the ratchet fires
if K18 is fixed — is that interaction handled?)"). `sed -n '562,611p'
docs/design/k18_memo_design.md | grep -n "ratchet\|known_fail"` returns
nothing — §5's seven numbered points never mention the known-fail
ratchet, the file move, or closing the known_issues.md K18 entry, even
though §5 point 1 ("A live `.rxt` guard corpus") is clearly the place this
belongs (it already discusses extending the 165+7 with the 83 `{0,2}`
patterns from §2b, but doesn't say those live IN
`tests/known_fail/k18_empty_exit_through_seen_eps.rxt` moved to a live
directory, vs. a new file).

**Proposed disposition.** Minor, low-cost fix: fold §4.5's requirement into
§5 point 1 as an explicit sub-bullet ("move
`tests/known_fail/k18_empty_exit_through_seen_eps.rxt` into a live corpus
directory, landing in the same commit as the fix, so the known-fail ratchet
does not fire red"), so a reader executing §5 as a checklist doesn't have
to separately remember a requirement stated three sections earlier.

## V5 — OBSERVATION (not a defect in the note, but relevant context for the panel): §4.4's "finding that is not mine" has ALREADY BEEN RESOLVED by the fuzzfix branch (commits c225a9f..7e27c19, merged 2026-08-15 15:31 EDT) — 32 minutes after this note's last commit (c162ee3, 14:59:53) — and the resolution CONTRADICTS the note's own BELIEVED attribution

**Claim/gap.** §4.4 reports the differential fuzzer red (347/442 content
divergences, 8 diverging patterns/seed, some aborting with stack smashing)
as "not this lane's finding," attributes it (marked BELIEVED) to "the
[M4.5] VM path... since I did not open a repro bundle," and asks: "someone
should decide whether it is K19/K20 fallout, a known-and-excluded fuzz
category, or a new K-entry."

**Evidence.** `git log` shows the fuzzfix branch (c225a9f, 89ccd89,
5cf31bc, 4639b4b, merged at 7e27c19, all timestamped 2026-08-15
15:29:33-15:31:32 -0400) landed ~32 minutes after this note's final commit
(c162ee3, 14:59:53 -0400) and `docs/dev/dev_journal.md`'s twenty-third
session reconstruction entry places both under the same crashed
twenty-second session, back to back, making the causal link explicit. The
actual root cause (`git diff 95cba2d..4639b4b -- tests/fuzz/fuzz_driver.c`,
and the merge commit message: "runtime-ncaps shared driver (274 stack
smashes -> 0)") was **not** the M4.5 VM path at all — it was
`tests/fuzz/fuzz_driver.c` declaring `ptrdiff_t caps[RX_NCAPS][2]` as a
stack array sized by a preprocessor macro baked in at the shared driver's
OWN ahead-of-time compile against a throwaway pattern, then reused
unmodified across every subsequent pattern regardless of that pattern's
actual (larger) `rx_info.ncaps` — a **test-infrastructure driver bug**, not
a defect in pcrec's emitted matcher code, and none of the note's three
candidate dispositions ("K19/K20 fallout, a known-and-excluded fuzz
category, or a new K-entry") names "fuzz-harness bug" as an option. The
note's own hedge ("I did not open a repro bundle") was well-calibrated —
the attribution was wrong precisely because that step was skipped, though
the answer was cheap to find once the bundle was opened.

**Docs-consistency angle.** Per this project's own convention for living
design docs (`docs/design/CLAUDE.md` shows every note in that directory
carrying PANELED/RULED/AMENDED annotations recording how open questions
were later resolved), `k18_memo_design.md` §4.4 and its `docs/design/CLAUDE.md`
summary paragraph both still read as though "someone should decide" is an
open question. Neither has been back-annotated with the resolution, even
though it happened same-session and is fully recorded in
`docs/dev/dev_journal.md`'s 2026-08-15 late-afternoon entry.

**Proposed disposition.** Not a blocker on this note's own content (the
finding was honestly marked BELIEVED and the note explicitly asked for a
decision, which happened). But before or during the R23 panel closes,
append a short annotation to §4.4 (and the `docs/design/CLAUDE.md` entry)
noting: RESOLVED 2026-08-15, fuzzfix branch, cause was
`tests/fuzz/fuzz_driver.c`'s stale-macro caps array, not the M4.5 VM path —
so a future reader doesn't re-open a question that's already closed, and so
the note's own BELIEVED mark on the VM-path attribution is corrected rather
than left silently wrong in the historical record.


## V6 — MINOR: §5 omits `make strict` and serial `PROCS=1`, both of which K17's own validation methodology explicitly ran and reported green

**Claim/gap.** The note frames §5 as "The K17 methodology, with the
additions this lane's own findings demand" — implying K17's methodology is
the floor, additions are on top. But K17's actual close record
(`docs/dev/decisions.md:174`, D44 table) states: "full `make test` +
`strict` green" — and `docs/dev/dev_journal.md`'s harness section documents
`PROCS=N` fan-out with "Serial and PROCS=6 runs measured identical" as part
of how this project validates harness changes don't depend on concurrency
accidents. Neither `make strict` nor a serial (PROCS=1) run appears
anywhere in §5's seven numbered points.
`sed -n '562,611p' docs/design/k18_memo_design.md | grep -n 'strict\|PROCS'`
returns nothing.

**Why it matters here specifically.** This lane's recommended design (A2)
introduces new hash-table/interner code with growth paths (§7 already
records one fixed-capacity table that HUNG rather than slowed when full) —
exactly the kind of new code where `-Wall -Wextra` and a serial run (to
rule out the new table's behavior depending on the PROCS fan-out's process
isolation) are cheap, high-value gates that K17 already established as
this project's floor.

**Proposed disposition.** Add `make strict` and a serial `PROCS=1` pass to
§5 (fold into point 6's "cost regression gates" or point 7's sanitizer
point — either location works), matching what K17's own close record
already reports as run.

## V7 — MAJOR: §4.6 ("what I did NOT measure") omits thread-safety of the new memo/interner tables, even though concurrent `pcrec_compile()` is part of the STANDING (non-opt-in) `make test` battery

**Claim/gap.** §4.6 lists exactly three unmeasured axes (captures, the
reverse machine in isolation, libpcre2 as a second oracle) and frames
itself as "where the risk sits." It says nothing about whether the new
context-interning hash table (§2a, §7) is safely SCOPED per `clo_visit`
call (stack/heap-per-compile) versus shared/static state that could race
under concurrent compiles. `grep -in 'thread\|tsan\|concurrent'
docs/design/k18_memo_design.md` returns only uses of "thread" in the
NFA-thread-list sense (the priority-ordered match-thread list `clo_visit`
emits) — never once in the concurrency sense.

**Evidence this is a real (not hypothetical) axis for this codebase.**
`tests/CLAUDE.md`'s `thread/` entry: "[TS-3] concurrent
`pcrec_compile()` on different patterns in different threads (library
built WITH TSan)... sabotage-validated with planted races." This is part
of the STANDING `make test` battery (not an opt-in leg like ubsan/asan),
so a new shared table introduced into the DFA-construction path is exactly
the kind of change TS-3 exists to catch — but only if the design actually
scopes the table correctly; §7's account of the interner's own history
(started as "a linear scan over all contexts," replaced with "a hash"
before final numbers were taken) never states whether either version was
per-call-local or file-scope shared state, and the design description in
§2a doesn't say either.

**Proposed disposition.** Add a §4.6 item stating this explicitly as
unmeasured-BELIEVED-or-unstated (matching the note's own honesty
discipline elsewhere), and add to §5 a requirement that the rewrite lane
either (a) confirms by construction that the new tables are allocated
per-`clo_visit`-invocation (stack or heap freed at closure end, never
static/file-scope) — a STRUCTURAL claim that should be citable to a line
number the way §2a's other STRUCTURAL claims are — or (b) if any part is
shared, runs it through `tests/thread`'s existing TS-3 harness before the
fix lands. Given TS-3 is already sabotage-validated infrastructure, this
is likely cheap to discharge, but the note currently doesn't even pose the
question.

## Clean checks (no defect found)

- **C1.** The 622-pattern harvested-corpus figure (§2, "the existing
  corpus") is exact: running `docs/design/k18_measurements/harvest_patterns.py`
  against the current tree reproduces 622 lines exactly.
- **C2.** The 165-case K18 acceptance corpus figure is exact:
  `tests/known_fail/k18_empty_exit_through_seen_eps.rxt` exists, has exactly
  15 `pattern` blocks and exactly 165 `m ` lines (subject/expectation
  pairs), matching the note's "165 pattern/subject pairs" and the file's own
  header comment ("165 pattern/subject pairs, both oracles, zero
  disagreements").
- **C3.** The 18,858-pattern dense shape-space sweep figure is exact:
  running `gen_shapes.py` with no arguments (its documented default,
  `lim = len(out)`) produces exactly 18858 lines.
- **C4.** `docs/design/k18_measurements/outputs/MANIFEST.txt` and its
  sibling files exist and are internally consistent with the note's cited
  numbers: `oracle_AB.tsv`/`.err` and `oracle_baseA.err` are described in
  the manifest as producing "A 98, B 0, neither 0" and "A 226, shipped 0,
  neither 0" respectively — matching §2b's "98 ... A agrees ... 98. B
  agrees on 0" and §4.3's "226 ... A agrees with the oracle on 226. The
  shipped compiler agrees on 0."
- **C5.** The 1704 "full `.rxt` suite" figure is not a number invented for
  this note — it is the project's own independently-tracked, repeatedly-cited
  corpus baseline (`docs/dev/plan.md:148`, `docs/dev/dev_journal.md:7958`
  and `:7999`, `docs/dev/wake.md:19,67`), most recently confirmed at the
  fuzzfix gate the same day ("corpus 1704/0"). Consistent.
- **C6.** `docs/design/k18_measurements/CLAUDE.md`'s file inventory matches
  the actual directory listing exactly (all `prototypes/*.py`, top-level
  harness scripts, and `outputs/` are present as described; nothing listed
  is missing, nothing present is undocumented).
- **C7.** `docs/dev/known_issues.md`'s K18 entry and `docs/design/CLAUDE.md`'s
  `k18_memo_design.md` summary paragraph are both consistent with the
  note's own content (repair direction, D=64 recommendation, cost law,
  blast-radius figures all match verbatim or in substance).
- **C8.** K18 being a pure DFA-construction bug, structurally separate from
  the [M4.5] VM engine (`tests/CLAUDE.md`'s `known_fail/` entry: "the VM's
  own §3.3 guard is a separate mechanism, so tests/vm exercising the K18
  family and passing is EXPECTED"), means the brief's "VM path vs DFA path"
  concern does not apply here as an omission — the two are already
  structurally independent by construction, and the note's scope (DFA-only)
  is correct as stated.

== r23-valplan COMPLETE ==

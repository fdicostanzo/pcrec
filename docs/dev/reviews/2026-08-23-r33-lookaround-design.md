# R33 — adversarial panel on docs/design/lookaround_design.md ([M6.6.1])

Target: lane/ladesign **9c10236** (design 2,133 lines; 9 probes archived under
docs/design/lookaround_measurements/). Panel convened 2026-08-23 14:3x by the
manager under D6: three read-only critics, distinct lenses, briefed to refute
and to measure both sides. Box rule during the panel: niced single-process
probes only (a mech matrix owned the cores). Full critic reports are appended
verbatim below the triage.

| critic | model | lens | HIGH | MED | LOW |
|---|---|---|---|---|---|
| C1 | opus | VM lowering + semantics vs libpcre2 (§2.3, §3, §4, §12) | 1 | 5 | 3 |
| C2 | opus | prefilter, engine selection, ENG-LOOK hand-off, gate + sabotage rows, §11 order (§5, §8-§12, §14) | 3 | 8 | 3 |
| C3 | sonnet | construct-table completeness, substitution driver, oracle facts, doc staleness (§2, §6.3, §7, §10, §13) | 1 | 3 | 1 |

## Triage (manager, 2026-08-23 15:0x)

Every finding is ACCEPTED as a design edit; none refutes the mechanism
(§0.2's "a sub-match whose result is a verdict and whose position is
discarded"). The fix round goes back to the design lane against 9c10236;
the panel's CONFIRMED lists (appended) stand as the design's measured core.

| id | sev | one line | disposition |
|---|---|---|---|
| C1-1 | HIGH | `v->fmin`/`v->fdyn` (the FOLLOW's minimum width) are baked into body prune bounds; a lookahead's follow overlaps its own bytes, so `(?!(a+)b)a+b` on "aab" prunes the body and answers a FALSE MATCH (0,3); §3.6 derives the non-atomic form by deleting the cut — where vm_atomic's scoping lives; no sabotage row | FIX: §3.2 rule — vm_look zeroes fmin/fdyn across every body emission and restores at exit, stated as a property of the OVERLAP not of the cut; §3.4 its own per-polarity ruling for lookbehind (inherited bound is sound for positive, verdict-flipping for negative); S-LA17 with the two predicted cells |
| C2-1 | HIGH | §5.8's sizing method: the unanchored forward DFA is ACCEPT-PRUNED (nfa.c:766-781, every accepting state a dead sink) — not the Σ*·L recognizer; under-counts (`a\|ab` 2 vs 3) | FIX: §5.8 states the method's defect; the table becomes a LOWER bound with the re-accepting machine's size re-derived (self-loop retained, or the powerset of L's NFA with the loop — say which) for the nine expansion bodies at least; the "0 over the cap" claim re-stated against the corrected sizes |
| C2-2 | HIGH | D65 flips `built` when the PORT answers at WANT_RESULT (syntax_dump.c:544-575), not when the emitter lands — wave B's "six rows still unbuilt" bar is unmeetable | FIX: fold wave B into C, or B's port refuses at WANT_RESULT; landing bars rewritten |
| C2-3 | HIGH | ~22 `case A_ATOMIC`-shaped walker arms in 10 files need an A_LOOK arm (-Wswitch); §5's ruling depends on two predicates not placed | FIX: §11 budgets the arms by file; names pcrec_has_bref/has_atomic/is_bare_anchor as the precedents and places pcrec_has_lookaround |
| C3-1 | HIGH | §6.3 Q4 is a substring test ("(?m:" etc.) — misses `(?im:` `(?i-m:`; inert today (count 270/8,495 reproduced exactly), corrupts cells on growth | FIX: parse the letter set each side of '-' in any `(?…:`; reuse mod_modifiers.c's parser |
| C1-2 | MED | §3.3 "no position slot" false for NEGATIVE lookbehind; composed shape undrawn | FIX: draw it |
| C1-3 | MED | non-atomic lookbehind shape undrawn; its top-level branch retry is observable | FIX: draw it, probe the retry cell |
| C1-4 | MED | §3.4 emits no `$_BACK_STEP_NONE` check, contradicting §4.2(3) and S-LA7 | FIX: reconcile |
| C1-5 | MED | §3.4's "end-check turns a silent wrong answer into a clean no-match" false for the negative polarity | FIX: per-polarity statement |
| C1-6 | MED | §3.7 back-step charge is per ATTEMPT POSITION; accounting sentence silent | FIX: say so |
| C2-4 | MED | §5.4 H1/H2 unfalsifiable by construction — a plumbing check, not evidence | FIX: relabel; §5.6 ruling 1 rests on §5.3+§5.5 |
| C2-5 | MED | S-LA10 masked: `\K` is not default-on | FIX: cell under `--features assertions,lookaround` |
| C2-6 | MED | §8.2's alpha-spelling fix moves three reject-table rows; wave F doesn't carry them | FIX: wave F carries them |
| C2-7 | MED | §9.3 assigns no SAB_SUITES; the two differential drivers get no mech arm | FIX: add both |
| C2-8 | MED | S-LA15/S-LA16 asserted, not specified | FIX: specify or drop ASK 1's appeal |
| C2-9 | MED | wave C's bar needs nonatomic.rxt, which needs D and F | FIX: reorder |
| C2-10 | MED | S-LA13 described backwards; `--emit-ir`'s description is a fourth reader | FIX: correct |
| C2-11 | MED | H3 window END modelled with libpcre2, never read off the emitted prefilter — C2 read it: CONFIRMS | FIX: put the emitted window numbers in §5.5 |
| C3-2 | MED | Q3 class walk mishandles leading `]` | FIX: consume one literal `]` after `[`/`[^` |
| C3-3 | MED | no Q-rule for `# pcre2-deviates` | FIX: Q6, costed 0/0 |
| C3-4 | MED | tests/assertions/CLAUDE.md:24 defines \Z as `(?=\n?\Z)` (circular) — correct `(?=\n?\z)` | FIX in [M6.6.2]'s doc sweep (not the design's file) |
| C1-7 | LOW | §2.7 \K needs its negative controls (legal AFTER a lookaround; refusal recursive) | FIX |
| C1-8 | LOW | §3.1 has five parse-resolved fields, not three | FIX |
| C1-9 | LOW | assertion-as-CONDITION interaction silent (refused by the conditionals doorway — say so) | FIX |
| C2-12 | LOW | S-LA5 names no row; detector must be capture-free | FIX |
| C2-13 | LOW | S-LA1 may be masked by possessify | FIX: body possessify cannot narrow |
| C2-14 | LOW | S-LA9 predicts a hang; it is PCREC_ERR_STEPS | FIX |
| C3-5 | LOW | tests/assertions/CLAUDE.md:53 goes false at landing | [M6.6.2] doc sweep |

STALENESS at landing (C3): APPROACH.md:145 (4 of 18 spellings); docs/pcre2_compliance.md:1208-1216 hand table + the generated index via compliance-refresh; annotations key `base:lookaround-verb-spellings`; tests/assertions/CLAUDE.md:24,53. Pre-existing, adjacent: compliance.md:1215 `[[:<:]]` row reads REJECTED while its annotation says shipped (MOD-0.3a).

ASKs for Frank (§14) — manager's recommendation to carry to him with the approved design: ASK 1 one node kind (with S-LA15/16 specified per C2-8); ASK 2 emit the end-check; ASK 3 dump rows for the six short alpha spellings; ASK 3a build the substitution driver in [M6.6.2]; ASK 4 `-fno-prefilter` third axis, `--no-captures` fourth.

## Round 2 — verifier (opus, r33v) on the fix round d6cdf16 (2026-08-23 15:4x)

All 25 round-1 findings applied by the design lane (none rejected; two came
back STRONGER when measured: C1-1's lookbehind half — exact counts take a
cursor rung with the follow-bound baked in; C3-1 — seven non-leading `(?m)`
blocks, population 270/8,495 → 263/8,260). The verifier independently
CONFIRMED all five HIGH fixes with its own probes (follow-scoping probe
byte-identical; an independent subset construction agreeing on every
modelled Σ*·L size; syntax_dump.c's per-row classification; the 23-site
`case A_ATOMIC` census, all in default-less switches; the substitution
population and three adversarial blocks) and EXTENDED C1-1's lookbehind
hazard from `a{3}` to exact-count groups generally (`((?:(?:ab){2}))c` 1 vs
`...cde` 3).

VERDICT: FIX-AGAIN — three text-only blockers introduced by the fix round:
V-1 §3.2.1 says "§3.6 restates" the scoping and §3.6 does not (the section
C1-1 named as the one that invites the deletion); V-2 §6.3's P1/P2 counts
270/368 are pre-fix and contradict their own 624 total (wave E2's bar
asserts against them); V-3 §11's folded B+C bar (three rows built, three
unbuilt) contradicts §8.3's "flips all six whatever the emitter does" — the
split needs the port to DECLINE the `<` tails at WANT_RESULT. Nine
non-blocking: V-4 F3's last row is a compile failure printed as a
measurement (`a(?=b+c)` refused → `[]`), V-5 §5.8's "everywhere else agree"
false (six rows without a prototype number; `(a|b)c` non-control under-count
3 vs 5; cap conclusion survives), V-6 four `default:`-carrying kind switches
`-Wswitch` won't flag (revdet.c:346, emit_vm.c:1108/1151/3018 — all sound
today, to be tabled in A2), V-7 S-LA17's anchor collides with vm_atomic's
idiom, V-8 "restores at L_next" → every return path, V-9 a PANEL OUTCOME
cite to §3.7 with nothing there, V-10 std1 is FROZEN so every lookaround
cell carries `features lookaround`, V-11 P-n order, V-12 `[^^]$` drops the
`$` in occurrences(). Round 3 dispatched to the lane (all twelve).

---

# APPENDIX — critic C1 report (verbatim)

# R33 critic C1 — the VM lowering and engine semantics against the oracle

Target: `worktrees/ladesign/docs/design/lookaround_design.md` at `9c10236`
(branch `lane/ladesign`). Lens: §2 semantic cells + §2.3/§2.4 preference
orders, §3 (emitted shape, negative form, captures, quantifiers, nesting,
budgets), §4 (the back-step seam entry), and the §12 predictions touching
these.

Oracle: libpcre2 **10.46 2025-08-27** through the lane's own
`lookaround_measurements/probes/la_oracle.py` (SELFCHECK clean, `[]`), python
`re` 3.14 as the second column. In-pcrec facts from
`worktrees/ladesign/build/pcrec` at `9c10236` and from reading
`src/gen/emit_vm.c` directly.

Probe scripts (mine, in this scratch dir): `p1_pref.py` `p2_caps.py`
`p3_nonatomic.py` `p4_fmin.py` `p5_silence.py`.

**Counts: 1 HIGH, 5 MEDIUM, 3 LOW.**

---

## C1-1 — HIGH — the lookaround body's FOLLOW-MIN is never scoped, and §3.6 deletes the only thing that would have scoped it

**The design's claim.** §0.2 and §3.5(3): *"everything inside the assertion is
ordinary emission, so every rung, every prune, every budget charge and every
future construct works inside a lookbehind on the day it works outside one,
with no second implementation to keep in step."* §3.2: *"its positive-
lookahead arm is `vm_atomic` (`emit_vm.c:4204-4292`) plus a saved position"*,
and *"THE TWO ADDED LINES ARE THE ENTIRE DIFFERENCE between `(?>ab)c` and
`(?=ab)c`"*. §3.6: *"The emitted shape is §3.2's with `vm_cut` not called."*

The words `fmin`, `fdyn` and "length prune" do not occur anywhere in the
document (`grep -n 'fmin\|fdyn\|prune' lookaround_design.md` returns two
hits, both about §5's prefilter WINDOW, neither about the body).

**The mechanism, MEASURED in-pcrec at `9c10236`.** `v->fmin` — the minimum
width of what FOLLOWS the node being emitted — is baked into a body's rung
bound as a literal:

```
build/pcrec -p rx --features all -o -  '(?:(a+)b)'        ->  if (RX_PRUNE_TOO_SHORT(rx_span_cursor, 1)) goto rx_fail;
build/pcrec -p rx --features all -o -  '(?:(a+)b)a+b'     ->  if (RX_PRUNE_TOO_SHORT(rx_span_cursor, 3)) goto rx_fail;
build/pcrec -p rx --features all -o -  '((?:aa|a)+)'      ->  if (RX_PRUNE_TOO_SHORT(scan_position, 1)) goto rx_fail;
build/pcrec -p rx --features all -o -  '((?:aa|a)+)bcd'   ->  if (RX_PRUNE_TOO_SHORT(scan_position, 4)) goto rx_fail;
```

The SAME body `(a+)b` gets bound 1 alone and bound 3 when `a+b` follows it.
`vm_mrl_test` (`emit_vm.c:2300-2311`) is the writer; `vm_poss_star`,
`vm_poss_chain`, `vm_rep`'s frames rung and the mandatory-copy gate all
consume `v->fmin`.

**The refutation.** A lookaround's follow starts at the assertion's ENTRY
position. For a LOOKAHEAD the body's bytes and the follow's bytes are *the
same bytes*, so `bodyremaining + v->fmin` double-counts them and is not a
sound bound on anything. `vm_atomic` avoids this by zeroing both terms
(`emit_vm.c:4244-4247`, restored at `4285-4286`) — but its own header
comment attributes that scoping to **the cut**:

> *"`(?>X)` matches X's OWN FIRST SUCCESS. Which success that is must be
> decided without consulting what follows the group… `v->fmin` is exactly
> such a peek."*  (`emit_vm.c:4198-4206`)

§3.6 derives the non-atomic form *by deleting the cut*. An implementer
following §3.6 has the design's own stated reason to delete the scoping with
it. §3.3 (negative) and §3.4 (lookbehind) are drawn as label shapes from
scratch and mention neither term.

**Predicted miscompiles, with libpcre2 10.46's answers (`p4_fmin.py`):**

| pattern | subject | PCRE2 10.46 | python `re` | with `v->fmin` live in the body |
|---|---|---|---|---|
| `(?=(a+)b)a+b` | `"aab"` | **(0,3), g1=(0,2)** | (0,3) | body's `a+` bound becomes 1+2=3; no cursor in 3 bytes clears it → **NOMATCH** |
| `(?!(a+)b)a+b` | `"aab"` | **NOMATCH** | NOMATCH | body pruned to fail → the negative assertion **succeeds** → **(0,3)**, a FALSE MATCH |
| `(?*(a+)b)a+b` | `"aab"` | **(0,3), g1=(0,2)** | ERR | same as row 1, and §3.6 is the arm most likely to lose the scoping |

The negative row is the dangerous one: an unsound prune inside a NEGATIVE
assertion turns "the body could not be shown to match" into "the assertion
holds", which is a **false positive**, not a missed match.

**The lookbehind needs its OWN ruling, and it is not the same one.** For
`(?<=X)` the body ENDS at the entry position, so an inherited `v->fmin` is
arithmetically *sound* (`cursor + bodyremaining + fmin == entrypos + fmin`,
which is exactly the real requirement) and is even a useful prune — but under
the NEGATIVE polarity an early body failure again flips the verdict, and
`v->fdyn` is a runtime term whose soundness is not obvious. So "the same as
the lookahead" is wrong in one direction and §3.5(3)'s "ordinary emission" is
wrong in the other; the design must pick, per direction and per polarity, and
today says nothing.

**No sabotage row defends it.** §9.3's S-LA1..S-LA16 cover the cut, the cursor
restore, the push order, the engine stamp, the seam, the sentinel, startpos,
`vm_nullable`, `\K`, the width rule, `mrl_win`, the three prefilter sites and
the three bool fields. None covers the follow scoping — so the one silent
miscompile in §3 has no detector.

**Fix (one line).** Add to §3.2: *"`vm_look` saves and zeroes `v->fmin` and
`v->fdyn` across every body emission and restores them at `L_next` — because
the follow's bytes OVERLAP the body's, not because of the cut, so the
non-atomic arm (§3.6) keeps the scoping when it drops `vm_cut`"*; give §3.4
its own sentence for the lookbehind; and add **S-LA17** (remove the scoping)
with prediction `(?=(a+)b)a+b` on `"aab"` red and `(?!(a+)b)a+b` on `"aab"`
answering (0,3).

---

## C1-2 — MEDIUM — §3.3's "no position slot" is false for the NEGATIVE LOOKBEHIND, and the composed shape is never drawn

**Claim.** §3.3: *"There is no capture snapshot and **no position slot**, and
P7 is why."* §3.4: *"The NEGATIVE lookbehind is §3.3's shape wrapped round
this one: the entry pushes `L_neg_ok` first, every branch's success falls into
`L_body_won`, and running out of branches falls through to `L_neg_ok` by
ordinary failure."* §3.7: *"The mark and position slots are **two** `stv`
slots per lookaround."*

**Refutation (by inspection of the design's own shapes).** §3.4's per-branch
end-check is `if (scan_position != (size_t)slot_values[SLOT_LOOK_POSk]) goto
rx_fail;` — it READS the position slot. Composing §3.3 literally ("no position
slot") onto §3.4 emits a negative lookbehind whose end-check compares against
a slot nothing wrote. The two sections cannot both be followed.

The slot count is inconsistent three ways as well: §3.3's negative lookahead
allocates 1 (mark only), §3.6's non-atomic forms allocate 1 (position only,
*"No mark slot is allocated for a non-atomic form"*), the negative lookbehind
needs 2, and §3.7 says "two per lookaround" flatly — which mis-sizes the `stv`
accounting §3.7 exists to state.

**Fix.** Replace §3.3's "no position slot" with "no position slot *for the
lookAHEAD*", and draw the four cells (ahead/behind × atomic/non-atomic ×
polarity) as one shape table with their slot counts, since §3.7's frame and
slot budget is derived from it.

---

## C1-3 — MEDIUM — the NON-ATOMIC LOOKBEHIND's shape is undrawn, and its top-level branch retry is observable

**Claim.** §3.6 is titled *"The NON-ATOMIC forms are the atomic shape MINUS
the cut"* and draws exactly one shape — the lookAHEAD's. §2.1 ships `(?<*X)`
and `(*naplb:X)`.

**MEASURED (libpcre2 10.46, `p3_nonatomic.py`), the discriminating cell:**

```
(?<*(a)|(ba))c\2   on "bacba"  ->  (2,5)  g1=unset  g2=(0,2)     <- retries into branch 2
(?<=(a)|(ba))c\2   on "bacba"  ->  NOMATCH                        <- atomic: branch 1 is final
(?<*(a)|(ba))c     on "bac"    ->  (2,3)  g1=(1,2)  g2=unset      <- written order still decides first try
(?<*(ba)|(a))c\2   on "baca"   ->  (2,4)  g1=unset  g2=(1,2)
```

So `(?<*` must, when the follow fails, retreat into a **later top-level
branch**, re-run `$_back_step` with *that branch's* width, and have branch 1's
captures undone. §3.4's branch chain plus "no cut" does deliver this (the
`RX_PUSH(&&L_b{i+1}, scan_position)` frames survive the assertion's exit and
the fail label rewinds their trail marks) — but the design never says that the
branch frames are *required* to survive, and §3.6's "No mark slot is allocated
for a non-atomic form" is the only sentence a reader gets about a
multi-branch non-atomic lookbehind.

The lookahead analogue is measured and agrees: `(?*(a)|(ab))\2` on `"abab"` →
(0,2) g2=(0,2) where `(?=(a)|(ab))\2` → NOMATCH.

**Fix.** State in §3.6 that for `(?<*` the per-branch frames of §3.4 are
load-bearing rather than discarded, and put `(?<*(a)|(ba))c\2` on `"bacba"` in
§10's `nonatomic.rxt` population — it is the only cell that separates the two
lookbehind atomicities across BRANCHES rather than within one.

---

## C1-4 — MEDIUM — §3.4 emits no `$_BACK_STEP_NONE` check, contradicting §4.2(3) and S-LA7

**Claim.** §4.2(3): *"The CALLER'S `scan_position < k` guard (§3.4) is then a
fast path and not the answer… the entry's sentinel is what makes it
correct."* §9.3 S-LA7 sabotages *"drop the `$_BACK_STEP_NONE` comparison,
keeping the `scan_position < k` guard"*.

**Refutation.** §3.4's canonical emitted shape — the one §11 Wave D tells the
implementer to build — is:

```
L_b1:  if (scan_position < k_1) goto L_b2;
       RX_PUSH(&&L_b2, scan_position)
       RX_CHARGE_WORK(k_1)
       scan_position = $_back_step(subject, subject_length, scan_position, k_1);
       goto L_body1
```

There is no sentinel comparison anywhere in §3, so S-LA7 has nothing to
delete and §4.2(3)'s "what makes it correct" is not in the design. Under a
UTF-8 backend the `scan_position < k_i` guard is inexact by construction (k
characters is *at least* k bytes, §4.2(3) says so), so `$_BACK_STEP_NONE`
reaches `scan_position` as `(size_t)-1`. The body's own
`scan_position < subject_length` guards make that a silent branch failure
rather than an out-of-bounds read — which is fine for `(?<=` (a declined
branch) and **wrong for `(?<!`**, where a declined branch is the assertion
holding (see C1-5).

**Fix.** Put the comparison in §3.4's shape —
`if (scan_position == $_BACK_STEP_NONE) goto L_b{i+1};` (or `goto rx_fail` on
the last branch) — so S-LA7 has an anchor and §4.2(3) describes emitted code.

---

## C1-5 — MEDIUM — §3.4's "the end-check turns a silent wrong answer into a clean no-match" is false for the NEGATIVE polarity

**Claim.** §3.4: *"if the width table is wrong, this comparison turns a silent
wrong answer into a clean no-match at that branch. That is a weaker outcome
than an abort and a much better one than a miscompile."* §14 ASK 2 recommends
emitting rather than asserting on that ground.

**Refutation.** The claim is polarity-blind and the construct is not. For
`(?<=X)` a branch declined by the end-check is conservative — the assertion
fails, and a failing assertion where PCRE2 succeeds shows up as a missing
match. For `(?<!X)` a branch declined by the end-check is the assertion
**succeeding**: a wrong `pcrec_maxw` (the module's one piece of genuinely new
analysis, §2.5) produces a **false match**, indistinguishable in the corpus
from a legitimate non-match of the body. The same holds for the sentinel path
in C1-4. So on the negative arm the end-check *is* the miscompile it is
advertised as preventing.

Everything else about P-4 holds — I could not find a node kind reachable in
§2.5's subset where `minw == maxw` and the consumed width varies (see
CONFIRMED-6).

**Fix.** Split ASK 2 by polarity: recommend the `assert()`-shaped abort (or an
`RX_R_*` return) for the negative arm even if the positive arm keeps the silent
decline, and make S-LA11's prediction include a `(?<!` cell, not only
`(?<=(a|bc))x`.

---

## C1-6 — MEDIUM — §3.7's back-step work charge is per ATTEMPT POSITION and the accounting sentence does not say so

**Claim.** §3.7: *"The back-step, `RX_CHARGE_WORK(k_i)` with `k_i` a literal…
Charging the compile-time constant rather than the runtime cost is
deliberate: it makes the artifact's work accounting independent of the
encoding backend."*

**Refutation.** True and incomplete. `RX_CHARGE_WORK` decrements a single
`run->work_left` (`emit_vm.c:5699-5712`) whose default is
`VM_DEFAULT_WORK_BUDGET = 1000000000LL` (`emit_vm.c:159`), and the charge
fires once per branch TRIED per candidate start. `rx_search`'s bumpalong
(`emit_vm.c:6244-6255`) walks every position, so a **leading** multi-branch
lookbehind charges up to `n · Σk_i`. With four branches of widths summing to
20 that is 2×10⁹ on a 100 MB subject — `PCREC_ERR_WORK` where PCRE2 matches.
This is a Σk multiplier on top of an already subject-length-dependent meter
(the macro's own comment says so), not a new class of behaviour, but §3.7 is
the section that owns the number and states only the per-call constant.

**Fix.** Add the `O(n · Σk_i)` shape to §3.7 with the 1e9 default beside it,
and put one long-subject leading-lookbehind cell in §10's population so the
bound is measured rather than reasoned about.

---

## C1-7 — LOW — §2.7's `\K` check needs its stated NEGATIVE controls: `\K` after a lookaround is legal, and the refusal must be recursive

**Claim.** §2.7: *"The refusal is a parse-time check in the module's hook:
while parsing a lookaround body, an `A_KRESET` node is an error."* S-LA10's
prediction names only `(?=a\K)b`.

**MEASURED (libpcre2 10.46, `p3_nonatomic.py` block K):** the refusal is
DEEP and the permission is REAL — both halves need corpus cells.

```
err 199:  (?=(a\K))x   (?=a(?:\K))x   (?=(?:(?=\K)))x   (?*a\K)x   (?<*\Ka)x
          (*pla:a\K)x  (*nlb:\Ka)x    (?<=\Ka)x         (?=a\K)x   (?!a\K)x   (?<!\Ka)x
compiles: (?=a)\Kb     a(?=b)\Kc      (?<=a)\Kb         a\Kb
```

A hook that rejects `A_KRESET` anywhere in the pattern once a lookaround has
been seen — the easy misreading of "while parsing a lookaround body" — breaks
the three compiling cells; one that only checks the body's immediate children
misses `(?=(a\K))x` and `(?=(?:(?=\K)))x`.

**Fix.** Name the three compiling controls and the nested-group /
nested-lookaround refusals in §2.7 and in S-LA10's prediction.

---

## C1-8 — LOW — §3.1 has FIVE parse-resolved fields, not three, and D62 control 3's obligation follows the other two

§3.1 lists `look_behind`, `look_neg`, `look_atomic`, `look_widths[]` and
`look_nbranch`; §3.1(a)/(b), §9.3 (S-LA14..S-LA16) and §14 ASK 1 all say
"three fields", one sabotage row per field. `look_widths[]`/`look_nbranch` are
parse-resolved state read by the emitter exactly as the bools are, and §3.1(c)
argues at length that they must be stored rather than recomputed — so the
"an analysis that pattern-matches `case A_LOOK:` and does not read the field"
hazard applies to them too.

**Fix.** Say "three flags and the width table"; either add a row for the width
table or state that S-LA11 (the parse-hook width rule) is its detector.

---

## C1-9 — LOW — the assertion-CONDITION interaction is silent, and it is the one a compliance reader will assume

`(?(?=a)ab|cd)`, `(?(?<=a)b|c)` and `(?(?!a)x|y)` are PCRE2 10.46 constructs
whose condition is a lookaround (measured: (0,2) / (0,2) / (1,2) / NOMATCH
respectively, `p5_silence.py`). MEASURED in-pcrec at `9c10236`, they route to
a different module and stay refused when `lookaround` lands:

```
build/pcrec … '(?(?=a)ab|cd)'  ->  module 'conditionals' is enabled but (?(...) is not implemented yet
build/pcrec … '(?=a)b'         ->  module 'lookaround' is enabled but (?=...) is not implemented yet
```

So the answer is right by construction — but §13's out-of-scope list never
says it, and §8.3's *"what the D65 `built` column will read, and the tally is
a deliverable"* is exactly where a reader would over-claim.

**Fix.** One bullet in §13: assertion-condition groups stay module
`conditionals` and are not unlocked by this module.

---

# CONFIRMED — claims I attacked and could not refute

1. **§2.4 level 1, "top-level branches are tried in WRITTEN ORDER"** — 24
   cells over 2- and 3-branch lookbehinds of mixed fixed widths, nested
   alternations inside a branch, class bodies and `{n}` bodies
   (`p1_pref.py` block A). Written order won in **24/24**, including every
   case where the shorter branch is written first and the longer is also
   viable: `(?<=(a)|(aa))c` on `"aac"` → g1=(1,2) vs `(?<=(aa)|(a))c` →
   g1=(0,2); `(?<=(\w)|(\w\w)|(\w\w\w))d` on `"abcd"` → g1=(2,3) vs the
   reversed spelling → g1=(0,3). **No cell picks the longer branch.**

2. **§2.4 level 2, "within one branch the step-back length is LONGEST
   FIRST"** — 9 cells reproduced exactly as the design reports them
   (`p1_pref.py` block B), including `(?<=(x|aa|a))c` on `"aac"` → g1=(0,2)
   (longest *viable*) and `(?<=(a|ba))c` on `"xac"` → g1=(1,2) (only length 1
   viable there).

3. **§2.5 / P-3, the subset asymmetry is REAL, not an accident.** The two
   spellings differ observably on the same subject:
   `(?<=(a)|(ba))c` on `"bac"` → g1=(1,2) (branch order, shorter first) while
   `(?<=(a|ba))c` on `"bac"` → g1=(0,2) (longest first). P-3's stated
   refutation — "find a subject on which `(?<=a|bc)x` picks the LONGER branch"
   — did not exist in 24 attempts. The ruling's ground stands.

4. **§3.3 / P-2, the negative form needs no snapshot.** STRUCTURAL, read
   rather than quoted: the fail label at `emit_vm.c:6062-6072` restores
   `scan_position` from the popped frame AND rewinds `trail_depth` to that
   frame's `trail_mark` before the indirect jump; `RX_PUSH`
   (`emit_vm.c:5773`, the untraced form, quoted in §3.3) records both at push time; and
   `RX_CUT` (`emit_vm.c:5783-5785`) is a **pure assignment** to
   `resume_depth` that touches neither the trail nor the slots. So popping the
   `L_neg_ok` frame restores cursor and captures with no extra machinery.
   MEASURED against 8 subjects designed to make a partially-captured failing
   body leak (`p2_caps.py` block E), including P-2's own "sharpest attack"
   shape — a capture written inside a negative body across a re-entered outer
   alternation: `(?:(?!(a))b|(a))` on `"a"` → (0,1) g1 **unset** g2=(0,1);
   `(?:(?!(a)(b))c|ab)` on `"ab"` → (0,2) both unset; `((?!(x))a)+` on `"aa"`
   → g1=(1,2) g2 unset. **Nothing leaks in any cell.**

5. **§3.2 property 3, captures inside a POSITIVE lookaround are retained on
   success and undone on an outer failure**, and both halves are needed:
   `(?=(a))a` on `"a"` → (0,1) g1=(0,1); `(?:(?=(a))b|(a))` on `"a"` → (0,1)
   g1 unset g2=(0,1). The lookBEHIND half too: `(?<=(a)(b))c` on `"abc"` →
   g1=(0,1) g2=(1,2) — spans entirely BEFORE the reported match start, which
   the emitted copy-out handles because `<prefix>_report_captures`
   (`emit_vm.c:6125-6143`) copies raw absolute `slot_values` and only
   `capture_spans[0]` is derived from `match_start`.

6. **§3.4 / P-4, the end-check cannot fire on a correct compiler for the
   shipped subset.** I could not find a second node kind reachable inside a
   §2.5-legal branch where `minw == maxw` and the consumed width varies:
   `A_BREF` is refused (§2.5), `A_KRESET` is refused (§2.7), every assertion
   kind and `A_LOOK` itself contribute 0 on every path, `A_REP` with
   `rmin == rmax` over a fixed body is fixed, and `A_ALT`/`A_CAT` are fixed
   iff their parts are. Degenerate `k = 0` works too: `(?<=a{0})x`, `(?<=)x`
   and `(?<=(?:))x` all → (0,1) in PCRE2 and fall out of the shape with
   `k = 0`. (What I did refute is the *consequence* of the check firing — see
   C1-5.)

7. **§3.8 / P-8, a lookbehind reads before `startpos` and it is free for the
   VM.** MEASURED: `(?<=ab)` on `"ab"` at **startpos 2** → **(2,2)**;
   `(?<=a)b` on `"ab"` at startpos 1 → (1,2); `(?<!a)b` same input same
   startpos → NOMATCH; `(?<=\w)a` on `"ba"` at startpos 1 → (1,2) while
   `(?<!\w)a` → NOMATCH (and `\ba` agrees, which is the assertions module
   already doing this). STRUCTURAL on the pcrec side: the emitted search sets
   `ctx.subject = subject; ctx.len = subject_length; ctx.pos =
   attempt_position` (`emit_vm.c:6243-6247`), so `subject` is the whole
   subject and `scan_position` is absolute — `pos - k` reaches below
   `search_from` with no plumbing. The loop also tries
   `attempt_position == subject_length`, which is what a whole-pattern
   lookaround needs: `(?<=ab)` on `"ab"` → (2,2), `(?!a)` on `"aa"` → (2,2).

8. **§2.6, quantified lookaround and the empty-iteration guard.** 16 cells
   across `*`, `+`, `{2}`, `{0}`, `*+` and both directions, all agreeing with
   PCRE2 and python (`p2_caps.py` block F): `(?=a)+` on `"a"` → (0,0),
   `(?=(a))*` on `"a"` → (0,0) with g1=(0,1) (one iteration's capture
   RETAINED), `(?!b){2}a` → (0,1), `(?:a(?=b))+b` on `"abab"` → (0,2),
   `(?<=(a))+b` on `"ab"` → (1,2) g1=(0,1). The mechanism the design relies on
   already exists and I confirmed it emits: `build/pcrec … '(?:\b)*+a'`
   emits `// unbounded repeat, greedy, frames rung, nullable body
   (empty-iteration guard)` — a zero-width assertion body under a POSSESSIVE
   quantifier is routed to the frames rung with the guard, so `A_LOOK`
   inherits it the moment `vm_nullable` answers true (S-LA9's claim).

9. **§2.3/§2.7's `\K` cells and err 199**, re-measured: all four polarities
   err 199 with the message naming `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK`, and
   `a\Kb` compiles as the control. Offsets 8/8/9/9.

10. **§2.1's ship/refuse split at the spelling level**, re-measured:
    `(*nanla:a)x` and `(*nanlb:a)x` are err 195 (as is the long form
    `(*non_atomic_negative_lookahead:`), `(?<!*a)x` is err 109, and
    `(?*a)x` `(?<*a)x` `(?<*a|bc)x` `(*naplb:a|bc)x` `(*plb:a|bc)x` all
    compile — so **there is no non-atomic negative form** and the
    length rule really is polarity- and atomicity-blind (`(?<*a*)x` is err
    125 like `(?<=a*)x`).

11. **§3.5's "forward body reuses `vm_emit` unchanged" pays off on the
    assertion cells inside a lookbehind body**, which the design does not
    claim but which the forward model gets for free and a reverse machine
    would not: `(?<=\Aab)c` on `"abc"` → (2,3) but on `"xabc"` → NOMATCH;
    `(?<=a$)b` on `"ab"` → NOMATCH; `(?<=a\b)b` on `"ab"` → NOMATCH;
    `(?<=\ba)b` on `"ab"` → (1,2); `(?<=\Ga)b` on `"ab"` → (1,2). Every one
    is what emitting the body forward at `pos-k` against the real subject
    produces.

12. **§4.1's sentinel is representable-safe.** `(size_t)-1` cannot collide
    with a legal position because a legal position is `<= n` and `n ==
    SIZE_MAX` is not a representable subject — confirmed by inspection of the
    entry signature and of `ctx.len`'s type. (The *call site* is C1-4.)

13. **§4.3 / P-1, the seam needs zero interface change.** I looked for the
    field, signature or caller §4's entry would force to move and found none:
    `PCREC_ENCE_BACK_STEP` is one enumerator, the byte row carries
    `engine_callable = true` off the existing struct, and nothing in
    `src/gen/enc/` is shaped per-entry. (C2's lens overlaps here; recording
    the negative result.)

# APPENDIX — critic C2 report (verbatim)

# R33 critic C2 — lookaround_design.md @ 9c10236 (lane/ladesign)

LENS: §5 (selection / prefilter / soundness / ENG-LOOK sizing), §8 (registry,
D65, the `(*` doorway), §9 (identity gate + sabotage rows), §10, §11, §12, §14.

Read-only. Nothing written inside the repo or its worktrees; `make` never run.
All commands `nice -n 19` + `/usr/bin/gnutimeout`. Scratch:
`/tmp/claude-1001/-home-duxevents-pcrec/b9a5b09a-f806-48a7-8ede-c2abbc6fd701/scratchpad/r33c2/`.

Counts: **3 HIGH, 8 MEDIUM, 3 LOW**, plus 7 CONFIRMED.

---

## C2-1 — HIGH — §5.8's sizing METHOD is refuted: pcrec's unanchored forward DFA is NOT the Σ*·L recognizer, and it UNDER-counts

**CLAIM (§5.8, and `probes/probe_englook_sizing.py:16-19`):**
> "The component a lookBEHIND body `L` needs is the recognizer for `Σ*·L`, and
> **pcrec's UNANCHORED FORWARD DFA for the pattern `L` IS that machine** —
> unanchoredness is the automaton's own self-loop (D58's 'Why' paragraph)."

**REFUTED, structurally and numerically.**

*Structural.* `src/ir/nfa.c:766-781`, `nfa_wrap_unanchored`, adds the self-loop
as the **LOWEST-PRIORITY** start alternative, and its own comment says why:
"Threads from earlier subject positions always outrank later ones, so **D3's
accept-pruning** yields the leftmost-first match end in one pass (D7)." Accept
pruning kills the self-loop thread at the first accept, so **every accepting
state in the emitted forward table is a dead sink**. Measured on the shipped
`worktrees/ladesign/build/pcrec`:

| body | forward states | accepting state's transition row |
|---|---|---|
| `foo` | 4 | state 3 = `-1, -1, -1` |
| `aa`  | 3 | state 2 = `-1, -1` |
| `ab\|b` | 2 | state 1 = `-1, -1, -1` |

A `Σ*·L` predicate machine must be **total** and must re-accept at every later
position: `(?<=foo)` has to answer YES at offset 6 of `"foofoo"` having already
accepted at 3. This machine stops answering after the first occurrence. It is
not the component; it is a *leftmost-occurrence search* automaton paired with a
separate reverse *start-finder*. `ab|b` shows the pairing directly: the forward
table has **2** states and its `a` transition returns to the start (the `ab`
branch is absent), while the reverse table has **3** (`"b"`, `"ba"`) — the two
halves are not the same language machine and neither alone is `Σ*·L`.

*Numerical — and this is the half that breaks the bound.* Truncation at the
first accept also deletes STATES whenever an alternation branch is
prefix-dominated:

| body | pcrec forward states (the probe's number) | minimal `D(Σ*·L)` |
|---|---|---|
| `a\|ab`   | **2** (`0`, `1="a" ACCEPTING`) | **3** (`ε`, ends-`a`, ends-`ab`) |
| `ab\|abc` | **3** (`0`, `"a"`, `"ab" ACCEPTING`) | **4** (`ε`, `a`, `ab`, `abc`) |

(Reproduce: `build/pcrec -p rx -o - 'a|ab'` → `rx_forward_is_accepting[2]`,
`rx_reverse_is_accepting[3]`; `'ab|abc'` → `[3]` / `[4]`. The forward/reverse
asymmetry the design's own table reports as "same" for most bodies is the tell.)

`§5.8`'s numbers are therefore not an upper bound on the component, and
`|D(main)| × Π|D(component)|` computed from them is not an upper bound on the
product. §5.8 says the bound "is the right quantity because the row's decline
rule ([ENG-CUT]'s shape: ESTIMATE BEFORE COMMITTING) must be written against a
bound and not a hope" — a decline rule written against an under-count declines
too little, which is the failure direction that matters. §2.5 ships
`(?<=a|bc)`-shaped bodies and `(?=a|ab)` outright, so the under-counted class
is inside the module's own population, not a corner.

**FIX:** delete the "IS that machine" identity. State that the emitted forward
DFA is the *leftmost-occurrence* automaton (accept-pruned, accepting states are
sinks), that `D(Σ*·L)` is a machine pcrec does not build today, and either (a)
mark §5.8's table PROTOTYPE/LOWER-BOUND and hand [ENG-LOOK] the construction as
its own first measurement, or (b) re-measure with the self-loop retained (the
DD-4 toggle `engine_m4.md` §7.3 already charters for `\G`) so the number is the
component's.

---

## C2-2 — HIGH — §11 wave B's landing bar cannot be met: D65 flips all six rows to `built` the moment the PORT is wired, not when the emitter lands

**CLAIM (§11 wave B):** *"Landing bar: … `--list-syntax` shows six rows still
`unbuilt`"*, with wave C's bar *"the four lookahead rows read `built`"* and
wave D's *"all six rows `built`"*.

**REFUTED.** §8.1 states the mechanism correctly — "derived per-construct at
dump time by driving each row's own `syntax` through a gate-forced-open doorway
call" — and then draws the wrong wave-level conclusion. The derivation is
`src/parse/syntax_dump.c:544-575`:

```c
ExtResult res = doorway_call(&cx, &d, WANT_RESULT);
...
if (res.what == EXT_NODE || res.what == EXT_MEMBERS || res.what == EXT_SCALAR)
    result = PCREC_BUILT_YES;
else if (res.what == EXT_REFUSAL && res.answered_at == WANT_RESULT)
    result = PCREC_BUILT_NO;
```

It classifies on the **parse doorway's returned `ExtResult`** and never runs the
emitter. Wave B's deliverable is exactly "`pcrec_laport_group` … the six
registry rows wired … the `A_LOOK` node kind", i.e. a port that returns
`EXT_NODE`. All six rows therefore read **`built`** at the end of wave B, while
"every accepted pattern hits the emitter's `ctx_fail`" (wave B's own text).

Two consequences, both worse than a wrong bar:

1. Wave B is described as "landable and testable on its own". As specified it
   lands a `--list-syntax` / compliance index that says `built` for six
   constructs that cannot compile — the precise lie D65's built column exists to
   prevent, and §8.3 commits to "zero rows move in the other direction".
2. Waves C and D's bars ("the four lookahead rows read `built`", "all six rows
   `built`") are then vacuous — they assert a transition that happened one or
   two waves earlier and would stay green under a completely absent emitter.

Also, in passing: only **three** of the six rows are lookahead-side (`(?=`,
`(?!`, `(?*`); wave C's "the four lookahead rows" miscounts.

**FIX:** either fold wave B into wave C (port + lowering land together), or have
wave B's port return an `EXT_REFUSAL` at `WANT_RESULT` until the emitter arm
exists and make the bar "six rows still `unbuilt`, and the refusal is the
enabled-but-unbuilt shape". Then restate C/D's bars as the real transitions.

---

## C2-3 — HIGH — the brief never budgets the ~22 AST-walker arms `A_LOOK` needs, including the two predicates §5's own ruling depends on

**CLAIM (§12 P-9):** *"One `A_LOOK` kind with three fields is right because all
three are read at ONE site. Refute by finding a second reader — `revdet.c`,
`possessify.c`, `altcls.c` and `atomic.c` are the four places
`atomic_groups_design.md` §6.5 found one."*

**PARTIALLY REFUTED / SCOPE GAP.** P-9 asks about the three *fields*; the
*node kind* is switched on at **23 sites in 10 files**
(`grep -rn "case A_ATOMIC" src/`):

```
src/opt/possessify.c  3   src/opt/revdet.c      4   src/opt/altcls.c   1
src/opt/atomic.c      5   src/opt/mrl.c         1   src/opt/select_engine.c 1
src/gen/emit_vm.c     5   src/ir/nfa.c          1   src/parse/parse.c  1
src/parse/mod_backrefs.c 1
```

§11 names only `mrl.c` (minw + new maxw), `nfa.c`'s epsilon arm and three
`emit_vm.c` arms. Unnamed and load-bearing for §5:

- **`pcrec_has_bref` (`src/opt/atomic.c:295`)** — the sole input to
  `select_engine.c:523`'s `has_bref`, which decides whether the prefilter is
  built at all. Its switch lists `A_CAP/A_REP/A_ATOMIC` as the descend cases and
  falls out to `return false` for anything else.
- **`pcrec_has_atomic` (`src/opt/atomic.c:37`)** — the other conjunct of the
  very predicate §5.6 is amending, and the guard on
  `pcrec_atomic_discharge` (`atomic.c:264`), which §5.6(4) says the new
  predicate must mirror ("asked of the POST-DISCHARGE tree").
- **`pcrec_is_bare_anchor` (`src/parse/parse.c:99`)** — decides whether a bare
  construct as a group's whole body gets wrapped so it can be quantified;
  §2.6 ships quantified lookaround and never mentions it.
- `select_engine.c:180`, `revdet.c` ×4, `possessify.c` ×3, `altcls.c`,
  `mod_backrefs.c:508`.

**Mitigation, verified:** **all 23** enclosing switches are `default:`-free
(read individually; `pcrec_is_bare_anchor` even documents the rule — *"No
`default:` — mrl.c:18-24's rule. A node kind added after this file is written
must be a COMPILE ERROR here"*), so adding `A_LOOK` to `AstKind` raises
`-Wswitch` at each. But `-Werror` is
deliberately not the default (`CLAUDE.md`, R5-Q1), so under a plain `make` these
are 22 warnings in a build log, and §11 mentions the `-Wswitch` alarm **only in
wave A** and only for the new `pcrec_maxw`.

**FIX:** add to §11's wave B bar: "adding `A_LOOK` raises N `-Wswitch`
diagnostics; the commit message states N and each is answered deliberately;
`make strict` green." Name `pcrec_has_bref`, `pcrec_has_atomic` and
`pcrec_is_bare_anchor` explicitly, and say where `pcrec_has_lookaround` lives
(`src/opt/atomic.c`, beside the other two — §5.6's snippet uses it and §11
never places it).

---

## C2-4 — MEDIUM — §5.4's H1 and H2 columns are UNFALSIFIABLE BY CONSTRUCTION; the "0 over 45 cells" is a plumbing check, not evidence

**CLAIM (§5.6 ruling 1):** *"The prefilter SHIPS. H1 and H2 hold at 0 violations
over 45 cells, so rejection and start-seeding are sound."*

**REFUTED as EVIDENCE (the property itself is true).** In
`probe_prefilter_hazard.py` the two columns are computed from libpcre2's
*leftmost-first* spans of `P` and `erase(P)`:

```python
h1 = "-" if es is not None or ts is None else "FAIL"
if es[0] > ts[0]: h2 = "FAIL"
```

Since `L(P) ⊆ L(erase(P))` at every position (§5.3's own one-line proof), `es is
None and ts is not None` and `es[0] > ts[0]` are both **impossible for any
population whatsoever**. There is no positive control for H1 or H2 and none can
be written — unlike H3, which has three planted families and a guard that fires
at 8. This is the lane's own named defect class ("a sweep population that could
not contain a qualifying row", §5.5 / `out/CLAUDE.md`) applied to its own
headline numbers, and §5.6 leans on them as if they were independent.

Compounding it: the same probe's IN-PCREC arm reports **prune ceiling `none` on
all 11** of its erasures (`out/prefilter_hazard.txt`), so none of the 45 cells
carries a live prefilter-window ceiling either. Every bit of load-bearing
measurement in §5 is §5.5's separate 16-of-30 sweep.

**FIX:** relabel §5.4's H1/H2 as ARGUED-with-a-plumbing-check (say the
comparison is analytically forced), and move §5.6 ruling 1's warrant onto §5.3's
proof plus §5.5. If a real H1/H2 instrument is wanted, it has to compare against
the **emitted** `rx_prefilter`, not against libpcre2 — see C2-11.

---

## C2-5 — MEDIUM — S-LA10 is masked by defence in depth: `\K` is not default-on

**CLAIM (§9.3 S-LA10):** delete the `A_KRESET`-in-body check ⇒ *"`(?=a\K)b`
compiles and silently reports a different match start; the reject-table cell
goes red."*

**REFUTED as written.** MEASURED on the lane's own build:

```
$ build/pcrec -p rx -o - 'a\Kb'
pcrec: \K requires module 'assertions' (pattern offset 1)
```

Module `assertions` is **not** default-on (`tests/reject/run_reject_tests.sh:1242`
pins `(?m)a` → `"requires module 'assertions'"`). Under the sabotage matrix's
default feature set `(?=a\K)b` is refused by the *assertions gate* whether or
not §2.7's check exists, and pcrec reports the LEFTMOST unhandled construct — so
the row goes green on a compiler with the check deleted. This is the S108 shape
exactly.

**FIX:** the S-LA10 detector cell must pass `--features assertions,lookaround`
(or `all`), and §9.3 should say so in the row. Sweep the other rows for the same
thing: S-LA1's `(?=(a|ab))\1$` needs `backrefs` enabled, and every `# pcre2-only`
row needs its differential arm actually assigned (C2-7).

---

## C2-6 — MEDIUM — §8.2's fix changes existing reject-table expectations, and §11 wave F does not carry them

**CLAIM (§8.2/§8.3):** the twelve alpha names take `M_lookaround`; *"everything
else inherits `verbs` and no other row changes."*

**REFUTED.** `tests/reject/run_reject_tests.sh:1355-1361`:

```sh
for v in '(*ACCEPT)' ... '(*script_run:a)' '(*sr:a)' '(*atomic:a)' '(*pla:a)' \
         '(*naplb:a)' '(*negative_lookbehind:a)' \
         '(*atomic:)'; do
    reject "$v" "requires module 'verbs'"
done
```

Three loop members — `(*pla:a)`, `(*naplb:a)`, `(*negative_lookbehind:a)` —
are lookaround alpha spellings asserted to answer `verbs`. Verified on HEAD:

```
(*pla:a)b                 => pcrec: (*...) requires module 'verbs' (pattern offset 0)
(*negative_lookbehind:a)b => pcrec: (*...) requires module 'verbs' (pattern offset 0)
```

After §8.2 these must say `lookaround`; after wave F they must **compile**, so
they leave the reject table entirely. §11's wave F bar says only "all twelve
refuse-or-compile with module `lookaround`" and never names the three rows that
have to move. (`reject '(*pla)'` at :1295 — `"(*alpha_assertion) not
recognized"` — is a FORM mismatch decided before module attribution and does
survive; the design should say which of the two it is, since a reader cannot
tell.)

**FIX:** add to wave F's landing bar: "the three `(*pla:a)`/`(*naplb:a)`/
`(*negative_lookbehind:a)` rows move out of `run_reject_tests.sh`'s
`verbs` loop; `(*pla)`'s form-error row is unchanged and is asserted so."

---

## C2-7 — MEDIUM — §9.3 assigns no `SAB_SUITES`, and the module's two differential drivers get no mech ARM

**CLAIM (§9.3):** rows follow S105's shape (`SAB_ID SAB_FILE SAB_SUITES
SAB_DESC SAB_BEFORE SAB_AFTER SAB_COUNT`); §11's close is "the FULL 118-row
matrix".

**GAP.** Not one of the 14 rows names its `SAB_SUITES`, and `tests/mech/CLAUDE.md`
is explicit that the arm list is closed and per-lane arms are added when a module
lands (`assertions` → `run_assertions_tests.sh`, "landed 2026-08-12"). §10.2
introduces `tests/lookaround/run_lookaround_diff.sh` and
`run_expansion_diff.sh` (the latter carrying **8,495 cells**, §10.1a's whole
depth instrument) and §9/§11 never add a mech arm for either — so the module's
largest correctness instrument is outside the matrix, and any sabotage whose
only signal is a differential disagreement scores UNDETECTED.

Good news, checked: `# pcre2-only` blocks ARE still executed by the `harness`
arm — `tests/harness/verify_rxt.py:121,388` skips only the *python oracle*
re-verification — so S-LA11 / S-LA16's `.rxt` cells are not skip-blind. The gap
is the drivers, not the corpus.

**FIX:** §9.3 gains a `SAB_SUITES` column; §11 wave E2 / wave F gain "a
`lookaround` mech arm (and a `laexpand` arm for the substitution driver) wired
in `run_sabotage_matrix.sh`, with the SKIP-is-not-a-pass verdict logic exercised
in the failing direction, as `pc3` was".

---

## C2-8 — MEDIUM — two of the sixteen sabotage claims are asserted, not specified

**CLAIM (§9.3, S-LA14's cell):** *"`.look_behind` and `.look_atomic` get
**S-LA15** and **S-LA16** on the same principle."*

**GAP.** The table has **14** rows. S-LA15 and S-LA16 have no file, no
BEFORE/AFTER, no prediction and no suite — and they are the control D62 requires
for §14 ASK 1's "one kind, three fields" recommendation, which the ASK then
cites as already settled ("with §9's three per-field sabotage rows as the control
D62 requires"). A control named but not specified is the shape §9.2 itself
withdraws a control for. (The panel brief says 19 rows; the document has 16
claims and 14 specifications — worth reconciling.)

**FIX:** write S-LA15 and S-LA16 out in full, or drop ASK 1's appeal to them.
S-LA16 in particular needs care: `.look_atomic` ignored ⇒ the non-atomic forms
behave atomically, which is observable only on the atomicity discriminator, i.e.
`nonatomic.rxt`'s `# pcre2-only` cells — so it also needs C2-7's arm.

---

## C2-9 — MEDIUM — §11's wave order: wave C's landing bar depends on waves D and F

**CLAIM (§11):** *"In order, each wave landable and testable on its own."*

**REFUTED.** Wave C's bar requires `nonatomic.rxt` green. §10.2 defines that
file as *"`(?*` `(?<*` and their `(*napla:`/`(*naplb:` spellings"*:

- `(?<*` is a lookBEHIND — the back-step is **wave D**;
- `(*napla:` / `(*naplb:` are alpha spellings — **wave F**.

So wave C's bar cannot go green until F. (Wave C's list of deliverables is
lookahead-only and consistent; it is the bar that reaches forward.)

**FIX:** split the file (`nonatomic_ahead.rxt` at C, the rest at D/F), or move
`nonatomic.rxt` to wave F's bar and give wave C the lookahead-only subset by
name.

---

## C2-10 — MEDIUM — S-LA13 is described backwards, and there is a FOURTH reader §5.6(3) does not count

**CLAIM (§9.3 S-LA13):** `src/gen/emit_vm.c` (**two sites**) — *"flip the
STAMP's source while leaving the two ceiling-building sites live"*.

**REFUTED (wording).** The stamp is one expression, `emit_vm.c:5603`
(`v.mrl_win ? "prefilter-window" : "subject-end"`). Flipping *its* source is a
ONE-site edit and does not need `SAB_FILE2`. The genuinely two-site sabotage is
the other way round: leave the stamp reading the flag and sabotage the **two
ceiling BUILDERS** — the retry recompute at `emit_vm.c:6176` and the search
entry at `emit_vm.c:6233` — which is what makes the stamp and the code disagree
in R31 E3's direction and needs `SAB_FILE2/BEFORE2/AFTER2`.

**Also:** §5.6(3) and the code comment both say "THREE SITES". `grep -n mrl_win
src/gen/emit_vm.c` returns **five** hits: `:5319` (assignment), `:5076`
(the `--emit-ir` prune-ceiling description), `:5603` (stamp), `:6176`, `:6233`.
The `--emit-ir` line at `:5076` is a fourth *reader* and a fourth thing that can
disagree with the code — `tests/codegen/run_ir_listing.sh` exists as its own mech
arm precisely because "the program listing cannot drift from the artifact it
describes".

**FIX:** restate S-LA13 as the two builders; add "`--emit-ir`'s description is
the fourth reader" to §5.6(3) and either fold it into codegen rule 1 or give it
its own row.

---

## C2-11 — MEDIUM — the H3 window END was modelled with libpcre2, never read off the emitted prefilter (the atomic lane did the opposite); I read it and it CONFIRMS

**CLAIM (§5.5):** *"MEASURED, `out/d66_subset.txt` S3 … with the erasure compiled
by the **shipped** pcrec and its `RX_VM_PRUNE_CEILING` stamp read off the
artifact."*

**INCOMPLETE.** Only the *ceiling-liveness* half is in-pcrec. The window END —
the number the ceiling actually becomes — comes from
`la.search(er, s, ts[0], PCRE2_ANCHORED)`, i.e. libpcre2. The precedent §5.5
invokes did it the other way: `emit_vm.c:5299-5301` records the atomic lane's
*"on the EMITTED prefilter rather than inferred from an oracle — 114 cells across
42 patterns carrying a 'prefilter-window' ceiling AND a window end strictly
BELOW the cut match's end"*.

I closed the gap. Compiled `((?:a|aq)(?:xy){0,4}q)` (the erasure of §5.5/§10.1's
own witness) with the lane's `build/pcrec`, called its `rx_prefilter` directly:

| subject | emitted `rx_prefilter` window | true match of `((?:a(?!q)\|aq)(?:xy){0,4}q)` (libpcre2 10.46) |
|---|---|---|
| `aqq`   | **(0,2)** | (0,3) |
| `aqxyq` | **(0,2)** | (0,5) |
| `aaqq`  | **(1,3)** | (1,4) |

and the artifact stamps `RX_VM_PRUNE_CEILING "prefilter-window"`. So the ceiling
really is 2 where the match ends at 3: **§5.6's ruling is correct and the hazard
is real in the default engine.** This is a strengthening, not a refutation — but
the design should carry these three in-pcrec numbers rather than the oracle's,
because §5.5's own argument is that an oracle stand-in is what the first version
of that sweep got wrong.

**FIX:** add the emitted-window column to §5.5's table; it is a 20-line probe.

---

## C2-12 — LOW — S-LA5 does not name which row it flips, and its detector must be capture-free

**CLAIM (§9.3 S-LA5):** *"flip one lookaround row's `engines` to `ANY_ENGINE`"*
⇒ *"`(?=a)b` on `"b"` answers (0,1)"*.

**CONDITIONAL.** SR-8 ANDs the per-row stamps, so flipping ONE of six rows only
frees patterns written with **that spelling** — the row must name it and the
detector cell must use it. And the cell must be **capture-free**: measured,
`(a)b` compiles to `RX_ENGINE "vm"` with `RX_VM_PREFILTER "hybrid"`, so a
capture-bearing detector keeps the VM regardless of the flipped mask and the
sabotage is masked. `(?=a)b` satisfies both; say so in the row.

---

## C2-13 — LOW — S-LA1's cut sabotage may be masked by `possessify.c`

**CLAIM (§9.3 S-LA1):** delete the `vm_cut` call from `vm_look`'s atomic arm ⇒
*"`(?=(a|ab))\1$` starts matching"*.

**RISK.** `src/opt/possessify.c` has 3 `A_ATOMIC` sites and is one of the four
second-readers §12 P-9 names. If the pass can independently possessify the
lookahead body's alternation, the choice points the deleted `RX_CUT` was meant
to remove never exist and the row goes green on a broken compiler — defence in
depth, S108's exact shape. Not confirmed either way here (no `A_LOOK` exists to
test), but it is cheap to make robust.

**FIX:** state in S-LA1 that its body must be one `possessify` provably cannot
narrow, and check that on the landed code rather than the sketch (§9.3's own
anchor-re-derivation rule, one step further).

---

## C2-14 — LOW — S-LA9's predicted symptom is probably `PCREC_ERR_STEPS`, not a hang

**CLAIM (§9.3 S-LA9):** `vm_nullable` returns false for `A_LOOK` ⇒ *"the matcher
**HANGS**. The row's suite assignment must therefore be one with a per-case
timeout (D45), and the row says so."*

**LIKELY WRONG.** Every VM artifact carries a step budget by default — the CLI's
own opt-out is `--fno-step-budget` ("emit no step counter at all"). A lost
empty-iteration guard should therefore burn the budget and return
`PCREC_ERR_STEPS`, not spin. That is *better* detection, but it changes what the
harness must treat as a failure (a give-up code, not a timeout) and it removes
the stated reason for the row's suite assignment.

**FIX:** re-predict against the budget; keep the timeout-suite assignment only if
`--fno-step-budget` is in play, and say which.

---

# CONFIRMED (with the probe for each)

**K-1 — the prefilter is leftmost-FIRST, so §5.4's anchored-PCRE2 stand-in is
faithful (§5.4's P16).** Compiled `(a|ab)` and `(ab|a)` and called the emitted
`rx_prefilter` directly: `(a|ab)` on `"ab"` → window **(0,1)**; `(ab|a)` on
`"ab"` → **(0,2)**. Alternation ORDER moves the window end, which a
longest-match DFA could not do. The model is right. (Note this is the *same*
mechanism as C2-1 — accept-pruning — which helps §5.4 and hurts §5.8.)

**K-2 — H1 and H2 are sound for the EMITTED forward+reverse pair, not just for
the oracle.** Read the emitted `rx_prefilter`: the forward scan commits to the
leftmost start (the self-loop is the lowest-priority alternative and is pruned at
the first accept), and the reverse walk is bounded by `if (rewind_position <=
search_from) break;` — so the reported start is ≤ any `P`-match start ≥
`search_from`. Rejection is a language question over a superset. Both hold.

**K-3 — §5.6(2)'s drop is SCOPED; a lookaround-free pattern loses nothing.**
`v.mrl_win` is a conjunction (`emit_vm.c:5319`), so `!pcrec_has_lookaround(root)`
is vacuously true on the existing corpus; and the other direction is already
asserted — `tests/codegen/run_codegen_tests.sh:1711-1725` rule 1c requires the
ATOMIC-FREE twin `(x)*(?:a|ab)c|abcd` to KEEP `prefilter-window` with ≥1
`window[0][1]` assignment. Extending rule 1/1c for lookaround is the right move.

**K-4 — §5.6(3)'s three ceiling sites exist and read the one flag today.**
`emit_vm.c:5603` (stamp), `:6176` (retry recompute), `:6233` (search entry). Rule
1 at `run_codegen_tests.sh:1667-1708` already asserts on BOTH sources
(`$ag_win == 0` AND stamp `"subject-end"`). (Fourth reader: C2-10.)

**K-5 — S-LA12 is reachable: a lookaround pattern gets a prefilter without
needing captures.** `select_engine.c:539`:
`fit.prefilter = has_bref ? false : … : (fit.chosen == ENGM_VM) && (cx->opt->engine != PCREC_ENGINE_VM)`.
Any auto-selected VM artifact without a backref gets the hybrid — no capture
requirement — so a VM-forced `A_LOOK` pattern carries one. Verified on the
witness: `((?:a|aq)(?:xy){0,4}q)` → `RX_VM_PREFILTER "hybrid"`,
`RX_VM_PRUNE_CEILING "prefilter-window"`.

**K-6 — §14 ASK 4: `-fno-prefilter` IS the right third axis.** Measured on
`(x)(?:a|ab)+d`: default → `RX_ENGINE "vm"` / prefilter `hybrid` / ceiling
`prefilter-window`; `-fno-prefilter` → `vm` / `none` / `subject-end`;
`--no-captures` → **no VM stamps at all** (the pattern compiles to the DFA
engine). So `--no-captures` would move the capture-bearing half of the
population off the very emitter this module edits, while `-fno-prefilter` keeps
it on the VM and varies only the ceiling. **Caveat worth adding to §9.1:** the
axis is *by construction* insensitive to the `v.mrl_win` edit (it pins the flag
false), so it cannot CATCH the module's only lookaround-free-population change —
the DEFAULT axis does, and the pair only localises. §9.1's sentence should say
"localises", not imply detection. ASK 4's fourth-axis suggestion (`--no-captures`
if cheap) is nearly free and near-worthless for the same reason.

**K-7 — `-Wswitch` will name the walker sites.** All 23 `case A_ATOMIC:`
switches are `default:`-free, so adding `A_LOOK` to `AstKind` is loud at every
one. This is the mitigation for C2-3, not a substitute for budgeting it.

---

# One-line fixes, collected

| # | fix |
|---|---|
| C2-1 | drop "IS that machine"; the forward DFA is accept-pruned and under-counts (`a\|ab` 2 vs 3) — mark §5.8's table a LOWER bound or re-measure with the self-loop retained |
| C2-2 | D65 flips on the PORT, not the emitter: fold wave B into C, or make B's port refuse at `WANT_RESULT` |
| C2-3 | budget the ~22 `-Wswitch` sites; name `pcrec_has_bref` / `pcrec_has_atomic` / `pcrec_is_bare_anchor`, and place `pcrec_has_lookaround` |
| C2-4 | relabel H1/H2 as analytically forced; §5.6 ruling 1 rests on §5.3 + §5.5 |
| C2-5 | S-LA10's cell needs `--features assertions,lookaround` |
| C2-6 | wave F must move the three `(*pla:a)`/`(*naplb:a)`/`(*negative_lookbehind:a)` reject rows |
| C2-7 | §9.3 gains `SAB_SUITES`; §11 adds mech arms for the two differential drivers |
| C2-8 | specify S-LA15/S-LA16 in full or drop ASK 1's appeal to them |
| C2-9 | wave C's bar must not require `nonatomic.rxt` (needs D and F) |
| C2-10 | S-LA13 is the two ceiling BUILDERS; count `--emit-ir`'s description as the fourth reader |
| C2-11 | put the emitted `rx_prefilter` window numbers in §5.5 |
| C2-12 | S-LA5 must name its row and use a capture-free cell |
| C2-13 | S-LA1's body must be one `possessify` cannot narrow |
| C2-14 | S-LA9 predicts `PCREC_ERR_STEPS`, not a hang |

# APPENDIX — critic C3 report (verbatim)

# R33 C3 (delivered in-message; saved by manager)
C3-1 HIGH  §6.3 Q4 scoped-modifier check is a substring test ("(?m:" / "(?-m" / "(?m-") — misses combined-letter groups (?im: (?mi: (?i-m: (?sm-x:; inert today (zero such forms in corpus; 270/468 blocks, 8,495/10,120 cells reproduced exactly), unsound on growth. Fix: parse the letter set on both sides of '-' in any (?...: spelling; reuse mod_modifiers.c.
C3-2 MEDIUM §6.3 Q3 class walk mishandles leading ']' ([]\b] — PCRE2 literal-first rule); inert today. Fix: consume one literal ']' after '[' / '[^'.
C3-3 MEDIUM §6.3 no Q-rule for `# pcre2-deviates` (D68 marker) — a qualifying deviating block would false-fail the A==C arm; inert today. Fix: Q6 exclusion, costed 0/0.
C3-4 MEDIUM tests/assertions/CLAUDE.md:24 defines PCRE2 \Z as (?=\n?\Z) — circular/wrong case; correct is (?=\n?\z) (108 cells/0 disagreements). Fix the line.
C3-5 LOW tests/assertions/CLAUDE.md:53 "module lookaround, which does not exist" goes false at landing.
STALENESS: APPROACH.md:145 lists 4 of 18 spellings; docs/pcre2_compliance.md:1208-1216 hand table rows REJECTED/PLANNED-HARD → OK / OK-LIMITED (fixed-per-branch) / alpha pending; generated index 1855-1867 via compliance-refresh; annotations key base:lookaround-verb-spellings ("module verbs") wrong after §8.2; match_api.md clean; registry.c:691-693,706 historical comment fine. Pre-existing: compliance.md:1215 [[:<:]] row REJECTED while annotation says shipped (MOD-0.3a).
CONFIRMED: population count exact (Q1 87b/0c, Q2 87b/754c, Q3 0/0, Q4 24b/871c, Q5 0/0); 18 ship / 3 refuse with err 195/109; max_varlookbehind 255 (err 200), fixed ceiling 32759 (err 120); \K err 199 all four; 14 quantified forms compile in python; 7 capture cells match python; 9 expansions python-clean; 6 registry rows VM_ONLY (580,581,599,600,601,707); (?(?=a)b|c) refused by conditionals doorway — out of scope; PCRE2_INFO_MAXLOOKBEHIND index 15.

# APPENDIX — verifier r33v report (round 2, verbatim, delivered in-message)

(verifier text appended by manager from the lane's message — see the Round 2 block above for the summary; the full text follows)

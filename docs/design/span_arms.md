# Span arms: the REP, EMPTY and positive-LOOKAROUND arms of the one fixed-width description

**Status: PROPOSED rev 0** (lane spanarms, opus, 2026-11-08; design and single-pattern
measurement only, no build go). Base: main `7b9ddd890` (every `file:line` below is at that
commit). Plan rows: [REPEAT-RUN], [REQ-EMPTYCAT] (its quantified half), [REQ-LOOKAROUND]; parent
note `docs/design/alt_normal_form.md` (its §3.5 arm table, §3.6, §9 rows S2-S4 and §10's "the
follow-up notes ... decision points listed, not decided" are what this note decides). Next in
Frank's 2026-11-06 order: [REWRITE-ADJ] after this note settles.

Evidence: `docs/dev/lanes/spanarms_evidence/` (`probe.sh`, the facts probe over the lane's own
build of `7b9ddd890`; `*.out`, its outputs; `oracle.out`, every expected answer quoted below,
from libpcre2-8 10.46 through `tests/lib/p2probe.c`). "Measured" means one of those files;
"predicted" means the spelled-out equivalent was measured (`xy(?:ab){2}zw` is predicted from the
measured run of `xyababzw`), never a hand count.

The note's one claim: **each of the three arms is ONE rule over the description, stated as a
language identity, so its soundness is the CAT arm's soundness and nothing new**:

- REP: `X{m,n}` IS `X^m · X{0,n-m}` and IS `X{0,n-m} · X^m` (two decompositions of one
  language); `X^m` is m copies through the CAT arm.
- EMPTY: a node that consumes nothing contributes the WIDTH-0 GROUP, CAT's unit; it is EXACT
  when it cannot fail and GUARDED when it can.
- positive LOOKAROUND: a guarded unit plus a GUARD, the body's fixed affix placed at its offset
  from the cursor; it INTERSECTS the consumed positions it overlaps and EXTENDS past them, and
  how far it may extend past the match is a REACH that each reader admits or refuses.

## 0. Premise tests (main `7b9ddd890`, all HOLD)

- **REP keeps only the body's best.** `rb_rep_into` (`src/facts/req.c:549-558`) builds
  `rr_none(rr_rep_w(rmax, ...))`, copies in `b->runs.best` alone and sets the description to
  `pcrec_pd_none()` with the comment "REP{n,n} is [REPEAT-RUN]'s (§3.5)" (`:557`). The `A_REP` arm
  (`:708-740`) takes it at `rmin >= 1` (`:721`) and a gap at `rmin == 0` (`:739`). Nothing is
  joined across an iteration. Measured: `A{4}` run none, `AAAA` `41414141`; `xy(?:ab){2}zw` run
  `ab` (2), `xyababzw` 8; `ab{3}c` none, `abbbc` 5.
- **The lookaround cuts the run.** `case A_LOOK:` (`req.c:761`) falls into `rb_row_into`
  (`:637-645`), whose `KTEXT_ZERO` arm calls `rb_assert_into` (`:627-631`): `rr_none(0)`, a cut,
  and the description `pd_none`. The header's reason is `req.c:56-61` (a lookbehind's bytes sit
  before the match start, possibly before `search_from`). Measured: `(?<=foo)bar` run `bar`,
  `bar(?=baz)` `bar`, `xyz(?<=yz)abc` `abc` (the consumed `xyz` cut too).
- **The EMPTY arm is not built either.** `case A_EMPTY:` is in the same cut list (`req.c:756`);
  stage 2a of alt_normal_form is census-first and unbuilt (plan [RUN-POS-SET] status
  2026-11-07). Measured: `abcd()efgh`, `abcd(?:|)efgh`, `abcd(?:)*efgh`, `abcd(?:){3}efgh`
  all run `efgh` (4). Not a STOP: the brief asks what remains after 2a's move; §4 keeps 2a's
  direct half as its first row, unchanged, and designs the rest.
- **The description module has no power or guard arm.** `src/facts/desc.h:41-45`: unit,
  none, pos, cat, alt. The adjacency head's REP arm is a WALL (`src/opt/altnf.c:223-230`,
  alt_normal_form §3.5 r7 FIX-1: "a REP head waits for [REPEAT-RUN]").
- **The SPAN facts already see through repeats.** `span_facts` and `kset_walk`
  (`src/facts/kset.c`, NFA-level, shape-blind) report `A{4}` as `4:65,65,65,65` and
  `xy(?:ab){2}zw` as `8:120,121,97,98,97,98,122,119`, identical to the spelled forms. So
  [REPEAT-RUN]'s "span analysis" half is ALREADY true; its run half is not. Both decline on a
  lookaround (`decline:erased-nfa`), except where the NFA itself narrows a one-character
  context (`a(?=b)[bc]` span `2:97,98`).
- **What the window site carries today (D172).** The window statement admits span starts in
  `[-MF_MAX_BACK, MF_WREACH)` = `[-8, 64)` (`memfn/include/memfn.h:235`, `:586-591`), checked
  loudly at `src/gen/memfn_sites.c:587-592`. pcrec states exactly two negative starts, both
  `-1`: MLINE's predecessor stop `{-1: \n}` (`src/gen/emit_dfa.c:8393`; `find_site` refuses any
  other negative offset, `:6909`) and the cover site's context-before side (`src/gen/known.c:465`,
  `MkEnd.ctx_before`, a MACHINE fact read off the anchored DFA, `src/gen/known.h:25`). The run
  span R (`pf_window_of`, `emit_dfa.c:6815-6871`) never starts below 0: `walk_proves` refuses
  `d < 0` (`:6809`). No lookbehind body's bytes are stated anywhere; D172's "fixed lookbehinds
  ... longer than 1 come with it" is unbuilt. The one existing "step back by the lookbehind"
  precedent is the UTF check (`emit_dfa.c:745-749`, `<prefix>_VALID_LB` = `Ctx.lb_max`,
  `:3610-3617`).

## 1. Goals

Ranked; the higher wins a conflict.

| # | goal | who benefits | measurable form (comparison, margin) |
|---|---|---|---|
| G1 | No answer moves | every caller | answer identity over corpus + bench, every encoding and axis (`make test`, `make test-axes`), PC-3 unchanged; margin 0 |
| G2 | Each arm is ONE rule in the one description | maintainers | per unit, the ledger (§9) lists the special cases deleted and the arm rows added; no second walk, no per-construct clause (`A{4}`, `(?:)*`, `(?=..)` are rows of one arm each); the reader of the description stays `req.c`'s one walk |
| G3 | No reader reads a run outside its admitted reach | every caller | every reader of a moved fact is in §5.4's admission table with its reach; a unit that widens a reach names the reader and its witness; unlisted reader = red at review |
| G4 | D186's bar per unit, per regime | users with pinned performance | each unit declares its kind (fact / choice) per regime; a choice unit: no regime loses beyond noise on every bench cell whose pick moved |
| G5 | The movers are the census's | the build lane, the critic | each unit's emitted movers equal an independent model's list (two-sided) over corpus + bench, both encodings; this note's predicted movers (§3.5, §4.5, §5.6) are the model's spot checks |

Non-goals: the VM half of [REPEAT-RUN] (a counter loop vs one compare: a separate CHOICE row
with A-ISL overlap, §3.8); lookaround REMOVAL, span intersection as an IR node, the end-of-match
mark and the group-0 group ([POSTFACT]'s 2026-11-08 entries; §7 only notes where they meet
this note); negative lookarounds beyond the guarded unit; [REWRITE-ADJ]; making kset/startset/
endwin readers of the description (alt_normal_form G-1); new public flag bits.

## 2. The general form

alt_normal_form §3.5: every fixed-width, capture-free piece has ONE description, a small set of
width groups, each a sequence of position sets with an `exact` bit, built bottom-up by the arm
combinators of `src/facts/desc.c` and read by `req.c`'s walk (the run) and `altnf.c` (the
adjacency head). This note adds one notion and three arms.

**The one notion: a GUARD and its REACH.** A description has a CONSUMED part (today's groups,
their positions at offsets `[0, width)` from the subtree's start) and a GUARD part: positions the
subject must hold at stated offsets from the subtree's start that the subtree does not consume,
offsets that may be NEGATIVE (before the subtree) or `>= width` (after it). The run carries its
guard as a REACH pair `(back, ahead)`: how many of its positions may lie before the match start
and after the match end. Every run today has reach `(0, 0)`. The soundness statement grows by
one clause: "every match contains the run at contiguous subject offsets, beginning at most
`back` bytes before the match start and ending at most `ahead` bytes after its end." A run with
`back > 0` still lies inside `[max(0, search_from - back), subject_length)`, because PCRE2 lets a
lookbehind read before the start offset, so a scan that starts `back` bytes earlier reads only
bytes the matcher may read.

**The three arms, one row each in the arm table (§6 T1):**

| node | consumed part | guard part | proof (a language identity) |
|---|---|---|---|
| REP `X{m,n}`, m ≥ 1 | head and best from `X^m · X{0,n-m}`, tail from `X{0,n-m} · X^m`; `all` iff m = n and `X^m` is `all` | the body's guards, per copy | `X{m,n}` = `X^m X{0,n-m}` = `X{0,n-m} X^m`; CAT is sound on each |
| REP `X{0,n}` | the width-0 EXACT unit where X's description is width 0 (it can match zero iterations); otherwise today's gap | none | `X{0,n}` admits ε; a width-0 X adds nothing else consumed |
| a node that consumes nothing (`A_EMPTY`, `\b`, `$`, `\G`, `\K`, a check callout, a lookaround) | the width-0 group: EXACT if the node cannot fail (`A_EMPTY`), GUARDED if it can | none, except a positive lookaround's | consumed bytes on either side of a zero-width node are adjacent in the subject |
| positive LOOKAROUND | the GUARDED unit | lookahead: the body's fixed HEAD affix at `[0, h)`; lookbehind: the body's fixed TAIL affix at `[-t, 0)` | the body matches at the cursor, so its fixed affix's positions hold in the subject there |
| negative lookaround, backref, variable, call | unchanged (a negative lookaround is a GUARDED unit; the others stay walls) | none | — |

GUARDED vs EXACT matters to one reader only: the owner (`altnf.c`) may treat only an EXACT unit
as "nothing here" in a rewrite; the run (a superset statement) joins across both. The adjacency
head ALREADY reads through every zero-width node (`altnf.c:192-210`), so the owner's column does
not move.

## 3. The REP arm ([REPEAT-RUN], alt_normal_form §9 S3)

### 3.1 The rule and its six decision points

alt_normal_form §9 S3 lists six points; each is decided here.

1. **REP as the description's power arm, not a `req.c`-local rule.** One combinator in
   `desc.c` (`pcrec_pd_pow`, name at build) and the run walk's `A_REP` arm calling the CAT step
   `m` times on the run accumulator. A `req.c`-local `rr_rep` would be a second spelling of CAT
   for one kind; the power IS repeated CAT, so it reuses `rr_cat` and `pcrec_pd_cat` and adds
   only the copy loop.
2. **The iteration-boundary join is sound because it is the CAT join.** reqpos_2b.md §2.4 item 4
   declined it "for want of a witness family", not for a soundness gap. Under the rule, the join
   between copy i's tail and copy i+1's head is `rr_cat`'s own `join` (`req.c:452-470`), whose
   soundness is today's; the witnesses of §3.6 are the family the decline asked for.
3. **The copy count is DERIVED from the run's storage bound, no constant.** Unrolling stops at
   the first of: m copies; or SATURATION, the copy after which no stored field can change. A
   body that is not `all` saturates at 2 copies (every later copy adds the same join
   `tail · head` again); an `all` body of width w ≥ 1 saturates when the stored head is full,
   at `ceil(PCREC_MAX_REQ_RUN_SCAN / w) + 1` copies (`limits.def:409`, 32 bytes); a width-0
   body is the unit (zero copies). `maxw` is always the exact `rr_rep_w(rmax, ...)`
   (`req.c:436-440`), and the head's `trunc` bit is set exactly as `rn_app` sets it today. No
   limits row is added: the bound is a property of an existing one.
4. **The VM half is a separate CHOICE row** (§3.8): not this note's.
5. **`NFA_ERASED_COUNT` is unaffected.** The run is AST-derived (`req.c:107`); the prefilter's
   count collapse reads the NFA. Nothing here reads or writes it.
6. **The population census is the trigger (D77)**, §8 unit R1.

**Offsets ([K82]).** In `X^m · X{0,n-m}` the first m copies start at the repeat's start, so the
head is at 0 and `best` keeps the offset the unrolled CAT computes; in `X{0,n-m} · X^m` the tail
ends at the repeat's end, so `rn_tail_off(maxw, n)` (`req.c:428-431`) applies unchanged. The
best of the two decompositions is taken from the first (its offsets are the smaller bounds);
the second contributes the tail only.

### 3.2 The owner and the code it touches

- `src/facts/req.c` `rb_rep_into` (`:549-558`) and the `A_REP` arm (`:708-740`): the arm's
  `rmin >= 1` branch becomes "unroll to `min(m, saturation)` through `rr_cat`, then the tail from
  the second decomposition, `all` per §2's row"; `rmin == 0` becomes "width-0 body: unit,
  else today's gap". The header paragraph `:65-68` ("a repeat's head and tail runs do NOT
  survive") and the arm comment `:709-720` are rewritten with it.
- `src/facts/desc.c`: a power combinator over the group list, `pcrec_pd_cat` applied m times
  with the same saturation rule (a group stores at most `max_pos` positions, `desc.h:33-38`);
  `REP{m,n}`, m < n, gives `pd_none` (variable width) exactly as today, so `req_pieces` moves
  only for exact repeats of a multi-group body.
- NOT touched by unit R1: `altnf.c:223-230`, the adjacency head's REP wall. A REP adjacency
  head is unit R2 (§8), with its own witness, because its reader is a TREE REWRITE (exactness),
  not a fact (superset). alt_normal_form FIX-1 option (a) stands until R2.

### 3.3 Readers it moves (found by grep at `7b9ddd890`)

The run walk's outputs are `req_set` (unchanged: the set walk already unions the body's set,
`rb_rep_into`'s `rb_union`), `req_set_maxoff` (unchanged), `req_whole_run` and its derived
`req_run`, `req_run_maxoff`, `req_byte`, `req_landmark_maxoff`, `run_pin` (`src/facts/facts.def:50-60`),
and `req_pieces`. Every reader of those is listed once in §5.4's admission table; for REP the
reach stays `(0, 0)`, so every reader admits the moved run as it admits today's (a longer run
of the same kind). The readers whose OUTPUT moves are the pick readers (`src/core/findings.c`,
the window/member choice), the window statement's R span (`emit_dfa.c:6815-6871`, longer R),
and the stamps `RX_REQ_RUN`/`RX_REQ_BYTE`/`RX_REQ_WHY`/`RX_REQ_HANDOFF`; `--emit-facts`
lists the new values. Answers do not move (§3.5).

### 3.4 Predicted movers (measured spellings)

| pattern | today (measured) | predicted (the spelling, measured) |
|---|---|---|
| `A{4}` | none | `41414141` (`AAAA`) |
| `ab{3}c` | none | `6162626263` (`abbbc`) |
| `xy(?:ab){2}zw` (alt_normal_form S3's witness) | `6162` (2) | 8 (`xyababzw`) |
| `(?i)xy(?:ab){2}zw` (byte and utf8) | none (the `[aA][bB]` pair is under the floor) | 8 cube positions (`(?i)xyababzw`) |
| `abcd(?:ab\|Ab){2}efgh` | `65666768` (4) | 12 positions (`abcd(?:ab\|Ab)(?:ab\|Ab)efgh`) |
| `xy(?:ab){2,3}zw` | `6162` (2) | 6, `xyabab` (`xyabab(?:ab)?zw`) |
| `xy(?:abc\|abd){2}zw` | `6162` (2) | 4, `xyab` (spelled) |
| `x(?:a[bc]){2}y` | none | 6 (`xa[bc]a[bc]y`) |
| `xy(?:é){3}zw` utf8 | `c3a9` (2) | 10 (spelled) |
| `(?:abc){20}` | `616263` (3) | 32 positions, truncated at the storage bound (a FACT witness, §3.6) |
| `xy(?:ab)+zw`, `xy(?:ab){1,}zw` | `6162` | 4, `xyab` (`m = 1`: head `ab`, tail `ab`) |
| `xy(?:ab){0,2}zw`, `xy(?:ab)*zw`, `[0-9]{4}` | `7a77` / none | unchanged (min-0 is a gap; `[0-9]` is out of the cube domain) |

The population (how many corpus and bench compiles move, and whether a bench cell is among them)
is the census of unit R1, not this table.

### 3.5 Answer identity

The run is a necessary condition; a longer necessary run moves which run the pre-check compares
and where, never which subjects match (alt_normal_form §8a C1: facts are order-free). The rule's
two decompositions are language identities, and the unrolled CAT is the existing `rr_cat`, so a
run that is not necessary can only come from a wrong decomposition: exactly what the witnesses
plant.

### 3.6 Sabotage witnesses (each can fail; expected answers from libpcre2, `oracle.out`)

| id (role) | planted error | pattern, subject, expected | correct run | sabotaged run, and why it fails |
|---|---|---|---|---|
| W-R1 (all at m < n) | `all` set for `X{m,n}` with m < n | `xy(?:ab){1,2}zw` on `xyababzw`: (0,8) | `xyab` (32 bits) | `xyabzw` (48): absent from the subject, the pre-check answers NOMATCH |
| W-R2 (copies = n) | unroll `rmax` copies, not `rmin` | `xy(?:ab){1,3}zw` on `xyabzw`: (0,6) | `xyab` | `xyababab...`: absent, NOMATCH |
| W-R3 (min-0 as m = 1) | a min-0 repeat of a consuming body joined as if `m ≥ 1` (the C-comment shape the `:722-738` comment names) | `ab(?:cd){0,2}ef` on `abcdef`: (0,6) | `ab` or `ef` | `abcdef`'s... the sabotage joins `ab·cd·ef` claiming `abcdef`, true here; on `abef` (expected (0,4)) it is absent: NOMATCH |
| W-R4 (width-0 test reads min width) | the "width-0 body is the unit" row reads `minw == 0` instead of `maxw == 0` | `ab(?:c?){2}de` on `abcde`: (0,5) | `de` | `abde` (the body treated as the unit): absent, NOMATCH |
| W-R5 (FACT witness, saturation) | saturation at one copy fewer | `(?:abc){20}` | 32 positions | 29: a shorter run, sound; cannot move an answer (lesson 1, stated): checked on the facts listing only |

W-R3's subject is `abef`, not `abcdef` (the row's first subject holds the sabotaged run by
accident; the listing keeps both so the reviewer sees why the second is the witness).
Each witness's REACH (the sabotage's site is reached by the witness pattern) is part of the
build's mech row ([MECH-REACH]).

### 3.7 Deny lever

By the owner's rule (2026-10-29, memory "flag follows caller effect"): the speed effect reaches a
caller only through the pick rows, each with its own deny; the risk is a WRONG answer (W-R1..R4).
So a TEST-ONLY lever, no public bit: alt_normal_form §11's one harness-only lever for 2a
("restore today's ALT outcome and EMPTY cut", not yet built) becomes ONE harness lever whose
value is a set of arms to restore (`alt`, `empty`, `rep`, `guard`, `look`), built by whichever
unit lands first (its later units add a member, not a lever). `-fno-req-run` (bit 31) and
`-fno-req-run-fold` (bit 44) keep their texts: bit 44 already denies every multi-member position,
so `(?i)xy(?:ab){2}zw`'s cube run is under it with no re-specification.

### 3.8 The VM half (pointer only)

The row's "the VM's literal-run selection" (`vm_det_seq`/`vm_cursor_fits`, ratchet row R02's
area A-SKIP; an exact `X{n}` matched by one compare instead of a counter loop) is a separate
CHOICE row with per-regime evidence and its A-ISL overlap (roadmap R04). It reads the same
power description when built; nothing in R1 depends on it.

## 4. The EMPTY arm ([REQ-EMPTYCAT], alt_normal_form §3.6, §9 S2)

### 4.1 What stage 2a moves, and what remains

Stage 2a (alt_normal_form §5, census-first, unbuilt) moves ONE kind: `case A_EMPTY`
(`req.c:756`) becomes the description's EMPTY arm, the unit of CAT; the kind row stays
(`src/core/kindrow.def:61`, TEXT `ZERO`). This note does not re-design that; it is row E-1 of the
table below. What remains is every OTHER node whose consumed description is width 0. Stated as
"the width-0 group is the identity of CAT", those are not special cases but the arm's other
rows:

| row | the subtree | its consumed description | today | after |
|---|---|---|---|---|
| E-1 | `A_EMPTY` (`abcd()efgh`, `abcd(?:\|)efgh`, altcls's empty residue, derive's pruned nodes) | width 0, EXACT | cut | unit (stage 2a) |
| E-2 | a repeat whose body's description is width 0 and EXACT, any `{m,n}` (`(?:)*`, `(?:){3}`) | width 0, EXACT | cut / gap | unit |
| E-3 | `X{0,n}` whose body is width 0, guarded or exact (`(?:\b)*`) | width 0, EXACT (zero iterations always match) | gap | unit |
| E-4 | a zero-width node that can fail: `\b`/`\B` (`A_CTX`), `$`/`^` (`A_EOL`, `A_CTX`), `\G`, `\K`, a check callout, a negative lookaround, and `X{m,n}`, m ≥ 1, of such a body (`(?:\b)+`, `pcrec_wrap_bare_anchor`'s `<anchor EMPTY>` under a quantifier) | width 0, GUARDED | cut | unit for the run (joins consumed contiguity); not a unit for the owner |
| E-5 | a positive lookaround | width 0, GUARDED, plus a guard | cut | §5 |

E-2/E-3 follow from §3's REP row with no extra clause (a width-0 body: zero copies; `X{0,n}`
admits ε). E-4 is the decision alt_normal_form left open as §9 S2 point (3): "whether a
zero-width ASSERTION under a repeat stays a D77 decline or gets its census". Decided here: it
gets its census, as unit E2 (§8), because its soundness is not in question. The bytes on either
side of a zero-width node ARE adjacent in the subject (`req.c:746-750` says so itself); what the
header forbids (`:752-755`) is joining through the BODY of a lookaround, which E-4 does not do.
The witness that separates the two is alt_normal_form's S-L (§5.7).

### 4.2 The owner and the code it touches

`req.c`'s `rb_walk_at` cut list (`:756-771`) splits by row: E-1 (2a) and E-2/E-3 (unit E1)
take `rb_init`'s identity (`rr_unit()` + `pcrec_pd_unit()`, `:511-516`) through the REP arm; E-4
(unit E2) gets a GUARDED unit, `rr_unit()` for the run and a description that is width 0 with
`exact = false` (a `PdGroup` field that exists, `desc.c:36-41`). `rb_row_into`'s `KTEXT_ZERO` row
(`:637-645`) is where E-4 lands, since every ZERO-text kind is E-4 except `A_EMPTY` (E-1, its own
`case`) and `A_LOOK` (E-5). The kind row is untouched (alt_normal_form §3.6's ruling).
`endwin.c:301` and `emit_vm.c:4093` stay kind tests (alt_normal_form FIX-9).

### 4.3 Readers it moves

The same fact set as §3.3, at reach `(0, 0)`: a guarded unit joins two consumed runs that are
both inside the match. Every reader admits it as today (§5.4).

### 4.4 Predicted movers (measured spellings)

| pattern | today | predicted |
|---|---|---|
| `abcd()efgh`, `abcd(?:\|)efgh` (E-1, 2a's) | 4 | 8 |
| `abcd(?:)*efgh`, `abcd(?:){3}efgh` (E-2; §9 S2's witness) | 4 | 8 |
| `abcd(?:\b)+efgh` (E-4; never matches, `d\be` has no boundary) | 4 | 8 (sound: a pattern that cannot match has every run) |
| `ab(?:x\b)+cd` (E-4 plus REP) | `6364` | `abx` with the REP head; `x\bc` never matches either, so the witness subject is a non-word spelling below |
| `xyz(?<=yz)abc` (E-4 alone, the lookbehind body not read) | `abc` (3) | 6, `xyzabc` |
| `x(?!ab)ac` (a negative lookaround, E-4) | `ac` | 3, `xac` |

### 4.5 Witnesses

| id | planted error | pattern, subject, expected | correct | sabotaged |
|---|---|---|---|---|
| S-g (alt_normal_form, 2a) | a consuming kind (`A_BREF`) sent to the EMPTY arm | `(ab)x\1y` on `abxaby`: (0,6) | `abx` | `abxy`: absent, NOMATCH |
| W-E1 (guarded read as positive) | a negative lookaround's body read as a guard (its positions intersected) | `x(?!ab)ac` on `xac`: (0,3) | `xac` | `ab ∩ ac` empties position 2: the run claims the pattern cannot match, NOMATCH |
| W-E2 (E-4's join through the body, S-L) | §5.7 | | | |

### 4.6 What closes [REQ-EMPTYCAT]

S2's five points: (1) decided by alt_normal_form (the unit is the description's, not the kind
row's); (2) E-2/E-3, here, by §3's rule; (3) E-4, here: a census, unit E2; (4) the producer
census is unit E2's census (it counts every compile whose run is cut by a zero-width node, per
producer kind); (5) the row closes when 2a, E1 and E2 have landed or been declined by their
census.

## 5. The positive LOOKAROUND arm ([REQ-LOOKAROUND], alt_normal_form §9 S4)

### 5.1 The rule

At a positive lookaround, the run walk holds `acc`, the facts of everything to its RIGHT
(`req.c:675-697`: the walk accumulates right to left). The arm is the guarded unit (E-4) plus
the body's fixed affix as a guard:

- a LOOKAHEAD's guard is the body's HEAD affix `H` (`h` positions from the cursor: the body's
  fixed-width prefix, the description's head over every branch, `rr_alt`'s common head where the
  body alternates); it is position-wise INTERSECTED with `acc.head` over `min(h, acc.head.n)`
  positions, and where `h > acc.head.n` and `acc.all` (the right side is a closed literal of
  width `acc.maxw`), its remaining `h - acc.head.n` positions EXTEND the head past the right
  side's end: they are reach `ahead`, and the result is not `all` (nothing may join after a
  guard extension: the next consumed byte follows the right side, not the guard);
- a LOOKBEHIND's guard is the body's TAIL affix `B` (`t` positions ending at the cursor); it
  waits for the LEFT neighbour: in `rr_cat(l, r)` (`req.c:450-470`), `r.head`'s back guard
  intersects `l.tail`'s last positions; where `t > l.tail.n` and `l.all`, the rest extends
  before `l`'s start: reach `back` grows by what `l.maxw` does not cover, and at the pattern's
  top level `back > 0` means the run begins before the match start.
- an EMPTY intersection at any position proves the subtree cannot match (`foo(?=bar)baz`:
  `r ∩ z`; libpcre2: NOMATCH on `foobaz` and on `foobarbaz`). This note records it as a fact
  the walk can state, no consumer (Unlocks U-dead).

**The three placements, a declared first-match table (§6 T4):**

| row | where the guard lands | example (measured today → predicted) | new reader obligation |
|---|---|---|---|
| INSIDE | every guard position overlaps a consumed position of the same match | `a(?=b)[bc]` none → `ab`; `(?=abcd)abcd` `abcd` → same (no mover) | none: the run stays inside the match (reach (0,0)) |
| AHEAD | some guard position lies past the match end | `bar(?=baz)` `bar` → `barbaz`, ahead 3 | readers that assume the run ends by the match end (§5.4, assumption C) |
| BACK | some guard position lies before the match start | `(?<=foo)bar` `bar` → `foobar`, back 3 | readers that scan from `search_from` or read the offset as non-negative (§5.4, A and B) |

Rows AHEAD and BACK are the same rule at different reaches; the walk takes the ADMITTED REACH as
a parameter, as it takes `pos_set` today (`pcrec_req_walk(cx, root, pos_set, ...)`,
`req.c:787-800`): at `(0, 0)` every guard position outside the match is dropped and the walk is
row INSIDE only. One fact, its reach a declared input, no second walk.

### 5.2 A variable lookaround's fixed part

S4 point (2): a lookbehind body of bounded variable width still has a fixed TAIL affix (the
description's tail of a variable subtree, alt_normal_form §3.5's last row; the same piece
vlookbehind_pieces.md calls the fixed tail it would hoist): `(?<=fo{1,3})bar` → `obar` at
back 1 (pcrec refuses the unbounded `(?<=fo+)bar` the plan row quotes: "every alternative of a
lookbehind must have a bounded length"); `(?<=ab|b)c` → `bc` at back 1 (the common tail of
`ab|b`). A lookahead body's fixed HEAD affix likewise (`x(?=ab|ac)a.` → `xa` plus the guard
`a` at 1: intersection `a ∩ a`, then `[bc]` at 2 out of the cube domain: no extension).

### 5.3 The window: the scan begins before the start offset

S4 point (4). A run with `back = k` is found in `[max(0, search_from - k), subject_length)`.
The window statement already has the shape: span starts down to `-MF_MAX_BACK` (`-8`), and a
floor (`MF_WFLOOR_SUBJECT`/`_EXPR`, `emit_dfa.c:6883-6897`) that says where reads may begin.
So BACK is, at the seam, a run span R with a negative start, bounded by the kit's shape bound
8, beyond which the reader refuses it (a reach row, §5.4). pcrec's own pre-check (the
`memchr`/`memmem` over the window, `src/gen/emit_dfa.c`'s run compare) steps its start back by
`k`, clamped at 0: the UTF check's precedent (`<prefix>_VALID_LB`). The run pin and its
walk-proven widening (`pf_window_of`, `walk_proves` refusing `d < 0`, `:6809`) do NOT extend
into negative offsets until the kset walk itself proves bytes before the start (G-1 territory):
until then R's stated span is the walk-proven part only and the back positions ride in the
pre-check, not in the window statement. S4 point (6), the span check reading the same pieces:
the kit verifies a found candidate against every stated span (D172), so a back span stated
later is verified with no new kit mechanism; that statement is unit L3b (§8).

### 5.4 Readers and the reach each admits

[TO BE FILLED FROM THE READER CENSUS]

### 5.5 Negative lookarounds

S4 point (5): walls for positions (no guard), GUARDED units for contiguity (E-4). W-E1 is the
witness that a negative body is never read as a guard.

### 5.6 Predicted movers (spellings measured; guard positions counted)

| pattern | today | INSIDE only (reach (0,0)) | full reach |
|---|---|---|---|
| `xyz(?<=yz)abc` | `abc` | `xyzabc` (E-4; the body intersects `yz`, no change) | same |
| `a(?=bc)bc` | `bc` | `abc` | same |
| `a(?=b)[bc]` | none | `ab` | same |
| `(?:(?=abcd)ab)cd` | `abcd` | `abcd` (intersection and extension inside the outer match) | same |
| `foo(?=bar)baz` | `baz` | the dead fact (U-dead) | same |
| `bar(?=baz)` | `bar` | `bar` | `barbaz`, ahead 3 |
| `(?<=foo)bar` | `bar` | `bar` | `foobar`, back 3 |
| `(?<=fo{1,3})bar` | `bar` | `bar` | `obar`, back 1 |
| `(?<=ab\|b)c` | none | none | `bc`, back 1 |
| `(?<=\x00\x01)[a-z]+` | none | none | `\x00\x01`, back 2 (the plan row's locate-on-the-lookbehind example) |

### 5.7 Witnesses

| id | planted error | pattern, subject, expected | correct | sabotaged |
|---|---|---|---|---|
| S-L (alt_normal_form §3.5, the leak) | the lookbehind's body read as CONSUMED (offset 0, not back) | `(?<=foo)bar` on `foobar` from offset 3: (3,6) | reach (0,0): `bar`; full reach: `foobar` at back 3 | `foobar@0` as a consumed run: a pre-check from offset 3 (no step back) finds no `foobar`: NOMATCH |
| W-L1 (§9 S4's witness: the window not widened back) | the pre-check scans from `search_from`, not `search_from - back` | `(?<=foo)bar` on `foobar` from offset 3: (3,6); from 2: (3,6); from 4: NOMATCH | the scan from 0 finds `foobar` | the scan from 3 misses it: NOMATCH where (3,6) is expected |
| W-L2 (extension treated as consumed) | a guard extension leaves `all` true | `(?:(?=abcd)ab)cd` on `abcd`: (0,4) | `abcd` | `abcdcd` (the outer `cd` appended after the guard): absent, NOMATCH |
| W-L3 (variable tail from the wrong branch) | the lookbehind's fixed tail taken as the FIRST branch's tail, not the common one | `(?<=ab\|b)c` on `xbc`: (2,3) | `bc` back 1 | `abc` back 2: absent, NOMATCH |
| W-L4 (ahead reader) | [TO BE FILLED FROM THE READER CENSUS] | | | |
| W-E1 | §4.5 | | | |

### 5.8 Lever

The same harness lever (§3.7), members `guard` (E-4) and `look` (the guard part), plus the
reach input itself: the harness lever forces reach `(0, 0)` for the `look` member's AHEAD/BACK
rows. No public bit: the reach widening is a choice reaching a caller only through the pick rows
(each deny-able) and the pre-check's earlier start (at most 8 bytes per call, a cost the
D186 bench decides), and its risk is wrong answers (W-L1..L4).

## 6. Decisions as declared tables (each first-match; the build spells them as rows)

**T1, the arm table** (the description's dispatch; one row per node class, §2's table): CLASS,
EMPTY (EXACT), zero-width (GUARDED), positive LOOKAROUND (GUARDED + guard), CAT, ALT, REP
(power), negative LOOKAROUND (GUARDED), BREF/VAR/consume callout/CALL (wall). The `switch` in
`rb_walk_at` stays exhaustive with no default (`req.c:124-128`'s rule); a kind maps to a row.

**T2, the REP rows** (first match):

| # | condition | consumed description | `all` |
|---|---|---|---|
| 1 | body description width 0 (any m, n) | the EXACT unit if the body is EXACT or m = 0, else the GUARDED unit | true |
| 2 | m = 0 | today's gap (`rr_none(rr_rep_w(...))`) | false |
| 3 | m = n | `X^c`, c = min(m, saturation) | iff body `all` and c = m |
| 4 | otherwise (m ≥ 1, m < n or unbounded) | head and best from `X^c · gap`, tail from `gap · X^c` | false |

**T3, the zero-width rows**: §4.1's E-1..E-5, first match on the kind row's TEXT `ZERO` and the
node kind (`A_EMPTY` before the rest; `A_LOOK` positive before negative).

**T4, the guard placement rows**: §5.1's INSIDE, AHEAD, BACK; a guard position outside the
admitted reach is dropped (the walk's reach input); an empty intersection anywhere states the
dead fact.

**T5, the reader admission rows**: §5.4.

**T6, the units and their triggers**: §8.

## 7. Forward context only: where the lookaround arm meets [POSTFACT]'s 2026-11-08 entries

Noted, not designed (`docs/design/plan_row_bodies/POSTFACT.md`):

- **Span intersection** (`B & P1 & P2` on one span; lookaheads CONTAINED in the span become a
  plain automaton): this note's INSIDE row is the FACT shadow of the contained case; the
  intersection node would make the guard a consumed-span condition the automaton checks, after
  which the run reads it as consumed (reach (0,0)) with no guard row needed.
- **Lookbehind removal by `\K` with an earlier scan and a floor** (exact for fixed-length A):
  the same step-back the BACK row's reader performs (scan from `max(0, s − maxlen(A))`, accept
  only at or after `s`); the BACK row's `back` is that `maxlen(A)` for a fixed body. If the
  rewrite lands, a fixed lookbehind becomes consumed text plus a start mark, and the BACK row's
  reach becomes the mark's offset: the reader obligation (the scan floor) is the same one.
- **The end-of-match mark** (the lookahead mirror): the AHEAD row's `ahead` is that mark's
  distance to the consumed end; a reader admitting AHEAD is a reader that already knows the
  reported end is not the consumed end.
- **The group-0 group** (`A(?<0>B)C`): both marks at once; under it a run over `ABC` has
  `back = |A|`, `ahead = |C|` relative to the reported match. The reach pair is exactly the
  vocabulary that construct's facts would need.
- **"Is read-before-start already a span fact?"** (POSTFACT's "To confirm"): the SHAPE is (D172
  spans start down to -8, `memfn.h:235`); the statement is not (§0: pcrec states only `-1`).

## 8. Staging (separable units; each names the measurement that triggers it, D77)

| unit | content | depends on | kind (byte / utf8) | trigger (D77: the census that starts it) | gates |
|---|---|---|---|---|---|
| E1 | T2 row 1 and T3 E-2/E-3 (exact width-0 units through REP); rides with stage 2a (E-1) if 2a's census fires, else alone | none (2a's lever if 2a is first) | choice / choice | stage 2a's census extended to `REP`-of-width-0 producers (the `pcrec_wrap_bare_anchor` wrapper, derive's pruned nodes): a bench cell among the movers | the census list = observed movers (two-sided); B0 identity diff with only those movers; PC-3; `make test`, `make test-axes` with the harness lever's `empty` member; S-g, W-R4 |
| R1 | T2 rows 3-4 (the power arm, runs and pieces) | none | choice / choice | [REPEAT-RUN]'s census: corpus + bench compiles whose run grows under an independent model of T2 (byte spellings of the lowered trees, `pred.py`'s method), a bench cell among them | as E1; W-R1..R5; the pieces listing moves only for exact repeats (declared stream rows) |
| E2 | T3 E-4 (guarded units) | none | choice / choice | a census of compiles whose run is cut by a zero-width node, per producer kind (S2 point 4), a bench cell among them | as E1; W-E1, S-L (S-L must stay red-able: the body is still not read) |
| L1 | T4 INSIDE (guard intersection within the match, reach (0,0)) and the dead fact as a listing value | E2 | choice / choice | the plan row's cheap census, narrowed: compiles with a positive lookaround whose run grows at reach (0,0) | as E1; W-L2, W-L3 |
| L2 | T4 AHEAD (reach `ahead` > 0) | L1, the §5.4 audit of every assumption-C reader | choice | a bench cell whose rarest bytes sit in a lookahead past the consumed end | W-L4; every assumption-C reader's admission row in the same change |
| L3a | T4 BACK in pcrec's own pre-check (scan from `search_from - back`, clamped) | L1 | choice | the plan row's census (rarest bytes inside a positive lookbehind), "likely after A-REV" (plan row) | W-L1, S-L |
| L3b | the BACK span stated to the kit (a negative R start, at most 8) | L3a, the kit's request round (a `fields.def`/window statement event is the kit's `MF_SITE_ABI` call, not pcrec's) | choice | the kit's answer that it consumes a back span | the kit's own witnesses + W-L1 at the seam |
| R2 | the REP adjacency head (`altnf.c:223-230`'s wall becomes `X^m`'s head, `closed` iff m = n) | R1 | choice (tree movers) | a census of owner refusals (row 3) whose intervening branch's head is a REP | alt_normal_form's S-d/S-k family re-run; a new witness: `(?:ab|a(?:x){2}|ad)` style, the REP head must not admit a move past a writing branch |

Order: E1 → (R1, E2 independent) → L1 → (L2, L3a) → L3b; R2 after R1 when its census fires. No
unit is an abi event by itself unless its movers include emitted scaffolding: runs and stamps are
VALUES (alt_normal_form §4.7's reading); each unit's identity gate says which streams move.

## 9. The ledger (G2)

| change | where (`7b9ddd890`) | kind |
|---|---|---|
| "a repeat's head and tail do not survive" | `req.c:65-68`, `:709-720`, `rb_rep_into` `:549-558` | REPLACED by T2 (unit R1) |
| "min-0 is a gap" for a width-0 body | `req.c:722-739` | REPLACED by T2 row 1 (E1) |
| `pcrec_pd_none()` for REP | `req.c:557` | REPLACED by the power combinator (R1) |
| the ZERO-text cut | `req.c:627-645`, `:756-771` | SPLIT by T3: unit (E1/2a), guarded unit (E2), guard (L1) |
| `A_LOOK`'s "joining across" comment | `req.c:744-755` | REWRITTEN (E2: joining across is sound; reading the body is the L rows, with reach) |
| the REP adjacency wall | `altnf.c:223-230` | REPLACED (R2) |
| the power combinator | `desc.c` (new) | ADDED (R1) |
| the reach input of the walk | `pcrec_req_walk`'s signature (`req.c:787`) | ADDED (L1; reach (0,0) until L2/L3a) |
| the dead fact | `--emit-facts` value | ADDED (L1), no consumer |
| one harness lever with an arm set | `cli/` harness options (alt_normal_form §11's lever, generalized) | ADDED once (first unit), members per unit |

## 10. Unlocks (each with its trigger)

| id | unlock | trigger |
|---|---|---|
| U-dead | a pattern whose description has an empty intersection cannot match: the compile could emit the constant NOMATCH artifact (`foo(?=bar)baz`, `abc(?=d)efg`) | a corpus or user pattern that is dead this way (count at L1's census) |
| U-vm | an exact `X{n}` of a fixed body matched by one compare in the VM (S3 point 4) | a VM bench cell with an exact counted repeat on its hot path |
| U-pieces | `req_pieces` through repeats feeds alt_normal_form U3 (the kit's piece-set request) | the kit's answer to that request |
| U-locate | a lookbehind's guard as a LOCATE candidate (`(?<=\x00\x01)[a-z]+` locates on the lookbehind bytes): it joins the one find-the-span choice set with its offset (plan row, Frank 2026-11-06) | L3b landed, and a bench cell where the guard is rarest |
| U-G1 | kset/startset/endwin read the description (alt_normal_form G-1): the window's R could then be walk-proven at negative offsets | G-1's own census |
| U-rewrite | [REWRITE-ADJ]'s REP-OF-REP / TRIVIAL-REP members read T2's rows (one REP rule for facts and rewrites) | [REWRITE-ADJ]'s first build |
| U-post | [POSTFACT]'s marks: the reach pair is their fact vocabulary (§7) | a design lane for span intersection or the marks |

## 11. Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.** Every number here is a compile-time fact of this box's
   compiler (gcc 15.2, Zen 4, the lane's own build of `7b9ddd890`); answers from libpcre2-8 10.46.
   Each unit's speed claim is owed per regime at its gate (bench strata; for L3a a find-all regime,
   where the step back is paid per call); a different regime can flip a pick, which is why every
   unit is a CHOICE.
2. **Independent control: RELEVANT.** Each census is an independent model of T2/T3/T4 over byte
   spellings of the lowered trees (no compiler code), compared two-sided with the observed movers
   (K35: the population is corpus + bench, counted); each witness has a libpcre2 expectation
   (`oracle.out`), never pcrec's; each sabotage reaches its site ([MECH-REACH]).
3. **What moves when data is regenerated: NOT RELEVANT beyond today's.** The arms add no table,
   calibration or data file; a UCD regeneration moves fold classes and so runs, as today
   (alt_normal_form §7.3).

## 12. Proposed decision (D-next, text only)

**The one fixed-width description gets its REP, EMPTY and positive-LOOKAROUND arms as language
identities, and a run gets a REACH.** `X{m,n}` reads as `X^m · X{0,n−m}` (head, best) and
`X{0,n−m} · X^m` (tail), `X^m` unrolled through CAT to a saturation derived from the run's
storage bound; every node that consumes nothing is CAT's width-0 unit, EXACT if it cannot fail and
GUARDED if it can, the run joining across both and the rewrite owner across EXACT only; a
positive lookaround adds its body's fixed affix as a guard at its offset, intersecting the
consumed positions it overlaps and extending past them; a run's reach `(back, ahead)` says how far
it may lie outside the match, the walk computes at the reach its readers admit (a declared table),
and a reader widens its admission only in a unit that names its witness. No public flag bit; one
harness lever with an arm set. Staged E1, R1, E2, L1, L2, L3a, L3b, R2, each on its census.

## 13. Open questions for Frank (plain words, each with a leaning)

[TO BE WRITTEN]

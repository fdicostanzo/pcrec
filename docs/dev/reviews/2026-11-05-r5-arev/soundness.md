# crit-arev soundness findings (lens: soundness, opus)

Subject: `R/subject_arev.md` (A-REV rev 0). Code read in `worktrees/crit-arev` (f15f30f25). Oracle:
`R/tools/oracle_probe` plus this lens's own start-offset probe `R/soundness/sprobe.c` (libpcre2-8
10.46 as a library: one `pcre2_match` per line, `PATTERN<TAB>SUBJECT<TAB>STARTOFFSET`).
`R` = /var/tmp/pcrec-pcrec/scratch/crit-arev; `T` = /home/pcrec/projects/pcrec/worktrees/crit-arev.

## Findings

### SOUND-1 — `erased == 0` does not make a REVERSE machine exact: `\G` in a lookbehind branch is admitted to `exist` and gives the wrong answer for both polarities

- **Status:** SUSPECTED for the answer (no lookbehind reverse machine exists to run); CONFIRMED
  for every link in the chain by code quote and oracle.
- **Severity:** answer. **Effort:** small (one conjunct). **Blast radius:** every variable
  lookbehind branch holding `\G`, both polarities, every artifact taking row 1 or row 2.
- **Design §:** §3.1 row 1 `exist` ("machine built `exact` and `erased == 0`; the branch has no
  capturing group") and row 2 `gate` (it acts on "no accept"); §2.2 "test existence ... exact yes /
  no"; the decision paragraph ("the exit is admitted on the machine's recorded exactness").
- **Chain:**
  1. `A_GSTART` sets no erasure bit: `src/core/kindrow.def` `KIND_ROW(A_GSTART, ZERO, TRANSPARENT,
     NONE, 0)`, and `src/ir/nfa.c:704` lowers it to `N_GSTART`, exactly. So a branch `\Ga{1,2}` has
     `erased == 0` and no group: row 1 admits it.
  2. The DFA builder evaluates `\G` ONLY in the start-state closure: `src/ir/dfa.c:1750`
     "`gst_ok` is FALSE at every successor ... one transition means one byte consumed, so `pos >
     startpos` unconditionally". True FORWARD. In a REVERSE walk the start state is the CURSOR
     (the body's right end); the body's left-end `\G` is met only after bytes are consumed, where
     `gst_ok` is false: the path dies. Reverse, "one byte consumed" means `pos < cursor`, not
     `pos > startpos`.
  3. No reverse machine has ever met `N_GSTART`: `pcrec_nfa_has_bot` (`src/ir/nfa.c:1342`) routes
     every `\G` pattern to ENG_ATTEMPT ("That the reverse machine then never evaluates N_GSTART is
     the same free consequence", nfa.c:1336). The per-site lookbehind machine is built from a
     BRANCH NFA: the main NFA lowers the whole `A_LOOK` to epsilon (`nfa.c:759`), so the
     pattern's own `has_bot` is false and that routing does not protect the branch machine.
  4. The existing reverse-walk client already knows this: the landmark walk's exactness conjunct
     `lc_g1` (`src/gen/lmwalk.c:174-184`) is `erased == 0` PLUS "no `\G` ... and no `\K`" ("R
     reads no position the walk moves"). arev's row 1 copies the `erased` half only.
- **Oracle (sprobe, libpcre2 10.46) vs what today's builder would make the row answer:**
  - `(?<=\Ga{1,2})b` on `aab` from 0: **(2,3)**. Reverse machine: the `\G` path dies, no accept;
    `exist`'s "no" (and `gate`'s "no accept: decided") → **nomatch**.
  - `(?<!\Ga{1,2})b` on `aab` from 0: **nomatch**. Machine: no accept → negative holds →
    **(2,3)**, a false match.
  - The same pair from offset 1: (2,3) / nomatch; the machine answers the same wrong way.
  - `\G` at the RIGHT end, `(?<=a{1,2}\G)b` on `aab` from 2: **(2,3)**; right only if the renderer
    picks the `gst_ok` start family when `cursor == startpos`. No reverse renderer ever chose that
    family (W1-W3 never meet `\G`) and `RevWalk` has no operand for it.
  - pcrec's VM handles `\G` inside a (fixed) lookbehind correctly today: `(?<=\Ga|bb)b` on `aab`
    from 0/1/2 = nomatch/(2,3)/nomatch, = libpcre2 (generated main, start offset patched in). So
    stage 1 `range` serves `\G` branches and they reach row 1's admission.
- **Note:** `gate` is unsound here too, not only `exist`. §3.1's "a superset machine's NO accept
  is always sound to act on" assumes a SUPERSET; a direction that kills `\G` paths builds a SUBSET
  that `erased` cannot see. General form: `Nfa.erased` records WIDENINGS of the lowering, never
  NARROWINGS by the walk direction.
- **Fix (general, an existing fact):** the whole `reverse-dfa` admission (rows 1 and 2; vlookbehind
  rev 1 §5.4) adds `!pcrec_nfa_has_bot(branch NFA)` — the existing predicate covering `\G` and
  every absent-previous context row (SOUND-2) — or the design adds a `\G`/absent-prev operand to
  the reverse walk with its own witnesses. Witness rows beside WD1: the two `\G` cells above, both
  polarities, from offsets 0, 1 and 2.

### SOUND-2 — `^` / `\A` / `(?m)^` in a lookbehind branch turns the reverse build into a compile REFUSAL, not a decline; "context at the floor as RECOVER reads it" is false for them

- **Status:** CONFIRMED by code quote (the per-site builder does not exist to run).
- **Severity:** answer (a pattern stage 1 compiles becomes `internal error` under S3, against
  G1 "no step changes a match ... or a give-up class" and §2.4 "an overflow is the row's decline,
  never a refusal"). **Effort:** small (SOUND-1's conjunct). **Blast radius:** every variable
  lookbehind with a subject/line-start anchor in a branch (`(?<=^ {0,3})#`-shaped patterns);
  vlookbehind rev 1's own §2 cell `(?<=^a{0,2})x` is one.
- **Design §:** §3.1 "The floor ... the context byte below the floor is read as on every reverse
  walk (S74)"; §2.4 the builder "of `revend_build_one`'s shape"; vlookbehind rev 1 §3 row "context
  at the start (`\b`, `^`)": "The reverse machine's views at the floor, as the RECOVER pass reads
  them".
- **Code:** `src/ir/dfa.c:1576-1586`: `DFA_INVARIANT(cx, !reverse ||
  !ctxfn_reads_absent_prev(nfa->st[i].ctxfn), "a reverse DFA met a context row that reads an absent
  previous character (the ENG_ATTEMPT routing of pcrec_nfa_has_bot was bypassed)")`;
  `dfa.c:424-425` defines `DFA_INVARIANT` as `pcrec_ctx_fail(... "internal error: %s" ...)`.
  `revend_build_one` (`src/core/compile.c:454-466`) saves/restores only the OVERFLOW record; it
  does not catch a `pcrec_ctx_fail`. RECOVER (W1) never reads `^` at its floor: such patterns never
  get a reverse machine (`pcrec_nfa_has_bot`'s SUBJECT_START/MLINE_BOL arm, nfa.c:1345-1351; the
  dfa.c comment: "`sides_of` never sets a reverse `left_abs`").
- **Oracle:** `(?<=^a{1,2})b` on `aab` from 2 = (2,3), `(?<!^a{1,2})b` from 2 = nomatch (the body
  lies before the start offset, `^` is the subject start); `(?<=\Aa{1,2})b` on `aab` = (2,3).
  pcrec compiles `(?<=^a|bb)b`, `(?<=\Aa|bb)b` and `(?m)(?<=^a|bb)b` today (fixed widths), so the
  variable forms are in stage 1's population.
- **What a correct walk would need** (not a reason to build it): with floor = 0, termination at 0
  IS "no previous character", so `^`/`\A` are representable by a reverse `left_abs` at position 0
  — a NEW reverse-builder capability with its own witness (S74's sibling for the absent side), not
  something any walk does today. Until then the admission declines them (SOUND-1's conjunct covers
  both).

### SOUND-3 — §3.1 row 1's hand "yes / no, the answer for either polarity" is one BRANCH's answer, not the lookbehind's; built literally it moves answers on multi-branch lookbehinds

- **Status:** CONFIRMED (the table hand-executed as written; oracle).
- **Severity:** answer if built literally; doc otherwise. **Effort:** wording. **Blast radius:**
  multi-branch lookbehinds whose varying branch takes row 1.
- **Design §:** §3.1 row 1 "hand: yes / no, the answer for either polarity"; §2.2 "test existence |
  `first`, result used as the answer | exact yes / no"; §2.1 `dead` for L "the exit row's decided
  branch".
- **Hand-execution:** `(?<!a{1,2}|b)x` on `bx`, cursor 1. Branch 1 `a{1,2}` varies, capture-free,
  exact → row 1. Walk from 1, floor max(0, 1−2) = 0: byte `b` is dead, no accept → "no". Taken as
  "the answer" for the negative polarity: the assertion holds → (1,2). libpcre2: **nomatch** (branch
  2 `b` matches; a negative lookbehind holds only when EVERY branch fails). The positive twin
  `(?<=a{1,2}|b)x` on `bx` = (1,2) (rev 1's F1 cell) becomes nomatch the same way. Only "yes" is
  the lookbehind's answer (positive holds / negative fails); "no" is always "this branch fails, the
  next branch starts from the CURSOR" (vlookbehind rev 1 F1, §5.1), which arev's table does not say.
- **Fix:** row 1's hand: "yes: decided (positive holds, negative fails); no: this branch fails, the
  next branch from the cursor". Row 2's hand already says "branch".

### SOUND-4 — "built `exact`" is not a recorded fact, and the word already means something narrower in a caller-visible stamp

- **Status:** CONFIRMED (code).
- **Severity:** doc / design (no answer moves while `erased == 0` stays a conjunct). **Effort:**
  wording. **Blast radius:** the build lane's reading of §2.4/§3.1.
- **Design §:** §2.4 "The BUILD REQUEST is part of the operand: `exact` or `collapsed`"; §3.1 row 1
  "machine built `exact` and `erased == 0`"; §2.5 G7; the decision paragraph "the machine's recorded
  exactness".
- **Code:** the only recorded fact is `Nfa.erased` (`src/core/internal.h:2419-2427`: "Exactness is
  then a RECORDED fact of the machine, `erased == 0`"; reset per build, nfa.c:1072/1089). The
  request is `pcrec_build_nfa`'s `collapse` argument, recorded per machine nowhere (the main
  machine's lives in `job->fit.prefilter_collapsed`); a collapse that fires records
  `NFA_ERASED_COUNT` (nfa.c:845-849), so "built exact" is implied by, and redundant with,
  `erased == 0`. Meanwhile `RX_VM_PREFILTER_LANG` (`src/gen/emit_vm.c:11307-11311`) stamps
  `"exact"` for any machine without the COUNT bit, atomic- and lookaround-erased ones included
  (its comment: "atomic and lookaround erasures stamp "exact" here: F-13, a vocabulary mover filed
  for a later abi"). A lane reading "built exact" in that vocabulary admits exactly WD1's machine.
- **With SOUND-1/2:** "exact" for a REVERSE walk is three facts, not one: no widening
  (`erased == 0`); no position the walk moves or cannot see (`\G`, `\K`: lmwalk's `lc_g1`); no
  absent-previous context row (`pcrec_nfa_has_bot`). §2.1 should name the admitted fact as ONE
  operand read after the build ("`exact`: `erased == 0` and `!has_bot`") rather than a request.

## PROBED-AND-HELD

- **The atomic counter-example, both polarities (WD1):** `(?<=(?>a|ab)b)x` on `abbx` nomatch,
  `(?<!(?>a|ab)b)x` (3,4) (oracle). `A_ATOMIC` lowers transparently and records
  `NFA_ERASED_ATOMIC` (nfa.c:954-956; kindrow.def's `A_ATOMIC` row) → row 1 declines; row 2 on a
  superset acts only on no-accept (sound), an accept passes to `range`. HELD. More cells, all
  oracle nomatch where the non-atomic twin matches, all carrying the ATOMIC bit (possessive
  spellings parse to `A_ATOMIC`, internal.h:1008ff): `(?<=x(?>a|ab))y` on `xaby`,
  `(?<=x(?>a|ab){1,2})y` on `xaaby`, `(?<=(?>a{1,2})a)x` on `aax`, `(?<=xa{1,3}+)a` and
  `(?<=x(?>a{1,3}))a` on `xaaa`. 7 cells HELD.
- **Can an optimizer delete a user atomic inside a lookbehind (erased == 0 over a live cut)?** The
  only deleter is `pcrec_discharge_atomic` (src/opt/atomic.c:537); its set comes from
  `pcrec_poss_survey` → the possessify walk, which "DOES NOT ENTER A LOOKAROUND BODY AT ALL"
  (possessify.c:1817ff; the `A_LOOK` arm at :1856 only collects calls). HELD. (Aside, not arev's:
  that comment's reason 2 says "Empty-follow-plus-`may_end` is right for the ATOMIC spellings,
  which commit to the body's first success" — false for a VARIABLE lookbehind, whose end-check can
  reject the first success (`(?<=xa{1,3}+)a` on `xaaa` nomatch). Harmless only because the walk
  does not enter; vlookbehind's build must not take that sentence as licence.)
- **Nested lookarounds:** `A_LOOK` → `NFA_ERASED_LOOK` (`frag_row`, nfa.c:596-600) → gate. A
  recognized one-character lookaround is `A_CTX` (exact, reversal identity, nfa.c's A_CTX arm);
  reading left of a candidate it reads the floor's context byte (S74), reading right of the cursor
  it reads the seed's right context. HELD on reading, provided L's `seed` carries the cursor's
  right context as W1's `seed_cond`/`seed_byte` do (§2.1 says it does).
- **Backreferences / variables:** the builder arm is a loud `pcrec_ctx_fail`; arev §3.1 (via
  vlookbehind §5.4) and rev 1 exclude them at admission. HELD. Linked calls hit the same loud arm
  (nfa.c A_CALL arm, "a LINKED subroutine call reached the machine builder"); today the pattern's
  `fit.prefilter` forcing keeps it away, but a per-site branch builder bypasses that gate: the
  admission should list "linked call" beside backreference/variable. Spliced calls are exact.
- **Callouts:** `NFA_ERASED_CALLOUT`, and pcrec refuses callouts in a lookbehind (rev 1 §3). HELD.
- **`\K`:** `(?<=a\K{1,2})b` REJECT in libpcre2; rev 1: both libraries refuse `\K` in a
  lookbehind (err 199). HELD.
- **(*ACCEPT), (*COMMIT), (*FAIL), conditionals:** pcrec refuses all (`requires module 'verbs'`,
  `(*COMMIT) is outside pcrec's scope`, `(?(...) is not implemented yet`). For the record (oracle):
  `(?<=a(*ACCEPT)b{1,2})x` on `ax` = (1,2), on `abbx` nomatch — ACCEPT ends the branch and the
  end-check still applies, so the branch's language is `{a}`, NARROWER than a lowering treating
  ACCEPT as epsilon. kindrow.def's ERASE column can express only "WIDER than its language"; when
  `verbs` lands its row must make the reverse row DECLINE, not set an erase bit. Future hole, not a
  finding against rev 0.
- **Anchors at the cursor end:** `(?<=a{1,2}$)` on `aa` [2-2], `(?<=a{1,2}\b)` on `aa b` [2-2]
  (oracle); `N_EOL` / right-side `A_CTX` are the reverse walk's START context, as W1 reads them
  today. HELD on reading.
- **Case folding:** `(?i)(?<=A{1,2})x` on `aax` [2-3]; classes are exact under fold. HELD.
- **Capture outside the lookbehind:** the evaluation sets no outer group; row 1's "no capturing
  group" is about the branch. HELD. (Speed-only aside: in a NEGATIVE lookbehind no capture is
  observable after it holds, so the conjunct is stricter than needed for that polarity.)
- **(e) The floor and a start offset:** `(?<=a{1,2})b` on `aab` from 2 = (2,3), `(?<!a{1,2})b`
  from 2 = nomatch, `(?<=a{1,2})x` on `aax` from 2 = (2,3) (sprobe): the body lies before the start
  offset, so `floor = max(0, cursor − W)` (absolute, not `search_from`) is right; accepts below
  `cursor − W` are impossible lengths even on a collapsed machine. HELD. `(?<=\ba{1,2})x` on `baax`
  nomatch (WD6's cell). HELD. Negative polarity on a superset (gate): no accept → holds, sound;
  accept → `range`. HELD apart from SOUND-1/2.
- **(d) §2.2's enumeration, hand-executed literally:** `(?<*(a|aaa))c\1` on `aaaca`, cursor 3;
  the branch's reverse machine accepts at s ∈ {0 (len 3), 2 (len 1)}. `farthest` floor 0 → 0; floor
  1 → 2; floor 3 → no accept. Order 0, 2 = rev 1's measured order (length 3, then 1); the S74 byte
  at floor t+1 is `subject[t]`, a real byte. HELD (5 walks traced, incl. `(?<=a{1,2}|b)x` on `bx`
  and `(?<=(a)|(aa))c` on `aac`, the latter served by gate → range since branch 1 has a group).
  Caveat for the HELD `commit` row only: `farthest` needs the machine built with `prune` OFF
  (`dfa.c:982-987` cuts lower-priority threads at an accept); every reverse build today passes
  `false` (compile.c:487, :555) but neither `RevWalk` nor §2.4's request names `prune`. `first` and
  existence are unaffected by pruning.
- **(b) `Nfa.erased`'s every writer and reader in the review tree:** writers — `frag_row`
  (nfa.c:596-603: `A_LOOK` → LOOK, `A_CALLOUT` → CALLOUT; `A_EMPTY`/`A_KRESET` record 0), the
  `A_REP` collapse (nfa.c:845-849, COUNT), `A_ATOMIC` (nfa.c:955, ATOMIC), resets (nfa.c:1072,
  :1089). Readers — `pcrec_vm_prefilter_window` (emit_vm.c:3776, `!erased`, on the FORWARD machine
  whose `\G`/`^` patterns are routed to ENG_ATTEMPT first: sound there), `lmwalk.c:114/183`
  (`lc_g1`: erased == 0 AND no `\G`/`\K` — the correct reverse form), `compile.c:554`
  (`lmnfa.erased == 0` before building ML, after `lc_g1` admitted), `kset.c:833` (`PF_WHY_ERASED`
  decline), `emit_dfa.c:12362` (a diagnostic print), `emit_vm.c:11311` (SOUND-4's stamp).
  Constructs that change acceptance and set NO bit: `\G` and absent-prev `A_CTX` rows in a reverse
  machine (SOUND-1/2) — direction narrowings, not lowering widenings. No existing reader other
  than the stamp over-reads erased == 0, because every one reads a forward machine or adds
  `lc_g1`'s conjuncts; arev's row 1 would be the first to read it alone on a reverse machine.
- **(c) exactness as a recorded fact:** exists today only as `Nfa.erased` (written by the lowering,
  reset per build) and, for the main machine's request, `fit.prefilter_collapsed`. A per-machine
  "built `exact`" request/record is new in arev and set by nobody yet (SOUND-4).

## Questions for a pcre2-reader

None needed: every PCRE2 fact used here was measured through the library (start offset, `\G`, `^`,
`(*ACCEPT)`, atomic/possessive cells).

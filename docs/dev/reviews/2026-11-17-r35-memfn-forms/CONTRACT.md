# CONTRACT findings: crit-memfn-forms

## Findings

### CONTRACT-1: the deny (and the lever at high heads) turns a compiling long cover into a REFUSED compile; no spec says so, and limits.md §3.12¶4 says the opposite
- status: CONFIRMED. Repro (comb tree, pattern files under CONTRACT/p/): `kit.sh comb OUT p/hex3400 /dev/null --window-search-width=4095 [--memfn=...]`.
  `[0-9a-f]{3400}`: default rc 0 (cover, 1 loop, 23,825 B); `--memfn=span-loop` rc 0 (14,984 B); `--memfn=no-span-loop` rc 1
  "pattern too large: 510342 bytes of emitted code (limit 500000)". Same at `{4095}` (612,507), with `-i` (753,040), `-e utf8`
  (511,695) and `-fmemfn-simd`. The threshold is k ~3,330: `{3300}` compiles (495,224 B), `{3330}` is refused (500,052).
  The lever does it too: `comb-h ... --harness=span-head=3397|3398|4095` are refused, while heads 0, 64 and 1000 compile.
  `--max-emit-code-bytes=2000000` makes the deny compile (509,924 B), and its answers are right (28/28 SAME).
  `\d{4000}` and `[ab]{4000}` stay under the cap with the deny (305 KB), but warn at the 250,000 advisory cap. The default
  does not warn. So the deny also changes stderr.
- severity: answer (a caller-visible compile refusal) + doc ; effort: S (spec) or M (a rung) ; blast radius: only callers who raise
  `--window-search-width` past ~3,300 with a wide-class window, plus the plan-A FALLBACK (forms OFF), which would ship this refusal as the default.
- where: docs/spec/registry.md §6¶8a (`span-loop`: "Answer-identical in every state"); tuning.md §2.43¶3d ("All three are
  answer-identical"); comb limits.md §3.12¶4 / tuning.md §2.56¶2 ("a width whose artifact exceeds the emitted-size cap also runs
  the engine ... the compile does not fail"); src/core/limits.def PCREC_MAX_VM_EMIT_CODE_BYTES (500,000; this cap binds), against
  PCREC_MAX_EMIT_BYTES (1,000,000; the cap the spec names).
- argument: in the strict sense the deny's answers are identical. But a refusal is a caller-observable state, and D80 wants it
  in the spec. Neither hunk mentions it. The covs2b sentence that should cover it is wrong for this shape: the code-byte cap
  binds first (~150 B per position puts I at ~3,330 positions), and limits.md §8.4's ladder has no rung that drops the cover to
  the engine, so the compile FAILS instead of running the engine. The promise is off by the same cap: its §3 Scope (plan B) says
  "~630 KB at 4095, under `PCREC_MAX_EMIT_BYTES` 1,000,000", but the binding cap is 500,000 code bytes. cards.py already lifts
  it for C4 (`--max-emit-code-bytes=4000000`, cards.py:303-305). D198 add. 1 says a pattern over the WIDTH limit "runs as
  today" (the engine). Here a pattern UNDER the width limit is refused, which is a second cliff no ruling names. Fix: (a) a
  sentence in ¶3d / §6¶8a: past about 3,300 wide positions the deny (I) can exceed the code-size cap and is refused; and
  correct §3.12¶4 to name the cap that binds; or (b) main's: a fit rung that declines the cover to the engine (then
  §3.12¶4 becomes true).

### CONTRACT-2: the shipped head 64 follows the launcher's ruling, not the promise's fallback, and that ruling has no in-tree record; the spec's label reads as if the cards had set 64
- status: CONFIRMED (text read).
  (a) Promise §3 "Scope", A's fallback, and §7 forms-now-or-next: if the cards cannot run before the landing, the forms land
  "BUILT but OFF (every span all-inline, as today)". The build instead ships H(64) (window.c `WF_SPAN_HEAD = 64`), per the
  launcher's ruling (COMMON). The two are byte-identical at every width <= 65: I checked 136/136 compiles at the default width
  (default == deny == base). They differ only at caller widths 66..4095 on the landing tree: H(64) loops there, while OFF would
  render I and be REFUSED past ~3,330 positions (CONTRACT-1). That is a real behavioural difference from the promise, and
  arguably the better one.
  (b) D149 asks for "a comment where it lives, plus a line in its design note". The comment is present (window.c: "UNMEASURED
  DEFAULT: CHOSEN grid top"). No in-tree design note carries the line. r45_reply rev 6 states only the post-card h\*, and it is
  not in this tree at all (CONTRACT-3). The launcher's ruling itself is in no decisions.md row, no plan.md row and no owner.md
  line at the freeze commit (grep).
  (c) tuning.md §2.43¶3d says "The shipped head is 64 positions (UNMEASURED: the grid top, set by the kit's form cards)". That
  reads as though the cards set 64. They have not run; they will REPLACE it. The label also drops "CHOSEN".
  registry.md §6¶8a states neither the number nor the label.
- severity: doc / design ; effort: S ; blast radius: the plan-A record and the D149 label.
- where: memfn/src/window.c:1474 area (`WF_SPAN_HEAD`); docs/spec/tuning.md §2.43¶3d; promise §3 Scope / §7.
- argument: D149 is satisfied at the code site but not at the design-note site. The promise's fallback text is silently
  superseded. Fix: one line where the ruling lives (decisions or the promise's next rev): "until the cards run, h = 64,
  UNMEASURED DEFAULT (CHOSEN grid top), superseding the all-inline fallback; differs from it only at widths > 65". Respell
  ¶3d as "(UNMEASURED DEFAULT: CHOSEN, the cards' grid top; the form cards will replace it)".

### CONTRACT-3: the spec and code cite `docs/design/memfn/r45_reply.md` §3, a file absent from the subject, from lane/covs2b and from main
- status: CONFIRMED. `git ls-tree -r 7506bca30 | grep -c r45_reply` = 0; it is also absent from `lane/covs2b` and `main`
  (`ls-tree ... docs/design/memfn`). It exists only on lane/memfn-r45 @69acf5376. Citers on the subject:
  docs/spec/registry.md §6¶8a (the new `span-loop` row), memfn/src/{window.c,compose.c,kit.h,options.def},
  src/core/internal.h, src/gen/memfn_sites.c (and, from the base, src/gen/{known.c,emit_dfa.c,memfn_sites.h}).
- severity: doc ; effort: S ; blast radius: every reader of the contract hunk. The caller-facing registry row points at a design
  that is not in the repository it ships in.
- where: docs/spec/registry.md §6¶8a, the `span-loop` row.
- argument: D80 makes the spec the contract, and the row defers its definition ("the span forms") to a missing file. The
  landing must carry r45_reply.md (merge lane/memfn-r45's doc), or the citation must name what IS in-tree. A landing-checklist item for main.

### CONTRACT-4: the lever's range has two sources, and pcrec's parse is wider than the kit's (signs, leading blanks)
- status: CONFIRMED. Repro: `kit.sh subject-h OUT p/hex32 /dev/null --harness=span-head=V`.
  - `-0`, `+8`, ` 8` (leading blank), `08` and `00000000000000000000008` are ACCEPTED. `-0` emits L (md5 = the force's).
    `+8` and ` 8` emit H(8).
  - `8 ` (trailing blank), `-1`, `4096`, `0x8`, `8a`, the empty value and 99999999999999999999999 are refused with
    "--harness=span-head= wants a head of 0..4095 positions".
  - The kit's own parse (compose.c lever_span_head) refuses any sign or blank. pcrec never shows it one, because
    cli/main.c:1544 runs `strtoul` (which skips leading blanks and takes a sign) and re-prints `%u`.
  - The bound 4095 is a LITERAL in cli/main.c. The kit's is `KIT_SPAN_HEAD_MAX (MF_WREACH - 1)`.
  - The comment beside the parse says "(N is validated by the kit, mf_lever)", but pcrec validates first, by its own copy.
- severity: maintenance ; effort: S ; blast radius: lever callers only (test-only).
- where: cli/main.c:1542-1552; memfn/src/kit.h `KIT_SPAN_HEAD_MAX`; memfn/src/compose.c lever_span_head.
- argument: a lever spelling the kit would refuse (`-0`) silently times L under a "head" name, which is the identity-check
  hazard the lever exists to prevent. If MF_WREACH moves, the CLI's 4095 goes stale with no compile-time tie. Fix: forward the
  text uninterpreted (`mf_lever(job->mf, "span-head=" + value)`, the kit refuses), or check digits only and add a
  `_Static_assert(4095 == MF_WREACH - 1)` beside the literal. Also see the general form under "Family" below.

### CONTRACT-5: the lever's docs omit that the FORCE also overrides it, and cli/CLAUDE.md's "spellings live ONLY in" list omits the cards script
- status: CONFIRMED.
  - `--harness=span-head=8 --memfn=span-loop` emits L, md5 64b55817, the same as the bare force (lev24). The deny emits I
    (lev23).
  - memfn.h's mf_lever comment says only "the deny `no-span-loop` still wins". cli/CLAUDE.md item (12) and internal.h say
    nothing about precedence. wf_span_head reads option row first, then lever, then default, so the force also beats the lever.
  - cli/CLAUDE.md says the harness spellings "live ONLY in `main.c`, `tests/compound/`, ...". memfn/tests/span_forms/cards.py
    spells `--harness=span-head=` (lines 11, 63, 791). It is outside the G7 fence (memfn/ is not scanned, as the promise
    says), so the fence holds, but the ONLY sentence is now false.
- severity: doc ; effort: S ; blast radius: card/identity-check authors.
- where: memfn/include/memfn.h:1719-1727; cli/CLAUDE.md "The harness build"; src/core/internal.h span_head comment.
- argument: a card cell that carried a `--memfn=span-loop` spelling would time L under every h label, and the lever's
  documentation does not warn about it. Fix: "either option-row spelling wins over the lever" in all three places, and add
  `memfn/tests/span_forms/cards.py` to cli/CLAUDE.md's list.

### CONTRACT-6: a promised reader is not built: formhash.c's own instance for the force spelling
- status: SUSPECTED deliberate deviation. Confirm it in the lane's report (denied to this lens). The promise, §3 "The option",
  "Its readers, each changed in the same build", lists "`memfn/src/formhash.c:425` (`s->opts = e->deny`): the force spelling
  gets its own form-hash instance, so measurement-set staleness sees L's bytes". The subject's formhash.c has no span-loop
  entry (grep: no `span-loop`, `span_head` or `WF_SPAN_HEAD`; the entry table is unchanged). kit-grid.tsv's `ver 7` header
  gives the likely reason: the cards are WHOLE-ARTIFACT cells, "so no card names a kit:form".
- severity: maintenance / doc ; effort: S (write the deviation down) ; blast radius: measurement-set staleness for L.
- where: memfn/src/formhash.c entry table (~:310-330); promise §3 "The option".
- argument: if no card reads a kit:form hash, the instance has no reader and D77 says do not build it. But the promise names
  it as owed "in the same build", and the deviation should be recorded where the promise's readers will look: the kit-grid
  header says it only implicitly.

### CONTRACT-7: RULING CHECK. The owner quotes are near-verbatim (one silent respacing, one marked elision). The 2026-11-16 owner rulings and the h = 64 ruling are recorded only in the promise, with an ambiguous polarity on one slug
- status: CONFIRMED (word-for-word comparison against `git show f2070d701:docs/dev/decisions.md` D198 addendum 1, line 10240;
  the same words appear at cover_cap.md:1258-1260, :813, :1364 and memfn/docs/requests.md:965 at that commit).
  - Quote 1 (promise §3 "The head h"). The promise has "default to sub span loops (excepting the measured head inline) then
    measure if inline was faster". The record has "I would default to sub span loops (excepting the measured head inline )
    then measure if inline was faster than the other way around."
    - The promise deletes the owner's space before ")" without saying so.
    - It truncates the sentence mid-clause with no ellipsis.
    - The meaning is kept.
  - Quote 2: "Then the speed dial option can be always inline should it prove that is faster". EXACT.
  - Quote 3 ("at 15:00"). The promise has "most all rx ... will inline due to being under the inline head portion". The
    record has "I predict most all rx will only have a short span and will inline due to being under the inline head portion
    of the prover."
    - The ellipsis is marked.
    - It elides "will only have a short span and", the owner's own reason (short spans).
    - It drops "of the prover".
    - Acceptable as marked, but the elided clause is the prediction drill (i) relies on, so quoting it in full costs nothing.
  - "His words name no number": TRUE of all three.
  - The owner's three rulings of 2026-11-16 have no record at the freeze commit in decisions.md, plan.md, owner.md,
    memfn/docs/requests.md or cover_cap.md (grep for the slugs and "forms now"): **forms-now-or-next** = FORMS NOW,
    **keep-short-spans** = NO, **near-miss-fix-later** = NO. Their only readable record is the promise itself, which says
    "via main"; any other record is in denied files (the journal/responses), which I did not read. The same holds for the
    launcher's h = 64 ruling (CONTRACT-2).
  - POLARITY: "near-miss-fix-later = NO" reads naturally as "do not leave the fix for later". The promise's §7 gives it the
    opposite meaning, "no fix in the first build until a timed card shows the loss", and COMMON and §4 agree with §7. The slug
    and its answer disagree in plain reading.
- severity: doc ; effort: S ; blast radius: the decision record (memory pcrec-plain-words-not-ids: the owner cites slugs).
- where: promise §3 lines 473-476, §0 rev-5 header (lines 61-63), §4 Disposition, §7.
- argument: D198 add. 1 is the only DECISION-tier home of the owner's rendering words. Rulings that bind a landing (plan A, no
  short-span exception, no near-miss skip, h = 64 pending the cards) belong in a decisions row, or a D198 addendum, with the
  owner's words verbatim and the slug's polarity spelled out ("near-miss fix in this build: NO").

### CONTRACT-8: the standing questions. The PAIR row and the VALUED lever: which family they join, the general form, and its unlocks with triggers
- status: design answer (no defect).
- severity: design ; effort: M (when triggered) ; blast radius: the kit's lever and option families.
- where: memfn/src/options.def (`span-loop`, MF_OPT_PAIR); memfn/src/compose.c (`kit_levers[]` + lever_span_head); cli/main.c
  harness parse.
- argument:
  - **The PAIR row** is the kit's FIRST pair row. It is the n-th member of the project's force-pair family: pcrec's own
    axes' deny/force pairs, and `-fmemfn-simd`, whose §2.43¶1 rule ("the deny ... passed with the force, wins") it copies.
    The registry (§6¶7, cli §1.16¶1, the `--list-axes` header) and mf_opts_check had parsed pair rows since R4a, so the row
    reuses the existing form. It is no new mechanism.
  - **The VALUED lever** `span-head=N` is the kit's first VALUED `mf_lever`, after the booleans `run-tie-left` and `mfind`.
    On pcrec's side it is the THIRD valued harness option, after `--harness=measures` (a file) and `--harness=restore=ARM+ARM`
    (a list).
  - Each valued option carries its own hand parse in cli/main.c. CONTRACT-4 shows the cost: a second range literal and a
    wider grammar than the kit's.
  - **The general form**: one declared LEVER TABLE in the kit (name, kind bool | uint range | list, its doc), parsed only by
    the kit. pcrec's harness forwards the text uninterpreted (`--harness=lever=TEXT`), as `--memfn=` already forwards
    options (cli §1.16¶1: "pcrec never splits, sorts or looks up an option").
  - Unlock 1: no per-lever pcrec code and no duplicated range. A new card-swept kit constant needs no pcrec change.
    TRIGGER: the second valued kit lever, for example a card sweep of any D149-labelled kit constant (vrun widths, cut-overs).
  - Unlock 2: the identity check's "lever at h\* == rebuilt default" becomes a property of the table (default = the row's
    value). TRIGGER: the same.
  - SIBLING NOTED, NOT THE SAME: the measurement-set channel (`--harness=measures`, `kit.` rows into mf_art_begin) also
    carries kit-read numbers on one binary. Its rows are MEASURED COSTS that selection reads (D157 facts). h\* is a SELECTED
    value, a rule's output. So folding h into a `kit.` measure row would blur facts and picks. Keep them separate unless a
    second picked constant shows the two converging. TRIGGER: a card-picked kit constant whose pick rule reads only `kit.` rows.

### Rulings, verdicts (part b)
- **D76/D94 (abi)**: NO event owed by the subject.
  - Default == deny == base, byte-identical in all 136 compiled cases: 43 patterns x {byte, -e utf8, -i, -fmemfn-simd}. The
    other 36 were refused by both trees alike, for module gating. abi 108 is unmoved, and no MF_SITE_ABI or scaffolding change
    is in the diff.
  - The force moves bytes (82/136) only under an option. cli.md §1.16¶6 says the flag is no abi event.
  - On the landing tree the default differs from I only at caller widths >= 66. Those widths are new with lane/covs2b and ride
    its own abi event, so no prior text moves.
- **D149**: labelled at the code site. The design-note line is missing (CONTRACT-2).
- **D157**:
  - On a shipped compile pcrec says nothing new to the kit: `opts` is copied uninterpreted, from one constructor
    (memfn_sites.c:504, every site).
  - The harness `span-head=N` names a kit form parameter. That is sanctioned by the test-only lever family (D197 precedent
    `mfind`) and by D198 add. 1 (3), the owner's rendering direction carried to the kit for this request.
  - pcrec's comments that describe the forms (internal.h, cli/CLAUDE.md) follow the `mfind` lever's precedent. Held.
- **D197**: the lever is an instrument only.
  - `build/pcrec` refuses `--harness=span-head=8` as an unknown option.
  - The field is internal (src/core/internal.h), with no lib/ declaration, and is set only under PCREC_HARNESS.
  - The G7 fence ALLOW regex needs no entry: no fenced directory spells `--harness=span-head=`. The S3276-S3279 rows spell
    `span-head=N` without `--harness=`. Held.
- **D198 add. 1**: the width cliff holds as ruled. A second, size cliff under the deny is unruled (CONTRACT-1).
- **D174**: `span-loop` names what the artifact shows (a loop over a span), like its siblings `window-skip` and `vrun-*`. Held.
- **D80**: hunks are present in registry §6¶8a, §6¶8b and tuning §2.43¶3d. The refusal is missing (CONTRACT-1), and so is the
  citation target (CONTRACT-3). cli.md §1.16 and §2.4 already covered pair rows.

## PROBED-AND-HELD

Case counts are compiles or emitted artifacts. Answer cases are subjects compared against libpcre2 through kit/oracle.
- **Option row spellings** (subject, `[0-9a-f]{32}`): 20 states.
  - unset / force / deny, both orders in ONE string (the deny wins: I), repeated tokens, `--memfn=` empty, and alongside
    no-window-skip / no-window-search: all behave as the spec says.
  - Two `--memfn=` FLAGS: the later wins (`--memfn=no-span-loop --memfn=span-loop` gives L). That is as cli.md §1.16¶4
    states, so held.
  - Unknown spellings are refused with the kit's text: `span-loops`, `SPAN-LOOP`, `span-loop=1`, `force-span-loop`,
    `no-no-span-loop`, `span_loop`, and a leading or trailing comma. 7/7.
- **--list-axes**: the row is `span-loop pair any scalar --memfn=no-span-loop|--memfn=span-loop` on subject and comb. Both
  have 14 memfn rows, which matches registry §6¶8b's floor 14 (the reader is axes_registry_check.sh:186). The header names pair
  spellings, and run_axes.sh / memfn_arm.py split the `|`.
- **Lever**: 28 cases.
  - 0..4095 accepted. Heads >= 30 on hex32 emit I's bytes, and 4095 emits I.
  - 4096, -1, empty, `8 `, `0x8`, `8a` and the overflow value are refused. `-0`, `+8` and ` 8` are accepted
    (CONTRACT-4).
  - The bare `--harness=span-head` is refused as unknown, and `build/pcrec` refuses the whole option.
  - With two levers the later one wins. The lever with the deny gives I; the lever with the force gives L (CONTRACT-5).
- **Answers at the default width**: 30 artifacts x 71 subjects = 2,130 SAME, 0 DIFF. They cover default, force and deny, each
  under byte, -i, -e utf8 and -fmemfn-simd, plus heads 0, 1, 2, 4, 8, 16, 24, 30 and 31 under byte and -i.
- **Live at both SIMD settings**: under -fmemfn-simd the force differs from default and deny, and default == deny (md5). Held.
- **Width 4095 (comb), `[0-9a-f]{3400}`**: 13 artifacts x 28 subjects = 308 SAME, 0 DIFF. They cover default, force, -i
  default and -i force, the deny with the raised code cap, levers 0, 64 and 1000, and the default width with and without the
  deny (unanchored). Every subject set includes near-misses at offsets 0, 1, 63-66, 100, 1000 and 3397-3399.
- **Forced moved patterns**: 22 patterns x {force, force -fmemfn-simd, default} x 120 subjects = 7,920+ SAME, 0 DIFF.
- **Size caps** (comb): 3 states x {3400, 4095} x {byte, -i, utf8, simd}.
  - The k sweep for the deny (1600..3350): the refusal starts at k ~3330 (CONTRACT-1).
  - `a{4000}` (literal) is one run compare in all states, identical bytes.
  - `\d{4000}` and `[ab]{4000}`: the deny compiles (305 KB, with a warning). The default and the force loop (16 KB / 12 KB).
  - A 3,400-position mixed-class window with no repeats: all three states compile identically (706 KB; under the code cap).
  - `([0-9][a-f]){1700}` runs the engine (`unanchored`) in every state.
  - PCREC_MAX_EMIT_BYTES (1,000,000) is never reached by these shapes. PCREC_DEFAULT_WARN_EMIT_BYTES (250,000) fires for the
    deny only. The DFA, NFA and anchored state caps did not bind at 4095.
- **The default head boundary** (comb, width = k): hex64 and hex65 have no loop. hex66 has no loop either: the offset k-1 is
  the searched position, so the stretch at 64 is one position, and a loop needs two. hex67 loops 64..66 (`j < 67`), hex68 and
  hex70 loop. This matches the spec ("two or more").
- **Byte identity at the default width**: 43 patterns x 4 flag sets = 172. 136 compile with default == deny == base; 36 are
  refused alike by both trees. The force moves 82.
- **Named witness `\w{32}\B`** (features assertions,classes): the force loops offsets 0..30. Offset 31 is the skip position,
  and the after side at 32 is tested inline. Heads 30, 31 and 32 emit no loop. The promise lists it as a POSSIBLE mover at
  h\* <= 32, and its prediction is a superset by design, so this is held, not red.
- **Site opts**: one constructor (memfn_sites.c:504) copies `--memfn=` into every site, so the deny reaches every window site.
- **G7 fence**: no fenced path spells `--harness=span-head=`. The ALLOW regex needs no change.

CRITIC COMPLETE

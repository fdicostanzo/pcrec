# R29 — D6 adversarial panel over docs/spec/match_api.md ([M4.7g], 2026-08-18)

The project's FIRST spec/contract document ([M4.7f], merged ccfa3a3 after one
manager read) gets its first adversarial pass, riding the M4.7 close. Three
read-only critics, spawned 2026-08-18 ~10:45 EDT, all reports delivered by
~11:10:

- **Critic A (opus) — spec vs shipped artifact.** Emitted 24 fresh artifacts
  (default / --no-captures / -p foo / --emit-main / budget-limited / DFA-only
  / VM), five gcc-compiled drivers, nm/readelf for placement, python `re`
  oracle for spans. Never ran make; no timing (battery occupied the box).
- **Critic B (sonnet) — spec vs the ruled corpus.** decisions.md D26–D56,
  known_issues K9/K23, match_api_m4.md/engine_m4.md, both R22 files,
  graduation hygiene.
- **Critic C (opus) — the adversarial consumer.** Read the spec cold (no
  src/, no design docs), listed ambiguities BEFORE opening artifacts, then
  wrote consumer programs strictly from the spec-only reading and measured
  where the artifact surprised it. Probes under the session scratchpad
  (c/, art/ — session-temporary, not archived; findings carry the evidence).

**Panel verdict in one line: the MATCHING SEMANTICS are contract-grade — §5,
§5.1, §3 anchoring, §1 composition and §7 truncation all survived active
attack on both engines, span-for-span against python `re` — but the document
is not yet safe to integrate FROM: the library calling sequence (§8) cannot
produce a working program, the find-all instruction (§3.1) writes an infinite
loop, and both shipped doc-comments an embedder actually reads state a return
contract the spec's own §4 contradicts and the artifacts refute at runtime.**

Convergence note: A and C reached A1≡C4 independently (artifact lens vs
consumer lens, same defect), and A independently re-verified C's behavioral
probes (anchoring, untouched-on-failure, R22 spans). B's ledger cleared every
decision D26–D56 except one omission (B1).

## Findings and dispositions

Severity is the reporting critic's. Dispositions: **FIX-CODE** (emitter or
lib/pcrec.h change, lane), **FIX-SPEC** (spec text, lane), **FILED** (plan
row / follow-up, no change now), **NO-ACTION** (reason given). All FIX items
land via lane/m47g-fix with measurement; ✓ marks re-verification required
against a fresh emitted artifact.

### The give-up-code documentation defect (one defect, three sightings)

- **A1 / C4 — BLOCKER. FIX-CODE ✓.** The emitted rx_matchfn ABI comment
  reads "Return values < -1 are RESERVED for a future abort semantic; no
  pcrec-emitted matcher produces one today" — an affirmative false statement
  (measured: --step-budget=3 `(a|aa)+b` returns −2 from _match, _match_caps;
  --backtrack-frames=1 returns −3 from _search) and a direct contradiction of
  §4. Worse, spec §2 quotes a CORRECTED version of this comment as if it were
  the shipped text, and §3.5 mischaracterizes the contradiction as a mere
  omission — the one place the spec's checked-against-artifacts method is
  load-bearing. Fix the EMITTED comment to state the [FLOOR,−2] give-up
  space; §2 then quotes the real text; §3.5 rewritten to record the history
  accurately.
- **A2 — BLOCKER. FIX-CODE ✓.** lib/pcrec.h's generated-searcher contract
  comment (~318–325) says the int return is two-valued (1/0) — under that
  reading `if (rx_search(...))` treats a give-up (−3 observed) as "matched".
  Fix the comment to name the negative give-up space. (The --emit-main
  main() already handles all three codes — the emitter knows what the header
  denies.)
- **A12 — NIT. FIX-SPEC.** §4 "a DFA artifact never EMITS these codes" →
  "never RETURNS" (DFA --emit-main literally emits the handler text).

### Library calling sequence (§8) — C's root-cause cluster

- **C2 — BLOCKER. FIX-SPEC ✓.** `pcrec_default_options()` is never
  mentioned; the spec-only initialization (zero-init) makes EVERY compile
  fail ("invalid symbol prefix"). §8 gains the mandatory init step and
  closes the NULL-prefix misreading.
- **C3 — BLOCKER. FIX-SPEC ✓.** `pcrec_output` used but never defined;
  malloc'd buffers and `pcrec_output_free()` unstated — a spec-only consumer
  leaks on every compile, and §5.2's "no lifecycle to manage" (match-path
  scoped) actively points away from the free function. §8 gains the type,
  the ownership rule, and the free call.
- **C13 — MAJOR. FIX-SPEC.** §7's "detectability instrument"
  (rx_info.pattern_len) is only reachable by string-searching emitted C
  source at compile time; the section never says so, and never gives the
  one-line pre-flight a consumer can actually write
  (`strlen(pattern) != known_length`). State both.
- **Root-cause fix (C's synthesis), adopted:** §8 gains ONE worked,
  compiles-as-written example — init → compile → check error → use
  out.c_src/h_src → pcrec_output_free — which closes C2, C3 and most of C13
  together. The lane MUST compile and run the example verbatim before it
  goes in the document.
- **B1 — MAJOR. FIX-SPEC.** D56's caller-facing guarantees are absent:
  pcrec_compile() never abort()s the caller (ctx_nomem routing; two
  deliberate residual aborts are internal-invariant/detached-StrBuf, not
  allocation failures), and a pattern can be REFUSED for compile-side
  resource reasons distinct from syntax errors (PCREC_MAX_SUBSET_ELEMS
  narrowing, D56). §8 gains both. Not a D26 wording matter — a behavioral
  safety promise the rulings make part of the surface.

### Find-all and entry-point semantics

- **C1 — BLOCKER. FIX-SPEC ✓.** §3.1's only find-all guidance ("restart at
  the previous match's end") is an infinite loop for any empty-matching
  pattern (measured: `a*` on "bbb" spins at 0). The spec states the
  empty-match advance rule (zero-length match at p → next search starts at
  p+1; note the rule's lossiness vs PCRE2's NOTEMPTY retry protocol, which
  pcrec does not offer; note the byte-vs-character caveat that M5 will
  sharpen) — verified against python `re` finditer behavior before landing.
- **C8 — MAJOR. FIX-SPEC.** "all report engine give-up THE SAME WAY" (§4) is
  true of the CODE SPACE but false of OCCURRENCE: measured, same (pattern,
  subject, position), _search returns 0 (DFA prefilter resolves it
  definitively) while _match/_match_caps return −2 (budget exhausted).
  Budget exhaustion is a property of the entry point. §4 reworded to promise
  code-space uniformity only, and §3.3's ergonomic framing gains the caveat.
  (C's sharper two-phase case — _search 1 then _match_caps give-up — was NOT
  demonstrated (possessification closed it on the test pattern); recorded
  inconclusive, not asserted.)
- **C10 — MAJOR. FIX-SPEC.** _search caps are ABSOLUTE offsets into s
  (measured), never stated; §3.3 answers this for _match_caps, §3.1 doesn't.
  One line.
- **C11 — MAJOR. FIX-SPEC.** "untouched on failure" (§5) never says a
  give-up is a failure for this rule. It is (measured; the generated source
  states it outright: "UNTOUCHED on every negative return, give-up
  included"). One clause.
- **C9 — MAJOR. FIX-SPEC.** The caps[k]-is-group-k identity is load-bearing
  for §5.1's examples and never stated — against the counter-signal of
  rx_group_entry.slot's existence. State it for captures-on builds.
- **C21 — NIT. FIX-SPEC.** `0` = no-match (_search) vs zero-length success
  (_match): one cross-reference line in §3.3.

### Reflection surface (§6, §6.3)

- **A3 — MAJOR. FIX-SPEC.** §6.3's "EVERYTHING rx_info states is also a
  compile-time macro" is false for 9 of 15 fields (measured: only ncaps,
  engine, engine_why, step_budget, work_budget, frame_capacity mirror) —
  including ngroups, the one §6.2 works hardest to distinguish. Narrow to
  the six real axes.
- **A4 — MAJOR. FIX-SPEC.** §6.3's masking rule is true for rx_info.flags
  (measured: denial bits emit `.flags = 0ULL`) and FALSE for the macros —
  every named axis visibly moves them (RX_VM_STRATS 0x1→0x2 under
  NO_POSSESSIFY, etc.). Adopt lib/CLAUDE.md's framing: flags mask REQUESTS;
  macros report what the emitter DID.
- **C5 — MAJOR. FIX-SPEC + FILED.** The D46 macros live in the emitted .c,
  not the .h — the §6.3 `#if` use case is unreachable in the split form the
  CLI produces by default. Spec states the visibility. Whether the macros
  should ALSO be emitted into the header is a design question — FILED as a
  candidate note on the plan's M4-follow-up territory, not decided here.
- **C12 — MAJOR. FIX-SPEC.** ENGM_DFA/ENGM_VM presented as constants; they
  exist only in comments (grep: zero #defines). Spec writes the numbers
  (`1 = DFA, 2 = VM`) instead of names a consumer cannot type.
- **C14 — MAJOR. FIX-SPEC.** rx_info.abi: state the current value (2), and
  state the pre-v1 honest advice (do not build on it yet, §9 posture).
- **A5 — MINOR. FIX-SPEC.** rx_info is NOT .rodata — it holds two pointers
  and lands in .data.rel.ro.local with two load-time relocations (readelf
  measured). "Zero runtime cost" is off by the relocations, and the
  distinction is exactly what a ROM/flash embedder cares about. State it
  precisely.
- **A8 — MINOR. FIX-SPEC.** §1's "exactly one of three groups" taxonomy
  misses PCREC_FEATURE_SET / PCREC_FEATURE_MODULES (PCREC_*-named,
  per-artifact, not in lib/pcrec.h — violating §8's own naming rule as
  stated); §6.3's catalogue omits <PREFIX>_ALTCLS_MERGES/_FACTORED, the only
  D46 stamps that also appear on DFA artifacts. Taxonomy and catalogue both
  amended.
- **A10 — MINOR. FIX-SPEC.** rx_ctx.ncap's "watermark mid-match" semantics
  have no producer (every call site sets 0). Flag as pending the way §6
  flags nnames/groups.
- **C19 — MINOR. FIX-SPEC.** Masked-flags round-trip: tell the consumer how
  to see which bits legitimately vanish (pointer to the lib/pcrec.h
  catalogue is fine; say that's where to look from §6.3 AND §8).
- **C20 — NIT. FIX-SPEC.** "sorted, bsearch-able" — by what key? State it
  (lane checks the design text; groups is NULL today so this is a promise
  being wired, not measured behavior).
- **B2 — NIT. FIX-SPEC.** frame_capacity sentinel asymmetry (options 0 =
  auto-size vs rx_info −1 = unbounded, same field name): state the asymmetry
  explicitly at both sites. No ruling violated (none exists for the options
  side).

### Method/evidence hygiene in the spec's own text

- **A7 / C15 — MINOR. FIX-SPEC.** §3.5 quotes the DFA emitter's rx_match
  body as "the emitted body" (singular) and its ellipsis elides exactly the
  sentence "Unreachable on this engine — a DFA artifact has no counter to
  exhaust" — verifying the propagation claim against the artifact where the
  branch can never execute (the control-shares-a-source failure class this
  project has already catalogued). The claim is TRUE (A proved it on the VM:
  −2/−3 live). Fix the evidence: quote both engines' shapes, restore the
  elided sentence, and keep the DFA-anchoring check visible (C15: the elided
  `if (found != 1 || caps[0][0] != ctx->pos)` is the ONLY thing making the
  DFA path honor §3.2).
- **A6 — MINOR. FIX-SPEC.** §3.2 "no search loop" is true of the VM emitter,
  false of the DFA emitter (which implements match-here as full search +
  start filter; answer still correct, measured both engines). Spec states
  the SEMANTIC claim (anchored; a match elsewhere is not reported) and drops
  the implementation claim.
- **A9 — MINOR. FIX-SPEC.** §1 cites `--prefix foo`; the CLI only has `-p`
  (measured: unknown-option error). Fix the flag spelling.
- **A11 — NIT. FIX-SPEC.** §3.1 claims an `if (caps)` guard inside
  --emit-main main(); main() has none (caps is never NULL there). Trim the
  claim to the search body, where it is true.
- **A13 / C18 — NIT. FIX-SPEC + FIX-CODE ✓.** §2's type order differs from
  the emitted ABI block (rx_renderfn placement) — spec reordered to match.
  The emitted prefix-independent comment hardcodes "== RX_NCAPS" under
  custom prefixes (r22a.h says RX_NCAPS where the macro is R22A_NCAPS) —
  emitter comment reworded prefix-neutrally (cheap, rides the A1 edit).
- **A14 — NIT. FIX-SPEC.** "only the file split differs" — the
  self-contained form also omits the PCREC_GEN_<PREFIX>_H guard (measured
  via header_name == NULL). One clause.
- **C16 — MINOR. FIX-SPEC.** rx_renderfn's sizing protocol (out==NULL,
  outcap==0 → returns would-be length) is shipped ABI text and absent from
  §2. Add it.

### Contract elements the panel says are missing entirely

- **C6 — MAJOR. FIX-SPEC.** Thread-safety/reentrancy never mentioned.
  Measured favorable: no mutable statics in any of seven artifacts; four
  matchers in one program ASan/UBSan clean. The spec gains the promise
  (concurrent calls safe with distinct caps buffers; no global state) as a
  CONTRACT constraint on future emitters — manager-ruled here, flagged for
  Frank's eyes at the close since it binds future engine work.
- **C7 — MAJOR. FIX-SPEC.** Subject-side contract unstated: NUL bytes in the
  subject are ordinary bytes (§7 covers only the pattern side), and the
  matcher never reads s[n] (measured under ASan on an exact-size buffer).
  Both promises stated — they are what the (s, n) signature is FOR.
- **C17 — MINOR. FILED.** No `extern "C"` guards in emitted headers. A real
  first-hour C++ integration cost, but an emitter surface change — filed as
  a candidate follow-up row, not landed in this pass.

### No-action

- **C's §3.3 note (ctx->caps/ncap "read as ordinary input") and caps_out ==
  NULL tolerance** — folded into the §3.3 edits above (C8/C11 touch the same
  paragraphs), not separate findings.
- **D26 guard held by all three critics**: zero findings demand
  PCRE2-identical diagnostic wording. Nothing to strike on tier grounds.

## Inconclusive (recorded, not resolved)

- Callout-lifetime bullets in §5 and §4's trap obligation: no producer
  exists to test against (both critics agree). Stays as written, explicitly
  design-promise-status.
- §7's libpcre2 ZERO_TERMINATED half: verified by the m47f lane at
  authoring; not re-run by this panel (out of lens; box busy). Standing.
- C8's sharper two-phase give-up case: not demonstrated; mechanism
  plausible; left open, no spec claim made either way.

## Clean ledger (summary — full detail in the critics' delivered reports)

- B cleared D26, D38+addenda, D39, D40+hygiene, D41, D42.1–.8, D43 (via
  D44.5 supersession — spec states the FINAL formula), D44, D45 (correctly
  out of scope), D46 (deferral to lib/pcrec.h verified accurate), D47,
  D49, D50–D55, K9, K23, C1–C11 table line-by-line, both R22 files,
  rx_renderfn's unconditional-declaration claim.
- A verified: §1 composition end-to-end (four prefixes, one TU, one binary,
  a shared rx_matchfn* array; ABI blocks byte-identical; exactly four
  exported symbols per artifact), §2 struct-tag reasoning (typedef absent,
  collision confirmed), §3.1 edge inputs (NULL/0, startpos>n, ==n, ^
  absolute on both engines), §5/§5.1 span-for-span vs python re incl. both
  R22 rules on both orderings, §6 counts (ngroups lexical, ncaps structural,
  --no-captures worked example exact), §6 pattern escaping (quote, tab,
  backslash, raw 0x01 all emit valid C), §7 truncation end-to-end through
  pcrec_compile(), §8 probe (a( b → −1/pos 1/PCREC_ERR_INPUT_PATTERN), §9
  commit lineage (c113890 exists, spec lands c24d699).
- C verified consumer-side: §4's error handler writable from the table
  (constants defined even on DFA artifacts), §6.2's worked example
  predictable before running, §9 posture plannable.

## Reflection

1. The panel earned its keep exactly where D27's lesson said it would: the
   manager's end-to-end read (thirtieth session) checked the spec AGAINST
   THE DOCUMENT'S OWN CITATIONS and found it coherent; the critics checked
   it against the ALPHABETS the document didn't choose — the shipped
   comments (A1/A2), the consumer's first hour (C2/C3), the rulings' full
   surface (B1) — and found the blockers there.
2. A7 is this project's check-design failure class appearing in a SPEC:
   evidence quoted from the artifact where the claimed behavior is
   unreachable. The catalogue entry ("controls sharing a source with what
   they control") now has a documentation instance.
3. The §2 paraphrase-as-quotation (A1) is the finding to remember: in a
   document whose authority rests on "checked against the shipped surface",
   an idealized quotation is not a small inaccuracy — it is the failure
   mode the document exists to prevent.

Fix pass: lane/m47g-fix (worktree), all FIX items above + the D57 note
update (rx_info struct-tag spelling blessed at this session's open — §2's
"still an open ruling" text now cites D57). Re-verification: every ✓ item
against freshly emitted artifacts; the §8 example compiled and run
verbatim; C1's protocol vs python re finditer; full `make test` async in
the worktree after the emitter comment edits (codegen structural checks pin
emitted text and may need floor updates travelling in the same change).

## Amendments from the fix pass (lane/m47g-fix, merged d523a88 — measured corrections to this review's own statements)

The lane re-measured every disposition rather than transcribing this
file, and three findings came back different from the review's text; the
spec records the measurements, and so does this amendment block:

1. **A3 undercounted.** Six of fifteen rx_info fields mirror as macros
   on a VM artifact (as A3 found) — but on a DFA artifact the mirror is
   **ncaps ALONE**: no <PREFIX>_ENGINE, no budgets, no _VM_* macros at
   all. A consumer `#if`-ing on <PREFIX>_ENGINE writes code that does
   not compile against half of what pcrec emits. Spec §6.3 states the
   per-engine inventory.
2. **C8's asymmetry runs BOTH ways.** Besides search=0/match=−2, the
   lane measured `--backtrack-frames=1` over "xxaaaaab": _search
   returns −3 while both anchored entries return a clean −1 — a
   demonstrated mirror of the "sharper two-phase case" this review
   recorded as not demonstrated. (A1's −3-from-_search claim was also
   subject-sensitive: true on "ab", not on "aaX"; the spec names the
   subject.)
3. **C1 needs NO duplicate suppression.** The advance rule alone
   reproduces `re.finditer` 12/12; the "suppress the duplicate" clause
   in the fix charter had no population. The REAL residual is sharper
   than this review stated: python 3.7+ finditer DOES the
   NOTEMPTY-style retry (|a over "aaa": 7 spans), so the documented
   loop is lossy against our own base oracle — not just PCRE2 — on
   empty-preferring patterns (|a, a*?, a??). Exact everywhere the
   pattern prefers a non-empty match; the spec states the class.

Also landed under this review's umbrella (manager scope-add from
Frank's live design question, same lane): the ALTCLS empty-alternative
merge barrier is now PINNED — tests/altcls/altcls.rxt (17 rows over
(?:a||b) / (?:a||b)c / (?:a|b||c|d)x, corpus 10,350→10,369),
stamp assertions MERGES 0/0/2 beside a live positive control, all three
patterns added to the differential population. SABOTAGE-VALIDATED: a
compiler built with the exact forbidden bug (altcls.c's run scan
continuing across A_EMPTY) turns 7 corpus rows and all 3 stamp pins red
while the positive control stays green. Row-design note for future
citation: '(?:a||b)c' on "bc" is correct but does NOT discriminate under
the sabotage; the discriminating subject is "c" → (0,1).

Verification-thoroughness note recorded in the lane's own journal entry
and worth keeping: §5.3's concurrency promise is warranted by the
shipped, sabotage-validated TS-1/TS-2/TS-3 thread suite, found only
because the full suite ran — check whether the suite already
establishes a property better before writing an ad-hoc probe for it.

One new defect found BY the fix pass's own UBSan probe, out of its
scope, filed as **K27**: the emitted search body calls
memchr(NULL, c, 0) on the contract's own legal s==NULL/n==0 edge —
correct behavior, technical UB, invisible to the suite because the
harness never passes NULL.

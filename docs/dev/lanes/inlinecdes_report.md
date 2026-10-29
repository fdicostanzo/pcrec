# inlinecdes — [INLINE-C] design note, pattern side (report)

Lane inlinecdes (opus), 2026-10-26, branch `lane/inlinecdes` from `570b601d6`.
Design only: nothing under `src/`, `tests/`, `docs/spec/` touched; no make
run. Deliverable: `docs/design/inline_c.md` (PROPOSED, rev 0), indexed in
`docs/design/CLAUDE.md`.

## Summary (what a fresh agent resumes from)

The note designs the pattern side of inline code on Frank's binding answers
Q1-Q8 (`inline_c_requirements.md` section 8):

- **One node, one call site.** `(?C)`, `(?Cn)`, `(?C"name")`, a tagged
  string ``(?C`c: ...`)`` and `(?{ ... })` all parse to `A_CALLOUT`; the
  reserved `VE_CALLOUT` gets its producer; one emitter takes the callee from
  a binding-row table (inline code = a direct call of a generated `static`
  function; named/numbered = D38's `extern const rx_callout_ref
  rx_callout_<name>`).
- **Site view without touching `rx_ctx`:** `ncap` the per-site constant;
  enclosing groups read last-closed via [M6.5.2]'s existing publish-at-close
  (the marked set becomes the union of every reader's refs); slot 0 carries
  the attempt start.
- **Return handling** extends `match_api.md` §4¶10's one table with two trap
  rows (a predicate returning > 0; a length past the end or off a character
  boundary).
- **Width classes** `W_PRED`/`W_ANY`: embedded code is a yes/no check unless
  tagged `consume` (catches `return 1;` loudly; gives the optimizer the
  empty-string fact). Bindings are full range (composition).
- **Optimizer rule:** to every pass a site is a capture- and position-reading
  consumer (the `A_BREF` class) of width [0,0] or [0,inf); this covers
  possessification, start facts (required runs, min width) and the prefilter
  language. Control: `make test-axes` plus the libpcre2 differential.
- **Reference semantics:** the unoptimized backtracking order = libpcre2 with
  `NO_AUTO_POSSESS|NO_START_OPTIMIZE` (Frank question 1).
- **Generated function** `<prefix>__code<seg>`, defined LAST in the `.c`
  behind `#line` (no restore needed), macro set `RX_SUBJ`/`RX_POS`/
  `RX_START`/`RX_CAP_S|E|LEN|P|SET(n)`/`RX_G_<name>`/`RX_PASS`/`RX_FAIL`,
  `#undef`ed after each; `code-header c "x.h"` head line + CLI; `ext harness`
  `link c "stub.c"` for tests (no new format line).
- **`verify`** (per segment, tail only in v1) is a VM HYBRID with one new
  attempt row `scan-end` (scan gives `[s,e)`, segments run at `e`, veto runs
  the VM anchored at `s`); a declared eligibility table with downgrade rows
  (all answer-safe) and a deny axis `-fno-callout-verify`; equivalence argued
  in §4.4. Gains only where the artifact delivers no groups and the scan
  proves the end; capture-reading segments wait for [CAP-SPAN].
- **Trust gate:** `--allow-code=c` on the command line only (no `features`,
  no config `pcrec` line, no env); local = FILE operand / `--pattern` /
  library pattern; reached code needs `sha256=` on EVERY `include`/`lib` line
  of its chain; pins are verified whenever present; `--list-callouts`.
- **Artifact as callout:** `<prefix>_match` bound by one const line; the
  `RX_CALLOUT_PCRE2(name, fn, user)` wrapper for PCRE2-convention functions;
  `PCREC_ERR_ABORT` reserved by name, not emitted.

## Conflicts found (STOP RULE) — note §10a

1. Q6 vs D38: none (D38 is native); the requirements' PCRE2-convention
   recommendation is superseded.
2. [M4-CALLOUTS] step-2 plan text still describes a `pcre2_callout_block`-
   mirroring native ABI: stale against D38; recommend amending the row body.
3. engine_m4.md's "apply the prefilter uniformly" (c) is unsound for D38's
   consuming callouts: recommend erasure by width class.
4. Q4 "DFA finds the match" vs D36/F7 "callout patterns are VM-only":
   recommend realizing `verify` as a VM hybrid (F7 holds literally, no new
   artifact class).
5-7. Gaps resolved without conflict: segment `user` NULL in v1; match start
   in slot 0 rather than a new `rx_ctx` field; the requirements' untagged
   `(?C{...})` examples are binding strings, not code.

## The staged plan (note §9)

1. Call site, extern-bound (`callouts`; [M4-CALLOUTS] step 2). abi event.
2. Embedded C (`code-c`), local-only gate (reached code refused). abi event.
3. `sha256=` pins + `--list-callouts`. No abi event.
4. `verify`. abi event; measurement card.
5. `RX_CALLOUT_PCRE2` wrapper (may ride stage 1's bump).
6. Later, not designed: template side, `post`, non-tail verify, `user=SYM`,
   lifting position refusals, `--check-c`, other languages.

Sabotage placeholders S-IC1..S-IC18 (+S-IC6b); the 20 draft tests map 11 to
stages 1-4 and 9 to the template phase (§9.3). Every stage's identity-gate
expectation is zero movers in the existing corpus.

## Open questions for Frank (note §10)

1. Which PCRE2 answer is pcrec's when PCRE2's own optimizations change it?
   Leaning: optimizations off.
2. Embedded code a yes/no check by default (positive return, fall-off or
   past-the-end length traps; `consume` opts into lengths)? Leaning: yes.

## Observations for the manager

- The plan row [M4-CALLOUTS] body is stale against D38 (conflict 2); the
  row is the manager's to edit.
- No PCRE2 re-probe of DT-1.6 under the proposed reference flags was run
  (the requirements' P10 answer used default flags); owed by stage 2.
- The note proposes D-ids only as placeholders; none was minted.

## STATE AT HANDOFF

Committed on `lane/inlinecdes`: the design note, its `docs/design/CLAUDE.md`
line, this report and its history-index line. Validation: none owed (design
lane, no make); the commit hook's staged checks passed on every commit.
Rulings file `docs/dev/lanes/inlinecdes_rulings.md` re-read before the
report: "(none yet)", so no ruling applied.

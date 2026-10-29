# rwsurvey report: where neighbour rewrites and set-scan edges would apply (lane rwsurvey, 2026-10-26)

Survey only; no change to `src/`, `tests/` or other docs (no build go). Instrument: a throwaway probe
under `studies/rwsurvey/` (its CLAUDE.md lists files and the rebuild command): a COPY of
`src/core/compile.c` with dump hooks injected by `sed` after parse, the tree hooks, altcls, atomic
discharge, engine selection and `lower_enc`, plus a hook around every `pcrec_scanedge_dfa` call.
Everything below is a count or a dump from that probe unless it is labelled HYPOTHESIS.

Populations. CORPUS = the 6,174 `pattern` rows of the 297 `tests/**/*.rxt` files (head `features`,
`encoding`, `flags i`, `engine` applied; 5,735 compile far enough to dump, 439 are refusals or
`\x00` skips). BENCH = the 367 pcrec-bench `bench/*/patterns/*.rx` files (read-only; 351 dump).
Frank's framing (2026-10-26) applies to Q2/Q3: the corpus SOURCE text is not a fair population for
the rewrite questions (it was written by us, so it shows what we wrote), so the tables report it as
a lower bound and the intermediate-form evidence (what a pass leaves) is the primary evidence.
For Q4 the corpus IS a fair population (the class splits are made by the compiler).

## Q1 Pipeline inventory (execution order)

`compile_driver` (src/core/compile.c) wraps everything in an attempt loop (`:2182`, bound
`COMPILE_MAX_ATTEMPTS`, `:655`): a size-cap or DFA-overflow retry re-runs EVERY step below from the
parse (measured: 190 of 5,735 corpus compiles and 30 of 351 bench compiles ran 2 or more attempts).
Within one attempt:

| # | step | where | layer | runs more than once / fixpoint? |
|---|---|---|---|---|
| 1 | parse: lexer to AST; case fold (D23: class bitmaps widened at parse, `cls_fold_select`, parse.c:744; a caseless backref folds at match time through the residual entry); counted repeat parsed as `A_REP{rmin,rmax}`; option scope resolved into the choice of node (D62: `(?m)^` -> `A_CTX`, `^` -> `A_CTX` pin, `$`/`\Z` -> `A_EOL`); `pcrec_wrap_bare_anchor` (parse.c:296) wraps a repeated bare anchor as `<anchor EMPTY>`; `${name}` -> `A_VAR` (module vars; value is a match-time input, never a compile-time one); `(?&n)` -> `A_CALL` | src/parse/parse.c:2216, compile.c:2625 | AST | once per attempt |
| 2 | tree-hook list: composer (`.rxt` `with`/definition injection, `rxt_compose.c`), then derive (`derive.c`: match-split Q, kills `\G`/non-multiline `^` `\A` to a never node, prune) | compile.c:2658-2664 | AST, rebuilds nodes | once; hooks are NULL on a plain compile |
| 3 | altcls: stage 1 merges adjacent bare-class alt branches (`b\|c` -> `[bc]`), stage 2 prefix-factors (`frank\|fred` -> `fr(?:ank\|ed)`) | src/opt/altcls.c, compile.c:2667 | AST, rebuilds nodes (allocates a fresh `A_CAP` over a merged class) | stage 2 has an internal loop (altcls.c:215, depth cap); the pass itself runs once |
| 4 | `pcrec_discharge_atomic`: deletes `A_ATOMIC(A_REP(X))` whose possessify verdict is a no-op | atomic.c, compile.c:2683 | AST | once |
| 5 | `pcrec_callgraph_build`: the only writer of `u.call.body`; Kleene fixpoints for minw/maxw/cwmin; splice/linkage per call target | callgraph.c, compile.c:2702 | graph over the AST | fixpoints inside; pass once |
| 6 | facts E1 seal: kind mask and nullability derived and STORED (compile.c:2712) | facts.c | facts | once |
| 7 | `pcrec_select_engine`: forcing analyses (fixpoint over engine masks), then on the VM engine only `run_possessify` (select_engine.c:497, called :1460) and `run_revdet` (:523) | select_engine.c, compile.c:2739 | AST (sets `u.rep.possessive`, `u.rep.revbody`) | possessify loops to a fixpoint, at most `SELECT_MAX_ROUNDS` = 8 (select_engine.c:97) because marking one quantifier changes another's follow; revdet is one walk |
| 8 | `pcrec_postresolve`: re-asks lookbehind fixed-width rules after the graph | postresolve.c, compile.c:2757 | checks only | once |
| 9 | `pcrec_lower_enc`: code-point classes to byte-sequence ASTs, sole producer of `A_WCLASS`; splices IN PLACE (never reallocates a group root) | lower_enc.c, compile.c:2810 | AST | once |
| 10 | facts E2 seal: re-derives kind mask and nullability on the lowered tree and refuses the compile if either moved (per the comment at compile.c:2712) | facts.c, compile.c:2826 | facts | once |
| 11 | NFA build `pcrec_build_nfa`: counted repeats UNROLLED into the spine (`X{m,n}` = m copies + a nested optional tail, nfa.c:789-830); `A_CAP` transparent; `CALL_SPLICE` callees INLINED (nfa.c:1005); the prefilter-collapse build rewrites `X{m,n}` to `X{min(m,1),}` inside the builder (nfa.c:810, only on a ladder rung); `pcrec_nfa_wrap_unanchored` (nfa.c:1244); facts E3 seal | nfa.c, compile.c:2848 | NFA | built up to 3 times: exact, collapsed (rung), and the marked builds below |
| 12 | D164 B3 `$` lowering: `pcrec_build_nfa_marked` lowers the end mark's tails (`$` before a final newline) into the machine, `pcrec_nfa_mark_distances`; forward, reverse and anchored copies (`xnfa`, `xrnfa`, `xadfa`); optional, adopted by `revend_choose_form` | compile.c:460, :527, :3010 | NFA | once per machine, optional |
| 13 | DFA build + Moore minimize (`pcrec_build_min_dfa` memoized across attempts, dfamemo.c:126; `pcrec_minimize_dfa`, minimize.c:74 iterates to a fixpoint) | ir/dfa.c:1546, opt/ | DFA | per machine (fwd, rev, anchored, notempty, x-fwd/x-rev/x-anch) |
| 14 | scanedge `pcrec_scanedge_dfa`: deletes scan-shaped state chains, per machine | scanedge.c, compile.c:3002-3004 and the `build_*` helpers | DFA | once per machine |
| 15 | emit (`pcrec_emit_dfa` / `pcrec_emit_vm`), kit delegation for search sites | gen/, memfn/ | text | once |

Fact: nothing iterates the pass list. The only fixpoints are inside single passes (possessify,
altcls factoring, the callgraph, minimize) and the whole-pipeline retry. "Passes run once; select_engine's
rewrite/`discharge` socket is deleted ([TOUR-5])" is src/opt/CLAUDE.md's own wording.
Counted-repeat handling and subroutine splice are inside the NFA builder (step 11), invisible to
every AST pass. `[VAR]` composes at match time, so it composes nothing for a compile-time rewrite;
the compile-time composition mechanisms are the `.rxt` composer (step 2) and `(?&n)` splice (step 11).

## Q2 Which passes create rewritable shapes

Method: the probe dumps the tree after steps 1, 2, 3, 4, 7, 9 and runs the shape detectors on each.
Codes: A = run X+/X* then optional/starred Y with Y a subset of X; B = `X+`/`X*` then non-multiline `$`
with the newline inside X; C = redundancy (empty node mid-CAT, adjacent equal-class repeats, repeat of a
repeat, trivial `{1}`/`{0}`, alternation with an empty or duplicate branch, redundant `A_ATOMIC`);
D = a context assertion after a maximal run whose truth the run already decides (`\w+\b`, `\d+(?!\d)`,
`(?m)[^\n]+$`), and two zero-width neighbours (`\b\b`, `\z` then a consumer).
Count = patterns whose tree carries the code at that stage (CORPUS, 5,735 dumped):

| code | source (after parse) | after altcls | after atomic discharge | after select (possessify) | after lower_enc |
|---|---|---|---|---|---|
| A absorb-optional | 6 | 6 | 6 | 6 | 6 |
| B absorb-EOL | 47 | 47 | 47 | 47 | 42 |
| C empty node mid-CAT | 83 | 83 | 83 | 83 | 83 |
| C merge-run (`\d+\d*`, `[0-9][0-9]?`) | 41 | 41 | 41 | 41 | 41 |
| C repeat of repeat | 178 | 178 | 178 | 178 | 178 |
| C `{1}` | 10 | 10 | 10 | 10 | 10 |
| C `{0}` (definition wrapper by design) | 149 | 149 | 149 | 149 | 139 |
| C alternation with an empty branch | 191 | **298** | 298 | 298 | 296 |
| C duplicate-branch alternation | 4 | 2 | 2 | 2 | 2 |
| C `A_ATOMIC` around a no-op / around `A_ATOMIC` | 9 / 1 | 9 / 1 | 9 / 0 | 9 / 0 | 9 / 0 |
| C `A_ATOMIC` around a rep already marked possessive | 0 | 0 | 0 | **57** | 57 |
| D context assertion implied after a maximal run (true / false) | 29 / 15 | same | same | same | same |
| D identical adjacent zero-width / `\z` then consumer | 8 / 17 | same | same | same | same |

First stage at which a code appears in a tree that did not carry it before (BENCH in brackets):
alternation-with-empty-branch is created by altcls in 107 corpus patterns [10 bench]; a duplicate-branch
alternation by altcls in 0 [1]; a redundant cut around a possessive rep by the possessify step in 57 [2].
No pass created an A, B or D shape in either population. So the pass-created set measured today is
exactly (c) below plus the witnesses in (a)/(b).

(a) A and (b) B: no pass produced one in 5,735 + 351 patterns, but the mechanism exists and is
demonstrated by constructed witnesses (probe dumps, not corpus rows):
- `\s+(?:\n|\r)?`: parse `<{\s 1,-1} {(|\n \r) 0,1}>`, after altcls `<{\s 1,-1} {[\n\r] 0,1}>`, and the A code
  fires at stage 3 only. Same with `[a-z]+(?:a|b)?c`.
- `(?:\s|\n)+$`: parse `<{(|\s \n) 1,-1} $>`, after altcls `<{\s 1,-1} $>`, and B fires at stage 3 only.
- `\s+(?:\n|\r)?$` chains both (altcls, then A, then B on the result): evidence that a table wants iteration,
  not a single pass (Q6).
- `(?>\s+)\n?` carries A under an `A_ATOMIC`; the discharge/possessify steps change the node that holds the
  run, so a table must see through the cut wrapper or run after discharge.
That is Frank's "it cleans up a previous optimization step" mechanism, shown to exist on altcls output
(class merge creates the subset) and shown to be empty on every pattern we or the bench authors wrote.

(c) redundancy the passes leave:
- altcls prefix factoring leaves alternations with an EMPTY branch: `f|frank` -> `f(|rank)` printed
  `(|EMPTY <r a n k>)`; `foo|foobar`, `/user|/users`, `in|instanceof`, `\.tar|\.tar\.gz`. Empty first means
  a lazy `?`, empty last a greedy `?` (priority order is the branch order). 107 corpus patterns, 10 bench.
  HYPOTHESIS: normalizing `(|X)` to `X??` / `(X|)` to `X?` would expose these to the repeat-based facts and
  to A/merge-run; not tested.
- possessify marks `u.rep.possessive` on a rep that already sits under the `A_ATOMIC` the parser built for
  `a++` / `(?>a+)`: tree `(>{a 1,-1+})` (57 corpus, 2 bench: qnt-poss-plus, qnt-poss-quest). Harmless today (the
  emitter treats the cut as a threaded context, `vm_cuts`); it is the pass leaving a duplicate marker.
- an empty node mid-concatenation: it does NOT come from option runs or `(?:)` (`a(?i)bc`, `a(?:)bc`, `a(?#c)bc`
  give `<<a b> c>`; the parser drops them) and `a(?:)bc` already yields `req_run 616263@1` under `--emit-facts`,
  identical to `abc`. The 83 corpus hits are all ZERO-WIDTH constructs: `pcrec_wrap_bare_anchor`'s
  `<anchor EMPTY>` wrapper under a quantifier (`x(\B)y` -> `<x (#1 <CTX155 EMPTY>)>`, `(\z)*`, `(?:\b)??`) and the
  derive hook's killed `\G` (`ab(?:\G)*cd` after the hooks: `<<<<a b> EMPTY> c> d>`, stage 2). So
  [REQ-EMPTYCAT]'s stray `A_EMPTY` is produced by the wrapper and the derive kill, not by parse-dropped
  constructs. The `req.c` handling was not traced here.
- repeat of repeat: 178 source-level (`(?:a+)*b`, `(?:\d+)+`, counted nests); altcls adds 4. A `{0,0}` DEFINE
  wrapper and its `A_CALL` splice are by design.
- (d) found while looking: context assertion after a run (`\w+\b`: 29 patterns true; Q5), identical
  adjacent zero-width (`\b\b`, a chain of `(?!a)(?!b)...`: 8), `\z` then a consumer / consumer then `\A`
  (`\zx`, `x\Ay`: 17, a branch that cannot match).
- After lower_enc, a class holding non-ASCII code points becomes `A_WCLASS` and a detector that reads
  `A_CLASS` stops seeing it: B drops 47 -> 42, e.g. `^[\s\x{200c}]+|[\s\x{200c}]+$` and `([^/]+)$` under utf8
  (the JS-style trim idiom). A table placed after step 9 must see through `A_WCLASS` (`pcrec_ast_seethru`).
- Subroutine and counted-repeat composition happen in the NFA builder: `(?(DEFINE)(?<w>\s+))(?&w)\n?` has the
  AST `<<{(#1 \s+) 0,0} CALL1> {\n 0,1}>`, so an AST pass sees a CALL, not a run, next to the optional; the
  adjacency exists only after splice (step 11). HYPOTHESIS: visible to a table only if it runs on the NFA, or
  after an AST-level splice; not measured.

DFA note (measured, probe `n`/`ncls` of the minimal machine): rewriting A on the DFA engine changes little
(`\s+\n?`: 2 states, 3 classes; `\s+`: 2 states, 2 classes: the language is the same, one byte class fewer),
while `\s+$` builds three extra optional machines (x-fwd/x-rev/x-anch, 4/5/3 states) and `\s+\z` builds
none. So B has the larger effect; A is mainly a VM and class-count matter.

## Q3 Outside-written patterns

Sources. bench/capability provenance (`provenance.tsv`): 41 authored + 29 EXTERNAL members (grok 7, vscode-json-grammar 5,
rebar-wild 5, CRS 5, OWASP validation 3, pcre2 testdata 2, moment-js 1, rust-regex testdata 1) and bench/litrun's 2
rebar-wild members (the same two noseyparker patterns). Every other bench set (altwide, bounded, email, loglines, sentinel,
syntax) has no provenance file and is authored or machine-generated (altwide/bounded: generated; email: a hand-inlined RFC 5322
specimen; sentinel: a re-use of capability members). The capability curation staging (`curation/wild`) holds only
excerpts, all adopted. No other third-party pattern list exists in either repo: `third_party/` is UCD data and two log
corpora (no patterns), `src/findings/*.rxt` are analyses, not patterns. So the outside-written population in
reach is 29 patterns; it is small, and a larger one would have to be fetched (bench-only question below).

Hits at SOURCE level (probe, stage 1), the 29 external members:

| external pattern (source) | code | shape |
|---|---|---|
| wild-waf-crs-942360-concat-sqli (CRS, verbatim) | A | `[^A-Z_a-z]+[\s\x0b]*?` : X+ then a LAZY starred subset (`\s` is inside the complement); no capture between |
| wild-waf-crs-942500-comment-obfuscation (CRS) | C repeat-of-repeat | `(?:[...]+)?` : a `?` over a `+` |
| wild-validator-ipv4-owasp (OWASP, verbatim) | C merge-run | `[01]?[0-9][0-9]?` : `[0-9]` then `[0-9]?` (= `{1,2}`), four times |
| wild-semdiv-empty-alt-repeat-pcre2 (pcre2 testinput1:4027) | C alt-with-empty | `(a\|)*\d` (a PCRE2 conformance case, kept as written) |
| wild-datetime-datefinder-alternation (rebar-wild) | C `{1}` | a trivial `{1}` |
| wild-logparse-syslogbase-expanded (grok) | C `{1}` | a trivial `{1}` |

Created by a pass in an external pattern: altcls leaves alternation-with-empty in wild-datetime-datefinder, wild-logparse-syslogbase and
wild-secrets-username-password-pair; datefinder also gets a duplicate-branch alternation.
No B hit and no D hit in the 29 (the `moment-iso8601` and `email-owasp` members the brief names carry none). Authored members with hits:
tail-space-eol and winpath-near-miss (B: `\s+$`, `[^<>:"/\\|?*]+$`), doubled-word `\b(\w+)\b` (D),
bounded nest2/nest3 (C), rec-define/bracket-array-define/email factored (`{0}` by design),
syntax qnt-plus-ctl `a+ab` and qnt-poss-plus (C merge-run, controls by intent).
Rate: 6 of 29 external patterns carry some code (5 distinct codes), 1 of 29 an A. HYPOTHESIS: the small sample cannot say whether
real-world trailing-whitespace trims are common; the corpus carries 28 distinct B patterns
(`\s+$`, `\s*$`, `^\s+|\s+$`, `(\s*)$`, `[\s\w]*$`, `\W*$`, ...), authored by us but they are the idioms users write; 8 of
those 28 have a capture around the run (`(\s+)$`, `([^/]+)$`), where the `$` rewrite still applies (only the anchor changes) but an A
rewrite across the capture would not (5 of the 6 A patterns have `capgap=1`: `(a+)(a?)$`, `(a*)(a*)\1\2b`).

## Q4 Scan-set reach

Method. Two probe binaries, same patterns: (base) the real `scanedge.c`; (set) a copy whose `shaped()` takes a class set S
(every class in S -> one successor, every other class -> one exit, `cls` = smallest class of S) and whose `same_shape()` also
requires equal sets (`mkscanedge_set.py`; every other precondition, view/accept invariance, chain-link, indegree, seed, slot cap
(`SCAN_MAX_EDGES`) and ordering is the real code). Count = scan-edge heads left after the pass (`scan_span` != 0), per machine,
per pattern. The set variant's artifacts are invalid; only the counts are used. Control: the base probe against the real
artifact's `RX_DFA_SCAN_EDGE` stamp: 5,712 corpus compiles compared, 5,590 agree (stamp != none iff the base probe kept a head in a
non-x machine), 121 are probe-says-edge and stamp-none (the machine carries an edge but is not the one emitted, e.g. `a\z`, `.*\z`),
1 the other way (`a\n{0,2}?$`); 343 bench compiles compared, 341 agree, the 2 others probe-says-edge (`\s+$`, whose x-machines are
the emitted ones, and `[a-z]{0,16384}?`).
So the numbers are machines BUILT, an upper bound on what an artifact carries.

CORPUS (5,735 patterns; machines per pattern vary), patterns with a head, base vs set:

| machine | machines | patterns with a head (base) | (set) | patterns that gain | extra heads (all unbounded self-loops) |
|---|---|---|---|---|---|
| fwd (unanchored forward) | 4,006 | 646 | 696 | 51 | 51 |
| rev (reverse) | 4,006 | 943 | 1,139 | 199 | 199 |
| anchored match-here | 2,664 | 465 | 497 | 32 | 32 |
| notempty (iterator retry) | 517 | 178 | 200 | 22 | 22 |
| x-fwd (`$`-lowered forward) | 66 | 11 | 34 | 23 | 38 |
| x-rev (`$`-lowered reverse) | 66 | 2 | 32 | 30 | 60 |
| x-anch | 44 | 1 | 10 | 9 | 9 |

By pattern: 269 of 5,735 patterns (4.7%) gain an edge on some machine; 234 on fwd or rev; 140 of those 234 had NO edge on fwd or
rev before (their first edge). Of the 66 patterns that build x-machines, 32 gain one (the trimreg family).
BENCH (351 patterns): 11 patterns gain (fwd 8, rev 3, anch 3, x 1 machine); 7 of them start with no edge. In bench/capability (70): 8
gain, 5 of them external: wild-codegrammar-json-number-extended, wild-logparse-base10num-grok (and its noatomic twin),
wild-logparse-winpath-grok, wild-secrets-username-password-pair; plus authored tail-space-eol, tail-ext-lower-txt, tail-dotstar-txt;
and syntax cls-s-uc, cls-range, asr-k-uc.
No BOUNDED chain gains anywhere under the real preconditions (every extra head is an unbounded `*`/`+` self-loop; the state-count
column is 0). A model that counts states instead of heads (my first probe) over-reports bounded chains; the real pass's
conditions (accept constancy, view invariance, landing-state, indegree) remove them. HYPOTHESIS: counted-chain gains need those
conditions relaxed separately.

Why the run was split into several classes (per gaining pattern; hand-read from the probe's class sets and from the machines):
- the run's byte set contains a byte the pattern treats specially elsewhere, and the byte classes are global to the machine:
  `\S+@\S+` (`@` is inside `\S`; S = {`@`, rest}), `0x[0-9a-fA-F]+` (the literal `0` of `0x` splits digit `0`: S = {`0`, `1-9A-Fa-f`}),
  json-number `0|[1-9]\d*` then `\d*` (S = {`0`, `1-9`}), `(?>[A-Za-z]+:|\\)(?:\\[^\\?*]*)+` (`:` and `[A-Za-z]` split `[^\\?*]`),
  `[a-z]+\.txt$` reverse (`t`, `x`, `.` split `a-z`), `.*\.txt$` reverse, `.*x`, `[^\n]*=`, `[ab]*\K[bc]+` (`b` is in `[bc]` and `a` is not),
  username-password (keyword letters `u s e r p a w o d` split `[a-zA-Z0-9.@_\-+]`); two causes dominate the 590 gain states the probe
  sampled (up to 4 per machine): 256 are told apart by a transition elsewhere (this case), 258 by a view or accept only (next items);
- the `$` lowering (D164 B3): in the x-machines `\n` gets its own class because the end mark's `\n` tail is read at the seed, so a `\s` run
  loops on class `{space,tab,VT,FF,CR}` and class `\n` going to the same successor: `\s+$`, `\s*$` (the 6.1x trimreg regression; 75 sampled
  states, all tagged machines); the set rule restores 2 unbounded edges on x-fwd, 2 on x-rev, 1 on x-anch for `\s+$`;
- multiline `$`/`\b` newline or word atoms: `(?m)[^c]+$` (258 sampled states differ only in a view/accept, the `(?m)$` newline atom), 1
  state a context-atom difference (`(?<![a-])(?<!\W)...`);
- `\K` marks (`(?:a\K|b)+c`).
The rewrite link: for `\s+$` the ABSORB-EOL rewrite (`\s+\z`) removes the `$` lowering, the set rule keeps the lowering and fixes the
scan; they are independent routes to the same 11.7 us (trimreg_report.md section 5).

## Q5 Anchor rewrites

Forms and how the tree spells them today (probe, after altcls): `^a` `<CTX1C0 a>` (SUBJECT_START pin); `\Aa` same; `a$` and `a\Z` BOTH
`<a $>` (one `A_EOL`); `a\z` `<a CTX124>` (SUBJECT_END pin); `(?m)^a` `<CTX1D8 a>`, `(?m)a$` `<a CTX1B6>`; `\Ga` `<\G a>` (`A_GSTART`);
`\b`, `\B`, `(?<=x)`, `(?<![a-z])`, `(?=b)` all `A_CTX` rows of src/core/ctxfn.def (`0AA`, `155`, `038`, `1C7`, `092`); `^$` `<CTX1C0 $>`.
Newline conventions: pcrec is LF only. CRLF / ANY / ANYCRLF / `PCRE2_DOLLAR_ENDONLY` are DD-11 ("not-started",
docs/pcre2_options.md rows) and `DEF_NEWLINE_CONV` has no producer (internal.h). So no convention-dependent rewrite exists to survey;
a table written today would carry the LF row only, and the CRLF/ANY/ANYCRLF cases are "newline inside X needs the whole sequence
covered" (the plan row's own words), unmeasurable here.

Already handled (by node choice or fact, not by a tree rewrite): option dependence is resolved at parse into the choice of node (D62
add., D168 add. 1); `\A`/`\z`/`(?m)^` and single-char lookarounds are one `A_CTX` kind with one 9-cell table, with a derived CLASS
(`CTX_PIN_START`/`CTX_PIN_END`/`CTX_CONTEXT`) every analysis switches on (D168 add. 3); `\b` before an offset enters the span facts
through the context producer (D168); the derive hook kills `\G`/non-multiline `^` `\A` under split Q; the DFA carries context atoms
(`catom`, `clsctx`) so `\b` costs no states. D168 says outright the producer READS `A_CTX` and does not rewrite the tree.

Remaining, i.e. neighbour rewrites that nothing performs (counts from the probe):
1. B: run then `$` (47 corpus patterns at stage 1, 28 distinct texts; `\s+$` -> `\s+\z` for greedy/possessive, lazy excluded).
2. D context assertion decided by the maximal run (greedy/possessive; lazy needs the assertion): `\w+\b` and `(?>\w+)\b` -> `\w++` without
   `\b` (X = C), `\d+(?!\d)`, `(?m)^[^\n]+$` (the multiline `$` after a run of `[^\n]`), `-+(?<!a)\w` (previous byte decided by the run). Corpus 27 distinct texts
   true (21 `\b`: 15 greedy, 3 possessive, 3 lazy; 5 `(?!C)`; 1 `(?<!C)`) and 13 texts where the assertion is FALSE at the maximal end (`\w+\B`,
   `\w+(?<=\W)`, `a+(?=A)`: the first attempt always fails, so the run must back off; not a drop, an observation), bench 1 (`\b(\w+)\b`). `a+\b` and `\d+(?![\d.])` are NOT implied (the probe checks X against C,
   the same-class test a first draft of mine got wrong).
3. Dead branches: `\z` then a consumer, a consumer then `\A` (`\zx`, `x\Ay`, `ab\A`: 15 distinct corpus patterns) and identical adjacent
   zero-width (`\b\b`, `(?!a)(?!b)...`, 8). The facts pass reports nothing for `\zx` and `x\Ay` under `--emit-facts` (no start/end lines).
4. Anchor next to run under CRLF/ANY: not representable until DD-11.
`(?m)^`/`(?m)$` retiring into `A_CTX` (the D168 add. 1 question) is done: they ARE `A_CTX` rows now (MLINE_BOL, MLINE_EOL). Only `A_EOL`
(`$`, `\Z`) keeps its own kind, and it is the one member of item 1.

## Q6 Placement of ONE declared rewrite table

Constraints read from the code (not tested): (i) altcls first after parse and the order is asserted by
`tests/codegen/run_cpset_structure.sh` (src/opt/CLAUDE.md); a new step between existing ones re-pins that assertion;
(ii) the call graph must run after every pass that REBUILDS nodes (altcls allocates `A_CAP`, the discharge splices); a rewrite that
rebuilds belongs above step 5, one that splices in place (like `lower_enc`) may sit below; (iii) the E1 seal (step 6) stores the kind mask
and nullability and the E2 seal (step 10) refuses the compile if the lowered tree moved either: a rewrite that deletes a node KIND
(dropping the last `\b` changes the mask bit; dropping an `A_ATOMIC` changes `has_atomic`) must run BEFORE step 6 or teach the seals;
(iv) possessify reads follow sets and only runs on the VM engine, after selection; (v) captures must not move (`capgap`: 5 of 6 A
patterns); (vi) a rewrite output of `X++` is spelled `A_ATOMIC(A_REP)` by the parser, which the discharge then cleans.

Candidate placements:
- P1, once, between altcls (3) and atomic discharge (4): sees altcls output (the class-merge shapes of Q2a/b, the empty-branch alternations)
  and everything the composer/derive produced; before the call graph and the E1 seal, so no seal moves; its `X++` outputs go through the
  discharge. Does NOT see what the discharge or possessify leaves. Costs a new row in the pass-order assertion.
- P2, once, after atomic discharge (4) and before the call graph (5): P1 plus the discharge output (a deleted `A_ATOMIC` exposes the run
  to its neighbour: a detector has to peel `A_ATOMIC` anyway at P1); the last point before the graph where rebuilding is free. The best single
  position by this evidence (HYPOTHESIS).
- P3, after possessify/revdet (end of 7): the only point that sees possessify's `(>{a+ possessive})` duplicates (57 corpus); engine already
  chosen and E1 sealed, so only fact-preserving actions are admissible there (the redundant-cut removal changes neither mask nor language,
  except it may change `has_atomic`; HYPOTHESIS, check against E2).
- P4, after lower_enc (9): byte-level, sees `A_WCLASS` (must see through it), must splice in place; adds nothing the earlier points lack.
- At the NFA (11): only place that sees splice and counted-repeat expansion; an NFA rewrite is a different mechanism (graph, not tree).
Iteration: A and B chain on altcls output (`\s+(?:\n|\r)?$`: altcls, A, then B), so a table at P2 wants to iterate to its own fixpoint with a
bound (the select_engine `SELECT_MAX_ROUNDS` shape), not to be one pass; altcls itself is not re-run after the table (a rewrite that
creates a class-mergeable alternation is not among the measured members). Several placements (P2 plus P3) are only needed if the possessify
duplicate is a member.

## Candidate members for [REWRITE-ADJ]

| member | what | evidence (source) | population |
|---|---|---|---|
| ABSORB-OPTIONAL (known) | `X+Y?`/`X+Y*`, Y subset of X, no capture between | 6 corpus, constructed witness via altcls (`\s+(?:\n\|\r)?`); external CRS 942360 `[^A-Z_a-z]+[\s\x0b]*?` | probe, stage 1/3 |
| ABSORB-EOL (known) | `X+$` -> `X+\z`, newline inside X, greedy/poss | 28 corpus texts, bench tail-space-eol/winpath-near-miss (authored), witness via altcls (`(?:\s\|\n)+$`); trimreg 6.1x | probe |
| CTX-IMPLIED-AFTER-RUN (new) | `X+A` with A true at the maximal end -> `X++`, A dropped (`\w+\b`, `\d+(?!\d)`, `(?m)^[^\n]+$`); needs the 9-cell table (ctxfn.def) and X/C set tests | 29 corpus, bench doubled-word; `\b\w+\b` is a common idiom | probe, generic detector |
| ALT-EMPTY normal form (new) | `(\|X)` -> `X??`, `(X\|)` -> `X?` after prefix factoring | altcls creates it in 107 corpus + 10 bench patterns, 3 external bench patterns | probe, stage 3 |
| MERGE-RUN (new) | `X X*`, `X+ X`, `X X?` equal class -> one counted repeat | 41 corpus; external OWASP ipv4 (`[0-9][0-9]?`) | probe |
| REP-OF-REP (new) | `(?:X+)?` -> `X*`, `(?:X{a}){b}` -> `X{ab}`, `(?:a+)*` -> `a*` | 178 corpus; external CRS 942500 | probe |
| TRIVIAL-REP (new) | `X{1}` -> `X`; `X{0}` outside a DEFINE -> empty | 10 corpus; external datefinder (rebar), syslogbase (grok) | probe |
| DUP-ZERO-WIDTH / DEAD-PIN (new) | `\b\b`, `(?!a)(?!b)` -> one `A_CTX`; `\zx`, `x\Ay` -> never | 8 / 15 distinct corpus | probe |
| REDUNDANT-CUT (new, possessify output) | `A_ATOMIC(A_REP possessive)` -> one of the two | 57 corpus, 2 bench | probe, stage 5 |
| possessify itself | disjoint-follower case, panel-repaired; leave until the table proves itself (existing note) | n/a | n/a |
Outside the tree table: the NFA builder's `X{m,n}` collapse (nfa.c:810) is a rewrite spelled inside a builder; the SCANEDGE-SET set rule (Q4).
`C-EMPTY-CAT` is not a member (the stray `A_EMPTY` comes from the anchor wrapper and the derive kill; option runs and `(?:)` are dropped by parse).

## Bench-only questions

- Does the bench hold (or can it cheaply fetch) the FULL upstream lists whose excerpts bench/capability adopted (CRS 942 rule set, grok-patterns,
  noseyparker, OWASP validation)? The 29 external patterns are too few to rate B/D/MERGE shapes in real-world text.
- bench/litrun's 2 external members are copies of capability's; bench/sentinel re-uses capability members, so the bench's distinct
  external count is 29, not 31 + 15.

## STATE AT HANDOFF

Complete: Q1-Q6 answered, probe committed under `studies/rwsurvey/`, dumps in `build/probe/` (gitignored, regenerate with
`studies/rwsurvey/{mkprobe.sh,run_survey.py,analyze.py}`; the Q4 runs took about 5 minutes of one core under `scripts/boxlock run`, labels
`rwsurvey-*`, no queue job). Not done: no NFA-level dump (the splice/unroll adjacency in Q2 is read from the AST and the builder source, not
observed); the placement claims in Q6 are read from code and comments, none tested; the set-rule counts are machines BUILT (base probe agrees
with the artifact stamp on 5,590 of 5,712 corpus and 341 of 343 bench compiles). Open for the manager: `studies/CLAUDE.md` has no line for `studies/rwsurvey/`
and the lane-report history index has no entry (both owed at merge; the brief limited me to the report and the probe directory).
Rulings file `docs/dev/lanes/rwsurvey_rulings.md`: last read at the report commit, no entries applied ("(none yet)").

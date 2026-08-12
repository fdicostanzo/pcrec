# tests/probes — design-measurement probe sources

Measurement programs against libpcre2 (through `../fuzz/pcre2_abi.h`), NOT
part of `make test`. These are the probes behind the extension design's
Part II / R14 / §18 measurements, committed so that the numbers quoted in
`docs/extension_design.md` and `docs/reviews/2026-08-11-r14-part2.md` are
reproducible, and so that **the SPEC-MOD0 author (a D27 writer denied the
design document) can be handed working probe code instead of prose** —
that hand-off is the reason this directory exists (plan step SPEC-MOD0).

Build any of them:

    TMPDIR=/var/tmp gcc -I tests/fuzz -o /var/tmp/probe tests/probes/<file> -ldl

(`TMPDIR` matters on the project box — /tmp is a quota'd tmpfs. libpcre2 is
runtime-only here: no header, no -dev link, hence the dlopen shim.)

Since D35 (2026-08-12) a probe's full OUTPUT is archived as a diffable,
source-stamped report via `scripts/measure.sh <probe>` →
`docs/measurements/<probe>.txt` — regenerated deliberately (probe edit,
oracle version bump, review needing evidence), never read by any check.

## Files

- `probe_qe.c` — the §13 lexical-mode evidence (`\Q\E` quantifier binding,
  class behaviour, `(?i)`/`(?x)` interactions, `(?#)` transparency), the
  62-escape class-position sweep behind §14.3's partition, and §16.1's
  endpoint doorway×side table.
- `probe_atom.c` — atom-position facts: the literal-fallback four at atom
  position, backref-vs-octal cells, the C2/F3 forward-reference
  re-verification, `\0`-never-backreferences.
- `probe_verify.c` — the author's 29-cell re-verification of the R14 panel's
  load-bearing measurements before they were applied (digit runs starting
  8/9, quantifiability, `(?#` in class, capture forms, conditional bodies,
  endpoint edges, the `(?x)`-comment count cell).
- `probe_defer.c` — the §18.1 deferred-resolution cells: `\12`'s
  octal-vs-backref decided by the RUNNING count; error precedence (every
  structural error beats err 115); conditional forward references.
- `probe_digit_sweep.c` — the generated 2,931-probe digit-model sweep
  (predictor stated in the header BEFORE the run; backref-ness read via
  `PCRE2_INFO_BACKREFMAX`, sanity-checked; zero disagreements at close).
- `probe_quant.c` — the §18.3 quantifiability determinism probes: the
  option-run form split (`a(?i)*` 109 vs `a(?i:b)*` compiles) and the
  per-VerbName split (`a(*FAIL)*` 109 vs `a(*pla:b)*` compiles).
- `probe_cls_bits.c` — MOD-0.3c: GENERATES src/parse/cls_bits.inc (--emit)
  from libpcre2 one-byte censuses — 20 positive tables (5 char-type sets +
  newline + 14 posix names), predictor stated in the header before the
  first run and confirmed exactly (10/6/63/3/5; 62/52/128/2/33/10/94/26/
  95/32/6/26/63/22; 1). Asserts the COMPLEMENT LAW (negation = exact
  256-bit complement) for every pair before emitting, which is why only
  positive tables exist to drift. Since the R16 follow-up it ALSO emits
  pcrec_cls_posix_map — the name->bits PAIRING as part of the same
  measured artifact, so the R16 lower/upper swap is no longer writable as
  a plausible source line (mod_classes.c walks the generated map; a
  registry_check tie holds the map's name set equal to posix_names[]'s
  producible names, both directions, sabotage-validated). registry_check
  ties each bare-escape SET port's census to the class_expect column;
  PC-4 re-measures live.
- `probe_ci_posix.c` — MOD-0.3c: the caseless×posix cells behind
  tests/classes/classes.rxt's `flags i` posix blocks — /[[:lower:]]/i
  matches 'A', /[[:^lower:]]/i matches neither case but matches '0',
  [^[:lower:]]/i likewise: fold-BEFORE-negate confirmed on all 8 cells
  (OS-1/D23's order rule, measured rather than reasoned at the moment a
  producer first composed -i with a posix set).
- `probe_nbrace.c` — MOD-0.3f/R16 (2026-08-12): the `\N{...}` vs
  quantifier-fallback boundary, 22 cells — PCRE2 tries the brace as a
  quantifier FIRST (`\N{2,3}`, `\N{,3}`, `\N{2, 3}` all compile as
  quantified bare `\N`; err 104/105 bodies prove the quantifier parser
  claimed the brace; `{}`, `{,}`, `{2,3,4}`, `{2x}`, unterminated stay the
  err-137 name construct). The oracle behind pcrec_brace_quant_shape (one
  scan, two load-bearing callers) and the R16 reject/corpus pins. Also
  corrected one cell in the R16 engine critic's own report ({,3} compiles)
  and exposed fuzz.py's stale a{,3} exclusion note.
- `probe_mod05.c` — MOD-0.5a scope probes (2026-08-12): the x-vs-xx class
  boundary ((?x) never touches class interiors, xx deletes exactly {09,20};
  the D30 §7 `(?xx)[a- ]` hazard cells with match spans); spaced brace
  quantifiers COMPILE as quantifiers at options=0 (10.43+ rule,
  pcrec_brace_quant_shape already agrees — verified both sides, no
  divergence); (?s)/(?U)/(?m)/(?n)/(?J) semantics cells; (?ri) and all four
  a-sub pairs census-identical at options=0 (MEASURED no-ops, real again
  under UTF/UCP). Its naive x-skip census has a recorded template flaw —
  see the MEASURED block in its header and probe_mod05b.c.
- `probe_mod05b.c` — MOD-0.5a follow-ups (2026-08-12): spaced-brace match
  cells; the (?^) reset scope PER LETTER (unsets i,m,n,s,x,xx; U and J
  SURVIVE — "unset imnsx" is the measured rule); the CONTROLLED x-skip
  census (a no-x control column removes the quantifier false positives):
  {09,0A,0B,0C,0D,20,85} — 0x85 NEL is skipped, so x-mode's skip set is
  NOT \s's set (census 6).
- `probe_mod05c.c` — MOD-0.5c port-implementation corners (2026-08-12):
  set/unset masks collect over the whole run and UNSET WINS regardless of
  order ((?i-i)/(?-ii) both case-sensitive); doubled-x is
  ADJACENCY-sensitive ((?xsx) and (?xaDx) are level 1); `-x` clears BOTH
  levels; `^` then adjacent xx is level 2; and the landing-round cells: a
  later bare (?x) DOWNGRADES an earlier xx with the (?xx)(?s) control
  keeping it — the per-char level-assignment rule in pcrec_modport_optrun.
- `probe_mod05d.c` — MOD-0.5d lexer-boundary cells (2026-08-12):
  quantifiers and lazy markers bind ACROSS skips ((?x)a + and (?x)a + ?);
  `#`-comments end at 0x0A ONLY (0x0D and the skipped 0x85 do NOT — the
  NEWLINE convention, not the skip set); the `(?` run is lexically tight
  (( ?i) is the 109 shape); newline-in-brace defeats quantifier-hood under
  x; xx deletion precedes the negation check ([ ^a] negates), range
  parsing ([a\t-\tz] ranges), and the dash-vs-literal lookahead; POSIX
  bracket names read raw; the \t ESCAPE survives deletion (the corpus
  transcription defect's oracle). The evidence behind parse.c's
  xskip/cls_skip/cls_peek_past_dash.
  REAL with census identical to `[^[:alpha:]]` (204 members, 0/256 diff);
  `[[:^foo:]]`/`[[:^<:]]` err 130; `[[:<:]]`/`[[:>:]]` compile as zero-width
  word-boundary assertions (match spans recorded); `(?[[a]])` COMPILES under
  10.46 while `(?[a])` is its own err 216. The evidence behind the MOD-0.3a
  attribution rulings (per-name `assertions` for `<`/`>`, the new
  `extended-classes` module) and the negated-name scope of the classes
  producer.
- `probe_fix3.c` — FIX-3 (K13): the twelve escape rows' class-position
  semantics, 41 cells with the member SET verified byte-exact (all 256
  single-byte subjects per compiling cell) — octal runs, the literal-fallback
  four, tails, range endpoints, and the error-151/108 cells with their
  offsets recorded. The oracle behind
  tests/base/class_escape_fallbacks.rxt's `# pcre2-only` blocks (U7).
- `probe_class_expect.c` — MOD-0.1 slice 3: the `class_expect` column's 44
  values, measured from libpcre2 (census of `^[S]$` over all 256 bytes; takes
  a `--list-syntax` dump path and probes every esc/class-bracket row). The
  independent cross-check of tests/spec_mod0/class_expectations.inc — the two
  implementations agreed 44/44 before the column was transcribed into
  registry.c.
- `probe_endpoint_k12.c` — MOD-0.1 endpoint-rule slice (K12): the 42 cells
  the §16 five-step rule changes or deliberately leaves — char-type escapes
  both sides, both-construct pairs, the step-3-beats-step-4 cells, the
  non-certified `\p` boundary, the bracket doorway's low side, non-range
  dashes and truncations. The oracle behind the K12 pins in tests/reject/.
- `probe_uprops.c` — MOD-0.6 phase-1 design probes (2026-08-12, module
  `unicode-props`): the three-answers inventory for `\p{Foo}` (options=0
  vs `PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL`, its bit established
  BEHAVIOURALLY — no `pcre2.h` on this box); a full 256-byte sweep of the
  byte after `\p`/`\P` showing there is NO decline-shaped tail (every byte
  lands on {COMPILES, ERR 146 malformed, ERR 147 unknown property}); the
  single-letter short-name census (case-insensitive, only C L M N P S Z);
  the insignificant-byte census (space/hyphen/underscore/tab/case, all
  insignificant, verified semantically); the streaming proof (a
  1-significant-char body padded past 100,000 insignificant bytes still
  compiles) and the exact 48/49 significant-character boundary, located
  both in a bare run and in a padded one to show the blame offset tracks
  significant-character count, not total body length; the in-class and
  endpoint-shape cells including the K10 oracle (`[\N{U+41}]` is ERR 193
  in every class position). The evidence behind
  docs/design_notes_mod06.md.

## The method these encode (R14's closing lesson)

State the predictor BEFORE running; generate probe sets from the claim's
FAILURE DIRECTIONS, not from the examples that produced the claim; and feed
the predictor from the oracle (libpcre2's own verdicts/introspection), never
from the row data under test. `probe_digit_sweep.c` is the template.

Maintenance: add a file per measurement campaign; keep each header's
predictor/purpose comment current; update this file when files are
added/removed.

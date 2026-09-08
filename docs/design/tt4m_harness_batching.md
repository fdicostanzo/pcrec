# [TT-4M] STEP 2 (2b) — harness adoption design: batched compilation in `tests/harness/run.sh`

Lane tt4m2 (sonnet), 2026-09-08. Written so an implementation lane (STEP
2c) can build from it without re-deciding anything this note already
rules on. Cites STEP 1's validation (`docs/dev/tt4m_darwin_validation.md`)
and STEP 2's own N x P sizing measurement (`docs/dev/
tt4m_step2a_parallel_sizing.md`) throughout; read both before this note if
their numbers are in question. `tests/harness/run.sh` and `tests/harness/
driver.c` are read-only inputs to this design (I read both closely enough
to be right about the current arm chain, the `PROCS>1` fan-out, the D45
budget wiring, and the RXTDUMP/SIZELOG hooks — see the citations below);
nothing under `tests/harness/`, `src/`, or `docs/spec/` is touched by this
lane. A light D6 panel on this note is the plan row's own next step, not
this lane's.

## What stays UNCHANGED (stated once, up front)

The `.rxt` driver protocol (`docs/spec/rxt_format.md`), every case
expectation kind (`m`/`n`/`ms`/`ns`/`g`/`gp`/`gu`/`perr`), the oracle tiers
(python `re` base, PCRE2 differential per-module), and the known-fail
ratchet are **entirely untouched by this design**. Batching is a change to
HOW `flush_block`'s compile step turns a parsed block into a runnable
binary, never to what a `.rxt` file means or what counts as a pass. Every
existing `.rxt` file's expectations read identically before and after
adoption — the acceptance bar (2d) is exactly "prove that."

## 1. Batching unit

**Fixed-N chunks of consecutive `pattern` blocks within ONE FILE's own
parse, N = the harness's chosen constant (STEP 2a: 64), the file's own
trailing remainder forming a smaller final chunk.** Not per-`.rxt`-file
(one batch = one file, whatever its size) and not per-worker (a batch
spanning multiple files).

**Why not per-file.** `run.sh`'s own corpus is wildly uneven — a census
over the 207 non-`known_fail` `.rxt` files (R55-4: RUN for real and
archived, not merely cited — `docs/dev/tt4m_step2a_parallel_sizing.md`'s
"Appendix: per-file block-count census" has the reproducible command and
the raw numbers) found block counts from 1 to 357 per file, mean 18.7,
median 12. A "one batch per file" policy would make almost every batch
far SMALLER than N=64 (mean 18.7 blocks) while three files
(`tests/lookaround/d27/matrix.rxt` at 357, `tests/utf8/
axis04_p_categories.rxt` at 136, `tests/assertions/multiline.rxt` at 89)
would form one oversized batch each — the file with 357 blocks would pay
STEP 2a's own measured degradation cost at N approaching 128 territory
(≈29s recovery, `docs/dev/tt4m_step2a_parallel_sizing.md` §4) for its
WHOLE file on a single bad pattern, which is a worse blast radius than
this note's own recommended N buys anywhere else in the corpus. Fixed-N
chunking avoids this by construction: it is ONE mechanism (no per-file
size branch, per the project's standing "general mechanisms, not special
cases" rule — `docs/dev/CLAUDE.md`'s situation-index row on that convention)
that DEGENERATES CORRECTLY at both ends — a file with fewer than N blocks
produces exactly one undersized batch (STEP 1 already measured that
batching wins even at N=4, so an undersized batch is still a clean win,
never a wasted mechanism), and a file with many multiples of N produces
several full-sized batches, none of them larger than the chosen N no
matter how large the file is.

**Why not cross-file.** `run.sh`'s `PROCS>1` fan-out (run.sh:266-390) is
ALREADY a per-FILE worker model: each worker is a full re-invocation of
this same script, `PROCS=1`, one file, its own temp dir, output replayed
in `files[]` order at the end. Grouping batches across files would mean
restructuring that dispatch model (accumulating blocks from multiple
files before the first flush) for no measured benefit — 2a's own P sweep
is precisely a model of "how many of these per-file batch pipelines run
at once," which is a direct stand-in for `PROCS` at the file level (see
"mapping (N,P) onto PROCS" below). Keeping batching INSIDE one file's own
block loop is the minimal change that reuses `PROCS`'s existing
concurrency rather than inventing a second one.

**Mapping the (N, P) recommendation onto the harness's existing PROCS
dispatch.** STEP 2a's own prototype pool is a flat cross-corpus pool, not
partitioned by file — its P models "P independent batch-compile-then-run
pipelines sharing this box's cores," which is EXACTLY what `PROCS`
FILE-workers already are once each worker internally batches its own
blocks. So: **N=64 is a literal constant** (a new env var, see item 8);
**P is NOT a new knob — it is `run.sh`'s existing `PROCS`**, and 2a's
finding ("P=8 is the knee on this box, P=12 buys nothing and can starve
workers or inflate CPU") is a finding about `PROCS` itself on THIS box,
not a separate parameter batching introduces. This is a real, if modest,
correction to today's blanket `PROCS=nproc` default recipes
(`test-corpus:`, `test-axes:`, `mech:` — Makefile:260/1349/1366): on
darwin, `nproc` is 10 but the measured knee is 8 (the performance-core
count, `hw.perflevel0.logicalcpu`), and 2a measured P=nproc(=10, untested
directly, but between the measured P=8 and P=12 cells) giving no more than
a few percent over P=8 while costing more CPU to contention. **This note
does NOT recommend changing the `PROCS=nproc` default** — that is a
box-topology-dependent tuning question distinct from whether batching
itself should land, and the Linux reference box's own `nproc`=12 might
sit closer to or further from its OWN core-topology knee than darwin's
does (unmeasured; see item 7). It is named here so an implementation
lane does not read 2a's P=8 finding as "hardcode PROCS default to 8."

**H11 targets (head-bearing files) and `perr` blocks stay OUT of the
batching unit entirely, unchanged from today.** A `perr` block never
reaches `gcc` at all (pcrec's own refusal, checked by exit code, is the
whole check) — it contributes nothing to a batch's pending list, same as
today's per-pattern path contributes nothing to `gcc` for it. H11's
per-target builds (`pcrec --source --target`, run.sh:812-865) are
`--source`-derived SEPARATE artifacts from a different pcrec invocation
than the one that would join a batch; **MEASURED FREE for the corpus**
(0 of 189 files are head-bearing, `tests/harness/CLAUDE.md`'s own
run.sh entry) — this is a zero-population edge case today, so leaving it
unbatched costs literally nothing and is the D77-correct move (revisit
if H11 populations ever grow beyond zero, with the measurement that
would trigger it, rather than build for it now).

**A THIRD exclusion, added by revision (R55-1, `docs/dev/reviews/
2026-09-08-r55-tt4m-batching.md`): a block carrying ANY routed cell stays
OUT of the batching unit too, exactly as `perr`/H11 do, detected PER-BLOCK
at parse.** Item 1's first draft named only `perr` and H11; nothing kept a
`frames-buffer=` block out of a batch, and this dispatch protocol's own
scope (item 2, below) only reproduces the DEFAULT route — a batch member
whose cases run through `<prefix>_search_in`/`<prefix>_match_in`/
`<prefix>_match_caps_in` cannot be served by `dispatch.c` as designed at
all. Live population today: `tests/recursion/framebuffer.rxt`'s
`^(a(?1)?b)$ / engine vm` block (9 directives). **"Routed" is read off
the route GRAMMAR, not off one spelling of one directive** — `tests/
harness/driver.c`'s `parse_route` (driver.c:231-261) and `run.sh`'s own
`valid_route` (run.sh:429-444, the ONE definition of the grammar the two
share so they cannot drift) recognize exactly FOUR shapes: `default`
(or the empty string), `null`, `<n>` (a single positive integer — frame
capacity, trail capacity implied equal), and `<frames>,<trail>` (two
positive integers, one comma). A block's cases run a non-default route
two ways, not one: an explicit `frames-buffer=<spec>` directive inside
the block naming any of the last three shapes (`run.sh`:1331-1355,
`cur_route` set per-case from the position of that line downward), OR —
the one a text-grep for the directive's own spelling would miss — the
run-wide `RXTROUTE` env var, which is each block's `cur_route` FLOOR
before any in-block directive is seen (`run.sh`:1106/1266-1269, reset to
`$RXTROUTE` at every file and block boundary, never to the literal string
`"default"`) — so a corpus-wide `RXTROUTE=null` sweep (the NULL-equivalence
control `tests/harness/CLAUDE.md`'s run.sh entry names) makes EVERY block
in that run carry a routed cell, `frames-buffer=` line or not. The
implementation lane's exclusion predicate is therefore: a block is
batching-ineligible if its resolved `cur_route` for ANY of its cases is
not `default`/empty — computed exactly where `run.sh` already computes
`cur_route` per case today, before this design's own compile-time
decision (batch vs. standalone) is made. The fuller dispatch driver that
COULD serve a routed block (modeling `_search_in`/`_match_in`/
`_match_caps_in` and the buffer-descriptor protocol, `driver.c`:281-380+)
is a later increment, not built here.

## 2. Dispatch protocol

**A harness-local generated file, `dispatch.c`, one per batch, following
STEP 2a's `dispatch_gen.py` shape exactly** (that file's own header
already states the [V-E] relationship — see below): `#include` each
batch member's own `PREFIX.h`, one `int main(int argc, char **argv)` that
reads an integer SELECTOR from `argv[1]` and dispatches to that member's
own `rx_search`/entry surface, argv/exit-code protocol otherwise
IDENTICAL to today's `driver.c` (decode() byte-for-byte, match/nomatch/
give-up printing byte-for-byte, including the four give-up words and the
`"internal"` fifth outcome — `tests/harness/CLAUDE.md`'s `driver.c`
entry has the full protocol this must reproduce). **Scope limit carried
forward from STEP 1/2a, NOW EXPLICITLY ENFORCED rather than merely
unexercised (R55-1)**: default route only (bare `<prefix>_search`, no
third `route` argument) for the FIRST landing — `_search_in`/`_match_in`'s
cross-check and `frames-buffer=`/`RXTROUTE` routed cases are not
"unmodeled and hoped never to arrive," they are item 1's own THIRD
exclusion, checked per block before that block is ever offered to a
batch, exactly as `perr`/H11 already are. A fuller dispatch driver
(modeling every route the grammar admits) is the later increment that
lets a routed block join a batch at all; until it lands, a routed block
always runs the STANDALONE per-pattern path, same as today.

**[V-E] replaces this file when that row opens (implement-then-replace,
D75's own worked example is the precedent this rule cites) — the selector
surface is kept COMPATIBLE with a by-name lookup so the swap is
mechanical.** Concretely: `dispatch.c`'s selector is an integer index into
the batch's member list IN THE ORDER THEY WERE COMPILED (the same order
`dispatch_gen.py` already emits them, argv order); [V-E]'s own design
(`docs/dev/plan.md` row `[V-E]`, ADDENDUM 2026-09-08) already names this
exact row as its SECOND candidate consumer and specifies its own emitted
unit array is either name-sorted (binary search) or linker-section
self-registered — either shape can be looked up by an integer position OR
by name without changing what `dispatch.c`'s CALLER (this design's own
compile-then-run loop) has to know: it always calls "the Nth member of
this batch," and whether "Nth member" resolves through a hand-rolled
`switch` (this note, today) or `[V-E]`'s own generated array indexing
(later) is invisible to the run.sh call site. No work is done here to
anticipate `[V-E]`'s landing beyond keeping this compatibility property
true; `dispatch_gen.py` is deliberately NOT designed to be a preview of
`[V-E]`'s own emitted format (that would be building ahead of a measured
need, D77).

## 3. SIZELOG's per-pattern gcc CPU/wall column

**Recommendation: option (a) — split each batch member into its own `-c`
compile (still ONE gcc PROCESS, still ONE final link) rather than (b) an
amortized column or (c) leaving SIZELOG runs unbatched.**

**Why (c) is not actually available, not merely undesirable.** SIZELOG
is not an opt-in axis a caller occasionally sets — `test-corpus:`'s own
Makefile recipe (Makefile:258-262) calls `tests/size/run_size_log.sh`
UNCONDITIONALLY on every `test-corpus` invocation, which THREADS
`SIZELOG` through `run.sh`'s existing compile pass on every single
`make test`/`make test-corpus` run there is (`tests/size/run_size_log.sh`'s
own header: "no second gcc invocation anywhere — the whole point of
riding the existing corpus"). **If SIZELOG runs stayed unbatched, `make
test-corpus` — the exact target STEP 2 exists to speed up — would NEVER
see batching's benefit at all**, because SIZELOG is set on literally every
full-corpus run, not a separate instrumented mode someone opts into
occasionally (unlike `LINTGEN`/`CLANGGEN`/the sanitizer axes, all
genuinely optional). Option (c) as stated in the plan row would silently
defeat the entire adoption. This is stated as a FINDING of this design
pass, not a neutral option among three — the plan row asked for all
three to be weighed, and weighing (c) is what surfaces why it fails.

**Why (a) over (b).** Option (b) (log the batch's shared total on every
member's row, tagged with a batch id) preserves the full compile-count
win but breaks per-pattern attribution in a way that has a REAL cost:
`tests/size/check_size_tripwire.sh` pins a max gcc-CPU-time ceiling
(`docs/dev/artifact_size_census.md`'s own numbers) meant to catch ONE
pathological pattern's compile-time regression. Averaging N members'
cost onto one shared number can DILUTE a genuinely slow new pattern below
the ceiling (false negative — exactly the corpus's own
`tests/base/k18_cost_gates.rxt` witness class D45's header worries about,
now hidden behind N-1 innocent neighbors) or falsely indict N-1 fast
patterns sharing a batch with one legitimately slow one (false positive,
extra investigation cost). A batch-id column lets a human NARROW a
regression to "one of these N" and re-run that one batch at N=1 to
disambiguate, but that is real added friction on the exact check this
row's own `[ART-SIZE.1b]` charter calls "the artifact-size log ...
per-pattern movement is a `git diff` a reviewer reads" — a reviewer
reading a `git diff` wants the number to mean what it says, not a hint to
go re-run something. Option (a) keeps every row's CPU/wall number an
EXACT per-pattern reading (same `bash time` wrapper trick `run.sh` already
uses, just around each `-c` sub-compile instead of around the whole
`gen_cc` call) at the cost of giving up the LARGER of STEP 1's two
measured levers only during SIZELOG-instrumented runs specifically: the
`.c`-per-TU `-c` compiles still spawn N times (no compile-invocation-count
win under SIZELOG), but the FINAL LINK still happens once, so the SECOND,
BIGGER lever STEP 1 found — collapsing the number of DISTINCT
EXECUTABLES launched at case-run time (11.79x on its own, bigger than the
2.65x compile-invocation lever — `docs/dev/tt4m_darwin_validation.md`,
"An unplanned second finding") — is UNAFFECTED, since that lever comes
entirely from the link step producing one binary per batch, not from how
the compiles leading up to it were sequenced. **So (a) is a real, if
partial, trade: SIZELOG-instrumented runs (which, per the finding above,
is EVERY full-corpus run) keep exact per-pattern attribution and still
get the bigger of the two measured wins, giving up only the smaller one.**

**The tripwire and the log header's row-count self-check need NO change
under (a).** Row count, column count, and the tripwire's ceiling check
are all defined per PATTERN already (`tests/size/CLAUDE.md`'s row format);
(a) produces exactly one row per pattern, with an exact (not amortized)
gcc CPU/wall reading, identical in shape to today's row. The only
implementation-lane change is inside `flush_block`'s batched branch: loop
the existing `gen_cc`-style timed compile once per member (as a `-c`
compile against the batch's shared output directory) instead of once for
the whole file, then one untimed (or separately, batch-level-timed) link
call at the end. `run_size_log.sh`'s own assembly step and
`check_size_tripwire.sh` read the assembled TSV exactly as they do today
and need not know batching exists at all.

## 4. Axis compatibility (GENCFLAGS/LINTGEN/CLANGGEN, the deny/force axes)

**All four survive batching unmodified — confirmed by reading how each
one actually reaches `run.sh`'s compile line, not assumed.**

- **GENCFLAGS (san axes, `LINTGEN=1`, `CLANGGEN=1`).** `run.sh`'s own
  header already documents these as flags on the SAME `GENCFLAGS`
  variable threaded to one `gen_cc` call site (run.sh:37-53). Batching
  changes WHAT is named on that one gcc command line (N+1 `.c` sources
  instead of 2) but not which flags are on it — every flag in
  `$GENCFLAGS $RXTFLAGS` still applies to the ENTIRE compile-and-link
  invocation, batched or not, because gcc applies its own flags to every
  named translation unit AND the link step of a single invocation
  uniformly. No batching-specific change needed.
- **The san axes' runtime libraries and `-fsanitize=` link flags MUST be
  on the LINK — this holds automatically under shape L and is worth
  saying explicitly because it is the one place batching's "one gcc
  invocation" property could have been a hazard.** `ubsan`/`asan`/`san`'s
  own `*_ENV` blocks (Makefile:1178-1300) pass `-fsanitize=...` through
  `GENCFLAGS`, and gcc's ONE-SHOT compile-and-link mode (no `-c`) applies
  every flag to BOTH the per-TU compile AND the final link automatically
  — this is already true of today's unbatched `gen_cc "$cur_pattern" "$CC"
  $GENCFLAGS ... driver.c gen.c` call (compile-and-link in one gcc
  invocation) and remains true when `gen.c` becomes N `.c` files plus
  `dispatch.c` named on the same line: gcc still compiles+links in one
  process, so the sanitizer runtime gets linked in exactly once, into the
  one batch executable, exactly as it is linked into today's one
  per-pattern executable. **The design owns saying this explicitly
  because option (a) above (SIZELOG's `-c`-per-TU split) reintroduces a
  SEPARATE link step** — that split-then-link shape must keep
  `-fsanitize=...` on BOTH the `-c` compiles (for instrumentation) AND the
  final link call (for the runtime library), which `_gen_cc_run`'s own
  `[TT-3]` ccache-shape precedent (`tests/lib/gen_timeout.sh:294-360`)
  already gets right for the identical reason and is the pattern to copy,
  not reinvent.
- **The deny/force axis flags (`run_axes.sh`, `make test-axes`).**
  `tests/axes/run_axes.sh` runs the WHOLE corpus through `run.sh` once per
  axis via `RXTFLAGS="<the axis's -fno-.../-f... spelling>"` plus
  `RXTDUMP` for the per-case comparison (`tests/axes/run_axes.sh:428-499`,
  confirmed by reading the actual env-var threading). `RXTFLAGS` is
  appended LAST to `pflags` in `flush_block`, so it reaches PCREC's own
  invocation (deciding what the artifact IS), not gcc's — batching a
  block's COMPILE never touches this: every batch member still gets its
  own `pcrec ... $RXTFLAGS ...` call exactly as today, before the batch's
  shared gcc/link step. The axis question is answered before batching's
  own mechanism (gcc invocation count) ever enters the picture.
  `RXTDUMP`'s own rows are written from the per-CASE loop in
  `flush_block` (run.sh:927-936), keyed on parse/case data that exists
  regardless of how the compile happened — unaffected by batching for the
  same reason item 5's mech rows are (see below).

## 5. Mech (sabotage rows anchored on the harness)

**Grepped `tests/mech/sabotages/*.sh` for every row whose OWN
`SAB_FILE=` NAMES `tests/harness/run.sh` or `tests/harness/driver.c`
(R55-7: `SAB_FILE=`-anchored, not a raw text-grep for the two paths —
a plain name-grep over every sabotage file's PROSE returns 13 hits, not
eight, since six of them (S108, S157, S159, S173, S213, S214) merely
MENTION `run.sh` in a comment while anchoring on a `src/` file; the false
recount is exactly the trap this note's own first draft walked into and
back out of): eight rows (S11, S194, S196, S198, S199, S203, S205 —
`SAB_FILE="tests/harness/run.sh"` — plus S43 — `SAB_FILE="tests/lib/
gen_timeout.sh"`). None of them anchor on
the COMPILE/LINK invocation line (`gen_cc "$cur_pattern" "$CC" ...
driver.c gen.c`) — every one anchors inside the `.rxt`-PARSING arm chain
(`flush_block`'s directive handling: `g`/`gp` line drop, `flags`
reset-at-block-boundary, `frames-buffer=` scoping, an invalid `features`
list, the head-detector boundary, the `rxt_escape` control-byte fallback)
or, for S43, inside `tests/lib/gen_timeout.sh`'s D45 budget wrapper
itself, not `run.sh`'s call site.**

This is the load-bearing fact for this item: **parsing happens upstream
of and independent from compiling.** `flush_block` finishes deciding a
block's `pflags`, `cur_route`, `case_gspec[]`, etc. entirely from the
`.rxt` text before it ever calls `pcrec` or `gcc` — batching changes only
what happens AFTER that point (whether this block's compile is issued
alone or bundled with N-1 neighbors into one gcc call). None of the eight
rows' detectors — the `rxtsource` parse differential (legs A/B/C), the
`harness` per-case count/answer check, or D45's budget fire-control — read
anything about compile GRANULARITY. **Per row**: S11/S194/S196/S198/S199/
S203/S205 are UNMOVED (their anchors sit in code paths batching never
touches). **S43 needs one stated adjustment, not a re-derivation**: its
detector (`run_gen_timeout_tests.sh`'s CPU fire control) proves the D45
wrapper still FIRES on an over-budget compile; item 6 below (REVISED per
R55-2) keeps every `gen_cc` call's budget UNSCALED at the per-member `-c`
sub-compile and at the link, with the N-scaled number surviving only as
an outer wall backstop — S43's own sabotage (removing BOTH clocks from
`gen_cc`) still removes them from whichever `gen_cc` invocation it
targets, unscaled per-member call or scaled outer backstop alike, so the
row's anchor and mechanism are unchanged either way.

No new mech row is needed for batching's OWN correctness — that is what
2a's own zero-mismatch answer-identity sweep (9 cells, 7,706 distinct
cases, `docs/dev/tt4m_step2a_parallel_sizing.md` §3) already establishes
at the mechanism level, and STEP 2c's own implementation should add
exactly ONE new row (a planted "batch link never falls back to
per-pattern recovery" sabotage, since that IS a new code path this
adoption introduces and none of the eight existing rows could detect its
removal) — named here as owed to 2c, not built by this design pass.

## 6. Degradation, attribution, and the timeout story

**Compile failure, per member, BEFORE the batch's shared gcc call: cheap,
already the general case, no fallback needed.** Today's `pcrec_err`/
`pcrec_rc` check (run.sh:640-698) already runs per-block; under batching
it runs per-MEMBER, before any batch is assembled — a member whose pcrec
compile fails simply never joins the batch's `member_srcs` list (STEP
2a's own `cmd_batched` implements exactly this: `pcrec_ok`/`prefixes`
skip a failed member and the batch proceeds with the rest,
`studies/tt4m_batchrun/batchrun.py:190-201`). This path needs no recovery
mechanism at all — the harness already reports this exactly as it does
today (per-pattern `record_fail` naming the pcrec diagnostic), it simply
never reaches gcc, batched or not.

**GCC/link failure, the real new case: TWO-TIER attribution, not the
"always fall back to N individual recompiles" shape 2a's own prototype
measures as its worst case.**

1. **Fast path (the common case): parse gcc's own stderr for the failing
   filename(s).** `[DD88]`'s one-artifact-per-TU discipline is why this is
   possible for free — the plan row's own D77 design input for `[V-E]`
   already names it: "D88's one-artifact-per-TU already makes GCC-side
   attribution free (the diagnostic names the file = the pattern)."
   `gcc`'s own diagnostics for an ordinary syntax/semantic error in one
   TU are prefixed with that TU's filename (`rx0007.c:42: error: ...`);
   grepping the batch's captured stderr for `^<prefix>\.c:` lines that
   match a KNOWN member's own generated filename identifies the
   failing member(s) directly. When this succeeds (one or a few named
   files), the harness: (a) `record_fail`s exactly those members' cases
   with the SAME message shape as today ("pattern '...' failed to
   compile: <the gcc diagnostic lines naming that file>"), (b) RELINKS
   the batch WITHOUT the failing member(s) — one more gcc invocation,
   but naming N-1 (or fewer) sources, not a fallback to N separate
   invocations — and (c) runs every surviving member's cases normally
   against the relinked binary.
2. **Slow fallback (the rare case): a link-time-only failure gcc cannot
   attribute to one file** (a cross-TU symbol collision, a `dispatch.c`
   bug, a linker-stage-only diagnostic with no per-file prefix). Falls
   back to STEP 2a's own measured shape exactly: recompile every member
   INDIVIDUALLY (the per-pattern baseline shape), attribute each member's
   own compile result to itself. **This is the shape 2a's degradation
   numbers measure, and they should be read as this path's WORST CASE,
   not the typical cost**: 3.61s/14.72s/29.22s wall at N=16/64/128
   (`docs/dev/tt4m_step2a_parallel_sizing.md` §4) is what a batch pays
   ONLY when the fast path cannot attribute the failure — sizing a batch
   choice against this worst case (as item 1's own N recommendation
   already does) is the conservative, correct thing to do, while the fast
   path means most real compile failures (an ordinary syntax error in one
   pattern's emitted C, the overwhelmingly common shape a corpus
   regression takes) pay close to nothing extra: one relink, not N
   recompiles.

**Reporting contract**: whichever path fires, every case belonging to a
member that ultimately succeeds must produce an ORDINARY pass/fail result
indistinguishable from an unbatched run of that same pattern — no case
belonging to an innocent batch neighbor may read as failed, delayed, or
differently-attributed because it happened to share a batch with a bad
pattern. This is the same "no vacuous pass, no spurious fail" bar every
other check in this tree holds itself to (K35's general-fix precedent);
it is the acceptance criterion 2d's answer-identity gate directly tests.

**Timeout story — REWRITTEN (R55-2, `docs/dev/reviews/
2026-09-08-r55-tt4m-batching.md`, num-F2/num-F3): the N-scaled number is
no longer the PRIMARY guard, because scaling the wrapper's own budget by N
dilutes the exact guard D45 exists to be — a single pathological compile
(D45's own motivating incident) would run for up to N times its own
budget before the ceiling fired, inside a batch built specifically to
group N-1 INNOCENT members around it.**

Per-case matcher-run timeout wrapping (`"$TIMEOUT_BIN" "$RUN_SECS"
"$bdir/t" ...`, run.sh:889) is **completely unchanged**, as before — it
wraps the same per-case spawn shape regardless of whether the executable
behind `$bdir/t` came from a batch or not (STEP 2a's own scope decision,
inherited from STEP 1, holds this shape identical on purpose).

**The batch COMPILE's guard is built on item 3's own split-then-link
STRUCTURE (option (a): N `-c` sub-compiles, then one link), not on a
single wrapped invocation of the whole sequence** — resolving the
contradiction the first draft left open between this section's
one-wrapped-call framing and item 3's N-`-c`-plus-link shape. Concretely:

1. **Each member's own `-c` sub-compile runs under `gen_cc` at the
   UNSCALED per-pattern budget** (`gen_cpu_secs()`/`gen_timeout_secs()`,
   `tests/lib/gen_timeout.sh:96-111`, unchanged from every other compile
   site in the tree) — no plumbing invention needed, because this is
   `_gen_cc_run`'s own already-shipped split-then-link precedent
   (`tests/lib/gen_timeout.sh:294-360`, gated on `CCACHE=1` today; item 3
   generalizes the SAME split to every batch, always) generalized from 2
   sources (driver.c, gen.c) to N. RLIMIT_CPU is a per-PROCESS limit set
   once on the wrapping `bash -c` subshell and inherited unscaled by
   every forked child (`gen_cc`'s own `ulimit -S -t "$cpu"` comment
   already states this is per-process, not cumulative) — so each of the
   N `-c` sub-compiles gets the FULL, ordinary per-pattern CPU ceiling on
   its own, catching a pathological single member within roughly ITS OWN
   budget rather than diluted N-fold. This is **strictly better than
   today's per-pattern shape, not merely equivalent to it**: same guard,
   fewer processes (N members share one link and one outer wrapper
   instead of each paying its own).
2. **The link step gets ONE additional unscaled budget** (its own
   ordinary `gen_cc` call at `gen_cpu_secs()`/`gen_timeout_secs()`, not
   N times either number) — linking N objects is not expected to cost
   anywhere near N compiles' worth of budget, so scaling it by N would
   only re-open the same dilution this rewrite exists to close, on the
   one step where a genuine link-level hang (a `dispatch.c` bug, a
   pathological symbol table) is exactly the kind of "stuck, not
   working" case D45's wall backstop is for.
3. **The batch-level N-scaled number SURVIVES, but only as an OUTER
   BACKSTOP around the whole per-batch sequence** (all N sub-compiles
   plus the link), stated as such rather than as the primary guard:
   `batch_gen_timeout_secs = N * gen_timeout_secs()` (wall only — the
   per-member/per-link CPU ceilings above are what does the real
   catching work) bounds the case where every INDIVIDUAL step stays
   under its own budget yet the AGGREGATE still runs unacceptably long
   (contention inflating every step by a little, rather than one step
   pathologically). This is a strict backstop, expected to fire rarely
   if ever, not the number that catches D45's own motivating incident —
   that job now belongs entirely to step 1 above's per-member budget.

`gen_cc`'s own diagnostic text (`D45 CPU BUDGET: compiling generated C
for [$what] exceeded ...`) names the FAILING MEMBER exactly as it does
for an unbatched pattern today when a per-member `-c` sub-compile breaches
its own budget (step 1 above) — a batch-level diagnostic naming
`batch <file>:<first-line>-<last-line>, N=64` is needed only for the link
step (step 2) or the outer backstop (step 3), where no single member's
name is the failure's own.

## 7. Linux parity

**Shape L is plain, portable gcc — naming N `.c` files plus `dispatch.c`
as separate arguments on one command line has no darwin-isms anywhere in
it.** The one darwin-specific lever this design's own STEP 1 evidence
found — the ~11.79x per-binary Mach-O first-launch cost collapse — is a
PLATFORM PROPERTY of what batching produces (fewer distinct executables),
not something the generated `dispatch.c` or the harness's own driver
shell code does differently per platform; `tests/lib/cc_resolve.sh`'s
Apple-clang-workaround is UNRELATED to batching (it already resolves a
real gcc regardless of batch size, and is a no-op on Linux by its own
header).

**Prediction, stated as a prediction to be checked, not assumed
transferable** (matching this project's own "measured not assumed"
standard, exactly the discipline STEP 1's memo already applied to its
own two levers): Linux's win from adopting this design is expected to be
DOMINATED by the smaller of STEP 1's two levers — the
gcc-invocation-count reduction alone (STEP 1's darwin number: 2.65x on
its own component; [TT-4.1]'s OWN Linux gcc-batching number, measured
independently on that box back at [TT-4]'s close, was 3.66x at N=16) —
because Linux's own per-process exec/launch cost is known from this
project's other cross-platform measurements ([XARCH] STEP 0,
`docs/dev/xarch_step0.md`) to not carry anything resembling macOS's
Mach-O first-touch tax. **The bigger lever (11.79x on darwin) may simply
not exist on Linux at all** — this is a real, open, and stated
uncertainty this design does not resolve, and the executor arm's job at
implementation time is exactly to check it, not to assume STEP 1's
combined 4.28x darwin multiple transfers.

**Validation plan**: at the STEP 2c/2d implementation's merge point, run
this same `studies/tt4m_batchrun/` tooling (already portable Python +
gcc, no darwin-only dependency) via the travel-topology executor channel
(`pcrecdev2`, per the standing `[travel-month-topology]` rule — never a
direct ssh heavy run) against the SAME chosen (N, P) this note
recommends, on the SAME cross-corpus pool shape 2a used, checking: (a) is
there a net win at all on Linux, sized against [TT-4.1]'s own historic
Linux gcc-batching number as a sanity floor; (b) does Linux reproduce
[TT-4.1]'s OWN non-monotonic parallel-dispatch finding (too-large N
regressing under real `PROCS`-width dispatch) at the SAME N this note
recommends, or does the Linux box's different `nproc` (12, vs darwin's
10) shift the knee; (c) answer-identity, the same zero-mismatch bar 2a
already cleared on darwin.

## 8. Rollout

**Opt-in first (`HARNESS_BATCH=N`, unset/0 = today's per-pattern shape,
byte-for-byte unchanged), converging to default-on once the acceptance
gate passes — not opt-in forever.**

**Why opt-in first matches house style.** Every other axis this file's
own header documents (`RXTFLAGS`, `RXTROUTE`, `LINTGEN`, `CLANGGEN`,
`SIZELOG`, `RXTDUMP`, and `[TT-3]`'s `CCACHE=1`) starts unset-means-
unchanged, and `run.sh`'s own header states the reason plainly for each:
"a plain run is byte-for-byte unchanged." A brand-new default compile
SHAPE for the whole corpus is a bigger behavioral change than any of
those (it touches every single `.rxt` file's compile path, not one
optional instrumentation pass), so it earns at least the same caution
`-Werror`'s own non-default ruling did (R5-Q1: "a stranger's `make` must
not fail on a newer gcc's new opinion") — a stranger's first `make test`
should not silently change shape underneath them before this design's own
numbers are confirmed on their box.

**Why NOT opt-in forever.** Unlike `CCACHE=1` (measured a clear NO for
`make test`'s own workload and staying opt-in permanently for that
reason, `docs/testing.md` "Compile caching") or `LINTGEN`/`CLANGGEN`
(deliberately permanent axis surveys, never meant to be the default
path), batching's entire justification IS `make test-corpus`'s everyday
cost — [TT-14]/[XARCH]'s spawn-tax framing is about the box everyone
develops on every day, not an occasional instrumented survey. An
opt-in-forever flag nobody remembers to set defeats the point of doing
this work at all.

**The flip condition (opt-in -> default-on), stated as the brief asks**:
a FULL `make test` run under `HARNESS_BATCH=<the chosen N>` produces
IDENTICAL pass/fail/pattern-compile-failure/size-log-row counts to a
plain `make test` — on BOTH darwin (this box) AND the Linux executor arm
(item 7) — with `make mech`'s sabotage matrix clean (the eight existing
harness-anchored rows unmoved per item 5, plus the one new batch-fallback
row item 6 owes) and `check_size_tripwire.sh` clean under item 3's design.
Only once ALL of those hold does `HARNESS_BATCH` default to the chosen N,
keeping the escape hatch (`HARNESS_BATCH=0` or `=1`) permanently
available — for a stranger's box that hits something this design did not
anticipate, and for a developer manually isolating one batch's own
failure by re-running it unbatched (item 6's slow-fallback path already
does this internally; the escape hatch is the same tool available by
hand).

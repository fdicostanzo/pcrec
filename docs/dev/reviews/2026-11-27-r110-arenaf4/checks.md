# CRITIC checks: arenaf4 (r110)

## Findings

### CHECK-1 (SUSPECTED, design/maintenance, small effort, blast: the K163 class net) The lent row proves nothing about `pcrec_ctx_lend` being CALLED
The net is only "a nonzero lent count refuses". Nothing requires walk_part to lend. The scanner's `readers` rule forbids
callers OUTSIDE walk_part but not the ABSENCE of the call (fixture list has MUST_PASS for a walk_part that lends, no
MUST_FAIL for one that does not). Plant that every named net misses (describe for the coordinator to build): in
compound.c walk_part delete the two lines `pcrec_ctx_lend(w->cx);` and `unsigned uses = pcrec_ctx_unlend(w->cx);`
(+ the `if (uses)` refusal, or `uses = 0`), AND apply S3653's two edits (outer-arena copy). Expected on that tree: no count,
compile succeeds, W7/W6 lent row prints INFO ("0 trial points ... not a gate") with rc 0, W1-W6 inject malloc only (the
outer-arena copy takes no malloc when it fits its block), compound tests see byte-identical output. I.e. the K163
regression class returns undetected: the INFO line is indistinguishable between "lent window empty because fixed" and
"empty because nobody lends". Confirming would need that plant; I did not run it. Suggested fix shape: a floor on the
lend count over the corpus is impossible by design (0 after fix), so the net must be structural: a scanner row that
requires walk_part to contain both lend and unlend (reached-or-stale, like the ALLOW rows), or a W7 row whose witness
PLANTS a lent use and must read it (a control that can fail, as the W7 hand-kept control does).

### CHECK-2 (CONFIRMED, doc/design, trivial) The lent row's "pre-fix control" claim is not reproducible: it can only FAIL by a compile refusal, never by sweeping
Facts: (1) plant:S3653 `kit/run.sh plant:S3653 -p rx --pattern '^abc|x+$'` -> rc=1, "internal error: a part compile used
the enclosing compile's error channel 1 time(s) [K163]"; subject same pattern rc=0 (RX_COMPOUND "split" present).
(2) `kit/alloc.sh plant:S3653 --w7-only` -> `FAIL: W7/W6 lent window (compound split): profiling pass did not succeed
cleanly (K=-1 ...)` and `alloc rc=1`; subject `--w7-only`: INFO line, `alloc rc=0`. So the row CAN fail, but only through
the profiling compile refusing (the same refusal test-compound already sees: 105 patterns, every compound one). It never
sweeps a lent trial point on any tree available: the BASE/pre-F4 tree has no `pcrec_ctx_lent_p`, so the row cannot run
there (BASE's driver "has no lent row" per COMMON); the comment's "On the pre-F4 tree (C0(d), lane arenabuild) its points
were the part's forms copy ... failing each stranded" is a historical claim with no tree/artifact a reader can rerun. The
row is therefore a second reader of the same refusal, not an independent control; sabotage (9)'s "floor" wording (alloc
sees what compound sees) is true but adds no new detection. Judged? The design table calls it a pre-fix control (K35);
the wording "can fail" is true only for a refusal. Severity doc; fix: say so in the row comment, or make the control real
(CHECK-1 planted-use witness).

### CHECK-3 (CONFIRMED-NO-DEFECT note, tooling) split_compare reports DIFFER for two-sided refusals
`kit/split_compare.sh base subject` over tests/compound/split.rxt: 105 patterns, 102 same, 3 "DIFFER" (#38 `^[\s\x{200c}]+|...`,
#78 `(?(?=^)a|ab)c`, #92 `^a(*COMMIT)b|c`). All three are rc=1 on BOTH trees with identical diagnostics (re-run by hand with
kit/run.sh: byte-mode \x{200c} too large; conditionals unimplemented; (*COMMIT) out of scope), no output file, so `cmp -s`
of two missing files reads DIFFER. Emitted C is byte-identical BASE vs SUBJECT for all 102 compiling patterns (the F4
"no abi bump" claim holds on this corpus). Note for the corpus: the 3 refusing rows mean split.rxt witnesses 102, not 105.

### CHECK-4 (SUSPECTED, maintenance, trivial) ALLOW row keys on (file, function) so it hides any other heap shape in `part_forms_copy`
`("src/core/compile.c","part_forms_copy","heap",...)` admits every malloc/strdup/realloc in that function. Shape it would
hide: a second heap call before the store (e.g. `char *q = strdup(s); char *p = malloc(n); if (!p) pcrec_ctx_nomem(cx);`)
-- `q` strands on the nomem longjmp and the scanner stays green (22 allowlisted sites, "0 heap builders"). Same as every
other ALLOW row's granularity (e.g. compile_driver "the Job itself"), so house-consistent; low value. The scanner on
plant:S3653 also PASSES (rc=0, 92 files, 22 allowlisted, 8 scope sites): the plant is not in its class, as designed.
Also: `part_forms_copy` assigns `*hold = p` unguarded; if the facts block ran twice for one part (a FIT_FORCE_NEXT
`goto facts_force` re-entry after the store; I did not find a non-nomem refusal after the store that selects that rung) the
first copy would be overwritten and leak. Confirming would need a failing force arrival after the pf store.

### CHECK-5 (CONFIRMED consistent) W6 re-pin 1014/1057 -> 1016/1061 re-derives
Per part: pcrec_arena_hold now taken twice (forms + text) in walk_part: +1 rec_take calloc (outer point -> refusal diagnosed,
not absorbed), and part_forms_copy's malloc replaces an arena-block copy (no malloc before): +1 heap call inside the part
(refuses the part, absorbed by the fallback). Two parts in `^abc|x+$` -> +4 trials, +2 absorptions = 1061, 1016. Direction
matches the comment/design. Confirmed by kit/alloc.sh --sites: BASE W6 = 1057 forced failures (PASS), SUBJECT W6 = 1061 (PASS, exact pin 1016 holds; 1016 `code=2` SITE lines), W7 rows rc=0 on both; subject `alloc rc=0`. Moved pin gave up nothing measurable: the +2 absorbed sites are the part's own heap copy (before: an arena copy with no malloc).

## PROBED-AND-HELD


- W6 re-pin (b): +4 trials/+2 absorptions re-derived and confirmed by `--sites` on both trees (1057 base, 1061 subject; 8 witnesses PASS).
- Emitted C byte-identity: split_compare base vs subject, 102/102 compiling split.rxt patterns same (3 refusals both trees, CHECK-3).
- plant:S3653 through every named net: run.sh rc=1 (K163 message), alloc --w7-only rc=1 (lent row FAIL via profiling refusal), scanner PASS (not its class; expected). Not run: test-compound/mech (forbidden); S3653's SAB_REACH (grep RX_COMPOUND "split" on the subject-shaped compile) verified true on subject (compound split emitted).
- Scanner on subject and plant: PASS 92 files, 22 allowlisted, 8 scope sites; new readers fixtures present (3 MUST_FAIL, 1 MUST_PASS); lent window row INFO-only on subject (0 points), so its pass is by emptiness (documented INFO, not PASS: K35 held for the reporting).
- Largest witness reached: W6 `^abc|x+$` (2 parts), 1061 forced failures; one nesting level (part inside the compound walk).

CRITIC COMPLETE

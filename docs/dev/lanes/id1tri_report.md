# id1tri report: the RED identity gate id1 (job 200-vlbbuild-id1)

Premise test: judge output VERDICT RED. (B) and (A) differing=0 on all 4 axes (default 4145, vm 4146, noprefilter 4145,
nocaptures 4145); linkage/elision PASS. mismatches=48, manifest=27, in-both=22, manifest-not-mismatched=5,
mismatched-not-in-manifest=26. The script's 4 FAILs are the 4 axes' refusal-mismatch FAIL (the red-by-construction one).

## Verdict: NO class (iii). The red is the JUDGE's, not a byte move.
Every mover is (i) or a manifest/judge gap; differing=0 everywhere.

### Mismatch set (48) = 22 + 24 + 2
- 22 = population.tsv call-free manifest rows, all compiled-vs-refused: class (i), expected (the freeze figure).
- 24 = compiled-vs-refused patterns NOT in population.tsv: class (i). Every one is a block of
  tests/lookaround/lookbehind_variable_witness.rxt (added by vlbbuild's U8 after the manifest froze; absent from the pin's
  tests; the briefing's prediction said "manifest + this lane's witness patterns"; the judge only knew the manifest).
  Examples: `(?<!ab?)x`, `(?<=(a|aa))c`, `(?<=a{1,2})b`, `(?<=a{1,9})x`, `(?<*(a{1,3}))c\1`, `é(?<=(a?))`, `(?<=(a|ab)(b|))x`.
  (The backref in `(?<*(a{1,3}))c\1` is OUTSIDE the lookbehind; F1 does not touch it.) The judge's own oracle test
  (libpcre2 accepts at max_varlookbehind 255, refuses at 0) passed for all 24.
- 2 = `(?<=a{65535}b)x`, `(?<=(?:a{1000}){66})x`, subject=REFUSED reference=COMPILED: the judge printed UNEXPECTED, but
  this is the 65535 ceiling, a DESIGNED mover in the other direction (vlookbehind.md §0 G1/§5.2 "pcrec compiles these
  today, which libpcre2 refuses (err 187)"; §13 Q2 "refuses two patterns pcrec compiles today"; sabotage S1969/W9b).
  Verified by running: the f5de088bf pin compiler emits both; the subject says "at most 65535 characters (this one has
  65536 / 66000)". The judge only allowed compiled-vs-refused, so these were mis-flagged. Class (i), ceiling flavour.

### manifest-not-mismatched (5), all (ii)/not-in-corpus, none a mover
- `(a)(?<=\1)x`, `(a|bc)(?<=\1)x`, `(?<=${v})x`: refused on BOTH sides. Pin: "variable-length lookbehind is not
  implemented ... fixed length"; HEAD (after F1 5bdc95759/937bed801): "a lookbehind containing a backreference, a
  variable or a consuming callout is not implemented". Different text, same accept/refuse, so no mismatch. (ii).
- `^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$`, `^(?:(?<g>a|ab)){0}ab(?<=(?&g))$`: call-bearing; the pin refuses, 3b9754edf
  and HEAD both compile them (checked). They are not in any .rxt (only .py/mech/findings files), so the identity
  corpus never holds them; the call-FREE refusal-mismatch check would not list them in any case. Not a mover for this
  instrument; they belong to the call-bearing arm (population absent), covered by the lookbehind call sweep.

## The correct id1 run
Two facts decide it.
1. **HEAD cannot be the subject as-is.** 482f15d87 stamps abi 96 (786312130, K137; `PCREC_ARTIFACT_ABI` in
   src/gen/emit_dfa.c is the ONLY src/gen/emit_dfa.c difference from 3b9754edf). run_recursion_identity.sh hard-fails
   at lines ~1380 when the subject and FILEPIN abi differ (f5de088bf = 95). That is why vlbbuild used 3b9754edf.
2. **3b9754edf as subject is still sound.** src diff 3b9754edf..HEAD is F1 (5bdc95759, 937bed801, refusal text/route for
   backref/var/callout inside a lookbehind, refused both sides), F15 (481b0d73b, a lookbehind sub-block guard), the K137
   abi bump (786312130) and WIP U6. Jobs 211/221 abisweep (3b9754edf abi 95 vs HEAD, 5048 patterns) found only utf8
   `-fno-comments` movers (K137), unexpected=0. The gate is byte-only with comments, so byte identity of HEAD vs the pins
   follows by composition with id1's (B)/(A) differing=0.

Therefore NO new box job is required for the identity facts: **re-judge the existing artifacts** (id1.log and
id1tmp/tmp.ao53pUw8UX/diff.* were kept by KEEP=1). I did exactly that with a corrected judge:
`$PCREC_TMPDIR/scratch/id1tri/id1_judge_v2.py` on `/var/tmp/pcrec-pcrec/scratch/vlbbuild/id1.log` + `id1tmp` with the
tree exported at 482f15d87 ($PCREC_TMPDIR/scratch/id1tri/head as ROOT): **id1: VERDICT GREEN**
(22 manifest + 24 witness-file stage-1 movers + 2 ceiling movers).

Judge v2 changes vs jobs/id1_judge.py (diff = ~12 lines):
- allowed mover set = population.tsv patterns UNION patterns that are a `pattern <p>` line of
  tests/lookaround/lookbehind_variable_witness.rxt (read from ROOT, the subject tree); any mismatch outside it is
  UNEXPECTED. (The witness file is the source of the extra patterns; if you want the K35 control independent of that
  source, add a count floor: expect 22 + 24 + 2 = 48 exactly, which both runs and the identity script's
  `refusal-mismatch=48` already agree on.)
- a `(refused, compiled)` mismatch is allowed iff libpcre2 refuses it even at max_varlookbehind 65535 (the ceiling).
- the other direction keeps the 255-accepts / 0-refuses oracle test.
- the 5 manifest-not-mismatched are printed as informational, not red.

## If you want a HEAD-subject run anyway (optional, not needed)
Same job as vlbbuild's jobs/id1.sh with: OLD=$S/old482 (a fresh path), `git archive 482f15d87 | tar -x -C $OLD`, then in
the SCRATCH copy only `sed -i 's/#define PCREC_ARTIFACT_ABI 96/#define PCREC_ARTIFACT_ABI 95/' $OLD/src/gen/emit_dfa.c`
(the stamp is the lone difference; byte-gate, comments on), make -j4, same KEEP=1 invocation with
RECURSION_IDENTITY_FILEPIN=f5de088bf RECURSION_IDENTITY_ABASE=4bd002e20, same pins, judged by id1_judge_v2.py
(install it as jobs/id1_judge.py in vlbbuild's scratch jobs dir, or point the job at the id1tri copy). Expected:
differing=0 on the 4 axes, mismatches=48 (the F1/F15 delta moves no corpus pattern), GREEN. Boxqueue lines as job 200:
cap 10800, patience none, expect verdict=1 lines=^id1: VERDICT GREEN. Queue after 220-228 finish; no manifest
regeneration script exists (population.tsv is vlbinv's hand-counted evidence, K35); none is needed with judge v2.

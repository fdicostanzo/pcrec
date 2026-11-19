# docs/dev/lanes/preddoc1_evidence/ — the predicate-document pilot's runs

Lane preddoc1 (2026-11-19), DESIGN EVIDENCE for the pilot of the reorganized predicate documents
(`docs/design/predicates*.md`): one run example per full `core/holes/*` piece, the manager's readings 1-12, and the
proof that the lint's L4 failures are only the two lint limits the rulings file accepts (R1, R2). Rules nothing.
Historical after merge; never edited after.

## Files

- `preddoc1_model.py` — STANDALONE. PART EX (one example per full holes piece, the three modes on libpcre2, python
  `re` agreeing where it can parse the pattern; each with its RIVAL reading as a plant), PARTS R1-R12 (the
  manager's readings), PART LT (it predicts the lint's L4 failures line by line, runs the lint, and requires the
  two sets to be EQUAL; every cited title, read up to its closing `")`, must be a true record title). A guarded
  runner runs each PART alone: a part that raises is the FAILED check `P<part>`. Header names plants s1-s15 and
  the `xEX-<tag>` rivals. Controls: libpcre2-8 10.46 via `../rxmodel_evidence/pcre2h.py` (run, never read:
  D181), python `re`, and the lint itself (for LT).
- `preddoc1_model.out` — forward run: 36 checks, 0 failed.
- `preddoc1_sabotage.out` — each of 33 plants alone: every one CAUGHT (rc 1, a named failing check).

## Run (one process each; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/preddoc1 && timeout 600 python3 -I -B \
        <worktree>/docs/dev/lanes/preddoc1_evidence/preddoc1_model.py > fwd.out)

Under a second. `PREDDOC1_SABOTAGE=s3` (one plant at a time).

## Limits

- RULE-AS-CODE (`class_hole`, `range_hole`, `count_copies`, `option_hole`, `flags_hole`) lowers a hole the way the
  documents say: an EX check is a consistency check of that lowering against libpcre2's answers, and the rival
  plant shows the example tells the readings apart. It is not an independent control on the rule itself.
- Plants s7 and s13 make PART EX raise, so PART R11 also fails: it uses a name PART EX defines later. Both are
  caught by their own check first.
- Count (d) of the report filters record titles by words; it is a proxy for "concerning holes", and the report
  names its two false positives.

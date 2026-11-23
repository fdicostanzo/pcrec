# tests/lookaround/d27_l1 — span_arms L1's D27 blinded witnesses

Goal-written witnesses for the lookaround L1 feature (`docs/design/span_arms.md` §14.4 L1): "a
positive lookaround's fixed bytes join the required run of its neighbours" (kind A), "a pattern
whose lookaround contradicts its consumed text is listed dead and still answers as PCRE2" (kind B),
and look-alike controls that must not be listed dead (kind C). Written by a D27-blinded author
(lane l1d27, `docs/dev/lanes/l1d27_report.md`); every answer is libpcre2-8 10.46's.

## Files

- `l1d27_witnesses.rxt` — the 88 witnesses' ANSWERS (find-all `m`/`ms`/`ns`/`mc` cells); rides
  `test-corpus` like every `.rxt` under `tests/`. The author's file: do not edit (re-cut from the
  author's generator in scratch if it must change). One build-side edit (lane l1ffix): the author's
  two HEAD lines `description` and `oracle pcre2/10.46` are `#` comments, since both words are still
  guarded by `tests/rxtsource`'s keyword census (a corpus line may not begin with one) and
  verify_rxt.py reads no head; so the file is python3-`re` cross-checked too (C3: 719 PASS, the 56
  `# pcre2-only` cells skipped) beside libpcre2's answers.
- `l1d27_listing.tsv` — the author's record of each witness's LISTING (`req_whole_run` value and
  why) and their PASS/FAIL against the spec. The author's file: do not edit except to re-pin a
  moved listing after re-judging it.
- `l1d27_limits.tsv` — BUILD-side: the declared limit each FAIL row rests on (five keys, each with
  its design sentence in the header). Lane l1ffix.
- `check_listing.py` — `make test-lookaround`'s listing check (also run over `../d27_l3` with a directory argument): pcrec's listing equals the record,
  every FAIL row names a declared limit, no PASS row does, non-empty population.

## Rules

- A later unit that lifts a limit (U-descguard, [REPEAT-RUN] R2, U-exactwidth) turns this check
  red on its rows: re-judge each against its `spec_expectation`, re-pin, drop the limit row.

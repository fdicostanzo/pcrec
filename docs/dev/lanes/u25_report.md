# u25 report — PCRE2 10.46 variable-length lookbehind vs invalid UTF

## STATE AT HANDOFF

Rulings file u25_rulings.md was empty (no entries applied). Premise held (U24 was the last row).

- Landed the reader's note: `docs/dev/pcre2_notes/lookbehind-invalid-utf.md` (checker passed), plus a "Notes index" in that dir's CLAUDE.md.
- Added U25 to `docs/dev/upstream_issues.md` (repro, both answers per build, JIT inferred not run, draft upstream text; nothing filed or sent).
- Exclusion: no U-row mechanism existed in the lookaround differential, so a narrow one was added in `tests/lookaround/vlb_one.sh`: only mode utf8-invalid, pattern `(?<*(.{1,3}))b`, five pinned cells (FF 61 62 at startpos 0,1,2; A9 C3 A9 62 at startpos 1,3) where pcrec's answer equals the pinned one and the oracle differs only by an earlier group-1 start. Verified with a faked oracle: the 5 cells tolerated (count 5), any other difference still FAILs. The `run_lookaround_diff.sh` §5 message cites U25. Corpus truth (pcrec 1..2) unchanged.
- Caveat: only the FF 61 62 vanilla answer (0..2) is observed from CI; the A9 C3 A9 62 cells are tolerated by rule (earlier group-1 start), their vanilla answer is inferred.
- `make test-lookaround` locally green (Ubuntu-patched oracle: 0 tolerated used). Not run against vanilla 10.46 here.
- docs/pcre2_compliance.md lists no lookbehind/invalid-UTF disagreement; skipped.
- Added to lanes history index.

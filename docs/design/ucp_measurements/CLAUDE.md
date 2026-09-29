# docs/design/ucp_measurements/ — the [UCP] design lane's probes

Lane `ucpdes`, 2026-09-28, on `main` at `4bb74bda`. Backs
`docs/design/ucp_design.md`. Never built or run by pcrec's make. Oracle probes
run over ssh stdin and write nothing on the remote box (the
`studies/ucp_study/` and `utf8_measurements/` convention); the 10.46 reference
is `duxevents@100.69.121.107` (tailnet), 10.48 is local Homebrew.

## probes/

- `ucp_sets.py [LIB]` — 57 set relations under UTF|UCP (and a few UTF-only
  controls): each side reduced to its member set over all code points by one
  `pcre2_substitute` (studies/ucp_study/classify_remote.py's method), compared,
  with a stated expectation per row and a count of rows that missed it.
- `ucp_points.py [LIB]` — point cells (caseless × UCP, the byte tier, `(?aW)`
  scoping, MIU mid-character starts) and BOUNDARY STREAMS: `\b`, `\B`,
  `(?<=\w)`, `(?!\w)` at every offset (one ANCHORED match per offset) of 14
  ill-formed subjects, under UTF|MIU and UTF|UCP|MIU. Carries a vacuity guard
  that the `PCRE2_MATCH_INVALID_UTF` bit (0x04000000) is live.
- `bottom_model.py STREAMS [CONTROL]` — the design's ⊥ context model scored
  against the UCP|MIU streams; controls `bottom-is-word` and
  `unrepaired-back-step` must disagree. Exports `dec` (the stage-4 decoder
  rule) for `segment_sym.py` — one decoder, not a copy.
- `segment_sym.py [MAXLEN]` — forward (decode, ⊥ = one byte) vs backward
  (repaired back_step, ⊥ = one byte) segmentation, exhaustive over a 20-byte
  boundary alphabet to MAXLEN; two failing-direction controls.
- `ctx_sets.py SHAPES.tsv` — over `docs/dev/lookaround_census/`'s all-(a)
  patterns: distinct context sets per pattern, and whether each utf8 pattern's
  sets are ASCII-only (all-byte exact) or need the island. Text extraction.

## out/

`ucp_sets_10.4{6,8}.txt`, `ucp_points_10.4{6,8}.txt` (10.46 = 10.48 on every
relation and point; only set sizes differ), `bottom_model_10.46.txt`,
`segment_sym.txt`, `ctx_sets_9399d927.txt`, `illformed_ctx_cells.txt` (a
hand-recorded three-row transcript: pcrec's `--emit-main` answers and a 10.46
UTF|MIU match, with the naive all-byte answer the design's precondition
prevents).

## Instrument defects found by running the probes (recorded, fixed)

1. **The first boundary-stream instrument under-marked.** It ran ONE global
   `pcre2_substitute` replacing every match of the zero-width pattern with `|`.
   Under `MATCH_INVALID_UTF` the global loop's empty-match advance skips
   offsets next to ill-formed bytes, so e.g. `\b` on `é FF a` showed no mark
   between `é` and `FF` — which would have read as "libpcre2 does not treat an
   ill-formed byte as a non-word boundary" and refuted the design's ⊥ rule.
   Replaced by one ANCHORED match per offset, which also exposes libpcre2's
   own MIU re-positioning (a match returned NOT at the offset asked, marked
   `?` and excluded from scoring rather than guessed).
2. **Two expectations in `ucp_sets.py` were guesses, and both were wrong**:
   that `(?aW)(?i)\w` and `(?aP)(?i)[[:lower:]]` fold into U+212A/U+017F.
   Measured: an ASCII-restricted set folds by the ASCII fold. The rows were
   kept, re-stated as DIFF rows against the guessed sets, beside EQ rows for
   the measured ones — so the transcript records the correction.

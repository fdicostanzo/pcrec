# docs/dev/lanes/ucpu2_evidence — [UCP] U2's reproduction pieces

Lane `ucpu2` (docs/dev/lanes/ucpu2_report.md). Scripts ran from the lane's
session scratchpad (`/tmp/ucpu2s/`); paths inside them name it.

- `p2.py` — the local libpcre2 ctypes oracle (10.48, Homebrew) the generators
  read.
- `gen_ctx.py` / `gen_ill.py` — generate `tests/ucp/ctxnode.rxt` and
  `tests/utf8/axis13_ctx_illformed.rxt` from that oracle (the latter under
  UTF|MATCH_INVALID_UTF).
- `cells_from_rxt.py` + `remote_verify_ctx.py` — turn a `.rxt` file into
  oracle cells and re-answer them on the 10.46 reference over one ssh-stdin
  session (writes nothing remote). Transcripts: `verify_ctxnode_10.48.txt`,
  `verify_ctxnode_10.46.txt` (187/0), `verify_axis13_10.46.txt` (32/0, MIU).
- `side_finding_empty_at_0x80_10.46.txt` — a PRE-EXISTING divergence found
  while writing axis13 and NOT U2's: an empty/nullable pattern on the lone
  byte `80` under `-e utf8` is `(0,0)` in pcrec (base binary too) and
  `(1,1)` in libpcre2 MIU (MIU re-positions past the invalid byte).
- `movers.py` + `movers_captures_on.tsv` / `movers_no_captures.tsv` — the
  U2 mover census (ucp_design.md §7 a1) over the lookaround census
  population: RX_ENGINE on the base binary, on U2, and on U2 under
  `-fno-ctx-node`.
- `ident.sh` — the identity sweep (every corpus pattern, both encodings,
  `--features all`, base vs U2, `-o -`).

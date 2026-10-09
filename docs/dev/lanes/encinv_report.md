# encinv: encoding data inventory + layout proposal

Lane `encinv`, 2026-10-09, opus. Branch `lane/encinv` off main `57fe04ef` (abi 71).
INVENTORY + PROPOSAL ONLY. Nothing under `src/`, `cli/`, `lib/`, `tests/`,
`third_party/` or `docs/spec/` moved.

## Deliverables

- `docs/design/encoding_data_layout.md`: the note. It contains the inventory (§1),
  diagnosis (§2), proposal (§3), no-mover migration (§4), the [U8-PICK] placement
  (§5), the standing questions (§6), six questions for Frank (§7) and the D77
  triggers (§8).
- A `docs/design/CLAUDE.md` entry, after `locate_finish.md`.
- This report.

## What was measured in the lane (worktree build only, `build/scratch/`, gitignored)

- `python3 tools/review/include_graph.py --out-backedges` lists two back-edges, and
  one of them is `src/core/findings.c:48 -> src/enc/enc.h`. The findings seam reaches
  up for the encoding name and `pcrec_utf8_encode`.
- A scratch `cpfreq` bundle with `serves byte-rate when byte via encode-utf8` parses,
  and a `-e byte --analysis mis 'xé'` compile stamps
  `RX_FINDINGS "byte-rate=mis:ae2a5428b495114c"`. The `when`/`via` pair is
  unconstrained. That is legitimate (a byte matcher over UTF-8 text), and it means
  the derivation names the subject text's encoder, not the compile encoding's.
- `rxt_find.c:309-317`: the chain terminal `default` is appended as one link and its
  own `include` is never followed. That rules out the "generated sibling bundle"
  route for a generated utf8 prior without a resolution-semantics change.

Everything else is grep and reading on `57fe04ef`, cited file:line in the note.

## Headline findings

1. Most of the "encoding data" is CODE-POINT data. Only bytes are encoding-specific.
   `src/enc/utf8_fold_pairs.inc` is Unicode content under an encoding name.
2. There are two per-encoding registries. `src/opt/lower_enc.c:439-442`'s
   `lower_ops[]` restates `onebyte_max` as `identity_max`. The documented
   third-encoding recipe ("nothing outside `src/enc/` is touched") is false. The
   lowering cannot move into `src/enc/`, because it calls `pcrec_ast_node` from
   `parse`.
3. Capabilities are inferred, not declared:
   - "UCP folds by Latin-1" is asked two ways: `parse.c:637`'s `max_cp <= 0xFF` and
     `enc.c:213`'s table-presence test.
   - "Unicode universe" is `max_cp >= 0x10FFFF`.
   - "Multi-byte" is `endwin.c:175`.
   - Code-point bitmaps are read as byte sets at `ir/dfa.c:174` and
     `enc.c:367-368`. That assumes ASCII-compatibility, which is not declared. A
     codepage encoding would be silently misread at three sites.
4. The two match-time fold tables come from two mechanisms. utf8's is a python-
   generated `.inc` included in its own text. byte's (K94) is generated at emit time
   by the SHARED `enc.c`, behind `if (t->id == PCREC_ENCE_SPAN_CASELESS_UCP)`.
5. There are four encoding vocabularies, and `latin1` means a data description, a
   derivation and a fold.
6. A third encoding touches 15 places today, and 9 of them are avoidable (note §2.7).
7. The byte prior is no longer "keyed by contents". D123-4's `serves when byte` is a
   declared key. Residue: D1 says `encoding ascii` but carries 128 high-byte rows.

## The proposal in one line

Key a data set by the most general axis its content depends on: code points by
source, bytes by encoding, corpus by analysis (encoding as the `serves when` key).
Keep one file per encoding (directories only at the D77 trigger). Make the `PcrecEnc`
row the manifest: add `encode` and `ucp_fold` fields, check ASCII-compatibility, and
key `lower_ops[]` through the row. Add a documentation-tier manifest table in
`src/enc/CLAUDE.md`.

## Migration (note §4)

The proof for every step is `scripts/emit_sweep.py` against a `git archive`
reference, plus `make test-codegen` and the fold-agreement, uprops `--check`,
findings and encseam sections.

- E0: docs-only manifest plus a recipe correction.
- E1: move the encoder into its backend and add `PcrecEnc.encode`.
- E2: replace `identity_max` with `onebyte_max`.
- E3: add `PcrecEnc.ucp_fold` and make the `fold_rows` `latin1` row a `ucp` row.
- E4: move the latin1 fold-table producer into `enc_byte.c` behind an entry data
  hook.
- E5: rename `utf8_fold_pairs.inc` to `ucd_fold_pairs.inc`.
- E6: resolve derivations through the registry's encoder.
- E7: assert ASCII-compatibility.
- E8: rename `DEF_ENCODING_UTF8` to `DEF_ENCODING_UNICODE`. This one is SPEC-MOVING:
  `--list-definitions` output, `docs/spec/registry.md:536` and `cli.md:228`.

No step is an abi event. Each `PcrecEnc`, `LowerOps` or `PcrecEncEntry` field change
is a D58 seam event to record. The abi-moving items stay separate: fold-table
unification (Q3) and the [U8-PICK] prior.

## [U8-PICK] placement

A `cpfreq` block in `src/findings/default.rxt`, `serves byte-rate when utf8 via
encode-utf8`. It is authored or generated depending on Q5. A generated sibling bundle
needs the terminal to follow its `include`, which is a `findings.md` §7 change.

## Questions for Frank (note §7, as discussion)

- Q1: directories per encoding now, or at the trigger. Leaning: at the trigger.
- Q2: `encode-latin1` should become `encode-<registry-name>`, i.e. `encode-byte`.
  Leaning: yes. It is a format/spec change, not abi.
- Q3: unify the fold tables. Leaning: not now. It is an abi event.
- Q4: the data-description vocabulary and D1's `encoding` line.
- Q5: whether the shipped utf8 prior is authored or generated. Leaning: authored,
  plus a named generated analysis.
- Q6: make ASCII-compatibility a ruled design limit. Leaning: yes.

## Validation

Not applicable: no code, test or spec moved. The worktree build (`make -j16`, rc 0)
was used only for the two probes above and for `include_graph.py`. No suite was run
and none is owed by this lane. Each build step E1-E8 owes its own proof, specified in
note §4.

## For a follow-up lane

Start from note §4's table. E0 and E2 are the cheapest and fully independent. E1,
E4 and E6 touch files that 14 + 11 sabotage rows anchor to, so re-verify each touched
anchor from `git show HEAD:<path>`. E8 needs its two spec hunks in the same commit.
Sabotage ids for E3/E7 (note §6, item 2(d)) come from a manager-assigned range.

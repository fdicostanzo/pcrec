# lens10_evidence/ — lane lens10kit's measurement scripts

Reproduction pieces for `../lens10_emission_kit_charter.md` (2026-09-17, lane
`lens10kit`, against `main` at `7d444f9e`). Read-only python-stdlib scripts
over the committed source; nothing here is built, run by `make`, or read by any
check. Run from the repository root.

Each script's module docstring states its own method and blind spots; the
charter's §1.7 consolidates them. `count_runs.py` is the base module — the
other four import its lexer, argument splitter and prefix-expression set, so
a change to the prefix list changes every number at once, by construction.

- `count_runs.py` — **the D77 measurement** `lens2_domain_tool_separation.md`
  §2.4 step 4 named and deliberately did not build: runs of ≥5 consecutive
  `sb_puts`/`sb_printf`/`sb_putc` calls emitting a contiguous literal block
  with only the prefix varying. Carries the string/comment-aware lexer, the
  statement-position and guarded-call rules, the contiguity rule, and
  `PREFIX_EXPRS`. Answer: **1** across both emitters.
  `python3 <script> src/gen/emit_vm.c src/gen/emit_dfa.c [--dump-args]`
- `count_tmpl.py` — the same population counted **per call** rather than per
  run, because the emitters already merge literal runs into one `sb_printf`
  with a multi-line concatenated format. Buckets each call `LIT` / `PFX-ONLY` /
  `MIXED` and reports literal bytes and format line-spans per bucket. This is
  the measurement the charter's verdict actually rests on.
- `decompose_652.py` — splits `lens2`'s `652 %s_ substitutions` by **which
  argument each one binds**, pairing conversions to varargs positionally.
  Expands `emit_dfa.c:4262-4263`'s `VROW`/`VTBL` arg-pair macros; prints an
  unpairable count (currently 0) so a future arg-pair macro fails loudly.
- `anchor_census.py` — the A3 sabotage census **by ANCHOR, not by row**: 16
  rows carry a second anchor (`SAB_FILE2`/`SAB_BEFORE2`), so 261 rows are 277
  independently re-aimable anchors. Classifies each anchor by what its
  `SAB_BEFORE` block quotes (`TEXTCALL` / `SNPRINTF` / `BUFDECL` / `OTHER`).
  `python3 <script> .`
- `buf_risk.py` — the RISK measurement: which fragment buffers can truncate at
  a legal maximum-length (60-byte) `-p` prefix. Scopes declarations to the
  enclosing top-level function and bounds the worst case as
  `fixed format text + 60 × (%s bound to the prefix)`, scoring every other
  conversion ZERO — **a strict under-estimate, so its output is a candidate
  list and never a clean bill of health.** Answer: 0 provable truncations,
  tightest margin 9 bytes.

Maintenance: these are a lane's historical evidence. If a number in the
charter is ever re-derived, re-run the script rather than editing the prose,
and note the commit it was re-run at.

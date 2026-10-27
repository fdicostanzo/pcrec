# tests/code/ — module `code-c`'s tests (embedded C)

**[INLINE-C] stage 2, 2026-10-27.** ``(?C`c: ...`)``: a code segment in the
pattern, compiled into the artifact as a file-local function the site calls
through the ONE call form. Contract `docs/spec/match_api.md` §11.9-§11.10;
design `docs/design/inline_c.md`. `make test-code` runs `run_code_tests.sh`
(mech arm `code`). The `(?{ ... })` spelling is row [SCANNER-DOGFOOD]'s.

## Files

- `ipv4.rxt` — UC-1a / UC-1b (DT-1.1..DT-1.6); `geoip.rxt` — UC-3
  (DT-3.1, DT-3.2); `macros.rxt` — the macro set, guarded accessors, single
  evaluation, `RX_G_<name>` with (?J), span helpers in a segment, PCRE2's
  delimiters and doubled-delimiter rule, `once`, `consume`. All run under
  `test-corpus` too.
- `harness.manifest` — `allow-code c` (the grant, for this directory's ENTRY
  files only, `rxt_format.md` §6¶3) and `link geoip.c`.
- `octet.h`, `geoip.h`, `geoip.c` — the user's header and source the
  segments call (found by the harness's `-I` of the `.rxt` directory).
- `t2/t2.rxt` — the T2 check (§5.7): no manifest, so the block's segment is
  refused (`perr`); S-IC9's and S-IC28's corpus witness.
- `frag/` — the harness rule (§5.2): `entry.rxt` is granted by its
  manifest, the fragment `frag_code.rxt` it includes is not (`perr`);
  S-IC29's witness.
- `verify_code.py` — this directory's oracle (its NAME makes verify_rxt.py
  skip the directory): libpcre2 10.46 runs the SAME segment text with the
  macro set re-written from §11.9 as functions; floor 30 cells; `consume`
  blocks are a counted skip.
- `span_check.c` — the seven span helpers against references written from
  §11.10, exhaustive over a small alphabet, the u64 boundary and UTF-8.
- `lib_check.c` — the library grant: `allow_code` is the only door.
- `poison.h` — S-IC30's witness: poisons names a matcher uses.
- `dt41.h` — DT-4.1 inline's counter.
- `card_inline.sh` — the inline-mode measurement card (goal 3b): inline vs
  the callout-free `--engine=vm` twin, fires counted; `--smoke` in make test,
  `--timed` only in a cleared timing window (UNMEASURED otherwise).
- `run_code_tests.sh` — the eleven arms (its header lists them).

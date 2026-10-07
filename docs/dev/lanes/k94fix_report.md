# k94fix report — K94 FIXED-pending-merge

Lane k94fix, branch `lane/k94fix` (from main 9a66d8bb). Fix for K94: in the
byte encoding a caseless backreference under `--ucp` folded ASCII only, while
the `--ucp` classes and libpcre2 fold Latin-1.

## What changed

- `src/enc/enc.h`, `src/enc/enc_byte.c`: new seam entry id
  `PCREC_ENCE_SPAN_CASELESS_UCP` (bit 7); byte has a row, utf8 does not. It
  defines the same `$_span_match_caseless` symbol as the plain row and is in the
  mask INSTEAD of it. Plain byte artifacts (no UCP) are byte-identical.
- `src/enc/enc.c`: `enc_emit_latin1_fold_table` emits a ~56-row
  `{byte, representative}` table before that entry's definitions, generated
  from fold.c.
- `src/core/fold.c`, `internal.h`: `pcrec_fold_latin1_rep(c)`, c's Latin-1 fold
  class named by its least member, walking the same `ucd_fold_next` links
  `latin1_partners` walks. ONE fold definition: the links.
- `src/core/internal.h`, `src/parse/mod_backrefs.c`, `mod_vars.c`: `bool ucp` on
  `u.bref` and `u.var`, read at the reference beside `caseless` (the emit side
  reads no `cx->mods`, D108).
- `src/gen/emit_vm.c`: `vm_caseless_entry(v, ucp)` asks the encoding TABLE
  (`pcrec_enc_has_entry`), never the encoding identity (DD-12 (7)). Both
  `vm_bref` and `vm_var` use it.
- Engine routes: only the VM emits the span compare (backrefs/variables force
  the VM; `--engine=vm` and default agree, brefdiff §2 green). No DFA path
  emits it. PCRE2 rejects backrefs in lookbehind and the lookbehind copy goes
  through the same `vm_bref`, so no separate route exists. The
  [OPT-LITSCAN] runtime AND-mask is not built; nothing to reconcile.

## Oracle (PCRE2 10.46, ubuntubudu, light probe)

`/(?s)(.)\1/i` with and without `,ucp` over all 65,536 byte pairs:
- ucp: 256 identity + 52 ASCII + 60 Latin-1 ordered pairs (U+00C0..U+00DE
  except U+00D7 vs U+00E0..U+00FE except U+00F7). 0xB5, 0xDF, 0xFF fold to
  nothing (partners are U+039C/U+03BC, U+1E9E, U+0178: outside Latin-1).
- no ucp: ASCII only (256 + 52).
Scoped cells (`(?i:\1)` folds, `(?i:(\xe9))\1` does not), a named reference and
a reference inside an alternation were probed individually.

## Tests

- `tests/backrefs/caseless_ucp.rxt`: 175 cells, 0 failed
  (`bash tests/harness/run.sh tests/backrefs/caseless_ucp.rxt`).
- `tests/backrefs/fold_agreement_ucp_check.c`, wired as brefdiff §9c: all
  65,536 pairs against `pcrec_fold_latin1.partners`, 112 folding bytes, one
  partner each, 0xB5/0xDF/0xFF inert. PASS. The existing §9/§9b are unchanged
  and PASS (the plain byte fold stays ASCII-only).
- Sabotage S590 (emitter ignores UCP), S591 (rep ASCII-only): both DETECTED
  (`mech run COMPLETE: 1 rows (unexpected 0, undetected 0, unreached 0)`).
  S271 re-anchored (its anchored line now names `vm_caseless_entry`); intent
  unchanged, re-run DETECTED.

## Validation

- `make strict`: clean.
- `bash tests/backrefs/run_backref_diff.sh`: `checks failed: 0`.
- `make test-codegen`: first run red on [SABANCHOR] only (S271's anchor, fixed
  above; `scripts/m6read_check_sab_anchors.py` now "all anchors resolve"); a
  clean re-run is recorded in the handback.
- Mover census, `scripts/emit_sweep.py --ref main`: self-check clean; real run
  streams 1 and 2 (default, `--engine=vm`) show 2 movers each, both new
  patterns of this lane's own `caseless_ucp.rxt` (those carrying `(*UCP)` in
  the pattern; the `flags u` blocks are not reached by the argv stream). 0
  movers in streams 3-6 and in the pre-existing population. The diff hunk is
  the appended Latin-1 table and body in a byte + UCP + caseless-backref
  artifact only.

## abi

No bump taken. No scaffolding of any pre-existing artifact moved; the only
moved artifacts are byte + UCP + caseless-reference artifacts, whose ANSWERS
change (that is the fix) and which gain one table and the entry body. The
manager should rule whether an answer-fixing text move in that narrow class is
an abi event under D76/D94 (the census says the identity gate has no mover
other than lane-new patterns). If ruled yes: bump, re-pin readers by grep, and
`make test-codegen`.

## Spec

`docs/spec/cli.md`: the Caseless bullet under `--ucp` and the caseless
backreference bullet now state the byte + UCP fold.
Variables (`${name}`, vars module) share the same entry, so a caseless
variable under byte `--ucp` folds Latin-1 too; `docs/spec/vars.md` says only
"exactly as a caseless backreference does", which stays true.

## Owed

Mac `make test` under `worktrees/.mac-suite.lock` (held by the kit's M1b gate
when this lane finished sequencing); see the handback for state. No Linux run.

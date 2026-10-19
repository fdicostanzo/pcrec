# ctxspan21 — ctx_span.md revision 2.1 (lane report)

Lane `ctxspan21`, opus, design text only, 2026-10-19, from main `fd1d1fc98` (abi 80).
Nothing under `src/` or `tests/` changed. The bench's timing window was running, so nothing
was built, compiled or run: every new claim is read off the source or the notes, and what
needs a run is marked OWED with its command.

## What it applies

The re-check of `ctx_span.md` revision 2 (critR; the section "Re-check of revision 2" at the
end of `docs/dev/reviews/2026-10-18-r4-ctx-span.md`), all ACCEPTED. Edits are marked
`[r4rc <id>]`; `ctx_span.md` §R2.1 maps finding to section and §13 carries the discharge
table.

- **R1 (MAJOR)**, §4.2.3: the absent index is gated on the row,
  `q = (right_abs && ctxfn_reads_absent_next(fn)) ? 2 : bit(right)` and the mirror. It equals
  today's six functions and the `N_BOT_M`/`N_EOL_M` arms (checked against the closure code
  in `src/ir/dfa.c`). P2a's zero-mover argument is restored on it, with `\bfoo\b` (where
  `has_end` holds, e.g. `-e utf8`) as the witness the old rule moves. P2d's zero movers rest
  on it.
  **Consequence found by this lane:** under the gate no reverse machine reads `left_abs`
  (every absent-prev row sets `has_bot`, which routes to `ENG_ATTEMPT`, which has no reverse
  pass). So A1's plant can no longer be reached by a witness. S341's re-aim moves to R1's
  plant, and A1's plant becomes SP-11, declared UNREACHED, behind a closure routing
  assertion.
- **R2 (BLOCKER if built)**, §3.4, §3.6, §3.8, kit_proof §5.2: the narrowing is per thread.
  A frontier entry carries its pending restriction, and arrivals at one state merge by union
  (exact for the set and for the next frontier). On the previous side the slice narrows only
  when every thread at `d − 1` passes the item, and otherwise ends `exact_len` at `d − 1`.
  **Where the narrowed sets live: decided as the slice's own record** (`MkLang`). The walk
  projects one frontier twice, `KsetWalk.k[]` with restrictions ignored (today's hull) and
  `MkLang` with them applied. So `prefix_k.c`'s offset-k selection and OFS rows, the run pin
  and the `--emit-facts` k-set rows are unmoved by construction. Letting them read the
  narrowed sets is filed as UL-k, a mover event.
  Both witnesses are added to CK-6, kit_proof X0, `witnesses.txt` and `conj.txt` D as text.
  The union-narrowing plant is SP-6 = S1150, PROPOSED and not allocated.
- **R3**, §3.3: a multi-byte newline convention is refused by name until UL-e.
- **R4**, §4.5.4 and §7: each step regenerates its edit set from the real diff and compares
  it with `edit_set.tsv`. The derived list is taken from the regenerated set.
- **U1, U2** filed in §10, plus UL-k.
- `docs/design/CLAUDE.md`: one REVISION 2.1 line. `kit_proof/CLAUDE.md`: the appended
  witness lines.

## OWED (not discharged)

- `conj.py` verdicts on the two new witness lines:
  `PCREC=build/pcrec python3 -I docs/design/kit_proof/conj.py witnesses < docs/design/kit_proof/witnesses.txt`
  (`conj.txt` D carries them as `(owed)`).
- `conj.py` does not model the in-span rule. The slice's own sets on both R2 witnesses, and
  S1150's reach, need the built walk (Z2).
- The R1 claim that `\bfoo\b` under `-e utf8` interns an `endvar` under the old rule is read
  from the code and not measured. It is the plant's reach check at P2a.
- `make test-spec-history` was not run. The text has no spec line cites by grep.

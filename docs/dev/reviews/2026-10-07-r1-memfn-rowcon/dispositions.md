# Kit manager's dispositions, ROWCON panel r1 (2026-10-07)

Disposition is by THEME. Every finding id from the four critic files maps to
exactly one theme (or to its own line if it fits none).

T-A BINDING TIME (contract B1, sound B1, vis majors on define/use): ACCEPT.
  fields.def gains a binding column: SITE | DEFINE_BOUND (value-equal at
  both ends; FUNC floor = S8) | USE_ONLY (subset check at use, refusal
  only) | DEFINE_ONLY. Each phase runs its own gate, and the rev-1
  "use mask == define mask" rule is withdrawn.
T-B CONTRACT RULINGS ARE CONTRACT CHANGES (contract M1, sound B2): ACCEPT.
  The defaults are chosen to KEEP pcrec's live meaning: an unstated miss
  is `n` for every valued handoff (PRE ASSIGN included), and floor NULL ≡
  "0". The changes land as integration.md rev 4.9 + an MF_SITE_ABI bump
  (kit-internal, no pcrec byte) + a responses.md notice + G2 expectation
  updates, made by a BLINDED author after g2x. These go to Frank as
  Q-ROW-1.
T-C TEXT SHAPE (S2-S7; sound B3, the disagreements #8-#9): ACCEPT the
  contract route. s/n/lo hook text must be a primary expression and
  on_miss must be one statement (or braced). The kit REFUSES
  non-conforming text with a conservative lexical check. That is
  zero-mover. Parenthesizing in the kit would be a byte move with no
  measured need, so it is REJECTED (D77). Part of Q-ROW-1.
T-D LISTING IS A DECLARED MOVER (contract M3, vis majors on listing):
  ACCEPT. T2's --list-axes rows are a declared dumps-stream mover + a D80
  spec hunk + registry count re-pins, under the same-commit rule. The arm
  denies move no default byte (non-default switches). The "zero-mover"
  claim is restated as "zero ARTIFACT movers; one declared listing mover".
T-E CHARTER AND GENERALITY (contract M2, vis B1): ACCEPT the gap, and
  REFER the charter to Frank as Q-ROW-4: a generic table engine in the
  kit widens D146's charter (search-site text). Recommendation: yes, as a
  kit UTILITY under MF_NS with a charter line in memfn/CLAUDE.md, because
  decisions move into the kit (Frank) and the kit cannot link pcrec. For
  the migration mapping: mf_select takes a SCOPE (slot id + route mask
  filter) so ONE array with a slot field fits (start_table Q2); a
  ROUTE_SKIPPED verdict; and the record carries scope + the caller's site
  key as an opaque const char* (pcrec's macro keeps the literal check and
  passes it).
T-F VISIBILITY CHANNEL (vis B2, contract M4, reach Q-ROW-2): RESOLVED
  without a pcrec change. The kit gets a COMPILE-TIME trace (MF_TRACE,
  kit-side, off by default) that prints each decision record to stderr
  during pcrec's own compile. site_census.py's traced build turns it on.
  The record stays kit-internal: no mf_result/mf_call ABI change and no
  form_id comparison. mf_explain is the API that G2 and K3 call. T6 (the
  pcrec hook) is DROPPED, so Q-ROW-2 is answered: no R-6.
T-G REACH GRAIN AND INDEPENDENCE (reach B1, B2, M2, M4, M5, m1; contract
  M6; vis deny-delta): ACCEPT.
  - Reach cells are (row, honoured field, declared value-class), with the
    classes in fields.def.
  - Independent controls: a name-level manifest of rows and witnesses (a
    committed table, not derived); text signatures checked in the
    artifact; G2 byte-loop agreement; start_table §3.4's deny-delta
    control.
  - A closed reason vocabulary for rows unreachable from pcrec:
    total-fallback | pending-site+trigger | contract-reach+G2-family.
    Anything else is deleted.
  - Count at successful render.
  - Counters are summed across the corpus by the census (the trace
    route), not kept in mf_art.
  - Witness drift is detected because each witness asserts its row by
    signature.
T-H GATE MODEL (sound M1, M2, M4, M5, M6; vis full-mask, reason codes,
  deny-switch, nesting, no-row semantics): ACCEPT.
  - Fields get a kind (obligation | permission | requirement |
    rendering) and per-value bits for enums.
  - Hooks are NORMALIZED once before the gate, and rows read only the
    normalized form.
  - A row has `requires` (positive, e.g. precheck's miss_leaves) as well
    as `honours`.
  - Shape-dependent honouring is expressed by splitting the row, or by an
    honours FUNCTION.
  - The vacuous static assert is replaced by G2's per-field cells on
    generic.
  - The record keeps the FULL failing mask, a predicate-false reason
    code, the deny source, and a bounded nesting depth.
  - No row applies → NULL, and the CALLER's policy decides (the kit
    refuses; pcrec may keep crashing).
T-I SCOPE TRIMS (contract M5): ACCEPT.
  - T4 (sub-tables) is dropped until a measured need, i.e. a K96-class
    finding inside a row's sub-choice.
  - pcrec adoption stays an OFFER after START-TABLE C7, not planned work.
  - Q-ROW-3 is answered "not now" (unanimous).
T-J D153 overlap (contract): NOTED. T0-T5 touch no pcrec file except T2's
  axes_dump listing hunk (an M1b-touched file, now merged; no in-flight
  lane edits it). That hunk is re-checked at T2's cut.
Anything uncovered: ACCEPT-AS-MINOR, folded into rev 2's text.

# l3enc report

STATE: stopped (disposition (b): a real, declared encoding fact; per the brief's STOP rule, the checker change is the manager's ruling)

## Summary
The byte/UTF-8 asymmetry on `(?<=a)(b)\1x` and `(?i)(?<=ab)(b)\1x` does not come from the pick rule's
logic. All three of its own inputs agree on both sides: `fwd_reentry` = 1, the candidate's consumed
extent `[lo, hi)` is nonempty, and `lb_bytes` admits BACK. The input that differs is the consumed
`best` the rule protects. It differs because the run choice's rarity tie row (`rn_rarer`, which reads
the byte-rate) has a rate under byte and NONE under UTF-8. That NONE is declared in the shipped data
(D123-4, `src/findings/default.rxt:42-46`: `serves byte-rate when byte`). Classified (b). No code was
changed. Tip: this report's commit on lane/l3enc (parent ca107608d).

## Why the encodings differ
Premise test, on this worktree's build (`build/pcrec --features all -e byte|utf8 -p rx --pattern P -o F`):
- `(?<=a)(b)\1x`: byte gives `RX_REQ_RUN "6162@1"`, `RX_REQ_BYTE "98"`, `RX_REQ_HANDOFF "-1"`. utf8 gives
  `RX_REQ_RUN "none"`, `RX_REQ_BYTE "120"`, `RX_REQ_HANDOFF "none"`.
- `(?i)(?<=ab)(b)\1x`: byte gives `RX_REQ_RUN "414242@2/dfdfdf"`, `RX_REQ_HANDOFF "-2"`. utf8 gives every
  stamp `none` (`RX_REQ_WHY "none"`).
- BASE (worktrees/l3r65tri-base build, 694d91dc4): no run and no handoff on either side for both
  patterns. This matches the triage report.

Inputs at TOP's BACK row. Seen with a temporary stderr print in `rb_top`
(`src/facts/req.c:1718-1733`), which has been reverted; the tree is clean and rebuilt:

| pattern / enc | consumed `best` (root->best) | BACK cand | fwd_reentry | lb_bytes | displaces | rn_cmp |
|---|---|---|---|---|---|---|
| `(?<=a)(b)\1x` byte | `x`, off UNBOUNDED, scan mass 997 | `ab` off -1, [1,2) | 1 | 1 | **1** | -8 (cand) |
| `(?<=a)(b)\1x` utf8 | `b`, off 0, mass 3906 (member count) | same | 1 | 4 | **0** | -8 |
| `(?i)(?<=ab)(b)\1x` byte | `[Xx]`, off UNBOUNDED, mass 1097 | `abb`/i off -2, [2,3) | 1 | 2 | **1** | -14 |
| `(?i)(?<=ab)(b)\1x` utf8 | `[Bb]`, off 0, mass 7812 | same | 1 | 8 | **0** | -14 |

- The displacement condition is `src/facts/req.c:1709`:
  `!w->fwd_reentry || best->n == 0 || (lo < hi && best->off >= PCREC_W_UNBOUNDED)`. Its only differing
  term is `best->off`: UNBOUNDED under byte, 0 under utf8.
- The consumed `best` is chosen by `rn_choice_rows` (`src/facts/req.c:534-540`). The two one-byte
  candidates (`b` at 0, `x` past the backreference at no static bound) tie on information.
  - Byte: row 2, `rn_rarer` (`req.c:488`, mass via `rn_scan_mass` `req.c:479`), decides by the byte-rate
    prior. `x` is rarer (997 against `b`'s higher mass), so `best` is the unbounded `x`, and BACK may
    displace it.
  - UTF-8: `pcrec_find_byte_rate` (`src/core/findings.c:429`) returns NULL (`rate:none(utf8)->rightmost`
    in `--emit-facts`). The mass is the member count, so `rn_rarer` ties. Row 3, `rn_nearer` (`req.c:496`),
    then keeps `b` at off 0, a bounded run, and the rule refuses BACK.
- The rate is the cause, not the encoding as such. Control: in `(?<=a)(q)\1e` the prior makes `q`
  rarer than `e`. Byte then keeps `q`@0 exactly as utf8 does, and both sides give `RX_REQ_RUN "none"`
  and `RX_REQ_HANDOFF "none"`.
- The rate's encoding scope is declared, not incidental. `src/findings/default.rxt:42-46` says the
  default prior serves the byte-rate only under `byte`, because its flat 0x80-0xff half would rank a
  UTF-8 lead byte rarest (D123-4). Under `-e utf8` every rate question takes its NONE answer (findings
  design §6.2).

## Disposition
(b): a real encoding fact. The run choice ranks equal-information runs by a byte-rate that the shipped
data declares for `byte` only. So the consumed run the pick rule is asked to protect is legitimately
encoding-dependent wherever two equal-information consumed runs, one bounded and one not, are separated
only by rarity. Each side is self-consistent under the ruled rule:
- byte: the protected run is unbounded, so there is no forward re-entry to keep, and BACK displaces it.
- utf8: the protected run is bounded, so BACK does not displace it.

Making the pick encoding-blind would mean either changing the run choice's tie rows or ignoring the
rate. That is not a change to the pick rule's own row or inputs, so it is outside this lane's fix
scope.

An observation for the ruling, not acted on: the bounded UTF-8 `best` (`b`@0) hands off nothing at
BASE either (`RX_REQ_HANDOFF "none"`). The re-entry the rule guards there does not exist in emitted
code. The rule's proxy "bounded offset" means "keeps the forward re-entry", which over-approximates in
this shape. Refining the proxy to "the handoff would actually fire" would need gen-tier dominance facts
(the start-byte row covering a K=0 single byte) in the facts layer. That is a layering question, not a
declared-input edit. It would also make both sides keep L3's run (l3tri's symmetric pins).

Implied checker change (the manager's ruling, per the brief): `tests/codegen/run_encoding_checks.sh`
DD12a(i)'s `presence_stmts` normalization would have to handle a run stated on ONE side only. The two
patterns would also be declared as K50 rows in `tests/codegen/manifests/k50_gate_refinement.txt`, as an
encoding-declared (rate-scoped) selection difference. The A-list re-check of the six BASE patterns was
not run because nothing was changed.

## Shard 13
Not made green. Per the brief, shard 13 and test-cpset-structure are fixed only under (a). They stay as
the triage lane left them: shard 13 is red on the three DD12a FINDING lines (l3r65tri_report.md,
"Shard 13 DD12a"), and cpset-structure is green from l3r65tri's restore. No answer mismatch against
libpcre2 was seen or tested: no corpus run was made.

## Validation dispatched
None. Nothing was changed, so there is nothing to validate, and a cloud run would only reproduce
shard 13's red. No `cloud/main/*/l3enc*` ref was created. Local box use: `nice make -j4` (three builds:
base, instrumented, reverted) and single-pattern compiles only. It ended at 23:32.

## STATE AT HANDOFF
- Branch lane/l3enc: this report only, on top of ca107608d. `src/` is unchanged; the instrumentation
  was reverted and the tree rebuilt clean.
- Last R-n applied: none (`l3enc_rulings.md` empty).
- Owed: the manager's ruling on (b). Choose between declaring the rate-scoped asymmetry, which means a
  checker generalization plus two K50 rows, and refining the pick rule's re-entry proxy (a layering
  question). After that comes a fix lane, then a cloud run.
- `docs/dev/lanes/l3enc_deliver.txt` is untracked (manager-written; I left it as found).
- Scratch: /var/tmp/pcrec-pcrec/scratch/l3enc/ (req.c.orig, the build logs).

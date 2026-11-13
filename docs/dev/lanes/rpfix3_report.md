# rpfix3 report: the 2^40 head_max crossing to the kit (lane rpfix3, opus, 2026-11-12)

## STATE AT HANDOFF

STATE: stopped (the brief's STOP RULE fired). No source change, no build, no run, no push, no cloudrun.

On the seam, 0 means "no handoff", not "unbounded". So mapping pcrec's
`PCREC_W_UNBOUNDED` to 0 would state a false fact. The cloud red (C10 presence,
`(a+)+zq`) would go green, but for the wrong reason.

Evidence (read-only):

1. **What the seam declares.** `memfn/include/memfn.h`, `mf_site.head_max`: "the largest distance, in bytes, from a match start to
   the landmark origin the site's verdict hands on (K ...): the handoff's K where the site ASSIGNs the landmark, else 0.
   An ALL_PRESENT site only (0 elsewhere, refused otherwise)." 0 is the value on a site that does NOT assign
   (none). It is not reserved for "no bound". No unbounded value is declared. This matches
   `docs/design/fact_consumers_inventory.md` §4's `head_max` row: "0 = no handoff (overloaded with distance 0)", reserved
   value "NO".
2. **Why main states 0.** On main, `req_handoff_applies` returns false at `k >= PCREC_W_UNBOUNDED`, so for `(a+)+zq`
   `handoff` is false. The site is then `MF_H_ON_MISS`, and `src/gen/emit_dfa.c` (the `s->head_max = handoff ? ... : 0` line in
   `req_site_define`) states 0, meaning "none". On lane/rpfix the [REQ-PAST-LAST] row admits the unbounded handoff, so the
   site is now `MF_H_ASSIGN` with K = 2^40. Main and the tip agree on the 0 VALUE, but not on what it means.
3. **What a 0 under ASSIGN would say.** On an ASSIGN site, `head_max` IS K, so 0 states "the landmark origin is at the
   match start (distance 0)". The kit reads it that way: `memfn/src/presence.c` (the fifth port, landmark admission,
   `if (s->handoff == MF_H_ASSIGN) { ... k = s->head_max; ... }`) uses it as `k` in its `k*h` cost. A 0 there prices the
   unbounded handoff as free. Today only the trace shadow reads that verdict (TH-5), so no byte moves now. It is still
   a false stated fact, and C10 would pin it.

The seam has no correct value for this today. The options are the manager's call:

- (a) Do not state the unbounded handoff as ASSIGN to the kit. State the site as main does (`MF_H_ON_MISS`, head_max 0,
  "none") while pcrec's own emitted stop stays the [REQ-PAST-LAST] row. This only fits if the kit's ON_MISS
  meaning is not contradicted by pcrec handing the landmark on; that needs checking against `memfn/src/compose.c`'s handoff rules.
- (b) A kit request for a declared "no bound" value of `head_max` (TH-5; the inventory §6's typed-width unit,
  [FACT-READS]; D157: pcrec states the fact, the kit spells it). Then re-pin C10's row to that value.
- (c) Interim: re-pin `tests/memfn/c10_presence.tsv`'s `(a+)+zq` row to 1099511627776. This records today's (undeclared)
  value honestly, with a comment naming TH-5, until (b) lands. This is a test-only change. It leaves 2^40 crossing undeclared.

Leaning: (c) now (honest, test-only, unblocks the branch), with (b) filed as the kit request. (a) needs its own check
first.

Owed: nothing launched. The cloud test on lane/rpfix is still red on C10 until one of the options lands.
No rulings file was named in the brief.

## CHANGES

- `docs/dev/lanes/rpfix3_report.md` (this report).
- `docs/dev/history/claude_md/docs__dev__lanes.md`: index line.
- No code, test or fixture change.

# SEAM critic — crit-memfn-sp1d (span_pick 1d, planning core)

Lens: could what crosses the planning face be written to text and read back
by another process with every answer unchanged? SUBJECT e9e5f035e, BASE
daf6f002b. Compiles counted in PROBED-AND-HELD.

## FINDINGS

### SEAM-1 — CONFIRMED: a WCAND record does not determine A-mass's pick (the stretch bit is missing)
- Severity: design (trace/seam sufficiency); effort XS (add `stretch=` to
  gate_cand and the record, plus a trace_format.md line); blast radius: the
  WCAND reader only (MF_TRACE builds), no emitted byte.
- Where: memfn/src/kit.h `gate_cand` (no stretch field);
  memfn/src/window.c `trace_cands` (~l.1093) vs `a_mass_choose` (~l.618), which
  picks the TIE row from `p->stretch` (T_MASS_STRETCH = HIGHER vs
  T_MASS_SET = LOWER); memfn/docs/trace_format.md WCAND paragraph.
- Repro (NONE regime, so masses are member counts):
  `tr-subject/pcrec -p rx --features all -e utf8 -o O/x.c --pattern '[ac][ac]'`
  and the same with `'[ab][ab]'`. Both: `chosen=A-mass`, and the WCAND input
  fields are byte-identical:
  `alt=0 off=0 members=2 mass=7812 core=1 stop=1 walked=0` and
  `alt=0 off=1 members=2 mass=7812 core=1 stop=1 walked=0`.
  Observed: `[ac][ac]` key=1 at off=1 (a cube, inside a 2-position span: the
  stretch row, ties HIGHER); `[ab][ab]` key=1 at off=0 (not a cube: the set
  row, ties LOWER). Same pair with a lead byte (`k[ac][ac]` / `k[ab][ab]`)
  holds the same records too (the lead byte wins there, so the keys agree).
  Expected for a self-sufficient record: equal inputs, equal key.
- Two records equal in every input field, chosen row equal, picks differ: the
  record is not the pick's input. A text reader needs hidden state (the
  site's span cover `multi` and the set's cube `shape`). 1d ADDED the record,
  so this is a gap in what 1d added, not a regression.

### SEAM-2 — CONFIRMED: A-model's inputs are not in the record (each walked offset's OWN set, its scan eligibility, F0's own mass)
- Severity: design (trace/seam sufficiency); effort S (a per-walked-offset
  `own_members=`/`own_mass=`/`scan=` and an `f0_mass`, or a per-alternative
  record); blast radius: WCAND readers only, no emitted byte.
- Where: window.c `cands` (~l.349: `w->mass` = the walked span's OWN set,
  KIT_MASS_CAP; `w->scan` = `scan_ok`, the OWN set's count == 1 and the span's
  core) vs `trace_cands` (~l.1093: `members`/`mass` are the C-meet's, `stop`
  is `stop_ok`, A-mass's domain). trace_format.md even says the walked offset
  is "priced on its span's OWN set", which the record does not carry.
- Repro: fixture driver /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1d/SEAM/drv/seam_drv.c
  (includes tests/memfn/arm_fixtures.c for its helpers; one gcc line against
  tr-subject/libpcrec.a). One RESEED alternative, NONE rates: F0 `{f}`@0
  verify-YES; walked `{g}`@1 (variant 0) or `{gG}`@1 (variant 1), walked `{h}`@2;
  a verify-NO run R at 1..2 = `{g},{h}`, so the meet at 1 is `{g}` in both.
  Both variants: wf_check and mf_define accept; `chosen=A-model`; the three
  WCAND records are identical in every input field
  (`off=0 members=1 mass=3906 core=1 stop=1 walked=0`,
  `off=1 members=1 mass=3906 core=1 stop=1 walked=1`,
  `off=2 members=1 mass=3906 core=1 stop=1 walked=1`).
  Observed: variant 0 key/stop = off 1 (`path=reseed`, nplan 1); variant 1
  key/stop = off 2 (`path=reseed+pin`, nplan 3): off 1's own set has two
  members, so it is no scan. Same records, same chosen row, different pick.
- A second hidden input of the same family (C-model, the plan rather than the
  stop): drv/seam_o.c. One RESEED alternative, F0 `{f}`, scan `{i}`@4, and
  three equal-mass walked sets `{gG},{hH},{jJ}` at 1,2,3, LISTED in two
  orders (1,2,3 vs 3,2,1). WCAND identical (it is written in OFFSET order;
  the list order is not recorded); stop @4 in both; reply plan `0,1` vs
  `0,3`. T_CMODEL is TIE_EXCHANGE over walk-index (listed) order, so the
  span list's ORDER is a semantic input of the plan face: a text form must
  preserve it, and the record does not.
- 1d ADDED the record and MOVED A-model's enumeration into `cands` (the
  `walk[]` list keeps listed order, as BASE's span loop did): no behaviour
  change, but the record 1d added omits exactly the inputs its own list holds.

### SEAM-3 — CONFIRMED: the incumbent (MARGIN vs M-parked) is not determined by the record
- Severity: design; effort S (A-parked's input, the verify-YES meet at 0:
  its member count and mass, plus each alternative's `entry`; or the deferred
  per-alternative price); blast radius: WCAND readers only.
- Where: window.c `a_parked_choose` (~l.535: prices k0 = the VERIFY-YES meet
  `yset` at offset 0, memchr vs bitmap by its count, and its mass) and
  `m_margin_holds` (~l.742: reads both alternatives' `cost`, `priced`, arow
  and `m_pair`'s `entry`); the record carries the all-span meet only.
- Repro: drv/seam_m.c, skewed rates (arm_fixtures' pur_rated). PARKED alt:
  verify-YES `{z}`@0 (variant 0) or `{za}`@0 (variant 1), plus a verify-NO R
  at 0..1 = `{z},{g}` (so the meet at 0 is `{z}` in both); RESEED alt =
  arm_fixtures' pur_reseed. All six WCAND records identical in every input
  field in both variants (e.g. `alt=0 off=0 members=1 mass=100 ...`).
  Observed: variant 0 `chosen=M-parked`, incumbent alt 0 @0
  (`path=parked+pin`); variant 1 `chosen=MARGIN`, incumbent alt 1 @1
  (`path=reseed`). The ROW records name the deciding M row, but nothing in
  the text lets a reader recompute it.
- span_pick.md §The shape "The trace" asks for "every candidate, the rows
  walked, the incumbent and the deciding row" and defers PRICES to T-PICK row
  1; the deferral is ruled. The finding is narrower: the record omits the
  price INPUTS (facts, not prices), so "the rows walked" is the only witness
  and is not checkable against the candidates. 1d ADDED.

### SEAM-4 — SUSPECTED (design note): what crosses the face is not what is traced, and the text association is order-borne
- Severity: design/doc; effort S; blast radius: trace readers.
- (a) pcrec's planning-face calls (`mf_wdecide`, emit_dfa.c :1068 and
  :7610) decide QUIET and write nothing; WCAND is written only by the kit's
  own define re-decision (`wf_prepare` -> `decide(.., quiet=0)`). The two
  agree today because both are the same function of the same inputs (the
  purity harness asserts the reply's order-independence). KEPT from BASE
  (breaker (c)'s fence, ruled); a stored-plan cache would make the trace
  describe a decision nobody read. No record anywhere writes the SITE FACTS
  (spans, entry, verify, core, list order), so no text exists from which the
  plan call's input could be read back; the seam is serializable in shape
  (all values; pointers only to host-owned arrays) but not serialized.
- (b) Within a define, the per-alternative wfA SEL/ROW/END blocks carry no
  `alt=` (seen on `abc[0-9]+xyz`: two identical `SEL table=wfA ... site=1`
  headers); a reader pairs them with WCAND's `alt=` by ORDER only. `site=H`
  is `art->nsites + 1`, a call-order label (breaker (b)); a pre-check's FUNC
  parts (window.c :2089, each through wf_prepare under the same label) would
  write WCAND blocks with the same `site=` and repeating `alt=`, told apart by
  order only (SUSPECTED: not reached by a pattern here). 1d ADDED `alt=` on
  WCAND, KEPT the rest.

### SEAM-5 — CONFIRMED (KEPT, not 1d's): the handed rates cross as an untyped, unsized, host-owned pointer
- Severity: design; effort S; blast radius: every rate reader (KEY, MARGIN,
  D-hors, PRES picks).
- `kit_byte_rate` (presence.c :49) returns `(const uint32_t *)payload` of the
  first kind tagged "byte-rate" whose `present` is PRESENT; it reads neither
  `mf_akind.version` nor any length, and the table is host-endian uint32[256]
  by convention. The art stores the HOST'S pointer (`art->an`, compose.c :884),
  so a host that changes its rate table between plan calls changes answers:
  shared mutable state the purity harness cannot see (its `pur_rates` is
  written once per mode before any call). A text form must fix the payload
  shape by (tag, version) and snapshot it at `mf_art_begin`. 1d only rewrote
  the compose.c comment (now accurate: "kit_byte_rate reads them").
- Repro: drv/seam_r.c (against the SUBJECT build/libpcrec.a): one art
  begun on pur_rated(), `mf_wdecide` on arm_fixtures' pur_site(0), then the
  host sets `pur_rates['z'] = 900000` and asks again on the SAME art: reply
  `stop 4 -> 2`. Expected of a pure plan face "no hidden state": the art's
  rates are an input fixed at mf_art_begin. (pcrec's own bundles are
  immutable for a compile, so no artifact moves today; the hazard is the
  seam's, not pcrec's.)

### SEAM-6 — CONFIRMED by reading (KEPT; 1d narrowed it to one site): the rules are process-static and unversioned in any crossing record
- Severity: design (low); effort S when wanted; blast radius: a future
  out-of-process planner/reader.
- `wf_ties[]` (window.c :85), `plan_cost.def` (the COST() cards, read by
  verify_cost/model_cost and MARGIN's MATERIAL_NUM/DEN), `MF_PPM_FULL`,
  `WF_LO` (MF_MAX_BACK) and the A/M/C row ORDER are compile-time constants of
  the kit build. No reply field, stamp or trace record names a version or
  digest of them (grep: no reader of plan_cost/wf_ties outside window.c, no
  stamp), so two processes built from different kits read the same WCAND
  text and disagree silently. 1d ADDED nothing here and helped: every argmin
  now reads its TIE row through `kit_pick_takes` (window.c :135), one site
  where a rules digest could be taken; `wf_ties[T_CMODEL/T_MARGIN].to` are
  still read directly (kit.h comment says so).

## PROBED-AND-HELD

- Compile count: 35 pcrec compiles (11 of them refused at the CLI: no
  `uniform` analysis in the built-in store, so the all-tie regime was probed
  with `-e utf8`, NONE, instead). Plus 4 fixture drivers (seam_drv, seam_m,
  seam_o, seam_r), one gcc line each, run once or twice: kit calls, not
  pcrec compiles.
- Inventory of what crosses `mf_wdecide(art, site, out)` (SUBJECT):
  READS `art->err[0]` (sticky refusal, breaker (a), ruled FENCED, KEPT),
  `art->an` via kit_byte_rate (SEAM-5, KEPT), `art->nsites`/`trace_id` only
  in trace labels (breaker (b)/(c), KEPT); the site (all plain values: span
  arrays by pointer, `opts` a string). Does NOT read `art->ms`, `policy`,
  `denies` or `levers` (the wfA/wfM walks pass denies 0 and their kit_tables
  have no `opt`), and `consulted` still has no writer (breaker (d) future;
  `git grep "consulted *="` in memfn/src: only mf_art_end's read). 1d added
  no `art->` read and no mutable static (diff grep).
- `mf_wreply`: fixed-size plain fields (`plan[MF_WPLAN_MAX]`, `stop_set[32]`,
  `path[16]`): text round-trips with no pointer. HELD.
- `gate_cand` and `kit_pick`: plain values, no pointer. `kit_pick.pos` means
  a different index per caller (WF_NPOS slot, walk index, run index, window
  start) but never leaves its caller; the run member keys by run-relative
  index, sound only because T_MASS_STRETCH is translation-invariant (the
  PRECONDITION comment at window.c ~l.818 says so). HELD.
- `kit_pos_at` callback + `void *src` (kit_run_member): kit-internal (callers
  window.c run_member/translate and presence.c), never on the planning face to
  pcrec; KEPT from 1c. A planner split carries the run's sets as data (both
  readers are 32-byte arrays or a RUN term's kit_run_set). HELD for the seam.
- `kit_run_member`'s `after` walk rewritten as `!kit_pick_takes(&c,
  after->mass, T_MASS_STRETCH, after->pos)`: algebraically equal to BASE's
  skip test (ms < after.mass, or equal and the row does not send `after`
  over j). HELD by derivation.
- presence.c T_WINDOW: `at` now `bw.pos` with no `at = lo_s` seed; the loop
  is never empty (n > MF_PRES_WINDOW and scan in [0, n) give lo_s <= hi_s),
  so -1 cannot escape. HELD by derivation.
- WCAND emission matches trace_format.md (fields, order: alternative then
  offset, before WPATH; none on a query/quiet decide): 18 traced patterns
  (default rates and NONE) and the 3 drivers. HELD.
- The purity property the harness claims (reply independent of define
  order) is untouched by SEAM-1..3: those are record-sufficiency gaps, not
  impurity. SEAM-5 is the one impurity found, outside the harness's reach.
- Denylist: no denied file opened.

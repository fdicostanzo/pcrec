# r4 light panel: window_contract.md revision 3 (E-1, §R3/§3.7)

Critic: read-only D6, 2026-10-16. Subject: `lane/wcrev3` (`cd9fda38d`, not
merged to main at review time), `docs/design/memfn/window_contract.md` §R3,
§3.1-§3.7, plus `docs/dev/lanes/wcrev3_report.md` and
`docs/design/memfn/window_contract_rev3/`. Read against main `ee5555f7b`
(`src/core/findings.c`, `src/gen/memfn_sites.c`, `src/gen/emit_dfa.c`,
`src/core/compile.c`, `docs/design/measure_sets.md` rev 3,
`docs/dev/decisions.md` D162). The probes ran main's `build/pcrec` on single
patterns. The fixtures were copied into the session scratchpad. No make was run.

Tally: 1 BLOCKER, 5 MAJOR, 6 MINOR.

---

## BLOCKER

### B1. E-1 is not zero-mover: the offer's derivation can REFUSE a compile that succeeds today (deny arms × an underivable bundle), and G1-E1's population cannot reach the case (K35)

**Evidence.** §3.7.1 says `pcrec_find_offer` "DERIVES through the same
memoized derivation the readers use (`find_derive_byte_rate`)". That function
calls `pcrec_ctx_fail` when the answering block normalizes to nothing
(`findings.c:303-311`: "counts nothing via %s", plus an internal-error arm).
Today that refusal is LAZY: it fires only when a reader asks. The offer runs on
every attempt (§3.7.1, "Every artifact builds it"), so it would fire on
compiles that ask nothing.

I reproduced this on main's binary with `tests/findings/run_findings_tests.sh`'s
own `l1none` fixture (a `cpfreq` block, `serves byte-rate when utf8 via
encode-latin1`, a single `U+20AC` row):

| invocation (`-e utf8 -I L1 --analysis l1none`) | today |
|---|---|
| `--pattern 'abc'`, default | refused: "counts nothing via encode-latin1" |
| `--pattern '^abc' -fno-req-byte` | **compiles, `RX_FINDINGS ""`** |
| `--pattern '^abc' -fno-req-byte -fno-req-run -fno-prefilter` | **compiles, `""`** |
| `--pattern 'caf.' --engine=vm -fno-req-byte -fno-req-run` | **compiles, `""`**, rc 0 |

Under E-1 as written, every bold row becomes a refusal. That is a
caller-observable mover: the refusal set changes, which needs D80. It
contradicts §3.7.3's "E-1 lands at zero movers in every arm, deny arms
included" and §3.7.9's "E-1 carries NONE". That claim is the main support for
the CONSULTED leaning that Q3 puts to Frank.

The gate cannot see it. G1-E1 and the census (`stampcount*.py`) compile
emit_sweep's argv stream with no `--analysis` and no `-I`. In that population
the store's terminal always answers and always derives, so an underivable block
never occurs. The deny arms are present, but the analysis axis is not. This is
K35 again, one axis over from the one §3.7.4 found.

T-KIND is also not total. "A block answers, but its derivation fails" matches
`measured` or `prior-authored` by predicate, yet there is no payload to carry.
The first-match table has no row for that cell.

Also relevant: `docs/spec/findings.md` 3a¶3 says such a block "is refused at
compile". Today that holds only when something asks. So either reading of the
spec moves somebody. That makes this a ruling, not an implementation detail.

**Fix.**
1. Split the derivation into a non-raising `derive → status` that the offer
   calls, and keep the `pcrec_ctx_fail` on the ASK path, so the refusal stays
   the asker's.
2. Add a T-KIND row `underivable` (a block answers and its derivation fails),
   with a stated state. My leaning is PRESENT / PRIOR_NONE for an `ALWAYS` kind
   (the no-information answer) and ABSENT otherwise.
3. Add a G1-E1 sub-population: each deny arm × {`--analysis weblog`, `log`,
   `l1none`-shaped, an `-I` bundle}, with a floor of at least one compile per
   cell that refuses today when asked and compiles when not.
4. If Frank prefers the spec's unconditional refusal instead, E-1 becomes a
   caller-observable change: it needs a D80 hunk on findings.md 3a¶3 and a
   census of the deny-arm refusals. Q3 should then say that "zero-mover" was
   never available.

---

## MAJOR

### M1. `arrives = MEASURED-ONLY` does not keep a kind absent: T-KIND's `prior-authored` row fires before `arrives` is read, which breaks D162 add. 2

**Evidence.** In T-KIND (§3.2), `arrives` appears only in the `prior-none` row.
The `prior-authored` row ("a block answers, and the answering link IS the
store's `default` bundle") has no `arrives` conjunct. D162 add. 2 says the
opposite (decisions.md, D162 add. 2 reading): "Every other analysis kind …
is present only when measured and is otherwise EXPLICITLY ABSENT, never filled
with a guess." Today this is latent, because `default.rxt` has no `bigram`
block. The first time pcrec ships an authored `bigram` block (B4 is the
natural moment), `run-rarity` arrives PRESENT/PRIOR_AUTHORED, which is exactly
the guess the ruling forbids. S987 plants only the `byte-rate` flip, so no
sabotage row covers it.

**Fix.** Make `arrives = ALWAYS` a conjunct of `prior-authored`, or make
`absent-by-arrival` a row ahead of it. Declare the witness UNREACHED until
`default.rxt` serves a second query, and give it a synthetic store fixture in
the test build. Also name the column after what it decides ("present without
measurement: yes/no") so its reach is not misread as "prior-none only".

### M2. Provenance is re-derived from the chain LINK although the data already declares it: a parallel mechanism, and §3.6's "filed" evidence-strength fact is both already present in the data and already triggered

**Evidence.**
- Every shipped data block carries a schema-validated `provenance` stanza.
  `default.rxt` has `source authored` and an `analyzer authored: …` line.
  `weblog.rxt` has `source elastic-examples-…`, `bytes 1000000` and a `sha256`.
  `log.rxt` has `bytes 999960` and `fidelity synthesized`, where `fidelity` is
  a CLOSED vocabulary: `rxt_schema.def:278`, `verbatim adapted synthesized`,
  required for a data block.
- T-KIND ignores all of this and calls a block `measured` if it was not reached
  as the store's default. Two consequences, both probed:
  - A byte-identical user copy of `default.rxt` at `-I DIR/default.rxt` with
    `--analysis default` resolves at link 0 (`stop -I`) with the built-in's own
    digest `1822fb973b95a4da`. T-KIND calls it `measured`, and rule 7 then
    admits the authored prior as EVIDENCE.
  - `log`'s synthesized corpus is `measured`, and §3.2 hands the difference to
    §3.6.
- §3.6 files evidence strength ("how much data a `measured` kind rests on") with
  the trigger "the first kit row that reads `measured` provenance as EVIDENCE".
  §3.3 rule 7 names exactly such rows, r17b′'s F0, R5, R6, R8 and P1, ported at
  B3a and routed at B3b. So the trigger fires inside this very plan, two steps
  after E-1. The fact also already has a home: the block's `provenance bytes`
  row.
- `PcrecFindTblBlock` (`findings.h:36-45`) does not carry the provenance stanza
  today. That is the real gap.

**Fix.** Source `mf_prov.source` from the answering block's own declared
provenance (`source authored` → PRIOR_AUTHORED; else MEASURED, with `fidelity`
carried). Carry `bytes` as the evidence-strength field now, while the
`mf_prov` layout is new and costs no extra `MF_SITE_ABI` event. That means
extending `PcrecFindTblBlock` and `findgen`'s pre-parse. Link identity can stay
as a cross-check (C-E1-1's second derivation) instead of being the rule. If
the leaning stays link identity, §3.6 must say why rule 7's named rows do not
fire its trigger.

### M3. The CONSULTED design's observable step is unplaced: `_FINDINGS` (and `_MEASURES`) are rendered BEFORE `mf_art_end`, so the kit's `consulted` cannot reach them where they are written today

**Evidence.**
- `emit_dfa.c:3040-3049`: the `_FINDINGS` stamp and its `rx_info` mirror
  (`:3348`) are written in `emit_info_def`, "after every emitter has run …
  because the stamp must read the record after the LAST reader (§6.4 rule 2)".
- The kit's per-kind `consulted` exists only at `mf_art_end`, which pcrec calls
  in `pcrec_memfn_stamps_render` (`memfn_stamps.c:241`, "It ENDS the attempt's
  kit state"). That runs at `compile.c:2971`, after the engine emitter.
- §3.7.3 ("pcrec ORs the kit's per-kind consulted into the stamp") and
  `measure_sets.md` §4.2 ("pcrec ORs `consulted` with its own readers'
  lookups") both assume a render point that does not exist. Under §6.4 rule 2
  the kit becomes the last reader, so both stamp lines and both `rx_info`
  initializers must move to the art-end mark pass, the mechanism the kit's own
  three stamps already use. Neither sibling design states this. It is also the
  natural single call site for `ks_stamp`.

**Fix.** State in §3.7.3 and §3.7.9 (B3b's obligations) that the `_FINDINGS`
line and `.findings =` render at the `pcrec_memfn_stamps_render` mark, after
`mf_art_end`, and that `_MEASURES` (M0) does the same. Add a check that the
move alone is zero-byte: emit_sweep, with the move landed before any kit
consulted is ORed. Add a sabotage row that renders the stamp before
`mf_art_end` with a kit-only consult present. Relay the same point to
`measure_sets.md`'s next revision, beside F-4.

### M4. C-CONS (and S990) repeat the K35 vacuity §3.7.4 found for G1-E1

**Evidence.** C-CONS compares "`consulted` per kind and `_FINDINGS`" between
SIMD-off and SIMD-on over "emit_sweep's `-fmemfn-simd` arm". At default flags
every artifact already stamps `byte-rate=…` from pcrec's own `req.c` ask
(§3.7.4: 0 `""` in all three default arms). So the OR masks any SIMD-only kit
consult, and `_FINDINGS` cannot differ at default flags. That is the argument
§3.7.4 makes for G1-E1, not applied here. The table also does not say how
"`consulted` per kind" is observed. No trace record or listing is named, so
the stamp half is the only named instrument, and it is blind.

**Fix.** Read `consulted` from a named trace record (C-E1-1's `KSRCTRACE` line
gaining a `consulted` field, or the kit's decision listing), compared
directly. Run the stamp half on a deny arm where `""` exists, crossed with
`-fmemfn-simd`. Add a floor: at least one artifact where the kit is the only
consumer.

### M5. The offer is built at a LAZY, first-caller-wins point; under OFFERED that point can fall after the stamp, so §3.7.5 is not "buildable with no further design"

**Evidence.** `pcrec_memfn_art` (`memfn_sites.c:66-79`) creates the art on the
first kit call: a site's `define`/`emit`, the prologue flush, or the art-end
stamps pass. §3.7.1 puts the build inside it. Under CONSULTED the timing only
moves where B1's refusal fires, which is mid-emission, possibly inside a site
render. Under OFFERED, the stamp reads `asked` in `emit_info_def`. On the VM
route the epilogue (`vm_emit_epilogue` → `pcrec_emit_info`, `emit_vm.c:13976`)
is called within `pcrec_emit_vm`, whose prologue flush is at `:14088`. An
artifact with no kit site before the epilogue would build the object only at
the art-end pass, after its stamp was written, and would stamp `""` under
OFFERED.

**Fix.** Build the object eagerly at one stated point: the attempt start in
`compile_driver`, right after the chain resolves, stored on `Job`. Then
`pcrec_memfn_art` only passes it, and the build point does not depend on which
kit call comes first. State that point in §3.7.1, and in §3.7.5 if OFFERED is
ruled.

---

## MINOR

### m1. `find_kinds[]` should BE the query vocabulary's home, not a fifth spelling checked by count, and its name collides with [KNOW-SRC]'s `ksrc_kinds[]`

**Evidence.** `find_derivs[]` (`findings.c:185-190`) is per (kind, via): it
lists `byte-rate` three times. A `_Static_assert`-shaped count of its distinct
third column is not a compile-time constant, so the check is runtime-only.
`find_kinds[]` is the first per-QUERY table. That is exactly what F-3's four
spellings lack. Separately, [KNOW-SRC] §9.2 has `ksrc_kinds[]` (knowledge
SOURCES: analysis, measures, lib). Two "kinds" tables one tier apart, both in
`src/core`, invite the wrong join.

**Fix.** Make `find_derivs[]`'s third column reference `find_kinds[]` rows (an
index or a pointer). Have `rxt_find.c:326`, `findings_dump.c:39` and
`rxt_source.c:617` read it. That retires F-3 instead of filing it. Rename it
`find_queries[]`. The `mf_analysis.kinds` / `mf_akind` spelling is the kit's to
finalize, but the pcrec-side name should not echo `KsKind`.

### m2. C-E1-4 shares a source with what it checks, and §3.7.7's header says none does

**Evidence.** C-E1-4 is "two derivations of one record, read through two
outputs". The stamp and the object both come from `find_derive_byte_rate`'s
memo, so a wrong memo agrees with itself (learnings §3). The table header
claims "each against a source the subject does not share". C-E1-3 labels its
own shared-source line honestly. C-E1-4 does not.

**Fix.** Label C-E1-4 as an AGREEMENT check (shared source). Name C-E1-1's
python digest as the independent line it leans on. Make S988's plant site
explicit: it is detectable only if the offer computes its digest itself,
instead of copying `fr->byte_rate_digest`.

### m3. G1-E1 omits the one arm where every VM artifact stamps `""`

**Evidence.** §3.7.4 measures `--engine=vm -fno-req-byte -fno-req-run` at
5,337/5,337 `""`. G1-E1 requires `--engine=vm` (0 `""`) and the two
`-fno-req-byte` arms, but not the VM deny arm. The VM's info block is emitted
on a different path from the DFA's (`emit_vm.c:13976`). The `-fno-req-byte`
floor (≥ 1,900) does not show how many of those are VM-engine artifacts.

**Fix.** Add the VM deny arm to G1-E1's required list, or split the floor by
`RX_ENGINE`.

### m4. F-2 is not reachable through the listing it names

**Evidence.** F-2 says `req_rate_why` writes `rate:builtin-prior` "with
`--analysis weblog` included" and calls re-sourcing it a "caller-visible
`--emit-facts` change". On main, `pcrec -p rx --analysis weblog --emit-facts
--pattern abc` is refused: "--analysis applies to a compile (a file operand or
--pattern) or to --list-analysis FILE only". The finding is latent: the token
is wrong in the record, but the CLI cannot list it.

**Fix.** Re-state F-2 as latent. Its trigger should be "the first path that
lists facts under a non-default analysis", rather than [IFACE-PUSH] alone.

### m5. D157: rule 7 names kit rows and their outcome

**Evidence.** §3.3 rule 7 says "This covers a priced pre-scan, D162 add. 1's
density decline, and r17b′'s F0, R5, R6, R8 and P1 … the pre-scan's default is
KEEP." That lists kit row ids and a kit row's chosen default inside pcrec's
contract. The FACT pcrec owes is only the provenance tag. Which rows read it as
evidence, and what they then pick, is the kit's method. §3.5's memo placement
and its "move it per compile" trigger are borderline in the same way, though
D162 add. 4 ruled the memo.

**Fix.** Keep rule 7 as "a reader of a kind as EVIDENCE reads only `measured`".
Move the row list and the KEEP default into a pointer to r17b′, the kit's
document.

### m6. The kind's state under `have ∧ ¬asked` is new; one comment and one invariant need saying

**Evidence.** After E-1, `byte_rate_have` (`findings.h:99`, "... and a block
answered") can be true with `byte_rate_asked` false. The comment's "..." reads
as "asked, and". `req_rate_why` (`req.c:653`) reads `have` directly. It is safe
today only because both callers ask first, which §3.7.6 argues and nothing
checks.

**Fix.** Re-word the record comment. Either route `req_rate_why` through
`pcrec_find_byte_rate`'s return value, or add a structural check
(`tests/findings/structural_check.py` already polices the gate) that `have`
has no reader outside `findings.c`.

---

## On the brief's five questions

1. **Zero-mover.** The stamp holds in every arm I can find: default, `-e utf8`,
   `--engine=vm`, `-fcomments` (`^abc -fno-req-byte -fcomments` still stamps
   `""`), and `--emit-facts`, which reads the record after the artifact and
   does not re-derive (facts_listing 5¶2). The refusal set does not hold (B1).
   The G1-E1 populations reach the deny arms' `""` artifacts, but not the
   analysis axis (B1) and not the VM deny arm (m3).
2. **Per-art vs per-site.** All five reasons hold. I found no kit reader that
   needs per-site. Every kit entry (`mf_define`/`use`/`call`/`emit`) takes the
   art. Compound parts get one art each with equal content, which C-E1-4
   covers. Caveat: "cannot disagree" is true per art, not per artifact. A
   compound artifact carries several arts, so equality across them is a check
   (C-E1-4), not a structural fact.
3. **`arrives`.** As data it passes the general-mechanism rule: no predicate
   names a kind. Its reach is wrong (M1). The column is arguably derivable:
   D162 add. 2's refinement, "a derived fact pcrec also uses is sent ALWAYS",
   puts `ALWAYS` exactly on the kinds pcrec itself reads. Keep the column, cite
   that rule in its header, and add a structural check that `ALWAYS` rows are
   exactly the kinds with a pcrec reader.
4. **Independence.** C-E1-1 and C-E1-2 are independent. C-E1-3 is honest about
   its shared line. C-E1-4 shares its source (m2). C-CONS is blind on its
   population (M4).
5. **D157.** m5. The `mf_prov`/`mf_akind` fields themselves are facts.

## Standing lenses

- **SIBLING-OF-A-FAMILY ([KNOW-SRC]).** §3.7.3's CONSULTED unification is right
  and well argued. The family has two more shared obligations that neither
  document states: the render point after `mf_art_end` (M3) and layer
  invariance (F-4, already filed). The `consulted` grain differs: one bool per
  set against one bit per kind. That is defensible, because the stamp item
  grain matches. But see U1.
- **NEW-DATASET.** `find_kinds[]` has a home (`findings.c`) but should absorb
  the vocabulary (m1). `mf_prov.source`'s fact already lives in each block's
  `provenance` stanza (M2). The evidence-strength fact already lives in
  `provenance bytes` (M2). No other new table.
- **UNLOCKS, with triggers:**
  - **U1, one kit out-channel for the family.** A single `mf_art_end` record of
    `consulted` keyed by (knowledge source, item), so `ks_stamp` reads one
    shape for analysis and measures. Trigger: the second kit output landing
    (B3b's per-kind bits, beside R-MS2), whichever of B3b/M0 is second.
  - **U2, content-sourced provenance.** Once blocks carry their stanza (M2), the
    `fidelity` and `bytes` facts reach the kit with no new layout event, and
    `--list-analysis` can show the kit's evidence basis per kind. Trigger: B3a,
    the first ported row reading `measured`.
  - **U3, one stamp render point.** Moving `_FINDINGS`/`_MEASURES` to the
    art-end mark (M3) gives `ks_stamp` one call site and lets a future
    consumed-subset digest (`measure_sets.md` §10.4) be computed after every
    reader. Trigger: B3b or M0, whichever lands first.
  - **U4, an eager per-attempt object on `Job`** (M5). The same value can feed
    pcrec's own readers through one accessor and retire the `byte_rate_*`
    record fields into the object. Trigger: [KNOW-SRC] K-steps migrating the
    loader (§3.7.10).

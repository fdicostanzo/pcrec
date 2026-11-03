# Lens `readers` — slot tracing and ruling check, memfn-sp1g (BASE c0f0d543b .. SUBJECT efd724b4b)

Disclosures:
- COMPILE CAP EXCEEDED: 224 single compiles against a cap of 200. A first 80-compile batch was invalid (it wrote different `-o` names, so the `#include "<name>.h"` line differed) and was re-run as 144 compiles. No other process was touched.
- DENYLIST: my diff over `memfn/` did not exclude `memfn/docs/journal.md`, so I saw its 2026-11-03 sp1g hunk (5 bullets). Nothing below relies on it. Every claim is checked against code at SUBJECT.

Verdict in one line: the code diff does exactly what span_pick rev 5.2's 1g row and its READER-LIST row say. Every reader the design named is handled. No emitted byte or `KSRCTRACE object` record moves (144 compiles). MISSED readers are all prose: window_contract §3.6/§3.7.1/§13, memfn.h's second "before B3a" clause, the invariant comment in memfn_sites.c, and kit comments naming `PRIOR_NONE`. Two check gaps: the L(4) family has no matrix plant, and the kept digest's write has no witness.

## Findings

### READERS-1 — window_contract.md: three sections still say `mf_prov.bytes`/`fidelity` and the `MF_PROV_*`/`MF_FID_*` mapping are BUILT, with no revision mark (MISSED readers)
- CONFIRMED (grep at SUBJECT: `git show efd724b4b:docs/design/memfn/window_contract.md | grep -n 'mf_prov\|MF_FID_\|MF_PROV_'`):
  - §3.6 :772-778 "Evidence strength ... BUILT ... So `mf_prov.bytes` (and `fidelity`) are in the layout from its first declaration".
  - §3.7.1 :798, the object-builder row: "The mapping `PcrecFind*` -> `MF_PROV_*`/`MF_KIND_*`/`MF_FID_*` stays in `memfn_sites.c`".
  - §13 :2035 "~~The EVIDENCE-STRENGTH fact~~ BUILT (`mf_prov.bytes`, `fidelity`, §3.1)".
  - Also §3.1's paragraph after the code block, :585-589 ("`bytes` and `fidelity` are in the layout from its first declaration"), and :598-599 ("no kit row reads it before B3a"). The new revision line covers only "the block below and the invariant's `prov.source` wording", so these are covered at best ambiguously.
  - The 1g reader row (span_pick.md :373) named only "§3.1/§3.2 (a revision line)". The design's own grep pattern hits these lines, so they are readers the design's list did not name. The lane added revision lines to §3.1 and §3.2 only.
- Observed: present-tense claims that are false at SUBJECT. Expected: a `[span_pick 1g]` mark on each, or §3.1's revision line widened to name §3.6, §3.7.1 and §13. §3.6/§13's "EVIDENCE-STRENGTH: BUILT" now means the kit cannot see evidence strength. That fact has a successor in span_pick ("stage 2's stated sampling noise", the `mf_prov` row at :418), and a reader of window_contract would not find it.
- Severity: doc. Effort: 4 one-line marks. Blast radius: design readers of window_contract (the next E-1/stage-2 author).
- §8.2 :1701 (the "`mf_analysis`/`mf_akind`/`mf_prov` layout changes -> MF_SITE_ABI" event row) is a rule, not a claim, so it is correctly left. The review-disposition rows :59, :114, :119 are history, so they are correctly left too.

### READERS-2 — memfn.h:1289-1290 keeps the stale "read by no kit row before B3a" that the 1g reader row asked to remove (MISSED second site)
- CONFIRMED: `git show efd724b4b:memfn/include/memfn.h | sed -n 1284,1291p` shows `mf_art_begin`'s comment: "`an` its analysis object (DECLARED, E-1; NULL-tolerant, read by no kit row before B3a)".
- The design (span_pick :373) lists "memfn.h :1205-1238 (its stale "NO kit row reads it before B3a" too)". The lane fixed the block comment at :1229-1234 but not the same clause in the prototype's comment. It is false: `kit_byte_rate` (presence.c :48-55) reads `an` on every art, and the window family reads it through it.
- The same clause also survives at memfn/src/kit.h :287 ("DECLARED, E-1: read by no row before B3a"), which nobody named, and at compose.c :882, which is 1d's per the design (correctly left for 1d).
- Severity: doc. Effort: one clause in memfn.h (plus kit.h:287 if taken here). Blast radius: kit header readers.

### READERS-3 — memfn_sites.c: the invariant comment and its refusal text still call it "the object's invariant", but the check reads pcrec's offer; the object's new "digest 0 without a payload" is checked nowhere
- CONFIRMED by reading SUBJECT `src/gen/memfn_sites.c` :189-212:
  - The comment says "The object's invariant (window_contract.md §3.1), checked as it is built: ... PRIOR_NONE states no bundle, digest or bytes; an ABSENT kind states no source".
  - The refusal says "the analysis object's '%s' kind ... breaks its invariant".
  - The function takes `const PcrecFindOffer *o`, and every clause tests offer fields (`source`, `bundle`, `bytes`) that the object no longer has.
  - window_contract's own new revision line (:538-540) already says the right thing: "the invariant itself is checked on pcrec's offer, before the object is built". The code comment above `pcrec_memfn_analysis_build` was not restated to match. The brief asked about exactly this comment.
- Second half (contract): memfn.h's new member comment for `digest` says "0 without a payload". `analysis_invariant` enforces digest 0 only under PRIOR_NONE. An ABSENT or UNSTATED-source offer with a nonzero digest passes and reaches `mf_akind.digest`. It is true in practice (both ABSENT `run-rarity` records in the probe show digest 0) but unchecked. The old header promised only "0 under PRIOR_NONE", which the check matched.
- Fix: "the OFFER's invariant (the object is built from it)". One extra clause `(o->payload == NULL) != (o->digest == 0)` would make the header's sentence a checked fact. It moves no byte.
- Severity: doc + contract (small). Effort: 3 lines. Blast radius: pcrec internal; a future wiring bug would surface only as a wrong kit trace.

### READERS-4 — kit comments still use the source word `PRIOR_NONE` that the kit no longer receives (MISSED: the design's grep pattern cannot see a bare `PRIOR_NONE`)
- CONFIRMED:
  - memfn/src/kit.h :322-324: "or NULL where it carries none (no object, the kind absent, PRIOR_NONE)".
  - memfn/src/presence.c :45-47: "or present with no table: PRIOR_NONE".
- At SUBJECT `PRIOR_NONE` is pcrec's offer vocabulary only (`PCREC_FIND_SRC_PRIOR_NONE`). The kit's spelling `MF_PROV_PRIOR_NONE` is deleted, and D186 add. 2 says "the kit never sees the source". The kit state is "PRESENT with a NULL payload".
- The design's pattern `MF_PROV_\|MF_FID_\|mf_prov\|...` misses these two. They are the only kit-side uses of the deleted vocabulary that remain.
- Severity: doc. Effort: 2 words. Blast radius: kit readers (D157 hygiene: the kit's text should not name pcrec's source states).

### READERS-5 — finder_check L lost its only matrix plant (S1092) and the re-aimed L(4) has none; the memfnfinder arm no longer guards family L
- CONFIRMED by reading SUBJECT `tests/mech/run_sabotage_matrix.sh` :518-523: "L's re-aimed part (4) ... was planted by hand in the lane ...; a matrix row for it waits for an S-id from the kit's range". `git ls-tree --name-only efd724b4b tests/mech/sabotages/ | grep -iE 'digest|akind|prov'` lists S996, S986, S1227 and S309, which plant pcrec-side digests, and S1030, S992 and S240, which plant pcrec's provenance. None plants a kit read of `mf_akind.digest`.
- The design's 1g row (:373) asks for "its plant a kit row reading `mf_akind.digest` (holds iff the digest is odd), red". A hand plant meets the letter of that. Against the house rule (learnings §3 / [MECH-REACH]: a witness must keep reaching its site), L(4b)'s render loop now has no standing plant. If AN_DIGESTS were edited to even values only, or the `--fd-an` plumbing stopped reaching `fd_render` (for example `fd_site_mode` short-circuiting before render), nothing would turn red.
- L(4a) (the header regex) has no plant either: the regex needs `typedef struct { ... } mf_akind;` exactly. If the header were rewritten as `typedef struct mf_akind {...} mf_akind;`, L(4a) turns red through its "declares no ..." branch, which is safe. So 4a's failure mode is loud and only 4b matters.
- The memfnfinder description at :488-495 still says "the pay rule's arithmetic grid". That is stale from 1f, not 1g, and noted only.
- Status: SUSPECTED as a gap; it is CONFIRMED that the plant is unregistered. What would settle it: main assigning the S-id now (the kit's range) and the plant file landing with 1g rather than later.
- Severity: maintenance (check design). Effort: one sabotage file (the lane already has the plant text). Blast radius: the one family that guards "the kit never reads the digest" until row 1.

### READERS-6 — the one field 1g KEEPS (`mf_akind.digest`) has no witness of its write; a plant `k[i].digest = 0` passes every check
- CONFIRMED by grep at SUBJECT:
  - pcrec's only writer is memfn_sites.c :265 `k[i].digest = o.digest;`.
  - The trace prints `o->digest`, the offer (memfn_sites.c :238). Before 1g, BYTES/FIDELITY were read from the built object to witness the wiring (BASE comment: "holds the wiring itself"). After 1g no column reads the object.
  - finder_check L(4b) asserts that the kit is INVARIANT to the digest. prov_check.c pins only the offset.
  - No reader of `mf_akind.digest` exists in memfn/src, tests/ or scripts/ (grep `\.digest|->digest` over memfn/src returns nothing).
- So zeroing, or writing the bundle's digest under the wrong kind, is green everywhere. Today that is harmless (no reader). The design's reason for keeping the field is that "the kit's trace names it from row 1" (span_pick :360), and at row 1 the first reader would inherit an unwitnessed write.
- Cheap fix that moves no byte: print the DIGEST column from `k->digest` (pass `&k[i]` back into `analysis_trace`). The record stays byte-identical, because the two values are equal today, and e1_object_check C-E1-1's independent python digest then holds the object's field. The cost is that the record mixes one object column into an offer record. State that in the header premise, or use the STATE column (`akind_state_map`, which is also unwitnessed) the same way.
- Severity: design/check (latent). Effort: 3 lines. Trigger if deferred: the first kit trace or row that reads `mf_akind.digest` (stage 3 row 1).

## PROBED-AND-HELD

- **Byte identity and the trace record.** I compared the base trace build against the SUBJECT trace build. `--emit-main -p rx`, same `-o` name in separate dirs. 2 encodings (byte, utf8) x 6 analysis chains (none, log, weblog, default, log+weblog, default+log) x 6 patterns (`a(b|c)+d`, `(?i)x/1234`, `foo.*bar`, `[a-z]+@[a-z]+\.com`, `zzzzzzz~J`, `^abc$`) = 72 pairs, 144 compiles. The emitted C, the ENTIRE stderr (every KSTRACE line) and the 144 `KSRCTRACE object` lines are byte-identical: 0 diffs. Records cover PRIOR_AUTHORED with `synthesized` fidelity (log), MEASURED (weblog, bytes 1000000), PRIOR_NONE and ABSENT.
- **The trace's new reads.** `o->bytes` is `unsigned long long`, matching `%llu`. `o->fidelity ? o->fidelity : "-"` matches the old reverse lookup (`prov_fidelity_token`) for every token in the closed set plus NULL. The old out-of-vocabulary refusal is gone, as the design says ("the schema's `closed fidelity` row already holds it").
- **Reader table** (grep at SUBJECT over src/ memfn/ tests/ scripts/ docs/spec docs/design docs/guide studies analyze cli lib, excluding denied paths), for `mf_prov`, `.prov.`, `->prov`, `mf_prov_source`, `mf_prov_fidelity`, `MF_PROV_*`, `MF_FID_*`, `pcrec_memfn_prov_stanza`, `prov_fidelity_rows`, `prov_fidelity_token`, `akind_source_map`, `--provchk`, `provchk`, `--fd-an` and `S1092`:
  - memfn.h struct and enums: HANDLED (deleted). The ABI history at :105-110 is correctly left (history, design C4). The new 22 entry is present.
  - memfn/include/CLAUDE.md, memfn/CLAUDE.md :38, tests/memfn/CLAUDE.md :82: HANDLED.
  - memfn_sites.c (`akind_source_map`, the writes, `prov_fidelity_rows`/`token`, `pcrec_memfn_prov_stanza`, the trace) and memfn_sites.h prototype: HANDLED.
  - prov_check.c (reduced, now includes only memfn.h) and run_finder.sh (:37-41 build, :67 argument): HANDLED. `$WORK/provchk` is still produced, unused, harmless.
  - finder_check.py (docstring, L, `--provchk` argument, `prov_run`, `schema_fidelity_tokens`, `check_prov` call): HANDLED.
  - arm_fixtures.c (:1265 usage, `fd_an_make`, `--fd-an DIGEST`, main's usage line): HANDLED. g2_win_gen.c :625 and :828: HANDLED.
  - S1092 file deleted and the matrix note added: HANDLED. Its line at :503 is correctly left (history).
  - window_contract §3.1/§3.2: HANDLED (revision lines). §3.6/§3.7.1/§13: MISSED (READERS-1).
  - e1_object_check.py header and tests/findings/CLAUDE.md: HANDLED. The check descriptions (C-E1-1..5) read true against the offer. C-E1-4 still says "against its final attempt's object", which is acceptable under the new PREMISE paragraph.
  - docs/design/ctx_span/{call_graph*.txt, sabotage_anchors*.tsv} and docs/design/measure_sets/k{2,3}_anchors.tsv name the deleted functions and S1092. These are frozen census snapshots: no script, test or Makefile reads them (grep), and 1f left S1025 there the same way. Correctly left (history).
  - memfn/docs/requests.md R-24 and docs/dev/full_suite_ledger.md: history, correctly left.
  - span_pick.md and decisions.md: the design and the ruling themselves.
  - `scripts/ksgen.c`, `findings.c`/`.h`, `rxt_find.c`, `rxt_source.c`, `findings_probe.c`, S1030 and S992 name pcrec's own `prov_fidelity` (the block field). They are not seam readers and are correctly untouched.
  - docs/spec and docs/guide: no hits (the design said "no docs/spec names them"; that holds, and D80 owes nothing).
- **MF_SITE_ABI 21->22 readers.** By grep, every code reader uses the symbol: compose.c :960/:1016, formhash.c, presence.c, window.c, every g2 generator (±1 relative). There is no numeric pin in tests, scripts or the stamp: MF_SITE_ABI reaches no emitted text (src/gen has no MF_SITE_ABI hit). The number 22 appears in memfn.h :39, memfn/include/CLAUDE.md, and the 1g comments in the tests. The 21 at memfn.h :1076/:1510 is history. memfn/docs/wake.md is the kit's session doc and is not a reader. MF_VOCAB and MF_CLASS_V are unchanged in the diff, so there is no pcrec abi move.
- **No more, no less.** The 16 changed files (outside lanes and history) are exactly the 1g row's list plus the CLAUDE.md files it names. No unrelated hunk. Nothing on the list is undone. The plant is by hand (see READERS-5).
- **D186 add. 2 at the freeze.** "pcrec's stamp and trace name the source and its digest; the kit's trace names only the digest it was handed; the provenance fields ... leave the seam ... the kit never sees the source": HELD. The kit has no source vocabulary left in code (only the comments in READERS-4).
  - "the kit's trace names the digest" (span_pick :360 "from row 1"; memfn.h :1240 "the kit's trace names only the digest it was handed"): at SUBJECT no kit trace names the digest at all. memfn/src has no `.digest` read, and L(4b) asserts exactly that. The header sentence is an upper bound ("only") and is vacuously true, so I hold it, but it reads like a present fact. It becomes true at row 1 (READERS-6's trigger).
- **D157.** The kit now receives facts only (rates and digest). HELD.
- **D94/D76.** This is an MF_SITE_ABI event only. No pcrec abi reader moves, because no emitted byte or stamp moves (probe above).
- **The design's Goals, in rank order:**
  1. Answers exact: no answer path changed (the kit never read the deleted fields; the probe shows identical bytes). SERVED.
  2. No regime slower: 0 movers. SERVED.
  3. One table per question: two pcrec-side mapping tables (`akind_source_map`, `prov_fidelity_rows`) and a refusal leave, and the source is resolved in pcrec's one first-match table. SERVED.
  4. Costs measured: indirectly. Evidence strength leaves the seam, and the band's sampling term becomes noise pcrec states at stage 2, so no hand-set evidence weighting can grow in the kit. SERVED (enabling).
  5. Blind picks are the default's: the kit can no longer distinguish default from measured rates, so "no bundle moves a blind pick" holds by construction at the seam. SERVED.
  The unit puts no lower goal ahead of a higher one.

## Standing questions

**(1) Sibling of a family.** Yes, at least the third member in both families.

- *Seam fields carrying facts the kit never reads.* By grep, `kit_byte_rate` (presence.c :48-55) is the kit's ONLY reader of the analysis object, and it reads `nkinds`, `kinds[i].tag`, `.present` and `.payload`. Never read:
  - `mf_akind.digest` (memfn.h ~:1245). Kept by ruling, unread, and its write unwitnessed (READERS-6).
  - `mf_akind.version` (memfn.h ~:1243). The kit casts `payload` to `uint32_t[256]` without checking `version == 1`. window_contract §8.2 :1700 says a payload-shape change moves only "its own `version`", not MF_SITE_ABI. So a version-2 byte-rate would be silently misread: a latent contract hole, not just an unread fact.
  - `mf_analysis.list_v` (memfn.h ~:1250). Never checked by the kit.
  - Earlier members already removed: `mf_prov.source`/`bundle`/`bytes`/`fidelity` (this unit), and the W0-W2/prefix/absent/consumable/ctx fields (MF_SITE_ABI 20, memfn.h's history). `mf_site.count_by_caller` and the `consulted` mirror asks (span_pick :446-450, memfn_stamps.c :385) are the out-channel twin: facts pcrec mirrors because the kit does not report reads.
- *A check that reads the offer, not the object.*
  - e1_object_check.py now reads the offer (this unit).
  - C-E1-4 already declares its SHARED SOURCE: the stamp and the object both read the findings memo (e1_object_check.py :38-41).
  - The [K113] part path, memfn_sites.c :253-256: parts reuse the walk's object, so they emit no record and have no check of their own.
  - The PRES ports are checked against the host's own picks (memfn.h :1548-1556, the KW-8 census, both reading the same handed table).
  Three or more members, so I propose unification: one rule, "a seam check reads the FIELD THE KIT RECEIVES, on at least one column", applied by making each trace record carry at least one object-side column. READERS-6's digest column is the first instance.

**(2) The general form and what it unlocks.**

1g is one instance of a general form: *the seam carries exactly the facts the kit's rows read, plus the declared identity of what was handed (a digest), and every other attribute stays in the caller's stamp and trace* (D157 tightened by D186 add. 2). That means each seam field has a declared reader, or a declared trigger at which it gains one.

What it unlocks, each with a trigger:
- (a) A **seam reader census**: a check that every `mf_*` struct member in memfn.h has a kit `.c` reader or is listed with its trigger. It would have caught `version`/`list_v` and would make the next 1g mechanical. *Trigger:* the next MF_SITE_ABI layout event, or the first time a field is added "for later" (D77).
- (b) **Version-checked payloads**: `kit_byte_rate` refuses or ignores a kind whose `version` it does not know. It closes the §8.2 hole above. *Trigger:* the first second payload shape for any kind (`run-rarity` gaining a payload, or a cpfreq-shaped rate).
- (c) A **digest-keyed kit memo**: window_contract §3.5's per-compile memo, "keyed by the `byte-rate` digest in kit state passed to `mf_art_begin`". With source gone, the digest is the whole identity of the handed table, so the memo key is now complete. *Trigger:* §3.5's own one, a measured memo-build cost above the noise of a minimal compile.
- (d) **Stated sampling noise** replacing `bytes`/`fidelity`: the band's noise term as a pcrec-stated fact, not an evidence-strength proxy. *Trigger:* stage 2 (the noise channel, span_pick §Staging).
- (e) **The kit trace naming the digest**: it makes "the kit's trace names only the digest" true rather than vacuous, and READERS-6's witness becomes mandatory. *Trigger:* stage 3 row 1.

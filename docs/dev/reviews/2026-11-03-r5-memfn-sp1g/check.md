# CHECK lens: memfn-sp1g (check adequacy, learnings §3)

Subject efd724b4b (lane/memfn-sp1g), base c0f0d543b. Read-only. Scratch tree:
`git archive SUBJECT` under check/tree, review tree's build/pcrec and
build/libpcrec.a copied in. Plants run by check/plant.sh: patch one file,
rebuild the fixture drivers exactly as run_finder.sh does (fx against
libpcrec.a, fxt from every memfn/src/*.c with -DMF_TRACE, provchk -Werror),
run `python3 -I tests/memfn/finder_check.py --root TREE --fx --fxt --tmp`,
restore. Unplanted control (check/w0): `checks passed: 923, checks failed: 0`.
One run_finder.sh run (run0.log; red only because the copied tree lacked
build/pcrec at that moment: environment, not the subject). About 170 single
compiles. Plant diffs and logs: check/plants/pN/{plant.diff,check.log}.

Axes note: a kit-source plant reaches only the TRACED driver here (the plain
one links the pre-built libpcrec.a). Under `make test` both axes carry it. No
verdict below depends on this.

## Findings

### CHECK-1 CONFIRMED: L's render loop never reaches a kit reader of the analysis object; a digest reader where the object IS read stays green
- Severity: contract (check adequacy). Effort: small. Blast radius: tests/memfn/finder_check.py L (4b).
- Where: finder_check.py `check_prov`, `for site in ("set10", "byte1t")` (~:658).
- Facts: the kit reads `mf_analysis` in one place, `kit_byte_rate`
  (memfn/src/presence.c :48); callers `kit_pres_picks` (presence.c :155,
  ALL_PRESENT sites) and window.c `decide` (:991). set10 and byte1t are FIND
  sites that never call it: on the unplanted fxt both render byte-identically
  (stdout+stderr) with NO analysis object and with `--fd-an 0`. L(4b) holds
  the digest fixed over sites where nothing reads the object: reach zero.
  pre-lead and pre-lead-run DO move with the object (no-analysis vs
  `--fd-an 0`: rc 0/1 and 1/0, stdout and stderr DIFF).
- Plant P4 (presence.c kit_pres_picks):
  `+ if (art->an && art->an->nkinds && (art->an->kinds[0].digest & 1)) return;  /* PLANT P4 */`
  L verdict: `checks passed: 923` / `checks failed: 0`, rc=0 (GREEN).
  Real defect: `fxt --fd-site pre-opt --fd-an 0` vs `--fd-an 1`: rc 0/1,
  stdout DIFF; pre-lead-run rc 0/1, DIFF.
- Plant P5 (presence.c kit_byte_rate, shared by presence and window):
  `- return an->kinds[i].present == MF_KIND_PRESENT`
  `+ return an->kinds[i].present == MF_KIND_PRESENT && !(an->kinds[i].digest & 1)   /* PLANT P5 */`
  L verdict: 923 / 0, rc=0 (GREEN). Real defect: pre-lead `--fd-an 0` vs `1`
  rc 1/0 DIFF; pre-lead-run rc 0/1 DIFF.
- The design's own plant ([rev5.2 C8], "a kit row reading digest, holds iff
  odd") reds only when placed in a FIND row byte1t reaches (P1, HELD below);
  the same reader where the object is consumed is invisible. The witness site
  was chosen beside the check, not beside the reader.
- Fix: add the rate-sensitive sites (pre-lead-run, pre-lead; a window site
  when the fixture has one) with a per-site REACH control: the
  `--fd-an AN_DIGESTS[0]` render must DIFFER from the no-analysis render,
  floor >= 1 such site. Cheap static complement: no memfn/src file names
  `digest` today (grep: 0 hits), so "no kit source names `digest`" catches
  P1-P5 regardless of reach (re-aim it when row 1's trace names the digest).

### CHECK-2 CONFIRMED: L(4a) is a denylist of four exact names on one struct; provenance re-enters under another name or at the list level, read by a kit row, and L stays green
- Severity: contract (check adequacy). Effort: small. Blast radius: finder_check.py L (4a); the memfn.h seam.
- Where: finder_check.py `PROV_FIELDS = ("source","bundle","bytes","fidelity")`,
  `KIT_READERS_RE = mf_prov|MF_PROV_|MF_FID_`, mf_akind only.
- Plant P6 (two files): memfn.h mf_akind, appended after payload (so
  prov_check's offsetof(digest)==16 still holds):
  `+ uint64_t    nbytes;     /* PLANT P6: bytes back under another name (0 = the default) */`
  finder.c fd_holds:
  `+ if (!strcmp(r->id, "D1") && q->art->an && q->art->an->nkinds && q->art->an->kinds[0].nbytes == 0) return 0;`
  (the "tell the default from a bundle" read D186 add. 2 removed the fields to prevent).
  L verdict: 923 / 0, rc=0 (GREEN); prov_check builds. Real defect: byte1t
  ROUTED D1 with no analysis, D1w under `--fd-an 0` and `--fd-an 1`.
- Plant P7: memfn.h mf_analysis `+ const char *bundle;` (a struct L(4a) never
  parses); fd_holds `+ if (!strcmp(r->id, "D1") && q->art->an && !q->art->an->bundle) return 0;`
  L verdict: 923 / 0 (GREEN). Same move D1 -> D1w under any analysis.
- L(4b) misses both too: its reference is now an analysis object (`--fd-an 0`),
  not BASE's no-analysis render, and the fixture never writes the new field.
  BASE's comparison against no object would have caught P6/P7 on byte1t.
- Fix: an ALLOWLIST: mf_akind's members EQUAL {tag, version, present, digest,
  payload} and mf_analysis's EQUAL {list_v, nkinds, kinds}; a new member is a
  seam event that must edit the check. Keep the no-analysis render as a
  second reference on sites that do not consult rates (set10/byte1t), exact today.

### CHECK-3 CONFIRMED (by construction): nothing witnesses pcrec's object builder any more; the record reads no object field
- Severity: maintenance (no reader today; material at row 1). Effort: trivial. Blast radius: src/gen/memfn_sites.c analysis_trace, tests/findings/e1_object_check.py.
- At BASE the record already read state, source, bundle and DIGEST from the
  offer `o`; only BYTES and FIDELITY came from the built object
  (`k->prov.bytes`, `k->prov.fidelity`): the only object witnesses, gone with
  the fields. At SUBJECT `analysis_trace(q, &o)` takes no mf_akind, so
  `k[i].digest = 0;` (or the other kind's digest) in
  pcrec_memfn_analysis_build moves no record, no artifact (no kit reader,
  CHECK-1 grep) and not L (L builds its object in arm_fixtures, never via
  pcrec). Not run (a libpcrec rebuild is outside this lens's cap); the
  argument is the function signature.
- The digest is the one provenance fact the seam keeps, and the design has
  the kit's trace name it from row 1 (span_pick :60, :360): its first reader
  arrives with no wiring witness behind it.
- e1_object_check now holds pcrec's OFFER to its hand table (C-E1-1 with an
  independent python digest: sound for the offer) but checks no OBJECT field,
  while its docstring still opens "the ANALYSIS OBJECT's checks" / "a source
  the object does not share". The new premise does not create a shared source
  (C-E1-4 was already flagged as one); it removes the object from scope.
- Fix (records stay byte-identical): pass `&k[i]` and print DIGEST from
  `k->digest` (STATE from `k->present` via a reverse name table), after the
  fields are set; C-E1-1's python digest then witnesses the object's digest
  per kind. Restate e1's docstring opening accordingly.

### CHECK-4 CONFIRMED: L(4b)'s digest list is a finite witness; a reader keyed on one value is green
- Severity: contract (minor; subsumed by CHECK-1's static scan). Effort: none beyond CHECK-1.
- Plant P3 (fd_holds): `+ if (!strcmp(r->id, "D1") && q->art->an && q->art->an->nkinds && q->art->an->kinds[0].digest == 0x5eedULL) return 0;`
  L verdict: 923 / 0 (GREEN). Real defect: byte1t `--fd-an 0` vs `0x5eed`: stdout and stderr DIFF.
- Realistic form: comparing to the DEFAULT table's digest (telling the default
  from a bundle by value). No dynamic list covers it; the static scan does.

### CHECK-5 CONFIRMED: S1092 retired with no matrix successor; L(4)'s plant exists only as a hand run
- Severity: maintenance. Effort: small (one S-id). Blast radius: tests/mech/run_sabotage_matrix.sh :518-523.
- S1092 planted `p->fidelity = MF_FID_UNSTATED` in pcrec_memfn_prov_stanza (a
  block's fidelity token reaching the kit as "declares none"); detector L
  (1)-(3) via provchk. That class is GONE with the code (no mapping, no
  field): retiring it is right.
- The successor class (a kit row reads mf_akind.digest) has no matrix row
  ("waits for an S-id from the kit's range"). When filed, plant it in
  kit_byte_rate (P5's shape): today it would be MISSED (CHECK-1), which is the point.

### CHECK-6 SUSPECTED: L(4b)'s traced-stderr axis collides with the design's row 1 (the kit's trace names the digest)
- Severity: design/maintenance. Effort: small, at row 1.
- span_pick rev 5.2 :60/:360: the kit's trace names the digest from row 1. L(4b)
  compares traced stderr across digests; a sanctioned trace line naming the
  digest on an L site reds L. Confirm at row 1; fix by masking the digest
  token or comparing decision lines only.

### CHECK-7 (doc, low): stale "no row reads it before B3a" outside memfn.h
- memfn/src/compose.c :882 and memfn/src/kit.h :287 still say no row reads the
  analysis object before B3a; presence.c and window.c read it. The design's 1g
  reader row (:373) named memfn.h's copy only; the lane fixed that one.

## PROBED-AND-HELD

- P1, the design's own L(4) plant ([rev5.2 C8]) in finder.c fd_holds:
  `+ if (!strcmp(r->id, "D1") && q->art->an && q->art->an->nkinds && (q->art->an->kinds[0].digest & 1)) return 0;   /* PLANT P1 */`
  L RED: `FAIL: L: traced kit: site byte1t renders differently with mf_akind.digest 1 (a kit row reads the digest)`
  and the same for `0xffffffffffffffff`; `checks passed: 921` / `checks failed: 2`, rc=1.
- P2, same reader on the SECOND kind (`kinds[1]`, run-rarity): L RED, same two
  lines, 921 / 2. Held because fd_an_make states one digest on every kind.
- High-bit and zero-vs-nonzero readers: covered by AN_DIGESTS (0, 1, 2, 0x1234,
  0xffffffffffffffff) on a reached site; not separately planted.
- prov_check.c: builds -Werror at SUBJECT; an insertion before `digest` breaks
  it (offsetof 16, LP64). Blind to anything appended after `payload` (P6 built
  clean): a layout pin by design, not a content check.
- `--fd-an DIGEST`: strtoull(.., 0) parses all five AN_DIGESTS; the reference
  rendered TEXT on both sites (control 923 / 0).
- Totals: unplanted control 923 passed / 0 failed; 7 plants (P1-P7): 2 red, 5 green.

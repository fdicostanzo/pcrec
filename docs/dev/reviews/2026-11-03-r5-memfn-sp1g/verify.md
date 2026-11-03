# Verify: critic round memfn-sp1g (SUBJECT efd724b4b)

All quotes via `git -C /home/pcrec/projects/pcrec show efd724b4b:<path> | sed -n`.

## Verdicts

### READERS-1  PARTLY
window_contract.md: line numbers differ slightly from the brief. Unmarked present-fact statements, quoted:
- :775-776 (§3.6) "So `mf_prov.bytes` (and `fidelity`) are in the layout from its first declaration (§3.1)" -- no 1g mark; HOLDS.
- :798 (§3.7.1 builder row) "The mapping `PcrecFind*` -> `MF_PROV_*`/`MF_KIND_*`/`MF_FID_*` stays in `memfn_sites.c`" -- no 1g mark; HOLDS.
- :2035-2036 (§13) "BUILT (`mf_prov.bytes`, `fidelity`, §3.1)" -- no 1g mark; HOLDS.
- :585-599 (§3.1) "`bytes` and `fidelity` are in the layout..." and "`prov.source` is `AUTHORED`... An `ABSENT` kind has `source == MF_PROV_UNSTATED`": NOT individually marked, but the 1g revision line at :533-539 says "The block below and the invariant's `prov.source` wording are the rev 3.1 record". So §3.1 is covered by a blanket mark (PARTLY); §3.6/§3.7.1/§13 are not covered (the §3.2 mark at :606 covers §3.2 only).
Also unmarked: :59, :114, :158, :1156, :1701, :1770 (history/rev rows, arguably record).

### READERS-2 + CHECK-7  HOLDS
- memfn/include/memfn.h:1289-1290 "`an` its analysis object (DECLARED, E-1; NULL-tolerant, read by no kit row before B3a)"
- memfn/src/kit.h:286-287 "analysis object (DECLARED, E-1: read by no row before B3a)"
- memfn/src/compose.c:882 `art->an = an;  /* DECLARED (E-1): no row reads it before B3a */`
- memfn/src/presence.c:48-55 `kit_byte_rate` reads `art->an->kinds[i]` (tag, present, payload), called at presence.c:155.

### READERS-3  HOLDS
- src/gen/memfn_sites.c:187-193 comment "The object's invariant ... checked as it is built ... PRIOR_NONE states no bundle, digest or bytes"; function `analysis_invariant(Ctx*, const char *tag, const PcrecFindOffer *o)` checks `o` (the offer), not the built object (:196-212).
- memfn.h:1245-1246 `uint64_t digest; /* ... 0 without a payload */`; the invariant tests digest only under `o->source == PCREC_FIND_SRC_PRIOR_NONE && (o->bundle || o->digest || o->bytes)` (:202-203); an ABSENT or other no-payload kind with nonzero digest is not refused. So comment overstates.

### READERS-4  HOLDS
The word PRIOR_NONE (a pcrec-side source enumerator, deleted from the kit seam) appears in the kit: memfn/src/kit.h:324 "(no object, the kind absent, PRIOR_NONE)" and memfn/src/presence.c:47 "or present with no table: PRIOR_NONE". (`git grep -n PRIOR_NONE efd724b4b -- memfn src`.)

### HOUSE-1  HOLDS
memfn.h:1240 "the kit's trace names only the digest it was handed". `git -C ... grep -n digest efd724b4b -- memfn/src` returned ZERO hits (the word is absent from every memfn/src file), so no kit trace names any digest at SUBJECT; the sentence describes a not-yet-built row-1 behaviour as present fact.

### READERS standing-question (kit_byte_rate ignores version)  HOLDS
memfn/src/presence.c:48-55: matches `tag` "byte-rate", returns `(const uint32_t *)an->kinds[i].payload` when `present == MF_KIND_PRESENT`; `mf_akind.version` is never read (`grep -n version presence.c` shows no use in that function).

### READERS-6 + CHECK-3 (V-B)  HOLDS
Copy of SUBJECT in verify/tree (`git archive efd724b4b | tar -x`); planted src/gen/memfn_sites.c:265 `k[i].digest = o.digest;` -> `k[i].digest = 0;`.
Built only the trace compiler: `nice make -C verify/tree -s -j2 BUILD_DIR=verify/kst CFLAGS="-O2 -g -DPCREC_KS_TRACE" verify/kst/pcrec`.
Compared emitted C (-o x.c), stdout, stderr (incl. KSRCTRACE object records), rc against bin/subj-trace/pcrec: 5 patterns x {byte,utf8} x {no analysis, `-I emit/fx/x/aada_<enc> --analysis aada` (measured/authored bundle, records show digest 8d099a526f15a5ff), `--analysis log`} = 30 cases (60 compiles), `diff -r -q`: 0 differences. Nothing witnesses the object builder's digest write.

### CHECK-1 (plants P4, P5; control P1; premise)  HOLDS
Own copy: verify/ctree (copy of check/tree), verify/plant.sh (check/plant.sh with D=verify, T=verify/ctree), verify/bld.sh, verify/orig, verify/plants/*.sub (the critic's .sub files). Method: `verify/plant.sh pN FILE verify/plants/pN.sub` (apply str.replace, bld.sh, `python3 -I ctree/tests/memfn/finder_check.py --root ... --fx --fxt --tmp`, restore).
- Unplanted control (same tree): `checks passed: 923 / checks failed: 0`.
- P1 (finder.c fd_holds, digest&1 -> D1 declines): RED, `checks passed: 921 / failed: 2`, "FAIL: L: traced kit: site byte1t renders differently with mf_akind.digest 1 (a kit row reads the digest)" (+ 0xffff...). Control works.
- P4 (presence.c kit_pres_picks, `return` if digest&1): L GREEN `923 / 0`, rc=0. Real defect: `plants/p4/fxt --fd-site pre-opt --fd-an 0` vs `--fd-an 1`: rc 0/1, output DIFF; `--fd-site pre-lead-run`: rc 0/1 DIFF.
- P5 (presence.c kit_byte_rate, `&& !(digest & 1)`): L GREEN `923 / 0`, rc=0. Real defect: `plants/p5/fxt --fd-site pre-lead --fd-an 0` vs `1`: rc 1/0 DIFF; pre-lead-run rc 0/1 DIFF.
- Premise: on the unplanted traced driver (plants/ctl/fxt) `--fd-site set10` and `--fd-site byte1t` render byte-identical (stdout+stderr cmp) with no `--fd-an` and with `--fd-an 0`. For contrast pre-lead and pre-lead-run differ (rc 0 vs 1 / 1 vs 0). HOLDS.

### CHECK-2 (P6, P7)  HOLDS
- P6: memfn.h mf_akind gains `uint64_t nbytes;` after payload; finder.c fd_holds declines D1 when `kinds[0].nbytes == 0` (plants/p6.sub). L GREEN `923 / 0`, rc=0 (prov_check builds under -Werror via bld.sh). Real defect: `plants/p6/fxt --fd-site byte1t` with no analysis traces `ROW ... row=D1 verdict=CHOSEN`, FDROUTE D1; with `--fd-an 0` and `--fd-an 1`: D1 PRED_FALSE, D1c DECLINED, D1w CHOSEN.
- P7: memfn.h mf_analysis gains `const char *bundle;`; fd_holds declines D1 when `an && !an->bundle`. L GREEN `923 / 0`, rc=0. Same behaviour: D1 chosen with no analysis, D1w with `--fd-an 0` and `1`.
(header restored from verify/orig after each; `diff -rq ctree/memfn tree/memfn` clean.)

### CHECK-4 (P3)  HOLDS
P3 (fd_holds: D1 declines when `kinds[0].digest == 0x5eedULL`): L GREEN `923 / 0`, rc=0. Real defect: `plants/p3/fxt --fd-site byte1t --fd-an 0` vs `--fd-an 0x5eed`: rc 0/0, output DIFF.

### HOUSE-3  HOLDS
unplanted fxt: `--fd-site byte1t --fd-an 0` and `--fd-site byte1t --fd-an zzz` both rc=0 and `cmp` identical output. Cause: arm_fixtures.c:1600 `fd_an_make(strtoull(digest, NULL, 0))` with no end-pointer/errno check, so "zzz" parses as 0 silently.

VERIFY COMPLETE

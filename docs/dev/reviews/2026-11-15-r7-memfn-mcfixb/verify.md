## Verdicts

### RULE-1: HOLDS
Code (slot/d197_rule.py:487): `v = rule(sys.argv[2], sys.argv[3], "--second" in a, conf)`; rule() at :231 `def rule(rundir, avx2dir, second=None, confirm=None)`, :235 `zip(("shipped","avx2"), second or ())`, :239 `is_second = second is not None`.
Ran (PCREC_TMPDIR=verify, records = critic's rule/p1 [libc memchr=avx2] and rule/dr/d197_avx2):
- CLI no flag: `d197_rule.py rule rule/p1 rule/dr/d197_avx2` -> all 3 levels `d197_verdict ... NOT-WIN (second-run-without-a-verdict) ... a second run never offers a third`.
- Direct `rule('p1','d197_avx2')` -> {'generic','x86-64','x86-64-v3': 'INCONCLUSIVE'} (the correct first-run answer). So CLI != API for the same input.
- CLI `--second dr/d197_shipped dr/d197_avx2` -> `File ... d197_rule.py, line 235, in rule ... TypeError: 'bool' object is not iterable` (uncaught, no exit 2).
- Direct `rule(shipped, avx2, True)` -> same TypeError.
Note: with a genuine shipped record (rule/dr) the no-flag CLI gives LOSS (3+ losses, no second-run effect), so the mis-score bites on INCONCLUSIVE/confirm paths only.

### RULE-2: HOLDS (with a scope note)
Code (slot/est.py read_cells, in the review tree): `got, pin = plan.sha256(os.path.join(rundir, f)), rec["run"].get("cells_sha256_" + j)` / `if got != pin: raise InputError("CELLS PIN %s: sha-256 %s, the record pins %s (a cells file edited after finalize, or a record finalized before r6)" ...)` -- an absent pin (None) never equals a hash, so it refuses.
Committed s2d records: docs/design/memfn/span_cards/s2d1/run_record.tsv (run s2d-20261106, code_commit 508178bd2...) and s2d2/run_record.tsv (s2d-20261107a, 1e4999d1c...); `grep -c cells_sha256` -> 0 in both. Their dirs hold NO cells files (only run_record.tsv + analyses), so the cells themselves are not in the tree; est would only reach the pin if cells are restored beside the record.
Ran: copies in verify/c1, verify/c2, `record.py window <copy> <its own run id> <its own code_commit>`:
- c1 -> `record: REFUSED: the record's libc is 'glibc 2.43', this box's 'glibc 2.43 memchr=evex': one window, one box` rc=2
- c2 -> identical REFUSED line, rc=2.
Modelled pre-r6 est (est._synth('verify/syn'), then strip cells_sha256_* from run_record.tsv, est.compute): with pins -> priced OK; pins removed -> `InputError CELLS PIN cells.J2.tsv: sha-256 3a188b045b2a5f86, the record pins none (a cells file edited after finalize, or a record finalized before r6)`.
Caveat: the libc refusal is r5's probe (not this diff); the pin refusal is this diff's. Both confirmed; no supported re-price/re-finalize path for old windows.

### RULE-3: HOLDS (design-level: deliberate per the tsv header, but its consequence is as stated)
Code (slot/d197_rule.py:57-59): `"memchr-variant-not-the-arms": lambda a: a["variant"] is None or a["which"] == "avx2" and a["variant"] != AVX2_VARIANT or a["which"] == "shipped" and (a["tunables"] or a["variant"] == AVX2_VARIANT)`; `bound_right` (:159) and the arm scoring (:125) use it; tsv row `no-verdict memchr-variant-not-the-arms` (d197_rule.tsv:92).
Ran the predicate directly (`WHEN['memchr-variant-not-the-arms']`):
shipped avx2 tunables='' -> no-verdict; shipped avx2 tunables='x' -> no-verdict; shipped evex '' -> ok; shipped evex 'x' -> no-verdict; avx2 arm avx2 -> ok.
Constructed record: critic's rule/p1 (libc `glibc 2.43 memchr=avx2`, no GLIBC_TUNABLES) scored by the CLI above: every level's shipped arm line is `no-verdict ... (memchr-variant-not-the-arms)` (generic loss 9/win 9, x86-64 loss 7/win 11, v3 loss 8/win 10 -- numbers computed, not used), and direct rule() -> INCONCLUSIVE at all three levels. So on an AVX2-only box (shipped memchr = avx2, no tunable) the shipped arm can never give a verdict.
Nuance: d197_rule.tsv:15-16 states the shipped arm "carries no GLIBC_TUNABLES and names no `avx2`" as a deliberate FIDELITY-2 rule (so the two arms are not twins); the critic's point is that this encodes the 7700X landscape. Fair as a design finding; no bug against the written rule.

### CHECKS-1: HOLDS (fails closed; flag not currently carried)
Re-ran the critic's plant.py (copied to verify/plant.py) against the review tree's link.py: `-O3 -fno-plt` rows marked `<<<<< UNEXPECTED`:
- `tailcall memchr in fn-memchr | fn-memchr | REFUSE ... a64_time calls an indirect jmp (jmp *0x0(%rip) ...)` (valid control refused)
- `libc-byte memchr | libc-byte | REFUSE ... indirect call (call *0x0(%rip) ...)`
- `unknown form any ext | s2d-verify | REFUSE ... indirect call`
(the other -fno-plt refusals are expected-bad cases that also refuse.) So the per-form callee allowlist TIMED_CALLEES (link.py:211, lookup :221) never sees the callee under -fno-plt because the indirect-branch refusal fires first.
Flags: link.py:38 `CC = ["gcc", "-std=gnu11", "-O2", "-march=x86-64", "-mtune=generic"]`; compile sites link.py:308, :591 use `CC + [...]`. No -fno-plt in link.py, run.py, plan.py, the slot dir, memfn or Makefile (grep -l empty); the only env reads are CODE_COMMIT, BQ_JOB, SLOT_TREE, SLOT_CONFIRM_CELLS -- no CFLAGS path. So the slot's flags cannot carry -fno-plt today (only if someone edits CC, or the system gcc defaults to it: `gcc -dumpspecs | grep -c no-plt` -> 0). Latent over-refusal, fails closed. Severity low as stated.

### CHECKS-2: HOLDS
memfn/src/window.c:1904: `_Static_assert(FF_MFIND < 31 && WF_ST_SHIFT < REN_FRAME, "the renderer key spaces are disjoint");` guarding `#define REN_PICK(f) (1u << (f))` (:1902). kit.h:667-670 enum ends `FF_HORS, FF_MFIND, FF__COUNT`, so today FF_MFIND is the last real member and the bound is equal to FF__COUNT-1 < 31; a form appended after FF_MFIND (before FF__COUNT) is not covered by this assert, whereas finder.c:72 and window.c:2520 do key to FF__COUNT. Maintenance only, ~20 members of headroom.

VERIFY COMPLETE

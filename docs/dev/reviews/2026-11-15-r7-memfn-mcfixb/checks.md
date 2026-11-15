# checks — memfn-mcfixb

## Findings

### CHECKS-1 (CONFIRMED, low, doc/maintenance): TIMED-SHAPE over-refuses under -fno-plt
plant.py (checks/) -O3 -fno-plt: fn-memchr tail `jmp *GOT` / `call *GOT(%rip)` is refused as "indirect" although it is memchr (valid control fails); libc-byte and unknown-form likewise. Default/-fPIC/-fcf-protection pass. Only matters if the slot's CC ever carries -fno-plt (link.py CC not checked for it); fails closed.

### CHECKS-2 (CONFIRMED, low, maintenance): the renderer key-space assert is still keyed to FF_MFIND, not FF__COUNT
window.c:1904 `_Static_assert(FF_MFIND < 31 && ...)` guards REN_PICK(f)=1u<<f; a form added after FF_MFIND is not bounded by it (only matters at >=31 members; ~20 away). Other per-form tables (ren_search/ren_fused/fn_rows) are keyed by REN_PICK bit sets or designated rows, not arrays sized by the enum: none other found indexed by fd_form. Fix: use FF__COUNT <= 31.


## PROBED-AND-HELD
- link.py shape-selftest: 7 cases, 0 wrong. Own plants (plant.py, 12 shapes x 4 flag sets = 48): memchr in mfind arm, tail-jmp to external (mfind), tail-jmp memchr in fn-memchr (PASS control), strlen in fn-memchr, global fn in other section / same section, extern call, libc-byte memchr, unknown form any ext, walk with memchr, pair strlen, mfind with cold-expect branch: all as expected at -O2, -fPIC, -fcf-protection; only -fno-plt over-refuses (CHECKS-1). Indirect call/jmp, PLT, section symbols all refused.
- FF__COUNT: (a) new member undeclared -> both finder.c and window.c static asserts fail; (b) declared in both -> compiles; control compiles. 
- run_g2_mfind.py: --sites 79/40/0/-5 -> argparse error; 80 admitted; --quick sets 80; run_g2.sh passes only --quick; no env path sets sites (G2M_SITES is a -D from a.sites, after the check).
- Zero movers: memfn/src diff is enum + static_assert only; all 18 memfn/src TUs compiled -O2 from BASE vs SUBJECT: disassembly+data identical (18/0 diff). No other src/ cli/ lib/ change in the diff, so emitted C cannot move; 400-compile sweep skipped as redundant.
- ac097a76e: comment-only in S3198 script header; its SAB_BEFORE anchor is vrun.c text; m6read_check_sab_anchors.py: 1301 sabotages, all anchors resolve.

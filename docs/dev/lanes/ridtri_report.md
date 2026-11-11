# ridtri report

## STATE AT HANDOFF

Subject: full suite 300-main-fullsuite (frozen 7d74499bc), stage `recidentity`
(`tests/codegen/run_recursion_identity.sh`), 7 checks passed, 4 failed.

Failing checks: comparison (B), whole-file vs FILEPIN cf578177ed, on the
[default], [vm], [noprefilter] and [nocaptures] axes (410/410/410/413
differing). Comparison (A) program-region was 0 differing on all four axes;
[linkage] and [elision] passed.

- Class A (an intended emitted-byte change owed a re-pin). Cause commit
  `001c0faf5` (sar1fix: r5 EMIT-1/EMIT-2 run choice, `req_whole_run` DERIVED),
  landed via `f7eb10528` (Merge lane/sar1mrg, span arms R1). abi stays 98 (no
  bump), so only the whole-file pin moved.
- First differing bytes (call-free `(?:a+)+b`, `((a+)(b+))+$`, pin vs build):
  `#define RX_REQ_RUN "none"` becomes `#define RX_REQ_RUN "6162@1"`. The
  `#include "a.h"` / `"b.h"` line differs only because my probe used two output
  names. The program region is identical, matching (A) = 0 differing.
- Fix: FILEPIN and ABASEPIN in `tests/codegen/run_recursion_identity.sh` move
  from cf578177ed to `f7eb10528`, per the header's re-pin procedure (history
  note in the pin comments). No emitter change.
- Proof: standalone `bash tests/codegen/run_recursion_identity.sh` on this
  branch, [default] axis: (B) same=4282 differing=0 and (A) same=4282
  differing=0, both PASS (log
  /var/tmp/pcrec-pcrec/scratch/ridtri/run1.log). The other axes of that run
  and the full make target are OWED to the queued job below.
- Not class B (region identical; the only moved byte is the sar1fix stamp).
  Not class C.

Jobs OWED: `330-ridtri-recid` (key ridtri-recid) runs
`make test-recursion-identity` on worktrees/ridtri; green means
`checks failed: 0`.

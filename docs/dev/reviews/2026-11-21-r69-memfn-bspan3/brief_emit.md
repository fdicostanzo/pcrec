CRITIC emit (opus): memfn-bspan3. Read /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/COMMON.md FIRST and obey it.
Lens: SOUNDNESS + READINESS on the EMITTED TEXT and the C18 AMENDMENT's rule (unit U3, and the C18 part of U4).
Your one question: is rev 3's emitted text (§4.1, §4.2, §5) and the amended C18 rule (§10.2 "The C18 amendment": the
SELECTOR/HELPER spelling and the -O0 rule (i)+(ii)) right as written: would a lane building it LITERALLY get answers
identical to today and a C18 that passes the correct text and fails a wrong one?
Your F-ids for the Fix ledger: F-1 (the rule part; its control PLANTS belong to lens checks), F-5 (lane order, signed
values), F-8 (the K >= 16 assert, B choice), F-13 (the wrapper's machine-code evidence text in §2 / §16 item 6b).
Drills that are YOURS: hand-execute §4.1 + §5 LITERALLY from rev 3's text, with every kept guard in force (`unused` +
`always_inline` on __body, the selector's one call, the bracket), at gcc -O2, -O0, -march=native and clang -Wall -Wextra
-Werror, on a few real sites built from the build tree's emitted C (kit/site.py --out keeps it) at widths 32 and 4095, B 16
and 32, HORS and R7w; guard pages both ends. r68 already hand-executed 16 sets x 14 K with index-order vs reversed tables;
do NOT repeat that sweep at scale: spot-check the corrected text (a handful of sets, k 16, 31, 32, 1000) and spend the rest
on what rev 3 CHANGED. For the C18 amendment: copy tests/memfn/simd_floor_check.py into your dir, apply the amendment as
§10.2 words it, and run it over a hand-built OFF/ON pair: does it now find the selector and helpers, does leg (c) pass, and
does the -O0 rule work: at -O0, where is the selector, where is the region pragma vs the simd_open/close bracket, does gcc
-O0 inline the always_inline chain into rxa_search, does "a ymm register in the function that calls the selector" hold and
can it distinguish anything? Read C18's real -O0 leg code (simd_floor_check.py + run_simd_floor.sh) for what object it
compiles. Per unit (U3, C18 in U4): verdict ready / ready with text fixes / not ready.
NOT yours: table/plan/one-writer structure (lens seam), counts and pins (lens pop), sabotage plants incl. C18's control
plants (lens checks), quotes/fork/ship-size (lens ruling).
Compile cap: 120 pcrec compiles; gcc/clang 200. Findings ids EMIT-n. Findings file (pre-created; APPEND only):
/var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/emit.findings.md. Your dir: /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/emit/.
Lanecheck name: emit.

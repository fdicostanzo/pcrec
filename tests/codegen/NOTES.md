
## [FINDALL-NEXT] lane iterland: additions carried from lane/itertri (verbatim)

  - **[FINDALL-NEXT] I4: THE ITERATOR ARM** (findall_iter_i2.md §5.2). Each
    rung's artifact is also linked with `tests/findall/iter_drv.c` over the
    witness's subjects: the generic info loops, `_next_n` and `_next` against each other
    and `_next` against libpcre2's global loop. Rung identity is not its
    expectation (the iterator answers PCRE2's iteration, which the find-all
    loop does not claim). SKIPS that arm loudly without libpcre2.
## [FINDALL-NEXT] I1 (lane i1build, 2026-10-21, abi 83)

- **run_residual_twins.sh** — IC1, the residual twins (findall_iter.md §2.4):
  each exported residual entry is a forwarder to a static `<prefix>__<name>`
  and every call inside the artifact reaches the twin, read off a -O2 -fPIC
  OBJECT (`nm` pairs a global `<p>_X` with a local `<p>__X`; a PLT32/PC32
  relocation against the global is a miss). Seven artifacts (the iterator,
  the subject check, variables, both engines, a compound shell), a PLANT
  (one twin call respelled to the exported name must read as a miss) and a
  population floor of (artifact, residual) pairs. In `make test-codegen`.

## Moved from CLAUDE.md (lane p1build, 2026-10-29, size limit)

- `run_prechecks.sh` §5 `<PREFIX>_REQ_WHY` ([OPT-PRECHECK-ADMIT], 2026-09-23, abi 30 -> 31): the ADMISSION of §3's and §4's pre-checks, ruled by Frank as G1 + G2 (G3 dropped on x86_64 measurement); neither decline is answer-detectable, so this file is where they are defended.

- run_residual_twins.sh (moved from CLAUDE.md, 2026-10-30): the premul table also has an iterator arm.

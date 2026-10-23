
## [FINDALL-NEXT] lane iterland: additions carried from lane/itertri (verbatim)

  **[FINDALL-NEXT] I0 (lane i1build, 2026-10-21): `reports_empty`** (E1, no
  deny, `pcrec_pattern_reports_empty`): can some match's REPORTED span be
  empty -- a nullable pattern, or one whose `\K` can be crossed with no
  byte after it (`ab\K`). One walk computes, per subtree, the least
  consumed length of a path that crosses no `\K` and the least length after
  the last `\K` a path crosses (`RepW`). `pf_check_e1` holds it to the
  lowered tree and `nullable ⇒ reports_empty`. Its readers are the
  find-all iterator's retry gate (compile.c's notempty machine, the VM
  accept guard, `<PREFIX>_ITER_RETRY`).

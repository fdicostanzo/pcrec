# tests/utfcheck — [UTF-VALID]'s suite (`make test-utfcheck`, in TEST_SECTIONS)

The opt-in subject UTF-8 validity check (`-futf-check`, the `whole`
contract) and the start alignment (`-fstartpos-guard=align`), ruled D133
(`docs/design/utf_valid_design.md`; the spec is `docs/spec/match_api.md`
§3.1/§3.1.2 and `docs/spec/tuning.md` §2.23/§2.36). The corpus cannot see
either: no `.rxt` directive compiles `-futf-check`, and every corpus cell
starts on a character boundary. This suite is the instrument that can.

## Files

- `gen_cases.py` — writes the QUESTION set (deterministic, seeded): the
  design's §1 rows (`pinned`), every §1.4 LB pattern pcrec compiles
  (`lb`), every ill-formed sequence kind at three depths plus the ASCII
  fast path's eight-byte windows with a long tail (`kinds`), every
  startpos of multi-byte subjects asked at the ALIGNED position (`align`,
  aligned by the byte rule computed here, not by pcrec), and a seeded
  fragment-alphabet differential (`random`). Modes: S (search), A
  (anchored, `PCRE2_ANCHORED`).
- `probe_pcre2.c` — the libpcre2 oracle: answers the questions under
  PCRE2_UTF with checking ON (rc, ovector, `pcre2_get_startchar`,
  `PCRE2_INFO_MAXLOOKBEHIND`). NOT built by `make`; run ONCE on the
  reference box. Reproduce (light: one small compile, ~6.5k matches, the
  temp dir removed):

      python3 gen_cases.py > q.tsv
      { echo __SRC__; cat probe_pcre2.c; echo __Q__; cat q.tsv; } | ssh duxevents@100.69.121.107 \
        'd=$(mktemp -d); cat > $d/in; awk "/^__SRC__\$/{m=1;next} /^__Q__\$/{m=2;next} m==1{print > \"$d/p.c\"} m==2{print > \"$d/q.tsv\"}" $d/in; gcc -O1 -o $d/probe $d/p.c $(pcre2-config --cflags --libs8); $d/probe < $d/q.tsv; rm -rf $d' > cases_10.46.tsv

- `cases_10.46.tsv` — that transcript, COMMITTED (libpcre2 10.46,
  ubuntubudu, 2026-09-30). The Mac's 10.48 answers every row identically
  except the meaningless `startchar` of a `-33` BADOFFSET row.
- `driver.c` — the pcrec side, linked against one `-p rx` artifact: drives
  every entry that takes a subject (`_search`/`_search_in`, `_match`/
  `_match_in`/`_match_caps`/`_match_caps_in`), requires the pairs to agree
  and `caps` untouched on every NEGATIVE return, and prints
  `<prefix>_valid_upto` at the startpos and at the aligned position.
- `check.py` — the comparator and every guard; its header is the rationale.
  Configs per pattern: K (`-futf-check`), KV (`--engine=vm`), KW (the
  capture-wrapped `(P)`, the VM hybrid), KA (`-futf-check
  -fstartpos-guard=align`), A (align alone, well-formed rows), D (the
  default artifact: never -9, `valid_upto` still exact, the same answer on
  an accepted range), B (`-e byte`: both flags inert, the artifact
  byte-identical). Plus the LB table (`rx_VALID_LB` vs
  `PCRE2_INFO_MAXLOOKBEHIND`), the SECOND ORACLE (python's strict decoder
  over the design's §1.3 range must agree with libpcre2 on every row
  before pcrec is scored), the design's §1 tables reproduced exactly, and
  populations floored (K35).
- `run_utfcheck.sh` — the launcher (`$PCREC`, `$CC` via cc_resolve.sh).

## The CLIP class — a measured PCRE2 behaviour, pinned EXACT

With UTF checking ON, libpcre2 treats `f` (startpos stepped back LB
characters) as the START OF THE SUBJECT for backwards reads: a `\b` at `f`
sees no previous character and a nested lookbehind stepping before `f`
fails — even on WELL-FORMED text (`(?<=\ba)b` on "xab" from 2 matches under
PCRE2_UTF and not from 0, and not without UTF). The design's §1.4 said PCRE2
"reads them unvalidated"; it does not read them. pcrec reads the real bytes
with or without the flag. So on the three patterns whose reach exceeds LB
(`CLIP` in check.py) the accepted ANSWER may differ from PCRE2's (4 cells
per config, pinned exactly), must equal the default artifact's, and the
refusal set and offset are exact there too. Recorded in
`docs/dev/lanes/uvbuild_report.md`.

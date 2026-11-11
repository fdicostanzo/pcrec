"""tests/ucp/ucp_sets.py — THE UCP MEMBERSHIP POPULATION, one list both halves
read: `build_ucp_store.py` (captures libpcre2's answers into the committed
store) and `ucp_compare.py` (compares pcrec's artifacts against them). One
list, so the capture and the comparison cannot drift apart.

Each entry is (construct, spelling):
  construct  the class construct's pattern text, as a UCP-config `membership`
             question asks it (tests/oracle/oracle_store.py's OracleId
             docstring).
  spelling   the DEFK_SET entry's `str` (src/parse/registry.c), the set's
             spelling under utf8. Also captured under UCP|UTF: the store then
             carries libpcre2's own construct==spelling relation, and
             tests/registry/definitions_check.c ties spelling==producer.

The third column (`wide_utf8`, the sets over the retired narrow-set knee) left
with that knee (review 2026-11-10 r4 ucpu3 RULES-9/checks-8): every set
compiles, so a column naming which ones were once refused selected nothing.
"""

SETS = [
    (r"\d",           r"\p{Nd}"),
    (r"\s",           r"\p{Xsp}"),
    (r"\w",           r"\p{Xwd}"),
    (r"[[:alnum:]]",  r"\p{Xan}"),
    (r"[[:alpha:]]",  r"\p{L}"),
    (r"[[:blank:]]",  r"[\t \xa0\x{1680}\x{180e}\x{2000}-\x{200a}\x{202f}\x{205f}\x{3000}]"),
    (r"[[:cntrl:]]",  r"\p{Cc}"),
    (r"[[:digit:]]",  r"\p{Nd}"),
    (r"[[:graph:]]",  r"[^\p{Z}\p{Cc}\p{Cs}\p{Co}\p{Cn}\x{61c}\x{180e}\x{2066}-\x{2069}]"),
    (r"[[:lower:]]",  r"\p{Ll}"),
    (r"[[:print:]]",  r"[^\p{Zl}\p{Zp}\p{Cc}\p{Cs}\p{Co}\p{Cn}\x{61c}\x{2066}-\x{2069}]"),
    (r"[[:punct:]]",  r"[\p{P}$+<=>^`|~]"),
    (r"[[:space:]]",  r"\p{Xps}"),
    (r"[[:upper:]]",  r"\p{Lu}"),
    (r"[[:word:]]",   r"\p{Xwd}"),
    (r"[[:xdigit:]]", r"[0-9A-Fa-f\x{ff10}-\x{ff19}\x{ff21}-\x{ff26}\x{ff41}-\x{ff46}]"),
]

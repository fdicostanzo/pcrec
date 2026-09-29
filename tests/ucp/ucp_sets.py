"""tests/ucp/ucp_sets.py — THE UCP MEMBERSHIP POPULATION, one list both halves
read: `build_ucp_store.py` (captures libpcre2's answers into the committed
store) and `ucp_compare.py` (compares pcrec's artifacts against them). One
list, so the capture and the comparison cannot drift apart.

Each entry is (construct, spelling, wide_utf8):
  construct  the class construct's pattern text, as a UCP-config `membership`
             question asks it (tests/oracle/oracle_store.py's OracleId
             docstring).
  spelling   the DEFK_SET entry's `str` (src/parse/registry.c), the set's
             spelling under utf8. Also captured under UCP|UTF: the store then
             carries libpcre2's own construct==spelling relation, and
             tests/registry/definitions_check.c ties spelling==producer.
  wide_utf8  pcrec REFUSES the construct under -e utf8 at [UCP] U1 (D130 Q3;
             limits.md §3.8), so its utf8 arm is checked through the spelling
             chain above instead of by compiling it.
"""

SETS = [
    (r"\d",           r"\p{Nd}",  False),
    (r"\s",           r"\p{Xsp}", False),
    (r"\w",           r"\p{Xwd}", True),
    (r"[[:alnum:]]",  r"\p{Xan}", True),
    (r"[[:alpha:]]",  r"\p{L}",   True),
    (r"[[:blank:]]",  r"[\t \xa0\x{1680}\x{180e}\x{2000}-\x{200a}\x{202f}\x{205f}\x{3000}]", False),
    (r"[[:cntrl:]]",  r"\p{Cc}",  False),
    (r"[[:digit:]]",  r"\p{Nd}",  False),
    (r"[[:graph:]]",  r"[^\p{Z}\p{Cc}\p{Cs}\p{Co}\p{Cn}\x{61c}\x{180e}\x{2066}-\x{2069}]", True),
    (r"[[:lower:]]",  r"\p{Ll}",  True),
    (r"[[:print:]]",  r"[^\p{Zl}\p{Zp}\p{Cc}\p{Cs}\p{Co}\p{Cn}\x{61c}\x{2066}-\x{2069}]", True),
    (r"[[:punct:]]",  r"[\p{P}$+<=>^`|~]", True),
    (r"[[:space:]]",  r"\p{Xps}", False),
    (r"[[:upper:]]",  r"\p{Lu}",  True),
    (r"[[:word:]]",   r"\p{Xwd}", True),
    (r"[[:xdigit:]]", r"[0-9A-Fa-f\x{ff10}-\x{ff19}\x{ff21}-\x{ff26}\x{ff41}-\x{ff46}]", False),
]

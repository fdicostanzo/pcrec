# studies/k70_probe/ — K70's oracle evidence

K70's own light probe (`docs/dev/known_issues.md` K70, `docs/dev/
ucp_study.md` §G.1's finding): two questions `probe_misc.py`
(`studies/ucp_study/`, lane ucpthink) did not answer — whether pcrec's
BYTE-mode `(?r)` no-op claim holds across the WHOLE Latin-1 range (not just
letters), and whether the `(?aD)`/`(?aP)`/`(?aS)`/`(?aT)`/`(?aW)` sub-letters
stay no-ops under `-e utf8` WITHOUT UCP (which pcrec does not implement).

## Files

- `probe_k70.py` — the probe (BOILERPLATE's light-probe protocol,
  `probe_misc.py`'s own shape: ctypes over `libpcre2-8`, no second
  binding). Run over ssh stdin against the tailnet 10.46 reference
  (`python3 - /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0`, no local
  argument needed elsewhere). Two row families: (1) `(?r)`/no-`(?r)` pairs
  over the ASCII alphabet's fold pairs plus the Latin-1 e-acute/E-acute
  pair plus a whole `[0xC0-0xDE]` class, all under BYTE (no UTF flag at
  all); (2) `(?aD)`/`(?aP)`/`(?aS)`/`(?aT)`/`(?aW)`/bare `(?a)` with-vs-
  without pairs, all under `UTF` alone (no `UCP`), on the same subjects
  `studies/ucp_study/probe_misc.py` used for the UCP-ON cells.
- `probe_k70_10.46.txt` — the transcript, libpcre2 10.46 (2025-08-27),
  fetched over `ssh duxevents@100.69.121.107` (the tailnet address; the
  travel-month topology memory's `192.168.1.100` is LAN-only and
  unreachable this session). Every `(?r)`/no-`(?r)` row reads IDENTICAL
  in both directions (byte mode: `(?r)` never changes an answer, letters
  or Latin-1) and every `(?aX)`-with/without pair reads IDENTICAL under
  UTF-no-UCP — the evidence `docs/dev/known_issues.md` K70 cites for both
  halves of the fix (`(?r)` refuses under `-e utf8` rather than
  implementing the restriction; the `a`-sub-letters get a comment, no
  code change).

## Reproduction

`cat probe_k70.py | ssh duxevents@100.69.121.107 'python3 - /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0'`

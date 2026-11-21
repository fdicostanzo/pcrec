# MODEL lens probes: a tiny evaluator built from condition_kind.md's TEXT (Part I s2, II.1, III a2, A2).
# Result rows of a statement on a subject: whole mode = fullmatch of the subject (one reading, Python re as PCRE stand-in);
# searched mode = every span (s,e) the pattern matches WHOLE, each with its own one parse (rev 22 s4.5, D196).
import re, itertools, sys
def rows(rx, subj, searched):
    r = re.compile(rx); out = []
    spans = [(s, e) for s in range(len(subj)+1) for e in range(s, len(subj)+1)] if searched else [(0, len(subj))]
    for s, e in spans:
        m = r.fullmatch(subj, s, e)
        if m: out.append(((s, e), m.groupdict()))
    return out
out = []
# (1) A & !B, label-free, searched: per SPAN (rev 22, filter roles tied to one stretch) vs per SUBJECT (source-row YES)
for subj in ["0 7", "0", "7", "00 70"]:
    A = rows(r'\d+', subj, True); B = rows(r'0+', subj, True)
    per_span = any(not re.fullmatch(r'0+', subj[s:e]) for (s, e), _ in A)
    per_subj = bool(A) and not B
    out.append(f"(1) /\\d+/ & !/0+/ searched on {subj!r}: per-span {'HOLDS' if per_span else 'FAILS'}; per-subject {'HOLDS' if per_subj else 'FAILS'}")
# (2) P & Q of two statements, searched: joined on the SOURCE row (Part I s2) vs the same stretch (ruled 2026-11-15 20:43)
for subj in ["ab", "a", "ba"]:
    P = rows('a', subj, True); Q = rows('b', subj, True)
    join_src = bool(P) and bool(Q)
    same = any(sp == sq for sp, _ in P for sq, _ in Q)
    out.append(f"(2) /a/ & /b/ searched on {subj!r}: joined on source row {'HOLDS' if join_src else 'FAILS'}; same stretch {'HOLDS' if same else 'FAILS'}")
# (3) when(c, p), x = /(?<d>\d)/ searched, c = (d: <5), p = (d: "0"); case-when per row vs the body (x&c&p) | (x & !(x&c)) with a per-subject complement
for subj in ["1 7", "7", "1", "0 7"]:
    X = rows(r'(?P<d>\d)', subj, True)
    c = lambda g: g['d'] is not None and int(g['d']) < 5
    p = lambda g: g['d'] == '0'
    case = any((p(g) if c(g) else True) for _, g in X)
    xc = [r for r in X if c(r[1])]
    body = any(c(g) and p(g) for _, g in X) or (bool(X) and not xc)
    out.append(f"(3) when((d: <5), (d: \"0\")) searched on {subj!r}: case-when per row {'HOLDS' if case else 'FAILS'}; body with per-subject complement {'HOLDS' if body else 'FAILS'}")
# (4) A2 all() over a record mixing a looped h with a set-once k, RZ = /(?<k>\d)(?:;(?<h>\d))*/, zero-pass subjects
RZ = [str(k) + ''.join(';' + str(h) for h in t) for k in range(10) for n in range(3) for t in itertools.product(range(10), repeat=n)]
def passes(subj):
    m = re.fullmatch(r'(?P<k>\d)((?:;\d)*)', subj); return m.group('k'), [x for x in m.group(2).split(';') if x]
d4 = []
for subj in RZ:
    k, hs = passes(subj)
    a2_rec = all(int(h) < 5 and 3 <= int(k) <= 7 for h in hs)            # every pass passes the record, none needed
    split = all(int(h) < 5 for h in hs) and 3 <= int(k) <= 7               # all((h:<5)) & (k: 3..7) (k set once: its pass = the match)
    plain = bool(hs) and all(int(h) < 5 for h in hs) and 3 <= int(k) <= 7  # plain record, LEFT JOIN row on zero passes (h NULL -> fails)
    if a2_rec != split: d4.append(subj)
out.append(f"(4) RZ ({len(RZ)}): all((h: <5, k: 3..7)) [A2] vs all((h: <5)) & (k: 3..7): differ on {len(d4)} {d4[:6]}")
# (5) P | Q, P = /(?<h>\d)/, Q = /(?<k>\d)/, whole, & (h = 0: <5): one reading (first alternative) vs union of rows (Part I s2)
for subj in ["7", "3"]:
    one = re.fullmatch(r'(?P<h>\d)|(?P<k>\d)', subj).groupdict()
    one_ans = int(one['h'] if one['h'] is not None else 0) < 5
    union = [{'h': subj, 'k': None}, {'h': None, 'k': subj}]
    un_ans = any(int(g['h'] if g['h'] is not None else 0) < 5 for g in union)
    out.append(f"(5) (P | Q) & (h = 0: <5) on {subj!r}: one reading {'HOLDS' if one_ans else 'FAILS'}; union of rows {'HOLDS' if un_ans else 'FAILS'}")
# (6) repeated-or-set-once by the PROGRAM: P = /(?:(?<h>\d);)*/ & /(?:\d;)?/, some((h = 0: <5)) on ''
for subj in ["", "3;", "7;"]:
    m = re.fullmatch(r'(?:(?P<h>\d);)*', subj); ok2 = re.fullmatch(r'(?:\d;)?', subj)
    if not (m and ok2): continue
    hs = re.findall(r'(\d);', subj)
    rep = any(int(h) < 5 for h in hs)                       # repeated (regex): passes = iterations, zero passes -> no pass
    so = int(hs[0] if hs else 0) < 5                        # set once (program): the pass is the match, the default fills absent h
    out.append(f"(6) some((h = 0: <5)) on {subj!r}: h repeated (regex) {'HOLDS' if rep else 'FAILS'}; h set once (program) {'HOLDS' if so else 'FAILS'}")
open(sys.argv[1], 'w').write('\n'.join(out) + '\n')

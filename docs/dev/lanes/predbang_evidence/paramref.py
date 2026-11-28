import re
# 2026-11-27 param-reference, the manager's reading: a parameter the body reads and never places is replaced by the
# caller's name at the call. Each program below is the EXPANSION, run as a regex plus a test on the named groups.
ISO = r'(?P<{p}year>\d{{4}})-(?P<{p}month>\d\d)-(?P<{p}day>\d\d)'
def run(rx, ok, whole, srch, fa):
    R = re.compile(rx)
    good = lambda m: m is not None and ok(m)
    def findall(s):
        out, i = [], 0
        while i <= len(s):
            m = R.match(s, i)
            if good(m): out.append(f'{m.group()}@{i}'); i = max(m.end(), i + 1)
            else: i += 1
        return out
    w = ' / '.join(f"`{x}` {'HOLDS' if good(R.fullmatch(x)) else 'FAILS'}" for x in whole)
    return f'WHOLE {w} | SEARCHED `{srch}`: {(findall(srch) or [None])[0]} | FIND-ALL `{fa}`: {findall(fa)}'
print('1. before2100(B) := (B.year: < 2100) ; isodate & before2100(isodate)  ==  isodate & (isodate.year: < 2100)')
print('  ', run(ISO.format(p=''), lambda m: int(m['year']) < 2100, ['2024-02-29', '2150-01-01'], 'x 2150-01-01 1999-12-31', '2024-02-29 2150-01-01 1999-12-31'))
print('2. [d = isodate] SEQ " " SEQ [e = isodate] & before2100(d) & !before2100(e)  ==  ... & (d.year: < 2100) & !(e.year: < 2100)')
print('  ', run(ISO.format(p='d_') + ' ' + ISO.format(p='e_'), lambda m: int(m['d_year']) < 2100 and not int(m['e_year']) < 2100,
                ['2024-02-29 2150-01-01', '2150-01-01 2024-02-29', '2024-02-29 2025-03-01'],
                '2150-01-01 2024-02-29 2150-01-01', '2024-02-29 2150-01-01 1999-12-31 2200-05-05'))
print('3. checked(B) := B & (B.year: < 2100) ; checked(isodate)  ==  isodate & (isodate.year: < 2100): the answers of 1')

import re
# 2026-11-27 body-own-name, the reading "a path that skips nothing is legal": the binding's own d, by a regex
# built from the program text (the labelled part's group left unnamed, the own group named d). Prints; asserts nothing.
def modes(rx, whole, srch, fa):
    ok = lambda m: m is not None and int(m.group('d')) < 5
    def findall(s):
        out, i = [], 0
        while i <= len(s):
            m = re.compile(rx).match(s, i)
            if ok(m): out.append(f'{m.group()}@{i}'); i = max(m.end(), i + 1)
            else: i += 1
        return out
    w = ' '.join(f"{x} {'HOLDS' if ok(re.fullmatch(rx, x)) else 'FAILS'}" for x in whole)
    return f'WHOLE {w} | SEARCHED {srch}: {(findall(srch) or [None])[0]} | FIND-ALL {fa}: {findall(fa)}'
print('[c = B(A)] & (c.d: <5), A := /(?<d>\\d)/, B(rx) := /${rx}-(?<d>\\d)/ ; the body\'s own d:')
print('  ', modes(r'(?:\d)-(?P<d>\d)', ['7-3', '3-7'], '3-7 7-3', '7-3 3-7 1-2 9-9'))
print('X & (X.d: <5), X := [a = P] SEQ /;(?<d>\\d)/, P := /(?<d>\\d)/ ; X\'s own d:')
print('  ', modes(r'(?:\d);(?P<d>\d)', ['7;3', '3;7'], '3;7 7;3', '7;3 3;7 1;2 9;9'))
print('the same X, the labelled part\'s d by its full path X.a.d:')
print('  ', modes(r'(?P<d>\d);(?:\d)', ['7;3', '3;7'], '7;3 3;7', '7;3 3;7 1;2 9;9'))

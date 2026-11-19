import re
def spans(rx, s):
    r = re.compile(rx)
    return [(i, j) for i in range(len(s)+1) for j in range(i, len(s)+1) if r.fullmatch(s[i:j])]
def rev22_and_not(A, B, s):   # same stretch: span in A, not in B
    b = set(spans(B, s)); return [sp for sp in spans(A, s) if sp not in b]
def s1_and_not(A, B, s):      # per subject anti-join
    return spans(A, s) if not spans(B, s) else []
def rev22_and(A, B, s):
    b = set(spans(B, s)); return [sp for sp in spans(A, s) if sp in b]
def join_on_source(A, B, s):  # result rows carry no span, joined on subject
    return [(x, y) for x in spans(A, s) for y in spans(B, s)]
for s in ['0 7', '00 70']:
    print('V1', repr(s), 'rev22 A&!B spans:', [s[i:j] for i, j in rev22_and_not(r'\d+', r'0+', s)],
          '| S1 rows:', s1_and_not(r'\d+', r'0+', s))
for s in ['ab', 'ba']:
    print('MODEL-2', repr(s), 'same-stretch &:', rev22_and('a', 'b', s),
          '| joined on source row:', len(join_on_source('a', 'b', s)), 'rows')

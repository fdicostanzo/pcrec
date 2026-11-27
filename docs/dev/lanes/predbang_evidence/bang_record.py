import itertools
# labels a, b each absent (None) or a digit; S := <5, T := >=3
S = lambda v: v < 5
T = lambda v: v >= 3
vals = [None] + list(range(10))
ent  = lambda v, X: v is not None and X(v)            # (v: X)
entn = lambda v, X: v is None or not X(v)             # (v ?! X)
bang = lambda v, X: v is not None and not X(v)        # (v ! X)
J = lambda a, b: (a, b) >= (5, 3)                     # the joint set >= (5, 3)
n = d1 = d2 = d3 = 0
for a, b in itertools.product(vals, vals):
    n += 1
    if (not (ent(a, S) and ent(b, T))) != (entn(a, S) or entn(b, T)): d1 += 1
    jt = a is not None and b is not None and J(a, b)  # ((a, b): >= (5, 3))
    if (not jt) != (entn(a, lambda v: v >= 5) or entn(b, lambda v: v >= 3)): d2 += 1
    # the documents' own split of the joint: (a: >5) | (a: 5, b: >=3); its negation written with the operators
    split_neg = entn(a, lambda v: v > 5) and (entn(a, lambda v: v == 5) or entn(b, T))
    if (not jt) != split_neg: d3 += 1
print(f'!(a: S, b: T)  against  (a ?! S) | (b ?! T): {d1} of {n} differ')
print(f'!((a, b): >= (5, 3))  against  (a ?! >=5) | (b ?! >=3): {d2} of {n} differ')
print(f'!((a, b): >= (5, 3))  against  (a ?! >5) & ((a ?! 5) | (b ?! >=3)): {d3} of {n} differ')

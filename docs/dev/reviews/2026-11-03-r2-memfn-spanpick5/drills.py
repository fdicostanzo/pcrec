#!/usr/bin/env python3
"""SIM drills on constructed outcomes: §The pick 3 implemented literally.
qualifier: price(inc) - price(c) > band(inc, c); pick = cheapest qualifier; qualifiers within
band(cheapest, q) of the cheapest go to TIE (stand-in: a declared order list); else incumbent."""
import math

def band(cards_a, cards_b, noise):
    # quadrature over cards of (coef_a - coef_b) * noise; cards = {card: coef}
    ks = set(cards_a) | set(cards_b)
    return math.sqrt(sum(((cards_a.get(k, 0) - cards_b.get(k, 0)) * noise[k]) ** 2 for k in ks))

def pick(inc, cands, price, bandf, tie_order):
    q = [c for c in cands if c != inc and price[inc] - price[c] > bandf(inc, c)]
    if not q: return inc, q, []
    cheapest = min(q, key=lambda c: price[c])          # text: "the CHEAPEST qualifier"
    tieset = [c for c in q if c == cheapest or price[c] - price[cheapest] <= bandf(cheapest, c)]
    return min(tieset, key=tie_order.index), q, tieset

# Drill (i): a never-picked QUALIFIER flips the pick through the tie set's anchor.
price = {'I': 100, 'q1': 80, 'q2': 84, 'c_new': 78}
B = {frozenset(p): 5 for p in [('I','q1'),('I','q2'),('I','c_new'),('q1','q2'),('q1','c_new'),('q2','c_new')]}
bf = lambda a, b: B[frozenset((a, b))]
order = ['q2', 'q1', 'c_new']     # TIE's declared order (member order etc.): q2 first, c_new last
print('(i) before:', pick('I', ['I', 'q1', 'q2'], price, bf, order))
print('(i) after adding c_new:', pick('I', ['I', 'q1', 'q2', 'c_new'], price, bf, order))

# Drill (i-b): exact price tie between two cheapest qualifiers -> anchor ambiguous; pairwise bands differ.
price2 = {'I': 100, 'a': 80, 'b': 80, 'c': 84}
B2 = {frozenset(p): v for p, v in [(('I','a'),5),(('I','b'),5),(('I','c'),5),(('a','b'),0),(('a','c'),5),(('b','c'),3)]}
bf2 = lambda x, y: B2[frozenset((x, y))]
for anchor in ('a', 'b'):
    ts = [c for c in ('a', 'b', 'c') if c == anchor or price2[c] - price2[anchor] <= bf2(anchor, c)]
    print('(i-b) anchor', anchor, 'tie set', ts)

# "With data" proof: "if c_P qualifies under B the pick is no dearer than it".
price3 = {'inc': 100, 'cs': 70, 'cP': 72, 'c3': 74}
B3 = {frozenset(p): v for p, v in [(('inc','cs'),5),(('inc','cP'),5),(('inc','c3'),5),(('cs','cP'),5),(('cs','c3'),5),(('cP','c3'),5)]}
bf3 = lambda x, y: B3[frozenset((x, y))]
pk = pick('inc', ['inc', 'cs', 'cP', 'c3'], price3, bf3, ['c3', 'cs', 'cP'])
print('(proof) c_P qualifies; pick', pk[0], 'price', price3[pk[0]], 'vs c_P', price3['cP'])

# (iii) a candidate within band of the incumbent but cheapest (pairwise bands differ)
price4 = {'I': 100, 'c': 90, 'q': 93}
B4 = {frozenset(p): v for p, v in [(('I','c'),12),(('I','q'),4),(('c','q'),12)]}
bf4 = lambda x, y: B4[frozenset((x, y))]
print('(iii) pick', pick('I', ['I', 'c', 'q'], price4, bf4, ['c', 'q']))

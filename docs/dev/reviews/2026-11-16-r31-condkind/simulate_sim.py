# SIMULATE critic: an evaluator of the model AS RULED, written from condition_kind.md's TEXT
# (Part I s2, II.1.1, III.1 (a2), III.3 A2). Independent of the lane scripts.
import re, itertools, sys
T, F, U = 'T', 'F', 'U'
def AND(*vs):
    if F in vs: return F
    if U in vs: return U
    return T
# ---- a result row: {'cols': {label: text|None}, 'passes': [ {label: text|None} ] or None (no loop)}
# ---- a SLOT: (label, default) ; default None = no default.  default per ENTRY (a2): COALESCE in the one slot.
def slot_val(row_vals, label, default):
    v = row_vals.get(label)
    if v is None and default is not None: return default
    return v
def num(s):
    try: return int(s)
    except: return None
# a set: python predicate on a tuple of texts (never sees None)
def test_tuple(vals, S):
    if any(v is None for v in vals): return U          # absent-rule (2): a NULL in the tuple -> UNKNOWN
    return T if S(*vals) else F
# dollar reads the REAL row (a2): S may take env
def pass_rows(row, looped):
    """the rows a PLAIN condition is ANDed over: the nested table with the LEFT JOIN row on zero passes;
    a condition naming no looped label reads the match once."""
    if not looped or row['passes'] is None:
        return [dict(row['cols'])]
    ps = row['passes'] or [dict()]                      # LEFT JOIN: zero passes -> one row of NULLs
    out = []
    for p in ps:
        d = dict(row['cols']); d.update(p); out.append(d)
    return out
def inner_rows(row, looped):
    """the rows a GROUP question counts: inner join (no LEFT JOIN row); set-once: the match is the pass."""
    if not looped or row['passes'] is None:
        return [dict(row['cols'])]
    out = []
    for p in row['passes']:
        d = dict(row['cols']); d.update(p); out.append(d)
    return out
class Cond:
    """a condition: slots [(label, default)], S(vals..., env) ; looped = names a looped label"""
    def __init__(s, slots, S, looped_labels=()):
        s.slots = slots; s.S = S; s.looped = any(l in looped_labels for l, _ in slots)
    def one(s, r):
        vals = [slot_val(r, l, d) for l, d in s.slots]
        if any(v is None for v in vals): return U
        try: ok = s.S(*vals, env=r)
        except NullRead: return U
        return T if ok else F
class NullRead(Exception): pass
def dollar(env, lab):
    v = env.get(lab)
    if v is None: raise NullRead()
    return v
def plain(c, row):  return AND(*[c.one(r) for r in pass_rows(row, c.looped)])
def record(cs, row): return AND(*[plain(c, row) for c in cs])     # (a2): a record is exactly the AND of its entries
def count(c, row):  return sum(1 for r in inner_rows(row, c.looped) if c.one(r) == T)
def some(c, row):   return T if count(c, row) >= 1 else F
def none(c, row):   return T if count(c, row) == 0 else F
def all_A2(c, row):
    rs = inner_rows(row, c.looped)
    return T if all(c.one(r) == T for r in rs) else F

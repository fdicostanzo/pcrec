# predarg: the candidate rule put into the in-force walker (WALK1127, loaded by load.py), and a verdict helper.
# Design evidence only; asserts nothing.
#
# The candidate, as put to the owner: "a path never goes through an argument's place. The labels inside an argument
# are reached only by the sender's own names for it, or where the body passes them on by an export list, in which
# case they count as the body's own labels."
#
# Modes of the walker (every mode applies body-own-name, READ1127 "direct" = "wins", and array-gate, "array" =
# "error", the two rulings the documents at the start commit do not carry):
#   now  the walker as it is (an argument's place is a step like any other).
#   A    the carve-out read as a DOOR: a spot whose chain from the start passes an argument's place is dropped unless
#        the place is LISTED: its nearest ancestor that is not itself an argument's place (a parameter passed on to
#        another macro sits in that macro's place) is an export list `[(=) = x]`. The list's alias and the place stay
#        steps between, as the model counts them, so a read through a list "skips".
#   A0   as A, strictly: the place's own parent must be the list (a parameter passed on to another macro is NOT
#        listed by that macro's list).
#   A2   as A, but a place is listed when ANY list stands above it inside the same body (`[(=) = [p = rx]]`).
#   B    as A, and "they count as the body's own labels" read literally: the list, the listed place and the binding
#        or call placed there are not steps (the listed labels sit directly under the call, as the body's own).
import load

NS = load.NS
ORIG_BETWEEN = NS["_between"]
MODE = ["now"]


def _listed(arg, any_above=False, strict=False):
    if strict:
        return arg.parent is not None and arg.parent.k == "list"
    x = arg.parent
    while x is not None and x.k == "arg":
        x = x.parent
    if x is None:
        return False
    if x.k == "list":
        return True
    if not any_above:
        return False
    while x is not None and x.k not in ("call",):
        if x.k == "list":
            return True
        x = x.parent
    return False


def between_c(start, x, P):
    out = ORIG_BETWEEN(start, x, P)
    if MODE[0] == "now":
        return out
    res = []
    for node, betw, gates, walls, chain in out:
        crossed = [n for n in chain[1:] if n.k == "arg"]
        if not all(_listed(n, MODE[0] == "A2", MODE[0] == "A0") for n in crossed):
            continue                                         # the candidate: no path through an argument's place
        if MODE[0] == "B":
            listed = set()
            for n in crossed:
                listed.add(id(n))
                y = n.parent
                while y is not None and y.k == "arg":
                    y = y.parent
                if y is not None:
                    listed.add(id(y))
                for k in n.kids:
                    if k.k in ("use", "call"):
                        listed.add(id(k))
            betw = [n for n in betw if id(n) not in listed]
            gates = [n for n in gates if id(n) not in listed]
        res.append((node, betw, gates, walls, chain))
    return res


NS["_between"] = between_c


def verdict(e, binds, read, mode, array=False):
    MODE[0] = mode
    try:
        v = NS["walk_v27"](e, binds, read, reading={"direct": "wins"}, array=array)
    finally:
        MODE[0] = "now"
    if v[0] == "legal":
        return "legal (%s%s)" % (v[3], "" if v[1] is None else ", %s's %s" % (v[1], v[2]))
    if v[0] == "refused":
        return "ERROR: " + v[1][:170]
    return "unparsed: " + v[1][:60]

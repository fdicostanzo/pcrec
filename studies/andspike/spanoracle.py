"""spanoracle.py -- PCRE2-callout exact-span oracle for X & Y and predicates.

Core idea (lane andspike brief): compile `(?:X)` followed by a callout, run it
ANCHORED from start offset i over the WHOLE subject (lookarounds, \\b, $ see the
real context), and let the callout either
  * record the current position and return 1 (fail here, keep backtracking):
    the run lists every end X reaches from i, in X's own preference order; or
  * return 0 only at position j: "does X match exactly [i, j)?".

Two X & Y implementations, meant to be differenced against each other:
  and_sets  -- (A) enumerate X's ends, keep the first one Y's exact-span check
               accepts; the start loop is ours (leftmost start i).
  and_inline-- (B) ONE unanchored pcre2_match of X whose end callout runs Y's
               exact-span check as a nested pcre2_match: PCRE2 owns the start
               loop, bump-along and every verb.
Both implement the manager's LEANING rule: leftmost start, then X's preference
order among the ends Y also accepts.

Wrapping: `LEAD (?:X)(?(R)|(?C1))`. LEAD is X's own leading start-of-pattern
options, hoisted (they are only legal at the very start). The `(?(R)|...)`
keeps the callout from firing at the end of a whole-pattern recursion (?R)
inside X, where the pattern "ends" at an inner position.
"""
import os
import re

import p2cb as p

# Controls for the sweeps (sweep.py): a sabotaged oracle the checks must catch.
#   order -- reverse each end list;  drop -- lose each list's last end.
SABOTAGE = os.environ.get("ANDSPIKE_SABOTAGE", "")

# Start-of-pattern items (pcre2pattern "pattern start options").
_LEAD = re.compile(r"^(?:\(\*(?:UTF|UCP|NO_[A-Z_]+|LIMIT_[A-Z_]+=\d+|CRLF|CR|LF|ANYCRLF|ANY|NUL|"
                   r"BSR_[A-Z]+|NOTEMPTY(?:_ATSTART)?|CASELESS_RESTRICT|TURKISH_CASING)\))+")
# Verbs whose backtracking behaviour the enumeration cannot honour (see report).
EXCLUDED_VERBS = re.compile(r"\(\*(?:ACCEPT|COMMIT|SKIP|PRUNE|THEN)\b")

END_CALLOUT = 1
START_CALLOUT = 2


def split_lead(x):
    m = _LEAD.match(x)
    return (m.group(0), x[m.end():]) if m else ("", x)


def wrapped(x, start_callout=False, recursion_guard=True):
    lead, body = split_lead(x)
    head = "(?(R)|(?C%d))" % START_CALLOUT if start_callout else ""
    tail = "(?(R)|(?C%d))" % END_CALLOUT if recursion_guard else "(?C%d)" % END_CALLOUT
    return lead + head + "(?:" + body + ")" + tail


class Oracle:
    def __init__(self, utf=False, opts=0, match_limit=10_000_000, callout_cap=1_000_000,
                 recursion_guard=True, no_opt=True):
        self.utf = utf
        self.copts = opts | (p.UTF if utf else 0) | (p.NO_OPT if no_opt else 0)
        self.match_limit = match_limit
        self.callout_cap = callout_cap
        self.recursion_guard = recursion_guard
        self._cache = {}
        self.stats = {"callouts": 0, "matches": 0}

    # -- helpers ---------------------------------------------------------
    def enc(self, s):
        return s.encode("utf-8") if self.utf else s.encode("latin-1")

    def code(self, x, start_callout=False):
        key = (x, start_callout)
        c = self._cache.get(key)
        if c is None:
            c = self._cache[key] = p.Code(wrapped(x, start_callout, self.recursion_guard), self.copts)
        return c

    def starts(self, sb):
        """Start offsets: every code-unit offset, or every UTF-8 char boundary."""
        if not self.utf:
            return list(range(len(sb) + 1))
        return [k for k in range(len(sb) + 1) if k == len(sb) or (sb[k] & 0xC0) != 0x80]

    def _run(self, c, sb, start, opts, cb):
        self.stats["matches"] += 1
        return c.match(sb, start, opts, cb, match_limit=self.match_limit)

    @staticmethod
    def _status(rc):
        if rc == p.ERROR_NOMATCH:
            return "ok"
        if rc > 0:
            return "accept-bypass"  # the match ended without passing the end callout
        if rc == p.ERROR_CALLOUT:
            return "cap"
        if rc in (p.ERROR_MATCHLIMIT, p.ERROR_DEPTHLIMIT, p.ERROR_HEAPLIMIT):
            return "limit"
        return "error %d" % rc

    # -- (1) enumeration -------------------------------------------------
    def ends(self, x, s, i):
        """Every end X reaches from i, first-occurrence order. Returns dict:
        ends, raw (callout count), kstart (start_match seen at each end's first
        callout -- differs from i only after \\K), status."""
        sb = s if isinstance(s, bytes) else self.enc(s)
        c = self.code(x)
        seen, order, kst = set(), [], []
        n = [0]

        def cb(blk):
            if blk.callout_number != END_CALLOUT:
                return 0
            n[0] += 1
            if n[0] > self.callout_cap:
                return p.ERROR_CALLOUT
            pos = blk.current_position
            if pos not in seen:
                seen.add(pos)
                order.append(pos)
                kst.append(blk.start_match)
            return 1

        rc, _ = self._run(c, sb, i, p.ANCHORED, cb)
        self.stats["callouts"] += n[0]
        if SABOTAGE == "order":
            order = order[::-1]
        elif SABOTAGE == "drop":
            order = order[:-1]
        return {"ends": order, "raw": n[0], "kstart": kst, "status": self._status(rc)}

    # -- (2) exact-span check ---------------------------------------------
    def spans(self, y, s, i, j, isolated=False):
        """Does Y match exactly [i, j) of s? In-context by default; isolated=True
        runs Y on the substring alone (the alternative semantics)."""
        sb = s if isinstance(s, bytes) else self.enc(s)
        if isolated:
            sb, i, j = sb[i:j], 0, j - i
        c = self.code(y)

        def cb(blk):
            if blk.callout_number != END_CALLOUT:
                return 0
            return 0 if blk.current_position == j else 1

        rc, _ = self._run(c, sb, i, p.ANCHORED, cb)
        if rc < 0 and rc != p.ERROR_NOMATCH:
            raise p.Pcre2Error("spans: " + self._status(rc))
        return rc > 0

    # -- (3) X & Y, implementation A (sets) --------------------------------
    def and_sets(self, x, y, s, isolated=False):
        sb = s if isinstance(s, bytes) else self.enc(s)
        for i in self.starts(sb):
            e = self.ends(x, sb, i)
            if e["status"] != "ok":
                return ("status", e["status"], i)
            for j in e["ends"]:
                if self.spans(y, sb, i, j, isolated):
                    return (i, j)
        return None

    # -- (4) X & Y, implementation B (inline: one PCRE2 run of X) ----------
    def and_inline(self, x, y, s):
        sb = s if isinstance(s, bytes) else self.enc(s)
        c = self.code(x, start_callout=True)
        att = [None]

        def cb(blk):
            if blk.callout_number == START_CALLOUT:
                att[0] = blk.current_position  # the attempt start (immune to \K)
                return 0
            return 0 if self.spans(y, sb, att[0], blk.current_position) else 1

        rc, ov = self._run(c, sb, 0, 0, cb)
        if rc > 0:
            return (att[0], ov[0][1])
        if rc == p.ERROR_NOMATCH:
            return None
        return ("status", self._status(rc), None)

    # -- (5) predicate: the match where the predicate holds ----------------
    def pred_match(self, x, pred, s, anchored_at=None):
        """PCRE2 search for X whose end callout evaluates pred(caps, subject):
        the first match, in PCRE2's own backtracking order, where pred holds.
        caps = [(start,end) or None for groups 1..]; returns the ovector."""
        sb = s if isinstance(s, bytes) else self.enc(s)
        c = self.code(x)

        def cb(blk):
            if blk.callout_number != END_CALLOUT:
                return 0
            return 0 if pred(p.caps_of(blk), sb) else 1

        if anchored_at is None:
            rc, ov = self._run(c, sb, 0, 0, cb)
        else:
            rc, ov = self._run(c, sb, anchored_at, p.ANCHORED, cb)
        if rc > 0:
            return ov
        if rc == p.ERROR_NOMATCH:
            return None
        return ("status", self._status(rc))

    # -- callout-free routes (independent cross-checks) --------------------
    def plain_first(self, x, s, i):
        """PCRE2's own anchored match of X at i, no callout: X's first end."""
        sb = s if isinstance(s, bytes) else self.enc(s)
        lead, body = split_lead(x)
        c = p.Code(lead + "(?:" + body + ")", self.copts)
        rc, ov = c.match(sb, i, p.ANCHORED, match_limit=self.match_limit)
        return ov[0][1] if rc > 0 else None

    def _remaining(self, sb, j):
        return len(sb[j:].decode("utf-8")) if self.utf else len(sb) - j

    def lookahead_order(self, x, s, i, limit=64):
        """X's end order rebuilt WITHOUT callouts: the k-th end is PCRE2's own
        match of `(?:X)(?!E1|...|Ek-1)`, where Ej = `(?s:.{r})\\z` pins the
        position by the characters remaining after it."""
        sb = s if isinstance(s, bytes) else self.enc(s)
        lead, body = split_lead(x)
        got = []
        while len(got) < limit:
            excl = "|".join("(?s:.{%d})\\z" % self._remaining(sb, j) for j in got)
            pat = lead + "(?:" + body + ")" + ("(?!" + excl + ")" if got else "")
            rc, ov = p.Code(pat, self.copts).match(sb, i, p.ANCHORED, match_limit=self.match_limit)
            if rc <= 0:
                break
            got.append(ov[0][1])
        return got

    def lookahead_spans(self, y, s, i, j):
        """Exact-span check WITHOUT callouts: `(?:Y)(?=(?s:.{r})\\z)`."""
        sb = s if isinstance(s, bytes) else self.enc(s)
        lead, body = split_lead(y)
        pat = lead + "(?:" + body + ")(?=(?s:.{%d})\\z)" % self._remaining(sb, j)
        rc, _ = p.Code(pat, self.copts).match(sb, i, p.ANCHORED, match_limit=self.match_limit)
        return rc > 0

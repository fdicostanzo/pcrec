"""simvm.py -- a faithful simulator of backrefs_design.md S3.2's emitted
model, in BOTH the refuted and the corrected publication disciplines.

PROVENANCE: the R32 panel's critic `r32eng` wrote this file to test S3.2,
and it is what FOUND E1. Adopted into this lane's committed instruments
with the `publish` axis added, rather than rewritten -- a lane that
re-implements the instrument that refuted it cannot detect that it has
softened it. The original is unchanged below except for the `publish`
parameter and the `pending` array; `publish='open'` reproduces the critic's
run cell for cell.

THE AXIS. `publish='open'` is the model S3.2 described at 4cd461f and the
one emit_vm.c:3813-3835 implements today: A_CAP writes slot[2k] when
control traverses the OPENING position and slot[2k+1] at the CLOSING one.
`publish='close'` is the correction: the opening position goes to a
per-group PENDING slot, and the (start, end) PAIR is published together at
close. Both writes are trailed and exactly restored, in both modes.

WHY THE AXIS EXISTS. Under `open`, while a group is RE-ENTERED on iteration
n > 1, slot[2k] holds iteration n's start and slot[2k+1] holds iteration
n-1's end. Neither is UNSET, so S3.2's two-slot UNSET test passes and the
compare runs on a span that is not a capture -- and when iteration n starts
after iteration n-1 ended, ref_s > ref_e and `ref_e - ref_s` underflows a
size_t in EMITTED code.

Model, exactly as the design specifies it:
  * slot_values[2k] / [2k+1], all PCREC_UNSET (-1) at search start
    (emit_vm.c:4841-4852)
  * A_CAP writes START on traverse of the OPENING position and END on
    traverse of the CLOSING position (emit_vm.c:3813-3835, read at HEAD)
  * every write is TRAILED and undone by EXACT RESTORE of the displaced
    value on backtracking (emit_vm.c:4772-4790, :5075-5081)
  * A_BREF (S3.2) reads the two slots AT THIS INSTANT, fails if either is
    PCREC_UNSET, else compares subject[ref_s:ref_e] at the cursor.
Leftmost-first search, greedy/lazy quantifiers, empty-iteration guard.
"""
UNSET = -1

class N:
    def __init__(s, k, **kw):
        s.k = k
        s.__dict__.update(kw)

def parse(p):
    i = [0]
    ncap = [0]
    def peek():  return p[i[0]] if i[0] < len(p) else None
    def alt():
        parts = [cat()]
        while peek() == '|':
            i[0] += 1; parts.append(cat())
        return parts[0] if len(parts) == 1 else N('alt', xs=parts)
    def cat():
        xs = []
        while True:
            c = peek()
            if c is None or c in '|)': break
            xs.append(quant())
        if not xs: return N('empty')
        return xs[0] if len(xs) == 1 else N('cat', xs=xs)
    def quant():
        a = atom()
        while True:
            c = peek()
            if c == '*': i[0]+=1; lo,hi=0,None
            elif c == '+': i[0]+=1; lo,hi=1,None
            elif c == '?': i[0]+=1; lo,hi=0,1
            elif c == '{':
                j = p.index('}', i[0]); body = p[i[0]+1:j]
                if ',' in body:
                    a1,b1 = body.split(',')
                    lo = int(a1); hi = int(b1) if b1 else None
                else:
                    lo = hi = int(body)
                i[0] = j+1
            else: return a
            greedy = True
            if peek() == '?': i[0]+=1; greedy=False
            elif peek() == '+': raise NotImplementedError('possessive')
            a = N('rep', x=a, lo=lo, hi=hi, greedy=greedy)
        return a
    def atom():
        c = p[i[0]]
        if c == '(':
            if p.startswith('(?:', i[0]):
                i[0]+=3; x = alt(); assert p[i[0]]==')'; i[0]+=1
                return x
            assert p[i[0]+1] != '?', 'unsupported group ' + p[i[0]:i[0]+4]
            i[0]+=1; ncap[0]+=1; n = ncap[0]
            x = alt(); assert p[i[0]]==')'; i[0]+=1
            return N('cap', n=n, x=x)
        if c == '\\':
            d = p[i[0]+1]
            if d.isdigit() and d != '0':
                i[0]+=2; return N('bref', n=int(d))
            if d == 'w': i[0]+=2; return N('cls', f=lambda ch: ch.isalnum() or ch=='_')
            if d == 's': i[0]+=2; return N('cls', f=lambda ch: ch in ' \t\n')
            i[0]+=2; return N('lit', c=d)
        if c == '.':
            i[0]+=1; return N('cls', f=lambda ch: ch != '\n')
        if c == '^': i[0]+=1; return N('bol')
        if c == '$': i[0]+=1; return N('eol')
        if c == '[':
            j = i[0]+1; neg = False
            if p[j]=='^': neg=True; j+=1
            items=[]; 
            while p[j] != ']':
                if p[j+1]=='-' and p[j+2] != ']':
                    items.append((p[j], p[j+2])); j+=3
                else:
                    items.append((p[j],p[j])); j+=1
            j+=1; i[0]=j
            def f(ch, items=items, neg=neg):
                r = any(a<=ch<=b for a,b in items)
                return (not r) if neg else r
            return N('cls', f=f)
        i[0]+=1; return N('lit', c=c)
    r = alt()
    assert i[0]==len(p), 'trailing ' + p[i[0]:]
    return r, ncap[0]

def run(pat, subj, start=0, caseless=False, publish='close'):
    assert publish in ('open', 'close')
    ast, ncap = parse(pat)
    slots = [UNSET]*(2*ncap+2)
    # The corrected model's extra state: ONE pending-start slot per group.
    # Trailed and exactly restored exactly as slots are -- the cost S3.2
    # prices is this array plus one extra trailed write per traverse.
    pending = [UNSET]*(ncap+1)
    fold = (lambda c: c.lower()) if caseless else (lambda c: c)
    n = len(subj)
    OOB = ['no']
    def m(node, pos, k):
        t = node.k
        if t=='empty': return k(pos)
        if t=='lit':
            return k(pos+1) if pos<n and fold(subj[pos])==fold(node.c) else False
        if t=='cls':
            return k(pos+1) if pos<n and node.f(subj[pos]) else False
        if t=='bol': return k(pos) if pos==0 else False
        if t=='eol': return k(pos) if pos==n else False
        if t=='cat':
            xs = node.xs
            def step(j, p_):
                if j==len(xs): return k(p_)
                return m(xs[j], p_, lambda q, j=j: step(j+1, q))
            return step(0,pos)
        if t=='alt':
            for x in node.xs:
                if m(x,pos,k): return True
            return False
        if t=='cap':
            i0, i1 = 2*node.n, 2*node.n+1
            if publish == 'open':
                old0 = slots[i0]; slots[i0] = pos      # WRITE ON OPEN TRAVERSE
                def close(q):
                    old1 = slots[i1]; slots[i1] = q    # WRITE ON CLOSE TRAVERSE
                    if k(q): return True
                    slots[i1] = old1                   # EXACT RESTORE
                    return False
                if m(node.x, pos, close): return True
                slots[i0] = old0                       # EXACT RESTORE
                return False
            # publish == 'close': the open position is PENDING, and the PAIR
            # is published together at close. A single pending slot per group
            # suffices because a group cannot be open twice at once without
            # recursion, which this module does not implement.
            oldp = pending[node.n]; pending[node.n] = pos   # PENDING (trailed)
            def close_c(q):
                old0, old1 = slots[i0], slots[i1]
                slots[i0] = pending[node.n]            # PUBLISH THE PAIR
                slots[i1] = q                          # ... together
                if k(q): return True
                slots[i0], slots[i1] = old0, old1      # EXACT RESTORE, both
                return False
            if m(node.x, pos, close_c): return True
            pending[node.n] = oldp                     # EXACT RESTORE
            return False
        if t=='bref':
            rs, re_ = slots[2*node.n], slots[2*node.n+1]
            if rs==UNSET or re_==UNSET: return False
            L = re_ - rs
            if L < 0:
                OOB[0] = 'REVERSED SPAN ref_s=%d ref_e=%d' % (rs,re_)
                return False        # a real artifact would over-read here
            if pos+L > n: return False
            if [fold(c) for c in subj[pos:pos+L]] != [fold(c) for c in subj[rs:re_]]:
                return False
            return k(pos+L)
        if t=='rep':
            lo, hi, greedy = node.lo, node.hi, node.greedy
            def rep(cnt, p_):
                can_more = (hi is None or cnt < hi)
                def more():
                    if not can_more: return False
                    return m(node.x, p_, lambda q: False if (q==p_ and cnt>=lo) else rep(cnt+1,q))
                def stop():
                    return k(p_) if cnt>=lo else False
                if greedy:
                    return more() or stop()
                return stop() or more()
            return rep(0,pos)
        raise Exception(t)
    for st in range(start, n+1):
        for i_ in range(len(slots)): slots[i_] = UNSET
        for i_ in range(len(pending)): pending[i_] = UNSET
        res = []
        if m(ast, st, lambda q: (res.append(q), True)[1]):
            groups = tuple(None if slots[2*g]==UNSET or slots[2*g+1]==UNSET
                           else (slots[2*g], slots[2*g+1]) for g in range(1,ncap+1))
            return ((st,res[0]), groups), OOB[0]
    return None, OOB[0]

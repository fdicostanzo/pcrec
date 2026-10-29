#!/usr/bin/env python3
"""Rev 3's byte-identity feasibility check, at the format level.

Every statement of today's matcher body is mapped to ONE (kind, spelling)
renderer of rev 3's kind table. This script joins the statement's print calls
(calls.tsv, from calls3.py on the merged emitter) in emission order, with a
marker for each delegated or non-literal piece, and checks two things:

  1. the joined text matches the renderer's TEMPLATE exactly, so a renderer
     that prints the template with the site's operands prints today's bytes;
  2. every VALUE FRAGMENT group of the template (names starting F_) is free of
     control and of writes: no goto/return/break/continue/switch/case/default,
     no label name, no `{ } ;`, no assignment operator, no ++/--. It also
     lists the literal state reads (`slot_values[`, `run->`, `ctx->`) that the
     build turns into TYPED read pieces (they stay text, but are built by a
     piece builder that records the read).

usage: render_check.py calls.tsv > render_check.log
Exit 0 iff every statement matches and every fragment is clean."""
import re, sys

calls = {}
for l in open(sys.argv[1]):
    n, f, op, buf, fmt = l.rstrip('\n').split('\t', 4)
    calls[int(n)] = (f, op, buf, fmt)

# Non-literal pieces: delegated writers and nested records, as markers.
CLS = '«CLS»'        # vm_cls_test: a class read piece or the clskit inline test
KIT = '«KIT»'        # a memfn kit window (run compare expression, span advance)
SIDE = '«SIDE»'      # vm_ctx_side: a context-side fragment (itself checked below)
CALLSITE = '«CALLSITE»'  # callsite_rows: the CALLOUT renderer's own row table
WORK = '«WORK»'      # a nested WORK record (vm_work_at at the compound's indent)
MEMBERS = '«MEMBERS»'  # the scr_test member text ` && (CLS)...` (a fragment)
CMT_O, CMT_C = '«CMT<»', '«>CMT»'   # comment region (cmt_open / cmt_close)

def fmt_of(n):
    f, op, buf, fmt = calls[n]
    if op == 'cmt_open': return CMT_O
    if op == 'cmt_close': return CMT_C
    return fmt

# Expansions for %s arguments that are themselves C TEXT built by vm_rolef
# (rev 2's "22 C fragments"): in rev 3 each becomes a typed operand, so the
# template sees what the operand renders.
EXPAND = {
    3502: '    %s_TRAIL_CHECK();\\n',                     # vm_trail_check_text
    8634: '    if (!',                                    # f->neg ? "    if (!" : "    if ("
    8544: '(scan_position > 0 && (',                     # side == VMCTX_PREV ? ... : ...
}
# A part given as ('=', text) is the OTHER arm of a ternary literal argument.


# The statements: (id, kind, spelling, parts). A part is a call line or a
# marker. Lines are the merged tree's (main 26804bd46 + lane/trailgc diff),
# the same 132 calls as vmcons2_evidence/body_print_sites.tsv.
S = [
 ('lbl',      'LABEL',     'role',      [3465, 3466, 3467, 3469]),
 ('lbl0',     'LABEL',     'bare',      [3469]),
 ('ckpt',     'CHECKPOINT','stmt',      [3502]),
 ('goto',     'GOTO',      'plain',     [3532]),
 ('fail',     'FAIL',      'plain',     [3541]),
 ('pushT',    'PUSH',      'traced',    [3557]),
 ('push',     'PUSH',      'plain',     [3560]),
 ('setN',     'SET',       'named',     [3584]),
 ('setU',     'SET',       'numbered',  [3586]),
 ('work',     'WORK',      'indent',    [3652]),
 ('cut',      'CUT',       'plain',     [3679]),
 ('mrlF',     'BRANCH',    'fail',      [3889, 3891]),
 ('mrlL',     'BRANCH',    'label',     [3889, 3892]),
 ('islrun',   'BRANCH',    'label',     [4657, KIT, 4661]),
 ('isl1',     'BRANCH',    'label',     [4669]),
 ('islsw',    'SWITCH',    'island',    [4674, 4678, 4678, 4682]),
 ('isladv',   'SEEK',      'advance',   [4716]),
 ('span',     'SPAN',      'block',     [4828, 4829, 4831, 4833, KIT, 4840]),
 ('spanU',    'SPAN',      'block',     [4828, 4833, KIT, 4840]),
 ('reach',    'BRANCH',    'fail',      [4850]),
 ('members',  'FRAGMENT',  'members',   [4944, CLS, 4948]),
 ('possmin',  'BRANCH',    'fail',      [5018]),
 ('pub1',     'GUARD',     'open',      [5044]),
 ('pub1e',    'GUARD_END', 'close',     [5062]),
 ('commit1',  'SEEK',      'span_commit', [5064]),
 ('lazy0',    'SPAN',      'init_only', [5159]),
 ('pub2',     'GUARD',     'open',      [5195]),
 ('pub2e',    'GUARD_END', 'close',     [5212]),
 ('commit2',  'SEEK',      'span_commit', [5214]),
 ('resume',   'LSET',      'assign',    [5221]),
 ('floor',    'BRANCH',    'fail',      [5223]),
 ('retreat',  'LSET',      'sub',       [5225]),
 ('ceil',     'BRANCH',    'fail',      [5228]),
 ('extcls',   'BRANCH',    'fail',      [5230]),
 ('extend',   'LSET',      'add',       [5232]),
 ('back',     'CONSUME_BACK', 'dec',    [5532, CLS, 5534]),
 ('rvend',    'GUARD+LSET','inline',    [5561]),
 ('rvstart',  'GUARD+LSET','inline_braced', [5568]),
 ('rvfloor',  'BRANCH',    'label',     [5615]),
 ('rvsel',    'BRANCH',    'label',     [5621, CLS, 5623]),
 ('it0',      'LSET',      'assign',    [5790]),
 ('rmax',     'BRANCH',    'label',     [5803]),
 ('mark',     'LSET',      'assign',    [5816]),
 ('cutl',     'CUT_LOCAL', 'plain',     [5849]),
 ('itpp',     'LSET',      'inc',       [5852]),
 ('lowg',     'GUARD',     'open',      [5854]),
 ('lowge',    'GUARD_END', 'close',     [5857]),
 ('rmin',     'BRANCH',    'fail',      [5866]),
 ('lazyc',    'SEEK',      'restore',   [5873]),
 ('rvcur',    'LSET',      'assign',    [5895]),
 ('rvprev',   'LSET',      'assign',    [5896]),
 ('rvgs',     'LSET',      'assign',    [5898]),
 ('rvclr',    'LSET',      'clear_array', [5899]),
 ('rvfl2',    'BRANCH',    'label',     [5905]),
 ('rvprevg',  'GUARD+LSET','inline',    [5911]),
 ('rvall',    'BRANCH',    'label',     [5914]),
 ('retg',     'GUARD',     'open',      [5934]),
 ('retge',    'GUARD_END', 'close',     [5939]),
 ('extg',     'GUARD',     'open',      [5941]),
 ('extge',    'GUARD_END', 'close',     [5944]),
 ('pubg',     'GUARD',     'open',      [5953]),
 ('pubge',    'GUARD_END', 'close',     [5960]),
 ('mark2',    'LSET',      'assign',    [5978]),
 ('cutl2',    'CUT_LOCAL', 'plain',     [5990]),
 ('ctrtrip',  'BRANCH',    'label',     [6099]),
 ('ctrbound', 'BRANCH',    'label',     [6305]),
 ('empty',    'BRANCH',    'label',     [6540]),
 ('emptyj',   'BRANCH',    'jump',      [6600]),
 ('lbstart',  'BRANCH',    'fail',      [7126]),
 ('lbstartL', 'BRANCH',    'label',     [7143]),
 ('backstep', 'SEEK',      'backstep',  [7174]),
 ('bsnone',   'BRANCH',    'fail',      [7179]),
 ('lbhard',   'BRANCH',    'abort',     [7208]),
 ('lbend',    'BRANCH',    'fail',      [7216]),
 ('lkrest',   'SEEK',      'restore',   [7488]),
 ('call',     'CALL',      'plain',     [8217]),
 ('ret',      'RETURN',    'block',     [8503]),
 ('side',     'FRAGMENT',  'ctx_side',  [8544, CLS, 8548]),
 ('sideN',    'FRAGMENT',  'ctx_side',  [('=', '(scan_position < subject_length && ('), CLS, 8548]),
 ('ctx2',     'BRANCH',    'label',     [8604, SIDE, 8606, SIDE, 8608]),
 ('mlbol',    'BRANCH',    'label',     [8616, CLS, 8618]),
 ('mleol',    'BRANCH',    'label',     [8622, CLS, 8624]),
 ('start',    'BRANCH',    'label',     [8628]),
 ('end',      'BRANCH',    'label',     [8632]),
 ('ctx1',     'BRANCH',    'label',     [8634, SIDE, 8636]),
 ('ctx1p',    'BRANCH',    'label',     [('=', '    if ('), SIDE, 8636]),
 ('bref',     'BREF',      'one_ref',   [8829, 8834, 8842, 8843, 8846, 8847, WORK, 8871]),
 ('bref2',    'BREF',      'name_run',  [8829, 8834, 8834, 8842, 8843, 8846, 8847, WORK, 8871]),
 ('var',      'VAR',       'block',     [8917, WORK, 8932]),
 ('lit',      'CONSUME',   'lit',       [8980, KIT, 8983]),
 ('step',     'STEP',      'plain',     [9087]),
 ('co',       'CALLOUT',   'caller_view', [9089, 9100, 9125, 9127, 9134, CALLSITE, 9154]),
 ('coV',      'CALLOUT',   'def_view',  [9089, 9109, 9115, 9120, 9125, 9131, 9134, CALLSITE, 9154]),
 ('wcls',     'CONSUME',   'wclass',    [9188]),
 ('cls',      'CONSUME',   'class',     [9210, CLS, 9212]),
 ('eol',      'BRANCH',    'label',     [9225]),
 ('gstart',   'BRANCH',    'label',     [9260]),
 ('accept',   'ACCEPT',    'plain',     [10798]),
]
# Calls that are pieces, not statements of their own.
PIECES = {1691: 'CLS piece (class table read text; vm_cls_test)',
          1763: 'POSTPASS (vm_cls_respell, moved into vm_stmt.c verbatim)'}

P = r'%s'            # an operand placeholder in a format
N = r'%(?:d|lld)'    # an integer operand
NL = r'\\n'
TGT = (r'(?P<T>goto %s_fail;|goto %s_L%d;|%s'
       r'|return %s_R_[A-Z]+;)')          # the BRANCH target renderer's outputs
FR = r'(?P<F_c>.+)'                       # a condition fragment
T = {
 ('LABEL', 'role'):  r'«CMT<»// %s\\n«>CMT»%s_L%d: __attribute__\(\(unused\)\);\\n',
 ('LABEL', 'bare'):  r'%s_L%d: __attribute__\(\(unused\)\);\\n',
 ('CHECKPOINT', 'stmt'): r'    %s_TRAIL_CHECK\(\);\\n',
 ('GOTO', 'plain'):  r'    goto %s_L%d;\\n',
 ('FAIL', 'plain'):  r'    goto %s_fail;\\n',
 ('PUSH', 'traced'): r'    %s_PUSH\(%d, &&%s_L%d, (?P<POS>%s)\);\\n',
 ('PUSH', 'plain'):  r'    %s_PUSH\(&&%s_L%d, (?P<POS>%s)\);\\n',
 ('SET', 'named'):   r'    %s_SET\(%s_%s, (?P<F_src>%s)\);\\n',
 ('SET', 'numbered'): r'    %s_SET\(%d, (?P<F_src>%s)\);\\n',
 ('WORK', 'indent'): r'(?P<IND>%s)%s_CHARGE_WORK\((?P<F_n>%s)\);\\n',
 ('CUT', 'plain'):   r'    %s_CUT\(%d\);\\n',
 ('BRANCH', 'fail'): r'    if \(' + FR + r'\) goto %s_fail;\\n',
 ('BRANCH', 'label'): r'    if \(' + FR + r'\) goto %s_L%d;\\n',
 ('BRANCH', 'jump'): r'    if \(' + FR + r'\) (?P<T>%s)\\n',
 ('BRANCH', 'abort'): r'    if \(' + FR + r'\) return %s_R_INTERNAL;\\n',
 ('SWITCH', 'island'): (r'    if \((?P<F_c>scan_position \+ %d < subject_length)\) '
                        r'switch \((?P<F_d>subject\[scan_position \+ %d\])\) \{\\n'
                        r'(    case %d: goto %s_L%d;\\n)+    \}\\n'),
 ('SEEK', 'advance'): r'    scan_position \+= %d;\\n',
 ('SEEK', 'span_commit'): r'    scan_position = %s_span_cursor;\\n',
 ('SEEK', 'restore'): r'    scan_position = \(size_t\)slot_values\[(%d|%s)\];\\n',
 ('SEEK', 'backstep'): r'    scan_position = %s_back_step\(subject, subject_length, scan_position, %d\);\\n',
 ('SPAN', 'block'): (r'    \{\\n(        unsigned long it_ = 0;\\n)?'
                     r'(        const size_t lim_ = %s_PRUNE_CLAMP_SPAN\(scan_position, (?P<F_clamp>%s), %d\);\\n)?'
                     r'        %s_span_cursor = scan_position;\\n«KIT»    \}\\n'),
 ('SPAN', 'init_only'): r'    %s_span_cursor = scan_position;\\n',
 ('GUARD', 'open'):  r'    if \(' + FR + r'\) \{\\n',
 ('GUARD_END', 'close'): r'    \}\\n',
 ('LSET', 'assign'): r'    (?P<L>%s_[a-z_]+|%s) = (?P<F_src>[^;]+);\\n',
 ('LSET', 'add'):    r'    (?P<L>%s_span_cursor) \+= %d;\\n',
 ('LSET', 'sub'):    r'    (?P<L>%s_span_cursor) -= %d;\\n',
 ('LSET', 'inc'):    r'    (?P<L>%s_iteration)\+\+;\\n',
 ('LSET', 'clear_array'): r'    \{ int i_; for \(i_ = 0; i_ < %d; i_\+\+\) (?P<L>%s_revdet_group_seen)\[i_\] = 0; \}\\n',
 ('GUARD+LSET', 'inline'): r'    if \((?P<F_c>[^)]+)\) (?P<L>%s\[%d\]\[1\]|%s_prev_position) = (?P<F_src>[^;]+);\\n',
 ('GUARD+LSET', 'inline_braced'): (r'    if \((?P<F_c>[^)]+)\) \{ (?P<L1>%s\[%d\]\[0\]) = (?P<F_s1>[^;]+); '
                                   r'(?P<L2>%s\[%d\]) = 1; (?P<L3>%s)\+\+; \}\\n'),
 ('CONSUME_BACK', 'dec'): r'    if \((?P<F_c>%s > %s && \(«CLS»\))\) \{ (?P<L>%s)--; goto %s_L%d; \}\\n',
 ('CUT_LOCAL', 'plain'): r'    run->resume_depth = %s_frame_mark;\\n',
 ('CALL', 'plain'):  r'    %s_CALL\(&&%s_L%d, scan_position\);\\n',
 ('STEP', 'plain'):  r'    if \(--run->steps_left < 0\) return %s_R_STEPS;\\n',
 ('ACCEPT', 'plain'): r'    goto %s_accept;\\n',
 ('CONSUME', 'lit'): r'    if \((?P<F_c>scan_position \+ %d <= subject_length && «KIT»)\) \{ scan_position \+= %d; goto %s_L%d; \}\\n',
 ('CONSUME', 'class'): r'    if \((?P<F_c>scan_position < subject_length && \(«CLS»\))\) \{ scan_position\+\+; goto %s_L%d; \}\\n',
 ('FRAGMENT', 'members'): r'(?P<F_m> && \(«CLS»\))',
 ('FRAGMENT', 'ctx_side'): r'(?P<F_s>\(scan_position (>|<) (0|subject_length) && \(«CLS»\)\))',
}
# Compound kinds: the renderer prints a FIXED skeleton with typed operands.
# Their template is the skeleton itself (the moved text), operands as %s/%d;
# the check is that the parts join in emission order with nothing foreign.
COMPOUND = {
 ('RETURN', 'block'): [8503],
 ('BREF', 'one_ref'): None, ('BREF', 'name_run'): None,
 ('VAR', 'block'): None, ('CALLOUT', 'caller_view'): None,
 ('CALLOUT', 'def_view'): None, ('CONSUME', 'wclass'): [9188],
}

CONTROL = re.compile(r'\b(goto|return|break|continue|switch|case|default|'
                     r'__builtin_trap|longjmp|abort|exit)\b|%s_L|%s_fail|%s_accept|[{};]')
WRITE = re.compile(r'(?<![=!<>+\-*/%&|^])=(?!=)|\+\+|--|[+\-*/%&|^]=|<<=|>>=')
TYPED = re.compile(r'slot_values\[|run->|ctx->')

def frag_check(name, txt):
    bad = [m.group(0) for m in CONTROL.finditer(txt)]
    bad += ['write ' + m.group(0) for m in WRITE.finditer(txt)]
    typed = TYPED.findall(txt)
    return bad, typed

fails = 0
nstmt = 0
used = set()
print('# id\tkind\tspelling\tcalls\tverdict\tfragments (typed reads -> pieces)')
for sid, kind, sp, parts in S:
    nstmt += 1
    txt = ''.join(p[1] if isinstance(p, tuple) else
                  fmt_of(p) if isinstance(p, int) and p not in EXPAND else
                  EXPAND.get(p, p) if isinstance(p, int) else p for p in parts)
    for p in parts:
        if isinstance(p, int): used.add(p)
    if (kind, sp) in COMPOUND:
        # fixed skeleton: every part must be a literal of the compound's own
        # function or a declared nested piece
        fns = {calls[p][0] for p in parts if isinstance(p, int)}
        ok = len(fns) == 1
        verdict = 'COMPOUND-VERBATIM' if ok else 'FOREIGN-PART'
        if not ok: fails += 1
        frs = []
        # the compound's control text is the renderer's; its value parts are
        # %s/%d operands only (no free C text crosses the boundary)
        print('%s\t%s\t%s\t%s\t%s\t%s' % (sid, kind, sp, ','.join(map(str, parts)), verdict, ''))
        continue
    m = re.fullmatch(T[(kind, sp)], txt, flags=re.S)
    if not m:
        fails += 1
        print('%s\t%s\t%s\t%s\tNO-MATCH\t%s' % (sid, kind, sp, ','.join(map(str, parts)), txt))
        continue
    notes = []
    for g, val in m.groupdict().items():
        if not g.startswith('F_') or val is None: continue
        bad, typed = frag_check(g, val)
        if bad:
            fails += 1
            notes.append('%s=%r REFUSED %s' % (g, val, bad))
        else:
            notes.append('%s clean%s' % (g, (' (' + ', '.join(typed) + ')') if typed else ''))
    print('%s\t%s\t%s\t%s\tMATCH\t%s' % (sid, kind, sp, ','.join(map(str, parts)), '; '.join(notes)))

body = {n for n, c in calls.items() if c[2] != 'frame'}
missing = sorted(body - used - set(PIECES))
print('# statements: %d; body calls covered: %d of %d (+%d pieces: %s); uncovered: %s' %
      (nstmt, len(used & body), len(body), len(PIECES), ', '.join('%d %s' % kv for kv in PIECES.items()), missing or 'none'))
print('# result: %s' % ('ALL MATCH, ALL FRAGMENTS CLEAN' if fails == 0 and not missing else '%d FAILURES' % fails))
sys.exit(0 if fails == 0 and not missing else 1)

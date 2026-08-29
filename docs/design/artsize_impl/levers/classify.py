#!/usr/bin/env python3
"""Measurement-only classifier for the three ART-SIZE STEP2 levers.
Operates purely on emitted artifact TEXT (never recompiles, never touches src/tests).
"""
import re, sys, json, statistics

LABEL_RE = re.compile(r'^rx_L(\d+): __attribute__\(\(unused\)\);\s*$')
ROLE_RE = re.compile(r'^// (.*)$')
GOTO_RE = re.compile(r'goto rx_L(\d+);')
ADDR_RE = re.compile(r'&&rx_L(\d+)')
PRUNE_RE = re.compile(r'RX_PRUNE_TOO_SHORT\(([^;]*?)\)(?=[,;)])')
# a full RX_PRUNE_TOO_SHORT(...) call; args may contain nested parens, so
# do a manual paren-matching scan instead of relying on the regex above.

def find_prune_calls(text):
    out = []
    i = 0
    marker = "RX_PRUNE_TOO_SHORT("
    while True:
        j = text.find(marker, i)
        if j < 0:
            break
        k = j + len(marker)
        depth = 1
        start_args = k
        while depth > 0 and k < len(text):
            if text[k] == '(':
                depth += 1
            elif text[k] == ')':
                depth -= 1
            k += 1
        call_text = text[j:k]  # includes trailing ')'
        args = text[start_args:k-1]
        out.append((j, k, call_text, args))
        i = k
    return out


def lever1(lines, prefix):
    """Span-loop shared-helper lever.
    Site anchor: a label whose role comment is exactly 'span-loop cursor ...'.
    A site's block runs from that label through the last label in the
    contiguous run of span-loop-family roles that follow
    ('span-loop:', 'span-loop retreat', 'span-loop extend'), i.e. up to
    (not including) the next label whose role is NOT one of those three
    continuation phrases (including a fresh 'span-loop cursor' entry,
    which starts a new site).
    """
    n = len(lines)
    # index label lines with their preceding role comment (if any)
    label_idx = []  # (line_no, role_text_or_None)
    for i, ln in enumerate(lines):
        m = LABEL_RE.match(ln)
        if m:
            role = None
            if i > 0:
                rm = ROLE_RE.match(lines[i-1])
                if rm:
                    role = rm.group(1)
            label_idx.append((i - (1 if role is not None else 0), i, role))

    CONT_PREFIXES = ("span-loop: ", "span-loop retreat", "span-loop extend")
    sites = []  # dict: start_line, end_line(exclusive), stride, mode, sig
    k = 0
    N = len(label_idx)
    while k < N:
        start_comment_line, lbl_line, role = label_idx[k]
        if role is None or not role.startswith("span-loop cursor"):
            k += 1
            continue
        # parse role: "span-loop cursor {m,n}, stride S, greedy|lazy[, POSSESSIFIED...]"
        rm = re.match(r'span-loop cursor (\{[^}]*\}), stride (\d+), (greedy|lazy)(.*)$', role)
        stride = int(rm.group(2)) if rm else None
        gl = rm.group(3) if rm else None
        poss = bool(rm and 'POSSESSIFIED' in rm.group(4))
        mode = ('poss' if poss else gl)
        block_start = start_comment_line
        # scan forward through contiguous continuation labels
        j = k + 1
        while j < N:
            _, _, r2 = label_idx[j]
            if r2 is not None and any(r2.startswith(p) for p in CONT_PREFIXES):
                j += 1
                continue
            break
        # end of block = just before label_idx[j]'s comment/label start, or EOF
        if j < N:
            end_line = label_idx[j][0]
        else:
            end_line = n
        block_start_line = start_comment_line
        block_text_lines = lines[block_start_line:end_line]
        block_bytes = sum(len(x) + 1 for x in block_text_lines)  # +1 for newline
        # extract class-test signature: first line containing '_span_cursor + '
        # followed by '<=' bound
        sig = None
        for bl in block_text_lines:
            mm = re.search(r'_span_cursor \+ (\d+) <= (subject_length|lim_)(?: && it_ < \d+UL)?(.*)$', bl)
            if mm:
                tail = mm.group(3)
                # trim off the trailing ') {' or ')) goto ..._fail;' control-flow tail
                # keep everything up to (but not including) the final control-flow marker
                tail = re.sub(r'\)\s*\{.*$', '', tail)
                tail = re.sub(r'\)\)\s*goto.*$', '', tail)
                sig = (mm.group(1), tail.strip())
                break
        sites.append({
            'start': block_start_line, 'end': end_line, 'stride': stride,
            'mode': mode, 'sig': sig, 'bytes': block_bytes, 'role': role,
        })
        k = j
    return sites


def lever2(lines):
    """Node-skeleton fold-candidate walk."""
    n = len(lines)
    text_all = "\n".join(lines)
    # address-taken labels (computed-goto / frame push targets)
    addr_taken = set(int(x) for x in ADDR_RE.findall(text_all))
    # incoming goto counts (including inline `if (...) goto rx_LN;` forms)
    goto_counts = {}
    for m in GOTO_RE.finditer(text_all):
        lid = int(m.group(1))
        goto_counts[lid] = goto_counts.get(lid, 0) + 1
    # label lines + whether preceding stmt is unconditional goto/return/break
    labels = []
    for i, ln in enumerate(lines):
        m = LABEL_RE.match(ln)
        if m:
            lid = int(m.group(1))
            # find the previous non-comment, non-blank line
            j = i - 1
            while j >= 0 and (lines[j].strip() == '' or lines[j].strip().startswith('//')):
                j -= 1
            prev = lines[j].strip() if j >= 0 else ''
            # fallthrough is possible unless prev is an unconditional
            # (unguarded) goto/return/break -- a guarded 'if (...) goto X;'
            # still falls through on the false path.
            unconditional_exit = bool(re.match(r'^(goto rx_L\d+;|return\b.*;|break;)$', prev))
            fallthrough_possible = not unconditional_exit
            labels.append((i, lid, fallthrough_possible))
    total_labels = len(labels)
    fold_candidates = 0
    label_line_bytes = []
    goto_line_bytes = []
    for i, ln in enumerate(lines):
        if LABEL_RE.match(ln):
            label_line_bytes.append(len(ln) + 1)
        if 'goto rx_L' in ln:
            goto_line_bytes.append(len(ln) + 1)
    for (i, lid, fallthrough_possible) in labels:
        gc = goto_counts.get(lid, 0)
        if gc == 1 and not fallthrough_possible and lid not in addr_taken:
            fold_candidates += 1
    avg_label_bytes = statistics.mean(label_line_bytes) if label_line_bytes else 0
    avg_goto_bytes = statistics.mean(goto_line_bytes) if goto_line_bytes else 0
    return {
        'total_labels': total_labels,
        'fold_candidates': fold_candidates,
        'addr_taken_count': len(addr_taken & set(l for _, l, _ in labels)),
        'avg_label_bytes': avg_label_bytes,
        'avg_goto_bytes': avg_goto_bytes,
        'total_goto_lines': sum(1 for ln in lines if 'goto rx_L' in ln),
    }


def lever3(text):
    calls = find_prune_calls(text)
    total_bytes = sum(len(c[2]) for c in calls)
    # group by full argument text, and by argument text with the leading
    # additive constant factored out: args look like
    # "scan_position, 59 + (1 * (20 - slot_values[1301]))" -- split on the
    # first top-level comma to get (posexpr, boundexpr), then within
    # boundexpr split "CONST + REST" at the first top-level '+'.
    distinct_full = {}
    distinct_grouped = {}
    for (j, k, call_text, args) in calls:
        # split args at first top-level comma
        depth = 0
        comma_at = None
        for idx, ch in enumerate(args):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            elif ch == ',' and depth == 0:
                comma_at = idx
                break
        posexpr = args[:comma_at].strip() if comma_at is not None else args.strip()
        boundexpr = args[comma_at+1:].strip() if comma_at is not None else ''
        distinct_full.setdefault((posexpr, boundexpr), 0)
        distinct_full[(posexpr, boundexpr)] += 1
        # factor out leading "CONST + " at top level
        mm = re.match(r'^(-?\d+)\s*\+\s*(.*)$', boundexpr)
        if mm:
            const_part, rest = mm.group(1), mm.group(2)
        else:
            const_part, rest = boundexpr, ''
        key = (posexpr, rest)
        distinct_grouped.setdefault(key, [])
        distinct_grouped[key].append(const_part)
    return {
        'count': len(calls),
        'total_bytes': total_bytes,
        'avg_call_bytes': (total_bytes / len(calls)) if calls else 0,
        'distinct_full_exprs': len(distinct_full),
        'distinct_groups_const_factored': len(distinct_grouped),
        'group_sizes': sorted((len(v) for v in distinct_grouped.values()), reverse=True)[:10],
    }


def analyze(path):
    with open(path, 'r', encoding='utf-8', errors='surrogateescape') as f:
        text = f.read()
    lines = text.split('\n')
    # detect prefix (rx by convention but confirm)
    m = re.search(r'^(\w+)_L0: __attribute__', text, re.M)
    prefix = m.group(1) if m else 'rx'

    l1_sites = lever1(lines, prefix)
    l2 = lever2(lines)
    l3 = lever3(text)

    # lever1 aggregate + savings model
    from collections import defaultdict
    shapes = defaultdict(list)
    for s in l1_sites:
        key = (s['stride'], s['mode'], s['sig'])
        shapes[key].append(s)
    n_sites = len(l1_sites)
    n_shapes = len(shapes)
    total_span_bytes = sum(s['bytes'] for s in l1_sites)
    CALL_SITE_BYTES = 50  # midpoint of 40-60B; justified via RX_CALL line length, see report
    HELPER_HEADER_BYTES = 80
    savings = 0
    reused_shapes = 0
    for key, sitelist in shapes.items():
        cnt = len(sitelist)
        if cnt <= 1:
            continue
        reused_shapes += 1
        avg_block = statistics.mean(s['bytes'] for s in sitelist)
        old = sum(s['bytes'] for s in sitelist)
        new = avg_block + HELPER_HEADER_BYTES + cnt * CALL_SITE_BYTES
        savings += max(0, old - new)

    # lever2 savings
    fold_bytes_each = l2['avg_label_bytes'] + l2['avg_goto_bytes']
    lever2_savings = l2['fold_candidates'] * fold_bytes_each

    # lever3 savings: groups with >1 member get one hoist + per-site const compare
    HOIST_COMPARE_BYTES = 40  # a per-site "if (x != CONST)"-shape comparison; conservative
    lever3_savings = 0
    # recompute grouped with sizes to get savings (need avg call bytes per group ~ total/count)
    avg_call = l3['avg_call_bytes']
    for sz in l3['group_sizes']:
        if sz > 1:
            old = sz * avg_call
            new = avg_call + sz * HOIST_COMPARE_BYTES  # one full eval + per-site compare
            lever3_savings += max(0, old - new)

    file_size = len(text)

    return {
        'path': path,
        'file_bytes': file_size,
        'lever1': {
            'sites': n_sites,
            'distinct_shapes': n_shapes,
            'reused_shapes(count>1)': reused_shapes,
            'span_loop_bytes': total_span_bytes,
            'span_loop_pct_of_file': 100.0 * total_span_bytes / file_size if file_size else 0,
            'bytes_saved': savings,
            'pct_saved_of_file': 100.0 * savings / file_size if file_size else 0,
        },
        'lever2': {
            **l2,
            'fold_pct': 100.0 * l2['fold_candidates'] / l2['total_labels'] if l2['total_labels'] else 0,
            'bytes_saved': lever2_savings,
            'pct_saved_of_file': 100.0 * lever2_savings / file_size if file_size else 0,
        },
        'lever3': {
            **l3,
            'bytes_saved': lever3_savings,
            'pct_saved_of_file': 100.0 * lever3_savings / file_size if file_size else 0,
        },
    }


if __name__ == '__main__':
    for p in sys.argv[1:]:
        r = analyze(p)
        print(json.dumps(r))

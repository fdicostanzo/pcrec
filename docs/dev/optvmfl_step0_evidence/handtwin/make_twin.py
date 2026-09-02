#!/usr/bin/env python3
"""Build a direct-branch-dispatcher hand-twin of a VM artifact.

Transform: `rx_frame.resume_label` from `const void *` to `int`; every
`RX_PUSH(&&rx_LN, ...)` call site's first argument from `&&rx_LN` to the
plain integer `N`; and the fail label's `goto *run->resume_stack[
frame_index].resume_label;` from a computed goto into a `switch` over the
label set this artifact's own RX_PUSH sites name. Everything else stays
byte-identical -- this is a targeted substitution, not a re-emission.
"""
import re, sys

def make_twin(src_path, dst_path):
    with open(src_path, "r") as fh:
        text = fh.read()

    # 1. struct field type
    old_field = "typedef struct { const void *resume_label; size_t resume_position; size_t trail_mark; } rx_frame;"
    new_field = "typedef struct { int resume_label; size_t resume_position; size_t trail_mark; } rx_frame;"
    assert old_field in text, "rx_frame typedef not found or already patched"
    text = text.replace(old_field, new_field)

    # 2. push-site labels: &&rx_L<N>  ->  <N>   (only inside RX_PUSH( ... ) calls)
    labels = sorted(set(int(m) for m in re.findall(r'RX_PUSH\(&&rx_L(\d+),', text)))
    assert labels, "no RX_PUSH(&&rx_L... sites found"
    text = re.sub(r'RX_PUSH\(&&rx_L(\d+),', lambda m: f'RX_PUSH({m.group(1)},', text)

    # sanity: no remaining &&rx_fail or other push forms in this population
    remaining = re.findall(r'RX_PUSH\(&&(\w+),', text)
    assert not remaining, f"unhandled RX_PUSH forms: {remaining}"

    # 3. the dispatch line itself
    old_dispatch = "        goto *run->resume_stack[frame_index].resume_label;\n"
    assert old_dispatch in text, "computed-goto dispatch line not found verbatim"
    cases = "\n".join(f"        case {n}: goto rx_L{n};" for n in labels)
    new_dispatch = (
        "        switch (run->resume_stack[frame_index].resume_label) {\n"
        f"{cases}\n"
        "        default: __builtin_unreachable();\n"
        "        }\n"
    )
    text = text.replace(old_dispatch, new_dispatch)

    with open(dst_path, "w") as fh:
        fh.write(text)
    return labels

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    labels = make_twin(src, dst)
    print(f"{dst}: {len(labels)} distinct resume labels: {labels}")

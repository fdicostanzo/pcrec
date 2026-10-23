#!/usr/bin/env bash
# docs/dev/lanes/s3_evidence/list_axes_delta.sh REF_PCREC NEW_PCREC — D172 S3's `--list-axes`
# delta held to the declared manifest beside this script (list_axes_delta.tsv), both ways.
# Exit 0 iff the real delta equals the declared one. Reads only the two listings.
set -u
export LC_ALL=C
MAN="$(cd "$(dirname "$0")" && pwd)/list_axes_delta.tsv"
key() {   # a listing line -> its identity key
    awk -F'\t' '$2 == "deny" || $2 == "pair" { print "memfn\t" $1; next } { print $1 "\t" $2 "\t" $3 }'
}
diff <("$1" --list-axes) <("$2" --list-axes) > /dev/null && { echo "list-axes delta: none (the manifest declares some)"; exit 1; }
real=$( { diff <("$1" --list-axes) <("$2" --list-axes) | sed -n 's/^< //p' | key | sed 's/^/-\t/';
          diff <("$1" --list-axes) <("$2" --list-axes) | sed -n 's/^> //p' | key | sed 's/^/+\t/'; } | sort)
decl=$(grep -v '^#' "$MAN" | sort)
if [ "$real" = "$decl" ]; then
    echo "list-axes delta: $(printf '%s\n' "$real" | wc -l) row(s), exactly as declared"
    exit 0
fi
echo "list-axes delta DIFFERS from the declaration:"
diff <(printf '%s\n' "$decl") <(printf '%s\n' "$real") | sed 's/^</  declared, not real:/; s/^>/  real, not declared:/'
exit 1

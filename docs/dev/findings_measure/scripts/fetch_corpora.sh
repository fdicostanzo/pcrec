#!/bin/sh
# Fetches the two corpora NOT committed here (ambiguous redistribution
# licence, R29/Q9) into ../corpora/, and verifies each against manifest.tsv's
# sha256. web_request.txt and prose.txt are already committed (Apache-2.0 /
# public domain) and this script does not touch them.
#
# Run from anywhere; paths are relative to this file.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
FM=$(dirname "$HERE")
CORPORA="$FM/corpora"
mkdir -p "$CORPORA"

fetch_and_check() {
    url=$1; out=$2; want_sha=$3
    echo "fetching $url -> $out"
    curl -sS -m 30 -o "$out" "$url"
    got_sha=$(shasum -a 256 "$out" | awk '{print $1}')
    if [ "$got_sha" != "$want_sha" ]; then
        echo "SHA256 MISMATCH for $out: got $got_sha want $want_sha" >&2
        echo "(the manifest is stale, or the upstream file changed -- do not" >&2
        echo " use this file for a re-run without re-checking the manifest)" >&2
        exit 1
    fi
    echo "  ok: $got_sha"
}

# log_lines: loghub HDFS_2k.log sample (logpai/loghub) -- "freely available
# for research or academic work", not a clearly permissive redistribution
# licence (R29), so kept out of the repo and re-fetched here.
fetch_and_check \
    "https://raw.githubusercontent.com/logpai/loghub/master/HDFS/HDFS_2k.log" \
    "$CORPORA/log_lines.txt" \
    "7c967000980c086ed55fa6544ba4f05fe66d44622795e890c68caf8bbb635035"

# json: three JSONPlaceholder mock-API endpoints, concatenated and trimmed
# to 1MB (no explicit open licence found at fetch time, R29 kept manifest-
# only). Re-derive the exact 1MB trim byte-for-byte via build_json_corpus.py.
curl -sS -m 30 -o "$CORPORA/.json1.raw" "https://jsonplaceholder.typicode.com/comments"
curl -sS -m 30 -o "$CORPORA/.json2.raw" "https://jsonplaceholder.typicode.com/posts"
curl -sS -m 30 -o "$CORPORA/.json3.raw" "https://jsonplaceholder.typicode.com/users"
python3 "$HERE/build_json_corpus.py" "$CORPORA/.json1.raw" "$CORPORA/.json2.raw" \
    "$CORPORA/.json3.raw" "$CORPORA/json.txt"
rm -f "$CORPORA/.json1.raw" "$CORPORA/.json2.raw" "$CORPORA/.json3.raw"
got_sha=$(shasum -a 256 "$CORPORA/json.txt" | awk '{print $1}')
echo "json.txt sha256 (informational, source API is not static/versioned so"
echo "  this will legitimately drift on re-fetch): $got_sha"

echo "done. log_lines.txt and json.txt are in $CORPORA (gitignored)."

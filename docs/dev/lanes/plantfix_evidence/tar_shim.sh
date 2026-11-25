#!/bin/bash
# scratch shim (lane plantfix): BSD tar has no --ignore-failed-read; drop it
args=(); for a in "$@"; do [ "$a" = --ignore-failed-read ] || args+=("$a"); done
exec /usr/bin/tar "${args[@]}"

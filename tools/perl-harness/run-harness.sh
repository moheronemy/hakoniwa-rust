#!/bin/sh
# Run stages of the original Perl turn code on a fixture and write the expected
# results used by the Rust comparison tests (see turn_dump.pl).
#
# Usage: tools/perl-harness/run-harness.sh FIXTURE STEPS
#   FIXTURE  directory name under crates/hakoniwa-core/tests/fixtures
#   STEPS    comma separated, e.g. estimate,estimate,income,commands
# Writes FIXTURE.rand<D>.expected.json for each D in $RANDS (default "0 50"),
# with rand() pinned to the number 0.D (e.g. 0 -> 0, 50 -> 0.5, 03125 -> 1/32).
# Use exact binary fractions so that Rust's generator can produce the same value.
set -eu
root=$(cd "$(dirname "$0")/../.." && pwd)
fixture="$root/crates/hakoniwa-core/tests/fixtures/$1"
steps=$2
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# hako-main.cgi: keep the settings and the subs, drop the top-level main code
awk '/require\(\$jcode\)/ { skip = 1 } skip && /^sub / { skip = 0 } !skip { print }' \
  "$root/hako-r-a_FE/hako-main.cgi" > "$work/main.pl"
cp "$root/hako-r-a_FE/hako-turn.cgi" "$work/turn.cgi"

cd "$work"
for r in ${RANDS:-0 50}; do
  rm -rf data && cp -r "$fixture" data
  out="$fixture.rand$r.expected.json"
  STEPS="$steps" HAKO_RAND="0.$r" \
    perl "$root/tools/perl-harness/turn_dump.pl" main.pl turn.cgi data 2>/dev/null > "$out"
  echo "wrote ${out#$root/}"
done

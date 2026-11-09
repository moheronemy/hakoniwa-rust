#!/bin/sh
# Regenerate the expected estimate() results for the phase1-mix fixture by
# running the original Perl code (see phase1_dump.pl).
set -eu
root=$(cd "$(dirname "$0")/../.." && pwd)
fixture="$root/crates/hakoniwa-core/tests/fixtures/phase1-mix"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# hako-main.cgi: keep the settings and the subs, drop the top-level main code
awk '/require\(\$jcode\)/ { skip = 1 } skip && /^sub / { skip = 0 } !skip { print }' \
  "$root/hako-r-a_FE/hako-main.cgi" > "$work/main.pl"
cp "$root/hako-r-a_FE/hako-turn.cgi" "$work/turn.cgi"

cd "$work"
for r in 0 50; do
  rm -rf data && cp -r "$fixture" data
  out="$fixture.rand$r.expected.json"
  HAKO_RAND="0.$r" perl "$root/tools/perl-harness/phase1_dump.pl" main.pl turn.cgi data > "$out"
  echo "wrote ${out#$root/}"
done

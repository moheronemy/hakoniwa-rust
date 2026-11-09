#!/bin/sh
# Regenerate crates/hakoniwa-core/src/tables.rs from hako-r-a_FE/hako-main.cgi.
# Requires: perl (with JSON::PP), python3, iconv, rustfmt.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

iconv -f EUC-JP -t UTF-8 "$root/hako-r-a_FE/hako-main.cgi" | tr -d '\r' > "$work/main.cgi"
# Configuration section only (everything before the "# COOKIE" variables block),
# with file-scoped `my` turned into package variables so they can be dumped.
awk '/^# COOKIE$/ { exit } { print }' "$work/main.cgi" \
  | sed 's/^my(\(.*\)) = /\1 = /; s/^my(\(.*\));/our(\1);/' > "$work/config.pl"
echo '1;' >> "$work/config.pl"
perl "$root/tools/dump-perl-config.pl" "$work/config.pl" > "$work/config.json"
python3 -I "$root/tools/gen_tables.py" "$work/config.json" "$work/main.cgi" \
  | rustfmt --edition 2024 > "$root/crates/hakoniwa-core/src/tables.rs"
echo "wrote crates/hakoniwa-core/src/tables.rs"

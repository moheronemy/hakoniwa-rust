use strict; no strict 'vars'; use JSON::PP;
# Usage: perl dump-perl-config.pl CONFIG.pl > config.json
# CONFIG.pl must be UTF-8 Perl that only assigns package variables.
my $code = do { local $/; open(my $fh, '<:raw', $ARGV[0]) or die "open: $!"; <$fh> };
eval "use utf8;\n$code\n;1" or die "load: $@";
binmode STDOUT, ":encoding(UTF-8)";
my %out;
no strict 'refs';
for my $name (sort keys %main::) {
  next if $name =~ /::$/ || $name =~ /^(ENV|INC|ARGV|STDIN|STDOUT|STDERR|_|0|main|JSON|0|@|!)$/ || $name !~ /^[A-Za-z]/;
  my $g = $main::{$name};
  next unless ref(\$g) eq 'GLOB';
  if (defined ${*{$g}{SCALAR}}) { $out{'$'.$name} = ${*{$g}{SCALAR}}; }
  if (*{$g}{ARRAY} && @{*{$g}{ARRAY}}) { $out{'@'.$name} = [@{*{$g}{ARRAY}}]; }
}
print JSON::PP->new->canonical->pretty->encode(\%out);

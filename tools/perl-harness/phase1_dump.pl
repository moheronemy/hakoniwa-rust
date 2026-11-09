#!/usr/bin/perl
# Run the original Perl turn code that phase 1 ported on a legacy data directory and
# dump the results: estimate() twice, then income(), then the command phase.
#
# Usage: perl phase1_dump.pl MAIN.pl TURN.cgi DATA_DIR > expected.json
#   MAIN.pl  : hako-main.cgi without its top-level main code (see run-phase1.sh)
#   TURN.cgi : hako-turn.cgi
#
# Randomness is pinned so the Rust side can reproduce it: rand($n) always returns
# $HAKO_RAND * $n (default 0; rand(0) counts as rand(1), as in Perl), so random($n)
# is int($HAKO_RAND * $n). The shuffled point array is in row-major order.
BEGIN {
    my $r = $ENV{HAKO_RAND} // 0;
    *CORE::GLOBAL::rand = sub { my $n = @_ ? $_[0] : 1; $n = 1 if !$n; $r * $n };
}
use Encode ();
use JSON::PP ();

my ($main_pl, $turn_cgi, $dir) = @ARGV;
for my $f ($main_pl, $turn_cgi) {
    my $path = $f =~ m{^/} ? $f : "./$f";
    do $path;
    die "load $f: $@" if $@;
}

# logHistory appends to a file; collect the lines instead
our @history;
{
    no warnings 'redefine';
    *main::logHistory = sub { push @history, "$HislandTurn,$_[0]" };
}

$HdirName = $dir;
readIslandsFile(-1) or die "readIslandsFile failed";

@Hrpx = ();
@Hrpy = ();
for my $i (0 .. $HpointNumber - 1) {
    push @Hrpx, $i % $HislandSize;
    push @Hrpy, int($i / $HislandSize);
}

my @persisted = qw(pop area farm factory mountain pts money food etc0 eisei1 eisei2
  eisei3 eisei4 eisei5 eisei6 etc5 etc6 etc8 etc9 totoyoso2 kei rena fore tare zipro
  leje monsterlive monsterlivetype anflag auc0 auc4 auc5 auc6 auc9);
my @scratch = qw(shouhi ene sabun con99 factory1 factory2 factoryt oil bas htf shtf
  hou shu sin jin h10 h11 co0 co1 co4 co7 co8 co77 co99 c13 c28 tet m26 m27 m74 m75 m79
  m84 m93 kyu ky2 zoo sci pro sba amu kin tra tra1 tra2 fukeikimoney unemployed
  monsterlive2 kachiten kachitent shoritu styusho teamforce force uni tuni auc0c auc5c
  dead ownfe absent incomemoney);

sub str { my $v = shift; defined $v ? Encode::decode('euc-jp', "$v") : '' }

sub snapshot {
    my @out;
    for my $island (@Hislands) {
        my %h = (id => str($island->{'id'}));
        $h{$_} = str($island->{$_}) for @persisted, @scratch;
        my @values;
        for my $y (0 .. $HislandSize - 1) {
            for my $x (0 .. $HislandSize - 1) {
                push @values, str($island->{'landValue'}[$x][$y]);
            }
        }
        $h{'land_values'} = \@values;
        $h{'commands'} = [map { str($_->{'kind'}) } @{$island->{'command'}}];
        push @out, \%h;
    }
    return \@out;
}

sub pass {
    my ($name) = @_;
    return { name => $name, islands => snapshot(), oyasumiritu => str($oyasumiritu) };
}

my @passes;
for my $pass (1 .. 2) {
    estimate($_) for 0 .. $HislandNumber - 1;
    push @passes, pass("estimate$pass");
}
income($Hislands[$_]) for 0 .. $HislandNumber - 1;
push @passes, pass("income");
for my $i (0 .. $HislandNumber - 1) {
    while (doCommand($Hislands[$i]) == 0) {}
}
my $commands = pass("commands");
# logFlush の順 (機密・遅延・通常、それぞれ新しい順)
$commands->{'logs'} = [map { str($_) }
    reverse(@HsecretLogPool), reverse(@HlateLogPool), reverse(@HlogPool)];
$commands->{'history'} = [map { str($_) } @history];
push @passes, $commands;
print JSON::PP->new->utf8->canonical->pretty->encode(\@passes);

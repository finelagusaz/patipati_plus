use strict;
use warnings;
use Test::More;
use FindBin;
require "$FindBin::Bin/../patipati/sub.pl";

my $today = get_date(time);
like($today, qr/^\d{8}\z/, 'get_date returns 8 digit date');

done_testing;

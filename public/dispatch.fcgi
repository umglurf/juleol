#!/usr/bin/env perl
BEGIN { $ENV{DANCER_APPHANDLER} = 'PSGI'; $ENV{DANCER_ENVIRONMENT} = 'production'}
use Dancer2;
use FindBin '$RealBin';
use Plack::Handler::FCGI;

# For some reason Apache SetEnv directives don't propagate
# correctly to the dispatchers, so forcing PSGI and env here
# is safer.
set apphandler => 'PSGI';
set environment => 'production';

my $psgi = path($RealBin, '..', 'bin', 'app.psgi');
my $app = do($psgi);
die "Unable to read startup script: $@" if $@;
my $server = Plack::Handler::FCGI->new(nproc => 5, listen => ['/var/run/fcgi.sock']);

$server->run($app);

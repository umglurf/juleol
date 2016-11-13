use strict;
use warnings;
use ExtUtils::MakeMaker;

# Normalize version strings like 6.30_02 to 6.3002,
# so that we can do numerical comparisons on it.
my $eumm_version = $ExtUtils::MakeMaker::VERSION;
$eumm_version =~ s/_//;

WriteMakefile(
    NAME                => 'juleol',
    AUTHOR              => q{Håvard Moen <post@haavard.name>},
    VERSION_FROM        => 'lib/juleol.pm',
    ABSTRACT            => 'Christmas beer rating application',
    ($eumm_version >= 6.3001
      ? ('LICENSE'=> 'perl')
      : ()),
    PL_FILES            => {},
    PREREQ_PM => {
        'Test::More' => 0,
        'YAML'       => 0,
        'Dancer2'     => 0.204000,
        'Dancer2::Plugin::DBIC'     => 0,
        'Dancer2::Plugin::Passphrase'     => 0,
        'Dancer2::Plugin::Auth::Tiny'     => 0,
        'Statistics::Basic'     => 0,
        'Try::Tiny'     => 0,
    },
    dist                => { COMPRESS => 'gzip -9f', SUFFIX => 'gz', },
    clean               => { FILES => 'juleol-*' },
);

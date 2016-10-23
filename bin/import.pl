#!/usr/bin/perl

use strict;
use IO::All;
use DBI;
use Data::Dumper;

my $year = shift @ARGV;
die unless $year =~ /^2\d{3}$/;

my $dbh = DBI->connect('DBI:mysql:juleol_dev', 'juleol_dev', 'hdi8qZku5SkhnToI', {mysql_enable_utf8 => 1}) or die;
$dbh->{'RaiseError'} = 1;
add_data($dbh, $year);
my $dbh = DBI->connect('DBI:mysql:juleol', 'juleol', '0FbWb5FqrmlKj35N', {mysql_enable_utf8 => 1}) or die;
$dbh->{'RaiseError'} = 1;
add_data($dbh, $year);

sub add_data {
  my $dbh = shift;
  my $year = shift;

  my $sth = $dbh->prepare('select id from tastings where year = ?');
  $sth->execute($year);
  my $tasting = $sth->fetchrow_array;
  unless($tasting) {
    my $insert = $dbh->prepare('insert into tastings (year) values (?)');
    $insert->execute($year);
    $sth->execute($year);
    $tasting = $sth->fetchrow_array;
  };
  die unless $tasting;

  my $add_beer = $dbh->prepare('insert into beers (name, number, tasting) values (?, ?, ?) on duplicate key update name = ?');
  my $data = io('/tmp/b')->utf8;
  my $i = 1;
  while(my $beer = $data->getline()) {
    chomp $beer;
    $add_beer->execute($beer, $i++, $tasting, $beer);
  };

  my $data = io('/tmp/s')->utf8;
  my @names = split(/\s{2,}/, $data->getline());

  my @participants;

  my $get_participant = $dbh->prepare('select id from participants where name = ? and tasting = ?');
  my $add_participant = $dbh->prepare('insert into participants (name, password, tasting) values (?, "xx", ?)');
  foreach my $name (@names) {
    $get_participant->execute($name, $tasting);
    my $participant = $get_participant->fetchrow_array;
    unless($participant) {
      $add_participant->execute($name, $tasting);
      $get_participant->execute($name, $tasting);
      $participant = $get_participant->fetchrow_array;
    };
    die unless $participant;
    push(@participants, $participant);
  };

  my $add_look = $dbh->prepare('insert into score_look (score, tasting, participant, beer) values (?, ?, ?, (select id from beers where tasting = ? and number = ?)) on duplicate key update score = ?');
  my $add_smell = $dbh->prepare('insert into score_smell (score, tasting, participant, beer) values (?, ?, ?, (select id from beers where tasting = ? and number = ?)) on duplicate key update score = ?');
  my $add_taste = $dbh->prepare('insert into score_taste (score, tasting, participant, beer) values (?, ?, ?, (select id from beers where tasting = ? and number = ?)) on duplicate key update score = ?');
  my $add_aftertaste = $dbh->prepare('insert into score_aftertaste (score, tasting, participant, beer) values (?, ?, ?, (select id from beers where tasting = ? and number = ?)) on duplicate key update score = ?');
  $data->getline();
  my $i = 1;
  while(my $line = $data->getline()) {
    my @chars = split(//, $line);
    foreach my $participant (@participants) {
      my $look = shift @chars;
      my $smell = shift @chars;
      my $taste = shift @chars;
      my $aftertaste = shift @chars;
      $add_look->execute($look, $tasting, $participant, $tasting, $i, $look) if $look =~ /^\d+$/;
      $add_smell->execute($smell, $tasting, $participant, $tasting, $i, $smell) if $smell =~ /^\d+$/;
      $add_taste->execute($taste, $tasting, $participant, $tasting, $i, $taste) if $taste =~ /^\d+$/;
      $add_aftertaste->execute($aftertaste, $tasting, $participant, $tasting, $i, $aftertaste) if $aftertaste =~ /^\d+$/;
    };
    $i++;
  };
};

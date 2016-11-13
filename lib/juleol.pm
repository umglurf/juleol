#  This file is part of juleol.
#
#   juleol is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   juleol is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with juleol.  If not, see <http://www.gnu.org/licenses/>.

package juleol;
use Dancer2;
use Dancer2::Plugin::DBIC;
use Dancer2::Plugin::Passphrase;
use Dancer2::Plugin::Auth::Tiny;

use Statistics::Basic qw(:all);
use Try::Tiny;

use Juleol::Admin;

our $VERSION = '0.1';

prefix '/';

get '/' => sub {
  my @tastings = rset('Tasting')->search({}, { order_by => ['year'] });
  template 'index', { tastings => \@tastings };
};

get '/result/:year' => sub {
  my $tasting = rset('Tasting')->find({ year => route_parameters->get('year') }, { prefetch => 'beers', order_by => [ 'beers.number' ] });
  unless($tasting) {
    status 'not_found';
    return "No such year";
  };
  my $order_key = '-asc';
  if(query_parameters->get('desc')) {
    $order_key = '-desc';
  };
  my $order = { $order_key => ['number', 'participant'] };
  if(query_parameters->get('order') eq 'name') {
    $order = { $order_key => ['name', 'participant'] };
  };
  my $search = { tasting => $tasting->id };
  my $selected_beers = {};
  if(query_parameters->get('beers')) {
    my @b = ();
    foreach my $beer (query_parameters->get_all('beers')) {
      if($beer =~ /^\d+$/) {
        push(@b, $beer);
        $selected_beers->{$beer} = 1;
      };
    };
    $search->{'number'} = { in => \@b };
  } else {
    foreach my $beer ($tasting->beers) {
      $selected_beers->{$beer->number} = 1;
    };
  };
  my $beerscores = rset('BeerScore')->search($search, { order_by => $order });
  my @participants;
  foreach my $p ($beerscores->search({}, { columns => ['participant'], distinct => 1 })) {
    push(@participants, $p->participant);
  };
  my @scores;
  my $id = -1;
  my $entry;
  while(my $score = $beerscores->next) {
    if($score->id != $id) {
      if($id > 0) {
        $entry->{'avg'} = sprintf("%.2f", $entry->{'sum'} / scalar(@{ $entry->{'participants'} }));
        $entry->{'std'} = sprintf("%.2f", stddev($entry->{'participants'}));
        my @dev = map { sprintf("%.2f", abs($_ - $entry->{'avg'})) } @{ $entry->{'participants'} };
        $entry->{'dev'} = \@dev;
        push(@scores, $entry);
      };
      $entry = {
        "id" => $score->id,
        "number" => $score->number,
        "name" => $score->name,
        "participants" => [],
        "sum" => 0,
      };
      $id = $score->id;
    };
    push(@{ $entry->{'participants'} }, $score->sum);
    $entry->{'sum'} += $score->sum;
  };
  $entry->{'avg'} = sprintf("%.2f", $entry->{'sum'} / scalar(@{ $entry->{'participants'} }));
  $entry->{'std'} = sprintf("%.2f", stddev($entry->{'participants'}));
  my @dev = map { sprintf("%.2f", abs($_ - $entry->{'avg'})) } @{ $entry->{'participants'} };
  $entry->{'dev'} = \@dev;
  push(@scores, $entry);
  if(query_parameters->get('order') eq 'sum') {
    $order = { $order_key => ['sum', 'participant'] };
    if($order_key eq '-asc') {
      @scores = sort { $a->{'sum'} <=> $b->{'sum'} } @scores;
    } else {
      @scores = sort { $b->{'sum'} <=> $a->{'sum'} } @scores;
    };
  };
  if(query_parameters->get('order') eq 'avg') {
    $order = { $order_key => ['avg', 'participant'] };
    if($order_key eq '-asc') {
      @scores = sort { $a->{'avg'} <=> $b->{'avg'} } @scores;
    } else {
      @scores = sort { $b->{'avg'} <=> $a->{'avg'} } @scores;
    };
  };
  if(query_parameters->get('order') eq 'std') {
    $order = { $order_key => ['std', 'participant'] };
    if($order_key eq '-asc') {
      @scores = sort { $a->{'std'} <=> $b->{'std'} } @scores;
    } else {
      @scores = sort { $b->{'std'} <=> $a->{'std'} } @scores;
    };
  };
  my $beers = [];
  my $beers_param = "";
  foreach my $beer ($tasting->beers) {
    my $e = {
      name => $beer->name,
      number => $beer->number,
      check => $selected_beers->{$beer->number} == 1 ? 'checked="checked"' : '',
    };
    push(@{ $beers }, $e);
    $beers_param .= '&beers=' . $beer->number if $selected_beers->{$beer->number};
  };
  template 'result', { tasting => $tasting, beers_param => $beers_param, beers => $beers, beerscores => \@scores, participants => \@participants, order => $order->{$order_key}, order_key => $order_key };
};

get '/rate/:year' => needs login => sub {
  my $tasting = rset('Tasting')->find({ year => route_parameters->get('year') }, { prefetch => 'beers', order_by => [ 'beers.number' ] });
  unless($tasting) {
    status 'not_found';
    return "No such year";
  };
  my $participant = rset('Participant')->search({ id => session('user'), tasting => $tasting->id })->single;
  unless($participant) {
    status 'error';
    return "This year is not a valid year for your user";
  };
  template 'rating', { tasting => $tasting, participant => $participant };
};

get '/result/participant/:id' => sub {
  my $beers = [];
  #foreach my $beer (rset('Participant')->search({ 'me.id' => route_parameters->get('id') }, { join => { tasting => ['beers'] }, '+colums' => ['beers.number', 'beers.name'], order_by => { '-asc' => 'beers.number'} })) {
  my $tasting =  rset('Participant')->search_related('tasting', { 'me.id' => route_parameters->get('id') });
  foreach my $beer ($tasting->search_related('beers', {}, { order => 'beers.number' })) {
    $beers->[$beer->number] = {};
    $beers->[$beer->number]->{'name'} = $beer->name;
    $beers->[$beer->number]->{'look'} = '';
    $beers->[$beer->number]->{'smell'} = '';
    $beers->[$beer->number]->{'taste'} = '';
    $beers->[$beer->number]->{'aftertaste'} = '';
    $beers->[$beer->number]->{'xmas'} = '';
  };
  foreach my $s (rset('Participant')->search_related('score_looks', { 'me.id' => route_parameters->get('id')}, { join => ['beer'], '+columns' => ['beer.number', 'beer.name'], order_by => { '-asc' => 'beer.number'} })) {
    $beers->[$s->beer->number]->{'look'} = $s->score;
  };
  foreach my $s (rset('Participant')->search_related('score_smells', { 'me.id' => route_parameters->get('id')}, { join => ['beer'], '+columns' => ['beer.number', 'beer.name'], order_by => { '-asc' => 'beer.number'} })) {
    $beers->[$s->beer->number]->{'smell'} = $s->score;
  };
  foreach my $s (rset('Participant')->search_related('score_tastes', { 'me.id' => route_parameters->get('id')}, { join => ['beer'], '+columns' => ['beer.number', 'beer.name'], order_by => { '-asc' => 'beer.number'} })) {
    $beers->[$s->beer->number]->{'taste'} = $s->score;
  };
  foreach my $s (rset('Participant')->search_related('score_aftertastes', { 'me.id' => route_parameters->get('id')}, { join => ['beer'], '+columns' => ['beer.number', 'beer.name'], order_by => { '-asc' => 'beer.number'} })) {
    $beers->[$s->beer->number]->{'aftertaste'} = $s->score;
  };
  foreach my $s (rset('Participant')->search_related('score_xmas', { 'me.id' => route_parameters->get('id')}, { join => ['beer'], '+columns' => ['beer.number', 'beer.name'], order_by => { '-asc' => 'beer.number'} })) {
    $beers->[$s->beer->number]->{'xmas'} = $s->score;
  };
  send_as JSON => { beers => $beers };
};

put '/rate/:year/:beer' => needs login => sub {
  my $beer = rset('Beer')->search(
    { 
      number => route_parameters->get('beer'), 
      'tasting.year' => route_parameters->get('year') 
    }, 
    { 
      join => 'tasting'
    })->single();
  unless($beer) {
    status 'not found';
    send_as JSON => { message => 'No such beer' };
  };
  my $participant = rset('Participant')->search({ id => session('user'), tasting => $beer->tasting->id })->single;
  unless($participant) {
    status 'error';
    send_as JSON => { message => "Unable to find participant" };
  };
  if(body_parameters->get('look')) {
    unless(body_parameters->get('look') =~ /^\d+$/ && body_parameters->get('look') >= 0 && body_parameters->get('look') <= 3) {
      status 'error';
      send_as JSON => { message => "Look is outside valid range (0-3)" };
    };
    try {
      rset('ScoreLooks')->update_or_create({
          score => body_parameters->get('look'),
          tasting => $beer->tasting->id,
          beer => $beer->id,
          participant => $participant->id
        }, { key => 'taste_participant_beer' });
    } catch {
      status 'error';
      send_as JSON => { message => "Unable to create or update look" };
    };
  };
  if(body_parameters->get('smell')) {
    unless(body_parameters->get('smell') =~ /^\d+$/ && body_parameters->get('smell') >= 0 && body_parameters->get('smell') <= 3) {
      status 'error';
      send_as JSON => { message => "Smell is outside valid range (0-3)" };
    };
    try {
      rset('ScoreSmells')->update_or_create({
          score => body_parameters->get('smell'),
          tasting => $beer->tasting->id,
          beer => $beer->id,
          participant => $participant->id
        }, { key => 'taste_participant_beer' });
    } catch {
      status 'error';
      send_as JSON => { message => "Unable to create or update smell" };
    };
  };
  if(body_parameters->get('taste')) {
    unless(body_parameters->get('taste') =~ /^\d+$/ && body_parameters->get('taste') >= 0 && body_parameters->get('taste') <= 9) {
      status 'error';
      send_as JSON => { message => "Invalid value for taste" };
    };
    try {
      rset('ScoreTastes')->update_or_create({
          score => body_parameters->get('taste'),
          tasting => $beer->tasting->id,
          beer => $beer->id,
          participant => $participant->id
        }, { key => 'taste_participant_beer' });
    } catch {
      status 'error';
      send_as JSON => { message => "Taste is outside valid range (0-9)" };
    };
  };
  if(body_parameters->get('aftertaste')) {
    unless(body_parameters->get('aftertaste') =~ /^\d+$/ && body_parameters->get('aftertaste') >= 0 && body_parameters->get('aftertaste') <= 5) {
      status 'error';
      send_as JSON => { message => "Aftertaste is outside valid range (0-5)" };
    };
    try {
      rset('ScoreAftertastes')->update_or_create({
          score => body_parameters->get('aftertaste'),
          tasting => $beer->tasting->id,
          beer => $beer->id,
          participant => $participant->id
        }, { key => 'taste_participant_beer' });
    } catch {
      status 'error';
      send_as JSON => { message => "Unable to create or update aftertaste" };
    };
  };
  if(body_parameters->get('xmas')) {
    unless(body_parameters->get('xmas') =~ /^\d+$/ && body_parameters->get('xmas') >= 0 && body_parameters->get('xmas') <= 3) {
      status 'error';
      send_as JSON => { message => "Xmas is outside valid range (0-3)" };
    };
    try {
      rset('ScoreXmas')->update_or_create({
          score => body_parameters->get('xmas'),
          tasting => $beer->tasting->id,
          beer => $beer->id,
          participant => $participant->id
        }, { key => 'taste_participant_beer' });
    } catch {
      status 'error';
      send_as JSON => { message => "Unable to create or update xmas" };
    };
  };
  send_as JSON => { message => "Result updated" };
};

get '/login' => sub {
  my @tastings = rset('Tasting')->search({}, { order_by => ['year'] });
  my $year = '';
  if(query_parameters->get('return_url') =~ /rate\/(\d+)$/) {
    $year = $1;
  };
  template 'login' => { tastings => \@tastings, year => $year, return_url => query_parameters->get('return_url') };
};

post '/login' => sub {
  my $user = _check_user( body_parameters->get('user'), body_parameters->get('password'), body_parameters->get('year') ); 
  if($user >= 0) {
    session user => $user;
    return redirect body_parameters->get('return_url') || '/';
  }
  else {
    my @tastings = rset('Tasting')->search({}, { order_by => ['year'] });
    template 'login' => { tastings => \@tastings, error => "invalid username or password", return_url => body_parameters->get('return_url') };
  }
};

get '/logout' => sub {
  app->destroy_session;
  redirect '/';
};

sub _check_user {
  my ($user, $password, $year) = @_;
  return -1 unless $year =~ /^2\d{3}$/;
  my $tasting = rset('Tasting')->search({ year => $year })->single;
  return -1 unless $tasting;
  my $participant = rset('Participant')->search(
    {
      'name' => $user,
      'tasting' => $tasting->id
    },
  )->single;
  return -1 unless $participant;
  my $id = -1;
  try {
    $id = $participant->id if passphrase($password)->matches($participant->password);
  } catch {
    $id = -1;
  };
  return $id;
};

true;

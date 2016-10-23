package juleol;
use Dancer2;
use Dancer2::Plugin::DBIC;
use Dancer2::Plugin::Passphrase;
use Dancer2::Plugin::Auth::Tiny;

use Statistics::Basic qw(:all);
use Try::Tiny;

use Juleol::Admin;

our $VERSION = '0.1';

#my $scores = rset('BeerScore')->search({ tasting => 10 }, { select => { sum => 'score' }, group_by => [ 'id' ] });
#while(my $score = $scores->next) {
#  print $score->name . ' ' . $score->score . "\n";
#};

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
  my $beerscores = rset('BeerScore')->search({ tasting => $tasting->id }, { order_by => $order });
  my @participants = $beerscores->search({}, { columns => ['participant', 'participant_name'], distinct => 1 });
  my @scores;
  my $id = -1;
  my $entry;
  while(my $score = $beerscores->next) {
    if($score->id != $id) {
      if($id > 0) {
        $entry->{'avg'} = sprintf("%.2f", $entry->{'sum'} / scalar(@{ $entry->{'participants'} }));
        $entry->{'std'} = sprintf("%.2f", stddev($entry->{'participants'}));
        my @dev = map { abs($_ - $entry->{'avg'}) } @{ $entry->{'participants'} };
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
  my @dev = map { abs($_ - $entry->{'avg'}) } @{ $entry->{'participants'} };
  $entry->{'dev'} = \@dev;
  push(@scores, $entry);
  if(query_parameters->get('order') eq 'sum') {
    $order = { $order_key => ['sum', 'participant'] };
    if($order_key eq '-asc') {
      @scores = sort { $a->{'sum'} cmp $b->{'sum'} } @scores;
    } else {
      @scores = sort { $b->{'sum'} cmp $a->{'sum'} } @scores;
    };
  };
  if(query_parameters->get('order') eq 'avg') {
    $order = { $order_key => ['avg', 'participant'] };
    if($order_key eq '-asc') {
      @scores = sort { $a->{'avg'} cmp $b->{'avg'} } @scores;
    } else {
      @scores = sort { $b->{'avg'} cmp $a->{'avg'} } @scores;
    };
  };
  if(query_parameters->get('order') eq 'std') {
    $order = { $order_key => ['std', 'participant'] };
    if($order_key eq '-asc') {
      @scores = sort { $a->{'std'} cmp $b->{'std'} } @scores;
    } else {
      @scores = sort { $b->{'std'} cmp $a->{'std'} } @scores;
    };
  };
  template 'result', { year => route_parameters->get('year'), beerscores => \@scores, participants => \@participants, order => $order->{$order_key}, order_key => $order_key };
};

get '/rate/:year' => needs login => sub {
  my $tasting = rset('Tasting')->find({ year => route_parameters->get('year') }, { prefetch => 'beers', order_by => [ 'beers.number' ] });
  unless($tasting) {
    status 'not_found';
    return "No such year";
  };
  my $participant = rset('Participant')->search({ name => session('user'), tasting => $tasting->id })->single;
  unless($participant) {
    status 'error';
    return "This year is not a valid year for your user";
  };
  template 'rating', { tasting => $tasting };
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
  my $participant = rset('Participant')->search({ name => session('user'), tasting => $beer->tasting->id })->single;
  unless($participant) {
    status 'error';
    send_as JSON => { message => "Unable to find participant" };
  };
  if(body_parameters->get('look')) {
    unless(body_parameters->get('look') =~ /^\d+$/ && body_parameters->get('look') >= 0 && body_parameters->get('look') <= 3) {
      status 'error';
      send_as JSON => { message => "Invalid value for look" };
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
      send_as JSON => { message => "Invalid value for smell" };
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
      send_as JSON => { message => "Unable to create or update taste" };
    };
  };
  if(body_parameters->get('aftertaste')) {
    unless(body_parameters->get('aftertaste') =~ /^\d+$/ && body_parameters->get('aftertaste') >= 0 && body_parameters->get('aftertaste') <= 5) {
      status 'error';
      send_as JSON => { message => "Invalid value for aftertaste" };
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
  send_as JSON => { message => "Result updated" };
};

get '/login' => sub {
  my @tastings = rset('Tasting')->search({}, { order_by => ['year'] });
  print "foo\n";
  template 'login' => { tastings => \@tastings, return_url => query_parameters->get('return_url') };
};

post '/login' => sub {
  if ( _is_valid( body_parameters->get('user'), body_parameters->get('password'), body_parameters->get('year') ) ) {
    session user => body_parameters->get('user');
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

sub _is_valid {
  my ($user, $password, $year) = @_;
  return 0 unless $year =~ /^2\d{3}$/;
  my $participant = rset('Participant')->find(
    {
      'name' => $user,
      'tasting.year' => 'year'
    },
    { join => 'tasting' }
  );
  return 0 unless $participant;
  return passphrase($password)->matches($participant->password);
};

true;

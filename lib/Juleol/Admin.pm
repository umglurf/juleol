package Juleol::Admin;
use Dancer2 appname => 'juleol';
use Dancer2::Plugin::DBIC;
use Dancer2::Plugin::Passphrase;
use Try::Tiny;

prefix '/admin';

get '/' => sub {
  my @tastings = rset('Tasting')->search({}, { order_by => ['year'] });
  template 'Admin/index', { tastings => \@tastings };
};

post '/' => sub {
  my $error = validate_create_tasting();
  my $message = undef;
  unless($error) {
    try {
      my $tasting = rset('Tasting')->create({ year => body_parameters->get('year') });
      for my $i (1 .. body_parameters->get('beers')) {
        rset('Beer')->create({ number => $i, tasting => $tasting->id });
      };
      $message = "Tasting created";
    } catch {
      $error = 'Unable to add new tasting';
    };
  };
  my $tastings = rset('Tasting')->search({}, { order_by => ['year'] });
  template 'Admin/index', { tastings => $tastings, error => $error, message => $message };
};

get '/:year' => sub {
  my $tasting = rset('Tasting')->find({ year => route_parameters->get('year') });
  unless($tasting) {
    status 'not_found';
    return "No such year";
  };
  template 'Admin/tasting', { tasting => $tasting };
};

put '/beer/:id' => sub {
  unless(body_parameters->get('name')) {
    status 'bad request';
    send_as JSON => { message => "Missing parameter name" };
  };
  my $beer = rset('Beer')->find(route_parameters->get('id'));
  unless($beer) {
    status 'not_found';
    send_as JSON => { message => "No such beer" };
  };
  try {
    $beer->update({ name => body_parameters->get('name') });
  } catch {
    status 'error';
    send_as JSON => { message => "Unable to update name" };
  };
  send_as JSON => { message => "Name updated" };
};

post '/participant' => sub {
  my $error = validate_create_participant();
  if($error) {
    status 'bad request';
    return $error;
  };
  my $tasting = rset('Tasting')->find(body_parameters->get('tasting'));
  unless($tasting) {
    status 'not_found';
    return "No such tasting";
  };
  my $message = undef;
  try {
    my $pass = passphrase( body_parameters->get('password') )->generate->rfc2307();
    my $participant = rset('Participant')->create({
        name => body_parameters->get('name'),
        password => $pass,
        tasting => $tasting->id
      });
    $message = 'Participant created';
  } catch {
    $error = "Unable to create participant";
  };
  template 'Admin/participant', { tasting => $tasting, error => $error, message => $message };
};

put '/participant/:id' => sub {
  unless(body_parameters->get('password')) {
    status 'bad request';
    send_as JSON => { message => "Missing parameter password" };
  };
  my $participant = rset('Participant')->find(route_parameters->get('id'));
  unless($participant) {
    status 'not_found';
    send_as JSON => { message => "No such participant" };
  };
  try {
    my $pass = passphrase( body_parameters->get('password') )->generate->rfc2307();
    $participant->update({ password => $pass });
  } catch {
    status 'error';
    send_as JSON => { message => "Unable to update password" };
  };
  send_as JSON => { message => "Password updated" };

};

sub validate_create_tasting {
  return 'Missing parameter year' unless body_parameters->get('year');
  return 'Missing parameter beers' unless body_parameters->get('beers');
  return 'Invalid value for year' unless body_parameters->get('year') =~ /^2\d{3}$/;
  return 'Invalid value for beers' unless body_parameters->get('beers') =~ /^\d+$/;
  return 'Invalid value for beers' unless body_parameters->get('beers') > 0 and body_parameters->get('beers') < 100;

  return undef;
};

sub validate_create_participant {
  return 'Missing parameter tasting' unless body_parameters->get('tasting');
  return 'Missing parameter name' unless body_parameters->get('name');
  return 'Missing parameter password' unless body_parameters->get('password');

  return undef;
};

true;


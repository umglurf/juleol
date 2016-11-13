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

package Juleol::Admin;
use Dancer2 appname => 'juleol';
use Dancer2::Plugin::DBIC;
use Dancer2::Plugin::Passphrase;
use Dancer2::Plugin::Auth::Tiny;
use Try::Tiny;

Dancer2::Plugin::Auth::Tiny->extend(
  admin => sub {
    my ($dsl, $coderef) = @_;
    return sub {
      if ( $dsl->app->session->read("is_admin") ) {
        goto $coderef;
      } else {
        $dsl->app->redirect('/admin/login');
      };
    }
  }
);

prefix '/admin';

get '/login' => sub {
  template 'Admin/login';
};

post '/login' => sub {
  my $admin = _check_admin( body_parameters->get('user'), body_parameters->get('password') ); 
  if($admin >= 0) {
    session is_admin => 1;
    return redirect '/admin/';
  }
  else {
    template 'Admin/login' => { error => "invalid username or password" };
  }
};

get '/logout' => sub {
  app->destroy_session;
  redirect '/admin/';
};


get '/' => needs admin => sub {
  my @tastings = rset('Tasting')->search({}, { order_by => ['year'] });
  template 'Admin/index', { tastings => \@tastings };
};

post '/' => needs admin => sub {
  my $error = validate_create_tasting();
  my $message = undef;
  unless($error) {
    try {
      my $tasting = rset('Tasting')->create({ year => body_parameters->get('year') });
      for my $i (1 .. body_parameters->get('beers')) {
        rset('Beer')->create({ number => $i, tasting => $tasting->id, name => "Unrevealed $i" });
      };
      $message = "Tasting created";
    } catch {
      $error = 'Unable to add new tasting';
    };
  };
  my $tastings = rset('Tasting')->search({}, { order_by => ['year'] });
  template 'Admin/index', { tastings => $tastings, error => $error, message => $message };
};

get '/:year' => needs admin => sub {
  my $tasting = rset('Tasting')->find({ year => route_parameters->get('year') });
  unless($tasting) {
    status 'not_found';
    return "No such year";
  };
  template 'Admin/tasting', { tasting => $tasting };
};

put '/beer/:id' => needs admin => sub {
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

post '/participant' => needs admin => sub {
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

put '/participant/:id' => needs admin => sub {
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

sub _check_admin {
  my ($user, $password) = @_;
  my $admin = rset('Admin')->search(
    {
      'name' => $user,
    },
  )->single;
  return -1 unless $admin;
  my $id = -1;
  try {
    $id = $admin->id if passphrase($password)->matches($admin->password);
  } catch {
    $id = -1;
  };
  return $id;
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


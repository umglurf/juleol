use utf8;
package Juleol::Schema::Result::Tasting;

# Created by DBIx::Class::Schema::Loader
# DO NOT MODIFY THE FIRST PART OF THIS FILE

=head1 NAME

Juleol::Schema::Result::Tasting

=cut

use strict;
use warnings;

use base 'DBIx::Class::Core';

=head1 TABLE: C<tastings>

=cut

__PACKAGE__->table("tastings");

=head1 ACCESSORS

=head2 id

  data_type: 'integer'
  extra: {unsigned => 1}
  is_auto_increment: 1
  is_nullable: 0

=head2 year

  data_type: 'integer'
  extra: {unsigned => 1}
  is_nullable: 0

=cut

__PACKAGE__->add_columns(
  "id",
  {
    data_type => "integer",
    extra => { unsigned => 1 },
    is_auto_increment => 1,
    is_nullable => 0,
  },
  "year",
  { data_type => "integer", extra => { unsigned => 1 }, is_nullable => 0 },
);

=head1 PRIMARY KEY

=over 4

=item * L</id>

=back

=cut

__PACKAGE__->set_primary_key("id");

=head1 UNIQUE CONSTRAINTS

=head2 C<year>

=over 4

=item * L</year>

=back

=cut

__PACKAGE__->add_unique_constraint("year", ["year"]);

=head1 RELATIONS

=head2 beers

Type: has_many

Related object: L<Juleol::Schema::Result::Beer>

=cut

__PACKAGE__->has_many(
  "beers",
  "Juleol::Schema::Result::Beer",
  { "foreign.tasting" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 participants

Type: has_many

Related object: L<Juleol::Schema::Result::Participant>

=cut

__PACKAGE__->has_many(
  "participants",
  "Juleol::Schema::Result::Participant",
  { "foreign.tasting" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 score_aftertastes

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreAftertastes>

=cut

__PACKAGE__->has_many(
  "score_aftertastes",
  "Juleol::Schema::Result::ScoreAftertastes",
  { "foreign.tasting" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 score_looks

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreLooks>

=cut

__PACKAGE__->has_many(
  "score_looks",
  "Juleol::Schema::Result::ScoreLooks",
  { "foreign.tasting" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 score_smells

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreSmells>

=cut

__PACKAGE__->has_many(
  "score_smells",
  "Juleol::Schema::Result::ScoreSmells",
  { "foreign.tasting" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 score_tastes

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreTastes>

=cut

__PACKAGE__->has_many(
  "score_tastes",
  "Juleol::Schema::Result::ScoreTastes",
  { "foreign.tasting" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);


# Created by DBIx::Class::Schema::Loader v0.07046 @ 2016-10-22 06:45:25
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:9YMN8mR+OcOPD/1lpzLePw


# You can replace this text with custom code or comments, and it will be preserved on regeneration
1;

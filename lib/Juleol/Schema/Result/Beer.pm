use utf8;
package Juleol::Schema::Result::Beer;

# Created by DBIx::Class::Schema::Loader
# DO NOT MODIFY THE FIRST PART OF THIS FILE

=head1 NAME

Juleol::Schema::Result::Beer

=cut

use strict;
use warnings;

use base 'DBIx::Class::Core';

=head1 TABLE: C<beers>

=cut

__PACKAGE__->table("beers");

=head1 ACCESSORS

=head2 id

  data_type: 'integer'
  extra: {unsigned => 1}
  is_auto_increment: 1
  is_nullable: 0

=head2 name

  data_type: 'varchar'
  default_value: 'unrevealed'
  is_nullable: 0
  size: 255

=head2 number

  data_type: 'tinyint'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 tasting

  data_type: 'integer'
  extra: {unsigned => 1}
  is_foreign_key: 1
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
  "name",
  {
    data_type => "varchar",
    default_value => "unrevealed",
    is_nullable => 0,
    size => 255,
  },
  "number",
  { data_type => "tinyint", extra => { unsigned => 1 }, is_nullable => 0 },
  "tasting",
  {
    data_type => "integer",
    extra => { unsigned => 1 },
    is_foreign_key => 1,
    is_nullable => 0,
  },
);

=head1 PRIMARY KEY

=over 4

=item * L</id>

=back

=cut

__PACKAGE__->set_primary_key("id");

=head1 RELATIONS

=head2 score_aftertastes

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreAftertastes>

=cut

__PACKAGE__->has_many(
  "score_aftertastes",
  "Juleol::Schema::Result::ScoreAftertastes",
  { "foreign.beer" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 score_looks

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreLooks>

=cut

__PACKAGE__->has_many(
  "score_looks",
  "Juleol::Schema::Result::ScoreLooks",
  { "foreign.beer" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 score_smells

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreSmells>

=cut

__PACKAGE__->has_many(
  "score_smells",
  "Juleol::Schema::Result::ScoreSmells",
  { "foreign.beer" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 score_tastes

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreTastes>

=cut

__PACKAGE__->has_many(
  "score_tastes",
  "Juleol::Schema::Result::ScoreTastes",
  { "foreign.beer" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 tasting

Type: belongs_to

Related object: L<Juleol::Schema::Result::Tasting>

=cut

__PACKAGE__->belongs_to(
  "tasting",
  "Juleol::Schema::Result::Tasting",
  { id => "tasting" },
  { is_deferrable => 1, on_delete => "RESTRICT", on_update => "RESTRICT" },
);


# Created by DBIx::Class::Schema::Loader v0.07046 @ 2016-10-22 06:45:25
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:AUNVIgSj1MeOC+lrfmhYvA


# You can replace this text with custom code or comments, and it will be preserved on regeneration
1;

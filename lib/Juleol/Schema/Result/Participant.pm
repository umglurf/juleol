use utf8;
package Juleol::Schema::Result::Participant;

# Created by DBIx::Class::Schema::Loader
# DO NOT MODIFY THE FIRST PART OF THIS FILE

=head1 NAME

Juleol::Schema::Result::Participant

=cut

use strict;
use warnings;

use base 'DBIx::Class::Core';

=head1 TABLE: C<participants>

=cut

__PACKAGE__->table("participants");

=head1 ACCESSORS

=head2 id

  data_type: 'integer'
  extra: {unsigned => 1}
  is_auto_increment: 1
  is_nullable: 0

=head2 name

  data_type: 'varchar'
  is_nullable: 0
  size: 255

=head2 password

  data_type: 'varchar'
  is_nullable: 0
  size: 255

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
  { data_type => "varchar", is_nullable => 0, size => 255 },
  "password",
  { data_type => "varchar", is_nullable => 0, size => 255 },
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

=head1 UNIQUE CONSTRAINTS

=head2 C<name>

=over 4

=item * L</name>

=back

=cut

__PACKAGE__->add_unique_constraint("name", ["name"]);

=head2 C<name_2>

=over 4

=item * L</name>

=item * L</tasting>

=back

=cut

__PACKAGE__->add_unique_constraint("name_2", ["name", "tasting"]);

=head1 RELATIONS

=head2 score_aftertastes

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreAftertastes>

=cut

__PACKAGE__->has_many(
  "score_aftertastes",
  "Juleol::Schema::Result::ScoreAftertastes",
  { "foreign.participant" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 score_looks

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreLooks>

=cut

__PACKAGE__->has_many(
  "score_looks",
  "Juleol::Schema::Result::ScoreLooks",
  { "foreign.participant" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 score_smells

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreSmells>

=cut

__PACKAGE__->has_many(
  "score_smells",
  "Juleol::Schema::Result::ScoreSmells",
  { "foreign.participant" => "self.id" },
  { cascade_copy => 0, cascade_delete => 0 },
);

=head2 score_tastes

Type: has_many

Related object: L<Juleol::Schema::Result::ScoreTastes>

=cut

__PACKAGE__->has_many(
  "score_tastes",
  "Juleol::Schema::Result::ScoreTastes",
  { "foreign.participant" => "self.id" },
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


# Created by DBIx::Class::Schema::Loader v0.07046 @ 2016-10-22 11:53:48
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:OZ0u0oKtsOKdVpRhrTMLNg


# You can replace this text with custom code or comments, and it will be preserved on regeneration
1;

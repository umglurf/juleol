use utf8;
package Juleol::Schema::Result::ScoreTastes;

# Created by DBIx::Class::Schema::Loader
# DO NOT MODIFY THE FIRST PART OF THIS FILE

=head1 NAME

Juleol::Schema::Result::ScoreTastes

=cut

use strict;
use warnings;

use base 'DBIx::Class::Core';

=head1 TABLE: C<score_taste>

=cut

__PACKAGE__->table("score_taste");

=head1 ACCESSORS

=head2 id

  data_type: 'integer'
  extra: {unsigned => 1}
  is_auto_increment: 1
  is_nullable: 0

=head2 score

  data_type: 'tinyint'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 tasting

  data_type: 'integer'
  extra: {unsigned => 1}
  is_foreign_key: 1
  is_nullable: 0

=head2 participant

  data_type: 'integer'
  extra: {unsigned => 1}
  is_foreign_key: 1
  is_nullable: 0

=head2 beer

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
  "score",
  { data_type => "tinyint", extra => { unsigned => 1 }, is_nullable => 0 },
  "tasting",
  {
    data_type => "integer",
    extra => { unsigned => 1 },
    is_foreign_key => 1,
    is_nullable => 0,
  },
  "participant",
  {
    data_type => "integer",
    extra => { unsigned => 1 },
    is_foreign_key => 1,
    is_nullable => 0,
  },
  "beer",
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

=head2 C<taste_participant_beer>

=over 4

=item * L</tasting>

=item * L</participant>

=item * L</beer>

=back

=cut

__PACKAGE__->add_unique_constraint("taste_participant_beer", ["tasting", "participant", "beer"]);

=head1 RELATIONS

=head2 beer

Type: belongs_to

Related object: L<Juleol::Schema::Result::Beer>

=cut

__PACKAGE__->belongs_to(
  "beer",
  "Juleol::Schema::Result::Beer",
  { id => "beer" },
  { is_deferrable => 1, on_delete => "RESTRICT", on_update => "RESTRICT" },
);

=head2 participant

Type: belongs_to

Related object: L<Juleol::Schema::Result::Participant>

=cut

__PACKAGE__->belongs_to(
  "participant",
  "Juleol::Schema::Result::Participant",
  { id => "participant" },
  { is_deferrable => 1, on_delete => "RESTRICT", on_update => "RESTRICT" },
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


# Created by DBIx::Class::Schema::Loader v0.07046 @ 2016-10-22 11:57:38
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:dqNiXaqKLeEaM310C6bpNg


# You can replace this text with custom code or comments, and it will be preserved on regeneration
1;

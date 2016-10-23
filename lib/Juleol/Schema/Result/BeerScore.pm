package Juleol::Schema::Result::BeerScore;
use strict;
use warnings;
use base qw/DBIx::Class::Core/;

__PACKAGE__->table_class('DBIx::Class::ResultSource::View');

# For the time being this is necessary even for virtual views
__PACKAGE__->table('beer_score');

#
# ->add_columns, etc.
#

# do not attempt to deploy() this view
__PACKAGE__->result_source_instance->is_virtual(1);

__PACKAGE__->result_source_instance->view_definition("
SELECT s.id AS id,
       p.id AS participant,
       p.name AS participant_name,
       s.number AS number,
       s.name AS name,
       s.tasting AS tasting,
       SUM(s.score) AS sum,
       AVG(s.score) AS avg,
       STD(s.score) AS std
      FROM (
    SELECT beers.id, beers.tasting, number, name, score, participant AS p_id FROM beers JOIN score_look ON score_look.beer = beers.id
    UNION ALL
    SELECT beers.id, beers.tasting, number, name, score, participant AS p_id FROM beers JOIN score_smell ON score_smell.beer = beers.id
    UNION ALL
    SELECT beers.id, beers.tasting, number, name, score, participant AS p_id FROM beers JOIN score_taste ON score_taste.beer = beers.id
    UNION ALL
    SELECT beers.id, beers.tasting, number, name, score, participant AS p_id FROM beers JOIN score_aftertaste ON score_aftertaste.beer = beers.id
  ) s JOIN participants AS p on p.id = s.p_id
  GROUP BY p.id, s.name
	");
__PACKAGE__->add_columns(
  "id",
  {
    data_type => "integer",
    extra => { unsigned => 1 },
    is_auto_increment => 1,
    is_nullable => 0,
  },
  "participant",
  {
    data_type => "integer",
    extra => { unsigned => 1 },
    is_foreign_key => 1,
    is_nullable => 0,
  },
  "participant_name",
  { data_type => "varchar", is_nullable => 0, size => 255 },
  "name",
  {
    data_type => "varchar",
    default_value => "unrevealed",
    is_nullable => 0,
    size => 255,
  },
  "number",
  { data_type => "tinyint", extra => { unsigned => 1 }, is_nullable => 0 },
  "sum",
  { data_type => "integer", extra => { unsigned => 1 }, is_nullable => 0 },
  "avg",
  { data_type => "float" },
  "std",
  { data_type => "float" },
);

__PACKAGE__->belongs_to(
  "tasting",
  "Juleol::Schema::Result::Tasting",
  { id => "tasting" },
  { is_deferrable => 1, on_delete => "RESTRICT", on_update => "RESTRICT" },
);
__PACKAGE__->belongs_to(
  "participant",
  "Juleol::Schema::Result::Participant",
  { id => "participant" },
  { is_deferrable => 1, on_delete => "RESTRICT", on_update => "RESTRICT" },
);


1;

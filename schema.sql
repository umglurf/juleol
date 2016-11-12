CREATE TABLE admins (
  id int unsigned not null auto_increment,
  name varchar(255) not null,
  password varchar(255) not null,
  PRIMARY KEY(id),
  UNIQUE(name)
);

CREATE TABLE tastings (
  id int unsigned not null auto_increment,
  year int unsigned not null,
  PRIMARY KEY(id),
  UNIQUE (year)
);

CREATE TABLE beers (
  id int unsigned not null auto_increment,
  name varchar(255) not null default 'unrevealed',
  number tinyint unsigned not null,
  tasting int unsigned not null,
  PRIMARY KEY(id),
  UNIQUE(number, tasting),
  FOREIGN KEY(tasting) REFERENCES tastings(id)
);

CREATE TABLE participants (
  id int unsigned not null auto_increment,
  name varchar(255) not null,
  password varchar(255) not null,
  tasting int unsigned not null,
  PRIMARY KEY(id),
  UNIQUE (name,tasting),
  FOREIGN KEY(tasting) REFERENCES tastings(id)
);

CREATE TABLE score_taste (
  id int unsigned not null auto_increment,
  score tinyint unsigned not null,
  tasting int unsigned not null,
  participant int unsigned not null,
  beer int unsigned not null,
  PRIMARY KEY(id),
  UNIQUE taste_participant_beer (tasting,participant,beer),
  FOREIGN KEY(tasting) REFERENCES tastings(id),
  FOREIGN KEY(participant) REFERENCES participants(id),
  FOREIGN KEY(beer) REFERENCES beers(id)
);

CREATE TABLE score_aftertaste (
  id int unsigned not null auto_increment,
  score tinyint unsigned not null,
  tasting int unsigned not null,
  participant int unsigned not null,
  beer int unsigned not null,
  PRIMARY KEY(id),
  UNIQUE taste_participant_beer (tasting,participant,beer),
  FOREIGN KEY(tasting) REFERENCES tastings(id),
  FOREIGN KEY(participant) REFERENCES participants(id),
  FOREIGN KEY(beer) REFERENCES beers(id)
);

CREATE TABLE score_smell (
  id int unsigned not null auto_increment,
  score tinyint unsigned not null,
  tasting int unsigned not null,
  participant int unsigned not null,
  beer int unsigned not null,
  PRIMARY KEY(id),
  UNIQUE taste_participant_beer (tasting,participant,beer),
  FOREIGN KEY(tasting) REFERENCES tastings(id),
  FOREIGN KEY(participant) REFERENCES participants(id),
  FOREIGN KEY(beer) REFERENCES beers(id)
);

CREATE TABLE score_look (
  id int unsigned not null auto_increment,
  score tinyint unsigned not null,
  tasting int unsigned not null,
  participant int unsigned not null,
  beer int unsigned not null,
  PRIMARY KEY(id),
  UNIQUE taste_participant_beer (tasting,participant,beer),
  FOREIGN KEY(tasting) REFERENCES tastings(id),
  FOREIGN KEY(participant) REFERENCES participants(id),
  FOREIGN KEY(beer) REFERENCES beers(id)
);

CREATE TABLE score_xmas (
  id int unsigned not null auto_increment,
  score tinyint unsigned not null,
  tasting int unsigned not null,
  participant int unsigned not null,
  beer int unsigned not null,
  PRIMARY KEY(id),
  UNIQUE taste_participant_beer (tasting,participant,beer),
  FOREIGN KEY(tasting) REFERENCES tastings(id),
  FOREIGN KEY(participant) REFERENCES participants(id),
  FOREIGN KEY(beer) REFERENCES beers(id)
);

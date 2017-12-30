#!/bin/bash

if [ -n "$COOKIE_SECRET_FILE" ]
then
  if [ -f "$COOKIE_SECRET_FILE" ]
  then
    COOKIE_SECRET="$(< $COOKIE_SECRET_FILE)"
  fi
fi

if [ -n "$MYSQL_PASSWORD_FILE" ]
then
  if [ -f "$MYSQL_PASSWORD_FILE" ]
  then
    MYSQL_PASSWORD="$(< $MYSQL_PASSWORD_FILE)"
  fi
fi

/bin/rm /var/www/juleol/environments/production_local.yml

if [ -n "$COOKIE_SECRET" ]
then
  cat <<EOD >> /var/www/juleol/environments/production_local.yml
engines:
  session:
      Cookie:
        secret_key: ${COOKIE_SECRET}
EOD
fi

if [ -n "$MYSQL_PASSWORD" ]
then
  cat <<EOD >> /var/www/juleol/environments/production_local.yml
plugins:
  DBIC:
    default:
      password: $MYSQL_PASSWORD
EOD
fi

exec /var/www/juleol/public/dispatch.fcgi

<!--
SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# juleol

![python test status badge](https://github.com/umglurf/juleol/workflows/Python%20unittest/badge.svg)

![build status badge](https://github.com/umglurf/juleol/workflows/Docker%20build%20and%20push/badge.svg)

Christmas beer rating application

This is a web application written in python flask to aid with the rating of Christmas beer (or other beers for that matter).

## Admin authentication

The admin interface is set up to authenticate against GitHub with oauth.
To create a new app, go to (https://github.com/settings/applications/new)
Set the following settings:
 * Homepage URL, the URL of the juleøl app. For development, use ```https://localhost:5000```
 * Authorization callback URL, ```Homepage_URL/admin/login/github/authorize```
Then set the environment variables
 * '''GITHUB_OAUTH_CLIENT_ID```
 * '''GITHUB_OAUTH_CLIENT_SECRET```

### Using generic oauth2 provider

To use a generic oauth2 provider, configure the provider using the same parameters as for github.
Then set  the following environment variables
 * ```ADMIN_OAUTH_PROVIDER=oauth-generic```
 * ```OAUTH_CLIENT_ID="YOUR_CLIENT_ID"```
 * ```OAUTH_CLIENT_SECRET="YOUR_CLIENT_SECRET"```
 * ```OAUTH_AUTHORIZATION_URL="URL TO AUTH ENDPOINT"```
 * ```OAUTH_TOKEN_URL="URL TO TOKEN ENDPOINT"```

### Using other oauth2 providers

To use [one of the build in oauth2 providers](https://flask-dance.readthedocs.io/en/latest/providers.html)
, modify ```__init__.py``` and add it there.

## User authentication

User authentication is set up to log in using oauth. Per now, only
google oauth authentication is supported.
You will need to [set up client credentials](https://support.google.com/cloud/answer/6158849?hl=en)
The type is Web Application. In authorized redirect URIs, use
```https://localhost:5000/login/google/authorized``` and for production use
```Homepage_URL/login/google/authorized```
Then set the environment variables
 * ```GOOGLE_OAUTH_CLIENT_ID```
 * ```GOOGLE_OAUTH_CLIENT_SECRET```


## Database configuration

See the README in the migrations folder

## Running the application using docker

To run the application, build an image using the Dockerfile or use the prebuild image.
To configure the
image, the following environment variables are supported
 * ```JULEOL_SETTINGS```, the filename to read settings from. If this is not
   set, the following variables can be set (otherwise must be set in the config
   file):
   * ```SECRET_KEY```, the flask secret key. Important to be set to a known value
        if running multiple instances. If not set, a random key is generated
        See the flask docs for more information
   * ```SQLALCHEMY_DATABASE_URI```, the database URI, see
   [flask sqlalchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/?highlight=sqlalchemy_database_uri)
   for more information about the format
   * ```GITHUB_OAUTH_CLIENT_ID``` and ```GITHUB_OAUTH_CLIENT_SECRET```, the
     oauth credentials to use with GitHub for admin auth
   * to use generic oauth2, set the environment variables as described above
   * ```GOOGLE_OAUTH_CLIENT_ID``` and ```GOOGLE_OAUTH_CLIENT_SECRET```, the
     oauth credentials to use with Google for user auth

## Developing

Set up a virtual env and install dependancies
```
mkdir juleol_virtualenv
virtualenv -p /usr/bin/python3 juleol_virtualenv
. juleol_virtualenv/bin/activate
pip install -e .
```

Start the database with
```
docker-compose up -d mysql
```

And start the development environment with
```
. $(dirname $0)/juleol_virtualenv/bin/activate
export FLASK_APP="$(dirname "$0")/juleol"
export FLASK_ENV=development

cfgfile=$(mktemp)
echo 'SQLALCHEMY_DATABASE_URI= "mysql+pymysql://juleol:juleol@127.0.0.1/juleol"' >> $cfgfile
echo 'SQLALCHEMY_ECHO = True' >> $cfgfile
echo 'SQLALCHEMY_TRACK_MODIFICATIONS = False' >> $cfgfile
echo "SECRET_KEY = b'$(tr -c -d [:alnum:] < /dev/urandom | dd bs=1 count=16 2>/dev/null)'" >> $cfgfile
export JULEOL_SETTINGS="$cfgfile"

flask run -h 127.0.0.1

rm -- "$cfgfile"
```

To test oauth authentication you will need to generate a self signed
certificate
```
openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.csr
openssl x509 -signkey server.key -req -in server.csr -out server.crt
```
then add
```
echo 'GITHUB_OAUTH_CLIENT_ID="XX"' >> $cfgfile
echo 'GITHUB_OAUTH_CLIENT_SECRET="XX"' >> $cfgfile
echo 'GOOGLE_OAUTH_CLIENT_ID="XX"' >> $cfgfile
echo 'GOOGLE_OAUTH_CLIENT_SECRET="XX"' >> $cfgfile
```
And change flask start to
```
flask run -h 127.0.0.1 --cert server.crt --key server.key
```

### Running tests

```python setup.py test```

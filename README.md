# juleol

Christmas beer rating application

This is a web application written in python flask to aid with the rating of Christmas beer (or other beers for that matter).

## Admin authentication

The admin interface is set up to authenticate against haavard.name with oauth.
To change to another oauth provider, see the
[Flask-Dance](https://flask-dance.readthedocs.io/) docs and change 
 * The blueprint setup in ```__init.py__```
 * The login_required function in ```admin.py```

## Running the application

To run the application, build an image using the Dockerfile. To configure the
image, the following environment variables are supported
 * ```JULEOL_SETTINGS```, the filename to read settings from. If this is not
   set, the following variables can be set (otherwise must be set in the config
   file):
   * ```SECRET_KEY```, the flask secret key. Important to be set to a known value
        if running multiple instances. If not set, a random key is generated
        See the flask docs for more information
   * ```SQLALCHEMY_DATABASE_URI```, the database URI, see flask sqlalchemy for
     more information about the format
   * ```HAAVARD_OAUTH_CLIENT_ID``` and ```HAAVARD_OAUTH_CLIENT_SECRET```, the
     oauth credentials to use againts haavard.name for admin auth

## Developing

Set up a virtual env and install dependancies
```
mkdir juleol_virtualenv
virtualenv -p /usr/bin/python3
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
echo 'HAAVARD_OAUTH_CLIENT_ID="XX"' >> $cfgfile
echo 'HAAVARD_OAUTH_CLIENT_SECRET="XX"' >> $cfgfile
```
And change flask start to
```
flask run -h 127.0.0.1 --cert server.crt --key server.key
```

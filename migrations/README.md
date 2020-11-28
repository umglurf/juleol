# Initializing and upgrading the database

To initialize the database or upgrade the schema, do the following:
1. Create a config file containing the database connection parameter SQLALCHEMY_DATABASE_URI, for example ```SQLALCHEMY_DATABASE_URI="mysql+pymsql://root:mypassword@localhost/juleol"```
2. Run ```FLASK_APP=juleol JULEOL_SETTINGS=/full/path/to/config/file flask db upgrade```

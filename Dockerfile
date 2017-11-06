FROM docker.haavard.name/baseimage:latest

RUN apt-get update && \
    apt-get -y --no-install-recommends install libdancer2-perl libdancer2-plugin-database-perl libclass-dbi-mysql-perl libtest2-suite-perl libfcgi-perl libfcgi-procmanager-perl libtry-tiny-perl libstatistics-basic-perl libyaml-perl libmodule-build-perl libcrypt-eksblowfish-perl libdigest-bcrypt-perl libcrypt-rijndael-perl libdbd-sqlite3-perl libdbix-class-schema-loader-perl libdbicx-sugar-perl libsql-translator-perl libdata-entropy-perl libhttp-lite-perl libtemplate-perl libsession-storage-secure-perl libtest-mockobject-perl build-essential nginx && \
    cpan -i Dancer2::Session::Cookie Dancer2::Plugin::DBIC Dancer2::Plugin::Passphrase Dancer2::Plugin::Auth::Tiny ExtUtils::MakeMaker

COPY . /var/www/juleol/
WORKDIR /var/www/juleol
RUN perl Makefile.PL && make install
WORKDIR /
RUN apt-get -y remove build-essential && \
    apt-get -y autoremove build-essential && \
    apt-get clean
COPY juleol.nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log
CMD ["/var/www/juleol/run.sh"]

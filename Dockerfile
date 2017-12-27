FROM docker.haavard.name/baseimage:latest

RUN apt-get update && \
    apt-get -y --no-install-recommends install curl unzip ca-certificates libdancer2-perl libdancer2-plugin-database-perl libclass-dbi-mysql-perl libdbd-sqlite3-perl libtest2-suite-perl libfcgi-perl libfcgi-procmanager-perl libtry-tiny-perl libstatistics-basic-perl libyaml-perl libmodule-build-perl libcrypt-eksblowfish-perl libdigest-bcrypt-perl libcrypt-rijndael-perl libdbd-sqlite3-perl libdbix-class-schema-loader-perl libdbicx-sugar-perl libsql-translator-perl libdata-entropy-perl libhttp-lite-perl libtemplate-perl libsession-storage-secure-perl libtest-mockobject-perl build-essential nginx && \
    cpan -i Dancer2::Session::Cookie Dancer2::Plugin::DBIC Dancer2::Plugin::Passphrase Dancer2::Plugin::Auth::Tiny ExtUtils::MakeMaker && \
    ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# Install Consul
# Releases at https://releases.hashicorp.com/consul
RUN export CONSUL_VERSION=1.0.2 \
    && export CONSUL_CHECKSUM=418329f0f4fc3f18ef08674537b576e57df3f3026f258794b4b4b611beae6c9b
    && curl --retry 7 --fail -vo /tmp/consul.zip "https://releases.hashicorp.com/consul/${CONSUL_VERSION}/consul_${CONSUL_VERSION}_linux_amd64.zip" \
    && echo "${CONSUL_CHECKSUM}  /tmp/consul.zip" | sha256sum -c \
    && unzip /tmp/consul -d /usr/local/bin \
    && rm /tmp/consul.zip \
    && mkdir /config

# Create empty directories for Consul config and data
RUN mkdir -p /etc/consul \
    && mkdir -p /var/lib/consul

# Add Containerpilot and set its configuration
ENV CONTAINERPILOT_VER 3.5.1
ENV CONTAINERPILOT /etc/containerpilot.json5

RUN export CONTAINERPILOT_CHECKSUM=7ee8e59588b6b593325930b0dc18d01f666031d7 \
    && curl -Lso /tmp/containerpilot.tar.gz \
         "https://github.com/joyent/containerpilot/releases/download/${CONTAINERPILOT_VER}/containerpilot-${CONTAINERPILOT_VER}.tar.gz" \
    && echo "${CONTAINERPILOT_CHECKSUM}  /tmp/containerpilot.tar.gz" | sha1sum -c \
    && tar zxf /tmp/containerpilot.tar.gz -C /usr/local/bin \
    && rm /tmp/containerpilot.tar.gz


COPY . /var/www/juleol/
WORKDIR /var/www/juleol
RUN perl Makefile.PL && make install && mkdir environments
WORKDIR /
RUN apt-get -y remove build-essential && \
    apt-get -y autoremove build-essential && \
    apt-get clean
COPY juleol.nginx.conf /etc/nginx/sites-available/default
COPY containerpilot.json5 /etc/
ENTRYPOINT 
CMD ["/usr/local/bin/containerpilot"]

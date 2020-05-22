FROM ubuntu:18.04 as build

WORKDIR /build

RUN apt-get update \
    && DEBIAN_FRONTENT=noninteractive apt-get -y upgrade \
    && DEBIAN_FRONTENT=noninteractive apt-get -y install build-essential dumb-init python3 python3-dev python3-setuptools virtualenv \
    && mkdir /usr/local/juleol \
    && virtualenv -p /usr/bin/python3 /usr/local/juleol

COPY . /build/
RUN . /usr/local/juleol/bin/activate \
    && python setup.py install \
    && python setup.py install_lib

FROM ubuntu:18.04 as prod

RUN apt-get update \
    && DEBIAN_FRONTENT=noninteractive apt-get -y install dumb-init python3 \
    && apt-get -y clean \
    && useradd -r juleol

COPY --from=build /usr/local/juleol /usr/local/juleol
COPY wscgi.py /usr/local/juleol
COPY run /bin/run

USER juleol

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/bin/run"]

# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

FROM alpine:3.12 as build

WORKDIR /build

RUN apk --no-cache add gcc libc-dev libffi-dev python3 python3-dev py3-cffi py3-pip py3-virtualenv \
    && mkdir /usr/local/juleol \
    && virtualenv -p /usr/bin/python3 /usr/local/juleol

COPY . /build/
RUN . /usr/local/juleol/bin/activate \
    && python setup.py install \
    && python setup.py install_lib

FROM alpine:3.12 as prod

RUN apk --no-cache add bash dumb-init python3 py3-pip \
    && addgroup -g 1000 juleol \
    && adduser -u 1000 -G juleol -D juleol

COPY --from=build /usr/local/juleol /usr/local/juleol
COPY wscgi.py /usr/local/juleol
COPY run /bin/run

USER juleol

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/bin/run"]

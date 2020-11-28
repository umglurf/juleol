# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

FROM alpine:3.12

RUN apk --no-cache add bash dumb-init python3 py3-pip py3-virtualenv \
    && addgroup -g 1000 juleol \
    && adduser -u 1000 -G juleol -D juleol

RUN pip3 install pipenv

WORKDIR /usr/local/juleol

COPY . /usr/local/juleol/

RUN chown -R juleol:juleol /usr/local/juleol

USER 1000

RUN pipenv install

ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED 1

COPY run /bin/run

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/bin/run"]

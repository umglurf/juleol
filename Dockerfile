# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

FROM alpine:3.14 AS base

RUN apk --no-cache add bash dumb-init python3 py3-pip py3-virtualenv py3-wheel \
    && addgroup -g 1000 juleol \
    && adduser -u 1000 -G juleol -D juleol

RUN pip3 install pipenv

WORKDIR /usr/local/juleol

FROM base as build

RUN apk add build-base python3-dev

COPY . /usr/local/juleol

RUN chown -R juleol:juleol /usr/local/juleol

USER 1000

RUN pipenv install

FROM base as prod

USER 1000

COPY --from=build /home/juleol /home/juleol
COPY --from=build /usr/local/juleol/ /usr/local/juleol

ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED 1

COPY run /bin/run

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/bin/run"]

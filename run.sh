#!/bin/bash

/usr/sbin/nginx
exec /var/www/juleol/public/dispatch.fcgi

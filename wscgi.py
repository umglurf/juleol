#!/usr/bin/env juleol

# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import juleol
from werkzeug.middleware.proxy_fix import ProxyFix

application = ProxyFix(juleol.create_app(), x_for=1, x_proto=1, x_host=1, x_port=1)

if __name__ == "__main__":
    application.run()

# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later


class DefaultConfig:
    ADMIN_OAUTH_PROVIDER = "github"
    USER_OAUTH_PROVIDER = "google"
    PREFERRED_URL_SCHEME = "https"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY_TABLE = "flask_session"
    SESSION_USE_SIGNER = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

"""
gitboard
~~~~~~~~

:copyright: (c) 2011 David Cramer.
:license: Apache License 2.0, see LICENSE for more details.
"""

from flask import Flask
from flaskext.redis import Redis
from jinja2 import Markup
from urllib import quote
from werkzeug.routing import BaseConverter
import logging

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('gitboard').version
except Exception, e:
    VERSION = 'unknown'

class UUIDConverter(BaseConverter):
    regex = '[a-zA-Z0-9]{32}'

app = Flask(__name__)
app.config.from_object('gitboard.conf.Config')

def configure_logging(app):
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper()))

    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    root.addHandler(handler)

    app.logger.addHandler(handler)

configure_logging(app)

app.url_map.converters['uuid'] = UUIDConverter

redis = Redis(app)

app.logger.info("Connected to Redis server at %s:%s" % (app.config['REDIS_HOST'], app.config['REDIS_PORT']))


app.jinja_env.filters['urlencode'] = quote
def linebreaks(value):
    return Markup(value.replace('\n', '<br/>'))

app.jinja_env.filters['linebreaks'] = linebreaks

import gitboard.views

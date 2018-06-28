from flask.cli import FlaskGroup

cli = FlaskGroup(help="gitboard")

from . import update  # NOQA

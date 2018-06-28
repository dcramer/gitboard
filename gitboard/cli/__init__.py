#!/usr/bin/env python


def main():
    import os

    os.environ.setdefault("PYTHONUNBUFFERED", "true")
    os.environ.setdefault("FLASK_APP", "gitboard.app")

    from .base import cli

    cli.main()

import click

from flask import current_app

from .base import cli


@cli.command()
def update():
    # from collections import defaultdict
    from gitboard.config import redis
    from gitboard.stats import Storage
    from gitboard.update import update_stats

    storage = Storage(redis)

    hours = 24

    # scores = defaultdict(int)
    for repo in current_app.config["REPOS"]:
        update_stats(repo)
        # print "----------------------------------------"
        # print "%dh Leaderboard for %s" % (hours, repo)
        # print "----------------------------------------"
        # i = 0
        # for author, score in storage.get_leaders(repo, hours):
        #     i += 1
        #     print "%d. %s (%s)" % (i, author, score)
        # print "----------------------------------------"

    click.echo("----------------------------------------")
    click.echo("%dh Global Leaderboard" % (hours,))
    click.echo("----------------------------------------")
    i = 0
    for author, score in storage.get_leaders(hours=hours):
        i += 1
        click.echo("%d. %s (%s)" % (i, author, score))
    click.echo("----------------------------------------")

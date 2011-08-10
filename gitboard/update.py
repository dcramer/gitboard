"""
gitboard.update
~~~~~~~~~~~~~~~

:copyright: (c) 2011 David Cramer.
:license: Apache License 2.0, see LICENSE for more details.
"""

from gitboard import app, redis
from gitboard.stats import Storage

import os, os.path
import time
from collections import defaultdict
from subprocess import Popen, PIPE

# Pretty-print the contents of the commit logs in a given format, where <format> can be one of oneline, short,
#            medium, full, fuller, email, raw and format:<string>

class CommandError(Exception):
    pass

class StreamReader(object):
    def __init__(self, p):
        self.p = p
    
    def __iter__(self):
        for line in self.p.stdout:
            line = line.strip()
            yield line
        if not self.p.wait() == 0:
            raise CommandError(self.p.stderr.read())

def execute(command, cwd=None):
    start = time.time()
    p = Popen(command, cwd=cwd, shell=True, stdout=PIPE, stderr=PIPE)
    try:
        return StreamReader(p)
    finally:
        print '>>> [%.4fs] %s' % (time.time() - start, command)

def get_repo_cache(repository):
    return os.path.join(app.config['CACHE_DIR'], *repository.split('/'))

def update_stats(repository):
    storage = Storage(redis.connect())
    
    since = storage.get_last_commit(repository)
    commits = get_commits_since(repository, since=since)
    for revision, commit in commits.iteritems():
        storage.store(repository, revision, **commit)

def get_commits_since(repository, since=None, until='HEAD'):
    """
    Polls the git repository returning a list of all commits since ``since` committish
    """
    
    aliases = app.config['ALIASES']

    # git shortlog -s HEAD | wc -l
    # git show-ref --tags
    commits = {}
    commits_by_author = defaultdict(list)
    
    repo_path = get_repo_cache(repository)
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
    
    if not os.path.exists(os.path.join(repo_path, '.git')):
        execute('git clone %s %s' % (repository, repo_path))
    
    execute('git fetch', cwd=repo_path)

    if since and until:
        refs = '%s..%s' % (since, until)
    elif since:
        refs = '%s..HEAD' % (since,)
    elif until:
        refs = until

    # list of files changed and their revision
    # 100644 blob 562d8ac92d42b40caf02f4340c6d89859eb2de1d	wsgi/spam.wsgi
    # for line in execute('git ls-tree -r HEAD', cwd=repo_path):
    #     if not line:
    #         continue
    #     info, filename = line.split('\t')
    #     mode, type_, revision = info.split(' ')
    #     if revision in 
    #     commits[revision]['files'] += 1
    
    # git log --shortstat --first-parent -m --pretty=format:"%T " HEAD
    # 562d8ac92d42b40caf02f4340c6d89859eb2de1d David Cramer
    # 54 files changed, 178230 insertions(+), 178275 deletions(-)
    chunk = []
    for line in execute('git log --shortstat --no-merges --all --pretty=format:"%%T %%at %%aE%%n%%s" %s' % refs, cwd=repo_path):
        if not line and len(chunk) > 2:
            # ['5314c27c5658be18b096ea9164232a7bd02ac74a', 'denormalize service urls', '3 files changed, 22 insertions(+), 13 deletions(-)']
            revision, timestamp, author = chunk[0].split(' ', 2)
            stats = chunk[-1].split(' ')
            author = aliases.get(author, author)
            commits[revision] = {
                'timestamp': int(timestamp),
                'author': author,
                'files': 0,
                'message': '\n'.join(chunk[1:-1]),
                'files': int(stats[0]),
                'insertions': int(stats[3]),
                'deletions': int(stats[5]),
            }
            commits_by_author[author].append(revision)

            chunk = []
        else:
            chunk.append(line)

    # git ls-tree -r HEAD
    # stdout = execute('git log --no-merges --all --format=oneline %s..%s' % (since or '', until), cwd=repo_path)
    return commits

if __name__ == '__main__':
    storage = Storage(redis.connect())

    hours = 24

    scores = defaultdict(int)
    for repo in app.config['REPOS']:
        try:
            update_stats(repo)
        except:
            continue
        # print "----------------------------------------"
        # print "%dh Leaderboard for %s" % (hours, repo)
        # print "----------------------------------------"
        # i = 0
        # for author, score in storage.get_leaders(repo, hours):
        #     i += 1
        #     print "%d. %s (%s)" % (i, author, score)
        # print "----------------------------------------"

    print "----------------------------------------"
    print "%dh Global Leaderboard" % (hours,)
    print "----------------------------------------"
    i = 0
    for author, score in storage.get_leaders(hours=hours):
        i += 1
        print "%d. %s (%s)" % (i, author, score)
    print "----------------------------------------"

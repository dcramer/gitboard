"""
gitboard.stats
~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from collections import defaultdict
from datetime import datetime, timedelta

class Storage(object):
    def __init__(self, redis):
        self.redis = redis
    
    def store(self, repository, revision, author, timestamp, message, **kwargs):
        self.redis.hmset('commits:%s:%s' % (repository, revision), dict(
            author=author,
            timestamp=timestamp,
            message=message,
            **kwargs
        ))
        
        added = self.redis.zadd('commits:%s' % repository, revision, timestamp)

        if not added:
            return
        
        date = datetime.fromtimestamp(timestamp)

        score = 1
        
        message_length = len(message or '')
        if message_length > 35:
            score += 1
        elif not message_length:
            score -= 3
        elif message_length < 10:
            score -=1

        if 'github.com' in message:
            score += 2
        elif 'http://' in message or 'https://' in message:
            score += 1

        self.redis.zincrby('scores:%s:%s' % (repository, date.strftime('%I-%d-%Y:%H:00')), author, score)
        self.redis.zincrby('scores:global:%s' % (date.strftime('%I-%d-%Y:%H:00')), author, score)

    def get_leaders(self, repository='global', hours=24):
        keybase = 'scores:%s:%%s' % (repository,)
        
        date = datetime.utcnow()
        
        results = defaultdict(int)
        for hour in xrange(hours):
            key = keybase % (date - timedelta(hours=hour)).strftime('%I-%d-%Y:%H:00')
            for result, score in self.redis.zrevrange(key, 0, -1, withscores=True):
                results[result] += score
        
        return sorted(results.items(), key=lambda x: x[1], reverse=True)

    def get_last_commit(self, repository):
        try:
            return self.redis.zrange('commits:%s' % repository, 0, 1)[0]
        except IndexError:
            return None
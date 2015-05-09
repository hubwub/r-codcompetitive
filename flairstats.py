"""
A quick and dirty script to show some flair statistics.

Currently it only shows how many users have flair, and how many use
each css class or flair text.

Usage:
    1) run flair-stats.py
    2) enter username and password when asked
    3) enter subreddit name (eg: starcraft)
    4) enter 'class' if css class shall be fetched, otherwise 'text'
    5) Wait for statistics to load (could take a while for big subreddits)

    Forked by joeycastillo to add custom user agent and rate limiting.
    Tested successfully on a subreddit with ~11,000 flair users.

    Forked by schrobby to include support for flair_text statistics.
"""

from __future__ import division

import cookielib
import urllib2
import json
import operator
from urllib import urlencode
from getpass import getpass
from time import sleep

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'very_quick_flair_stats_generator.py 0.1a')]

def login(user, passwd):
    url = 'http://www.reddit.com/api/login'
    r = opener.open(url, urlencode({'user': user, 'passwd': passwd}))

def get_modhash():
    url = 'http://www.reddit.com/api/me.json'
    data = json.load(opener.open(url))
    return data['data']['modhash'] if 'data' in data else False

def flair_stats(subreddit, modhash, fetch):
    url = 'http://www.reddit.com/r/%s/api/flairlist.json?' % (subreddit,)
    stats = {'total': 0, 'class': {} }
    q = {'limit': 1000, 'uh': modhash}

    _next = None
    while True:
        if _next:
            q['after'] = _next
        sleep(2)
        data = json.load(opener.open(url + urlencode(q)))
        if not data:
            break
        for user in data['users']:
            c = user['flair_' + fetch]
            if c not in stats['class']:
                stats['class'][c] = 0
            stats['class'][c] += 1
            stats['total'] += 1
        if 'next' not in data:
            break
        _next = data['next']

    return stats

if __name__ == '__main__':
    import sys
    username = raw_input('username: ')
    passwd = getpass('password: ')
    login(username, passwd)
    modhash = get_modhash()
    if not modhash:
        print 'Unable to get modhash (invalid login?)'
        sys.exit(1)

    subreddit = raw_input('subreddit: ')
    fetch = 'css_class' if raw_input('fetch class or text: ') == 'class' else 'text'
    print 'Loading stats...'
    stats = flair_stats(subreddit, modhash, fetch)
    print
    print 'Total flair users: %d' % (stats['total'],)
    flair_stats = stats['class']
    sorted_fstats = sorted(flair_stats.items(), key=operator.itemgetter(1), reverse=True)
    for k, v in sorted_fstats:
        print '\t%s: %d (%.2f%%)' % (k, v, v / stats['total'] * 100)


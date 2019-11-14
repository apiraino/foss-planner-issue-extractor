# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import os
import requests
import json
import dateparser
import csv

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)
GITHUB_URL = 'api.github.com/repos'
GITHUB_OWNER = 'rust-lang'
GITHUB_REPO = 'rust'
# GITHUB_OWNER = 'gtk-rs'
# GITHUB_REPO = 'gtk'
DEST_FILE = 'issues.csv'
HEADER = ['ID', 'CREATED_AT', 'UPDATED_AT', 'TITLE', 'AUTHOR', 'REVIEWER', 'URL', 'COMMENT_TS', 'LAST_COMMENT_URL']

# https://hackmd.io/i4JxpNcWSWmx73qGwFWX-w


class ReqError(Exception):
    def __init__(self, message, retry=False):
        super(ReqError, self).__init__(message)
        self.retry = retry


if not GITHUB_TOKEN:
    raise ReqError('Missing $GITHUB_TOKEN')


def _make_request(method, url, payload=None):
    try:
        resp = requests.request(
            method,
            url,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'token {}'.format(GITHUB_TOKEN)
            },
            data=json.dumps(payload),
            timeout=30,
            verify=True
        )
    except requests.exceptions.Timeout as exc:
        raise ReqError(
            u'Timeout: could not connect to host {}: {}'.format(url, exc),
            retry=True
        )
    except requests.exceptions.ConnectionError as exc:
        raise ReqError(
            u'ConnectionError: could not connect to host {}: {}'
            .format(url, exc),
            retry=True
        )
    if resp.status_code // 100 > 2:
        raise ReqError(
            u'Error in server response, got {}: {}'
            .format(resp.status_code,
                    resp.content)
        )
    return resp


def make_issue_url(param_sort='updated#desc', labels=''):
    (sort, direction) = param_sort.split('#')
    url = 'https://{}/{}/{}/issues?state=open&sort={}&direction={}'.format(
        GITHUB_URL,
        GITHUB_OWNER,
        GITHUB_REPO,
        sort,
        direction
    )
    if labels:
        url += '&labels={}'.format(labels)
    return url


def make_request(url):
    # print('Requesting {}'.format(url))
    items = list()
    resp = _make_request('GET', url)
    items = resp.json()
    while 'next' in resp.links:
        url = resp.links['next']['url']
        # print('Requesting {}'.format(url))
        resp = _make_request('GET', url)
        items.extend(resp.json())
    return items


def parse_issue(issue):
    author = issue['user']['login']
    assignee = reviewer = comment_ts = comment_url = None
    if issue.get('assignee'):
        assignee = issue['assignee']['login']
        comment_ts, reviewer, comment_url = get_last_comment(issue['comments_url'], assignee, author)
        if not reviewer:
            reviewer = assignee
    return {
        'id': issue['number'],
        'title': issue['title'],
        'created_at': issue['created_at'],
        'updated_at': issue['updated_at'],
        'num_comments': issue['comments'],
        'state': issue['state'],
        'url': issue['html_url'],
        'author': author,
        'reviewer': reviewer,
        'comment_ts': comment_ts,
        'last_comment_url': comment_url
    }


def parse_body(issue_body=''):
    body_lines = issue_body.split('\r\n')
    return body_lines[0]


def get_last_comment(comments_url, assignee, author):
    curr_date = dateparser.parse('1970-01-01T00:00:00Z')
    comment_url = reviewer = updated_at_str = None
    comments = make_request(comments_url)
    comments.reverse()
    print('-- Found {} comments'.format(len(comments)))
    for comment in comments:
        if (comment['user']['login'] in [assignee, author] or
                comment['author_association'] in ['MEMBER', 'CONTRIBUTOR']):
            new_date = dateparser.parse(comment['created_at'])
            if new_date > curr_date:
                updated_at_str = comment['created_at']
                comment_url = comment['html_url']
                reviewer = comment['user']['login']
                curr_date = new_date
    return (updated_at_str, reviewer, comment_url)


if __name__ == '__main__':
    print("-- Getting issues from github ...")
    # - filter by S-waiting-on-review
    # - filter by S-waiting-on-author
    labels = ''
    if len(sys.argv) == 2:
        labels = sys.argv[1]
    issue_url = make_issue_url(labels=labels)
    issues = make_request(issue_url)
    issues.reverse()
    print('-- Found {} open issues'.format(len(issues)))
    if os.path.exists(DEST_FILE):
        os.unlink(DEST_FILE)

    with open(DEST_FILE, 'w') as fp:
        _writer = csv.writer(fp, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        _count = 0
        row = []
        for header_fld in HEADER:
            row.append(header_fld)
        _writer.writerow(row)
        for issue in issues:
            row = []
            print("-- Got issue #{}".format(issue['number']))
            # if _count == 10:
            #     break
            data = parse_issue(issue)
            body = parse_body(issue['body'])
            for fld in data:
                row.append(str(data[fld]))
            _writer.writerow(row)
            _count += 1
        print("-- {} written".format(DEST_FILE))

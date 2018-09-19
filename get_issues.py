# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import requests
import json

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)
GITHUB_URL = 'api.github.com/repos'
GITHUB_OWNER = 'rust-community'
GITHUB_REPO = 'foss-events-planner'
DEST_FILE = 'issues.txt'


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


def make_request():
    # only 'open' issues to avoid PRs :-/
    url = 'https://{}/{}/{}/issues?state=open'.format(
        GITHUB_URL,
        GITHUB_OWNER,
        GITHUB_REPO
    )
    issues = list()

    def parse_resp(data):
        for issue in data:
            issues.append(
                {
                    'title': issue['title'],
                    'body': issue['body']
                }
            )

    resp = _make_request('GET', url)
    parse_resp(resp.json())
    while 'next' in resp.links:
        url = resp.links['next']['url']
        resp = _make_request('GET', url)
        parse_resp(resp.json())
    return issues


if __name__ == '__main__':
    print("-- Getting issues from github ...")
    issues = make_request()
    print('-- Found {} open issues'.format(len(issues)))
    # import pudb; pudb.set_trace()
    if os.path.exists(DEST_FILE):
        os.unlink(DEST_FILE)
    with open(DEST_FILE, 'w') as fp:
        for issue in issues:
            issue_body = issue['body'] or ''
            for body_line in issue_body.split('\r\n'):
                fp.write("[{}] {}--\n".format(
                    issue['title'],
                    body_line
                ))
        print("-- {} written".format(DEST_FILE))

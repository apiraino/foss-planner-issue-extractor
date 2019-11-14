### Retrieve and pretty print the RustFest FOSS planner issues


Tested on Python 2.7+ and 3.7.

Login into GitHub and [generate an access
token](https://github.com/settings/tokens) for your account. Export it as `$GITHUB_TOKEN`.

### Requirements

- `pip install requests`

or

- `[ pip | brew ] install pipenv`
- `pipenv install` install packages and create a vitualenv automatically
- `pipenv shell` to enter the virtualenv

### Run

1. Get issues
```
$ python get_issues.py
```

2. Then grep+sed to extract them ordered
``` bash
$ sh sort_issues_by_label.sh
```

### Notes

This script equals to running a paginated version (+ parsing) of:
```bash
$ curl --silent -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/<repo_owner>/<repo_name>/issues
```

[Gihub APIs](https://developer.github.com/v3/issues/#parameters)

Issues and pull requests *are* the [same entity](https://developer.github.com/v3/issues/#list-issues-for-a-repository) in Github:

<figure>
    <img src="gh_api_pr_issue.png">
    <figcaption>(because endpoints aren't cheap)</figcaption>
</figure>

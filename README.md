ckanext-ytp-comments
====================
A custom CKAN extension for Data.Qld

[![Tests](https://github.com/qld-gov-au/ckanext-ytp-comments/actions/workflows/test.yml/badge.svg)](https://github.com/qld-gov-au/ckanext-ytp-comments/actions/workflows/test.yml)

[![CircleCI](https://circleci.com/gh/qld-gov-au/ckanext-ytp-comments/tree/develop.svg?style=shield)](https://circleci.com/gh/qld-gov-au/ckanext-ytp-comments/tree/develop)

## Local environment setup
- Make sure that you have latest versions of all required software installed:
  - [Docker](https://www.docker.com/)
  - [Pygmy](https://pygmy.readthedocs.io/)
  - [Ahoy](https://github.com/ahoy-cli/ahoy)
- Make sure that all local web development services are shut down (Apache/Nginx, Mysql, MAMP etc).
- Checkout project repository (in one of the [supported Docker directories](https://docs.docker.com/docker-for-mac/osxfs/#access-control)).
- `pygmy up`
- `ahoy build`
- You may need to use sudo on linux

Building on Ubuntu (optional: behind proxy)
- composer from compose
  - sudo pip install docker-compose
- sudo apt-get install composer
- ensure /etc/gemrc has the following
  ``http_proxy: http://localhost:3128
    https_proxy: http://localhost:3128``
- if squid proxy is in use on your machine ensure that ``acl localnet src 172.17.0.0/16``  #  allows your public ip for loopback
- https://docs.docker.com/network/proxy/
  ~/.docker/config.json
  ``
{
 "proxies":
  {
  "default":
   {
     "httpProxy": "http://hostexternalip:3128",
     "httpsProxy": "http://hostexternalip:3128",
     "noProxy": ""
   }
  }
}
``
  - https://docs.docker.com/config/daemon/systemd/
    sudo mkdir -p /etc/systemd/system/docker.service.d
    sudo vi /etc/systemd/system/docker.service.d/http-proxy.conf
    ``[Service]
      Environment="HTTP_PROXY=http://localhost:3128/"``
    sudo vi /etc/systemd/system/docker.service.d/https-proxy.conf
    ``[Service]
      Environment="HTTPS_PROXY=http://localhost:3128/"``
    sudo systemctl daemon-reload
    sudo systemctl restart docker


Use `admin`/`password` to login to CKAN.

## Available `ahoy` commands
Run each command as `ahoy <command>`.
  ```
   build        Build or rebuild project.
   clean        Remove containers and all build files.
   cli          Start a shell inside CLI container or run a command.
   doctor       Find problems with current project setup.
   down         Stop Docker containers and remove container, images, volumes and networks.
   flush-redis  Flush Redis cache.
   info         Print information about this project.
   install-site Install a site.
   lint         Lint code.
   logs         Show Docker logs.
   pull         Pull latest docker images.
   reset        Reset environment: remove containers, all build, manually created and Drupal-Dev files.
   restart      Restart all stopped and running Docker containers.
   start        Start existing Docker containers.
   stop         Stop running Docker containers.
   test-bdd     Run BDD tests.
   test-unit    Run unit tests.
   up           Build and start Docker containers.
  ```

## Coding standards
Python code linting uses [flake8](https://github.com/PyCQA/flake8) with configuration captured in `.flake8` file.

Set `ALLOW_LINT_FAIL=1` in `.env` to allow lint failures.

## Nose tests
`ahoy test-unit`

Set `ALLOW_UNIT_FAIL=1` in `.env` to allow unit test failures.

## Behavioral tests
`ahoy test-bdd`

Set `ALLOW_BDD_FAIL=1` in `.env` to allow BDD test failures.

### How it works
We are using [Behave](https://github.com/behave/behave) BDD _framework_ with additional _step definitions_ provided by [Behaving](https://github.com/ggozad/behaving) library.

Custom steps described in `test/features/steps/steps.py`.

Test scenarios located in `test/features/*.feature` files.

Test environment configuration is located in `test/features/environment.py` and is setup to connect to a remote Chrome
instance running in a separate Docker container.

During the test, Behaving passes connection information to [Splinter](https://github.com/cobrateam/splinter) which
instantiates WebDriver object and establishes connection with Chrome instance. All further communications with Chrome
are handled through this driver, but in a developer-friendly way.

For a list of supported step-definitions, see https://github.com/ggozad/behaving#behavingweb-supported-matcherssteps.

## Automated builds (Continuous Integration)
In software engineering, continuous integration (CI) is the practice of merging all developer working copies to a shared mainline several times a day.
Before feature changes can be merged into a shared mainline, a complete build must run and pass all tests on CI server.

This project uses [GitHub Actions](https://github.com/features/actions) as a CI server: it imports production backups into fully built codebase and runs code linting and tests. When tests pass, a deployment process is triggered for nominated branches (usually, `master` and `develop`).

## Follow / Mute comments

Comment notifications (via email) are managed by opt-in, i.e. without opting in to receive comment notifications at the content item or thread level,
only authors or organisation admins will receive email notifications.

This feature allows users to following or mute comments at the content item level or for a specific comment thread on the content item.

When a user follows comments on a content item or content item thread they will receive email notifications when new comments or replies are posted.

### Blacklist Words

Comments are checked using the [profanityfilter](https://github.com/areebbeigh/profanityfilter) Python module; any comments containing profanity are blocked.

'profanityfilter' has a built-in blacklist of words. Additional banned words are contained in `ckanext/ytp/comments/bad_words.txt` by default.
You can point to another word list by setting `ckan.comments.bad_words_file` in your config.

Any words from the built-in list that you do *not* wish to block are contained in `ckanext/ytp/comments/good_words.txt` by default.
You can point to another word list by setting `ckan.comments.good_words_file` in your config.

## Installation

1. Initialise the comment notification recipients database table, e.g.

        cd /usr/lib/ckan/default/src/ckanext-ytp-comments  # Your PATH may vary
        ckan -c /etc/ckan/default/development.ini initdb  # Use YOUR path and relevant CKAN .ini file
        ckan -c /etc/ckan/default/development.ini updatedb  # Use YOUR path and relevant CKAN .ini file
        ckan -c /etc/ckan/default/development.ini init_notifications_db  # Use YOUR path and relevant CKAN .ini file

    This will create a new table in the CKAN database named `comment_notification_recipient` that holds the status of individual user's follow or mute preferences.

    *Note:* if your deployment process does not run `python setup.py develop` after deploying code changes for extensions, you may need to run this in order for 'ckan' to recognise the `init_notifications_db` command:

        python setup.py develop

2. Add the following config settings to your CKAN `.ini` file:

        ckan.comments.follow_mute_enabled = True
        # Optional
        ckan.comments.bad_words_file = /path/to/blacklist_words.txt
        ckan.comments.good_words_file = /path/to/whitelist_words.txt
        # To display dataset comments on a datasets tab page instead of below the dataset additional information, set to True
        ckan.comments.show_comments_tab_page = True # Defaults to False

3. Restart CKAN


tuneharvest
===========

[![Build Status](https://travis-ci.org/kcsaff/tuneharvest.svg?branch=master)](https://travis-ci.org/kcsaff/tuneharvest)

This is a simple tool to harvest music suggestions from a slack channel, and then
create & maintain a youtube playlist of these suggestions.

Requirements
============

1. Python 3.3+
2. A slack account
3. A youtube account

Installation
============

```
make install
```

Development
===========

```
make venv
. venv/bin/activate
python main.py
```

Configuration
=============

Slack token
-----------

Slack requires a single token, which you should store in a text file;
provide the name of the text file as an argument ``--token`` or ``-t`` to
the ``from slack`` subcommand.

Youtube keys
------------

You need to obtain a JSON secrets file from Google; you will also need
to obtain a refresh token that will either be obtained by user login in
a browser, or by following
[these instructions](http://stackoverflow.com/questions/19449061/upload-videos-to-my-youtube-channel-without-user-authentication-using-youtubeapi).

Getting this file is unfortunately a complicate, multi-step process -- foruntately, you only need to do it once per account.

 * Go to [Google's API developer console](https://console.developers.google.com/apis/dashboard?debugUI=DEVELOPERS&authuser=1&pli=1)
 * Create or select project
    * Click the dropdown "Select a project ▾"
    * Select, or, most likely, create a new project -- click the "➕" symbol and follow instructions
 * Create credentials
    * Click "Credentials" in the left-hand panel
    * Click the "Create Credentials ▾" dropdown, and select "Service account key"
    * Create a new service account using the "JSON" key type
    * Select service account role (TODO: what is necessary here?)
 * Enable Youtube API
    * Click "⊞ Enable API"
    * Select "Youtube Data API"
    * Click "▶ Enable"

Command-line usage
==================

Replace items in {brackets} with your values to execute these commands.

Harvest from a slack channel to a youtube playlist
--------------------------------------------------

```
tuneharvest from slack --token {token.txt} --query "has:link in:{my-music-channel}" \
    to youtube --secrets {secrets.txt} --title "{My playlist title}"
```

Harvest from a discourse thread to a youtube playlist
-----------------------------------------------------

```
tuneharvest from discourse {https://my.discourse-instance.com/t/my-music-thread} \
    to youtube --secrets {secrets.txt} --title "{My playlist title}"
```

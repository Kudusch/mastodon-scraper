#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config as config
import mastodon
import mastodon_functions as mf
import datetime
import sys
import traceback
import logging

logging.getLogger("mastodon_functions").setLevel(logging.DEBUG)

for api_base, access_token in config.mastodon_tokens.items():
    toots = mf.stream_timeline(api_base, access_token, max_toots = 50)
    mf.toots_to_csv(toots, file_name = f"test_{api_base}.csv", parse_html = True, instance_name = api_base, verbose = False)


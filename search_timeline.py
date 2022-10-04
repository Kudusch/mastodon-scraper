#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config as config
import mastodon_functions as mf
from datetime import datetime
import sys
import traceback
import logging

logging.getLogger("mastodon_functions").setLevel(logging.DEBUG)

query = sys.argv[1]

print(f"Searching for the query: {query}")

for api_base, access_token in config.mastodon_tokens.items():
    print(api_base)
    try:
        toots = mf.search_timeline(q = query, api_base = api_base, access_token = access_token, max_toots = 1000, verbose = False)
        mf.toots_to_csv(toots, file_name = f"../Data/timeline_test/{query}/{api_base}.csv", parse_html = True, instance_name = api_base, verbose = False)
        if toots:
            print(f"\t{api_base}: {len(toots)} toots received")
        else:
            print(f"\t{api_base}: No toots received")
    except Exception:
        print(f"Error getting toots from {api_base}")
        print(traceback.format_exc())

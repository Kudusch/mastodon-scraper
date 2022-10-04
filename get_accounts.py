#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config as config
from mastodon import Mastodon
import time
import requests
import json
import sys
import csv

# mastodon = Mastodon(
#     access_token = config.mastodon_tokens['access_token'],
#     api_base_url = config.mastodon_tokens['api_base_url']
# )

# print(mastodon)

domain = sys.argv[1]
#domain = "social.tchncs.de"

print(f"Getting users known to '{domain}'")

api_base = f"https://{domain}/api/v1"

params = (
    ("order", "new"),
    ("limit", 80)
)

r = requests.get(f"{api_base}/directory", params = params + (("offset", 0),))
if r.status_code == 200:
    accounts = r.json()
    current_offset = 80
    print(f"Recieved {len(accounts)} accounts", end = "\r")

    # 300 requests per 5 minutes, 1 request per second
    try:
        while r.status_code == 200 and len(r.json()) > 0:
            time.sleep(1)
            r = requests.get(f"{api_base}/directory", params = params + (("offset", current_offset),))
            accounts.extend(r.json())
            current_offset += 80
            print(f"Recieved {len(accounts)} accounts", end = "\r")
    except Exception as e:
        print(str(e))

    print(f"Recieved {len(accounts)} accounts")
    json.dump(accounts, open(f"Data/{domain}_accounts.json", "w"))

    with open(f"Data/{domain}_accounts.csv", "w") as out_file:
        writer = csv.writer(out_file, delimiter=";")
        writer.writerow(['id', 'username', 'acct', 'display_name', 'locked', 'bot', 'discoverable', 'group', 'created_at', 'note', 'url', 'avatar', 'avatar_static', 'header', 'header_static', 'followers_count', 'following_count', 'statuses_count', 'last_status_at', 'emojis', 'fields'])
        for a in accounts:
            writer.writerow([
                a['id'], 
                a['username'], 
                a['acct'], 
                a['display_name'], 
                a['locked'], 
                a['bot'], 
                a['discoverable'], 
                a['group'], 
                a['created_at'], 
                a['note'], 
                a['url'], 
                a['avatar'], 
                a['avatar_static'],
                a['header'], 
                a['header_static'], 
                a['followers_count'], 
                a['following_count'], 
                a['statuses_count'], 
                a['last_status_at'], 
                json.dumps(a['emojis']), 
                json.dumps(a['fields'])
            ])

else:
    print(r.text, r.url)
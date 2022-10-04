#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config as config
import mastodon_functions as mf
from mastodon import Mastodon
from datetime import datetime
import sys
import traceback
import logging

#logging.getLogger("mastodon_functions").setLevel(logging.DEBUG)

queried_hashtag = sys.argv[1]

instance_list = ["mastodon.social", "mastodon.xyz", "pawoo.net", "social.tchncs.de", "mastodon.cloud", "fosstodon.org", "cybre.space", "mamot.fr", "octodon.social", "mastodon.technology", "mstdn.io", "mstdn.jp", "chaos.social", "qoto.org", "linuxrocks.online", "framapiaf.org", "social.coop", "eldritch.cafe", "social.linux.pizza", "floss.social", "anticapitalist.party", "toot.cafe", "queer.party", "koyu.space", "mastodon.bida.im", "scholar.social", "mas.to", "icosahedron.website", "mastodon.ar.al", "wandering.shop", "hackers.town", "bsd.network", "toot.cat", "layer8.space", "sunbeam.city", "elekk.xyz", "writing.exchange", "social.weho.st", "bitcoinhackers.org", "maly.io", "101010.pl", "social.librem.one", "pleroma.soykaf.com", "photog.social", "aleph.land", "metalhead.club", "mastodon.online", "www.masto.pt", "masto.pt", "vulpine.club"]

print(f"Searching for the hashtag #{queried_hashtag}")

for api_base in instance_list:
    try:
        toots = mf.search_hashtag(queried_hashtag, api_base, min_date = "2022-01-01", verbose = False)
        mf.toots_to_csv(toots, file_name = f"../Data/search_test/{queried_hashtag}/{api_base}.csv", parse_html = True, instance_name = api_base, verbose = False)
        if toots:
            print(f"\t{api_base}: {len(toots)} toots received")
        else:
            print(f"\t{api_base}: No toots received")
    except Exception:
        print(f"Error getting toots from {api_base}")
        print(traceback.format_exc())

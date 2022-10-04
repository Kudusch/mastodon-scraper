#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mastodon
from bs4 import BeautifulSoup
import time
import os
import csv
import sys
import json
import logging
import datetime
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4') # ignore MarkupResemblesLocatorWarning

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '[%(levelname)s] | %(asctime)s | "%(message)s" | %(filename)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)

key_names = ["id", "created_at", "edited_at", "content", "reblog", "sensitive", "spoiler_text", "visibility", "replies_count", "reblogs_count", "favourites_count", "language", "in_reply_to_id", "in_reply_to_account_id", "user_id", "user_name", "user_acct", "user_locked", "user_bot", "user_discoverable", "user_group", "user_created_at", "user_note", "user_url", "user_avatar", "user_header", "user_followers_count", "user_following_count", "user_statuses_count", "user_last_status_at", "user_emojis", "user_fields", "media_id", "media_type", "media_url", "media_preview_url", "media_remote_url", "media_preview_remote_url", "media_text_url", "media_meta", "media_description", "media_blurhash", "mentions_id", "mentions_username", "mentions_url", "mentions_acct", "hashtags", "card_url", "card_title", "card_description", "card_type", "card_author_name", "card_author_url", "card_provider_name", "card_provider_url", "card_html", "card_width", "card_height", "card_image", "card_embed_url", "card_blurhash", "poll_id", "poll_expires_at", "poll_expired", "poll_multiple", "poll_votes_count", "poll_voters_count", "poll_options", "poll_votes", "uri", "url", "instance_name", "queried_at"]

def get_datetime_range(toots):
    values = [t["created_at"] for t in toots]
    return(f"created_at from {min(values):%Y-%m-%d %H:%M} to {max(values):%Y-%m-%d %H:%M}")

def add_queried_at(toots):
    queried_at = datetime.datetime.now()
    for toot in toots:
        toot["queried_at"] = queried_at
    return toots

def filter_toots(toots, query):
    filtered_toots = [t for t in toots if query in t["content"]]
    return filtered_toots

# check moved_to
def sanitize_toot(raw_toot, instance_name = None, parse_html = False):
    toot = {
        "id":raw_toot["id"],
        "in_reply_to_id":raw_toot["in_reply_to_id"],
        "in_reply_to_account_id":raw_toot["in_reply_to_account_id"],
        "sensitive":raw_toot["sensitive"],
        "spoiler_text":raw_toot["spoiler_text"],
        "visibility":raw_toot["visibility"],
        "language":raw_toot["language"],
        "uri":raw_toot["uri"],
        "url":raw_toot["url"],
        "replies_count":raw_toot["replies_count"],
        "reblogs_count":raw_toot["reblogs_count"],
        "favourites_count":raw_toot["favourites_count"],
        "reblog":raw_toot["reblog"],
    }

    if parse_html:
        try:
            toot_content = BeautifulSoup(raw_toot["content"], "html.parser")
            for e in toot_content.find_all(["p", "br"]):
                e.append('\n')
            toot["content"] = toot_content.text
        except MarkupResemblesLocatorWarning:
            pass
        except:
            toot["content"] = raw_toot["content"]
    else:
        toot["content"] = raw_toot["content"]

    toot["created_at"] = format(raw_toot["created_at"], "%Y-%m-%dT%H:%M:%S")
    if "edited_at" in raw_toot.keys() and raw_toot["edited_at"] is not None:
        toot["edited_at"] = datetime.datetime.strptime(f"{raw_toot['edited_at']} -0000", "%Y-%m-%dT%H:%M:%S.%fZ %z")
        toot["edited_at"] = format(toot["edited_at"], "%Y-%m-%dT%H:%M:%S")
    else:
        toot["edited_at"] = ""
    
    toot["user_id"] = raw_toot["account"]["id"]
    toot["user_name"] = raw_toot["account"]["display_name"]
    toot["user_acct"] = raw_toot["account"]["acct"]
    toot["user_locked"] = raw_toot["account"]["locked"]
    toot["user_bot"] = raw_toot["account"]["bot"]
    try:
        toot["user_discoverable"] = raw_toot["account"]["discoverable"]
    except:
        toot["user_discoverable"] = ""
    try:
        toot["user_group"] = raw_toot["account"]["group"]
    except:
        toot["user_group"] = ""
    toot["user_created_at"] = format(raw_toot["account"]["created_at"], "%Y-%m-%dT%H:%M:%S")
    toot["user_note"] = raw_toot["account"]["note"]
    toot["user_url"] = raw_toot["account"]["url"]
    toot["user_avatar"] = raw_toot["account"]["avatar"]
    toot["user_header"] = raw_toot["account"]["header"]
    toot["user_followers_count"] = raw_toot["account"]["followers_count"]
    toot["user_following_count"] = raw_toot["account"]["following_count"]
    toot["user_statuses_count"] = raw_toot["account"]["statuses_count"]
    try:
        toot["user_last_status_at"] = format(raw_toot["account"]["last_status_at"], "%Y-%m-%dT%H:%M:%S")
    except:
        toot["user_last_status_at"] = ""
    toot["user_emojis"] = json.dumps(raw_toot["account"]["emojis"])
    toot["user_fields"] = json.dumps(raw_toot["account"]["fields"])

    list_id = []
    list_type = []
    list_url = []
    list_preview_url = []
    list_remote_url = []
    list_preview_remote_url = []
    list_text_url = []
    list_meta = []
    list_description = []
    list_blurhash = []
    for media in raw_toot["media_attachments"]:
        list_id.append(media["id"])
        list_type.append(media["type"])
        list_url.append(media["url"])
        list_preview_url.append(media["preview_url"])
        list_remote_url.append(media["remote_url"])
        try:
            list_preview_remote_url.append(media["preview_remote_url"])
        except:
            list_preview_remote_url.append("")
        list_text_url.append(media["text_url"])
        try:
            list_meta.append(media["meta"])
        except:
            list_meta.append("")
        list_description.append(media["description"])
        try:
            list_blurhash.append(media["blurhash"])
        except:
            list_blurhash.append("")

    toot["media_id"] = json.dumps(list_id)
    toot["media_type"] = json.dumps(list_type)
    toot["media_url"] = json.dumps(list_url)
    toot["media_preview_url"] = json.dumps(list_preview_url)
    toot["media_remote_url"] = json.dumps(list_remote_url)
    toot["media_preview_remote_url"] = json.dumps(list_preview_remote_url)
    toot["media_text_url"] = json.dumps(list_text_url)
    toot["media_meta"] = json.dumps(list_meta)
    toot["media_description"] = json.dumps(list_description)
    toot["media_blurhash"] = json.dumps(list_blurhash)

    list_id = []
    list_username = []
    list_url = []
    list_acct = []
    for mention in raw_toot["mentions"]:
        list_id.append(mention["id"])
        list_username.append(mention["username"])
        list_url.append(mention["url"])
        list_acct.append(mention["acct"])

    toot["mentions_id"] = json.dumps(list_id)
    toot["mentions_username"] = json.dumps(list_username)
    toot["mentions_url"] = json.dumps(list_url)
    toot["mentions_acct"] = json.dumps(list_acct)

    toot["hashtags"] = json.dumps([hashtag["name"] for hashtag in raw_toot["tags"]])

    if raw_toot["card"] is not None:
        toot["card_url"] = raw_toot["card"]["url"]
        toot["card_title"] = raw_toot["card"]["title"]
        toot["card_description"] = raw_toot["card"]["description"]
        toot["card_type"] = raw_toot["card"]["type"]
        try:
            toot["card_author_name"] = raw_toot["card"]["author_name"]
        except:
            toot["card_author_name"] = ""
        toot["card_author_url"] = raw_toot["card"]["author_url"]
        toot["card_provider_name"] = raw_toot["card"]["provider_name"]
        toot["card_provider_url"] = raw_toot["card"]["provider_url"]
        toot["card_html"] = raw_toot["card"]["html"]
        toot["card_width"] = raw_toot["card"]["width"]
        toot["card_height"] = raw_toot["card"]["height"]
        toot["card_image"] = raw_toot["card"]["image"]
        toot["card_embed_url"] = raw_toot["card"]["embed_url"]
        try:
            toot["card_blurhash"] = raw_toot["card"]["blurhash"]
        except:
            toot["card_blurhash"] = ""
    else:
        toot["card_url"] = ""
        toot["card_title"] = ""
        toot["card_description"] = ""
        toot["card_type"] = ""
        toot["card_author_name"] = ""
        toot["card_author_url"] = ""
        toot["card_provider_name"] = ""
        toot["card_provider_url"] = ""
        toot["card_html"] = ""
        toot["card_width"] = ""
        toot["card_height"] = ""
        toot["card_image"] = ""
        toot["card_embed_url"] = ""
        toot["card_blurhash"] = ""

    if raw_toot["poll"] is not None:
        toot["poll_id"] = raw_toot["poll"]["id"]
        try:
            toot["poll_expires_at"] = format(raw_toot["poll"]["expires_at"], "%Y-%m-%dT%H:%M:%S")
        except:
            toot["poll_expires_at"] = ""
        toot["poll_expired"] = raw_toot["poll"]["expired"]
        toot["poll_multiple"] = raw_toot["poll"]["multiple"]
        toot["poll_votes_count"] = raw_toot["poll"]["votes_count"]
        toot["poll_voters_count"] = raw_toot["poll"]["voters_count"]
        toot["poll_options"] = json.dumps([option["title"] for option in raw_toot["poll"]["options"]])
        toot["poll_votes"] = json.dumps([option["votes_count"] for option in raw_toot["poll"]["options"]])
    else:
        toot["poll_id"] = ""
        toot["poll_expires_at"] = ""
        toot["poll_expired"] = ""
        toot["poll_multiple"] = ""
        toot["poll_votes_count"] = ""
        toot["poll_voters_count"] = ""
        toot["poll_options"] = ""
        toot["poll_votes"] = ""

    toot["queried_at"] = format(raw_toot["queried_at"], "%Y-%m-%dT%H:%M:%S")
    
    if instance_name is not None:
        toot["instance_name"] = instance_name
    else:
        toot["instance_name"] = ""

    return toot

def toots_to_csv(queried_toots, file_name, parse_html = False, instance_name = None, append=False, verbose=False):
    if verbose and logger.level >= 20:
        logger.setLevel(logging.INFO)
    
    file_mode = "a+" if append else "w"
    if append:
        logger.info(f"Appending to {file_name}")
    else:
        logger.info(f"Writing to {file_name}")
        if os.path.isfile(file_name):
            logger.warning(f"Overwriting existing file!")

    if queried_toots:
        with open(file_name, file_mode, newline='') as f:
            writer = csv.writer(f, dialect="unix")
            if not append:
                writer.writerow(key_names)
            elif append and os.path.getsize(file_name) == 0:
                writer.writerow(key_names)
            for toot in queried_toots:
                try:
                    sanitized_toot = sanitize_toot(toot, parse_html = parse_html, instance_name = instance_name)
                    writer.writerow([sanitized_toot[k] for k in key_names])
                except Exception as e:
                    logger.error(f"Error sanitizing toot: {str(e)}")
        logger.info(f"{len(queried_toots)} toots written")
    else:
        logger.warning(f"No toots to write to file")

    if verbose and logger.level >= 20:
        logger.setLevel(logging.WARNING)

def search_hashtag(queried_hashtag, api_base, max_toots = None, min_date = None, verbose=False):
    if verbose and logger.level >= 20:
        logger.setLevel(logging.INFO)

    api = mastodon.Mastodon(api_base_url = api_base)

    if queried_hashtag[0] == "#":
        logger.warning(f"Leading '#' was removed from queried hashtag.")
        queried_hashtag = queried_hashtag[1:]

    if max_toots is not None and min_date is None:
        max_toots = int(max_toots)
    elif min_date is not None and max_toots is None:
        min_date = datetime.datetime.strptime(f"{min_date} -0000", "%Y-%m-%d %z")
    else:
        raise Exception("Must set either max_toots or min_date")

    queried_toots = []
    try:
        new_toots = api.timeline_hashtag(hashtag = queried_hashtag, limit=40)
        new_toots = add_queried_at(new_toots)
        queried_toots.extend(new_toots)
    except mastodon.MastodonAPIError as e:
        logger.warning(f"There was a problem connecting to {api_base}: {e.args[1:]}")
        return None

    if len(queried_toots) == 0:
        logger.warning(f"No toots with that hashtag found")
        
        if verbose and logger.level >= 20:
            logger.setLevel(logging.WARNING)
        return None

    max_id = min([t["id"] for t in new_toots])
    last_toot_at = min([t["created_at"] for t in new_toots])
    logger.debug(f"Retrieved {len(queried_toots)} toots {last_toot_at:%Y-%m-%d %H:%M}")

    paginate = True
    while paginate:
        new_toots = api.timeline_hashtag(hashtag = queried_hashtag, limit=40, max_id =  max_id)
        if len(new_toots) > 0:
            max_id = min([t["id"] for t in new_toots])
            last_toot_at = min([t["created_at"] for t in new_toots])
            new_toots = add_queried_at(new_toots)
            queried_toots.extend(new_toots)
            if max_toots is not None and min_date is None:
                paginate = True if len(queried_toots) < max_toots else False
            elif min_date is not None and max_toots is None:
                paginate = True if min_date < last_toot_at else False
            time.sleep(2)
            logger.debug(f"Retrieved {len(new_toots)} new toots and {len(queried_toots)} toots in total ({last_toot_at:%Y-%m-%d %H:%M})")
        else:
            paginate = False

    logger.info(f"Retrieved {len(queried_toots)} toots ({get_datetime_range(queried_toots)})")

    if verbose and logger.level >= 20:
        logger.setLevel(logging.WARNING)

    return queried_toots

def search_timeline(q, api_base, access_token, max_toots = None, min_date = None, verbose=False):
    if verbose and logger.level >= 20:
        logger.setLevel(logging.INFO)

    api = mastodon.Mastodon(api_base_url = api_base, access_token = access_token)

    if q is None:
        logger.error(f"Must supply a query")
        return None

    if max_toots is not None and min_date is None:
        max_toots = int(max_toots)
    elif min_date is not None and max_toots is None:
        min_date = datetime.datetime.strptime(f"{min_date} -0000", "%Y-%m-%d %z")
    else:
        raise Exception("Must set either max_toots or min_date")

    queried_toots = []
    try:
        new_toots = api.timeline_public(limit=40)
        new_toots = add_queried_at(new_toots)
        queried_toots.extend(filter_toots(new_toots, q))
    except mastodon.MastodonAPIError as e:
        logger.warning(f"There was a problem connecting to {api_base}: {e.args[1:]}")
        return None

    max_id = min([t["id"] for t in new_toots])
    last_toot_at = min([t["created_at"] for t in new_toots])
    logger.debug(f"Retrieved {len(queried_toots)} toots {last_toot_at:%Y-%m-%d %H:%M}")

    paginate = True
    while paginate:
        new_toots = api.timeline_public(limit=40, max_id =  max_id)
        max_id = min([t["id"] for t in new_toots])
        last_toot_at = min([t["created_at"] for t in new_toots])
        new_toots = add_queried_at(new_toots)
        queried_toots.extend(filter_toots(new_toots, q))
        if max_toots is not None and min_date is None:
            paginate = True if len(queried_toots) < max_toots else False
        elif min_date is not None and max_toots is None:
            paginate = True if min_date < last_toot_at else False
        time.sleep(2)
        logger.debug(f"Retrieved {len(new_toots)} new toots and {len(queried_toots)} toots in total ({last_toot_at:%Y-%m-%d %H:%M})")

    logger.info(f"Retrieved {len(queried_toots)} toots ({get_datetime_range(queried_toots)})")

    if verbose and logger.level >= 20:
        logger.setLevel(logging.WARNING)

    return queried_toots


def sample_timeline(api_base, access_token, max_toots = None, min_date = None, verbose=False):
    if verbose and logger.level >= 20:
        logger.setLevel(logging.INFO)

    api = mastodon.Mastodon(api_base_url = api_base, access_token = access_token)

    if max_toots is not None and min_date is None:
        max_toots = int(max_toots)
    elif min_date is not None and max_toots is None:
        min_date = datetime.datetime.strptime(f"{min_date} -0000", "%Y-%m-%d %z")
    else:
        raise Exception("Must set either max_toots or min_date")

    queried_toots = []
    try:
        new_toots = api.timeline_public(limit=40)
        new_toots = add_queried_at(new_toots)
        queried_toots.extend(new_toots)
    except mastodon.MastodonAPIError as e:
        logger.warning(f"There was a problem connecting to {api_base}: {e.args[1:]}")
        return None

    max_id = min([t["id"] for t in new_toots])
    last_toot_at = min([t["created_at"] for t in new_toots])
    logger.debug(f"Retrieved {len(queried_toots)} toots {last_toot_at:%Y-%m-%d %H:%M}")

    paginate = True
    while paginate:
        new_toots = api.timeline_public(limit = 40, max_id =  max_id)
        max_id = min([t["id"] for t in new_toots])
        last_toot_at = min([t["created_at"] for t in new_toots])
        new_toots = add_queried_at(new_toots)
        queried_toots.extend(new_toots)
        if max_toots is not None and min_date is None:
            paginate = True if len(queried_toots) < max_toots else False
        elif min_date is not None and max_toots is None:
            paginate = True if min_date < last_toot_at else False
        time.sleep(2)
        logger.debug(f"Retrieved {len(queried_toots)} toots {last_toot_at:%Y-%m-%d %H:%M}")

    logger.info(f"Retrieved {len(queried_toots)} toots ({get_datetime_range(queried_toots)})")

    if verbose and logger.level >= 20:
        logger.setLevel(logging.WARNING)

    return queried_toots

class Sampler(mastodon.StreamListener):
    def __init__(self, filter_string=None):
        self.toots = []
        self.n_toots = 0
        self.filter_string = filter_string
    
    def on_update(self, status):
        status["queried_at"] = datetime.datetime.now()
        self.toots.append(status)
        self.n_toots += 1
    
    def on_status_update(self, status):
        status["queried_at"] = datetime.datetime.now()
        self.toots.append(status)
        self.n_toots += 1

def stream_timeline(api_base, access_token, max_toots=None, timeframe=None, filter_string=None, verbose=False):
    
    if verbose and logger.level >= 20:
        logger.setLevel(logging.INFO)
    
    start_time = int(time.time())
    time_passed = int(time.time()) - start_time
    
    api = mastodon.Mastodon(api_base_url = api_base, access_token = access_token)
    stream_listener = Sampler()
    
    try:
        stream_handler = api.stream_public(listener = stream_listener, run_async = True, reconnect_async = True, reconnect_async_wait_sec = 30)
        if max_toots is not None:
            while stream_listener.n_toots < max_toots and stream_handler.is_alive():
                time_passed = int(time.time()) - start_time
                print(f"\tStreamed {(stream_listener.n_toots/max_toots):.2%} toots ({(stream_listener.n_toots/time_passed if stream_listener.n_toots != 0 else 0.0):.2f} toots per second)", end = "\r")
                time.sleep(5)
        elif timeframe is not None:
            while time_passed < timeframe and stream_handler.is_alive():
                time_passed = int(time.time()) - start_time
                print(f"\tStreamed {(time_passed/timeframe):.2%} of timeframe ({stream_listener.n_toots} toots @ {(stream_listener.n_toots/time_passed if stream_listener.n_toots != 0 else 0.0):.2f} toots per second)", end = "\r")
                time.sleep(5)
    except:
        print("Error")
    finally:
        stream_handler.close()

    if verbose and logger.level >= 20:
        logger.setLevel(logging.WARNING)

    return stream_listener.toots

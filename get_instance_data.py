#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config as config
#from mastodon import Mastodon
import time
import requests
import json
import sys
import os
import re
import csv


def is_birdsite_fork(r):
    regex = r"<input name=['\"]__RequestVerificationToken['\"] type=['\"]hidden['\"]"
    if re.search(regex, r.text, re.MULTILINE | re.IGNORECASE):
        return(True)
    else:
        return(False)

def get_meta_from_json(domains):
    if ".json" in domains:
        domains = json.load(open(domains, "r"))
    else:
        domains = [domains]

    for i, domain in enumerate(domains):
        if not os.path.exists(f"instances_meta/{domain}_meta.json"):
            api_base = f"https://{domain}/api/v1"
            try:
                r = requests.get(f"{api_base}/instance", timeout=5)
            except requests.exceptions.Timeout as e:
                print(f"{i}\tSomething went wrong with '{domain}' (timeout)")
                continue
            except Exception as e:
                print(f"{i}\tSomething went wrong with '{domain}'", str(e))
                continue
            if r.status_code == 200:
                try:
                    instance_meta = r.json()
                except:
                    print(f"{i}\tSomething went wrong with '{domain}' can't parse json")
                    continue
                json.dump(instance_meta, open(f"instances_meta/{domain}_meta.json", "w"))
                print(f"{i}\tGetting meta data for '{domain}'")
            else:
                r = requests.get(f"https://{domain}")
                if r.status_code == 200 and is_birdsite_fork(r):
                    json.dump({'uri':domain, "version":"BirdsiteLIVE"}, open(f"instances_meta/{domain}_meta.json", "w"))
                else:
                    print(f"{i}\tSomething went wrong with '{domain}'", r.status_code)
        else:
            print(f"{i}\tCached meta data for '{domain}'")

def get_activity_from_json(domains):
    if ".json" in domains:
        domains = json.load(open(domains, "r"))
    else:
        domains = [domains]

    with open("out.csv", "w", newline='') as f:
        writer = csv.writer(f, dialect="unix")
        writer.writerow(["instance_name", "week", "statuses", "logins", "registrations"])
        for i, domain in enumerate(domains):
            api_base = f"https://{domain}/api/v1"
            try:
                r = requests.get(f"{api_base}/instance/activity", timeout=5)
            except requests.exceptions.Timeout as e:
                print(f"{i}\tSomething went wrong with '{domain}' (timeout)")
                continue
            except Exception as e:
                print(f"{i}\tSomething went wrong with '{domain}'", str(e))
                continue
            if r.status_code == 200:
                try:
                    instance_meta = r.json()
                except:
                    print(f"{i}\tSomething went wrong with '{domain}' can't parse json")
                    continue
                if not "error" in instance_meta.keys():
                    for week in instance_meta:
                        writer.writerow([domain, week["week"], week["statuses"], week["logins"], week["registrations"]])
                else:
                    print(f"{i}\tSomething went wrong with '{domain}' ({instance_meta["error"]})")
                    continue




def get_rules(instance):
    if "rules" in instance.keys():
        return json.dumps([r["text"] for r in instance["rules"]])
    else:
        return ""

def to_csv(domains, dir):
    key_names = ["instance_name", "title", "short_description", "description", "user_count", "status_count", "domain_count", "registrations", "approval_required", "rules"]
    
    domains = json.load(open(domains, "r"))
    
    with open("out.csv", "w", newline='') as f:
        writer = csv.writer(f, dialect="unix")
        writer.writerow(key_names)

        for instance in domains:
            if os.path.exists(f"instances_meta/{instance}_meta.json"):
                instance = json.load(open(f"instances_meta/{instance}_meta.json", "r"))
                try:
                    writer.writerow([
                        instance["uri"],
                        instance["title"] if "title" in instance.keys() else "",
                        instance["short_description"] if "short_description" in instance.keys() else "",
                        instance["description"] if "description" in instance.keys() else "",
                        instance["stats"]["user_count"] if "stats" in instance.keys() and "user_count" in instance["stats"].keys() else "",
                        instance["stats"]["status_count"] if "stats" in instance.keys() and "status_count" in instance["stats"].keys() else "",
                        instance["stats"]["domain_count"] if "stats" in instance.keys() and "domain_count" in instance["stats"].keys() else "",
                        instance["registrations"] if "registrations" in instance.keys() else "",
                        instance["approval_required"] if "approval_required" in instance.keys() else "",
                        get_rules(instance)
                    ])
                except:
                    writer.writerow([
                    instance,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    ""
                ])    
            else:
                writer.writerow([
                    instance,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    ""
                ])
        

#get_from_json(sys.argv[1])
#to_csv(sys.argv[1], sys.argv[2])
get_activity_from_json(sys.argv[1])
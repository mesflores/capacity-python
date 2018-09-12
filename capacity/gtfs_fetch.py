"""Functions to fetch fresh GTFS Data"""

import os.path
import shlex
import subprocess

import requests
import feedparser

URL_FEED = 'https://gitlab.com/LACMTA/gtfs_rail/commits/master.atom'
EVERGREEN = "https://gitlab.com/LACMTA/gtfs_rail/raw/master/gtfs_rail.zip"

def get_last_commit():
    """ What is the last commit seen in the feed?"""

    url = URL_FEED
    feed = feedparser.parse(url)
    lastupdate = feed['feed']['updated']

    return lastupdate

def check_up_to_date(log_dir):
    """ Check to see if we need to do anything"""

    last_edit_file = os.path.join(log_dir, "last_edit")

    # Grab the stamp in the file
    try:
        with open(last_edit_file, 'r') as last_edit_f:
            last_edit = last_edit_f.read()
    except IOError:
        # No logged time, just re-fetch
        return False

    curr_edit = get_last_commit()

    # Just return true if they match
    return curr_edit == last_edit

def get_data(log_dir):
    """grab the latest data"""
    save_file = os.path.join(log_dir, "gtfs_data.zip")
    # Grab the file and save it
    resp = requests.get(EVERGREEN)
    with open(save_file, 'wb') as zip_file:
        zip_file.write(resp.content)

    # Go in there and unzip it!
    subprocess.Popen(shlex.split("unzip -o gtfs_data.zip"), cwd=log_dir)

    # Update the file
    current = get_last_commit()
    last_edit_file = os.path.join(log_dir, "last_edit")
    with open(last_edit_file, 'w') as last_edit_f:
        last_edit_f.write(current)


def update_gtfs():
    """Update the files, if we need to"""
    log_dir = "gtfs_data"
    if not check_up_to_date(log_dir):
        # We need to update!
        get_data(log_dir)

    # else all good -- do nothing

#!/usr/bin/env python3

# Copyright 2018 University of Sheffield (Jon Barker)
# MIT License (https://opensource.org/licenses/MIT)

import json
import datetime

CHIME5_JSON = 'chime5.json'  # Name of the CHiME5 json metadata file


def chime_data(sets_to_load=None):
    """Load CHiME corpus data for specified sets eg. sets=['train', 'eval']

    Defaults to all
    """
    if sets_to_load is None:
        sets_to_load = ['train', 'dev', 'eval']

    with open(CHIME5_JSON) as fh:
        data = json.load(fh)

    data = {k: v for (k, v) in data.items() if v['dataset'] in sets_to_load}

    return data


def time_text_to_float(time_string):
    """Convert tramscript time from text to float format."""
    hours, minutes, seconds = time_string.split(':')
    seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    return seconds


def time_float_to_text(time_float):
    """Convert tramscript time from float to text format."""
    # Milliseconds are rounded to 2 dp.
    time = datetime.datetime.min + datetime.timedelta(seconds=time_float+0.005)
    return time.strftime('%H:%M:%S.%f')[:-4]

def load_transcript(session, root, convert=False):
    """Load final merged transcripts.

    session: recording session name, e.g. 'S12'
    """
    with open(root + "/" + session + ".json") as f:
                transcript = json.load(f)
    if convert:
        for item in transcript:
            for key in item['start_time']:
                item['start_time'][key] = time_text_to_float(item['start_time'][key])
            for key in item['end_time']:
                item['end_time'][key] = time_text_to_float(item['end_time'][key])
    return transcript


def save_transcript(transcript, session, root, convert=False, challenge='CHIME5'):
    """Save transcripts to json file."""

    # Need to make a deep copy so time to string conversions only happen locally
    transcript_copy = [element.copy() for element in transcript]

    if convert:
        for item in transcript_copy:
            # For CHiME-5 every time is a dictionary with entries for each device
            if type(item['start_time']) == dict:
                for key in item['start_time']:
                    item['start_time'][key] = time_float_to_text(
                        item['start_time'][key])
                for key in item['end_time']:
                    item['end_time'][key] = time_float_to_text(
                        item['end_time'][key])
            else: 
                # For CHiME-6 there is only one start and end time per utterance.
                item['start_time'] = time_float_to_text(item['start_time'])
                item['end_time'] = time_float_to_text(item['end_time'])

    with open(root + "/" + session + ".json", 'w') as outfile:
        json.dump(transcript_copy, outfile, indent=4)

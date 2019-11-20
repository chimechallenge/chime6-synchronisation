#!/usr/bin/env python3

# Copyright 2018 University of Sheffield (Jon Barker)
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

"""
align_transcription.py

Apply the alignments to the transcription file
"""

import argparse
import traceback
import numpy as np
import json

import transcript_utils as tu

CHIME_DATA = tu.chime_data()

CHIME_SAMPLE_RATE = 16000  # CHiME sample rate.

def correct_transcription_for_clock_drift(session, linear_fit_data, in_path, out_path, chime5_mode=False):
    """Apply clock drift to transcription file.
    
    chime5_mode - if true then for each utterance write an (identical) start and end time for every device, 
        otherwise use new, non-redundant chime6 format which only records the start and end time once
    """
    dataset = CHIME_DATA[session]['dataset']
    transcription = tu.load_transcript(session, in_path + '/' + dataset, convert=True)

    if session not in linear_fit_data:
        print("WARNING: Linear fit data missing for session" + session)
    
    # Compute alignments for the TASCAM binaural mics
    pids = CHIME_DATA[session]['pids']
    for pid in pids:
        print(pid)
        if pid not in linear_fit_data[session]:
            print("WARNING: Linear fit data mission for session " + session + " speaker " + pid)
            return
        
        fit = linear_fit_data[session][pid]
        speed = fit['speed']  # start as required speed up needed
        padding = fit['padding']  # stored as samples of padding needed
        delta_t = padding / CHIME_SAMPLE_RATE
        # process transcription for each speaker
        for utterance in transcription:
            if utterance.get('speaker', None) == pid:
                start_time = utterance['start_time']['original'] / speed + delta_t
                end_time = utterance['end_time']['original'] / speed + delta_t
                if chime5_mode:
                    # Identical time entry for each device
                    for key in utterance['start_time']:
                        utterance['start_time'][key] = start_time
                    for key in utterance['end_time']:
                        utterance['end_time'][key] = end_time
                else:
                    # A single time entry 
                    utterance['start_time'] = start_time
                    utterance['end_time'] = end_time

    # Remove the speakerless segments that marked position of redactions. 
    # There's no easy way to correct these timings without going back to the original transcripts
    # because the necessary speaker ids were removed as part of the redaction.
    transcription = [utterance for utterance in transcription if 'speaker' in utterance]
    tu.save_transcript(transcription, session, out_path + '/' + dataset, convert=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions",
                        help="list of sessions to process (defaults to all)")
    parser.add_argument("--clock_drift_data", help="json file storing clock drift data")  
    parser.add_argument('--chime5', action='store_true', help="write transcript file in older CHiME-5 format") 
    parser.add_argument("in_path", help="path for the input transcription file")
    parser.add_argument("out_path", help="path for the output transcription files")
    
    args = parser.parse_args()
    if args.sessions is None:
        sessions = tu.chime_data()
    else:
        sessions = args.sessions.split()

    print(args.chime5)
    with open(args.clock_drift_data) as f:
        linear_fit_data = json.load(f)

    for session in sessions:
        try:
            print(session)
            correct_transcription_for_clock_drift(session, linear_fit_data, args.in_path, args.out_path, 
                                                  chime5_mode=args.chime5)
        except:
            traceback.print_exc()


if __name__ == '__main__':
    main()
